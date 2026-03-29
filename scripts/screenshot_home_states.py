"""
Take homepage screenshots in multiple featured-project count states.

States: 6 (primary audit), 4, 3, 1
Viewports: 1440x900, 768x1024, 390x844

Usage: uv run python scripts/screenshot_home_states.py
Server must be running on localhost:8765.
"""

import asyncio
import os
import sys

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

import django
django.setup()

from asgiref.sync import sync_to_async
from playwright.async_api import async_playwright
from apps.projects.models import Project

OUT = "artifacts/visual-audit/home-grid-states"
BASE_URL = "http://localhost:8765"
VIEWPORTS = [(1440, 900), (768, 1024), (390, 844)]


@sync_to_async
def get_all_featured():
    return list(Project.objects.filter(featured=True).order_by("order"))


@sync_to_async
def set_featured_count(all_featured, n):
    for i, p in enumerate(all_featured):
        p.featured = i < n
        p.save(update_fields=["featured"])
    actual = Project.objects.filter(featured=True).count()
    print(f"  DB featured count: {actual}")


async def shoot(label, viewports):
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for w, h in viewports:
            page = await browser.new_page(viewport={"width": w, "height": h})
            await page.goto(f"{BASE_URL}/", wait_until="networkidle")
            path = f"{OUT}/{label}_{w}x{h}.png"
            await page.screenshot(path=path, full_page=True)
            print(f"  saved {path}")
        await browser.close()


async def main():
    all_featured = await get_all_featured()
    print(f"Total featured in DB: {len(all_featured)}")

    states = [6, 4, 3, 1]
    for n in states:
        print(f"\n=== State: {n} featured projects ===")
        await set_featured_count(all_featured, n)
        await shoot(f"home-n{n}", VIEWPORTS)

    # Restore to full set
    print("\n=== Restoring to full featured set ===")
    await set_featured_count(all_featured, len(all_featured))


asyncio.run(main())
print("\nDone. Screenshots in", OUT)
