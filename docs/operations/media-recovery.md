# Media Recovery

This site stores client-uploaded media outside the git repository.

Images uploaded through Django admin are saved through `ImageField` and
`FileField` fields. In production, those uploads are routed to Cloudinary. The
database stores file names such as `projects/covers/example.jpg`, while
Cloudinary stores the actual image bytes.

If the Cloudinary account expires, is deleted, or becomes unavailable, the
database can still point at the old file names, but the public image URLs will
no longer return the images. That is why cloning the repository does not restore
admin-uploaded images: git contains the code, templates, static CSS, and static
assets, but it does not contain files uploaded by the client through the admin.

## Inventory First

Run the media audit command against the database you want to inspect:

```bash
python manage.py audit_media
```

For spreadsheet-friendly output:

```bash
python manage.py audit_media --format csv
```

The command lists the model, object id, object label, field name, stored file
name/path, generated URL if available, and any errors. By default it does not
ask the storage backend whether files exist, so it can inspect database
references without Cloudinary credentials.

If Cloudinary or local media storage is available and you want an existence
check, run:

```bash
python manage.py audit_media --check-exists
```

## Recovery Options

A. Reactivate or renew the same Cloudinary account if the assets still exist.
This is the safest first option because the database references may already
match the stored Cloudinary public IDs.

B. Export or download the old Cloudinary assets if account access is restored.
Keep the original folder paths and filenames where possible so existing
database references continue to resolve.

C. Create a new client-owned Cloudinary account and re-upload images through
Django admin. This creates fresh stored file references using the active
production storage backend.

D. Recover the original image files from client or local backups if the
Cloudinary assets are gone. Re-upload them through Django admin or through a
controlled import command.

## Recommended Path For JAT21

1. Run `python manage.py audit_media` against the current production database or
   a safe database export.
2. Use the inventory to identify every missing project cover, gallery image,
   site logo, social sharing image, portrait, and CV file reference.
3. Try to restore access to the original Cloudinary account before changing
   production settings or database values.
4. If the original assets still exist, renew/reactivate Cloudinary and confirm
   the existing URLs resolve.
5. If the assets are gone, gather original files from the client or backups,
   create a client-owned Cloudinary account, configure production credentials,
   and re-upload through Django admin.
6. After recovery, run the audit again and spot-check the public project pages.

Do not redesign or restructure the site as part of media recovery. The image
problem is primarily about stored uploaded files and production media storage,
not page layout or visual design.
