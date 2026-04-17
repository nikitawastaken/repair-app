import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import ClientView from '../views/ClientView.vue'
import MasterBoardView from '../views/MasterBoardView.vue'
import MasterMyTicketsView from '../views/MasterMyTicketsView.vue'
import AdminView from '../views/AdminView.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { requiresAuth: false },
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterView,
    meta: { requiresAuth: false },
  },
  {
    path: '/client',
    name: 'ClientView',
    component: ClientView,
    meta: { requiresAuth: true, requiredRoles: ['client'] },
  },
  {
    path: '/master/board',
    name: 'MasterBoard',
    component: MasterBoardView,
    meta: { requiresAuth: true, requiredRoles: ['master', 'admin'] },
  },
  {
    path: '/master/my-tickets',
    name: 'MasterMyTickets',
    component: MasterMyTicketsView,
    meta: { requiresAuth: true, requiredRoles: ['master', 'admin'] },
  },
  {
    path: '/master',
    redirect: '/master/board',
  },
  {
    path: '/admin',
    name: 'AdminView',
    component: AdminView,
    meta: { requiresAuth: true, requiredRoles: ['admin'] },
  },
  {
    path: '/',
    redirect: () => {
      const auth = useAuthStore()
      if (!auth.isLoggedIn) return '/login'

      // Редиректим в зависимости от роли
      const role = auth.user?.role
      if (role === 'admin') return '/admin'
      if (role === 'master') return '/master/board'
      return '/client'
    },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Глобальный guard для проверки прав доступа
router.beforeEach((to, from, next) => {
  const auth = useAuthStore()

  // Проверка аутентификации
  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    return next('/login')
  }

  // Проверка ролей
  if (to.meta.requiredRoles && auth.user) {
    const userRole = auth.user.role
    if (!to.meta.requiredRoles.includes(userRole)) {
      // Редиректим на подходящую страницу
      if (userRole === 'admin') return next('/admin')
      if (userRole === 'master') return next('/master/board')
      return next('/client')
    }
  }

  // Редирект авторизованных со страниц логина
  if ((to.path === '/login' || to.path === '/register') && auth.isLoggedIn) {
    const role = auth.user?.role
    if (role === 'admin') return next('/admin')
    if (role === 'master') return next('/master/board')
    return next('/client')
  }

  next()
})

export default router
