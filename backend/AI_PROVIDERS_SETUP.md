# AI Provider Setup Guide

The application now supports multiple AI providers with automatic priority-based selection. All providers deliver **personalized, non-hardcoded responses** based on user profiles.

## Priority Order (Automatic Selection)

1. **OpenAI** (Recommended - Most Stable) ⭐
2. **Ollama** (Free, Local, No API Key)
3. **Gemini** (Less Stable)
4. **Local Transformers** (Basic Fallback)

The system automatically uses the first available provider in this order.

---

## Option 1: OpenAI (RECOMMENDED - Most Stable) ⭐

### Setup
1. Get API key from: https://platform.openai.com/api-keys
2. Set environment variable:
   ```bash
   # Windows PowerShell
   $env:OPENAI_API_KEY="sk-your-key-here"
   
   # Linux/Mac
   export OPENAI_API_KEY="sk-your-key-here"
   
   # Or in .env file
   OPENAI_API_KEY=sk-your-key-here
   ```

3. (Optional) Choose model:
   ```bash
   OPENAI_MODEL=gpt-4          # Better quality, more expensive
   OPENAI_MODEL=gpt-3.5-turbo  # Default, good balance
   ```

### Pros
- ✅ Most stable and reliable
- ✅ Excellent personalization
- ✅ Fast responses
- ✅ Industry standard

### Cons
- ⚠️ Requires paid API key (pay-per-use)
- ⚠️ Costs ~$0.002 per request (GPT-3.5-turbo)

---

## Option 2: Ollama (FREE, Local, No API Key) 🆓

### Setup
1. Install Ollama: https://ollama.ai
2. Pull a model:
   ```bash
   ollama pull llama2        # or
   ollama pull mistral       # or
   ollama pull codellama
   ```
3. Start Ollama (runs automatically on install):
   ```bash
   ollama serve  # Usually runs automatically
   ```
4. (Optional) Configure if not using defaults:
   ```bash
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama2  # or mistral, codellama, etc.
   ```

### Pros
- ✅ **100% FREE** - No API key needed
- ✅ Runs locally (privacy-friendly)
- ✅ Works offline
- ✅ Good personalization quality

### Cons
- ⚠️ Requires local installation (~4GB+ disk space)
- ⚠️ Slower than cloud APIs (runs on your machine)
- ⚠️ Needs good RAM (8GB+ recommended)

---

## Option 3: Gemini (Less Stable)

### Setup
```bash
GOOGLE_API_KEY=your-key-here
USE_GENAI=1
```

### Pros
- ✅ Free tier available
- ✅ Good quality

### Cons
- ⚠️ Less stable (as you mentioned)
- ⚠️ Rate limits

---

## Option 4: Local Transformers (Basic Fallback)

### Setup
```bash
USE_LOCAL_MODEL=1
```

### Pros
- ✅ Completely offline
- ✅ No API costs

### Cons
- ⚠️ Lower quality personalization
- ⚠️ Requires significant RAM
- ⚠️ Slower than other options

---

## Recommended Setup

**For Production (Stable):**
```bash
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-3.5-turbo
```

**For Development (Free):**
```bash
# Install Ollama first, then:
OLLAMA_MODEL=llama2
# No API key needed!
```

**For Maximum Reliability:**
Set up both OpenAI (primary) and Ollama (fallback):
```bash
OPENAI_API_KEY=sk-your-key-here
OLLAMA_MODEL=llama2
# System will use OpenAI, fallback to Ollama if OpenAI fails
```

---

## Testing

After setup, start the backend and check console output:
- ✅ OpenAI configured - Model: gpt-3.5-turbo
- ✅ Ollama configured - Base URL: http://localhost:11434, Model: llama2
- ✅ Google Generative AI (Gemini) configured
- ✅ Local text-generation model loaded

The first available provider will be used automatically.

---

## Personalization

**All providers** will generate personalized responses based on:
- User's age, weight, gender
- Health conditions
- Medication history (patient + family)
- Conversation history
- Sentiment analysis

Responses are **NOT hardcoded** - they're generated in real-time using the user's specific profile data.

