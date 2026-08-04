namespace SemanticKernelDemo.Dispatcher.Handlers;

/// <summary>
/// 示例处理器：问候语。演示"匹配规则 + 处理逻辑"的写法模板。
/// 你后续的处理器照此结构实现即可。
/// </summary>
public sealed class GreetingHandler : ITaskHandler
{
    public string Name => "Greeting";

    public bool CanHandle(TaskContext context)
        => context.Message.Contains("你好", StringComparison.OrdinalIgnoreCase)
           || context.Message.Contains("hello", StringComparison.OrdinalIgnoreCase);

    public Task<string> HandleAsync(TaskContext context, CancellationToken ct)
        => Task.FromResult($"你好，{context.SessionId}！有什么可以帮你？");
}