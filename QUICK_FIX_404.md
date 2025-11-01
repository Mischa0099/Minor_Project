# 🔴 QUICK FIX: 404 Not Found Error

## The Problem
You're seeing: `<title>404 Not Found</title>`

This means **the backend API routes aren't being found**.

---

## Immediate Fix (3 Steps)

### Step 1: Check Backend is Running

**Open PowerShell/Terminal:**
```powershell
cd backend
python app.py
```

**You MUST see:**
```
Running on http://0.0.0.0:5000
 * Debug mode: on
```

**If you see errors**, fix them first!

---

### Step 2: Test Backend Directly

**Open browser and visit:**
```
http://localhost:5000/ping
```

**Expected:** Should show `pong` (not 404)

**If you see 404:**
- Backend isn't actually running
- Port 5000 is blocked
- Check for Python errors in terminal

---

### Step 3: Check Routes are Registered

**Visit:**
```
http://localhost:5000/api/routes
```

**Expected:** JSON showing all routes like:
```json
{
  "routes": [
    {"path": "/api/auth/register", "methods": ["POST"]},
    {"path": "/api/auth/login", "methods": ["POST"]},
    ...
  ]
}
```

**If you see 404 on this:**
- Routes aren't being registered
- Check backend console for: `Warning: could not register some blueprints`

---

## Common Causes

### ❌ Cause 1: Backend Not Started
**Fix:** Run `python app.py` in backend folder

### ❌ Cause 2: Backend Crashed on Startup
**Fix:** Check terminal for error messages, fix them

### ❌ Cause 3: Wrong Port
**Fix:** Backend must run on port 5000 (check console output)

### ❌ Cause 4: Route Import Errors
**Fix:** Check backend console for import errors

---

## Quick Diagnostic Test

**Run this test script:**
```powershell
cd backend
python test_backend_quick.py
```

**This will test:**
- ✅ Backend connection
- ✅ Route registration
- ✅ API endpoints

---

## Still 404?

**Share:**
1. **Backend console output** (when you run `python app.py`)
2. **What happens** when you visit `http://localhost:5000/ping`
3. **What happens** when you visit `http://localhost:5000/api/routes`

---

## Expected Backend Console

✅ **Good:**
```
Running on http://0.0.0.0:5000
* Debug mode: on
```

❌ **Bad:**
```
Error: ...
Traceback: ...
ModuleNotFoundError: ...
```

**Fix any errors before proceeding!**

