using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Agents;
using Microsoft.SemanticKernel.Agents.Chat;
using Microsoft.SemanticKernel.ChatCompletion;

namespace SemanticKernelDemo.Agents;

/// <summary>
/// 总-分式多 Agent 协作的"选择策略"：
/// 由"总规划师" Agent 读取对话历史，动态决定下一个应该由哪个成员发言。
/// 成员没有固定职责，完全由规划师按任务灵活指定。
/// 当规划师认为任务已完成时，返回规划师自身，由其汇总产出最终答案。
/// </summary>
public sealed class PlannerSelectionStrategy : SelectionStrategy
{
    private readonly ChatCompletionAgent _planner;
    private readonly Agent _fallback;
    private readonly string _plannerInstructions;

    public PlannerSelectionStrategy(ChatCompletionAgent planner, Agent fallback, string plannerInstructions)
    {
        _planner = planner;
        _fallback = fallback;
        _plannerInstructions = plannerInstructions;
    }

    protected override async Task<Agent> SelectAgentAsync(
        IReadOnlyList<Agent> agents,
        IReadOnlyList<ChatMessageContent> history,
        CancellationToken cancellationToken)
    {
        var names = string.Join(", ", agents.Select(a => $"\"{a.Name}\""));

        // 构造规划师看到的场景：系统提示词 + 团队对话历史 + 选择指令
        var prompt = new ChatHistory();
        prompt.AddSystemMessage(_plannerInstructions);
        foreach (var m in history.Where(m => m.Role != AuthorRole.System))
        {
            prompt.Add(m);
        }
        prompt.AddUserMessage($"根据以上对话，从这些成员中选择下一个发言人：{names}。若任务已完成，回复 DONE。只回复一个名字或 DONE。");

        var reply = await _planner.InvokeAsync(prompt, cancellationToken: cancellationToken).ToListAsync(cancellationToken);
        var choice = string.Concat(reply.Select(r => r.Message.Content)).Trim() ?? string.Empty;

        // 规划师判定任务完成 → 让规划师汇总最终答案
        if (choice.Contains("DONE", StringComparison.OrdinalIgnoreCase))
        {
            return _planner;
        }

        // 否则按规划师指定的名字挑选成员；找不到则回退到默认成员
        return agents.FirstOrDefault(a => choice.Contains(a.Name ?? string.Empty, StringComparison.OrdinalIgnoreCase)) ?? _fallback;
    }
}