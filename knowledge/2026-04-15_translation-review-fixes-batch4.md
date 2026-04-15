# 2026-04-15 Translation Review Fixes Batch 4

## Scope

- Applied the follow-up fixes from the missing-translation review.
- Synced the missing TypeScript content in `tutorials/multi-tool-agent` for ko/ja.
- Normalized remaining English table headers and obvious status labels in localized integration docs.

## Main Changes

- `docs/ko/tutorials/multi-tool-agent.md`
- `docs/ja/tutorials/multi-tool-agent.md`
  - added the missing TypeScript sections for:
    - environment setup
    - project creation
    - running the agent
  - restored the missing TypeScript `.env` guidance in the model setup section

- localized table-header and config-label remnants in ko/ja integration docs:
  - `agentphone`
  - `atlassian`
  - `cartesia`
  - `chroma`
  - `daytona`
  - `elevenlabs`
  - `github`
  - `hugging-face`
  - `linear`
  - `mailgun`
  - `mongodb`
  - `n8n`
  - `paypal`
  - `pinecone`
  - `qdrant`
  - `restate`
  - `supermetrics`
  - `windsor-ai`

## Validation

- `git diff --check`
- repo-wide `rg` scan for the reviewed English table-header patterns:
  - `Tool | Description`
  - `Variable | Description | Default`
  - `Variable | Description | Required`
  - `Capability | Description`
  - `Required (stdio mode)`
