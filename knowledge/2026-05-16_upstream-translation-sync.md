# 2026-05-16 Upstream Translation Sync

## Scope

- Fetched `upstream/main` and confirmed no additional upstream commits remained after merge.
- Merged upstream into local `main`.
- Local upstream merge commit: `6790e216`.
- Upstream range reviewed: `cac85aa9..83742996`.
- Upstream commits included:
  - New DBOS durable execution integration.
  - New Grafana Cloud MCP integration.
  - New Agent Identity Auth Manager integration and catalog link.
  - Atlan integration copy and tool-list updates.
  - BigQuery Agent Analytics `AGENT_RESPONSE` event/view updates.
  - RunConfig documentation rewrite for ADK 1.33.0.
  - Observability `--otel_to_cloud` flag correction.
  - Authentication page Agent Identity integration link.
  - CLI and REST API reference updates.

## Translation Updates

- Added new Korean and Japanese integration pages:
  - `docs/ko/integrations/agent-identity.md`
  - `docs/ja/integrations/agent-identity.md`
  - `docs/ko/integrations/dbos.md`
  - `docs/ja/integrations/dbos.md`
  - `docs/ko/integrations/grafana-cloud.md`
  - `docs/ja/integrations/grafana-cloud.md`
- Updated Korean and Japanese translations for:
  - `docs/*/integrations/atlan.md`
  - `docs/*/integrations/bigquery-agent-analytics.md`
  - `docs/*/runtime/runconfig.md`
  - `docs/*/observability/logging.md`
  - `docs/*/observability/metrics.md`
  - `docs/*/observability/traces.md`
  - `docs/*/tools-custom/authentication.md`
- Preserved source front matter, integration metadata, tab structure, code blocks, and internal links while localizing prose.

## Asset and Catalog Fixes

- Updated `scripts/integrations.py` so integration catalog card links and icon URLs are emitted as page-relative paths instead of root-absolute paths.
- Converted remaining local image references from root-absolute paths to relative paths across English, Korean, and Japanese markdown docs.
- Confirmed generated catalog pages for English, Korean, and Japanese show Agent Identity, DBOS, Grafana Cloud, and Atlan with resolvable relative icon paths.

## Validation

- Authored markdown coverage audit: `ko missing 0`, `ja missing 0`, excluding the internal translation sync spec and generated Java API legal/license markdown.
- Changed-document structure audit passed for new integrations, Atlan, BigQuery Agent Analytics, RunConfig, metrics, traces, and authentication.
- Localized logging pages received the upstream `--otel_to_cloud` flag correction; their existing localized structure remains intentionally different from the English source.
- Root-absolute local image reference audit: `0`.
- Generated site asset audit: `site asset refs 16926`, `missing 0`.
- Integration catalog render audit: no root-absolute asset refs on English, Korean, or Japanese catalog pages.
- `git diff --check`: passed.
- `uv run --with-requirements requirements.txt mkdocs build`: passed.

## Notes

- `mkdocs build` still reports existing non-blocking localized anchor and `mkdocs_llmstxt` warnings outside this sync scope; the site build completed successfully.
- Generated API reference updates were merged from upstream and do not require localized prose edits in this repository's current translation structure.
