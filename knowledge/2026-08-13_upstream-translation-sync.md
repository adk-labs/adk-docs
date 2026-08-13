# Upstream Translation Sync Knowledge Document (2026-08-13)

## 1. Context & Scope
- **Upstream Repository**: `https://github.com/google/adk-docs.git` (`upstream/main`)
- **Pinned Upstream Commit**: `a7584a1dc9c123c838d1ae13dbedbaf02b86441c`
- **Target Locales**: Korean (`docs/ko/`), Japanese (`docs/ja/`)

## 2. Work Units & Synchronized Changes

### Work Unit 1: Existing Integrations Fixes & Improvements (`d9e930e82`)
- **Files Modified**: 18 integration pages in `docs/ko/integrations/` and `docs/ja/integrations/`.
- **Key Changes**:
  - `agent-identity.md`: Updated env var to `ADK_USE_V1ALPHA`.
  - `agent-registry.md`: Updated header forwarding and `RemoteA2aAgent` client authentication guidance.
  - `api-registry.md`: Updated import path to `google.adk.integrations.api_registry`.
  - `apigee-api-hub.md`: Updated toolset passing syntax (`tools=[sample_toolset]`).
  - `application-integration.md`: Clarified `tool_name_prefix` scope under `connection=`.
  - `cisco-ai-defense.md`, `cloud-trace.md`, `code-exec-agent-runtime.md`, `computer-use.md`, `freeplay.md`, `future-agi.md`, `mlflow-scorers.md`, `phoenix.md`, `reflect-and-retry.md`, `skills-registry.md`, `temporal.md`, `windsor-ai.md`: Synchronized code snippet imports, async main wrappers, and exception handling notes.
  - `gcs.md`: Updated bucket capability requirements and added unprefixed `tool_filter` reference note.

### Work Unit 2: New Integration Page for Bash Tool (`a7584a1dc`)
- **New Files**:
  - `docs/ko/integrations/bashtool.md`: Added Korean documentation for `ExecuteBashTool` (POSIX sandbox bash execution, security policies, resource limits).
  - `docs/ja/integrations/bashtool.md`: Added Japanese documentation for `ExecuteBashTool`.
  - Shared icon `docs/integrations/assets/bash.png`.

## 3. Verification & Build Results
- **Heading & Structure Parity**: Verified 100% structural parity across EN, KO, and JA pages.
- **Build Status**: Verified via `mkdocs build`.
