
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

COPY backend/requirements.txt .
RUN pip install -r requirements.txt
RUN python -m nltk.downloader vader_lexicon
COPY backend/ .

COPY . .
# Copy frontend build output to backend folder for serving
COPY --from=frontend-builder /app/frontend/dist ./frontend_dist

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]