# 2026-04-10 Translation Sync Batch 2

## Scope

- Synced ko/ja docs for the 2026-04-07 to 2026-04-10 upstream changes outside the homepage/evaluate batch.
- Updated localized nav and include handling in `mkdocs.yml`.
- Added new localized integration pages:
  - `agentphone`
  - `environment-toolset`
  - `firestore-session-service`

## Main Areas

- A2A
- agents
- apps
- artifacts
- community
- context/compaction
- deploy/gke
- get-started
- grounding
- integrations
- observability
- plugins
- safety
- sessions
- skills
- streaming
- tools-custom
- tutorials
- workflows

## Follow-up Adjustments Included In This Batch

- Localized internal links in changed ko/ja docs where matching localized targets exist.
- Synced new homepage include usage with localized navigation behavior.
- Brought changed Gemini model references to `gemini-flash-latest` where upstream already moved.

## Validation

- `git diff --check`
- localized internal-link scan for currently changed ko/ja files
- file presence check for new localized pages
