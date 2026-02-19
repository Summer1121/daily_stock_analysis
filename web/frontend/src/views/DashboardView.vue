<template>
  <div class="dashboard-view">
    <h1 class="page-title">交易看板</h1>
    <p class="page-desc">查看持仓、盈亏与汇总。配置自选股后运行分析即可在此查看决策与交易概况。</p>
    <div class="dashboard-cards">
      <div class="card card-welcome">
        <h2 class="card-heading">欢迎使用 A股智能分析系统</h2>
        <p class="card-text">从左侧菜单进入：<strong>实时新闻</strong> 查看股票相关资讯，<strong>分析记录</strong> 查看历史分析结果，<strong>系统配置</strong> 管理自选股与 API，<strong>手动交易</strong> 与 <strong>策略回测</strong> 用于交易与回测功能。</p>
      </div>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.dashboard-view {
  max-width: 900px;
}

.page-desc {
  color: var(--text-secondary);
  font-size: 0.95rem;
  margin-bottom: 1.5rem;
}

.dashboard-cards {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.card-welcome .card-heading {
  font-size: 1.15rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  color: var(--text-primary);
}

.card-text {
  color: var(--text-secondary);
  line-height: 1.7;
  font-size: 0.95rem;
}
</style>
