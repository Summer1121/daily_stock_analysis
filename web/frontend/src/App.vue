<template>
  <div class="app-layout">
    <aside class="sidebar">
      <div class="sidebar-brand">
        <span class="sidebar-logo">📈</span>
        <h1 class="sidebar-title">A股分析</h1>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/" class="nav-item" exact-active-class="nav-item--active">
          <span class="nav-icon">📊</span>
          <span>交易看板</span>
        </router-link>
        <router-link to="/news" class="nav-item" exact-active-class="nav-item--active">
          <span class="nav-icon">📰</span>
          <span>实时新闻</span>
        </router-link>
        <router-link to="/analysis" class="nav-item" exact-active-class="nav-item--active">
          <span class="nav-icon">🔍</span>
          <span>分析记录</span>
        </router-link>
        <router-link to="/configuration" class="nav-item" exact-active-class="nav-item--active">
          <span class="nav-icon">⚙️</span>
          <span>系统配置</span>
        </router-link>
        <router-link to="/trading" class="nav-item" exact-active-class="nav-item--active">
          <span class="nav-icon">🕹️</span>
          <span>手动交易</span>
        </router-link>
        <router-link to="/backtester" class="nav-item" exact-active-class="nav-item--active">
          <span class="nav-icon">⏪</span>
          <span>策略回测</span>
        </router-link>
      </nav>
    </aside>
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 220px;
  min-width: 220px;
  background: var(--bg-sidebar);
  color: var(--text-sidebar);
  padding: 1.25rem 0;
  display: flex;
  flex-direction: column;
}

.sidebar-brand {
  padding: 0 1.25rem 1.25rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  margin-bottom: 1rem;
}

.sidebar-logo {
  font-size: 1.75rem;
  display: block;
  margin-bottom: 0.25rem;
}

.sidebar-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-sidebar);
  letter-spacing: 0.02em;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 0 0.75rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.65rem 0.85rem;
  border-radius: var(--radius-sm);
  color: var(--text-sidebar-muted);
  text-decoration: none;
  font-size: 0.95rem;
  transition: background 0.15s, color 0.15s;
}

.nav-item:hover {
  background: var(--bg-sidebar-hover);
  color: var(--text-sidebar);
  text-decoration: none;
}

.nav-item--active {
  background: var(--bg-sidebar-active);
  color: #fff;
  font-weight: 500;
  text-decoration: none;
}

.nav-icon {
  font-size: 1.1rem;
  opacity: 0.9;
}

.main-content {
  flex: 1;
  padding: 1.5rem 2rem;
  overflow-x: hidden;
  min-width: 0;
}

@media (max-width: 768px) {
  .sidebar {
    width: 64px;
    min-width: 64px;
    padding: 0.75rem 0;
  }
  .sidebar-brand,
  .sidebar-title,
  .nav-item span:not(.nav-icon) {
    display: none;
  }
  .sidebar-logo {
    margin: 0;
    text-align: center;
  }
  .nav-item {
    justify-content: center;
    padding: 0.75rem;
  }
  .main-content {
    padding: 1rem;
  }
}
</style>
