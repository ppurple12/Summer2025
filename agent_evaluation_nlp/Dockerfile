# Build frontend
FROM node:18 AS frontend-builder
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# Backend stage
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies, including OpenSSL dev and pkg-config for Rust build
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    curl \
    build-essential \
    pkg-config \
    libssl-dev \
 && rm -rf /var/lib/apt/lists/*
COPY backend/requirements.txt .
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

COPY agent_evaluation_nlp/backend/ .  

# Copy frontend build output
COPY --from=frontend-builder /app/dist ./frontend_dist

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
