# Global Specification

**Status:** Active  
**Applies to:** Shared public shell and cross-cutting public UI behavior  
**Last updated:** 2026-04-03

## Scope

This file defines the global, cross-cutting requirements that apply across Jeannote's public-facing UI.

It covers:
- shared shell structure
- metadata fallback behavior
- global accessibility baseline
- shared motion and interaction rules
- viewport and overflow expectations
- touch/keyboard baseline
- current performance baseline
- empty/error/loading-state baseline
- global audit checks

It does not define component-specific visual or behavioral detail. Those belong in:

- `docs/specs/components/HERO.md`
- `docs/specs/components/NAVBAR.md`

Typography-specific requirements belong in:
- `docs/specs/TYPOGRAPHY.md`

Layout-specific requirements belong in:
- `docs/specs/LAYOUT.md`

Testing policy and scenario coverage belong in:
- `docs/qa/TESTING.md`
- `docs/qa/TEST_MATRIX.md`

### Keyword definitions

- **MUST / REQUIRED**: mandatory for shipped behavior unless this file explicitly marks the item as a known gap, release target, or non-automated expectation.
- **SHOULD / RECOMMENDED**: expected default behavior; deviations need a clear product, accessibility, or implementation reason.
- **MAY / OPTIONAL**: permitted but not required.

### Precedence

- This file defines the global baseline for the shared public shell and other cross-cutting public UI behavior.
- `docs/specs/components/HERO.md` and `docs/specs/components/NAVBAR.md` MAY specialize within their domains, but they MUST NOT weaken the baseline defined here unless this file is updated too.
- `docs/specs/TYPOGRAPHY.md` and `docs/specs/LAYOUT.md` own their measurable domain-specific rules; this file only sets cross-cutting baseline requirements that rely on them.
- `docs/product/DOCTRINE.md` guides judgment and prioritization, but it does not override measurable requirements in this file or in component specs.

---

## Status and Current Evidence

### Current implementation sources
Implemented in:
- `templates/base.html`
- `templates/includes/nav.html`
- `templates/includes/footer.html`
- `static/css/base/base.css`
- `static/css/utilities/utilities.css`
- `static/css/components/nav.css`
- `static/css/components/hero.css`
- `static/css/components/components.css`
- `static/js/main.js`

### Current automated / direct evidence
Backed in part by:
- `tests/core/test_views.py`
- `tests/e2e/test_navigation.py`
- `tests/e2e/test_homepage.py`
- `tests/pages/test_views.py`

### Current known evidence model
This file distinguishes between:
- **Required baseline** - what must be true
- **Currently implemented** - what code currently does
- **Current evidence** - what tests currently prove
- **Known gap / release target** - what is expected but not yet fully automated or fully proven

This prevents the spec from overstating what is enforced today.

---

## 1. Global Baseline Requirements

### 1.1 Accessibility baseline

#### Standard
Jeannote targets **WCAG 2.1 AA** as the baseline accessibility standard for the shipped public UI.

#### Contrast
Minimum contrast requirements:
- **Normal text:** 4.5:1
- **Large text:** 3:1
- **Meaningful non-text UI / focus indicators / control boundaries:** 3:1

This applies to:
- header/nav text
- hero text over imagery
- body text
- footer/supporting text
- CTA text
- focus-visible states

#### Keyboard access
All primary public interactions MUST be operable by keyboard, including:
- skip link
- navbar links
- mobile nav toggle
- CTA buttons
- public form controls where rendered

#### Focus visibility
All focusable interactive elements MUST provide a visible `:focus-visible` state.

#### Landmarks and structure
Public pages using the shared shell MUST expose:
- one skip link before the header
- one `main#main-content` target
- shared header and footer structure

#### Reduced motion
Motion MUST NOT be required for comprehension.  
When reduced motion is requested, implemented decorative motion MUST be reduced or disabled.

---

### 1.2 Browser and viewport baseline

#### Automated browser baseline
Current required automated browser verification MUST include:
- **Chromium** via Playwright

#### Release verification expectation
Until broader automation is added, release sign-off SHOULD include spot verification in:
- Safari
- Firefox

#### Required viewport matrix
Current required baseline viewports:

| Label | Size | Use |
| --- | ---: | --- |
| Mobile | 390×844 | primary mobile baseline |
| Tablet | 768×1024 | tablet and breakpoint baseline |
| Desktop | 1440×900 | desktop baseline |

Additional stress widths MAY be used in the matrix when required by a specific system.

---

### 1.3 Overflow and shell integrity baseline

- No horizontal document scrolling is allowed at required baseline viewports.
- Shared shell elements MUST NOT collide with one another.
- Public content MUST NOT visibly escape intended containers in a broken way.
- Missing optional content MUST NOT create broken-looking shell output.

---

### 1.4 Touch and interaction baseline

- Touch-first controls MUST provide a minimum **44x44 CSS px** hit area.
- Hover MUST NOT be the only path to essential meaning or essential navigation.
- Breakpoint transitions MUST recover cleanly without leaving stale mobile-menu or scroll-lock state behind.

---

### 1.5 Motion baseline

- Smooth scrolling MAY be present in the shared shell.
- Decorative reveal motion MAY run only when reduced motion is not requested.
- Reduced-motion users MUST NOT receive unnecessary hero or auto-rotation motion where the implementation already supports reduction.

---

### 1.6 Metadata / SEO baseline

Public pages MUST maintain a minimum metadata baseline:
- valid page title
- canonical link behavior
- Open Graph image fallback
- Twitter image fallback

This file defines the baseline fallback behavior; component-level or page-level SEO detail MAY live elsewhere.

---

### 1.7 Performance baseline

#### Current baseline expectation
The public shell MUST remain usable and visually stable without avoidable layout instability or obvious asset waste.

#### Release targets
These are current release targets, not yet universal hard CI gates unless explicitly wired in testing:

- **LCP:** under 2.5s
- **CLS:** under 0.1
- **INP:** under 200ms

#### Practical baseline
At minimum:
- fonts MUST NOT create a broken first-render experience
- images MUST NOT create obvious shell instability
- optional content absence MUST NOT create reflow that reads as broken

If performance enforcement grows materially, it MAY later be split into a dedicated spec.

---

### 1.8 Empty / error / loading baseline

#### Empty-state baseline
Optional content MUST collapse intentionally:
- no broken image icons
- no blank shell artifacts
- no obvious "template error" visual states

#### Error-state baseline
Production UI MUST NOT expose:
- stack traces
- raw template exceptions
- visibly broken shell output

#### Loading-state baseline
Where delayed or progressive rendering exists, it MUST NOT create:
- obvious shell collapse
- broken interaction states
- large avoidable layout shift

---

## 2. Current Implemented Shared Shell Contract

The following describes the current shared shell behavior already implemented in code.

| Area | Current implemented requirement |
| --- | --- |
| Document shell | Every page extends `templates/base.html` and renders one `main#main-content` region between the shared header and shared footer. |
| Skip link | One `.skip-link` appears before the header and targets `#main-content`. |
| Header | The shared header is fixed to the top edge and uses a `4.5rem` nav height. |
| Footer | The shared footer appears on every page after `<main>`. |
| Canonical URL | The canonical link defaults to `request.build_absolute_uri` unless a page overrides the block. |
| Open Graph image fallback | Fallback order is page `og_image`, then `site_settings.og_image`, then `static/images/og-default.svg`. |
| Twitter image fallback | Twitter image uses the same fallback order as Open Graph. |
| Site title pattern | Base title pattern uses an em dash separator: `<page title> — <site name>`, with the homepage currently overriding to `<site name> — Architecture Practice`. |
| Global font load | `Cormorant Garamond` and `DM Sans` are loaded once in the base template from Google Fonts. |
| Focus state | Implemented via `:focus-visible { outline: 2px solid var(--focus-ring); outline-offset: 3px; }` with `:focus:not(:focus-visible) { outline: none; }` — keeps the shared keyboard focus treatment explicit and avoids showing the outline on pointer focus. |
| Body shell | `body` is a column flex container with `min-height: 100vh`; `main` flexes to fill the remaining space. |

---

## 3. Current Implemented Shared Interaction Contract

The following are current implemented shared interaction rules already depended on by the public shell.

| Area | Current implemented requirement |
| --- | --- |
| Header scroll state | The shared header gains `.scrolled` when `window.scrollY > 60`. |
| Home transparent header | On the homepage, the header stays transparent until either `.scrolled` or `.nav-open` is applied. |
| Mobile nav open state | Opening the mobile menu sets `.is-open` on `.nav__links` and `.nav__toggle`, sets `aria-expanded="true"`, adds `.nav-open` to `#site-header`, and sets `document.body.style.overflow = 'hidden'`. |
| Mobile nav close state | Closing the menu reverses those class and attribute changes and restores `document.body.style.overflow` to empty. |
| Escape behavior | Pressing `Escape` while the mobile menu is open closes it and restores focus to the toggle. |
| Focus handoff | Keyboard-opening the mobile menu moves focus to the first menu link. Shift+Tab from the first link returns focus to the toggle. |
| Breakpoint recovery | If the viewport crosses above `767px`, the mobile menu is forced closed so scroll lock cannot remain stuck. |
| Reveal motion | `.reveal` animations only run when `prefers-reduced-motion: no-preference`; otherwise content appears without animation. |
| Reduced motion | Hero scroll-line animation is disabled when `prefers-reduced-motion: reduce`. Testimonial auto-rotation does not start when reduced motion is requested. |

---

## 4. Audit Checks

Every required global state MUST map to evidence in `docs/qa/TEST_MATRIX.md`.

### Requirement-to-audit traceability

| Requirement section | Primary audit IDs |
| --- | --- |
| 1.1 Accessibility baseline | G-01, G-02, G-05, G-06, G-08, G-09 |
| 1.2 Browser and viewport baseline | G-07, G-10 |
| 1.3 Overflow and shell integrity baseline | G-01, G-10 |
| 1.4 Touch and interaction baseline | G-05, G-06, G-07 |
| 1.5 Motion baseline | G-09 |
| 1.6 Metadata / SEO baseline | G-03 |
| 1.7 Performance baseline | Release target only; no dedicated global audit check yet |
| 1.8 Empty / error / loading baseline | Release target only; no dedicated global audit check yet |

The table below defines the current audit checks and their pass conditions.

| ID | Check | Pass condition |
| --- | --- | --- |
| G-01 | Base shell landmarks | The rendered public shell includes one `.skip-link`, one `#site-header`, one `main#main-content`, and one `.site-footer` on required public routes. |
| G-02 | Skip-link target | The skip link `href` remains `#main-content` and the page contains one matching `main` target. |
| G-03 | Metadata fallback | With no page override and no `site_settings.og_image`, rendered metadata points to `images/og-default.svg`. |
| G-04 | Header scroll threshold | At `window.scrollY = 61`, `#site-header` has `.scrolled`; at `0`, it does not. |
| G-05 | Mobile menu lock | On mobile, opening the menu sets `aria-expanded="true"` and body overflow to `hidden`; closing resets both. |
| G-06 | Escape close | On mobile, pressing `Escape` while the menu is open closes it and returns focus to the toggle. |
| G-07 | Desktop recovery | Crossing from mobile to tablet/desktop closes the mobile menu automatically. |
| G-08 | Focus visibility | Keyboard focus shows the shared `2px` accent outline on interactive elements that use default focus styling. |
| G-09 | Reduced motion | Shared reduced-motion rules prevent avoidable shell or hero motion where implemented. |
| G-10 | No horizontal overflow | No horizontal page overflow occurs at required baseline viewports. |

---

## 5. Current Known Gaps / Release Targets

These are expectations or standards that may not yet be fully automated or fully evidenced in the current suite.

- Broader browser verification outside Chromium is still primarily a release sign-off task unless separately automated.
- Performance targets exist as release goals but may not yet be enforced by a dedicated automated budget gate.
- Accessibility automation beyond current focused assertions may be expanded later.
- Error-state, 404, and richer loading-state verification may require deeper page-level or form-level coverage than this global shell spec currently proves.

These items MUST NOT be silently treated as "already enforced" if the evidence does not yet exist.

---

## 6. Documentation and QA Linkage

### 1:1 Rule
Every required state in this file MUST map to one or more rows in:
- `docs/qa/TEST_MATRIX.md`

### Behavior-change rule
If shared-shell behavior changes:
- update this file
- update the relevant matrix rows
- update tests where required
- add a changelog entry if shipped behavior changed
- add a decision-log entry if the decision was non-obvious

### Docs debt rule
If code and this file disagree:
- the mismatch MUST be flagged immediately
- it MUST NOT be silently normalized in future documentation
- release readiness MUST reflect the mismatch if it affects shipped behavior

---

## Related Documents

- `docs/product/DOCTRINE.md`
- `docs/specs/TECHNICAL_SPEC.md`
- `docs/specs/TYPOGRAPHY.md`
- `docs/specs/LAYOUT.md`
- `docs/specs/components/HERO.md`
- `docs/specs/components/NAVBAR.md`
- `docs/qa/TESTING.md`
- `docs/qa/TEST_MATRIX.md`
