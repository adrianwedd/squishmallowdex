# Squishmallowdex

![Squishmallowdex Logo](squishmallowdex.png)

**Your very own Squishmallow collection tracker - like a Pokédex, but for Squishmallows!**

This program downloads information about every Squishmallow from the internet and saves it to your computer. Then you can search and browse your collection even without internet!

---

## Quick Start (Mac / Linux)

1. **Download** this folder to your computer
2. **Open Terminal** (Mac: Spotlight → type "Terminal" → Enter)
3. **Go to the folder:** Type `cd ` then drag the folder onto Terminal and press Enter
4. **Run setup:** `./setup.sh`
5. **Catch Squishmallows:** `python3 squishmallowdex.py --limit 50`

That's it! Watch as Squishmallows get added to your collection!

---

## Quick Start (Windows)

### Step 1: Install Python

1. Go to **https://www.python.org/downloads/**
2. Click the big yellow **"Download Python"** button
3. Run the installer
4. **IMPORTANT:** Check **"Add Python to PATH"** at the bottom!
5. Click "Install Now"

### Step 2: Download and Run

1. **Download** this folder to your computer
2. **Open Command Prompt** (Start → type "cmd" → Enter)
3. **Go to the folder:** Type `cd ` then drag the folder onto the window and press Enter
4. **Install helpers:** `pip3 install requests beautifulsoup4`
5. **Catch Squishmallows:** `python3 squishmallowdex.py --limit 50`

Watch as Squishmallows get added to your collection!

---

## Viewing Your Collection

After the program finishes, look in your Squishmallowdex folder. You'll see a new file:

**`squishmallowdex.html`** - This is your collection!

**To open it:**
- **Double-click** on the file, OR
- **Drag it** into Chrome, Safari, Firefox, or any web browser

You'll see a beautiful searchable table with all your Squishmallows!

### What you can do:
- **Search** - Type in the search box to find Squishmallows by name, color, or type
- **Sort** - Click on any column header to sort
- **Favourite** - Click the heart to mark your favourites
- **Own** - Check the box for Squishmallows you actually own!
- **Filter** - Click "Favourites" or "I Own" to show only those

---

## Catching More Squishmallows

Want more? Just run the command again! Open Terminal, go to the folder (Step 3), and try:

### Catch 100 more:
```
python3 squishmallowdex.py --limit 100
```

### Catch ALL of them (this takes a long time!):
```
python3 squishmallowdex.py --limit 0
```

### Just see your stats:
```
python3 squishmallowdex.py --stats-only
```

---

## Stopping and Resuming

- **To stop:** Press **Ctrl+C** (hold the Ctrl key and press C)
- **To resume:** Just run the same command again - it remembers where you were!

Your progress is saved automatically!

---

## Troubleshooting

### "python3 is not recognized" or "command not found"
- Python isn't installed correctly. Go back to "Installing Python" above
- On Windows, make sure you checked "Add Python to PATH" during installation

### "No module named requests" or "No module named bs4"
- Run this command: `pip3 install requests beautifulsoup4`

### The pictures aren't showing
- The first run downloads pictures, which takes time
- Make sure you're connected to the internet

### Something else went wrong
- Try running with `--rebuild` to start fresh:
  ```
  python3 squishmallowdex.py --rebuild --limit 50
  ```

### Still stuck?
- Ask a grown-up for help!
- Check the `squishmallow.log` file for error messages

---

## Tips & Tricks

- **Works offline!** Once downloaded, you can view your collection without internet
- **Add to phone!** Open the HTML file on your phone and "Add to Home Screen" for an app-like experience
- **Slow internet?** The program waits between downloads to be polite to the website

---

## Contributing

![Squishy](squishy-readme.png)

Found a bug? Have an idea? Contributions are welcome!

---

## Have Fun!

**Gotta Squish 'Em All!**

---

*Made with love for young collectors who want to learn coding too!*
