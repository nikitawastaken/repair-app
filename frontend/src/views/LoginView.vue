<template>
  <div class="login-view">
    <div class="auth-container">
      <h2>Вход</h2>

      <form @submit.prevent="login">
        <div class="form-group">
          <label for="email">Email</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            placeholder="example@repair.ru"
            required
          />
        </div>

        <div class="form-group">
          <label for="password">Пароль</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            placeholder="Введите пароль"
            required
          />
        </div>

        <button type="submit" class="btn btn-primary" :disabled="auth.loading">
          {{ auth.loading ? 'Вход...' : 'Войти' }}
        </button>
      </form>

      <div v-if="auth.error" class="alert alert-error">
        {{ auth.error }}
      </div>

      <div class="auth-links">
        <p>Нет аккаунта? <router-link to="/register">Зарегистрируйтесь</router-link></p>
      </div>

      <div class="test-accounts">
        <h3>Тестовые аккаунты:</h3>
        <table>
          <tr>
            <th>Email</th>
            <th>Пароль</th>
            <th>Роль</th>
          </tr>
          <tr>
            <td>admin@repair.ru</td>
            <td>Admin1234!</td>
            <td>Администратор</td>
          </tr>
          <tr>
            <td>master1@repair.ru</td>
            <td>Master123!</td>
            <td>Мастер</td>
          </tr>
          <tr>
            <td>client1@repair.ru</td>
            <td>Client123!</td>
            <td>Клиент</td>
          </tr>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const form = reactive({
  email: '',
  password: '',
})

async function login() {
  try {
    await auth.login(form.email, form.password)
    router.push('/client')
  } catch (err) {
    // Ошибка уже установлена в store
  }
}
</script>

<style scoped>
.login-view {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 80px);
  background-color: #f5f5f5;
}

.auth-container {
  background-color: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

h2 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: #2c3e50;
}

input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 5px rgba(52, 152, 219, 0.3);
}

.btn {
  width: 100%;
  padding: 10px;
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
  padding: 10px 15px;
  border-radius: 4px;
  margin-top: 15px;
  font-size: 14px;
}

.alert-error {
  background-color: #ffebee;
  color: #d32f2f;
  border: 1px solid #ef5350;
}

.auth-links {
  text-align: center;
  margin-top: 15px;
  font-size: 14px;
}

.auth-links a {
  color: #3498db;
  text-decoration: none;
}

.auth-links a:hover {
  text-decoration: underline;
}

.test-accounts {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ddd;
}

.test-accounts h3 {
  font-size: 14px;
  margin-bottom: 10px;
  color: #2c3e50;
}

.test-accounts table {
  width: 100%;
  font-size: 12px;
  border-collapse: collapse;
}

.test-accounts th,
.test-accounts td {
  padding: 5px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.test-accounts th {
  background-color: #f5f5f5;
  font-weight: bold;
}
</style>
