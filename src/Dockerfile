# ------------------- BUILD FRONTEND -------------------
FROM node:20 AS frontend
WORKDIR /app/frontend
COPY frontend/ .
RUN npm install
RUN npm run build

# ------------ COMBINE BACKEND AND FRONTEND ------------
FROM selenium/standalone-chrome
WORKDIR /app
COPY --from=frontend /app/frontend/dist /app/frontend/dist

ENV PYTHONPATH=/app/backend/src:$PYTHONPATH
WORKDIR /app/backend
COPY backend/ .

# Add commands for user management
COPY backend/src/user_management.py /app/backend/src/user_management.py
COPY entrypoint.sh /app/entrypoint.sh

USER root
RUN chmod +x /app/entrypoint.sh

RUN apt-get update && apt-get install -y python3-venv python3-dev python3-tk
RUN python3 -m venv venv
ENV PATH="/app/backend/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# Setup seleniumbase with chromedriver
RUN seleniumbase get chromedriver --path

# Cleanup
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

EXPOSE 7653
ENV FLASK_ENV=production
VOLUME /config

ENTRYPOINT ["/app/entrypoint.sh"]
# Note: More than 1 worker is not supported with socketio
CMD ["gunicorn", "main:app", "-b", "0.0.0.0:7653", "-w", "1", "--worker-class", "eventlet"]
