<template>
  <div class="register-view">
    <div class="auth-container">
      <h1>📝 Регистрация</h1>
      <p class="subtitle">Выберите вашу роль и создайте аккаунт</p>

      <form @submit.prevent="register">
        <div class="form-group">
          <label for="full_name">Полное имя *</label>
          <input
            id="full_name"
            v-model="form.fullName"
            type="text"
            placeholder="Ваше имя"
            required
          />
        </div>

        <div class="form-group">
          <label for="email">Email *</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            placeholder="example@repair.ru"
            required
          />
        </div>

        <div class="form-group">
          <label for="role">Ваша роль *</label>
          <div class="role-options">
            <label class="role-option">
              <input
                v-model="form.role"
                type="radio"
                value="client"
                required
              />
              <span class="role-label">
                <strong>👤 Клиент</strong>
                <small>Создание заявок и отслеживание их статуса</small>
              </span>
            </label>
            <label class="role-option">
              <input
                v-model="form.role"
                type="radio"
                value="master"
                required
              />
              <span class="role-label">
                <strong>🔧 Мастер</strong>
                <small>Поиск и выполнение заявок от клиентов</small>
              </span>
            </label>
          </div>
        </div>

        <div class="form-group">
          <label for="password">Пароль (минимум 8 символов) *</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            placeholder="••••••••"
            minlength="8"
            required
          />
        </div>

        <div class="form-group">
          <label for="password_confirm">Подтвердите пароль *</label>
          <input
            id="password_confirm"
            v-model="form.passwordConfirm"
            type="password"
            placeholder="••••••••"
            required
          />
          <span v-if="passwordError" class="error">{{ passwordError }}</span>
        </div>

        <button type="submit" class="btn btn-primary" :disabled="auth.loading">
          {{ auth.loading ? '⏳ Регистрация...' : '✓ Зарегистрироваться' }}
        </button>
      </form>

      <div v-if="auth.error" class="alert alert-error">
        <strong>Ошибка:</strong> {{ auth.error }}
      </div>

      <div class="auth-links">
        <p>Уже есть аккаунт? <router-link to="/login">Войдите здесь</router-link></p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const form = reactive({
  fullName: '',
  email: '',
  password: '',
  passwordConfirm: '',
  role: 'client',
})

const passwordError = computed(() => {
  if (form.password && form.passwordConfirm && form.password !== form.passwordConfirm) {
    return 'Пароли не совпадают'
  }
  return ''
})

async function register() {
  if (passwordError.value) return

  try {
    await auth.register(form.email, form.password, form.fullName, form.role)
    // Автоматически логинимся после регистрации
    await auth.login(form.email, form.password)

    // Редирект в зависимости от роли
    if (form.role === 'master') {
      router.push('/master/board')
    } else {
      router.push('/client')
    }
  } catch (err) {
    // Ошибка уже установлена в store
  }
}
</script>

<style scoped>
.register-view {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 80px);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.auth-container {
  background-color: white;
  padding: 35px;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  width: 100%;
  max-width: 450px;
}

h1 {
  text-align: center;
  color: #2c3e50;
  margin: 0 0 10px 0;
  font-size: 28px;
}

.subtitle {
  text-align: center;
  color: #7f8c8d;
  margin-bottom: 25px;
  font-size: 14px;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #2c3e50;
  font-size: 14px;
}

input[type="text"],
input[type="email"],
input[type="password"] {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
  transition: all 0.3s ease;
}

input[type="text"]:focus,
input[type="email"]:focus,
input[type="password"]:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 8px rgba(102, 126, 234, 0.3);
}

.role-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.role-option {
  display: flex;
  align-items: flex-start;
  padding: 12px;
  border: 2px solid #ecf0f1;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.role-option:hover {
  border-color: #667eea;
  background-color: #f8f9fa;
}

.role-option input[type="radio"] {
  width: auto;
  margin-right: 12px;
  margin-top: 2px;
  cursor: pointer;
}

.role-option input[type="radio"]:checked ~ .role-label {
  color: #667eea;
}

.role-option input[type="radio"]:checked + .role-label {
  color: #667eea;
}

.role-label {
  display: flex;
  flex-direction: column;
  gap: 3px;
  flex: 1;
}

.role-label strong {
  color: #2c3e50;
  font-size: 14px;
}

.role-label small {
  color: #95a5a6;
  font-size: 12px;
}

.error {
  display: block;
  color: #e74c3c;
  font-size: 12px;
  margin-top: 5px;
}

.btn {
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 15px;
  font-weight: bold;
  transition: all 0.3s ease;
}

.btn-primary {
  background-color: #667eea;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #5568d3;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.alert {
  padding: 12px 15px;
  border-radius: 6px;
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
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ecf0f1;
}

.auth-links p {
  margin: 0;
  color: #7f8c8d;
  font-size: 14px;
}

.auth-links a {
  color: #667eea;
  text-decoration: none;
  font-weight: bold;
}

.auth-links a:hover {
  text-decoration: underline;
}

@media (max-width: 480px) {
  .auth-container {
    padding: 25px;
  }

  h1 {
    font-size: 24px;
  }

  .role-options {
    gap: 10px;
  }

  .role-option {
    padding: 10px;
  }
}

.error {
  display: block;
  color: #e74c3c;
  font-size: 12px;
  margin-top: 5px;
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
</style>
