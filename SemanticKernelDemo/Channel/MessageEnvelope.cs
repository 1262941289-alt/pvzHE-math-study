namespace SemanticKernelDemo.Channel;

/// <summary>
/// 消息信封：在通道上传输的统一消息结构。
/// 双方（本桥与你的 .NET 服务）通过该结构互相收发。
/// </summary>
public sealed record MessageEnvelope(
    string MessageId,
    string Type,          // 消息类型，用于钩子路由
    string SessionId,
    string Payload,       // 业务内容（JSON 字符串）
    DateTime Timestamp = default)
{
    public static MessageEnvelope Create(string type, string sessionId, string payload)
        => new(Guid.NewGuid().ToString("N"), type, sessionId, payload, DateTime.UtcNow);
}