"""
Navbar brand spec QA screenshots.

Captures the five state-matrix cases from the approved spec at three viewports.
Also captures the homepage transparent-header state (un-scrolled) for logo inversion QA.

Artifacts: artifacts/visual-audit/nav-brand-qa-YYYY-MM-DD/
Filename:  {case_id:02d}-{slug}-{vp_name}.png

Usage:
    uv run python scripts/audit_nav_brand.py
Server: must be running on localhost:8000
"""
from __future__ import annotations

import asyncio
import datetime
import io
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

import django
django.setup()

from asgiref.sync import sync_to_async
from PIL import Image as PILImage
from django.core.files.base import ContentFile
from playwright.async_api import async_playwright
from apps.core.models import SiteSettings

DATE = datetime.date.today().isoformat()
OUT  = ROOT / "artifacts" / "visual-audit" / f"nav-brand-qa-{DATE}"
BASE = "http://localhost:8000"

VIEWPORTS = [
    ("desktop", {"width": 1440, "height": 900}),
    ("tablet",  {"width": 768,  "height": 1024}),
    ("mobile",  {"width": 390,  "height": 844}),
]

# ── ORM helpers ───────────────────────────────────────────────────────────────

@sync_to_async
def settings_snapshot():
    s = SiteSettings.load()
    return {
        "site_name": s.site_name,
        "nav_name":  s.nav_name,
        "logo":      bool(s.logo),
    }


@sync_to_async
def apply_settings(**kwargs):
    s = SiteSettings.load()
    for k, v in kwargs.items():
        setattr(s, k, v)
    s.save()


@sync_to_async
def set_logo(data: bytes | None):
    s = SiteSettings.load()
    if s.logo:
        s.logo.delete(save=False)
    if data is not None:
        s.logo.save("_audit_nav_logo.png", ContentFile(data), save=True)
    else:
        s.logo = None
        s.save(update_fields=["logo"])


def _make_wordmark_png(width: int, height: int = 40, dark: bool = True) -> bytes:
    """Synthetic wordmark PNG for logo testing."""
    colour = (20, 18, 15) if dark else (220, 218, 210)
    img = PILImage.new("RGBA", (width, height), color=(0, 0, 0, 0))
    # Draw a filled rectangle to simulate a wordmark silhouette
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    draw.rectangle([4, 8, width - 4, height - 8], fill=(*colour, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# Normal wordmark (≈ 200×40): fits within max-width
NORMAL_LOGO = _make_wordmark_png(200)
# Wide wordmark (320×40): exceeds 160px max-width cap
WIDE_LOGO   = _make_wordmark_png(320)

# ── Screenshot helper ─────────────────────────────────────────────────────────

async def shoot(browser, case_id: int, slug: str, vp_crop: str = "nav") -> list[str]:
    """
    Capture at each viewport.
    vp_crop='nav' → screenshot just the header region (top 100px).
    vp_crop='full' → full-page screenshot.
    """
    paths = []
    for vp_name, vp in VIEWPORTS:
        fname = OUT / f"{case_id:02d}-{slug}-{vp_name}.png"
        ctx  = await browser.new_context(viewport=vp)
        page = await ctx.new_page()
        await page.goto(f"{BASE}/", wait_until="networkidle", timeout=20_000)
        await page.wait_for_timeout(500)
        if vp_crop == "nav":
            # Clip to header height + a small buffer
            header = await page.query_selector(".site-header")
            box = await header.bounding_box()
            clip = {"x": 0, "y": 0, "width": vp["width"], "height": int(box["height"]) + 4}
            await page.screenshot(path=str(fname), clip=clip)
        else:
            await page.screenshot(path=str(fname), full_page=False)
        await ctx.close()
        paths.append(str(fname.relative_to(ROOT)))
        print(f"    {fname.name}")
    return paths


# ── Main audit ────────────────────────────────────────────────────────────────

async def run_audit(browser):
    snap = await settings_snapshot()
    print(f"\n  DB snapshot: site_name={snap['site_name']!r}, nav_name={snap['nav_name']!r}, logo={snap['logo']}")

    results = []

    # ── A: Long nav_name (no logo) ────────────────────────────────────────────
    print("\n[A] Long nav_name — 'Whitfield Kellerman Partnership' (30 chars)")
    await apply_settings(nav_name="Whitfield Kellerman Partnership")
    await set_logo(None)
    paths = await shoot(browser, 1, "long-nav-name")
    results.append({"id": "A", "name": "Long nav_name", "paths": paths})

    # ── B: No logo + long site_name, no nav_name (safety-net ellipsis case) ───
    print("\n[B] No logo + long site_name + no nav_name (safety net)")
    await apply_settings(
        site_name="Beaumont Whitfield Kellerman Partnership",
        nav_name="",
    )
    paths = await shoot(browser, 2, "long-site-name-no-nav-name")
    results.append({"id": "B", "name": "Long site_name, no nav_name", "paths": paths})

    # ── C: Wide wordmark logo (max-width cap test) ────────────────────────────
    print("\n[C] Wide wordmark logo (320×40 synthetic, exceeds 160px cap)")
    await set_logo(WIDE_LOGO)
    paths = await shoot(browser, 3, "wide-logo")
    results.append({"id": "C", "name": "Wide logo", "paths": paths})

    # ── D: Transparent hero state — logo inversion ────────────────────────────
    # Full viewport crop so the hero + transparent nav are both visible.
    print("\n[D] Transparent hero state — logo over hero image (inversion QA)")
    # Keep wide logo from case C but switch to normal-width for realistic test
    await set_logo(NORMAL_LOGO)
    paths = await shoot(browser, 4, "transparent-hero-logo", vp_crop="full")
    results.append({"id": "D", "name": "Transparent hero + logo", "paths": paths})

    # ── D-text: Transparent hero + text nav_name (white rule) ─────────────────
    print("\n[D-text] Transparent hero state — nav_name text colour (white rule)")
    await set_logo(None)
    await apply_settings(nav_name="Strand Architecture")
    paths = await shoot(browser, 5, "transparent-hero-text", vp_crop="full")
    results.append({"id": "D-text", "name": "Transparent hero + text", "paths": paths})

    # ── E: Mobile menu-open ───────────────────────────────────────────────────
    print("\n[E] Mobile menu-open state — brand + toggle visible on dark overlay")
    await apply_settings(nav_name="Strand Architecture")
    await set_logo(None)

    fname = OUT / "06-mobile-menu-open-mobile.png"
    ctx  = await browser.new_context(viewport={"width": 390, "height": 844})
    page = await ctx.new_page()
    await page.goto(f"{BASE}/", wait_until="networkidle", timeout=20_000)
    await page.wait_for_timeout(400)
    await page.click(".nav__toggle")
    await page.wait_for_timeout(400)
    await page.screenshot(path=str(fname), full_page=False)
    await ctx.close()
    paths = [str(fname.relative_to(ROOT))]
    print(f"    {fname.name}")
    results.append({"id": "E", "name": "Mobile menu-open", "paths": paths})

    # ── E-logo: Mobile menu-open + logo ───────────────────────────────────────
    print("\n[E-logo] Mobile menu-open + logo (logo invert rule)")
    await set_logo(NORMAL_LOGO)

    fname = OUT / "07-mobile-menu-open-logo-mobile.png"
    ctx  = await browser.new_context(viewport={"width": 390, "height": 844})
    page = await ctx.new_page()
    await page.goto(f"{BASE}/", wait_until="networkidle", timeout=20_000)
    await page.wait_for_timeout(400)
    await page.click(".nav__toggle")
    await page.wait_for_timeout(400)
    await page.screenshot(path=str(fname), full_page=False)
    await ctx.close()
    paths = [str(fname.relative_to(ROOT))]
    print(f"    {fname.name}")
    results.append({"id": "E-logo", "name": "Mobile menu-open + logo", "paths": paths})

    # ── Restore ───────────────────────────────────────────────────────────────
    await set_logo(None)
    await apply_settings(site_name=snap["site_name"], nav_name=snap["nav_name"])
    print("\n  ✓ DB restored")

    return results


async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    print(f"Output: {OUT}/")

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        results = await run_audit(browser)
        await browser.close()

    total = sum(len(r["paths"]) for r in results)
    print(f"\n{'=' * 60}")
    print(f"ARTIFACTS  ({total} screenshots)")
    print(f"{'=' * 60}")
    for r in results:
        print(f"\n  [{r['id']}] {r['name']}")
        for p in r["paths"]:
            print(f"    {p}")
    print(f"\n  Directory: artifacts/visual-audit/nav-brand-qa-{DATE}/")


asyncio.run(main())
