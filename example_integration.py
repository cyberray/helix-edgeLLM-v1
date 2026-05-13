"""
Complete Integration Example - Edge LLM System
Demonstrates the full hybrid edge-cloud system with reasoning and coding capabilities
"""

import asyncio
import os
from typing import Optional
from dotenv import load_dotenv
from llm_edge_router import LLMEdgeRouter, TaskComplexity
import json
from datetime import datetime


class EdgeLLMAgent:
    """
    Complete agent with reasoning and coding capabilities
    Combines local models with cloud fallback
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.router = LLMEdgeRouter()
        self.conversation_history = []
        self.metrics = []
        
        # Load environment variables
        load_dotenv()
        
        # Load config
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = self._default_config()
    
    def _default_config(self):
        return {
            "system_prompt": "You are a helpful AI assistant with strong reasoning and coding capabilities.",
            "max_conversation_length": 10,
            "enable_memory": True,
            "log_metrics": True,
        }
    
    async def chat(
        self,
        message: str,
        task_type: str = "general",
        stream: bool = False,
    ):
        """
        Main chat interface with intelligent routing
        """
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Determine context length
        context_length = sum(
            len(msg["content"]) * 1.3  # Rough token estimate
            for msg in self.conversation_history
        )
        
        # Route the request
        start_time = asyncio.get_event_loop().time()
        
        routing_decision = self.router.route_request(
            prompt=message,
            context_length=int(context_length),
            task_type=task_type,
        )
        
        print(f"\n🎯 Routing Decision:")
        print(f"   Model: {routing_decision.selected_model}")
        print(f"   Tier: {routing_decision.tier.value}")
        print(f"   Reason: {routing_decision.reason}")
        print(f"   Est. Latency: {routing_decision.estimated_latency_ms}ms\n")
        
        # Generate response
        result = await self.router.generate(
            prompt=self._format_prompt(message),
            model_id=routing_decision.selected_model
        )
        
        end_time = asyncio.get_event_loop().time()
        actual_latency = (end_time - start_time) * 1000
        
        # Add to history
        self.conversation_history.append({
            "role": "assistant",
            "content": result["response"],
            "model": routing_decision.selected_model,
            "timestamp": datetime.now().isoformat()
        })
        
        # Log metrics
        if self.config.get("log_metrics"):
            self._log_metrics({
                "model": routing_decision.selected_model,
                "tier": routing_decision.tier.value,
                "latency_ms": actual_latency,
                "task_type": task_type,
                "success": True,
            })
        
        # Trim conversation history if needed
        if len(self.conversation_history) > self.config["max_conversation_length"] * 2:
            self.conversation_history = self.conversation_history[-self.config["max_conversation_length"] * 2:]
        
        return result["response"]
    
    def _format_prompt(self, message: str) -> str:
        """Format prompt with system message and conversation history"""
        
        prompt_parts = [self.config["system_prompt"], "\n\n"]
        
        # Add recent conversation history (last 5 exchanges)
        recent_history = self.conversation_history[-10:]
        for msg in recent_history:
            role = msg["role"].capitalize()
            content = msg["content"]
            prompt_parts.append(f"{role}: {content}\n\n")
        
        prompt_parts.append(f"User: {message}\n\nAssistant:")
        
        return "".join(prompt_parts)
    
    def _log_metrics(self, metrics: dict):
        """Log inference metrics"""
        metrics["timestamp"] = datetime.now().isoformat()
        self.metrics.append(metrics)
        
        # Also write to file
        with open("metrics.jsonl", "a") as f:
            f.write(json.dumps(metrics) + "\n")
    
    async def analyze_code(self, code: str, language: str = "python"):
        """Specialized code analysis"""
        
        prompt = f"""Analyze this {language} code for:
1. Potential bugs or issues
2. Performance optimizations
3. Best practices violations
4. Security concerns

Code:
```{language}
{code}
```

Provide detailed analysis with specific recommendations."""
        
        return await self.chat(prompt, task_type="coding")
    
    async def solve_problem(self, problem: str, approach: str = "step-by-step"):
        """Complex reasoning task"""
        
        prompt = f"""Solve this problem using {approach} reasoning:

{problem}

Break down your thinking process and provide a clear solution."""
        
        return await self.chat(prompt, task_type="reasoning")
    
    async def generate_code(
        self,
        description: str,
        language: str = "python",
        include_tests: bool = False
    ):
        """Code generation with optional tests"""
        
        prompt = f"""Generate {language} code for:

{description}

Requirements:
- Clean, readable code
- Proper error handling
- Type hints (if applicable)
- Comments for complex logic
"""
        
        if include_tests:
            prompt += "- Include unit tests\n"
        
        return await self.chat(prompt, task_type="coding")
    
    def get_metrics_summary(self):
        """Get summary of usage metrics"""
        
        if not self.metrics:
            return "No metrics available"
        
        total_requests = len(self.metrics)
        avg_latency = sum(m["latency_ms"] for m in self.metrics) / total_requests
        
        tier_distribution = {}
        for m in self.metrics:
            tier = m["tier"]
            tier_distribution[tier] = tier_distribution.get(tier, 0) + 1
        
        return {
            "total_requests": total_requests,
            "avg_latency_ms": round(avg_latency, 2),
            "tier_distribution": tier_distribution,
            "success_rate": sum(1 for m in self.metrics if m.get("success")) / total_requests
        }
    
    def save_conversation(self, filename: str = "conversation.json"):
        """Save conversation history"""
        
        with open(filename, 'w') as f:
            json.dump({
                "conversation": self.conversation_history,
                "metrics": self.get_metrics_summary(),
            }, f, indent=2)
        
        print(f"Conversation saved to {filename}")


# Example usage demonstrations
async def demo_simple_query(agent: EdgeLLMAgent):
    """Demo: Simple query (should use local model)"""
    print("\n" + "="*60)
    print("DEMO 1: Simple Query (Local Model)")
    print("="*60)
    
    response = await agent.chat("What is the Pythagorean theorem?")
    print(f"Response: {response}")


async def demo_coding_task(agent: EdgeLLMAgent):
    """Demo: Coding task"""
    print("\n" + "="*60)
    print("DEMO 2: Code Generation")
    print("="*60)
    
    response = await agent.generate_code(
        description="A function to find the longest palindromic substring in a string",
        language="python",
        include_tests=True
    )
    print(f"Generated Code:\n{response}")


async def demo_code_analysis(agent: EdgeLLMAgent):
    """Demo: Code analysis"""
    print("\n" + "="*60)
    print("DEMO 3: Code Analysis")
    print("="*60)
    
    buggy_code = """
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)

# Usage
result = calculate_average([1, 2, 3, 0])
"""
    
    response = await agent.analyze_code(buggy_code)
    print(f"Analysis:\n{response}")


async def demo_complex_reasoning(agent: EdgeLLMAgent):
    """Demo: Complex reasoning (should prefer cloud)"""
    print("\n" + "="*60)
    print("DEMO 4: Complex Reasoning")
    print("="*60)
    
    response = await agent.solve_problem(
        problem="""A train travels from City A to City B at 60 mph. 
On the return trip, it travels at 40 mph due to weather conditions. 
What is the average speed for the entire round trip?"""
    )
    print(f"Solution:\n{response}")


async def demo_multi_turn_conversation(agent: EdgeLLMAgent):
    """Demo: Multi-turn conversation with context"""
    print("\n" + "="*60)
    print("DEMO 5: Multi-turn Conversation")
    print("="*60)
    
    responses = []
    
    # Turn 1
    r1 = await agent.chat("I'm building a web scraper in Python. Where should I start?")
    responses.append(("Turn 1", r1))
    
    # Turn 2 (with context)
    r2 = await agent.chat("What libraries would you recommend?")
    responses.append(("Turn 2", r2))
    
    # Turn 3 (with context)
    r3 = await agent.chat("Show me a simple example using those libraries")
    responses.append(("Turn 3", r3))
    
    for turn, response in responses:
        print(f"\n{turn}:\n{response[:200]}...")


async def demo_offline_mode(agent: EdgeLLMAgent):
    """Demo: Offline mode (force local)"""
    print("\n" + "="*60)
    print("DEMO 6: Offline Mode")
    print("="*60)
    
    # Simulate offline
    agent.router.set_offline_mode(True)
    
    response = await agent.chat(
        "Explain how binary search works",
        task_type="reasoning"
    )
    print(f"Response (offline):\n{response}")
    
    # Re-enable online
    agent.router.set_offline_mode(False)


async def demo_battery_saver(agent: EdgeLLMAgent):
    """Demo: Battery saver mode"""
    print("\n" + "="*60)
    print("DEMO 7: Battery Saver Mode")
    print("="*60)
    
    # Enable battery saver
    agent.router.set_battery_saver(True)
    
    response = await agent.chat("What are design patterns in software engineering?")
    print(f"Response (battery saver):\n{response}")
    
    # Disable battery saver
    agent.router.set_battery_saver(False)


async def interactive_mode(agent: EdgeLLMAgent):
    """Interactive chat mode"""
    print("\n" + "="*60)
    print("Interactive Mode - Type 'quit' to exit")
    print("="*60 + "\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            # Parse special commands
            if user_input.startswith("/"):
                await handle_command(agent, user_input)
                continue
            
            # Regular chat
            response = await agent.chat(user_input)
            print(f"\nAssistant: {response}\n")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    # Show summary
    print("\n" + "="*60)
    print("Session Summary")
    print("="*60)
    summary = agent.get_metrics_summary()
    for key, value in summary.items():
        print(f"{key}: {value}")


async def handle_command(agent: EdgeLLMAgent, command: str):
    """Handle special commands"""
    
    if command == "/help":
        print("""
Available commands:
  /help       - Show this help
  /metrics    - Show usage metrics
  /save       - Save conversation
  /clear      - Clear conversation history
  /offline    - Toggle offline mode
  /battery    - Toggle battery saver mode
  /models     - List available models
""")
    
    elif command == "/metrics":
        summary = agent.get_metrics_summary()
        print(json.dumps(summary, indent=2))
    
    elif command == "/save":
        agent.save_conversation()
    
    elif command == "/clear":
        agent.conversation_history = []
        print("Conversation cleared")
    
    elif command == "/offline":
        current = agent.router.offline_mode
        agent.router.set_offline_mode(not current)
        print(f"Offline mode: {'ON' if not current else 'OFF'}")
    
    elif command == "/battery":
        current = agent.router.battery_saver
        agent.router.set_battery_saver(not current)
        print(f"Battery saver: {'ON' if not current else 'OFF'}")
    
    elif command == "/models":
        print("\nAvailable models:")
        for model_id, model in agent.router.models.items():
            print(f"  - {model_id} ({model.tier.value})")


async def main():
    """Main entry point"""
    
    print("""
╔══════════════════════════════════════════════════════════╗
║   Edge LLM System - Complete Integration Demo           ║
║   Hybrid Local + Cloud AI with Reasoning & Coding       ║
╚══════════════════════════════════════════════════════════╝
""")
    
    # Initialize agent
    agent = EdgeLLMAgent()
    
    # Run demonstrations
    print("\nRunning demonstrations...\n")
    
    await demo_simple_query(agent)
    await asyncio.sleep(1)
    
    await demo_coding_task(agent)
    await asyncio.sleep(1)
    
    await demo_code_analysis(agent)
    await asyncio.sleep(1)
    
    await demo_complex_reasoning(agent)
    await asyncio.sleep(1)
    
    await demo_multi_turn_conversation(agent)
    await asyncio.sleep(1)
    
    await demo_offline_mode(agent)
    await asyncio.sleep(1)
    
    await demo_battery_saver(agent)
    await asyncio.sleep(1)
    
    # Show metrics
    print("\n" + "="*60)
    print("Overall Metrics")
    print("="*60)
    summary = agent.get_metrics_summary()
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    # Interactive mode
    print("\n\nEnter interactive mode? (y/N): ", end="")
    if input().strip().lower() == 'y':
        await interactive_mode(agent)
    
    print("\n👋 Thanks for trying Edge LLM System!")


if __name__ == "__main__":
    asyncio.run(main())
