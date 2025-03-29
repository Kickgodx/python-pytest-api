# Используем официальный образ Python на основе Debian (Alpine может иметь проблемы с Chrome)
FROM python:3.12-alpine

# Создаём рабочую директорию
WORKDIR /app

# Копируем requirements.txt
COPY requirements.txt .

# Создаём виртуальное окружение и устанавливаем зависимости
RUN python -m venv venv && . venv/bin/activate && pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы проекта
COPY . .

# Запускаем тесты
CMD ["sh", "-c", ". venv/bin/activate && pytest"]
#CMD ["tail", "-f", "/dev/null"]
#CMD bash
# apt --fix-broken install