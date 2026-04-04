# Typography Specification

**Status:** Active  
**Applies to:** Shared type system and cross-component text behavior  
**Last updated:** 2026-03-30

## Scope

This file defines the measurable typography system used across Jeannote's public UI.

It covers:
- font stack and loading model
- type-role assignment
- shared text baselines
- hero, navbar, section, card, footer, and CTA typography
- responsive type behavior across desktop / tablet / mobile
- current implemented mobile and tablet typography refinements
- micro-scale rules
- typography audit checks

It does not define:
- component-specific fallback logic unrelated to typography
- layout/grid/container rules
- global shell interaction rules
- buyer-facing configuration guidance

Those belong in:
- `docs/specs/components/HERO.md`
- `docs/specs/components/NAVBAR.md`
- `docs/specs/LAYOUT.md`
- `docs/admin/CUSTOMIZATION.md`

Global accessibility, viewport, and shell baselines belong in:
- `docs/specs/GLOBAL.md`

---

## Keyword Definitions

- **MUST / REQUIRED** — non-negotiable for shipped behavior
- **SHOULD / RECOMMENDED** — expected default behavior; deviations require a clear product or implementation reason
- **MAY / OPTIONAL** — permitted but not required

---

## Precedence

- This file defines the shared typography baseline.
- Component specs MAY specialize within their domain, but they MUST NOT weaken this baseline without documenting the change and updating this file if the baseline itself changes.
- `docs/specs/GLOBAL.md` owns global accessibility and shell-level requirements.
- `docs/specs/LAYOUT.md` owns spacing, container, and breakpoint layout rules.
- `docs/product/DOCTRINE.md` guides judgment but does not override measurable typography requirements.

---

## Status and Current Evidence

### Current implementation sources
Implemented in:
- `templates/base.html`
- `static/css/base/tokens.css`
- `static/css/base/base.css`
- `static/css/components/nav.css`
- `static/css/components/hero.css`
- `static/css/components/components.css`
- `static/css/components/buttons.css`
- `apps/projects/static/css/project-cards.css`
- `static/css/components/footer.css`

### Current automated / direct evidence
Backed in part by:
- `tests/e2e/test_homepage.py`
- `tests/e2e/test_navigation.py`
- `tests/pages/test_views.py`
- typography-focused screenshot audit artifacts and analysis captured during the March 2026 refinement pass

### Current evidence model
This file distinguishes between:
- **Required baseline** — what must be true
- **Currently implemented** — what code currently does
- **Current evidence** — what tests and screenshot review currently prove
- **Known gap / release target** — what is expected but not yet fully automated or fully proven

This prevents the typography spec from overstating enforcement.

---

## 1. Typography Baseline Requirements

### 1.1 Font stack and loading

#### Font families
The public UI uses a two-family system:

| Role | Font |
| --- | --- |
| Display / brand / editorial headings | `Cormorant Garamond` |
| Functional UI / body / controls | `DM Sans` |

#### Baseline requirements
- Serif display text MUST be reserved for identity, editorial emphasis, and high-level headings.
- Sans text MUST carry body copy, navigation labels, button labels, metadata, and functional UI text unless a current implemented component intentionally promotes a mobile overlay state into a display role.
- Fonts MUST be loaded once at the shared template level.
- Font loading MUST avoid a broken first-render experience.
- Current implementation preconnects to Google Fonts and loads both families once from `templates/base.html` using `display=swap`.

---

### 1.2 Body text baseline

#### Required baseline
- Base body size MUST remain at `1rem` (`16px` at the default root size).
- Base body text MUST prioritize readability over extreme visual lightness.
- Body line-height MUST support sustained reading.

#### Current implemented values

| Selector | Current value |
| --- | --- |
| `body` font-family | `DM Sans` |
| `body` font-size | `1rem` |
| `body` font-weight | `400` |
| `body` line-height | `1.7` |

#### Rationale
This is the practical reading baseline for public copy. It supports portfolio reading, project summaries, and supporting text across real devices.

---

### 1.3 Display typography baseline

Display typography uses the serif family and carries most of the visual identity.

#### Required baseline
- Display typography MUST remain readable when wrapped.
- Display typography MAY be tight on desktop, but it MUST gain breathing room at narrower breakpoints where wrapping becomes more likely.
- Thin display styling MUST NOT become fragile on mobile over imagery.

#### Current implemented display roles

| Element | Current value |
| --- | --- |
| `hero__title` | `clamp(3rem, 7vw, 6.5rem)` |
| `section__title` | `clamp(2rem, 4vw, 3.25rem)` |
| `homepage-coda__title` | `clamp(1.4rem, 2.2vw, 2rem)` |
| `project-card__title` | `clamp(1.25rem, 1.8vw, 1.5rem)` |

---

### 1.4 Micro-scale baseline

Jeannote uses a disciplined two-tier micro-scale for small text.

#### Required baseline
Small text in the public UI MUST resolve into two main functional tiers:

| Tier | Size | Use |
| --- | ---: | --- |
| Metadata / decorative label tier | `0.75rem` | labels, eyebrow text, quiet metadata |
| Functional small-text tier | `0.875rem` | links, buttons, supporting readable copy, card supporting text |

Values between these tiers SHOULD be minimized unless a specific text role clearly justifies them.

#### Current implemented examples

| Selector | Current value |
| --- | --- |
| `hero__label` | `0.75rem` |
| `section__label` | `0.75rem` |
| `project-card__meta` | `0.75rem` |
| `nav__link` | `0.875rem` |
| `section__header-link` | `0.875rem` |
| `project-card__cta` | `0.875rem` |
| `project-card__desc` | `0.875rem` |
| `.btn` | `0.875rem` |
| `.btn--large` | `0.875rem` |

#### Exception note
Decorative exceptions MAY sit below the functional small-text tier when they are not primary reading targets. Current implemented example: `.hero__scroll` uses `0.7rem` because it is a decorative scroll affordance, not body copy or functional UI text.

---

## 2. Current Implemented Typography Contract

### 2.1 Shared body and supporting text

| Area | Current implemented requirement |
| --- | --- |
| Base copy | Body copy uses `DM Sans`, `1rem`, `400`, `1.7` line-height |
| Supporting text | Supporting public text inherits body weight unless a component overrides it explicitly |
| Muted/supporting copy | Supporting copy remains subordinate by color and role, not by extreme weight reduction |
| Functional labels | Functional small text uses the `0.875rem` tier |
| Quiet metadata | Decorative/meta text uses the `0.75rem` tier |

---

### 2.2 Hero typography

| Area | Current implemented requirement |
| --- | --- |
| Title family | `Cormorant Garamond` |
| Title size | `clamp(3rem, 7vw, 6.5rem)` |
| Title weight | `300` by default; `400` at `max-width: 767px` |
| Title line-height | `1.02` by default; `1.06` from `768px` to `1024px`; `1.1` at `max-width: 767px` |
| Title letter-spacing | `-0.02em` |
| Subtitle family | `DM Sans` |
| Subtitle size | `clamp(1rem, 2.5vw, 1.4rem)` |
| Subtitle weight | `300` |
| Subtitle line-height | `1.6` |
| Label family | `DM Sans` |
| Label size | `0.75rem` |

#### Current hero breakpoint intent
- **Desktop:** expressive display, tight editorial rhythm
- **Tablet:** balanced display, slightly relaxed title line-height, stronger subtitle presence
- **Mobile:** compact display, stronger title weight, safer line-height

---

### 2.3 Navbar / brand typography

| Area | Current implemented requirement |
| --- | --- |
| Brand text family | `Cormorant Garamond` |
| Brand text size | `1.1rem` |
| Brand text weight | `500` |
| Brand text tracking | `0.05em` |
| Brand text transform | uppercase |
| Monogram family | `Cormorant Garamond` |
| Monogram size | `1.5rem` |
| Monogram weight | `500` |
| Monogram tracking | `0.15em` |
| Monogram transform | uppercase |
| Desktop / tablet nav link family | `DM Sans` |
| Desktop / tablet nav link size | `0.875rem` |
| Desktop / tablet nav link weight | `400` |
| Desktop / tablet nav link tracking | `0.04em` |
| Mobile overlay nav link family | `Cormorant Garamond` |
| Mobile overlay nav link size | `2rem` |
| Mobile overlay CTA treatment | `nav__cta` resets to the same serif `2rem` link system as the other overlay links |

#### Required baseline
- Brand text and monograms MUST read as identity elements, not generic utility text.
- Functional desktop and tablet nav links MUST remain readable at the functional small-text tier.
- Monograms MUST remain typographically distinct from ordinary navbar text.
- Mobile overlay nav links MAY elevate into a display treatment, but they MUST remain visually coherent with the overlay navigation system rather than mixing small utility text with large editorial text.

---

### 2.4 CTA and interactive text

| Area | Current implemented requirement |
| --- | --- |
| Button family | `DM Sans` |
| Button size | `0.875rem` |
| Button weight | `400` |
| Button transform | uppercase |
| Header link action text | `0.875rem` |
| Card CTA text | `0.875rem` |

#### Required baseline
- Interactive text MUST remain readable at the functional small-text tier unless a current implemented mobile-overlay navigation state intentionally promotes it into the display system.
- CTA labels MUST NOT rely on undersized text to appear refined.
- Button sizing MAY vary by padding and container treatment, but not by drifting to an inconsistent text scale without reason.

---

### 2.5 Section and card typography

| Area | Current implemented requirement |
| --- | --- |
| Section title | `clamp(2rem, 4vw, 3.25rem)` in serif display treatment |
| Coda title | `clamp(1.4rem, 2.2vw, 2rem)` in serif display treatment |
| Project card title | `clamp(1.25rem, 1.8vw, 1.5rem)` |
| Project card description | `0.875rem` |
| Project card meta | `0.75rem` |

#### Required baseline
- Card titles MUST read as titles, not as enlarged body text.
- Card descriptions MUST remain comfortably readable at the functional small-text tier.
- Section hierarchy MUST preserve clear separation between label, title, and supporting text.

---

### 2.6 Footer typography

| Area | Current implemented requirement |
| --- | --- |
| Footer brand family | `Cormorant Garamond` |
| Footer brand size | `1.1rem` |
| Footer brand tracking | `0.05em` |
| Footer brand transform | uppercase |
| Footer tagline size | `0.875rem` |
| Footer tagline line-height | `1.6` |
| Footer social link size | `0.75rem` |
| Footer social link weight | `500` |
| Footer social link tracking | `0.08em` |

#### Required baseline
- Footer brand text MUST remain aligned with the same identity system as the navbar brand.
- Footer supporting text MUST remain readable and subordinate without collapsing into decorative undersizing.
- Footer utility links MAY use the metadata tier, but they MUST remain readable against the footer contrast treatment.

---

## 3. Responsive Typography Rules

### 3.1 Desktop baseline

#### Required behavior
At desktop widths:
- display typography MAY be tighter and more editorial
- hierarchy MUST remain strong
- supporting text MUST remain subordinate without becoming weak
- text measure MUST remain readable

#### Current implemented emphasis
Desktop is the strongest editorial expression of the type system.

---

### 3.2 Tablet baseline

#### Required behavior
Tablet MUST feel intentionally designed, not merely interpolated between desktop and mobile.

#### Current implemented tablet refinements
- Hero title line-height is relaxed to `1.06` between `768px` and `1024px`
- Hero subtitle clamp scales visibly through the tablet range instead of flattening at the mobile floor
- Project card title floor is raised to maintain title presence on tablet

#### Required outcome
Tablet typography MUST preserve:
- readable hero wrapping behavior
- a real second-level hierarchy in the hero subtitle
- project card titles that still read like titles

---

### 3.3 Mobile baseline

#### Required behavior
Mobile typography MUST prioritize robustness and readability over extreme delicacy.

#### Current implemented mobile refinements
- Hero title weight increases to `400`
- Hero title line-height increases to `1.1`
- Body text remains at the `16px` baseline
- Functional small-text tier remains readable at `0.875rem`
- Mobile nav overlay links shift into a serif display treatment at `2rem`

#### Required outcome
Mobile hero typography MUST NOT become fragile over imagery due to overly light weight or overly tight leading.

---

## 4. Readability Constraints

### 4.1 Minimum body readability
- Body and body-like text MUST remain at or above the `1rem` baseline unless a role is explicitly small-text metadata, functional small text, or a decorative non-reading exception.
- Supporting readable copy MUST prefer the functional small-text tier over decorative undersizing.

### 4.2 Wrapping safety
- Wrapped display text MUST retain enough line-height to remain readable.
- Long-title stress states MUST NOT create visibly trapped or colliding serif lines at mobile widths.

### 4.3 Hierarchy integrity
- Hero title MUST dominate hero subtitle.
- Hero subtitle MUST remain visibly stronger than generic body copy.
- Card titles MUST remain visually distinct from card descriptions.
- Brand identity text MUST remain distinct from nav-link utility text.

---

## 5. Audit Checks

Every required typography state MUST map to evidence in `docs/qa/TEST_MATRIX.md`.

### Requirement-to-audit traceability

| Requirement section | Primary audit anchors |
| --- | --- |
| 1.2 Body text baseline | typography screenshot review, footer/supporting-text review |
| 1.3 Display typography baseline | hero desktop/tablet/mobile audit states |
| 1.4 Micro-scale baseline | card/CTA/supporting-text audit states |
| 2.2 Hero typography | hero default and stress-state evidence |
| 2.3 Navbar / brand typography | navbar brand states, monogram states, mobile overlay nav states |
| 2.6 Footer typography | footer supporting-text review |
| 3.2 Tablet baseline | tablet hero and tablet card-title audit states |
| 3.3 Mobile baseline | mobile hero default and long-title stress states |
| 4.2 Wrapping safety | long-title mobile audit evidence |

### Current audit expectations

| ID | Check | Pass condition |
| --- | --- | --- |
| T-01 | Font load | Base template loads both Google Fonts families exactly once with `display=swap`. |
| T-02 | Body baseline | `body` computes to sans `1rem / 1.7` regular text. |
| T-03 | Hero desktop hierarchy | Desktop hero title, subtitle, and CTA hierarchy remain visibly ordered and readable. |
| T-04 | Hero tablet hierarchy | Tablet hero subtitle retains real second-level hierarchy and does not collapse into generic body copy. |
| T-05 | Hero mobile robustness | Mobile hero title remains readable over imagery with current weight and line-height rules. |
| T-06 | Long-title mobile wrap | Long hero title wraps without cramped leading or broken composition. |
| T-07 | Card title readability | Project card titles still read as titles at tablet and desktop widths. |
| T-08 | Body and supporting readability | Body, footer, and supporting text remain readable after current body-weight and micro-scale rules. |
| T-09 | Navbar identity distinction | Brand text, monogram, and mobile overlay links remain typographically distinct from desktop utility nav text. |

---

## 6. Current Known Gaps / Release Targets

These are expectations that may not yet be fully automated or fully evidenced as dedicated typography assertions.

- Some typography states are still proven primarily by screenshot review rather than dedicated numeric assertions.
- Cross-browser typography rendering differences, especially serif rendering outside Chromium, remain a release sign-off concern unless explicitly automated.
- If typography coverage grows substantially, some checks MAY later move into more targeted visual or computed-style assertions.

These items MUST NOT be silently treated as fully automated if they are not.

---

## 7. Documentation and QA Linkage

### 1:1 Rule
Every required typography state MUST map to one or more rows in:
- `docs/qa/TEST_MATRIX.md`

### Behavior-change rule
If shared typography behavior changes:
- update this file
- update any affected component spec
- update the relevant matrix rows
- update tests or screenshot evidence where required
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
- `docs/specs/GLOBAL.md`
- `docs/specs/LAYOUT.md`
- `docs/specs/components/HERO.md`
- `docs/specs/components/NAVBAR.md`
- `docs/qa/TESTING.md`
- `docs/qa/TEST_MATRIX.md`
