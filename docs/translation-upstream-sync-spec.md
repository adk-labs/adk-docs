# ADK upstream sync 명세서 (ko/ja)

기준 커밋: `a9bbec2e` (merge `upstream/main`)

## 1) `a9bbec2e` 기준 KO/JA가 즉시 반영해야 할 42개 문서

다음 문서들은 영어 원문이 현재 `docs/` 기준으로 존재하지만, 현재 저장소의 `docs/ko`/`docs/ja`에 파일이 없음. 신규 생성 필요(각각 한/일본어 번역본 2건).

- `docs/integrations/api-registry.md`
- `docs/integrations/application-integration.md`
- `docs/integrations/asana.md`
- `docs/integrations/atlassian.md`
- `docs/integrations/bigquery.md`
- `docs/integrations/bigtable.md`
- `docs/integrations/cartesia.md`
- `docs/integrations/chroma.md`
- `docs/integrations/code-execution.md`
- `docs/integrations/data-agent.md`
- `docs/integrations/daytona.md`
- `docs/integrations/elevenlabs.md`
- `docs/integrations/gke-code-executor.md`
- `docs/integrations/google-search.md`
- `docs/integrations/linear.md`
- `docs/integrations/mailgun.md`
- `docs/integrations/mlflow.md`
- `docs/integrations/mongodb.md`
- `docs/integrations/n8n.md`
- `docs/integrations/paypal.md`
- `docs/integrations/pinecone.md`
- `docs/integrations/postman.md`
- `docs/integrations/pubsub.md`
- `docs/integrations/qdrant.md`
- `docs/integrations/restate.md`
- `docs/integrations/spanner.md`
- `docs/integrations/stripe.md`
- `docs/integrations/vertex-ai-rag-engine.md`
- `docs/integrations/vertex-ai-search.md`
- `docs/observability/index.md`
- `docs/runtime/command-line.md`
- `docs/runtime/event-loop.md`
- `docs/runtime/web-interface.md`
- `docs/sessions/session/migrate.md`
- `docs/sessions/session/rewind.md`
- `docs/streaming/dev-guide/part2.md`
- `docs/streaming/dev-guide/part3.md`
- `docs/streaming/dev-guide/part4.md`
- `docs/streaming/dev-guide/part5.md`
- `docs/tools/limitations.md`
- `docs/tutorials/coding-with-ai.md`
- `docs/deploy/agent-engine/test.md`

## 1-2) 1차 반영 상태 (현재 작업 기록)

- `docs/ko`/`docs/ja` 기준 42개 문서 중 **84개 파일 생성 완료**: English 원문 복사본 기반 (지금은 1차 반영 상태)
- 대상 문서: 위 1) 항목 42개
- 다음 단계: 각 문서 본문에 대해 한글/일본어로 전문 번역 반영

## 2) `mkdocs.yml`에서 이미 반영된 변경 (변경점 점검 포인트)

현재 `mkdocs.yml`에는 다음 항목이 반영되어야 할 항목으로 존재(또는 조정됨):

- `integrations/index.md` 추가
- 에이전트 런타임 하위에 `web-interface`, `command-line`, `event-loop`
- 배포 `agent-engine` 하위 `index/deploy/asp/test`
- 세션 하위에 `session/migrate`, `session/rewind`
- 스트리밍 개발 가이드 `part2~part5`
- `runtime`/`sessions`/`streaming`/`observability`/`tutorials`의 KO/JA 라벨링 유지
- Tools/observability 이동에 따른 `plugins`/`tools`/`observability` 리다이렉트 매핑 정합성
- `deploy/agent-engine/test.md` 경로로 이동한 테스트 문서 링크 정합성

(현재 `mkdocs.yml`의 로컬 diff를 다시 검토하면 위 항목이 반영되어 있는지 즉시 확인 가능)

## 3) 실행 순서(1 > 2 > 3)

1. **원문 추출**: 위 42개 영어 원문을 기준으로 분량/섹션별로 번역 블록 분리
2. **번역 적용**: `docs/ko/<path>` 및 `docs/ja/<path>` 신규 생성
   - 코드 블록, CLI/URL/API 스니펫, 설정 키명, 스키마/샘플은 번역하지 않음
   - 기술 용어(예: session, toolset, streaming)는 원문 용어를 우선 유지하고 괄호로 한글/일본어 병기
3. **검증 체크**: `mkdocs.yml` nav/redirects 경로와 신규 문서 경로 정합성, Markdown 링크 유효성, 각 문서 frontmatter 존재 여부

## 4) 추가로 필요한 작업

- `docs/ko` / `docs/ja` 42개 문서의 1차 번역 생성이 완료되면 `git status` 기준 KO/JA 신규 파일 수 42→84 건수 검증
- 생성 완료 후 `docs/translation-upstream-sync-spec.md`의 항목을 `완료` 상태로 갱신
