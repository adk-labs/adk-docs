# 2026-04-06 Translation Sync Batch 1

## Scope

- Upstream sync basis: `upstream/main` merged on 2026-04-06
- Focus areas in this batch:
  - localized nav and redirect sync for the quickstart-to-tutorial move
  - ko/ja translation of the renamed multi-tool tutorial page
  - Java parity sync for `google-gemma`
  - Live Demos sync for `streaming/index`
  - runtime/CTA retargets and ASP wording refresh
  - subagent review and remediation

## Localized files added

- `docs/ko/tutorials/multi-tool-agent.md`
- `docs/ja/tutorials/multi-tool-agent.md`

## Localized files deleted

- `docs/ko/get-started/quickstart.md`
- `docs/ja/get-started/quickstart.md`

## Localized files updated

- `mkdocs.yml`
- `docs/ko/agents/config.md`
- `docs/ja/agents/config.md`
- `docs/ko/agents/models/google-gemma.md`
- `docs/ja/agents/models/google-gemma.md`
- `docs/ko/deploy/agent-engine/asp.md`
- `docs/ja/deploy/agent-engine/asp.md`
- `docs/ko/get-started/about.md`
- `docs/ja/get-started/about.md`
- `docs/ko/get-started/installation.md`
- `docs/ja/get-started/installation.md`
- `docs/ko/plugins/index.md`
- `docs/ja/plugins/index.md`
- `docs/ko/streaming/index.md`
- `docs/ja/streaming/index.md`
- `docs/ko/tutorials/index.md`
- `docs/ja/tutorials/index.md`
- `docs/ko/tutorials/agent-team.md`
- `docs/ja/tutorials/agent-team.md`

## Change summary

- Added ko/ja `tutorials/multi-tool-agent.md` pages and retired the old localized `get-started/quickstart.md` pages to match the upstream rename
- Added locale redirect mappings and updated localized nav entries in `mkdocs.yml`
- Retargeted tutorial landing pages, agent-team intro links, and multi-tool tutorial next-step links to the new localized tutorial/runtime destinations
- Synced `get-started/about` and `get-started/installation` CTAs to `/get-started/`
- Synced `agents/config` and `plugins/index` runtime links to `Agent Runtime`
- Refreshed localized ASP docs to the upstream `Get started` / `my_agent` wording
- Reworked localized `google-gemma` sections to include Java tabs, LangChain4j vLLM setup, and the updated food-tour prerequisite note
- Added localized `Live Demos` cards, screenshots, and links to `streaming/index`
- Brought localized plugin support tags up to the current upstream language set

## Review and verification

- Spawned worker subagents for the translation pass and integrated their changes
- Ran a review subagent on the changed scope; its initial findings covered the quickstart rename, ASP wording, Gemma Java parity, streaming Live Demos, and stale CTA/runtime links
- Applied follow-up fixes for all review findings in scope and re-checked the working tree locally
- Verified new localized tutorial files exist and old localized quickstart files are retired
- Verified localized links now target `tutorials/multi-tool-agent`, `tutorials/agent-team`, `/get-started/`, and `/runtime/` where upstream changed them
- Ran `git diff --check`
