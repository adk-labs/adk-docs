# 2026-03-18 Translation Sync Batch 2

## Scope

- Upstream window: 2026-03-17 through 2026-03-18
- English source docs synced in this batch:
  - `docs/a2a/index.md`
  - `docs/a2a/quickstart-consuming.md`
  - `docs/a2a/quickstart-exposing.md`
  - `docs/a2a/a2a-extension.md`

## Localized files updated

- `docs/ko/a2a/index.md`
- `docs/ja/a2a/index.md`
- `docs/ko/a2a/quickstart-consuming.md`
- `docs/ja/a2a/quickstart-consuming.md`
- `docs/ko/a2a/quickstart-exposing.md`
- `docs/ja/a2a/quickstart-exposing.md`
- `docs/ko/a2a/a2a-extension.md`
- `docs/ja/a2a/a2a-extension.md`
- `mkdocs.yml`

## Change summary

- Added the new localized `a2a-extension` page for ko/ja and exposed it in localized navigation
- Synced the new `use_legacy=False` guidance and advanced client configuration content in localized A2A consuming docs
- Synced the new `to_a2a()` internals, executor configuration guidance, and Agent Executor V2 section in localized A2A exposing docs
- Added the new A2A extension links in localized A2A index pages

## Verification

- Compared the A2A English diffs against localized pages and matched new headings, notes, and code block placement
- Preserved relative links and localized nav labels in `mkdocs.yml`
- Ran `git diff --check` on the batch 2 localized docs, `mkdocs.yml`, and this knowledge file
- Ran an independent explorer review across the 2026-03-17 to 2026-03-18 localized doc changes; it reported no concrete findings
