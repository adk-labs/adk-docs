# 2026-03-21 Translation Sync Batch 1

## Scope

- Upstream sync basis: `upstream/main` merged on 2026-03-21
- English docs covered in this batch:
  - `docs/2.0/index.md`
  - `docs/index.md`
  - `docs/integrations/index.md`
  - `docs/tools-custom/index.md`
- Navigation covered:
  - `mkdocs.yml`

## Localized files added

- `docs/ko/2.0/index.md`
- `docs/ja/2.0/index.md`

## Localized files updated

- `docs/ko/index.md`
- `docs/ja/index.md`
- `docs/ko/integrations/index.md`
- `docs/ja/integrations/index.md`
- `docs/ko/tools-custom/index.md`
- `docs/ja/tools-custom/index.md`

## Navigation updates

- Added locale nav entry for `ADK 2.0` overview in ko/ja

## Quantitative summary

- New localized docs: 2
- Updated localized docs: 6
- Navigation files updated: 1
- Knowledge files added in this batch: 1
- Total files in this batch: 10

## Verification

- Matched the latest upstream changes for home page warning, integrations intro, and tools-custom Java snippet
- Added localized `ADK 2.0` overview docs with localized internal links
- Ran `git diff --check` on every file in this batch

## Remaining work

The new `workflows` doc set still needs ko/ja translation and locale nav expansion:

- `docs/workflows/index.md`
- `docs/workflows/collaboration.md`
- `docs/workflows/data-handling.md`
- `docs/workflows/dynamic.md`
- `docs/workflows/graph-routes.md`
- `docs/workflows/human-input.md`
