# Cloudflare R2 Media Storage

JAT21 can store new Django admin uploads in Cloudflare R2 using its
S3-compatible API. This keeps the existing Cloudinary option available, but
removes the hard dependency on a paid Cloudinary renewal for a small portfolio
site.

This change does not recover old images by itself. Missing images still need to
come from an old Cloudinary export, client originals, local backups, or website
archives, then be re-uploaded through Django admin.

## Why R2

Admin-uploaded project images are not committed to git. Production needs durable
object storage because Railway filesystems are ephemeral. Cloudinary handled
that before, but renewal or upgrade cost is too high for this client. R2 is a
lower-cost object store that works with Django through `django-storages` and
`boto3`.

## Create The R2 Bucket

1. In Cloudflare, open **R2 Object Storage**.
2. Create a bucket for site media, for example `jat21-media`.
3. Create an R2 API token with object read/write access to that bucket.
4. Copy the access key ID and secret access key.
5. Copy the account-specific S3 endpoint. It looks like:

```text
https://<account-id>.r2.cloudflarestorage.com
```

For public image delivery, configure either a public R2 custom domain or another
Cloudflare route for the bucket, then use that host as `AWS_S3_CUSTOM_DOMAIN`.
Example:

```text
media.jat21.com
```

## Railway Environment Variables

Set these in the Railway service environment:

```bash
MEDIA_STORAGE_BACKEND=s3
AWS_ACCESS_KEY_ID=<r2-access-key-id>
AWS_SECRET_ACCESS_KEY=<r2-secret-access-key>
AWS_STORAGE_BUCKET_NAME=jat21-media
AWS_S3_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com
AWS_S3_REGION_NAME=auto
AWS_S3_CUSTOM_DOMAIN=media.jat21.com
AWS_S3_ADDRESSING_STYLE=path
AWS_S3_SIGNATURE_VERSION=s3v4
AWS_QUERYSTRING_AUTH=False
AWS_S3_CACHE_CONTROL=max-age=86400
```

Keep the existing production `SECRET_KEY`, `DATABASE_URL`, `ALLOWED_HOSTS`,
`CSRF_TRUSTED_ORIGINS`, email, and other non-media variables unchanged.

## How Admin Uploads Work

After deployment with `MEDIA_STORAGE_BACKEND=s3`, new files uploaded in Django
admin through existing `ImageField` and `FileField` fields are stored in R2.
The admin workflow does not change:

- Project cover images continue using `projects/covers/`.
- Project gallery images continue using `projects/gallery/`.
- Site logo and Open Graph image continue using `site/`.
- About portrait and CV continue using `about/` and `about/cv/`.

If `AWS_S3_CUSTOM_DOMAIN` is set and publicly routed, public pages will render
media URLs from that domain.

## Roll Back To Cloudinary

Cloudinary support remains available. To roll back, set:

```bash
MEDIA_STORAGE_BACKEND=cloudinary
CLOUDINARY_CLOUD_NAME=<cloudinary-cloud-name>
CLOUDINARY_API_KEY=<cloudinary-api-key>
CLOUDINARY_API_SECRET=<cloudinary-api-secret>
```

Then redeploy. Existing database file paths will only work if the corresponding
files exist in the selected storage backend. Switching storage providers does
not copy files automatically.

## Recovery Reminder

R2 is the destination for media going forward. Existing missing images still
need to be recovered separately from:

- old Cloudinary export if accessible
- client originals
- local backups
- browser or website archives if necessary

Once files are recovered, re-upload them through Django admin so the database
and selected storage backend stay in sync.
