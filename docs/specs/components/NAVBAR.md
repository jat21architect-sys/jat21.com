# Navbar Spec

## Scope

This spec covers the shared top navigation only. It documents brand fallback order, mobile-menu behavior, required states, and the current admin safety rules already implemented in templates, CSS, JS, and `core_tags`.

## Status

Implemented in:

- `templates/includes/nav.html`
- `static/css/components/nav.css`
- `static/js/main.js`
- `apps/core/templatetags/core_tags.py`
- `apps/site/models/site.py`
- `apps/site/admin/site.py`

Backed in part by:

- `tests/pages/test_views.py`
- `tests/core/test_templatetags.py`
- `tests/e2e/test_navigation.py`
- `scripts/audit_nav_brand.py`

## DOM Contract

| Element | Requirement |
| --- | --- |
| Header root | Shared header root is `<header class="site-header" id="site-header">`. |
| Nav shell | The navigation shell is `<nav class="nav container">`. |
| Brand anchor | The brand is always one `<a class="nav__brand">` linking to the homepage. |
| Brand accessibility | The brand anchor always carries `aria-label` and `title` equal to the full `site_settings.site_name` fallback string. |
| Toggle | One `<button class="nav__toggle">` exists with `aria-label="Toggle menu"` and runtime-managed `aria-expanded`. |
| Link list | One `<ul class="nav__links">` contains four links in this order: Projects, About, Services, Contact. |
| Active class | The current route adds `.is-active` to the matching link in the template. |

## Brand Fallback Order

| Priority | Condition | Rendered output |
| --- | --- | --- |
| `1` | `site_settings.logo` is present | `<img class="nav__logo">` |
| `2` | No logo and `site_settings.nav_name` is non-blank | `<span class="nav__name">` with the exact `nav_name` string |
| `3` | No logo, no `nav_name`, and `nav_needs_monogram(site_name)` is true | `<span class="nav__monogram">` using `nav_monogram(site_name)` |
| `4` | No logo, no `nav_name`, and `site_name` passes the safe-text test | `<span class="nav__name">` with the full `site_name` |

## Safe-Text Thresholds

| Constant | Value | Meaning |
| --- | --- | --- |
| `NAV_TEXT_MAX_CHARS` | `18` | Full `site_name` text path is allowed only at or below this character count. |
| `NAV_TEXT_MAX_WORDS` | `2` | Full `site_name` text path is allowed only at or below this word count. |

If either threshold fails, the automatic brand path switches to the monogram.

## Monogram Rules

| Step | Current behavior |
| --- | --- |
| Normalise | Collapse repeated whitespace. |
| Tokenise | Split on spaces and `+`; hyphens stay inside a token. |
| Filter | Remove only syntactic stop words: `and`, `&`, `of`, `the`, `for`, `a`, `an`, `+`. |
| Preserve | Keep profession descriptors such as `Architects`, `Architecture`, and `Partners`. |
| Extract | Take the first character of each surviving token, uppercase it, and cap the result at 3 letters. |
| Fallback | If no initials survive, return the first character of the original name. |

## Required States

| State ID | State | Pass condition |
| --- | --- | --- |
| `N-01` | Logo override | When `logo` exists, the navbar renders `.nav__logo` and does not render `.nav__name` or `.nav__monogram`. |
| `N-02` | `nav_name` override | When `nav_name` is non-blank and there is no logo, the navbar renders `.nav__name` from `nav_name` and does not enter the monogram path. |
| `N-03` | Full-text auto path | When `site_name` is at or below `18` characters and `2` words, with no logo or `nav_name`, the navbar renders full text in `.nav__name`. |
| `N-04` | Monogram auto path | When `site_name` fails either safe-text threshold, with no logo or `nav_name`, the navbar renders `.nav__monogram`. |
| `N-05` | Brand accessibility label | The brand anchor always exposes the full practice name via `aria-label`, regardless of whether the visible brand is full text, `nav_name`, or monogram. |
| `N-06` | Transparent home state | On the homepage before scroll and while the mobile menu is closed, the header is transparent and brand/link text switches to white; logo images are inverted to white. |
| `N-07` | Scrolled state | When `window.scrollY > 60`, the header gains `.scrolled` and uses the solid blurred background treatment. |
| `N-08` | Mobile closed state | At `<=767px`, the toggle is visible, the overlay menu is hidden, and `aria-expanded` is `false`. |
| `N-09` | Mobile open state | Opening the menu applies `.is-open` to the toggle and link list, applies `.nav-open` to the header, locks body scroll, and shows the full-screen dark overlay. |
| `N-10` | Escape and focus return | Pressing `Escape` while the mobile menu is open closes it and returns focus to the toggle. |
| `N-11` | Breakpoint recovery | If the menu is open and the viewport crosses above `767px`, the script closes the menu and removes scroll lock. |
| `N-12` | Tablet/desktop inline state | At `>=768px`, the toggle is hidden and the link list is visible inline. |
| `N-13` | Active route marker | The current page link carries `.is-active`; on desktop the Contact link keeps CTA chrome, while on the mobile overlay it is reset into the serif link system. |

## Render Constraints

| Area | Requirement |
| --- | --- |
| Header height | `.nav` height is `var(--header-height)` (currently `4.5rem`). |
| Text brand safety net | `.nav__name` uses `max-width: clamp(120px, 38vw, 240px)` with ellipsis. This safety net applies to `nav_name`; automatic full-text `site_name` rendering should stay within the safe-text thresholds instead of relying on truncation. |
| Logo cap | `.nav__logo` max width is `160px` and height is `2.5rem`. |
| Mobile overlay | The menu overlay fills the viewport with `position: fixed; inset: 0`. |
| Mobile link typography | On the overlay, nav links and Contact use the serif system at `2rem`, not the desktop sans/CTA styles. |

## Admin Safety Already Implemented

| Safeguard | Current behavior |
| --- | --- |
| Blank `site_name` warning | Admin warns that the site name appears in the page heading, navigation, and footer. |
| Long `site_name` info | Admin shows an info message when `site_name` exceeds `30` characters and neither `nav_name` nor `logo` is set. |
| Single-letter monogram warning | Admin warns when the computed automatic monogram would collapse to one letter and no override is set. |

## Notes

- `tests/core/test_templatetags.py` proves the monogram algorithm in isolation. `tests/pages/test_views.py` proves the rendered path selection in templates. `tests/e2e/test_navigation.py` proves the mobile interaction behavior.
- The long-`nav_name` truncation safety net is implemented in CSS and exercised by `scripts/audit_nav_brand.py`, but it is not currently covered by an automated assertion.
