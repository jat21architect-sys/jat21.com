# Documentation System

This directory is the implementation-facing documentation system for Jeannote. It documents current behavior, test coverage expectations, admin-facing configuration, and explicit product decisions.

The docs in this folder are not a redesign workspace. They are the operational source of truth for what is already built, how it is verified, and what must be updated in the same PR when behavior changes.

## Quick Start

1. Read this file first.
2. Read the shared specs before changing shared UI:
   - [specs/GLOBAL.md](specs/GLOBAL.md)
   - [specs/TYPOGRAPHY.md](specs/TYPOGRAPHY.md)
   - [specs/LAYOUT.md](specs/LAYOUT.md)
   - [specs/TOKENS.md](specs/TOKENS.md)
3. If the change touches a component, update its component spec in `docs/specs/components/`.
4. If the change is configurable in admin, update `docs/admin/FIELDS.md` and `docs/admin/CUSTOMIZATION.md` in the same PR.
5. If the change adds or removes a required state, update `docs/qa/TEST_MATRIX.md` in the same PR.
6. If code and docs disagree, fix the docs to match shipped behavior or fix the code before merge.

## Golden Rules

1. `1:1 Rule` - every required state in a component spec must map to a row in `qa/TEST_MATRIX.md`.
2. `Admin First Rule` - configurable features are not done until fields and customization behavior are documented.
3. `No Fluff Rule` - specs must use constraints, not adjectives.

## File Map

| Path | Purpose | Status |
| --- | --- | --- |
| [`docs/README.md`](README.md) | Operating guide for the doc system: structure, update rules, and contribution workflow. | Active |
| `docs/CHANGELOG.md` | Change history for this documentation system using Keep a Changelog style. Not the repo-root product release changelog. | Active |
| `docs/DECISION_LOG.md` | Reverse-chronological log of documentation and product decisions that affect specs, QA, or admin behavior. | Active |
| `docs/product/DOCTRINE.md` | Product principles only. No implementation detail, no layout rules, no marketing copy. | Active |
| [`docs/specs/TECHNICAL_SPEC.md`](specs/TECHNICAL_SPEC.md) | Gateway spec that points to the detailed specs and explains how the system fits together. | Active |
| [`docs/specs/GLOBAL.md`](specs/GLOBAL.md) | Shared site-shell, metadata, accessibility, motion, and cross-page behavior. | Active |
| [`docs/specs/TYPOGRAPHY.md`](specs/TYPOGRAPHY.md) | Measured type system: fonts, roles, sizes, weights, line-height, tracking, and text rules. | Active |
| [`docs/specs/LAYOUT.md`](specs/LAYOUT.md) | Shared spacing, container, grid, sticky-offset, and breakpoint rules. | Active |
| [`docs/specs/TOKENS.md`](specs/TOKENS.md) | Token governance: primitive vs semantic usage, theming rules, and the CSS acceptance checklist. | Active |
| `docs/specs/components/HERO.md` | Home hero contract: structure, states, content rules, and QA mapping. | Active |
| `docs/specs/components/NAVBAR.md` | Navigation contract: brand fallback, menu states, accessibility, and QA mapping. | Active |
| `docs/qa/TESTING.md` | Test strategy and scope by layer. | Active |
| `docs/qa/TEST_MATRIX.md` | Required state-to-test matrix for shared behavior and component states. | Active |
| `docs/qa/RELEASE_CHECKLIST.md` | Documentation-aware release gate. | Active |
| `docs/admin/FIELDS.md` | Field-by-field admin reference for configurable behavior. | Active |
| `docs/admin/CUSTOMIZATION.md` | Buyer-oriented guidance for what can be changed safely, with boundaries and expected outcomes. | Active |

## PR Documentation Checklist

- Update the affected spec in the same PR as the code change.
- Update `docs/qa/TEST_MATRIX.md` when a required state is added, removed, or redefined.
- Update admin docs when a feature is configurable, newly constrained, or newly protected.
- Keep every statement grounded in current implementation or current tests.
- Record measurable constraints, selectors, thresholds, and fallback behavior.
- Remove or rewrite statements that describe old behavior.
- If the change is user-visible and durable, add it to the appropriate changelog.

## Documentation Update Rules

- Document current implemented behavior, not intended future behavior.
- Prefer code-backed statements: selectors, thresholds, breakpoints, field limits, fallback order, and tested states.
- Cite the owning layer in prose when useful: template, CSS, JS, model, admin, or test.
- Keep `TECHNICAL_SPEC.md` as a gateway. Put detail in the specific spec that owns it.
- Put principles in `product/DOCTRINE.md`, not in implementation specs.
- Put buyer guidance in `admin/CUSTOMIZATION.md`, not in engineering specs.
- Do not create new folders or files unless the current structure clearly cannot represent shipped behavior.

## Stale Doc Policy

A doc is stale when either of these is true:

- It contradicts current code or tests.
- It omits a required state or configurable behavior that already ships.

Stale docs block merge. If an urgent code fix must land first, the affected doc must be updated in the same PR. If that is genuinely impossible, mark the doc with a short `Stale:` note at the top and clear it in the next follow-up PR.

## Current Docs Debt

- No open documentation debt is currently tracked in the docs system.
- Open QA backlog remains tracked in `qa/TEST_MATRIX.md`.

## How To Add A New Component

1. Confirm the component has a stable template/CSS/JS surface in the codebase.
2. Add `docs/specs/components/COMPONENT_NAME.md`.
3. Document only measurable requirements: DOM contract, content source, variants, required states, fallbacks, accessibility rules, and admin inputs.
4. Add a matching row for every required state in `docs/qa/TEST_MATRIX.md`.
5. Add or update tests that prove those states.
6. Update `docs/specs/TECHNICAL_SPEC.md` so the component is discoverable from the gateway spec.
7. If the component is configurable, update `docs/admin/FIELDS.md` and `docs/admin/CUSTOMIZATION.md` in the same PR.

## Scope Notes

- Legacy operational docs are intentionally kept outside the locked structure and linked here for now:
  [docs/recovery-runbook.md](recovery-runbook.md)
  [docs/sentry-rollout.md](sentry-rollout.md)
- They should remain in place unless a later maintenance pass explicitly migrates or retires them.
