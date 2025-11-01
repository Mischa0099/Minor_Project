# 🚀 Quick Setup (Choose ONE Option)

## Option 1: OpenAI (5 minutes) - RECOMMENDED ⭐

```powershell
# 1. Install package
cd backend
pip install openai==1.3.0

# 2. Get API key from: https://platform.openai.com/api-keys

# 3. Create .env file in backend/ folder with:
OPENAI_API_KEY=sk-your-key-here

# 4. Done! Start backend
python app.py
```

---

## Option 2: Ollama (10 minutes) - FREE 🆓

```powershell
# 1. Download & Install from: https://ollama.ai

# 2. Open new terminal, pull model:
ollama pull llama2

# 3. Done! Start backend (no API key needed)
cd backend
python app.py
```

---

**That's it!** The system will automatically use whichever is available.

No other code changes needed - everything is already updated! ✅

