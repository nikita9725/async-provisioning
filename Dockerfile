# === STAGE 1: сборка зависимостей ===
FROM astral/uv:0.7.16-python3.13-bookworm-slim AS builder

# Переменные для настройки UV
ENV UV_COMPILE_BYTECODE="1"
ENV UV_LINK_MODE="copy"
ENV UV_PYTHON_DOWNLOADS="0"

WORKDIR /app

# Копируем только файлы зависимостей для лучшего кеширования
COPY pyproject.toml uv.lock ./

# Установка зависимостей с кешированем
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

# Копируем остальной код и финалищируем сборку
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# === STAGE 2: финальная сборка ===
FROM python:3.13.5-slim-bullseye AS runtime

# Копируем исходный код из builder
COPY --from=builder --chown=app:app /app /app

WORKDIR /app

# Активизируем виртуальное окружение
ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "main.py"]
