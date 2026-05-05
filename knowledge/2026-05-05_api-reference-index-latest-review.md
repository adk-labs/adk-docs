# 2026-05-05 API reference index latest review

## Scope

- Reviewed upstream-changed human-facing Markdown documents after the latest upstream merge.
- Included `docs/api-reference/index.md`, which was previously outside the normal translation coverage audit because most API reference output is generated.

## Finding

- `docs/api-reference/index.md` changed upstream to use absolute `https://adk.dev/api-reference/...` links.
- Korean and Japanese localized API reference index pages still used rendered relative links for Python, TypeScript, Java, CLI, Agent Config, and REST API references.

## Fix

- Updated rendered API reference links in:
  - `docs/ko/api-reference/index.md`
  - `docs/ja/api-reference/index.md`

## Validation

- Upstream-changed human-facing Markdown coverage: `ko missing 0`, `ja missing 0`.
- Rendered stale relative API reference links after excluding HTML comments: `ko 0`, `ja 0`.
- Strict structural audit for new and fully translated changed documents: `0` problems.
- `git diff --check`: passed.
