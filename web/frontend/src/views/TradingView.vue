<template>
  <div class="trading-view">
    <h1 class="page-title">手动交易</h1>
    <p class="page-desc">查看账户与持仓，管理策略开关，或手动下单。</p>

    <div v-if="dashboardData" class="cards">
      <div class="card">
        <h2 class="card-heading">账户概览</h2>
        <div class="stat-row">
          <span class="stat-label">总资产</span>
          <span class="stat-value">{{ dashboardData.account_balance?.total_assets ?? '—' }}</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">可用资金</span>
          <span class="stat-value">{{ dashboardData.account_balance?.available_cash ?? '—' }}</span>
        </div>
      </div>

      <div class="card" v-if="dashboardData.positions?.length">
        <h2 class="card-heading">持仓</h2>
        <ul class="position-list">
          <li v-for="position in dashboardData.positions" :key="position.id" class="position-item">
            <div class="position-header">
              <strong>{{ position.stock_code }}</strong>
              <span>数量 {{ position.quantity }} · 成本 {{ position.cost_price }}</span>
            </div>
            <div class="position-detail">
              现价 {{ position.current_price }} · 市值 {{ position.market_value }}
            </div>
          </li>
        </ul>
      </div>
      <div class="card" v-else>
        <h2 class="card-heading">持仓</h2>
        <div class="empty-state">暂无持仓</div>
      </div>

      <div class="card">
        <h2 class="card-heading">策略</h2>
        <ul class="strategy-list">
          <li v-for="strategy in strategies" :key="strategy.name" class="strategy-item">
            <span>{{ strategy.name }}</span>
            <span class="strategy-status">{{ strategy.enabled ? '已启用' : '已禁用' }}</span>
            <button type="button" class="btn btn-secondary btn-sm" @click="toggleStrategy(strategy.name)">切换</button>
          </li>
        </ul>
      </div>

      <div class="card">
        <h2 class="card-heading">手动下单</h2>
        <form @submit.prevent="placeOrder" class="order-form">
          <div class="form-row">
            <label class="label">股票代码</label>
            <input v-model="order.stock_code" class="input" placeholder="如 600519" />
          </div>
          <div class="form-row">
            <label class="label">方向</label>
            <select v-model="order.direction" class="input">
              <option value="BUY">买入</option>
              <option value="SELL">卖出</option>
            </select>
          </div>
          <div class="form-row">
            <label class="label">数量</label>
            <input v-model.number="order.quantity" type="number" class="input" min="1" />
          </div>
          <button type="submit" class="btn btn-primary">提交订单</button>
        </form>
      </div>
    </div>

    <div v-else class="card">
      <div class="empty-state">加载中或暂无交易数据…</div>
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
  const res = await fetch('/api/trading/dashboard')
  dashboardData.value = await res.json()
}

const fetchStrategies = async () => {
  const res = await fetch('/api/trading/strategies')
  strategies.value = await res.json()
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

<style scoped>
.trading-view {
  max-width: 720px;
}

.page-desc {
  color: var(--text-secondary);
  font-size: 0.95rem;
  margin-bottom: 1.5rem;
}

.cards {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.card-heading {
  font-size: 1.05rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  color: var(--text-primary);
}

.stat-row {
  display: flex;
  justify-content: space-between;
  padding: 0.4rem 0;
  font-size: 0.95rem;
}

.stat-label {
  color: var(--text-secondary);
}

.stat-value {
  font-weight: 500;
}

.position-list,
.strategy-list {
  list-style: none;
}

.position-item,
.strategy-item {
  padding: 0.6rem 0;
  border-bottom: 1px solid var(--border);
}
.position-item:last-child,
.strategy-item:last-child {
  border-bottom: none;
}

.position-header {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.position-detail {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-top: 0.25rem;
}

.strategy-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.strategy-status {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.btn-sm {
  padding: 0.35rem 0.75rem;
  font-size: 0.875rem;
  margin-left: auto;
}

.order-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.form-row .label {
  margin-bottom: 0.25rem;
}
</style>
