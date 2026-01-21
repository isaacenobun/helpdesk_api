# ================================
# Stage 1: Build dependencies
# ================================
FROM python:3.11-slim AS build

WORKDIR /usr/src/app

# System dependencies for building wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements first for better caching
COPY requirements.tx[t] ./requirements.txt

# Install Python dependencies
RUN pip install --upgrade pip && \
    if [ -f requirements.txt ]; then \
        pip install -r requirements.txt && \
        pip install gunicorn psycopg2-binary; \
    fi

# Copy application source
COPY . .

# Collect static files ONLY if this is a Django project
RUN if [ -f manage.py ]; then \
        python manage.py collectstatic --noinput; \
    else \
        echo "manage.py not found, skipping collectstatic"; \
    fi


# ================================
# Stage 2: Runtime image
# ================================
FROM python:3.11-slim

WORKDIR /usr/src/app

# Runtime system dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtualenv from build stage
COPY --from=build /opt/venv /opt/venv

# Copy app source from build stage
COPY --from=build /usr/src/app /usr/src/app

ENV PATH="/opt/venv/bin:$PATH"

# Non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /usr/src/app
USER appuser

ENV PORT=8080
EXPOSE 8080

# Run migrations ONLY if Django exists, then start gunicorn
CMD if [ -f manage.py ]; then \
        python manage.py migrate; \
    else \
        echo "manage.py not found, skipping migrate"; \
    fi && \
    gunicorn --bind 0.0.0.0:$PORT --workers 4 --threads 2 --timeout 120 myproject.wsgi:application
