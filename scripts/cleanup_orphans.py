"""One-time script: remove gallery files that are not referenced by any ProjectImage."""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()

from portfolio.models import ProjectImage  # noqa: E402

referenced = set(
    os.path.basename(p)
    for p in ProjectImage.objects.values_list("image", flat=True)
)

gallery_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "media", "projects", "gallery")
on_disk = set(os.listdir(gallery_dir))
orphans = sorted(on_disk - referenced)

if not orphans:
    print("Clean — no orphaned files.")
    sys.exit(0)

print(f"Orphaned files ({len(orphans)}):")
for f in orphans:
    print(f"  {f}")

answer = input("\nDelete all of the above? [yes/no]: ").strip().lower()
if answer != "yes":
    print("Aborted.")
    sys.exit(0)

for f in orphans:
    path = os.path.join(gallery_dir, f)
    os.remove(path)
    print(f"  deleted: {f}")

print(f"\nDone. {len(orphans)} file(s) removed.")
