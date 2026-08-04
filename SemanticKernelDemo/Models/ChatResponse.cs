namespace SemanticKernelDemo.Models;

/// <summary>多 Agent 协作中的一次发言记录。</summary>
public sealed record ChatTurn(string Author, string Content);

/// <summary>
/// 聊天响应：最终答案 + 完整的团队协作过程（每个 Agent 的发言）。
/// </summary>
public sealed record ChatResponse(
    string SessionId,
    string Response,
    IReadOnlyList<ChatTurn> Turns);