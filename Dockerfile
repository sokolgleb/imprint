# Используем легковесный образ с поддержкой uv
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

# Устанавливаем зависимости отдельно для кэширования
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

# Копируем исходный код
COPY . .
RUN uv sync --frozen

# Финальный образ
FROM python:3.12-slim-bookworm
WORKDIR /app

# Копируем только установленное окружение и код
COPY --from=builder /app /app

# Прописываем путь к виртуальному окружению uv
ENV PATH="/app/.venv/bin:$PATH"

# Открываем порт и запускаем
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
