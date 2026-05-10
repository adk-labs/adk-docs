# 2026-05-10 Upstream Translation Sync

## Scope

- Fetched and merged `upstream/main` into local `main`.
- Upstream merge commit: `1afe582f`.
- Upstream range reviewed: `31ffb15b..cac85aa9`.
- Latest upstream commits included Atlan MCP integration, Dapr durable execution integration, and Go module dependency bumps in examples/tooling.

## Translation Updates

- Added new Korean and Japanese pages:
  - `docs/ko/integrations/atlan.md`
  - `docs/ja/integrations/atlan.md`
  - `docs/ko/integrations/dapr.md`
  - `docs/ja/integrations/dapr.md`
- Preserved source front matter, integration tags, catalog icons, tabs, and code blocks while localizing prose and tables.
- Localized internal links for the Dapr integration to the corresponding Korean and Japanese documentation paths.
- Confirmed upstream integration assets are present:
  - `docs/integrations/assets/atlan.png`
  - `docs/integrations/assets/dapr.png`

## Validation

- Full English source coverage audit: `ko missing 0`, `ja missing 0`, excluding the local internal `docs/translation-upstream-sync-spec.md`.
- New document structure audit:
  - `integrations/atlan.md`: code fence and tab counts match source for KO/JA.
  - `integrations/dapr.md`: code fence counts match source for KO/JA.
- Catalog/render check confirmed Atlan and Dapr appear on both localized integration catalog pages and use `/integrations/assets/atlan.png` and `/integrations/assets/dapr.png`.
- Asset build check confirmed `site/integrations/assets/atlan.png` and `site/integrations/assets/dapr.png` are generated.
- `git diff --check`: passed.
- `uv run --with-requirements requirements.txt mkdocs build`: passed.

## Notes

- `mkdocs build` still reports existing localized anchor and `mkdocs_llmstxt` warnings outside this sync scope; the build completed successfully.
- Go dependency updates were merged from upstream and did not require translation changes.
