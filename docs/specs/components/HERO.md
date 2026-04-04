# Hero Spec

## Scope

This spec covers the homepage hero only. It documents the current DOM contract, data sources, required states, and measurable rules already implemented in the homepage template, view, CSS, and audit tooling.

## Status

Implemented in:

- `apps/pages/views.py`
- `apps/pages/templates/pages/home.html`
- `static/css/components/hero.css`
- `apps/site/models/site.py`

Backed in part by:

- `tests/pages/test_views.py`
- `tests/e2e/test_homepage.py`
- `scripts/audit_hero_spec.py`

## DOM Contract

| Element | Requirement |
| --- | --- |
| Section root | Homepage hero root is `<section class="hero">`; add `hero--compact` only when `site_settings.hero_compact` is true. |
| Media layer | Hero media contains either one `<img class="hero__bg">` or one `<div class="hero__bg hero__bg--placeholder">`. |
| Overlay | One `.hero__overlay` must sit above the media layer. |
| Content wrapper | Text and CTAs live inside `.hero__content.container`. |
| Label | `.hero__label` is optional and must render only when `site_settings.hero_label` is non-blank. |
| Title | `.hero__title` is the only `h1` in the hero and uses `site_settings.site_name` with the same default fallback as the rest of the site shell. |
| Subtitle | `.hero__subtitle` is optional and must render only when `site_settings.tagline` is non-blank. |
| CTA group | `.hero__cta` contains exactly two links in the shipped template: `View Projects` and `Start a Conversation`. |
| Scroll affordance | `.hero__scroll` links to `#featured` and contains one `.hero__scroll-line`. |

## Data Sources

| Input | Current behavior |
| --- | --- |
| `site_settings.site_name` | Renders as the hero title. |
| `site_settings.hero_label` | Renders above the title only when non-blank. |
| `site_settings.tagline` | Renders below the title only when non-blank. |
| `site_settings.hero_compact` | Toggles the `hero--compact` modifier on the section root. |
| `hero_project` | Comes from `HomeView`; it is the first selected homepage project. |
| `hero_project.cover_image` | Supplies the background image when present. |

## Required States

| State ID | State | Pass condition |
| --- | --- | --- |
| `H-01` | Default hero state | On the homepage, the hero renders one `h1`, both CTA links, one scroll link to `#featured`, and no `hero--compact` class when `hero_compact=False`. |
| `H-02` | Label present | `.hero__label` is rendered only when `hero_label` is non-blank. |
| `H-03` | Label absent | `.hero__label` is omitted when `hero_label` is blank. |
| `H-04` | Tagline absent | `.hero__subtitle` is omitted when `tagline` is blank. |
| `H-05` | Compact mode | `hero--compact` is added when `hero_compact=True`; the title max size drops from `6.5rem` to `4.5rem`. |
| `H-06` | Background image | If `hero_project.cover_image` exists, the hero renders it as `.hero__bg` with `loading="eager"`. |
| `H-07` | Placeholder background | If no hero cover image exists, the hero renders `.hero__bg--placeholder` instead of an `<img>`. |
| `H-08` | Hero project selection and fallback | `hero_project` is the first featured project ordered by `order`; if there are no featured projects, the first fallback homepage project becomes the hero source. |
| `H-09` | Scroll affordance responsiveness | `.hero__scroll` is visible above `639px` and hidden at `639px` and below. |
| `H-10` | Reduced-motion behavior | With `prefers-reduced-motion: reduce`, the scroll-line animation stops and the hero background image transition is disabled. |

## Layout And Interaction Rules

| Area | Requirement |
| --- | --- |
| Height | `.hero` uses `min-height: 100svh` and bottom-aligns the content block. |
| Content width | `.hero__content` max width is `720px`. |
| Subtitle width | `.hero__subtitle` max width is `520px`. |
| CTA wrapping | `.hero__cta` is a wrapping flex row; at `<=480px`, buttons may wrap and must not overflow. |
| Background fit | Hero images use full-bleed `object-fit: cover` and `object-position: center 30%`. |
| Hover motion | On hover-capable devices, the background image scales to `1.02` on hero hover. |

## Notes

- `scripts/audit_hero_spec.py` includes additional stress cases such as long-content combinations, dark/light image contrast, and a single-CTA screenshot. Those cases are useful for visual QA, but the single-CTA case is not a configurable user-facing state in the shipped template.
- Model help text currently recommends shorter content for fit, but the hard behavior is still the DOM and CSS contract above. Soft guidance is not treated as validation.
