<template>
  <div class="analysis-view">
    <h1 class="page-title">分析记录</h1>
    <p class="page-desc">输入股票代码（6 位 A 股或 hk + 5 位港股）查询历史分析记录。</p>

    <div class="card form-card">
      <form @submit.prevent="fetchAnalysis" class="analysis-form">
        <div class="form-row">
          <label for="stock-code" class="label">股票代码</label>
          <input
            id="stock-code"
            v-model="stockCode"
            type="text"
            class="input"
            placeholder="例如：600519 或 hk00700"
            maxlength="10"
          />
        </div>
        <button type="submit" class="btn btn-primary">查询</button>
      </form>
    </div>

    <div v-if="analysisHistory.length > 0" class="card result-card">
      <h2 class="result-title">{{ stockCode }}</h2>
      <ul class="record-list">
        <li v-for="record in analysisHistory" :key="record.id" class="record-item">
          <div class="record-meta">
            <span class="record-date">日期：{{ record.date }}</span>
            <span class="record-score">评分：{{ record.sentiment_score }}</span>
            <span class="record-advice">建议：{{ record.operation_advice }}</span>
          </div>
          <p class="record-prediction"><strong>走势预测：</strong>{{ record.trend_prediction }}</p>
          <p v-if="record.analysis_summary" class="record-summary"><strong>摘要：</strong>{{ record.analysis_summary }}</p>
        </li>
      </ul>
    </div>

    <div v-else-if="hasSearched && stockCode" class="card">
      <div class="empty-state">未查到该股票的分析记录。</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const stockCode = ref('')
const analysisHistory = ref([])
const hasSearched = ref(false)

const fetchAnalysis = async () => {
  if (!stockCode.value.trim()) return
  hasSearched.value = true
  const response = await fetch(`/api/analysis/${encodeURIComponent(stockCode.value.trim())}`)
  analysisHistory.value = await response.json()
}
</script>

<style scoped>
.analysis-view {
  max-width: 720px;
}

.page-desc {
  color: var(--text-secondary);
  font-size: 0.95rem;
  margin-bottom: 1.5rem;
}

.form-card {
  margin-bottom: 1.5rem;
}

.analysis-form {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 0.75rem;
}

.form-row {
  flex: 1;
  min-width: 200px;
}

.form-row .label {
  margin-bottom: 0.35rem;
}

.result-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--text-primary);
}

.record-list {
  list-style: none;
}

.record-item {
  padding: 1rem 0;
  border-bottom: 1px solid var(--border);
}
.record-item:last-child {
  border-bottom: none;
}

.record-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
}

.record-prediction,
.record-summary {
  font-size: 0.95rem;
  line-height: 1.6;
  color: var(--text-primary);
  margin-top: 0.35rem;
}
</style>
