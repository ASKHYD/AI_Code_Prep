"""
Metric-Numerals A/B Evaluation Generator & Capture Script
Phase 2 Wave 0 Task 2

Renders the 3 Home stat cards ("1 day", "0 due", "12 problems") in both variants:
  - Variant A: Fraunces Display numerals (Serif Display, 700 weight, 40px)
  - Variant B: Inter SemiBold tabular figures (Sans-Serif, 600 weight, 38px, font-variant-numeric: tabular-nums)
  - Note: Monospace is strictly BANNED for metric cards (typewriter slop)

Outputs:
  - scratch/eval_metrics_ab.html (rendered HTML with self-hosted offline fonts in base64)
  - docs/screenshots/r3/metrics_ab_eval.png (1920x1080 comparative screenshot)
"""

import asyncio
import base64
import json
import os
import pathlib
import shutil
import subprocess
import tempfile
import time
import urllib.request
import websockets

WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent
FONTS_DIR = WORKSPACE_ROOT / "assets" / "fonts"
DOCS_DIR = WORKSPACE_ROOT / "docs" / "screenshots" / "r3"
BRAIN_DIR = pathlib.Path(
    r"C:\Users\MS Computer\.gemini\antigravity\brain\e5d544c1-51ae-466c-b76a-3d00eb35369d\screenshots\r3"
)

HTML_OUTPUT_PATH = WORKSPACE_ROOT / "scratch" / "eval_metrics_ab.html"
PNG_OUTPUT_PATH = DOCS_DIR / "metrics_ab_eval.png"

def get_font_b64(filename: str) -> str:
    path = FONTS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing required offline font: {path}")
    return base64.b64encode(path.read_bytes()).decode("ascii")

def build_html() -> str:
    fraunces_700 = get_font_b64("fraunces-latin-700-normal.woff2")
    fraunces_600 = get_font_b64("fraunces-latin-600-normal.woff2")
    inter_400 = get_font_b64("inter-latin-400-normal.woff2")
    inter_500 = get_font_b64("inter-latin-500-normal.woff2")
    inter_600 = get_font_b64("inter-latin-600-normal.woff2")
    inter_700 = get_font_b64("inter-latin-700-normal.woff2")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Metric Numeral Typography Evaluation (A/B Test) | AI Coding Prep Coach</title>
  <style>
    @font-face {{
      font-family: 'Fraunces';
      font-style: normal;
      font-weight: 600;
      src: url('data:font/woff2;base64,{fraunces_600}') format('woff2');
    }}
    @font-face {{
      font-family: 'Fraunces';
      font-style: normal;
      font-weight: 700;
      src: url('data:font/woff2;base64,{fraunces_700}') format('woff2');
    }}
    @font-face {{
      font-family: 'Inter';
      font-style: normal;
      font-weight: 400;
      src: url('data:font/woff2;base64,{inter_400}') format('woff2');
    }}
    @font-face {{
      font-family: 'Inter';
      font-style: normal;
      font-weight: 500;
      src: url('data:font/woff2;base64,{inter_500}') format('woff2');
    }}
    @font-face {{
      font-family: 'Inter';
      font-style: normal;
      font-weight: 600;
      src: url('data:font/woff2;base64,{inter_600}') format('woff2');
    }}
    @font-face {{
      font-family: 'Inter';
      font-style: normal;
      font-weight: 700;
      src: url('data:font/woff2;base64,{inter_700}') format('woff2');
    }}

    :root {{
      --paper: #FBFAF7;
      --surface: #FFFFFF;
      --ink: #171712;
      --muted: #66635A;
      --hairline: #E7E1D6;

      --wash-mint: #DFF3E4;
      --partner-green: #167B48;
      --fill-green: #1F9D63;

      --wash-sky: #DCEBFF;
      --partner-blue: #1D5EC2;
      --fill-blue: #2273E6;

      --wash-butter: #FFF0C4;
      --partner-amber: #9A3412;
      --fill-amber: #B45309;

      --wash-rose: #FFE0E0;
      --partner-red: #C5221F;
      --fill-red: #D92D20;

      --radius-card: 20px;
      --radius-tile: 12px;
      --radius-pill: 999px;
      --shadow-soft: 0 1px 2px rgba(23, 23, 18, 0.05), 0 6px 18px rgba(23, 23, 18, 0.05);

      --font-display: 'Fraunces', Georgia, serif;
      --font-body: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      width: 1920px;
      height: 1080px;
      max-height: 1080px;
      overflow: hidden;
      background-color: var(--paper);
      color: var(--ink);
      font-family: var(--font-body);
      -webkit-font-smoothing: antialiased;
      padding: 24px 44px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}

    /* Header */
    .header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      padding-bottom: 14px;
      border-bottom: 1px solid var(--hairline);
    }}

    .header-left {{
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}

    .header-pill {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 3px 12px;
      border-radius: var(--radius-pill);
      background-color: var(--wash-mint);
      color: var(--partner-green);
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      width: fit-content;
    }}

    .header-title {{
      font-family: var(--font-display);
      font-size: 27px;
      font-weight: 700;
      color: var(--ink);
      letter-spacing: -0.02em;
      line-height: 1.15;
    }}

    .header-subtitle {{
      font-size: 13px;
      color: var(--muted);
      max-width: 1100px;
    }}

    .header-badges {{
      display: flex;
      gap: 10px;
      align-items: center;
    }}

    .rule-tag {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 5px 12px;
      border-radius: var(--radius-pill);
      background-color: var(--surface);
      border: 1px solid var(--hairline);
      font-size: 12px;
      font-weight: 600;
      color: var(--muted);
    }}

    .rule-tag.ban {{
      background-color: var(--wash-rose);
      color: var(--partner-red);
      border-color: rgba(197, 34, 31, 0.25);
    }}

    /* Main Comparison Container */
    .comparison-grid {{
      display: flex;
      flex-direction: column;
      gap: 16px;
      margin-top: 4px;
    }}

    /* Variant Block */
    .variant-card {{
      background-color: var(--surface);
      border: 1px solid var(--hairline);
      border-radius: 20px;
      padding: 16px 24px;
      box-shadow: var(--shadow-soft);
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}

    .variant-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .variant-meta {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .variant-badge {{
      padding: 4px 12px;
      border-radius: var(--radius-pill);
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }}

    .variant-badge-a {{
      background-color: #F0EDE6;
      color: #555042;
    }}

    .variant-badge-b {{
      background-color: #E2ECFD;
      color: #1754B4;
    }}

    .variant-title {{
      font-family: var(--font-display);
      font-size: 18px;
      font-weight: 700;
      color: var(--ink);
    }}

    .variant-specs {{
      font-size: 12px;
      color: var(--muted);
      font-weight: 500;
    }}

    .variant-verdict {{
      font-size: 12px;
      font-weight: 600;
      padding: 3px 10px;
      border-radius: 6px;
    }}

    .verdict-a {{
      background-color: #F8F4EC;
      color: #7A693F;
    }}

    .verdict-b {{
      background-color: var(--wash-mint);
      color: var(--partner-green);
    }}

    /* Stat Cards Row */
    .stat-row {{
      display: grid;
      grid-template-columns: repeat(3, 1fr) 420px;
      gap: 16px;
      align-items: stretch;
    }}

    .stat-card {{
      border-radius: var(--radius-card);
      padding: 18px 20px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      min-height: 154px;
      position: relative;
    }}

    .card-mint {{
      background-color: var(--wash-mint);
      border: 1px solid rgba(22, 123, 72, 0.15);
    }}

    .card-sky {{
      background-color: var(--wash-sky);
      border: 1px solid rgba(29, 94, 194, 0.15);
    }}

    .card-butter {{
      background-color: var(--wash-butter);
      border: 1px solid rgba(180, 83, 9, 0.18);
    }}

    .stat-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }}

    .stat-icon-tile {{
      width: 38px;
      height: 38px;
      border-radius: var(--radius-tile);
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--surface);
    }}

    .tile-green {{ background-color: var(--fill-green); }}
    .tile-blue {{ background-color: var(--fill-blue); }}
    .tile-amber {{ background-color: var(--fill-amber); }}

    .badge {{
      display: inline-flex;
      align-items: center;
      padding: 3px 10px;
      border-radius: var(--radius-pill);
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }}

    .badge-mint {{
      background-color: rgba(255, 255, 255, 0.7);
      color: var(--partner-green);
    }}

    .badge-sky {{
      background-color: rgba(255, 255, 255, 0.7);
      color: var(--partner-blue);
    }}

    .badge-butter {{
      background-color: rgba(255, 255, 255, 0.7);
      color: var(--partner-amber);
    }}

    .stat-content {{
      display: flex;
      flex-direction: column;
    }}

    .stat-label {{
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--muted);
    }}

    /* The core comparison numeral classes */
    .numeral-a {{
      font-family: var(--font-display);
      font-size: 38px;
      font-weight: 700;
      color: var(--ink);
      line-height: 1.1;
      margin-top: 2px;
      letter-spacing: -0.015em;
    }}

    .numeral-b {{
      font-family: var(--font-body);
      font-size: 36px;
      font-weight: 600;
      color: var(--ink);
      line-height: 1.1;
      margin-top: 2px;
      font-variant-numeric: tabular-nums;
      letter-spacing: -0.025em;
    }}

    .stat-caption {{
      font-size: 12px;
      color: var(--muted);
      margin-top: 6px;
      line-height: 1.35;
    }}

    /* Inspection specimen box */
    .specimen-box {{
      background-color: #F8F7F3;
      border: 1px dashed var(--hairline);
      border-radius: var(--radius-card);
      padding: 14px 18px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}

    .specimen-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--muted);
    }}

    .specimen-zero-highlight {{
      display: flex;
      align-items: center;
      gap: 16px;
      padding: 8px 12px;
      border-radius: 10px;
      background-color: var(--surface);
      border: 1px solid var(--hairline);
    }}

    .zero-display-a {{
      font-family: var(--font-display);
      font-size: 40px;
      font-weight: 700;
      color: var(--partner-red);
      line-height: 1;
    }}

    .zero-display-b {{
      font-family: var(--font-body);
      font-size: 40px;
      font-weight: 600;
      font-variant-numeric: tabular-nums;
      color: var(--partner-green);
      line-height: 1;
    }}

    .zero-desc {{
      font-size: 12px;
      line-height: 1.35;
      color: var(--ink);
    }}

    .specimen-strip {{
      display: flex;
      justify-content: space-between;
      padding-top: 4px;
      border-top: 1px solid var(--hairline);
    }}

    .strip-a {{
      font-family: var(--font-display);
      font-size: 16px;
      font-weight: 700;
      color: var(--ink);
      letter-spacing: 0.1em;
    }}

    .strip-b {{
      font-family: var(--font-body);
      font-size: 16px;
      font-weight: 600;
      font-variant-numeric: tabular-nums;
      color: var(--ink);
      letter-spacing: 0.12em;
    }}

    /* Bottom Evaluation Bar */
    .footer-bar {{
      display: grid;
      grid-template-columns: 1.1fr 1.3fr 1fr;
      gap: 16px;
      padding-top: 12px;
      border-top: 1px solid var(--hairline);
    }}

    .info-card {{
      background-color: var(--surface);
      border: 1px solid var(--hairline);
      border-radius: 14px;
      padding: 12px 16px;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}

    .info-card-title {{
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .info-card-text {{
      font-size: 12px;
      color: var(--muted);
      line-height: 1.4;
    }}
  </style>
</head>
<body>

  <!-- Header -->
  <header class="header">
    <div class="header-left">
      <div class="header-pill">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
        Phase 2 Wave 0 · Metric-Numerals A/B Evaluation
      </div>
      <h1 class="header-title">Metric Numeral Typography: Fraunces Display vs Inter SemiBold Tabular</h1>
      <p class="header-subtitle">Direct side-by-side comparison of the 3 primary Home stat cards to resolve owner zero-glyph readability observation [DECISION-004 & NOTE-003]. Rendered with offline self-hosted fonts.</p>
    </div>
    <div class="header-badges">
      <div class="rule-tag ban">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"/></svg>
        Monospace Strictly BANNED
      </div>
      <div class="rule-tag">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
        Full 1920×1080 Rendering
      </div>
    </div>
  </header>

  <!-- Comparison Grid -->
  <div class="comparison-grid">

    <!-- VARIANT A -->
    <section class="variant-card">
      <div class="variant-header">
        <div class="variant-meta">
          <span class="variant-badge variant-badge-a">Variant A</span>
          <h2 class="variant-title">Fraunces Display 700 (Phase 1 Baseline)</h2>
          <span class="variant-specs">font-family: 'Fraunces', Georgia, serif · 700 bold · 38px · line-height 1.1</span>
        </div>
        <div class="variant-verdict verdict-a">
          Serif Display Warmth · Circular '0' Glyphs (Can mimic lowercase 'o')
        </div>
      </div>

      <div class="stat-row">
        <!-- Mint Card -->
        <div class="stat-card card-mint">
          <div class="stat-top">
            <div class="stat-icon-tile tile-green">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15.914 4a1.5 1.5 0 0 0-2.474-1.561l-9 9A1.5 1.5 0 0 0 5.5 14h4.002a.5.5 0 0 1 .471.666L8.086 20a1.5 1.5 0 0 0 2.475 1.56l9-9A1.5 1.5 0 0 0 18.5 10h-3.997a.5.5 0 0 1-.472-.667z"/></svg>
            </div>
            <span class="badge badge-mint">Active</span>
          </div>
          <div class="stat-content">
            <span class="stat-label">Active Streak</span>
            <span class="numeral-a">1 day</span>
            <span class="stat-caption">Practice tomorrow to reach a 2-day streak.</span>
          </div>
        </div>

        <!-- Sky Card -->
        <div class="stat-card card-sky">
          <div class="stat-top">
            <div class="stat-icon-tile tile-blue">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m16 9-5.5 5.5L8 12"/></svg>
            </div>
            <span class="badge badge-sky">On Schedule</span>
          </div>
          <div class="stat-content">
            <span class="stat-label">Due for Review</span>
            <span class="numeral-a">0 due</span>
            <span class="stat-caption">All scheduled reviews are completely caught up.</span>
          </div>
        </div>

        <!-- Butter Card -->
        <div class="stat-card card-butter">
          <div class="stat-top">
            <div class="stat-icon-tile tile-amber">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v16"/><path d="M20.001 19A2 2 0 0 0 22 17V5a2 2 0 0 0-1.999-2L16 3.002A5 5 0 0 0 12 5a5 5 0 0 0-4-2H4a2 2 0 0 0-2 2v12a2 2 0 0 0 1.999 2H8a5 5 0 0 1 4 2 5 5 0 0 1 4-2z"/></svg>
            </div>
            <span class="badge badge-butter">Library</span>
          </div>
          <div class="stat-content">
            <span class="stat-label">Total Problems</span>
            <span class="numeral-a">12 problems</span>
            <span class="stat-caption">Curated across DSA, Strings, and Practical Python.</span>
          </div>
        </div>

        <!-- Specimen Inspection Box -->
        <div class="specimen-box">
          <div class="specimen-header">
            <span>Glyph Focus: Fraunces '0'</span>
            <span style="color: var(--partner-red);">Issue Identified</span>
          </div>
          <div class="specimen-zero-highlight">
            <div class="zero-display-a">0 due</div>
            <div class="zero-desc">
              <strong>Fraunces Display "0":</strong> Curvature is round and wide. At 40px without leading digits, reads ambiguously like <em style="font-family: var(--font-display); font-size: 15px;">"o due"</em>.
            </div>
          </div>
          <div class="specimen-strip">
            <span style="font-size: 10px; font-weight: 700; color: var(--muted); text-transform: uppercase;">Numerals:</span>
            <span class="strip-a">0 1 2 3 4 5 6 7 8 9</span>
          </div>
        </div>
      </div>
    </section>

    <!-- VARIANT B -->
    <section class="variant-card" style="border-color: rgba(22, 123, 72, 0.3);">
      <div class="variant-header">
        <div class="variant-meta">
          <span class="variant-badge variant-badge-b">Variant B (Recommended)</span>
          <h2 class="variant-title">Inter SemiBold 600 Tabular (Modern Product Figure)</h2>
          <span class="variant-specs">font-family: 'Inter', sans-serif · 600 semibold · 36px · tabular-nums · -0.025em</span>
        </div>
        <div class="variant-verdict verdict-b">
          Crisp Numeric Clarity · Tall Distinct '0' Oval · Uniform Tabular Alignment
        </div>
      </div>

      <div class="stat-row">
        <!-- Mint Card -->
        <div class="stat-card card-mint">
          <div class="stat-top">
            <div class="stat-icon-tile tile-green">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15.914 4a1.5 1.5 0 0 0-2.474-1.561l-9 9A1.5 1.5 0 0 0 5.5 14h4.002a.5.5 0 0 1 .471.666L8.086 20a1.5 1.5 0 0 0 2.475 1.56l9-9A1.5 1.5 0 0 0 18.5 10h-3.997a.5.5 0 0 1-.472-.667z"/></svg>
            </div>
            <span class="badge badge-mint">Active</span>
          </div>
          <div class="stat-content">
            <span class="stat-label">Active Streak</span>
            <span class="numeral-b">1 day</span>
            <span class="stat-caption">Practice tomorrow to reach a 2-day streak.</span>
          </div>
        </div>

        <!-- Sky Card -->
        <div class="stat-card card-sky">
          <div class="stat-top">
            <div class="stat-icon-tile tile-blue">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m16 9-5.5 5.5L8 12"/></svg>
            </div>
            <span class="badge badge-sky">On Schedule</span>
          </div>
          <div class="stat-content">
            <span class="stat-label">Due for Review</span>
            <span class="numeral-b">0 due</span>
            <span class="stat-caption">All scheduled reviews are completely caught up.</span>
          </div>
        </div>

        <!-- Butter Card -->
        <div class="stat-card card-butter">
          <div class="stat-top">
            <div class="stat-icon-tile tile-amber">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v16"/><path d="M20.001 19A2 2 0 0 0 22 17V5a2 2 0 0 0-1.999-2L16 3.002A5 5 0 0 0 12 5a5 5 0 0 0-4-2H4a2 2 0 0 0-2 2v12a2 2 0 0 0 1.999 2H8a5 5 0 0 1 4 2 5 5 0 0 1 4-2z"/></svg>
            </div>
            <span class="badge badge-butter">Library</span>
          </div>
          <div class="stat-content">
            <span class="stat-label">Total Problems</span>
            <span class="numeral-b">12 problems</span>
            <span class="stat-caption">Curated across DSA, Strings, and Practical Python.</span>
          </div>
        </div>

        <!-- Specimen Inspection Box -->
        <div class="specimen-box" style="background-color: #F0F9F3; border-color: rgba(22, 123, 72, 0.25);">
          <div class="specimen-header">
            <span>Glyph Focus: Inter Tabular '0'</span>
            <span style="color: var(--partner-green);">Crisp Distinction</span>
          </div>
          <div class="specimen-zero-highlight">
            <div class="zero-display-b">0 due</div>
            <div class="zero-desc">
              <strong>Inter SemiBold "0":</strong> Engineered upright geometric oval. Unmistakable as a digit, never confused with lowercase "o". High contrast readability.
            </div>
          </div>
          <div class="specimen-strip">
            <span style="font-size: 10px; font-weight: 700; color: var(--muted); text-transform: uppercase;">Numerals:</span>
            <span class="strip-b">0 1 2 3 4 5 6 7 8 9</span>
          </div>
        </div>
      </div>
    </section>

  </div>

  <!-- Footer Evaluation Bar -->
  <footer class="footer-bar">
    <div class="info-card">
      <div class="info-card-title" style="color: var(--partner-red);">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"/></svg>
        Monospace Strictly Banned
      </div>
      <div class="info-card-text">
        Code/monospace fonts (JetBrains Mono) are strictly forbidden for metric values per Decision-004. Monospace metric numerals look like typewriter slop and destroy visual balance.
      </div>
    </div>

    <div class="info-card">
      <div class="info-card-title" style="color: var(--ink);">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>
        Owner Recommendation
      </div>
      <div class="info-card-text">
        Adopt <strong>Variant B (Inter SemiBold 600 Tabular)</strong> for all primary metric values (Active Streak, Due for Review, Total Problems, Submissions count). Retain Fraunces for card headers and section titles.
      </div>
    </div>

    <div class="info-card" style="border-color: rgba(22, 123, 72, 0.3); background-color: #FAFDFC;">
      <div class="info-card-title" style="color: var(--partner-green);">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
        Implementation Next Steps
      </div>
      <div class="info-card-text">
        Present this artifact to the project owner. The selected numeral typography will be locked into Phase 2 Wave 3 (Home Screen implementation).
      </div>
    </div>
  </footer>

</body>
</html>
"""
    return html

async def capture_page(html_file_path: pathlib.Path, png_output_path: pathlib.Path):
    profile_dir = tempfile.mkdtemp(prefix="chrome_metric_eval_")
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    port = 9224

    proc = subprocess.Popen([
        chrome_path,
        "--headless=new",
        "--disable-gpu",
        "--disable-extensions",
        f"--remote-debugging-port={port}",
        f"--user-data-dir={profile_dir}",
        "--window-size=1920,1080"
    ])

    try:
        # Wait for Chrome debug port to open and find page target
        ws_url = None
        for _ in range(30):
            time.sleep(0.2)
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=1) as response:
                    tabs = json.loads(response.read().decode("utf-8"))
                    page_tabs = [t for t in tabs if t.get("type") == "page"]
                    if page_tabs:
                        ws_url = page_tabs[0].get("webSocketDebuggerUrl")
                        if ws_url:
                            break
            except Exception:
                pass

        if not ws_url:
            raise RuntimeError(f"Could not connect to Chrome debugging port {port}")

        async with websockets.connect(ws_url, max_size=50 * 1024 * 1024) as ws:
            msg_id = 1

            async def send_cmd(method, params=None):
                nonlocal msg_id
                cid = msg_id
                msg_id += 1
                await ws.send(json.dumps({"id": cid, "method": method, "params": params or {}}))
                while True:
                    raw = await ws.recv()
                    data = json.loads(raw)
                    if data.get("id") == cid:
                        return data.get("result", {})

            await send_cmd("Page.enable")
            await send_cmd("Emulation.setDeviceMetricsOverride", {
                "width": 1920,
                "height": 1080,
                "deviceScaleFactor": 1,
                "mobile": False
            })

            file_url = html_file_path.resolve().as_uri()
            print(f"Navigating to {file_url} ...", flush=True)
            await send_cmd("Page.navigate", {"url": file_url})

            # Wait 2.5s for fonts to settle
            await asyncio.sleep(2.5)

            print("Capturing 1920x1080 screenshot ...", flush=True)
            res = await send_cmd("Page.captureScreenshot", {"format": "png"})
            data_b64 = res.get("data")
            if not data_b64:
                raise RuntimeError(f"Failed to capture screenshot: {res}")

            img_bytes = base64.b64decode(data_b64)
            png_output_path.parent.mkdir(parents=True, exist_ok=True)
            png_output_path.write_bytes(img_bytes)
            print(f"Saved screenshot to {png_output_path} ({len(img_bytes)} bytes)", flush=True)

            # Also mirror to brain directory if exists
            if BRAIN_DIR.exists():
                brain_target = BRAIN_DIR / png_output_path.name
                brain_target.write_bytes(img_bytes)
                print(f"Mirrored screenshot to brain: {brain_target}", flush=True)

    finally:
        try:
            proc.terminate()
            proc.wait(timeout=3)
        except Exception:
            proc.kill()
        shutil.rmtree(profile_dir, ignore_errors=True)

def main():
    print("Generating Metric-Numerals A/B Evaluation HTML...", flush=True)
    html_content = build_html()
    HTML_OUTPUT_PATH.write_text(html_content, encoding="utf-8")
    print(f"Saved evaluation HTML to {HTML_OUTPUT_PATH} ({len(html_content)} bytes)", flush=True)

    print("Launching headless Chrome for 1920x1080 screenshot capture...", flush=True)
    asyncio.run(capture_page(HTML_OUTPUT_PATH, PNG_OUTPUT_PATH))

    if PNG_OUTPUT_PATH.exists():
        size = PNG_OUTPUT_PATH.stat().st_size
        print(f"SUCCESS: Screenshot verified at {PNG_OUTPUT_PATH} ({size} bytes)", flush=True)
    else:
        raise FileNotFoundError(f"Screenshot was not generated at {PNG_OUTPUT_PATH}")

if __name__ == "__main__":
    main()
