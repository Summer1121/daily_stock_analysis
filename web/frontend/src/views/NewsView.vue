<template>
  <div class="news-view">
    <h1 class="page-title">实时新闻</h1>
    <p class="page-desc">通过 WebSocket 接收股票相关新闻流，按股票代码分组展示。</p>

    <div v-if="Object.keys(news).length === 0" class="card">
      <div class="empty-state">
        <p>暂无新闻数据，请确保后端已配置搜索 API（如 Tavily、Bocha），并已连接 WebSocket。</p>
      </div>
    </div>

    <div v-else class="news-list">
      <div v-for="(stock_news, stock_code) in news" :key="stock_code" class="card news-card">
        <h2 class="news-card-title">{{ stock_code }}</h2>
        <ul class="news-items">
          <li v-for="(item, index) in stock_news.results" :key="index" class="news-item">
            <a :href="item.url" target="_blank" rel="noopener" class="news-item-link">{{ item.title }}</a>
            <p v-if="item.snippet" class="news-item-snippet">{{ item.snippet }}</p>
          </li>
        </ul>
      </div>
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

<style scoped>
.news-view {
  max-width: 880px;
}

.page-desc {
  color: var(--text-secondary);
  font-size: 0.95rem;
  margin-bottom: 1.5rem;
}

.news-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.news-card-title {
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border);
}

.news-items {
  list-style: none;
}

.news-item {
  padding: 0.6rem 0;
  border-bottom: 1px solid var(--border);
}
.news-item:last-child {
  border-bottom: none;
}

.news-item-link {
  color: var(--accent);
  font-weight: 500;
  text-decoration: none;
}
.news-item-link:hover {
  text-decoration: underline;
}

.news-item-snippet {
  margin-top: 0.35rem;
  font-size: 0.875rem;
  color: var(--text-secondary);
  line-height: 1.5;
}
</style>
