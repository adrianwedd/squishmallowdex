# Cloudflare Pages - Quick Start

## 🚀 5-Minute Setup

### 1. Connect Repository (2 min)
1. Go to https://dash.cloudflare.com/ → **Pages**
2. Click **Create a project** → **Connect to Git**
3. Select **GitHub** → Authorize → Choose **squishmallowdex**

### 2. Configure Build (1 min)
```
Framework preset: None
Build command: bash cloudflare-build.sh
Build output: /docs
Root directory: (leave empty)
```

Add environment variable:
- `PYTHON_VERSION` = `3.11`

### 3. Deploy (2 min)
Click **Save and Deploy** → Wait for build (5-10 min)

---

## 📝 Build Command Options

### Option 1: Use Build Script (Recommended)
```bash
bash cloudflare-build.sh
```

### Option 2: Direct Commands
```bash
python3 squishmallowdex.py && python3 deploy.py
```

### Option 3: Minimal (if collection already generated)
```bash
python3 deploy.py
```

---

## 🔧 Post-Deployment

### Add Custom Domain
1. **Custom domains** → **Set up a custom domain**
2. Add CNAME record in Cloudflare DNS:
   ```
   Type: CNAME
   Name: @ or www
   Target: squishmallowdex.pages.dev
   ```

### Enable HTTPS
- Automatic with Cloudflare
- Force HTTPS: **SSL/TLS** → **Always Use HTTPS** → ON

### Configure Caching
Already configured in `docs/_headers`! ✅

---

## 📊 After First Deploy

Your site will be live at:
- **Pages URL:** `https://squishmallowdex.pages.dev`
- **Custom domain:** `https://yourdomain.com` (after DNS setup)

Test:
- [ ] Landing page loads
- [ ] Collection browser works
- [ ] Search/filter functional
- [ ] Images load from CDN
- [ ] Offline mode works

---

## 🔄 Automatic Updates

Every push to `main` triggers rebuild:
```bash
git add .
git commit -m "Update collection"
git push
```

Cloudflare automatically:
1. Detects push
2. Builds collection
3. Deploys to CDN
4. Updates live site

---

## 💡 Pro Tips

**Speed up builds:**
- Cloudflare caches dependencies
- Incremental builds coming soon

**Monitor deployments:**
- Watch build logs in Pages dashboard
- Enable deployment notifications

**Optimize performance:**
- Images cached for 1 year
- HTML cached for 1 hour
- Brotli compression enabled

---

## 🆘 Need Help?

See full guide: [CLOUDFLARE_SETUP.md](CLOUDFLARE_SETUP.md)

Common issues:
- **Build fails:** Check Python version (3.11)
- **Images missing:** Verify `squish_images/` exists
- **Domain not working:** Wait for DNS propagation (24-48h)

---

**That's it! Your Squishmallowdex is now on Cloudflare! 🎉**
