<template>
  <form @submit.prevent="submitForm" class="ticket-form">
    <h3>Создать новую заявку</h3>

    <div class="form-row">
      <div class="form-group">
        <label for="title">Название заявки *</label>
        <input
          id="title"
          v-model="form.title"
          type="text"
          placeholder="Например: Сломан холодильник"
          required
        />
        <span v-if="errors.title" class="error">{{ errors.title }}</span>
      </div>

      <div class="form-group">
        <label for="category">Категория *</label>
        <select id="category" v-model="form.category" required>
          <option value="">Выберите категорию</option>
          <option>Сантехника</option>
          <option>Электрика</option>
          <option>Мебель</option>
          <option>Бытовая техника</option>
          <option>Отделка</option>
        </select>
        <span v-if="errors.category" class="error">{{ errors.category }}</span>
      </div>
    </div>

    <div class="form-group">
      <label for="description">Описание проблемы *</label>
      <textarea
        id="description"
        v-model="form.description"
        placeholder="Опишите проблему подробнее..."
        rows="4"
        required
      />
      <span v-if="errors.description" class="error">{{ errors.description }}</span>
    </div>

    <div class="form-row">
      <div class="form-group">
        <label for="price">Предложенная сумма (руб.) *</label>
        <input
          id="price"
          v-model.number="form.price"
          type="number"
          placeholder="Например: 2500"
          step="100"
          min="0"
          required
        />
        <span v-if="errors.price" class="error">{{ errors.price }}</span>
      </div>

      <div class="form-group">
        <label for="address">Адрес выполнения *</label>
        <input
          id="address"
          v-model="form.address"
          type="text"
          placeholder="Например: ул. Ленина, 45, кв. 12"
          required
        />
        <span v-if="errors.address" class="error">{{ errors.address }}</span>
      </div>
    </div>

    <button type="submit" class="btn btn-primary" :disabled="loading">
      {{ loading ? 'Создание...' : 'Создать заявку' }}
    </button>

    <div v-if="apiError" class="alert alert-error">
      {{ apiError }}
    </div>
  </form>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useTicketsStore } from '../stores/tickets'

const emit = defineEmits(['ticket-created'])

const ticketsStore = useTicketsStore()
const loading = ref(false)
const apiError = ref(null)

const form = reactive({
  title: '',
  description: '',
  price: null,
  address: '',
  category: '',
})

const errors = reactive({
  title: '',
  description: '',
  price: '',
  address: '',
  category: '',
})

function validateForm() {
  errors.title = ''
  errors.description = ''
  errors.price = ''
  errors.address = ''
  errors.category = ''

  if (!form.title?.trim()) {
    errors.title = 'Название не может быть пустым'
  }

  if (!form.description?.trim()) {
    errors.description = 'Описание не может быть пустым'
  }

  if (!form.price || form.price <= 0) {
    errors.price = 'Цена должна быть больше нуля'
  }

  if (!form.address?.trim()) {
    errors.address = 'Адрес не может быть пустым'
  }

  if (!form.category) {
    errors.category = 'Выберите категорию'
  }

  return !errors.title && !errors.description && !errors.price && !errors.address && !errors.category
}

async function submitForm() {
  if (!validateForm()) return

  loading.value = true
  apiError.value = null

  try {
    const ticket = await ticketsStore.createTicket({
      title: form.title.trim(),
      description: form.description.trim(),
      price: form.price,
      address: form.address.trim(),
      category: form.category,
    })

    form.title = ''
    form.description = ''
    form.price = null
    form.address = ''
    form.category = ''

    emit('ticket-created', ticket)
  } catch (err) {
    apiError.value = ticketsStore.error || 'Ошибка при создании заявки'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.ticket-form {
  background-color: white;
  padding: 25px;
  border-radius: 8px;
  border: 1px solid #ddd;
  margin-bottom: 30px;
}

h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #2c3e50;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: #2c3e50;
  font-size: 14px;
}

input,
textarea,
select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: inherit;
  font-size: 14px;
  box-sizing: border-box;
}

input:focus,
textarea:focus,
select:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 5px rgba(52, 152, 219, 0.3);
}

textarea {
  resize: vertical;
}

.error {
  display: block;
  color: #e74c3c;
  font-size: 12px;
  margin-top: 5px;
}

.btn {
  padding: 12px 24px;
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
  opacity: 0.6;
  cursor: not-allowed;
}

.alert {
  padding: 12px 15px;
  border-radius: 4px;
  margin-top: 15px;
  font-size: 14px;
}

.alert-error {
  background-color: #ffebee;
  color: #d32f2f;
  border: 1px solid #ef5350;
}

@media (max-width: 600px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
