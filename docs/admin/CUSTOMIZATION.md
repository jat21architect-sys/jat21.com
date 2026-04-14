# Customization

Jeannote is an opinionated architecture portfolio template, not a no-code site builder.
This document is the canonical source of truth for what buyers can change in admin, what
requires environment or deployment configuration, what still requires code edits, and
what is intentionally fixed by product choice.

## How To Read This Doc

Use the classification labels exactly as written:

- `admin-managed`: editable in Django admin without changing code or deployment config.
- `env/config-managed — required for launch`: not admin-managed; must be configured in
  the environment or deployment settings before launch.
- `env/config-managed — optional integration`: not admin-managed; optional tooling or
  infrastructure integration that can be added later.
- `code-only (simple editorial change)`: visible copy or assets that currently require a
  code or template edit, but do not meaningfully change application behavior.
- `code-only (behavior-coupled / risky)`: surfaces that are tied to routes, forms,
  taxonomy, metadata selection, or other logic where edits carry higher implementation
  risk.
- `intentionally opinionated`: fixed by product choice. These are not bugs in the docs;
  they are deliberate constraints of the template.

The `recommended action` column means:

- `leave as-is`: current behavior is acceptable for the product as positioned.
- `document clearly`: keep it for now, but make the limitation explicit in buyer-facing docs.
- `move to admin later`: a reasonable later-stage product improvement, but not required to
  tell the truth now.
- `refactor before sale`: current behavior creates too much trust risk to leave vague.
- `keep opinionated`: intentionally fixed unless the product direction changes.

## Canonical Customization Matrix

| surface | current source of truth | classification | buyer expectation risk | recommended action | notes |
| --- | --- | --- | --- | --- | --- |
| Site name | `SiteSettings.site_name` | `admin-managed` | low | leave as-is | Public brand name across hero, footer, page-title fallback, and accessibility labels. |
| Tagline | `SiteSettings.tagline` | `admin-managed` | low | leave as-is | Used in homepage hero and footer. |
| Hero label | `SiteSettings.hero_label` | `admin-managed` | low | leave as-is | Homepage pre-title label. |
| Hero compact mode | `SiteSettings.hero_compact` | `admin-managed` | low | leave as-is | Layout toggle for long names or taglines. |
| Navbar brand text override | `SiteSettings.nav_name` | `admin-managed` | medium | document clearly | Buyer can override automatic brand behavior, but the fallback logic remains code-driven. |
| Navbar logo | `SiteSettings.logo` | `admin-managed` | low | leave as-is | Replaces text brand path. |
| Navbar labels | shared header template | `code-only (simple editorial change)` | high | move to admin later | `Projects`, `About`, `Services`, and `Contact` are fixed. |
| Navbar order and routes | shared header template | `intentionally opinionated` | high | keep opinionated | Core information architecture. Changing it is product-structure work, not content editing. |
| Footer brand block | `SiteSettings.site_name`, `tagline` | `admin-managed` | low | leave as-is | Public footer identity is editable. |
| Footer public email, social links, and location | `SiteSettings.contact_email`, social URLs, `location` | `admin-managed` | low | leave as-is | Strong current admin surface. |
| Footer nav labels, order, and routes | shared footer template | `code-only (simple editorial change)` | medium | document clearly | Mirrors main nav; not admin-editable. |
| Footer legal sentence structure | shared footer template | `code-only (simple editorial change)` | low | document clearly | Year and identity update automatically, sentence framing is fixed. |
| Privacy link placement | shared footer template | `code-only (simple editorial change)` | low | document clearly | Always present in the footer legal line. |
| Homepage hero title, subtitle, and label | `SiteSettings` | `admin-managed` | low | leave as-is | Core brand copy is genuinely editable. |
| Homepage hero image source | featured project ordering plus project cover image | `admin-managed` | medium | document clearly | Controlled indirectly through content and ordering, not explicit hero-image selection. |
| Homepage hero CTA labels | homepage template | `code-only (simple editorial change)` | high | move to admin later | `View Projects` and `Start a Conversation`. |
| Homepage hero CTA destinations | homepage template | `intentionally opinionated` | high | keep opinionated | Part of the site structure, not just copy. |
| Homepage services strip content | `Service` records | `admin-managed` | low | leave as-is | Titles, summaries, order, and active state. |
| Homepage services strip action labels | homepage template | `code-only (simple editorial change)` | medium | document clearly | `All Services` and similar fixed labels. |
| Homepage featured-project section headings | homepage template | `code-only (simple editorial change)` | medium | move to admin later | `Featured Projects`, `All Projects`, `View Project`. |
| Homepage featured-project pool and counts | `Project.featured`, `Project.order`, `SiteSettings.homepage_projects_*_count` | `admin-managed` | low | leave as-is | Good current implementation. |
| Homepage closing/editorial line | `SiteSettings.homepage_closing_text` | `admin-managed` | low | leave as-is | Already a strong buyer-facing customization point. |
| Homepage closing CTA label | homepage template | `code-only (simple editorial change)` | high | move to admin later | `Get in Touch` is fixed. |
| About hero title, meta, and subtitle | `AboutProfile` plus `SiteSettings` | `admin-managed` | low | leave as-is | Well modeled. |
| About portrait, CV, and contact CTA visibility | `AboutProfile` plus `SiteSettings.contact_email` | `admin-managed` | medium | document clearly | Some visible states are gated by field combinations. |
| About narrative and profile facts | `AboutProfile` | `admin-managed` | low | leave as-is | Strong current admin surface. |
| About CTA invitation text | `AboutProfile.closing_invitation` | `admin-managed` | medium | document clearly | If the invitation is too long, the template behavior changes. |
| About CTA button labels and routes | about template | `code-only (simple editorial change)` | medium | document clearly | `Get in Touch` and `View Projects` are fixed. |
| About CTA fallback heading logic | about template plus length check | `code-only (behavior-coupled / risky)` | medium | document clearly | Over-80-character copy changes how the section is rendered. |
| Services page service records | `Service` model | `admin-managed` | low | leave as-is | Titles, summaries, descriptions, value proposition, deliverables, and order. |
| Services page hero label, title, and subtitle | services template | `code-only (simple editorial change)` | high | move to admin later | High-visibility buyer-facing copy. |
| Services page empty-state prose | services template | `code-only (simple editorial change)` | medium | document clearly | Only visible if no active services exist. |
| Services end-strip copy | services template | `code-only (simple editorial change)` | medium | move to admin later | Closing editorial or trust copy is fixed. |
| Services CTA labels | services template | `code-only (simple editorial change)` | medium | document clearly | `Enquire About This Service` and `Get in Touch`. |
| Service CTA prefill behavior | service slug plus built-in slug map | `code-only (behavior-coupled / risky)` | high | refactor before sale | Slugs are not cosmetic; changing them affects contact-form prefill behavior. |
| Projects list page hero strings | projects list template | `code-only (simple editorial change)` | medium | document clearly | `Portfolio` and `Projects`. |
| Project categories and taxonomy labels | `Project.CATEGORY_CHOICES` | `intentionally opinionated` | high | keep opinionated | Fixed to `Housing`, `Civic`, and `Workplace`. |
| Project filter behavior and query params | projects model and view logic | `intentionally opinionated` | high | keep opinionated | Category logic is application behavior, not content. |
| Projects list cards content and images | `Project` fields and media | `admin-managed` | low | leave as-is | Titles, descriptions, years, locations, and images. |
| Projects list empty-state text | projects list template | `code-only (simple editorial change)` | medium | document clearly | `No projects found in this category.` |
| Projects list pagination labels | projects list template | `code-only (simple editorial change)` | low | leave as-is | `Previous`, `Next`, and `Page X of Y`. |
| Projects close editorial line | projects list template | `code-only (simple editorial change)` | high | move to admin later | Strongly voiced and buyer-visible. |
| Projects close CTA label | projects list template | `code-only (simple editorial change)` | high | move to admin later | `Start a Conversation`. |
| Project detail narrative content | `Project` fields | `admin-managed` | low | leave as-is | Main case-study body is properly content-managed. |
| Project detail hero image, galleries, and testimonials | `ProjectImage`, `Testimonial`, `Project` | `admin-managed` | low | leave as-is | Strong content model. |
| Project detail section headings | project detail template | `code-only (simple editorial change)` | medium | document clearly | `Overview`, `Challenge & Context`, `Design Concept`, `Process`, `Outcome`, and similar headings. |
| Project detail testimonial and related-project headings | project detail template | `code-only (simple editorial change)` | medium | document clearly | `What the Client Said` and `Related Projects`. |
| Project detail bottom CTA labels | project detail template | `code-only (simple editorial change)` | medium | move to admin later | `All Projects` and `Discuss a Similar Project`. |
| Contact page hero copy | contact template | `code-only (simple editorial change)` | high | move to admin later | `Get in Touch`, `Let's Talk`, and the intro line. |
| Contact process and trust copy | contact template | `code-only (simple editorial change)` | high | move to admin later | `What to expect` block and trust note are public trust surfaces. |
| Contact public response-time wording | `SiteSettings.contact_response_time` | `admin-managed` | low | leave as-is | Good existing admin hook. |
| Contact public contact details and social links | `SiteSettings` | `admin-managed` | low | leave as-is | Email, phone, location, and selected socials. |
| Contact form field set | `ContactForm` | `code-only (behavior-coupled / risky)` | high | document clearly | Fixed in code. |
| Contact form field choices | `PROJECT_TYPE_CHOICES`, `BUDGET_CHOICES`, `TIMELINE_CHOICES` | `code-only (behavior-coupled / risky)` | high | document clearly | Buyers may assume these dropdowns are admin-managed. They are not. |
| Contact placeholders, hints, and validation copy | `ContactForm` plus contact template | `code-only (simple editorial change)` | high | move to admin later | High-visibility buyer voice surface. |
| Contact anti-spam timing and token rules | settings plus form logic | `env/config-managed — required for launch` | medium | document clearly | Operational rather than editorial; should be left alone unless you understand the delivery flow. |
| Contact notification inbox | `CONTACT_EMAIL` env var | `env/config-managed — required for launch` | high | refactor before sale | Biggest launch trap: the site can look complete while internal delivery is not configured. |
| Email sender, backend, and SMTP settings | environment and Django settings | `env/config-managed — required for launch` | medium | document clearly | Required for full delivery behavior. |
| Contact success response-time value | `SiteSettings.contact_response_time` | `admin-managed` | low | leave as-is | Timeframe itself is editable. |
| Contact success headings, body, and CTAs | success template | `code-only (simple editorial change)` | medium | document clearly | Sent and saved-only wording is fixed. |
| Default share image asset | `SiteSettings.og_image` | `admin-managed` | medium | leave as-is | Buyer can upload a default OG image. |
| Project-specific share image asset | project cover or gallery media | `admin-managed` | medium | document clearly | Buyer controls assets, but not always explicit precedence. |
| Share-image precedence and metadata logic | base template plus project view logic | `code-only (behavior-coupled / risky)` | high | refactor before sale | Current selection and URL behavior is code-driven and trust-sensitive. |
| Global analytics integration | `SiteSettings.google_analytics_id` | `admin-managed` | low | leave as-is | Good current implementation. |
| Production media storage | production settings and Cloudinary credentials | `env/config-managed — required for launch` | high | refactor before sale | Required before accepting real uploads in production. |
| Sentry integration | environment and production settings | `env/config-managed — optional integration` | low | document clearly | Infrastructure integration, not content management. |
| Privacy page body copy | privacy template | `code-only (simple editorial change)` | high | move to admin later | Public trust surface buyers will expect to customize. |
| Privacy contact link target | `SiteSettings.contact_email` fallback to contact form | `admin-managed` | low | leave as-is | Contact detail is dynamic; body copy is not. |
| Fonts, color system, spacing, and layout system | shared CSS and tokens | `intentionally opinionated` | medium | keep opinionated | Normal for a coded template, but should be described honestly. |
| Favicon | static asset | `code-only (simple editorial change)` | medium | document clearly | Buyer-visible brand artifact, currently not admin-managed. |

## Hard-Coded Traps

- The site looks more admin-editable than it really is. Nav labels, several CTA labels,
  privacy copy, contact copy, and multiple editorial strings are still template-level.
- Project categories are not seeded demo content. They are fixed product taxonomy.
- Service slugs are not just cosmetic. They affect contact-form prefill behavior.
- The public contact page can look complete while internal contact delivery is still
  unconfigured if `CONTACT_EMAIL` and SMTP settings are missing.
- Homepage hero and some share-image behavior are driven indirectly by project ordering,
  cover images, and fallback logic rather than one explicit “hero image” control.
- About CTA behavior changes based on copy length. Long text does not render the same way
  as short text.

## What Is Intentionally Opinionated

These are deliberate product choices in the current version of Jeannote:

- the core information architecture: `Projects`, `About`, `Services`, `Contact`
- the architecture-specific public taxonomy: `Housing`, `Civic`, and `Workplace`
- the overall design system, layout language, and route structure
- CTA destinations that reinforce the primary site flow

If you need those surfaces to behave like a no-code site builder, Jeannote is the wrong
product shape in its current form.

## Launch-Critical Config vs Optional Integrations

### `env/config-managed — required for launch`

Before launch, confirm these are configured outside Django admin:

- `CONTACT_EMAIL` and SMTP settings so contact-form submissions actually reach you
- production media storage credentials so uploaded images persist and resolve correctly
- standard production Django settings such as `DATABASE_URL`, `ALLOWED_HOSTS`, and
  `CSRF_TRUSTED_ORIGINS`

### `env/config-managed — optional integration`

These do not block launch:

- `SENTRY_DSN` and related Sentry settings
- analytics or tracking IDs you choose to add later

## Common Assumptions To Avoid

- Nav labels and routes are not `admin-managed`.
- Project categories are fixed in code.
- Contact form structure and dropdown choices are code-defined.
- Some CTA and editorial strings still require template edits.
- Production media and contact delivery require config, not admin content.
