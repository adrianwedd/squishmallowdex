# Usage Guide

## Catching Squishmallows

Open Terminal, go to the folder, and run:

```bash
# Catch 50 Squishmallows
python3 squishmallowdex.py --limit 50

# Catch 100
python3 squishmallowdex.py --limit 100

# Catch ALL of them (takes a long time!)
python3 squishmallowdex.py --limit 0

# Just see your stats
python3 squishmallowdex.py --stats-only
```

---

## Viewing Your Collection

After running, open **squishmallowdex.html** in any browser.

### Features:
- **Search** - Find by name, color, or type
- **Sort** - Click any column header
- **Favourite** - Click the heart ❤️
- **Own** - Check the box for ones you have
- **Filter** - Show only favourites or owned

---

## Stopping and Resuming

- **To stop:** Press `Ctrl+C`
- **To resume:** Run the same command again - it remembers where you were!

Progress is saved automatically.

---

## Starting Fresh

To rebuild from scratch:

```bash
python3 squishmallowdex.py --rebuild --limit 50
```

---

## Portable Mode (Self-Contained HTML)

Want a single file with all images built-in? Use `--embed-images`:

```bash
# After catching some Squishmallows, create portable version
python3 squishmallowdex.py --stats-only --embed-images
```

This creates a ~6-30MB HTML file (depending on collection size) with all images embedded as thumbnails. Perfect for:
- Sharing your collection with friends
- Viewing on devices without internet
- Keeping everything in one file

---

## Tips

- **Works offline!** View your collection without internet
- **Add to phone!** Open the HTML file and "Add to Home Screen"
- **Slow internet?** The program waits between downloads to be polite
