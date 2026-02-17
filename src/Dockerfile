# ------------------- BUILD FRONTEND -------------------
FROM node:24-slim AS frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install

COPY frontend/ .
RUN npm run build

# ------------ COMBINE BACKEND AND FRONTEND ------------
FROM python:3.12-slim

ENV PYTHONPATH=/app/backend/src:$PYTHONPATH
ENV PYTHONDONTWRITEBYTECODE=1
ENV RUN_MODE=production

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

# Copy source code
COPY entrypoint.sh start.sh /app/
RUN chmod +x /app/entrypoint.sh /app/start.sh
COPY --from=frontend /app/frontend/dist /app/frontend/dist
COPY backend/src ./src

EXPOSE 7653
VOLUME /config

HEALTHCHECK --interval=15m --timeout=30s --start-period=5s --retries=3 CMD [ "curl", "http://localhost:7653/api/health" ]
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["/app/start.sh"]
