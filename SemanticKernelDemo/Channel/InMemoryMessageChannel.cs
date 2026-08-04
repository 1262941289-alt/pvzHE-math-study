namespace SemanticKernelDemo.Channel;

/// <summary>
/// 内存通道：进程内收发消息，无需任何 broker。适合本地开发、测试与演示。
/// 发布即同步调用已订阅的处理函数（进程内直连）。
/// 生产环境请改用 <see cref="RabbitMqMessageChannel"/>。
/// </summary>
public sealed class InMemoryMessageChannel : IMessageChannel
{
    private Func<MessageEnvelope, CancellationToken, Task>? _handler;

    public string Name => "in-memory";

    public Task PublishAsync(MessageEnvelope envelope, CancellationToken ct)
    {
        // 内存通道：发布即就地处理（进程内，无 broker 延迟）。
        return _handler is not null
            ? _handler(envelope, ct)
            : Task.CompletedTask;
    }

    public Task SubscribeAsync(Func<MessageEnvelope, CancellationToken, Task> handler, CancellationToken ct)
    {
        _handler = handler;
        return Task.CompletedTask;
    }

    public Task StartAsync(CancellationToken ct) => Task.CompletedTask;

    public Task StopAsync(CancellationToken ct) => Task.CompletedTask;
}