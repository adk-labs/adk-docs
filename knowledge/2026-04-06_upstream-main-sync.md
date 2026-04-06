# 2026-04-06 Upstream Main Sync

## Summary

- Local branch: `main`
- Upstream branch: `upstream/main`
- Merge base before sync: `66c1bb12e07023504f456509e8b6245f22fbdacf`
- Upstream head merged: `75671758163fc8e140598109ba7d85e6f1961878`
- Upstream commits ahead before merge: `4`
- Merge commit: `14285edb0e1141fb8551270839737e87f17a193e`
- Merge method: `git merge --no-edit upstream/main`

## Change-log basis reviewed

- `upstream-doc-change-log/2026-04-04.md`
- `upstream-doc-change-log/2026-04-05.md`
- `upstream-doc-change-log/2026-04-06.md`

## Major upstream themes

- Quickstart tutorial move from `docs/get-started/quickstart.md` to `docs/tutorials/multi-tool-agent.md`
- Redirect and nav retargeting from quickstart paths to `get-started` and `tutorials`
- Java example expansion on `docs/agents/models/google-gemma.md`
- New `Live Demos` section on `docs/streaming/index.md`
- Small runtime/CTA link retargets in `agents/config`, `plugins/index`, `get-started/about`, `get-started/installation`, and `tutorials/agent-team`
- Agent Engine ASP guide wording refresh from quickstart-specific setup to generic `my_agent`

## Docs changed in upstream merge

- Changed English markdown docs in range: `10`
- Renamed English markdown docs in range: `1`
- Localized follow-up needed for:
  - `docs/agents/config.md`
  - `docs/agents/models/google-gemma.md`
  - `docs/deploy/agent-engine/asp.md`
  - `docs/get-started/about.md`
  - `docs/get-started/installation.md`
  - `docs/plugins/index.md`
  - `docs/streaming/index.md`
  - `docs/tutorials/agent-team.md`
  - `docs/tutorials/index.md`
  - `docs/tutorials/multi-tool-agent.md`
  - `mkdocs.yml`

## Localization impact

- New ko/ja tutorial pages required:
  - `docs/ko/tutorials/multi-tool-agent.md`
  - `docs/ja/tutorials/multi-tool-agent.md`
- Old localized quickstart pages should be retired and served through redirects:
  - `docs/ko/get-started/quickstart.md`
  - `docs/ja/get-started/quickstart.md`
- Locale nav and redirect mappings required in `mkdocs.yml`
- Existing ko/ja docs required content sync for new Java tabs, Live Demos cards, and runtime/CTA link changes

## Notes

- `2026-04-05.md` and `2026-04-06.md` contained no additional markdown changes beyond the `2026-04-04.md` range.
- Translation sync and subagent review results are recorded in the follow-up translation batch note.
