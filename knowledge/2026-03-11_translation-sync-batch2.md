# 2026-03-11 Translation Sync Batch 2

## Scope

- Upstream window: 2026-03-06 through 2026-03-11
- English source docs synced in this batch:
  - `docs/context/index.md`
  - `docs/plugins/index.md`
  - `docs/sessions/memory.md`
  - `docs/tutorials/coding-with-ai.md`

## Localized files updated

- `docs/ko/context/index.md`
- `docs/ja/context/index.md`
- `docs/ko/plugins/index.md`
- `docs/ja/plugins/index.md`
- `docs/ko/sessions/memory.md`
- `docs/ja/sessions/memory.md`
- `docs/ko/tutorials/coding-with-ai.md`
- `docs/ja/tutorials/coding-with-ai.md`

## Change summary

- Added TypeScript `Context`-based examples in `context` locale docs where upstream unified `CallbackContext` and `ToolContext`
- Added Java examples in `memory` locale docs
- Synced `coding-with-ai` locale docs to the new ADK Skills and MCP-server focused structure
- Synced `plugins` locale docs with newly added TypeScript and Java examples plus Java callback signatures

## Quantitative summary

- English source docs synced: 4
- Localized docs updated: 8
- Knowledge files added in this batch: 1
- Total files in this batch: 9

## Verification

- Compared the relevant English upstream diffs against localized docs
- Ensured no whitespace or marker errors with `git diff --check`
- Reviewed the resulting batch diff stat for all 8 localized docs

## Notes

- Initial parallel worker attempts were interrupted to avoid overlapping edits.
- Partial workspace edits produced before interruption were retained and completed locally.
