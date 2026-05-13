#!/usr/bin/env python3
"""
Edge LLM CLI - Command Line Interface
Quick tool for interacting with the Edge LLM System
"""

import click
import asyncio
import json
import os
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich.panel import Panel
from rich.markdown import Markdown
from typing import Optional
import time

from llm_edge_router import LLMEdgeRouter
from example_integration import EdgeLLMAgent

console = Console()


ROUTING_API_KEYS = [
    ("GEMINI_API_KEY", "Google Gemini"),
    ("GROQ_API_KEY", "Groq"),
    ("OPENROUTER_API_KEY", "OpenRouter"),
    ("TOGETHER_API_KEY", "Together.ai"),
]

OPTIONAL_API_KEYS = [
    ("HF_API_TOKEN", "Hugging Face"),
]


def is_key_configured(value: Optional[str]) -> bool:
    if not value:
        return False
    value_lower = value.strip().lower()
    placeholder_markers = [
        "your_",
        "_here",
        "replace_me",
        "changeme",
        "example",
    ]
    return not any(marker in value_lower for marker in placeholder_markers)


def get_effective_key(env_name: str) -> Optional[str]:
    value = os.getenv(env_name)
    if env_name == "HF_API_TOKEN" and not is_key_configured(value):
        value = os.getenv("HF_API_KEY")
    return value


def print_startup_key_warning() -> None:
    placeholders = []
    for env_name, display_name in ROUTING_API_KEYS:
        value = get_effective_key(env_name)
        if value and not is_key_configured(value):
            placeholders.append(display_name)

    if placeholders:
        warning_text = (
            "⚠️ Placeholder API keys detected\n"
            "Cloud routing may be unavailable until real routing keys are configured.\n"
            f"Detected placeholders: {', '.join(placeholders)}\n"
            "Use: python edge-llm-cli.py config"
        )
        console.print(Panel.fit(warning_text, style="bold yellow"))


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Edge LLM System - Command Line Interface"""
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except Exception:
        # Continue even if dotenv is missing or fails
        pass

    print_startup_key_warning()


@cli.command()
@click.argument('prompt', required=False)
@click.option('--model', '-m', help='Specific model to use')
@click.option('--task-type', '-t', default='general', help='Task type (general, coding, reasoning)')
@click.option('--offline', is_flag=True, help='Force offline/local mode')
@click.option('--stream', is_flag=True, help='Stream response')
def chat(prompt, model, task_type, offline, stream):
    """Chat with the LLM system"""
    
    async def run_chat():
        agent = EdgeLLMAgent()
        
        if offline:
            agent.router.set_offline_mode(True)
        
        # Interactive mode if no prompt
        if not prompt:
            console.print(Panel.fit(
                "💬 Interactive Chat Mode\nType 'quit' to exit, '/help' for commands",
                style="bold blue"
            ))
            
            while True:
                try:
                    user_input = console.input("\n[bold green]You:[/] ").strip()
                    
                    if not user_input:
                        continue
                    
                    if user_input.lower() in ['quit', 'exit', 'q']:
                        break
                    
                    if user_input.startswith('/'):
                        handle_chat_command(agent, user_input)
                        continue
                    
                    # Generate response
                    with console.status("[bold yellow]Thinking..."):
                        response = await agent.chat(user_input, task_type=task_type)
                    
                    console.print(f"\n[bold cyan]Assistant:[/] {response}")
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    console.print(f"[bold red]Error:[/] {e}")
            
            # Show session summary
            summary = agent.get_metrics_summary()
            console.print(f"\n[dim]Session: {summary['total_requests']} requests, "
                         f"avg {summary['avg_latency_ms']:.0f}ms[/]")
        
        # Single query mode
        else:
            with console.status("[bold yellow]Generating..."):
                response = await agent.chat(prompt, task_type=task_type)
            
            console.print(Panel(response, title="Response", style="cyan"))
    
    asyncio.run(run_chat())


def handle_chat_command(agent, command):
    """Handle special chat commands"""
    
    if command == '/help':
        console.print("""
[bold]Available Commands:[/]
  /help      - Show this help
  /models    - List available models
  /metrics   - Show usage metrics
  /save      - Save conversation
  /clear     - Clear history
  /offline   - Toggle offline mode
  /battery   - Toggle battery saver
        """)
    
    elif command == '/models':
        table = Table(title="Available Models")
        table.add_column("ID", style="cyan")
        table.add_column("Tier", style="green")
        table.add_column("Context", style="yellow")
        
        for model_id, model in agent.router.models.items():
            table.add_row(
                model_id,
                model.tier.value,
                f"{model.max_context:,}"
            )
        
        console.print(table)
    
    elif command == '/metrics':
        summary = agent.get_metrics_summary()
        console.print(json.dumps(summary, indent=2))
    
    elif command == '/save':
        agent.save_conversation()
        console.print("[green]✓ Conversation saved[/]")
    
    elif command == '/clear':
        agent.conversation_history = []
        console.print("[green]✓ History cleared[/]")
    
    elif command == '/offline':
        current = agent.router.offline_mode
        agent.router.set_offline_mode(not current)
        console.print(f"[green]Offline mode: {'ON' if not current else 'OFF'}[/]")
    
    elif command == '/battery':
        current = agent.router.battery_saver
        agent.router.set_battery_saver(not current)
        console.print(f"[green]Battery saver: {'ON' if not current else 'OFF'}[/]")


@cli.command()
@click.option('--model', '-m', help='Specific model to benchmark')
@click.option('--iterations', '-n', default=10, help='Number of iterations')
def benchmark(model, iterations):
    """Benchmark model performance"""
    
    console.print(Panel.fit("🔥 Benchmarking Edge LLM System", style="bold blue"))
    
    router = LLMEdgeRouter()
    
    test_prompts = [
        ("Simple: What is 2+2?", "general"),
        ("Medium: Write a Python function to reverse a string", "coding"),
        ("Complex: Explain quantum computing", "reasoning"),
    ]
    
    results = []
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Running benchmarks...", total=len(test_prompts) * iterations)
        
        for prompt, task_type in test_prompts:
            latencies = []
            
            for i in range(iterations):
                start = time.time()
                decision = router.route_request(prompt, task_type=task_type)
                end = time.time()
                
                latency_ms = (end - start) * 1000
                latencies.append(latency_ms)
                
                progress.update(task, advance=1)
            
            avg_latency = sum(latencies) / len(latencies)
            min_latency = min(latencies)
            max_latency = max(latencies)
            p95_latency = sorted(latencies)[int(0.95 * len(latencies))]
            
            results.append({
                "prompt": prompt,
                "model": decision.selected_model,
                "tier": decision.tier.value,
                "avg_ms": avg_latency,
                "min_ms": min_latency,
                "max_ms": max_latency,
                "p95_ms": p95_latency,
            })
    
    # Display results
    table = Table(title="Benchmark Results")
    table.add_column("Query", style="cyan")
    table.add_column("Model", style="green")
    table.add_column("Tier", style="yellow")
    table.add_column("Avg (ms)", justify="right")
    table.add_column("P95 (ms)", justify="right")
    
    for result in results:
        table.add_row(
            result["prompt"][:40] + "..." if len(result["prompt"]) > 40 else result["prompt"],
            result["model"],
            result["tier"],
            f"{result['avg_ms']:.2f}",
            f"{result['p95_ms']:.2f}"
        )
    
    console.print(table)


@cli.command()
def models():
    """List all available models"""
    
    router = LLMEdgeRouter()
    
    # Local models
    console.print(Panel.fit("📦 Local Models", style="bold green"))
    
    local_table = Table()
    local_table.add_column("ID", style="cyan")
    local_table.add_column("Name", style="white")
    local_table.add_column("Context", justify="right")
    local_table.add_column("Latency", justify="right")
    local_table.add_column("Strengths")
    
    for model_id, model in router.models.items():
        if model.tier.value == "local":
            local_table.add_row(
                model_id,
                model.name,
                f"{model.max_context:,}",
                f"{model.avg_latency_ms}ms",
                ", ".join(model.strengths[:2])
            )
    
    console.print(local_table)
    
    # Cloud models
    console.print("\n")
    console.print(Panel.fit("☁️  Cloud Models", style="bold blue"))
    
    cloud_table = Table()
    cloud_table.add_column("ID", style="cyan")
    cloud_table.add_column("Name", style="white")
    cloud_table.add_column("Context", justify="right")
    cloud_table.add_column("Cost", justify="right")
    cloud_table.add_column("Strengths")
    
    for model_id, model in router.models.items():
        if model.tier.value != "local":
            cost = "Free" if model.cost_per_1k_tokens == 0 else f"${model.cost_per_1k_tokens}/1K"
            cloud_table.add_row(
                model_id,
                model.name,
                f"{model.max_context:,}",
                cost,
                ", ".join(model.strengths[:2])
            )
    
    console.print(cloud_table)


@cli.command()
@click.argument('prompt')
@click.option('--language', '-l', default='python', help='Programming language')
@click.option('--tests', is_flag=True, help='Include unit tests')
def code(prompt, language, tests):
    """Generate code from description"""
    
    async def run_code_gen():
        agent = EdgeLLMAgent()
        
        with console.status("[bold yellow]Generating code..."):
            result = await agent.generate_code(
                description=prompt,
                language=language,
                include_tests=tests
            )
        
        # Display with syntax highlighting
        console.print(Panel(
            Markdown(f"```{language}\n{result}\n```"),
            title=f"Generated {language.capitalize()} Code",
            style="green"
        ))
    
    asyncio.run(run_code_gen())


@cli.command()
@click.argument('file', type=click.Path(exists=True))
@click.option('--language', '-l', help='Programming language (auto-detect if not specified)')
def analyze(file, language):
    """Analyze code file for issues"""
    
    file_path = Path(file)
    
    # Auto-detect language
    if not language:
        language = file_path.suffix[1:]  # Remove leading dot
    
    # Read code
    with open(file_path, 'r') as f:
        code = f.read()
    
    async def run_analysis():
        agent = EdgeLLMAgent()
        
        with console.status("[bold yellow]Analyzing code..."):
            result = await agent.analyze_code(code, language=language)
        
        console.print(Panel(result, title="Code Analysis", style="cyan"))
    
    asyncio.run(run_analysis())


@cli.command()
@click.argument('problem')
def solve(problem):
    """Solve a problem with step-by-step reasoning"""
    
    async def run_solve():
        agent = EdgeLLMAgent()
        
        with console.status("[bold yellow]Solving problem..."):
            result = await agent.solve_problem(problem)
        
        console.print(Panel(Markdown(result), title="Solution", style="green"))
    
    asyncio.run(run_solve())


@cli.command()
@click.option('--platform', '-p', type=click.Choice(['ios', 'android', 'web', 'desktop']))
@click.option('--size-limit', '-s', type=int, help='Size limit in MB')
def setup(platform, size_limit):
    """Setup models for deployment"""
    
    import download_models
    
    downloader = download_models.ModelDownloader()
    
    if platform:
        console.print(f"[bold blue]Setting up models for {platform}...[/]")
        downloader.setup_for_platform(platform)
    
    elif size_limit:
        console.print(f"[bold blue]Finding models under {size_limit}MB...[/]")
        models = downloader.optimize_for_size(size_limit)
        
        if models:
            download = click.confirm("Download these models?")
            if download:
                downloader.download_multiple(models)
    
    else:
        console.print("[yellow]Please specify --platform or --size-limit[/]")


@cli.command()
def status():
    """Show system status and configuration"""

    from dotenv import load_dotenv
    
    load_dotenv()
    
    console.print(Panel.fit("📊 System Status", style="bold blue"))
    
    # Models
    router = LLMEdgeRouter()
    console.print(f"\n[bold]Models:[/] {len(router.models)} available")
    console.print(f"  Local: {sum(1 for m in router.models.values() if m.tier.value == 'local')}")
    console.print(f"  Cloud: {sum(1 for m in router.models.values() if m.tier.value != 'local')}")
    
    # Configuration
    console.print(f"\n[bold]Configuration:[/]")
    console.print(f"  Offline Mode: {router.offline_mode}")
    console.print(f"  Battery Saver: {router.battery_saver}")

    # OpenRouter runtime behavior
    raw_fallback_mode = os.getenv("OPENROUTER_FALLBACK_MODE", "local").strip().lower()
    fallback_mode = raw_fallback_mode if raw_fallback_mode in {"local", "error"} else "local"
    fallback_note = "" if raw_fallback_mode in {"local", "error"} else f" (invalid '{raw_fallback_mode}', using local)"
    openrouter_model = os.getenv("OPENROUTER_MODEL", "inclusionai/ring-2.6-1t:free")
    free_only_raw = os.getenv("FREE_LLM_ONLY", "true").strip().lower()
    free_only_enabled = free_only_raw in {"1", "true", "yes", "on"}
    openrouter_fallback_models = os.getenv("OPENROUTER_FREE_FALLBACK_MODELS", "").strip()
    openrouter_max_retries = os.getenv("OPENROUTER_MAX_RETRIES", "2").strip()
    openrouter_retry_base = os.getenv("OPENROUTER_RETRY_BASE_SECONDS", "0.75").strip()
    console.print(f"  OpenRouter Fallback Mode: {fallback_mode}{fallback_note}")
    console.print(f"  OpenRouter Model: {openrouter_model}")
    console.print(f"  Free LLM Only: {free_only_enabled}")
    console.print(f"  OpenRouter Fallback Models: {openrouter_fallback_models or '(none)'}")
    console.print(f"  OpenRouter Max Retries: {openrouter_max_retries}")
    console.print(f"  OpenRouter Retry Base Seconds: {openrouter_retry_base}")
    
    # API Keys
    console.print(f"\n[bold]API Keys:[/]")
    for key, name in ROUTING_API_KEYS:
        configured = is_key_configured(get_effective_key(key))
        status = "✓ Configured" if configured else "✗ Not set"
        style = "green" if configured else "red"
        console.print(f"  {name}: [{style}]{status}[/]")

    # Optional keys (do not affect cloud routing availability)
    console.print(f"\n[bold]Optional Keys:[/]")
    for key, name in OPTIONAL_API_KEYS:
        configured = is_key_configured(get_effective_key(key))
        status = "✓ Configured" if configured else "○ Skipped (optional)"
        style = "green" if configured else "dim"
        console.print(f"  {name}: [{style}]{status}[/]")
    
    # Downloaded models
    models_dir = Path("./models")
    if models_dir.exists():
        model_files = list(models_dir.glob("*.gguf")) + list(models_dir.glob("*.bin"))
        console.print(f"\n[bold]Downloaded Models:[/] {len(model_files)}")
        for model_file in model_files:
            size_mb = model_file.stat().st_size / 1024 / 1024
            console.print(f"  {model_file.name} ({size_mb:.1f}MB)")


@cli.command()
def config():
    """Interactive configuration wizard"""
    
    console.print(Panel.fit("⚙️  Configuration Wizard", style="bold blue"))
    
    # API Keys
    console.print("\n[bold]Cloud API Configuration (optional)[/]")
    console.print("Press Enter to skip any key\n")
    
    env_file = Path(".env")
    env_lines = []
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            env_lines = f.readlines()
    
    api_keys = {
        "GEMINI_API_KEY": ("Google Gemini", "https://ai.google.dev/"),
        "GROQ_API_KEY": ("Groq", "https://console.groq.com/"),
        "OPENROUTER_API_KEY": ("OpenRouter", "https://openrouter.ai/keys"),
        "TOGETHER_API_KEY": ("Together.ai", "https://api.together.xyz/"),
        "HF_API_TOKEN": ("Hugging Face", "https://huggingface.co/settings/tokens"),
    }
    
    for key, (name, url) in api_keys.items():
        console.print(f"[cyan]{name}[/]")
        console.print(f"  Get key: {url}")
        
        current = os.getenv(key)
        if key == "HF_API_TOKEN" and not current:
            current = os.getenv("HF_API_KEY")
        if current:
            console.print(f"  Current: {current[:10]}...")
        
        new_key = console.input("  Enter key (or press Enter to skip): ").strip()
        
        if new_key:
            # Update env lines
            found = False
            for i, line in enumerate(env_lines):
                if line.startswith(f"{key}="):
                    env_lines[i] = f"{key}={new_key}\n"
                    found = True
                    break
            
            if not found:
                env_lines.append(f"{key}={new_key}\n")
            
            console.print("[green]  ✓ Updated[/]\n")
        else:
            console.print("[dim]  Skipped[/]\n")
    
    # Save
    if env_lines:
        with open(env_file, 'w') as f:
            f.writelines(env_lines)
        
        console.print(f"[green]✓ Configuration saved to {env_file}[/]")


if __name__ == '__main__':
    cli()
