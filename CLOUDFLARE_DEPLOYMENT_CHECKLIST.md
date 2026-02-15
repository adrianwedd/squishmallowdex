# ✅ Cloudflare Pages Deployment Checklist

## What We Just Set Up

All configuration files are ready and pushed to GitHub! Here's what's included:

### Configuration Files ✅
- ✅ `wrangler.toml` - Cloudflare project config
- ✅ `.cloudflare/pages.json` - Build settings
- ✅ `cloudflare-build.sh` - Automated build script
- ✅ `docs/_redirects` - URL routing rules
- ✅ `docs/_headers` - Security & caching headers
- ✅ Documentation (setup guides)

### Repository Status
- ✅ Committed: 10 files changed
- ✅ Pushed to GitHub: main branch
- ✅ Ready for Cloudflare connection

---

## 🎯 Your Next Steps (15 minutes)

### Step 1: Connect to Cloudflare Pages (5 min)

1. **Open Cloudflare Dashboard**
   - URL: https://dash.cloudflare.com/
   - Login with your Cloudflare account

2. **Navigate to Pages**
   - Click **Pages** in left sidebar
   - Click **Create a project**

3. **Connect to GitHub**
   - Click **Connect to Git**
   - Select **GitHub**
   - Authorize Cloudflare (if first time)
   - Choose repository: **squishmallowdex** (or adrianwedd/squishmallowdex)
   - Click **Begin setup**

### Step 2: Configure Build (5 min)

**Project name:** `squishmallowdex` (or your preferred name)

**Production branch:** `main`

**Build settings:**
```
Framework preset: None
Build command: bash cloudflare-build.sh
Build output directory: /docs
Root directory: (leave blank)
```

**Environment variables:**
Click **Add variable**
- Variable name: `PYTHON_VERSION`
- Value: `3.11`

Click **Save and Deploy**

### Step 3: Wait for First Build (5-10 min)

Cloudflare will now:
1. Clone your repository
2. Install Python 3.11
3. Run `cloudflare-build.sh`
4. Generate the collection (3000+ Squishmallows)
5. Deploy to global CDN

**Watch the build logs!** You'll see:
```
🚀 Starting Cloudflare Pages build...
📦 Installing Python dependencies...
🎨 Generating Squishmallowdex collection...
📂 Deploying to /docs...
✅ Build successful!
```

### Step 4: Test Your Site (2 min)

Once deployed, Cloudflare gives you a URL:
- **Pages URL:** `https://squishmallowdex.pages.dev`

Test these pages:
- [ ] `https://squishmallowdex.pages.dev/` - Landing page
- [ ] `https://squishmallowdex.pages.dev/squishmallowdex.html` - Collection
- [ ] `https://squishmallowdex.pages.dev/about.html` - About
- [ ] `https://squishmallowdex.pages.dev/guide.html` - Guide

Check:
- [ ] All pages load
- [ ] Images display
- [ ] Search works
- [ ] Filters work
- [ ] Favorites save

---

## 🌐 Step 5: Add Your Custom Domain (Optional, 10 min)

### In Cloudflare Pages Dashboard:

1. Click your project → **Custom domains**
2. Click **Set up a custom domain**
3. Enter your domain name (e.g., `squishmallows.com`)
4. Click **Continue**

### Configure DNS:

**Option A: Root domain (squishmallows.com)**
```
Type: CNAME
Name: @
Target: squishmallowdex.pages.dev
Proxy: ON (orange cloud)
```

**Option B: Subdomain (www.squishmallows.com)**
```
Type: CNAME
Name: www
Target: squishmallowdex.pages.dev
Proxy: ON (orange cloud)
```

### Enable HTTPS:

1. Go to **SSL/TLS** → **Overview**
2. Set encryption mode: **Full**
3. Go to **SSL/TLS** → **Edge Certificates**
4. Enable **Always Use HTTPS**: ON

**DNS propagation takes 5 minutes - 48 hours**

---

## 🚀 Step 6: Optimize Performance (5 min)

### Auto Minify

1. **Speed** → **Optimization**
2. Enable Auto Minify:
   - ✅ JavaScript
   - ✅ CSS
   - ✅ HTML

### Brotli Compression

1. **Speed** → **Optimization**
2. Enable **Brotli** compression

### HTTP/3 (QUIC)

1. **Network** → **Settings**
2. Enable **HTTP/3 (with QUIC)**

---

## 📊 Step 7: Enable Analytics (3 min)

### Built-in Pages Analytics

Already enabled! View in your Pages project:
- **Deployments** tab → Click any deployment
- See: Page views, visitors, bandwidth

### Cloudflare Web Analytics (Optional)

1. **Analytics & Logs** → **Web Analytics**
2. Click **Add a site**
3. Enter your domain
4. Copy the analytics script
5. Add to `docs/index.html` (optional - we don't track by default)

---

## ✅ Verification Checklist

After setup, verify:

### Deployment ✅
- [ ] Build completed successfully
- [ ] No errors in build logs
- [ ] All files deployed to CDN

### Site Functionality ✅
- [ ] Landing page loads
- [ ] Collection browser works
- [ ] Search functionality works
- [ ] Filtering works
- [ ] Images load from CDN
- [ ] Favorites save (localStorage)
- [ ] Ownership tracking works
- [ ] Offline mode works (after first load)

### Custom Domain ✅
- [ ] Domain DNS configured
- [ ] HTTPS enabled
- [ ] Redirects work (www → non-www or vice versa)
- [ ] All pages accessible

### Performance ✅
- [ ] Images cached properly
- [ ] Page load time < 2 seconds
- [ ] Lighthouse score > 90

### Security ✅
- [ ] HTTPS enforced
- [ ] Security headers set
- [ ] No mixed content warnings

---

## 🔄 Automatic Updates

Your site now auto-deploys! 🎉

**On every push to main:**
1. You commit changes: `git commit -m "Update"`
2. You push: `git push`
3. Cloudflare detects push
4. Cloudflare rebuilds site (5-10 min)
5. New version deployed globally
6. Cache purged automatically

**Weekly auto-updates:**
- GitHub Actions runs every Sunday at 2am UTC
- Regenerates collection with latest data
- Pushes to main → triggers Cloudflare rebuild

---

## 📈 Monitor Your Site

### Deployment Dashboard
Check: https://dash.cloudflare.com/ → **Pages** → **squishmallowdex**

**Deployments tab:**
- See all builds (successful, failed, in progress)
- View build logs
- Rollback to previous version if needed

**Analytics tab:**
- Page views over time
- Unique visitors
- Top pages
- Geographic distribution

**Custom domains tab:**
- Domain status
- SSL certificate status

---

## 🆘 Troubleshooting

### Build Fails

**Check build logs:**
1. Go to **Deployments** tab
2. Click failed deployment
3. View logs for errors

**Common issues:**
- Python version mismatch → Set `PYTHON_VERSION=3.11`
- Missing dependencies → Check `requirements-test.txt`
- Build timeout → Should complete in 5-10 min

### Domain Not Working

**DNS not propagated:**
- Wait 24-48 hours
- Check DNS: `dig yourdomain.com`
- Should point to Cloudflare nameservers

**SSL errors:**
- Ensure SSL/TLS mode is **Full**
- Wait for certificate to provision (up to 24 hours)

### Images Not Loading

**Check network tab:**
- Are images 404?
- Check path in browser: `/squish_images/image.jpg`

**Purge cache:**
1. **Caching** → **Configuration**
2. Click **Purge Everything**

---

## 📚 Documentation Reference

- **Quick Start:** [CLOUDFLARE_QUICK_START.md](CLOUDFLARE_QUICK_START.md)
- **Full Setup:** [CLOUDFLARE_SETUP.md](CLOUDFLARE_SETUP.md)
- **Cloudflare Docs:** https://developers.cloudflare.com/pages/

---

## 🎯 Success Criteria

Your deployment is successful when:

- ✅ Site loads at your Pages URL
- ✅ Custom domain works (if configured)
- ✅ All pages functional
- ✅ Images load from CDN
- ✅ Search and filters work
- ✅ LocalStorage persists (favorites/ownership)
- ✅ Automatic deployments work
- ✅ Build time < 10 minutes
- ✅ Page load time < 2 seconds

---

## 🎉 You're Done!

Once all checks pass:

1. **Update README** with your live URL
2. **Share your site!** Tell collectors about it
3. **Start v1.2.0 work** - Affiliate links and i18n
4. **Monitor analytics** - See who's using it

---

## 💡 Pro Tips

**Fast deploys:**
- Cloudflare caches Python packages
- Subsequent builds faster (2-5 min)

**Preview deployments:**
- Every PR gets a preview URL
- Test before merging to main

**Rollback easily:**
- Keep failed deployments
- Instant rollback from dashboard

**Custom functions:**
- Add serverless functions in `/functions` folder
- API endpoints for future features

---

**Need help?** Create an issue on GitHub or ask in Cloudflare Community!

🚀 **Happy deploying!**
