using System.Text.Json;
using Microsoft.Extensions.Options;
using Microsoft.SemanticKernel;
using SemanticKernelDemo;
using SemanticKernelDemo.Channel;
using SemanticKernelDemo.Dispatcher;
using SemanticKernelDemo.Dispatcher.Handlers;
using SemanticKernelDemo.Models;
using SemanticKernelDemo.Options;
using SemanticKernelDemo.Services;

var builder = WebApplication.CreateBuilder(args);

// ---------- 配置绑定 ----------
builder.Services
    .Configure<CompletionOptions>(builder.Configuration.GetSection("Completion"))
    .Configure<ChannelOptions>(builder.Configuration.GetSection("Channel"));

// ---------- 核心服务 ----------
builder.Services.AddSingleton<Kernel>(sp =>
    KernelFactory.Create(sp.GetRequiredService<IOptions<CompletionOptions>>().Value));

builder.Services.AddSingleton<AgentChatService>();

// 分发器框架：把示例 handler 挂进去；你后续在此注册自己的 handler。
// 例：改成 FanOut 模式可让所有匹配的 handler 都执行。
builder.Services.AddSingleton(sp =>
{
    var dispatcher = new TaskDispatcher(DispatchMode.FirstMatch);
    dispatcher.Register(new GreetingHandler());
    dispatcher.Register(new TimeHandler());
    return dispatcher;
});

// ---------- 消息通道 + 钩子（与你的 .NET 服务双向通信） ----------
builder.Services.AddSingleton<IMessageChannel>(sp =>
{
    var options = sp.GetRequiredService<IOptions<ChannelOptions>>().Value;
    if (options.Provider.Equals(ChannelProviders.RabbitMq, StringComparison.OrdinalIgnoreCase))
    {
        var rmq = options.RabbitMQ;
        return new RabbitMqMessageChannel(rmq.HostName, rmq.UserName, rmq.Password, rmq.QueueName);
    }
    return new InMemoryMessageChannel();
});

builder.Services.AddSingleton<MessageHook>();
builder.Services.AddSingleton<ChannelDemo>();

var app = builder.Build();

// 启动通道消费者（内存通道：起一个消费任务；RabbitMQ：起订阅）
await app.Services.GetRequiredService<MessageHook>().StartAsync(CancellationToken.None);

// 未配置 API Key 时，服务仍可启动（健康检查可用），但 /api/chat 返回明确错误。
var configured = app.Services.GetRequiredService<IOptions<CompletionOptions>>().Value.IsConfigured;

// 规整 sessionId：空则生成新 id。
static string NormalizeSessionId(string? sessionId)
    => string.IsNullOrWhiteSpace(sessionId) ? Guid.NewGuid().ToString("N") : sessionId;

// ---------- 健康检查 ----------
app.MapGet("/api/health", (AgentChatService service) => Results.Ok(new
{
    status = "ok",
    configured,
    sessions = service.SessionCount,
}));

// ---------- 聊天桥：POST /api/chat ----------
// 请求体：{ "sessionId": "xxx", "message": "你好" }
// 返回：  最终答案 + 完整的团队协作过程
app.MapPost("/api/chat", async (ChatRequest request, AgentChatService service, CancellationToken ct) =>
{
    if (!configured)
    {
        return Results.Json(
            new { error = "未配置 API Key。请设置环境变量 SemanticKernel__Completion__ApiKey 或填写 appsettings.json。" },
            statusCode: StatusCodes.Status503ServiceUnavailable);
    }

    if (string.IsNullOrWhiteSpace(request.Message))
    {
        return Results.BadRequest(new { error = "message 不能为空。" });
    }

    var response = await service.ChatAsync(NormalizeSessionId(request.SessionId), request.Message, ct);
    return Results.Ok(response);
});

// ---------- 流式聊天：POST /api/chat/stream（SSE） ----------
// 请求体同 /api/chat。返回 text/event-stream，每个 Agent 发言推一个事件：
//   event: turn
//   data: {"author":"Planner","content":"..."}
// 结束时推 event: done。
app.MapPost("/api/chat/stream", async (ChatRequest request, AgentChatService service, HttpResponse response, CancellationToken ct) =>
{
    if (!configured)
    {
        return Results.Json(
            new { error = "未配置 API Key。请设置环境变量 SemanticKernel__Completion__ApiKey 或填写 appsettings.json。" },
            statusCode: StatusCodes.Status503ServiceUnavailable);
    }

    if (string.IsNullOrWhiteSpace(request.Message))
    {
        return Results.BadRequest(new { error = "message 不能为空。" });
    }

    var sessionId = NormalizeSessionId(request.SessionId);
    response.Headers.ContentType = "text/event-stream";
    response.Headers.CacheControl = "no-cache";
    response.Headers.Connection = "keep-alive";

    await foreach (var turn in service.StreamChatAsync(sessionId, request.Message, ct))
    {
        var data = JsonSerializer.Serialize(turn);
        await response.WriteAsync($"event: turn\ndata: {data}\n\n", ct);
        await response.Body.FlushAsync(ct);
    }

    await response.WriteAsync($"event: done\ndata: {{\"sessionId\":\"{sessionId}\"}}\n\n", ct);
    await response.Body.FlushAsync(ct);
    return Results.Empty;
});

// ---------- 分发器 demo：POST /api/dispatch ----------
// 请求体：{ "sessionId": "xxx", "message": "你好" }
// 按已注册的 handler 匹配规则分发，返回命中的处理器与结果。
app.MapPost("/api/dispatch", async (ChatRequest request, TaskDispatcher dispatcher, CancellationToken ct) =>
{
    if (string.IsNullOrWhiteSpace(request.Message))
    {
        return Results.BadRequest(new { error = "message 不能为空。" });
    }

    var context = new TaskContext(
        sessionId: NormalizeSessionId(request.SessionId),
        message: request.Message);

    var results = await dispatcher.DispatchAsync(context, ct);
    return Results.Ok(results);
});

// ---------- 通道 demo：POST /api/channel/ping ----------
// 请求体：{ "sessionId": "xxx" }
// 发布一条 "ping" 消息到通道，由已注册的钩子处理并返回响应（验证双向通信）。
app.MapPost("/api/channel/ping", async (ChatRequest request, ChannelDemo demo, CancellationToken ct) =>
{
    var result = await demo.PingAsync(NormalizeSessionId(request.SessionId), ct);
    return Results.Ok(result);
});

// ---------- 删除会话：DELETE /api/chat/{sessionId} ----------
app.MapDelete("/api/chat/{sessionId}", (string sessionId, AgentChatService service) =>
    service.DeleteSession(sessionId)
        ? Results.Ok(new { deleted = sessionId })
        : Results.NotFound(new { error = "会话不存在。" }));

app.Run();