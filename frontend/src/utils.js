/**
 * Утилиты и вспомогательные функции.
 */

/**
 * Форматирует дату в локальный формат.
 */
export function formatDate(dateString) {
  const options = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }
  return new Date(dateString).toLocaleDateString('ru-RU', options)
}

/**
 * Получает метку статуса заявки на русском.
 */
export function getStatusLabel(status) {
  const labels = {
    new: 'Новая',
    in_progress: 'В процессе',
    done: 'Выполнена',
    rejected: 'Отклонена',
  }
  return labels[status] || status
}

/**
 * Получает CSS класс для статуса.
 */
export function getStatusClass(status) {
  return `status-${status}`
}

/**
 * Валидирует email.
 */
export function isValidEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * Валидирует пароль (минимум 8 символов).
 */
export function isValidPassword(password) {
  return password.length >= 8
}
