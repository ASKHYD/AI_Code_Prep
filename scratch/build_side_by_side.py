"""
scratch/build_side_by_side.py

Generates dual-resolution side-by-side comparison images placing each real
Streamlit app screenshot next to its corresponding Phase 1 mockup:
  - Home: docs/screenshots/r3/home_real_{res}.png vs docs/screenshots/r3/home_{res}.png
  - Practice: docs/screenshots/r3/practice_real_{res}.png vs docs/screenshots/r3/practice_{res}.png
  - Mock: docs/screenshots/r3/mock_real_{res}.png vs docs/screenshots/r3/mock_{res}.png
  - Dashboard: docs/screenshots/r3/dashboard_real_{res}.png vs docs/screenshots/r3/dashboard_{res}.png

Outputs to docs/screenshots/r3/{screen}_comparison_{res}.png
"""

from __future__ import annotations

import pathlib
from PIL import Image, ImageDraw, ImageFont

WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS_DIR = WORKSPACE_ROOT / "docs" / "screenshots" / "r3"
BRAIN_DIR = pathlib.Path(
    r"C:\Users\MS Computer\.gemini\antigravity\brain\a88a339d-8602-40c1-9fa8-9253ebf3f144"
)

SCREENS = ["home", "practice", "mock", "dashboard"]
RESOLUTIONS = ["1920x1080", "1600x1000"]

HEADER_HEIGHT = 64
BORDER_WIDTH = 2
CANVAS_BG = (251, 250, 247)  # #FBFAF7
HEADER_BG = (23, 23, 18)     # #171712 Deep ink
TEXT_COLOR = (255, 255, 255)
ACCENT_MOCK = (108, 76, 241) # Lilac/Violet partner
ACCENT_REAL = (21, 128, 61)  # Primary CTA green


def build_comparison(screen: str, res: str) -> pathlib.Path:
    mock_path = DOCS_DIR / f"{screen}_{res}.png"
    real_path = DOCS_DIR / f"{screen}_real_{res}.png"

    if not mock_path.exists():
        raise FileNotFoundError(f"Mockup screenshot not found: {mock_path}")
    if not real_path.exists():
        raise FileNotFoundError(f"Real app screenshot not found: {real_path}")

    img_mock = Image.open(mock_path).convert("RGB")
    img_real = Image.open(real_path).convert("RGB")

    # Target equal height
    target_height = min(img_mock.height, img_real.height)
    if img_mock.height != target_height:
        scale = target_height / img_mock.height
        img_mock = img_mock.resize((int(img_mock.width * scale), target_height), Image.Resampling.LANCZOS)
    if img_real.height != target_height:
        scale = target_height / img_real.height
        img_real = img_real.resize((int(img_real.width * scale), target_height), Image.Resampling.LANCZOS)

    total_width = img_mock.width + img_real.width + BORDER_WIDTH
    total_height = target_height + HEADER_HEIGHT

    composite = Image.new("RGB", (total_width, total_height), CANVAS_BG)
    draw = ImageDraw.Draw(composite)

    # Header bar
    draw.rectangle([0, 0, total_width, HEADER_HEIGHT], fill=HEADER_BG)

    # Load font if available, else default
    try:
        font_large = ImageFont.truetype("arial.ttf", 22)
        font_sub = ImageFont.truetype("arial.ttf", 15)
    except Exception:
        font_large = ImageFont.load_default()
        font_sub = font_large

    # Left Header: Phase 1 Mockup
    mock_title = f"PHASE 1 SPECIFICATION MOCKUP — {screen.upper()} ({res})"
    mock_desc = "Direction A Pure HTML/CSS Static Reference"
    draw.text((24, 12), mock_title, fill=TEXT_COLOR, font=font_large)
    draw.text((24, 38), mock_desc, fill=(180, 180, 175), font=font_sub)

    # Right Header: Phase 2 Real App
    right_x = img_mock.width + BORDER_WIDTH + 24
    real_title = f"PHASE 2 LIVE STREAMLIT APP — {screen.upper()} ({res})"
    real_desc = "Direction A Implemented Local Streamlit Engine"
    draw.text((right_x, 12), real_title, fill=(220, 245, 220), font=font_large)
    draw.text((right_x, 38), real_desc, fill=(180, 210, 180), font=font_sub)

    # Paste screenshots
    composite.paste(img_mock, (0, HEADER_HEIGHT))
    composite.paste(img_real, (img_mock.width + BORDER_WIDTH, HEADER_HEIGHT))

    # Divider line
    draw.line(
        [(img_mock.width, 0), (img_mock.width, total_height)],
        fill=(231, 225, 214), # #E7E1D6
        width=BORDER_WIDTH,
    )

    out_path = DOCS_DIR / f"{screen}_comparison_{res}.png"
    composite.save(out_path, format="PNG", optimize=True)
    print(f"[Side-by-Side] Generated: {out_path} ({composite.width}x{composite.height})")

    if BRAIN_DIR.exists():
        brain_out = BRAIN_DIR / f"{screen}_comparison_{res}.png"
        composite.save(brain_out, format="PNG")
        print(f"[Side-by-Side] Mirrored to brain: {brain_out}")

    return out_path


def main():
    print("================ GENERATING DUAL-RESOLUTION SIDE-BY-SIDES ================")
    BRAIN_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    for screen in SCREENS:
        for res in RESOLUTIONS:
            build_comparison(screen, res)
            count += 1
    print(f"\n✅ Successfully built all {count} dual-resolution side-by-side comparison images!")


if __name__ == "__main__":
    main()
