# CLAUDE.md — Squishmallowdex Project Guide

## Pipeline: generate → deploy → commit → push

**Every change to `squishmallowdex.py` that affects HTML output requires this sequence:**

```bash
python3 squishmallowdex.py --no-download   # regenerate squishmallowdex.html
python3 deploy.py                           # sync to docs/ (live site)
git add squishmallowdex.html docs/squishmallowdex.html
git commit -m "..."
git push
```

Skipping `deploy.py` leaves the live site (squishmallowdex.com) on the old version.
`docs/` is what Cloudflare Pages serves. `squishmallowdex.html` (root) is the generated source.

---

## Key files

| File | Purpose |
|------|---------|
| `squishmallowdex.py` | Single source of truth — scraper, HTML generator, CLI |
| `squishmallowdex.html` | Generated output; committed to git, served from root |
| `squishmallowdex.csv` | Data store; gitignored (local only) |
| `deploy.py` | Copies root HTML + images → `docs/` for Cloudflare Pages |
| `docs/squishmallowdex.html` | Live site file; must be kept in sync with root |
| `cloudflare-build.sh` | CI build script run by Cloudflare Pages |
| `squish_images/` | Downloaded thumbnails; gitignored |
| `cache_html/` | Cached wiki pages; gitignored |

---

## Architecture of `squishmallowdex.py`

```
_render_css()          → all CSS (inline in <style>)
_table_config()        → column definitions (name, hidden, sortable)
_build_table_header()  → <thead> HTML
_build_table_body()    → <tbody> HTML (all rows)
build_html_rows()      → enriches raw CSV rows with <img> tags
render_html()          → assembles the complete HTML page
```

The HTML template is an f-string inside `render_html()`. JavaScript is also inline.

Column indices are hard-coded in JS (`cells[N]`). If columns change in `_table_config()`, update the JS `extractRowModel` indices and `sortableCols` map accordingly.

---

## CSS/JS conventions

- All styles live in `_render_css()` as a Python f-string (use `{{` / `}}` to escape CSS braces).
- View modes are controlled by body classes: `mode-table` / `mode-cards`.
  - `mode-table` hides `.card-wrap` and shows `.pagination`
  - `mode-cards` hides `.table-wrap` and `.pagination`
- `<body class="mode-table">` in the HTML template prevents flash before JS runs.
- Card view builds all cards from `rowModels` (extracted from the DOM once on load).
- Pagination only applies in table mode.

---

## CLI flags to know

```bash
--no-download          # Regenerate HTML from existing CSV without hitting the network
--source site          # Fetch data from squishmallowdex.com instead of scraping the wiki
--source wiki          # Default: scrape the Fandom wiki page by page
--stats-only           # Regenerate HTML/CSV without fetching new data
--embed-images         # Embed images as base64 (self-contained file, ~30–50 MB)
--refresh              # Ignore cache, re-download everything
--rebuild              # Re-process all cached pages from scratch
```

---

## Gotchas

- `squishmallowdex.csv` is gitignored — it's local data only.
- `squishmallowdex.html` (root) is **not** gitignored — commit it alongside `docs/squishmallowdex.html`.
- The `--no-download` flag reuses existing local images. Use it for HTML-only changes to avoid slow re-fetches.
- `deploy.py` also copies `squish_images/` — if images changed locally, run it to sync those too.
- The `--source site` scraper parses `<td data-col="N">` from the live HTML table. If columns are added/removed, update `col_map` in `fetch_from_site()`.
