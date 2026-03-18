# 2026-03-18 Translation Sync Batch 1

## Scope

- Upstream window: 2026-03-17 through 2026-03-18
- English source docs synced in this batch:
  - `docs/agents/llm-agents.md`
  - `docs/get-started/index.md`
  - `docs/integrations/bigquery-agent-analytics.md`

## Localized files updated

- `docs/ko/agents/llm-agents.md`
- `docs/ja/agents/llm-agents.md`
- `docs/ko/get-started/index.md`
- `docs/ja/get-started/index.md`
- `docs/ko/integrations/bigquery-agent-analytics.md`
- `docs/ja/integrations/bigquery-agent-analytics.md`

## Change summary

- Synced the Java output schema constant rename in localized `llm-agents`
- Added the technical overview link to localized `get-started/index`
- Reworked the advanced BigQuery analysis subsection headings and removed the deprecated `connection_id` argument from the root-cause query

## Verification

- Reviewed the merged upstream diffs for the three English source docs against the localized files
- Preserved localized heading hierarchy and SQL/code block structure
- Ran `git diff --check` on the batch 1 localized docs and this knowledge file
