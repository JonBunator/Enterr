# ------------------- BASE -------------------
FROM python:3.12-slim AS base

ENV PYTHONPATH=/app/backend/src:$PYTHONPATH
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies for backend (browser automation)
RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
    libgtk-3-0 \
    libdbus-glib-1-2 \
    libxt6 \
    libasound2 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxcursor1 \
    libxi6 \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdrm2 \
    libgbm1 \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/backend

# Install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Download Camoufox browser
RUN camoufox fetch

COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

VOLUME /config
ENTRYPOINT ["/app/entrypoint.sh"]

# ------------------- DEVELOPMENT -------------------
FROM base AS development

ENV RUN_MODE=development

# Install Node.js for frontend dev server
RUN curl -fsSL https://deb.nodesource.com/setup_24.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install frontend dependencies
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install

WORKDIR /app
COPY start-dev.sh /app/
RUN chmod +x /app/start-dev.sh

EXPOSE 7653 5173
CMD ["/app/start-dev.sh"]

# ------------------- PRODUCTION -------------------
FROM node:24-slim AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

FROM base AS production
ENV RUN_MODE=production

COPY start.sh /app/
RUN chmod +x /app/start.sh
COPY --from=frontend-build /app/frontend/dist /app/frontend/dist
COPY backend/src ./src

EXPOSE 7653
HEALTHCHECK --interval=15m --timeout=30s --start-period=5s --retries=3 CMD [ "curl", "http://localhost:7653/api/health" ]
CMD ["/app/start.sh"]
