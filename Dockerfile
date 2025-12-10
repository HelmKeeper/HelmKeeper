FROM python:3.12-slim

# Install system dependencies
# git: for some helm plugins or deps
# curl: to download helm
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Helm (Latest)
RUN curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Set working directory
WORKDIR /app

# Install Poetry
ENV POETRY_VERSION=1.7.1
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Configure Poetry: No interaction, no virtualenv (install globally in container)
RUN poetry config virtualenvs.create false --local

# Install Python deps via Poetry
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --only main

# Copy application code
COPY main.py .

# Entrypoint
ENTRYPOINT ["python3", "main.py"]
