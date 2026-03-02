#!/usr/bin/env python3
"""
✨ Squishmallowdex ✨
Build a local, searchable Squishmallow table from the Squishmallows Wiki (Fandom).

This is YOUR personal Pokédex... but for Squishmallows!
Run this script to catch 'em all and build an offline collection you can browse anytime.

Personal/educational use only. Be polite: cache and delay requests.
This script is written to be friendly for learning and tinkering.
"""

from __future__ import annotations

# Standard library
import argparse
import base64
import csv
import hashlib
import json
import os
import random
import re
import sys
import time
from collections import Counter
from dataclasses import dataclass, field
from html import escape
from io import BytesIO
from typing import ClassVar, TextIO
from urllib.parse import quote, urljoin, urlparse

# Third-party
import requests
from bs4 import BeautifulSoup

# Import affiliate configuration
try:
    from affiliate_config import search_amazon_url
except ImportError:
    # Fallback if affiliate_config.py doesn't exist
    def search_amazon_url(name, marketplace="US"):
        from urllib.parse import quote_plus
        query = quote_plus(f"{name} squishmallow")
        return f"https://www.amazon.com/s?k={query}&tag=adrianwedd-20"

# Optional third-party (with graceful fallback)
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

if HAS_PIL:
    PIL_RESAMPLING = getattr(Image, "Resampling", Image).LANCZOS


# ═══════════════════════════════════════════════════════════════════════════════
# ⚙️ CONFIGURATION CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

# Request timeouts (seconds)
DEFAULT_PAGE_TIMEOUT = 30     # Timeout for page fetches
DEFAULT_IMAGE_TIMEOUT = 15    # Timeout for image fetches

# Delays between requests (seconds) - be polite to servers!
DEFAULT_REQUEST_DELAY = 1.2   # Delay between individual requests
DEFAULT_BATCH_DELAY = 5.0     # Extra delay between batches

# Batch processing
DEFAULT_BATCH_SIZE = 10       # Save progress every N catches

# Image settings
DEFAULT_THUMB_SIZE = 100      # Thumbnail size in pixels


# ═══════════════════════════════════════════════════════════════════════════════
# 🎨 FUN OUTPUT SYSTEM - Makes the console exciting!
# ═══════════════════════════════════════════════════════════════════════════════

def skipped_file_path(progress_file: str) -> str:
    """
    Derive the skipped-URLs file path from the progress file path.
    Works correctly regardless of file extension.
    """
    base, ext = os.path.splitext(progress_file)
    return f"{base}_skipped{ext or '.txt'}"


def load_ansi_art(filepath: str) -> str | None:
    """
    Load ANSI art from a file.
    Returns the content if the file exists, None otherwise.
    """
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception:
        return None


# Path to the phoenix ANSI art (relative to script location)
PHOENIX_ART_PATH = os.path.join(os.path.dirname(__file__) or ".", "phoenix.t.utf.ans")

# Path to the logo image for HTML output
LOGO_PATH = os.path.join(os.path.dirname(__file__) or ".", "squishmallowdex.png")


@dataclass
class AdventureLog:
    """Tracks stats and handles fun, educational output for young collectors."""

    verbose: int = 0  # 0=normal, 1=verbose (-v), 2=debug (-vv)
    adventure_mode: bool = True  # Default: adventure mode ON for maximum fun!
    use_color: bool = True
    quiet: bool = False  # Minimal output mode
    show_phoenix_art: bool = False  # Show the phoenix celebration at the end
    start_time: float = field(default_factory=time.time)
    log_file: str = "squishmallow.log"  # File to write logs to
    _file_handle: TextIO | None = field(default=None, repr=False)

    # Stats we track during the run
    new_catches: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    skipped: int = 0
    errors: int = 0
    types_seen: Counter = field(default_factory=Counter)
    colors_seen: Counter = field(default_factory=Counter)
    squads_seen: Counter = field(default_factory=Counter)
    sizes_seen: Counter = field(default_factory=Counter)
    years_seen: Counter = field(default_factory=Counter)
    letters_seen: set[str] = field(default_factory=set)
    names_collected: list[str] = field(default_factory=list)

    # Fun celebration milestones
    MILESTONES = [10, 25, 50, 100, 150, 200, 250, 300, 400, 500, 750, 1000]
    _ANSI_PATTERN: ClassVar[re.Pattern] = re.compile(r"\033\[[0-9;]*m")

    # Educational facts shown during download
    DID_YOU_KNOW = [
        # Internet & Networking
        "💡 The internet sends data in tiny packets, like digital letters!",
        "💡 Servers are big computers that store websites for everyone to visit!",
        "💡 URLs are like street addresses for websites!",
        "💡 HTTP stands for HyperText Transfer Protocol - it's how browsers talk to servers!",
        "💡 Your computer's 'User-Agent' tells websites what browser you're using!",
        "💡 WiFi signals are invisible radio waves bouncing around your house!",
        "💡 Data can travel around the world in less than a second!",
        "💡 The first website ever made is still online - it was created in 1991!",
        "💡 Undersea cables carry 99% of international internet traffic!",
        "💡 A megabyte is about 1 million characters - like a really long book!",
        # Programming & Code
        "💡 Python was named after Monty Python, not the snake! 🐍",
        "💡 HTML is the language websites speak - it stands for HyperText Markup Language!",
        "💡 JSON is a way computers share information - it's like a recipe card!",
        "💡 A 'bug' got its name when a real moth got stuck in an early computer!",
        "💡 Programmers use 'loops' to repeat things - like singing a chorus!",
        "💡 Variables are like labeled boxes that store information!",
        "💡 An 'algorithm' is just a fancy word for step-by-step instructions!",
        "💡 The first programmer ever was Ada Lovelace, in the 1840s!",
        "💡 Computers only understand 1s and 0s - called binary code!",
        "💡 Emojis are actually a type of font, just like letters! 😊",
        # This Script
        "💡 A 'cache' is like a memory box - we save pages so we don't download twice!",
        "💡 Parsing means reading through data to find the important parts!",
        "💡 A hash turns any text into a unique code - like a fingerprint for data!",
        "💡 CSV files are spreadsheets that any program can read!",
        "💡 Timeouts prevent your program from waiting forever if a server is slow!",
        "💡 Web scraping is like being a detective, finding clues hidden in web pages!",
        "💡 Rate limiting means being polite - we wait between requests so servers aren't overwhelmed!",
        "💡 This script saves your progress so you can stop and resume anytime!",
        "💡 Each Squishmallow page gets a unique filename based on its URL!",
        "💡 The HTML file works offline - no internet needed to browse your collection!",
        # Fun Tech Facts
        "💡 The first computer mouse was made of wood!",
        "💡 A 'gigabyte' could store about 300 songs!",
        "💡 The @ symbol is over 500 years old!",
        "💡 The first video game was created in 1958!",
        "💡 NASA uses Python for data analysis and mission planning!",
        "💡 Some computers can do billions of calculations per second!",
        "💡 QR codes were invented to track car parts in factories!",
        "💡 The cloud is really just other people's computers storing your stuff!",
        "💡 The undo command was invented at Xerox PARC in the 1970s!",
        "💡 Early typewriters only had uppercase - that's why we have Shift keys!",
        # Gentle Reminders & Self-Care
        "💧 Hey! Have you had some water recently? Your brain works better hydrated!",
        "💧 Water break! Even computers need cooling - and so do you!",
        "💧 Quick reminder: grab a drink of water! Hydration = happy brain!",
        "🌟 Stretch break! Roll your shoulders and take a deep breath!",
        "🌟 How's your posture? Sit up tall like a proud Squishmallow!",
        "🌟 Blink a few times! Your eyes are working hard!",
        "🌟 Take three deep breaths - you're doing great!",
        "💜 Hey, have you told Mum she's beautiful today? Go tell her!",
        "💜 Reminder: Tell your closest sibling they're awesome!",
        "💜 When did you last hug someone you love? Hugs are free!",
        "💜 Your family loves you! Maybe go tell them you love them too!",
        "💜 Smile at someone today - smiles are contagious!",
        "💜 You could make someone's day - tell them something you like about them!",
        "🎀 You're doing amazing! Collecting Squishmallows AND learning code!",
        "🎀 Fun fact: YOU are the rarest collector of all - there's only one you!",
        "🎀 Taking breaks is smart, not lazy. Rest when you need to!",
        "🎀 Mistakes help us learn - every coder makes them!",
        "🎀 Being kind to yourself is just as important as being kind to others!",
        "🍎 Have you eaten something today? Brains need fuel!",
        "🍎 A healthy snack might be nice right about now!",
        # Squishmallow Collecting Tips
        "🏷️ TIP: Check the tag! Collector Numbers help identify rare editions!",
        "🏷️ TIP: Keep your tags if you want to know the Squishdate later!",
        "🏷️ TIP: The bio poem on the tag tells you their personality!",
        "🔍 TIP: Use the search in your Squishmallowdex to find squish by color!",
        "🔍 TIP: Search by Squad to see all your Halloween or Valentine squish!",
        "🔍 TIP: You can search by Type to find all your unicorns or cats!",
        "📸 TIP: Take photos of your collection - it's fun to see it grow!",
        "📸 TIP: A group photo of your squish makes a great phone wallpaper!",
        "🎁 TIP: Trading with friends is a fun way to grow your collection!",
        "🧹 TIP: Spot clean your Squishmallows with mild soap and water!",
        "🧹 TIP: Let your squish air dry completely before cuddling again!",
        "🧹 TIP: Some Squishmallows can go in a pillowcase in the washing machine!",
        "🛏️ TIP: Squishmallows make great pillows for reading or watching shows!",
        "🛏️ TIP: Stack your squish to make a cozy reading nook!",
        "🛏️ TIP: A Squishmallow under your arm helps you sleep on your side!",
        "📦 TIP: Store squish in a breathable bag or bin - not airtight plastic!",
        "📦 TIP: Rotate which squish are on display to keep things fresh!",
        "📦 TIP: A hanging net in the corner is great for displaying squish!",
        "🌈 TIP: Sort your collection by color for a rainbow display!",
        "🌈 TIP: Group squish by Squad for themed displays!",
        "🌈 TIP: Smaller sizes are great for backpacks and travel!",
        "⭐ TIP: Clip-on Squishmallows are perfect for bags and keychains!",
        "⭐ TIP: Flip-a-Mallows are two squish in one - flip them inside out!",
        "⭐ TIP: HugMees are extra long for hugging!",
        "⭐ TIP: Stackables are flat on the bottom so they don't roll away!",
        "⭐ TIP: Squishville are tiny collectible Squishmallows with playsets!",
        "❤️ TIP: Every Squishmallow has a name and birthday - learn your faves!",
        "❤️ TIP: Some squish have the same name but different looks - variants!",
        "❤️ TIP: Your first Squishmallow is special - remember which one it was?",
        "❤️ TIP: It's okay to have favourites - they all still love you!",
        # Squishmallowdex Script Tips
        "🖥️ SQUISHMALLOWDEX: Catch 10 new squish → python3 squishmallowdex.py --limit 10",
        "🖥️ SQUISHMALLOWDEX: See your stats → python3 squishmallowdex.py --stats-only",
        "🖥️ SQUISHMALLOWDEX: Faster run (skip images) → python3 squishmallowdex.py --no-download-images",
        "🖥️ SQUISHMALLOWDEX: Press Ctrl+C anytime to stop - your progress is saved!",
        "🖥️ SQUISHMALLOWDEX: Quiet mode → python3 squishmallowdex.py --quiet",
        "🖥️ SQUISHMALLOWDEX: Maximum detail → python3 squishmallowdex.py -vv",
        "🖥️ SQUISHMALLOWDEX: Force re-download → python3 squishmallowdex.py --refresh",
        "🖥️ SQUISHMALLOWDEX: Check squishmallow.log for a full record of each run!",
        "🖥️ SQUISHMALLOWDEX: Open squishmallowdex.html in a browser to search your collection!",
        "🖥️ SQUISHMALLOWDEX: Open squishmallowdex.csv in Excel or Google Sheets!",
        "🖥️ SQUISHMALLOWDEX: See all options → python3 squishmallowdex.py --help",
        "🖥️ SQUISHMALLOWDEX: The cache_html folder makes reruns super fast!",
        "🖥️ SQUISHMALLOWDEX: Skip fun facts → python3 squishmallowdex.py --no-adventure",
        "🖥️ SQUISHMALLOWDEX: Catch 'em all! → python3 squishmallowdex.py --limit 0",
        "🖥️ SQUISHMALLOWDEX: Combine options → python3 squishmallowdex.py --limit 50 --quiet",
        # Terminal Tips
        "💻 TERMINAL: Use 'cd folder' to change directory - cd = change directory!",
        "💻 TERMINAL: Type 'ls' to list files in your current folder!",
        "💻 TERMINAL: Use 'cat file.txt' to display a file's contents!",
        "💻 TERMINAL: Try 'head file.txt' to see just the first 10 lines!",
        "💻 TERMINAL: Use 'tail file.txt' to see the last 10 lines!",
        "💻 TERMINAL: 'grep word file.txt' searches for 'word' in a file!",
        "💻 TERMINAL: Use 'grep -i' for case-insensitive search!",
        "💻 TERMINAL: The pipe | sends output to another command!",
        "💻 TERMINAL: Try 'cat file.txt | grep word' to search file contents!",
        "💻 TERMINAL: Use 'wc -l file.txt' to count lines in a file!",
        "💻 TERMINAL: Press Tab to autocomplete file and folder names!",
        "💻 TERMINAL: Press Up arrow to recall your last command!",
        "💻 TERMINAL: Use 'pwd' to see what folder you're in (print working directory)!",
        "💻 TERMINAL: 'mkdir newfolder' creates a new folder!",
        "💻 TERMINAL: 'cp file1 file2' copies a file!",
        "💻 TERMINAL: 'mv file1 file2' moves or renames a file!",
        "💻 TERMINAL: Use 'clear' to clear your terminal screen!",
        "💻 TERMINAL: 'python3 script.py' runs a Python script!",
        "💻 TERMINAL: Use 'less file.txt' to scroll through a big file!",
        "💻 TERMINAL: Press 'q' to quit less, man pages, and other viewers!",
    ]

    CATCH_MESSAGES = [
        # Classic catches
        "✨ CAUGHT! {name} joined your Squishmallowdex!",
        "🎯 GOT ONE! {name} is now in your collection!",
        "⭐ AWESOME! You found {name}!",
        "💖 SQUISH! {name} has been added!",
        "🌟 NICE CATCH! {name} is yours!",
        "💫 WOOHOO! {name} collected!",
        "🎪 AMAZING! {name} joins the squad!",
        "🎨 BEAUTIFUL! {name} is now catalogued!",
        # Excitement
        "🎉 YES! {name} is in the collection!",
        "🌈 WONDERFUL! {name} found a new home!",
        "💖 ADORABLE! {name} joins the family!",
        "🎊 HOORAY! Say hello to {name}!",
        "🥳 PARTY TIME! {name} has arrived!",
        "✨ SPARKLY! {name} is now yours!",
        "🌸 LOVELY! {name} joins the crew!",
        "💕 SWEET! {name} collected successfully!",
        # Action-packed
        "🚀 ZOOM! {name} blasts into your collection!",
        "⚡ ZAP! {name} captured!",
        "💥 BOOM! {name} is yours now!",
        "🎮 LEVEL UP! {name} unlocked!",
        "🏆 VICTORY! {name} acquired!",
        "🎯 BULLSEYE! {name} added!",
        "🔥 ON FIRE! {name} collected!",
        "💎 JACKPOT! {name} is in!",
        # Cute & Cozy
        "🧁 SWEET! {name} joins the cuddle pile!",
        "☁️ FLUFFY! {name} floats into your collection!",
        "🌙 DREAMY! {name} found!",
        "🍬 SUGAR! {name} is collected!",
        "🎀 PRECIOUS! {name} joins you!",
        "🌺 PRETTY! {name} catalogued!",
        "🦋 FLUTTER! {name} lands in your dex!",
        "🍩 SWEET CATCH! {name} is yours!",
        # Adventurous
        "🗺️ DISCOVERED! {name} joins the adventure!",
        "🔍 FOUND IT! {name} was hiding here!",
        "🏕️ ADVENTURE! {name} joins the expedition!",
        "🌊 SPLASH! {name} dives into your collection!",
        "🏔️ SUMMIT! {name} conquered!",
        "🌿 WILD! {name} discovered in the wild!",
        "🔮 MYSTICAL! {name} appears!",
        "🗝️ UNLOCKED! {name} joins the vault!",
        # Celebratory
        "🎵 HARMONY! {name} joins the chorus!",
        "🎭 SPECTACULAR! {name} takes the stage!",
        "🎬 ACTION! {name} enters the scene!",
        "📸 SNAPSHOT! {name} captured!",
        "🏅 CHAMPION! {name} wins a spot!",
        "👑 ROYAL! {name} crowned and collected!",
        "🎁 SURPRISE! {name} unwrapped!",
        "🌠 STELLAR! {name} shoots into your dex!",
        # Quirky
        "🦄 MAGICAL! {name} gallops in!",
        "🐾 PAWSOME! {name} joins the pack!",
        "🎈 POP! {name} floats into the collection!",
        "🍀 LUCKY! {name} found!",
    ]

    MILESTONE_MESSAGES = [
        "🎉 WOW! You've collected {n} Squishmallows! You're a SUPER collector!",
        "🏆 INCREDIBLE! {n} Squishmallows caught! Keep going!",
        "🎊 AMAZING! {n} in your Squishmallowdex! You're on fire!",
        "⭐ STELLAR! {n} Squishmallows! This collection is LEGENDARY!",
    ]

    # ANSI color codes (disabled if use_color=False or terminal doesn't support it)
    COLORS = {
        "reset": "\033[0m",
        "bold": "\033[1m",
        "dim": "\033[38;5;117m",
        "pink": "\033[38;5;213m",
        "purple": "\033[38;5;141m",
        "blue": "\033[38;5;75m",
        "cyan": "\033[38;5;87m",
        "green": "\033[38;5;120m",
        "yellow": "\033[38;5;228m",
        "orange": "\033[38;5;215m",
        "red": "\033[38;5;203m",
        "gray": "\033[38;5;252m",
    }

    def _c(self, color: str, text: str) -> str:
        """Apply color if colors are enabled."""
        if not self.use_color:
            return text
        return f"{self.COLORS.get(color, '')}{text}{self.COLORS['reset']}"

    def _strip_ansi(self, text: str) -> str:
        """Remove ANSI color codes for file logging."""
        return self._ANSI_PATTERN.sub("", text)

    def _log_to_file(self, text: str) -> None:
        """Write a line to the log file (without colors)."""
        if self._file_handle:
            clean = self._strip_ansi(text)
            self._file_handle.write(clean + "\n")
            self._file_handle.flush()

    def _print(self, text: str, **kwargs) -> None:
        """Print to console AND log to file."""
        print(text, **kwargs)
        # Don't log carriage-return lines (progress bars) to file
        if kwargs.get("end") != "\r":
            self._log_to_file(text)

    def open_log(self) -> None:
        """Open the log file for writing, creating parent directories if needed."""
        # Ensure parent directory exists
        log_dir = os.path.dirname(self.log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        self._file_handle = open(self.log_file, "a", encoding="utf-8")
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self._file_handle.write(f"\n{'=' * 70}\n")
        self._file_handle.write(f"Squishmallowdex run started at {timestamp}\n")
        self._file_handle.write(f"{'=' * 70}\n\n")
        self._file_handle.flush()

    def close_log(self) -> None:
        """Close the log file."""
        if self._file_handle:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            self._file_handle.write(f"\nRun completed at {timestamp}\n")
            self._file_handle.close()
            self._file_handle = None

    def banner(self) -> None:
        """Print the startup banner (suppressed in quiet mode)."""
        if self.quiet:
            return
        banner = """
╔═════════════════════════════════════════════════════════════╗
║                                                             ║
║   ███████╗ ██████╗ ██╗   ██╗██╗███████╗██╗  ██╗             ║
║   ██╔════╝██╔═══██╗██║   ██║██║██╔════╝██║  ██║             ║
║   ███████╗██║   ██║██║   ██║██║███████╗███████║  MALLOWDEX  ║
║   ╚════██║██║▄▄ ██║██║   ██║██║╚════██║██╔══██║             ║
║   ███████║╚██████╔╝╚██████╔╝██║███████║██║  ██║  v1.0.0     ║
║   ╚══════╝ ╚══▀▀═╝  ╚═════╝ ╚═╝╚══════╝╚═╝  ╚═╝             ║
║                                                             ║
║     🌟 Gotta Squish 'Em All! Your Offline Collection 🌟     ║
║                                                             ║
╚═════════════════════════════════════════════════════════════╝
"""
        self._print(self._c("cyan", banner))

    def info(self, msg: str, level: int = 0) -> None:
        """Print info message if verbosity is high enough (suppressed in quiet mode)."""
        if self.quiet:
            return
        if self.verbose >= level:
            self._print(self._c("cyan", f"  ℹ️  {msg}"))

    def debug(self, msg: str) -> None:
        """Print debug message (only in super verbose mode, suppressed in quiet mode)."""
        if self.quiet:
            return
        if self.verbose >= 2:
            self._print(self._c("gray", f"     🔍 {msg}"))

    def step(self, msg: str) -> None:
        """Print a major step (suppressed in quiet mode)."""
        if self.quiet:
            return
        self._print("")
        self._print(self._c("purple", f"  🚀 {msg}"))
        self._print("")

    def catch(self, name: str, total_count: int) -> None:
        """Celebrate catching a new Squishmallow!"""
        self.new_catches += 1

        if self.quiet:
            return

        msg = random.choice(self.CATCH_MESSAGES).format(name=name)
        self._print(self._c("green", f"  {msg}"))

        # Check for milestones
        if total_count in self.MILESTONES:
            self._celebrate_milestone(total_count)

        # Show educational facts every 10 catches in adventure mode
        if self.adventure_mode and self.new_catches > 0 and self.new_catches % 10 == 0:
            fact = self.DID_YOU_KNOW[self.new_catches // 10 % len(self.DID_YOU_KNOW)]
            self._print(self._c("blue", f"     {fact}"))

    def _celebrate_milestone(self, n: int) -> None:
        """Big celebration for hitting a milestone!"""
        msg = random.choice(self.MILESTONE_MESSAGES).format(n=n)
        border = "🎉" * 20
        self._print("")
        self._print(self._c("yellow", f"  {border}"))
        self._print(self._c("yellow", f"  {msg}"))
        self._print(self._c("yellow", f"  {border}"))
        self._print("")

    def skip(self, name: str, reason: str = "") -> None:
        """Note when we skip a page."""
        self.skipped += 1
        if self.quiet:
            return
        if self.verbose >= 1:
            reason_str = f" ({reason})" if reason else ""
            self._print(self._c("gray", f"  ⏭️  Skipped: {name}{reason_str}"))

    def cache_hit(self, what: str) -> None:
        """Note a cache hit (verbose mode)."""
        self.cache_hits += 1
        if self.quiet:
            return
        if self.verbose >= 2:
            self._print(self._c("gray", f"     💾 Cache hit: {what}"))

    def cache_miss(self, what: str) -> None:
        """Note a cache miss (verbose mode)."""
        self.cache_misses += 1
        if self.quiet:
            return
        if self.verbose >= 1:
            self._print(self._c("dim", f"     🌐 Downloading: {what}"))

    def error(self, msg: str) -> None:
        """Print an error."""
        self.errors += 1
        self._print(self._c("red", f"  ❌ ERROR: {msg}"))

    def warn(self, msg: str) -> None:
        """Print a warning."""
        self._print(self._c("orange", f"  ⚠️  {msg}"))

    def track_squish(self, row: dict) -> None:
        """Track stats about a collected Squishmallow."""
        if row.get("Type"):
            self.types_seen[row["Type"]] += 1
        if row.get("Color"):
            self.colors_seen[row["Color"]] += 1
        if row.get("Squad"):
            self.squads_seen[row["Squad"]] += 1
        if row.get("Size(s)"):
            # Sizes can be comma-separated, count each
            for size in row["Size(s)"].split(","):
                size = size.strip()
                if size:
                    self.sizes_seen[size] += 1
        if row.get("Year"):
            self.years_seen[row["Year"]] += 1
        if row.get("Name"):
            name = row["Name"]
            self.names_collected.append(name)
            if name and name[0].upper().isalpha():
                self.letters_seen.add(name[0].upper())

    def show_phoenix(self) -> None:
        """Display the epic phoenix ANSI art as a celebration (suppressed in quiet mode)."""
        if self.quiet:
            return
        art = load_ansi_art(PHOENIX_ART_PATH)
        if art:
            self._print("\n")
            # Print directly without color wrapping since it has its own ANSI codes
            # Note: This looks best in a color-capable terminal!
            print(art)
            self._log_to_file(art)  # Capture actual art in log file
            self._print(self._c("yellow", "    🔥 THE PHOENIX RISES! YOUR COLLECTION IS LEGENDARY! 🔥\n"))

    def summary(self, total_rows: int, existing_count: int, total_available: int = 0,
                 skipped_count: int = 0, csv_path: str = "", html_path: str = "",
                 dry_run: bool = False) -> None:
        """Print the epic summary at the end!"""
        elapsed = time.time() - self.start_time
        mins, secs = divmod(int(elapsed), 60)

        # Track if we should show phoenix at the end (easter egg for collecting ALL)
        total_valid = total_available - skipped_count
        collected_all = total_valid > 0 and total_rows >= total_valid

        self._print("")
        if dry_run:
            self._print(self._c("pink", "    SQUISHMALLOWDEX DRY RUN COMPLETE!"))
        else:
            self._print(self._c("pink", "    SQUISHMALLOWDEX BATCH COMPLETE!"))
        self._print("")

        # ─── Run Stats ───
        self._print(self._c("purple", "    ─── Run Stats ───"))
        if dry_run:
            self._print(f"    Would collect:        {self._c('green', str(self.new_catches))}")
            self._print(f"    Already have:         {existing_count}")
        else:
            self._print(f"    Total collected:      {self._c('bold', str(total_rows))}")
            self._print(f"    New this run:         {self._c('green', str(self.new_catches))}")
            self._print(f"    Already had:          {existing_count}")
        self._print(f"    Skipped:              {self.skipped}")
        if self.errors:
            self._print(f"    Errors:               {self._c('red', str(self.errors))}")
        self._print(f"    Time taken:           {mins}m {secs}s")

        if self.verbose >= 1:
            self._print(f"    Cache hits:           {self.cache_hits}")
            self._print(f"    Downloads:            {self.cache_misses}")

        # ─── Completion Progress ───
        if total_available > 0:
            self._print("")
            self._print(self._c("purple", "    ─── Completion Progress ───"))
            # Subtract skipped pages (invalid/redirect) from total
            total_valid = total_available - skipped_count
            pct = (total_rows / total_valid) * 100 if total_valid > 0 else 100
            remaining = total_valid - total_rows
            self._print(f"    Progress:             {pct:.1f}% complete!")
            if skipped_count > 0:
                self._print(f"    Skipped pages:        {skipped_count} (redirects/invalid)")
            if remaining > 0:
                self._print(f"    Remaining:            {self._c('yellow', f'{remaining} more to catch em all!')}")
            else:
                self._print(self._c("green", "    🎉 YOU CAUGHT 'EM ALL! 🎉"))

        # ─── Collection Diversity ───
        self._print("")
        self._print(self._c("purple", "    ─── Collection Diversity ───"))
        self._print(f"    Unique types:         {len(self.types_seen)}")
        self._print(f"    Unique colors:        {len(self.colors_seen)}")
        self._print(f"    Unique squads:        {len(self.squads_seen)}")

        # Alphabet coverage
        if self.letters_seen:
            all_letters = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            missing = all_letters - self.letters_seen
            coverage = f"{len(self.letters_seen)}/26 letters"
            if missing and len(missing) <= 5:
                coverage += f" (missing: {', '.join(sorted(missing))})"
            elif not missing:
                coverage += " - COMPLETE! 🎉"
            self._print(f"    Alphabet coverage:    {coverage}")

        # ─── Types & Squads ───
        self._print("")
        self._print(self._c("purple", "    ─── Types & Squads ───"))
        if self.types_seen:
            top_type = self.types_seen.most_common(1)[0]
            self._print(f"    Most common type:     {top_type[0]} ({top_type[1]})")
            # Unicorns - types with only 1
            unicorns = [t for t, c in self.types_seen.items() if c == 1]
            if unicorns:
                self._print(f"    Rare types (only 1):  {len(unicorns)} unique types!")

        if self.colors_seen:
            top_color = self.colors_seen.most_common(1)[0]
            rarest_color = self.colors_seen.most_common()[-1]
            self._print(f"    Most common color:    {top_color[0]} ({top_color[1]})")
            self._print(f"    Rarest color:         {rarest_color[0]} ({rarest_color[1]})")

        if self.squads_seen:
            top_squad = self.squads_seen.most_common(1)[0]
            smallest_squad = self.squads_seen.most_common()[-1]
            self._print(f"    Biggest squad:        {top_squad[0]} ({top_squad[1]})")
            self._print(f"    Smallest squad:       {smallest_squad[0]} ({smallest_squad[1]})")

        # ─── Sizes ───
        if self.sizes_seen:
            self._print("")
            self._print(self._c("purple", "    ─── Sizes ───"))
            top_size = self.sizes_seen.most_common(1)[0]
            self._print(f"    Most common size:     {top_size[0]} ({top_size[1]})")
            self._print(f"    Size variety:         {len(self.sizes_seen)} different sizes")

        # ─── Years & Dates ───
        if self.years_seen:
            self._print("")
            self._print(self._c("purple", "    ─── Years & Dates ───"))
            years = sorted([y for y in self.years_seen.keys() if y])
            if years:
                self._print(f"    Year range:           {years[0]} - {years[-1]}")
            top_year = self.years_seen.most_common(1)[0]
            self._print(f"    Most common year:     {top_year[0]} ({top_year[1]})")


        # ─── Name Fun ───
        non_empty_names = [n for n in self.names_collected if n]
        if non_empty_names:
            self._print("")
            self._print(self._c("purple", "    ─── Name Fun ───"))
            longest = max(non_empty_names, key=len)
            shortest = min(non_empty_names, key=len)
            self._print(f"    Longest name:         {longest} ({len(longest)} chars)")
            self._print(f"    Shortest name:        {shortest} ({len(shortest)} chars)")

            # Most common starting letter
            if self.letters_seen:
                letter_counts = Counter(n[0].upper() for n in self.names_collected if n and n[0].isalpha())
                if letter_counts:
                    top_letter = letter_counts.most_common(1)[0]
                    self._print(f"    Most common letter:   {top_letter[0]} ({top_letter[1]} names)")

        # ─── Random Spotlight ───
        if non_empty_names:
            self._print("")
            spotlight = random.choice(non_empty_names)
            self._print(self._c("yellow", f"    ⭐ Today's featured squish: {spotlight}!"))

        self._print("")

        # Show actual file paths
        if html_path:
            abs_html = os.path.abspath(html_path)
            self._print(self._c("green", "    Your Squishmallowdex is ready!"))
            self._print(self._c("cyan", f"    HTML: {abs_html}"))
        if csv_path:
            abs_csv = os.path.abspath(csv_path)
            self._print(self._c("cyan", f"    CSV:  {abs_csv}"))
        abs_log = os.path.abspath(self.log_file)
        self._print(self._c("gray", f"    Log:  {abs_log}\n"))

        # Easter egg: Show phoenix LAST when ALL squishmallows are collected!
        if self.show_phoenix_art or collected_all:
            self.show_phoenix()


# Global logger instance.
# This is intentionally global to simplify function signatures throughout the codebase.
# The AdventureLog handles both console output and file logging, and is configured
# once in main() based on CLI arguments. Thread safety is not a concern as this
# script runs single-threaded.
log: AdventureLog = AdventureLog()

BASE = "https://squishmallowsquad.fandom.com"
MASTER_LIST = urljoin(BASE, "/wiki/Master_List")
SITE_URL = "https://squishmallowdex.com/squishmallowdex.html"

HEADERS = {
    "User-Agent": "Squishmallowdex/1.0 (personal use)",
}

SKIP_NAMESPACES = (
    "File:",
    "Category:",
    "Special:",
    "Help:",
    "User:",
    "Template:",
    "Talk:",
)

NOISY_PAGES = re.compile(
    r"/wiki/(Master_List|Main_Page|All_Pages|Animals|Foods|Mythical_Creatures|By_.*)$"
)
NON_CHARACTER_TITLES = re.compile(
    r"\b(Master List|Main Page|All Pages|Squishville|Roblox)\b", re.I
)


def _sha1(s: str) -> str:
    # Hashing gives us stable, filesystem-safe filenames for cached pages and images.
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


def cache_path(cache_dir: str, url: str) -> str:
    # Use the URL hash so each page maps to exactly one cached file.
    return os.path.join(cache_dir, f"{_sha1(url)}.html")


def fetch(
    url: str,
    session: requests.Session,
    *,
    cache_dir: str,
    refresh: bool,
    delay: float,
) -> bytes:
    """
    Our "polite fetcher" - downloads web pages carefully and saves them.

    How it works:
    1) Check if we already have this page saved (cache hit = fast!)
    2) If not, download it from the internet (cache miss = slower)
    3) Wait a bit before the next request (so we don't overwhelm the server)
    """
    os.makedirs(cache_dir, exist_ok=True)
    path = cache_path(cache_dir, url)

    # Check the cache first - like looking in your backpack before buying a new pencil!
    if os.path.exists(path) and not refresh:
        log.cache_hit(url.split("/")[-1])
        with open(path, "rb") as f:
            return f.read()

    # Cache miss - we need to download from the internet
    log.cache_miss(url.split("/")[-1])
    log.debug(f"Full URL: {url}")

    # Network call: keep a short timeout so we don't hang forever.
    resp = session.get(url, headers=HEADERS, timeout=DEFAULT_PAGE_TIMEOUT)
    resp.raise_for_status()
    content = resp.content

    # Save to cache for next time
    with open(path, "wb") as f:
        f.write(content)
    log.debug(f"Saved {len(content):,} bytes to cache")

    # Slow down between requests so we don't hammer the site.
    # This is called "rate limiting" - it's the polite thing to do!
    time.sleep(delay)
    return content


def extract_master_list_urls(master_html: bytes) -> list[str]:
    # Parse the Master List and collect all /wiki/... links.
    soup = BeautifulSoup(master_html, "html.parser")
    content = soup.select_one("div.mw-parser-output") or soup

    urls: list[str] = []
    seen: set[str] = set()

    # Each Squishmallow page is usually linked from the Master List.
    for a in content.select("a[href^='/wiki/']"):
        href = (a.get("href") or "").split("#")[0]
        if not href.startswith("/wiki/"):
            continue

        title_part = href.replace("/wiki/", "", 1)
        # Skip non-article namespaces like File:, Category:, etc.
        if any(title_part.startswith(ns) for ns in SKIP_NAMESPACES):
            continue

        full = urljoin(BASE, href)
        if full not in seen:
            seen.add(full)
            urls.append(full)

    # Filter obvious list/index pages that are not individual characters.
    urls = [u for u in urls if not NOISY_PAGES.search(u)]
    return urls


def fetch_from_site(session: requests.Session) -> list[dict[str, str | None]]:
    """Fetch and parse all Squishmallow data from the deployed squishmallowdex.com site.

    Parses the HTML table (id="dex") and maps data-col indices to CSV field names.
    Returns a list of row dicts compatible with the CSV schema.
    """
    col_map = {
        3: "ImageURL",   # <img src> or wrapping <a href>
        4: "Name",
        5: "Type",
        6: "Color",
        7: "Squad",
        8: "Size(s)",
        9: "Collector Number",
        10: "Year",
        11: "Bio",
    }
    log.step(f"Fetching data from {SITE_URL} ...")
    try:
        resp = session.get(SITE_URL, headers=HEADERS, timeout=DEFAULT_PAGE_TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as e:
        log.warn(f"Failed to fetch site: {e}")
        return []

    soup = BeautifulSoup(resp.content, "html.parser")
    tbody = soup.select_one("table#dex tbody")
    if not tbody:
        log.warn("Could not find table#dex tbody in site HTML.")
        return []

    rows: list[dict[str, str | None]] = []
    for tr in tbody.find_all("tr"):
        row: dict[str, str | None] = {
            "Name": None, "URL": None, "ImageURL": None,
            "Type": None, "Color": None, "Squad": None,
            "Size(s)": None, "Collector Number": None, "Year": None,
            "Bio": None, "Extra": None,
        }
        for td in tr.find_all("td"):
            col = td.get("data-col")
            if col is None:
                continue
            col = int(col)
            if col not in col_map:
                continue
            field = col_map[col]
            if field == "ImageURL":
                img = td.find("img")
                link = td.find("a")
                row["ImageURL"] = (link.get("href") if link else None) or (img.get("src") if img else None)
            else:
                row[field] = td.get_text(strip=True) or None
        if row.get("Name"):
            rows.append(row)

    log.info(f"Loaded {len(rows)} Squishmallows from site.", 0)
    return rows


def normalize_label(label: str) -> str:
    # Infobox labels sometimes have messy whitespace; normalize it.
    return re.sub(r"\s+", " ", label.strip())


def parse_infobox(soup: BeautifulSoup) -> dict[str, str]:
    # The wiki uses a "portable infobox" with label/value pairs.
    info: dict[str, str] = {}
    aside = soup.select_one("aside.portable-infobox")
    if not aside:
        return info

    for item in aside.select(".pi-data"):
        lab_el = item.select_one(".pi-data-label")
        val_el = item.select_one(".pi-data-value")
        if not lab_el or not val_el:
            continue

        # Labels are things like "Type", "Color", "Squad", etc.
        label = normalize_label(lab_el.get_text(" ", strip=True))
        links = [
            a.get_text(" ", strip=True)
            for a in val_el.select("a")
            if a.get_text(strip=True)
        ]
        # Prefer linked values (cleaner) but fall back to raw text when needed.
        value = ", ".join(dict.fromkeys(links)) if links else val_el.get_text(" ", strip=True)

        if label and value:
            info[label] = value

    return info


def section_text_after_heading(
    soup: BeautifulSoup, heading_text: str, max_chars: int = 2500
) -> str | None:
    # Find the first heading like "Bio" and collect text until the next heading.
    headline = None
    for span in soup.select("span.mw-headline"):
        if span.get_text(strip=True) == heading_text:
            headline = span
            break
    if not headline:
        return None

    heading = headline.parent
    parts: list[str] = []

    # Walk forward through SIBLINGS only (not descendants) to avoid duplicates.
    for sib in heading.find_next_siblings():
        if sib.name in ("h2", "h3", "h4") and sib.find("span", class_="mw-headline"):
            break
        if sib.name in ("p", "blockquote", "ul", "ol", "div"):
            txt = " ".join(sib.stripped_strings)
            if txt:
                parts.append(txt)
        # Stop if the bio is getting huge; we want readable snippets.
        if sum(len(p) for p in parts) > max_chars:
            break

    text = " ".join(parts).strip()
    return text or None


def parse_squish_page(
    html: bytes, url: str
) -> tuple[dict[str, str | None], dict[str, str]]:
    # Parse a single Squishmallow page into a row dict + full infobox dict.
    soup = BeautifulSoup(html, "html.parser")

    # 1) Name: prefer the visible H1 title, fallback to OpenGraph title.
    name = None
    h1 = soup.find("h1")
    if h1:
        name = h1.get_text(" ", strip=True)
    if not name:
        ogt = soup.find("meta", property="og:title")
        if ogt and ogt.get("content"):
            name = ogt["content"].split("|")[0].strip()

    # 2) Image: OpenGraph image is the most reliable thumbnail.
    image = None
    ogi = soup.find("meta", property="og:image")
    if ogi and ogi.get("content"):
        image = ogi["content"]

    # 3) Infobox: structured stats we can keep in columns.
    info = parse_infobox(soup)

    # These are the fields we want to elevate into their own columns.
    wanted = [
        "Type",
        "Color",
        "Squad",
        "Size(s)",
        "Collector Number",
        "Year",
    ]
    row: dict[str, str | None] = {
        "Name": name,
        "URL": url,
        "ImageURL": image,
        "Bio": section_text_after_heading(soup, "Bio"),
    }

    for k in wanted:
        row[k] = info.get(k)

    # Preserve any remaining infobox keys so nothing is lost.
    extras = {k: v for k, v in info.items() if k not in wanted}
    row["Extra"] = json.dumps(extras, ensure_ascii=False) if extras else None
    return row, info


def is_character_page(name: str | None, info: dict[str, str]) -> bool:
    # Heuristic filter: we only keep pages that look like character profiles.
    if not name:
        return False
    if NON_CHARACTER_TITLES.search(name):
        return False
    if not info:
        return False
    required_keys = {
        "Type",
        "Color",
        "Squad",
        "Size(s)",
        "Collector Number",
        "Year",
    }
    # A page without any of these keys is probably a list/meta page.
    if not any(k in info for k in required_keys):
        return False
    return True


def download_image(
    session: requests.Session, url: str, out_dir: str, refresh: bool
) -> str | None:
    # Download and cache a thumbnail so the HTML page works offline.
    if not url:
        return None
    os.makedirs(out_dir, exist_ok=True)

    ext = os.path.splitext(urlparse(url).path)[1].lower()
    if ext not in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
        ext = ".jpg"

    path = os.path.join(out_dir, f"{_sha1(url)}{ext}")
    if os.path.exists(path) and not refresh:
        return path

    # Image fetch: keep timeout short so a single broken image doesn't stall.
    resp = session.get(url, headers=HEADERS, timeout=DEFAULT_IMAGE_TIMEOUT)
    resp.raise_for_status()
    content = resp.content

    # Validate we got the full image (protect against truncated downloads)
    expected_len = resp.headers.get("Content-Length")
    if expected_len:
        try:
            if len(content) < int(expected_len):
                log.warn(f"Incomplete image download: got {len(content)} of {expected_len} bytes")
                return None
        except ValueError:
            pass  # Invalid Content-Length header, skip validation

    # Basic sanity check: images should have some content
    if len(content) < 100:
        log.warn(f"Suspiciously small image ({len(content)} bytes), skipping")
        return None

    with open(path, "wb") as f:
        f.write(content)
    return path


def _get_cached_image_path(images_dir: str, url: str) -> str:
    """Return the expected cache path for an image URL."""
    ext = os.path.splitext(urlparse(url).path)[1].lower()
    if ext not in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
        ext = ".jpg"
    return os.path.join(images_dir, f"{_sha1(url)}{ext}")


def image_to_base64_thumbnail(
    image_source: str, session: requests.Session | None = None, max_size: int = 100
) -> str | None:
    """Resize an image to a thumbnail and return as base64 data URL.

    image_source can be a local path or a URL. If it's a URL and session is provided,
    the image will be downloaded and converted.
    """
    if not HAS_PIL or not image_source:
        return None
    try:
        # Determine if it's a URL or local file
        if image_source.startswith(("http://", "https://")):
            if session is None:
                return None
            resp = session.get(image_source, timeout=DEFAULT_IMAGE_TIMEOUT)
            if resp.status_code != 200:
                return None
            img = Image.open(BytesIO(resp.content))
        elif os.path.exists(image_source):
            img = Image.open(image_source)
        else:
            return None

        with img:
            # Convert to RGB if necessary (for PNG with transparency, etc.)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            # Resize maintaining aspect ratio
            img.thumbnail((max_size, max_size), PIL_RESAMPLING)
            # Save to bytes as JPEG
            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=60)
            b64 = base64.b64encode(buffer.getvalue()).decode("ascii")
            return f"data:image/jpeg;base64,{b64}"
    except Exception as e:
        if log.verbose >= 2:
            log.debug(f"Image processing failed for {image_source}: {e}")
        return None


def _table_config() -> tuple[list[str], set[str], set[str], set[str]]:
    columns = [
        "♥",        # Favourite (heart)
        "Own",      # I own this
        "🛒",        # Buy on Amazon
        "Image",
        "Name",
        "Type",
        "Color",
        "Squad",
        "Size(s)",
        "Collector Number",
        "Year",
        "Bio",
    ]
    hidden_default = {"Squad", "Size(s)", "Collector Number"}
    no_sort = {"♥", "Own", "🛒", "Image", "Bio"}
    html_columns = {"Image"}
    return columns, hidden_default, no_sort, html_columns


def _build_table_header(columns: list[str], hidden_default: set[str], no_sort: set[str]) -> str:
    head_cells = []
    for i, col in enumerate(columns):
        sortable = "true" if col not in no_sort else "false"
        hidden = "true" if col in hidden_default else "false"
        head_cells.append(
            f'<th data-col="{i}" data-sortable="{sortable}" data-hidden="{hidden}">{escape(col)}</th>'
        )
    return f"<tr>{''.join(head_cells)}</tr>"


def _build_table_body(
    rows: list[dict[str, str | None]],
    columns: list[str],
    html_columns: set[str],
) -> str:
    body_rows = []
    for row in rows:
        # Use URL hash as unique ID for localStorage
        row_id = _sha1(row.get("URL") or row.get("Name") or "")[:12]
        cells = []
        for i, col in enumerate(columns):
            if col == "♥":
                # Heart button for favourites
                cells.append(
                    f'<td data-col="{i}"><button class="heart-btn" data-id="{row_id}" aria-label="Favourite">♡</button></td>'
                )
            elif col == "Own":
                # Checkbox for "I own this"
                cells.append(
                    f'<td data-col="{i}"><input type="checkbox" class="own-cb" data-id="{row_id}" aria-label="I own this"></td>'
                )
            elif col == "🛒":
                # Buy button for Amazon affiliate link
                name = row.get("Name") or ""
                # Use centralized affiliate link generation
                buy_link = search_amazon_url(name)
                cells.append(
                    f'<td data-col="{i}"><a href="{buy_link}" target="_blank" rel="noopener" class="buy-btn" data-id="{row_id}" aria-label="Buy on Amazon">🛒</a></td>'
                )
            else:
                val = row.get(col) or ""
                if col not in html_columns:
                    val = escape(str(val))
                cells.append(f'<td data-col="{i}">{val}</td>')
        body_rows.append(f'<tr data-id="{row_id}">{"".join(cells)}</tr>')
    return "".join(body_rows)


def _load_b64(path: str) -> str:
    if not path or not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def _build_logo_html(logo_path: str) -> str:
    logo_b64 = _load_b64(logo_path)
    if not logo_b64:
        return ""
    return f'<img src="data:image/png;base64,{logo_b64}" alt="Squishmallowdex" class="logo"/>'


def _load_pwa_icons(logo_path: str) -> tuple[str, str]:
    script_dir = os.path.dirname(logo_path) if logo_path else "."
    icon_192_path = os.path.join(script_dir, "icon-192.png")
    icon_512_path = os.path.join(script_dir, "icon-512.png")
    return _load_b64(icon_192_path), _load_b64(icon_512_path)


def _build_manifest_json(icon_192_b64: str, icon_512_b64: str) -> str:
    pwa_icons = []
    if icon_192_b64:
        pwa_icons.append({"src": f"data:image/png;base64,{icon_192_b64}", "sizes": "192x192", "type": "image/png"})
    if icon_512_b64:
        pwa_icons.append({"src": f"data:image/png;base64,{icon_512_b64}", "sizes": "512x512", "type": "image/png"})
    manifest = {
        "name": "Squishmallowdex",
        "short_name": "Squishdex",
        "description": "Your Pokédex for Squishmallows - works offline!",
        "start_url": ".",
        "display": "standalone",
        "theme_color": "#00bcd4",
        "background_color": "#ffffff",
        "icons": pwa_icons,
    }
    return quote(json.dumps(manifest), safe="")


def _render_css(thumb_size: int, thumb_size_768: int, thumb_size_480: int) -> str:
    return f"""
  :root {{
    --ink: #1f1a16;
    --accent: #00bcd4;
    --card: #ffffff;
    --muted: #6b5b52;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: "Trebuchet MS", "Verdana", "Geneva", sans-serif;
    color: var(--ink);
    background: #32bcc6;
  }}
  header {{
    padding: 24px 20px 16px;
    display: flex;
    align-items: center;
    gap: 16px;
  }}
  .logo {{
    height: 64px;
    width: auto;
    border-radius: 12px;
    background: #fff;
    padding: 4px;
  }}
  .header-text {{
    flex: 0 0 auto;
  }}
  h1 {{
    margin: 0 0 4px;
    font-size: 28px;
    letter-spacing: 0.5px;
  }}
  .sub {{
    margin: 0;
    color: var(--muted);
    font-size: 14px;
  }}
  .controls {{
    display: flex;
    gap: 10px;
    align-items: center;
    flex: 1;
    justify-content: flex-end;
  }}
  .search {{
    flex: 1;
    min-width: 200px;
    max-width: 400px;
    padding: 10px 12px;
    border: 2px solid var(--accent);
    border-radius: 12px;
    font-size: 16px;
    background: var(--card);
  }}
  .col-picker {{
    position: relative;
  }}
  .col-btn {{
    padding: 10px 14px;
    border: 2px solid #ddd;
    border-radius: 12px;
    background: var(--card);
    cursor: pointer;
    font-size: 14px;
    display: flex;
    align-items: center;
    gap: 6px;
  }}
  .col-btn:hover {{
    border-color: var(--accent);
  }}
  .col-dropdown {{
    display: none;
    position: absolute;
    top: 100%;
    right: 0;
    margin-top: 4px;
    background: var(--card);
    border: 1px solid #ddd;
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    padding: 8px 0;
    min-width: 180px;
    z-index: 100;
  }}
  .col-dropdown.open {{
    display: block;
  }}
  .col-dropdown label {{
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 14px;
    cursor: pointer;
    font-size: 14px;
  }}
  .col-dropdown label:hover {{
    background: #e0f7fa;
  }}
  .col-dropdown input {{
    width: 16px;
    height: 16px;
    accent-color: var(--accent);
  }}
  .table-wrap {{
    padding: 0 16px 28px;
    overflow-x: auto;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    background: var(--card);
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  }}
  th, td {{
    padding: 10px 12px;
    text-align: left;
    vertical-align: top;
    border-bottom: 1px solid #e0e0e0;
  }}
  th {{
    background: #e0f7fa;
    position: sticky;
    top: 0;
    z-index: 1;
    white-space: nowrap;
  }}
  th[data-sortable="true"] {{
    cursor: pointer;
    user-select: none;
  }}
  th[data-sortable="true"]:hover {{
    background: #b2ebf2;
  }}
  th .sort-indicator {{
    margin-left: 4px;
    opacity: 0.3;
  }}
  th.sorted .sort-indicator {{
    opacity: 1;
  }}
  tr:hover {{
    background: #e0f7fa;
  }}
  img.thumb {{
    width: {thumb_size}px;
    height: {thumb_size}px;
    object-fit: cover;
    border-radius: 12px;
    border: 2px solid #80deea;
  }}
  /* Bio column: limit width for comfortable reading */
  td[data-col="10"] {{
    max-width: 300px;
    line-height: 1.4;
  }}
  /* Heart button */
  .heart-btn {{
    background: none;
    border: none;
    font-size: 20px;
    cursor: pointer;
    padding: 4px 8px;
    border-radius: 8px;
    transition: transform 0.15s;
  }}
  .heart-btn:hover {{
    transform: scale(1.2);
  }}
  .heart-btn.active {{
    color: #e74c3c;
  }}
  .heart-btn.active::after {{
    content: '';
  }}
  .heart-btn:not(.active)::after {{
    content: '';
  }}
  /* Checkbox styling */
  .own-cb {{
    width: 20px;
    height: 20px;
    cursor: pointer;
    accent-color: var(--accent);
  }}
  /* Buy button */
  .buy-btn {{
    display: inline-block;
    background: var(--accent);
    color: white;
    text-decoration: none;
    font-size: 18px;
    padding: 6px 12px;
    border-radius: 8px;
    transition: all 0.2s;
    border: none;
    cursor: pointer;
  }}
  .buy-btn:hover {{
    transform: scale(1.1);
    background: #00a3b8;
    box-shadow: 0 2px 8px rgba(0, 188, 212, 0.3);
  }}
  .buy-btn:active {{
    transform: scale(0.95);
  }}
  /* Filter buttons */
  .filters {{
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }}
  .filter-btn {{
    padding: 8px 14px;
    border: 2px solid #ddd;
    border-radius: 20px;
    background: var(--card);
    cursor: pointer;
    font-size: 13px;
    transition: all 0.15s;
  }}
  .filter-btn:hover {{
    border-color: var(--accent);
  }}
  .filter-btn.active {{
    background: var(--accent);
    color: white;
    border-color: var(--accent);
  }}
  /* Mobile responsive */
  @media (max-width: 768px) {{
    header {{
      padding: 16px;
      flex-wrap: wrap;
    }}
    .logo {{
      height: 48px;
    }}
    h1 {{
      font-size: 22px;
    }}
    .controls {{
      flex-wrap: wrap;
      width: 100%;
      justify-content: flex-start;
    }}
    .search {{
      max-width: none;
      flex: 1 1 100%;
    }}
    .filters {{
      width: auto;
    }}
    th, td {{
      padding: 8px 6px;
      font-size: 14px;
    }}
    img.thumb {{
      width: {thumb_size_768}px;
      height: {thumb_size_768}px;
    }}
    td[data-col="10"] {{
      max-width: 200px;
      font-size: 13px;
    }}
  }}
  @media (max-width: 480px) {{
    .table-wrap {{
      padding: 0 8px 20px;
    }}
    th, td {{
      padding: 6px 4px;
      font-size: 13px;
    }}
    img.thumb {{
      width: {thumb_size_480}px;
      height: {thumb_size_480}px;
    }}
    .heart-btn {{
      font-size: 18px;
      padding: 2px 4px;
    }}
    .own-cb {{
      width: 18px;
      height: 18px;
    }}
  }}
  .page-link {{
    color: var(--accent);
    text-decoration: none;
    font-weight: 600;
  }}
  .hidden {{
    display: none !important;
  }}
  .count {{
    color: var(--muted);
    font-size: 13px;
    padding: 8px 16px;
  }}
  /* Footer */
  .site-footer {{
    background: var(--ink);
    color: white;
    padding: 24px 20px;
    margin-top: 40px;
    text-align: center;
  }}
  .ftc-disclosure {{
    margin: 0 0 12px;
    font-size: 13px;
    opacity: 0.9;
    max-width: 800px;
    margin-left: auto;
    margin-right: auto;
  }}
  .ftc-disclosure strong {{
    color: var(--accent);
  }}
  .footer-links {{
    margin: 0;
    font-size: 14px;
  }}
  .footer-links a {{
    color: var(--accent);
    text-decoration: none;
    margin: 0 8px;
  }}
  .footer-links a:hover {{
    text-decoration: underline;
  }}
  /* Pagination */
  .pagination {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 12px 16px;
    flex-wrap: wrap;
  }}
  .page-btn {{
    padding: 8px 12px;
    border: 2px solid #ddd;
    border-radius: 8px;
    background: var(--card);
    cursor: pointer;
    font-size: 16px;
    min-width: 40px;
    transition: all 0.15s;
  }}
  .page-btn:hover:not(:disabled) {{
    border-color: var(--accent);
    background: #e0f7fa;
  }}
  .page-btn:disabled {{
    opacity: 0.3;
    cursor: not-allowed;
  }}
  .page-info {{
    padding: 8px 16px;
    font-size: 14px;
    color: var(--muted);
    font-weight: 500;
  }}
  .page-size {{
    padding: 8px 12px;
    border: 2px solid #ddd;
    border-radius: 8px;
    background: var(--card);
    cursor: pointer;
    font-size: 14px;
  }}
  .page-size:hover {{
    border-color: var(--accent);
  }}
  @media (max-width: 480px) {{
    .pagination {{
      gap: 4px;
      padding: 8px;
    }}
    .page-btn {{
      padding: 6px 10px;
      font-size: 14px;
      min-width: 36px;
    }}
    .page-info {{
      font-size: 13px;
      padding: 6px 12px;
    }}
    .page-size {{
      font-size: 13px;
      padding: 6px 10px;
    }}
  }}
  /* ─── View toggle ─── */
  .view-toggle {{
    display: inline-flex;
    gap: 4px;
    padding: 4px;
    border-radius: 14px;
    background: rgba(255,255,255,0.7);
    border: 2px solid rgba(255,255,255,0.5);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.65);
  }}
  .view-btn {{
    padding: 8px 12px;
    border: none;
    border-radius: 10px;
    background: transparent;
    color: var(--ink);
    cursor: pointer;
    font-size: 13px;
    font-weight: 700;
  }}
  .view-btn[aria-pressed="true"] {{
    background: var(--card);
    color: #00879a;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
  }}
  /* ─── Card view ─── */
  .card-wrap {{
    padding: 0 16px 28px;
  }}
  .card-toolbar {{
    display: none;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    margin: 0 0 12px;
    padding: 10px 12px;
    background: rgba(255,255,255,0.88);
    border: 1px solid rgba(0,0,0,0.07);
    border-radius: 14px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.06);
  }}
  .card-wrap.active .card-toolbar {{
    display: flex;
  }}
  .card-toolbar label {{
    font-size: 13px;
    color: var(--muted);
    font-weight: 700;
  }}
  .card-sort {{
    margin-left: auto;
    min-width: 220px;
    max-width: 340px;
    width: 100%;
    padding: 8px 10px;
    border-radius: 10px;
    border: 2px solid #d9eef1;
    background: #fff;
    font-size: 14px;
  }}
  .card-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 14px;
  }}
  .card-loader {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    padding: 60px 20px;
    color: var(--muted);
    font-size: 15px;
    font-weight: 600;
  }}
  .card-loader[hidden] {{ display: none; }}
  .card-loader-spinner {{
    width: 28px;
    height: 28px;
    border: 3px solid #d9eef1;
    border-top-color: var(--accent);
    border-radius: 50%;
    animation: card-spin 0.7s linear infinite;
    flex-shrink: 0;
  }}
  @keyframes card-spin {{ to {{ transform: rotate(360deg); }} }}
  .squish-card {{
    position: relative;
    display: grid;
    grid-template-rows: auto auto 1fr auto;
    gap: 10px;
    background:
      radial-gradient(circle at top right, rgba(0,188,212,0.12), transparent 45%),
      radial-gradient(circle at top left, rgba(255,255,255,0.8), transparent 55%),
      #fff;
    border: 1px solid rgba(0,0,0,0.08);
    border-radius: 18px;
    padding: 12px;
    box-shadow: 0 10px 24px rgba(0,0,0,0.08);
    overflow: hidden;
  }}
  @media (prefers-reduced-motion: no-preference) {{
    #cardWrap.active {{
      animation: cardWrapFadeIn 0.15s ease;
    }}
    @keyframes cardWrapFadeIn {{
      from {{ opacity: 0; }}
      to   {{ opacity: 1; }}
    }}
    .squish-card {{
      transition: transform 0.18s ease, box-shadow 0.18s ease;
    }}
    .squish-card:hover {{
      transform: translateY(-2px);
      box-shadow: 0 14px 30px rgba(0,0,0,0.12);
    }}
  }}
  .card-media {{
    position: relative;
    display: block;
    border-radius: 14px;
    overflow: hidden;
    background: #eafcff;
    aspect-ratio: 1 / 1;
  }}
  .card-media img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    border: none;
    border-radius: 0;
  }}
  .card-title {{
    display: flex;
    align-items: start;
    justify-content: space-between;
    gap: 8px;
  }}
  .card-title h2 {{
    margin: 0;
    font-size: 18px;
    line-height: 1.15;
  }}
  .card-type {{
    margin: 4px 0 0;
    color: var(--muted);
    font-size: 13px;
    font-weight: 700;
  }}
  .card-meta {{
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }}
  .chip {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    max-width: 100%;
    padding: 5px 8px;
    border-radius: 999px;
    background: #e7fbfe;
    border: 1px solid #caeff4;
    color: #155760;
    font-size: 12px;
    line-height: 1.2;
  }}
  .chip strong {{
    color: #0b7280;
    font-weight: 700;
  }}
  .card-bio {{
    margin: 0;
    color: #4f4a45;
    font-size: 13px;
    line-height: 1.35;
    display: -webkit-box;
    -webkit-line-clamp: 4;
    -webkit-box-orient: vertical;
    overflow: hidden;
    min-height: 4.8em;
  }}
  .card-actions {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: auto;
    padding-top: 4px;
  }}
  .card-own-wrap {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    color: var(--muted);
    font-size: 12px;
    font-weight: 700;
  }}
  .card-actions .buy-btn {{
    margin-left: auto;
    padding: 6px 10px;
    font-size: 16px;
  }}
  /* ─── Mode visibility ─── */
  .mode-table .card-wrap {{ display: none; }}
  .mode-cards .table-wrap {{ display: none; }}
  .mode-cards .pagination {{ display: none; }}
  .mode-cards .col-btn {{
    opacity: 0.55;
    cursor: not-allowed;
  }}
  .mode-cards .col-btn:hover {{
    border-color: #ddd;
  }}
  @media (max-width: 768px) {{
    .view-toggle {{ order: -1; }}
    .card-wrap {{ padding: 0 8px 20px; }}
    .card-toolbar {{
      flex-direction: column;
      align-items: flex-start;
    }}
    .card-sort {{ min-width: 0; max-width: none; }}
    .card-grid {{
      grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
      gap: 10px;
    }}
  }}
  @media (max-width: 480px) {{
    .card-wrap {{ padding: 0 6px 16px; }}
    .card-grid {{
      grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
      gap: 8px;
    }}
  }}
"""


def render_html(
    rows: list[dict[str, str | None]],
    out_path: str,
    title: str,
    logo_path: str = "",
    thumb_size: int = DEFAULT_THUMB_SIZE,
) -> None:
    # Render a self-contained HTML page with search, sorting, and column picker.
    # Calculate responsive thumbnail sizes (proportional scaling for smaller screens)
    thumb_size_768 = int(thumb_size * 0.78)  # ~78% for tablets
    thumb_size_480 = int(thumb_size * 0.67)  # ~67% for mobile

    columns, hidden_default, no_sort, html_columns = _table_config()
    head = _build_table_header(columns, hidden_default, no_sort)
    body_html = _build_table_body(rows, columns, html_columns)
    logo_html = _build_logo_html(logo_path)
    icon_192_b64, icon_512_b64 = _load_pwa_icons(logo_path)

    # Column config as JSON for JS
    col_config = json.dumps([{"name": c, "hidden": c in hidden_default, "sortable": c not in no_sort} for c in columns])

    # PWA manifest - URL-encoded for data URI
    manifest_json = _build_manifest_json(icon_192_b64, icon_512_b64)
    css = _render_css(thumb_size, thumb_size_768, thumb_size_480)

    # Inline CSS/JS so the page works fully offline.
    html = f"""<!doctype html>
<html lang="en">
<head>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-MLCG3SLHC2"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());

  gtag('config', 'G-MLCG3SLHC2');
</script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5242622588206425"
     crossorigin="anonymous"></script>

<!-- SEO Meta Tags -->
<meta name="description" content="Discover and explore the complete Squishmallows collection! Search through thousands of adorable Squishmallows plushies, find rare characters, learn about new releases, and build your perfect collection."/>
<meta name="keywords" content="squishmallows, squishmallow, plush toys, stuffed animals, squishmallow collection, rare squishmallows, squishmallow database, kellytoy, squishy toys, collectible plushies"/>
<meta name="author" content="Squishmallowdex"/>
<meta name="robots" content="index, follow"/>
<link rel="canonical" href="https://squishmallowdex.com"/>

<!-- Open Graph / Facebook -->
<meta property="og:type" content="website"/>
<meta property="og:url" content="https://squishmallowdex.com"/>
<meta property="og:title" content="Squishmallowdex - Complete Squishmallows Collection & Database"/>
<meta property="og:description" content="Discover and explore the complete Squishmallows collection! Search through thousands of adorable Squishmallows plushies, find rare characters, learn about new releases, and build your perfect collection."/>
<meta property="og:image" content="https://squishmallowdex.com/og-image.png"/>
<meta property="og:site_name" content="Squishmallowdex"/>

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:url" content="https://squishmallowdex.com"/>
<meta name="twitter:title" content="Squishmallowdex - Complete Squishmallows Collection & Database"/>
<meta name="twitter:description" content="Discover and explore the complete Squishmallows collection! Search through thousands of adorable Squishmallows plushies, find rare characters, learn about new releases, and build your perfect collection."/>
<meta name="twitter:image" content="https://squishmallowdex.com/og-image.png"/>
<meta name="twitter:site" content="@squishmallowdex"/>
<meta name="twitter:creator" content="@squishmallowdex"/>

<!-- Structured Data (JSON-LD) -->
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "Squishmallowdex",
  "description": "Discover and explore the complete Squishmallows collection! Search through thousands of adorable Squishmallows plushies, find rare characters, learn about new releases, and build your perfect collection.",
  "url": "https://squishmallowdex.com",
  "potentialAction": {{
    "@type": "SearchAction",
    "target": {{
      "@type": "EntryPoint",
      "urlTemplate": "https://squishmallowdex.com?q={{{{search_term_string}}}}"
    }},
    "query-input": "required name=search_term_string"
  }}
}}
</script>

<!-- Organization JSON-LD -->
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Squishmallowdex",
  "url": "https://squishmallowdex.com",
  "logo": "https://squishmallowdex.com/og-image.png",
  "description": "Your comprehensive database for Squishmallows - search, track, and collect over 3,000 plush toys",
  "sameAs": [
    "https://github.com/adrianwedd/squishmallowdex"
  ],
  "contactPoint": {{
    "@type": "ContactPoint",
    "contactType": "Customer Service",
    "url": "https://squishmallowdex.com/about"
  }}
}}
</script>

<!-- CollectionPage JSON-LD -->
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "name": "{title}",
  "description": "Browse and search through the complete collection of Squishmallows plush toys - over 3,000 unique characters",
  "url": "https://squishmallowdex.com/squishmallowdex",
  "about": {{
    "@type": "Thing",
    "name": "Squishmallows",
    "description": "Collectible plush toys by Kelly Toy Holdings LLC"
  }},
  "mainEntity": {{
    "@type": "ItemList",
    "numberOfItems": {len(rows)},
    "itemListElement": "Collection of Squishmallows plush toys"
  }}
}}
</script>

<!-- BreadcrumbList JSON-LD -->
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {{
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://squishmallowdex.com"
    }},
    {{
      "@type": "ListItem",
      "position": 2,
      "name": "Collection",
      "item": "https://squishmallowdex.com/squishmallowdex"
    }}
  ]
}}
</script>

<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<meta name="apple-mobile-web-app-capable" content="yes"/>
<meta name="apple-mobile-web-app-status-bar-style" content="default"/>
<meta name="apple-mobile-web-app-title" content="Squishmallowdex"/>
<meta name="theme-color" content="#00bcd4"/>
<link rel="manifest" href="data:application/json,{manifest_json}"/>
<title>{escape(title)}</title>
<style>
{css}
</style>
</head>
<body class="mode-table">
<header>
  {logo_html}
  <div class="header-text">
    <h1>{escape(title)}</h1>
    <p class="sub">Your Pok&#233;dex for Squishmallows. Works offline!</p>
  </div>
  <div class="controls">
    <input id="search" class="search" type="search" placeholder="Search by name, type, color..."/>
    <div class="view-toggle" role="group" aria-label="View mode">
      <button class="view-btn" id="viewTableBtn" type="button" aria-pressed="true">Table</button>
      <button class="view-btn" id="viewCardsBtn" type="button" aria-pressed="false">Cards</button>
      <button class="view-btn" id="compactBtn" type="button" aria-pressed="false" title="Compact card view" hidden>Compact</button>
    </div>
    <div class="filters">
      <button class="filter-btn" id="filterFav">❤️ Favourites</button>
      <button class="filter-btn" id="filterOwn">✓ I Own</button>
    </div>
    <div class="col-picker">
      <button class="col-btn" id="colBtn">⚙️ Columns</button>
      <div class="col-dropdown" id="colDropdown"></div>
    </div>
  </div>
</header>
<div class="count" id="count"></div>
<div class="pagination" id="paginationTop">
  <button class="page-btn" id="firstPage" aria-label="First page">«</button>
  <button class="page-btn" id="prevPage" aria-label="Previous page">‹</button>
  <span class="page-info" id="pageInfo">Page 1</span>
  <button class="page-btn" id="nextPage" aria-label="Next page">›</button>
  <button class="page-btn" id="lastPage" aria-label="Last page">»</button>
  <select class="page-size" id="pageSize" aria-label="Items per page">
    <option value="50">50 per page</option>
    <option value="100" selected>100 per page</option>
    <option value="250">250 per page</option>
    <option value="500">500 per page</option>
  </select>
</div>
<div class="table-wrap">
  <table id="dex">
    <thead>{head}</thead>
    <tbody>
      {body_html}
    </tbody>
  </table>
</div>
<div class="card-wrap" id="cardWrap" aria-live="polite">
  <div class="card-toolbar">
    <label for="cardSort">Sort cards by</label>
    <select id="cardSort" class="card-sort" aria-label="Sort cards">
      <option value="table">Table order</option>
      <option value="name:asc">Name (A–Z)</option>
      <option value="name:desc">Name (Z–A)</option>
      <option value="type:asc">Type (A–Z)</option>
      <option value="type:desc">Type (Z–A)</option>
      <option value="year:desc">Year (newest)</option>
      <option value="year:asc">Year (oldest)</option>
      <option value="collector:desc">Collector # (high)</option>
      <option value="collector:asc">Collector # (low)</option>
    </select>
  </div>
  <div class="card-loader" id="cardLoader" hidden aria-label="Loading cards…" role="status"><span class="card-loader-spinner"></span><span>Loading cards…</span></div>
  <div class="card-grid" id="cardGrid"></div>
</div>
<script>
(function() {{
  // ─── Safe localStorage ───
  function safeGet(key, def) {{
    try {{
      const v = localStorage.getItem(key);
      return v !== null ? v : (def !== undefined ? def : '{{}}');
    }} catch(e) {{ return def !== undefined ? def : '{{}}'; }}
  }}
  function safeSet(key, value) {{
    try {{ localStorage.setItem(key, value); }} catch(e) {{}}
  }}

  // ─── DOM refs ───
  const colConfig    = {col_config};
  const table        = document.getElementById('dex');
  const tbody        = table.querySelector('tbody');
  const headers      = Array.from(table.querySelectorAll('th'));
  const search       = document.getElementById('search');
  const colBtn       = document.getElementById('colBtn');
  const colDropdown  = document.getElementById('colDropdown');
  const countEl      = document.getElementById('count');
  const filterFav    = document.getElementById('filterFav');
  const filterOwn    = document.getElementById('filterOwn');
  const viewTableBtn = document.getElementById('viewTableBtn');
  const viewCardsBtn = document.getElementById('viewCardsBtn');
  const cardWrap     = document.getElementById('cardWrap');
  const cardGrid     = document.getElementById('cardGrid');
  const cardSort     = document.getElementById('cardSort');
  const cardLoader   = document.getElementById('cardLoader');
  const firstPageBtn = document.getElementById('firstPage');
  const prevPageBtn  = document.getElementById('prevPage');
  const nextPageBtn  = document.getElementById('nextPage');
  const lastPageBtn  = document.getElementById('lastPage');
  const pageInfo     = document.getElementById('pageInfo');
  const pageSizeEl   = document.getElementById('pageSize');

  // ─── State ───
  const sortableCols = new Map([[4,'name'],[5,'type'],[6,'color'],[7,'squad'],[8,'sizes'],[9,'collector'],[10,'year']]);
  const fieldToCol   = new Map(Array.from(sortableCols).map(([col,field]) => [field, col]));
  let visibility  = {{}};
  let favourites  = {{}};
  let owned       = {{}};
  let buyClicks   = {{}};
  let showOnlyFav = false;
  let showOnlyOwn = false;
  let viewMode    = safeGet('squishdex-view') === 'cards' ? 'cards' : 'table';
  let viewRenderToken = 0;
  let searchTimer = null;
  let currentPage = 1;
  let pageSize    = 100;
  let lastTotalPages = 1;
  const sortState = {{ field: null, dir: 1, col: -1 }};

  try {{ visibility = JSON.parse(safeGet('squishdex-cols')); }} catch(e) {{}}
  try {{ favourites = JSON.parse(safeGet('squishdex-fav')); }} catch(e) {{}}
  try {{ owned      = JSON.parse(safeGet('squishdex-own')); }} catch(e) {{}}
  try {{ buyClicks  = JSON.parse(safeGet('squishdex-buyclicks')); }} catch(e) {{}}

  colConfig.forEach(c => {{
    if (visibility[c.name] === undefined) visibility[c.name] = !c.hidden;
  }});

  // ─── Row models (extracted once from DOM) ───
  const rowModels = Array.from(tbody.querySelectorAll('tr')).map(extractRowModel);
  const cardsById = new Map();

  // ─── Bootstrap ───
  buildColumnPicker();
  buildSortHeaders();
  buildCardView();
  bindControls();
  bindItemControls();
  applyVisibility();
  restoreCardSort();
  applyViewMode(viewMode);

  // ─── Row model extraction ───
  function extractRowModel(tr, sourceIndex) {{
    const cells = tr.children;
    const imageLink = cells[3]?.querySelector('a');
    const img       = imageLink?.querySelector('img');
    const buyLink   = cells[2]?.querySelector('a');
    const m = {{
      id: tr.dataset.id, row: tr, sourceIndex,
      name:      cellText(cells[4]),
      type:      cellText(cells[5]),
      color:     cellText(cells[6]),
      squad:     cellText(cells[7]),
      sizes:     cellText(cells[8]),
      collector: cellText(cells[9]),
      year:      cellText(cells[10]),
      bio:       cellText(cells[11]),
      buyHref:   buyLink  ? buyLink.getAttribute('href')  : '',
      imageHref: imageLink ? imageLink.getAttribute('href') : '',
      imageSrc:  img ? img.getAttribute('src')  : '',
      imageAlt:  img ? (img.getAttribute('alt') || '') : ''
    }};
    m.collectorNum = parseNum(m.collector);
    m.yearNum      = parseNum(m.year);
    m.searchText   = tr.textContent.toLowerCase();
    return m;
  }}
  function cellText(cell) {{ return cell ? cell.textContent.trim() : ''; }}
  function parseNum(v) {{
    if (!v) return null;
    const n = parseFloat(String(v).replace(/,/g, ''));
    return Number.isFinite(n) ? n : null;
  }}

  // ─── Column picker ───
  function buildColumnPicker() {{
    colConfig.forEach(c => {{
      const label = document.createElement('label');
      const cb = document.createElement('input');
      cb.type = 'checkbox';
      cb.checked = visibility[c.name];
      cb.addEventListener('change', () => {{
        visibility[c.name] = cb.checked;
        safeSet('squishdex-cols', JSON.stringify(visibility));
        applyVisibility();
      }});
      label.append(cb, document.createTextNode(c.name));
      colDropdown.appendChild(label);
    }});
    colBtn.addEventListener('click', e => {{
      if (viewMode === 'cards') return;
      e.stopPropagation();
      colDropdown.classList.toggle('open');
    }});
    document.addEventListener('click', () => colDropdown.classList.remove('open'));
    colDropdown.addEventListener('click', e => e.stopPropagation());
  }}
  function applyVisibility() {{
    colConfig.forEach((c, i) => {{
      const show = visibility[c.name];
      table.querySelectorAll(`[data-col="${{i}}"]`).forEach(el => el.classList.toggle('hidden', !show));
    }});
  }}

  // ─── Sort headers ───
  function buildSortHeaders() {{
    headers.forEach((th, i) => {{
      if (th.dataset.sortable !== 'true') return;
      const ind = document.createElement('span');
      ind.className = 'sort-indicator';
      ind.textContent = '↕';
      th.appendChild(ind);
      th._sortIndicator = ind;
      th.setAttribute('tabindex', '0');
      th.addEventListener('click', () => {{
        const field = sortableCols.get(i);
        if (!field) return;
        sortState.col === i ? (sortState.dir *= -1) : Object.assign(sortState, {{col: i, field, dir: 1}});
        persistCardSort();
        syncCardSortControl();
        applyFiltersAndSort();
      }});
      th.addEventListener('keydown', e => {{
        if (e.key === 'Enter' || e.key === ' ') {{ e.preventDefault(); th.click(); }}
      }});
    }});
  }}
  function updateHeaderIndicators() {{
    headers.forEach(th => {{
      if (!th._sortIndicator) return;
      th.classList.remove('sorted');
      th._sortIndicator.textContent = '↕';
    }});
    if (sortState.col < 0) return;
    const th = headers[sortState.col];
    if (th?._sortIndicator) {{
      th.classList.add('sorted');
      th._sortIndicator.textContent = sortState.dir === 1 ? '↑' : '↓';
    }}
  }}

  // ─── Card view ───
  function buildCardView() {{
    const frag = document.createDocumentFragment();
    rowModels.forEach(m => {{
      const card = document.createElement('article');
      card.className = 'squish-card';
      card.dataset.id = m.id;

      const media = document.createElement(m.imageHref ? 'a' : 'div');
      media.className = 'card-media';
      if (m.imageHref) {{
        media.href = m.imageHref; media.target = '_blank'; media.rel = 'noopener';
        media.setAttribute('aria-label', `View full image of ${{m.name || 'Squishmallow'}}`);
      }}
      if (m.imageSrc) {{
        const img = document.createElement('img');
        img.src = m.imageSrc; img.loading = 'lazy';
        img.alt = m.imageAlt || `${{m.name || 'Squishmallow'}} image`;
        media.appendChild(img);
      }}
      card.appendChild(media);

      const titleDiv = document.createElement('div');
      titleDiv.className = 'card-title';
      const titleText = document.createElement('div');
      const h2 = document.createElement('h2');
      h2.textContent = m.name || 'Unknown';
      titleText.appendChild(h2);
      const typeP = document.createElement('p');
      typeP.className = 'card-type';
      typeP.textContent = m.type || '';
      titleText.appendChild(typeP);
      titleDiv.appendChild(titleText);
      card.appendChild(titleDiv);

      const meta = document.createElement('div');
      meta.className = 'card-meta';
      appendChip(meta, 'Color', m.color);
      appendChip(meta, 'Year',  m.year);
      appendChip(meta, 'Size',  m.sizes, 'low');
      appendChip(meta, '#',     m.collector);
      appendChip(meta, 'Squad', m.squad, 'low');
      card.appendChild(meta);

      const bio = document.createElement('p');
      bio.className = 'card-bio';
      bio.textContent = m.bio || 'No bio listed yet.';
      card.appendChild(bio);

      const actions = document.createElement('div');
      actions.className = 'card-actions';
      const heart = document.createElement('button');
      heart.type = 'button'; heart.className = 'heart-btn'; heart.dataset.id = m.id;
      heart.setAttribute('aria-label', `Favourite ${{m.name || 'Squishmallow'}}`);
      heart.textContent = '♡';
      actions.appendChild(heart);

      const ownWrap = document.createElement('label');
      ownWrap.className = 'card-own-wrap';
      const ownCb = document.createElement('input');
      ownCb.type = 'checkbox'; ownCb.className = 'own-cb'; ownCb.dataset.id = m.id;
      ownCb.setAttribute('aria-label', `I own ${{m.name || 'this squishmallow'}}`);
      const ownTxt = document.createElement('span');
      ownTxt.textContent = 'Own';
      ownWrap.append(ownCb, ownTxt);
      actions.appendChild(ownWrap);

      if (m.buyHref) {{
        const buy = document.createElement('a');
        buy.className = 'buy-btn'; buy.href = m.buyHref;
        buy.target = '_blank'; buy.rel = 'noopener'; buy.dataset.id = m.id;
        buy.textContent = '🛒';
        buy.setAttribute('aria-label', `Buy ${{m.name || 'Squishmallow'}} on Amazon`);
        actions.appendChild(buy);
      }} else {{ actions.appendChild(document.createElement('span')); }}

      card.appendChild(actions);
      m.card = card;
      cardsById.set(m.id, card);
      frag.appendChild(card);
    }});
    cardGrid.appendChild(frag);
  }}
  function appendChip(parent, label, value, priority) {{
    if (!value) return;
    const chip = document.createElement('span');
    chip.className = 'chip';
    if (priority) chip.dataset.priority = priority;
    const strong = document.createElement('strong');
    strong.textContent = label;
    chip.appendChild(strong);
    chip.appendChild(document.createTextNode(` ${{value}}`));
    parent.appendChild(chip);
  }}

  // ─── View mode ───
  function applyViewMode(mode) {{
    viewMode = mode === 'cards' ? 'cards' : 'table';
    document.body.classList.toggle('mode-cards', viewMode === 'cards');
    document.body.classList.toggle('mode-table', viewMode === 'table');
    viewTableBtn.setAttribute('aria-pressed', String(viewMode === 'table'));
    viewCardsBtn.setAttribute('aria-pressed', String(viewMode === 'cards'));
    const disabled = viewMode === 'cards';
    colBtn.disabled = disabled;
    colBtn.setAttribute('aria-disabled', String(disabled));
    colBtn.title = disabled ? 'Table view only' : '';
    if (disabled) colDropdown.classList.remove('open');
    const compactBtn = document.getElementById('compactBtn');
    if (compactBtn) compactBtn.hidden = viewMode !== 'cards';
    safeSet('squishdex-view', viewMode);

    if (viewMode === 'cards') {{
      const token = ++viewRenderToken;
      cardLoader.hidden = false;
      cardGrid.hidden = true;
      requestAnimationFrame(() => requestAnimationFrame(() => {{
        if (token !== viewRenderToken) return;
        applyFiltersAndSort();
        cardLoader.hidden = true;
        cardGrid.hidden = false;
        cardWrap.classList.add('active');
      }}));
    }} else {{
      ++viewRenderToken;
      cardWrap.classList.remove('active');
      applyFiltersAndSort();
    }}
  }}

  // ─── Card sort ───
  function restoreCardSort() {{
    applyCardSortSelection(localStorage.getItem('squishdex-card-sort') || 'table');
    syncCardSortControl();
  }}
  function applyCardSortSelection(value) {{
    if (!value || value === 'table') {{
      sortState.field = null; sortState.dir = 1; sortState.col = -1;
      updateHeaderIndicators(); return;
    }}
    const [field, dir] = value.split(':');
    sortState.field = field;
    sortState.dir   = dir === 'desc' ? -1 : 1;
    sortState.col   = fieldToCol.has(field) ? fieldToCol.get(field) : -1;
    updateHeaderIndicators();
  }}
  function currentSortValue() {{
    return sortState.field ? `${{sortState.field}}:${{sortState.dir === 1 ? 'asc' : 'desc'}}` : 'table';
  }}
  function persistCardSort() {{
    safeSet('squishdex-card-sort', currentSortValue());
  }}
  function syncCardSortControl() {{
    const value = currentSortValue();
    cardSort.value = Array.from(cardSort.options).some(o => o.value === value) ? value : 'table';
    updateHeaderIndicators();
  }}

  // ─── Controls ───
  function bindControls() {{
    search.addEventListener('input', () => {{
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => {{ currentPage = 1; applyFiltersAndSort(); }}, 130);
    }});
    filterFav.addEventListener('click', () => {{
      showOnlyFav = !showOnlyFav;
      filterFav.classList.toggle('active', showOnlyFav);
      currentPage = 1; applyFiltersAndSort();
    }});
    filterOwn.addEventListener('click', () => {{
      showOnlyOwn = !showOnlyOwn;
      filterOwn.classList.toggle('active', showOnlyOwn);
      currentPage = 1; applyFiltersAndSort();
    }});
    viewTableBtn.addEventListener('click', () => applyViewMode('table'));
    viewCardsBtn.addEventListener('click', () => applyViewMode('cards'));
    cardSort.addEventListener('change', () => {{
      applyCardSortSelection(cardSort.value);
      persistCardSort();
      applyFiltersAndSort();
    }});
    const compactBtn = document.getElementById('compactBtn');
    let density = safeGet('squishdex-density', 'normal');
    const applyDensity = () => {{
      document.body.classList.toggle('density-compact', density === 'compact');
      if (compactBtn) compactBtn.setAttribute('aria-pressed', String(density === 'compact'));
    }};
    applyDensity();
    if (compactBtn) {{
      compactBtn.addEventListener('click', () => {{
        density = density === 'compact' ? 'normal' : 'compact';
        safeSet('squishdex-density', density);
        applyDensity();
      }});
    }}
    firstPageBtn.addEventListener('click', () => goToPage(1));
    prevPageBtn.addEventListener('click', () => goToPage(currentPage - 1));
    nextPageBtn.addEventListener('click', () => goToPage(currentPage + 1));
    lastPageBtn.addEventListener('click', () => goToPage(lastTotalPages));
    pageSizeEl.addEventListener('change', () => {{
      pageSize = parseInt(pageSizeEl.value);
      currentPage = 1;
      applyFiltersAndSort();
    }});
  }}
  function goToPage(page) {{
    currentPage = page;
    applyFiltersAndSort();
    window.scrollTo({{ top: 0, behavior: 'smooth' }});
  }}

  // ─── Item controls ───
  function bindItemControls() {{
    document.querySelectorAll('.heart-btn').forEach(btn => {{
      const id = btn.dataset.id;
      btn.addEventListener('click', () => {{
        favourites[id] = !favourites[id];
        safeSet('squishdex-fav', JSON.stringify(favourites));
        syncSelection(id);
        applyFiltersAndSort();
      }});
    }});
    document.querySelectorAll('.own-cb').forEach(cb => {{
      const id = cb.dataset.id;
      cb.addEventListener('change', () => {{
        owned[id] = cb.checked;
        safeSet('squishdex-own', JSON.stringify(owned));
        syncSelection(id);
        applyFiltersAndSort();
      }});
    }});
    rowModels.forEach(m => syncSelection(m.id));
    document.querySelectorAll('.buy-btn').forEach(btn => {{
      btn.addEventListener('click', () => {{
        const id = btn.dataset.id;
        buyClicks[id] = (buyClicks[id] || 0) + 1;
        safeSet('squishdex-buyclicks', JSON.stringify(buyClicks));
      }});
    }});
  }}
  function syncSelection(id) {{
    const isFav = !!favourites[id];
    document.querySelectorAll(`.heart-btn[data-id="${{id}}"]`).forEach(btn => {{
      btn.classList.toggle('active', isFav);
      btn.textContent = isFav ? '❤️' : '♡';
    }});
    const isOwned = !!owned[id];
    document.querySelectorAll(`.own-cb[data-id="${{id}}"]`).forEach(cb => {{ cb.checked = isOwned; }});
  }}

  // ─── Filter + sort + pagination ───
  function computeVisibleIds() {{
    const q = search.value.trim().toLowerCase();
    const ids = new Set();
    rowModels.forEach(m => {{
      const ok = (!q || m.searchText.includes(q))
              && (!showOnlyFav || !!favourites[m.id])
              && (!showOnlyOwn || !!owned[m.id]);
      if (ok) ids.add(m.id);
    }});
    return ids;
  }}
  function compareModels(a, b) {{
    if (!sortState.field) return a.sourceIndex - b.sourceIndex;
    let r = 0;
    if (sortState.field === 'collector' || sortState.field === 'year') {{
      const an = sortState.field === 'collector' ? a.collectorNum : a.yearNum;
      const bn = sortState.field === 'collector' ? b.collectorNum : b.yearNum;
      if (an == null && bn == null) r = 0;
      else if (an == null) return 1;
      else if (bn == null) return -1;
      else r = an - bn;
    }} else {{
      r = String(a[sortState.field] || '').toLowerCase().localeCompare(String(b[sortState.field] || '').toLowerCase());
    }}
    if (r === 0) r = String(a.name || '').localeCompare(String(b.name || ''));
    if (r === 0) r = a.sourceIndex - b.sourceIndex;
    return r * sortState.dir;
  }}
  function applyFiltersAndSort() {{
    const visibleIds = computeVisibleIds();
    const ordered    = rowModels.slice().sort(compareModels);
    if (viewMode === 'table') {{
      applyTablePagination(ordered, visibleIds);
    }} else {{
      const frag = document.createDocumentFragment();
      ordered.forEach(m => {{
        m.card.classList.toggle('hidden', !visibleIds.has(m.id));
        frag.appendChild(m.card);
      }});
      cardGrid.appendChild(frag);
      const visible = visibleIds.size, total = rowModels.length;
      countEl.textContent = visible === total
        ? `${{total}} Squishmallows`
        : `Showing ${{visible}} of ${{total}}`;
    }}
  }}
  function applyTablePagination(ordered, visibleIds) {{
    const frag = document.createDocumentFragment();
    ordered.forEach(m => frag.appendChild(m.row));
    tbody.appendChild(frag);

    const visibleModels = ordered.filter(m => visibleIds.has(m.id));
    const filteredCount = visibleModels.length;
    const total         = rowModels.length;
    const totalPages    = Math.ceil(filteredCount / pageSize) || 1;
    lastTotalPages = totalPages;
    if (currentPage > totalPages) currentPage = totalPages;
    if (currentPage < 1) currentPage = 1;

    const start = (currentPage - 1) * pageSize;
    const end   = start + pageSize;
    let visIdx = 0;
    ordered.forEach(m => {{
      if (!visibleIds.has(m.id)) {{ m.row.style.display = 'none'; return; }}
      m.row.style.display = (visIdx >= start && visIdx < end) ? '' : 'none';
      visIdx++;
    }});

    const showing = Math.min(pageSize, filteredCount - start);
    pageInfo.textContent = `Page ${{currentPage}} of ${{totalPages}}`;
    firstPageBtn.disabled = currentPage === 1;
    prevPageBtn.disabled  = currentPage === 1;
    nextPageBtn.disabled  = currentPage === totalPages;
    lastPageBtn.disabled  = currentPage === totalPages;
    if (filteredCount === total) {{
      countEl.textContent = `Showing ${{start + 1}}–${{start + showing}} of ${{total}} Squishmallows`;
    }} else {{
      countEl.textContent = `Showing ${{start + 1}}–${{start + showing}} of ${{filteredCount}} (${{total}} total)`;
    }}
  }}
}})();
</script>
<footer class="site-footer">
  <p class="ftc-disclosure">
    <strong>Affiliate Disclosure:</strong> As an Amazon Associate, we earn from qualifying purchases.
    When you buy through our links, we may earn a small commission at no extra cost to you.
    This helps support this free educational project. Thank you! ❤️
  </p>
  <p class="footer-links">
    <a href="about.html">About</a> •
    <a href="guide.html">Usage Guide</a> •
    <a href="https://github.com/adrianwedd/squishmallowdex" target="_blank" rel="noopener">GitHub</a>
  </p>
</footer>
</body>
</html>
"""

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)


def build_html_rows(
    rows: list[dict[str, str | None]],
    session: requests.Session,
    *,
    download_images: bool,
    images_dir: str,
    refresh: bool,
    embed_images: bool = False,
    thumb_size: int = DEFAULT_THUMB_SIZE,
) -> list[dict[str, str | None]]:
    # Convert raw rows into HTML-ready rows (adds <img> and link columns).
    html_rows: list[dict[str, str | None]] = []
    total = len(rows)
    for idx, row in enumerate(rows, 1):
        local_img = None
        img_url = row.get("ImageURL") or ""
        if img_url:
            cached_path = _get_cached_image_path(images_dir, img_url)
            if os.path.exists(cached_path) and not refresh:
                local_img = cached_path
            elif download_images:
                local_img = download_image(session, img_url, images_dir, refresh)

        # Embed as base64 thumbnail if requested
        if embed_images:
            # Try local image first, then fetch from URL
            if idx == 1 or idx % 100 == 0 or idx == total:
                print(f"\r  Embedding images: {idx}/{total}", end="", flush=True)
            img_src = (
                image_to_base64_thumbnail(local_img, session, max_size=thumb_size) if local_img else None
            ) or image_to_base64_thumbnail(img_url, session, max_size=thumb_size) or img_url
        else:
            img_src = local_img or row.get("ImageURL") or ""
        full_img = row.get("ImageURL") or ""
        row_html = dict(row)
        # Make image clickable to open full-size version
        if img_src:
            img_tag = f'<img class="thumb" src="{escape(img_src)}" loading="lazy"/>'
            if full_img:
                row_html["Image"] = f'<a href="{escape(full_img)}" target="_blank" rel="noopener">{img_tag}</a>'
            else:
                row_html["Image"] = img_tag
        else:
            row_html["Image"] = ""
        html_rows.append(row_html)

    if embed_images and total > 0:
        print()  # Newline after progress
    return html_rows


def write_csv(rows: list[dict[str, str | None]], out_path: str) -> None:
    # CSV is "portable": you can open it in spreadsheets or use it in other tools.
    # Write a spreadsheet-friendly CSV with all raw fields.
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "Name",
                "URL",
                "ImageURL",
                "Type",
                "Color",
                "Squad",
                "Size(s)",
                "Collector Number",
                "Year",
                "Bio",
                "Extra",
            ],
            extrasaction="ignore",  # Ignore old fields like Squishdate
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_json(rows: list[dict[str, str | None]], out_path: str) -> None:
    """Export collection as JSON array."""
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)


def read_existing_csv(csv_path: str) -> list[dict[str, str | None]]:
    # If a previous run exists, load it so we can keep building on it.
    if not os.path.exists(csv_path):
        return []
    rows: list[dict[str, str | None]] = []
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))
    return rows


def read_progress(progress_path: str) -> set[str]:
    # The progress file stores one URL per line.
    if not os.path.exists(progress_path):
        return set()
    with open(progress_path, "r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


def append_progress(progress_path: str, url: str) -> None:
    # Append a single URL so we can resume without repeating work.
    with open(progress_path, "a", encoding="utf-8") as f:
        f.write(url + "\n")


def _sync_progress_file(progress_path: str) -> None:
    """Ensure progress file is flushed to disk."""
    if not os.path.exists(progress_path):
        return
    with open(progress_path, "a") as f:
        f.flush()
        os.fsync(f.fileno())


def save_collection(
    rows: list[dict[str, str | None]],
    session: requests.Session,
    *,
    html_path: str,
    csv_path: str,
    images_dir: str,
    download_images: bool,
    refresh: bool,
    embed_images: bool = False,
    dry_run: bool = False,
    thumb_size: int = DEFAULT_THUMB_SIZE,
    json_path: str | None = None,
) -> None:
    """Save the collection to HTML, CSV, and optionally JSON files.

    If dry_run=True, builds the HTML rows (validates logic) but skips writing files.
    """
    html_rows = build_html_rows(
        rows,
        session,
        download_images=download_images and not dry_run,
        images_dir=images_dir,
        refresh=refresh,
        embed_images=embed_images and not dry_run,
        thumb_size=thumb_size,
    )
    if not dry_run:
        render_html(html_rows, html_path, "Squishmallowdex", logo_path=LOGO_PATH, thumb_size=thumb_size)
        write_csv(rows, csv_path)
        if json_path:
            write_json(rows, json_path)
    else:
        log.debug(f"[DRY RUN] Would write HTML to {html_path}")
        log.debug(f"[DRY RUN] Would write CSV to {csv_path}")
        if json_path:
            log.debug(f"[DRY RUN] Would write JSON to {json_path}")


def main() -> None:
    global log

    ap = argparse.ArgumentParser(
        description=(
            "✨ SQUISHMALLOWDEX ✨\n"
            "Build your own searchable Squishmallow database!\n"
            "Like a Pokédex, but for Squishmallows. Works offline too!"
        ),
        epilog=(
            "🌟 QUICK START EXAMPLES 🌟\n"
            "─────────────────────────────────────────────────────────\n"
            "  Catch your first 50 Squishmallows (with images!):\n"
            "    python squishmallowdex.py --limit 50\n"
            "\n"
            "  Faster run (skip image downloads):\n"
            "    python squishmallowdex.py --limit 50 --no-download-images\n"
            "\n"
            "  See downloads and network activity:\n"
            "    python squishmallowdex.py -v\n"
            "\n"
            "  Full debug mode:\n"
            "    python squishmallowdex.py -vv\n"
            "\n"
            "  Just check your collection stats:\n"
            "    python squishmallowdex.py --stats-only\n"
            "\n"
            "💡 TIP: You can stop anytime with Ctrl+C and resume later!\n"
            "        Your progress is saved after every batch.\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # === Collection Options ===
    collect = ap.add_argument_group("✨ Collection Options")
    collect.add_argument(
        "--limit",
        type=int,
        default=0,
        metavar="N",
        help="How many NEW Squishmallows to catch this run (0 = catch 'em all!).",
    )
    collect.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        metavar="N",
        help=f"Save progress every N catches (default: {DEFAULT_BATCH_SIZE}).",
    )
    collect.add_argument(
        "--no-download-images",
        action="store_true",
        help="Skip downloading pictures (faster, uses less space).",
    )
    collect.add_argument(
        "--embed-images",
        action="store_true",
        help="Embed images in HTML as thumbnails (self-contained, ~30-50MB file).",
    )
    collect.add_argument(
        "--thumb-size",
        type=int,
        default=DEFAULT_THUMB_SIZE,
        metavar="PX",
        help=f"Thumbnail size in pixels (default: {DEFAULT_THUMB_SIZE}).",
    )
    collect.add_argument(
        "--stats-only",
        action="store_true",
        help="Just show collection stats, don't download anything new.",
    )
    collect.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate run without writing files (preview what would be collected).",
    )
    collect.add_argument(
        "--source",
        choices=["wiki", "site"],
        default="wiki",
        help="Data source: 'wiki' scrapes the Fandom wiki (default), 'site' fetches from squishmallowdex.com.",
    )

    # === Output Options ===
    output = ap.add_argument_group("📁 Output Files")
    output.add_argument(
        "--out",
        default="squishmallowdex.html",
        metavar="FILE",
        help="HTML file to create (open in browser).",
    )
    output.add_argument(
        "--csv",
        default="squishmallowdex.csv",
        metavar="FILE",
        help="CSV file to create (open in spreadsheet).",
    )
    output.add_argument(
        "--json",
        default=None,
        metavar="FILE",
        help="Export collection as JSON file (optional).",
    )
    output.add_argument(
        "--images-dir",
        default="squish_images",
        metavar="DIR",
        help="Folder for downloaded images.",
    )

    # === Display Options ===
    display = ap.add_argument_group("🎨 Display Options")
    display.add_argument(
        "-v", "--verbose",
        action="count",
        default=0,
        help="Show more details (-v = downloads/skips, -vv = debug).",
    )
    display.add_argument(
        "--no-adventure",
        action="store_true",
        help="Turn off fun facts and tips.",
    )
    display.add_argument(
        "--no-color",
        action="store_true",
        help="Turn off colors (for terminals that don't support them).",
    )
    display.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Minimal output (just errors and final summary).",
    )
    display.add_argument(
        "--log",
        default="squishmallow.log",
        metavar="FILE",
        help="Log file to write all output (default: squishmallow.log).",
    )
    display.add_argument(
        "--phoenix",
        action="store_true",
        help=argparse.SUPPRESS,  # Hidden easter egg!
    )

    # === Advanced Options ===
    advanced = ap.add_argument_group("⚙️  Advanced Options (for power users!)")
    advanced.add_argument(
        "--delay",
        type=float,
        default=DEFAULT_REQUEST_DELAY,
        metavar="SEC",
        help=f"Wait time between downloads (default: {DEFAULT_REQUEST_DELAY}s).",
    )
    advanced.add_argument(
        "--batch-delay",
        type=float,
        default=DEFAULT_BATCH_DELAY,
        metavar="SEC",
        help=f"Extra wait time between batches (default: {DEFAULT_BATCH_DELAY}s).",
    )
    advanced.add_argument(
        "--cache",
        default="cache_html",
        metavar="DIR",
        help="Folder for cached web pages.",
    )
    advanced.add_argument(
        "--progress-file",
        default="progress_urls.txt",
        metavar="FILE",
        help="File that tracks which pages we've visited.",
    )
    advanced.add_argument(
        "--refresh",
        action="store_true",
        help="Re-download everything (ignores cache).",
    )
    advanced.add_argument(
        "--rebuild",
        action="store_true",
        help="Rebuild collection from cache (re-process all cached pages).",
    )

    args = ap.parse_args()

    # --dry-run and --stats-only are mutually exclusive
    if args.dry_run and args.stats_only:
        ap.error("--dry-run and --stats-only cannot be used together")

    # --thumb-size must be positive
    if args.thumb_size < 1:
        ap.error("--thumb-size must be a positive integer (minimum 1)")

    # Set up the adventure logger with user's preferences
    log = AdventureLog(
        verbose=0 if args.quiet else args.verbose,
        adventure_mode=not args.no_adventure,
        use_color=not args.no_color and sys.stdout.isatty(),
        quiet=args.quiet,
        show_phoenix_art=args.phoenix,
        start_time=time.time(),
        log_file=args.log,
    )

    session = None
    try:
        # Open log file for this session
        log.open_log()

        # Show the awesome banner!
        log.banner()

        # Dry-run mode indicator
        if args.dry_run:
            log.warn("🔍 DRY RUN MODE - No files will be written")

        # A Session keeps connections open between requests (faster + nicer).
        session = requests.Session()

        # Handle --rebuild: clear progress to re-process all cached pages
        if args.rebuild:
            log.info("Rebuild mode: clearing progress files to re-process from cache...", 0)
            skipped_file = skipped_file_path(args.progress_file)
            for f in [args.progress_file, skipped_file]:
                if os.path.exists(f):
                    os.remove(f)

        # Load any existing CSV so we can resume without losing progress.
        # In rebuild mode, we start fresh.
        rows: list[dict[str, str | None]] = [] if args.rebuild else read_existing_csv(args.csv)
        existing_count = len(rows)

        # Track stats for existing rows
        for row in rows:
            log.track_squish(row)

        # ─────────────────────────────────────────────────────────────────────────
        # STATS-ONLY MODE: Just show what we have and exit
        # ─────────────────────────────────────────────────────────────────────────
        if args.stats_only:
            log.step("Checking your collection...")
            if not rows:
                log.warn("No Squishmallows collected yet! Run without --stats-only to start catching.")
            else:
                log.info(f"Found {len(rows)} Squishmallows in your collection!")
                # Regenerate HTML (especially useful with --embed-images)
                save_collection(
                    rows, session,
                    html_path=args.out, csv_path=args.csv,
                    images_dir=args.images_dir,
                    download_images=not args.no_download_images,
                    refresh=args.refresh,
                    embed_images=args.embed_images,
                    dry_run=args.dry_run,
                    thumb_size=args.thumb_size,
                    json_path=args.json,
                )
                log.summary(len(rows), existing_count, csv_path=args.csv, html_path=args.out)
            return

        # ─────────────────────────────────────────────────────────────────────────
        # COLLECTION MODE: Let's catch some Squishmallows!
        # ─────────────────────────────────────────────────────────────────────────

        if args.source == "site":
            # Fast path: pull all data from the deployed squishmallowdex.com in one request.
            site_rows = fetch_from_site(session)
            if site_rows:
                rows = site_rows
                save_collection(
                    rows, session,
                    html_path=args.out, csv_path=args.csv,
                    images_dir=args.images_dir,
                    download_images=not args.no_download_images,
                    refresh=args.refresh,
                    embed_images=args.embed_images,
                    dry_run=args.dry_run,
                    thumb_size=args.thumb_size,
                    json_path=args.json,
                )
                log.summary(len(rows), existing_count, csv_path=args.csv, html_path=args.out)
            else:
                log.warn("No data retrieved from site. Nothing saved.")
            return

        log.step("Step 1: Fetching the Master List of all Squishmallows...")

        if log.adventure_mode:
            log.info("The Master List is like a treasure map - it shows us where all the Squishmallows are!", 0)

        master_html = fetch(
            MASTER_LIST, session, cache_dir=args.cache, refresh=args.refresh, delay=args.delay
        )
        urls = extract_master_list_urls(master_html)

        log.info(f"Found {len(urls)} potential Squishmallow pages to explore!", 0)

        # The progress file tracks which URLs we've already finished so we can skip them.
        processed_urls = read_progress(args.progress_file)
        skipped_file = skipped_file_path(args.progress_file)
        skipped_urls = read_progress(skipped_file)

        # If we have prior rows but no progress file, rebuild progress from CSV.
        if rows and not processed_urls:
            log.info("Rebuilding progress from existing CSV...", 1)
            processed_urls = {r.get("URL", "") for r in rows if r.get("URL")}
            # Write all at once instead of appending one by one (avoids duplicates)
            if not args.dry_run:
                with open(args.progress_file, "w", encoding="utf-8") as f:
                    for url in sorted(processed_urls):
                        f.write(url + "\n")

        if existing_count > 0:
            log.info(f"Resuming collection! You already have {existing_count} Squishmallows.", 0)

        log.step("Step 2: Hunting for Squishmallows!")

        if log.adventure_mode:
            log.info("Each page we visit might contain a new friend for your collection!", 0)

        collected_in_batch = 0
        batch_number = 1
        limit = args.limit if args.limit and args.limit > 0 else None

        # Count how many we need to process
        urls_to_process = [u for u in urls if u not in processed_urls and u not in skipped_urls]
        if limit:
            # Limit means "process this many more", not "have this many total"
            remaining_to_catch = min(limit, len(urls_to_process))
        else:
            remaining_to_catch = len(urls_to_process)

        if remaining_to_catch <= 0:
            log.info("Your collection is already complete! Nothing new to catch.", 0)
        else:
            log.info(f"About to hunt for up to {remaining_to_catch} new Squishmallows...", 0)

        for u in urls:
            # Skip already processed or known non-character pages
            if u in processed_urls or u in skipped_urls:
                continue
            if limit is not None and log.new_catches >= limit:
                log.info(f"Reached your limit of {limit} new Squishmallows!", 0)
                break

            try:
                # In dry-run mode, skip fetching entirely (no network, no cache writes)
                if args.dry_run:
                    log.info(f"[DRY RUN] Would fetch: {u.split('/')[-1]}", 0)
                    log.new_catches += 1
                    collected_in_batch += 1
                    if collected_in_batch >= args.batch_size:
                        log.info(f"[DRY RUN] Would save batch {batch_number}", 0)
                        batch_number += 1
                        collected_in_batch = 0
                    continue

                # Fetch and parse a single page.
                page_html = fetch(
                    u, session, cache_dir=args.cache, refresh=args.refresh, delay=args.delay
                )
                row, info = parse_squish_page(page_html, u)

                # Skip pages that look like lists or meta pages.
                if not is_character_page(row.get("Name"), info):
                    log.skip(row.get("Name") or u.split("/")[-1], "not a character page")
                    # FIX: Record skipped URLs so we don't re-parse them next time
                    skipped_urls.add(u)
                    if not args.dry_run:
                        append_progress(skipped_file, u)
                    continue

                rows.append(row)
                log.track_squish(row)
                processed_urls.add(u)
                if not args.dry_run:
                    append_progress(args.progress_file, u)
                collected_in_batch += 1

                # Celebrate the catch!
                log.catch(row.get("Name") or "Unknown", len(rows))

                # When we hit a batch boundary, write outputs and pause briefly.
                if collected_in_batch >= args.batch_size:
                    log.step(f"Batch {batch_number} complete! Saving your progress...")
                    save_collection(
                        rows, session,
                        html_path=args.out, csv_path=args.csv,
                        images_dir=args.images_dir,
                        download_images=not args.no_download_images,
                        refresh=args.refresh,
                        embed_images=args.embed_images,
                        dry_run=args.dry_run,
                        thumb_size=args.thumb_size,
                        json_path=args.json,
                    )
                    if not args.dry_run:
                        _sync_progress_file(args.progress_file)
                        _sync_progress_file(skipped_file)
                    log.info(f"Saved! {len(rows)} total Squishmallows in {args.out}", 0)

                    if log.adventure_mode:
                        log.info("Taking a short break to be nice to the server... 🍵", 0)

                    batch_number += 1
                    collected_in_batch = 0
                    time.sleep(args.batch_delay)

            except KeyboardInterrupt:
                log.warn("Stopping early! Don't worry, your progress is saved.")
                break
            except Exception as exc:
                log.error(f"Problem with {u.split('/')[-1]}: {exc}")
                log.debug(f"Full error: {type(exc).__name__}: {exc}")

        # Final write for any leftover rows (last partial batch).
        if args.dry_run:
            log.step("Step 3: Dry run complete! (no files written)")
        else:
            log.step("Step 3: Saving your Squishmallowdex!")

        save_collection(
            rows, session,
            html_path=args.out, csv_path=args.csv,
            images_dir=args.images_dir,
            download_images=not args.no_download_images,
            refresh=args.refresh,
            embed_images=args.embed_images,
            dry_run=args.dry_run,
            thumb_size=args.thumb_size,
            json_path=args.json,
        )
        if not args.dry_run:
            _sync_progress_file(args.progress_file)
            _sync_progress_file(skipped_file)
            log.debug(f"Wrote HTML to {args.out}")
            log.debug(f"Wrote CSV to {args.csv}")
            if args.json:
                log.debug(f"Wrote JSON to {args.json}")

        # Show the epic summary!
        log.summary(len(rows), existing_count, total_available=len(urls),
                    skipped_count=len(skipped_urls), csv_path=args.csv, html_path=args.out,
                    dry_run=args.dry_run)
    finally:
        if session is not None:
            session.close()
        log.close_log()


if __name__ == "__main__":
    main()
