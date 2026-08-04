namespace SemanticKernelDemo.Dispatcher;

/// <summary>分发结果：由哪个处理器处理，产出什么。</summary>
public sealed record DispatchResult(string HandlerName, string Content);