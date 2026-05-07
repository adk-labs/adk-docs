# 2026-05-08 Upstream Translation Sync

## Scope

- Fetched and merged `upstream/main` into local `main`.
- Upstream merge commit: `cd3c471a`.
- Upstream range reviewed: `f6b1259c..31ffb15b`.
- Latest upstream commits included ZoomInfo MCP integration, Windows shell API key command clarification, function tool default guidance, `LoadArtifactsTool` documentation, callback parameter-name clarification, BigQuery Agent Analytics restructuring, StackOne search-and-execute mode, dependency/link checker updates, and Python API reference regeneration.

## Translation Updates

- Added new Korean and Japanese pages:
  - `docs/ko/integrations/zoominfo.md`
  - `docs/ja/integrations/zoominfo.md`
- Rebuilt Korean and Japanese `integrations/bigquery-agent-analytics.md` against the latest upstream structure, including:
  - captured events summary
  - quickstart-first layout
  - configuration tables
  - schema/view sections
  - query recipes
  - Agent Runtime deployment section
  - operations and SDK/dashboard sections
- Updated Korean and Japanese `integrations/stackone.md` for `search_and_execute` mode and new plugin parameters.
- Updated Korean and Japanese changed sections for:
  - `artifacts/index.md` (`LoadArtifactsTool`)
  - `callbacks/types-of-callbacks.md` (Python callback parameter names)
  - `get-started/{python,typescript,go,java}.md` (Windows shell-specific API key commands)
  - `tools-custom/function-tools.md` and `tools-custom/index.md` (default-value guidance)

## Validation

- Full English source coverage audit: `ko missing 0`, `ja missing 0`.
- Changed upstream document coverage audit: `ko changed-doc missing 0`, `ja changed-doc missing 0`.
- Core updated integration structure audit:
  - `integrations/bigquery-agent-analytics.md`: code fence and tab counts match source for KO/JA.
  - `integrations/stackone.md`: code fence and tab counts match source for KO/JA.
  - `integrations/zoominfo.md`: code fence and tab counts match source for KO/JA.
- Catalog/render check confirmed ZoomInfo appears on both localized integration catalog pages and uses `/integrations/assets/zoominfo.png`.
- `git diff --check`: passed.
- `uv run --with-requirements requirements.txt mkdocs build`: passed.

## Notes

- `mkdocs build` still reports existing localized anchor and `mkdocs_llmstxt` warnings outside this sync scope; the build completed successfully.
- Python API reference generated files were merged from upstream as source artifacts and are not translated separately.
