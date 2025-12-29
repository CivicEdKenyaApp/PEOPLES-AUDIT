# API Server Fixes - 503/405/404 Errors Resolution

## Issues Fixed

### 1. ✅ HEAD Method Not Allowed (405 Errors)
**Problem**: Browser/iframe was sending HEAD requests, but endpoints only supported GET.

**Fix**: Added `@app.head()` decorators to all endpoints:
- `/sankey` - Now supports both GET and HEAD
- `/dashboard` - Now supports both GET and HEAD
- `/html/{filename}` - Now supports both GET and HEAD
- `/data/{filetype}/{filename}` - Now supports both GET and HEAD
- All other endpoints - Now support HEAD

**Also Updated CORS**:
```python
allow_methods=["GET", "HEAD", "OPTIONS"]  # Added HEAD and OPTIONS
```

### 2. ✅ 503 Service Unavailable for `/sankey`
**Problem**: 
- The endpoint wasn't finding `sankey.html` correctly
- Theme parameter wasn't being handled
- No error handling for missing files

**Fix**:
- Added explicit path checking: `ROOT_DIR / "stage_4_visuals" / "sankey.html"`
- Added fallback to search in multiple locations
- Added theme parameter support (even if not used, it won't cause errors)
- Added comprehensive error handling and logging

### 3. ✅ 404 Not Found for Chart HTML Files
**Problem**: Browser was trying to access `/opt/render/project/src/stage_4_visuals/charts/html/debt_timeline.html` which is a local file path, not a URL.

**Fix**: 
- Added static file mounting for charts directory:
```python
app.mount("/charts", StaticFiles(directory=str(CHARTS_STATIC_DIR)), name="charts")
```
- Now charts are accessible at: `/charts/html/debt_timeline.html`
- Added `/charts/html/{filename}` route for direct access

### 4. ✅ CORS for Iframe Embedding
**Problem**: Iframe embedding might have CORS issues.

**Fix**:
- Added `"*"` to allowed origins (can be restricted if needed)
- Ensured `allow_credentials=True` for proper iframe support
- Added OPTIONS method support for preflight requests

## New Features

### Static File Serving
Charts are now accessible via:
- `/charts/html/debt_timeline.html`
- `/charts/html/corruption_by_sector.html`
- `/charts/html/budget_allocation.html`
- etc.

### Enhanced Logging
- Better startup logging showing all paths and file availability
- More detailed error messages
- Path checking on startup

### Better Error Handling
- Try multiple file locations before failing
- Clear error messages indicating where files were checked
- Graceful degradation

## Updated Endpoints

### `/sankey?theme=light`
- ✅ Supports GET and HEAD
- ✅ Handles theme parameter (light/dark)
- ✅ Searches multiple locations for sankey.html
- ✅ Better error messages

### `/dashboard?theme=light`
- ✅ Supports GET and HEAD
- ✅ Handles theme parameter
- ✅ Checks multiple locations

### `/charts/html/{filename}`
- ✅ New: Direct access to chart HTML files
- ✅ Also available via static mount at `/charts/html/{filename}`

### `/list`
- ✅ Now includes chart files listing
- ✅ Shows path information for debugging
- ✅ Indicates file availability

## Testing Checklist

After deploying, test these:

1. **HEAD Requests** (should return 200, not 405):
   ```bash
   curl -I https://peoples-audit.onrender.com/sankey?theme=light
   curl -I https://peoples-audit.onrender.com/dashboard?theme=light
   ```

2. **GET Requests** (should return 200, not 503):
   ```bash
   curl https://peoples-audit.onrender.com/sankey?theme=light
   curl https://peoples-audit.onrender.com/dashboard?theme=light
   ```

3. **Chart Files** (should return 200, not 404):
   ```bash
   curl https://peoples-audit.onrender.com/charts/html/debt_timeline.html
   curl https://peoples-audit.onrender.com/charts/html/corruption_by_sector.html
   ```

4. **File Listing**:
   ```bash
   curl https://peoples-audit.onrender.com/list
   ```

5. **Iframe Embedding**:
   ```html
   <iframe src="https://peoples-audit.onrender.com/sankey?theme=light" 
           width="100%" 
           height="600px"
           frameborder="0">
   </iframe>
   ```

## What to Watch For

### 1. File Paths on Render
The server uses `/opt/render/project/src` as the default root. If your files are in a different location:
- Set environment variable: `PEOPLES_AUDIT_ROOT=/path/to/your/files`
- Or update the `ROOT_DIR` in `api_server.py`

### 2. Missing Files
If you see 404 errors:
- Check that the pipeline has run and generated files
- Verify file locations match what the server expects
- Check server logs for path information
- Use `/list` endpoint to see what files are available

### 3. Static File Mounting
If charts still return 404:
- Verify `CHARTS_STATIC_DIR` exists and contains `html/` subdirectory
- Check that files have `.html` extension
- Ensure directory permissions allow reading

### 4. CORS Issues
If iframe embedding still fails:
- Check browser console for CORS errors
- Verify your domain is in `ALLOWED_ORIGINS` (or `"*"` is present)
- Ensure `allow_credentials=True` is set

### 5. Server Resources
If you see 503 errors:
- Check Render dashboard for resource usage
- Verify server is running (check `/healthz`)
- Check server logs for errors
- Consider upgrading Render plan if consistently overloaded

## Deployment Steps

1. **Commit Changes**:
   ```bash
   git add api_server.py
   git commit -m "Fix 503/405/404 errors: Add HEAD support, static file serving, better error handling"
   git push
   ```

2. **Render Auto-Deploy**:
   - Render should automatically deploy on push
   - Monitor deployment logs

3. **Verify Deployment**:
   - Check `/healthz` endpoint
   - Test `/list` to see available files
   - Test `/sankey?theme=light` in browser
   - Test iframe embedding on your site

4. **Monitor Logs**:
   - Watch Render logs for any errors
   - Check for file path issues
   - Verify all endpoints are accessible

## Expected Behavior After Fix

✅ **HEAD requests** → 200 OK (not 405)  
✅ **GET /sankey** → 200 OK with HTML (not 503)  
✅ **GET /dashboard** → 200 OK with HTML (not 503)  
✅ **GET /charts/html/*.html** → 200 OK (not 404)  
✅ **Iframe embedding** → Works without CORS errors  
✅ **Theme parameter** → Accepted (even if not used)  

## Troubleshooting

### Still Getting 503?
1. Check server logs for actual errors
2. Verify files exist at expected paths
3. Check Render resource limits
4. Restart the service on Render

### Still Getting 405?
1. Verify you deployed the updated `api_server.py`
2. Clear browser cache
3. Check that HEAD method is in CORS allow_methods

### Still Getting 404?
1. Use `/list` endpoint to see available files
2. Check file paths in server logs
3. Verify pipeline generated the files
4. Check file permissions

### Iframe Still Not Working?
1. Check browser console for errors
2. Verify CORS headers in Network tab
3. Test direct URL access first
4. Check iframe sandbox attributes if used

## Additional Notes

- The server now logs more information on startup
- All endpoints support both GET and HEAD
- Static files are served efficiently via FastAPI's StaticFiles
- Error messages are more descriptive
- Multiple file location fallbacks prevent unnecessary 404s

