# 🦙 Ollama Setup Guide

## Problem: "ollama not recognised"

This means Ollama isn't in your system PATH. Here's how to fix it:

---

## Quick Fix Options

### Option 1: Use Full Path (Easiest)

**Instead of:** `ollama pull llama2`

**Use:**
```powershell
& "$env:USERPROFILE\AppData\Local\Programs\Ollama\ollama.exe" pull llama2
```

**Or if installed elsewhere:**
```powershell
& "C:\Users\$env:USERNAME\AppData\Local\Programs\Ollama\ollama.exe" pull llama2
```

---

### Option 2: Add to PATH (Permanent Fix)

1. **Find Ollama installation:**
   - Usually at: `C:\Users\YourName\AppData\Local\Programs\Ollama\`
   - Or: `C:\Program Files\Ollama\`

2. **Add to PATH:**
   - Press `Win + X` → System → Advanced system settings
   - Click "Environment Variables"
   - Under "User variables", find "Path"
   - Click "Edit" → "New"
   - Add: `C:\Users\YourName\AppData\Local\Programs\Ollama`
   - Click OK on all dialogs

3. **Restart PowerShell/Terminal**

4. **Verify:**
   ```powershell
   ollama --version
   ```

---

### Option 3: Restart Terminal After Install

**After installing Ollama:**
1. **Close all PowerShell/CMD windows**
2. **Open new PowerShell**
3. **Try:** `ollama pull llama2`

---

## Pull a Model (Once Ollama Works)

### Available Models (Recommended):

**Small & Fast (Good for testing):**
```powershell
ollama pull llama2          # ~3.8GB - Recommended for start
ollama pull mistral         # ~4.1GB - Good quality
```

**Medium:**
```powershell
ollama pull codellama       # ~3.8GB - Good for code
ollama pull llama2:13b      # ~7.3GB - Better quality
```

**Small (Quick test):**
```powershell
ollama pull phi             # ~1.6GB - Very fast
```

### Recommended First Pull:
```powershell
ollama pull llama2
```

**This will:**
- Download ~3.8GB
- Take 5-15 minutes depending on internet
- Be available at `http://localhost:11434`

---

## Model Names for API

**Once you pull a model, use these names in your backend:**

### Default Models:
- `llama2` - Most common
- `mistral` - Good alternative
- `codellama` - For code
- `phi` - Small & fast
- `llama2:13b` - Larger, better quality

### Set in Backend:

**Option 1: Environment Variable**
```powershell
# In backend/.env file or PowerShell:
$env:OLLAMA_MODEL="llama2"
```

**Option 2: Default (Already Set)**
The backend already defaults to `llama2`:
```python
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama2')
```

**So if you pull `llama2`, no configuration needed!**

---

## Verify Ollama is Working

### Step 1: Check Ollama Service
```powershell
# Try to access Ollama API directly:
curl http://localhost:11434/api/tags
```

**Or in browser:**
```
http://localhost:11434/api/tags
```

**Should return JSON with your models.**

---

### Step 2: List Installed Models
```powershell
# Using full path:
& "$env:USERPROFILE\AppData\Local\Programs\Ollama\ollama.exe" list

# Or if in PATH:
ollama list
```

**Should show:**
```
NAME            ID              SIZE    MODIFIED
llama2          abc123...       3.8GB   2 hours ago
```

---

### Step 3: Test Model
```powershell
& "$env:USERPROFILE\AppData\Local\Programs\Ollama\ollama.exe" run llama2 "Hello, what is 2+2?"
```

**Should return a response from the model.**

---

## Backend Configuration

### Once Model is Pulled:

**The backend will automatically detect Ollama if:**
1. ✅ Ollama is running (usually runs automatically)
2. ✅ Model is downloaded (`ollama pull llama2`)
3. ✅ Ollama is accessible at `http://localhost:11434`

**No configuration needed!** The backend defaults to:
- Base URL: `http://localhost:11434`
- Model: `llama2`

### To Use Different Model:

**In `backend/.env` file:**
```
OLLAMA_MODEL=mistral
# or
OLLAMA_BASE_URL=http://localhost:11434
```

---

## Troubleshooting

### Issue 1: "ollama: command not found"
**Fix:** Use full path (see Option 1 above) or add to PATH

### Issue 2: "Connection refused" in backend
**Fix:** 
- Make sure Ollama is running
- Check: `http://localhost:11434/api/tags` works
- Restart Ollama if needed

### Issue 3: "Model not found"
**Fix:**
- Pull the model first: `ollama pull llama2`
- Check: `ollama list` shows your model
- Verify model name matches in backend config

### Issue 4: Ollama not starting
**Fix:**
- Open Ollama app manually
- Or start service: `ollama serve`
- Check Windows Services if installed as service

---

## Quick Start Checklist

1. ✅ Install Ollama from https://ollama.ai
2. ✅ Pull a model: `ollama pull llama2` (or use full path)
3. ✅ Verify: `ollama list` shows the model
4. ✅ Start backend: `python app.py`
5. ✅ Check console: Should see `✅ Ollama configured`
6. ✅ Test in chat - should get personalized responses!

---

## Model Recommendation

**For Healthcare Chatbot:**
- **Start with:** `llama2` (good balance)
- **Better quality:** `mistral` or `llama2:13b`
- **Faster:** `phi` (but less capable)

**Once you pull any model, restart backend and it should work!** 🚀

