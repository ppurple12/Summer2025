# Build frontend
# ---------- Frontend Build Stage ----------
FROM node:18 AS frontend-builder
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# ---------- Backend Stage ----------
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    curl \
    build-essential \
    pkg-config \
    libssl-dev \
 && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt
RUN python3 -m nltk.downloader vader_lexicon
RUN mkdir -p backend
COPY backend/all_mpnet_base_v2.onnx backend/all_mpnet_base_v2.onnx 

# Copy backend code
COPY backend/ .
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    git-lfs \
 && git lfs install

# Make sure ONNX file is pulled as full binary (if coming from Git)
RUN git lfs pull
# Ensure the ONNX model ends up in the exact path your app expects
RUN mkdir -p agent_evaluation_nlp/backend
COPY backend/all_mpnet_base_v2.onnx agent_evaluation_nlp/backend/all_mpnet_base_v2.onnx

# Copy frontend build output
COPY --from=frontend-builder /app/dist ./frontend_dist

# Start the FastAPI app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]