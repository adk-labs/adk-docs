# 2026-03-15 Translation Sync Batch 2

## Scope

- Upstream window: 2026-03-12 through 2026-03-15
- English source docs synced in this batch:
  - `docs/context/caching.md`
  - `docs/context/index.md`
  - `docs/sessions/state.md`

## Localized files updated

- `docs/ko/context/caching.md`
- `docs/ja/context/caching.md`
- `docs/ko/context/index.md`
- `docs/ja/context/index.md`
- `docs/ko/sessions/state.md`
- `docs/ja/sessions/state.md`

## Change summary

- Added Java support markers and Java `ContextCacheConfig` examples to localized `context/caching`
- Synced the latest runner and `InvocationContext` examples plus Java auth/memory/direct-context sections in localized `context/index`
- Added Java instruction templating and `InstructionProvider` examples to localized `sessions/state`

## Quantitative summary

- English source docs synced: 3
- Localized docs updated: 6
- Knowledge files added in this batch: 1
- Total files in this batch: 7

## Verification

- Compared current upstream English sections against localized ko/ja files for the changed areas
- Preserved tabbed examples, code fences, and localized explanatory prose
- Ran `git diff --check` on all files in this batch

## Notes

- `docs/context/index.md` had large upstream Java example additions concentrated in specific sections, so this batch updated the affected sections directly instead of retranslating the entire document.
