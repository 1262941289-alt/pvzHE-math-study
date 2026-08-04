namespace SemanticKernelDemo.Options;

/// <summary>聊天模型学习配置，绑定自 appsettings.json 的 "Completion" 段。</summary>
public sealed class CompletionOptions
{
    public string Provider { get; set; } = Providers.OpenAi;
    public string ModelId { get; set; } = "gpt-4o-mini";
    public string ApiKey { get; set; } = string.Empty;
    public string Endpoint { get; set; } = string.Empty;

    /// <summary>是否已配置 API Key，决定 Agent 能力是否可用。</summary>
    public bool IsConfigured => !string.IsNullOrWhiteSpace(ApiKey);
}