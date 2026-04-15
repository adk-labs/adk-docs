# 2026-04-15 Translation Sync Batch 1

## Scope

- Synced ko/ja docs for the 2026-04-11 to 2026-04-15 upstream changes.
- Added new localized integration pages for `adspirer`.
- Fixed the localized landing pages so `/ko/` and `/ja/` use locale-specific homepage includes and correct relative asset paths.

## Main Areas

- `2.0/index`
- `apps/index`
- `artifacts/index`
- `context/compaction`
- `evaluate/user-sim`
- `events/index`
- `get-started`
- `integrations`
- `sessions/session`
- `tutorials/multi-tool-agent`
- localized homepage entry pages and homepage include assets

## Follow-up Adjustments Included In This Batch

- Synced the new Artifacts TypeScript snippets into ko/ja.
- Synced the new Events TypeScript sections into ko/ja.
- Added the missing `adspirer` localized pages in ko/ja.
- Brought the Japanese `bigquery-agent-analytics` document up to the latest upstream structure for views, state redaction, analytics queries, and credential-logging guidance.
- Fixed localized homepage include paths:
  - `docs/ko/index.md`
  - `docs/ja/index.md`
- Fixed localized homepage asset paths inside locale includes:
  - `docs/ko/_includes/homepage/_framework.md`
  - `docs/ko/_includes/homepage/_ecosystem.md`
  - `docs/ko/_includes/homepage/_eval.md`
  - `docs/ja/_includes/homepage/_framework.md`
  - `docs/ja/_includes/homepage/_ecosystem.md`
  - `docs/ja/_includes/homepage/_eval.md`

## Validation

- `git diff --check`
- targeted `rg` scans for stale markers and localized homepage asset/include paths
- attempted `mkdocs build --strict` in a temporary virtualenv, but local `python3` is `3.9.6` and `mkdocs-llmstxt==0.5.0` requires Python 3.10+, so build verification could not be completed on this machine
