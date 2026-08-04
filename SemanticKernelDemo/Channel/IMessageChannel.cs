namespace SemanticKernelDemo.Channel;

/// <summary>
/// 消息通道抽象：收发消息的统一入口。可插拔底层传输（内存 / RabbitMQ / MQ 等）。
/// 你的 .NET 服务与本桥通过该通道互相通信。
/// </summary>
public interface IMessageChannel
{
    /// <summary>通道名称，用于日志与标识。</summary>
    string Name { get; }

    /// <summary>发布一条消息到通道。</summary>
    Task PublishAsync(MessageEnvelope envelope, CancellationToken ct);

    /// <summary>订阅消息接收。注册的处理函数在收到消息时被调用。</summary>
    Task SubscribeAsync(Func<MessageEnvelope, CancellationToken, Task> handler, CancellationToken ct);

    /// <summary>启动消费者（RabbitMQ 等需要；内存通道可空实现）。</summary>
    Task StartAsync(CancellationToken ct);

    /// <summary>停止消费者。</summary>
    Task StopAsync(CancellationToken ct);
}