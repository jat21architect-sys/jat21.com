# Layout Specification

**Status:** Active  
**Applies to:** Shared spatial system, containers, section rhythm, and cross-page responsive layout behavior  
**Last updated:** 2026-04-03

## Scope

This file defines the measurable layout system used across Jeannote's public UI.

It covers:
- layout tokens and container widths
- shared gutter behavior
- section spacing rhythm
- sticky offset consistency below the fixed header
- shared project-grid behavior
- homepage per-breakpoint featured-project visibility rules
- current responsive footer grid behavior
- breakpoints in active use
- layout audit checks

It does not define:
- typography rules
- color and visual styling rules unrelated to spacing or structure
- global shell interaction logic
- buyer-facing configuration guidance
- page-specific layout systems that are not yet part of the shared baseline

Those belong in:
- `docs/specs/TYPOGRAPHY.md`
- `docs/specs/GLOBAL.md`
- `docs/specs/components/HERO.md`
- `docs/specs/components/NAVBAR.md`
- `docs/admin/CUSTOMIZATION.md`

---

## Keyword Definitions

- **MUST / REQUIRED** — non-negotiable for shipped behavior
- **SHOULD / RECOMMENDED** — expected default behavior; deviations require a clear product or implementation reason
- **MAY / OPTIONAL** — permitted but not required

---

## Precedence

- This file defines the shared layout baseline.
- Component specs MAY specialize within their domain, but they MUST NOT weaken this baseline without documenting the change and updating this file if the baseline itself changes.
- `docs/specs/GLOBAL.md` owns shell-level and accessibility baselines.
- `docs/specs/TYPOGRAPHY.md` owns type metrics and hierarchy, not spacing or structural layout.
- `docs/product/DOCTRINE.md` guides judgment but does not override measurable layout requirements.

---

## Status and Current Evidence

### Current implementation sources
Implemented in:
- `static/css/base/tokens.css`
- `static/css/base/base.css`
- `apps/projects/static/css/project-cards.css`
- `static/css/components/footer.css`
- `static/css/components/hero.css`
- `templates/base.html`
- `apps/pages/views.py`
- `apps/site/models/site.py`

### Current automated / direct evidence
Backed in part by:
- `tests/pages/test_views.py`
- `tests/core/test_models.py`
- direct CSS and template review captured during the March 2026 refinement pass

### Current evidence model
This file distinguishes between:
- **Required baseline** — what must be true
- **Currently implemented** — what code currently does
- **Current evidence** — what tests and direct review currently prove
- **Known gap / release target** — what is expected but not yet fully automated or fully proven

This prevents the layout spec from overstating enforcement.

---

## 1. Layout Baseline Requirements

### 1.1 Container and gutter baseline

#### Layout tokens

| Token | Value | Use |
| --- | --- | --- |
| `--container` | `1280px` | Default max content width |
| `--container-narrow` | `780px` | Narrow reading or confirmation layouts |
| `--gutter` | `clamp(1.5rem, 4vw, 3rem)` | Shared horizontal page padding |
| `--space-sm` | `1rem` | Small gaps |
| `--space-md` | `2rem` | Mid gaps / compact sections |
| `--space-lg` | `4rem` | Standard large section gap on mobile |
| `--space-xl` | `7rem` | Standard large section gap on desktop |

#### Required baseline
- Shared page containers MUST use the common container and gutter tokens.
- Reading and confirmation layouts MAY use the narrow container token.
- Shared horizontal padding MUST remain token-driven rather than hard-coded per template.
- `main` MUST flex to fill the remaining vertical shell space below the fixed header.

---

### 1.2 Section rhythm baseline

#### Required baseline
- Standard sections MUST use the shared vertical rhythm tokens rather than ad hoc per-page spacing.
- Archive and browse layouts MAY use a denser section rhythm when the filter bar already provides visual separation, but that density belongs in the owning feature CSS rather than the shared base layer.
- Shared section surface variants MUST preserve the same spacing rhythm as the base section treatment unless explicitly documented otherwise.

---

### 1.3 Sticky and offset baseline

#### Required baseline
- Shared sticky surfaces that sit below the fixed header MUST use the same top offset as the header height.
- Offset values MUST remain consistent across header-adjacent sticky systems.

---

### 1.4 Grid and count baseline

#### Required baseline
- Shared project grids MUST collapse cleanly across the active breakpoint system.
- Homepage featured-project visibility MUST be driven by validated admin counts, not by unvalidated template logic.
- Count-driven responsive hiding MUST be signaled through explicit HTML classes so CSS can enforce per-breakpoint limits.

---

### 1.5 Breakpoint baseline

#### Required baseline
- Breakpoints in active use MUST be documented with their current purpose.
- Tablet and mobile behavior MUST read as intentional layout states, not accidental by-products of desktop CSS.

---

## 2. Current Implemented Layout Contract

| Area | Current implemented requirement |
| --- | --- |
| `.container` | Max width `1280px`, centered with shared gutter padding. |
| `.container--narrow` | Max width `780px`, centered with the same gutter behavior as `.container`. |
| `main` | Expands to fill remaining vertical space because `body` is a flex column and `main` is `flex: 1`. |
| `.section` | Default `padding-block` is `var(--space-lg)` (4rem) — mobile-safe base. Enhanced to `var(--space-xl)` (7rem) at `min-width: 769px`. |
| `.section--tinted` | Uses tinted background only; spacing remains the same as `.section`. |
| Shared header offset | Fixed header height is `var(--header-height)` (4.5rem). The filter bar sits directly below the header (`top: var(--header-height)`). Sticky sidebars (about, contact) include 1rem breathing room (`top: calc(var(--header-height) + 1rem)`). |
| Filter bar | `.filter-bar` is sticky with `top: var(--header-height)` and `z-index: 50`. |
| Page hero short layout | `.page-hero--short` uses `padding-block: calc(var(--header-height) + var(--space-md)) var(--space-md)`. |
| `.projects-grid` default | 2 columns with `2rem` gap. |
| `.projects-grid--featured` default | 12-column grid with standard cards spanning 4 columns and large cards spanning 8. |
| Homepage featured grid base | `.projects-grid--home` defaults to 2 columns with `2rem` gap before count-driven desktop overrides apply. |
| Homepage query cap | `HomeView` queries at most `homepage_projects_desktop_count` items before responsive hiding is applied. |
| Homepage project count defaults | Defaults are mobile `3`, tablet `4`, desktop `6`. |
| Homepage project count validation | Each count must be between `1` and `6`; mobile cannot exceed tablet; tablet cannot exceed desktop. |
| Homepage count classes | Homepage grid includes `hp-mob-N` and `hp-tab-N` classes that match `SiteSettings`. |
| Mobile homepage hiding | At `<=639px`, `hp-mob-N` hides cards after the `N`th item. |
| Tablet homepage hiding | At `640-959px`, `hp-tab-N` hides cards after the `N`th item. |
| Desktop homepage columns | At `>=960px`, `projects-grid--home-n1` becomes a single contained column up to `480px`; `n3`, `n5`, and `n6` use 3 columns; `n2` and `n4` remain 2 columns. |
| Featured grid fallback | At `<=1024px`, featured grids collapse to 2 columns; at `<=640px`, they collapse to 1 column. |
| Footer grid default | `.footer__inner` uses 3 columns by default. |
| Footer grid no-contact fallback | When `.footer__contact` is absent, `.footer__inner` collapses to 2 columns. |
| Footer tablet layout | At `<=768px`, `.footer__inner` remains 2 columns, brand spans both columns, and footer bottom content stacks vertically. |
| Footer phone layout | At `<=480px`, `.footer__inner` collapses to 1 column and the footer spacing tightens from `var(--space-xl)` / `var(--space-lg)` to `var(--space-lg)` / `var(--space-md)`. |

---

## 3. Responsive Layout Rules

### 3.1 Desktop baseline

#### Required behavior
At desktop widths:
- containers MUST cap at the shared max width
- standard sections MUST use the full desktop vertical rhythm
- homepage featured grids MUST follow the count-driven desktop column rules

#### Current implemented emphasis
Desktop is the widest expression of the shared container system and the only range where homepage count classes change the column count rather than just hiding overflow cards.

---

### 3.2 Tablet baseline

#### Required behavior
Tablet MUST feel intentionally composed, not merely compressed desktop CSS.

#### Current implemented tablet refinements
- Homepage `hp-tab-N` hiding applies only from `640px` to `959px`
- Featured project grids collapse from 12-column behavior to 2 columns at `<=1024px`
- Footer layout stays at 2 columns through `768px`

#### Required outcome
Tablet layout MUST preserve:
- deliberate homepage project counts
- readable multi-column featured-project layouts
- footer balance without premature single-column collapse

---

### 3.3 Mobile baseline

#### Required behavior
Mobile layout MUST prioritize robustness and clear vertical flow over preserving desktop density.

#### Current implemented mobile refinements
- Shared project grids collapse to 1 column at `<=640px`
- Homepage `hp-mob-N` hiding applies at `<=639px`
- Footer layout collapses to 1 column at `<=480px`
- Footer spacing tightens at `<=480px`
- Filter buttons compress further at `<=480px`

#### Required outcome
Mobile layout MUST NOT create horizontal overflow, broken card grids, or footer dead zones caused by desktop assumptions surviving into narrow screens.

---

## 4. Audit Checks

Every required layout state MUST map to evidence in `docs/qa/TEST_MATRIX.md`.

### Requirement-to-audit traceability

| Requirement section | Primary audit anchors |
| --- | --- |
| 1.1 Container and gutter baseline | L-01, L-02 |
| 1.2 Section rhythm baseline | L-03 |
| 1.3 Sticky and offset baseline | L-04 |
| 1.4 Grid and count baseline | L-05, L-06, L-07, L-08, L-09 |
| 1.5 Breakpoint baseline | L-07, L-08, L-09 |

### Current audit expectations

| ID | Check | Pass condition |
| --- | --- | --- |
| L-01 | Container width | `.container` maxes at `1280px` and keeps gutter padding on both sides. |
| L-02 | Narrow container | `.container--narrow` maxes at `780px`. |
| L-03 | Section rhythm | `.section` computes to `4rem` vertical padding by default (mobile) and `7rem` at `min-width: 769px` (desktop). |
| L-04 | Sticky offset consistency | Filter bar `top` equals `var(--header-height)`. Sticky sidebars use `calc(var(--header-height) + 1rem)`. Both track the token. |
| L-05 | Homepage context classes | Homepage grid HTML includes `hp-mob-N` and `hp-tab-N` classes that match current `SiteSettings`. |
| L-06 | Homepage count validation | Invalid count combinations fail model validation before they reach templates. |
| L-07 | Mobile project hiding | At a mobile viewport, cards after the configured `hp-mob-N` threshold are not displayed. |
| L-08 | Tablet project hiding | At a tablet viewport, cards after the configured `hp-tab-N` threshold are not displayed. |
| L-09 | Desktop home grid | Desktop grid columns match the count-driven rules for `n1`, `n3`, `n5`, and `n6`. |

---

## 5. Current Known Gaps / Release Targets

These are expectations that may not yet be fully automated or fully evidenced as dedicated layout assertions.

- Some `L-*` rows are now mirrored in `docs/qa/TEST_MATRIX.md` through direct CSS review rather than dedicated browser assertions. In particular, the responsive homepage hiding rules and desktop count-grid rules are not yet proven by dedicated viewport tests.
- Responsive footer-grid behavior is currently documented here but not yet represented by a dedicated `L-*` audit row.
- Broader page-specific layout systems such as About, Contact, Services, and Project Detail layouts remain outside this shared-layout baseline unless separately specified.

These items MUST NOT be silently treated as fully automated or fully mirrored if they are not.

---

## 6. Documentation and QA Linkage

### 1:1 Rule
Every required layout state MUST map to one or more rows in:
- `docs/qa/TEST_MATRIX.md`

### Behavior-change rule
If shared layout behavior changes:
- update this file
- update any affected component or page-level spec
- update the relevant matrix rows
- update tests or direct review evidence where required
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
- `docs/specs/TYPOGRAPHY.md`
- `docs/specs/components/HERO.md`
- `docs/specs/components/NAVBAR.md`
- `docs/qa/TESTING.md`
- `docs/qa/TEST_MATRIX.md`
