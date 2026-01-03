# Installation Guide

## Mac / Linux

Python is already installed! Just run:

```bash
./setup.sh
```

This checks Python and installs the required packages.

---

## Windows

### Step 1: Install Python

1. Go to **https://www.python.org/downloads/**
2. Click the big yellow **"Download Python"** button
3. Run the installer
4. **IMPORTANT:** Check **"Add Python to PATH"** at the bottom!
5. Click "Install Now"

### Step 2: Install Dependencies

Open Command Prompt (Start → type "cmd" → Enter), go to the folder, and run:

```
pip3 install requests beautifulsoup4
```

---

## Troubleshooting

### "python3 is not recognized" or "command not found"
- Python isn't installed correctly
- On Windows, make sure you checked "Add Python to PATH" during installation

### "No module named requests" or "No module named bs4"
- Run: `pip3 install requests beautifulsoup4`

### The pictures aren't showing
- The first run downloads pictures, which takes time
- Make sure you're connected to the internet

### Something else went wrong
- Try running with `--rebuild` to start fresh:
  ```
  python3 squishmallowdex.py --rebuild --limit 50
  ```

### Still stuck?
- Check the `squishmallow.log` file for error messages
