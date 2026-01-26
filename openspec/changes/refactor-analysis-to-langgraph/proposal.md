# Change: 将分析编排重构为 LangGraph

## Why
目前的 `LLMOrchestrator` 使用线性、命令式的 Python 脚本来协调 Agent。这种方法有几个局限性：
1. **灵活性不足**：难以添加循环（例如：“研究 -> 摘要 -> 决策 -> 需要更多信息 -> 重新研究”）。
2. **状态管理困难**：上下文通过字典（dict）随意传递，难以追踪状态变化或实现执行持久化。
3. **可观测性差**：如果不使用外部日志工具，很难可视化或追踪决策流。
4. **面向未来**：后续功能如“人机交互确认”（用于交易审批）和“自动交易”需要系统能够暂停和恢复执行，而 LangGraph 原生支持这些特性。

## What Changes
- **重构 `LLMOrchestrator`**：将线性执行逻辑替换为 `langgraph.StateGraph`。
- **定义 State**：引入正式的 `AgentState` (TypedDict) 来管理节点间共享的数据（消息、技术面数据、分析结果）。
- **节点化 (Node-ification)**：将现有的 `SearchService`、`SummarizerAgent` 和 `DecisionAgent` 的调用封装成图节点。
- **依赖项**：在 `requirements.txt` 中添加 `langgraph` 和 `langchain-core`。

## Impact
- **受影响的 Specs**：新增 `analysis-workflow` 能力。
- **受影响的代码**：
    - `analysis/orchestrator.py` (重大重构)
    - `requirements.txt` (新增依赖)
    - 现有的 Agent (`SummarizerAgent`, `DecisionAgent`) 保持逻辑不变，但调用方式会改变。