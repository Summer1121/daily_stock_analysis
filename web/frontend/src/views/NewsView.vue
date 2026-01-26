<template>
  <div>
    <h1>Real-time News</h1>
    <div v-for="(stock_news, stock_code) in news" :key="stock_code">
      <h2>{{ stock_code }}</h2>
      <ul>
        <li v-for="(item, index) in stock_news.results" :key="index">
          <a :href="item.url" target="_blank">{{ item.title }}</a>
          <p>{{ item.snippet }}</p>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const news = ref({})
let socket = null

onMounted(() => {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const host = window.location.host
  socket = new WebSocket(`${protocol}//${host}/api/news/ws`)

  socket.onmessage = (event) => {
    news.value = JSON.parse(event.data)
  }
})

onUnmounted(() => {
  if (socket) {
    socket.close()
  }
})
</script>
