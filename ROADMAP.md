# Squishmallowdex Roadmap

## Current Release

### v1.1.0 (Released)
- Dry-run mode (`--dry-run`)
- Thumbnail size control (`--thumb-size`)
- XSS prevention for all text columns
- Responsive thumbnail scaling
- Kid-friendly documentation
- Windows `setup.bat`

---

## Upcoming Releases

### v1.2.0 - Self-Upgrade
One-command upgrades that preserve your collection.

```bash
python3 squishmallowdex.py --upgrade
```

**Features:**
- `--version` - Show current version
- `--check-update` - Check for newer releases
- `--upgrade` - Download and install latest version
- `--list-backups` - Show available backups
- `--restore` - Roll back to a previous backup

**How it works:**
1. Checks GitHub for new releases
2. Shows what's changed
3. Backs up your collection (HTML, CSV, cache)
4. Downloads and installs the update
5. Runs any needed migrations
6. Verifies everything works (or rolls back)

**Branch:** `v1.2.0`

---

## Ideas for Future Releases

- **Wishlist mode** - Track Squishmallows you want
- **Collection sharing** - Export/import collections with friends
- **Price tracking** - Optional integration with price data
- **Custom tags** - Add your own labels to Squishmallows
- **Photo upload** - Add photos of your actual collection
- **Multi-language** - Translate the interface

---

## Contributing

Have an idea? Open an issue or PR!
