# two-tier-llm-architecture Specification

## Purpose
TBD - created by archiving change add-auto-trading-mechanism. Update Purpose after archive.
## Requirements
### Requirement: 系统必须实现一个双层 Agent 架构，分离信息处理和决策制定。
**说明**: 为了降低对昂贵大模型的 Token 消耗，系统应采用一个“摘要+决策”的两步流程。一个轻量级模型负责前期信息处理，一个强大的模型负责最终决策。

**#### Scenario: 系统需要分析一篇包含大量信息的市场研究报告。**
- `GIVEN` 系统获取了一篇 5000 字的关于某行业的研究报告。
- `WHEN` `Orchestrator` (协调器) 开始处理该信息。
- `THEN` `Orchestrator` 必须首先调用 `SummarizerAgent` (摘要 Agent)。
- `AND` `SummarizerAgent` 使用一个轻量级、低成本的模型将报告压缩成 300 字的结构化要点。
- `AND` `Orchestrator` 随后必须将这些要点（而不是原始报告）连同其他关键数据一起发送给 `DecisionAgent` (决策 Agent) 进行最终分析。

### Requirement: 摘要 Agent 必须是可配置的。
**说明**: 用户应能够根据自己的成本和性能需求，灵活选择用于摘要的轻量级模型。

**#### Scenario: 用户希望使用本地模型进行摘要以节省成本。**
- `GIVEN` 用户已在本地通过 Ollama 部署了 `qwen:7b` 模型。
- `WHEN` 用户在配置文件中设置 `SUMMARIZER_MODEL_TYPE=ollama` 和 `SUMMARIZER_MODEL_NAME=qwen:7b`。
- `THEN` `SummarizerAgent` 在初始化时必须加载并使用本地的 Ollama 模型进行摘要工作。

**#### Scenario: 用户希望使用一个云端的小模型进行摘要。**
- `GIVEN` 用户希望使用 `gemini-3-flash-preview`。
- `WHEN` 用户在配置文件中设置 `SUMMARIZER_MODEL_TYPE=gemini` 和 `SUMMARIZER_MODEL_NAME=gemini-3-flash-preview`。
- `THEN` `SummarizerAgent` 在初始化时必须使用 Google 的 `gemini-3-flash-preview` 模型进行摘要工作。

### Requirement: 决策 Agent 必须接收结构化的输入。
**说明**: 决策 Agent 接收的输入应该是经过预处理的、信息密度高的结构化数据，以保证其决策质量和效率。

**#### Scenario: 决策 Agent 开始一次分析任务。**
- `GIVEN` `SummarizerAgent` 已经处理完所有新闻。
- `WHEN` `Orchestrator` 调用 `DecisionAgent`。
- `THEN` `Orchestrator` 传递给 `DecisionAgent` 的 Prompt 中，必须包含清晰分区的结构化信息，例如：
  ```
  [市场新闻摘要]
  - ...
  [公司公告要点]
  - ...
  [核心量价指标]
  - MA5: 10.5, MA10: 10.2
  ```
- `AND` Prompt 中不应包含未经处理的原始新闻长文本。

