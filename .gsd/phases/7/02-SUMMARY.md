# Wave 2 Implementation Summary: Home Bento & Dashboard Implementation

**Phase**: Milestone 3, Phase 7: Terracotta Streamlit Implementation (T2)  
**Wave**: Wave 2  
**Completed**: 2026-11-07  
**Status**: COMPLETE (Tasks 2.1, 2.2, 2.3)

---

## 1. Accomplishments

1. **Task 2.1 — Home Screen Bento Layout & Verified FSRS Copy**:
   - Hero header in `DM Serif Display` 34px ("Today's Practice").
   - Primary pill CTA "Start Daily Practice →" styled in `#C2452D` with `#FFF8F0` text and 9999px radius.
   - 3 Stat Bento Cards:
     - Active Streak (olive `ACTIVE` when streak > 0, quiet `NOT STARTED` when 0).
     - Problems Due Today (tabular numerals, `FSRS` badge if due > 0, `CLEAR` if 0).
     - Target Retention (90.0% tabular numeral in `Plus Jakarta Sans`, olive badge).
   - Verbatim FSRS explanation copy preserved: "Adaptive spaced repetition (FSRS) scheduled from your objective test results."

2. **Task 2.2 — Home Problem Queue Table (Terracotta Styling with C1–C3 Logic)**:
   - Wrapped in 24px white container with warm hairline and header "Recommended Practice Queue".
   - Maintained all Phase 3 invariants:
     - `build_interleaved_queue` due-first partition (C3).
     - Amber `<span class="stat-badge badge-amber">DUE FOR REVIEW</span>` pill with subtitle "Due for review · Scheduled by FSRS" (C2).
     - Computed dynamic deltas `Next Due: +{N} Day(s)` for solved non-due problems (C2).
     - Quiet gray `Unattempted` pills.
     - Topic pills in Mediterranean blue (`badge-blue`).
     - Seam invariant: zero adjacent problems share a topic.

3. **Task 2.3 — Dashboard View (Plotly Attempted Chart Above Full Topic Table)**:
   - Hero header in `DM Serif Display` 34px ("Performance Analytics").
   - Summary stat bento cards: Solved Problems, Practice Sessions, Average Hints Used.
   - Plotly horizontal pass rate chart for **ATTEMPTED topics only** placed strictly **ABOVE** the full table (F2 fix):
     - Terracotta color palette (Olive `#6B7F3B` for $\ge 70\%$, Terracotta `#C2452D` for $< 70\%$).
     - Clean white card with subtle gridlines.
   - Full 11-topic mastery table placed below:
     - Lists all 11 curriculum topics from `store.topic_stats()`.
     - Unattempted rows display status `<span class="stat-badge badge-quiet">NOT STARTED</span>` with `—` progress bar (never `0%`).
   - Commit: `b4ceeac`.

---

## 2. Invariants Maintained
- 71/71 tests green in 31.66s.
- `coach/*.py` and problem JSON files strictly frozen.
