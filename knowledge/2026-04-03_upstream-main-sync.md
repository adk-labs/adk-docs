# 2026-04-03 Upstream Main Sync

## Summary

- Local branch: `main`
- Upstream branch: `upstream/main`
- Merge base before sync: `5331a07f1bf93843fc7d2130726849b891c14399`
- Upstream head merged: `66c1bb12e07023504f456509e8b6245f22fbdacf`
- Upstream commits ahead before merge: `56`
- Merge commit: `55c601d446a46a053b399157b929e24b0bf98c97`
- Merge method: `git merge --no-edit upstream/main`

## Major upstream themes

- `adk.dev` custom-domain migration and site URL/path updates
- ADK Go `1.0.0` launch messaging and additional Go snippets across docs
- ADK Java `1.0.0` documentation updates and new A2A Java quickstarts
- New Gemma documentation and Gemma 4 examples
- New evaluation and optimization docs
- New integration pages for `A2UI`, `Couchbase`, `Google Developer Knowledge`, `LangWatch`, and `Temporal`
- Community section move from top-level pages to `docs/community/*`
- REST API reference move from Markdown wrapper to generated HTML/OpenAPI output

## Docs changed in upstream merge

- Changed English markdown docs in range: `135`
- Representative areas affected:
  - `docs/index.md`
  - `docs/get-started/*.md`
  - `docs/agents/models/*.md`
  - `docs/a2a/*.md`
  - `docs/evaluate/custom_metrics.md`
  - `docs/optimize/index.md`
  - `docs/integrations/*.md`
  - `docs/observability/logging.md`
  - `docs/sessions/memory.md`
  - `docs/streaming/streaming-tools.md`
  - `docs/community/index.md`
  - `docs/community/contributing-guide.md`
  - `mkdocs.yml`

## Localization impact

- New ko/ja docs required for new upstream pages:
  - `docs/*/a2a/quickstart-consuming-java.md`
  - `docs/*/a2a/quickstart-exposing-java.md`
  - `docs/*/agents/models/google-gemma.md`
  - `docs/*/community/index.md`
  - `docs/*/community/contributing-guide.md`
  - `docs/*/evaluate/custom_metrics.md`
  - `docs/*/integrations/a2ui.md`
  - `docs/*/integrations/couchbase.md`
  - `docs/*/integrations/google-developer-knowledge.md`
  - `docs/*/integrations/langwatch.md`
  - `docs/*/integrations/temporal.md`
  - `docs/*/optimize/index.md`
- Existing ko/ja docs require follow-up sync for:
  - nav structure in `mkdocs.yml`
  - `adk.dev` link/path migration
  - Go/Java snippet parity in changed docs
  - community path move and REST API reference target change

## Notes

- The merge also updated generated API reference artifacts and static assets; those do not require locale-specific authoring beyond nav/reference handling.
- Translation sync and review will be recorded in follow-up batch notes.
