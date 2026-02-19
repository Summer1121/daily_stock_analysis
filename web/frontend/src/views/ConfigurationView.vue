<template>
  <div class="configuration-view">
    <h1 class="page-title">系统配置</h1>
    <p class="page-desc">管理自选股、数据路径、交易模式与 AI 等设置。保存后生效。</p>

    <form @submit.prevent="saveConfig" class="config-form">
      <section class="card config-section">
        <h2 class="section-title">通用设置</h2>
        <div class="form-grid">
          <div class="form-group">
            <label for="stock_list" class="label">自选股列表（逗号分隔）</label>
            <input type="text" id="stock_list" v-model="config.stock_list" class="input" placeholder="600519, 300750, 002594" />
          </div>
          <div class="form-group">
            <label for="database_path" class="label">数据库路径</label>
            <input type="text" id="database_path" v-model="config.database_path" class="input" />
          </div>
          <div class="form-group">
            <label for="log_dir" class="label">日志目录</label>
            <input type="text" id="log_dir" v-model="config.log_dir" class="input" />
          </div>
          <div class="form-group">
            <label for="log_level" class="label">日志级别</label>
            <select id="log_level" v-model="config.log_level" class="input">
              <option value="DEBUG">DEBUG</option>
              <option value="INFO">INFO</option>
              <option value="WARNING">WARNING</option>
              <option value="ERROR">ERROR</option>
              <option value="CRITICAL">CRITICAL</option>
            </select>
          </div>
          <div class="form-group form-group-checkbox">
            <input type="checkbox" id="debug" v-model="config.debug" class="input-checkbox" />
            <label for="debug" class="label-inline">调试模式</label>
          </div>
        </div>
      </section>

      <section class="card config-section">
        <h2 class="section-title">交易与回测设置</h2>
        <div class="form-grid">
          <div class="form-group">
            <label for="trading_mode" class="label">交易模式</label>
            <select id="trading_mode" v-model="config.trading_mode" class="input">
              <option value="paper">模拟交易</option>
              <option value="live">实盘交易</option>
            </select>
          </div>
          <div class="form-group">
            <label for="trading_capital" class="label">初始交易资金</label>
            <input type="number" id="trading_capital" v-model.number="config.trading_capital" class="input" />
          </div>
          <div class="form-group">
            <label for="trading_max_position_per_stock" class="label">单股最大持仓金额</label>
            <input type="number" id="trading_max_position_per_stock" v-model.number="config.trading_max_position_per_stock" class="input" />
          </div>

          <template v-if="config.trading_mode === 'live'">
            <div class="form-group form-group-full">
              <h3 class="subsection-title">实盘交易设置</h3>
            </div>
            <div class="form-group">
              <label for="trading_broker" class="label">经纪商类型</label>
              <select id="trading_broker" v-model="config.trading_broker" class="input">
                <option value="real_api">量化接口（API）</option>
                <option value="real_ui_automation">模拟人工操作（UI Automation）</option>
              </select>
            </div>

            <template v-if="config.trading_broker === 'real_api'">
              <div class="form-group">
                <label for="real_broker_type" class="label">具体券商（API）</label>
                <input type="text" id="real_broker_type" v-model="config.real_broker_type" placeholder="如：tiger" class="input" />
              </div>
              <div class="form-group">
                <label for="real_broker_api_key" class="label">API Key</label>
                <input type="text" id="real_broker_api_key" v-model="config.real_broker_api_key" class="input" />
              </div>
              <div class="form-group">
                <label for="real_broker_api_secret" class="label">API Secret</label>
                <input type="text" id="real_broker_api_secret" v-model="config.real_broker_api_secret" class="input" />
              </div>
            </template>

            <template v-if="config.trading_broker === 'real_ui_automation'">
              <div class="form-group">
                <label for="real_broker_type_ui" class="label">具体券商/工具（UI Automation）</label>
                <input type="text" id="real_broker_type_ui" v-model="config.real_broker_type" placeholder="如：ths_web" class="input" />
              </div>
              <div class="form-group">
                <label for="real_broker_account" class="label">交易账号</label>
                <input type="text" id="real_broker_account" v-model="config.real_broker_account" class="input" />
              </div>
              <div class="form-group">
                <label for="real_broker_password" class="label">交易密码</label>
                <input type="password" id="real_broker_password" v-model="config.real_broker_password" class="input" />
              </div>
              <div class="form-group">
                <label for="ui_automation_browser" class="label">自动化浏览器</label>
                <select id="ui_automation_browser" v-model="config.ui_automation_browser" class="input">
                  <option value="chrome">Chrome</option>
                  <option value="firefox">Firefox</option>
                  <option value="edge">Edge</option>
                </select>
              </div>
              <div class="form-group form-group-checkbox">
                <input type="checkbox" id="ui_automation_headless" v-model="config.ui_automation_headless" class="input-checkbox" />
                <label for="ui_automation_headless" class="label-inline">无头模式运行浏览器</label>
              </div>
              <div class="form-group form-group-full">
                <div class="alert alert-warning">
                  <strong>风险提示：</strong>通过模拟人工操作进行实盘交易存在法律、合规与资金安全风险，可能违反券商协议与监管规定。请仅在充分理解风险并完成合规评估后使用，系统不对由此造成的损失负责。
                </div>
              </div>
            </template>
            <div class="form-group form-group-full">
              <button type="button" @click="testBrokerConnection" class="btn btn-secondary">测试连接</button>
            </div>
          </template>
        </div>
      </section>

      <section class="card config-section">
        <h2 class="section-title">AI 分析设置</h2>
        <div class="form-grid">
          <div class="form-group">
            <label for="gemini_api_key" class="label">Gemini API Key</label>
            <input type="password" id="gemini_api_key" v-model="config.gemini_api_key" class="input" />
          </div>
          <div class="form-group">
            <label for="gemini_model" class="label">Gemini 主模型</label>
            <input type="text" id="gemini_model" v-model="config.gemini_model" class="input" placeholder="gemini-3-flash-preview" />
          </div>
        </div>
      </section>

      <button type="submit" class="btn btn-primary">保存配置</button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const config = ref({
  stock_list: '',
  database_path: '',
  log_dir: '',
  log_level: 'INFO',
  debug: false,
  trading_mode: 'paper',
  trading_capital: 100000.0,
  trading_max_position_per_stock: 20000.0,
  trading_broker: 'real_api',
  real_broker_type: '',
  real_broker_api_key: '',
  real_broker_api_secret: '',
  real_broker_account: '',
  real_broker_password: '',
  ui_automation_browser: 'chrome',
  ui_automation_headless: true,
  gemini_api_key: '',
  gemini_model: 'gemini-3-flash-preview',
})

onMounted(async () => {
  await fetchConfig()
})

const fetchConfig = async () => {
  try {
    const response = await fetch('/api/config')
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const data = await response.json()
    data.stock_list = Array.isArray(data.stock_list) ? data.stock_list.join(', ') : (data.stock_list || '')
    data.custom_webhook_urls = Array.isArray(data.custom_webhook_urls) ? data.custom_webhook_urls.join(', ') : (data.custom_webhook_urls || '')
    config.value = data
  } catch (e) {
    console.error('获取配置失败:', e)
  }
}

const saveConfig = async () => {
  try {
    const configToSend = { ...config.value }
    if (typeof configToSend.stock_list === 'string') {
      configToSend.stock_list = configToSend.stock_list.split(',').map(s => s.trim()).filter(Boolean)
    }
    if (typeof configToSend.custom_webhook_urls === 'string') {
      configToSend.custom_webhook_urls = configToSend.custom_webhook_urls.split(',').map(s => s.trim()).filter(Boolean)
    }
    const response = await fetch('/api/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(configToSend),
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    alert('配置保存成功')
    await fetchConfig()
  } catch (e) {
    console.error('保存配置失败:', e)
    alert(`配置保存失败：${e.message}`)
  }
}

const testBrokerConnection = async () => {
  alert('测试连接功能待后端接口实现')
}
</script>

<style scoped>
.configuration-view {
  max-width: 900px;
}

.page-desc {
  color: var(--text-secondary);
  font-size: 0.95rem;
  margin-bottom: 1.5rem;
}

.config-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.config-section {
  padding: 1.25rem 1.5rem;
}

.section-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.subsection-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 0.75rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group-full {
  grid-column: 1 / -1;
}

.form-group-checkbox {
  flex-direction: row;
  align-items: center;
}

.input-checkbox {
  width: auto;
  margin-right: 0.5rem;
}

.label-inline {
  margin-bottom: 0;
}

.alert {
  padding: 0.75rem 1rem;
  border-radius: var(--radius-sm);
  font-size: 0.9rem;
  line-height: 1.5;
}

.alert-warning {
  background: #fff8e6;
  border: 1px solid #ffc107;
  color: #7d5a00;
}
</style>
