# ✅ Ollama Setup - Quick Guide

## Good News! 🎉

**Ollama is already running and accessible!** The API is working on `http://localhost:11434`

**Your model:** `llama2:latest` is already downloaded and ready to use!

---

## Model Names in Code

The backend code uses model names. Here's what to use:

### For Ollama, use one of these formats:
- `llama2` - Short name (usually works)
- `llama2:latest` - Full name with tag
- `mistral` - If you have mistral installed
- `codellama` - If you have codellama installed

**Your current model:** `llama2:latest`

---

## Configuration Options

### Option 1: Use Default (Recommended)
The code defaults to `llama2` which should work with `llama2:latest`.

**No configuration needed!** Just start backend:
```powershell
python app.py
```

### Option 2: Explicitly Set Model Name
Create `backend/.env` file:
```
OLLAMA_MODEL=llama2:latest
```

Or set environment variable:
```powershell
$env:OLLAMA_MODEL="llama2:latest"
```

---

## About "ollama not recognized"

**This is normal!** The `ollama` CLI command might not be in your PATH, but that's OK because:

✅ **We use Ollama via API, not CLI**
- Backend connects to: `http://localhost:11434/api/generate`
- No need for `ollama` command in terminal
- Ollama server is running (we verified it)

---

## If You Need to Download More Models

Since `ollama` command isn't in PATH, you have options:

### Option A: Use Ollama Desktop App
1. Open Ollama desktop application
2. Use the UI to pull/download models
3. Models will be available via API automatically

### Option B: Add Ollama to PATH
1. Find Ollama installation folder (usually `C:\Users\<user>\AppData\Local\Programs\Ollama`)
2. Add to PATH or use full path:
   ```powershell
   C:\Users\<your-user>\AppData\Local\Programs\Ollama\ollama.exe pull llama2
   ```

### Option C: Use API Directly (Advanced)
```powershell
# Pull model via API
curl -X POST http://localhost:11434/api/pull -d '{"name":"mistral"}'
```

---

## Test Ollama Connection

**Test if backend can connect:**

1. **Start backend:**
   ```powershell
   cd backend
   python app.py
   ```

2. **Look for in console:**
   ```
   ✅ Ollama configured (lazy) - Base URL: http://localhost:11434, Model: llama2
   ```

3. **If you see this, Ollama is working!** ✅

---

## Model Names Reference

| Model Name | Code Config | Description |
|------------|-------------|-------------|
| `llama2:latest` | `OLLAMA_MODEL=llama2` or `llama2:latest` | Your current model |
| `mistral` | `OLLAMA_MODEL=mistral` | Smaller, faster alternative |
| `codellama` | `OLLAMA_MODEL=codellama` | For code generation |
| `llama2:7b` | `OLLAMA_MODEL=llama2:7b` | Specific size variant |

---

## Quick Start

**Just start the backend - Ollama should auto-detect:**

```powershell
cd backend
python app.py
```

**Expected output:**
```
✅ Ollama configured (lazy) - Base URL: http://localhost:11434, Model: llama2
```

**That's it!** No CLI commands needed. The backend will use Ollama automatically for personalized responses.

---

## Troubleshooting

### Backend doesn't detect Ollama?
1. **Verify Ollama is running:**
   ```
   http://localhost:11434/api/tags
   ```
   Should return JSON with models

2. **Check backend console** for Ollama connection errors

3. **Verify model exists:**
   - Model should show in API response
   - Name should match `OLLAMA_MODEL` setting

---

**You're all set!** Start the backend and Ollama will be used automatically for personalized AI responses. 🚀

