namespace SemanticKernelDemo.Options;

/// <summary>消息通道配置，绑定自 appsettings.json 的 "Channel" 段。</summary>
public sealed class ChannelOptions
{
    public string Provider { get; set; } = ChannelProviders.InMemory;
    public RabbitMqOptions RabbitMQ { get; set; } = new();
}

/// <summary>RabbitMQ 连接与队列配置。</summary>
public sealed class RabbitMqOptions
{
    public string HostName { get; set; } = "localhost";
    public string UserName { get; set; } = "guest";
    public string Password { get; set; } = "guest";
    public string QueueName { get; set; } = "bridge";
}