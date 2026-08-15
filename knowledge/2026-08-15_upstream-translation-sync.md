# Upstream Translation Sync Knowledge Document (2026-08-15)

## 1. Context & Scope
- **Upstream Repository**: `https://github.com/google/adk-docs.git` (`upstream/main`)
- **Pinned Upstream Commit**: `c236a946a7a756e1a9d9aadff36ea14d1d0518e1`
- **Target Locales**: Korean (`docs/ko/`), Japanese (`docs/ja/`)

## 2. Upstream Commits & Work Units Synchronized

### Work Unit 1: Plugins (Kotlin Tabs & Snippets) (`c317e4820`)
- **Files Modified**: `docs/ko/plugins/index.md`, `docs/ja/plugins/index.md`
- **Key Changes**:
  - Added `<span class="lst-kotlin">Kotlin v0.7.0</span>` badge.
  - Added Kotlin tabs for `create_plugin` and `register_plugin` using `CountInvocationPlugin.kt`.

### Work Unit 2: Sessions, State, Events, Artifacts (`c85aecd2a`)
- **Files Modified**: `artifacts/index.md`, `events/index.md`, `sessions/memory.md`, `sessions/session/index.md`, `sessions/state.md`
- **Key Changes**:
  - Updated GCP / DB extra install flags (`google-adk[gcp]`, `google-adk[db]`).
  - Added `VertexAiArtifactService` to built-in services list.
  - Clarified event `id` and `timestamp` ownership and memory entry fields (`id`, `author`, `timestamp`, `custom_metadata`).
  - Documented `get_user_state` behavior and `DatabaseSessionService` per-session concurrency locks.

### Work Unit 3: Evaluate & Optimize (`1bd29540d`)
- **Files Modified**: `evaluate/criteria.md`, `evaluate/environment_simulation.md`, `evaluate/index.md`, `evaluate/user-sim.md`, `optimize/index.md`
- **Key Changes**:
  - Updated `adk eval` CLI syntax for `<EVAL_SET_FILE_PATH_OR_ID>...` and agent directory path semantics.
  - Added user simulation parameters (`include_function_calls`, invocation counting).
  - Clarified experimental status for GEPA optimizers and updated `SimplePromptOptimizer` import paths.

### Work Unit 4: Runtime & Apps (`5cd8d56db`)
- **Files Modified**: `apps/index.md`, `runtime/ambient-agents.md`, `runtime/api-server.md`, `runtime/command-line.md`, `runtime/event-loop.md`, `runtime/resume.md`, `runtime/runconfig.md`, `runtime/web-interface/index.md`
- **Key Changes**:
  - Documented blocking I/O behavior in asyncio event loop and `RunConfig.tool_thread_pool_config`.
  - Updated resumable agent state management (`ctx.set_agent_state`) and Python badge version (`v1.16.0`).
  - Added `model_input_context`, `history_config`, and `translation_config` to `RunConfig`.
  - Documented default per-agent SQLite session URI and `--no_use_local_storage` CLI flag in web UI.

### Work Unit 5: Callbacks & Safety (`c236a946a`)
- **Files Modified**: `callbacks/design-patterns-and-best-practices.md`, `callbacks/index.md`, `callbacks/types-of-callbacks.md`, `safety/index.md`
- **Key Changes**:
  - Added `on_model_error_callback` and `on_tool_error_callback` to callback tables.
  - Documented Python async callback support and callback list execution chain rules.
  - Corrected context references (`tool_context.state`) in safety callbacks.

## 3. Verification & Build Results
- Verified structural parity across all 25 modified files.
- Executed `mkdocs build` to confirm clean documentation compilation.
