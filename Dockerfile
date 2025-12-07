FROM python:3.13-slim

# Устанавливаем uv
RUN pip install --no-cache-dir uv

# Создаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY pyproject.toml ./

# Создаем виртуальное окружение и устанавливаем зависимости
RUN uv venv && \
    . /app/.venv/bin/activate && \
    uv pip install -e .

# Копируем исходный код
COPY src/ ./src/
COPY README.md ./

# Создаем директорию для данных
RUN mkdir -p /app/data

# Устанавливаем переменные окружения
ENV PYTHONPATH=/app/src
ENV DATABASE_URL=sqlite:////app/data/database.db

# Открываем порт
EXPOSE 8000

# Команда для запуска
CMD ["/app/.venv/bin/uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]