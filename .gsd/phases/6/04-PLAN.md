---
phase: 6
plan: "04"
wave: 3
depends_on: ["02", "03"]
---

# Plan 6.4: Anti-Slop Audit, Dual-Resolution CDP Captures & Phase Return

## Objective
Conduct the formal anti-slop audit across all 7 Terracotta Editorial mockups to eliminate AI generator tropes, capture full-fidelity Chrome CDP screenshots at 1450×900 (primary owner viewport) and 1920×1080 (secondary viewport), verify zero application code mutations, compile the complete resources exercised block, and file the Phase 6 Return at the Terracotta Editorial gate.

## Context
- `.gsd/SPEC.md`
- `.gsd/phases/6/DISCUSS.md`
- `mockups/terracotta/*.html`
- `scratch/capture_r4_mockups.py` (CDP capture automation script reference)

---

## Tasks

<task type="auto">
  <name>Task 4.1: Anti-Slop Audit Verification</name>
  <files>scratch/run_terracotta_audit.py, .gsd/phases/6/04-SUMMARY.md</files>
  <action>
    <!-- Skill binding: /impeccable + /agency-ui-finish-gate-reviewer -->
    1. Write and run `scratch/run_terracotta_audit.py` to inspect all 7 mockups against the 5 prohibited tropes:
       - **Chip Soup**: Verify queues and tables contain at most ONE status pill per row (difficulty/topic rendered as colored text).
       - **Invented Figures**: Verify problem names belong strictly to the 12 problems in `data/problems/*.json` and metrics match store data (2 attempts, 1 solved).
       - **Gradient / Glass / Glow**: Verify CSS contains zero `backdrop-filter`, zero linear-gradients across cards, and zero box-shadow glows.
       - **Serif Body Text**: Verify `DM Serif Display` is applied strictly to display headlines and wordmarks, with body and UI text using Humanist Sans.
       - **Mono Metrics**: Verify metric numbers do not use `JetBrains Mono` (reserved exclusively for code, editor strip, and timer).
    2. Confirm audit passes with 0 violations across all 7 HTML files.
  </action>
  <verify>.venv\Scripts\python.exe scratch/run_terracotta_audit.py</verify>
  <done>Anti-slop audit completed and verified 0 trope violations across all mockups.</done>
</task>

<task type="auto">
  <name>Task 4.2: Dual-Resolution Chrome CDP Captures & Phase 6 Return</name>
  <files>scratch/capture_terracotta_mockups.py, docs/screenshots/terracotta/, .gsd/phases/6/PHASE_RETURN.md</files>
  <action>
    <!-- Skill binding: /agency-evidence-collector + /empirical-validation -->
    1. Author `scratch/capture_terracotta_mockups.py` using headless Chrome CDP to capture each of the 7 mockups at:
       - **Primary Viewport**: 1450 × 900 (owner's native test window)
       - **Secondary Viewport**: 1920 × 1080
       - Output directory: `docs/screenshots/terracotta/` (14 captures total).
       - Copy primary 1450×900 screenshots to the conversation artifacts directory.
    2. Verify code quarantine: run git diff stat to prove `app.py`, `coach/*.py`, `data/problems/*.json`, and `tests/*` are 100% untouched.
    3. Run pytest to confirm test suite remains 57/57 passing.
    4. Author and file `.gsd/phases/6/PHASE_RETURN.md`:
       - Token sheet summary and named deviations from AI renders.
       - Complete table of 14 captured screenshots by file name and byte size.
       - Full Resources Exercised accounting block (all named resources).
       - Known limits and transition path to Phase 7.
       - Verbatim stop sentence: `"Stopped at Terracotta Editorial gate, awaiting owner approval."`
  </action>
  <verify>.venv\Scripts\python.exe scratch/capture_terracotta_mockups.py</verify>
  <done>All 14 captures taken, pytest 57/57 confirmed, freezes verified, and PHASE_RETURN.md filed.</done>
</task>

---

## Must-Haves
After all tasks complete, verify:
- [ ] 0 anti-slop violations found by automated audit.
- [ ] 14 screenshots saved in `docs/screenshots/terracotta/` (7 at 1450×900, 7 at 1920×1080).
- [ ] Pytest passes 57/57.
- [ ] Zero application code diffs outside `mockups/terracotta/`, `DESIGN.md`, and docs.
- [ ] Phase Return filed ending with `"Stopped at Terracotta Editorial gate, awaiting owner approval."`

## Success Criteria
- [ ] High-fidelity captures ready for owner visual acceptance.
- [ ] Gate G-T1 ready for owner sign-off.

