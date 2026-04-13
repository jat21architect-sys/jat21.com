# Running a Demo

How to stand up a working preview of this template in under five minutes —
locally or on a public URL — so you can evaluate it before customising.

---

## Option A — Local preview (fastest)

Use [SETUP.md](SETUP.md) Phase 1 for the canonical first-run path:

- clone the repo and install dependencies
- create `.env` and set `SECRET_KEY`
- run `migrate`, `createsuperuser`, and `seed_demo`
- start the dev server

Open **<http://127.0.0.1:8000>**.

The site renders immediately with starter/demo content — projects, services,
and a populated About page. Log in to **<http://127.0.0.1:8000/admin>**
to explore the content management interface.

> **Demo media bundle:** The repo ships a tracked demo-media bundle under
> `apps/site/demo_seed/strand-architecture`. `seed_demo` auto-discovers it and
> attaches the bundled project media during first-run setup.

---

## Option B — Docker (no Python on the host)

For the full Docker reference — including setup, one-off commands, volume behaviour,
and the dev-vs-production distinction — use
[README.md §Run locally with Docker](README.md#run-locally-with-docker).

For demo purposes, the important part is still the same: bring the stack up,
create an admin user, and load `seed_demo` so the preview site renders with the
starter dataset on first visit.

Open **<http://localhost:8000>**.

---

## Option C — Public preview URL (share with others)

To share a live preview, deploy a prod-like instance using the canonical
deployment reference in [README.md](README.md). After the preview instance is
running, load the demo dataset with `seed_demo` so the public URL shows the
starter projects, services, and About content immediately.

This path is for evaluation and review only. For real setup and launch, use
[SETUP.md](SETUP.md).

> **Note on media uploads in demo mode:** Production uses Cloudinary for
> media storage. For a demo without Cloudinary, uploaded media will not persist
> across deploys. The tracked demo-media bundle still lets `seed_demo` attach a
> strong local or preview dataset, but your own uploads should use production storage.

---

## What the demo shows

After running `seed_demo`, the site contains:

### Home page

- Practice tagline
- Up to six featured projects in the homepage grid (drawn from seven featured demo projects; three shown by default on mobile)
- Services summary section
- Homepage closing CTA

### Projects

- Eleven project records across `Housing`, `Civic`, and `Workplace`
- Seven are marked featured for homepage selection
- Each project has a full narrative: overview, challenge, concept, and outcome
- Category filter works on the list page

### Services

- Three service records with `summary`, `who_for`, `value_proposition`, and `deliverables`

### About

- Populated identity, narrative, approach, and professional-profile sections
- Real demo values for `experience_years`, location, and studio identity
- Default demo runs in text-only mode until a real person/studio portrait is supplied

### Contact

- Fully functional contact form
- Submissions save to the database and appear in admin under Contact Inquiries
- Email notifications require SMTP configuration (local dev uses console backend — emails print to terminal)

### Admin

- Log in at `/admin/` to see the full content management interface
- All content visible on the site is managed entirely through admin — no template editing required

## What is demo content vs system configuration?

- **Demo/example content:** practice name, About copy, services, projects, testimonials, and other starter text/media loaded by `seed_demo`
- **System/config:** navigation structure, page layouts, contact-delivery plumbing, environment variables, and the shared styling system
- **What to edit first:** `Site Settings`, then `About Profile`, then `Services`, then `Projects`
- **For real setup and launch:** continue in [SETUP.md](SETUP.md)

---

## Resetting demo content

To reset the starter content to a clean slate (destructive):

```bash
uv run python manage.py flush --no-input
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py seed_demo
```

Or to wipe only projects and start fresh there:

```bash
# In the Django shell
uv run python manage.py shell
>>> from apps.projects.models import Project, ProjectImage, Testimonial
>>> Testimonial.objects.all().delete()
>>> ProjectImage.objects.all().delete()
>>> Project.objects.all().delete()
```
