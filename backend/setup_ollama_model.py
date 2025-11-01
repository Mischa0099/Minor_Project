#!/usr/bin/env python
"""Helper script to pull a smaller Ollama model"""
import requests
import json

OLLAMA_BASE_URL = "http://localhost:11434"

# Smaller models that use less memory
SMALLER_MODELS = [
    "llama2:7b",      # Smaller version of llama2
    "mistral",        # Very efficient, smaller
    "phi",            # Very small, fast
    "tinyllama",      # Smallest option
]

print("=" * 60)
print("OLLAMA MODEL SETUP")
print("=" * 60)
print("\n⚠️  Your current model (llama2:latest) needs more memory.")
print("\n💡 Recommended: Pull a smaller model")
print("\nAvailable smaller models:")

for i, model in enumerate(SMALLER_MODELS, 1):
    print(f"  {i}. {model}")

print("\n" + "=" * 60)
print("TO PULL A MODEL:")
print("=" * 60)
print("\nOption 1: Use Ollama Desktop App")
print("  - Open Ollama app")
print("  - Click 'Pull a model'")
print("  - Type: mistral (recommended)")
print("  - Click Download")

print("\nOption 2: Use API (PowerShell):")
print('  curl -X POST http://localhost:11434/api/pull -d \'{\"name\":\"mistral\"}\'')
print("\n  Or use Invoke-WebRequest:")
print('  Invoke-WebRequest -Uri http://localhost:11434/api/pull -Method POST -Body \'{\"name\":\"mistral\"}\' -ContentType \"application/json\"')

print("\n" + "=" * 60)
print("RECOMMENDED: mistral")
print("=" * 60)
print("- Smaller and faster than llama2")
print("- Uses less memory")
print("- Good quality for chat")
print("- Perfect for healthcare assistant")

print("\nAfter pulling mistral, update backend/.env:")
print("  OLLAMA_MODEL=mistral")

print("\n" + "=" * 60)

