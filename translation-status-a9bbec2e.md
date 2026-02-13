# a9bbec2e 동기화 현황 (영문 docs 변경 기준)

- 기준 커밋: a9bbec2e
- 대상: docs/ 영문 원문 변경 파일
- 상태 정의: started(ko/ja 패치 착수), pending(착수 전)

## 1) 수정된 문서 (M)

| 문서 | ko | ja | 상태 |
|---|---|---|---|
| docs/a2a/quickstart-exposing.md | started | started | started |
| docs/agents/config.md | started | started | started |
| docs/agents/custom-agents.md | started | started | started |
| docs/agents/index.md | started | started | started |
| docs/agents/llm-agents.md | started | started | started |
| docs/agents/multi-agents.md | started | started | started |
| docs/agents/workflow-agents/index.md | started | started | started |
| docs/agents/workflow-agents/loop-agents.md | started | started | started |
| docs/agents/workflow-agents/parallel-agents.md | started | started | started |
| docs/agents/workflow-agents/sequential-agents.md | started | started | started |
| docs/api-reference/index.md | started | started | started |
| docs/apps/index.md | started | started | started |
| docs/artifacts/index.md | started | started | started |
| docs/callbacks/index.md | started | started | started |
| docs/callbacks/types-of-callbacks.md | started | started | started |
| docs/community.md | started | started | started |
| docs/context/compaction.md | started | started | started |
| docs/context/index.md | started | started | started |
| docs/contributing-guide.md | started | started | started |
| docs/deploy/cloud-run.md | started | started | started |
| docs/deploy/gke.md | started | started | started |
| docs/deploy/index.md | started | started | started |
| docs/evaluate/criteria.md | started | started | started |
| docs/evaluate/index.md | started | started | started |
| docs/evaluate/user-sim.md | started | started | started |
| docs/events/index.md | started | started | started |
| docs/get-started/go.md | started | started | started |
| docs/get-started/index.md | started | started | started |
| docs/get-started/installation.md | started | started | started |
| docs/get-started/java.md | started | started | started |
| docs/get-started/python.md | started | started | started |
| docs/get-started/quickstart.md | started | started | started |
| docs/get-started/streaming/quickstart-streaming-java.md | started | started | started |
| docs/get-started/streaming/quickstart-streaming.md | started | started | started |
| docs/grounding/google_search_grounding.md | started | started | started |
| docs/grounding/vertex_ai_search_grounding.md | started | started | started |
| docs/index.md | started | started | started |
| docs/mcp/index.md | started | started | started |
| docs/observability/logging.md | started | started | started |
| docs/plugins/index.md | started | started | started |
| docs/release-notes.md | started | started | started |
| docs/runtime/api-server.md | started | started | started |
| docs/runtime/index.md | started | started | started |
| docs/runtime/resume.md | started | started | started |
| docs/runtime/runconfig.md | started | started | started |
| docs/safety/index.md | started | started | started |
| docs/sessions/index.md | started | started | started |
| docs/sessions/memory.md | started | started | started |
| docs/sessions/state.md | started | started | started |
| docs/streaming/configuration.md | started | started | started |
| docs/streaming/dev-guide/part1.md | started | started | started |
| docs/streaming/index.md | started | started | started |
| docs/streaming/streaming-tools.md | started | started | started |
| docs/tools-custom/authentication.md | started | started | started |
| docs/tools-custom/function-tools.md | started | started | started |
| docs/tools-custom/index.md | started | started | started |
| docs/tools-custom/mcp-tools.md | started | started | started |
| docs/tools-custom/performance.md | started | started | started |
| docs/tutorials/agent-team.md | started | started | started |

## 2) 추가된 문서 (A)

- docs/agents/models/anthropic.md
- docs/agents/models/apigee.md
- docs/agents/models/google-gemini.md
- docs/agents/models/index.md
- docs/agents/models/litellm.md
- docs/agents/models/ollama.md
- docs/agents/models/vertex.md
- docs/agents/models/vllm.md
- docs/deploy/agent-engine/asp.md
- docs/deploy/agent-engine/deploy.md
- docs/deploy/agent-engine/index.md
- docs/deploy/agent-engine/test.md
- docs/get-started/typescript.md
- docs/grounding/index.md
- docs/integrations/agentmail.md
- docs/integrations/api-registry.md
- docs/integrations/apigee-api-hub.md
- docs/integrations/asana.md
- docs/integrations/atlassian.md
- docs/integrations/bigquery-agent-analytics.md
- docs/integrations/bigquery.md
- docs/integrations/bigtable.md
- docs/integrations/cartesia.md
- docs/integrations/chroma.md
- docs/integrations/code-execution.md
- docs/integrations/data-agent.md
- docs/integrations/daytona.md
- docs/integrations/elevenlabs.md
- docs/integrations/express-mode.md
- docs/integrations/gke-code-executor.md
- docs/integrations/google-search.md
- docs/integrations/hugging-face.md
- docs/integrations/index.md
- docs/integrations/linear.md
- docs/integrations/mailgun.md
- docs/integrations/mlflow.md
- docs/integrations/mongodb.md
- docs/integrations/n8n.md
- docs/integrations/paypal.md
- docs/integrations/pinecone.md
- docs/integrations/postman.md
- docs/integrations/pubsub.md
- docs/integrations/qdrant.md
- docs/integrations/restate.md
- docs/integrations/spanner.md
- docs/integrations/stripe.md
- docs/integrations/vertex-ai-rag-engine.md
- docs/integrations/vertex-ai-search.md
- docs/observability/index.md
- docs/runtime/command-line.md
- docs/runtime/event-loop.md
- docs/runtime/web-interface.md
- docs/sessions/session/migrate.md
- docs/sessions/session/rewind.md
- docs/streaming/dev-guide/part2.md
- docs/streaming/dev-guide/part3.md
- docs/streaming/dev-guide/part4.md
- docs/streaming/dev-guide/part5.md
- docs/tools/limitations.md
- docs/tutorials/coding-with-ai.md

## 3) 이름 변경 문서 (R)

- docs/integrations/ag-ui.md
- docs/integrations/agentops.md
- docs/integrations/application-integration.md
- docs/integrations/arize-ax.md
- docs/integrations/cloud-trace.md
- docs/integrations/code-exec-agent-engine.md
- docs/integrations/computer-use.md
- docs/integrations/freeplay.md
- docs/integrations/github.md
- docs/integrations/gitlab.md
- docs/integrations/mcp-toolbox-for-databases.md
- docs/integrations/monocle.md
- docs/integrations/notion.md
- docs/integrations/phoenix.md
- docs/integrations/reflect-and-retry.md
- docs/integrations/weave.md
- docs/sessions/session/index.md

## 4) 삭제 문서 (D)

- docs/agents/models.md
- docs/deploy/agent-engine.md
- docs/sessions/express-mode.md
- docs/streaming/custom-streaming-ws.md
- docs/streaming/custom-streaming.md
- docs/tools/built-in-tools.md
- docs/tools/google-cloud/bigquery-agent-analytics.md
- docs/tools/index.md
- docs/tools/third-party/agentql.md
- docs/tools/third-party/bright-data.md
- docs/tools/third-party/browserbase.md
- docs/tools/third-party/exa.md
- docs/tools/third-party/firecrawl.md
- docs/tools/third-party/hugging-face.md
- docs/tools/third-party/index.md
- docs/tools/third-party/scrapegraphai.md
- docs/tools/third-party/tavily.md
