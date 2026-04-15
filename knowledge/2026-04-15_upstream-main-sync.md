# 2026-04-15 Upstream Main Sync

## Scope

- Fetched `upstream/main` on 2026-04-15 (Asia/Seoul).
- Reviewed `upstream-doc-change-log` entries for 2026-04-11 through 2026-04-15.
- Merged `upstream/main` into local `main`.

## Notes

- Latest upstream doc commit at merge time: `65613801` `TS snippets for Artifacts (#1638)`.
- Merge commit created locally: `0b433f64`.
- Merge completed without conflicts.

## Change-Log Review

- 2026-04-11:
  - `events/index`
- 2026-04-12:
  - no markdown changes
- 2026-04-13:
  - no markdown changes
- 2026-04-14:
  - new `integrations/adspirer`
  - `2.0/index`
  - `apps/index`
  - `context/compaction`
  - `evaluate/user-sim`
  - `get-started/installation`
  - `get-started/python`
  - `get-started/streaming/quickstart-streaming`
  - `integrations/agentphone`
  - `integrations/bigquery-agent-analytics`
  - `integrations/computer-use`
  - `sessions/session/index`
  - `tutorials/multi-tool-agent`
- 2026-04-15:
  - `artifacts/index`

## Validation

- `git fetch upstream --prune`
- `git fetch origin --prune`
- `git merge --no-edit upstream/main`
