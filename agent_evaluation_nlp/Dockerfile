# Build frontend stage
FROM node:18 AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# Backend stage
FROM python:3.12-slim
WORKDIR /app

# Install pip and other dependencies
RUN apt-get update && apt-get install -y python3-pip && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip3 install -r requirements.txt

# Download NLTK resource
RUN python3 -m nltk.downloader vader_lexicon

COPY backend/ .

# Copy frontend build output to backend folder for serving
COPY --from=frontend-builder /app/frontend/dist ./frontend_dist

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]