# 2026-05-05 upstream translation gap review

## Scope

- Synced `upstream/main` into local `main` with merge commit `521312d4`.
- Reviewed English source Markdown coverage after the upstream update.
- Translation coverage audit excludes generated or build-excluded API reference files under `docs/api-reference/`, consistent with the existing localization workflow.

## Missing translation findings

Initial coverage review found three new upstream English source documents missing in both Korean and Japanese:

- `integrations/markifact.md`
- `observability/metrics.md`
- `runtime/cancel.md`

These files were added for both languages:

- `docs/ko/integrations/markifact.md`
- `docs/ja/integrations/markifact.md`
- `docs/ko/observability/metrics.md`
- `docs/ja/observability/metrics.md`
- `docs/ko/runtime/cancel.md`
- `docs/ja/runtime/cancel.md`

## Additional upstream translation updates

- Added Korean and Japanese translations for new routing docs:
  - `agents/routing.md`
  - `agents/models/routing.md`
- Updated Korean and Japanese nav entries in `mkdocs.yml` for agent routing, model routing, cancel runs, and metrics.
- Updated existing localized pages for upstream changes:
  - `agents/index.md`
  - `agents/models/index.md`
  - `deploy/cloud-run.md`
  - `observability/index.md`
  - `runtime/ambient-agents.md`
  - `runtime/index.md`
- Added explicit localized anchor compatibility for links to the LLM-driven delegation section in `agents/multi-agents.md`.

## Validation

- Full English source coverage audit: `ko missing 0`, `ja missing 0`.
- Changed upstream document coverage audit: `ko changed-doc missing 0`, `ja changed-doc missing 0`.
- New translated document structure audit: `new-doc structural problems 0`.
- `git diff --check`: passed.
- `uv run --with-requirements requirements.txt mkdocs build`: passed.

## Notes

- `docs/api-reference/java/legal/*.md` remains untranslated because this path is excluded from the build by `mkdocs.yml`.
- Existing localized documentation still contains unrelated historical anchor and `mkdocs_llmstxt` warnings; they are outside this translation coverage pass and do not block the normal build.
