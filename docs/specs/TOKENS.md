# Token Governance

**Status:** Active  
**Applies to:** Shared frontend token usage, theming boundaries, and token-growth control  
**Last updated:** 2026-04-03

## Scope

This file defines how Jeannote's CSS token layer is structured and how contributors should decide between primitives, semantic aliases, and local raw values.

It covers:
- token-layer responsibilities
- the definition of shared UI
- when a new primitive is allowed
- when a new semantic alias is allowed
- when a raw value is acceptable
- the default theming path for buyers and contributors
- a small acceptance checklist for CSS changes

It does not define:
- typography metrics
- spacing/layout behavior
- component contracts
- page-specific art direction rules

Those belong in:
- `docs/specs/TYPOGRAPHY.md`
- `docs/specs/LAYOUT.md`
- `docs/specs/components/`

---

## Core Rule

Semantic tokens are a customization seam, not a second palette.

---

## Ownership

This spec owns the token-governance rules for shared UI.

The implementation surface is:
- `static/css/base/tokens.css` for the token definitions
- shared shell/reusable CSS that consumes those tokens

If a change adds, removes, renames, or materially repurposes a shared token, this file should be updated in the same change.

---

## 1. Token Layers

### 1.1 Primitive layer

Primitives own source values such as:
- brand and neutral palette values
- font families
- type scale values
- spacing values
- layout constants
- motion constants

Current implementation source:
- `static/css/base/tokens.css`

Primitive values are the palette/source of truth. They are not the default authoring surface for shared UI styling.

### 1.2 Semantic layer

Semantic aliases own repeated shared-UI roles such as:
- page background
- muted/tinted shared surface
- inverse surface
- primary text color
- secondary/supporting text color
- inverse text color
- shared accent/emphasis
- subtle shared border on light surfaces
- focus ring

Current implementation source:
- `static/css/base/tokens.css`

Shared UI should prefer semantic aliases by default.

`--text-*` is reserved for typography scale values such as `--text-base`, `--text-sm`, and `--text-xs`.
Shared text-color roles should use a distinct family such as `--color-text-*`.

### 1.3 Component and page-local styling

Component/page CSS owns:
- composition
- exceptions
- local art direction
- overlays, translucency, gradients, and one-off visual tuning
- values that are not yet repeated enough to justify promotion

Local CSS may use:
- existing semantic aliases
- primitives directly
- raw values

Raw values are acceptable only when promoting them would add noise rather than reuse.

---

## 2. Definition of Shared UI

For this repo, **shared UI** means:
- repo-level shell CSS under `static/css/base/`
- repo-level shared components under `static/css/components/`
- repo-level utilities under `static/css/utilities/`
- repeated patterns rendered on multiple pages or apps, even if the file lives under an app

Current example:
- project cards in `apps/projects/static/css/project-cards.css`, because that pattern is used on the projects archive, related-projects sections, and the homepage.

It does **not** automatically mean:
- every app-local file
- every page-specific treatment
- every decorative overlay or transparency value
- every form-specific nuance in a feature app

---

## 3. Token Addition Rule

Every new value must answer one of these questions:

1. Is this a new brand/source value?
   If yes, add a primitive.

2. Is this a repeated role across shipped shared UI?
   If yes, add a semantic alias.

3. Is this only local, one-off, or art-direction specific?
   If yes, keep it local and do not add a token yet.

If a proposed token does not clearly satisfy one of those cases, it should not be added.

---

## 4. Theming Rule

For routine rebranding and downstream customization:
- edit semantic aliases first
- treat primitives as palette/source values
- avoid editing component CSS for global look-and-feel changes unless the change is genuinely component-specific

For one-off design work:
- use local values where that keeps intent clearer than introducing a new token

---

## 5. Naming Rule For Semantic Tokens

A semantic token must describe an owned role, not just a slightly different color.

Good role-oriented examples:
- page surface
- muted surface
- inverse surface
- default text
- muted text
- shared accent
- subtle border
- focus ring

Avoid adding vague near-duplicates such as:
- `surface-soft`
- `surface-subtle`
- `surface-light`

unless the codebase proves that those are distinct, repeated roles.

---

## 6. CSS Acceptance Checklist

Before merging a shared-UI CSS change, check:

- If the rule is shared UI, did you use a semantic alias by default?
- If you added a token, is it clearly a primitive or a repeated semantic role?
- If you added a semantic token, does it have a concrete owned role?
- If you used a raw value, is it local one-off styling, translucency, or art direction rather than a missing shared role?
- If the change is a global rebrand/theming change, did you try the semantic layer before editing component CSS?
- If you changed the shared token model itself, did you update `docs/specs/TOKENS.md` in the same change?

---

## 7. Current Non-Goals

The current system does **not** need:
- a large semantic token matrix
- component-specific token families
- multiple themes
- a large shadow/radius/z-index system
- blanket prohibition on primitive usage inside all component CSS

Token growth should stay controlled unless real shipped UI proves otherwise.
