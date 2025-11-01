# 🔍 Debug AI Provider Issues

## Check Backend Console Output

When you start the backend or send a chat message, look for these messages:

### ✅ Success Messages (You'll see ONE of these):
- `✅ OpenAI configured (lazy) - Model: gpt-3.5-turbo`
- `✅ Ollama configured (lazy) - Base URL: http://localhost:11434, Model: llama2`
- `✅ Google Generative AI (Gemini) configured (lazy)`
- `✅ Local text-generation model loaded.`

### ⚠️ Warning Messages (If you see these, AI won't work):
- `ℹ️ OPENAI_API_KEY not set or empty. OpenAI will be skipped.`
- `ℹ️ OpenAI package not installed. Install with: pip install openai`
- `ℹ️ Ollama not running at http://localhost:11434`
- `ℹ️ GOOGLE_API_KEY not set. Gemini generation will be skipped.`

### 🔍 Debug Output (When sending chat message):
You should see:
```
🔍 AI Provider Status Check for user X:
   HAS_OPENAI: True, openai_client: True
   HAS_OLLAMA: False, ollama_base_url: None
   HAS_GENAI: False, chat_session: None
   USE_GENAI: False
   text_generator: None
✅ AI provider detected! Attempting to generate personalized response...
```

## Common Issues & Fixes

### Issue 1: "OPENAI_API_KEY not set"
**Fix:**
1. Create `backend/.env` file
2. Add: `OPENAI_API_KEY=sk-your-key-here`
3. Restart backend

### Issue 2: "OpenAI package not installed"
**Fix:**
```powershell
cd backend
pip install openai==1.3.0
```

### Issue 3: "Ollama not running"
**Fix:**
1. Download from https://ollama.ai
2. Install and start Ollama
3. Run: `ollama pull llama2`
4. Restart backend

### Issue 4: All providers show False/None
**Problem:** No AI provider configured at all

**Fix:**
1. Choose ONE provider (OpenAI or Ollama)
2. Follow setup instructions
3. Restart backend
4. Check console for ✅ success message

## Quick Test

1. **Start backend** and check console for initialization messages
2. **Send a chat message** and check console for debug output
3. **Look for** "✅ AI provider detected!" message
4. **If you see** "⚠️ WARNING: No AI model available" → follow setup guide

## Environment Variables Check

Run this in backend folder to check environment:
```powershell
# Check if .env file exists
Test-Path .env

# Check OpenAI key (won't show value, just if it's set)
echo $env:OPENAI_API_KEY

# For Python, check:
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('OPENAI_API_KEY:', 'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET')"
```

## Still Not Working?

1. **Check backend console** for error messages
2. **Share the debug output** from console
3. **Verify** you restarted backend after configuration
4. **Check** `.env` file is in `backend/` folder (not root)
5. **Verify** API key doesn't have extra spaces or quotes

