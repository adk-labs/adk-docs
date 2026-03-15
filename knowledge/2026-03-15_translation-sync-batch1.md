# 2026-03-15 Translation Sync Batch 1

## Scope

- Upstream window: 2026-03-12 through 2026-03-15
- Basis: `upstream/main` merged into local `main` at `8a03175972de08674faaf302b37b7ecc7b687b2c`
- Source of change detection:
  - `upstream-doc-change-log/2026-03-12.md`
  - `upstream-doc-change-log/2026-03-14.md`

## English source docs synced

- `docs/tutorials/coding-with-ai.md`
- `docs/agents/config.md`
- `docs/agents/models/google-gemini.md`
- `docs/apps/index.md`

## Localized files updated

- `docs/ko/tutorials/coding-with-ai.md`
- `docs/ja/tutorials/coding-with-ai.md`
- `docs/ko/agents/config.md`
- `docs/ja/agents/config.md`
- `docs/ko/agents/models/google-gemini.md`
- `docs/ja/agents/models/google-gemini.md`
- `docs/ko/apps/index.md`
- `docs/ja/apps/index.md`

## Change summary

- Renamed `ADK Skills` to `ADK Dev Skills` and synced the new global install command in `coding-with-ai`
- Added Java support markers and programmatic loading guidance to localized `agents/config`
- Synced new Java retry and Interactions API examples into localized `google-gemini`
- Added Java `App` construction and runner examples to localized `apps/index`

## Quantitative summary

- English source docs synced: 4
- Localized docs updated: 8
- Knowledge files added in this batch: 1
- Total files in this batch: 9

## Verification

- Reviewed merged upstream diffs for all four English docs against current ko/ja translations
- Preserved tabbed code blocks, fences, and localized prose structure
- Ran `git diff --check` on all files in this batch

## Remaining work

The following larger docs remain for batch 2 sync:

- `docs/context/caching.md`
- `docs/context/index.md`
- `docs/sessions/state.md`
