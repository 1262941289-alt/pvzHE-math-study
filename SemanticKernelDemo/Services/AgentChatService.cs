using System.Collections.Concurrent;
using System.Runtime.CompilerServices;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Agents;
using Microsoft.SemanticKernel.Agents.Chat;
using Microsoft.SemanticKernel.ChatCompletion;
using SemanticKernelDemo.Agents;
using SemanticKernelDemo.Models;

namespace SemanticKernelDemo.Services;

/// <summary>
/// 沟通桥的核心服务：以 sessionId 维护多 Agent 协作会话，供 HTTP 层调用。
/// 会话按 ID 隔离，每个会话拥有独立的对话历史与团队状态。
/// </summary>
public sealed class AgentChatService
{
    /// <summary>协作终止的上限轮数，防止无限循环。</summary>
    private const int MaxIterations = 10;

    private const string PlannerInstructions = """
        你是总规划师（Orchestrator）。你的职责是协调团队完成用户任务。
        规则：
        1. 收到任务后，把任务拆解，并动态分配给合适的团队成员。团队成员没有固定职责，由你按任务灵活指定。
        2. 每次只响应一个成员的名字，表示让该成员发言。
        3. 当任务已完成、或所有成员都已发言完毕时，回复 DONE，然后由你汇总最终答案。
        """;

    private const string WorkerInstructions = "你是一名协作团队成员。当轮到你做任务时，认真完成，回答要简洁、准确。";

    private readonly Kernel _kernel;
    private readonly ConcurrentDictionary<string, AgentGroupChat> _sessions = new();

    public AgentChatService(Kernel kernel)
    {
        _kernel = kernel;
    }

    /// <summary>处理一次用户消息，返回 Agent 协作的最终答案与完整过程。</summary>
    public async Task<ChatResponse> ChatAsync(string sessionId, string message, CancellationToken ct)
    {
        var turns = new List<ChatTurn>();
        await foreach (var turn in StreamChatAsync(sessionId, message, ct))
        {
            turns.Add(turn);
        }

        var final = turns.LastOrDefault()?.Content ?? string.Empty;
        return new ChatResponse(sessionId, final, turns);
    }

    /// <summary>
    /// 流式处理一次用户消息：逐个产出每个 Agent 的发言，供 SSE/流式输出使用。
    /// </summary>
    public async IAsyncEnumerable<ChatTurn> StreamChatAsync(
        string sessionId,
        string message,
        [EnumeratorCancellation] CancellationToken ct)
    {
        var groupChat = _sessions.GetOrAdd(sessionId, _ => BuildGroupChat());

        groupChat.AddChatMessage(new ChatMessageContent(AuthorRole.User, message));

        await foreach (var msg in groupChat.InvokeAsync(ct))
        {
            yield return new ChatTurn(msg.AuthorName ?? "Agent", msg.Content ?? string.Empty);
        }
    }

    /// <summary>删除指定会话，释放其历史。</summary>
    public bool DeleteSession(string sessionId) => _sessions.TryRemove(sessionId, out _);

    /// <summary>当前存活会话数。</summary>
    public int SessionCount => _sessions.Count;

    private AgentGroupChat BuildGroupChat()
    {
        var planner = new ChatCompletionAgent
        {
            Name = AgentNames.Planner,
            Instructions = PlannerInstructions,
            Kernel = _kernel,
        };

        var workers = AgentNames.Workers
            .Select(name => new ChatCompletionAgent
            {
                Name = name,
                Instructions = WorkerInstructions,
                Kernel = _kernel,
            })
            .ToList();

        var groupChat = new AgentGroupChat();
        groupChat.AddAgent(planner);
        foreach (var worker in workers)
        {
            groupChat.AddAgent(worker);
        }

        groupChat.ExecutionSettings = new AgentGroupChatSettings
        {
            SelectionStrategy = new PlannerSelectionStrategy(
                planner: planner,
                fallback: workers[0],
                plannerInstructions: PlannerInstructions),
            TerminationStrategy = new PlannerTerminationStrategy(AgentNames.Planner)
            {
                MaximumIterations = MaxIterations,
            },
        };

        return groupChat;
    }
}