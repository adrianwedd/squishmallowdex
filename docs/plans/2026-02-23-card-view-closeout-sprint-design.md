# Card View Close-Out Sprint — Design Doc

**Date:** 2026-02-23
**Issue:** #12 — Card view follow-up: parity QA, polish, and regression validation
**Closes also:** #6 (buy buttons — already shipped), #7 (FTC disclosures — already shipped)

---

## Goal

Work through every acceptance criterion and checklist item in issue #12, producing a fully hardened card view with no known regressions. Each phase is a discrete commit with evidence recorded as a comment on #12.

## Out of Scope

- Color filtering (#9)
- i18n framework (#3 / #5 / #8)
- New affiliate work
- Virtual scrolling / full DOM virtualization

---

## Phase Exit Rule

No known regressions introduced in previously completed phases. Each phase commit must leave the feature in a working, shippable state.

---

## Phases

### Phase 1 — Functional QA + Persistence

**Goal:** Verify and harden baseline behavior and all localStorage persistence.

**Work:**
- Default view is `table` on first load (no prior `squishdex-view` key).
- Switching views preserves active search text, favorites-only, owned-only filters, and sort state.
- Result count matches visible items in both views under all filter combinations.
- Column picker enabled in table mode, disabled in card mode, re-enabled on switch back.
- Reload persistence for `squishdex-view`, `squishdex-card-sort`, `squishdex-cols`.

**Baseline a11y (must-pass here):**
- `aria-pressed` correct on Table / Cards toggle buttons.

**Evidence:** Console + manual QA notes. Comment on #12 ticking Phase 1 items.

**#12 items covered:**
- Table view remains default on first load ✓
- Switching between views preserves active search/filter/sort state ✓
- Result count matches visible items in both views under all filters ✓
- Column picker does not break when toggling back/forth ✓
- View mode persists after reload (`squishdex-view`) ✓
- Search by name returns same count in table and cards ✓
- Clearing search restores full count without stale hidden rows/cards ✓
- `Table` and `Cards` buttons expose correct pressed state (`aria-pressed`) ✓

---

### Phase 2 — State Sync

**Goal:** Favorites and ownership state updates instantly across both views and survives reload.

**Work:**
- Favoriting in table → card updates immediately (no reload required).
- Favoriting in card → table updates immediately.
- Ownership toggle in table → card checkbox updates immediately.
- Ownership toggle in card → table checkbox updates immediately.
- Reload preserves favorites/ownership from localStorage.

**Baseline a11y (must-pass here):**
- Card action buttons have descriptive `aria-label` values (favorite, own, wiki, buy).

**Evidence:** Manual state sync walkthrough. Comment on #12 ticking Phase 2 items.

**#12 items covered:**
- Favorites and ownership toggles update instantly in both views ✓
- Favorite an item in table → card updates immediately ✓
- Favorite an item in card → table updates immediately ✓
- Toggle ownership in table → card checkbox updates immediately ✓
- Toggle ownership in card → table checkbox updates immediately ✓
- Reload preserves favorites/ownership states from localStorage ✓
- Screen reader labels for card favorite/owned/wiki/buy actions are descriptive ✓

---

### Phase 3 — Sorting

**Goal:** All sort paths work correctly with unambiguous missing-value behavior.

**Missing value rule:** Missing or empty values sort **last** in both ascending and descending directions for all card and table sorts.

**Work:**
- Table sort by Name, Type, Color, Squad, Size(s), Collector Number, Year — all columns work.
- Re-clicking a sortable table header toggles ascending/descending.
- Card sort Name (A–Z / Z–A), Type, Year, Collector # — all options order cards correctly.
- Missing Year values sort last (both directions).
- Missing Collector # values sort last (both directions).
- Sorting under active filters preserves filtered result set (no phantom rows).

**Baseline a11y (must-pass here):**
- Card sort `<label>` is correctly associated with the `<select>` control.
- Card sort is keyboard-operable.

**Evidence:** Sort matrix walkthrough. Comment on #12 ticking Phase 3 items.

**#12 items covered:**
- Table sort by all 7 columns still works ✓
- Re-clicking toggles asc/descending ✓
- Card sort Name / Year / Collector # orders cards correctly ✓
- Missing values sort last (both directions) ✓
- Sorting under active filters preserves filtered set ✓
- Card sort label/control association and keyboard operation ✓

---

### Phase 4 — Accessibility (remaining)

**Goal:** Full keyboard and screen reader usability across both views.

**Work:**
- Visible focus styles on all interactive controls in table and card views.
- Focus order is sensible in card view (logical tab sequence through cards).
- Keyboard navigation works: view toggle, individual card actions, card sort control.
- Verify no focus traps or skipped elements.

**Evidence:** Keyboard-only walkthrough. Comment on #12 ticking Phase 4 items.

**#12 items covered:**
- Verify screen reader labels for card actions are descriptive ✓ (confirmed from Phase 2)
- Ensure focus order is sensible in card view ✓
- Confirm visible focus styles on all interactive controls in both views ✓
- Validate card sort label/control association and keyboard operation ✓ (confirmed from Phase 3)

---

### Phase 5 — Performance

**Goal:** Smooth typing, no rAF race regressions, acceptable memory footprint.

**Work:**
- Add search debounce (100–150ms) if typing feels laggy on large dataset.
- Apply `prefers-reduced-motion` media query to card hover effects.
- **Rapid-toggle regression test:** spam Table/Cards toggle 10+ times; confirm no stale queued renders, no flicker, spinner shows and hides cleanly each time.
- Memory spot-check: open DevTools, toggle/filter repeatedly, confirm no obvious heap growth pattern.
- Profile typing in search on mobile (or simulated throttled CPU) to validate debounce effect.

**Evidence:** DevTools screenshots (memory, network/animation frames if relevant). Comment on #12 ticking Phase 5 items.

**#12 items covered:**
- Profile typing in search on lower-end mobile devices ✓
- Search debounce (100–150ms) if typing feels laggy ✓
- `prefers-reduced-motion` for card hover effects ✓
- Memory footprint after repeated toggling/filtering ✓
- (New) Rapid-toggle / double-rAF race regression ✓

---

### Phase 6 — Polish

**Goal:** Nice-to-have UX improvements that don't introduce regressions.

**Work:**
- Reduced-motion-friendly view transition (e.g. skip fade/animation when `prefers-reduced-motion: reduce`).
- Compact card density option (CSS class toggle, persisted to localStorage).
- Mobile card chip prioritisation (hide low-priority chips at narrow breakpoints).

**Evidence:** Visual QA on mobile + desktop. Comment on #12 ticking Phase 6 items.

**#12 items covered:**
- Add reduced-motion-friendly view transition ✓
- Add compact card density option ✓
- Improve card meta chip prioritisation for small screens ✓
- Mobile card layout is readable and avoids horizontal scrolling ✓

---

## Completion Criteria

- All checkboxes in #12 ticked.
- #12 closed.
- #6 closed (already shipped — buy buttons live).
- #7 closed (already shipped — affiliate disclosures live).
- No open regressions against Phase 1–5 behavior after Phase 6.
