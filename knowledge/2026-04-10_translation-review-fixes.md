# 2026-04-10 Translation Review Fixes

## Trigger

- Applied follow-up fixes from subagent review of the translated upstream scope.

## Fixed Findings

- `tools-custom/mcp-tools`
  - synced the Grounding Lite section to the current upstream structure
  - replaced stale `server-google-maps` / `maps_assistant_agent` examples
  - added missing TypeScript Grounding Lite sample
  - normalized remaining stale `gemini-*` examples in the changed scope
- `integrations/mcp-toolbox-for-databases`
  - added the missing TypeScript install/load section in ko/ja
- `integrations/gke-code-executor`
  - updated changed code examples from `gemini-2.5-flash` to `gemini-flash-latest`
- `optimize/index`
  - updated `optimizer_model` default to `gemini-flash-latest`
- `docs/ja/tools-custom/mcp-tools.md`
  - continued cleanup of cross-locale Korean text left in the Japanese document

## Validation

- `git diff --check`
- stale marker search:
  - `gemini-1.5-flash`
  - `server-google-maps`
  - `gemini-2.5-flash`
- mixed-language scan for the reviewed Japanese MCP page
