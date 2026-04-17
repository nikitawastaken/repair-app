import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'

/**
 * Store аутентификации.
 * Хранит токен и данные пользователя.
 *
 * Роли пользователя:
 * - admin: администратор (может удалять заявки и блокировать пользователей)
 * - master: мастер (может браться за заявки и выполнять их)
 * - client: клиент (может создавать заявки)
 */
export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('access_token') || null)
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const loading = ref(false)
  const error = ref(null)

  const isLoggedIn = computed(() => !!token.value && !!user.value)

  async function register(email, password, fullName, role = 'client') {
    loading.value = true
    error.value = null
    try {
      const response = await api.post('/auth/register', {
        email,
        password,
        full_name: fullName,
        role,
      })
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Ошибка регистрации'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function login(email, password) {
    loading.value = true
    error.value = null
    try {
      const response = await api.post('/auth/login', { email, password })
      const data = response.data

      token.value = data.access_token
      localStorage.setItem('access_token', data.access_token)

      // Загружаем полные данные пользователя
      try {
        const userResponse = await api.get('/auth/me')
        user.value = userResponse.data
        localStorage.setItem('user', JSON.stringify(user.value))
      } catch (err) {
        // Fallback: используем данные из JWT, если /auth/me не работает
        const decoded = JSON.parse(atob(data.access_token.split('.')[1]))
        user.value = { id: parseInt(decoded.sub), email }
        localStorage.setItem('user', JSON.stringify(user.value))
      }

      return data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Ошибка логина'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchUserData() {
    try {
      const userResponse = await api.get('/auth/me')
      user.value = userResponse.data
      localStorage.setItem('user', JSON.stringify(user.value))
    } catch (err) {
      logout()
    }
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    error.value = null
  }

  return {
    token,
    user,
    loading,
    error,
    isLoggedIn,
    register,
    login,
    logout,
    fetchUserData,
  }
})
