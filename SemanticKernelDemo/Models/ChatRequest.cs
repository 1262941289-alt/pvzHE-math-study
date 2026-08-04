namespace SemanticKernelDemo.Models;

/// <summary>
/// 聊天请求：会话 ID + 用户消息。
/// Java 端与浏览器插件通过此结构调用。
/// </summary>
public sealed record ChatRequest(string SessionId, string Message);