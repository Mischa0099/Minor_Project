#!/usr/bin/env python
"""Test Ollama connection"""
import requests

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama2"  # or "llama2:latest"

print("=" * 60)
print("OLLAMA CONNECTION TEST")
print("=" * 60)

# Test 1: Check if Ollama is running
print("\n1. Testing Ollama API connection...")
try:
    response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
    if response.status_code == 200:
        print("   ✅ Ollama API is accessible!")
        models = response.json().get('models', [])
        if models:
            print(f"   ✅ Found {len(models)} model(s):")
            for model in models:
                print(f"      - {model.get('name', 'Unknown')}")
        else:
            print("   ⚠️  No models found. Pull a model first.")
    else:
        print(f"   ❌ Ollama returned status {response.status_code}")
except requests.exceptions.ConnectionError:
    print("   ❌ Cannot connect to Ollama. Make sure Ollama is running.")
    print("      Start Ollama desktop app or service.")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Try to generate a response
print(f"\n2. Testing model '{OLLAMA_MODEL}'...")
try:
    test_prompt = "Say hello in one sentence."
    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json={
            "model": OLLAMA_MODEL,
            "prompt": test_prompt,
            "stream": False
        },
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        generated_text = result.get('response', '').strip()
        if generated_text:
            print(f"   ✅ Model is working!")
            print(f"   Response: {generated_text[:100]}...")
        else:
            print("   ⚠️  Model responded but no text generated")
    elif response.status_code == 404:
        print(f"   ❌ Model '{OLLAMA_MODEL}' not found")
        print(f"   💡 Try: OLLAMA_MODEL=llama2:latest")
    else:
        print(f"   ❌ Error: Status {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("RECOMMENDATIONS")
print("=" * 60)

# Check available models and recommend
try:
    response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
    if response.status_code == 200:
        models = response.json().get('models', [])
        if models:
            first_model = models[0].get('name', '')
            # Recommend short name (without :latest)
            recommended = first_model.split(':')[0]
            print(f"\n✅ Recommended model name: {recommended}")
            print(f"   (Your model: {first_model})")
            print(f"\n💡 Set in backend/.env:")
            print(f"   OLLAMA_MODEL={recommended}")
            print(f"\n   Or use default 'llama2' - it should work!")
except:
    pass

print("\n💡 Backend will auto-detect Ollama when you start it.")
print("💡 Look for: '✅ Ollama configured' in backend console.")

