# Card View Close-Out Sprint Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Close every open checkbox in issue #12 (card view parity QA, polish, and regression validation) and close stale issues #6 and #7.

**Architecture:** Single-file app — all work is in `docs/squishmallowdex.html`. No build step, no test framework; verification is manual QA in browser + DevTools. Each phase is one commit.

**Tech Stack:** Vanilla JS, CSS, HTML. LocalStorage for persistence. No dependencies.

---

## Phase exit rule

Before committing each phase: confirm no known regressions introduced in any previously completed phase.

---

## Phase 1 — Functional QA + Persistence

**File:** `docs/squishmallowdex.html`

**Goal:** Verify and fix baseline behavior and all localStorage keys.

### Task 1.1: Verify LS_KEYS map

**Step 1: Read the LS_KEYS constant**

Open `docs/squishmallowdex.html`, search for `LS_KEYS`. Confirm it contains:
- `view` → `'squishdex-view'`
- `cardSort` → `'squishdex-card-sort'`
- `cols` → `'squishdex-cols'`
- `fav`, `own`, `buyClicks`

If any key is missing, add it now.

**Step 2: Verify view init reads LS_KEYS.view**

Find `viewMode` initialisation near top of IIFE. It should read:
```js
const viewMode = localStorage.getItem(LS_KEYS.view) || 'table';
```
If it reads a bare string `'squishdex-view'` instead of `LS_KEYS.view`, fix it.

**Step 3: Verify restoreCardSort reads LS_KEYS.cardSort**

Find `restoreCardSort()`. Confirm:
```js
applyCardSortSelection(localStorage.getItem(LS_KEYS.cardSort) || 'table');
```

**Step 4: Verify column visibility reads LS_KEYS.cols**

Find `visibility` initialisation. Confirm it reads `LS_KEYS.cols`.

### Task 1.2: Manual QA — first load (no prior storage)

**Step 1: Clear localStorage in DevTools**

Open browser DevTools → Application → Storage → Clear site data.

**Step 2: Reload page**

Expected: table view is active, `aria-pressed="true"` on Table button, Cards button `aria-pressed="false"`.

**Step 3: Confirm column picker is enabled**

Click the Columns button. Dropdown should open.

**Step 4: Confirm result count**

Count displayed should equal total number of Squishmallows.

### Task 1.3: Manual QA — filter/sort state preserved on view switch

**Step 1: Enter a search term (e.g. "cat")**

Result count should drop.

**Step 2: Switch to Cards view**

Expected: same filtered result count in card view. Search text still in input. No reset.

**Step 3: Switch back to Table view**

Expected: same search term, same count, sort column unchanged.

**Step 4: Enable Favorites-only filter, switch views**

Expected: filter remains active in both directions.

### Task 1.4: Manual QA — column picker disabled in card mode

**Step 1: Switch to Cards view**

Click Columns button. Expected: nothing happens (button is disabled).

**Step 2: Switch back to Table view**

Click Columns button. Expected: dropdown opens normally.

### Task 1.5: Manual QA — reload persistence

**Step 1: Switch to Cards view, set card sort to "Name (Z→A)"**

**Step 2: Hide a table column (e.g. Squad) in table view first, then switch to cards, then reload**

After reload:
- View mode should be Cards ✓
- Card sort should be "Name (Z→A)" ✓
- Table column visibility should be restored after switching back to Table ✓

### Task 1.6: Fix any issues found

Fix whatever failed in Tasks 1.2–1.5. Common fixes:
- `viewMode` not persisted on init call (already handled by `applyViewMode` writing `LS_KEYS.view`)
- Column picker `disabled` not reset when switching table→cards→table (check `applyViewMode` else branch)

### Task 1.7: Commit Phase 1

```bash
git add docs/squishmallowdex.html
git commit -m "fix(phase1): functional QA and persistence verification

Verified and fixed: default table on first load, filter/sort
state preserved across view switches, column picker disabled
in card mode, reload persistence for view/cardSort/cols keys."
```

Post a comment on #12 ticking:
- [ ] Table view remains default on first load
- [ ] Switching between views preserves active search/filter/sort state
- [ ] Result count matches visible items in both views under all filters
- [ ] Column picker does not break when toggling back/forth
- [ ] View mode persists after reload (squishdex-view)
- [ ] Search by name returns same count in table and cards
- [ ] Clearing search restores full count
- [ ] Table and Cards buttons expose correct pressed state (aria-pressed) ← baseline a11y

---

## Phase 2 — State Sync

**File:** `docs/squishmallowdex.html`

**Goal:** Favorites and ownership sync instantly across both views.

### Task 2.1: Understand syncSelectionState

Read `syncSelectionState(id)` (around line 1037). It queries ALL `.heart-btn[data-id]` and `.own-cb[data-id]` elements — this should cover both table row and card controls simultaneously.

Confirm the card's heart button and own checkbox have matching `data-id` attributes. Read `buildCardView()` (~line 863) to verify.

### Task 2.2: Manual QA — favorite sync

**Step 1: Open in table view. Favorite any item.**

Expected: heart filled immediately in table row.

**Step 2: Switch to Cards view.**

Expected: that item's card heart is already filled (no re-click needed).

**Step 3: In Cards view, unfavorite a different item.**

**Step 4: Switch back to Table view.**

Expected: that item's heart is empty in the table row.

### Task 2.3: Manual QA — ownership sync

Repeat Task 2.2 steps using the Own checkbox instead of the heart.

### Task 2.4: Manual QA — reload persistence for fav/own

**Step 1:** Favorite 3 items and own 2 items. Reload page.

Expected: same items still favorited/owned after reload.

### Task 2.5: Fix any sync issues

Most likely fix if sync fails: card controls built in `buildCardView()` may not be in the DOM before `bindItemControls()` runs — check init order (~line 762). Current order:
```
buildCardView()   ← builds card DOM
bindItemControls() ← queries ALL .heart-btn / .own-cb including cards
```
This should be correct. If sync still breaks, check that `syncSelectionState` is called after `buildCardView`.

### Task 2.6: Verify card action aria-labels (baseline a11y)

Read `buildCardView()` — confirm each card's heart, own, wiki, and buy elements have descriptive `aria-label` values that include the Squishmallow's name. Current code:
- heart: `Favourite ${model.name}`
- own: `I own ${model.name}`
- wiki: `Open wiki page for ${model.name}`
- buy: `Buy ${model.name} on Amazon`

If any are generic (e.g. just "Favourite" without the name), update them now.

### Task 2.7: Commit Phase 2

```bash
git add docs/squishmallowdex.html
git commit -m "fix(phase2): state sync and card action aria-labels

Verified favorites and ownership sync instantly across table
and card views. Confirmed descriptive aria-labels on all card
action controls including Squishmallow name."
```

Post comment on #12 ticking:
- [ ] Favorites and ownership toggles update instantly in both views
- [ ] Favorite in table → card updates immediately
- [ ] Favorite in card → table updates immediately
- [ ] Ownership in table → card updates immediately
- [ ] Ownership in card → table updates immediately
- [ ] Reload preserves favorites/ownership from localStorage
- [ ] Screen reader labels for card actions are descriptive ← baseline a11y

---

## Phase 3 — Sorting

**File:** `docs/squishmallowdex.html`

**Goal:** All sort paths verified; missing values sort last in both directions.

### Task 3.1: Verify missing-value sort rule in compareModels

Read `compareModels()` (~line 1167). For `collector` and `year`:
```js
if (aNum == null) return 1;   // null sorts last (ascending)
if (bNum == null) return -1;  // null sorts last (ascending)
```
**Problem:** When `sortState.dir === -1` (descending), these early returns are NOT multiplied by `dir`, so null values sort FIRST in descending order — violating the "missing values sort last in both directions" rule.

**Fix:** Change the null-guard early returns to use a sentinel large value instead:

```js
if (sortState.field === 'collector' || sortState.field === 'year') {
  const aNum = sortState.field === 'collector' ? a.collectorNum : a.yearNum;
  const bNum = sortState.field === 'collector' ? b.collectorNum : b.yearNum;
  const aSafe = aNum ?? Infinity;
  const bSafe = bNum ?? Infinity;
  result = aSafe - bSafe;
  // Infinity - Infinity = NaN, handle tie:
  if (!Number.isFinite(result)) result = 0;
}
```

With this approach: `Infinity * dir` still sorts nulls last in both asc and desc because `Infinity * 1 = Infinity` (last) and `Infinity * -1 = -Infinity` (first in reversed order... wait — need to think carefully).

Actually the cleanest approach: keep the numeric subtraction but post-multiply, and handle nulls with a sentinel:

```js
if (sortState.field === 'collector' || sortState.field === 'year') {
  const aNum = sortState.field === 'collector' ? a.collectorNum : a.yearNum;
  const bNum = sortState.field === 'collector' ? b.collectorNum : b.yearNum;
  const bothNull = aNum == null && bNum == null;
  const aNull = aNum == null;
  const bNull = bNum == null;
  if (bothNull) result = 0;
  else if (aNull) result = 1;   // a is null → a comes after b (last)
  else if (bNull) result = -1;  // b is null → b comes after a (last)
  else result = aNum - bNum;
  // Do NOT multiply null guards by dir — nulls always sort last
  if (aNull || bNull) return result; // skip dir multiplication below
}
```

Then at the bottom: `return result * sortState.dir;`

Apply this fix in `compareModels`.

### Task 3.2: Manual QA — table sort all 7 columns

In table view, click each sortable header: Name, Type, Color, Squad, Size(s), Collector Number, Year.

For each:
- First click: ascending order ↑ indicator shows.
- Second click: descending order ↓ indicator shows.
- Items with blank values should appear at the bottom in both directions for Collector # and Year.

### Task 3.3: Manual QA — card sort

Switch to Cards view. Try each card sort option:
- Name (A–Z): alphabetical ascending
- Name (Z–A): alphabetical descending
- Year (oldest first): ascending, blanks last
- Year (newest first): descending, blanks last
- Collector # (low→high): ascending, blanks last
- Collector # (high→low): descending, blanks last

### Task 3.4: Verify card sort label/control association (baseline a11y)

In `docs/squishmallowdex.html`, find the card sort HTML (search for `card-sort` or `cardSort`). Confirm:
- The `<select id="cardSort">` has a corresponding `<label for="cardSort">` (or `aria-label`).
- The label text is descriptive (e.g. "Sort cards by").

If the label is missing or uses a different `for` value, fix it.

**Step 2: Verify keyboard operation**

Tab to the card sort control. Press Space/Arrow keys. Confirm options are selectable and cards re-sort.

### Task 3.5: Manual QA — sorting under active filters

**Step 1:** Enter search "cat", switch to Cards, sort by Name (Z–A).

Expected: only matching cards shown, in Z–A order.

**Step 2:** Change sort to Year. Expected: same filtered set, sorted by year.

### Task 3.6: Commit Phase 3

```bash
git add docs/squishmallowdex.html
git commit -m "fix(phase3): sort missing values last in both directions

Fixed compareModels to sort null collector# and year values
last regardless of sort direction. Verified all 7 table sort
columns, card sort options, and sorting under active filters.
Fixed card sort label/control association for accessibility."
```

Post comment on #12 ticking:
- [ ] Table sort by Name, Type, Color, Squad, Size(s), Collector Number, Year still works
- [ ] Re-clicking sortable header toggles ascending/descending
- [ ] Card sort Name/Year/Collector# orders cards correctly
- [ ] Missing values sort last in both directions
- [ ] Sorting under active filters preserves filtered result set
- [ ] Card sort label/control association and keyboard operation ← baseline a11y

---

## Phase 4 — Accessibility (remaining)

**File:** `docs/squishmallowdex.html`

**Goal:** Visible focus styles, sensible focus order, keyboard nav throughout.

### Task 4.1: Audit focus styles

Open page, tab through all controls. Check for visible focus rings on:
- Search input
- Favorites filter button
- Owned filter button
- Table/Cards toggle buttons
- Column picker button
- Table sort headers
- Card sort dropdown
- Each card: heart button, own checkbox, wiki link, buy link

If any control has `outline: none` or `outline: 0` without a custom focus style replacing it, add a visible focus style:
```css
:focus-visible {
  outline: 2px solid #00bcd4;
  outline-offset: 2px;
}
```
Add this rule globally if not already present. Search for existing `:focus` / `:focus-visible` rules first to avoid duplication.

### Task 4.2: Audit focus order in card view

Switch to Cards view. Tab through the page. Expected logical order:
1. Skip link / header controls (search, filters, view toggle, column picker, card sort)
2. First card: heart → own → wiki → buy
3. Second card: heart → own → wiki → buy
4. ...

If cards are focusable but in DOM order that differs from visual order, check CSS. Cards should be in source order (they are appended in `buildCardView()` matching `rowModels` order).

### Task 4.3: Keyboard nav — view toggle

Tab to the Table/Cards buttons. Press Enter or Space on Cards. Confirm card view activates. Press Tab to Table, activate. Confirm it works.

### Task 4.4: Keyboard nav — card actions

Tab into a card. Press Space on heart → item should be favorited. Tab to own checkbox → Space toggles it. Tab to wiki link → Enter opens wiki in new tab. Tab to buy link → Enter opens Amazon in new tab.

### Task 4.5: Fix any issues found

Common fixes:
- Missing `:focus-visible` styles
- `tabindex="-1"` on interactive elements that should be reachable
- Card media `<a>` that opens full image but lacks descriptive `aria-label` — add `aria-label="${model.name} full image"` if missing

### Task 4.6: Commit Phase 4

```bash
git add docs/squishmallowdex.html
git commit -m "fix(phase4): accessibility - focus styles, order, keyboard nav

Added/verified visible focus styles on all interactive controls.
Confirmed logical tab order in card view. Keyboard navigation
works for view toggle, card actions, and card sort control."
```

Post comment on #12 ticking:
- [ ] Visible focus styles on all interactive controls in both views
- [ ] Focus order is sensible in card view
- [ ] Keyboard navigation across view toggle, card actions, card sort

---

## Phase 5 — Performance

**File:** `docs/squishmallowdex.html`

**Goal:** Smooth search input, no rAF race regressions, acceptable memory.

### Task 5.1: Add search debounce

Currently `search.addEventListener('input', applyFiltersAndSort)` fires on every keystroke.

**Find the listener** in `bindGlobalControls()` (~line 984):
```js
search.addEventListener('input', applyFiltersAndSort);
```

**Replace with debounced version:**
```js
let searchDebounceTimer = null;
search.addEventListener('input', () => {
  clearTimeout(searchDebounceTimer);
  searchDebounceTimer = setTimeout(applyFiltersAndSort, 130);
});
```

Place `let searchDebounceTimer = null;` at the top of the IIFE alongside other state variables.

### Task 5.2: Verify debounce feels responsive

Type rapidly in search. Cards/table should update ~130ms after you stop typing, not on every keystroke. Should feel instantaneous in normal use.

### Task 5.3: Add prefers-reduced-motion for card hover

Find card hover CSS (search for `.squish-card:hover`). It likely has a `transform` or `box-shadow` transition.

Wrap motion effects in a media query:
```css
@media (prefers-reduced-motion: no-preference) {
  .squish-card {
    transition: transform 0.15s ease, box-shadow 0.15s ease;
  }
  .squish-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.15);
  }
}
```

Remove any `transition` or `transform` on `.squish-card` that lives outside this media query.

### Task 5.4: Rapid-toggle regression test

**Step 1: Open DevTools → Console. Add a temporary log:**
```js
// Paste in console temporarily
const orig = HTMLElement.prototype.appendChild;
let callCount = 0;
// Don't actually patch — just manually spam the toggle instead.
```

**Step 2: Click Table → Cards → Table → Cards → Table → Cards rapidly (~10 times in 2 seconds)**

Expected:
- Spinner appears and disappears cleanly each time cards mode is entered.
- No flicker of partially-built card grid.
- No console errors.
- Final state matches the last button clicked.

**Step 3: If stale renders are visible:**

The race is in `applyViewMode` — rapid clicks queue multiple double-rAF callbacks. Fix by adding a guard token:

```js
let viewRenderToken = 0; // at top of IIFE with other state

function applyViewMode(mode) {
  // ... existing sync work ...

  if (viewMode === 'cards') {
    const token = ++viewRenderToken;
    cardLoader.hidden = false;
    cardGrid.hidden = true;
    requestAnimationFrame(() => requestAnimationFrame(() => {
      if (token !== viewRenderToken) return; // stale render, discard
      applyFiltersAndSort();
      cardLoader.hidden = true;
      cardGrid.hidden = false;
    }));
  } else {
    applyFiltersAndSort();
  }
}
```

Add `let viewRenderToken = 0;` to the top-of-IIFE state declarations.

### Task 5.5: Memory spot-check

Open DevTools → Memory → Take heap snapshot. Toggle Table/Cards 20 times. Take another snapshot. Compare. There should be no significant heap growth pattern (minor GC churn is fine; a growing retained size that doesn't stabilise is a problem).

If no issues found, note "no memory leak detected" in the #12 comment.

### Task 5.6: Commit Phase 5

```bash
git add docs/squishmallowdex.html
git commit -m "perf(phase5): debounce search, reduce motion, fix rAF race

Added 130ms search debounce. Wrapped card hover transitions
in prefers-reduced-motion media query. Added viewRenderToken
guard to prevent stale double-rAF renders on rapid view toggle."
```

Post comment on #12 ticking:
- [ ] Search debounce (100–150ms)
- [ ] prefers-reduced-motion for card hover effects
- [ ] Rapid-toggle / double-rAF race regression — no stale renders
- [ ] Memory footprint after repeated toggling — no leak detected
- [ ] Profile typing in search on mobile / throttled CPU

---

## Phase 6 — Polish

**File:** `docs/squishmallowdex.html`

**Goal:** Reduced-motion view transition, compact density option, mobile chip priority.

### Task 6.1: Reduced-motion view transition

Currently switching views has no animated transition (just show/hide). Add a subtle fade for users who allow motion, and an instant switch for those who prefer reduced motion.

Add CSS:
```css
@media (prefers-reduced-motion: no-preference) {
  #cardWrap {
    animation: fadeIn 0.15s ease;
  }
  @keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
  }
}
```

This applies on each switch to card view. No JS changes needed.

### Task 6.2: Compact card density option

Add a toggle button in the toolbar (near the view toggle) to switch between normal and compact card density. Persist to `localStorage` under key `squishdex-density`.

**Add LS key:**
```js
const LS_KEYS = {
  // ... existing keys ...
  density: 'squishdex-density',
};
```

**Add button HTML** (near `viewCardsBtn`):
```html
<button class="view-btn" id="compactBtn" type="button" aria-pressed="false" title="Compact card view" style="display:none">Compact</button>
```

Show/hide with `display:none` toggled by `applyViewMode`: show in cards mode, hide in table mode.

**Add CSS:**
```css
body.density-compact .squish-card {
  font-size: 0.8rem;
}
body.density-compact .card-bio {
  display: none;
}
body.density-compact .card-media img {
  max-height: 80px;
}
```

**Add JS in `bindGlobalControls()`:**
```js
const compactBtn = document.getElementById('compactBtn');
let density = localStorage.getItem(LS_KEYS.density) || 'normal';
const applyDensity = () => {
  document.body.classList.toggle('density-compact', density === 'compact');
  compactBtn.setAttribute('aria-pressed', String(density === 'compact'));
};
applyDensity();
compactBtn.addEventListener('click', () => {
  density = density === 'compact' ? 'normal' : 'compact';
  localStorage.setItem(LS_KEYS.density, density);
  applyDensity();
});
```

In `applyViewMode`, add:
```js
compactBtn.style.display = viewMode === 'cards' ? '' : 'none';
```

### Task 6.3: Mobile chip prioritisation

On narrow screens (<480px), hide low-priority chips (Squad, Size) to reduce card clutter.

Find the existing `@media` block for mobile. Add:
```css
@media (max-width: 480px) {
  .chip[data-priority="low"] {
    display: none;
  }
}
```

In `appendChip()`, mark Squad and Size as low priority:
```js
function appendChip(parent, label, value, priority) {
  if (!value) return;
  const chip = document.createElement('span');
  chip.className = 'chip';
  if (priority) chip.dataset.priority = priority;
  // ... rest unchanged
}
```

Update callers in `buildCardView()`:
```js
appendChip(meta, 'Color', model.color);
appendChip(meta, 'Year', model.year);
appendChip(meta, 'Size', model.sizes, 'low');
appendChip(meta, '#', model.collector);
appendChip(meta, 'Squad', model.squad, 'low');
```

### Task 6.4: Verify mobile layout

Open DevTools → Toggle device toolbar → iPhone SE (375px wide).

Check:
- Cards fill width without horizontal scroll.
- Squad and Size chips hidden at 375px.
- Color, Year, Collector# chips still visible.
- Compact button visible in cards mode only.

### Task 6.5: Commit Phase 6

```bash
git add docs/squishmallowdex.html
git commit -m "polish(phase6): motion transition, compact density, mobile chips

Added fade-in transition for card view (respects prefers-reduced-motion).
Added compact card density toggle persisted to localStorage.
Low-priority chips (Size, Squad) hidden on narrow mobile screens."
```

Post comment on #12 ticking:
- [ ] Reduced-motion-friendly view transition
- [ ] Compact card density option
- [ ] Mobile card chip prioritisation for small screens
- [ ] Mobile card layout is readable, no horizontal scroll

---

## Completion

### Close stale issues

```bash
gh issue close 6 --comment "Buy buttons (🛒) are live in the card and table views with affiliate tag. Closing as shipped."
gh issue close 7 --comment "FTC affiliate disclosure is present in the page footer. Closing as shipped."
gh issue close 12 --comment "All acceptance criteria met across 6 phases. Closing."
```

### Push

```bash
git push origin main
```
