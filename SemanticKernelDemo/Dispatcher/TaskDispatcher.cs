namespace SemanticKernelDemo.Dispatcher;

/// <summary>分发模式：只取第一个匹配，还是把所有匹配的处理器都执行。</summary>
public enum DispatchMode
{
    /// <summary>只取第一个匹配的处理器。</summary>
    FirstMatch,

    /// <summary>把所有匹配的处理器都执行（汇总结果）。</summary>
    FanOut,
}

/// <summary>
/// 核心分发器框架。注册若干 <see cref="ITaskHandler"/>，按匹配规则把任务分发给合适的处理器。
/// 你只需注册自己的 handler，分发流程由本框架驱动。
/// </summary>
public sealed class TaskDispatcher
{
    private readonly List<ITaskHandler> _handlers = new();
    private readonly ITaskHandler? _fallback;
    private readonly DispatchMode _mode;

    public TaskDispatcher(DispatchMode mode = DispatchMode.FirstMatch, ITaskHandler? fallback = null)
    {
        _mode = mode;
        _fallback = fallback;
    }

    /// <summary>注册一个处理器。</summary>
    public void Register(ITaskHandler handler) => _handlers.Add(handler);

    /// <summary>分发任务：按匹配规则选出处理器并执行，返回结果列表。</summary>
    public async Task<IReadOnlyList<DispatchResult>> DispatchAsync(TaskContext context, CancellationToken ct)
    {
        var matches = _handlers.Where(h => h.CanHandle(context)).ToList();

        // 无匹配：走兜底（若有），否则返回空
        if (matches.Count == 0)
        {
            return _fallback is null
                ? new List<DispatchResult>()
                : new[] { await DispatchOneAsync(_fallback, context, ct) };
        }

        // 首匹配模式：只执行第一个
        if (_mode == DispatchMode.FirstMatch)
        {
            return new[] { await DispatchOneAsync(matches[0], context, ct) };
        }

        // 扇出模式：执行所有匹配
        var results = new List<DispatchResult>(matches.Count);
        foreach (var handler in matches)
        {
            results.Add(await DispatchOneAsync(handler, context, ct));
        }
        return results;
    }

    private static async Task<DispatchResult> DispatchOneAsync(ITaskHandler handler, TaskContext context, CancellationToken ct)
    {
        var content = await handler.HandleAsync(context, ct);
        return new DispatchResult(handler.Name, content);
    }
}