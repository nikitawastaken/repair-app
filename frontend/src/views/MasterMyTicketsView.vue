<template>
  <div class="master-my-tickets">
    <div class="container">
      <h1>Мои заявки</h1>

      <div class="tabs">
        <button
          v-for="tab in tabs"
          :key="tab.value"
          @click="activeTab = tab.value"
          :class="['tab-btn', { active: activeTab === tab.value }]"
        >
          {{ tab.label }} ({{ getTicketCount(tab.value) }})
        </button>
      </div>

      <div v-if="ticketsStore.loading" class="loading">
        <p>⏳ Загрузка заявок...</p>
      </div>

      <div v-else>
        <div v-if="filteredTickets.length === 0" class="no-tickets">
          <p v-if="activeTab === 'in_progress'">
            📭 У вас нет активных заявок
          </p>
          <p v-else-if="activeTab === 'done'">
            📭 Вы ещё не завершили ни одну заявку
          </p>
          <p v-else>
            📭 Нет заявок
          </p>
        </div>

        <div v-else class="tickets-list">
          <div v-for="ticket in filteredTickets" :key="ticket.id" class="ticket-item">
            <div class="ticket-main">
              <div class="ticket-content">
                <h3>{{ ticket.title }}</h3>
                <p class="ticket-meta-info">
                  <span class="meta-badge">{{ ticket.category }}</span>
                  <span class="meta-badge price">{{ ticket.price }} ₽</span>
                  <span class="meta-badge">📍 {{ ticket.address }}</span>
                </p>
                <p class="description">{{ ticket.description }}</p>

                <div class="client-info">
                  <small>👤 Заказчик ID: {{ ticket.client_id }}</small>
                </div>
              </div>

              <div class="status-section">
                <span class="status-label">Статус:</span>
                <span class="status-badge" :class="`status-${ticket.status}`">
                  {{ getStatusLabel(ticket.status) }}
                </span>
              </div>
            </div>

            <div class="ticket-actions">
              <div v-if="activeTab === 'in_progress'" class="action-buttons">
                <button
                  @click="completeTicket(ticket.id)"
                  class="btn btn-success"
                  :disabled="actioningId === ticket.id"
                >
                  {{ actioningId === ticket.id ? '⏳ Завершаю...' : '✓ Завершить' }}
                </button>
                <button
                  @click="abandonTicket(ticket.id)"
                  class="btn btn-danger"
                  :disabled="actioningId === ticket.id"
                >
                  {{ actioningId === ticket.id ? '⏳ Отказываю...' : '✕ Отказаться' }}
                </button>
              </div>
              <div v-else class="info-only">
                <small class="timestamp">📅 {{ formatDate(ticket.created_at) }}</small>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="ticketsStore.error" class="alert alert-error">
        <strong>Ошибка:</strong> {{ ticketsStore.error }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import { useTicketsStore } from '../stores/tickets'

const ticketsStore = useTicketsStore()
const activeTab = ref('in_progress')
const actioningId = ref(null)

const tabs = [
  { label: '🔵 В работе', value: 'in_progress' },
  { label: '✅ Завершены', value: 'done' },
]

onMounted(async () => {
  await ticketsStore.fetchTickets({ my_tickets: true })
})

const filteredTickets = computed(() => {
  return ticketsStore.tickets.filter((t) => t.status === activeTab.value)
})

function getTicketCount(status) {
  return ticketsStore.tickets.filter((t) => t.status === status).length
}

function getStatusLabel(status) {
  const labels = {
    in_progress: '🔵 В работе',
    done: '✅ Завершена',
  }
  return labels[status] || status
}

async function completeTicket(ticketId) {
  if (!confirm('Вы уверены, что работа завершена?')) return

  actioningId.value = ticketId
  try {
    await ticketsStore.completeTicket(ticketId)
    await ticketsStore.fetchTickets()
  } finally {
    actioningId.value = null
  }
}

async function abandonTicket(ticketId) {
  if (!confirm('Отказаться от заявки? Её снова смогут взять другие мастера.')) return

  actioningId.value = ticketId
  try {
    await ticketsStore.abandonTicket(ticketId)
    await ticketsStore.fetchTickets()
  } finally {
    actioningId.value = null
  }
}

function formatDate(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('ru-RU', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<style scoped>
.master-my-tickets {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  min-height: 100vh;
  padding: 30px 20px;
}

.container {
  max-width: 900px;
  margin: 0 auto;
}

h1 {
  color: white;
  margin-bottom: 30px;
  font-size: 32px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  background: white;
  padding: 10px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.tab-btn {
  flex: 1;
  padding: 12px 20px;
  border: none;
  border-radius: 4px;
  background-color: #ecf0f1;
  color: #2c3e50;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.tab-btn.active {
  background-color: #3498db;
  color: white;
}

.tab-btn:hover {
  background-color: #bdc3c7;
}

.tab-btn.active:hover {
  background-color: #2980b9;
}

.loading {
  text-align: center;
  padding: 50px 20px;
  background: white;
  border-radius: 8px;
  color: #7f8c8d;
  font-size: 16px;
}

.no-tickets {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 8px;
  color: #95a5a6;
}

.tickets-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.ticket-item {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.ticket-item:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.ticket-main {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 15px;
}

.ticket-content {
  flex: 1;
}

.ticket-content h3 {
  margin: 0 0 10px 0;
  color: #2c3e50;
  font-size: 18px;
}

.ticket-meta-info {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.meta-badge {
  display: inline-block;
  background-color: #ecf0f1;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  color: #34495e;
}

.meta-badge.price {
  background-color: #d5f4e6;
  color: #27ae60;
  font-weight: bold;
}

.description {
  color: #34495e;
  line-height: 1.5;
  margin: 10px 0;
  font-size: 14px;
}

.client-info {
  color: #95a5a6;
  font-size: 13px;
  margin-top: 8px;
}

.status-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  min-width: 120px;
}

.status-label {
  color: #7f8c8d;
  font-size: 12px;
  font-weight: bold;
}

.status-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: bold;
}

.status-in_progress {
  background-color: #cce5ff;
  color: #004085;
}

.status-done {
  background-color: #d4edda;
  color: #155724;
}

.ticket-actions {
  border-top: 1px solid #ecf0f1;
  padding-top: 15px;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.btn {
  flex: 1;
  padding: 10px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  font-weight: bold;
  transition: all 0.2s ease;
}

.btn-success {
  background-color: #27ae60;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background-color: #229954;
}

.btn-danger {
  background-color: #e74c3c;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background-color: #c0392b;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.info-only {
  display: flex;
  justify-content: center;
}

.timestamp {
  color: #95a5a6;
  font-size: 12px;
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
  .ticket-main {
    flex-direction: column;
  }

  .status-section {
    flex-direction: row;
  }

  .action-buttons {
    flex-direction: column;
  }

  h1 {
    font-size: 24px;
  }
}
</style>
