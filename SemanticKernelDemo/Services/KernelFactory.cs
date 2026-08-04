using Microsoft.SemanticKernel;
using SemanticKernelDemo.Options;

namespace SemanticKernelDemo.Services;

/// <summary>构建 Semantic Kernel 实例与聊天模型。</summary>
public static class KernelFactory
{
    public static Kernel Create(CompletionOptions options)
    {
        var builder = Kernel.CreateBuilder();

        if (options.IsConfigured)
        {
            if (options.Provider.Equals(Providers.AzureOpenAi, StringComparison.OrdinalIgnoreCase))
            {
                builder.AddAzureOpenAIChatCompletion(options.ModelId, options.Endpoint, options.ApiKey);
            }
            else
            {
                builder.AddOpenAIChatCompletion(options.ModelId, options.ApiKey);
            }
        }

        var kernel = builder.Build();
        kernel.Plugins.AddFromType<TimePlugin>();
        return kernel;
    }
}