# Squishmallowdex Roadmap

## Current Release

### v1.2.0 (Released)
- **Card view** — toggle between table and card layouts, persisted across reloads
- **Loading spinner** with deferred rendering (no flash of partial cards)
- **Shared filter/sort pipeline** — search, favorites-only, owned-only work in both views
- **Compact card density** toggle, persisted to localStorage
- **Sort fix** — missing Collector # and Year values now sort last in both ascending and descending order
- **rAF race guard** — rapid view toggles no longer produce stale renders
- **Search debounce** (130ms) for smooth typing on large datasets
- **Accessibility** — `:focus-visible` styles, keyboard-navigable sort headers, descriptive aria-labels on all card actions
- **Reduced-motion support** — card hover transitions and view fade gated on `prefers-reduced-motion`
- **Mobile chip priority** — Size and Squad chips hidden on narrow screens to reduce clutter
- Amazon affiliate buy buttons and FTC disclosure in footer

### v1.1.0 (Released)
- Dry-run mode (`--dry-run`)
- Thumbnail size control (`--thumb-size`)
- XSS prevention for all text columns
- Responsive thumbnail scaling
- Kid-friendly documentation
- Windows `setup.bat`

---

## Upcoming Releases

### v1.3.0 - Self-Upgrade
One-command upgrades that preserve your collection.

```bash
python3 squishmallowdex.py --upgrade
```

**Branch:** `v1.3.0`

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
