# Build frontend
FROM node:18 AS frontend-builder
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# Backend stage
FROM python:3.12-slim
WORKDIR /app

# Install pip and dependencies
RUN apt-get update && apt-get install -y --no-install-recommends python3-pip && \
    rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY backend/ .

# Copy only frontend output
COPY --from=frontend-builder /app/dist ./frontend_dist

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]