# 🚀 Deploy to Cloudflare Pages - Now!

## Current Status
- ✅ Wrangler installed (v4.51.0)
- ✅ Site built in `/docs` directory
- ✅ Deploy script ready
- ⏳ Needs: Cloudflare authentication

---

## Step 1: Authenticate with Cloudflare

### Option A: API Token (Recommended - More Reliable)

1. **Create API Token:**
   - Go to: https://dash.cloudflare.com/profile/api-tokens
   - Click **"Create Token"**
   - Use template: **"Edit Cloudflare Workers"**
   - Click **"Continue to summary"**
   - Click **"Create Token"**
   - **Copy the token** (you won't see it again!)

2. **Set the token:**
   ```bash
   export CLOUDFLARE_API_TOKEN='your-token-here'
   ```

3. **Verify:**
   ```bash
   wrangler whoami
   ```

### Option B: OAuth Login (If you prefer)

```bash
wrangler login
```

Then authorize in the browser that opens.

---

## Step 2: Deploy!

### Quick Deploy (Automatic)

```bash
./deploy-cloudflare.sh
```

### Manual Deploy

```bash
wrangler pages deploy docs \
    --project-name=squishmallowdex \
    --branch=main
```

---

## What Happens

```
1. Wrangler uploads /docs directory to Cloudflare
2. Cloudflare creates Pages project "squishmallowdex"
3. Files deployed to global CDN (300+ locations)
4. Site live instantly!
```

**No build needed** - we're deploying pre-built files from `/docs`

---

## After Deploy

### Your site will be live at:
```
https://squishmallowdex.pages.dev
```

### Add custom domain (optional):
```bash
wrangler pages deployment tail squishmallowdex
```

Then in Cloudflare dashboard:
- Pages → squishmallowdex → Custom domains → Add domain

---

## Troubleshooting

### "Not logged in" error

**Solution:**
```bash
# Try OAuth again
wrangler login

# Or use API token
export CLOUDFLARE_API_TOKEN='your-token'
wrangler whoami  # Should show your account
```

### "Project already exists" error

**Solution:**
```bash
# Deploy to existing project
wrangler pages deploy docs --project-name=squishmallowdex

# Or create with different name
wrangler pages deploy docs --project-name=squishmallowdex-v2
```

### Files not uploading

**Solution:**
```bash
# Check docs directory exists
ls -la docs/

# Should show:
# - index.html
# - squishmallowdex.html
# - squish_images/ (with 3000+ images)
```

---

## Alternative: Dashboard Upload

If CLI doesn't work, use the dashboard:

1. Go to: https://dash.cloudflare.com/
2. Navigate to: **Pages**
3. Click: **Upload assets**
4. Drag the `/docs` folder
5. Project name: `squishmallowdex`
6. Click: **Deploy**

---

## Expected Output

When deployment succeeds, you'll see:

```
✨ Success! Uploaded 3041 files (5.2 MiB total)

✨ Deployment complete! Take a peek over at
   https://squishmallowdex.pages.dev
```

---

## Next Steps After Deployment

1. ✅ **Test the site** - Visit the URL
2. 🌐 **Add custom domain** (optional)
3. 📊 **Check analytics** in dashboard
4. 🔄 **Set up auto-deploy** (already configured - pushes to main trigger rebuild)

---

## Git Integration (Auto-Deploy)

Once deployed via CLI once, connect GitHub:

1. **Cloudflare Dashboard** → Pages → squishmallowdex
2. Click **Settings** → **Builds & deployments**
3. Click **Connect to Git**
4. Select your GitHub repo
5. Configure:
   - **Production branch:** main
   - **Build command:** `bash cloudflare-build.sh`
   - **Build output directory:** `/docs`

Now every push to main auto-deploys! 🎉

---

## Quick Command Reference

```bash
# Login
wrangler login

# Deploy
wrangler pages deploy docs --project-name=squishmallowdex

# Check status
wrangler pages deployment list --project-name=squishmallowdex

# View logs
wrangler pages deployment tail

# Check who you're logged in as
wrangler whoami
```

---

## 🆘 Still Having Issues?

**Try this sequence:**

```bash
# 1. Logout (clear auth)
wrangler logout

# 2. Login fresh
wrangler login
# Complete OAuth in browser

# 3. Verify
wrangler whoami
# Should show your email

# 4. Deploy
wrangler pages deploy docs --project-name=squishmallowdex
```

---

**Ready? Run `./deploy-cloudflare.sh` now!** 🚀
