# Quick Fix Summary - API Server Issues

## Problems Identified & Fixed

### ❌ Problem 1: 405 Method Not Allowed
**Error**: `HEAD /sankey?theme=light HTTP/1.1" 405 Method Not Allowed`

**Cause**: Browser/iframe sends HEAD requests, but server only had GET endpoints.

**✅ Fixed**: Added `@app.head()` decorators to all endpoints.

---

### ❌ Problem 2: 503 Service Unavailable  
**Error**: `GET /sankey?theme=light 503 (Service Unavailable)`

**Cause**: 
- Endpoint couldn't find `sankey.html` file
- No error handling for missing files
- Theme parameter not handled

**✅ Fixed**: 
- Added explicit file path checking
- Added fallback file location search
- Added theme parameter support
- Better error handling

---

### ❌ Problem 3: 404 Not Found for Charts
**Error**: `GET /opt/render/project/src/stage_4_visuals/charts/html/debt_timeline.html 404`

**Cause**: Browser trying to access local file paths instead of URLs. No static file serving configured.

**✅ Fixed**: 
- Added static file mounting: `app.mount("/charts", ...)`
- Charts now accessible at: `/charts/html/debt_timeline.html`

---

## Files Changed

1. **`api_server.py`** - Complete rewrite with:
   - HEAD method support on all endpoints
   - Static file serving for charts
   - Better error handling
   - Multiple file location fallbacks
   - Enhanced logging

2. **`API_SERVER_FIXES.md`** - Detailed documentation

3. **`QUICK_FIX_SUMMARY.md`** - This file

---

## What You Need to Do

### 1. Deploy the Fix
```bash
git add api_server.py
git commit -m "Fix 503/405/404 errors for iframe embedding"
git push
```

Render will auto-deploy.

### 2. Test After Deployment

**Test HEAD requests** (should work now):
```bash
curl -I https://peoples-audit.onrender.com/sankey?theme=light
```

**Test GET requests** (should work now):
```bash
curl https://peoples-audit.onrender.com/sankey?theme=light
```

**Test chart files** (should work now):
```bash
curl https://peoples-audit.onrender.com/charts/html/debt_timeline.html
```

### 3. Verify on Your Site

Embed in your iframe:
```html
<iframe 
  src="https://peoples-audit.onrender.com/sankey?theme=light" 
  width="100%" 
  height="600px"
  frameborder="0">
</iframe>
```

Should work without console errors!

---

## Expected Results

✅ No more 405 errors  
✅ No more 503 errors  
✅ No more 404 errors for charts  
✅ Iframe embedding works  
✅ All endpoints support HEAD requests  

---

## If Issues Persist

1. **Check Render Logs**: Look for file path errors
2. **Verify Files Exist**: Use `/list` endpoint to see available files
3. **Check File Paths**: Server expects files at:
   - `stage_4_visuals/sankey.html`
   - `stage_4_visuals/dashboard.html`
   - `stage_4_visuals/charts/html/*.html`

4. **Restart Service**: On Render dashboard, restart the service

---

## Quick Test Commands

```bash
# Health check
curl https://peoples-audit.onrender.com/healthz

# List available files
curl https://peoples-audit.onrender.com/list

# Test sankey
curl -I https://peoples-audit.onrender.com/sankey?theme=light  # HEAD
curl https://peoples-audit.onrender.com/sankey?theme=light      # GET

# Test dashboard
curl -I https://peoples-audit.onrender.com/dashboard?theme=light  # HEAD
curl https://peoples-audit.onrender.com/dashboard?theme=light     # GET

# Test charts
curl https://peoples-audit.onrender.com/charts/html/debt_timeline.html
```

All should return 200 OK (not 405, 503, or 404)!

