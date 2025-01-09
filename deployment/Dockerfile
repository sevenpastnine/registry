# -----------------------------------------------------------------------------
#  Frontend

FROM node:23 AS frontend-builder

WORKDIR /build

COPY package.json package-lock.json ./
RUN npm install

COPY vite.config.js tailwind.config.js postcss.config.js ./
COPY tsconfig.json ./
COPY frontend frontend
COPY backend backend

RUN npm run build

# -----------------------------------------------------------------------------
# Backend

FROM python:3.13-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

RUN pip install pdm

COPY pyproject.toml pdm.lock ./
RUN . $HOME/.cargo/env && pdm sync --global --project . --no-editable --production

COPY manage.py .
COPY backend backend
COPY --from=frontend-builder /build/backend/static/frontend ./backend/static/frontend

CMD python manage.py collectstatic --no-input --clear && \
    python manage.py migrate && \
    rm -f /app/var/run/wsgi.sock /app/var/run/wsgi.sock.lock && \
    daphne --unix-socket /app/var/run/wsgi.sock backend.asgi:application
