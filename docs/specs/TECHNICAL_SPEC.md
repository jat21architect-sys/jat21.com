# Technical Spec

This file is the gateway into the Jeannote doc system. It is not the place for detailed UI rules. Shared behavior, component contracts, and QA scenarios live in the files linked below.

## Scope

Use this file to answer three questions:

1. What are the main runtime surfaces?
2. Which spec owns which decision?
3. What docs debt is still visible and unresolved?

## Runtime Map

| Surface | Current owner |
| --- | --- |
| Site shell | `templates/base.html`, `templates/includes/nav.html`, `templates/includes/footer.html` |
| Homepage composition | `apps/pages/views.py`, `apps/pages/templates/pages/home.html` |
| Shared styling entrypoint | `static/css/main.css` |
| Shared interaction JS | `static/js/main.js` |
| Shared global content/config | `apps/site/models/site.py` (`SiteSettings`, `AboutProfile`) |
| Brand fallback logic | `apps/core/templatetags/core_tags.py` |
| Shared QA entrypoints | `tests/`, `.github/workflows/ci.yml`, `Makefile`, `scripts/audit_hero_spec.py`, `scripts/audit_nav_brand.py` |

## Spec Ownership

| Topic | Owning doc |
| --- | --- |
| Shared shell, metadata, accessibility, shared motion | [GLOBAL.md](GLOBAL.md) |
| Shared font stack and type metrics | [TYPOGRAPHY.md](TYPOGRAPHY.md) |
| Shared spacing, container, breakpoint, and grid rules | [LAYOUT.md](LAYOUT.md) |
| Shared token governance and theming boundaries | [TOKENS.md](TOKENS.md) |
| Homepage hero contract | [components/HERO.md](components/HERO.md) |
| Shared navbar contract | [components/NAVBAR.md](components/NAVBAR.md) |
| Test policy, commands, and layer selection | [../qa/TESTING.md](../qa/TESTING.md) |
| Required state coverage map | [../qa/TEST_MATRIX.md](../qa/TEST_MATRIX.md) |
| Release gate | [../qa/RELEASE_CHECKLIST.md](../qa/RELEASE_CHECKLIST.md) |

## Current Implementation Notes

- `SiteSettings` is the primary config surface for hero and navbar behavior: `site_name`, `tagline`, `hero_label`, `hero_compact`, `nav_name`, `logo`, metadata fields, and homepage project-count settings.
- The shared shell and shared frontend baseline live at repo level in `templates/` and `static/`.
- `apps/core` owns only cross-cutting Django glue.
- `apps/site` owns Jeannote's site-wide content/config models, admin safety, and launch-readiness logic.
- `apps/pages` owns Jeannote's Home, About, and Privacy composition.
- `HomeView` selects `homepage_projects`, exposes breakpoint count classes, and sets `hero_project` to the first selected homepage project.
- The shared JS owns header scroll state and mobile navigation state; those behaviors are not duplicated in templates.
- The project already ships automated tests plus manual visual audit scripts. The matrix distinguishes between those coverage types instead of treating them as equivalent.

## Outstanding Docs Debt

- None currently open in the doc system.
- Legacy operational docs are intentionally linked from `docs/README.md` and kept outside the locked structure.

## Out Of Scope

- Do not add detailed component rules here.
- Do not restate the audit tables from `GLOBAL.md`, `TYPOGRAPHY.md`, `LAYOUT.md`, `HERO.md`, or `NAVBAR.md`.
- Do not use this file as a change log or decision log.
