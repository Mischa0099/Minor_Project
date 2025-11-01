# 🔴 URGENT: Fix AI Provider Configuration

## Problem
You're getting generic, non-personalized responses because **no AI provider is configured**.

The system is falling back to basic rule-based responses which are not properly personalized.

## Quick Fix - Choose ONE Option

### ⭐ Option 1: OpenAI (5 minutes - RECOMMENDED)

**Step 1:** Get API Key
- Go to: https://platform.openai.com/api-keys
- Sign up/login
- Create new API key
- Copy it (starts with `sk-...`)

**Step 2:** Install Package
```powershell
cd backend
pip install openai==1.3.0
```

**Step 3:** Set Environment Variable
Create or edit `backend/.env` file:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

**Step 4:** Restart Backend
```powershell
# Stop backend (Ctrl+C)
# Restart:
python app.py
```

**Step 5:** Verify
Look for in console: `✅ OpenAI configured - Model: gpt-3.5-turbo`

---

### 🆓 Option 2: Ollama (FREE, No API Key)

**Step 1:** Install Ollama
- Download: https://ollama.ai
- Install on Windows

**Step 2:** Download Model
Open new terminal:
```powershell
ollama pull llama2
```
(This takes 5-10 minutes, downloads ~4GB)

**Step 3:** Verify Ollama is Running
```powershell
ollama list
```
Should show: `llama2`

**Step 4:** Restart Backend
```powershell
# Stop backend (Ctrl+C)
cd backend
python app.py
```

**Step 5:** Verify
Look for: `✅ Ollama configured - Base URL: http://localhost:11434, Model: llama2`

---

## Test After Configuration

1. **Restart backend** after setting up
2. **Check console** for ✅ success messages
3. **Fill your profile** completely (Name, Age, Weight, Health Conditions, Medication History)
4. **Send chat message**: "Hello" or "I have a headache"
5. **Should see personalized response** referencing your profile

---

## Current Status Check

**Without AI Provider:**
- ❌ Generic responses
- ❌ Not personalized
- ❌ Hardcoded fallback

**With AI Provider:**
- ✅ Personalized responses
- ✅ Uses your profile data
- ✅ Real-time AI generation

---

## Why This Happened

The system checks for AI providers in this order:
1. OpenAI (if `OPENAI_API_KEY` set)
2. Ollama (if installed and running)
3. Gemini (if `GOOGLE_API_KEY` set)
4. Local transformers (if `USE_LOCAL_MODEL=1`)

Since none are configured, it falls back to basic rule-based responses which are NOT personalized properly.

---

## After Setup

Once you configure an AI provider:
1. Responses will be **personalized** using your profile
2. Responses will reference your **age, weight, health conditions, medication history**
3. Responses will be **generated in real-time**, not hardcoded
4. Much better quality and relevance

---

## Still Having Issues?

1. Check backend console for error messages
2. Verify environment variable is set correctly
3. Restart backend after configuration
4. Check if API key is valid (for OpenAI)
5. Check if Ollama is running (for Ollama)

---

**IMPORTANT:** Until you configure an AI provider, responses will remain generic and non-personalized. This is expected behavior - the system needs an AI provider to generate personalized responses.

