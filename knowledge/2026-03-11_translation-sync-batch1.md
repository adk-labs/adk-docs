# 2026-03-11 Translation Sync Batch 1

## Scope

- Upstream window: 2026-03-06 through 2026-03-11
- Basis: `upstream/main` merged into local `main` at `d054fd262e88d02303b6b1ce05e426a58b2c85fb`
- Source of change detection:
  - `upstream-doc-change-log/2026-03-07.md`
  - `upstream-doc-change-log/2026-03-10.md`

## Work unit

This batch covers newly added English docs plus small and medium upstream edits
that were already isolated in ko/ja working tree diffs.

### New localized docs

- `docs/ko/agents/models/litert-lm.md`
- `docs/ja/agents/models/litert-lm.md`
- `docs/ko/integrations/galileo.md`
- `docs/ja/integrations/galileo.md`

### Synced localized updates

- `docs/ko/index.md`
- `docs/ja/index.md`
- `docs/ko/get-started/about.md`
- `docs/ja/get-started/about.md`
- `docs/ko/streaming/index.md`
- `docs/ja/streaming/index.md`
- `docs/ko/streaming/streaming-tools.md`
- `docs/ja/streaming/streaming-tools.md`
- `docs/ko/streaming/dev-guide/part1.md`
- `docs/ko/artifacts/index.md`
- `docs/ja/artifacts/index.md`
- `docs/ko/safety/index.md`
- `docs/ja/safety/index.md`
- `docs/ko/sessions/state.md`
- `docs/ja/sessions/state.md`
- `docs/ko/integrations/bigtable.md`
- `docs/ja/integrations/bigtable.md`
- `docs/ko/integrations/bigquery-agent-analytics.md`
- `docs/ja/integrations/bigquery-agent-analytics.md`
- `docs/ko/agents/models/index.md`
- `docs/ja/agents/models/index.md`

### Navigation

- `mkdocs.yml`
  - Added ko/ja nav entries for `LiteRT-LM`
  - Normalized localized internal links touched in this batch

## Quantitative summary

- New localized docs: 4
- Updated localized docs: 21
- Navigation files updated: 1
- Knowledge files added in this batch: 1
- Total files in this batch: 27

## Verification

- Reviewed English upstream diffs for this batch against current localized docs
- Preserved code fences, admonitions, and frontmatter where applicable
- Ran `git diff --check` on all files in this batch

## Remaining work

The following larger docs remain for batch 2 sync:

- `docs/context/index.md`
- `docs/plugins/index.md`
- `docs/sessions/memory.md`
- `docs/tutorials/coding-with-ai.md`
