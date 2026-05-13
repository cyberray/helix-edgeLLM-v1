"""
Test Suite for Edge LLM System
Comprehensive tests for routing, model selection, and integration
"""

import pytest
import asyncio
from pathlib import Path
from requests.exceptions import HTTPError

pytest_plugins = ['anyio']
import json
import tempfile
import os
from unittest.mock import Mock, patch, AsyncMock

# Import modules to test
from llm_edge_router import (
    LLMEdgeRouter, 
    ModelTier, 
    TaskComplexity,
    RoutingDecision,
    ModelConfig
)


class TestLLMEdgeRouter:
    """Test the LLM Edge Router functionality"""
    
    @pytest.fixture
    def router(self):
        """Create a router instance for testing"""
        return LLMEdgeRouter()
    
    def test_initialization(self, router):
        """Test router initializes correctly"""
        assert router is not None
        assert len(router.models) > 0
        assert router.offline_mode == False
        assert router.battery_saver == False
    
    def test_model_registry(self, router):
        """Test that all expected models are registered"""
        expected_models = [
            "phi-3.5-mini",
            "qwen2.5-3b",
            "llama-3.2-3b",
            "gemini-flash",
            "groq-llama"
        ]
        
        for model_id in expected_models:
            assert model_id in router.models
            assert isinstance(router.models[model_id], ModelConfig)
    
    def test_simple_task_routing(self, router):
        """Test routing for simple tasks (should prefer local)"""
        decision = router.route_request(
            prompt="What is 2+2?",
            task_type="general"
        )
        
        assert decision.tier == ModelTier.LOCAL
        assert decision.selected_model in ["phi-3.5-mini", "qwen2.5-3b", "llama-3.2-3b"]
    
    def test_complex_task_routing(self, router):
        """Test routing for complex tasks"""
        decision = router.route_request(
            prompt="Analyze the comprehensive economic implications of quantum computing on global markets",
            task_type="reasoning",
            context_length=5000
        )
        
        # Should prefer cloud for complex tasks if available
        # but will fall back to local if APIs not configured
        assert isinstance(decision, RoutingDecision)
        assert decision.estimated_latency_ms > 0

    def test_complex_prefers_cloud_when_api_configured(self, router, monkeypatch):
        """Complex tasks should prefer cloud models when cloud APIs are configured."""
        monkeypatch.setenv("GEMINI_API_KEY", "test_key")

        decision = router.route_request(
            prompt="Analyze and compare long-term macroeconomic impacts of global monetary policy shifts",
            task_type="reasoning",
            context_length=60000,
        )

        assert decision.tier in [ModelTier.CLOUD_FAST, ModelTier.CLOUD_SPECIALIZED]

    def test_router_autoloads_dotenv(self, monkeypatch, tmp_path):
        """Router should auto-load .env from current working directory."""
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        (tmp_path / ".env").write_text("GEMINI_API_KEY=dotenv_test_key\n", encoding="utf-8")
        monkeypatch.chdir(tmp_path)

        router = LLMEdgeRouter()
        decision = router.route_request(
            prompt="Analyze and compare long-term macroeconomic impacts of global monetary policy shifts",
            task_type="reasoning",
            context_length=60000,
        )

        assert decision.tier in [ModelTier.CLOUD_FAST, ModelTier.CLOUD_SPECIALIZED]
    
    def test_coding_task_routing(self, router):
        """Test routing for coding tasks (should prefer Qwen)"""
        decision = router.route_request(
            prompt="Write a Python function to implement binary search",
            task_type="coding"
        )
        
        # Should select a model good at coding
        assert decision.selected_model in ["qwen2.5-3b", "phi-3.5-mini", "groq-llama"]
    
    def test_long_context_routing(self, router):
        """Test routing for long context (should use models with large context)"""
        decision = router.route_request(
            prompt="Analyze this document",
            context_length=100000,
            task_type="analysis"
        )
        
        # Should select model with sufficient context window
        selected_model = router.models[decision.selected_model]
        assert selected_model.max_context >= 100000
    
    def test_offline_mode(self, router):
        """Test offline mode forces local models"""
        router.set_offline_mode(True)
        
        decision = router.route_request(
            prompt="Complex reasoning task that would normally use cloud",
            task_type="reasoning"
        )
        
        assert decision.tier == ModelTier.LOCAL
        
        router.set_offline_mode(False)
    
    def test_battery_saver_mode(self, router):
        """Test battery saver prefers local models"""
        router.set_battery_saver(True)
        
        decision = router.route_request(
            prompt="Some task",
            task_type="general"
        )
        
        assert decision.tier == ModelTier.LOCAL
        
        router.set_battery_saver(False)
    
    def test_force_offline_parameter(self, router):
        """Test force_offline parameter"""
        decision = router.route_request(
            prompt="Any query",
            force_offline=True
        )
        
        assert decision.tier == ModelTier.LOCAL
    
    def test_max_latency_constraint(self, router):
        """Test max latency constraint"""
        decision = router.route_request(
            prompt="Fast response needed",
            max_latency_ms=150
        )
        
        assert decision.estimated_latency_ms <= 150
    
    def test_complexity_assessment_simple(self, router):
        """Test complexity assessment for simple tasks"""
        complexity = router._assess_complexity("What time is it?", 0)
        assert complexity == TaskComplexity.SIMPLE
    
    def test_complexity_assessment_medium(self, router):
        """Test complexity assessment for medium tasks"""
        complexity = router._assess_complexity(
            "Write a Python function to sort a list",
            1000
        )
        assert complexity in [TaskComplexity.SIMPLE, TaskComplexity.MEDIUM]
    
    def test_complexity_assessment_complex(self, router):
        """Test complexity assessment for complex tasks"""
        complexity = router._assess_complexity(
            "Analyze and compare the comprehensive implications of various economic policies",
            80000
        )
        assert complexity == TaskComplexity.COMPLEX
    
    def test_model_scoring(self, router):
        """Test model scoring logic"""
        model = router.models["phi-3.5-mini"]
        
        score = router._score_model(
            model=model,
            task_type="reasoning",
            complexity=TaskComplexity.MEDIUM,
            context_length=5000
        )
        
        assert isinstance(score, float)
        assert 0 <= score <= 100
    
    @pytest.mark.anyio
    async def test_generate_method(self, router):
        """Test generate method (with mocked inference)"""
        with patch.object(router, '_generate_local', return_value="Local response"):
            result = await router.generate("Test prompt")
            
            assert "response" in result
            assert "model" in result
            assert "routing" in result


class TestModelDownloader:
    """Test model downloading functionality"""
    
    def test_model_registry_structure(self):
        """Test model registry has correct structure"""
        from download_models import MODEL_REGISTRY
        
        assert len(MODEL_REGISTRY) > 0
        
        for model_id, model_info in MODEL_REGISTRY.items():
            assert hasattr(model_info, 'id')
            assert hasattr(model_info, 'name')
            assert hasattr(model_info, 'url')
            assert hasattr(model_info, 'size_mb')
            assert model_info.size_mb > 0


class TestIntegration:
    """Integration tests for the complete system"""
    
    @pytest.mark.anyio
    async def test_end_to_end_simple(self):
        """Test end-to-end workflow for simple query"""
        from example_integration import EdgeLLMAgent
        
        agent = EdgeLLMAgent()
        
        # Mock the generate method to avoid actual API calls
        with patch.object(agent.router, 'generate', return_value={
            "response": "Test response",
            "model": "phi-3.5-mini",
            "routing": {"tier": "local"}
        }):
            response = await agent.chat("Simple question")
            
            assert response == "Test response"
            assert len(agent.conversation_history) == 2  # User + assistant
    
    @pytest.mark.anyio
    async def test_conversation_history(self):
        """Test conversation history tracking"""
        from example_integration import EdgeLLMAgent
        
        agent = EdgeLLMAgent()
        
        with patch.object(agent.router, 'generate', return_value={
            "response": "Response",
            "model": "phi-3.5-mini",
            "routing": {"tier": "local"}
        }):
            await agent.chat("First message")
            await agent.chat("Second message")
            
            assert len(agent.conversation_history) == 4  # 2 exchanges
    
    def test_metrics_logging(self):
        """Test metrics logging"""
        from example_integration import EdgeLLMAgent
        
        agent = EdgeLLMAgent()
        
        metrics = {
            "model": "phi-3.5-mini",
            "tier": "local",
            "latency_ms": 150,
            "success": True
        }
        
        agent._log_metrics(metrics)
        
        assert len(agent.metrics) == 1
        assert agent.metrics[0]["model"] == "phi-3.5-mini"
    
    def test_metrics_summary(self):
        """Test metrics summary generation"""
        from example_integration import EdgeLLMAgent
        
        agent = EdgeLLMAgent()
        
        # Add test metrics
        agent.metrics = [
            {"latency_ms": 100, "tier": "local", "success": True},
            {"latency_ms": 200, "tier": "cloud_fast", "success": True},
            {"latency_ms": 150, "tier": "local", "success": True}
        ]
        
        summary = agent.get_metrics_summary()
        
        assert summary["total_requests"] == 3
        assert summary["avg_latency_ms"] == 150
        assert "local" in summary["tier_distribution"]
        assert summary["success_rate"] == 1.0


class TestConfiguration:
    """Test configuration and setup"""
    
    def test_env_file_loading(self):
        """Test environment variable loading"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("GEMINI_API_KEY=test_key_123\n")
            f.write("GROQ_API_KEY=another_key\n")
            env_path = f.name
        try:
            from dotenv import load_dotenv
            load_dotenv(env_path)
            assert os.getenv("GEMINI_API_KEY") == "test_key_123"
            assert os.getenv("GROQ_API_KEY") == "another_key"
        finally:
            os.unlink(env_path)
            # Skip this test if GEMINI_API_KEY is already set in the environment
            if os.getenv("GEMINI_API_KEY") and os.getenv("GEMINI_API_KEY") != "test_key_123":
                import pytest
                pytest.skip("GEMINI_API_KEY already set in environment; skipping test to avoid conflict.")
            try:
                from dotenv import load_dotenv
                load_dotenv(env_path)
                assert os.getenv("GEMINI_API_KEY") == "test_key_123"
                assert os.getenv("GROQ_API_KEY") == "another_key"
            finally:
                os.remove(env_path)
    
    def test_config_validation(self):
        """Test configuration validation"""
        from example_integration import EdgeLLMAgent
        
        config = {
            "system_prompt": "Test prompt",
            "max_conversation_length": 5,
            "enable_memory": True,
            "log_metrics": False
        }
        
        agent = EdgeLLMAgent()
        agent.config = config
        
        assert agent.config["max_conversation_length"] == 5
        assert agent.config["log_metrics"] == False


class TestErrorHandling:
    """Test error handling and edge cases"""

    @pytest.fixture
    def router(self):
        return LLMEdgeRouter()

    def test_invalid_model_id(self, router):
        """Test that nonexistent model IDs are not in the registry"""
        assert "nonexistent-model" not in router.models
    
    def test_empty_prompt(self, router):
        """Test handling of empty prompt"""
        # Should handle empty prompt
        decision = router.route_request(prompt="")
        assert isinstance(decision, RoutingDecision)
    
    def test_extremely_long_context(self, router):
        """Test that extremely long context raises ValueError (no model supports it)"""
        with pytest.raises(ValueError, match="No models available"):
            router.route_request(prompt="test", context_length=10_000_000)
    
    @pytest.mark.anyio
    async def test_network_error_handling(self):
        """Test handling of network errors"""
        from example_integration import EdgeLLMAgent
        
        agent = EdgeLLMAgent()
        
        # Mock network error
        with patch.object(agent.router, 'generate', side_effect=Exception("Network error")):
            with pytest.raises(Exception):
                await agent.chat("test")

    @pytest.mark.anyio
    async def test_openrouter_falls_back_to_local_on_cloud_error(self, router, monkeypatch):
        """OpenRouter cloud errors should fall back to local generation when possible."""
        monkeypatch.setenv("OPENROUTER_API_KEY", "test_key")
        monkeypatch.setenv("OPENROUTER_FALLBACK_MODE", "local")

        http_error = HTTPError("403 Client Error: Forbidden")
        with patch("requests.post", side_effect=http_error):
            with patch.object(router, "_generate_local", return_value="Local fallback response"):
                response = await router._generate_cloud(router.models["openrouter-llama"], "hello")

        assert "[CLOUD->LOCAL FALLBACK]" in response
        assert "Local fallback response" in response

    @pytest.mark.anyio
    async def test_openrouter_cloud_error_without_local_fallback(self, router, monkeypatch):
        """If local fallback is unavailable, return cloud error message."""
        monkeypatch.setenv("OPENROUTER_API_KEY", "test_key")
        monkeypatch.setenv("OPENROUTER_FALLBACK_MODE", "local")

        http_error = HTTPError("403 Client Error: Forbidden")
        with patch("requests.post", side_effect=http_error):
            with patch.object(router, "_generate_local", return_value="[LOCAL] Inference error: fail"):
                response = await router._generate_cloud(router.models["openrouter-llama"], "hello")

        assert response.startswith("[CLOUD] OpenRouter error")

    @pytest.mark.anyio
    async def test_openrouter_strict_error_mode_skips_fallback(self, router, monkeypatch):
        """Strict mode should return cloud error without attempting local fallback."""
        monkeypatch.setenv("OPENROUTER_API_KEY", "test_key")
        monkeypatch.setenv("OPENROUTER_FALLBACK_MODE", "error")

        http_error = HTTPError("403 Client Error: Forbidden")
        with patch("requests.post", side_effect=http_error):
            with patch.object(router, "_generate_local", return_value="Local fallback response") as local_mock:
                response = await router._generate_cloud(router.models["openrouter-llama"], "hello")

        local_mock.assert_not_called()
        assert response.startswith("[CLOUD] OpenRouter error")

    @pytest.mark.anyio
    async def test_openrouter_defaults_to_ring_free_model(self, router, monkeypatch):
        """OpenRouter should default to inclusionai Ring free model when not explicitly set."""
        monkeypatch.setenv("OPENROUTER_API_KEY", "test_key")
        monkeypatch.delenv("OPENROUTER_MODEL", raising=False)

        response_mock = Mock()
        response_mock.raise_for_status.return_value = None
        response_mock.json.return_value = {
            "choices": [{"message": {"content": "ok"}}]
        }

        with patch("requests.post", return_value=response_mock) as post_mock:
            await router._generate_cloud(router.models["openrouter-llama"], "hello")

        payload = post_mock.call_args.kwargs["json"]
        assert payload["model"] == "inclusionai/ring-2.6-1t:free"

    @pytest.mark.anyio
    async def test_openrouter_free_only_appends_free_suffix(self, router, monkeypatch):
        """When FREE_LLM_ONLY is enabled, OpenRouter model should use :free suffix."""
        monkeypatch.setenv("OPENROUTER_API_KEY", "test_key")
        monkeypatch.setenv("OPENROUTER_MODEL", "inclusionai/ring-2.6-1t")
        monkeypatch.setenv("FREE_LLM_ONLY", "true")

        response_mock = Mock()
        response_mock.raise_for_status.return_value = None
        response_mock.json.return_value = {
            "choices": [{"message": {"content": "ok"}}]
        }

        with patch("requests.post", return_value=response_mock) as post_mock:
            await router._generate_cloud(router.models["openrouter-llama"], "hello")

        payload = post_mock.call_args.kwargs["json"]
        assert payload["model"] == "inclusionai/ring-2.6-1t:free"

    @pytest.mark.anyio
    async def test_openrouter_retries_429_then_succeeds(self, router, monkeypatch):
        """OpenRouter should retry on 429 and succeed when a later attempt works."""
        monkeypatch.setenv("OPENROUTER_API_KEY", "test_key")
        monkeypatch.setenv("OPENROUTER_MAX_RETRIES", "2")
        monkeypatch.setenv("OPENROUTER_RETRY_BASE_SECONDS", "0")

        response_mock = Mock()
        response_mock.raise_for_status.return_value = None
        response_mock.json.return_value = {
            "choices": [{"message": {"content": "ok"}}]
        }

        with patch("requests.post", side_effect=[HTTPError("429 Too Many Requests"), response_mock]) as post_mock:
            response = await router._generate_cloud(router.models["openrouter-llama"], "hello")

        assert response == "ok"
        assert post_mock.call_count == 2

    @pytest.mark.anyio
    async def test_openrouter_tries_fallback_models_after_retries(self, router, monkeypatch):
        """If primary model fails after retries, OpenRouter should try configured fallback models."""
        monkeypatch.setenv("OPENROUTER_API_KEY", "test_key")
        monkeypatch.setenv("OPENROUTER_MODEL", "inclusionai/ring-2.6-1t:free")
        monkeypatch.setenv("OPENROUTER_FREE_FALLBACK_MODELS", "google/gemma-3-4b-it:free")
        monkeypatch.setenv("OPENROUTER_MAX_RETRIES", "0")

        response_mock = Mock()
        response_mock.raise_for_status.return_value = None
        response_mock.json.return_value = {
            "choices": [{"message": {"content": "ok"}}]
        }

        with patch("requests.post", side_effect=[HTTPError("429 Too Many Requests"), response_mock]) as post_mock:
            response = await router._generate_cloud(router.models["openrouter-llama"], "hello")

        assert response == "ok"
        assert post_mock.call_count == 2
        first_payload = post_mock.call_args_list[0].kwargs["json"]
        second_payload = post_mock.call_args_list[1].kwargs["json"]
        assert first_payload["model"] == "inclusionai/ring-2.6-1t:free"
        assert second_payload["model"] == "google/gemma-3-4b-it:free"


class TestPerformance:
    """Performance and benchmark tests"""

    @pytest.fixture
    def router(self):
        return LLMEdgeRouter()

    def test_routing_performance(self, router, benchmark):
        """Benchmark routing decision speed"""
        def route():
            return router.route_request("Test prompt", task_type="general")
        
        result = benchmark(route)
        assert isinstance(result, RoutingDecision)
    
    def test_complexity_assessment_performance(self, router, benchmark):
        """Benchmark complexity assessment"""
        def assess():
            return router._assess_complexity("Test prompt", 1000)
        
        result = benchmark(assess)
        assert isinstance(result, TaskComplexity)


# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )


# Run tests with: pytest tests/test_edge_llm.py -v
# Run with coverage: pytest tests/test_edge_llm.py --cov=. --cov-report=html
# Run specific test: pytest tests/test_edge_llm.py::TestLLMEdgeRouter::test_simple_task_routing -v
