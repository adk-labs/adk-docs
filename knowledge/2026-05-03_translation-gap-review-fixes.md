# 2026-05-03 Translation Gap Review Fixes

## Scope

- Re-ran translation coverage review after the upstream translation sync.
- Confirmed KO/JA localized Markdown file coverage against English source docs:
  - `ko missing 0`
  - `ja missing 0`
- Confirmed `main` contains current `upstream/main` after fetch.

## Fixes

- Fixed Japanese MkDocs collapsible block markers in `docs/ja/runtime/ambient-agents.md`.
  - Restored ASCII quote syntax for `??? "..."` and `???+ "..."`.
- Improved Datadog localized wording in:
  - `docs/ko/integrations/datadog.md`
  - `docs/ja/integrations/datadog.md`
- Removed the remaining long English link-label text in the KO/JA Datadog docs.

## Validation

- File coverage audit including `_includes`: KO/JA missing count is 0.
- Targeted integrity audit for latest new/renamed docs:
  - code fences
  - Markdown links
  - tab blocks
  - snippet includes
  - generated placeholder residue
- English-residue heuristic for latest new/renamed docs: 0 flagged long English-like lines after fixes.
- `git diff --check`
- `uv run --with-requirements requirements.txt mkdocs build`
  - Result: build completed successfully.
  - Note: strict mode remains blocked by pre-existing repository warnings outside this review scope.
