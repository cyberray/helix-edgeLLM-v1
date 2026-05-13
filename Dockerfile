# --- Backend (FastAPI + Python) ---
FROM python:3.11-slim AS backend

WORKDIR /app

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY llm_edge_router.py api_server.py ./
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

# Copy backend from backend stage
COPY --from=backend /app /app

# Copy built frontend from frontend stage
COPY --from=frontend /frontend/dist /app/static

# Install production server
RUN pip install --no-cache-dir uvicorn[standard] fastapi

# Expose port
EXPOSE 8000

# Start FastAPI with Uvicorn, serving static files
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
