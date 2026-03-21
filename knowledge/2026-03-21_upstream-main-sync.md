# 2026-03-21 Upstream Main Sync

## Summary

- Local branch: `main`
- Upstream branch: `upstream/main`
- Merge base before sync: `94f933b73e724b57d6379a33564db8f37521efd2`
- Upstream commits ahead before merge: 7
- Merge method: `git merge --no-edit upstream/main`

## Upstream commits included

- `4849e6a9` docs: adk2 update
- `227f1e45` fix: fix the input for Get started example
- `33fcfe76` add site owner verification file (b/493636107)
- `cd40b73a` docs: update adk-deploy-guide skill for Terraform-managed GKE resources
- `136deb59` docs: update ADK 2.0 get started code sample
- `8fbeac4a` docs: adk2 add note for updating existing 1.0 projects
- `5331a07f` Added the missing java snippet to tools-custom/index.md

## Docs changed in upstream merge

- `docs/2.0/index.md`
- `docs/index.md`
- `docs/integrations/index.md`
- `docs/tools-custom/index.md`
- `docs/workflows/index.md`
- `docs/workflows/collaboration.md`
- `docs/workflows/data-handling.md`
- `docs/workflows/dynamic.md`
- `docs/workflows/graph-routes.md`
- `docs/workflows/human-input.md`
- `mkdocs.yml`

## Localization impact

- New ko/ja docs required:
  - `docs/ko/2.0/index.md`
  - `docs/ja/2.0/index.md`
  - `docs/ko/workflows/index.md`
  - `docs/ja/workflows/index.md`
  - `docs/ko/workflows/collaboration.md`
  - `docs/ja/workflows/collaboration.md`
  - `docs/ko/workflows/data-handling.md`
  - `docs/ja/workflows/data-handling.md`
  - `docs/ko/workflows/dynamic.md`
  - `docs/ja/workflows/dynamic.md`
  - `docs/ko/workflows/graph-routes.md`
  - `docs/ja/workflows/graph-routes.md`
  - `docs/ko/workflows/human-input.md`
  - `docs/ja/workflows/human-input.md`

- Existing ko/ja docs to review against latest English:
  - `docs/ko/index.md`
  - `docs/ja/index.md`
  - `docs/ko/integrations/index.md`
  - `docs/ja/integrations/index.md`
  - `docs/ko/tools-custom/index.md`
  - `docs/ja/tools-custom/index.md`

## Notes

- Asset and verification-file additions were merged as upstream changes and do not require translation.
- Translation and nav sync will be handled in follow-up batches.
