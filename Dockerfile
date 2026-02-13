FROM python:3.14-slim
ARG INSTALL_DEV=false

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/app" \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV PATH="$POETRY_HOME/bin:$PATH"

WORKDIR /app

COPY pyproject.toml poetry.lock* ./

# RUN poetry install --no-root --no-dev
# RUN poetry install --no-root --with dev

RUN if [ "$INSTALL_DEV" = "true" ]; then \
      poetry install --no-root --with dev ; \
    else \
      poetry install --no-root --only main ; \
    fi

COPY . .

#EXPOSE 8000

CMD ["gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]