"""
Установка корневого URL API для Vite на основе переменной окружения.
"""
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default {
  install: (app) => {
    app.config.globalProperties.$apiUrl = API_BASE_URL
  },
}
