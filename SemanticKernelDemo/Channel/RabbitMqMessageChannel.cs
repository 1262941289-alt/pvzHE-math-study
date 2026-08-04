using System.Text;
using System.Text.Json;
using RabbitMQ.Client;
using RabbitMQ.Client.Events;

namespace SemanticKernelDemo.Channel;

/// <summary>
/// RabbitMQ 通道：通过消息队列与本桥之外的服务（如你的 .NET 服务）双向通信。
/// 需要可用的 RabbitMQ 实例。消息体为 <see cref="MessageEnvelope"/> 的 JSON。
/// </summary>
public sealed class RabbitMqMessageChannel : IMessageChannel, IAsyncDisposable
{
    private readonly string _queueName;
    private readonly IConnection _connection;
    private readonly IChannel _channel;
    private Func<MessageEnvelope, CancellationToken, Task>? _handler;

    public string Name => "rabbitmq";

    public RabbitMqMessageChannel(string hostName, string? userName, string? password, string queueName)
    {
        _queueName = queueName;

        var factory = new ConnectionFactory
        {
            HostName = hostName,
            UserName = userName ?? "guest",
            Password = password ?? "guest",
        };
        _connection = factory.CreateConnectionAsync().GetAwaiter().GetResult();
        _channel = _connection.CreateChannelAsync().GetAwaiter().GetResult();
        _channel.QueueDeclareAsync(queue: queueName, durable: true, exclusive: false, autoDelete: false)
            .GetAwaiter().GetResult();
    }

    public Task PublishAsync(MessageEnvelope envelope, CancellationToken ct)
    {
        var body = Encoding.UTF8.GetBytes(JsonSerializer.Serialize(envelope));
        return _channel.BasicPublishAsync(
            exchange: string.Empty,
            routingKey: _queueName,
            mandatory: false,
            body: body).AsTask();
    }

    public Task SubscribeAsync(Func<MessageEnvelope, CancellationToken, Task> handler, CancellationToken ct)
    {
        _handler = handler;
        return Task.CompletedTask;
    }

    public Task StartAsync(CancellationToken ct)
    {
        var consumer = new AsyncEventingBasicConsumer(_channel);
        consumer.ReceivedAsync += async (_, args) =>
        {
            if (_handler is null)
            {
                return;
            }

            var json = Encoding.UTF8.GetString(args.Body.Span);
            var envelope = JsonSerializer.Deserialize<MessageEnvelope>(json);
            if (envelope is not null)
            {
                await _handler(envelope, ct);
            }
        };

        _channel.BasicConsumeAsync(queue: _queueName, autoAck: true, consumer: consumer);
        return Task.CompletedTask;
    }

    public Task StopAsync(CancellationToken ct) => Task.CompletedTask;

    public async ValueTask DisposeAsync()
    {
        await _channel.CloseAsync();
        await _connection.CloseAsync();
    }
}