using System.ComponentModel;
using Microsoft.SemanticKernel;

namespace SemanticKernelDemo;

/// <summary>
/// 演示插件：展示如何把普通 C# 方法封装成 Semantic Kernel 插件函数，
/// 供 Agent 在对话中自动调用（function calling）。
/// </summary>
public sealed class TimePlugin
{
    [KernelFunction("get_current_time")]
    [Description("获取当前的本地日期和时间。当用户询问时间、日期时调用。")]
    public string GetCurrentTime()
        => DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss");
}