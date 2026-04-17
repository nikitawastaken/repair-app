<template>
  <div class="master-view">
    <h2>Назначенные мне заявки</h2>

    <div v-if="ticketsStore.loading" class="loading">Загрузка заявок...</div>

    <div v-else>
      <div v-if="ticketsStore.tickets.length === 0" class="no-tickets">
        <p>Вам не назначено ни одной заявки.</p>
      </div>

      <div v-for="ticket in ticketsStore.tickets" :key="ticket.id" class="ticket-item">
        <TicketCard :ticket="ticket" />

        <div class="ticket-actions">
          <select v-model="selectedStatus[ticket.id]" class="select">
            <option value="">Выберите новый статус</option>
            <option value="in_progress" v-if="ticket.status === 'new'">
              Взять в работу
            </option>
            <option value="done" v-if="ticket.status === 'in_progress'">
              Завершить
            </option>
            <option value="rejected" v-if="ticket.status === 'in_progress'">
              Отклонить
            </option>
          </select>

          <button
            @click="updateStatus(ticket.id)"
            :disabled="!selectedStatus[ticket.id]"
            class="btn btn-primary"
          >
            Обновить статус
          </button>

          <div v-if="errors[ticket.id]" class="alert alert-error">
            {{ errors[ticket.id] }}
          </div>
        </div>
      </div>
    </div>

    <div v-if="ticketsStore.error" class="alert alert-error">
      {{ ticketsStore.error }}
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive } from 'vue'
import { useTicketsStore } from '../stores/tickets'
import TicketCard from '../components/TicketCard.vue'

const ticketsStore = useTicketsStore()
const selectedStatus = reactive({})
const errors = reactive({})

onMounted(async () => {
  await ticketsStore.fetchTickets()
})

async function updateStatus(ticketId) {
  const newStatus = selectedStatus[ticketId]
  if (!newStatus) return

  errors[ticketId] = null

  try {
    await ticketsStore.updateTicketStatus(ticketId, newStatus)
    selectedStatus[ticketId] = ''
  } catch (err) {
    errors[ticketId] = ticketsStore.error || 'Ошибка при обновлении статуса'
  }
}
</script>

<style scoped>
.master-view {
  max-width: 900px;
  margin: 0 auto;
}

h2 {
  color: #2c3e50;
  margin-bottom: 20px;
}

.loading {
  text-align: center;
  padding: 20px;
  color: #666;
}

.no-tickets {
  text-align: center;
  padding: 40px 20px;
  background-color: #f5f5f5;
  border-radius: 8px;
  color: #999;
}

.ticket-item {
  margin-bottom: 20px;
}

.ticket-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
  padding: 10px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.select {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.select:focus {
  outline: none;
  border-color: #3498db;
}

.btn {
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: bold;
  transition: all 0.3s ease;
}

.btn-primary {
  background-color: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2980b9;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.alert {
  padding: 10px 15px;
  border-radius: 4px;
  margin-top: 10px;
  font-size: 12px;
}

.alert-error {
  background-color: #ffebee;
  color: #d32f2f;
  border: 1px solid #ef5350;
}
</style>
