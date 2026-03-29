"""
Hero spec v3 visual audit.

Captures screenshots for all 14 audit cases at desktop/tablet/mobile viewports,
then restores the database to its original state.

Artifacts: artifacts/visual-audit/hero-audit-YYYY-MM-DD/
Filename:  {case_id:02d}-{case_slug}-{vp_name}.png

Usage:
    uv run python scripts/audit_hero_spec.py

Server: must be running on localhost:8000
    uv run python manage.py runserver --settings=config.settings.dev
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

import django  # noqa: E402
django.setup()

from asgiref.sync import sync_to_async       # noqa: E402
from PIL import Image as PILImage            # noqa: E402
from django.core.files.base import ContentFile  # noqa: E402
from playwright.async_api import async_playwright  # noqa: E402
from apps.core.models import SiteSettings    # noqa: E402
from apps.projects.models import Project     # noqa: E402

# ── Config ────────────────────────────────────────────────────────────────────

DATE = datetime.date.today().isoformat()
OUT  = ROOT / "artifacts" / "visual-audit" / f"hero-audit-{DATE}"
BASE = "http://localhost:8000"

VIEWPORTS = [
    ("desktop", {"width": 1440, "height": 900}),
    ("tablet",  {"width": 768,  "height": 1024}),
    ("mobile",  {"width": 390,  "height": 844}),
]

# ── Content fixtures ───────────────────────────────────────────────────────────

# Short content: typical demo-length values
SHORT_NAME   = "Demo Architecture Studio"
SHORT_LABEL  = "Architecture & Urbanism"
SHORT_TAGLINE = "Architectural design shaped by context, clarity, and identity."

# Long content stress: exercises the vertical budget limit
LONG_NAME    = "Beaumont Whitfield Kellerman Partnership"
LONG_LABEL   = "Architecture · Urban Design · Conservation"
LONG_TAGLINE = (
    "Our practice establishes a rigorous architectural language through sustained "
    "engagement with site, programme, structure, and material — in that order."
)

# ── Synthetic images ───────────────────────────────────────────────────────────

def _make_jpeg(r: int, g: int, b: int, w: int = 1440, h: int = 900) -> bytes:
    img = PILImage.new("RGB", (w, h), color=(r, g, b))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()


# High contrast = near-black image (overlay on dark → text very readable)
DARK_IMAGE  = _make_jpeg(20, 18, 15)
# Low contrast = near-white warm image (overlay on light → hardest legibility case)
LIGHT_IMAGE = _make_jpeg(235, 233, 225)

# ── ORM helpers ───────────────────────────────────────────────────────────────

@sync_to_async
def settings_snapshot() -> dict:
    s = SiteSettings.load()
    return {
        "site_name":   s.site_name,
        "tagline":     s.tagline,
        "hero_label":  s.hero_label,
        "hero_compact": s.hero_compact,
    }


@sync_to_async
def apply_settings(**kwargs) -> None:
    s = SiteSettings.load()
    for k, v in kwargs.items():
        setattr(s, k, v)
    s.save()


@sync_to_async
def cover_snapshot() -> tuple[str | None, bytes | None]:
    """Read original cover bytes before any manipulation."""
    p = Project.objects.filter(featured=True).order_by("order").first()
    if not p or not p.cover_image:
        return None, None
    try:
        with p.cover_image.open("rb") as f:
            return p.cover_image.name, f.read()
    except Exception:
        return p.cover_image.name, None


@sync_to_async
def set_hero_cover(data: bytes | None, name: str = "_audit_tmp.jpg") -> None:
    """Replace or remove the cover on the first featured project."""
    p = Project.objects.filter(featured=True).order_by("order").first()
    if not p:
        return
    if p.cover_image:
        p.cover_image.delete(save=False)
    if data is not None:
        p.cover_image.save(name, ContentFile(data), save=True)
    else:
        p.cover_image = ""
        p.save(update_fields=["cover_image"])


@sync_to_async
def restore_hero_cover(orig_name: str | None, orig_data: bytes | None) -> None:
    """Wipe current cover and re-attach the original bytes."""
    p = Project.objects.filter(featured=True).order_by("order").first()
    if not p:
        return
    if p.cover_image:
        p.cover_image.delete(save=False)
    if orig_data:
        fname = (orig_name or "cover.jpg").split("/")[-1]
        p.cover_image.save(fname, ContentFile(orig_data), save=True)
    else:
        p.cover_image = ""
        p.save(update_fields=["cover_image"])


# ── Screenshot helper ──────────────────────────────────────────────────────────

async def shoot(
    browser,
    case_id: int,
    slug: str,
    post_load_js: str = "",
) -> list[str]:
    """Take one screenshot per viewport for the given case. Returns relative paths."""
    paths = []
    for vp_name, vp in VIEWPORTS:
        fname = OUT / f"{case_id:02d}-{slug}-{vp_name}.png"
        ctx  = await browser.new_context(viewport=vp)
        page = await ctx.new_page()
        await page.goto(f"{BASE}/", wait_until="networkidle", timeout=20_000)
        await page.wait_for_timeout(600)
        await page.evaluate("window.scrollTo(0, 0)")
        if post_load_js:
            await page.evaluate(post_load_js)
            await page.wait_for_timeout(150)
        await page.screenshot(path=str(fname), full_page=False)  # viewport crop = hero focus
        await ctx.close()
        rel = str(fname.relative_to(ROOT))
        paths.append(rel)
        print(f"    {fname.name}")
    return paths


# ── JS helpers ────────────────────────────────────────────────────────────────

REMOVE_SECOND_CTA = """
    const btns = document.querySelectorAll('.hero__cta .btn');
    if (btns.length > 1) btns[1].remove();
"""

# ── Main audit ────────────────────────────────────────────────────────────────

async def run_audit(browser) -> list[dict]:
    snap_settings = await settings_snapshot()
    orig_name, orig_data = await cover_snapshot()

    label_present = bool(snap_settings["hero_label"])
    print(f"\n  DB snapshot: site_name={snap_settings['site_name']!r}, "
          f"hero_label={snap_settings['hero_label']!r}, "
          f"hero_compact={snap_settings['hero_compact']}")

    results: list[dict] = []

    # ── Cases 1–3: Default responsive (desktop / tablet / mobile) ─────────────
    # The seed state is: no hero_label, standard tagline, compact=False.
    # These three viewports are the canonical "default state" screenshots.
    print("\n[01-03] Default responsive — desktop / tablet / mobile")
    await apply_settings(**snap_settings)  # ensure default
    paths = await shoot(browser, 1, "default-responsive")
    results.append({
        "ids": [1, 2, 3],
        "name": "Default responsive",
        "slug": "01-default-responsive",
        "paths": paths,
        "vp_note": "desktop=paths[0], tablet=paths[1], mobile=paths[2]",
    })

    # ── Case 4: Short content + default hero image ─────────────────────────────
    # Explicit short label + unchanged tagline + current cover.
    print("\n[04] Short content + default hero image")
    await apply_settings(
        site_name=SHORT_NAME,
        tagline=SHORT_TAGLINE,
        hero_label=SHORT_LABEL,
        hero_compact=False,
    )
    paths = await shoot(browser, 4, "short-content-default-image")
    results.append({
        "ids": [4], "name": "Short content + default image",
        "slug": "04-short-content-default-image", "paths": paths,
    })

    # ── Case 5: Long content stress + default image ────────────────────────────
    print("\n[05] Long content stress + default hero image")
    await apply_settings(
        site_name=LONG_NAME,
        tagline=LONG_TAGLINE,
        hero_label=LONG_LABEL,
        hero_compact=False,
    )
    paths = await shoot(browser, 5, "long-content-stress")
    results.append({
        "ids": [5], "name": "Long content stress",
        "slug": "05-long-content-stress", "paths": paths,
    })

    # ── Case 6: hero_compact + long content stress ─────────────────────────────
    print("\n[06] hero_compact=True + long content stress")
    await apply_settings(
        site_name=LONG_NAME,
        tagline=LONG_TAGLINE,
        hero_label=LONG_LABEL,
        hero_compact=True,
    )
    paths = await shoot(browser, 6, "compact-long-content")
    results.append({
        "ids": [6], "name": "hero_compact + long content",
        "slug": "06-compact-long-content", "paths": paths,
    })

    # ── Case 7: No hero_label ──────────────────────────────────────────────────
    print("\n[07] No hero_label (label absent from DOM)")
    await apply_settings(
        site_name=SHORT_NAME,
        tagline=SHORT_TAGLINE,
        hero_label="",
        hero_compact=False,
    )
    paths = await shoot(browser, 7, "no-hero-label")
    results.append({
        "ids": [7], "name": "No hero_label",
        "slug": "07-no-hero-label", "paths": paths,
    })

    # ── Case 8: No tagline ─────────────────────────────────────────────────────
    print("\n[08] No tagline (tagline absent from DOM)")
    await apply_settings(
        site_name=SHORT_NAME,
        tagline="",
        hero_label=SHORT_LABEL,
        hero_compact=False,
    )
    paths = await shoot(browser, 8, "no-tagline")
    results.append({
        "ids": [8], "name": "No tagline",
        "slug": "08-no-tagline", "paths": paths,
    })

    # ── Case 9: Single CTA only (JS removes second button post-load) ───────────
    print("\n[09] Single CTA only")
    await apply_settings(
        site_name=SHORT_NAME,
        tagline=SHORT_TAGLINE,
        hero_label=SHORT_LABEL,
        hero_compact=False,
    )
    paths = await shoot(browser, 9, "single-cta", post_load_js=REMOVE_SECOND_CTA)
    results.append({
        "ids": [9], "name": "Single CTA only",
        "slug": "09-single-cta", "paths": paths,
    })

    # ── Case 10: No background image (placeholder state) ──────────────────────
    print("\n[10] No background image / placeholder state")
    await apply_settings(
        site_name=SHORT_NAME,
        tagline=SHORT_TAGLINE,
        hero_label=SHORT_LABEL,
        hero_compact=False,
    )
    await set_hero_cover(None)  # detach cover → triggers hero__bg--placeholder
    paths = await shoot(browser, 10, "no-hero-image")
    results.append({
        "ids": [10], "name": "No background image",
        "slug": "10-no-hero-image", "paths": paths,
    })
    await restore_hero_cover(orig_name, orig_data)  # restore for image cases

    # ── Case 11: Short content + high-contrast (dark) image ───────────────────
    print("\n[11] Short content + high-contrast dark image")
    await apply_settings(
        site_name=SHORT_NAME,
        tagline=SHORT_TAGLINE,
        hero_label=SHORT_LABEL,
        hero_compact=False,
    )
    await set_hero_cover(DARK_IMAGE, "_audit_dark.jpg")
    paths = await shoot(browser, 11, "short-content-dark-image")
    results.append({
        "ids": [11], "name": "Short content + dark image",
        "slug": "11-short-content-dark-image", "paths": paths,
    })

    # ── Case 12: Short content + low-contrast (light) image ───────────────────
    print("\n[12] Short content + low-contrast light image")
    await set_hero_cover(LIGHT_IMAGE, "_audit_light.jpg")
    paths = await shoot(browser, 12, "short-content-light-image")
    results.append({
        "ids": [12], "name": "Short content + light image",
        "slug": "12-short-content-light-image", "paths": paths,
    })

    # ── Case 13: Long content + high-contrast (dark) image ────────────────────
    print("\n[13] Long content + high-contrast dark image")
    await apply_settings(
        site_name=LONG_NAME,
        tagline=LONG_TAGLINE,
        hero_label=LONG_LABEL,
        hero_compact=False,
    )
    await set_hero_cover(DARK_IMAGE, "_audit_dark.jpg")
    paths = await shoot(browser, 13, "long-content-dark-image")
    results.append({
        "ids": [13], "name": "Long content + dark image",
        "slug": "13-long-content-dark-image", "paths": paths,
    })

    # ── Case 14: Long content + low-contrast (light) image ────────────────────
    print("\n[14] Long content + low-contrast light image")
    await set_hero_cover(LIGHT_IMAGE, "_audit_light.jpg")
    paths = await shoot(browser, 14, "long-content-light-image")
    results.append({
        "ids": [14], "name": "Long content + light image",
        "slug": "14-long-content-light-image", "paths": paths,
    })

    # ── Restore ───────────────────────────────────────────────────────────────
    await restore_hero_cover(orig_name, orig_data)
    await apply_settings(**snap_settings)
    print("\n  ✓ DB restored to original state")

    return results


async def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    print(f"Output: {OUT}/")

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        results = await run_audit(browser)
        await browser.close()

    # ── Artifact manifest ─────────────────────────────────────────────────────
    total = sum(len(r.get("paths", [])) for r in results)
    print(f"\n{'=' * 60}")
    print(f"ARTIFACTS  ({total} screenshots)")
    print(f"{'=' * 60}")
    for r in results:
        print(f"\n  [{','.join(str(i) for i in r['ids'])}] {r['name']}")
        for p in r.get("paths", []):
            print(f"    {p}")

    print(f"\n  Directory: artifacts/visual-audit/hero-audit-{DATE}/")


asyncio.run(main())
