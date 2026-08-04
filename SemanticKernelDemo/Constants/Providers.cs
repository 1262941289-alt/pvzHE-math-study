namespace SemanticKernelDemo;

/// <summary>聊天模型提供商名称。</summary>
public static class Providers
{
    public const string OpenAi = "OpenAI";
    public const string AzureOpenAi = "AzureOpenAI";
}

/// <summary>消息通道提供商名称。</summary>
public static class ChannelProviders
{
    public const string InMemory = "InMemory";
    public const string RabbitMq = "RabbitMQ";
}