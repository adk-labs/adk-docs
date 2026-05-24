# 2026-05-24 upstream translation sync

## Scope

- Fetched `upstream/main` and merged the latest upstream changes through `7d0a76a8` (`Update e2a integration page with remote MCP server and 7 tools`).
- Upstream range reviewed: `83742996..7d0a76a8`.
- Resolved merge conflicts in `mkdocs.yml` and `docs/workflows/index.md`.
- Kept local KO/JA navigation and redirect behavior while incorporating upstream nav changes.

## Upstream Changes Covered

- Kotlin language support: quickstart, API reference nav, snippets, examples, and support tags.
- ADK 2.0 graph workflow reorganization: workflow graph docs moved under `graphs/`.
- Runtime web interface page moved to `runtime/web-interface/index.md`.
- New integrations: e2a, Future AGI, Redis, and Google Cloud Skill Registry.
- API reference updates: Python REST/API reference for ADK 2.0.0, Java ADK 1.3.0, Kotlin API reference.
- Documentation updates for memory services, RunConfig, CLI reference, routes, visual builder, and link fixes.

## Translation Work

- Added KO/JA translations for:
  - `get-started/kotlin.md`
  - `integrations/e2a.md`
  - `integrations/future-agi.md`
  - `integrations/redis.md`
  - `integrations/skills-registry.md`
  - `workflows/index.md`
  - homepage Graph Workflows include
- Moved localized pages to match upstream structure:
  - `workflows/graph-routes.md` -> `graphs/routes.md`
  - `workflows/data-handling.md` -> `graphs/data-handling.md`
  - `workflows/human-input.md` -> `graphs/human-input.md`
  - `workflows/dynamic.md` -> `graphs/dynamic.md`
  - `agents/multi-agents.md` -> `workflows/patterns.md`
  - `runtime/web-interface.md` -> `runtime/web-interface/index.md`
- Updated KO/JA nav for Kotlin, Graph Workflows, runtime web interface, and API reference links.
- Synced language support tags for upstream-changed localized documents.
- Added Kotlin snippet coverage to KO/JA RunConfig and Memory docs.
- Updated KO/JA Memory docs for the latest three-service model, including RAG Memory.

## Path And Asset Fixes

- Replaced root-relative local image paths introduced by upstream with relative paths for GitHub Pages compatibility.
- Updated override SDK icon paths to use MkDocs `url` filter.
- Updated announcement links to use MkDocs `url` filter.
- Fixed moved-document links for:
  - `multi-agents.md` -> `workflows/patterns.md`
  - `runtime/web-interface.md` -> `runtime/web-interface/index.md`
  - Human-in-the-loop anchors
- Fixed stale localized snippet paths:
  - `vertexai_rag_engine.py` -> `rag_engine.py`
  - `vertexai_search.py` -> `agent_search.py`

## Validation

- Missing KO/JA source document coverage: `ko missing 0`, `ja missing 0` (excluding internal `translation-upstream-sync-spec.md` and generated API reference docs).
- Snippet existence audit: `missing snippets 0`.
- `git diff --check`: passed.
- MkDocs build: completed successfully (`Documentation built in 48.32 seconds`).
- Generated site asset audit: `site asset refs 40485`, `missing 0`.
- Integration catalog audit confirmed e2a, Future AGI, Redis, and Google Cloud Skill Registry appear in EN/KO/JA catalog pages with no root-absolute catalog asset refs.

## Follow-up: Kotlin Translation Gap Remediation

### Scope

- Re-reviewed upstream Kotlin-related documentation changes against KO/JA localized pages.
- Confirmed localized document file coverage remained complete: `ko missing 0`, `ja missing 0`.
- Found KO/JA pages where upstream Kotlin examples or Kotlin support tags had not yet been reflected.

### Changes Applied

- Added missing Kotlin support/example coverage to KO/JA docs for:
  - `agents/custom-agents.md`
  - `agents/llm-agents.md`
  - `artifacts/index.md`
  - `callbacks/index.md`
  - `observability/index.md`
  - `observability/logging.md`
  - `observability/metrics.md`
  - `observability/traces.md`
  - `runtime/event-loop.md`
  - `runtime/resume.md`
  - `sessions/session/index.md`
  - `sessions/state.md`
  - `tools-custom/function-tools.md`
  - `tools/limitations.md`
  - `tutorials/multi-tool-agent.md`
  - `workflows/patterns.md`
- Fixed the upstream English `docs/observability/logging.md` Kotlin snippet include that had been split across two lines.

### Validation

- Kotlin reflection audit: `kotlin reflection issues 0`.
- Snippet existence audit: `missing snippets 0`.
- `git diff --check`: passed.
- MkDocs build: completed successfully (`Documentation built in 49.87 seconds`).
- Generated site asset audit: `site asset refs 40485`, `missing 0`.

## Follow-up: Localized Community Link Fix

- Fixed KO/JA community translation links to use GitHub Pages project paths:
  - `https://adk-labs.github.io/adk-docs/ko/`
  - `https://adk-labs.github.io/adk-docs/ja/`
- Updated both current `community/index.md` pages and legacy localized `community.md` pages.
- Verified no stale `https://adk.dev/ko/`, `https://adk.dev/ja/`, `https://adk-labs.github.io/ko/`, or `https://adk-labs.github.io/ja/` links remain in docs.
- Verified both corrected URLs return HTTP `200`.

## Follow-up: Localized Get Started Parity Fix

- Updated KO/JA `get-started/index.md` cards to match upstream ordering:
  - Python
  - TypeScript
  - Go
  - Java
  - Kotlin
- Added the missing Kotlin quickstart card to both localized pages.
- Verified card order parity across EN/KO/JA and reran `mkdocs build` successfully.
