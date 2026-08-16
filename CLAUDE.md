# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository purpose

This is the documentation site for **Agent Development Kit (ADK)**, published at
[adk.dev](https://adk.dev) and built with MkDocs Material. It documents ADK across five
languages (Python, TypeScript, Go, Java, Kotlin). The actual ADK framework source code
lives in separate repositories (`google/adk-python`, `google/adk-go`, `google/adk-java`,
etc.) — this repo is docs and code snippets only.

**Do not edit `docs/api-reference/`** — it's pre-built HTML regenerated from upstream ADK
source repos and gets overwritten on every regen.

## Commands

Build and serve docs locally (from repo root):

```bash
pip install -r requirements.txt
mkdocs serve          # local dev server at http://127.0.0.1:8000/
mkdocs build --strict # what CI runs on every PR (build-docs.yaml); fails on warnings
```

Snippet validation (each language's `examples/<lang>/snippets/` tree is built/linted
independently; run from repo root):

```bash
./tools/go-snippets/runner.sh build [file...]        # omit file args to build everything
./tools/go-snippets/runner_test.sh                   # unit tests for the runner script
./tools/kotlin-snippets/runner.sh build [file...]
./tools/kotlin-snippets/runner.sh lint [file...]      # enforces Google Kotlin Style via ktlint
```

Python sample apps under `examples/python/` are linted/tested per-directory in CI
(`black .` / `flake8 .` / `pytest`, matrixed across Python 3.9–3.12) but there's no
single top-level command — CI discovers every subdirectory containing a `requirements.txt`.

Link checking uses `lychee` (config in `lychee.toml`); it's what `link-checker.yaml` runs
in CI, not something normally run locally.

## Architecture

### Docs tree and navigation

- `docs/` holds all Markdown content, organized by product area (`agents/`, `tools-custom/`,
  `sessions/`, `deploy/`, `evaluate/`, `integrations/`, `a2a/`, `streaming/`, etc.).
- Navigation, redirects, and the i18n language list are all centrally defined in
  `mkdocs.yml` (~800 lines) — adding a new page usually requires a nav entry there too,
  **except** integration pages (see below, auto-discovered).
- `mkdocs.yml`'s `redirects` plugin config carries a long-lived map of legacy URLs to
  current ones. When moving/renaming a page, add a redirect there pointing directly at the
  final destination — never chain redirects.
- Translations live in `docs/ko/` and `docs/ja/` (via `mkdocs-static-i18n`, `docs_structure:
  folder`). Each locale has its own `nav` block inside the `i18n` plugin config in
  `mkdocs.yml`. `docs/translation-upstream-sync-spec.md` and root-level
  `translation-status-*.md` files track in-progress sync state against a pinned upstream
  commit — these are working notes, not authoritative docs.
- `docs/_includes/`, `docs/ko/_includes/`, `docs/ja/_includes/` hold snippet-include
  partials (via `pymdownx.snippets`) and are excluded from the nav/build via
  `exclude_docs`/`not_in_nav`.

### Integrations catalog (auto-discovery, not manual nav)

`docs/integrations/*.md` pages are **not** listed individually in `mkdocs.yml`. They're
auto-discovered and rendered as a card grid by `render_catalog()`, a Jinja macro defined in
`scripts/integrations.py` and wired in via the `mkdocs-macros-plugin` (custom `{{% %}}`
delimiters to avoid clashing with Markdown). `docs/integrations/index.md` calls
`render_catalog('integrations/*.md')`.

Each integration page needs exactly four frontmatter fields (`catalog_title`,
`catalog_description`, `catalog_icon`, `catalog_tags`) — only use `catalog_tags` values
that already exist elsewhere in the catalog (`grep catalog_tags docs/integrations/*.md`
to check). Cards sort alphabetically by filename, so avoid `adk-`-prefixed slugs. Full
conventions, category templates (MCP tool / observability / plugin), and a review
checklist live in the `.agents/skills/integration-create` and
`.agents/skills/integration-review` skills — use those skills (via CONTRIBUTING.md's
"AI-Assisted Development" section) rather than re-deriving conventions from scratch when
adding or reviewing an integration page.

### Multi-language code snippets

`examples/<lang>/snippets/` (Go, Python, TypeScript, Java, Kotlin) hold the runnable code
samples embedded in docs pages via `pymdownx.snippets`. Each language has its own
validation tool under `tools/<lang>-snippets/`:

- A `files_to_test.txt` registry lists every snippet file that must build; a
  `check_<lang>_snippets.sh` script fails CI if a new snippet file isn't registered.
- For Go, multi-file `package main` snippets must have **all** their files listed on the
  same line in `files_to_test.txt`, or the build fails with undefined-symbol errors.
- `runner.sh build|lint` does the actual build/lint work and is safe to run locally from
  the repo root.

Reference doc generation tools live in `tools/python-api-docs/`, `tools/python-cli-docs/`,
`tools/python-rest-api-docs/`, and `tools/kotlin-api-docs/` (each with a `generate.sh`) —
these regenerate the pre-built `docs/api-reference/` HTML from upstream source and should
not be run casually; see the "API and CLI Reference" section of `CONTRIBUTING.md`.

### Language support tags

Docs pages that describe a feature available in only some SDKs use the
`<div class="language-support-tag">` convention (see `docs/stylesheets/language-tags.css`
for `.lst-python`, `.lst-go`, `.lst-java`, `.lst-typescript`, `.lst-kotlin`) rather than
prose like "available in Python only." Follow existing pages' usage rather than
inventing new phrasing.

### CI workflows worth knowing about (`.github/workflows/`)

- `build-docs.yaml`: `mkdocs build --strict` on every PR — the main gate for doc changes.
- `publish-docs.yaml`: `mkdocs gh-deploy --force` on push to `main`.
- `link-checker.yaml`: runs `lychee` against `docs/**/*.md`.
- `go-snippets-pr-check.yaml` / `kotlin-snippets-pr-check.yaml`: registry check + build
  (+lint for Kotlin) for changed snippet files only; full builds run weekly/on schedule.
- `python-lint.yaml` / `python-tests.yaml`: per-sample-directory `black`/`flake8`/`pytest`
  matrix for `samples/python/**` (a path pattern for a directory that doesn't currently
  exist in this checkout — the actual Python examples live under `examples/python/`).
- `daily-upstream-doc-change-log.yaml`: runs `scripts/collect_upstream_doc_changes.py`
  daily, diffing against upstream `google/adk-docs` and committing reports into
  `upstream-doc-change-log/`. This is automation, not something to run manually.
- `header-checker-lint.yml`: enforces Apache-2.0 license headers on `.py` files
  (config at `.github/header-checker-lint.yml`).

### Contribution conventions

- `CONTRIBUTING.md` is the canonical human-facing contribution guide; read it before
  making structural changes (new pages need an issue first for anything beyond typo
  fixes; major reorganizations need maintainer buy-in first).
- Two Claude/AI-agent skills ship in `.agents/skills/`: `integration-create` and
  `integration-review`. Prefer invoking these for integration-page work over ad hoc
  approaches, since they encode the catalog's structural and style rules.
- Canonical upstream framework source repos (for verifying API correctness in samples,
  or for filing framework bugs vs. docs bugs): `google/adk-python`,
  `google/adk-python-community`, `google/adk-go`, `google/adk-java` — see
  `docs/community/contributing-guide.md` for the full table and links.
