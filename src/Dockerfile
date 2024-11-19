# ------------------- BUILD BACKEND -------------------
FROM python:3.9-slim AS backend
WORKDIR /app/backend
COPY backend/ .
RUN pip3 install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# ------------------- BUILD FRONTEND -------------------
FROM node:18 AS frontend
WORKDIR /app/frontend
COPY frontend/ .
RUN npm install
RUN npm run build

# ------------ COMBINE BACKEND AND FRONTEND ------------
FROM python:3.9-slim
WORKDIR /app
COPY --from=backend /app/backend /app/backend
COPY --from=frontend /app/frontend/dist /app/frontend/dist
WORKDIR /app/backend
RUN pip3 install --no-cache-dir -r requirements.txt
EXPOSE 8080
# Note: More than 1 worker is not supported with socketio
CMD ["gunicorn", "main:app", "-b", "0.0.0.0:8080", "-w", "1", "--worker-class", "eventlet"]
