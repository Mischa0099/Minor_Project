# Backend README

This backend supports an optional ML stack for chat and sentiment analysis.

Quick start (CPU-only, local development):

1. Create and activate a virtual environment (PowerShell):

```powershell
cd backend
python -m venv .venv
& '.\.venv\Scripts\Activate.ps1'
```

2. Install requirements (includes base packages). For full ML behavior, install the ML stack:

```powershell
& '.\.venv\Scripts\pip.exe' install -r requirements.txt
# For CPU-only PyTorch (recommended for local dev):
& '.\.venv\Scripts\pip.exe' install torch --extra-index-url https://download.pytorch.org/whl/cpu
```

3. Environment variables (optional):
- `GOOGLE_API_KEY` - set this if you want to use Google Generative AI (Gemini).
- `USE_LOCAL_MODEL` - set to `1` or `true` to enable a local text-generation model (`distilgpt2`) for replies.
- `USE_GENAI` - default true; set to `0` if you do not want to attempt Gemini even if `GOOGLE_API_KEY` is set.

4. Run the server:

```powershell
& '.\.venv\Scripts\python.exe' app.py
```

5. Test the API:

```powershell
& '.\.venv\Scripts\python.exe' test_api.py
```

Quick test (pytest):

```powershell
# from backend folder
& '.\.venv\Scripts\pip.exe' install pytest
& '.\.venv\Scripts\python.exe' -m pytest -q
```

CI:
- A GitHub Actions workflow is included at `.github/workflows/ci.yml` that runs the unit tests on push/PR to `master`.

Notes:
- The sentiment model used by default is `cardiffnlp/twitter-roberta-base-sentiment-latest` and may download ~500MB of weights on first use.
- The code uses lazy loading for heavy models; the first chat request may be slow while models download.
- If you have GPU and want to use it, ensure you install a CUDA-enabled `torch` wheel compatible with your CUDA version.

If you'd like, I can:
- Configure the app to download models to a specific cache directory.
- Add a small progress indicator for model downloads.
- Wire deployment-friendly configuration (prefetch models on startup in a separate background thread).
