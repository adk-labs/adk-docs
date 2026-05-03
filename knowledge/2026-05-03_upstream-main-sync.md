# 2026-05-03 Upstream Main Sync

## Scope

- Fetched `upstream/main` and `origin/main` on 2026-05-03 (Asia/Seoul).
- Merged `upstream/main` into local `main`.
- Latest upstream commit at fetch time: `7e3b3863` `Remove metrics page that documents unreleased functionality (#1712)`.
- Local merge commit: `229e53ab`.

## Merge Notes

- Merge initially conflicted in:
  - `docs/community/index.md`
  - `docs/tools-custom/mcp-tools.md`
- Resolved by accepting upstream asset/link updates:
  - ADK Live API community card now uses `community-adk-gemini-live-api.png`.
  - MCP filesystem example image now uses Markdown image syntax.

## Change-Log Review

- Reviewed `upstream-doc-change-log` entries through `2026-05-02.md`.
- Key document changes included:
  - Agent Engine to Agent Runtime rename.
  - Vertex AI Search to Agent Search / Grounding with Search rename.
  - Vertex AI RAG Engine to Knowledge Engine rename.
  - MLflow tracing split and MLflow Gateway addition.
  - New integrations for Agent Registry, Database Memory, Cisco AI Defense, Datadog.
  - New observability traces page.
  - New runtime Ambient Agents page.

## Validation

- `git fetch upstream --prune`
- `git fetch origin --prune`
- `git merge --no-edit upstream/main`
- `git diff --check`
