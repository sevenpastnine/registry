# -----------------------------------------------------------------------------
#  Frontend

FROM node:22 AS frontend-builder

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

ARG WORKERS

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN pip install pdm gunicorn

COPY pyproject.toml pdm.lock ./
RUN pdm sync --global --project . --no-editable --production

COPY manage.py .
COPY backend backend
COPY --from=frontend-builder /build/backend/static/frontend ./backend/static/frontend

CMD python manage.py migrate && \
    python manage.py collectstatic --no-input --clear && \
    gunicorn --bind=unix:/app/var/run/wsgi.sock --workers=${WORKERS} backend.wsgi
