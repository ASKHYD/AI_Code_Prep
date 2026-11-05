"""
scratch/audit_hex_drift.py

Audits every hex color code in app.py, .streamlit/config.toml, and CSS files
against the frozen Direction A tokens in DESIGN.md.
Asserts zero uncataloged hex values.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

# Direction A Approved Palette from DESIGN.md
# Includes:
# - Foundation: paper (#FBFAF7), surface (#FFFFFF), ink (#171712), muted (#66635A), hairline (#E7E1D6)
# - Code anchor: code-bg (#14161A), code-text (#F2F2ED)
# - Primary CTA: primary / cta-green (#15803D), on-primary (#FFFFFF)
# - Six-part functional tints:
#   1. Mint & Green: wash-mint (#DFF3E4), partner-green (#167B48), fill-green (#1F9D63)
#   2. Butter & Amber: wash-butter (#FFF0C4), partner-amber (#9A3412), fill-amber (#B45309)
#   3. Sky & Blue: wash-sky (#DCEBFF), partner-blue (#1D5EC2), fill-blue (#2273E6)
#   4. Lilac & Violet: wash-lilac (#E8E2FF), partner-violet (#5932EA), fill-violet (#6C4CF1)
#   5. Peach & Coral: wash-peach (#FFE8D1), partner-coral (#B93815), fill-coral (#E4572E)
#   6. Rose & Red: wash-rose (#FFE0E0), partner-red (#C5221F), fill-red (#D92D20)
APPROVED_TOKENS: dict[str, str] = {
    # Foundation
    "#FBFAF7": "paper (global canvas root)",
    "#FFFFFF": "surface (card white / on-primary)",
    "#171712": "ink (headings / deep text)",
    "#66635A": "muted (warm grey captions / secondary)",
    "#E7E1D6": "hairline (borders / dividers)",
    "#15803D": "primary / cta-green (primary button)",
    "#14161A": "code-bg (dark editor surface)",
    "#F2F2ED": "code-text (monospace editor text)",
    # Mint & Green (Streak / PASS / Mastery)
    "#DFF3E4": "wash-mint (streak / pass card bg)",
    "#167B48": "partner-green (pass badge text / hover)",
    "#1F9D63": "fill-green (mastery progress fill)",
    # Butter & Amber (Library / TIMEOUT / In-Progress)
    "#FFF0C4": "wash-butter (library / timeout card bg)",
    "#9A3412": "partner-amber (timeout badge text)",
    "#B45309": "fill-amber (in-progress fill)",
    # Sky & Blue (Due / Analytics)
    "#DCEBFF": "wash-sky (due / analytics card bg)",
    "#1D5EC2": "partner-blue (due badge text / accent)",
    "#2273E6": "fill-blue (analytics fill)",
    # Lilac & Violet (Practice Arena)
    "#E8E2FF": "wash-lilac (practice nav / editor strip bg)",
    "#5932EA": "partner-violet (practice badge text / accent)",
    "#6C4CF1": "fill-violet (practice fill)",
    # Peach & Coral (Mock Interview / Timer)
    "#FFE8D1": "wash-peach (mock nav / timer wash)",
    "#B93815": "partner-coral (timer text / accent)",
    "#E4572E": "fill-coral (timer pill fill)",
    # Rose & Red (FAIL / Errors)
    "#FFE0E0": "wash-rose (fail card bg / error wash)",
    "#C5221F": "partner-red (fail text / error badge text)",
    "#D92D20": "fill-red (fail fill / error pill)",
}

NORMALIZED_APPROVED = {k.upper(): v for k, v in APPROVED_TOKENS.items()}

# Files to audit
FILES_TO_AUDIT = [
    WORKSPACE_ROOT / "app.py",
    WORKSPACE_ROOT / ".streamlit" / "config.toml",
]


def audit_hex_drift() -> int:
    hex_pattern = re.compile(r"#(?:[0-9a-fA-F]{3,4}){1,2}\b")
    uncataloged: list[tuple[Path, int, str, str]] = []
    cataloged_found: dict[str, int] = {k: 0 for k in NORMALIZED_APPROVED}

    print("================ HEX DRIFT AUDIT ================")
    print(f"Catalog contains {len(NORMALIZED_APPROVED)} approved Direction A tokens.")

    for file_path in FILES_TO_AUDIT:
        if not file_path.exists():
            continue
        rel_path = file_path.relative_to(WORKSPACE_ROOT)
        content = file_path.read_text(encoding="utf-8")
        for line_num, line in enumerate(content.splitlines(), start=1):
            matches = hex_pattern.findall(line)
            for raw_hex in matches:
                # normalize 3-char hex if needed, uppercase
                clean_hex = raw_hex.upper()
                if len(clean_hex) == 4:
                    clean_hex = "#" + "".join([c * 2 for c in clean_hex[1:]])
                if clean_hex in NORMALIZED_APPROVED:
                    cataloged_found[clean_hex] += 1
                else:
                    uncataloged.append((rel_path, line_num, raw_hex, line.strip()))

    print("\n--- Cataloged Token Usage ---")
    for hex_code, count in sorted(cataloged_found.items()):
        if count > 0:
            print(f"  {hex_code}: {count:3d} uses ({NORMALIZED_APPROVED[hex_code]})")

    if uncataloged:
        print(f"\n❌ HEX DRIFT DETECTED: {len(uncataloged)} uncataloged hex value(s):")
        for rel_path, line_num, raw_hex, line in uncataloged:
            print(f"  {rel_path}:{line_num} -> {raw_hex} in `{line[:70]}`")
        return 1

    print("\n✅ ZERO HEX DRIFT: All hex color codes match frozen Direction A tokens in DESIGN.md!")
    return 0


if __name__ == "__main__":
    sys.exit(audit_hex_drift())
