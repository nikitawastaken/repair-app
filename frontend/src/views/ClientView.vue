<template>
  <div class="client-view">
    <div class="container">
      <h1>Личный кабинет клиента</h1>

      <TicketForm @ticket-created="onTicketCreated" />

      <div class="tickets-section">
        <h2>Ваши заявки</h2>

        <div v-if="ticketsStore.loading" class="loading">
          <p>⏳ Загрузка заявок...</p>
        </div>

        <div v-else>
          <div v-if="ticketsStore.tickets.length === 0" class="no-tickets">
            <p>У вас пока нет заявок.</p>
            <p class="hint">Создайте новую заявку выше, и мастера смогут её увидеть!</p>
          </div>

          <div v-else class="tickets-grid">
            <div v-for="ticket in ticketsStore.tickets" :key="ticket.id" class="ticket-item">
              <div class="ticket-header">
                <h3>{{ ticket.title }}</h3>
                <span class="status-badge" :class="`status-${ticket.status}`">
                  {{ getStatusLabel(ticket.status) }}
                </span>
              </div>

              <div class="ticket-meta">
                <div class="meta-row">
                  <span class="label">Категория:</span>
                  <span class="value">{{ ticket.category }}</span>
                </div>
                <div class="meta-row">
                  <span class="label">Сумма:</span>
                  <span class="value price">{{ ticket.price }} ₽</span>
                </div>
                <div class="meta-row">
                  <span class="label">Адрес:</span>
                  <span class="value">{{ ticket.address }}</span>
                </div>
              </div>

              <p class="description">{{ ticket.description }}</p>

              <div v-if="ticket.master_id" class="assigned-to">
                <p class="assigned-label">
                  ✓ Мастер в работе (ID: {{ ticket.master_id }})
                </p>
              </div>

              <div class="ticket-actions">
                <button
                  v-if="ticket.status === 'new'"
                  @click="cancelTicket(ticket.id)"
                  class="btn btn-secondary"
                  :disabled="cancelingId === ticket.id"
                >
                  {{ cancelingId === ticket.id ? 'Отзыв...' : 'Отозвать' }}
                </button>
                <span v-else class="status-info">
                  Статус: {{ getStatusDescription(ticket.status) }}
                </span>
              </div>

              <div class="ticket-footer">
                <small class="timestamp">{{ formatDate(ticket.created_at) }}</small>
              </div>
            </div>
          </div>
        </div>

        <div v-if="ticketsStore.error" class="alert alert-error">
          <strong>Ошибка:</strong> {{ ticketsStore.error }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useTicketsStore } from '../stores/tickets'
import TicketForm from '../components/TicketForm.vue'

const ticketsStore = useTicketsStore()
const cancelingId = ref(null)

onMounted(async () => {
  await ticketsStore.fetchTickets()
})

function onTicketCreated() {
  ticketsStore.fetchTickets()
}

async function cancelTicket(ticketId) {
  if (!confirm('Вы уверены? Отменить отзыв невозможно.')) return

  cancelingId.value = ticketId
  try {
    await ticketsStore.cancelTicket(ticketId)
    await ticketsStore.fetchTickets()
  } finally {
    cancelingId.value = null
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

function getStatusDescription(status) {
  const descriptions = {
    in_progress: 'Мастер работает над заявкой',
    done: 'Работа завершена',
    cancelled: 'Заявка отменена',
  }
  return descriptions[status] || ''
}

function formatDate(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('ru-RU', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<style scoped>
.client-view {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 100vh;
  padding: 30px 20px;
}

.container {
  max-width: 900px;
  margin: 0 auto;
}

h1 {
  color: #2c3e50;
  margin-bottom: 30px;
  font-size: 28px;
}

h2 {
  color: #34495e;
  margin: 30px 0 20px 0;
  font-size: 20px;
  border-bottom: 2px solid #3498db;
  padding-bottom: 10px;
}

.loading {
  text-align: center;
  padding: 40px 20px;
  background: white;
  border-radius: 8px;
  color: #7f8c8d;
  font-size: 16px;
}

.no-tickets {
  text-align: center;
  padding: 50px 20px;
  background: white;
  border-radius: 8px;
  color: #95a5a6;
}

.no-tickets p {
  margin: 10px 0;
}

.hint {
  font-size: 14px;
  color: #bdc3c7;
}

.tickets-section {
  margin-top: 30px;
}

.tickets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.ticket-item {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  display: flex;
  flex-direction: column;
}

.ticket-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.ticket-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 15px;
}

.ticket-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 16px;
  flex: 1;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
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

.ticket-meta {
  background-color: #f8f9fa;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 15px;
  font-size: 13px;
}

.meta-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}

.meta-row:last-child {
  margin-bottom: 0;
}

.label {
  color: #7f8c8d;
  font-weight: 600;
}

.value {
  color: #2c3e50;
  word-break: break-word;
}

.price {
  color: #27ae60;
  font-weight: bold;
  font-size: 14px;
}

.description {
  color: #34495e;
  line-height: 1.5;
  margin: 15px 0;
  font-size: 14px;
}

.assigned-to {
  background-color: #e7f3ff;
  border-left: 3px solid #2196F3;
  padding: 10px;
  border-radius: 4px;
  margin: 10px 0;
}

.assigned-label {
  margin: 0;
  color: #0066cc;
  font-size: 13px;
}

.ticket-actions {
  display: flex;
  gap: 10px;
  margin: 15px 0;
  flex-wrap: wrap;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  font-weight: bold;
  transition: all 0.2s ease;
}

.btn-secondary {
  background-color: #e74c3c;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #c0392b;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.status-info {
  color: #95a5a6;
  font-size: 13px;
  font-style: italic;
}

.ticket-footer {
  margin-top: auto;
  padding-top: 15px;
  border-top: 1px solid #ecf0f1;
}

.timestamp {
  color: #95a5a6;
}

.alert {
  padding: 15px;
  border-radius: 4px;
  margin-top: 20px;
}

.alert-error {
  background-color: #ffebee;
  color: #d32f2f;
  border: 1px solid #ef5350;
  border-radius: 8px;
}

@media (max-width: 768px) {
  .tickets-grid {
    grid-template-columns: 1fr;
  }

  h1 {
    font-size: 22px;
  }
}
</style>
