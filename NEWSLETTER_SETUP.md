# Email Newsletter Setup Guide

## 🎯 Goal
Build an email list of Squishmallow collectors and send them updates about:
- New Squishmallow additions to the database
- Rare finds and restocks
- Collecting tips and guides
- Exclusive deals and announcements

---

## Option 1: Formspree (Free & Easy - Recommended for Starting)

**Best for:** Getting started quickly, under 50 emails/month

### Setup Steps:

1. **Create Account**
   - Go to: https://formspree.io
   - Sign up (free plan available)
   - Create a new form

2. **Get Form Endpoint**
   - Copy your form endpoint: `https://formspree.io/f/YOUR_FORM_ID`

3. **Update Blog Page**
   - Replace `YOUR_FORM_ID` in `docs/blog/index.html`
   - Example: `<form action="https://formspree.io/f/xpznabcd">`

4. **Configure Notifications**
   - Set where new signups are sent (your email)
   - Export subscribers as CSV monthly

**Pros:**
- ✅ Free up to 50 submissions/month
- ✅ No coding required
- ✅ Spam protection included
- ✅ GDPR compliant

**Cons:**
- ❌ Manual newsletter sending
- ❌ Limited automation
- ❌ Need to export/import to email service

---

## Option 2: Mailchimp (Free up to 500 subscribers)

**Best for:** Professional email campaigns, automation

### Setup Steps:

1. **Create Account**
   - Go to: https://mailchimp.com
   - Sign up (free up to 500 contacts)

2. **Create Audience**
   - Dashboard → Audience → Create Audience
   - Name: "Squishmallow Collectors"

3. **Get Embed Code**
   - Audience → Signup forms → Embedded forms
   - Copy the generated HTML
   - Style to match your site

4. **Create Welcome Email**
   - Campaigns → Email → Automated → Welcome new subscribers
   - Design your welcome email with free Squish guide

5. **Schedule Campaigns**
   - Weekly/monthly newsletters
   - New release alerts
   - Blog post roundups

**Pros:**
- ✅ Professional email campaigns
- ✅ Automation (welcome emails, drip campaigns)
- ✅ Analytics and reporting
- ✅ Templates and drag-drop editor
- ✅ Segmentation and personalization

**Cons:**
- ❌ Free plan shows Mailchimp branding
- ❌ More complex setup

---

## Option 3: ConvertKit (Creator-focused)

**Best for:** Content creators, paid plan recommended

### Features:
- Landing pages
- Email sequences
- Tag-based segmentation
- Sell digital products (premium guides)

**Pricing:** Free up to 300 subscribers

---

## Newsletter Content Ideas

### Weekly Newsletter Structure:
```
Subject: 🎯 This Week in Squish: New Drops & Rare Finds

📰 This Week's Highlights
- New release: Spring Collection at Target
- Restock alert: Belana the Cow at Costco
- Community spotlight: @collector_name's display

🔍 Featured Squish of the Week
- Deep dive into a rare/popular Squishmallow
- Where to find it
- Price range

💡 Collecting Tip
- Storage ideas
- Authentication tips
- Budget strategies

🛒 Deals & Restocks
- Where Squishmallows are on sale
- Upcoming releases
- Pre-order opportunities

📊 Collection Stats
- New additions to Squishmallowdex this week
- Most searched Squishmallows
- Trending animals/colors
```

### Content Calendar:
- **Mondays:** Weekly roundup (new releases, restocks)
- **Wednesdays:** Deep dive guide (rare Squish, collecting tips)
- **Fridays:** Weekend deals and upcoming drops

---

## Automated Newsletter Script

Create a simple Python script to send weekly updates:

```python
# newsletter_generator.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import csv
from datetime import datetime

def generate_weekly_newsletter():
    """Generate content for weekly newsletter"""
    # Get new Squishmallows added this week
    # Get blog posts published
    # Get community highlights

    subject = f"🎯 This Week in Squish - {datetime.now().strftime('%B %d, %Y')}"
    html_content = """
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h1 style="color: #00bcd4;">This Week in Squishmallows</h1>

        <h2>New Additions This Week</h2>
        <p>[Automatically populated from database]</p>

        <h2>Rare Finds</h2>
        <p>Collectors spotted these HTF Squish in stock:</p>
        <ul>
            <li>Item 1</li>
            <li>Item 2</li>
        </ul>

        <h2>Latest Blog Posts</h2>
        <p><a href="https://squishmallowdex.com/blog">Read on the blog</a></p>

        <hr>
        <p style="color: #999; font-size: 12px;">
        You're receiving this because you subscribed at Squishmallowdex.com<br>
        <a href="{unsubscribe_link}">Unsubscribe</a>
        </p>
    </body>
    </html>
    """

    return subject, html_content

def send_to_subscribers(subject, html_content):
    """Send email to all subscribers"""
    # Load subscribers from CSV
    with open('subscribers.csv', 'r') as f:
        subscribers = csv.DictReader(f)

        for subscriber in subscribers:
            send_email(
                to=subscriber['email'],
                subject=subject,
                html=html_content
            )

# Schedule this to run weekly using cron or GitHub Actions
```

---

## Growth Strategies

### 1. Popup/Inline Forms
- Exit-intent popup on collection page
- Inline signup after browsing 10+ Squish
- Slide-in form after 30 seconds

### 2. Lead Magnets
- **Free PDF:** "Top 50 Rare Squishmallows 2026"
- **Checklist:** "Collector's Wishlist Template"
- **Guide:** "How to Spot Fake Squishmallows"

### 3. Social Proof
- Show subscriber count: "Join 1,000+ collectors"
- Testimonials from subscribers
- Preview of past newsletters

### 4. Cross-Promotion
- Share newsletters on Twitter/Instagram
- Mention in YouTube videos (if you create them)
- Guest posts on collecting blogs

---

## Analytics to Track

1. **Subscriber Growth**
   - New signups per week
   - Unsubscribe rate
   - Traffic sources

2. **Engagement**
   - Open rate (aim for 20-30%)
   - Click-through rate (aim for 2-5%)
   - Most clicked links

3. **Revenue**
   - Affiliate clicks from newsletter
   - AdSense clicks from blog traffic
   - Premium guide sales (future)

---

## Legal Requirements

### Required Elements:
- ✅ Clear unsubscribe link in every email
- ✅ Your physical address (or use PO Box)
- ✅ Privacy policy explaining data use
- ✅ CAN-SPAM compliance

### Privacy Policy Additions:
```
Email Newsletter:
- We collect email addresses for our newsletter
- You can unsubscribe anytime
- We never sell or share your email
- We use [Mailchimp/Formspree] to manage subscriptions
```

---

## Next Steps

1. ☐ Choose email service (Formspree or Mailchimp)
2. ☐ Set up account and get form/embed code
3. ☐ Update blog page with newsletter form
4. ☐ Create welcome email template
5. ☐ Design first newsletter
6. ☐ Schedule first campaign
7. ☐ Add privacy policy section
8. ☐ Promote newsletter on social media

**Recommendation:** Start with Formspree to collect emails, then migrate to Mailchimp when you hit 50+ subscribers for automation features.
