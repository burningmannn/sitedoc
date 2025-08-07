FROM python:3.11-slim

WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё приложение
COPY . .

EXPOSE 8000

# Запуск Python-файла напрямую
CMD ["python", "main.py"]