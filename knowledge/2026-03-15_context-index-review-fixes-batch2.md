# 2026-03-15 context/index review fixes batch 2

## Scope

- Follow-up sync for remaining review findings in `docs/ko/context/index.md`
- Follow-up sync for remaining review findings in `docs/ja/context/index.md`

## Localized files updated

- `docs/ko/context/index.md`
- `docs/ja/context/index.md`

## Change summary

- Re-synced `CallbackContext` and `ToolContext` examples with the latest upstream structure
- Replaced stale callback/state/user-input examples in the `Accessing Information` section
- Replaced stale state-passing, preference, artifact save/load, and artifact list examples
- Corrected broken Java snippets and filled missing TypeScript examples in the Japanese doc
- Localized remaining English strings introduced by the example sync

## Verification

- Searched for previously reported stale markers and broken snippet patterns in both localized files
- Ran `git diff --check` on the updated files
