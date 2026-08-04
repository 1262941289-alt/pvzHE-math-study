namespace SemanticKernelDemo.Dispatcher;

/// <summary>
/// 一次待分发任务的上下文。承载输入消息、会话 ID 与可选的附加元数据。
/// </summary>
public sealed class TaskContext
{
    public string SessionId { get; }

    public string Message { get; }

    /// <summary>附加元数据，供 handler 与分发规则使用。</summary>
    public IDictionary<string, object> Metadata { get; } = new Dictionary<string, object>();

    public TaskContext(string sessionId, string message)
    {
        SessionId = sessionId;
        Message = message;
    }
}