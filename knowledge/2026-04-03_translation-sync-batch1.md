# 2026-04-03 Translation Sync Batch 1

## Scope

- Upstream sync basis: `upstream/main` merged on 2026-04-03
- Focus areas in this batch:
  - locale nav sync in `mkdocs.yml`
  - `adk.dev` link/path migration across localized docs
  - new localized core pages
  - stale localized core docs called out by subagent review

## Localized files added

- `docs/ko/a2a/quickstart-consuming-java.md`
- `docs/ja/a2a/quickstart-consuming-java.md`
- `docs/ko/a2a/quickstart-exposing-java.md`
- `docs/ja/a2a/quickstart-exposing-java.md`
- `docs/ko/agents/models/google-gemma.md`
- `docs/ja/agents/models/google-gemma.md`
- `docs/ko/community/index.md`
- `docs/ja/community/index.md`
- `docs/ko/community/contributing-guide.md`
- `docs/ja/community/contributing-guide.md`
- `docs/ko/evaluate/custom_metrics.md`
- `docs/ja/evaluate/custom_metrics.md`
- `docs/ko/optimize/index.md`
- `docs/ja/optimize/index.md`

## Localized files updated

- `mkdocs.yml`
- localized docs under `docs/ko/**` and `docs/ja/**` affected by the `adk.dev` path migration
- targeted content sync for:
  - `docs/*/index.md`
  - `docs/*/get-started/go.md`
  - `docs/*/get-started/quickstart.md`
  - `docs/*/agents/models/google-gemini.md`
  - `docs/*/agents/models/vllm.md`
  - `docs/*/streaming/streaming-tools.md`
  - `docs/*/sessions/memory.md`
  - `docs/*/observability/logging.md`

## Change summary

- Synced locale nav to match upstream community move, REST API HTML target, Gemma page, custom metrics, optimization, and A2A Java quickstarts
- Applied the `adk.dev` internal-link migration across localized docs to follow the custom-domain rollout
- Added ko/ja translations for the new A2A Java quickstarts, Gemma page, community pages, custom metrics page, and optimization page
- Updated localized home page release messaging for ADK Go `1.0.0` and ADK Java `1.0.0`
- Pulled in missing Go/Java coverage for quickstart, streaming tools, memory, and observability/logging based on the subagent review findings

## Review and verification

- Ran an explorer review over the upstream range and used its findings to close the identified locale gaps
- Verified required new core docs exist in both `ko` and `ja`
- Verified locale nav now includes the new upstream entries and moved targets
- Ran `git diff --check`

