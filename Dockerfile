# --- Backend (FastAPI + Python) ---

# --- Backend (FastAPI + Python) ---
FROM python:3.11-slim AS backend

WORKDIR /app


# Install build tools for llama-cpp-python
RUN apt-get update && apt-get install -y --no-install-recommends \
	build-essential \
	cmake \
	&& rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt


# Copy backend code and download script
COPY llm_edge_router.py api_server.py download_models.py ./

# Download models during build
RUN python download_models.py

# Copy models directory if present (optional, won't overwrite downloaded models)
COPY models ./models

# Copy .env if needed (for local dev only; use secrets in prod)
# COPY .env ./

# --- Frontend (Vite/React) ---
FROM node:20-alpine AS frontend
WORKDIR /frontend
COPY package.json package-lock.json ./
RUN npm ci
COPY . ./
RUN npm run build

# --- Final image: serve frontend + backend ---
FROM python:3.11-slim
WORKDIR /app

# Install build tools for llama-cpp-python runtime (needed for some wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
	build-essential \
	cmake \
	&& rm -rf /var/lib/apt/lists/*

# Copy backend from backend stage
COPY --from=backend /app /app

# Copy built frontend from frontend stage
COPY --from=frontend /frontend/dist /app/static

# Install production server
RUN pip install --no-cache-dir uvicorn[standard] fastapi

# Expose port
EXPOSE 8000

# Start FastAPI with Uvicorn, serving static files
CMD ["sh", "-c", "ls -l /app && python3 --version && uvicorn api_server:app --host 0.0.0.0 --port 8000"]