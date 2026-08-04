namespace SemanticKernelDemo.Dispatcher;

/// <summary>
/// 任务处理器抽象。每个实现负责"判断是否能处理某任务" + "实际处理"。
/// 这是你后续填充业务逻辑的地方。
/// </summary>
public interface ITaskHandler
{
    /// <summary>处理器名称，用于日志与结果标识。</summary>
    string Name { get; }

    /// <summary>判断当前任务是否应由本处理器处理（匹配规则，由你实现）。</summary>
    bool CanHandle(TaskContext context);

    /// <summary>实际处理任务，返回处理结果文本。</summary>
    Task<string> HandleAsync(TaskContext context, CancellationToken ct);
}