# 2026-04-10 Upstream Main Sync

## Scope

- Fetched `upstream/main` on 2026-04-10 (Asia/Seoul).
- Reviewed `upstream-doc-change-log` entries for 2026-04-07 through 2026-04-10.
- Merged `upstream/main` into local `main`.

## Notes

- Latest upstream doc commit at merge time: `60f388b8` `docs: add note about Gemini latest selector (#1622)`.
- Merge commit created locally: `e4f97bdb`.
- Resolved the only merge conflict in `docs/tools-custom/mcp-tools.md`.
- Conflict resolution kept the new Grounding Lite image reference:
  - `../../assets/adk-tool-maps-lite-mcp-adk-web-demo.png`

## Change-Log Review

- 2026-04-07:
  - evaluate docs
  - `bigquery-agent-analytics`
  - sessions/session
  - tools-custom/authentication
- 2026-04-08:
  - homepage include split
  - `evaluate/environment_simulation`
  - `tools-custom/mcp-tools`
- 2026-04-09:
  - new `integrations/agentphone`
  - community
  - sessions/memory
- 2026-04-10:
  - new `integrations/environment-toolset`
  - new `integrations/firestore-session-service`
  - broad doc updates across agents, integrations, tools, workflows, sessions, plugins
  - `mkdocs.yml`

## Validation

- `git merge --no-edit upstream/main`
- manual conflict review in `docs/tools-custom/mcp-tools.md`
