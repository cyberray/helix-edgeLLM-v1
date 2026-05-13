# Edge LLM System - Quick Reference Cheat Sheet

## 🚀 Getting Started (3 Commands)

```bash
# 1. Automated setup (recommended)
./quickstart.sh

# 2. Manual setup
pip install -r requirements.txt
python download_models.py --platform desktop

# 3. Start chatting
./edge-llm-cli.py chat
```

---

## 📦 Model Management

```bash
# List available models
python download_models.py --list

# Download specific model
python download_models.py --download phi-3.5-mini-q4

# Download for platform
python download_models.py --platform ios        # iOS
python download_models.py --platform android    # Android
python download_models.py --platform web        # Web

# Find models by size
python download_models.py --size-limit 2000     # Under 2GB

# Check downloaded models
python download_models.py --downloaded

# Force re-download
python download_models.py --download phi-3.5-mini-q4 --force
```

---

## 💬 CLI Commands

```bash
# Chat (interactive)
./edge-llm-cli.py chat

# Chat (single query)
./edge-llm-cli.py chat "What is machine learning?"

# Offline mode
./edge-llm-cli.py chat --offline "Explain recursion"

# Code generation
./edge-llm-cli.py code "binary search algorithm" --tests

# Code analysis
./edge-llm-cli.py analyze myfile.py

# Problem solving
./edge-llm-cli.py solve "Calculate compound interest"

# List models
./edge-llm-cli.py models

# Run benchmarks
./edge-llm-cli.py benchmark

# System status
./edge-llm-cli.py status

# Configuration wizard
./edge-llm-cli.py config
```

---

## 🐍 Python API

### Basic Usage
```python
from llm_edge_router import LLMEdgeRouter
import asyncio

async def main():
    router = LLMEdgeRouter()
    
    # Generate response
    result = await router.generate("What is AI?")
    print(result["response"])

asyncio.run(main())
```

### With Routing
```python
# Auto-route based on task
decision = router.route_request(
    prompt="Write a sorting function",
    task_type="coding"
)

print(f"Selected: {decision.selected_model}")
print(f"Reason: {decision.reason}")
```

### Force Offline
```python
router.set_offline_mode(True)
result = await router.generate("Explain TCP/IP")
```

### Battery Saver
```python
router.set_battery_saver(True)
result = await router.generate("Calculate 2+2")
```

---

## 🤖 Complete Agent

```python
from example_integration import EdgeLLMAgent
import asyncio

async def main():
    agent = EdgeLLMAgent()
    
    # Chat
    response = await agent.chat("Hello!")
    
    # Generate code
    code = await agent.generate_code(
        "Binary search",
        language="python",
        include_tests=True
    )
    
    # Analyze code
    analysis = await agent.analyze_code(code, "python")
    
    # Solve problem
    solution = await agent.solve_problem("Fermi paradox")
    
    # Get metrics
    summary = agent.get_metrics_summary()
    print(summary)

asyncio.run(main())
```

---

## 🎯 Model Selection Guide

### By Size
- **Smallest:** Gemma 2 2B Q4 (1.4GB) - Fast, resource-constrained
- **Medium:** Llama 3.2 3B Q4 (1.7GB) - Balanced
- **Balanced:** Qwen2.5 3B Q4 (1.9GB) - Best coding
- **Best All-Around:** Phi-3.5-mini Q4 (2GB) - 128K context

### By Task
- **Coding:** Qwen2.5 3B Q4
- **Reasoning:** Phi-3.5-mini Q4
- **Speed:** Gemma 2 2B Q4
- **Long Context:** Phi-3.5-mini Q4 (128K)

### By Platform
- **iOS:** Phi-3.5-mini Q4, Qwen2.5 3B Q4
- **Android:** Phi-3.5-mini Q4, Llama 3.2 3B Q4
- **Web:** Gemma 2 2B Q4
- **Desktop:** Phi-3.5-mini Q5 (higher quality)

---

## ☁️ Cloud APIs

### Get Free API Keys
```bash
# Gemini (1M tokens/day free)
# https://ai.google.dev/

# Groq (750+ tok/s, 14K tokens/day free)
# https://console.groq.com/

# Together.ai ($1/month free credits)
# https://api.together.xyz/

# Hugging Face
# https://huggingface.co/settings/tokens
```

### Configure Keys
```bash
# Interactive
./edge-llm-cli.py config

# Manual
cat > .env << EOF
GEMINI_API_KEY=your_key
GROQ_API_KEY=your_key
TOGETHER_API_KEY=your_key
HF_API_TOKEN=your_token
EOF
```

### Use in Code
```python
from dotenv import load_dotenv
load_dotenv()

# API keys auto-loaded
result = await router.generate(
    "Complex reasoning task",
    # Will use cloud if needed
)
```

---

## 🧪 Testing

```bash
# Run all tests
pytest test_edge_llm.py -v

# Run with coverage
pytest test_edge_llm.py --cov=. --cov-report=html

# Run specific test
pytest test_edge_llm.py::TestLLMEdgeRouter::test_simple_task_routing

# Run integration tests
pytest test_edge_llm.py -m integration

# Run demos
python example_integration.py
```

---

## 📱 Platform Deployment

### iOS
```bash
# 1. Setup llama.cpp
cd llama.cpp && mkdir build-ios && cd build-ios
cmake .. -G Xcode -DCMAKE_SYSTEM_NAME=iOS -DLLAMA_METAL=ON
cmake --build . --config Release

# 2. Create Xcode project (follow STEP_BY_STEP_DEPLOYMENT.md)
# 3. Add model to bundle
# 4. Build and run
```

### Android
```bash
# 1. Create project in Android Studio
# 2. Add MediaPipe dependency to build.gradle
implementation 'com.google.mediapipe:tasks-genai:0.10.9'

# 3. Copy model to assets/
# 4. Build and run
./gradlew assembleRelease
```

### Web
```bash
# 1. Create project
mkdir edge-llm-web && cd edge-llm-web
npm init -y

# 2. Install dependencies
npm install @xenova/transformers vite

# 3. Create files (index.html, main.js, llm-worker.js)
# 4. Run dev server
npm run dev

# 5. Build for production
npm run build
```

---

## 🐳 Docker

```bash
# Build
docker build -t edge-llm .

# Run
docker run -it --rm \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/.env:/app/.env \
  edge-llm

# With docker-compose
docker-compose up

# API server mode
docker run -p 8000:8000 edge-llm python api_server.py
```

---

## 🔧 Troubleshooting

### llama-cpp-python won't install
```bash
# macOS Apple Silicon
CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python

# NVIDIA GPU
CMAKE_ARGS="-DLLAMA_CUDA=on" pip install llama-cpp-python

# CPU only
pip install llama-cpp-python --no-cache-dir
```

### Model download failed
```bash
# Check internet
ping google.com

# Retry download
python download_models.py --download phi-3.5-mini-q4 --force

# Check space
df -h .
```

### Out of memory
```bash
# Use smaller model
python download_models.py --download gemma-2-2b-q4

# Or smaller quantization
python download_models.py --download phi-3.5-mini-q3
```

### Import errors
```bash
# Recreate environment
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📊 Performance Tips

### Speed Up Inference
```python
# Use smaller model
router.models["gemma-2-2b"]

# Reduce max tokens
result = await router.generate(prompt, max_tokens=256)

# Use Q4 instead of Q5 quantization
```

### Reduce Memory
```python
# Enable battery saver (uses local only)
router.set_battery_saver(True)

# Limit context length
decision = router.route_request(prompt, context_length=2048)
```

### Optimize Loading
```python
# Preload model
router.preload_model("phi-3.5-mini")

# Cache frequently used models
router.enable_model_cache(max_size=2)
```

---

## 📈 Monitoring

### Check Status
```bash
./edge-llm-cli.py status
```

### View Metrics
```python
agent = EdgeLLMAgent()
# ... use agent ...

summary = agent.get_metrics_summary()
print(f"Requests: {summary['total_requests']}")
print(f"Avg latency: {summary['avg_latency_ms']}ms")
print(f"Tier distribution: {summary['tier_distribution']}")
```

### Log to File
```python
# Metrics auto-logged to metrics.jsonl
tail -f metrics.jsonl
```

---

## 🔗 Quick Links

- **Full Docs:** README.md
- **Deployment:** STEP_BY_STEP_DEPLOYMENT.md
- **Platform Code:** platform_implementations.md
- **Docker:** DOCKER_DEPLOYMENT.md
- **Decision Guide:** DEPLOYMENT_DECISION_GUIDE.md

---

## 💡 Common Patterns

### Pattern 1: Simple Q&A
```python
result = await router.generate("What is Python?")
```

### Pattern 2: Code Generation
```python
result = await router.generate(
    "Write a function to calculate fibonacci",
    task_type="coding"
)
```

### Pattern 3: Offline Mode
```python
router.set_offline_mode(True)
result = await router.generate("Explain async/await")
```

### Pattern 4: Conversation
```python
agent = EdgeLLMAgent()
await agent.chat("Hi")
await agent.chat("Tell me more")  # Has context
```

### Pattern 5: Batch Processing
```python
queries = ["Q1", "Q2", "Q3"]
results = [await router.generate(q) for q in queries]
```

---

## ⚡ One-Liners

```bash
# Install everything
curl -sSL https://... | bash  # (use quickstart.sh)

# Download all models
for m in phi-3.5-mini-q4 qwen2.5-3b-q4; do python download_models.py --download $m; done

# Test everything
python -c "from llm_edge_router import LLMEdgeRouter; r=LLMEdgeRouter(); print('OK')"

# Start chatting
./edge-llm-cli.py chat

# Full demo
python example_integration.py
```

---

**Keep this cheat sheet handy for quick reference! 📌**

For detailed explanations, see the full documentation.
