# 2026-03-15 context/index review fixes

## Scope

- Review-driven follow-up fixes after the 2026-03-15 upstream translation sync
- Localized files updated:
  - `docs/ko/context/index.md`
  - `docs/ja/context/index.md`

## Findings addressed

- Restored the missing TypeScript tab in the top "How the framework provides context" section
- Replaced stale or unrelated `ReadonlyContext` TypeScript snippets with the current upstream instruction-provider example
- Corrected the `ReadonlyContext` Java example so it shows read-only access and an `UnsupportedOperationException` comment instead of mutating state

## Verification

- Re-checked the previously reported review findings against the localized files
- Ran `git diff --check` on both updated docs and this knowledge note

## Notes

- This work unit only fixed the review findings and did not introduce new translation scope beyond `docs/context/index.md`.
