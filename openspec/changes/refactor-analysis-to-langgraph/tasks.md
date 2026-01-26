## 1. 准备工作
- [ ] 1.1 在 `requirements.txt` 中添加 `langgraph` 和 `langchain-core`。

## 2. 核心实现
- [ ] 2.1 在 `analysis/orchestrator.py` 中定义 `AgentState` 类。
- [ ] 2.2 实现 `search_node` 包装函数。
- [ ] 2.3 实现 `summarize_node` 包装函数。
- [ ] 2.4 实现 `decision_node` 包装函数。
- [ ] 2.5 重构 `LLMOrchestrator.__init__` 以构建并编译 `StateGraph`。

## 3. 集成与测试
- [ ] 3.1 更新 `LLMOrchestrator.analyze` 方法以调用图并返回 `AnalysisResult`。
- [ ] 3.2 验证 `analyze` 方法的输出是否符合调用方的预期格式（保持向下兼容）。
- [ ] 3.3 运行现有测试确保没有回归错误。