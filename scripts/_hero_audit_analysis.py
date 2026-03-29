"""Pixel analysis for hero-audit-2026-03-29 screenshots."""
from pathlib import Path
from PIL import Image
import numpy as np

DIR = Path("artifacts/visual-audit/hero-audit-2026-03-29")

CASES = [
    (1,  "01-default-responsive"),
    (4,  "04-short-content-default-image"),
    (5,  "05-long-content-stress"),
    (6,  "06-compact-long-content"),
    (7,  "07-no-hero-label"),
    (8,  "08-no-tagline"),
    (9,  "09-single-cta"),
    (10, "10-no-hero-image"),
    (11, "11-short-content-dark-image"),
    (12, "12-short-content-light-image"),
    (13, "13-long-content-dark-image"),
    (14, "14-long-content-light-image"),
]

VP_LABEL = "desktop"


def bright(arr, y1, y2, x1, x2):
    return float(np.mean(arr[y1:y2, x1:x2]))


def stddev(arr, y1, y2, x1, x2):
    return float(np.std(arr[y1:y2, x1:x2]))


print(f"{'#':<3} {'file':<45} {'title_bg':>9} {'top_br':>7} {'top_std':>8} {'bot_br':>8}")
print("-" * 90)

for case_id, slug in CASES:
    fname = DIR / f"{slug}-{VP_LABEL}.png"
    if not fname.exists():
        print(f"{case_id:<3}  NOT FOUND: {fname.name}")
        continue

    img = Image.open(fname).convert("RGB")
    arr = np.array(img, dtype=float)
    h, w = arr.shape[:2]

    # title zone: ~52-72% down the viewport (where h1 lives in bottom-anchored hero)
    ty1, ty2 = int(h * 0.52), int(h * 0.72)
    # top zone: top 20% of viewport (upper image area)
    top_y1, top_y2 = 0, int(h * 0.20)
    # bottom zone: bottom 15% (heaviest overlay)
    bot_y1, bot_y2 = int(h * 0.85), h

    title_br = bright(arr, ty1, ty2, 60, min(900, w))
    top_br   = bright(arr, top_y1, top_y2, 0, w)
    top_std  = stddev(arr, top_y1, top_y2, 0, w)
    bot_br   = bright(arr, bot_y1, bot_y2, 0, w)

    print(f"{case_id:<3}  {fname.name:<45} {title_br:9.1f} {top_br:7.1f} {top_std:8.1f} {bot_br:8.1f}")

print()
print("Metrics:")
print("  title_bg  — mean brightness of title zone (heatmap 0=black 255=white)")
print("               <80 = good overlay darkness for white text")
print("               >120 = legibility concern (light background behind text)")
print("  top_br    — mean brightness of top 20% (upper image area)")
print("               ~20 = dark/near-black image  |  ~230 = light/near-white image")
print("               ~50-180 = photographic image likely showing detail")
print("  top_std   — pixel stddev in top 20%")
print("               <15 = flat/synthetic  |  >30 = photographic texture")
print("  bot_br    — mean brightness of bottom 15% (should be darkest zone ≈20-40)")

print()
print("Thresholds from spec:")
print("  AC-12 (long-content legibility): title_bg must stay <80 in all cases")
print("  AC-13 (short-content image visible): top_br must be meaningfully non-zero")
print("          and top_std > 15 for photographic cases (image not buried by overlay)")
