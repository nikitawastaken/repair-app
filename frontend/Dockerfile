# Frontend Dockerfile
FROM node:20-alpine

WORKDIR /app

# Копируем package.json и package-lock.json
COPY package*.json ./

# Устанавливаем зависимости
RUN npm ci

# Копируем приложение
COPY . .

# Запускаем Vite dev server
CMD ["npm", "run", "dev"]
