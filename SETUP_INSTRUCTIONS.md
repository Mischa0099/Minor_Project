# Setup Instructions - Stable AI Providers

## Quick Start Guide

### Step 1: Install OpenAI Package

Open PowerShell in your backend folder and run:

```powershell
cd backend
pip install openai==1.3.0
```

Or if using virtual environment:
```powershell
cd backend
.venv\Scripts\activate
pip install openai==1.3.0
```

---

## Step 2: Choose Your AI Provider

You have **2 main options** - choose ONE:

### **Option A: OpenAI (RECOMMENDED - Most Stable)** ⭐

**Best for:** Production, reliability, fast responses

1. **Get API Key:**
   - Go to: https://platform.openai.com/api-keys
   - Sign up/Login
   - Create a new API key
   - Copy the key (starts with `sk-...`)

2. **Set Environment Variable:**
   
   **Method 1: Create/Edit `.env` file in `backend/` folder:**
   ```
   OPENAI_API_KEY=sk-your-actual-key-here
   OPENAI_MODEL=gpt-3.5-turbo
   ```
   
   **Method 2: Set in PowerShell (temporary):**
   ```powershell
   $env:OPENAI_API_KEY="sk-your-actual-key-here"
   $env:OPENAI_MODEL="gpt-3.5-turbo"
   ```

3. **Done!** The system will automatically use OpenAI.

**Cost:** ~$0.002 per request (very cheap for GPT-3.5-turbo)

---

### **Option B: Ollama (FREE - No API Key)** 🆓

**Best for:** Development, privacy, offline use, no costs

1. **Install Ollama:**
   - Download from: https://ollama.ai
   - Install the Windows version
   - Ollama will start automatically

2. **Download a Model:**
   Open a new terminal/PowerShell and run:
   ```powershell
   ollama pull llama2
   ```
   (This downloads ~4GB, takes a few minutes)
   
   Or try a smaller model:
   ```powershell
   ollama pull mistral
   ```

3. **Verify Ollama is Running:**
   ```powershell
   ollama list
   ```
   Should show the model you downloaded.

4. **Set Environment Variable (Optional):**
   
   Only if you want to customize (defaults work fine):
   ```powershell
   # In .env file or PowerShell
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama2
   ```
   
   If using default settings, **you don't need to set anything!**

5. **Done!** The system will automatically detect Ollama.

**Cost:** FREE (runs on your computer)

---

## Step 3: Test Your Setup

1. **Start your backend:**
   ```powershell
   cd backend
   python app.py
   ```

2. **Check Console Output:**
   
   You should see ONE of these:
   - `✅ OpenAI configured - Model: gpt-3.5-turbo` (if using OpenAI)
   - `✅ Ollama configured - Base URL: http://localhost:11434, Model: llama2` (if using Ollama)
   
   If you see errors, see Troubleshooting below.

3. **Test in Frontend:**
   - Login to your app
   - Go to Chat page
   - Send a message
   - You should get a **personalized AI response** (not hardcoded!)

---

## Step 4: Verify Personalization Works

1. **Fill out User Profile:**
   - Go to Profile page
   - Enter: Name, Age, Weight, Health Conditions, Medication History
   - Save profile

2. **Test Chat:**
   - Ask: "I have a headache, what should I do?"
   - The response should reference YOUR specific profile (age, conditions, etc.)
   - Example: "Given your age of 30 and your diabetes condition..."

---

## Troubleshooting

### OpenAI Issues:

**"OpenAI package not installed"**
```powershell
pip install openai==1.3.0
```

**"OPENAI_API_KEY not set"**
- Check your `.env` file has the key
- Or set in PowerShell: `$env:OPENAI_API_KEY="sk-..."`

**"Invalid API key"**
- Get a new key from https://platform.openai.com/api-keys
- Make sure you copied the full key (starts with `sk-`)

### Ollama Issues:

**"Ollama not available"**
1. Check Ollama is running:
   ```powershell
   ollama list
   ```
   
2. If not installed, download from https://ollama.ai

3. If installed but not running:
   ```powershell
   ollama serve
   ```

**"Model not found"**
- Pull the model: `ollama pull llama2`
- Or change model: `OLLAMA_MODEL=mistral`

---

## Comparison

| Feature | OpenAI | Ollama |
|---------|--------|--------|
| **Stability** | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐ Very Good |
| **Speed** | ⭐⭐⭐⭐⭐ Very Fast | ⭐⭐⭐ Moderate |
| **Cost** | ~$0.002/request | FREE |
| **Setup** | Easy (API key) | Easy (install app) |
| **Privacy** | Cloud-based | Local (private) |
| **Internet** | Required | Not required |
| **Recommended** | ✅ Production | ✅ Development |

---

## What Changed?

✅ **Added OpenAI support** - Most stable option  
✅ **Added Ollama support** - Free, local alternative  
✅ **Automatic priority** - Uses best available provider  
✅ **Still personalized** - All responses use user profile  
✅ **Still real-time** - No hardcoded responses  

**You don't need Gemini anymore** unless you want it as a fallback!

---

## Quick Reference

### Environment Variables (.env file):

**For OpenAI:**
```
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-3.5-turbo
```

**For Ollama (optional, defaults work):**
```
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

**Disable Gemini (if you want):**
```
USE_GENAI=0
```

---

## Need Help?

1. Check console output when starting backend
2. Make sure you installed: `pip install openai==1.3.0`
3. For OpenAI: Verify API key is correct
4. For Ollama: Verify `ollama list` shows your model
5. Test with a simple chat message to see if responses are personalized

