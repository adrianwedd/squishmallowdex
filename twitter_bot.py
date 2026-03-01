#!/usr/bin/env python3
"""
Squishmallow Twitter Bot - Auto-post about new additions and collecting tips

Features:
- Tweet about new Squishmallows added to the database
- Share collecting tips and facts
- Retweet community posts
- Respond to mentions with Squish facts

Setup required:
1. Twitter Developer Account (https://developer.twitter.com)
2. Create an app and get API keys
3. Install tweepy: pip install tweepy
4. Set environment variables for API keys
"""

import tweepy
import os
import random
import csv
from datetime import datetime, timedelta
from pathlib import Path


# Twitter API credentials (set these as environment variables)
API_KEY = os.getenv('TWITTER_API_KEY')
API_SECRET = os.getenv('TWITTER_API_SECRET')
ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
ACCESS_SECRET = os.getenv('TWITTER_ACCESS_SECRET')
BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')


class SquishmallowBot:
    """Twitter bot for Squishmallow updates and engagement."""

    def __init__(self):
        """Initialize Twitter API client."""
        self.client = tweepy.Client(
            bearer_token=BEARER_TOKEN,
            consumer_key=API_KEY,
            consumer_secret=API_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_SECRET
        )

    def tweet_new_squishmallow(self, name: str, animal: str, size: str, image_url: str = None):
        """Tweet about a newly added Squishmallow."""
        emoji_map = {
            'Cat': '🐱',
            'Dog': '🐶',
            'Frog': '🐸',
            'Cow': '🐮',
            'Dragon': '🐉',
            'Unicorn': '🦄',
            'Axolotl': '🦎',
            'Bigfoot': '👣',
            'Mushroom': '🍄',
        }

        emoji = emoji_map.get(animal, '✨')

        tweets = [
            f"🆕 New Squish Alert! {emoji}\n\n{name} the {animal} ({size}) is now in the Squishmallowdex!\n\nCheck it out: https://squishmallowdex.com #Squishmallows",
            f"{emoji} Just added: {name}!\n\nThis adorable {size} {animal} is now searchable in our collection.\n\nExplore: https://squishmallowdex.com #SquishHunt",
            f"NEW SQUISH! {emoji}\n\n{name} the {animal}\nSize: {size}\n\nFind them in your collection: https://squishmallowdex.com\n\n#Squishmallows #Collecting"
        ]

        tweet_text = random.choice(tweets)

        try:
            response = self.client.create_tweet(text=tweet_text)
            print(f"✅ Tweeted about {name}: {response.data['id']}")
            return response.data['id']
        except Exception as e:
            print(f"❌ Error tweeting: {e}")
            return None

    def tweet_collecting_tip(self):
        """Tweet a random collecting tip."""
        tips = [
            "💡 Collecting Tip: Always check the tag! Authentic Squishmallows have Kelly Toy or Jazwares tags. #SquishmallowTips",
            "🎯 Pro Tip: Join local collector groups on Facebook - they share restock alerts before anyone else! #SquishCommunity",
            "🛍️ Budget Tip: Five Below drops new 5\" Squish regularly for just $5.55. Perfect for starting your collection! #Squishmallows",
            "📦 Storage Tip: Use cube organizers or hammock nets to display your collection - keeps them dust-free and Instagram-ready! #SquishDisplay",
            "🔍 HTF Tip: Check stores early morning on weekdays - that's when restocks happen! #SquishHunting",
            "💰 Value Tip: Keep tags on if you ever want to resell - NWT (New With Tags) Squish are worth 2-3x more! #Collecting",
            "🎨 Display Tip: Group by color or theme for aesthetic photos. Rainbow collections get the most likes! 🌈 #SquishCollection",
            "⚠️ Authentication Tip: Real Squishmallows are super soft, not rough or plasticky. Trust the feel! #SquishTips"
        ]

        tip = random.choice(tips)

        try:
            response = self.client.create_tweet(text=tip)
            print(f"✅ Posted collecting tip: {response.data['id']}")
            return response.data['id']
        except Exception as e:
            print(f"❌ Error posting tip: {e}")
            return None

    def tweet_daily_squish(self):
        """Tweet about a random Squishmallow from the collection."""
        # Read from CSV and pick a random one
        csv_path = Path("squishmallowdex.csv")

        if not csv_path.exists():
            print("❌ CSV not found")
            return None

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            squish_list = list(reader)

        if not squish_list:
            return None

        squish = random.choice(squish_list)
        name = squish.get('Name', 'Unknown')
        animal = squish.get('Animal', 'Squish')
        bio = squish.get('Bio', '')[:100]  # Truncate bio

        tweet_text = f"✨ Today's Featured Squish: {name} the {animal}!\n\n{bio}...\n\nDiscover more: https://squishmallowdex.com\n\n#Squishmallows #DailySquish"

        try:
            response = self.client.create_tweet(text=tweet_text)
            print(f"✅ Posted daily Squish: {name}")
            return response.data['id']
        except Exception as e:
            print(f"❌ Error posting daily Squish: {e}")
            return None

    def tweet_weekly_stats(self):
        """Tweet collection statistics."""
        csv_path = Path("squishmallowdex.csv")

        if not csv_path.exists():
            return None

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            squish_list = list(reader)

        total = len(squish_list)
        animals = {}

        for squish in squish_list:
            animal = squish.get('Animal', 'Unknown')
            animals[animal] = animals.get(animal, 0) + 1

        top_animal = max(animals.items(), key=lambda x: x[1])

        tweet_text = f"📊 Collection Stats!\n\n🎯 Total Squish: {total:,}\n🏆 Most Common: {top_animal[0]} ({top_animal[1]} different designs)\n\nExplore the full collection: https://squishmallowdex.com\n\n#Squishmallows #Stats"

        try:
            response = self.client.create_tweet(text=tweet_text)
            print(f"✅ Posted weekly stats")
            return response.data['id']
        except Exception as e:
            print(f"❌ Error posting stats: {e}")
            return None


def main():
    """Main function to run the bot."""
    import argparse

    parser = argparse.ArgumentParser(description='Squishmallow Twitter Bot')
    parser.add_argument('--mode', choices=['new', 'tip', 'daily', 'stats'], default='daily',
                        help='Type of tweet to post')

    args = parser.parse_args()

    # Check if API keys are set
    if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET]):
        print("❌ Error: Twitter API credentials not set")
        print("Set environment variables:")
        print("  TWITTER_API_KEY")
        print("  TWITTER_API_SECRET")
        print("  TWITTER_ACCESS_TOKEN")
        print("  TWITTER_ACCESS_SECRET")
        print("  TWITTER_BEARER_TOKEN")
        return

    bot = SquishmallowBot()

    if args.mode == 'new':
        # Example: tweet about a new Squishmallow
        bot.tweet_new_squishmallow(
            name="Example",
            animal="Cat",
            size="8\""
        )
    elif args.mode == 'tip':
        bot.tweet_collecting_tip()
    elif args.mode == 'daily':
        bot.tweet_daily_squish()
    elif args.mode == 'stats':
        bot.tweet_weekly_stats()


if __name__ == '__main__':
    main()
