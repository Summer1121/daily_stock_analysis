<template>
  <div>
    <h1>Backtester</h1>
    <form @submit.prevent="runBacktest">
      <div>
        <label for="stock_codes">Stock Codes (comma separated)</label>
        <input id="stock_codes" v-model="backtestRequest.stock_codes" />
      </div>
      <div>
        <label for="start_date">Start Date</label>
        <input id="start_date" type="date" v-model="backtestRequest.start_date" />
      </div>
      <div>
        <label for="end_date">End Date</label>
        <input id="end_date" type="date" v-model="backtestRequest.end_date" />
      </div>
      <div>
        <label for="strategy_name">Strategy</label>
        <select id="strategy_name" v-model="backtestRequest.strategy_name">
          <option v-for="strategy in strategies" :key="strategy.name" :value="strategy.name">
            {{ strategy.name }}
          </option>
        </select>
      </div>
      <button type="submit">Run Backtest</button>
    </form>
    <div v-if="report">
      <h2>Backtest Report</h2>
      <pre>{{ report }}</pre>
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
  const response = await fetch('/api/trading/strategies')
  strategies.value = await response.json()
}

const runBacktest = async () => {
  const requestBody = {
    ...backtestRequest,
    stock_codes: backtestRequest.stock_codes.split(',').map(s => s.trim()),
  }
  const response = await fetch('/api/trading/backtest', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestBody),
  })
  report.value = await response.json()
}

onMounted(fetchStrategies)
</script>
