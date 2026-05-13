# Docker Configuration for Edge LLM System

## Dockerfile for Local Development and Testing

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY llm_edge_router.py .
COPY example_integration.py .
COPY download_models.py .

# Create directories
RUN mkdir -p /app/models /app/data

# Expose port for API (if needed)
EXPOSE 8000

# Default command
CMD ["python", "example_integration.py"]
```

## Docker Compose for Full Stack

```yaml
# docker-compose.yml
version: '3.8'

services:
  llm-router:
    build: .
    container_name: edge-llm-router
    volumes:
      - ./models:/app/models
      - ./data:/app/data
      - ./.env:/app/.env
    environment:
      - PYTHONUNBUFFERED=1
    ports:
      - "8000:8000"
    command: python example_integration.py
    
  # Optional: API server
  llm-api:
    build: .
    container_name: edge-llm-api
    volumes:
      - ./models:/app/models
      - ./.env:/app/.env
    ports:
      - "8001:8001"
    command: python api_server.py
    depends_on:
      - llm-router

  # Optional: Web UI
  llm-ui:
    image: node:18-alpine
    container_name: edge-llm-ui
    working_dir: /app
    volumes:
      - ./web:/app
    ports:
      - "3000:3000"
    command: npm run dev
```

## Build and Run

```bash
# Build the image
docker build -t edge-llm-system .

# Run interactively
docker run -it --rm \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/.env:/app/.env \
  edge-llm-system

# Run with docker-compose
docker-compose up

# Download models in container
docker run -it --rm \
  -v $(pwd)/models:/app/models \
  edge-llm-system \
  python download_models.py --platform desktop
```

---

## Kubernetes Deployment (Optional)

```yaml
# k8s-deployment.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: llm-config
data:
  config.json: |
    {
      "models_dir": "/models",
      "max_context_length": 128000,
      "enable_metrics": true
    }

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: llm-models-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: edge-llm-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: edge-llm
  template:
    metadata:
      labels:
        app: edge-llm
    spec:
      containers:
      - name: llm-router
        image: edge-llm-system:latest
        ports:
        - containerPort: 8000
        volumeMounts:
        - name: models
          mountPath: /app/models
        - name: config
          mountPath: /app/config
        env:
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: llm-secrets
              key: gemini-api-key
        resources:
          requests:
            memory: "8Gi"
            cpu: "2"
          limits:
            memory: "16Gi"
            cpu: "4"
      volumes:
      - name: models
        persistentVolumeClaim:
          claimName: llm-models-pvc
      - name: config
        configMap:
          name: llm-config

---
apiVersion: v1
kind: Service
metadata:
  name: edge-llm-service
spec:
  selector:
    app: edge-llm
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

---

## API Server (Optional)

```python
# api_server.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from llm_edge_router import LLMEdgeRouter
import asyncio
import uvicorn

app = FastAPI(title="Edge LLM API")
router = LLMEdgeRouter()

class GenerateRequest(BaseModel):
    prompt: str
    model_id: Optional[str] = None
    task_type: str = "general"
    max_tokens: int = 512
    temperature: float = 0.7

class GenerateResponse(BaseModel):
    response: str
    model_used: str
    tier: str
    latency_ms: float

@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    """Generate text using the LLM router"""
    try:
        import time
        start = time.time()
        
        result = await router.generate(
            prompt=request.prompt,
            model_id=request.model_id,
            task_type=request.task_type,
        )
        
        latency = (time.time() - start) * 1000
        
        return GenerateResponse(
            response=result["response"],
            model_used=result["model"],
            tier=result["routing"]["tier"],
            latency_ms=latency
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models")
async def list_models():
    """List available models"""
    return {
        "local": [
            {
                "id": model_id,
                "name": model.name,
                "tier": model.tier.value,
                "context_window": model.max_context
            }
            for model_id, model in router.models.items()
            if model.tier.value == "local"
        ],
        "cloud": [
            {
                "id": model_id,
                "name": model.name,
                "tier": model.tier.value,
                "context_window": model.max_context
            }
            for model_id, model in router.models.items()
            if model.tier.value != "local"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "models_loaded": len(router.models)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## Deployment Scripts

### deploy.sh - Automated Deployment

```bash
#!/bin/bash
# deploy.sh - Automated deployment script

set -e

echo "🚀 Edge LLM System Deployment Script"
echo "======================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PLATFORM=${1:-"desktop"}
MODELS_DIR="./models"
ENV_FILE=".env"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check Python
check_python() {
    log_info "Checking Python installation..."
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 not found. Please install Python 3.9+"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    log_info "Found Python $PYTHON_VERSION"
}

# Install dependencies
install_dependencies() {
    log_info "Installing Python dependencies..."
    
    if [ ! -f "requirements.txt" ]; then
        log_error "requirements.txt not found"
        exit 1
    fi
    
    python3 -m pip install -r requirements.txt
    log_info "Dependencies installed"
}

# Setup environment
setup_environment() {
    log_info "Setting up environment..."
    
    if [ ! -f "$ENV_FILE" ]; then
        log_warn "No .env file found. Creating template..."
        cat > $ENV_FILE << EOF
# Cloud API Keys (optional)
GEMINI_API_KEY=
GROQ_API_KEY=
TOGETHER_API_KEY=
HF_API_TOKEN=

# Configuration
MODELS_DIR=./models
MAX_CONTEXT_LENGTH=128000
ENABLE_METRICS=true
EOF
        log_info "Created $ENV_FILE - please add your API keys"
    else
        log_info "Found existing $ENV_FILE"
    fi
}

# Download models
download_models() {
    log_info "Downloading models for $PLATFORM..."
    
    if [ ! -d "$MODELS_DIR" ]; then
        mkdir -p "$MODELS_DIR"
    fi
    
    python3 download_models.py --platform "$PLATFORM"
    
    if [ $? -eq 0 ]; then
        log_info "Models downloaded successfully"
    else
        log_error "Model download failed"
        exit 1
    fi
}

# Test installation
test_installation() {
    log_info "Testing installation..."
    
    python3 -c "from llm_edge_router import LLMEdgeRouter; r = LLMEdgeRouter(); print('✓ Import successful')"
    
    if [ $? -eq 0 ]; then
        log_info "Installation test passed"
    else
        log_error "Installation test failed"
        exit 1
    fi
}

# Main deployment flow
main() {
    echo ""
    log_info "Starting deployment for platform: $PLATFORM"
    echo ""
    
    check_python
    install_dependencies
    setup_environment
    download_models
    test_installation
    
    echo ""
    log_info "✅ Deployment complete!"
    echo ""
    echo "Next steps:"
    echo "  1. Configure API keys in $ENV_FILE (optional)"
    echo "  2. Run: python example_integration.py"
    echo "  3. Or import in your code: from llm_edge_router import LLMEdgeRouter"
    echo ""
}

# Run
main
```

### Make it executable

```bash
chmod +x deploy.sh

# Run deployment
./deploy.sh ios
./deploy.sh android
./deploy.sh web
./deploy.sh desktop
```

---

## CI/CD Configuration

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy Edge LLM System

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python -m pytest tests/
    
    - name: Test imports
      run: |
        python -c "from llm_edge_router import LLMEdgeRouter"
  
  build:
    runs-on: ubuntu-latest
    needs: test
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: |
        docker build -t edge-llm-system:latest .
    
    - name: Test Docker image
      run: |
        docker run --rm edge-llm-system:latest python -c "from llm_edge_router import LLMEdgeRouter; print('OK')"
```

---

## Production Checklist

### Before Deployment

- [ ] Test all models locally
- [ ] Configure API keys securely
- [ ] Set up monitoring/logging
- [ ] Review model licenses
- [ ] Test offline mode
- [ ] Benchmark performance
- [ ] Security audit (API keys, etc.)

### Platform-Specific

**iOS:**
- [ ] TestFlight beta testing
- [ ] App Store compliance check
- [ ] Memory profiling on devices
- [ ] Battery impact testing

**Android:**
- [ ] Google Play compliance
- [ ] Test on multiple devices
- [ ] ProGuard/R8 configuration
- [ ] APK size optimization

**Web:**
- [ ] Service worker testing
- [ ] HTTPS configuration
- [ ] CDN setup for models
- [ ] Cross-browser testing

### Monitoring

```python
# monitoring_config.py
MONITORING = {
    "enable_metrics": True,
    "metrics_file": "metrics.jsonl",
    "alert_on_errors": True,
    "log_level": "INFO",
    "track": [
        "latency",
        "model_usage",
        "error_rate",
        "tier_distribution"
    ]
}
```

---

## Scaling Considerations

### Horizontal Scaling

```bash
# Use load balancer with multiple instances
docker-compose up --scale llm-api=3

# Or Kubernetes
kubectl scale deployment edge-llm-deployment --replicas=5
```

### Model Caching

```python
# Shared model cache across instances
from redis import Redis

redis_client = Redis(host='localhost', port=6379)

# Cache model outputs
def cached_generate(prompt, ttl=3600):
    cache_key = f"llm:{hash(prompt)}"
    
    cached = redis_client.get(cache_key)
    if cached:
        return cached.decode()
    
    result = router.generate(prompt)
    redis_client.setex(cache_key, ttl, result)
    
    return result
```

---

## Cost Optimization

### Free Tier Limits

```python
# Track usage against free tiers
FREE_TIER_LIMITS = {
    "gemini-flash": {
        "requests_per_minute": 15,
        "tokens_per_day": 1_000_000
    },
    "groq-llama": {
        "requests_per_minute": 30,
        "tokens_per_day": 14_400
    }
}

# Implement rate limiting
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=15, period=60)  # Gemini limit
def call_gemini_api(prompt):
    # Your API call
    pass
```

---

## Backup and Recovery

```bash
#!/bin/bash
# backup.sh - Backup models and data

DATE=$(date +%Y%m%d)
BACKUP_DIR="./backups/$DATE"

mkdir -p "$BACKUP_DIR"

# Backup models
tar -czf "$BACKUP_DIR/models.tar.gz" ./models/

# Backup data
tar -czf "$BACKUP_DIR/data.tar.gz" ./data/

# Backup config
cp .env "$BACKUP_DIR/.env"
cp config.json "$BACKUP_DIR/config.json"

echo "Backup complete: $BACKUP_DIR"
```

---

This deployment configuration provides everything needed for production deployment of the Edge LLM System!
