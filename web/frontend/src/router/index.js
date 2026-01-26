import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: DashboardView
    },
    {
      path: '/news',
      name: 'news',
      component: () => import('../views/NewsView.vue')
    },
    {
      path: '/analysis',
      name: 'analysis',
      component: () => import('../views/AnalysisView.vue')
    },
    {
      path: '/configuration',
      name: 'configuration',
      component: () => import('../views/ConfigurationView.vue')
    },
    {
      path: '/trading',
      name: 'trading',
      component: () => import('../views/TradingView.vue')
    },
    {
      path: '/backtester',
      name: 'backtester',
      component: () => import('../views/BacktesterView.vue')
    }
  ]
})

export default router
