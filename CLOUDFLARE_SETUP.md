# Cloudflare Pages Setup Guide

This guide walks you through deploying Squishmallowdex to Cloudflare Pages with automatic builds on every push.

---

## Prerequisites

- [x] GitHub repository (already set up)
- [x] Cloudflare account
- [x] Domain registered and DNS pointing to Cloudflare

---

## Step 1: Connect GitHub to Cloudflare Pages

1. **Log in to Cloudflare Dashboard**
   - Go to: https://dash.cloudflare.com/

2. **Navigate to Pages**
   - Click **Pages** in the left sidebar
   - Click **Create a project**

3. **Connect to Git**
   - Click **Connect to Git**
   - Choose **GitHub**
   - Authorize Cloudflare to access your repositories
   - Select **adrianwedd/squishmallowdex** (or your repo name)

---

## Step 2: Configure Build Settings

### Framework Preset
- Select: **None** (we have a custom build)

### Build Configuration

```yaml
Production branch: main
Build command: bash cloudflare-build.sh
Build output directory: /docs
Root directory: (leave blank)
```

### Environment Variables

Add these environment variables:

| Variable Name | Value |
|---------------|-------|
| `PYTHON_VERSION` | `3.11` |

---

## Step 3: Advanced Build Settings (Optional)

### Build Caching
- Enable build caching for faster builds
- Cache Python packages between builds

### Build Watch Paths
Add these paths to trigger rebuilds:
- `squishmallowdex.py`
- `deploy.py`
- `requirements-test.txt`
- `docs/**/*`

---

## Step 4: Custom Domain Setup

### Add Your Custom Domain

1. **In Cloudflare Pages:**
   - Go to your project → **Custom domains**
   - Click **Set up a custom domain**
   - Enter your domain name

2. **Configure DNS:**
   - Cloudflare will show you the required DNS records
   - Add a CNAME record pointing to your Pages project:
     ```
     Type: CNAME
     Name: @ (or www)
     Target: squishmallowdex.pages.dev
     ```

3. **Enable HTTPS:**
   - Cloudflare automatically provisions SSL/TLS
   - Enable **Always Use HTTPS** in SSL/TLS settings
   - Set SSL/TLS encryption mode to **Full**

---

## Step 5: Configure Performance Settings

### Caching Rules

In **Caching** → **Cache Rules**, create these rules:

**Rule 1: Cache Images Forever**
```
Match: /squish_images/*
Cache Level: Standard
Edge Cache TTL: 1 year
Browser Cache TTL: 1 year
```

**Rule 2: Cache Assets**
```
Match: /assets/*
Cache Level: Standard
Edge Cache TTL: 1 year
Browser Cache TTL: 1 year
```

**Rule 3: Cache HTML with Revalidation**
```
Match: /*.html
Cache Level: Standard
Edge Cache TTL: 1 hour
Browser Cache TTL: 1 hour
```

### Speed Settings

1. **Auto Minify:**
   - Enable: HTML, CSS, JavaScript

2. **Brotli Compression:**
   - Enable for better compression

3. **HTTP/3 (with QUIC):**
   - Enable for faster connections

---

## Step 6: Set Up Analytics

### Web Analytics

1. Go to **Analytics & Logs** → **Web Analytics**
2. Enable **Cloudflare Web Analytics**
3. Add the analytics snippet to your pages (optional - privacy-first)

### Pages Analytics

- Cloudflare Pages includes built-in analytics
- View in your project dashboard:
  - Page views
  - Unique visitors
  - Geographic distribution
  - Top pages

---

## Step 7: Configure Redirects (Optional)

Create a `docs/_redirects` file for URL redirects:

```
# Redirect root to index
/  /index.html  200

# 404 handling
/* /404.html 404

# Optional: Redirect www to non-www
https://www.yourdomain.com/* https://yourdomain.com/:splat 301
```

---

## Step 8: Deploy!

### Manual Deployment

1. Push your changes to GitHub:
   ```bash
   git add .
   git commit -m "Configure Cloudflare Pages deployment"
   git push
   ```

2. Cloudflare Pages will automatically:
   - Detect the push
   - Run the build command
   - Deploy to production
   - Update your custom domain

### Monitor Deployment

1. Go to your Cloudflare Pages project
2. Click on the **Deployments** tab
3. Watch the build logs in real-time
4. Build typically takes 5-10 minutes

---

## Step 9: Verify Deployment

### Check Your Site

1. **Visit your Pages URL:**
   - https://squishmallowdex.pages.dev

2. **Visit your custom domain:**
   - https://yourdomain.com

3. **Test all pages:**
   - Landing page (index.html)
   - Collection browser (squishmallowdex.html)
   - About page (about.html)
   - Guide page (guide.html)
   - 404 page (404.html)

4. **Test functionality:**
   - Search works
   - Filters work
   - Images load
   - Favorites save (localStorage)
   - Offline mode (after first load)

---

## Build Process Flow

```
1. Push to GitHub (main branch)
   ↓
2. Cloudflare detects commit
   ↓
3. Clone repository
   ↓
4. Install Python 3.11
   ↓
5. Install dependencies (pip install -r requirements-test.txt)
   ↓
6. Run cloudflare-build.sh
   ├─ Generate collection (squishmallowdex.py)
   ├─ Deploy to /docs (deploy.py)
   └─ Verify files
   ↓
7. Upload /docs directory to CDN
   ↓
8. Deploy to production (instant)
   ↓
9. Purge cache
   ↓
10. Site live! 🎉
```

---

## Troubleshooting

### Build Fails

**Python version mismatch:**
- Check `PYTHON_VERSION` environment variable is set to `3.11`
- Cloudflare supports Python 3.7, 3.8, 3.11

**Missing dependencies:**
- Ensure `requirements-test.txt` includes all required packages
- Check build logs for specific errors

**Build timeout:**
- Cloudflare has a 20-minute build timeout
- If generating all 3000+ Squishmallows, this should be sufficient
- Consider implementing incremental builds if needed

### Images Not Loading

**CORS issues:**
- Images should work fine with same-origin
- If using external images, configure CORS headers

**Cache not working:**
- Check caching rules in Cloudflare dashboard
- Purge cache if needed: **Caching** → **Purge Everything**

### Custom Domain Not Working

**DNS propagation:**
- Can take 24-48 hours for DNS to fully propagate
- Check DNS with: `dig yourdomain.com`

**SSL/TLS issues:**
- Ensure SSL/TLS mode is **Full** or **Full (strict)**
- Check certificate status in SSL/TLS → Edge Certificates

---

## Performance Optimizations

### Image Optimization

Cloudflare can optimize images automatically:

1. Enable **Polish** (requires Pro plan or higher)
2. Or use Cloudflare Images (separate product)

For free tier, images are already optimized in the build.

### Bandwidth Savings

Cloudflare Pages includes:
- **Unlimited bandwidth** (no extra cost)
- **Unlimited requests**
- **Global CDN** with 300+ locations

### Build Optimization

Speed up builds with:
- Build caching (enabled by default)
- Incremental builds (custom implementation)
- Parallel image processing

---

## Monitoring & Maintenance

### Weekly Builds

The existing GitHub Actions workflow can be adapted:

```yaml
# .github/workflows/trigger-cloudflare-build.yml
name: Trigger Weekly Cloudflare Build

on:
  schedule:
    - cron: '0 2 * * 0'  # Sunday 2am UTC
  workflow_dispatch:

jobs:
  trigger:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger empty commit
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git commit --allow-empty -m "🤖 Trigger weekly rebuild"
          git push
```

### Analytics Review

Check weekly:
- Page views and traffic trends
- Top pages (which Squishmallows are popular?)
- Geographic distribution
- Load times and performance

---

## Cost Breakdown

### Cloudflare Pages (Free Tier)
- ✅ Unlimited bandwidth
- ✅ Unlimited requests
- ✅ 500 builds/month
- ✅ 1 build at a time
- ✅ 20 min build time per build

### Custom Domain
- Cost: $8-15/year (domain registration)
- SSL/TLS: Free with Cloudflare

### Total Monthly Cost
- **$0/month** for hosting (Free tier)
- Domain: ~$1/month (annual registration)

---

## Next Steps After Setup

1. ✅ **Test deployment** - Verify everything works
2. 📊 **Set up monitoring** - Configure analytics
3. 🔒 **Security review** - Enable security headers
4. 🚀 **Performance tuning** - Optimize caching rules
5. 📱 **Mobile testing** - Test on various devices
6. 🌍 **Start i18n** - Begin translation work
7. 💰 **Add affiliate links** - Implement monetization

---

## Support Resources

- **Cloudflare Pages Docs:** https://developers.cloudflare.com/pages/
- **Cloudflare Community:** https://community.cloudflare.com/
- **Build Troubleshooting:** https://developers.cloudflare.com/pages/platform/build-configuration/
- **GitHub Issues:** https://github.com/adrianwedd/squishmallowdex/issues

---

## Summary Checklist

Before going live:

- [ ] Repository connected to Cloudflare Pages
- [ ] Build command configured: `bash cloudflare-build.sh`
- [ ] Output directory set to: `/docs`
- [ ] Environment variables added
- [ ] Custom domain configured
- [ ] DNS records updated
- [ ] SSL/TLS enabled (Always Use HTTPS)
- [ ] Caching rules configured
- [ ] Test deployment successful
- [ ] All pages loading correctly
- [ ] Images loading from CDN
- [ ] Offline mode working
- [ ] Analytics tracking enabled
- [ ] Documentation updated

---

**Ready to deploy!** 🚀

After setup, your site will automatically rebuild and deploy every time you push to the `main` branch.
