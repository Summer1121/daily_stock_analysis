# Spec Delta: `broker-integration`

本规范定义了与交易经纪商（券商）进行交互的统一接口。

## ADDED Requirements

### Requirement: 系统必须提供一个用于与交易经纪商交互的抽象接口。
**说明**: 为了使系统能够支持不同的券商，所有交易操作（如下单、查询）都必须通过一个统一的、抽象的接口进行。

**#### Scenario: 开发者希望为系统添加一个新的真实券商支持。**
-   `GIVEN` 系统中存在一个 `AbstractBroker` 抽象基类。
-   `WHEN` 开发者创建一个新的类（例如 `TigerBroker`），该类继承自 `AbstractBroker` 并实现了所有必需的方法（如 `place_order`, `get_account_balance` 等）。
-   `AND` 用户在配置中将 `TRADING_BROKER` 设置为 `tiger`。
-   `THEN` 交易引擎在运行时能够加载并使用 `TigerBroker` 实例来执行真实的交易操作。

### Requirement: 系统必须实现一个功能完备的模拟经纪商 (Paper Broker) 作为默认选项。
**说明**: 为了确保安全性并提供一个零风险的测试环境，系统必须内置一个模拟经纪商。该经纪商不能执行任何真实的交易，仅在本地数据库中模拟所有操作。

**#### Scenario: 用户首次启用交易功能，未进行任何特殊配置。**
-   `GIVEN` 用户未设置 `TRADING_MODE` 或 `TRADING_BROKER` 环境变量。
-   `WHEN` 交易引擎初始化。
-   `THEN` 系统必须自动加载 `PaperBroker` 作为交易执行器。

**#### Scenario: 用户在模拟模式下完成一笔“买入”交易。**
-   `GIVEN` 系统正在使用 `PaperBroker` 运行。
-   `AND` 交易引擎决定买入 100 股 `600519`。
-   `WHEN` 引擎调用 `PaperBroker` 的 `place_order` 方法。
-   `THEN` `PaperBroker` 必须在数据库的 `orders` 表中创建一条新的订单记录。
-   `AND` `PaperBroker` 必须在数据库的 `positions` 表中增加或更新 `600519` 的持仓记录。
-   `AND` `PaperBroker` 不能向任何外部券商 API 发送任何请求。

### Requirement: 交易经纪商接口必须支持获取账户的资金状况。
**说明**: 交易引擎需要知道当前的可用资金和总资产，以作出正确的决策。

**#### Scenario: 交易引擎在决策前检查账户资金。**
-   `GIVEN` 系统正在运行（无论是模拟或真实模式）。
-   `WHEN` 交易引擎调用当前经纪商实例的 `get_account_balance` 方法。
-   `THEN` 系统必须返回一个包含总资产、可用现金、持仓市值等信息的 `AccountBalance` 对象。

### Requirement: 经纪商的敏感凭证（API Key/Secret）决不能硬编码在代码中。
**说明**: 为了安全，所有敏感信息必须从外部配置（如环境变量）中读取。

**#### Scenario: 开发者在实现一个新的真实券商适配器。**
-   `GIVEN` 开发者正在编写 `RealBroker` 类。
-   `WHEN` 该类需要使用 API Key 进行认证。
-   `THEN` 它必须从配置服务或环境变量（例如 `os.getenv("BROKER_API_KEY")`）中获取该 Key。
-   `AND` 代码中不能出现任何类似 `api_key = "my_secret_key"` 的硬编码字符串。
-   `AND` 相关的文档和示例（`.env.example`）必须清楚地标明该配置的敏感性。