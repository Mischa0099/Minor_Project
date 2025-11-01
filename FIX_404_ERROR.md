# 🔴 Fix 404 Not Found Error

## Quick Diagnosis

The 404 error means the backend is **not responding** or routes aren't found. Let's fix this:

---

## Step 1: Check Backend is Running

**In Terminal 1 (Backend):**
```powershell
cd backend
python app.py
```

**You should see:**
```
Running on http://0.0.0.0:5000
* Debug mode: on
```

**If you see errors**, fix them first.

---

## Step 2: Test Backend Directly

**Open browser and go to:**
```
http://localhost:5000/ping
```

**Should return:** `pong`

**If this fails:**
- Backend is not running
- Port 5000 is blocked
- Python error on startup

---

## Step 3: Check Routes

**Test route listing:**
```
http://localhost:5000/api/routes
```

**Should show:** JSON with all available routes

**Expected routes:**
- `/api/auth/register`
- `/api/auth/login`
- `/api/user/profile`
- `/api/chat/`
- `/ping`

---

## Step 4: Check Frontend Proxy

**Frontend should proxy to backend automatically**

**In Terminal 2 (Frontend):**
```powershell
cd frontend
npm start
```

**Check that:**
1. Frontend runs on `http://localhost:3000`
2. Backend runs on `http://localhost:5000`
3. No port conflicts

---

## Step 5: Test API Connection

**Open browser console (F12) when on frontend**

**Check Network tab:**
1. Try to login/register
2. Look for requests to `/api/auth/login` or `/api/auth/register`
3. Check if requests show:
   - ✅ Status 200/201 = Working
   - ❌ Status 404 = Route not found
   - ❌ Status 0/Network Error = Backend not running

---

## Common Issues & Fixes

### Issue 1: Backend Not Running
**Symptoms:** 404 on all API calls

**Fix:**
```powershell
cd backend
python app.py
# Should see: Running on http://0.0.0.0:5000
```

### Issue 2: Wrong Port
**Symptoms:** Frontend can't connect

**Fix:**
- Backend should be on port 5000
- Frontend should be on port 3000
- Check `package.json` has: `"proxy": "http://127.0.0.1:5000"`

### Issue 3: CORS Error
**Symptoms:** Network error in console

**Fix:**
- Already enabled in `app.py` with `CORS(app)`
- If still issues, check backend console for CORS errors

### Issue 4: Route Registration Failed
**Symptoms:** Backend runs but routes return 404

**Check backend console for:**
```
Warning: could not register some blueprints at import time: ...
```

**Fix:**
- Check if route files exist
- Check for syntax errors in route files
- Check imports in `app.py`

### Issue 5: Proxy Not Working
**Symptoms:** Frontend makes requests but gets 404

**Fix:**
1. Restart frontend: `npm start`
2. Clear browser cache
3. Try accessing backend directly: `http://localhost:5000/api/auth/register` (POST)

---

## Quick Test Script

**Create test file:** `test_backend.py`
```python
import requests

# Test ping
r = requests.get('http://localhost:5000/ping')
print(f"Ping: {r.status_code} - {r.text}")

# Test routes
r = requests.get('http://localhost:5000/api/routes')
print(f"Routes: {r.status_code}")
if r.status_code == 200:
    print(r.json())
```

**Run:**
```powershell
pip install requests
python test_backend.py
```

---

## Still Getting 404?

1. **Share backend console output** when starting
2. **Share the exact URL** that's returning 404
3. **Share browser Network tab** showing the failed request
4. **Verify both servers are running** (backend + frontend)

---

## Expected Behavior

✅ **Working:**
- Backend console shows: `Running on http://0.0.0.0:5000`
- `http://localhost:5000/ping` returns `pong`
- Frontend can login/register/chat

❌ **Not Working:**
- 404 errors on API calls
- Network errors in browser console
- Backend not running

