# Squishmallowdex

**Your very own Squishmallow collection tracker - like a Pokédex, but for Squishmallows!**

This program downloads information about every Squishmallow from the internet and saves it to your computer. Then you can search and browse your collection even without internet!

---

## What You Need

Before you start, make sure you have:

1. **A computer** (Mac, Windows, or Linux)
2. **Python 3** installed (ask a grown-up if you're not sure)
3. **Terminal** - this is where you type commands:
   - On Mac: Open "Terminal" from Applications > Utilities
   - On Windows: Open "Command Prompt" or "PowerShell"

---

## Getting Started

### Step 1: Open Terminal

Find and open your terminal program. You'll see a window where you can type commands.

### Step 2: Go to the folder

Type this command and press Enter:

```
cd /path/to/squishmallows
```

(Replace `/path/to/squishmallows` with wherever you saved this folder!)

**Tip:** You can drag the folder onto the terminal window and it will type the path for you!

### Step 3: Catch your first Squishmallows!

Type this command and press Enter:

```
python3 squishmallowdex.py --limit 50
```

This will catch your first 50 Squishmallows! Watch as they get added to your collection!

---

## Viewing Your Collection

After running the script, you'll have two new files:

| File | What it is |
|------|------------|
| `squishmallowdex.html` | Open this in a web browser to see your collection with pictures! |
| `squishmallowdex.csv` | Open this in Excel or Google Sheets to see all the data! |

**To open the HTML file:** Double-click it, or drag it into your web browser (Chrome, Safari, Firefox, etc.)

---

## Cool Commands to Try

### Catch more Squishmallows
```
python3 squishmallowdex.py --limit 100
```

### Catch ALL the Squishmallows (this takes a while!)
```
python3 squishmallowdex.py --limit 0
```

### See your collection stats
```
python3 squishmallowdex.py --stats-only
```

### Faster mode (skip downloading pictures)
```
python3 squishmallowdex.py --limit 50 --no-download-images
```

### Quiet mode (less messages)
```
python3 squishmallowdex.py --limit 50 --quiet
```

### See everything that's happening
```
python3 squishmallowdex.py --limit 10 -v
```

### Super detailed mode (for debugging)
```
python3 squishmallowdex.py --limit 10 -vv
```

### Rebuild your whole collection from scratch
```
python3 squishmallowdex.py --rebuild --limit 500
```

---

## Tips & Tricks

- **You can stop anytime!** Press `Ctrl+C` to stop. Your progress is saved!

- **Resume later:** Just run the command again and it will continue where you left off.

- **Slow internet?** The script is polite and waits between downloads so it doesn't overwhelm the website.

- **Something went wrong?** Try running with `--rebuild` to start fresh.

- **Want to see the log?** Check `squishmallow.log` for a record of everything that happened.

---

## Using Your Squishmallowdex

Once you open `squishmallowdex.html` in a browser:

- **Search:** Type in the search box to find Squishmallows by name, type, or color
- **Sort:** Click on column headers (Name, Type, Color, Year) to sort
- **Show/Hide columns:** Click the "Columns" button to choose what to show
- **See full picture:** Click on any Squishmallow's picture to see the big version
- **Visit wiki:** Click "wiki" to see that Squishmallow's page online

---

## What's in this folder?

| File/Folder | What it is |
|-------------|------------|
| `squishmallowdex.py` | The main program |
| `squishmallowdex.html` | Your collection (open in browser) |
| `squishmallowdex.csv` | Your collection (open in spreadsheet) |
| `squishmallowdex.png` | The logo |
| `squish_images/` | Downloaded pictures of your Squishmallows |
| `cache_html/` | Saved web pages (makes re-runs fast!) |
| `progress_urls.txt` | Keeps track of which pages we've visited |
| `squishmallow.log` | A log of everything that happened |

---

## Need Help?

- **See all options:** `python3 squishmallowdex.py --help`
- **Ask a grown-up** if you get stuck!

---

## Have Fun!

Gotta Squish 'Em All!

---

*Made with love for young collectors who want to learn coding too!*
