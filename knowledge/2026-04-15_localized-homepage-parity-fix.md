# 2026-04-15 Localized Homepage Parity Fix

## Scope

- Investigated the reported visual mismatch between:
  - `https://adk.dev/`
  - `https://adk-labs.github.io/adk-docs/ko/`
- Verified the currently deployed ko/ja homepage asset paths.
- Fixed remaining homepage-specific rendering mismatch in the theme override.

## Diagnosis

- The localized homepage asset paths were already serving correctly on the live site:
  - `../stylesheets/homepage.css`
  - `../assets/hp-adk-web1.png`
  - `../assets/integrations-list.png`
  - `../assets/adk-eval-case.gif`
  - `../assets/adk-demo.cast`
- The remaining visual difference was caused by the content action buttons (`Edit`, `View source`, `Copy`) appearing on:
  - `docs/ko/index.md`
  - `docs/ja/index.md`
- Root cause:
  - `overrides/partials/actions.html` excluded only `index.md`
  - localized homepage source paths (`ko/index.md`, `ja/index.md`) were still treated as normal content pages

## Changes

- Updated `overrides/partials/actions.html` to exclude homepage action buttons for:
  - `index.md`
  - `ko/index.md`
  - `ja/index.md`
- Added a homepage CSS fallback in `docs/stylesheets/homepage.css` to hide `.md-content__button` on landing pages.

## Validation

- live HTML inspection with `curl`
- confirmed correct localized asset references in deployed ko/ja homepage HTML
- `git diff --check`
