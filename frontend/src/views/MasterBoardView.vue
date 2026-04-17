<template>
  <div class="master-board">
    <div class="container">
      <h1>Доска открытых заявок</h1>

      <div class="filters-section">
        <h3>Фильтры и поиск</h3>
        <div class="filters-grid">
          <div class="filter-group">
            <label for="search">Поиск</label>
            <input
              id="search"
              v-model="filters.search"
              type="text"
              placeholder="Ищите по названию или описанию..."
              @input="applyFilters"
            />
          </div>

          <div class="filter-group">
            <label for="category">Категория</label>
            <select id="category" v-model="filters.category" @change="applyFilters">
              <option value="">Все категории</option>
              <option>Сантехника</option>
              <option>Электрика</option>
              <option>Мебель</option>
              <option>Бытовая техника</option>
              <option>Отделка</option>
            </select>
          </div>

          <div class="filter-group">
            <label for="min_price">Мин. цена</label>
            <input
              id="min_price"
              v-model.number="filters.min_price"
              type="number"
              placeholder="От"
              @input="applyFilters"
            />
          </div>

          <div class="filter-group">
            <label for="max_price">Макс. цена</label>
            <input
              id="max_price"
              v-model.number="filters.max_price"
              type="number"
              placeholder="До"
              @input="applyFilters"
            />
          </div>

          <div class="filter-group">
            <label for="sort_by">Сортировка</label>
            <select id="sort_by" v-model="filters.sort_by" @change="applyFilters">
              <option value="created_at">По дате (новые первыми)</option>
              <option value="price">По цене (возрастание)</option>
              <option value="price_desc">По цене (убывание)</option>
            </select>
          </div>

          <button class="btn btn-light" @click="resetFilters">🔄 Сбросить</button>
        </div>
      </div>

      <div v-if="ticketsStore.loading" class="loading">
        <p>⏳ Загрузка заявок...</p>
      </div>

      <div v-else>
        <div v-if="filteredTickets.length === 0" class="no-tickets">
          <p>😴 Нет открытых заявок с такими параметрами.</p>
          <p class="hint">Попробуйте изменить фильтры</p>
        </div>

        <div v-else class="tickets-grid">
          <div v-for="ticket in filteredTickets" :key="ticket.id" class="ticket-card">
            <div class="card-header">
              <h3>{{ ticket.title }}</h3>
              <span class="category-badge">{{ ticket.category }}</span>
            </div>

            <div class="card-meta">
              <div class="meta-item">
                <span class="meta-label">💰 Цена:</span>
                <span class="meta-value price">{{ ticket.price }} ₽</span>
              </div>
              <div class="meta-item">
                <span class="meta-label">📍 Адрес:</span>
                <span class="meta-value">{{ ticket.address }}</span>
              </div>
              <div class="meta-item">
                <span class="meta-label">👤 Заказчик:</span>
                <span class="meta-value">ID: {{ ticket.client_id }}</span>
              </div>
            </div>

            <p class="description">{{ truncateText(ticket.description, 150) }}</p>

            <div v-if="ticket.master_id" class="already-taken">
              <p>⚠️ Уже в работе у мастера</p>
            </div>

            <button
              v-else
              @click="takeTicket(ticket.id)"
              class="btn btn-success"
              :disabled="takingId === ticket.id"
            >
              {{ takingId === ticket.id ? '⏳ Принимаю...' : '✓ Взять в работу' }}
            </button>

            <small class="timestamp">📅 {{ formatDate(ticket.created_at) }}</small>
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
const takingId = ref(null)

const filters = ref({
  search: '',
  category: '',
  min_price: null,
  max_price: null,
  sort_by: 'created_at',
})

onMounted(async () => {
  await ticketsStore.fetchTickets()
})

const filteredTickets = computed(() => {
  let tickets = ticketsStore.tickets.filter((t) => t.status === 'new' && !t.master_id)

  // Поиск
  if (filters.value.search) {
    const query = filters.value.search.toLowerCase()
    tickets = tickets.filter(
      (t) =>
        t.title.toLowerCase().includes(query) ||
        t.description.toLowerCase().includes(query)
    )
  }

  // Категория
  if (filters.value.category) {
    tickets = tickets.filter((t) => t.category === filters.value.category)
  }

  // Цена
  if (filters.value.min_price !== null && filters.value.min_price > 0) {
    tickets = tickets.filter((t) => t.price >= filters.value.min_price)
  }
  if (filters.value.max_price !== null && filters.value.max_price > 0) {
    tickets = tickets.filter((t) => t.price <= filters.value.max_price)
  }

  // Сортировка
  if (filters.value.sort_by === 'price') {
    tickets.sort((a, b) => a.price - b.price)
  } else if (filters.value.sort_by === 'price_desc') {
    tickets.sort((a, b) => b.price - a.price)
  } else {
    // created_at (новые первыми)
    tickets.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  }

  return tickets
})

function applyFilters() {
  // Фильтры уже применяются через computed property
}

function resetFilters() {
  filters.value = {
    search: '',
    category: '',
    min_price: null,
    max_price: null,
    sort_by: 'created_at',
  }
}

async function takeTicket(ticketId) {
  takingId.value = ticketId
  try {
    await ticketsStore.takeTicket(ticketId)
    await ticketsStore.fetchTickets()
  } finally {
    takingId.value = null
  }
}

function truncateText(text, maxLen) {
  if (!text) return ''
  return text.length > maxLen ? text.substring(0, maxLen) + '...' : text
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
.master-board {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  padding: 30px 20px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  color: white;
  margin-bottom: 30px;
  font-size: 32px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

h3 {
  color: #2c3e50;
  margin: 0 0 15px 0;
  font-size: 16px;
}

.filters-section {
  background: white;
  padding: 25px;
  border-radius: 8px;
  margin-bottom: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 15px;
  align-items: flex-end;
}

.filter-group {
  display: flex;
  flex-direction: column;
}

.filter-group label {
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 5px;
  font-size: 13px;
}

.filter-group input,
.filter-group select {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 13px;
  font-family: inherit;
}

.filter-group input:focus,
.filter-group select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 5px rgba(102, 126, 234, 0.3);
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

.hint {
  margin-top: 10px;
  font-size: 14px;
  color: #bdc3c7;
}

.tickets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.ticket-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  display: flex;
  flex-direction: column;
}

.ticket-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 15px;
}

.card-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 16px;
  flex: 1;
}

.category-badge {
  background: #667eea;
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
  white-space: nowrap;
}

.card-meta {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 15px;
  font-size: 13px;
}

.meta-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.meta-item:last-child {
  margin-bottom: 0;
}

.meta-label {
  color: #7f8c8d;
  font-weight: 600;
}

.meta-value {
  color: #2c3e50;
  text-align: right;
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

.already-taken {
  background: #fff3cd;
  border-left: 3px solid #ffc107;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
  font-size: 13px;
}

.already-taken p {
  margin: 0;
  color: #856404;
}

.btn {
  padding: 10px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  font-weight: bold;
  transition: all 0.2s ease;
  margin-bottom: 10px;
}

.btn-success {
  background-color: #27ae60;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background-color: #229954;
}

.btn-light {
  background-color: #ecf0f1;
  color: #2c3e50;
}

.btn-light:hover {
  background-color: #d5dbdb;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.timestamp {
  color: #95a5a6;
  font-size: 12px;
  margin-top: auto;
  padding-top: 10px;
  border-top: 1px solid #ecf0f1;
  display: block;
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
  .tickets-grid {
    grid-template-columns: 1fr;
  }

  h1 {
    font-size: 24px;
  }

  .filters-grid {
    grid-template-columns: 1fr;
  }
}
</style>
