# Platform-Specific LLM Deployment Examples

## iOS Deployment with llama.cpp and Swift

### 1. Setup llama.cpp for iOS

```swift
// LLMManager.swift
import Foundation

class LLMManager {
    private var context: OpaquePointer?
    private var model: OpaquePointer?
    
    init() {
        // Initialize llama.cpp
        llama_backend_init(false)
    }
    
    func loadModel(path: String, contextSize: Int32 = 2048) -> Bool {
        // Model parameters
        var params = llama_model_default_params()
        params.n_gpu_layers = 99 // Use Metal for GPU acceleration
        
        // Load model
        model = llama_load_model_from_file(path, params)
        guard model != nil else {
            print("Failed to load model")
            return false
        }
        
        // Create context
        var ctxParams = llama_context_default_params()
        ctxParams.n_ctx = UInt32(contextSize)
        ctxParams.n_threads = 4
        
        context = llama_new_context_with_model(model, ctxParams)
        guard context != nil else {
            print("Failed to create context")
            return false
        }
        
        print("Model loaded successfully")
        return true
    }
    
    func generate(prompt: String, maxTokens: Int32 = 512) -> String {
        guard let context = context, let model = model else {
            return "Model not loaded"
        }
        
        // Tokenize prompt
        let tokens = tokenize(prompt: prompt)
        
        // Evaluate prompt
        llama_batch_clear(&batch)
        for (i, token) in tokens.enumerated() {
            llama_batch_add(&batch, token, Int32(i), [0], false)
        }
        
        if llama_decode(context, batch) != 0 {
            return "Failed to evaluate prompt"
        }
        
        // Generate tokens
        var result = ""
        var nCur = tokens.count
        
        for _ in 0..<maxTokens {
            let logits = llama_get_logits_ith(context, -1)
            let nVocab = llama_n_vocab(model)
            
            // Sample next token
            let nextToken = sampleToken(logits: logits, vocabSize: nVocab)
            
            // Check for end of generation
            if nextToken == llama_token_eos(model) {
                break
            }
            
            // Decode token to text
            let text = decodeToken(token: nextToken)
            result += text
            
            // Prepare for next iteration
            llama_batch_clear(&batch)
            llama_batch_add(&batch, nextToken, Int32(nCur), [0], true)
            nCur += 1
            
            if llama_decode(context, batch) != 0 {
                break
            }
        }
        
        return result
    }
    
    private func tokenize(prompt: String) -> [llama_token] {
        guard let model = model else { return [] }
        
        let maxTokens = prompt.utf8.count + 1
        var tokens = [llama_token](repeating: 0, count: maxTokens)
        let nTokens = llama_tokenize(
            model,
            prompt,
            Int32(prompt.utf8.count),
            &tokens,
            Int32(maxTokens),
            true,
            false
        )
        
        return Array(tokens.prefix(Int(nTokens)))
    }
    
    private func sampleToken(logits: UnsafePointer<Float>?, vocabSize: Int32) -> llama_token {
        // Simple greedy sampling
        var maxLogit: Float = -Float.infinity
        var maxToken: llama_token = 0
        
        for i in 0..<Int(vocabSize) {
            if let logit = logits?[i], logit > maxLogit {
                maxLogit = logit
                maxToken = llama_token(i)
            }
        }
        
        return maxToken
    }
    
    private func decodeToken(token: llama_token) -> String {
        guard let model = model else { return "" }
        
        var buffer = [CChar](repeating: 0, count: 32)
        llama_token_to_piece(model, token, &buffer, Int32(buffer.count))
        
        return String(cString: buffer)
    }
    
    deinit {
        if context != nil {
            llama_free(context)
        }
        if model != nil {
            llama_free_model(model)
        }
        llama_backend_free()
    }
}
```

### 2. Model Download Manager

```swift
// ModelDownloader.swift
import Foundation

class ModelDownloader {
    static let shared = ModelDownloader()
    
    private let modelURLs = [
        "phi-3.5-mini-q4": "https://huggingface.co/microsoft/Phi-3.5-mini-instruct-gguf/resolve/main/Phi-3.5-mini-instruct-Q4_K_M.gguf",
        "qwen2.5-3b-q4": "https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf",
    ]
    
    func downloadModel(name: String, progress: @escaping (Double) -> Void) async throws -> URL {
        guard let urlString = modelURLs[name],
              let url = URL(string: urlString) else {
            throw NSError(domain: "Invalid model name", code: 400)
        }
        
        let documentsPath = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let destinationURL = documentsPath.appendingPathComponent("\(name).gguf")
        
        // Check if already downloaded
        if FileManager.default.fileExists(atPath: destinationURL.path) {
            return destinationURL
        }
        
        // Download
        let (tempURL, response) = try await URLSession.shared.download(from: url) { bytesDownloaded, totalBytes in
            let p = Double(bytesDownloaded) / Double(totalBytes)
            DispatchQueue.main.async {
                progress(p)
            }
        }
        
        try FileManager.default.moveItem(at: tempURL, to: destinationURL)
        return destinationURL
    }
}
```

---

## Android Deployment with MediaPipe

### 1. Setup MediaPipe LLM Inference

```kotlin
// LLMInference.kt
import com.google.mediapipe.tasks.genai.llminference.LlmInference
import android.content.Context
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow

class LLMInference(private val context: Context) {
    private var llmInference: LlmInference? = null
    
    suspend fun initialize(modelPath: String) {
        val options = LlmInference.LlmInferenceOptions.builder()
            .setModelPath(modelPath)
            .setMaxTokens(512)
            .setTopK(40)
            .setTemperature(0.8f)
            .setRandomSeed(0)
            .build()
        
        llmInference = LlmInference.createFromOptions(context, options)
    }
    
    fun generateStream(prompt: String): Flow<String> = flow {
        llmInference?.let { inference ->
            inference.generateResponseAsync(prompt).addListener(
                { partialResult ->
                    emit(partialResult ?: "")
                },
                { error ->
                    throw error
                }
            )
        } ?: throw IllegalStateException("LLM not initialized")
    }
    
    suspend fun generate(prompt: String): String {
        return llmInference?.generateResponse(prompt) 
            ?: throw IllegalStateException("LLM not initialized")
    }
    
    fun release() {
        llmInference?.close()
        llmInference = null
    }
}
```

### 2. ViewModel with Hybrid Strategy

```kotlin
// LLMViewModel.kt
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

class LLMViewModel(
    private val context: Context
) : ViewModel() {
    
    private val localInference = LLMInference(context)
    private val cloudAPI = createCloudAPI()
    
    private val _response = MutableStateFlow("")
    val response: StateFlow<String> = _response
    
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading
    
    suspend fun initializeLocalModel(modelName: String) {
        val modelPath = "${context.filesDir}/$modelName.gguf"
        localInference.initialize(modelPath)
    }
    
    fun generateResponse(
        prompt: String,
        useLocal: Boolean = true,
        taskComplexity: TaskComplexity = TaskComplexity.MEDIUM
    ) {
        viewModelScope.launch {
            _isLoading.value = true
            _response.value = ""
            
            try {
                // Routing logic
                val shouldUseLocal = when {
                    useLocal -> true
                    !isNetworkAvailable() -> true
                    taskComplexity == TaskComplexity.SIMPLE -> true
                    isBatterySaverEnabled() -> true
                    else -> false
                }
                
                if (shouldUseLocal) {
                    generateLocal(prompt)
                } else {
                    generateCloud(prompt)
                }
            } catch (e: Exception) {
                _response.value = "Error: ${e.message}"
            } finally {
                _isLoading.value = false
            }
        }
    }
    
    private suspend fun generateLocal(prompt: String) {
        localInference.generateStream(prompt).collect { partial ->
            _response.value += partial
        }
    }
    
    private suspend fun generateCloud(prompt: String) {
        val request = CloudRequest(
            model = "gemini-1.5-flash",
            messages = listOf(Message("user", prompt))
        )
        
        val result = cloudAPI.generate(request)
        _response.value = result.choices[0].message.content
    }
    
    private fun isNetworkAvailable(): Boolean {
        val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) 
            as ConnectivityManager
        val network = connectivityManager.activeNetwork ?: return false
        val capabilities = connectivityManager.getNetworkCapabilities(network) ?: return false
        return capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
    }
    
    private fun isBatterySaverEnabled(): Boolean {
        val powerManager = context.getSystemService(Context.POWER_SERVICE) as PowerManager
        return powerManager.isPowerSaveMode
    }
    
    override fun onCleared() {
        super.onCleared()
        localInference.release()
    }
}

enum class TaskComplexity {
    SIMPLE, MEDIUM, COMPLEX
}
```

---

## Web Deployment with Transformers.js

### 1. Web Worker for Model Inference

```javascript
// llm-worker.js
import { pipeline, env } from '@xenova/transformers';

// Configure for WebGPU if available
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
            { 
                quantized: true,
                device: 'webgpu' // Falls back to WASM if WebGPU unavailable
            }
        );
        
        this.modelLoaded = true;
        console.log('Model loaded successfully');
    }
    
    async generate(prompt, options = {}) {
        if (!this.modelLoaded) {
            throw new Error('Model not loaded');
        }
        
        const defaultOptions = {
            max_new_tokens: 512,
            temperature: 0.7,
            top_k: 50,
            top_p: 0.95,
            do_sample: true,
            ...options
        };
        
        const result = await this.generator(prompt, defaultOptions);
        return result[0].generated_text;
    }
    
    async generateStream(prompt, onToken) {
        if (!this.modelLoaded) {
            throw new Error('Model not loaded');
        }
        
        // Stream tokens as they're generated
        const stream = await this.generator(prompt, {
            max_new_tokens: 512,
            temperature: 0.7,
            callback_function: (tokens) => {
                onToken(tokens);
            }
        });
        
        return stream;
    }
}

// Worker message handling
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
                self.postMessage({ 
                    type: 'response', 
                    data: response 
                });
                break;
                
            case 'stream':
                await worker.generateStream(
                    data.prompt,
                    (tokens) => {
                        self.postMessage({ 
                            type: 'token', 
                            data: tokens 
                        });
                    }
                );
                self.postMessage({ type: 'complete' });
                break;
                
            default:
                throw new Error(`Unknown message type: ${type}`);
        }
    } catch (error) {
        self.postMessage({ 
            type: 'error', 
            data: error.message 
        });
    }
};
```

### 2. Main Application with Hybrid Strategy

```javascript
// hybrid-llm-client.js
class HybridLLMClient {
    constructor() {
        this.worker = null;
        this.localModelLoaded = false;
        this.preferLocal = true;
        
        // Cloud API endpoints
        this.cloudAPIs = {
            gemini: 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent',
            groq: 'https://api.groq.com/openai/v1/chat/completions',
        };
    }
    
    async initialize() {
        // Initialize Web Worker for local inference
        this.worker = new Worker('llm-worker.js', { type: 'module' });
        
        this.worker.onmessage = (event) => {
            const { type, data } = event.data;
            
            switch (type) {
                case 'loaded':
                    this.localModelLoaded = true;
                    console.log('Local model ready');
                    break;
                    
                case 'response':
                    this.handleResponse(data);
                    break;
                    
                case 'token':
                    this.handleToken(data);
                    break;
                    
                case 'error':
                    this.handleError(data);
                    break;
            }
        };
        
        // Load local model
        this.worker.postMessage({ 
            type: 'load', 
            data: { modelName: 'Xenova/Phi-3-mini-4k-instruct' } 
        });
    }
    
    async generate(prompt, options = {}) {
        const {
            forceLocal = false,
            forceCloud = false,
            taskComplexity = 'medium',
            maxTokens = 512,
        } = options;
        
        // Routing decision
        const useLocal = this.shouldUseLocal(
            forceLocal, 
            forceCloud, 
            taskComplexity
        );
        
        if (useLocal && this.localModelLoaded) {
            return this.generateLocal(prompt, { max_new_tokens: maxTokens });
        } else {
            return this.generateCloud(prompt, { max_tokens: maxTokens });
        }
    }
    
    shouldUseLocal(forceLocal, forceCloud, taskComplexity) {
        if (forceLocal) return true;
        if (forceCloud) return false;
        if (!this.localModelLoaded) return false;
        if (!navigator.onLine) return true;
        
        // Prefer local for simple tasks
        if (taskComplexity === 'simple') return true;
        
        // Use cloud for complex tasks
        if (taskComplexity === 'complex') return false;
        
        return this.preferLocal;
    }
    
    generateLocal(prompt, options) {
        return new Promise((resolve, reject) => {
            this.handleResponse = resolve;
            this.handleError = reject;
            
            this.worker.postMessage({
                type: 'generate',
                data: { prompt, options }
            });
        });
    }
    
    async generateCloud(prompt, options) {
        const apiKey = this.getAPIKey();
        if (!apiKey) {
            throw new Error('Cloud API key not configured');
        }
        
        const response = await fetch(this.cloudAPIs.gemini + `?key=${apiKey}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                contents: [{
                    parts: [{ text: prompt }]
                }],
                generationConfig: {
                    maxOutputTokens: options.max_tokens || 512,
                    temperature: 0.7,
                }
            })
        });
        
        const data = await response.json();
        return data.candidates[0].content.parts[0].text;
    }
    
    async generateStream(prompt, onToken, options = {}) {
        const useLocal = this.shouldUseLocal(
            options.forceLocal,
            options.forceCloud,
            options.taskComplexity || 'medium'
        );
        
        if (useLocal && this.localModelLoaded) {
            this.handleToken = onToken;
            this.worker.postMessage({
                type: 'stream',
                data: { prompt, options }
            });
        } else {
            // Cloud streaming implementation
            await this.streamCloud(prompt, onToken, options);
        }
    }
    
    async streamCloud(prompt, onToken, options) {
        const apiKey = this.getAPIKey();
        const response = await fetch(this.cloudAPIs.groq, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                model: 'llama-3.1-70b-versatile',
                messages: [{ role: 'user', content: prompt }],
                stream: true,
                max_tokens: options.max_tokens || 512,
            })
        });
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value);
            const lines = chunk.split('\n').filter(line => line.trim());
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6);
                    if (data === '[DONE]') continue;
                    
                    try {
                        const parsed = JSON.parse(data);
                        const token = parsed.choices[0]?.delta?.content;
                        if (token) onToken(token);
                    } catch (e) {
                        console.error('Parse error:', e);
                    }
                }
            }
        }
    }
    
    getAPIKey() {
        return localStorage.getItem('llm_api_key');
    }
    
    setAPIKey(key) {
        localStorage.setItem('llm_api_key', key);
    }
    
    setPreference(preferLocal) {
        this.preferLocal = preferLocal;
    }
}

// Usage example
const client = new HybridLLMClient();
await client.initialize();

// Simple query (uses local)
const simpleResponse = await client.generate(
    "What is 2+2?",
    { taskComplexity: 'simple' }
);

// Complex analysis (uses cloud if available)
const complexResponse = await client.generate(
    "Analyze the economic implications of quantum computing",
    { taskComplexity: 'complex' }
);

// Streaming generation
await client.generateStream(
    "Write a story about...",
    (token) => console.log(token),
    { taskComplexity: 'medium' }
);
```

---

## Configuration File

```json
// llm-config.json
{
  "models": {
    "local": [
      {
        "id": "phi-3.5-mini-q4",
        "name": "Phi-3.5-mini Q4",
        "file": "Phi-3.5-mini-instruct-Q4_K_M.gguf",
        "size_mb": 2048,
        "context_length": 128000,
        "platforms": ["ios", "android", "web"]
      },
      {
        "id": "qwen2.5-3b-q4",
        "name": "Qwen2.5 3B Q4",
        "file": "qwen2.5-3b-instruct-q4_k_m.gguf",
        "size_mb": 1900,
        "context_length": 32000,
        "platforms": ["ios", "android", "web"]
      }
    ],
    "cloud": [
      {
        "id": "gemini-flash",
        "name": "Gemini 1.5 Flash",
        "endpoint": "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
        "free_tier": {
          "requests_per_minute": 15,
          "tokens_per_day": 1000000
        }
      },
      {
        "id": "groq-llama",
        "name": "Llama 3.1 70B (Groq)",
        "endpoint": "https://api.groq.com/openai/v1/chat/completions",
        "free_tier": {
          "requests_per_minute": 30,
          "tokens_per_day": 14400
        }
      }
    ]
  },
  "routing": {
    "default_strategy": "hybrid",
    "prefer_local_for": ["simple", "privacy_sensitive"],
    "prefer_cloud_for": ["complex", "long_context"],
    "offline_fallback": "phi-3.5-mini-q4",
    "battery_saver_model": "qwen2.5-3b-q4"
  }
}
```

This provides complete, production-ready code for deploying LLMs on iOS, Android, and Web with intelligent hybrid routing!
