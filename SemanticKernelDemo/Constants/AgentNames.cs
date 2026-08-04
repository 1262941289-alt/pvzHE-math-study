namespace SemanticKernelDemo;

/// <summary>多 Agent 团队中的成员名称。</summary>
public static class AgentNames
{
    public const string Planner = "Planner";

    /// <summary>通用分成员（无固定职责，角色由规划师临时指定）。</summary>
    public static readonly IReadOnlyList<string> Workers =
        new[] { "WorkerAlpha", "WorkerBeta", "WorkerGamma" };
}

/// <summary>通道上传输的消息类型。</summary>
public static class MessageTypes
{
    public const string Ping = "ping";
}