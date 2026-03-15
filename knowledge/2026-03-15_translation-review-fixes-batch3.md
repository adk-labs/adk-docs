# 2026-03-15 translation review fixes batch 3

## Scope

- Follow-up fixes for remaining upstream translation gaps found during the 2026-03-15 re-review
- Files covered:
  - `docs/ko/context/index.md`
  - `docs/ja/context/index.md`
  - `docs/ko/apps/index.md`
  - `docs/ja/apps/index.md`

## Change summary

- Updated the localized `ReadonlyContext` Python examples to match the latest upstream property-based state access and read-only explanation
- Localized remaining English strings in the affected Java and TypeScript auth, memory, and readonly-context examples
- Replaced outdated Python `Pseudocode` labels with `Example` labels in the changed `context/index` sections
- Localized the remaining English Python comment added in `apps/index`

## Verification

- Ran `git diff --check` on the updated docs and this knowledge file
- Searched for the previously reported leftover English markers in the updated `context/index` and `apps/index` files
