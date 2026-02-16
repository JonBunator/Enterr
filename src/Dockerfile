# ------------------- BUILD FRONTEND -------------------
FROM node:25-slim AS frontend
WORKDIR /app/frontend
COPY frontend/ .
RUN npm install
RUN npm run build

# ------------ COMBINE BACKEND AND FRONTEND ------------
FROM selenium/standalone-chrome
WORKDIR /app
COPY --from=frontend /app/frontend/dist /app/frontend/dist

ENV PYTHONPATH=/app/backend/src:$PYTHONPATH
ENV DISPLAY=:99
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app/backend
COPY backend/src /app/backend/src
COPY backend/src/user_management.py /app/backend/src/user_management.py
COPY entrypoint.sh /app/entrypoint.sh
COPY start.sh /app/start.sh

USER root
RUN chmod +x /app/entrypoint.sh
RUN chmod +x /app/start.sh

RUN apt-get update && apt-get install -y python3-venv python3-dev python3-tk
RUN python3 -m venv venv
ENV PATH="/app/backend/venv/bin:$PATH"
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Setup seleniumbase with chromedriver
RUN seleniumbase get chromedriver --path

# Cleanup
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

EXPOSE 7653
ENV RUN_MODE=production
VOLUME /config

HEALTHCHECK --interval=15m --timeout=30s --start-period=5s --retries=3 CMD [ "curl", "http://localhost:7653/api/health" ]
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["/app/start.sh"]
