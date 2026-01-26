<template>
  <div>
    <h1>Analysis History</h1>
    <form @submit.prevent="fetchAnalysis">
      <input v-model="stockCode" placeholder="Enter stock code" />
      <button type="submit">Fetch</button>
    </form>
    <div v-if="analysisHistory.length > 0">
      <h2>{{ stockCode }}</h2>
      <ul>
        <li v-for="record in analysisHistory" :key="record.id">
          <p><strong>Date:</strong> {{ record.date }}</p>
          <p><strong>Score:</strong> {{ record.sentiment_score }}</p>
          <p><strong>Prediction:</strong> {{ record.trend_prediction }}</p>
          <p><strong>Advice:</strong> {{ record.operation_advice }}</p>
          <p><strong>Summary:</strong> {{ record.analysis_summary }}</p>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const stockCode = ref('')
const analysisHistory = ref([])

const fetchAnalysis = async () => {
  if (!stockCode.value) return
  const response = await fetch(`/api/analysis/${stockCode.value}`)
  analysisHistory.value = await response.json()
}
</script>
