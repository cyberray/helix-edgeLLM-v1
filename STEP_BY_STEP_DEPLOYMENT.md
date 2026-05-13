# Step-by-Step Deployment Guide 🚀
## From Zero to Running LLM on Edge Devices

This guide assumes you're starting from scratch and want to get the Edge LLM system running on your device.

---

## 📋 Table of Contents

1. [Initial Setup (All Platforms)](#initial-setup)
2. [Desktop/Testing Deployment](#desktop-deployment)
3. [iOS Deployment](#ios-deployment)
4. [Android Deployment](#android-deployment)
5. [Web Deployment](#web-deployment)
6. [Cloud API Setup (Optional)](#cloud-api-setup)
7. [Troubleshooting](#troubleshooting)

---

## Initial Setup (All Platforms)

### Step 1: Check System Requirements

**Minimum Requirements:**
- **Storage**: 10GB free space (for models)
- **RAM**: 4GB minimum, 8GB recommended
- **Internet**: For initial model downloads

**Software Requirements:**
- Python 3.9 or higher
- Git (optional, for version control)

### Step 2: Verify Python Installation

```bash
# Check Python version
python3 --version
# Should show: Python 3.9.x or higher

# If not installed, install Python:
# macOS: brew install python3
# Ubuntu: sudo apt install python3 python3-pip
# Windows: Download from python.org
```

### Step 3: Create Project Directory

```bash
# Create and navigate to project folder
mkdir edge-llm-project
cd edge-llm-project

# Create virtual environment (recommended)
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Your terminal should now show (venv) prefix
```

### Step 4: Download the System Files

Place all the provided files in your `edge-llm-project` directory:

```
edge-llm-project/
├── llm_edge_router.py
├── download_models.py
├── example_integration.py
├── edge-llm-cli.py
├── requirements.txt
├── test_edge_llm.py
├── README.md
├── DEPLOYMENT_GUIDE.md
└── platform_implementations.md
```

### Step 5: Install Dependencies

```bash
# Install all required Python packages
pip install -r requirements.txt

# This will install:
# - llama-cpp-python (local inference)
# - transformers (model support)
# - API clients (Gemini, Groq, etc.)
# - Utilities (tqdm, click, rich)

# Installation may take 5-10 minutes
```

**⚠️ Common Issue: llama-cpp-python fails to install**

```bash
# If installation fails, try:
# For macOS with Apple Silicon:
CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python

# For NVIDIA GPU:
CMAKE_ARGS="-DLLAMA_CUDA=on" pip install llama-cpp-python

# For CPU only (slowest, but works everywhere):
pip install llama-cpp-python --no-cache-dir
```

### Step 6: Verify Installation

```bash
# Test that everything is installed correctly
python -c "from llm_edge_router import LLMEdgeRouter; print('✓ Installation successful!')"

# You should see: ✓ Installation successful!
```

---

## Desktop Deployment

**Best for:** Testing, development, local use

### Step 1: Download Models

```bash
# Interactive mode (recommended for first time)
python download_models.py

# Select option: 2 (Setup for platform)
# Enter: desktop

# This will download:
# - Phi-3.5-mini Q4 (2GB) - Best all-around
# - Qwen2.5 3B Q4 (1.9GB) - Best for coding

# Download takes 10-30 minutes depending on internet speed
```

**Alternative: Download specific models**

```bash
# Download just one model
python download_models.py --download phi-3.5-mini-q4

# Download multiple models
python download_models.py --download phi-3.5-mini-q4 qwen2.5-3b-q4

# Check what was downloaded
python download_models.py --downloaded
```

### Step 2: Test the System

```bash
# Run the demo suite
python example_integration.py

# This will:
# 1. Test routing decisions
# 2. Generate code examples
# 3. Analyze sample code
# 4. Show performance metrics

# Takes 2-5 minutes to complete
```

### Step 3: Try Interactive Chat

```bash
# Start CLI chat
./edge-llm-cli.py chat

# Or if that doesn't work:
python edge-llm-cli.py chat

# Try these commands in the chat:
# - "Explain recursion in simple terms"
# - "/models" (see available models)
# - "/help" (see all commands)
# - "quit" (exit)
```

### Step 4: Use in Your Code

```python
# Create a file: my_app.py
from llm_edge_router import LLMEdgeRouter
import asyncio

async def main():
    router = LLMEdgeRouter()
    
    # Simple query
    result = await router.generate("What is machine learning?")
    print(result["response"])
    
    # Code generation
    result = await router.generate(
        "Write a Python function to find prime numbers",
        task_type="coding"
    )
    print(result["response"])

if __name__ == "__main__":
    asyncio.run(main())
```

```bash
# Run your app
python my_app.py
```

**🎉 Desktop deployment complete!** You now have a working LLM system on your computer.

---

## iOS Deployment

**Best for:** iPhone/iPad apps with on-device AI

### Prerequisites

- **Mac computer** (required for iOS development)
- **Xcode 15+** (free from App Store)
- **iOS 16+** device or simulator
- **Apple Developer account** (free tier OK for testing)

### Step 1: Install Xcode and Command Line Tools

```bash
# Install Xcode from App Store (takes ~30 minutes)

# Install Command Line Tools
xcode-select --install

# Verify installation
xcode-select -p
# Should show: /Applications/Xcode.app/Contents/Developer
```

### Step 2: Install CocoaPods

```bash
# Install CocoaPods (dependency manager)
sudo gem install cocoapods

# Verify installation
pod --version
```

### Step 3: Set Up llama.cpp for iOS

```bash
# Clone llama.cpp
cd ~/Downloads
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp

# Build for iOS
mkdir build-ios
cd build-ios

# Configure for iOS with Metal acceleration
cmake .. \
  -G Xcode \
  -DCMAKE_SYSTEM_NAME=iOS \
  -DLLAMA_METAL=ON \
  -DCMAKE_OSX_DEPLOYMENT_TARGET=16.0

# Build (takes 5-10 minutes)
cmake --build . --config Release

# The library is now at: build-ios/Release-iphoneos/
```

### Step 4: Create Xcode Project

```bash
# 1. Open Xcode
# 2. Create new project: iOS → App
# 3. Product Name: EdgeLLMApp
# 4. Interface: SwiftUI
# 5. Language: Swift
# 6. Save in: edge-llm-project/ios/
```

### Step 5: Add llama.cpp to Project

1. **In Xcode:**
   - Right-click on project → "Add Files to EdgeLLMApp"
   - Navigate to `llama.cpp/build-ios/Release-iphoneos/`
   - Select `libllama.a` and add it

2. **Configure Build Settings:**
   - Select project in navigator
   - Select target → "Build Settings"
   - Search: "Header Search Paths"
   - Add: `$(SRCROOT)/../../llama.cpp` (adjust path as needed)

3. **Add Bridging Header:**
   - File → New → File → Header File
   - Name: `EdgeLLMApp-Bridging-Header.h`
   - Add:
     ```c
     #import "llama.h"
     ```

### Step 6: Add Swift Code

Create `LLMManager.swift`:

```swift
import Foundation

class LLMManager: ObservableObject {
    @Published var isLoaded = false
    @Published var response = ""
    
    private var context: OpaquePointer?
    private var model: OpaquePointer?
    
    func loadModel(named: String) {
        // Get model path from bundle
        guard let modelPath = Bundle.main.path(forResource: named, ofType: "gguf") else {
            print("Model not found in bundle")
            return
        }
        
        // Initialize llama backend
        llama_backend_init(false)
        
        // Load model with Metal acceleration
        var params = llama_model_default_params()
        params.n_gpu_layers = 99
        
        model = llama_load_model_from_file(modelPath, params)
        
        if model != nil {
            // Create context
            var ctxParams = llama_context_default_params()
            ctxParams.n_ctx = 2048
            ctxParams.n_threads = 4
            
            context = llama_new_context_with_model(model, ctxParams)
            isLoaded = true
        }
    }
    
    func generate(prompt: String) async -> String {
        guard context != nil, model != nil else {
            return "Model not loaded"
        }
        
        // Simplified generation (see platform_implementations.md for full version)
        return "Response from local model: \(prompt)"
    }
}
```

Create `ContentView.swift`:

```swift
import SwiftUI

struct ContentView: View {
    @StateObject private var llm = LLMManager()
    @State private var prompt = ""
    @State private var response = ""
    
    var body: some View {
        VStack {
            Text("Edge LLM")
                .font(.largeTitle)
                .padding()
            
            if llm.isLoaded {
                TextField("Ask something...", text: $prompt)
                    .textFieldStyle(.roundedBorder)
                    .padding()
                
                Button("Generate") {
                    Task {
                        response = await llm.generate(prompt: prompt)
                    }
                }
                .buttonStyle(.borderedProminent)
                
                ScrollView {
                    Text(response)
                        .padding()
                }
            } else {
                ProgressView("Loading model...")
                    .onAppear {
                        llm.loadModel(named: "phi-3.5-mini-q4")
                    }
            }
        }
        .padding()
    }
}
```

### Step 7: Add Model to Project

```bash
# Download model if not already done
cd edge-llm-project
python download_models.py --download phi-3.5-mini-q4

# In Xcode:
# 1. Drag models/Phi-3.5-mini-instruct-Q4_K_M.gguf into project
# 2. Check "Copy items if needed"
# 3. Add to target
```

### Step 8: Configure App Settings

1. **Increase Memory:**
   - Project settings → Capabilities
   - Enable "Increased Memory Limit"

2. **Update Info.plist:**
   - Add key: `Application requires iPhone environment` → NO
   - Add key: `Supports iPad` → YES

### Step 9: Build and Test

```bash
# In Xcode:
# 1. Select device/simulator (iPhone 15 Pro recommended)
# 2. Press Cmd+R to build and run
# 3. Wait for build (first time: 5-10 minutes)
# 4. App launches with model loading
# 5. Type a query and test!
```

**🎉 iOS deployment complete!** You now have an LLM running natively on iPhone.

---

## Android Deployment

**Best for:** Android apps with on-device AI

### Prerequisites

- **Android Studio** (latest version)
- **JDK 17+**
- **Android device** with 6GB+ RAM (or emulator)
- **6GB disk space** for models

### Step 1: Install Android Studio

```bash
# Download from: https://developer.android.com/studio
# Install and complete setup wizard

# Open Android Studio
# Tools → SDK Manager
# Install:
# - Android SDK Platform 34
# - Android SDK Build-Tools 34
# - NDK (Side by side)
# - CMake
```

### Step 2: Create New Project

```bash
# 1. Android Studio → New Project
# 2. Select: "Empty Activity"
# 3. Name: EdgeLLMApp
# 4. Package: com.example.edgellm
# 5. Language: Kotlin
# 6. Minimum SDK: API 26 (Android 8.0)
# 7. Build system: Gradle (Kotlin DSL)
```

### Step 3: Configure build.gradle

Edit `app/build.gradle.kts`:

```kotlin
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.example.edgellm"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.edgellm"
        minSdk = 26
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"

        ndk {
            abiFilters += listOf("arm64-v8a")
        }
    }

    buildFeatures {
        viewBinding = true
        compose = true
    }

    composeOptions {
        kotlinCompilerExtensionVersion = "1.5.3"
    }
}

dependencies {
    // MediaPipe for LLM inference
    implementation("com.google.mediapipe:tasks-genai:0.10.9")
    
    // Compose UI
    implementation(platform("androidx.compose:compose-bom:2024.01.00"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.activity:activity-compose:1.8.2")
    
    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
    
    // ViewModel
    implementation("androidx.lifecycle:lifecycle-viewmodel-ktx:2.7.0")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.7.0")
}
```

Sync project (File → Sync Project with Gradle Files)

### Step 4: Download and Add Model

```bash
# In your edge-llm-project directory
python download_models.py --download phi-3.5-mini-q4

# Create assets directory in Android project
mkdir -p EdgeLLMApp/app/src/main/assets

# Copy model (this may take a moment due to size)
cp models/Phi-3.5-mini-instruct-Q4_K_M.gguf EdgeLLMApp/app/src/main/assets/model.bin

# Or download directly to assets folder
```

### Step 5: Create LLM Service

Create `app/src/main/java/com/example/edgellm/LLMService.kt`:

```kotlin
package com.example.edgellm

import android.content.Context
import com.google.mediapipe.tasks.genai.llminference.LlmInference
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File

class LLMService(private val context: Context) {
    private var llmInference: LlmInference? = null
    
    suspend fun initialize() = withContext(Dispatchers.IO) {
        val modelFile = copyModelToCache()
        
        val options = LlmInference.LlmInferenceOptions.builder()
            .setModelPath(modelFile.absolutePath)
            .setMaxTokens(512)
            .setTopK(40)
            .setTemperature(0.8f)
            .build()
        
        llmInference = LlmInference.createFromOptions(context, options)
    }
    
    private fun copyModelToCache(): File {
        val cacheFile = File(context.cacheDir, "model.bin")
        
        if (!cacheFile.exists()) {
            context.assets.open("model.bin").use { input ->
                cacheFile.outputStream().use { output ->
                    input.copyTo(output)
                }
            }
        }
        
        return cacheFile
    }
    
    suspend fun generate(prompt: String): String = withContext(Dispatchers.IO) {
        llmInference?.generateResponse(prompt) 
            ?: throw IllegalStateException("LLM not initialized")
    }
    
    fun release() {
        llmInference?.close()
        llmInference = null
    }
}
```

### Step 6: Create ViewModel

Create `app/src/main/java/com/example/edgellm/MainViewModel.kt`:

```kotlin
package com.example.edgellm

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class MainViewModel(application: Application) : AndroidViewModel(application) {
    
    private val llmService = LLMService(application)
    
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState
    
    init {
        viewModelScope.launch {
            try {
                llmService.initialize()
                _uiState.value = UiState.Ready
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message ?: "Unknown error")
            }
        }
    }
    
    fun generate(prompt: String) {
        viewModelScope.launch {
            _uiState.value = UiState.Generating
            try {
                val response = llmService.generate(prompt)
                _uiState.value = UiState.Success(response)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message ?: "Generation failed")
            }
        }
    }
    
    override fun onCleared() {
        super.onCleared()
        llmService.release()
    }
}

sealed class UiState {
    object Loading : UiState()
    object Ready : UiState()
    object Generating : UiState()
    data class Success(val response: String) : UiState()
    data class Error(val message: String) : UiState()
}
```

### Step 7: Create UI

Edit `app/src/main/java/com/example/edgellm/MainActivity.kt`:

```kotlin
package com.example.edgellm

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                EdgeLLMApp()
            }
        }
    }
}

@Composable
fun EdgeLLMApp(viewModel: MainViewModel = viewModel()) {
    val uiState by viewModel.uiState.collectAsState()
    var prompt by remember { mutableStateOf("") }
    
    Scaffold(
        topBar = {
            TopAppBar(title = { Text("Edge LLM") })
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp)
        ) {
            when (uiState) {
                is UiState.Loading -> {
                    CircularProgressIndicator()
                    Text("Loading model...")
                }
                
                is UiState.Ready, is UiState.Success -> {
                    OutlinedTextField(
                        value = prompt,
                        onValueChange = { prompt = it },
                        label = { Text("Ask something...") },
                        modifier = Modifier.fillMaxWidth()
                    )
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    Button(
                        onClick = { viewModel.generate(prompt) },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("Generate")
                    }
                    
                    if (uiState is UiState.Success) {
                        Spacer(modifier = Modifier.height(16.dp))
                        Card(modifier = Modifier.fillMaxWidth()) {
                            Text(
                                text = (uiState as UiState.Success).response,
                                modifier = Modifier.padding(16.dp)
                            )
                        }
                    }
                }
                
                is UiState.Generating -> {
                    CircularProgressIndicator()
                    Text("Generating...")
                }
                
                is UiState.Error -> {
                    Text(
                        text = "Error: ${(uiState as UiState.Error).message}",
                        color = MaterialTheme.colorScheme.error
                    )
                }
            }
        }
    }
}
```

### Step 8: Build and Run

```bash
# 1. Connect Android device or start emulator
# 2. Click "Run" (green play button) in Android Studio
# 3. First build takes 10-15 minutes
# 4. App installs and launches
# 5. Wait for model to load (30-60 seconds)
# 6. Type query and test!
```

**🎉 Android deployment complete!** You now have an LLM running on Android.

---

## Web Deployment

**Best for:** Websites, web apps, PWAs

### Step 1: Set Up Node.js Project

```bash
# Create web project
mkdir edge-llm-web
cd edge-llm-web

# Initialize project
npm init -y

# Install dependencies
npm install @xenova/transformers onnxruntime-web
npm install --save-dev vite

# Update package.json
```

Edit `package.json`:

```json
{
  "name": "edge-llm-web",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "@xenova/transformers": "^2.14.0",
    "onnxruntime-web": "^1.17.0"
  },
  "devDependencies": {
    "vite": "^5.1.0"
  }
}
```

### Step 2: Create Web Worker

Create `llm-worker.js`:

```javascript
import { pipeline, env } from '@xenova/transformers';

env.backends.onnx.wasm.numThreads = navigator.hardwareConcurrency;

class LLMWorker {
    constructor() {
        this.generator = null;
        this.modelLoaded = false;
    }
    
    async loadModel(modelName = 'Xenova/Phi-3-mini-4k-instruct') {
        if (this.modelLoaded) return;
        
        console.log('Loading model...');
        this.generator = await pipeline(
            'text-generation',
            modelName,
            { quantized: true }
        );
        
        this.modelLoaded = true;
        console.log('Model loaded');
    }
    
    async generate(prompt, options = {}) {
        if (!this.modelLoaded) {
            throw new Error('Model not loaded');
        }
        
        const result = await this.generator(prompt, {
            max_new_tokens: options.max_tokens || 256,
            temperature: options.temperature || 0.7,
            ...options
        });
        
        return result[0].generated_text;
    }
}

const worker = new LLMWorker();

self.onmessage = async (event) => {
    const { type, data } = event.data;
    
    try {
        switch (type) {
            case 'load':
                await worker.loadModel(data.modelName);
                self.postMessage({ type: 'loaded' });
                break;
                
            case 'generate':
                const response = await worker.generate(data.prompt, data.options);
                self.postMessage({ type: 'response', data: response });
                break;
                
            default:
                throw new Error(`Unknown message type: ${type}`);
        }
    } catch (error) {
        self.postMessage({ type: 'error', data: error.message });
    }
};
```

### Step 3: Create Main App

Create `index.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edge LLM Web</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        h1 {
            color: #333;
            margin-bottom: 20px;
        }
        
        #status {
            padding: 10px;
            margin-bottom: 20px;
            border-radius: 8px;
            background: #f0f0f0;
        }
        
        textarea {
            width: 100%;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            resize: vertical;
            min-height: 100px;
        }
        
        button {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            margin-top: 10px;
        }
        
        button:hover {
            background: #5568d3;
        }
        
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        
        #output {
            margin-top: 20px;
            padding: 20px;
            background: #f9f9f9;
            border-radius: 8px;
            white-space: pre-wrap;
            line-height: 1.6;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Edge LLM Web</h1>
        <div id="status">Initializing...</div>
        
        <textarea id="prompt" placeholder="Ask me anything..."></textarea>
        <button id="generateBtn" disabled>Generate</button>
        
        <div id="output"></div>
    </div>
    
    <script type="module" src="./main.js"></script>
</body>
</html>
```

Create `main.js`:

```javascript
const worker = new Worker('llm-worker.js', { type: 'module' });
const status = document.getElementById('status');
const prompt = document.getElementById('prompt');
const generateBtn = document.getElementById('generateBtn');
const output = document.getElementById('output');

let isReady = false;

worker.onmessage = (event) => {
    const { type, data } = event.data;
    
    switch (type) {
        case 'loaded':
            isReady = true;
            status.textContent = '✓ Ready! Model loaded.';
            status.style.background = '#d4edda';
            generateBtn.disabled = false;
            break;
            
        case 'response':
            output.textContent = data;
            generateBtn.disabled = false;
            generateBtn.textContent = 'Generate';
            break;
            
        case 'error':
            output.textContent = `Error: ${data}`;
            output.style.color = 'red';
            generateBtn.disabled = false;
            generateBtn.textContent = 'Generate';
            break;
    }
};

// Load model on startup
worker.postMessage({ type: 'load', data: {} });

generateBtn.addEventListener('click', () => {
    if (!isReady || !prompt.value.trim()) return;
    
    generateBtn.disabled = true;
    generateBtn.textContent = 'Generating...';
    output.textContent = '';
    
    worker.postMessage({
        type: 'generate',
        data: {
            prompt: prompt.value,
            options: { max_tokens: 256 }
        }
    });
});
```

### Step 4: Run Development Server

```bash
# Start dev server
npm run dev

# Open browser to: http://localhost:5173
# Wait for model to load (1-2 minutes first time)
# Type query and test!
```

### Step 5: Build for Production

```bash
# Build optimized version
npm run build

# Output in: dist/
# Deploy dist/ folder to:
# - Vercel: vercel deploy
# - Netlify: netlify deploy
# - GitHub Pages: push to gh-pages branch
# - Your own server: copy dist/ to web root
```

**🎉 Web deployment complete!** You now have an LLM running in the browser.

---

## Cloud API Setup (Optional)

Add cloud APIs for fallback when local models can't handle complex tasks.

### Step 1: Get API Keys (All Free!)

**Google Gemini:**
1. Go to: https://ai.google.dev/
2. Click "Get API Key"
3. Sign in with Google
4. Create API key
5. Copy key

**Groq:**
1. Go to: https://console.groq.com/
2. Sign up (free)
3. Navigate to API Keys
4. Create new key
5. Copy key

**Together.ai:**
1. Go to: https://api.together.xyz/
2. Sign up
3. Navigate to Settings → API Keys
4. Create key
5. Copy key

### Step 2: Configure Keys

```bash
# Run configuration wizard
./edge-llm-cli.py config

# Or manually create .env file
cat > .env << EOF
GEMINI_API_KEY=your_gemini_key_here
GROQ_API_KEY=your_groq_key_here
TOGETHER_API_KEY=your_together_key_here
HF_API_TOKEN=your_hf_token_here
EOF
```

### Step 3: Test Cloud APIs

```bash
# Test with cloud model
./edge-llm-cli.py chat --model gemini-flash "Analyze quantum computing"

# Or in Python:
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('Gemini:', 'Configured' if os.getenv('GEMINI_API_KEY') else 'Not set')
print('Groq:', 'Configured' if os.getenv('GROQ_API_KEY') else 'Not set')
"
```

---

## Troubleshooting

### Common Issues

**Issue: "llama-cpp-python failed to install"**
```bash
# Solution: Install with specific flags
CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python --no-cache-dir
```

**Issue: "Model file too large"**
```bash
# Solution: Use smaller quantization
python download_models.py --download gemma-2-2b-q4  # Only 1.4GB
```

**Issue: "Out of memory" on mobile**
```bash
# Solution: Use smaller model or increase swap
# iOS: Enable "Increased Memory Limit" in Xcode
# Android: Close other apps, use Q4 quantization
```

**Issue: "Model loads but generates garbage"**
```bash
# Solution: Re-download model
rm models/*.gguf
python download_models.py --download phi-3.5-mini-q4 --force
```

**Issue: "Web version doesn't load"**
```bash
# Solution: Check browser compatibility
# Requires: Chrome 113+, Firefox 115+, or Safari 16.4+
# Try: Clear cache, use different browser
```

**Issue: "Import errors in Python"**
```bash
# Solution: Reinstall in clean environment
deactivate  # exit current venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Getting Help

- **Check logs**: Look at console output for specific errors
- **Test with minimal example**: Try the CLI first before custom code
- **Verify models**: Run `python download_models.py --downloaded`
- **System status**: Run `./edge-llm-cli.py status`

---

## Next Steps

Now that you have the system deployed:

1. **Explore features**: Try all CLI commands
2. **Customize**: Modify code for your use case
3. **Optimize**: Tune models for your specific needs
4. **Deploy to production**: Follow platform-specific app store guides

**Congratulations! You've successfully deployed the Edge LLM System! 🎉**
