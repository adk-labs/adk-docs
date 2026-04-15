# 2026-04-15 Localized Homepage Breadcrumb Fix

## Scope

- Investigated the remaining localized homepage mismatch on:
  - `https://adk-labs.github.io/adk-docs/ko/`
  - `https://adk-labs.github.io/adk-docs/ja/`
- Compared live localized homepage HTML against `https://adk.dev/`.

## Diagnosis

- The localized homepage asset paths were already correct.
- The remaining visual mismatch came from the Material breadcrumb path component:
  - `Agent Development Kit (ADK) > 홈`
  - `Agent Development Kit (ADK) > ホーム`
- Live inspection showed `navigation.path` was still rendered above the landing content on localized homepages.

## Changes

- Updated `docs/stylesheets/homepage.css` to hide `.md-path` on landing pages via the existing `body.adk-landing-page` scope.

## Validation

- live HTML inspection with `curl`
- `git diff --check`
