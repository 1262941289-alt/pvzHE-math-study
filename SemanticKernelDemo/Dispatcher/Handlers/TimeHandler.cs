namespace SemanticKernelDemo.Dispatcher.Handlers;

/// <summary>
/// 示例处理器：查询当前时间。演示如何把业务逻辑封装进 handler。
/// </summary>
public sealed class TimeHandler : ITaskHandler
{
    public string Name => "Time";

    public bool CanHandle(TaskContext context)
        => context.Message.Contains("时间", StringComparison.OrdinalIgnoreCase)
           || context.Message.Contains("几点", StringComparison.OrdinalIgnoreCase);

    public Task<string> HandleAsync(TaskContext context, CancellationToken ct)
        => Task.FromResult($"当前时间是 {DateTime.Now:yyyy-MM-dd HH:mm:ss}。");
}