# File Sharing System

Система для загрузки и обмена файлами с административной панелью. Проект состоит из двух частей:
- **Backend**: FastAPI (Python) + PostgreSQL
- **Frontend**: Nuxt.js (Vue.js) + TailwindCSS + PrimeVue

## Архитектура проекта

```
site/
├── server_back/     # Backend API (FastAPI)
├── server_front/    # Frontend (Nuxt.js)
└── README.md
```

## Требования

### Системные требования
- **Python 3.11+**
- **Node.js 18+**
- **Docker & Docker Compose** (для быстрого запуска)
- **PostgreSQL** (если запуск без Docker)

### Порты по умолчанию
- Backend API: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- PostgreSQL: `localhost:5432`

---

## 🚀 Быстрый запуск с Docker

### 1. Запуск базы данных
```bash
cd server_back
docker-compose up -d
```

### 2. Настройка переменных окружения

Создайте файл `.env` в папке `server_back/`:

```env
# База данных PostgreSQL
PS_DATABASE_NAME=postgresql
PS_DRIVER=asyncpg
PS_USERNAME=postgres
PS_PASSWORD=1
PS_HOST=localhost
PS_TABLE_NAME=postgresql

# Redis (если используется)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Настройки приложения
BASE_URL=http://localhost:8000
```

### 3. Запуск Backend
```bash
cd server_back

# Установка зависимостей
pip install -r requirements.txt

# Запуск миграций базы данных
alembic upgrade head

# Запуск сервера
python main.py
```

### 4. Запуск Frontend
```bash
cd server_front

# Установка зависимостей
npm install

# Запуск в режиме разработки
npm run dev
```

Приложение будет доступно по адресу: `http://localhost:3000`

---

## 🐳 Запуск полностью в Docker

### 1. Создайте docker-compose.yml в корне проекта:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16
    restart: always
    environment:
      POSTGRES_DB: postgresql
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: 1
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./server_back
    ports:
      - "8000:8000"
    depends_on:
      - postgres
    environment:
      PS_DATABASE_NAME: postgresql
      PS_DRIVER: asyncpg
      PS_USERNAME: postgres
      PS_PASSWORD: 1
      PS_HOST: postgres
      PS_TABLE_NAME: postgresql
    volumes:
      - ./server_back/app/uploads:/app/app/uploads
      - ./server_back/logs:/app/logs

  frontend:
    build: ./server_front
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
```

### 2. Запуск всех сервисов:
```bash
docker-compose up --build
```

---

## ⚙️ Ручная настройка без Docker

### Backend (FastAPI)

1. **Установка PostgreSQL**
   ```bash
   # macOS
   brew install postgresql
   brew services start postgresql
   
   # Ubuntu
   sudo apt-get install postgresql postgresql-contrib
   sudo systemctl start postgresql
   ```

2. **Создание базы данных**
   ```bash
   sudo -u postgres psql
   CREATE DATABASE postgresql;
   CREATE USER postgres WITH PASSWORD '1';
   GRANT ALL PRIVILEGES ON DATABASE postgresql TO postgres;
   \q
   ```

3. **Установка Python зависимостей**
   ```bash
   cd server_back
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # или venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

4. **Настройка переменных окружения**
   Создайте `.env` файл в `server_back/` (см. пример выше)

5. **Запуск миграций**
   ```bash
   alembic upgrade head
   ```

6. **Запуск сервера**
   ```bash
   python main.py
   ```

### Frontend (Nuxt.js)

1. **Установка зависимостей**
   ```bash
   cd server_front
   npm install
   ```

2. **Настройка конфигурации**
   Убедитесь что в `nuxt.config.ts` правильно указан адрес API:
   ```typescript
   runtimeConfig: {
     public: {
       apiBase: 'http://localhost:8000'
     }
   }
   ```

3. **Запуск в режиме разработки**
   ```bash
   npm run dev
   ```

4. **Сборка для продакшена**
   ```bash
   npm run build
   npm run start
   ```

---

## 📋 Доступные команды

### Backend
```bash
# Запуск сервера разработки
python main.py

# Создание новой миграции
alembic revision --autogenerate -m "migration name"

# Применение миграций
alembic upgrade head

# Откат последней миграции
alembic downgrade -1
```

### Frontend
```bash
# Разработка
npm run dev

# Сборка
npm run build

# Продакшн
npm run start

# Генерация статического сайта
npm run generate

# Предпросмотр сборки
npm run preview
```

---

## 🔧 Конфигурация

### Переменные окружения Backend (.env)

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `PS_DATABASE_NAME` | Тип БД | `postgresql` |
| `PS_DRIVER` | Драйвер БД | `asyncpg` |
| `PS_USERNAME` | Пользователь БД | `postgres` |
| `PS_PASSWORD` | Пароль БД | `1` |
| `PS_HOST` | Хост БД | `localhost` |
| `PS_TABLE_NAME` | Имя БД | `postgresql` |
| `BASE_URL` | URL API | `http://localhost:8000` |
| `REDIS_HOST` | Хост Redis | `localhost` |
| `REDIS_PORT` | Порт Redis | `6379` |

### CORS настройки
Backend настроен для работы с фронтендом на:
- `http://localhost:3000`
- `http://192.168.1.76:3000`

---

## 📁 Структура проекта

### Backend (`server_back/`)
```
server_back/
├── api/routes/          # API маршруты
├── core/               # Конфигурация, БД, утилиты
├── app/uploads/        # Загруженные файлы
├── logs/              # Логи приложения
├── alembic/           # Миграции БД
├── main.py            # Точка входа
└── requirements.txt   # Python зависимости
```

### Frontend (`server_front/`)
```
server_front/
├── components/        # Vue компоненты
├── pages/            # Страницы приложения
├── layouts/          # Макеты страниц
├── stores/           # Pinia стор
├── composables/      # Composables
├── middleware/       # Middleware
├── assets/           # Статические ресурсы
└── nuxt.config.ts    # Конфигурация Nuxt
```

---

## 🚨 Устранение неполадок

### Backend не запускается
1. Проверьте подключение к PostgreSQL
2. Убедитесь что все переменные окружения заданы
3. Проверьте логи в `server_back/logs/`

### Frontend не подключается к API
1. Проверьте что Backend запущен на порту 8000
2. Проверьте настройки CORS в `server_back/main.py`
3. Убедитесь что `apiBase` в `nuxt.config.ts` правильный

### Проблемы с базой данных
1. Проверьте статус PostgreSQL: `brew services list | grep postgres`
2. Запустите миграции: `alembic upgrade head`
3. Проверьте подключение: `psql -h localhost -U postgres -d postgresql`

---

## 📦 Продакшн развертывание

### С Docker
```bash
docker-compose -f docker-compose.yml up -d --build
```

### Без Docker
1. Настройте reverse proxy (nginx)
2. Используйте process manager (pm2, systemd)
3. Настройте SSL сертификаты
4. Конфигурируйте переменные окружения для продакшена

---

## 🤝 Разработка

1. Форкните репозиторий
2. Создайте ветку для фичи
3. Внесите изменения
4. Создайте Pull Request

## 📝 Лицензия

MIT License
