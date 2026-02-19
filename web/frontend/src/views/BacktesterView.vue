<template>
  <div class="backtester-view">
    <h1 class="page-title">策略回测</h1>
    <p class="page-desc">选择股票、日期范围与策略，在历史数据上评估表现。</p>

    <div class="card form-card">
      <form @submit.prevent="runBacktest" class="backtest-form">
        <div class="form-row">
          <label for="stock_codes" class="label">股票代码（逗号分隔）</label>
          <input id="stock_codes" v-model="backtestRequest.stock_codes" class="input" placeholder="600519, 300750" />
        </div>
        <div class="form-row">
          <label for="start_date" class="label">开始日期</label>
          <input id="start_date" type="date" v-model="backtestRequest.start_date" class="input" />
        </div>
        <div class="form-row">
          <label for="end_date" class="label">结束日期</label>
          <input id="end_date" type="date" v-model="backtestRequest.end_date" class="input" />
        </div>
        <div class="form-row">
          <label for="strategy_name" class="label">策略</label>
          <select id="strategy_name" v-model="backtestRequest.strategy_name" class="input">
            <option v-for="s in strategies" :key="s.name" :value="s.name">{{ s.name }}</option>
          </select>
        </div>
        <button type="submit" class="btn btn-primary">运行回测</button>
      </form>
    </div>

    <div v-if="report" class="card result-card">
      <h2 class="card-heading">回测报告</h2>
      <pre class="report-pre">{{ typeof report === 'object' ? JSON.stringify(report, null, 2) : report }}</pre>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'

const strategies = ref([])
const backtestRequest = reactive({
  stock_codes: '',
  start_date: '',
  end_date: '',
  strategy_name: 'FollowLLMStrategy',
})
const report = ref(null)

const fetchStrategies = async () => {
  const res = await fetch('/api/trading/strategies')
  strategies.value = await res.json()
}

const runBacktest = async () => {
  const body = {
    ...backtestRequest,
    stock_codes: backtestRequest.stock_codes.split(',').map(s => s.trim()).filter(Boolean),
  }
  const res = await fetch('/api/trading/backtest', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  report.value = await res.json()
}

onMounted(fetchStrategies)
</script>

<style scoped>
.backtester-view {
  max-width: 640px;
}

.page-desc {
  color: var(--text-secondary);
  font-size: 0.95rem;
  margin-bottom: 1.5rem;
}

.form-card {
  margin-bottom: 1.5rem;
}

.backtest-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.form-row .label {
  margin-bottom: 0.25rem;
}

.result-card .card-heading {
  font-size: 1.05rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  color: var(--text-primary);
}

.report-pre {
  background: var(--bg-page);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 1rem;
  font-size: 0.875rem;
  line-height: 1.5;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-word;
  color: var(--text-primary);
}
</style>
