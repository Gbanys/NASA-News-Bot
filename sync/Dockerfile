FROM python:3.11-slim

ENV POETRY_VERSION=1.8.2
ENV PYTHONUNBUFFERED=1 

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi

RUN apt-get update && \
    apt-get install -y chromium && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY ./sync /app/sync
WORKDIR /app/sync

CMD ["sleep", "3600"]