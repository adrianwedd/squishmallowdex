# Twitter Bot Setup Guide

## 🎯 Goal
Automate Twitter presence with:
- Daily featured Squishmallow posts
- New addition announcements
- Collecting tips and tricks
- Weekly collection stats
- Community engagement

---

## Step 1: Create Twitter Developer Account

1. **Apply for Developer Access**
   - Go to: https://developer.twitter.com/en/apply-for-access
   - Click "Apply for a developer account"
   - Choose "Hobbyist" → "Making a bot"

2. **Fill Out Application**
   - Use case: "Automated posts about Squishmallow collecting"
   - Describe: "Tweet about new Squishmallows, collecting tips, and community engagement"
   - No ads or commercial use (unless monetized)

3. **Wait for Approval**
   - Usually approved within 24 hours
   - Check email for confirmation

---

## Step 2: Create Twitter App

1. **Create New App**
   - Dashboard: https://developer.twitter.com/en/portal/dashboard
   - Click "Create App"
   - Name: "Squishmallowdex Bot"
   - Description: "Automated Squishmallow collection updates"

2. **Get API Keys**
   - Click "Keys and tokens"
   - Generate:
     - API Key & Secret
     - Access Token & Secret
     - Bearer Token
   - **Save these securely** - you can't view them again!

3. **Set Permissions**
   - Go to "User authentication settings"
   - Enable "OAuth 1.0a"
   - Permissions: "Read and write"
   - Callback URL: `https://squishmallowdex.com/callback`
   - Website URL: `https://squishmallowdex.com`

---

## Step 3: Install Dependencies

```bash
pip install tweepy
```

---

## Step 4: Set Environment Variables

### On Mac/Linux:
```bash
export TWITTER_API_KEY="your_api_key_here"
export TWITTER_API_SECRET="your_api_secret_here"
export TWITTER_ACCESS_TOKEN="your_access_token_here"
export TWITTER_ACCESS_SECRET="your_access_secret_here"
export TWITTER_BEARER_TOKEN="your_bearer_token_here"
```

### On Windows (PowerShell):
```powershell
$env:TWITTER_API_KEY="your_api_key_here"
$env:TWITTER_API_SECRET="your_api_secret_here"
$env:TWITTER_ACCESS_TOKEN="your_access_token_here"
$env:TWITTER_ACCESS_SECRET="your_access_secret_here"
$env:TWITTER_BEARER_TOKEN="your_bearer_token_here"
```

### Permanent Setup (.env file):
```bash
# Create .env file in project root
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_SECRET=your_access_secret_here
TWITTER_BEARER_TOKEN=your_bearer_token_here
```

Then load in script:
```python
from dotenv import load_dotenv
load_dotenv()
```

---

## Step 5: Test the Bot

### Tweet a collecting tip:
```bash
python twitter_bot.py --mode tip
```

### Tweet about daily featured Squish:
```bash
python twitter_bot.py --mode daily
```

### Tweet collection stats:
```bash
python twitter_bot.py --mode stats
```

### Tweet about new addition:
```bash
python twitter_bot.py --mode new
```

---

## Step 6: Automate with GitHub Actions

Create `.github/workflows/twitter-bot.yml`:

```yaml
name: Twitter Bot - Daily Posts

on:
  schedule:
    # Daily at 10 AM EST (3 PM UTC)
    - cron: '0 15 * * *'
  workflow_dispatch:  # Manual trigger

jobs:
  tweet:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install tweepy

      - name: Post daily Squish
        env:
          TWITTER_API_KEY: ${{ secrets.TWITTER_API_KEY }}
          TWITTER_API_SECRET: ${{ secrets.TWITTER_API_SECRET }}
          TWITTER_ACCESS_TOKEN: ${{ secrets.TWITTER_ACCESS_TOKEN }}
          TWITTER_ACCESS_SECRET: ${{ secrets.TWITTER_ACCESS_SECRET }}
          TWITTER_BEARER_TOKEN: ${{ secrets.TWITTER_BEARER_TOKEN }}
        run: |
          python twitter_bot.py --mode daily
```

### Add Secrets to GitHub:
1. Go to repository Settings → Secrets and variables → Actions
2. Add each secret:
   - `TWITTER_API_KEY`
   - `TWITTER_API_SECRET`
   - `TWITTER_ACCESS_TOKEN`
   - `TWITTER_ACCESS_SECRET`
   - `TWITTER_BEARER_TOKEN`

---

## Posting Schedule

### Daily (Automated):
- **10 AM EST** - Featured Squishmallow of the day

### 3x per week (Mon/Wed/Fri):
- **12 PM EST** - Collecting tip

### Weekly (Sunday):
- **5 PM EST** - Collection statistics

### On-demand (Manual):
- New Squishmallow additions
- Blog post announcements
- Community highlights
- Restock alerts

---

## Content Strategy

### Tweet Templates:

#### New Addition:
```
🆕 New Squish Alert! 🐱

[Name] the [Animal] ([Size]) is now in the Squishmallowdex!

Check it out: https://squishmallowdex.com

#Squishmallows #NewRelease
```

#### Collecting Tip:
```
💡 Collecting Tip:

[Tip content]

#SquishmallowTips #Collecting
```

#### Daily Featured:
```
✨ Today's Featured Squish: [Name] the [Animal]!

[Short bio/fun fact]

Discover more: https://squishmallowdex.com

#Squishmallows #DailySquish
```

#### Weekly Stats:
```
📊 Collection Stats!

🎯 Total Squish: [count]
🏆 Most Common: [animal]
📈 Added This Week: [count]

Explore: https://squishmallowdex.com

#Squishmallows #Stats
```

---

## Engagement Strategy

### 1. Hashtag Strategy
**Primary:**
- #Squishmallows
- #Squish
- #SquishHunt

**Secondary:**
- #PlushCollector
- #SquishmallowCollector
- #Toys
- #Collecting

**Trending:**
- #SquishSunday (Sundays)
- #SquishFinds (rare finds)
- #SquishMail (new arrivals)

### 2. Retweet Community
- Retweet collector photos (with permission)
- Share rare finds from community
- Highlight creative displays

### 3. Respond to Mentions
Bot can auto-respond with:
- Squish facts when tagged
- Collection links
- Buying guide links

---

## Analytics to Track

1. **Engagement Rate**
   - Likes, retweets, replies
   - Best performing tweet types
   - Optimal posting times

2. **Follower Growth**
   - New followers per week
   - Follower demographics
   - Top sources

3. **Traffic**
   - Clicks to squishmallowdex.com
   - Conversion to email signups
   - Affiliate clicks

---

## Advanced Features (Future)

### Image Posting:
```python
def tweet_with_image(self, text: str, image_path: str):
    # Upload media
    media = self.api.media_upload(image_path)

    # Post tweet with image
    self.client.create_tweet(
        text=text,
        media_ids=[media.media_id]
    )
```

### Thread Support:
```python
def tweet_thread(self, tweets: list):
    previous_id = None
    for tweet_text in tweets:
        response = self.client.create_tweet(
            text=tweet_text,
            in_reply_to_tweet_id=previous_id
        )
        previous_id = response.data['id']
```

### Polls:
```python
def tweet_poll(self, question: str, options: list):
    self.client.create_tweet(
        text=question,
        poll_options=options,
        poll_duration_minutes=1440  # 24 hours
    )
```

---

## Best Practices

1. **Don't Over-post**
   - Max 3-5 tweets per day
   - Space them out (3-4 hours apart)

2. **Add Value**
   - Every tweet should inform or entertain
   - No pure promotional content
   - Mix automated with manual tweets

3. **Engage Authentically**
   - Respond to mentions personally (not automated)
   - Thank collectors for shares
   - Join conversations

4. **Monitor Performance**
   - Review analytics weekly
   - Adjust posting times based on engagement
   - Test different content types

5. **Stay Compliant**
   - Follow Twitter Automation Rules
   - Don't spam hashtags
   - No aggressive following/unfollowing
   - Respect rate limits

---

## Troubleshooting

### Rate Limits:
- **Tweets:** 300 per 3 hours (app limit)
- **Follows:** 400 per day
- **DMs:** 500 per day

If rate limited, wait and retry.

### API Errors:
```python
try:
    bot.tweet_daily_squish()
except tweepy.errors.TooManyRequests:
    print("Rate limited - waiting...")
    time.sleep(15 * 60)  # Wait 15 minutes
except tweepy.errors.Forbidden:
    print("Check API permissions")
```

---

## Next Steps

1. ☐ Apply for Twitter Developer account
2. ☐ Create app and get API keys
3. ☐ Set environment variables
4. ☐ Test bot with manual posts
5. ☐ Set up GitHub Actions for automation
6. ☐ Schedule regular posts
7. ☐ Monitor engagement and adjust
8. ☐ Build follower base organically

**Estimated Setup Time:** 2-3 hours (mostly waiting for developer approval)
