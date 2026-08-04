using System.Collections.Concurrent;
using SemanticKernelDemo.Channel;

namespace SemanticKernelDemo.Services;

/// <summary>
/// 通道演示：演示"钩子"如何注册回调，以及发布消息后如何被钩子处理。
/// 你的现有 .NET 服务可在此注册自己感兴趣的消息类型钩子。
/// </summary>
public sealed class ChannelDemo
{
    private readonly MessageHook _hook;
    private readonly ConcurrentDictionary<string, string> _responses = new();

    public ChannelDemo(MessageHook hook)
    {
        _hook = hook;

        // 钩子：收到 "ping" 类型消息时，回一个 pong。
        _hook.Register(MessageTypes.Ping, (envelope, _) =>
        {
            _responses[envelope.MessageId] = $"pong:{envelope.SessionId}";
            return Task.CompletedTask;
        });
    }

    /// <summary>发布一条 "ping" 消息，并返回钩子处理后的响应（内存通道下同步可得）。</summary>
    public async Task<object> PingAsync(string sessionId, CancellationToken ct)
    {
        var envelope = MessageEnvelope.Create(MessageTypes.Ping, sessionId, "你好");
        await _hook.PublishAsync(envelope, ct);

        _responses.TryGetValue(envelope.MessageId, out var hookResponse);
        return new { envelope, hookResponse };
    }
}