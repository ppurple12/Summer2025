# Use python:3.12-slim as base
FROM python:3.12-slim AS backend

# Set working directory
WORKDIR /app

# Install only what's needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip gcc g++ libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY backend/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Frontend build stage
FROM node:18 AS frontend
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Final lightweight image
FROM python:3.12-slim AS final
WORKDIR /app

COPY --from=backend /app /app
COPY --from=frontend /app/dist ./frontend_dist

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]