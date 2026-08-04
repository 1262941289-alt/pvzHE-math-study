using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Agents;
using Microsoft.SemanticKernel.Agents.Chat;

namespace SemanticKernelDemo.Agents;

/// <summary>
/// 总-分式协作的"终止策略"：
/// 规划师平时只作为选择器出现（不进入团队历史），仅在任务完成时才作为"成员"产出最终答案。
/// 因此一旦历史最后一条消息来自规划师，即视为协作完成并结束。
/// </summary>
public sealed class PlannerTerminationStrategy : TerminationStrategy
{
    private readonly string _plannerName;

    public PlannerTerminationStrategy(string plannerName) => _plannerName = plannerName;

    protected override Task<bool> ShouldAgentTerminateAsync(
        Agent agent,
        IReadOnlyList<ChatMessageContent> history,
        CancellationToken cancellationToken)
    {
        var last = history.LastOrDefault();
        return Task.FromResult(last is not null && last.AuthorName == _plannerName);
    }
}