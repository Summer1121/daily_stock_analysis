## ADDED Requirements

### Requirement: 基于图的编排
系统 SHALL 使用状态图（State Graph）架构来管理分析工作流，确保状态持久化并明确处理步骤之间的转换。

#### Scenario: 成功的线性执行
- **WHEN** 调用 `analyze` 并传入股票上下文
- **THEN** 系统初始化一个 `AgentState` 对象
- **AND THEN** 执行 `SearchNode` 以填充 `raw_news`
- **AND THEN** 执行 `SummarizeNode` 以填充 `news_summary`
- **AND THEN** 执行 `DecisionNode` 以生成 `analysis_result`
- **AND THEN** 返回与旧版本兼容的最终结果

#### Scenario: 鲁棒性处理（缺失工具）
- **GIVEN** `SearchService` 不可用或返回空结果
- **WHEN** 工作流执行 `SearchNode`
- **THEN** 系统应更新状态中的新闻为空，但不抛出异常
- **AND THEN** `SummarizeNode` 应优雅地跳过执行或生成空摘要
- **AND THEN** `DecisionNode` 应仅依据技术面上下文继续执行