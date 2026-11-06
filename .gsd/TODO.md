# TODO.md — Pending Items

> Quick capture of ideas, tasks, and issues.
>
> Use `/add-todo` to add items, `/check-todos` to view.

## Priority Levels

| Level | Use For |
|---|---|
| `high` 🔴 | Blocking issues, urgent fixes |
| `medium` 🟡 | Normal priority (default) |
| `low` 🟢 | Nice-to-have, future ideas |

---

## Milestone 1: Premium UI Redesign (Status: ✅ Complete / Verified)

- [x] Plan Phase 1 (Tokens + Static HTML mockups) `high` — 2026-11-05 ✓ 2026-11-05
- [x] Verify screenshot tooling for automated CDP capture of HTML mockups `medium` — 2026-11-05 ✓ 2026-11-05
- [x] Phase 1 Owner Visual Review Gate & Sign-Off `high` — 2026-11-05 ✓ 2026-11-05
- [x] Topbar Workbench Static Mockups & Corrective Rounds (approved) `high` — 2026-11-06 ✓ 2026-11-06
- [x] Phase 2 Topbar Workbench Final Corrective (09-PLAN: Waves 0, 1, 2) `high` — 2026-11-06 ✓ 2026-11-06
- [x] Phase 2 Owner Live Acceptance Sign-off on `http://localhost:8501` `high` — 2026-11-06 ✓ 2026-11-07

---

## Milestone 2: Make the Loop Smarter

### Phase 3: FSRS + Interleaving (Status: ✅ Verified — Awaiting Live Acceptance)
- [x] Entry Gate G1: Backend Verification Battery triaged by owner `high` — 2026-11-06 ✓ 2026-11-07
- [x] Entry Gate G2: Phase 2 formally closed by owner live approval `high` — 2026-11-06 ✓ 2026-11-07
- [x] Pin `fsrs` in `requirements.txt` and verify installation `high` — 2026-11-07 ✓ 2026-11-07
- [x] Workstream 1: Create FSRS card state SQLite table alongside existing store `high` — 2026-11-07 ✓ 2026-11-07
- [x] Workstream 1: Implement judge-to-rating mapping (`Again`, `Hard`, `Good`; `Easy` omitted) `high` — 2026-11-07 ✓ 2026-11-07
- [x] Workstream 1: Write idempotent migration script from historical attempts on DB copy `high` — 2026-11-07 ✓ 2026-11-07
- [x] Workstream 1: Retire old 1/1/3/7/21-day ladder from scheduling path `high` — 2026-11-07 ✓ 2026-11-07
- [x] Workstream 1: Truth-in-copy update for Home repetition subline `medium` — 2026-11-07 ✓ 2026-11-07
- [x] Workstream 2: Implement topic interleaving for review queue and mock selection `high` — 2026-11-07 ✓ 2026-11-07
- [x] Verification: Test suite for rating mapping, migration idempotency, due-set equivalence, and interleaving adjacency `high` — 2026-11-07 ✓ 2026-11-07
- [x] Live CDP captures at 1450×900 of Home screen with FSRS due chip and queue `medium` — 2026-11-07 ✓ 2026-11-07
- [ ] Phase 3 Owner Live Acceptance Sign-off on `http://localhost:8501` `high` — 2026-11-07

### Milestone 2 Backlog (Future Phases — Do Not Plan Now)
- [ ] Phase 4: Per-Run Resource Measurement (peak memory allocation + execution time instrumentation inside judge runner; unlock `Rating.Easy`) `medium` — 2026-11-06
- [ ] Phase 5: Attempt History Timeline & Ruff Static Analysis Panel (attempt history diffs, code evolution, inline Ruff linting in Practice Arena) `low` — 2026-11-06

---

## Milestone 3: Terracotta Editorial Redesign

### Phase 6: Terracotta Static Mockups & Token Sheet (T1 — Current Planning)
- [ ] Author `DESIGN.md` Terracotta token sheet (sun-white, sandy beige, terracotta, olive, blue, clay, fig, sea-foam) `high` — 2026-11-07
- [ ] Build static HTML mockups using real problem & store data (Home, Practice, Mock start, Mock session, Mock scorecard, Dashboard, Tokens) `high` — 2026-11-07
- [ ] Anti-slop audit against generator tropes (no chip soup, no invented figures, no gradients/glass/glow, no serif body text, no mono metrics) `high` — 2026-11-07
- [ ] Capture dual-resolution CDP screenshots at 1450×900 PRIMARY and 1920×1080 secondary `medium` — 2026-11-07
- [ ] Gate G-T1: Stop for owner mockup and token sheet approval `high` — 2026-11-07

### Phase 7: Terracotta Streamlit Implementation (T2 — Gated)
- [ ] Gate G-EXEC verification: verify Phase 6 mockup approval + Phase 3 live acceptance `high` — 2026-11-07
- [ ] Self-host DM Serif Display and humanist sans in `assets/fonts/` with `@font-face` proof `medium` — 2026-11-07
- [ ] Streamlit theme configuration in `.streamlit/config.toml` `medium` — 2026-11-07
- [ ] Implement keyed-container CSS (`.st-key-*`) in `app.py` presentation layer `high` — 2026-11-07
- [ ] Update Plotly Dashboard chart colors to Terracotta zone palette `medium` — 2026-11-07
- [ ] Verification suite: 57/57 pytest invariant, freeze verification, live CDP measurements at 1450 `high` — 2026-11-07

---

*Last updated: 2026-11-07*
