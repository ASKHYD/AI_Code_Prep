# Phase 2 Wave 0: Regression Guard & Metric-Numerals A/B Evaluation Summary

## Objective
Establish the pre-implementation regression baseline for Phase 2 by executing all 26 pytest tests with strict quarantine verification, and capture an empirical 1920×1080 A/B evaluation screenshot comparing Fraunces Display numerals against Inter SemiBold tabular numerals across the three primary Home stat cards.

## Executed Tasks

### Task 1: Pre-Implementation Regression Guard & Shell Gate Verification
- **Command Executed**: `powershell -ExecutionPolicy Bypass -File scratch/verify_regression.ps1`
- **Results**:
  - Confirmed 26 of 26 tests passed in 14.88s, including the R1 `longest_substring` fixture.
  - Quarantined paths (`coach/*.py`, `data/problems/*.json`, `tests/*`) confirmed completely clean with 0 dirty files.
  - Confirmed Shell Gate recount verdict: 0 impossible elements in Streamlit shell.
- **Commit**: `4a1b80d feat(phase-2): verify pre-implementation regression guard and shell gate`

### Task 2: Generate Metric-Numerals A/B Evaluation Screenshots
- **Artifacts Created**:
  - `scratch/eval_metrics_ab.py`: Standalone Python script that builds the self-hosted HTML evaluation fixture with embedded base64 fonts (`Fraunces` and `Inter`) and launches headless Chrome via DevTools Protocol (CDP) to capture full HD evidence.
  - `scratch/eval_metrics_ab.html`: Self-contained HTML layout displaying both typography variants across the three Home stat cards ("1 day", "0 due", "12 problems") alongside glyph inspection callouts.
  - `docs/screenshots/r3/metrics_ab_eval.png`: 1920×1080 rendered comparative screenshot (240,273 bytes).
- **Evaluation Findings**:
  - **Variant A (Fraunces Display 700)**: Displays circular, wide zero glyphs in "0 due". As observed in owner feedback [DECISION-004], the numeral reads ambiguously similar to a lowercase letter "o" in isolated stat contexts.
  - **Variant B (Inter SemiBold 600 Tabular)**: Displays tall, distinct geometric oval zero glyphs with `font-variant-numeric: tabular-nums; letter-spacing: -0.025em;`. Provides unmistakable digit clarity and uniform numeric alignment while preserving the modern, warm learning app aesthetic.
  - **Rule Enforcement**: Monospace fonts (`JetBrains Mono`) are strictly banned for metric numerals to avoid typewriter slop.
- **Commit**: `08761cf feat(phase-2): generate metric numerals A/B evaluation screenshots`

## Verification Evidence
- `powershell -ExecutionPolicy Bypass -File scratch/verify_regression.ps1` → 26 passed, 0 failures, quarantine clean.
- `Test-Path docs/screenshots/r3/metrics_ab_eval.png` → `True` (verified via visual inspection tool).

## Deviations
None.

## Decisions & Recommendations
- Recommended selection for Phase 2 Wave 3 (Home Screen implementation): **Variant B (Inter SemiBold 600 Tabular)** for primary stat card numerals (`1 day`, `0 due`, `12 problems`). Card headers and titles will continue using Fraunces Display 700.
