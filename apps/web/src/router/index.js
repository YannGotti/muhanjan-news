import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import AdminView from '../views/AdminView.vue'
import StreamView from '../views/StreamView.vue'

const routes = [
  {
    path: '/',
    redirect: () => (localStorage.getItem('mn_token') ? '/admin' : '/login'),
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { public: true, title: 'Вход' },
  },
  {
    path: '/admin',
    name: 'admin',
    component: AdminView,
    meta: { requiresAuth: true, title: 'Панель модерации' },
  },
  {
    path: '/stream',
    name: 'stream',
    component: StreamView,
    meta: { public: true, title: 'Эфирная лента' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const hasToken = Boolean(localStorage.getItem('mn_token'))

  if (to.meta?.requiresAuth && !hasToken) {
    return '/login'
  }

  if (to.path === '/login' && hasToken) {
    return '/admin'
  }

  return true
})

router.afterEach((to) => {
  document.title = `MuhanjanNews · ${to.meta?.title || 'Панель'}`
})

export default router
