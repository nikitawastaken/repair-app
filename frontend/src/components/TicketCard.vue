<template>
  <div class="ticket-card" :class="`status-${ticket.status}`">
    <div class="ticket-header">
      <h3 class="ticket-title">{{ ticket.title }}</h3>
      <span class="ticket-status-badge" :class="`status-${ticket.status}`">
        {{ getStatusLabel(ticket.status) }}
      </span>
    </div>
    <p class="ticket-description">{{ ticket.description }}</p>
    <div class="ticket-meta">
      <small class="ticket-date">
        Создана: {{ formatDate(ticket.created_at) }}
      </small>
      <small class="ticket-master" v-if="ticket.master_id">
        Мастер: #{{ ticket.master_id }}
      </small>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'

const props = defineProps({
  ticket: {
    type: Object,
    required: true,
  },
})

function getStatusLabel(status) {
  const labels = {
    new: 'Новая',
    in_progress: 'В процессе',
    done: 'Выполнена',
    rejected: 'Отклонена',
  }
  return labels[status] || status
}

function formatDate(dateString) {
  const options = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }
  return new Date(dateString).toLocaleDateString('ru-RU', options)
}
</script>

<style scoped>
.ticket-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  background-color: white;
  transition: box-shadow 0.3s ease;
}

.ticket-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.ticket-card.status-new {
  border-left: 4px solid #3498db;
}

.ticket-card.status-in_progress {
  border-left: 4px solid #f39c12;
}

.ticket-card.status-done {
  border-left: 4px solid #27ae60;
}

.ticket-card.status-rejected {
  border-left: 4px solid #e74c3c;
}

.ticket-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 10px;
}

.ticket-title {
  font-size: 18px;
  font-weight: bold;
  color: #2c3e50;
  margin: 0;
  flex: 1;
}

.ticket-status-badge {
  display: inline-block;
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
  white-space: nowrap;
  margin-left: 10px;
}

.ticket-status-badge.status-new {
  background-color: #e3f2fd;
  color: #1976d2;
}

.ticket-status-badge.status-in_progress {
  background-color: #fff3e0;
  color: #f57c00;
}

.ticket-status-badge.status-done {
  background-color: #e8f5e9;
  color: #388e3c;
}

.ticket-status-badge.status-rejected {
  background-color: #ffebee;
  color: #d32f2f;
}

.ticket-description {
  color: #555;
  font-size: 14px;
  line-height: 1.5;
  margin: 10px 0;
}

.ticket-meta {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #999;
}

.ticket-date,
.ticket-master {
  display: block;
}
</style>
