<template>
  <div class="admin-view">
    <div class="container">
      <h1>👨‍💼 Панель администратора</h1>

      <div class="admin-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.value"
          @click="activeTab = tab.value"
          :class="['tab-btn', { active: activeTab === tab.value }]"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Вкладка "Все заявки" -->
      <div v-if="activeTab === 'tickets'" class="tab-content">
        <h2>Все заявки</h2>

        <div v-if="ticketsStore.loading" class="loading">
          <p>⏳ Загрузка заявок...</p>
        </div>

        <div v-else>
          <div v-if="ticketsStore.tickets.length === 0" class="no-data">
            <p>📭 Заявок не найдено</p>
          </div>

          <div v-else class="tickets-table-wrapper">
            <table class="table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Название</th>
                  <th>Категория</th>
                  <th>Цена</th>
                  <th>Статус</th>
                  <th>Клиент</th>
                  <th>Мастер</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="ticket in ticketsStore.tickets" :key="ticket.id">
                  <td class="cell-id">#{{ ticket.id }}</td>
                  <td class="cell-title">
                    <strong>{{ ticket.title }}</strong>
                  </td>
                  <td>{{ ticket.category }}</td>
                  <td class="cell-price">{{ ticket.price }} ₽</td>
                  <td>
                    <span class="status-badge" :class="`status-${ticket.status}`">
                      {{ getStatusLabel(ticket.status) }}
                    </span>
                  </td>
                  <td class="cell-id">ID: {{ ticket.client_id }}</td>
                  <td class="cell-id">{{ ticket.master_id ? `ID: ${ticket.master_id}` : '—' }}</td>
                  <td class="cell-actions">
                    <button
                      @click="deleteTicket(ticket.id)"
                      class="btn btn-danger btn-sm"
                      :disabled="deletingId === ticket.id"
                    >
                      {{ deletingId === ticket.id ? '⏳' : '🗑️ Удалить' }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-if="ticketsStore.error" class="alert alert-error">
            <strong>Ошибка:</strong> {{ ticketsStore.error }}
          </div>
        </div>
      </div>

      <!-- Вкладка "Пользователи" -->
      <div v-if="activeTab === 'users'" class="tab-content">
        <h2>Управление пользователями</h2>

        <div v-if="usersLoading" class="loading">
          <p>⏳ Загрузка пользователей...</p>
        </div>

        <div v-else>
          <div v-if="users.length === 0" class="no-data">
            <p>📭 Пользователей не найдено</p>
          </div>

          <div v-else class="users-table-wrapper">
            <table class="table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Email</th>
                  <th>Имя</th>
                  <th>Роль</th>
                  <th>Статус</th>
                  <th>Регистрация</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in users" :key="user.id" :class="{ 'row-blocked': user.is_blocked }">
                  <td class="cell-id">#{{ user.id }}</td>
                  <td class="cell-email">{{ user.email }}</td>
                  <td>{{ user.full_name }}</td>
                  <td>
                    <span class="role-badge" :class="`role-${user.role}`">
                      {{ getRoleLabel(user.role) }}
                    </span>
                  </td>
                  <td>
                    <span v-if="user.is_blocked" class="status-blocked">🔒 Заблокирован</span>
                    <span v-else class="status-active">✅ Активен</span>
                  </td>
                  <td class="cell-date">{{ formatDate(user.created_at) }}</td>
                  <td class="cell-actions">
                    <button
                      @click="toggleBlockUser(user.id)"
                      :class="['btn', user.is_blocked ? 'btn-success' : 'btn-warning', 'btn-sm']"
                      :disabled="blockingId === user.id"
                    >
                      {{
                        blockingId === user.id
                          ? '⏳'
                          : user.is_blocked
                            ? '🔓 Разблокировать'
                            : '🔒 Заблокировать'
                      }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-if="usersError" class="alert alert-error">
            <strong>Ошибка:</strong> {{ usersError }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useTicketsStore } from '../stores/tickets'
import api from '../api'

const ticketsStore = useTicketsStore()

const activeTab = ref('tickets')
const users = ref([])
const usersLoading = ref(false)
const usersError = ref(null)
const deletingId = ref(null)
const blockingId = ref(null)

const tabs = [
  { label: '📋 Все заявки', value: 'tickets' },
  { label: '👥 Пользователи', value: 'users' },
]

onMounted(async () => {
  await ticketsStore.fetchTickets()
})

// Загружаем пользователей при переходе на вкладку
watch(
  () => activeTab.value,
  async (newTab) => {
    if (newTab === 'users') {
      await loadUsers()
    }
  }
)

async function loadUsers() {
  usersLoading.value = true
  usersError.value = null
  try {
    const response = await api.get('/admin/users')
    users.value = response.data
  } catch (err) {
    usersError.value = err.response?.data?.detail || 'Ошибка при загрузке пользователей'
  } finally {
    usersLoading.value = false
  }
}

async function deleteTicket(ticketId) {
  if (!confirm('Вы уверены? Это действие невозможно отменить.')) return

  deletingId.value = ticketId
  try {
    await api.delete(`/admin/tickets/${ticketId}`)
    await ticketsStore.fetchTickets()
  } catch (err) {
    alert(err.response?.data?.detail || 'Ошибка при удалении заявки')
  } finally {
    deletingId.value = null
  }
}

async function toggleBlockUser(userId) {
  const user = users.value.find((u) => u.id === userId)
  const action = user.is_blocked ? 'разблокировать' : 'заблокировать'

  if (!confirm(`Вы действительно хотите ${action} этого пользователя?`)) return

  blockingId.value = userId
  try {
    await api.patch(`/admin/users/${userId}/block`)
    await loadUsers()
  } catch (err) {
    alert(err.response?.data?.detail || `Ошибка при ${action} пользователя`)
  } finally {
    blockingId.value = null
  }
}

function getStatusLabel(status) {
  const labels = {
    new: '🟢 Новая',
    in_progress: '🔵 В работе',
    done: '✅ Завершена',
    cancelled: '❌ Отменена',
  }
  return labels[status] || status
}

function getRoleLabel(role) {
  const labels = {
    admin: '👨‍💼 Администратор',
    master: '🔧 Мастер',
    client: '👤 Клиент',
  }
  return labels[role] || role
}

function formatDate(dateString) {
  if (!dateString) return '—'
  const date = new Date(dateString)
  return date.toLocaleString('ru-RU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}
</script>

<style scoped>
.admin-view {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  padding: 30px 20px;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
}

h1 {
  color: white;
  margin-bottom: 30px;
  font-size: 32px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

h2 {
  color: #2c3e50;
  margin: 0 0 20px 0;
  font-size: 20px;
}

.admin-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 25px;
  background: white;
  padding: 10px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.tab-btn {
  flex: 1;
  padding: 12px 20px;
  border: none;
  background-color: #ecf0f1;
  color: #2c3e50;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.tab-btn.active {
  background-color: #667eea;
  color: white;
}

.tab-btn:hover {
  background-color: #bdc3c7;
}

.tab-btn.active:hover {
  background-color: #5568d3;
}

.tab-content {
  background: white;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.loading {
  text-align: center;
  padding: 50px 20px;
  color: #7f8c8d;
  font-size: 16px;
}

.no-data {
  text-align: center;
  padding: 60px 20px;
  background: #f8f9fa;
  border-radius: 8px;
  color: #95a5a6;
}

.tickets-table-wrapper,
.users-table-wrapper {
  overflow-x: auto;
}

.table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.table th {
  background-color: #f5f7fa;
  padding: 12px;
  text-align: left;
  font-weight: bold;
  border-bottom: 2px solid #ddd;
  color: #2c3e50;
}

.table td {
  padding: 12px;
  border-bottom: 1px solid #ecf0f1;
  vertical-align: middle;
}

.table tbody tr {
  transition: background-color 0.2s ease;
}

.table tbody tr:hover {
  background-color: #f8f9fa;
}

.row-blocked {
  background-color: #fff5f5;
}

.cell-id {
  color: #7f8c8d;
  font-weight: 600;
}

.cell-title {
  max-width: 200px;
  word-break: break-word;
}

.cell-price {
  color: #27ae60;
  font-weight: bold;
}

.cell-email {
  word-break: break-word;
}

.cell-date {
  white-space: nowrap;
  color: #95a5a6;
  font-size: 12px;
}

.cell-actions {
  display: flex;
  gap: 5px;
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: bold;
  white-space: nowrap;
}

.status-new {
  background-color: #d4edda;
  color: #155724;
}

.status-in_progress {
  background-color: #cce5ff;
  color: #004085;
}

.status-done {
  background-color: #d4edda;
  color: #155724;
}

.status-cancelled {
  background-color: #f8d7da;
  color: #721c24;
}

.role-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: bold;
  white-space: nowrap;
}

.role-admin {
  background-color: #e2e3e5;
  color: #383d41;
}

.role-master {
  background-color: #cfe2ff;
  color: #084298;
}

.role-client {
  background-color: #d1e7dd;
  color: #0a3622;
}

.status-blocked {
  color: #d32f2f;
  font-weight: bold;
  font-size: 12px;
}

.status-active {
  color: #27ae60;
  font-weight: bold;
  font-size: 12px;
}

.btn {
  padding: 6px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 11px;
  font-weight: bold;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn-sm {
  padding: 5px 8px;
  font-size: 10px;
}

.btn-danger {
  background-color: #e74c3c;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background-color: #c0392b;
}

.btn-success {
  background-color: #27ae60;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background-color: #229954;
}

.btn-warning {
  background-color: #f39c12;
  color: white;
}

.btn-warning:hover:not(:disabled) {
  background-color: #e67e22;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.alert {
  padding: 15px;
  border-radius: 8px;
  margin-top: 20px;
}

.alert-error {
  background-color: #ffebee;
  color: #d32f2f;
  border: 1px solid #ef5350;
}

@media (max-width: 768px) {
  .table {
    font-size: 11px;
  }

  .table th,
  .table td {
    padding: 8px;
  }

  .cell-title {
    max-width: 100px;
  }

  .btn {
    padding: 4px 6px;
    font-size: 9px;
  }
}

.alert-error {
  margin-top: 15px;
  font-size: 14px;
  background-color: #ffebee;
  color: #d32f2f;
  border: 1px solid #ef5350;
}
</style>
