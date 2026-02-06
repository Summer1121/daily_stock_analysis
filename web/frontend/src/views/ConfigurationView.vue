<template>
  <div class="configuration-view">
    <h1 class="text-2xl font-bold mb-6">系统配置</h1>

    <form @submit.prevent="saveConfig" class="space-y-6">
      <!-- 通用配置 -->
      <section class="config-section">
        <h2 class="text-xl font-semibold mb-4">通用设置</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="form-group">
            <label for="stock_list" class="block text-sm font-medium text-gray-700">自选股列表 (逗号分隔)</label>
            <input type="text" id="stock_list" v-model="config.stock_list" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50">
          </div>
          <div class="form-group">
            <label for="database_path" class="block text-sm font-medium text-gray-700">数据库路径</label>
            <input type="text" id="database_path" v-model="config.database_path" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50">
          </div>
          <div class="form-group">
            <label for="log_dir" class="block text-sm font-medium text-gray-700">日志目录</label>
            <input type="text" id="log_dir" v-model="config.log_dir" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50">
          </div>
          <div class="form-group">
            <label for="log_level" class="block text-sm font-medium text-gray-700">日志级别</label>
            <select id="log_level" v-model="config.log_level" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50">
              <option value="DEBUG">DEBUG</option>
              <option value="INFO">INFO</option>
              <option value="WARNING">WARNING</option>
              <option value="ERROR">ERROR</option>
              <option value="CRITICAL">CRITICAL</option>
            </select>
          </div>
          <div class="form-group flex items-center">
            <input type="checkbox" id="debug" v-model="config.debug" class="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500">
            <label for="debug" class="ml-2 block text-sm font-medium text-gray-700">调试模式</label>
          </div>
        </div>
      </section>

      <!-- 交易与回测配置 -->
      <section class="config-section">
        <h2 class="text-xl font-semibold mb-4">交易与回测设置</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="form-group">
            <label for="trading_mode" class="block text-sm font-medium text-gray-700">交易模式</label>
            <select id="trading_mode" v-model="config.trading_mode" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50">
              <option value="paper">模拟交易 (Paper Trading)</option>
              <option value="live">实盘交易 (Live Trading)</option>
            </select>
          </div>
          <div class="form-group">
            <label for="trading_capital" class="block text-sm font-medium text-gray-700">初始交易资金</label>
            <input type="number" id="trading_capital" v-model.number="config.trading_capital" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50">
          </div>
          <div class="form-group">
            <label for="trading_max_position_per_stock" class="block text-sm font-medium text-gray-700">单股最大持仓金额</label>
            <input type="number" id="trading_max_position_per_stock" v-model.number="config.trading_max_position_per_stock" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50">
          </div>

          <!-- 实盘交易配置 (仅当 trading_mode 为 live 时显示) -->
          <template v-if="config.trading_mode === 'live'">
            <div class="col-span-1 md:col-span-2 mt-4">
              <h3 class="text-lg font-semibold mb-3">实盘交易设置</h3>
            </div>
            
            <div class="form-group">
              <label for="trading_broker" class="block text-sm font-medium text-gray-700">经纪商类型</label>
              <select id="trading_broker" v-model="config.trading_broker" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50">
                <option value="real_api">量化接口 (API)</option>
                <option value="real_ui_automation">模拟人工操作 (UI Automation)</option>
              </select>
            </div>

            <!-- 量化接口配置 (仅当 trading_broker 为 real_api 时显示) -->
            <template v-if="config.trading_broker === 'real_api'">
              <div class="form-group">
                <label for="real_broker_type" class="block text-sm font-medium text-gray-700">具体券商 (API)</label>
                <input type="text" id="real_broker_type" v-model="config.real_broker_type" placeholder="如: guosen, tiger" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50">
              </div>
              <div class="form-group">
                <label for="real_broker_api_key" class="block text-sm font-medium text-gray-700">API Key</label>
                <input type="text" id="real_broker_api_key" v-model="config.real_broker_api_key" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50">
              </div>
              <div class="form-group">
                <label for="real_broker_api_secret" class="block text-sm font-medium text-gray-700">API Secret</label>
                <input type="text" id="real_broker_api_secret" v-model="config.real_broker_api_secret" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50">
              </div>
            </template>

            <!-- UI 自动化配置 (仅当 trading_broker 为 real_ui_automation 时显示) -->
            <template v-if="config.trading_broker === 'real_ui_automation'">
              <div class="form-group">
                <label for="real_broker_type" class="block text-sm font-medium text-gray-700">具体券商/工具 (UI Automation)</label>
                <input type="text" id="real_broker_type" v-model="config.real_broker_type" placeholder="如: ths_web" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50">
              </div>
              <div class="form-group">
                <label for="real_broker_account" class="block text-sm font-medium text-gray-700">交易账号</label>
                <input type="text" id="real_broker_account" v-model="config.real_broker_account" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50">
              </div>
              <div class="form-group">
                <label for="real_broker_password" class="block text-sm font-medium text-gray-700">交易密码</label>
                <input type="password" id="real_broker_password" v-model="config.real_broker_password" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50">
              </div>
              <div class="form-group">
                <label for="ui_automation_browser" class="block text-sm font-medium text-gray-700">自动化浏览器</label>
                <select id="ui_automation_browser" v-model="config.ui_automation_browser" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50">
                  <option value="chrome">Chrome</option>
                  <option value="firefox">Firefox</option>
                  <option value="edge">Edge</option>
                </select>
              </div>
              <div class="form-group flex items-center">
                <input type="checkbox" id="ui_automation_headless" v-model="config.ui_automation_headless" class="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500">
                <label for="ui_automation_headless" class="ml-2 block text-sm font-medium text-gray-700">无头模式运行浏览器</label>
              </div>

              <!-- UI 自动化风险提示 -->
              <div class="col-span-1 md:col-span-2 bg-yellow-50 border-l-4 border-yellow-400 p-4 mt-4">
                <div class="flex">
                  <div class="flex-shrink-0">
                    <svg class="h-5 w-5 text-yellow-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                      <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                    </svg>
                  </div>
                  <div class="ml-3">
                    <h3 class="text-sm font-medium text-yellow-800">风险提示：模拟人工操作 (UI Automation)</h3>
                    <div class="mt-2 text-sm text-yellow-700">
                      <p>通过模拟人工操作进行实盘交易存在**巨大的法律、合规、资金安全和稳定性风险**。这可能违反券商的服务协议、中国证监会的监管规定，并导致账户被封禁、资金损失甚至法律责任。</p>
                      <p class="mt-1">**强烈建议仅在充分理解并接受所有风险的情况下进行技术验证，不应在未经严格测试和合规评估的情况下用于真实资金交易。**</p>
                      <p class="mt-1">系统将不对因使用此功能造成的任何损失负责。</p>
                    </div>
                  </div>
                </div>
              </div>
            </template>
            
            <div class="col-span-1 md:col-span-2">
              <button type="button" @click="testBrokerConnection" class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500">
                测试连接
              </button>
            </div>
          </template>
        </div>
      </section>

      <!-- AI 分析配置 -->
      <section class="config-section">
        <h2 class="text-xl font-semibold mb-4">AI 分析设置</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="form-group">
            <label for="gemini_api_key" class="block text-sm font-medium text-gray-700">Gemini API Key</label>
            <input type="password" id="gemini_api_key" v-model="config.gemini_api_key" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50">
          </div>
          <div class="form-group">
            <label for="gemini_model" class="block text-sm font-medium text-gray-700">Gemini 主模型</label>
            <input type="text" id="gemini_model" v-model="config.gemini_model" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50">
          </div>
          <!-- 更多 AI 配置项 -->
        </div>
      </section>

      <button type="submit" class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
        保存配置
      </button>
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
  trading_broker: 'real_api', // Default for live trading
  real_broker_type: '',
  real_broker_api_key: '',
  real_broker_api_secret: '',
  real_broker_account: '',
  real_broker_password: '',
  ui_automation_browser: 'chrome',
  ui_automation_headless: true,
  gemini_api_key: '',
  gemini_model: 'gemini-3-flash-preview',
  // ... 其他配置项的默认值
})

onMounted(async () => {
  await fetchConfig()
})

const fetchConfig = async () => {
  try {
    const response = await fetch('/api/config')
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const data = await response.json()
    // Flatten stock_list and custom_webhook_urls from array to comma-separated string for input fields
    data.stock_list = Array.isArray(data.stock_list) ? data.stock_list.join(', ') : data.stock_list
    data.custom_webhook_urls = Array.isArray(data.custom_webhook_urls) ? data.custom_webhook_urls.join(', ') : data.custom_webhook_urls
    config.value = data
  } catch (error) {
    console.error("Failed to fetch config:", error)
    // Handle error, maybe show a message to the user
  }
}

const saveConfig = async () => {
  try {
    // Before sending, convert comma-separated strings back to arrays
    const configToSend = { ...config.value };
    if (typeof configToSend.stock_list === 'string') {
        configToSend.stock_list = configToSend.stock_list.split(',').map(s => s.trim()).filter(s => s.length > 0);
    }
    if (typeof configToSend.custom_webhook_urls === 'string') {
        configToSend.custom_webhook_urls = configToSend.custom_webhook_urls.split(',').map(s => s.trim()).filter(s => s.length > 0);
    }

    const response = await fetch('/api/config', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(configToSend),
    })
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    alert('配置保存成功！');
    // Optionally re-fetch config to ensure UI is in sync with backend's interpretation
    await fetchConfig();
  } catch (error) {
    console.error("Failed to save config:", error)
    alert(`配置保存失败: ${error.message}`);
  }
}

const testBrokerConnection = async () => {
  // This function will need a backend API endpoint to test the connection
  alert('测试连接功能待实现。');
  console.log('测试连接配置:', config.value);
  // Example: await fetch('/api/test-broker-connection', { method: 'POST', body: JSON.stringify(config.value) });
}
</script>

<style scoped>
.configuration-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.config-section {
  background-color: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.form-group label {
  color: #374151;
}

.form-group input[type="text"],
.form-group input[type="number"],
.form-group input[type="password"],
.form-group select {
  border-color: #d1d5db;
}

.form-group input[type="checkbox"] {
  border-color: #d1d5db;
}
</style>
