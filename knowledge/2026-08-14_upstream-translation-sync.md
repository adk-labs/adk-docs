# Upstream Translation Sync Knowledge Document (2026-08-14)

## 1. Context & Scope
- **Upstream Repository**: `https://github.com/google/adk-docs.git` (`upstream/main`)
- **Pinned Upstream Commit**: `6b8b086052633f9dafd0d00b540a53a1b360c960`
- **Target Locales**: Korean (`docs/ko/`), Japanese (`docs/ja/`)

## 2. Upstream Commits Synchronized
1. `6b8b08605`: `Add Kotlin snippet for remote MCP with a suspend headerProvider` (#2113)
   - Updated `docs/ko/tools-custom/mcp-tools.md` and `docs/ja/tools-custom/mcp-tools.md`:
     - Added `<span class="lst-kotlin">Kotlin v0.7.0</span>` to the language support tag badge.
     - Added Python, TypeScript, Java, and Kotlin tabs under the Remote MCP Agent Configuration section.
     - Documented `McpToolset.McpToolsetConfig` with suspend `headerProvider` and session reuse considerations in Korean and Japanese.

## 3. Verification & Parity Results
- **Heading & Structure Parity**: Verified 100% structural parity across EN, KO, and JA pages.
- **Code Snippet & Badge Parity**: Verified `Kotlin v0.7.0` badges and multi-language tabs.
