# Card View Implementation Plan (Table + Card Toggle)

## Objective
Add a **card view** to Squishmallowdex while preserving the current table experience as the default and keeping all existing behavior (search, favorites, ownership, sorting, column preferences) intact.

## Current State (Baseline)
- UI is currently table-first (`#dex` with `tbody > tr` rows).
- Search/filtering/favorite/owned logic is centralized in one script and directly manipulates table rows via `row.style.display`.
- Column visibility is table-specific and persisted with `localStorage` key `squishdex-cols`.
- Favorites and owned states are persisted with `squishdex-fav` and `squishdex-own`.

## Implementation Strategy

### 1) Add a view-mode control in header
- Add a compact toggle next to existing controls:
  - `Table` (default)
  - `Cards`
- Persist selection in localStorage under a new key, e.g. `squishdex-view`.
- On load, apply saved view mode before first render for minimal layout shift.

### 2) Introduce a dedicated card container
- Add a sibling container to `.table-wrap`:
  - `#cardView` wrapping a responsive grid (`.card-grid`).
- Reuse existing row data by transforming each `<tr>` into a card model once at initialization.
- Each card should include:
  - image
  - name + type
  - color, year, size, collector number (when present)
  - bio snippet (truncated)
  - wiki link
  - existing favorite heart, owned checkbox, and buy button

### 3) Unify filtering state across both views
- Refactor filtering to compute `visibleIds` once from:
  - search query
  - favorites-only toggle
  - owned-only toggle
- Apply visibility to:
  - table rows (`display: none`)
  - cards (`display: none` or hidden class)
- Keep count logic based on the same `visibleIds` set so results match in both views.

### 4) Define sorting behavior for card mode
- Keep existing sortable headers for table mode.
- In card mode, add a lightweight sort control (dropdown) with key fields:
  - Name (A–Z / Z–A)
  - Type (A–Z / Z–A)
  - Year (newest/oldest)
  - Collector Number (high/low)
- Reuse the same compare function for both table ordering and card ordering to avoid drift.

### 5) Handle column picker behavior cleanly
- Keep column picker active only in table mode.
- In card mode:
  - disable/hide the column picker button, or
  - leave it visible but disabled with tooltip text "Table view only".
- Continue persisting `squishdex-cols` unchanged.

### 6) Accessibility + responsive UX
- View toggle should be keyboard-operable and expose `aria-pressed` state.
- Ensure card actions (heart, own checkbox, buy link, wiki link) remain focusable and screen-reader-labeled.
- Add responsive grid breakpoints:
  - 1 column mobile
  - 2 columns tablet
  - 3–5 columns desktop depending on width

## Data/Code Refactor Plan

### Extract row data helper
Create helper utilities in the current inline script:
- `extractRowModel(tr)` → normalized object `{ id, name, type, year, ... }`
- `getFilteredIds(state)` → list/set of matching ids
- `sortModels(models, sortKey, sortDir)`

### Rendering helpers
- `renderCardView(models)` for initial card DOM creation.
- `applyViewMode(mode)` toggles visibility between table and card containers.
- `applyFiltersAndSort()` becomes the single orchestration entry point called by search/filter/sort/view events.

## Performance Notes
- Build card DOM once and reuse nodes; avoid full rebuild on each keystroke.
- Debounce search input slightly (optional 100–150ms) for smoother typing on lower-end devices.
- Keep lazy-loading on images in cards (`loading="lazy"`).

## QA / Validation Checklist
1. Default load remains table view.
2. Toggling to card view preserves current search/filter state.
3. Favorites and owned changes sync instantly in both views.
4. Count text remains correct while switching views.
5. Reload persists selected view mode.
6. Table sorting still works exactly as before.
7. Card sorting works and does not affect filter correctness.
8. Mobile layout remains readable and scroll-free horizontally.

## Rollout Plan

### Phase 1 (MVP)
- Add view toggle + card grid rendering.
- Share existing search/favorite/owned filtering.
- Persist view mode.

### Phase 2 (Parity)
- Add card-mode sorting.
- Tighten accessibility labels and keyboard behavior.
- Polish responsive card density and spacing.

### Phase 3 (Polish)
- Optional animation between modes.
- Optional "compact card" option for power users.

## Risks and Mitigations
- **Risk:** Logic divergence between table and cards.
  - **Mitigation:** single filter/sort state and shared helper functions.
- **Risk:** Large DOM cost with thousands of cards.
  - **Mitigation:** one-time render + node reuse; defer virtualization unless needed.
- **Risk:** Regression to existing table controls.
  - **Mitigation:** preserve current table path and add targeted smoke checks for existing actions.

## Estimated Effort
- Phase 1: 1–2 days
- Phase 2: 0.5–1 day
- Phase 3: 0.5 day

**Total:** ~2–3.5 days of implementation + validation.
