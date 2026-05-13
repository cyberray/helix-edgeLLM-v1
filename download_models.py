#!/usr/bin/env python3
"""
Model Download and Setup Script
Automatically downloads, verifies, and configures LLM models for edge deployment
"""

import os
import sys
import hashlib
import requests
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass
from tqdm import tqdm
import json
import argparse


@dataclass
class ModelInfo:
    """Model metadata and download information"""
    id: str
    name: str
    provider: str
    file_name: str
    size_mb: int
    url: str
    sha256: str
    quantization: str
    recommended_use: str


# Model registry with verified download links
MODEL_REGISTRY = {
    "phi-3.5-mini-q4": ModelInfo(
        id="phi-3.5-mini-q4",
        name="Phi-3.5-mini Q4_K_M",
        provider="Microsoft",
        file_name="Phi-3.5-mini-instruct-Q4_K_M.gguf",
        size_mb=2048,
        url="https://huggingface.co/microsoft/Phi-3.5-mini-instruct-gguf/resolve/main/Phi-3.5-mini-instruct-Q4_K_M.gguf",
        sha256="",  # Add actual hash
        quantization="Q4_K_M",
        recommended_use="General purpose, best balance"
    ),
    "phi-3.5-mini-q5": ModelInfo(
        id="phi-3.5-mini-q5",
        name="Phi-3.5-mini Q5_K_M",
        provider="Microsoft",
        file_name="Phi-3.5-mini-instruct-Q5_K_M.gguf",
        size_mb=2500,
        url="https://huggingface.co/microsoft/Phi-3.5-mini-instruct-gguf/resolve/main/Phi-3.5-mini-instruct-Q5_K_M.gguf",
        sha256="",
        quantization="Q5_K_M",
        recommended_use="Higher quality, more storage"
    ),
    "qwen2.5-3b-q4": ModelInfo(
        id="qwen2.5-3b-q4",
        name="Qwen2.5 3B Q4_K_M",
        provider="Alibaba",
        file_name="qwen2.5-3b-instruct-q4_k_m.gguf",
        size_mb=1900,
        url="https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf",
        sha256="",
        quantization="Q4_K_M",
        recommended_use="Coding tasks, multilingual"
    ),
    "llama-3.2-3b-q4": ModelInfo(
        id="llama-3.2-3b-q4",
        name="Llama 3.2 3B Q4_0",
        provider="Meta",
        file_name="Llama-3.2-3B-Instruct-Q4_0.gguf",
        size_mb=1700,
        url="https://huggingface.co/lmstudio-community/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_0.gguf",
        sha256="",
        quantization="Q4_0",
        recommended_use="Fast inference, general tasks"
    ),
    "gemma-2-2b-q4": ModelInfo(
        id="gemma-2-2b-q4",
        name="Gemma 2 2B Q4_K_M",
        provider="Google",
        file_name="gemma-2-2b-it-Q4_K_M.gguf",
        size_mb=1400,
        url="https://huggingface.co/lmstudio-community/gemma-2-2b-it-GGUF/resolve/main/gemma-2-2b-it-Q4_K_M.gguf",
        sha256="",
        quantization="Q4_K_M",
        recommended_use="Smallest model, resource-constrained devices"
    ),
}


class ModelDownloader:
    """Handles model downloading, verification, and setup"""
    
    def __init__(self, models_dir: str = "./models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.models_dir / "models.json"
        
    def download_model(self, model_id: str, force: bool = False) -> Path:
        """Download a model by ID"""
        
        if model_id not in MODEL_REGISTRY:
            available = ", ".join(MODEL_REGISTRY.keys())
            raise ValueError(f"Unknown model: {model_id}. Available: {available}")
        
        model = MODEL_REGISTRY[model_id]
        destination = self.models_dir / model.file_name
        
        # Check if already exists
        if destination.exists() and not force:
            print(f"✓ Model already exists: {destination}")
            self._save_model_config(model, destination)
            return destination
        
        print(f"\n📥 Downloading {model.name}")
        print(f"   Provider: {model.provider}")
        print(f"   Size: {model.size_mb}MB")
        print(f"   Quantization: {model.quantization}")
        print(f"   Use case: {model.recommended_use}\n")
        
        # Download with progress bar
        response = requests.get(model.url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(destination, 'wb') as f, tqdm(
            desc=model.file_name,
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))
        
        print(f"\n✓ Downloaded to: {destination}")
        
        # Verify if hash provided
        if model.sha256:
            print("Verifying checksum...", end=" ")
            if self._verify_checksum(destination, model.sha256):
                print("✓ Verified")
            else:
                print("✗ Checksum mismatch!")
                destination.unlink()
                raise ValueError("Checksum verification failed")
        
        # Save model config
        self._save_model_config(model, destination)
        
        return destination
    
    def download_multiple(self, model_ids: List[str], force: bool = False):
        """Download multiple models"""
        results = {}
        
        for model_id in model_ids:
            try:
                path = self.download_model(model_id, force)
                results[model_id] = {"status": "success", "path": str(path)}
            except Exception as e:
                results[model_id] = {"status": "failed", "error": str(e)}
                print(f"✗ Failed to download {model_id}: {e}")
        
        return results
    
    def list_available_models(self):
        """List all available models in registry"""
        print("\n📋 Available Models:\n")
        
        for model_id, model in MODEL_REGISTRY.items():
            print(f"  {model_id}")
            print(f"    Name: {model.name}")
            print(f"    Provider: {model.provider}")
            print(f"    Size: {model.size_mb}MB")
            print(f"    Quantization: {model.quantization}")
            print(f"    Use: {model.recommended_use}")
            print()
    
    def list_downloaded_models(self):
        """List models that have been downloaded"""
        if not self.config_file.exists():
            print("No models downloaded yet")
            return
        
        with open(self.config_file, 'r') as f:
            config = json.load(f)
        
        print("\n📦 Downloaded Models:\n")
        for model_id, info in config.items():
            path = Path(info['path'])
            exists = path.exists()
            status = "✓" if exists else "✗ Missing"
            
            print(f"  {status} {model_id}")
            print(f"    Path: {info['path']}")
            print(f"    Size: {info.get('size_mb', 'unknown')}MB")
            print()
    
    def _verify_checksum(self, file_path: Path, expected_hash: str) -> bool:
        """Verify SHA256 checksum"""
        sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        
        return sha256.hexdigest() == expected_hash
    
    def _save_model_config(self, model: ModelInfo, path: Path):
        """Save model configuration"""
        config = {}
        
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config = json.load(f)
        
        config[model.id] = {
            "name": model.name,
            "provider": model.provider,
            "path": str(path),
            "size_mb": model.size_mb,
            "quantization": model.quantization,
            "recommended_use": model.recommended_use,
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def setup_for_platform(self, platform: str, model_ids: Optional[List[str]] = None):
        """Setup models for specific platform"""
        
        platform_recommendations = {
            "ios": ["phi-3.5-mini-q4", "qwen2.5-3b-q4"],
            "android": ["phi-3.5-mini-q4", "llama-3.2-3b-q4"],
            "web": ["gemma-2-2b-q4", "phi-3.5-mini-q4"],
            "desktop": ["phi-3.5-mini-q5", "qwen2.5-3b-q4"],
        }
        
        if platform not in platform_recommendations:
            print(f"Unknown platform: {platform}")
            print(f"Available: {', '.join(platform_recommendations.keys())}")
            return
        
        models_to_download = model_ids or platform_recommendations[platform]
        
        print(f"\n🚀 Setting up models for {platform.upper()}")
        print(f"   Recommended models: {', '.join(models_to_download)}\n")
        
        results = self.download_multiple(models_to_download)
        
        # Print summary
        success_count = sum(1 for r in results.values() if r['status'] == 'success')
        print(f"\n✓ Setup complete: {success_count}/{len(results)} models ready")
        
        return results
    
    def optimize_for_size(self, target_size_mb: int):
        """Recommend models that fit within size budget"""
        print(f"\n🎯 Finding models under {target_size_mb}MB:\n")
        
        fitting_models = []
        for model_id, model in MODEL_REGISTRY.items():
            if model.size_mb <= target_size_mb:
                fitting_models.append((model_id, model))
        
        if not fitting_models:
            print("No models fit within budget")
            return []
        
        # Sort by size (largest first for best quality)
        fitting_models.sort(key=lambda x: x[1].size_mb, reverse=True)
        
        for model_id, model in fitting_models:
            print(f"  ✓ {model_id}")
            print(f"    Size: {model.size_mb}MB")
            print(f"    Use: {model.recommended_use}")
            print()
        
        return [m[0] for m in fitting_models]


def setup_cloud_apis():
    """Interactive setup for cloud API keys"""
    print("\n☁️  Cloud API Setup\n")
    print("Configure free cloud APIs for fallback (optional):\n")
    
    apis = {
        "GEMINI_API_KEY": {
            "name": "Google Gemini",
            "url": "https://ai.google.dev/",
            "free_tier": "15 RPM, 1M tokens/day"
        },
        "GROQ_API_KEY": {
            "name": "Groq",
            "url": "https://console.groq.com/",
            "free_tier": "30 RPM, 14,400 tokens/day"
        },
        "OPENROUTER_API_KEY": {
            "name": "OpenRouter",
            "url": "https://openrouter.ai/keys",
            "free_tier": "Depends on selected model and account credits"
        },
        "TOGETHER_API_KEY": {
            "name": "Together.ai",
            "url": "https://api.together.xyz/",
            "free_tier": "$1/month credits"
        },
        "HF_API_TOKEN": {
            "name": "Hugging Face",
            "url": "https://huggingface.co/settings/tokens",
            "free_tier": "Rate limited"
        }
    }
    
    env_file = Path(".env")
    env_lines = []
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            env_lines = f.readlines()
    
    for key, info in apis.items():
        print(f"{info['name']} ({key})")
        print(f"  Get key: {info['url']}")
        print(f"  Free tier: {info['free_tier']}")
        
        current_value = os.getenv(key)
        if current_value:
            print(f"  Current: {current_value[:10]}...")
            response = input("  Update? (y/N): ").strip().lower()
            if response != 'y':
                print()
                continue
        
        api_key = input("  Enter API key (or press Enter to skip): ").strip()
        
        if api_key:
            # Update or add to env file
            found = False
            for i, line in enumerate(env_lines):
                if line.startswith(f"{key}="):
                    env_lines[i] = f"{key}={api_key}\n"
                    found = True
                    break
            
            if not found:
                env_lines.append(f"{key}={api_key}\n")
            
            print("  ✓ Saved")
        
        print()
    
    # Write updated .env file
    if env_lines:
        with open(env_file, 'w') as f:
            f.writelines(env_lines)
        
        print(f"✓ API keys saved to {env_file}")
        print("  Load with: python-dotenv")


def main():
    parser = argparse.ArgumentParser(
        description="Download and setup LLM models for edge deployment"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available models"
    )
    
    parser.add_argument(
        "--downloaded",
        action="store_true",
        help="List downloaded models"
    )
    
    parser.add_argument(
        "--download",
        nargs='+',
        metavar="MODEL_ID",
        help="Download specific model(s)"
    )
    
    parser.add_argument(
        "--platform",
        choices=["ios", "android", "web", "desktop"],
        help="Setup recommended models for platform"
    )
    
    parser.add_argument(
        "--size-limit",
        type=int,
        metavar="MB",
        help="Find models under size limit"
    )
    
    parser.add_argument(
        "--setup-apis",
        action="store_true",
        help="Interactive cloud API setup"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-download even if exists"
    )
    
    parser.add_argument(
        "--models-dir",
        default="./models",
        help="Directory for models (default: ./models)"
    )
    
    args = parser.parse_args()
    
    downloader = ModelDownloader(args.models_dir)
    
    # Handle commands
    if args.list:
        downloader.list_available_models()
    
    elif args.downloaded:
        downloader.list_downloaded_models()
    
    elif args.download:
        downloader.download_multiple(args.download, args.force)
    
    elif args.platform:
        downloader.setup_for_platform(args.platform)
    
    elif args.size_limit:
        fitting = downloader.optimize_for_size(args.size_limit)
        response = input("\nDownload all fitting models? (y/N): ").strip().lower()
        if response == 'y':
            downloader.download_multiple(fitting)
    
    elif args.setup_apis:
        setup_cloud_apis()
    
    else:
        # Interactive mode
        print("🤖 LLM Edge Setup Wizard\n")
        print("1. List available models")
        print("2. Setup for platform")
        print("3. Download specific model")
        print("4. Setup cloud APIs")
        print("5. Find models by size limit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == "1":
            downloader.list_available_models()
        
        elif choice == "2":
            print("\nPlatforms: ios, android, web, desktop")
            platform = input("Select platform: ").strip().lower()
            downloader.setup_for_platform(platform)
        
        elif choice == "3":
            downloader.list_available_models()
            model_ids = input("\nEnter model ID(s) (space-separated): ").strip().split()
            downloader.download_multiple(model_ids)
        
        elif choice == "4":
            setup_cloud_apis()
        
        elif choice == "5":
            size = int(input("Size limit (MB): ").strip())
            fitting = downloader.optimize_for_size(size)
            if fitting:
                response = input("\nDownload all? (y/N): ").strip().lower()
                if response == 'y':
                    downloader.download_multiple(fitting)


if __name__ == "__main__":
    main()
