<template>
  <div>
    <h1>Trading</h1>
    <div v-if="dashboardData">
      <h2>Account Balance</h2>
      <p>Total Assets: {{ dashboardData.account_balance.total_assets }}</p>
      <p>Available Cash: {{ dashboardData.account_balance.available_cash }}</p>
      
      <h2>Positions</h2>
      <ul>
        <li v-for="position in dashboardData.positions" :key="position.id">
          <p><strong>Stock:</strong> {{ position.stock_code }}</p>
          <p><strong>Quantity:</strong> {{ position.quantity }}</p>
          <p><strong>Cost Price:</strong> {{ position.cost_price }}</p>
          <p><strong>Current Price:</strong> {{ position.current_price }}</p>
          <p><strong>Market Value:</strong> {{ position.market_value }}</p>
        </li>
      </ul>
    </div>
    <div>
      <h2>Strategies</h2>
      <ul>
        <li v-for="strategy in strategies" :key="strategy.name">
          {{ strategy.name }} - {{ strategy.enabled ? 'Enabled' : 'Disabled' }}
          <button @click="toggleStrategy(strategy.name)">Toggle</button>
        </li>
      </ul>
    </div>
    <div>
      <h2>Manual Trade</h2>
      <form @submit.prevent="placeOrder">
        <input v-model="order.stock_code" placeholder="Stock Code" />
        <select v-model="order.direction">
          <option>BUY</option>
          <option>SELL</option>
        </select>
        <input v-model.number="order.quantity" type="number" placeholder="Quantity" />
        <button type="submit">Place Order</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'

const dashboardData = ref(null)
const strategies = ref([])
const order = reactive({
  stock_code: '',
  direction: 'BUY',
  quantity: 100,
})

const fetchDashboard = async () => {
  const response = await fetch('/api/trading/dashboard')
  dashboardData.value = await response.json()
}

const fetchStrategies = async () => {
  const response = await fetch('/api/trading/strategies')
  strategies.value = await response.json()
}

const toggleStrategy = async (name) => {
  await fetch(`/api/trading/strategies/${name}/toggle`, { method: 'POST' })
  await fetchStrategies()
}

const placeOrder = async () => {
  await fetch('/api/trading/order', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(order),
  })
  await fetchDashboard()
}

onMounted(async () => {
  await fetchDashboard()
  await fetchStrategies()
})
</script>
