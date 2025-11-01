# 🔧 Ollama Model Setup - Fix Memory Issue

## Current Situation

✅ **Ollama is running** - API accessible at `http://localhost:11434`  
✅ **Model downloaded** - `llama2:latest` is available  
❌ **Memory error** - Model too large for your system  

---

## Solution: Use Smaller Model

### Recommended: **mistral** (Best Option)

**Why mistral?**
- ✅ Smaller (~4GB vs ~7GB for llama2)
- ✅ Faster responses
- ✅ Uses less RAM
- ✅ Good quality for healthcare chat
- ✅ Already configured as default in code now

---

## Step 1: Pull mistral Model

### Option A: Ollama Desktop App (Easiest)
1. **Open Ollama desktop application**
2. **Click "Pull a model"** button
3. **Type:** `mistral`
4. **Click Download/Enter**
5. Wait for download (~4GB, 5-10 minutes)

### Option B: PowerShell (If CLI works)
```powershell
# Find Ollama installation and use full path
& "C:\Users\<your-user>\AppData\Local\Programs\Ollama\ollama.exe" pull mistral
```

### Option C: API Call (PowerShell)
```powershell
Invoke-WebRequest -Uri http://localhost:11434/api/pull -Method POST -Body '{"name":"mistral"}' -ContentType "application/json"
```

---

## Step 2: Update Configuration

**Already done!** ✅ The code now defaults to `mistral`.

**OR** create `backend/.env` file:
```
OLLAMA_MODEL=mistral
```

---

## Step 3: Test

1. **Start backend:**
   ```powershell
   cd backend
   python app.py
   ```

2. **Look for:**
   ```
   ✅ Ollama configured (lazy) - Base URL: http://localhost:11434, Model: mistral
   ```

3. **Test chat** - Should work now!

---

## Alternative Smaller Models

If `mistral` still has issues, try even smaller:

### Option 1: phi (Very Small)
```powershell
# Pull via Ollama app or API
Invoke-WebRequest -Uri http://localhost:11434/api/pull -Method POST -Body '{"name":"phi"}' -ContentType "application/json"
```
Then set: `OLLAMA_MODEL=phi`

### Option 2: tinyllama (Smallest)
```powershell
# Pull via Ollama app or API
Invoke-WebRequest -Uri http://localhost:11434/api/pull -Method POST -Body '{"name":"tinyllama"}' -ContentType "application/json"
```
Then set: `OLLAMA_MODEL=tinyllama`

---

## Quick Test After Pulling

**Run test script:**
```powershell
python test_ollama.py
```

**Should show:**
```
✅ Model is working!
Response: Hello...
```

---

## Summary

1. ✅ **Pull mistral** (via Ollama app or API)
2. ✅ **Code already configured** to use mistral
3. ✅ **Start backend** - Should work!

**You don't need the `ollama` CLI command** - use the Ollama desktop app to pull models, or use the API. Both work fine! 🚀

