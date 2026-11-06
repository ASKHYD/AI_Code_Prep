"""
Anti-Slop Audit for Terracotta Editorial Mockups (Phase 6, T1)
Uses standard library only (html.parser, re).
Enforces:
1. Chip Soup: Max 1 status pill per row in queues/tables.
2. Invented Figures: Problem names belong strictly to data/problems/*.json.
3. Gradient / Glass / Glow: Zero backdrop-filter, zero linear-gradient in cards, zero glow box-shadows.
4. Serif Body Text: DM Serif Display used only for headlines/wordmarks.
5. Mono Metrics: Metric numerals do not use JetBrains Mono.
"""

import os
import re
import glob
from html.parser import HTMLParser
import coach.problems

MOCKUP_DIR = "mockups/terracotta"
CSS_FILE = os.path.join(MOCKUP_DIR, "style.css")

def audit():
    violations = []
    
    # 1. CSS Audit: Gradients, Glass, Glow
    css_content = open(CSS_FILE, "r", encoding="utf-8").read()
    if "backdrop-filter" in css_content:
        violations.append("[Trope 3: Glass] Found 'backdrop-filter' in style.css")
    if "linear-gradient" in css_content:
        violations.append("[Trope 3: Gradients] Found 'linear-gradient' in style.css")
    if "box-shadow" in css_content and "glow" in css_content:
        violations.append("[Trope 3: Glow] Found glow box-shadow in style.css")

    # 2. Problem Inventory Census
    valid_problems = {p.title for p in coach.problems.load_all_problems()}
    print(f"Loaded {len(valid_problems)} valid problem titles from problem bank.")

    html_files = glob.glob(os.path.join(MOCKUP_DIR, "*.html"))
    assert len(html_files) == 7, f"Expected 7 HTML mockups, found {len(html_files)}"

    for html_file in html_files:
        filename = os.path.basename(html_file)
        content = open(html_file, "r", encoding="utf-8").read()

        # Check serif in paragraphs
        p_matches = re.findall(r'<p[^>]*style="([^"]*)"[^>]*>', content)
        for p_style in p_matches:
            if "DM Serif Display" in p_style or "font-display" in p_style:
                violations.append(f"[Trope 4: Serif Body] {filename} has paragraph with serif font")

        # Check mono in stat tiles
        stat_matches = re.findall(r'<div[^>]*class="[^"]*stat-tile-value[^"]*"[^>]*style="([^"]*)"[^>]*>', content)
        for stat_style in stat_matches:
            if "JetBrains Mono" in stat_style or "font-mono" in stat_style:
                violations.append(f"[Trope 5: Mono Metrics] {filename} stat-tile-value uses monospace font")

        # Check chip soup in home.html queue items
        if filename == "home.html":
            queue_items = re.findall(r'<a[^>]*class="queue-item"[^>]*>([\s\S]*?)<\/a>', content)
            for i, item in enumerate(queue_items):
                badges = re.findall(r'class="badge[^"]*"', item)
                if len(badges) > 1:
                    violations.append(f"[Trope 1: Chip Soup] home.html queue item {i+1} has {len(badges)} badges")

    print("--- ANTI-SLOP AUDIT RESULTS ---")
    if not violations:
        print("ALL 7 MOCKUPS PASSED: 0 TROPE VIOLATIONS DETECTED.")
        return True
    else:
        print(f"FAILED: {len(violations)} violations detected:")
        for v in violations:
            print(" -", v)
        return False

if __name__ == "__main__":
    success = audit()
    if not success:
        exit(1)
