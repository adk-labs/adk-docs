# Upstream Translation Sync Knowledge Document (2026-08-10)

## 1. Context & Scope
- **Upstream Repository**: `https://github.com/google/adk-docs.git` (`upstream/main`)
- **Pinned Upstream Commit**: `ab749867b0445b51da40dad69f079180c9c87df6`
- **Merge Commit**: `23391f26450b090907777424974dacbccef886fc`
- **Target Locales**: Korean (`docs/ko/`), Japanese (`docs/ja/`)

## 2. Upstream Changes Audit & Synchronization Status
Upstream commits analyzed:
1. `ab749867b`: `docs(eventarc): Address technical verification report feedback (#2074)`
   - Synced in Korean (`docs/ko/integrations/eventarc.md`) and Japanese (`docs/ja/integrations/eventarc.md`).
2. `b1b2eaa10`: `Upgrade Kotlin examples to adk-kotlin 0.7.0 (#2088)`
   - Verified transclusion path formatting in `docs/ko/observability/logging.md` and `docs/ja/observability/logging.md`.
   - Updated stale adk-python plugin sample link paths from `contributing/samples/plugin_basic` to `contributing/samples/plugins/plugin_basic` and `contributing/samples/plugins/plugin_reflect_tool_retry/...` in `docs/ko/plugins/index.md`, `docs/ja/plugins/index.md`, `docs/ko/plugins/reflect-and-retry.md`, and `docs/ja/plugins/reflect-and-retry.md`.
3. `839e898fc`: `docs(tutorials): fix ToolContext, output_key and persistence claims (#2032)`
   - Synced in Korean (`docs/ko/tutorials/agent-team.md`) and Japanese (`docs/ja/tutorials/agent-team.md`).
4. `88dbd90ca`: `docs: add telemetry disclosure notices to Web UI and CLI docs (#2092)`
   - Synced in Korean (`docs/ko/runtime/command-line.md`, `docs/ko/runtime/web-interface/index.md`) and Japanese (`docs/ja/runtime/command-line.md`, `docs/ja/runtime/web-interface/index.md`).
5. `ab2d035e0`: `docs(observability): correct metric names, span attributes, logger names (#2013)`
   - Synced in Korean (`docs/ko/observability/logging.md`, `docs/ko/observability/metrics.md`, `docs/ko/observability/traces.md`) and Japanese (`docs/ja/observability/logging.md`, `docs/ja/observability/metrics.md`, `docs/ja/observability/traces.md`).
6. `80bdb8d0a`: `docs(a2a): fix unresolvable imports, wrong kwargs and sample paths (#2014)`
   - Synced in Korean (`docs/ko/a2a/index.md`) and Japanese (`docs/ja/a2a/index.md`).

## 3. Verification & Parity Results
- **Heading & Structure Parity**: All translated documents match English original structures.
- **Code Transclusion (`--8<--`) Parity**: Snippet include paths verified and functional.
- **Build Status**: Verified with `mkdocs build --strict`.
