import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

/**
 * Store заявок.
 * Управляет операциями с заявками для трёх типов пользователей.
 *
 * API эндпоинты:
 * - GET /tickets - получить заявки (фильтрация на backend)
 * - POST /tickets - создать заявку
 * - PATCH /tickets/{id}/take - мастер берёт заявку
 * - PATCH /tickets/{id}/abandon - мастер отказывается от заявки
 * - PATCH /tickets/{id}/done - мастер завершает заявку
 * - PATCH /tickets/{id}/cancel - клиент отзывает заявку
 * - DELETE /admin/tickets/{id} - админ удаляет заявку (используется в AdminView)
 */
export const useTicketsStore = defineStore('tickets', () => {
  const tickets = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function fetchTickets(params = {}) {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('/tickets', { params })
      tickets.value = response.data || []
    } catch (err) {
      error.value = err.response?.data?.detail || 'Ошибка загрузки заявок'
      tickets.value = []
    } finally {
      loading.value = false
    }
  }

  async function createTicket(ticketData) {
    error.value = null
    try {
      const response = await api.post('/tickets', ticketData)
      tickets.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Ошибка создания заявки'
      throw err
    }
  }

  async function takeTicket(ticketId) {
    error.value = null
    try {
      const response = await api.patch(`/tickets/${ticketId}/take`)
      const index = tickets.value.findIndex((t) => t.id === ticketId)
      if (index !== -1) {
        tickets.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Ошибка при принятии заявки'
      throw err
    }
  }

  async function abandonTicket(ticketId) {
    error.value = null
    try {
      const response = await api.patch(`/tickets/${ticketId}/abandon`)
      const index = tickets.value.findIndex((t) => t.id === ticketId)
      if (index !== -1) {
        tickets.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Ошибка при отказе от заявки'
      throw err
    }
  }

  async function completeTicket(ticketId) {
    error.value = null
    try {
      const response = await api.patch(`/tickets/${ticketId}/done`)
      const index = tickets.value.findIndex((t) => t.id === ticketId)
      if (index !== -1) {
        tickets.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Ошибка при завершении заявки'
      throw err
    }
  }

  async function cancelTicket(ticketId) {
    error.value = null
    try {
      const response = await api.patch(`/tickets/${ticketId}/cancel`)
      const index = tickets.value.findIndex((t) => t.id === ticketId)
      if (index !== -1) {
        tickets.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Ошибка при отзыве заявки'
      throw err
    }
  }

  return {
    tickets,
    loading,
    error,
    fetchTickets,
    createTicket,
    takeTicket,
    abandonTicket,
    completeTicket,
    cancelTicket,
  }
})
