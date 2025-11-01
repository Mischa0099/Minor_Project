# Troubleshooting Guide - Login/Chat Issues

## Quick Checklist

### 1. **Backend is Running?**
```powershell
# In backend folder, run:
cd backend
python app.py
```
You should see: `Running on http://0.0.0.0:5000`

### 2. **Frontend is Running?**
```powershell
# In frontend folder, run:
cd frontend
npm start
```
You should see: `Compiled successfully` and browser opens to `http://localhost:3000`

### 3. **Database Created?**
- Backend automatically creates `instance/database.db` on first run
- If you see database errors, delete `instance/database.db` and restart backend

### 4. **Check Console for Errors**

**Browser Console (F12):**
- Look for red error messages
- Check Network tab to see if API calls are failing

**Backend Console:**
- Look for error messages
- Check if routes are registered correctly

---

## Common Issues & Fixes

### ❌ "Cannot POST /api/auth/login"
**Problem:** Backend not running or wrong URL

**Fix:**
1. Make sure backend is running on port 5000
2. Check `package.json` has: `"proxy": "http://127.0.0.1:5000"`
3. Restart both frontend and backend

---

### ❌ "Network Error" or "Failed to fetch"
**Problem:** Backend not accessible

**Fix:**
1. Check backend is running: `python app.py`
2. Verify backend shows: `Running on http://0.0.0.0:5000`
3. Check CORS is enabled in backend (should be automatic)
4. Try accessing backend directly: `http://localhost:5000/ping` (should return "pong")

---

### ❌ "Registration failed" or "Login failed"
**Problem:** Backend API error

**Fix:**
1. Check backend console for error messages
2. Verify database file exists: `backend/instance/database.db`
3. If database errors, delete database and restart:
   ```powershell
   # Delete database
   Remove-Item backend\instance\database.db
   # Restart backend
   python backend\app.py
   ```

---

### ❌ "Unauthorized" when accessing Chat/Profile
**Problem:** Not logged in or token expired

**Fix:**
1. Make sure you registered and logged in successfully
2. Check browser localStorage has "token" key (F12 > Application > Local Storage)
3. Try logging out and logging in again
4. Check backend JWT_SECRET_KEY is set (optional, has default)

---

### ❌ Can't send chat messages
**Problem:** Backend not receiving requests or AI not configured

**Fix:**
1. Check backend console when sending message - should see logs
2. Verify you have AI provider configured (OpenAI or Ollama)
3. Check error message in browser alert - it will tell you what's wrong
4. Make sure you're logged in (token in localStorage)

---

### ❌ Chat messages show but no AI response
**Problem:** AI provider not configured

**Fix:**
1. Check backend console for warnings about missing AI providers
2. Configure OpenAI or Ollama (see SETUP_INSTRUCTIONS.md)
3. Restart backend after configuring

---

## Step-by-Step Debugging

### 1. Test Backend API Directly
```powershell
# Test ping endpoint
curl http://localhost:5000/ping
# Should return: pong

# Test register (replace email/password)
curl -X POST http://localhost:5000/api/auth/register -H "Content-Type: application/json" -d "{\"email\":\"test@test.com\",\"password\":\"test123\"}"
# Should return: {"message":"User registered successfully"}
```

### 2. Test Frontend Connection
1. Open browser console (F12)
2. Go to Network tab
3. Try to register/login
4. Check if requests go to `http://localhost:5000/api/...`
5. Check response status (should be 200 or 201)

### 3. Check Authentication
1. Open browser console (F12)
2. Go to Application > Local Storage
3. Check if "token" exists after login
4. Value should start with "eyJ..." (JWT token)

### 4. Test Protected Routes
1. Try accessing `/chat` or `/profile` without login
2. Should redirect to `/login`
3. After login, should be able to access

---

## Security Checks ✅

### Data Security
- ✅ Passwords are hashed (not stored plain text)
- ✅ JWT tokens for authentication
- ✅ Protected routes require login
- ✅ User data isolated by user_id
- ✅ Personal info stored securely in database

### Authentication Flow
1. User registers → password hashed → stored in database
2. User logs in → password verified → JWT token issued
3. Token stored in localStorage (browser)
4. Token sent with every API request
5. Backend verifies token before allowing access

---

## Still Having Issues?

1. **Check all console logs** (frontend and backend)
2. **Verify both servers are running**
3. **Clear browser cache and localStorage**
4. **Restart both servers**
5. **Check for typos in email/password**
6. **Try registering a new account**

If still not working, share:
- Backend console error messages
- Browser console error messages
- Network tab showing failed requests

