# 2026-06-02 upstream translation sync

## Scope

- Upstream latest checked: `upstream/main` at `e7bc6f1b`.
- Local base after upstream merge: `73453101`.
- Current upstream markdown changes reviewed from `7d0a76a8b8c47d1b3024cd3f5061098f9005f663..upstream/main`.
- KO/JA translation scope covered the changed source docs:
  - `docs/callbacks/types-of-callbacks.md`
  - `docs/deploy/agent-runtime/agents-cli.md`
  - `docs/deploy/agent-runtime/deploy.md`
  - `docs/deploy/agent-runtime/index.md`
  - `docs/deploy/agent-runtime/test.md`
  - `docs/get-started/installation.md`
  - `docs/get-started/kotlin.md`
  - `docs/tutorials/multi-tool-agent.md`

## Translation Work

- Added the `after_agent_callback` output modification limitation note in Korean and Japanese.
- Updated the After Agent callback example wording from replacement semantics to append semantics.
- Updated Kotlin dependency examples to ADK Kotlin `0.2.0`.
- Added ``standardInput = System.`in` `` to the localized Kotlin `run` task examples.
- Removed the obsolete `InMemoryRunner` web-server setup from localized Kotlin quickstart code.
- Added the missing Kotlin tab to localized advanced setup pages and aligned Java ADK dependency examples to `1.3.0`.
- Updated multi-tool-agent Java/Kotlin setup text to point to localized Java and Kotlin quickstarts.
- Added Agent Runtime Go `v1.2.0` support tags in localized Agent Runtime pages.
- Added localized Go deployment payload, project layout, `adkgo deploy agentengine` command, Go CLI option summary, and Go deployment output examples.
- Updated localized Agent Runtime test instructions to use the current **Copy query URL** flow.

## Validation

- `git diff --check`: passed.
- Changed source markdown counterpart audit: KO/JA file gaps `0`.
- Full source markdown counterpart audit: KO/JA file gaps `0`.
- Language support tag class audit: gaps `0`.
- Snippet include path audit: missing paths `0`.
- Changed-doc exact term audit for newly introduced technical strings: no actionable translation gaps.
- `uv run --with-requirements requirements.txt mkdocs build`: passed.
- Built page existence check for changed KO/JA pages: passed.
- Local asset reference audit on built `site`: checked `40890`, missing `0`.

## Notes

- MkDocs still reports existing repository-wide warnings for nav-excluded integration pages, localized anchor mismatches, and `mkdocs_llmstxt` skipped page URIs. These were present outside this translation scope and did not fail the build.
