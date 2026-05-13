# Complete Edge LLM Deployment Guide
### Free LLMs for Mobile & Edge with Reasoning and Coding Capabilities

---

## Quick Start

```bash
# 1. Clone and setup
git clone <your-repo>
cd edge-llm-system

# 2. Install dependencies
pip install -r requirements.txt
npm install

# 3. Download models
python scripts/download_models.py --model phi-3.5-mini --quantization q4

# 4. Test local inference
python scripts/test_inference.py

# 5. Deploy to target platform
# iOS: ./scripts/deploy_ios.sh
# Android: ./scripts/deploy_android.sh
# Web: ./scripts/deploy_web.sh
```

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Model Selection Strategy](#model-selection-strategy)
4. [Platform-Specific Setup](#platform-specific-setup)
5. [Deployment Steps](#deployment-steps)
6. [Testing & Benchmarking](#testing--benchmarking)
7. [Production Optimization](#production-optimization)
8. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

### Three-Tier Hybrid System

```
┌─────────────────────────────────────────────────┐
│           User Request                          │
└──────────────┬──────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────┐
│         Smart Router (llm_edge_router.py)       │
│  • Analyzes task complexity                     │
│  • Checks network/battery status                │
│  • Selects optimal model                        │
└──────┬──────────────────────────────┬───────────┘
       │                              │
       ▼                              ▼
┌──────────────┐            ┌────────────────────┐
│  TIER 1      │            │  TIER 2 & 3       │
│  Local/Edge  │            │  Cloud APIs       │
├──────────────┤            ├───────────────────┤
│ Phi-3.5-mini │            │ Gemini Flash      │
│ Qwen2.5 3B   │            │ Groq Llama 70B    │
│ Llama 3.2 3B │            │ Together Mixtral  │
│              │            │ HuggingFace       │
│ • Offline    │            │                   │
│ • Private    │            │ • High quality    │
│ • Fast       │            │ • Long context    │
│ • Free       │            │ • Specialized     │
└──────────────┘            └───────────────────┘
```

---

## Prerequisites

### System Requirements

**For Local Inference:**
- **iOS**: iPhone 12+, iPad Pro, 4GB+ RAM, iOS 16+
- **Android**: 6GB+ RAM, Android 10+, ARM64
- **Web**: Chrome 113+, 4GB+ RAM, WebGPU support

**For Development:**
- Python 3.9+
- Node.js 18+
- 20GB+ free disk space (for models)
- Git

### Install Core Dependencies

```bash
# Python dependencies
cat > requirements.txt << 'EOF'
# Core LLM libraries
llama-cpp-python==0.2.56
transformers==4.38.0
onnxruntime==1.17.0
torch==2.2.0

# API clients
google-generativeai==0.3.2
groq==0.4.1
anthropic==0.18.0
openai==1.12.0

# Utilities
requests==2.31.0
aiohttp==3.9.3
pydantic==2.6.1
python-dotenv==1.0.1
tqdm==4.66.1
numpy==1.26.3

# Optional: GPU acceleration
# onnxruntime-gpu==1.17.0
EOF

pip install -r requirements.txt

# Node.js dependencies for web
cat > package.json << 'EOF'
{
  "name": "edge-llm-web",
  "version": "1.0.0",
  "type": "module",
  "dependencies": {
    "@xenova/transformers": "^2.14.0",
    "onnxruntime-web": "^1.17.0",
    "vite": "^5.1.0"
  }
}
EOF

npm install
```

---

## Model Selection Strategy

### Decision Matrix

| Use Case | Task | Best Model | Tier | Reason |
|----------|------|------------|------|--------|
| Code completion | Simple | Qwen2.5 3B | Local | Fast, coding-optimized |
| Quick Q&A | Simple | Phi-3.5-mini | Local | Balanced, offline |
| Code review | Medium | Qwen2.5 3B | Local | Strong coding |
| Document analysis | Medium | Phi-3.5-mini | Local | Long context |
| Complex reasoning | Complex | Groq Llama 70B | Cloud | Best quality, fast |
| Long context (>50K) | Complex | Gemini Flash | Cloud | 1M context window |
| Specialized tasks | Various | Together/HF | Cloud | Model variety |

### Quantization Guide

```python
# Model size vs. quality tradeoff

QUANTIZATIONS = {
    "Q4_K_M": {
        "size_reduction": "~75%",  # e.g., 14GB -> 3.5GB
        "quality_loss": "Minimal (~2-3%)",
        "recommended": True,
        "use_case": "General deployment"
    },
    "Q5_K_M": {
        "size_reduction": "~65%",
        "quality_loss": "Negligible (~1%)",
        "recommended": "If storage allows",
        "use_case": "High quality needed"
    },
    "Q8_0": {
        "size_reduction": "~50%",
        "quality_loss": "Almost none",
        "recommended": "For desktops only",
        "use_case": "Maximum quality"
    },
    "Q3_K_M": {
        "size_reduction": "~80%",
        "quality_loss": "Noticeable (~5-7%)",
        "recommended": False,
        "use_case": "Extreme size constraints"
    }
}
```

---

## Platform-Specific Setup

### iOS Deployment

#### 1. Install Xcode and Dependencies

```bash
# Install Xcode from App Store
# Then install command line tools:
xcode-select --install

# Install CocoaPods
sudo gem install cocoapods

# Install llama.cpp
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make

# Build for iOS
mkdir build-ios
cd build-ios
cmake .. -G Xcode \
    -DCMAKE_SYSTEM_NAME=iOS \
    -DLLAMA_METAL=ON \
    -DCMAKE_OSX_DEPLOYMENT_TARGET=16.0
cmake --build . --config Release
```

#### 2. Create Xcode Project Structure

```
MyLLMApp/
├── MyLLMApp/
│   ├── Models/
│   │   ├── LLMManager.swift
│   │   └── ModelDownloader.swift
│   ├── ViewModels/
│   │   └── ChatViewModel.swift
│   ├── Views/
│   │   ├── ContentView.swift
│   │   └── ChatView.swift
│   └── Resources/
│       └── models/ (gitignored)
├── llama.xcframework/
└── MyLLMApp.xcodeproj
```

#### 3. Configure Podfile

```ruby
# Podfile
platform :ios, '16.0'

target 'MyLLMApp' do
  use_frameworks!
  
  # For model management
  pod 'Alamofire', '~> 5.8'
  
  # For UI
  pod 'MarkdownView', '~> 1.7'
end
```

#### 4. Model Integration

```swift
// In your app delegate or SwiftUI App
import UIKit

@main
class AppDelegate: UIResponder, UIApplicationDelegate {
    var llmManager: LLMManager?
    
    func application(_ application: UIApplication,
                     didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        
        // Initialize LLM Manager
        llmManager = LLMManager()
        
        // Check and download model if needed
        Task {
            await downloadModelIfNeeded()
        }
        
        return true
    }
    
    private func downloadModelIfNeeded() async {
        let modelName = "phi-3.5-mini-q4"
        let documentsPath = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let modelPath = documentsPath.appendingPathComponent("\(modelName).gguf")
        
        if !FileManager.default.fileExists(atPath: modelPath.path) {
            print("Downloading model...")
            do {
                let downloadedURL = try await ModelDownloader.shared.downloadModel(
                    name: modelName,
                    progress: { progress in
                        print("Download progress: \(Int(progress * 100))%")
                    }
                )
                
                // Load model
                if llmManager?.loadModel(path: downloadedURL.path) == true {
                    print("Model loaded successfully")
                }
            } catch {
                print("Failed to download model: \(error)")
            }
        } else {
            // Model exists, load it
            if llmManager?.loadModel(path: modelPath.path) == true {
                print("Model loaded from cache")
            }
        }
    }
}
```

---

### Android Deployment

#### 1. Setup Android Project

```bash
# Create new Android project or use existing
# Add to app/build.gradle:

android {
    compileSdk 34
    
    defaultConfig {
        minSdk 26
        targetSdk 34
        
        ndk {
            abiFilters 'arm64-v8a'
        }
    }
    
    buildFeatures {
        viewBinding true
        compose true
    }
}

dependencies {
    // MediaPipe for LLM inference
    implementation 'com.google.mediapipe:tasks-genai:0.10.9'
    
    // Networking
    implementation 'com.squareup.retrofit2:retrofit:2.9.0'
    implementation 'com.squareup.retrofit2:converter-gson:2.9.0'
    
    // Coroutines
    implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3'
    
    // ViewModel
    implementation 'androidx.lifecycle:lifecycle-viewmodel-ktx:2.7.0'
    
    // Compose
    implementation platform('androidx.compose:compose-bom:2024.01.00')
    implementation 'androidx.compose.ui:ui'
    implementation 'androidx.compose.material3:material3'
}
```

#### 2. Download and Package Model

```bash
# Download model
wget https://huggingface.co/microsoft/Phi-3.5-mini-instruct-gguf/resolve/main/Phi-3.5-mini-instruct-Q4_K_M.gguf

# Convert to MediaPipe format (if needed)
# For llama.cpp: build Android library
cd llama.cpp
mkdir build-android
cd build-android

cmake .. \
    -DCMAKE_TOOLCHAIN_FILE=$ANDROID_NDK/build/cmake/android.toolchain.cmake \
    -DANDROID_ABI=arm64-v8a \
    -DANDROID_PLATFORM=android-26 \
    -DLLAMA_BUILD_EXAMPLES=OFF

make -j$(nproc)

# Copy to Android project
cp libllama.so ../android-app/app/src/main/jniLibs/arm64-v8a/
```

#### 3. Implement LLM Service

```kotlin
// LLMService.kt
class LLMService(private val context: Context) {
    private var localInference: LLMInference? = null
    private val cloudAPI = RetrofitBuilder.createGeminiAPI()
    
    suspend fun initialize() {
        withContext(Dispatchers.IO) {
            val modelFile = File(context.filesDir, "phi-3.5-mini-q4.bin")
            
            if (!modelFile.exists()) {
                downloadModel(modelFile)
            }
            
            localInference = LLMInference(context)
            localInference?.initialize(modelFile.absolutePath)
        }
    }
    
    private suspend fun downloadModel(destination: File) {
        val url = "https://huggingface.co/..." // Model URL
        
        // Implement download with progress
        val request = Request.Builder().url(url).build()
        val response = OkHttpClient().newCall(request).execute()
        
        response.body?.let { body ->
            destination.outputStream().use { output ->
                body.byteStream().copyTo(output)
            }
        }
    }
    
    suspend fun generate(prompt: String, useLocal: Boolean = true): String {
        return if (useLocal && localInference != null) {
            localInference!!.generate(prompt)
        } else {
            generateCloud(prompt)
        }
    }
    
    private suspend fun generateCloud(prompt: String): String {
        val request = GeminiRequest(
            contents = listOf(Content(parts = listOf(Part(text = prompt))))
        )
        
        val response = cloudAPI.generate(request)
        return response.candidates[0].content.parts[0].text
    }
}
```

---

### Web Deployment

#### 1. Setup Vite Project

```bash
npm create vite@latest edge-llm-web -- --template vanilla
cd edge-llm-web
npm install @xenova/transformers onnxruntime-web
```

#### 2. Configure Service Worker

```javascript
// sw.js - Service Worker for offline capability
const CACHE_NAME = 'llm-cache-v1';
const MODEL_CACHE = 'llm-models-v1';

const CACHED_RESOURCES = [
  '/',
  '/index.html',
  '/style.css',
  '/main.js',
];

// Install: cache static resources
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(CACHED_RESOURCES);
    })
  );
});

// Fetch: serve from cache, network fallback
self.addEventListener('fetch', (event) => {
  const { request } = event;
  
  // Cache models separately
  if (request.url.includes('huggingface.co')) {
    event.respondWith(
      caches.open(MODEL_CACHE).then((cache) => {
        return cache.match(request).then((response) => {
          if (response) return response;
          
          return fetch(request).then((networkResponse) => {
            cache.put(request, networkResponse.clone());
            return networkResponse;
          });
        });
      })
    );
    return;
  }
  
  // Regular resources
  event.respondWith(
    caches.match(request).then((response) => {
      return response || fetch(request);
    })
  );
});
```

#### 3. Main Application Setup

```javascript
// main.js
import { HybridLLMClient } from './hybrid-llm-client.js';

class App {
  constructor() {
    this.llmClient = new HybridLLMClient();
    this.isInitialized = false;
  }
  
  async init() {
    // Register service worker
    if ('serviceWorker' in navigator) {
      try {
        await navigator.serviceWorker.register('/sw.js');
        console.log('Service Worker registered');
      } catch (error) {
        console.error('Service Worker registration failed:', error);
      }
    }
    
    // Initialize LLM client
    await this.llmClient.initialize();
    this.isInitialized = true;
    
    this.setupUI();
  }
  
  setupUI() {
    const input = document.getElementById('prompt-input');
    const submitBtn = document.getElementById('submit-btn');
    const output = document.getElementById('output');
    const localToggle = document.getElementById('local-toggle');
    
    submitBtn.addEventListener('click', async () => {
      const prompt = input.value.trim();
      if (!prompt) return;
      
      submitBtn.disabled = true;
      output.textContent = 'Generating...';
      
      try {
        const response = await this.llmClient.generate(prompt, {
          forceLocal: localToggle.checked,
        });
        
        output.textContent = response;
      } catch (error) {
        output.textContent = `Error: ${error.message}`;
      } finally {
        submitBtn.disabled = false;
      }
    });
  }
}

// Start app
const app = new App();
app.init();
```

---

## Testing & Benchmarking

### Automated Test Suite

```python
# tests/test_performance.py
import time
import psutil
import json
from llm_edge_router import LLMEdgeRouter

class PerformanceTester:
    def __init__(self):
        self.router = LLMEdgeRouter()
        self.results = []
    
    def test_latency(self, prompt: str, iterations: int = 10):
        """Measure inference latency"""
        latencies = []
        
        for i in range(iterations):
            start = time.time()
            _ = self.router.route_request(prompt)
            end = time.time()
            
            latency_ms = (end - start) * 1000
            latencies.append(latency_ms)
        
        return {
            "avg_ms": sum(latencies) / len(latencies),
            "min_ms": min(latencies),
            "max_ms": max(latencies),
            "p95_ms": sorted(latencies)[int(0.95 * len(latencies))]
        }
    
    def test_memory(self, model_id: str):
        """Measure memory usage"""
        process = psutil.Process()
        
        mem_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Load model (simulated)
        model = self.router.models[model_id]
        
        mem_after = process.memory_info().rss / 1024 / 1024  # MB
        
        return {
            "before_mb": mem_before,
            "after_mb": mem_after,
            "delta_mb": mem_after - mem_before
        }
    
    def test_routing_accuracy(self, test_cases: list):
        """Test routing decisions"""
        correct = 0
        
        for case in test_cases:
            decision = self.router.route_request(
                prompt=case["prompt"],
                context_length=case.get("context", 0),
                task_type=case.get("task_type", "general")
            )
            
            expected_tier = case["expected_tier"]
            if decision.tier.value == expected_tier:
                correct += 1
        
        return {
            "accuracy": correct / len(test_cases),
            "correct": correct,
            "total": len(test_cases)
        }
    
    def run_full_benchmark(self):
        """Run comprehensive benchmark suite"""
        print("Running performance benchmarks...")
        
        # Test cases
        test_prompts = [
            ("Simple: What is 2+2?", "simple"),
            ("Medium: Write a Python function to sort a list", "medium"),
            ("Complex: Analyze the economic implications of AI", "complex")
        ]
        
        for prompt, complexity in test_prompts:
            print(f"\n{prompt}")
            latency_results = self.test_latency(prompt)
            print(f"  Latency: {latency_results['avg_ms']:.2f}ms (avg)")
            print(f"  P95: {latency_results['p95_ms']:.2f}ms")
        
        # Memory tests
        print("\nMemory Usage:")
        for model_id in ["phi-3.5-mini", "qwen2.5-3b"]:
            mem_results = self.test_memory(model_id)
            print(f"  {model_id}: {mem_results['delta_mb']:.2f}MB")
        
        # Routing accuracy
        routing_cases = [
            {"prompt": "Quick question", "expected_tier": "local"},
            {"prompt": "Comprehensive analysis needed", "expected_tier": "cloud_fast"},
            {"prompt": "Analyze document", "context": 100000, "expected_tier": "cloud_fast"}
        ]
        
        routing_results = self.test_routing_accuracy(routing_cases)
        print(f"\nRouting Accuracy: {routing_results['accuracy']*100:.1f}%")

if __name__ == "__main__":
    tester = PerformanceTester()
    tester.run_full_benchmark()
```

---

## Production Optimization

### 1. Model Caching Strategy

```python
# Implement intelligent model loading/unloading
class ModelCache:
    def __init__(self, max_models: int = 2):
        self.cache = {}
        self.max_models = max_models
        self.access_count = {}
    
    def load(self, model_id: str):
        if model_id in self.cache:
            self.access_count[model_id] += 1
            return self.cache[model_id]
        
        # Evict least-used model if cache full
        if len(self.cache) >= self.max_models:
            lru_model = min(self.access_count, key=self.access_count.get)
            del self.cache[lru_model]
            del self.access_count[lru_model]
        
        # Load new model
        model = load_model(model_id)  # Your loading logic
        self.cache[model_id] = model
        self.access_count[model_id] = 1
        
        return model
```

### 2. Battery Optimization

```python
# Adaptive inference based on battery level
def get_inference_config():
    battery = psutil.sensors_battery()
    
    if battery.percent < 20:
        return {
            "prefer_local": True,
            "max_tokens": 256,
            "quantization": "q4"
        }
    elif battery.percent < 50:
        return {
            "prefer_local": True,
            "max_tokens": 512,
            "quantization": "q4"
        }
    else:
        return {
            "prefer_local": False,
            "max_tokens": 1024,
            "quantization": "q5"
        }
```

### 3. Network-Aware Routing

```python
# Measure network quality and adjust
import speedtest

def check_network_quality():
    try:
        st = speedtest.Speedtest()
        download_speed = st.download() / 1_000_000  # Mbps
        latency = st.results.ping
        
        if download_speed < 1 or latency > 200:
            return "poor"
        elif download_speed < 5 or latency > 100:
            return "fair"
        else:
            return "good"
    except:
        return "unknown"

# Use in routing
def route_with_network_awareness(prompt, router):
    quality = check_network_quality()
    
    if quality in ["poor", "unknown"]:
        return router.route_request(prompt, force_offline=True)
    else:
        return router.route_request(prompt)
```

---

## Deployment Checklist

### Pre-Deployment
- [ ] Test all models locally
- [ ] Run benchmark suite
- [ ] Verify API keys are secure
- [ ] Check model licenses
- [ ] Test offline mode
- [ ] Measure memory usage
- [ ] Profile battery impact

### iOS Deployment
- [ ] App Store compliance check
- [ ] TestFlight beta testing
- [ ] Performance profiling on device
- [ ] Memory leak testing
- [ ] Background mode testing

### Android Deployment
- [ ] Google Play compliance
- [ ] Test on multiple devices
- [ ] Battery optimization verification
- [ ] APK size optimization
- [ ] ProGuard configuration

### Web Deployment
- [ ] Service worker testing
- [ ] Cross-browser compatibility
- [ ] PWA manifest
- [ ] HTTPS configuration
- [ ] CDN setup for models

---

## Production Monitoring

```python
# monitoring.py
import logging
from datetime import datetime
from dataclasses import dataclass, asdict
import json

@dataclass
class InferenceMetrics:
    timestamp: str
    model_id: str
    tier: str
    latency_ms: float
    tokens_generated: int
    success: bool
    error: str = None

class MetricsLogger:
    def __init__(self, log_file: str = "metrics.jsonl"):
        self.log_file = log_file
        
    def log_inference(self, metrics: InferenceMetrics):
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(asdict(metrics)) + '\n')
    
    def get_stats(self, last_n_hours: int = 24):
        # Analyze metrics
        stats = {
            "total_requests": 0,
            "avg_latency_ms": 0,
            "success_rate": 0,
            "tier_distribution": {}
        }
        
        # Implementation...
        
        return stats
```

This guide provides everything needed for production deployment of edge LLMs with hybrid cloud fallback!
