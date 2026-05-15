"""
LLM Edge Router - Hybrid Edge-Cloud Orchestration System
Intelligently routes requests between local models and cloud APIs based on:
- Task complexity
- Context length requirements
- Network availability
- Battery/resource constraints
"""

import os
import json
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import asyncio

# Model file mappings: model_id -> GGUF filename in models/
_GGUF_FILENAMES: Dict[str, str] = {
    "qwen2.5-3b": "qwen2.5-3b-instruct-q4_k_m.gguf",
    "phi-3.5-mini": "phi-3.5-mini-instruct-q4_k_m.gguf",

}

_llama_instances: Dict[str, Any] = {}

_OPENROUTER_DEFAULT_MODEL = "inclusionai/ring-2.6-1t:free"


def _is_truthy_env(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


def _normalize_openrouter_model(model_name: str, free_only: bool) -> str:
    model_name = model_name.strip()
    if free_only and model_name and ":free" not in model_name:
        return f"{model_name}:free"
    return model_name


def _parse_model_list(raw: str, free_only: bool) -> List[str]:
    models: List[str] = []
    seen = set()
    for item in (raw or "").split(","):
        normalized = _normalize_openrouter_model(item, free_only)
        if normalized and normalized not in seen:
            models.append(normalized)
            seen.add(normalized)
    return models


class ModelTier(Enum):
    """Model tiers for hybrid deployment strategy"""
    LOCAL = "local"  # On-device models
    CLOUD_FAST = "cloud_fast"  # Fast cloud APIs (Gemini Flash, Groq)
    CLOUD_SPECIALIZED = "cloud_specialized"  # Specialized models


class TaskComplexity(Enum):
    """Task complexity levels for routing decisions"""
    SIMPLE = 1  # Basic queries, code completion
    MEDIUM = 2  # Standard reasoning, code generation
    COMPLEX = 3  # Deep analysis, long context


@dataclass
class ModelConfig:
    """Configuration for a specific LLM"""
    name: str
    tier: ModelTier
    max_context: int
    cost_per_1k_tokens: float
    avg_latency_ms: int
    supports_offline: bool
    strengths: List[str]
    endpoint: Optional[str] = None
    api_key_env: Optional[str] = None


@dataclass
class RoutingDecision:
    """Result of routing logic"""
    selected_model: str
    reason: str
    tier: ModelTier
    estimated_cost: float
    estimated_latency_ms: int


class LLMEdgeRouter:
    """
    Intelligent router for hybrid edge-cloud LLM deployment.
    Automatically selects the best model based on task requirements.
    """
    
    def __init__(self):
        self._load_environment_config()
        self.models = self._initialize_models()
        self.offline_mode = False
        self.battery_saver = False
        self.max_cost_per_request = 0.01  # $0.01 default limit

    def _load_environment_config(self):
        """Load environment variables from .env if available.

        Loads from both project-root and current working directory .env files
        without overriding already-exported environment variables.
        """
        try:
            from dotenv import load_dotenv
        except ImportError:
            return

        project_env = Path(__file__).resolve().parent / ".env"
        cwd_env = Path.cwd() / ".env"

        env_candidates = []
        if project_env.exists():
            env_candidates.append(project_env)
        if cwd_env.exists() and cwd_env.resolve() != project_env.resolve():
            env_candidates.append(cwd_env)

        for env_path in env_candidates:
            load_dotenv(dotenv_path=env_path, override=False)
        
    def _initialize_models(self) -> Dict[str, ModelConfig]:
        """Initialize available models with configurations"""
        return {
            # Local/Edge Models
            "phi-3.5-mini": ModelConfig(
                name="Phi-3.5-mini",
                tier=ModelTier.LOCAL,
                max_context=128000,
                cost_per_1k_tokens=0.0,
                avg_latency_ms=150,
                supports_offline=True,
                strengths=["reasoning", "long_context", "privacy"],
            ),
            "qwen2.5-3b": ModelConfig(
                name="Qwen2.5 3B",
                tier=ModelTier.LOCAL,
                max_context=32000,
                cost_per_1k_tokens=0.0,
                avg_latency_ms=120,
                supports_offline=True,
                strengths=["coding", "math", "multilingual"],
            ),

            
            # Cloud Fast Models
            "gemini-flash": ModelConfig(
                name="Gemini 1.5 Flash",
                tier=ModelTier.CLOUD_FAST,
                max_context=1000000,
                cost_per_1k_tokens=0.0,  # Free tier
                avg_latency_ms=300,
                supports_offline=False,
                strengths=["speed", "long_context", "multimodal"],
                endpoint="https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
                api_key_env="GEMINI_API_KEY",
            ),
            "groq-llama": ModelConfig(
                name="Llama 3.1 70B (Groq)",
                tier=ModelTier.CLOUD_FAST,
                max_context=128000,
                cost_per_1k_tokens=0.0,  # Free tier
                avg_latency_ms=200,
                supports_offline=False,
                strengths=["speed", "reasoning", "quality"],
                endpoint="https://api.groq.com/openai/v1/chat/completions",
                api_key_env="GROQ_API_KEY",
            ),
            "openrouter-llama": ModelConfig(
                name="Llama 3.1 70B (OpenRouter)",
                tier=ModelTier.CLOUD_FAST,
                max_context=128000,
                cost_per_1k_tokens=0.0,  # User-configurable via OpenRouter account
                avg_latency_ms=280,
                supports_offline=False,
                strengths=["speed", "reasoning", "quality"],
                endpoint="https://openrouter.ai/api/v1/chat/completions",
                api_key_env="OPENROUTER_API_KEY",
            ),
            
            # Cloud Specialized
            "together-mixtral": ModelConfig(
                name="Mixtral 8x7B",
                tier=ModelTier.CLOUD_SPECIALIZED,
                max_context=32000,
                cost_per_1k_tokens=0.0,  # Free credits
                avg_latency_ms=400,
                supports_offline=False,
                strengths=["moe", "efficiency", "versatile"],
                endpoint="https://api.together.xyz/v1/chat/completions",
                api_key_env="TOGETHER_API_KEY",
            ),
        }
    
    def route_request(
        self,
        prompt: str,
        context_length: int = 0,
        task_type: str = "general",
        force_offline: bool = False,
        max_latency_ms: Optional[int] = None,
    ) -> RoutingDecision:
        """
        Intelligently route a request to the best available model.
        
        Args:
            prompt: The user's prompt/query
            context_length: Estimated context length needed
            task_type: Type of task (general, coding, reasoning, analysis)
            force_offline: Force local model even if cloud would be better
            max_latency_ms: Maximum acceptable latency
            
        Returns:
            RoutingDecision with selected model and reasoning
        """
        
        # Determine task complexity
        complexity = self._assess_complexity(prompt, context_length)
        
        # Filter available models
        available_models = self._get_available_models(
            offline_required=force_offline or self.offline_mode,
            max_latency=max_latency_ms,
            min_context=context_length,
        )
        
        if not available_models:
            raise ValueError("No models available matching constraints")
        
        # Score each model for this task
        scored_models = []
        for model_id, model in available_models.items():
            score = self._score_model(
                model=model,
                task_type=task_type,
                complexity=complexity,
                context_length=context_length,
            )
            scored_models.append((model_id, model, score))
        
        # Select best model
        scored_models.sort(key=lambda x: x[2], reverse=True)
        best_model_id, best_model, best_score = scored_models[0]
        
        # Generate routing decision
        reason = self._generate_routing_reason(
            model=best_model,
            complexity=complexity,
            task_type=task_type,
            context_length=context_length,
        )
        
        return RoutingDecision(
            selected_model=best_model_id,
            reason=reason,
            tier=best_model.tier,
            estimated_cost=self._estimate_cost(best_model, context_length),
            estimated_latency_ms=best_model.avg_latency_ms,
        )
    
    def _assess_complexity(self, prompt: str, context_length: int) -> TaskComplexity:
        """Assess task complexity based on prompt and context"""
        
        # Check for complexity indicators
        complex_keywords = [
            "analyze", "compare", "evaluate", "synthesize", "explain in detail",
            "complex", "comprehensive", "deep dive", "thorough analysis"
        ]
        
        medium_keywords = [
            "write", "create", "generate", "code", "implement", "design"
        ]
        
        # Long context usually indicates complex task
        if context_length > 50000:
            return TaskComplexity.COMPLEX
        
        # Check keywords
        prompt_lower = prompt.lower()
        if any(kw in prompt_lower for kw in complex_keywords):
            return TaskComplexity.COMPLEX
        
        if any(kw in prompt_lower for kw in medium_keywords):
            return TaskComplexity.MEDIUM
        
        # Short prompts are usually simple
        if len(prompt.split()) < 10:
            return TaskComplexity.SIMPLE
        
        return TaskComplexity.MEDIUM
    
    def _get_available_models(
        self,
        offline_required: bool = False,
        max_latency: Optional[int] = None,
        min_context: int = 0,
    ) -> Dict[str, ModelConfig]:
        """Filter models based on constraints"""

        free_only = _is_truthy_env("FREE_LLM_ONLY", "true")

        available = {}
        for model_id, model in self.models.items():
            # Check offline requirement
            if offline_required and not model.supports_offline:
                continue
            
            # Check latency constraint
            if max_latency and model.avg_latency_ms > max_latency:
                continue
            
            # Check context window
            if model.max_context < min_context:
                continue
            
            # Check battery saver mode (prefer local models)
            if self.battery_saver and model.tier != ModelTier.LOCAL:
                continue

            # Optional free-only mode for cloud routing
            if free_only and model.tier != ModelTier.LOCAL and model.cost_per_1k_tokens > 0:
                continue
            
            # Check API key availability for cloud models
            if model.api_key_env and not os.getenv(model.api_key_env):
                continue
            
            available[model_id] = model
        
        return available
    
    def _score_model(
        self,
        model: ModelConfig,
        task_type: str,
        complexity: TaskComplexity,
        context_length: int,
    ) -> float:
        """Score a model for a specific task (0-100)"""
        
        score = 50.0  # Base score
        
        # Tier-based scoring
        if complexity == TaskComplexity.SIMPLE:
            if model.tier == ModelTier.LOCAL:
                score += 30  # Prefer local for simple tasks
        elif complexity == TaskComplexity.COMPLEX:
            if model.tier == ModelTier.CLOUD_FAST:
                score += 35  # Prefer cloud for complex tasks when available
            elif model.tier == ModelTier.CLOUD_SPECIALIZED:
                score += 25
            elif model.tier == ModelTier.LOCAL:
                score -= 15  # Keep local fallback, but de-prioritize for complex
        
        # Task-type matching
        task_strength_map = {
            "coding": "coding",
            "reasoning": "reasoning",
            "analysis": "reasoning",
            "math": "math",
            "general": "general",
        }
        
        if task_type in task_strength_map:
            if task_strength_map[task_type] in model.strengths:
                score += 20
        
        # Context length scoring
        if context_length > 0:
            context_ratio = context_length / model.max_context
            if context_ratio > 0.8:
                score -= 20  # Penalize if near limit
            elif context_ratio > 0.5:
                score -= 10
        
        # Cost consideration
        if model.cost_per_1k_tokens == 0:
            score += 15  # Bonus for free models
        
        # Latency bonus
        if model.avg_latency_ms < 200:
            score += 10
        
        # Privacy bonus for local models
        if model.tier == ModelTier.LOCAL and "privacy" in model.strengths:
            score += 5
        
        return score
    
    def _generate_routing_reason(
        self,
        model: ModelConfig,
        complexity: TaskComplexity,
        task_type: str,
        context_length: int,
    ) -> str:
        """Generate human-readable routing reason"""
        
        reasons = []
        
        if model.tier == ModelTier.LOCAL:
            reasons.append("Using on-device model for privacy and speed")
        else:
            reasons.append(f"Using cloud model for enhanced capabilities")
        
        if complexity == TaskComplexity.COMPLEX:
            reasons.append("Task requires deep reasoning")
        
        if context_length > 30000:
            reasons.append(f"Long context ({context_length} tokens)")
        
        if task_type in [s for s in model.strengths]:
            reasons.append(f"Optimized for {task_type}")
        
        return "; ".join(reasons)
    
    def _estimate_cost(self, model: ModelConfig, context_length: int) -> float:
        """Estimate cost for the request"""
        estimated_tokens = context_length + 1000  # Context + estimated response
        return (estimated_tokens / 1000) * model.cost_per_1k_tokens
    
    async def generate(
        self,
        prompt: str,
        model_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a response using the router or specified model.
        
        Args:
            prompt: User prompt
            model_id: Optional specific model to use (bypasses routing)
            **kwargs: Additional arguments for routing/generation
            
        Returns:
            Dictionary with response and metadata
        """
        
        # Route request if no model specified
        if model_id is None:
            decision = self.route_request(prompt, **kwargs)
            model_id = decision.selected_model
            routing_info = {
                "reason": decision.reason,
                "tier": decision.tier.value,
                "estimated_cost": decision.estimated_cost,
                "estimated_latency_ms": decision.estimated_latency_ms,
            }
        else:
            routing_info = {"manual_selection": True}
        
        model = self.models[model_id]
        
        # Generate response based on model tier
        if model.tier == ModelTier.LOCAL:
            response = await self._generate_local(model, prompt)
        else:
            response = await self._generate_cloud(model, prompt)
        
        return {
            "response": response,
            "model": model_id,
            "routing": routing_info,
        }
    
    async def _generate_local(self, model: ModelConfig, prompt: str) -> str:
        """Generate using local GGUF model via llama-cpp-python."""
        model_id = next((k for k, v in self.models.items() if v is model), None)
        gguf_file = _GGUF_FILENAMES.get(model_id)

        models_dir = Path(__file__).parent / "models"
        gguf_path = models_dir / gguf_file if gguf_file else None

        # Fall back to first available GGUF if the specific one isn't downloaded
        if not gguf_path or not gguf_path.exists():
            available = sorted(models_dir.glob("*.gguf"))
            if not available:
                return f"[LOCAL] No GGUF model found in {models_dir}. Please run download_models.py first."
            gguf_path = available[0]

        try:
            from llama_cpp import Llama

            cache_key = str(gguf_path)
            if cache_key not in _llama_instances:
                _llama_instances[cache_key] = Llama(
                    model_path=str(gguf_path),
                    n_ctx=2048,
                    n_threads=os.cpu_count() or 4,
                    verbose=False,
                )

            llm = _llama_instances[cache_key]
            loop = asyncio.get_event_loop()
            output = await loop.run_in_executor(
                None,
                lambda: llm.create_chat_completion(
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=512,
                    temperature=0.7,
                ),
            )
            return output["choices"][0]["message"]["content"]
        except Exception as e:
            return f"[LOCAL] Inference error: {e}"
    
    async def _generate_cloud(self, model: ModelConfig, prompt: str) -> str:
        """Generate using cloud API."""

        # Implement OpenRouter live calls. Keep placeholder fallback for providers
        # not yet wired with SDK/API clients.
        if model.api_key_env == "OPENROUTER_API_KEY":
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                return "[CLOUD] OpenRouter API key is missing. Set OPENROUTER_API_KEY in .env."

            free_only = _is_truthy_env("FREE_LLM_ONLY", "true")
            primary_model = _normalize_openrouter_model(
                os.getenv("OPENROUTER_MODEL", _OPENROUTER_DEFAULT_MODEL),
                free_only,
            )
            fallback_models = _parse_model_list(
                os.getenv("OPENROUTER_FREE_FALLBACK_MODELS", ""),
                free_only,
            )
            candidate_models = [primary_model] + [m for m in fallback_models if m != primary_model]

            max_retries = max(0, int(os.getenv("OPENROUTER_MAX_RETRIES", "2")))
            retry_base_seconds = max(0.0, float(os.getenv("OPENROUTER_RETRY_BASE_SECONDS", "0.75")))

            payload_base = {
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 512,
            }
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://localhost",
                "X-OpenRouter-Title": "edge-llm-project",
            }

            def _post_openrouter(payload: Dict[str, Any]) -> str:
                import requests

                response = requests.post(
                    model.endpoint or "https://openrouter.ai/api/v1/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=30,
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]

            try:
                loop = asyncio.get_event_loop()
                errors: List[str] = []

                for model_name in candidate_models:
                    payload = {**payload_base, "model": model_name}

                    for attempt in range(max_retries + 1):
                        try:
                            return await loop.run_in_executor(None, _post_openrouter, payload)
                        except Exception as e:
                            error_text = str(e)
                            is_rate_limited = "429" in error_text or "Too Many Requests" in error_text
                            is_last_try = attempt >= max_retries

                            if is_rate_limited and not is_last_try:
                                delay = retry_base_seconds * (2 ** attempt)
                                await asyncio.sleep(delay)
                                continue

                            errors.append(f"{model_name}: {e}")
                            break

                raise RuntimeError("; ".join(errors) if errors else "OpenRouter request failed")
            except Exception as e:
                fallback_mode = os.getenv("OPENROUTER_FALLBACK_MODE", "local").strip().lower()
                if fallback_mode != "error":
                    fallback = await self._fallback_to_local(prompt)
                    if fallback:
                        fallback_model_id, fallback_response = fallback
                        return (
                            f"[CLOUD->LOCAL FALLBACK] OpenRouter error: {e}\n"
                            f"Using local model: {fallback_model_id}\n"
                            f"{fallback_response}"
                        )
                return f"[CLOUD] OpenRouter error: {e}"

        # Placeholder fallback for providers not yet wired in this repository
        return f"[CLOUD] Response from {model.name}: {prompt[:50]}..."

    async def _fallback_to_local(self, prompt: str) -> Optional[tuple[str, str]]:
        """Best-effort fallback to an available local model."""
        local_priority = ["qwen2.5-3b", "phi-3.5-mini"]

        for model_id in local_priority:
            local_model = self.models.get(model_id)
            if not local_model or local_model.tier != ModelTier.LOCAL:
                continue

            response = await self._generate_local(local_model, prompt)
            # Avoid returning clearly failed local attempts.
            if response and not response.startswith("[LOCAL] Inference error"):
                return model_id, response

        return None
    
    def set_offline_mode(self, enabled: bool):
        """Enable/disable offline mode (local models only)"""
        self.offline_mode = enabled
    
    def set_battery_saver(self, enabled: bool):
        """Enable/disable battery saver mode (prefer local models)"""
        self.battery_saver = enabled


# Example usage and testing
def main():
    """Example usage of the LLM Edge Router"""
    
    router = LLMEdgeRouter()
    
    print("=== LLM Edge Router - Example Usage ===\n")
    
    # Example 1: Simple query (should use local model)
    decision1 = router.route_request(
        prompt="What is 2+2?",
        task_type="general",
    )
    print(f"Example 1 - Simple query:")
    print(f"  Selected: {decision1.selected_model}")
    print(f"  Reason: {decision1.reason}")
    print(f"  Tier: {decision1.tier.value}")
    print(f"  Latency: {decision1.estimated_latency_ms}ms\n")
    
    # Example 2: Complex coding task (should use cloud if available)
    decision2 = router.route_request(
        prompt="Write a comprehensive system for building a distributed database with ACID guarantees",
        task_type="coding",
        context_length=5000,
    )
    print(f"Example 2 - Complex coding:")
    print(f"  Selected: {decision2.selected_model}")
    print(f"  Reason: {decision2.reason}")
    print(f"  Tier: {decision2.tier.value}")
    print(f"  Latency: {decision2.estimated_latency_ms}ms\n")
    
    # Example 3: Long context analysis (should use model with large context)
    decision3 = router.route_request(
        prompt="Analyze this document and provide insights",
        task_type="analysis",
        context_length=80000,
    )
    print(f"Example 3 - Long context analysis:")
    print(f"  Selected: {decision3.selected_model}")
    print(f"  Reason: {decision3.reason}")
    print(f"  Tier: {decision3.tier.value}")
    print(f"  Latency: {decision3.estimated_latency_ms}ms\n")
    
    # Example 4: Offline mode (must use local)
    decision4 = router.route_request(
        prompt="Complex reasoning task",
        task_type="reasoning",
        force_offline=True,
    )
    print(f"Example 4 - Offline mode:")
    print(f"  Selected: {decision4.selected_model}")
    print(f"  Reason: {decision4.reason}")
    print(f"  Tier: {decision4.tier.value}")
    print(f"  Latency: {decision4.estimated_latency_ms}ms\n")
    
    # Example 5: Low latency requirement
    decision5 = router.route_request(
        prompt="Real-time code completion",
        task_type="coding",
        max_latency_ms=150,
    )
    print(f"Example 5 - Low latency requirement:")
    print(f"  Selected: {decision5.selected_model}")
    print(f"  Reason: {decision5.reason}")
    print(f"  Tier: {decision5.tier.value}")
    print(f"  Latency: {decision5.estimated_latency_ms}ms\n")
    
    print("\n=== Model Inventory ===")
    for model_id, model in router.models.items():
        print(f"\n{model_id}:")
        print(f"  Tier: {model.tier.value}")
        print(f"  Context: {model.max_context:,} tokens")
        print(f"  Latency: {model.avg_latency_ms}ms")
        print(f"  Offline: {model.supports_offline}")
        print(f"  Strengths: {', '.join(model.strengths)}")


if __name__ == "__main__":
    main()
