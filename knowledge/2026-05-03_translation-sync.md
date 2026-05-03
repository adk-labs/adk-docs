# 2026-05-03 Translation Sync

## Scope

- Synced Korean and Japanese docs for the latest upstream changes after merge `229e53ab`.
- Confirmed English source document coverage for `docs/ko` and `docs/ja`: 0 missing files, excluding the local internal `docs/translation-upstream-sync-spec.md`.

## Main Changes

- Added localized pages for new upstream docs:
  - `integrations/agent-registry`
  - `integrations/cisco-ai-defense`
  - `integrations/database-memory`
  - `integrations/datadog`
  - `integrations/mlflow-gateway`
  - `observability/traces`
  - `runtime/ambient-agents`
- Renamed and refreshed localized docs for upstream product/path renames:
  - `agents/models/agent-platform`
  - `deploy/agent-runtime/*`
  - `grounding/grounding_with_search`
  - `integrations/agent-search`
  - `integrations/code-exec-agent-runtime`
  - `integrations/knowledge-engine`
  - `integrations/mlflow-tracing`
- Updated localized `mkdocs.yml` navigation for:
  - Agent Platform hosted models
  - Agent Runtime deployment
  - Ambient Agents
  - Observability Traces
  - Grounding with Search
- Added localized copies of new image assets used by translated pages.
- Updated localized community cards from Vertex AI Live API to Gemini Live API.
- Normalized stale localized rename links and malformed admonition markers.

## Validation

- KO/JA missing translation audit: `ko missing 0`, `ja missing 0`.
- Targeted Markdown integrity check for the 17 renamed/new docs:
  - code fence counts match source
  - Markdown link counts match source
  - no generated placeholder residue
  - no malformed admonition markers in generated target docs
- `git diff --check`
- `uv run --with-requirements requirements.txt mkdocs build`
  - Result: build completed successfully.
  - Note: `mkdocs build --strict` still fails because the repo currently has many pre-existing link/anchor and `mkdocs_llmstxt` warnings outside this sync scope.
