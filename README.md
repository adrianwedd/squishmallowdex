# Squishmallowdex

![Squishmallowdex Logo](squishmallowdex.png)

**Your very own Squishmallow collection tracker - like a Pokédex, but for Squishmallows!**

This program downloads information about every Squishmallow from the internet and saves it to your computer. Then you can search and browse your collection even without internet!

---

## Before You Start (One-Time Setup)

You need to install **Python** on your computer first. Python is a programming language - it's what makes this program work!

### Installing Python

#### On Mac:
1. Open **Safari** (or any web browser)
2. Go to: **https://www.python.org/downloads/**
3. Click the big yellow **"Download Python"** button
4. When it downloads, double-click the file to install it
5. Click through the installer (just keep clicking "Continue" and "Agree")
6. Done! Python is now installed

#### On Windows:
1. Open your web browser
2. Go to: **https://www.python.org/downloads/**
3. Click the big yellow **"Download Python"** button
4. When it downloads, double-click the file
5. **IMPORTANT:** Check the box that says **"Add Python to PATH"** at the bottom!
6. Click "Install Now"
7. Done! Python is now installed

---

## How to Run Squishmallowdex

### Step 1: Download this folder

If you haven't already, download this whole folder to your computer. Remember where you saved it! (For example: your Desktop, or your Downloads folder)

### Step 2: Open the Terminal

The Terminal is a special window where you can type commands to your computer. Don't worry - it's not scary!

#### On Mac:
1. Click the **magnifying glass** in the top-right corner of your screen (it's called Spotlight)
2. Type: **Terminal**
3. Press **Enter** (or click on Terminal when it appears)
4. A white or black window with text will open - that's Terminal!

#### On Windows:
1. Click the **Start** button (Windows icon in the bottom-left)
2. Type: **cmd**
3. Click on **"Command Prompt"** when it appears
4. A black window with text will open - that's your terminal!

### Step 3: Go to the Squishmallowdex folder

Now you need to tell the terminal where the Squishmallowdex folder is.

**The Easy Way (Recommended!):**
1. Type `cd ` (that's the letters **c** and **d**, then a **space**) - don't press Enter yet!
2. Now **drag the Squishmallowdex folder** from Finder/File Explorer and **drop it onto the terminal window**
3. The folder path will magically appear!
4. Now press **Enter**

**Example of what it might look like:**
```
cd /Users/yourname/Desktop/squishmallows
```

### Step 4: Install the required helpers

The first time you run this, you need to install two helper programs. Copy and paste this command, then press Enter:

```
pip3 install requests beautifulsoup4
```

You only need to do this once!

### Step 5: Catch your first Squishmallows!

Now for the fun part! Type this command and press Enter:

```
python3 squishmallowdex.py --limit 50
```

Watch as 50 Squishmallows get added to your collection! You'll see fun messages as each one is caught.

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

## Have Fun!

**Gotta Squish 'Em All!**

---

*Made with love for young collectors who want to learn coding too!*
