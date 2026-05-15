import React, { useState, useEffect } from 'react';
import { Search, Cpu, Zap, Code, Brain, Download, ExternalLink, ChevronDown, ChevronUp, Filter } from 'lucide-react';

const LLMEdgeSystem = () => {
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedModel, setSelectedModel] = useState(null);
  const [sortBy, setSortBy] = useState('size');
  const [testInput, setTestInput] = useState('');
  const [testResults, setTestResults] = useState(null);
  const [isTesting, setIsTesting] = useState(false);
  const [expandedCards, setExpandedCards] = useState(new Set());

  const runRoutingTest = async () => {
    const prompt = testInput.trim();
    if (!prompt) {
      setTestResults({ error: 'Please enter a prompt first.' });
      return;
    }

    setIsTesting(true);
    setTestResults(null);

    try {
      const API_BASE = 'https://magnificent-simplicity-production-3ad9.up.railway.app';
      const routeRes = await fetch(`${API_BASE}/api/route`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt,
          task_type: 'general',
          context_length: 0,
        }),
      });

      if (!routeRes.ok) {
        const err = await routeRes.json().catch(() => ({}));
        throw new Error(err.detail || 'Failed to get routing decision');
      }

      const routeData = await routeRes.json();

      const generateRes = await fetch(`${API_BASE}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt,
          model_id: routeData.selected_model,
          task_type: 'general',
        }),
      });

      if (!generateRes.ok) {
        const err = await generateRes.json().catch(() => ({}));
        throw new Error(err.detail || 'Failed to generate response');
      }

      const generateData = await generateRes.json();

      setTestResults({
        model: routeData.selected_model,
        tier: routeData.tier,
        reason: routeData.reason,
        latency: routeData.estimated_latency_ms,
        response: generateData.response,
      });
    } catch (error) {
      setTestResults({ error: error.message });
    } finally {
      setIsTesting(false);
    }
  };

  const llmDatabase = [
    {
      id: 'phi-3.5-mini',
      name: 'Phi-3.5-mini',
      provider: 'Microsoft',
      category: 'local',
      size: '3.8GB',
      sizeBytes: 3800000000,
      params: '3.8B',
      contextWindow: '128K',
      reasoning: 9,
      coding: 8,
      speed: 9,
      deployment: 'iOS, Android, Web',
      license: 'MIT',
      description: 'Exceptional reasoning for its size. Optimized for mobile with ONNX and CoreML support.',
      strengths: ['Mobile-optimized', 'Long context', 'Strong reasoning', 'MIT license'],
      useCases: ['On-device analysis', 'Code review', 'Document understanding'],
      frameworks: ['llama.cpp', 'ONNX Runtime', 'CoreML', 'TensorFlow Lite'],
      quantization: ['Q4_K_M (2GB)', 'Q5_K_M (2.5GB)', 'Q8_0 (3.8GB)'],
      apiEndpoint: null
    },
    {
      id: 'llama-3.2-3b',
      name: 'Llama 3.2 3B',
      provider: 'Meta',
      category: 'local',
      size: '3.2GB',
      sizeBytes: 3200000000,
      params: '3B',
      contextWindow: '128K',
      reasoning: 8,
      coding: 7,
      speed: 9,
      deployment: 'iOS, Android, Web',
      license: 'Llama 3.2 License',
      description: 'Lightweight variant of Llama 3.2, excellent for on-device inference.',
      strengths: ['Fast inference', 'Low memory', 'Good general knowledge', 'Mobile SDK available'],
      useCases: ['Chatbots', 'Text analysis', 'Basic coding tasks'],
      frameworks: ['llama.cpp', 'ExecuTorch', 'MLC-LLM', 'GGUF'],
      quantization: ['Q4_0 (1.7GB)', 'Q5_K_M (2.2GB)', 'Q8_0 (3.2GB)'],
      apiEndpoint: null
    },
    {
      id: 'gemma-2-2b',
      name: 'Gemma 2 2B',
      provider: 'Google',
      category: 'local',
      size: '2.5GB',
      sizeBytes: 2500000000,
      params: '2B',
      contextWindow: '8K',
      reasoning: 7,
      coding: 6,
      speed: 10,
      deployment: 'iOS, Android, Web, Edge',
      license: 'Gemma License',
      description: 'Smallest Gemma model, ultra-fast for edge devices.',
      strengths: ['Ultra-lightweight', 'Fast startup', 'Low power consumption', 'JAX/Keras native'],
      useCases: ['Quick responses', 'Classification', 'Simple reasoning'],
      frameworks: ['llama.cpp', 'Keras', 'JAX', 'TensorFlow Lite'],
      quantization: ['Q4_K_M (1.4GB)', 'Q5_K_M (1.6GB)', 'FP16 (2.5GB)'],
      apiEndpoint: null
    },
    {
      id: 'qwen2.5-3b',
      name: 'Qwen2.5 3B',
      provider: 'Alibaba',
      category: 'local',
      size: '3.5GB',
      sizeBytes: 3500000000,
      params: '3B',
      contextWindow: '32K',
      reasoning: 8,
      coding: 9,
      speed: 9,
      deployment: 'iOS, Android, Linux',
      license: 'Apache 2.0',
      description: 'Outstanding coding capabilities for its size. Multilingual support.',
      strengths: ['Best-in-class coding', 'Multilingual', 'Apache 2.0', 'Strong math'],
      useCases: ['Code generation', 'Code debugging', 'Technical writing'],
      frameworks: ['llama.cpp', 'vLLM', 'Transformers', 'GGUF'],
      quantization: ['Q4_K_M (1.9GB)', 'Q5_K_M (2.3GB)', 'Q8_0 (3.5GB)'],
      apiEndpoint: null
    },
    {
      id: 'gemini-flash',
      name: 'Gemini 1.5 Flash',
      provider: 'Google',
      category: 'cloud',
      size: 'API',
      sizeBytes: 0,
      params: 'Unknown',
      contextWindow: '1M',
      reasoning: 9,
      coding: 9,
      speed: 10,
      deployment: 'API',
      license: 'Commercial (Free tier)',
      description: 'Lightning-fast cloud inference with massive context. Free tier: 15 RPM, 1M tokens/day.',
      strengths: ['Ultra-fast', 'Massive context', 'Multimodal', 'Generous free tier'],
      useCases: ['Complex reasoning', 'Long document analysis', 'Vision tasks'],
      frameworks: ['Google AI SDK', 'REST API', 'Vertex AI'],
      quantization: ['N/A'],
      apiEndpoint: 'https://generativelanguage.googleapis.com'
    },
    {
      id: 'groq-llama',
      name: 'Llama 3.1 70B (Groq)',
      provider: 'Groq',
      category: 'cloud',
      size: 'API',
      sizeBytes: 0,
      params: '70B',
      contextWindow: '128K',
      reasoning: 10,
      coding: 9,
      speed: 10,
      deployment: 'API',
      license: 'Commercial (Free tier)',
      description: 'Fastest LLM inference available. Free tier: 30 RPM, 14,400 tokens/day.',
      strengths: ['Extreme speed (750+ tok/s)', 'High quality', 'Free tier', 'No rate limit throttling'],
      useCases: ['Real-time applications', 'Interactive agents', 'Code generation'],
      frameworks: ['Groq SDK', 'OpenAI-compatible API'],
      quantization: ['N/A'],
      apiEndpoint: 'https://api.groq.com'
    },
    {
      id: 'together-mixtral',
      name: 'Mixtral 8x7B (Together)',
      provider: 'Together.ai',
      category: 'cloud',
      size: 'API',
      sizeBytes: 0,
      params: '47B Active',
      contextWindow: '32K',
      reasoning: 9,
      coding: 8,
      speed: 9,
      deployment: 'API',
      license: 'Commercial (Free credits)',
      description: 'MoE architecture for efficient inference. Free: $1 monthly credits.',
      strengths: ['Efficient MoE', 'Good value', 'Multiple models', 'Fast switching'],
      useCases: ['Multi-model testing', 'Production inference', 'Batch processing'],
      frameworks: ['Together SDK', 'OpenAI-compatible API'],
      quantization: ['N/A'],
      apiEndpoint: 'https://api.together.xyz'
    },
    {
      id: 'hf-inference',
      name: 'Hugging Face Inference',
      provider: 'Hugging Face',
      category: 'cloud',
      size: 'API',
      sizeBytes: 0,
      params: 'Various',
      contextWindow: 'Model-dependent',
      reasoning: 8,
      coding: 8,
      speed: 7,
      deployment: 'API',
      license: 'Free tier',
      description: 'Access 1000+ models through unified API. Free tier with rate limits.',
      strengths: ['Model variety', 'Easy experimentation', 'Community models', 'Simple integration'],
      useCases: ['Model comparison', 'Prototyping', 'Specialized tasks'],
      frameworks: ['Hugging Face SDK', 'REST API', 'Inference Endpoints'],
      quantization: ['N/A'],
      apiEndpoint: 'https://api-inference.huggingface.co'
    }
  ];

  const hybridStrategy = {
    title: 'Hybrid Edge-Cloud Strategy',
    description: 'Optimal approach for mobile/edge deployment',
    tiers: [
      {
        name: 'Tier 1: On-Device (Primary)',
        model: 'Phi-3.5-mini or Qwen2.5 3B',
        use: 'Fast responses, offline capability, privacy-sensitive tasks',
        trigger: 'Default for all requests, simple reasoning, code completion'
      },
      {
        name: 'Tier 2: Cloud Fallback (Secondary)',
        model: 'Gemini Flash or Groq',
        use: 'Complex reasoning, long context, when quality matters most',
        trigger: 'User explicitly requests deeper analysis, task requires >8K context, on-device fails'
      },
      {
        name: 'Tier 3: Specialized (Tertiary)',
        model: 'Together.ai or Hugging Face',
        use: 'Specific model requirements, experimentation',
        trigger: 'User requests specific model, specialized task requirements'
      }
    ]
  };

  const deploymentGuide = {
    ios: {
      title: 'iOS Deployment',
      steps: [
        'Convert model to CoreML format using coremltools',
        'Integrate with MLX or llama.cpp Swift bindings',
        'Use Metal Performance Shaders for GPU acceleration',
        'Implement model download/caching system',
        'Test on target devices (iPhone 12+, iPad recommended)'
      ],
      frameworks: ['CoreML', 'MLX', 'llama.cpp', 'ONNX Runtime'],
      requirements: 'iOS 16+, 4GB+ RAM, 8GB+ storage'
    },
    android: {
      title: 'Android Deployment',
      steps: [
        'Use MediaPipe LLM Inference API or TFLite',
        'Implement llama.cpp via JNI or Termux',
        'Leverage GPU delegates (OpenCL/Vulkan)',
        'Add model quantization pipeline',
        'Test on mid-range devices (6GB+ RAM)'
      ],
      frameworks: ['MediaPipe', 'TensorFlow Lite', 'llama.cpp', 'ONNX Runtime'],
      requirements: 'Android 10+, 6GB+ RAM, 8GB+ storage'
    },
    web: {
      title: 'Web/PWA Deployment',
      steps: [
        'Use ONNX Runtime Web with WebAssembly',
        'Implement WebGPU for acceleration (Chrome)',
        'Set up service workers for offline capability',
        'Implement progressive model loading',
        'Add IndexedDB for model caching'
      ],
      frameworks: ['ONNX Runtime Web', 'Transformers.js', 'WebLLM'],
      requirements: 'Chrome 113+, 4GB+ RAM, WebGPU support'
    }
  };

  const filteredModels = llmDatabase.filter(model => 
    selectedCategory === 'all' || model.category === selectedCategory
  ).sort((a, b) => {
    if (sortBy === 'size') return a.sizeBytes - b.sizeBytes;
    if (sortBy === 'reasoning') return b.reasoning - a.reasoning;
    if (sortBy === 'coding') return b.coding - a.coding;
    return 0;
  });

  const toggleExpanded = (id) => {
    const newSet = new Set(expandedCards);
    if (newSet.has(id)) {
      newSet.delete(id);
    } else {
      newSet.add(id);
    }
    setExpandedCards(newSet);
  };

  const ScoreBar = ({ score, label }) => (
    <div className="score-bar">
      <div className="score-label">{label}</div>
      <div className="score-track">
        <div className="score-fill" style={{ width: `${score * 10}%` }} />
      </div>
      <div className="score-value">{score}/10</div>
    </div>
  );

  return (
    <div className="llm-system">
      <div className="header">
        <div className="header-content">
          <div className="title-section">
            <h1>Edge LLM Architect</h1>
            <p className="subtitle">Free LLMs for Mobile & Edge Deployment</p>
          </div>
          <div className="header-stats">
            <div className="stat">
              <Cpu size={20} />
              <span>{llmDatabase.filter(m => m.category === 'local').length} Local Models</span>
            </div>
            <div className="stat">
              <Zap size={20} />
              <span>{llmDatabase.filter(m => m.category === 'cloud').length} Cloud APIs</span>
            </div>
          </div>
        </div>
      </div>

      <div className="controls">
        <div className="filter-group">
          <Filter size={18} />
          <button
            className={`filter-btn ${selectedCategory === 'all' ? 'active' : ''}`}
            onClick={() => setSelectedCategory('all')}
          >
            All Models
          </button>
          <button
            className={`filter-btn ${selectedCategory === 'local' ? 'active' : ''}`}
            onClick={() => setSelectedCategory('local')}
          >
            Local/Edge
          </button>
          <button
            className={`filter-btn ${selectedCategory === 'cloud' ? 'active' : ''}`}
            onClick={() => setSelectedCategory('cloud')}
          >
            Cloud APIs
          </button>
        </div>
        
        <select 
          className="sort-select"
          value={sortBy} 
          onChange={(e) => setSortBy(e.target.value)}
        >
          <option value="size">Sort by Size</option>
          <option value="reasoning">Sort by Reasoning</option>
          <option value="coding">Sort by Coding</option>
        </select>
      </div>

      <div className="routing-playground">
        <h2>Routing Playground</h2>
        <p>Test real router decisions and responses through the backend API.</p>
        <textarea
          value={testInput}
          onChange={(e) => setTestInput(e.target.value)}
          placeholder="Type a prompt to test routing..."
          rows={4}
        />
        <button className="test-btn" onClick={runRoutingTest} disabled={isTesting}>
          {isTesting ? 'Running...' : 'Run Routing Test'}
        </button>

        {testResults && (
          <div className="test-results">
            {testResults.error ? (
              <p className="test-error">Error: {testResults.error}</p>
            ) : (
              <>
                <p><strong>Model:</strong> <span className="test-model">{testResults.model}</span></p>
                <p><strong>Tier:</strong> <span className="test-tier">{testResults.tier}</span></p>
                <p><strong>Reason:</strong> <span className="test-reason">{testResults.reason}</span></p>
                <p><strong>Estimated latency:</strong> {testResults.latency}ms</p>
                <div className="test-response">
                  <strong>Response:</strong>
                  <p>{testResults.response}</p>
                </div>
              </>
            )}
          </div>
        )}
      </div>

      <div className="strategy-banner">
        <div className="strategy-header">
          <Brain size={24} />
          <h2>{hybridStrategy.title}</h2>
        </div>
        <p className="strategy-desc">{hybridStrategy.description}</p>
        <div className="tiers">
          {hybridStrategy.tiers.map((tier, idx) => (
            <div key={idx} className="tier">
              <div className="tier-header">
                <span className="tier-number">{idx + 1}</span>
                <h3>{tier.name}</h3>
              </div>
              <div className="tier-model">{tier.model}</div>
              <div className="tier-use">{tier.use}</div>
              <div className="tier-trigger">Trigger: {tier.trigger}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="models-grid">
        {filteredModels.map(model => (
          <div 
            key={model.id} 
            className={`model-card ${model.category} ${selectedModel?.id === model.id ? 'selected' : ''}`}
            onClick={() => setSelectedModel(model)}
          >
            <div className="model-header">
              <div className="model-title">
                <h3>{model.name}</h3>
                <span className="model-provider">{model.provider}</span>
              </div>
              <div className="model-badge">{model.category === 'local' ? 'LOCAL' : 'CLOUD'}</div>
            </div>

            <p className="model-description">{model.description}</p>

            <div className="model-specs">
              <div className="spec">
                <Download size={16} />
                <span>{model.size}</span>
              </div>
              <div className="spec">
                <Code size={16} />
                <span>{model.contextWindow}</span>
              </div>
              <div className="spec">
                <Cpu size={16} />
                <span>{model.params}</span>
              </div>
            </div>

            <div className="scores">
              <ScoreBar score={model.reasoning} label="Reasoning" />
              <ScoreBar score={model.coding} label="Coding" />
              <ScoreBar score={model.speed} label="Speed" />
            </div>

            <div className="model-strengths">
              {model.strengths.slice(0, 3).map((strength, idx) => (
                <span key={idx} className="strength-tag">{strength}</span>
              ))}
            </div>

            <button 
              className="expand-btn"
              onClick={(e) => {
                e.stopPropagation();
                toggleExpanded(model.id);
              }}
            >
              {expandedCards.has(model.id) ? (
                <>Less Info <ChevronUp size={16} /></>
              ) : (
                <>More Info <ChevronDown size={16} /></>
              )}
            </button>

            {expandedCards.has(model.id) && (
              <div className="expanded-content" onClick={(e) => e.stopPropagation()}>
                <div className="section">
                  <h4>Use Cases</h4>
                  <ul>
                    {model.useCases.map((use, idx) => (
                      <li key={idx}>{use}</li>
                    ))}
                  </ul>
                </div>

                <div className="section">
                  <h4>Frameworks</h4>
                  <div className="framework-tags">
                    {model.frameworks.map((fw, idx) => (
                      <span key={idx} className="framework-tag">{fw}</span>
                    ))}
                  </div>
                </div>

                {model.category === 'local' && (
                  <div className="section">
                    <h4>Quantization Options</h4>
                    <ul>
                      {model.quantization.map((quant, idx) => (
                        <li key={idx}>{quant}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="section">
                  <h4>Deployment</h4>
                  <p>{model.deployment}</p>
                </div>

                <div className="section">
                  <h4>License</h4>
                  <p>{model.license}</p>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="deployment-guides">
        <h2>Deployment Guides</h2>
        <div className="guides-grid">
          {Object.entries(deploymentGuide).map(([platform, guide]) => (
            <div key={platform} className="guide-card">
              <h3>{guide.title}</h3>
              <div className="guide-requirements">
                <strong>Requirements:</strong> {guide.requirements}
              </div>
              <div className="guide-steps">
                <h4>Implementation Steps:</h4>
                <ol>
                  {guide.steps.map((step, idx) => (
                    <li key={idx}>{step}</li>
                  ))}
                </ol>
              </div>
              <div className="guide-frameworks">
                <h4>Recommended Frameworks:</h4>
                <div className="framework-list">
                  {guide.frameworks.map((fw, idx) => (
                    <span key={idx} className="framework-tag">{fw}</span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="resources">
        <h2>Implementation Resources</h2>
        <div className="resource-grid">
          <div className="resource-card">
            <Code size={24} />
            <h3>Code Examples</h3>
            <ul>
              <li><a href="https://github.com/ggerganov/llama.cpp" target="_blank" rel="noopener">llama.cpp (C++)</a></li>
              <li><a href="https://github.com/ml-explore/mlx" target="_blank" rel="noopener">MLX (Apple Silicon)</a></li>
              <li><a href="https://github.com/huggingface/transformers.js" target="_blank" rel="noopener">Transformers.js (Web)</a></li>
              <li><a href="https://github.com/google-ai-edge/mediapipe" target="_blank" rel="noopener">MediaPipe (Android)</a></li>
            </ul>
          </div>
          
          <div className="resource-card">
            <Download size={24} />
            <h3>Model Downloads</h3>
            <ul>
              <li><a href="https://huggingface.co/models" target="_blank" rel="noopener">Hugging Face Hub</a></li>
              <li><a href="https://ollama.com/library" target="_blank" rel="noopener">Ollama Library</a></li>
              <li><a href="https://github.com/ggerganov/llama.cpp/discussions" target="_blank" rel="noopener">GGUF Models</a></li>
            </ul>
          </div>
          
          <div className="resource-card">
            <ExternalLink size={24} />
            <h3>API Documentation</h3>
            <ul>
              <li><a href="https://ai.google.dev/gemini-api" target="_blank" rel="noopener">Google Gemini API</a></li>
              <li><a href="https://console.groq.com/docs" target="_blank" rel="noopener">Groq API Docs</a></li>
              <li><a href="https://docs.together.ai" target="_blank" rel="noopener">Together.ai Docs</a></li>
              <li><a href="https://huggingface.co/docs/api-inference" target="_blank" rel="noopener">HF Inference API</a></li>
            </ul>
          </div>
        </div>
      </div>

      <style>{`
        .llm-system {
          min-height: 100vh;
          background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
          color: #e8eaf6;
          font-family: 'Berkeley Mono', 'JetBrains Mono', 'Fira Code', monospace;
          padding: 0;
        }

        .header {
          background: linear-gradient(135deg, #1e2749 0%, #2d3561 100%);
          border-bottom: 2px solid #3d4785;
          padding: 3rem 2rem;
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }

        .header-content {
          max-width: 1400px;
          margin: 0 auto;
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 2rem;
        }

        .title-section h1 {
          font-size: 3rem;
          font-weight: 700;
          margin: 0;
          background: linear-gradient(135deg, #00d4ff 0%, #7b2ff7 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          letter-spacing: -0.02em;
        }

        .subtitle {
          font-size: 1.125rem;
          color: #9fa8da;
          margin: 0.5rem 0 0 0;
          font-weight: 400;
          letter-spacing: 0.02em;
        }

        .header-stats {
          display: flex;
          gap: 2rem;
        }

        .stat {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.75rem 1.25rem;
          background: rgba(61, 71, 133, 0.3);
          border: 1px solid #3d4785;
          border-radius: 8px;
          font-size: 0.875rem;
          color: #c5cae9;
        }

        .controls {
          max-width: 1400px;
          margin: 2rem auto;
          padding: 0 2rem;
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 1rem;
        }

        .routing-playground {
          max-width: 1400px;
          margin: 1.5rem auto;
          padding: 1.5rem 2rem;
          background: linear-gradient(135deg, rgba(30, 39, 73, 0.6) 0%, rgba(45, 53, 97, 0.6) 100%);
          border: 1px solid #3d4785;
          border-radius: 12px;
        }

        .routing-playground h2 {
          margin: 0 0 0.5rem 0;
          color: #00d4ff;
          font-size: 1.5rem;
        }

        .routing-playground p {
          margin: 0 0 0.75rem 0;
          color: #9fa8da;
          font-size: 0.9rem;
        }

        .routing-playground textarea {
          width: 100%;
          resize: vertical;
          min-height: 90px;
          border-radius: 8px;
          border: 1px solid #3d4785;
          background: rgba(10, 14, 39, 0.75);
          color: #e8eaf6;
          padding: 0.75rem;
          font-family: inherit;
          font-size: 0.9rem;
          margin-bottom: 0.75rem;
        }

        .test-btn {
          background: linear-gradient(135deg, #00d4ff 0%, #7b2ff7 100%);
          border: none;
          color: white;
          font-family: inherit;
          font-size: 0.875rem;
          font-weight: 600;
          padding: 0.625rem 1.25rem;
          border-radius: 6px;
          cursor: pointer;
          transition: opacity 0.2s ease;
        }

        .test-btn:disabled {
          cursor: not-allowed;
          opacity: 0.7;
        }

        .test-results {
          margin-top: 1rem;
          background: rgba(10, 14, 39, 0.65);
          border: 1px solid #3d4785;
          border-radius: 8px;
          padding: 1rem;
        }

        .test-results p {
          margin: 0.25rem 0;
          color: #c5cae9;
        }

        .test-error {
          color: #ff8a80 !important;
        }

        .test-response {
          margin-top: 0.75rem;
          border-top: 1px solid #3d4785;
          padding-top: 0.75rem;
        }

        .filter-group {
          display: flex;
          gap: 0.5rem;
          align-items: center;
        }

        .filter-btn {
          background: rgba(61, 71, 133, 0.2);
          border: 1px solid #3d4785;
          color: #c5cae9;
          padding: 0.625rem 1.25rem;
          border-radius: 6px;
          cursor: pointer;
          font-family: inherit;
          font-size: 0.875rem;
          transition: all 0.2s ease;
        }

        .filter-btn:hover {
          background: rgba(61, 71, 133, 0.4);
          border-color: #5c6bc0;
        }

        .filter-btn.active {
          background: linear-gradient(135deg, #00d4ff 0%, #7b2ff7 100%);
          border-color: transparent;
          color: white;
          font-weight: 600;
        }

        .sort-select {
          background: rgba(61, 71, 133, 0.2);
          border: 1px solid #3d4785;
          color: #c5cae9;
          padding: 0.625rem 1rem;
          border-radius: 6px;
          font-family: inherit;
          font-size: 0.875rem;
          cursor: pointer;
        }

        .strategy-banner {
          max-width: 1400px;
          margin: 2rem auto;
          padding: 2rem;
          background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(123, 47, 247, 0.1) 100%);
          border: 2px solid rgba(0, 212, 255, 0.3);
          border-radius: 12px;
        }

        .strategy-header {
          display: flex;
          align-items: center;
          gap: 1rem;
          margin-bottom: 1rem;
        }

        .strategy-header h2 {
          margin: 0;
          font-size: 1.75rem;
          color: #00d4ff;
        }

        .strategy-desc {
          color: #9fa8da;
          margin-bottom: 1.5rem;
          font-size: 1rem;
        }

        .tiers {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 1rem;
        }

        .tier {
          background: rgba(30, 39, 73, 0.5);
          border: 1px solid #3d4785;
          border-radius: 8px;
          padding: 1.25rem;
        }

        .tier-header {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          margin-bottom: 0.75rem;
        }

        .tier-number {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          background: linear-gradient(135deg, #00d4ff 0%, #7b2ff7 100%);
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 700;
          font-size: 1rem;
        }

        .tier h3 {
          margin: 0;
          font-size: 1rem;
          color: #c5cae9;
        }

        .tier-model {
          font-weight: 600;
          color: #00d4ff;
          margin-bottom: 0.5rem;
          font-size: 0.875rem;
        }

        .tier-use, .tier-trigger {
          font-size: 0.813rem;
          color: #9fa8da;
          margin-bottom: 0.25rem;
          line-height: 1.5;
        }

        .models-grid {
          max-width: 1400px;
          margin: 2rem auto;
          padding: 0 2rem;
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
          gap: 1.5rem;
        }

        .model-card {
          background: linear-gradient(135deg, rgba(30, 39, 73, 0.6) 0%, rgba(45, 53, 97, 0.6) 100%);
          border: 1px solid #3d4785;
          border-radius: 12px;
          padding: 1.5rem;
          cursor: pointer;
          transition: all 0.3s ease;
          position: relative;
          overflow: hidden;
        }

        .model-card::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          height: 3px;
          background: linear-gradient(90deg, #00d4ff 0%, #7b2ff7 100%);
          opacity: 0;
          transition: opacity 0.3s ease;
        }

        .model-card:hover {
          transform: translateY(-4px);
          border-color: #5c6bc0;
          box-shadow: 0 12px 40px rgba(0, 212, 255, 0.2);
        }

        .model-card:hover::before {
          opacity: 1;
        }

        .model-card.selected {
          border-color: #00d4ff;
          box-shadow: 0 12px 40px rgba(0, 212, 255, 0.3);
        }

        .model-card.selected::before {
          opacity: 1;
        }

        .model-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 1rem;
        }

        .model-title h3 {
          margin: 0 0 0.25rem 0;
          font-size: 1.375rem;
          color: #fff;
          font-weight: 600;
        }

        .model-provider {
          font-size: 0.813rem;
          color: #9fa8da;
          font-weight: 400;
        }

        .model-badge {
          background: rgba(0, 212, 255, 0.2);
          color: #00d4ff;
          padding: 0.375rem 0.75rem;
          border-radius: 6px;
          font-size: 0.75rem;
          font-weight: 700;
          letter-spacing: 0.05em;
        }

        .model-card.cloud .model-badge {
          background: rgba(123, 47, 247, 0.2);
          color: #b388ff;
        }

        .model-description {
          color: #c5cae9;
          font-size: 0.875rem;
          line-height: 1.6;
          margin-bottom: 1rem;
        }

        .model-specs {
          display: flex;
          gap: 1rem;
          margin-bottom: 1.25rem;
        }

        .spec {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          color: #9fa8da;
          font-size: 0.813rem;
        }

        .scores {
          margin-bottom: 1rem;
        }

        .score-bar {
          display: grid;
          grid-template-columns: 80px 1fr 40px;
          align-items: center;
          gap: 0.75rem;
          margin-bottom: 0.75rem;
        }

        .score-label {
          font-size: 0.813rem;
          color: #9fa8da;
        }

        .score-track {
          height: 6px;
          background: rgba(61, 71, 133, 0.3);
          border-radius: 3px;
          overflow: hidden;
          position: relative;
        }

        .score-fill {
          height: 100%;
          background: linear-gradient(90deg, #00d4ff 0%, #7b2ff7 100%);
          border-radius: 3px;
          transition: width 0.3s ease;
        }

        .score-value {
          font-size: 0.813rem;
          color: #c5cae9;
          font-weight: 600;
          text-align: right;
        }

        .model-strengths {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
          margin-bottom: 1rem;
        }

        .strength-tag {
          background: rgba(0, 212, 255, 0.1);
          border: 1px solid rgba(0, 212, 255, 0.3);
          color: #00d4ff;
          padding: 0.375rem 0.75rem;
          border-radius: 6px;
          font-size: 0.75rem;
          font-weight: 500;
        }

        .expand-btn {
          width: 100%;
          background: rgba(61, 71, 133, 0.3);
          border: 1px solid #3d4785;
          color: #c5cae9;
          padding: 0.625rem;
          border-radius: 6px;
          cursor: pointer;
          font-family: inherit;
          font-size: 0.813rem;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.5rem;
          transition: all 0.2s ease;
        }

        .expand-btn:hover {
          background: rgba(61, 71, 133, 0.5);
          border-color: #5c6bc0;
        }

        .expanded-content {
          margin-top: 1rem;
          padding-top: 1rem;
          border-top: 1px solid #3d4785;
        }

        .section {
          margin-bottom: 1rem;
        }

        .section h4 {
          margin: 0 0 0.5rem 0;
          font-size: 0.875rem;
          color: #00d4ff;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }

        .section ul {
          margin: 0;
          padding-left: 1.25rem;
          color: #c5cae9;
          font-size: 0.813rem;
          line-height: 1.6;
        }

        .section li {
          margin-bottom: 0.25rem;
        }

        .section p {
          margin: 0;
          color: #c5cae9;
          font-size: 0.813rem;
          line-height: 1.6;
        }

        .framework-tags, .framework-list {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
        }

        .framework-tag {
          background: rgba(123, 47, 247, 0.1);
          border: 1px solid rgba(123, 47, 247, 0.3);
          color: #b388ff;
          padding: 0.25rem 0.625rem;
          border-radius: 4px;
          font-size: 0.75rem;
        }

        .deployment-guides {
          max-width: 1400px;
          margin: 3rem auto 2rem;
          padding: 0 2rem;
        }

        .deployment-guides h2 {
          font-size: 2rem;
          color: #fff;
          margin-bottom: 1.5rem;
        }

        .guides-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
          gap: 1.5rem;
        }

        .guide-card {
          background: linear-gradient(135deg, rgba(30, 39, 73, 0.6) 0%, rgba(45, 53, 97, 0.6) 100%);
          border: 1px solid #3d4785;
          border-radius: 12px;
          padding: 1.5rem;
        }

        .guide-card h3 {
          font-size: 1.25rem;
          color: #00d4ff;
          margin: 0 0 1rem 0;
        }

        .guide-requirements {
          background: rgba(0, 212, 255, 0.1);
          border-left: 3px solid #00d4ff;
          padding: 0.75rem;
          margin-bottom: 1rem;
          font-size: 0.813rem;
          color: #c5cae9;
          border-radius: 4px;
        }

        .guide-steps h4, .guide-frameworks h4 {
          font-size: 0.875rem;
          color: #b388ff;
          margin: 0 0 0.5rem 0;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }

        .guide-steps ol {
          margin: 0;
          padding-left: 1.25rem;
          color: #c5cae9;
          font-size: 0.813rem;
          line-height: 1.7;
        }

        .guide-steps li {
          margin-bottom: 0.5rem;
        }

        .guide-frameworks {
          margin-top: 1rem;
        }

        .resources {
          max-width: 1400px;
          margin: 3rem auto 2rem;
          padding: 0 2rem 4rem;
        }

        .resources h2 {
          font-size: 2rem;
          color: #fff;
          margin-bottom: 1.5rem;
        }

        .resource-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 1.5rem;
        }

        .resource-card {
          background: linear-gradient(135deg, rgba(30, 39, 73, 0.6) 0%, rgba(45, 53, 97, 0.6) 100%);
          border: 1px solid #3d4785;
          border-radius: 12px;
          padding: 1.5rem;
        }

        .resource-card h3 {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          font-size: 1.125rem;
          color: #00d4ff;
          margin: 0 0 1rem 0;
        }

        .resource-card ul {
          margin: 0;
          padding: 0;
          list-style: none;
        }

        .resource-card li {
          margin-bottom: 0.75rem;
        }

        .resource-card a {
          color: #c5cae9;
          text-decoration: none;
          font-size: 0.875rem;
          transition: color 0.2s ease;
          display: inline-block;
          position: relative;
          padding-left: 1.25rem;
        }

        .resource-card a::before {
          content: '→';
          position: absolute;
          left: 0;
          color: #00d4ff;
          transition: transform 0.2s ease;
        }

        .resource-card a:hover {
          color: #00d4ff;
        }

        .resource-card a:hover::before {
          transform: translateX(4px);
        }

        @media (max-width: 768px) {
          .header-content {
            flex-direction: column;
            align-items: flex-start;
          }

          .header-stats {
            width: 100%;
            justify-content: space-between;
          }

          .controls {
            flex-direction: column;
            align-items: stretch;
          }

          .filter-group {
            flex-wrap: wrap;
          }

          .models-grid, .guides-grid, .resource-grid {
            grid-template-columns: 1fr;
          }

          .title-section h1 {
            font-size: 2rem;
          }
        }
      `}</style>
    </div>
  );
};

export default LLMEdgeSystem;
