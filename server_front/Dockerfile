# Используем официальный Node.js образ
FROM node:18-slim

# Создаем рабочую директорию
WORKDIR /app

# Копируем package.json и package-lock.json
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем весь проект
COPY . .

# Собираем Nuxt-приложение
RUN npm run build

# Прокидываем порт (Nuxt по умолчанию использует 3000)
EXPOSE 3000

# Запускаем Nuxt-приложение
CMD ["npm", "run", "start"]
