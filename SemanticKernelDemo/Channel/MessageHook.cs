namespace SemanticKernelDemo.Channel;

/// <summary>
/// 消息钩子：你的现有项目在此注册"按消息类型触发的回调"。
/// 通道收到消息后，自动路由到对应类型的钩子处理函数。
/// 这是"留一个钩子方便调用"的落地位置。
/// </summary>
public sealed class MessageHook
{
    private readonly IMessageChannel _channel;
    private readonly Dictionary<string, Func<MessageEnvelope, CancellationToken, Task>> _handlers = new();
    private bool _started;

    public MessageHook(IMessageChannel channel)
    {
        _channel = channel;
    }

    /// <summary>注册一个按消息类型触发的钩子。</summary>
    public void Register(string type, Func<MessageEnvelope, CancellationToken, Task> handler)
    {
        _handlers[type] = handler;
    }

    /// <summary>向通道发布一条消息（发往你的 .NET 服务）。</summary>
    public Task PublishAsync(MessageEnvelope envelope, CancellationToken ct)
        => _channel.PublishAsync(envelope, ct);

    /// <summary>开始接收消息：把通道收到的事件路由到已注册的钩子。</summary>
    public async Task StartAsync(CancellationToken ct)
    {
        if (_started) return;
        await _channel.SubscribeAsync(OnMessageAsync, ct);
        await _channel.StartAsync(ct);
        _started = true;
    }

    public Task StopAsync(CancellationToken ct) => _channel.StopAsync(ct);

    private Task OnMessageAsync(MessageEnvelope envelope, CancellationToken ct)
    {
        if (_handlers.TryGetValue(envelope.Type, out var handler))
        {
            return handler(envelope, ct);
        }
        return Task.CompletedTask;
    }
}