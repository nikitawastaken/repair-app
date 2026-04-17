<template>
  <div class="navbar">
    <div class="navbar-content">
      <router-link to="/" class="navbar-title">🔧 Repair App</router-link>

      <div class="navbar-menu">
        <template v-if="auth.isLoggedIn">
          <!-- Навигация для мастера -->
          <div v-if="auth.user?.role === 'master'" class="nav-tabs">
            <router-link
              to="/master/board"
              class="nav-tab"
              :class="{ active: isRouteActive('/master/board') }"
            >
              📋 Доска заявок
            </router-link>
            <router-link
              to="/master/my-tickets"
              class="nav-tab"
              :class="{ active: isRouteActive('/master/my-tickets') }"
            >
              ✓ Мои заявки
            </router-link>
          </div>

          <!-- Навигация для администратора -->
          <div v-if="auth.user?.role === 'admin'" class="nav-tabs">
            <router-link
              to="/admin"
              class="nav-tab"
              :class="{ active: isRouteActive('/admin') }"
            >
              👨‍💼 Управление
            </router-link>
          </div>

          <!-- Навигация для клиента -->
          <div v-if="auth.user?.role === 'client'" class="nav-tabs">
            <router-link
              to="/client"
              class="nav-tab"
              :class="{ active: isRouteActive('/client') }"
            >
              📝 Мои заявки
            </router-link>
          </div>

          <span class="navbar-user">👤 {{ auth.user?.email }}</span>
          <button @click="logout" class="btn btn-danger">🚪 Выход</button>
        </template>

        <template v-else>
          <router-link to="/login" class="btn btn-primary">Вход</router-link>
          <router-link to="/register" class="btn btn-secondary">Регистрация</router-link>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'
import { useRouter, useRoute } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

function logout() {
  auth.logout()
  router.push('/login')
}

function isRouteActive(path) {
  return route.path === path
}
</script>

<style scoped>
.navbar {
  background: linear-gradient(90deg, #2c3e50 0%, #34495e 100%);
  color: white;
  padding: 12px 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  position: sticky;
  top: 0;
  z-index: 100;
}

.navbar-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.navbar-title {
  font-size: 22px;
  font-weight: bold;
  margin: 0;
  color: white;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.navbar-title:hover {
  opacity: 0.8;
}

.navbar-menu {
  display: flex;
  gap: 20px;
  align-items: center;
  flex: 1;
  justify-content: flex-end;
}

.nav-tabs {
  display: flex;
  gap: 10px;
  align-items: center;
}

.nav-tab {
  padding: 8px 16px;
  text-decoration: none;
  color: white;
  border-radius: 4px;
  transition: all 0.3s ease;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid transparent;
}

.nav-tab:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.nav-tab.active {
  background-color: #3498db;
  border-color: #2980b9;
  font-weight: bold;
}

.navbar-user {
  font-size: 13px;
  color: #ecf0f1;
  white-space: nowrap;
}

.btn {
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
  font-size: 13px;
  transition: all 0.3s ease;
  white-space: nowrap;
  font-weight: 500;
}

.btn-primary {
  background-color: #3498db;
  color: white;
}

.btn-primary:hover {
  background-color: #2980b9;
}

.btn-secondary {
  background-color: #95a5a6;
  color: white;
}

.btn-secondary:hover {
  background-color: #7f8c8d;
}

.btn-danger {
  background-color: #e74c3c;
  color: white;
}

.btn-danger:hover {
  background-color: #c0392b;
}

@media (max-width: 768px) {
  .navbar-content {
    flex-direction: column;
    gap: 10px;
  }

  .navbar-menu {
    justify-content: space-between;
    width: 100%;
  }

  .nav-tabs {
    flex-direction: column;
    width: 100%;
  }

  .nav-tab {
    text-align: center;
  }
}
</style>
