# Upstream Translation Sync Knowledge Document (2026-08-11)

## 1. Context & Scope
- **Upstream Repository**: `https://github.com/google/adk-docs.git` (`upstream/main`)
- **Pinned Upstream Commit**: `60b802ed321f892957d0e59f70d0781ee27be0ac`
- **Target Locales**: Korean (`docs/ko/`), Japanese (`docs/ja/`)

## 2. Upstream Commits Synchronized
1. `60b802ed3`: `ADK_SUPPRESS_A2A_EXPERIMENTAL_FEATURE_WARNINGS` (#1533)
   - Updated `docs/ko/a2a/quickstart-exposing.md` and `docs/ja/a2a/quickstart-exposing.md` with tip callouts documenting experimental feature warning suppression in logs.
2. `d94dc2cd1`: `Add Kotlin snippet for context caching configuration` (#2091)
   - Updated `docs/ko/context/caching.md` and `docs/ja/context/caching.md`: added Kotlin v0.7.0 language support badge and `=== "Kotlin"` code block tab for `ContextCacheConfig`.
3. `34d4ec292`: `Add Kotlin snippet for the Knowledge Engine retrieval tool` (#2090)
   - Updated `docs/ko/integrations/knowledge-engine.md` and `docs/ja/integrations/knowledge-engine.md`: added Kotlin v0.7.0 language support badge and `=== "Kotlin"` code snippet tab for `RagEngine.kt`.
4. `12c70c710`: `Add Kotlin snippets for Memory Bank and RAG memory` (#2089)
   - Updated `docs/ko/sessions/memory.md` and `docs/ja/sessions/memory.md`: added `=== "Kotlin"` code snippet tabs under `Memory Bank` and `RAG Memory` sections for `MemoryExample.kt`.

## 3. Verification & Parity Results
- **Heading & Structure Parity**: All translated documents in `docs/ko/` and `docs/ja/` match English original structures.
- **Code Transclusion (`--8<--`) & Snippet Parity**: Verified snippet transclusion references (`MemoryExample.kt:memory_bank`, `MemoryExample.kt:rag_memory`, `RagEngine.kt:full_code`).
