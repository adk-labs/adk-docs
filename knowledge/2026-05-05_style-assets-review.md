# 2026-05-05 style and asset review

## Scope

- Reviewed generated `site/` output for missing local CSS, JavaScript, image, font, and media assets.
- Browser-tested representative English, Korean, and Japanese pages using Playwright against a local static server.
- Focused on localized homepage style parity, integration catalog images, community resource cards, and localized tool pages with raw HTML image tags.

## Findings and fixes

- Fixed localized integration catalog icons for `data-agent.md` and `express-mode.md` to match upstream `agent-platform.svg` instead of missing `vertex-ai.png`.
- Fixed raw HTML image paths in localized Tavily and MCP tool pages so generated pages resolve images from the correct `assets/` directory.
- Fixed English community page image paths so generated `/community/` pages load card thumbnails from root assets.
- Added the missing Sphinx `api-reference/python/_static/css/custom.css` placeholder referenced by generated Python API reference pages.
- Converted `exclude_docs` to MkDocs gitignore-style multiline syntax and excluded `_includes/**`, `ko/_includes/**`, and `ja/_includes/**` so include fragments are not emitted as standalone pages.

## Validation

- `uv run --with-requirements requirements.txt mkdocs build`: passed.
- Generated site local asset scan: `site missing assets 0`.
- `_includes` standalone pages: no generated files after `exclude_docs` fix.
- Playwright smoke checks:
  - `/`, `/ko/`, `/ja/`: landing page detected, `homepage.css` and `custom.css` loaded, no broken images.
  - `/community/`, `/ko/integrations/`, `/ja/integrations/`, `/ko/tools-custom/mcp-tools/`: no broken images in rendered pages.

## Notes

- Browser console still reports missing localized sitemap XML files (`/ko/sitemap.xml`, `/ja/sitemap.xml`) from the root page. These are not CSS/image/script assets and were left outside this style/asset pass.
- Existing `mkdocs_llmstxt` warnings remain unrelated to asset availability and do not block the normal build.
