import csv
import sys
from itertools import chain

from django.apps import apps
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.db import OperationalError, ProgrammingError
from django.db.models import FileField

FIELD_NAMES = (
    "model",
    "object_id",
    "object_label",
    "field",
    "stored_name",
    "url",
    "exists",
    "error",
)


class Command(BaseCommand):
    help = "List database references held in FileField and ImageField fields."

    def add_arguments(self, parser):
        parser.add_argument(
            "--format",
            choices=("text", "csv"),
            default="text",
            help="Output format. Defaults to a readable text table.",
        )
        parser.add_argument(
            "--check-exists",
            action="store_true",
            help=(
                "Ask the active storage backend whether each file exists. "
                "This may contact remote storage in production."
            ),
        )

    def handle(self, *args, **options):
        rows = list(self._iter_media_rows(check_exists=options["check_exists"]))

        if options["format"] == "csv":
            self._write_csv(rows)
            return

        storage_backend = (
            f"{default_storage.__class__.__module__}.{default_storage.__class__.__name__}"
        )
        self.stdout.write(f"Storage backend: {storage_backend}")
        self.stdout.write(f"Media references found: {len(rows)}")
        self.stdout.write("")
        self._write_text(rows)

    def _iter_media_rows(self, *, check_exists: bool):
        for model in apps.get_models():
            fields = [
                field
                for field in model._meta.get_fields()
                if isinstance(field, FileField) and not field.many_to_many and not field.one_to_many
            ]
            if not fields:
                continue

            try:
                objects = model.objects.all().iterator()
                first = next(objects, None)
            except (OperationalError, ProgrammingError) as exc:
                self.stderr.write(self.style.WARNING(f"Skipping {model._meta.label}: {exc}"))
                continue

            iterable = () if first is None else chain((first,), objects)
            for obj in iterable:
                model_label = model._meta.label
                object_id = obj.pk
                object_label = self._safe_object_label(obj)

                for field in fields:
                    file_value = getattr(obj, field.name)
                    stored_name = getattr(file_value, "name", "") or ""
                    if not stored_name:
                        continue

                    url, url_error = self._safe_url(file_value)
                    exists, exists_error = self._safe_exists(stored_name, check_exists=check_exists)
                    error = "; ".join(part for part in (url_error, exists_error) if part)

                    yield {
                        "model": model_label,
                        "object_id": object_id,
                        "object_label": object_label,
                        "field": field.name,
                        "stored_name": stored_name,
                        "url": url,
                        "exists": exists,
                        "error": error,
                    }

    def _safe_object_label(self, obj):
        try:
            return str(obj)
        except Exception as exc:  # pragma: no cover - defensive against custom __str__
            return f"<error: {exc}>"

    def _safe_url(self, file_value):
        try:
            return file_value.url, ""
        except Exception as exc:
            return "", f"url: {exc}"

    def _safe_exists(self, stored_name: str, *, check_exists: bool):
        if not check_exists:
            return "not checked", ""

        try:
            return str(default_storage.exists(stored_name)), ""
        except Exception as exc:
            return "error", f"exists: {exc}"

    def _write_csv(self, rows):
        writer = csv.DictWriter(sys.stdout, fieldnames=FIELD_NAMES)
        writer.writeheader()
        writer.writerows(rows)

    def _write_text(self, rows):
        if not rows:
            self.stdout.write("No stored media references found.")
            return

        for row in rows:
            self.stdout.write("\t".join(str(row[field]) for field in FIELD_NAMES))
