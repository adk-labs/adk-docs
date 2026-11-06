---
catalog_title: BigQuery Agent Analytics Plugin
catalog_description: 심층적인 에이전트 동작 분석 및 로깅을 위한 플러그인
catalog_icon: /integrations/assets/bigquery.png
catalog_tags: ["observability", "google"]
---

# ADK용 BigQuery Agent Analytics 플러그인

<div class="language-support-tag">
  <span class="lst-supported">ADK 지원 버전</span><span class="lst-python">Python v1.21.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v1.5.0</span><span class="lst-kotlin">Kotlin v0.8.0</span>
</div>

BigQuery Agent Analytics 플러그인은 심층적인 에이전트 동작 분석을 위한 강력한 솔루션을 제공하여 Agent Development Kit(ADK)를 크게 향상시킵니다. ADK 플러그인 아키텍처와 **BigQuery Storage Write API**를 사용하여 중요한 운영 이벤트를 Google BigQuery 테이블에 직접 캡처하고 기록함으로써, 디버깅, 실시간 모니터링 및 종합적인 오프라인 성능 평가를 위한 고급 기능을 제공합니다.

또한 이 플러그인은 **자동 스키마 업그레이드(Auto Schema Upgrade)**(기존 테이블에 새 열을 안전하게 추가), **도구 출처(Tool Provenance)** 추적(`LOCAL`, `MCP`, `SUB_AGENT`, `A2A`, `TRANSFER_AGENT`, `TRANSFER_A2A`, `TOOLBOX`, `SKILL`), human-in-the-loop 상호작용을 위한 **HITL 이벤트 추적**, **자동 뷰 생성(Automatic View Creation)**(쿼리하기 쉬운 평면화된 이벤트 뷰 생성)을 제공합니다.

**ADK 2.0** 멀티 에이전트 워크플로에 대한 지원을 통해 **Python** 및 **Go**에서 에이전트 핸드오프, 상태 체크포인트, 이벤트 압축(compaction) 및 장기 실행 도구로 추적 기능을 확장합니다. 네 가지 워크플로 이벤트 유형인 `AGENT_TRANSFER`, `AGENT_STATE_CHECKPOINT`(Go에서는 `CustomMetadataAllowlist`에서 체크포인트 키가 활성화된 경우 방출됨), `EVENT_COMPACTION`, `TOOL_PAUSED`가 추가되었습니다. 또한 모든 행에 `attributes.adk` 엔벨로프를 스탬프하여 에이전트 실행 그래프를 재구성하고 일시중지된 도구를 이를 재개하는 행과 조인할 수 있도록 합니다. **Java**의 경우 현재 `TOOL_PAUSED` 이벤트 및 일시중지/재개 페어링 키만 지원하며 `attributes.adk` 엔벨로프는 지원하지 않습니다. 자세한 내용은 [에이전트 워크플로 및 일시중지/재개 이벤트(ADK 2.0)](#adk-2-events)를 참고하세요.

이 플러그인에는 세 가지 안정성 및 관측 가능성 기능이 포함되어 있습니다(Java: v1.7.0 이상, Go):

- **리전 간 Storage Write API 라우팅:** `US` 멀티 리전 외부(예: `EU` 또는 `northamerica-northeast1`)의 BigQuery 데이터 세트에 대한 쓰기가 이제 쓰기 스트림을 소유한 리전으로 라우팅됩니다. 이전에는 "session not found" / stream-not-found 오류로 실패하고 모든 행이 조용히 누락될 수 있었습니다.
- **전송 및 콘텐츠 인시던트 관측 가능성:** 전송 손실이 원인별로 추적됩니다. 또한 Python과 Go에서는 센티널(sentinel) 행이 기록되는 포맷터 실패(및 Python의 경우 파서 실패)도 집계합니다. 이러한 카운터는 `BigQueryAgentAnalyticsPlugin.get_drop_stats()`(Python), `DropStats()`(Go, `agentanalytics.AsBigQueryAgentAnalyticsPlugin`을 통해), 또는 `getDropStats()`(Java)를 통해 노출되므로, 호스트에서 이를 폴링하여 자체 모니터링 시스템으로 내보낼 수 있습니다. 원인 키 및 시맨틱은 언어마다 다르며, 자세한 내용은 [드롭된 이벤트 관측 가능성](#dropped-event-observability)을 참고하세요.
- **Cloud Trace에서 중복 span 제거:** Agent Engine 원격 분석(`GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY=true`) 또는 기타 Cloud Trace 내보내기 도구가 전역 tracer provider에 연결되어 있을 때, 플러그인이 각 프레임워크 span 옆에 중복 span을 생성하지 않습니다. 플러그인은 여전히 주변 OTel span에서 `trace_id`를 상속하므로 BigQuery 행이 Cloud Trace 트레이스와 원활하게 조인됩니다.

Python(v2.7.0 이상) 및 Go에서는 모든 행이 쓰기 큐에 들어가기 전에 고유한 32자 16진수 `event_id`를 부여받습니다. 이 ID는 Storage Write API 재시도 전반에서 유지되므로 소비자가 재시도 중복을 식별할 수 있습니다. 선택적 `exactly_once_delivery`(Go의 경우 `ExactlyOnceDelivery`) 모드는 커밋된 스트림과 명시적 오프셋을 사용하여 활성 프로세서 내에서 모호한 재시도로 인한 중복을 방지합니다. 이 모드는 무손실 전송을 보장하지 않으며, 스트림 교체 및 `ResourceExhausted` 재시도 처리가 Python과 Go 간에 다르므로 자세한 내용은 [전송 및 중복 제거](#delivery-and-deduplication)를 참고하세요.

또한 Python(v2.7.0 이상) 및 Go는 모델 및 워크플로 종료 세부정보를 캡처합니다. 최종 `LLM_RESPONSE` 행에는 `finish_reason`과 모델에서 제공한 경우 정제된 `error_message`가 포함됩니다. 워크플로 노드는 `NODE_OUTPUT` 및 `NODE_ERROR`를 내보낼 수 있으며, 에이전트 또는 실행 실패는 `AGENT_ERROR` 및 `INVOCATION_ERROR`를 내보냅니다(Go에서 `AGENT_ERROR`는 ADK가 `AfterAgent` 콜백 없이 처리하는 실패한 활성화도 포함함).

ADK Python v2.13.0 이상에서는 플러그인에 다음 기능이 추가되었습니다:

- **도구 결과 오류 분류**(`tool_result_classifier` 및 `ToolResultClassification`): `isError=True` / `is_error=True`가 있는 MCP 도구 결과 및 `ReflectAndRetryToolPlugin` 오류 응답에 대한 기본 감지와 함께 제공되어, 예외를 발생시키는 대신 반환 값으로 실패를 보고하는 도구가 `TOOL_ERROR` 행으로 기록됩니다.
- **에이전트 평가 뷰**(`create_eval_views=True` 또는 온디맨드 `await plugin.create_eval_views()`): BigQuery에서 직접 `AgentData` 평가 트레이스를 재구성하는 `v_eval_session` 및 `v_eval_turn` 뷰를 생성합니다.

!!! warning "BigQuery Storage Write API"

    이 기능은 유료 서비스인 **BigQuery Storage Write API**를 사용합니다. 비용에 대한 자세한 내용은 [BigQuery 문서](https://cloud.google.com/bigquery/pricing?e=48754805&hl=ko#data-ingestion-pricing)를 참고하세요.

??? note "Kotlin 지원"

    **Kotlin** 플러그인은 호출 수명 주기 이벤트를 로깅합니다. 호출이 시작될 때 `INVOCATION_STARTING` 행을 작성하고 종료될 때 `INVOCATION_COMPLETED` 행을 작성하며, 아직 존재하지 않는 경우 처음 사용할 때 파티셔닝 및 클러스터링된 이벤트 테이블을 생성합니다.

    행은 Python, Go 및 Java에서 사용하는 Storage Write API 대신 호출 경로에서 동기적으로 `tabledata.insertAll`을 통해 한 번에 하나씩 삽입됩니다.

    Kotlin에서는 LLM, 도구, 에이전트, 상태, HITL 및 A2A 이벤트, ADK 2.0 워크플로 이벤트, 자동 뷰 생성, 자동 스키마 업그레이드, 도구 출처, GCS 오프로딩, 드롭 통계가 구현되어 있지 않습니다.

## 사용 사례

- **에이전트 워크플로 디버깅 및 분석:** 광범위한 *플러그인 수명 주기 이벤트*(LLM 호출, 도구 사용) 및 *에이전트 생성 이벤트*(사용자 입력, 모델 응답)를 명확하게 정의된 스키마로 캡처합니다.
- **대용량 분석 및 디버깅:** 높은 처리량과 짧은 지연 시간을 지원하기 위해 Storage Write API를 사용하여 비동기식으로 로깅 작업을 수행합니다.
- **멀티모달 분석:** 텍스트, 이미지 및 기타 양식을 기록하고 분석합니다. 대용량 파일은 GCS로 오프로드되어 Object Tables를 통해 BigQuery ML에서 액세스할 수 있습니다.
- **분산 추적(Distributed Tracing):** 에이전트 실행 흐름을 시각화하기 위해 OpenTelemetry 스타일의 추적(`trace_id`, `span_id`)을 기본적으로 지원합니다.
- **도구 출처(Tool Provenance):** 각 도구 호출의 출처(로컬 함수, MCP 서버, 하위 에이전트, A2A 원격 에이전트, 전송 에이전트, Toolbox 도구 또는 Skill 툴셋)를 추적합니다.
- **Human-in-the-Loop(HITL) 추적:** 자격 증명 요청, 확인 프롬프트 및 사용자 입력 요청을 위한 전용 이벤트 유형을 제공합니다.
- **에이전트 워크플로 추적(ADK 2.0):** 실행 그래프를 재구성하기 위한 `attributes.adk` 엔벨로프와 함께 에이전트 전송, 상태 체크포인트, 이벤트 압축 및 장기 실행 도구 일시중지/재개를 캡처합니다.
- **쿼리 가능한 이벤트 뷰:** JSON 페이로드 데이터를 unnest하여 다운스트림 분석을 간소화하는 평면화된 이벤트 유형별 BigQuery 뷰(예: `v_llm_request`, `v_tool_completed`)를 자동으로 생성합니다.

### 캡처된 이벤트 요약

다음 표에는 플러그인이 기록하는 모든 이벤트 유형이 나열되어 있습니다. 자세한 페이로드 예시는 [이벤트 유형 및 페이로드](#event-types)를 참고하세요. **뷰(View)** 열은 선택적 BigQuery 뷰를 보여줍니다. Python과 Go는 기본적으로 뷰를 생성하며, Java는 `createViews(true)`가 구성된 경우에만 뷰를 생성합니다.

**Kotlin**의 경우 플러그인은 `INVOCATION_STARTING` 및 `INVOCATION_COMPLETED`만 기록하고 뷰를 생성하지 않으므로 다른 행과 전체 **뷰** 열은 Python, Go 및 Java에 적용됩니다.

ADK Python v2.13.0 및 Go는 아래의 28가지 이벤트 유형을 지원하고 25개의 이벤트 유형별 뷰를 제공합니다. 세 가지 HITL 완료 이벤트에는 전용 뷰가 없습니다.

- **Python** 및 **Go**는 표의 모든 28가지 이벤트 유형을 내보냅니다.
- **Java**는 표의 28가지 이벤트 유형 중 21가지를 내보냅니다: `INVOCATION_ERROR`, `AGENT_ERROR`, `AGENT_TRANSFER`, `AGENT_STATE_CHECKPOINT`, `EVENT_COMPACTION`, `NODE_OUTPUT`, `NODE_ERROR`를 제외한 모든 행을 내보냅니다(워크플로 이벤트 중에서는 `TOOL_PAUSED`를 내보냄).

| 이벤트 유형 | 캡처 시점 | 주요 페이로드 필드 | 뷰 |
| --- | --- | --- | --- |
| `USER_MESSAGE_RECEIVED` | 사용자 메시지가 호출에 입력될 때 | 텍스트 요약 / 콘텐츠 파트 | `v_user_message_received` |
| `INVOCATION_STARTING` | 호출이 시작될 때 | *(공통 열만 해당)* | `v_invocation_starting` |
| `INVOCATION_COMPLETED` | 호출이 끝날 때 | *(공통 열만 해당)* | `v_invocation_completed` |
| `INVOCATION_ERROR` | 호출이 처리되지 않은 예외로 실패할 때 | 오류 메시지, 정제된 트레이스백 | `v_invocation_error` |
| `AGENT_STARTING` | 에이전트 실행이 시작될 때 | 지침 텍스트; ADK Python v2.12.0+에서는 지침 출처, 정적 지침, 설명, 모델 및 하위 에이전트 이름도 포함(Go는 에이전트 자체에 설정된 경우 `instruction_source`, `agent_description`, `sub_agents`, `model`을 기록하며 `static_instruction`은 채우지 않음) | `v_agent_starting` |
| `AGENT_COMPLETED` | 에이전트 실행이 끝날 때 | 지연 시간 | `v_agent_completed` |
| `AGENT_ERROR` | 에이전트 실행이 실패할 때; Go에서는 ADK가 `AfterAgent` 콜백 없이 처리하는 실패한 활성화도 포함됨 | 오류 메시지, 정제된 트레이스백, 지연 시간 | `v_agent_error` |
| `LLM_REQUEST` | 모델 요청이 전송될 때 | 모델, 프롬프트, 구성, 도구 | `v_llm_request` |
| `LLM_RESPONSE` | 모델 응답이 수신될 때 | 응답, 사용 토큰, 캐시 메타데이터, 종료 이유, 지연 시간, TTFT | `v_llm_response` |
| `LLM_ERROR` | 모델 호출이 실패할 때 | 오류 메시지, 지연 시간 | `v_llm_error` |
| `TOOL_STARTING` | 도구가 실행을 시작할 때 | 도구 이름, 인수, 출처 | `v_tool_starting` |
| `TOOL_COMPLETED` | 도구가 성공적으로 완료될 때 | 도구 이름, 결과, 출처, 지연 시간 | `v_tool_completed` |
| `TOOL_ERROR` | 도구가 실패할 때 | 도구 이름, 인수, 출처, 오류, 지연 시간 | `v_tool_error` |
| `STATE_DELTA` | 세션 상태가 변경될 때 | 상태 델타 | `v_state_delta` |
| `HITL_CREDENTIAL_REQUEST` | 자격 증명 요청이 방출될 때 | 합성 도구 이름, 인수 | `v_hitl_credential_request` |
| `HITL_CONFIRMATION_REQUEST` | 확인 요청이 방출될 때 | 합성 도구 이름, 인수 | `v_hitl_confirmation_request` |
| `HITL_INPUT_REQUEST` | 사용자 입력 요청이 방출될 때 | 합성 도구 이름, 인수 | `v_hitl_input_request` |
| `HITL_CREDENTIAL_REQUEST_COMPLETED` | 사용자가 자격 증명 응답을 제공할 때 | 합성 도구 이름, 결과 | *(기본 테이블만 해당)* |
| `HITL_CONFIRMATION_REQUEST_COMPLETED` | 사용자가 확인 응답을 제공할 때 | 합성 도구 이름, 결과 | *(기본 테이블만 해당)* |
| `HITL_INPUT_REQUEST_COMPLETED` | 사용자가 입력 응답을 제공할 때 | 합성 도구 이름, 결과 | *(기본 테이블만 해당)* |
| `A2A_INTERACTION` | 원격 A2A 호출이 완료될 때 | 응답, 작업 ID, 컨텍스트 ID, 요청/응답 | `v_a2a_interaction` |
| `AGENT_RESPONSE` | 최종 에이전트 응답이 생성될 때 | 응답 (content), 소스 이벤트 ID/작성자/브랜치 (attributes) | `v_agent_response` |
| `AGENT_TRANSFER` | 한 에이전트가 다른 에이전트로 제어권을 넘길 때 | 출발 에이전트, 도착 에이전트, 소스 이벤트 ID | `v_agent_transfer` |
| `AGENT_STATE_CHECKPOINT` | 에이전트가 상태의 스냅샷을 생성할 때(또는 실행 종료를 표시할 때); Go에서는 `CustomMetadataAllowlist`에서 체크포인트 키가 활성화된 경우 방출됨 | 에이전트 상태, 에이전트 종료 플래그, 소스 이벤트 ID | `v_agent_state_checkpoint` |
| `EVENT_COMPACTION` | 일련의 이벤트 기간이 요약으로 압축될 때 | 윈도우 시작/종료 타임스탬프, 압축된 콘텐츠 | `v_event_compaction` |
| `TOOL_PAUSED` | 장기 실행 도구(또는 HITL 요청)가 일시중지되어 재개를 기다릴 때 | 도구 이름, 인수, 일시중지 종류, 함수 호출 ID | `v_tool_paused` |
| `NODE_OUTPUT` | 워크플로 노드가 최종 구조화된 출력을 내보낼 때 | 출력, 노드 경로, 실행 ID, 부모 실행 ID | `v_node_output` |
| `NODE_ERROR` | 워크플로 노드가 비모델 오류로 종료될 때 | 오류 코드, 오류 메시지, 노드 경로, 실행 ID, 부모 실행 ID | `v_node_error` |

## 설치

=== "Python"

    전용 BigQuery Agent Analytics 엑스트라(extra)를 사용하여 ADK를 설치합니다. 이 엑스트라에는 플러그인에 필요한 BigQuery 클라이언트, Cloud Storage 클라이언트 및 `pyarrow`가 포함되어 있습니다:

    ```bash
    pip install "google-adk[bigquery-analytics]>=2.7.0"
    ```

    `pyarrow` 종속 항목은 더 이상 일반 `gcp` 엑스트라에 포함되지 않습니다. `pyarrow`가 누락된 경우 플러그인의 import 오류를 통해 설치해야 할 `bigquery-analytics` 엑스트라를 안내합니다.

=== "Go"

    Go 플러그인은 필요한 경우가 아니면 코어 ADK 애플리케이션이 BigQuery 및 Cloud Storage 클라이언트 종속 항목을 가져오지 않도록 `adk-go` 저장소에서 독립적인 Go 서브모듈(`plugin/agentanalytics/go.mod`)로 게시됩니다. Go 플러그인은 코어 `google.golang.org/adk/v2`와 별도로 버전이 관리됩니다(`/v2` 메이저 버전 접미사 없이 `module google.golang.org/adk/plugin/agentanalytics` 사용; 플러그인 릴리스 `v0.1.0`부터 `plugin/agentanalytics/v0.1.0`으로 태그가 지정되며, 지원 배지의 `Go v0.1.0`이 이를 나타냄). `go get`을 사용하여 코어 ADK Go(`v2.0.0+`)와 플러그인 모듈을 설치하세요(`@latest`는 최신 태그가 지정된 릴리스로 확인되며, `google.golang.org/adk/plugin/agentanalytics@v0.1.0`과 같이 명시적 플러그인 릴리스를 고정할 수도 있음):

    ```bash
    go get google.golang.org/adk/v2@latest
    go get google.golang.org/adk/plugin/agentanalytics@latest
    ```

## 빠른 시작

=== "Python"

    플러그인을 에이전트의 `App` 객체에 추가합니다. 전제 조건은
    [전제 조건](#prerequisites)을 참고하세요.

    ```python title="agent.py"
    import os
    from google.adk.agents import Agent
    from google.adk.apps import App
    from google.adk.models.google_llm import Gemini
    from google.adk.plugins.bigquery_agent_analytics_plugin import BigQueryAgentAnalyticsPlugin

    os.environ['GOOGLE_CLOUD_PROJECT'] = 'your-gcp-project-id'
    os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'
    os.environ['GOOGLE_GENAI_USE_ENTERPRISE'] = 'True'

    plugin = BigQueryAgentAnalyticsPlugin(
        project_id="your-gcp-project-id",
        dataset_id="your-big-query-dataset-id",
    )

    root_agent = Agent(
        model=Gemini(model="gemini-flash-latest"),
        name='my_agent',
        instruction="You are a helpful assistant.",
    )

    app = App(
        name="my_agent",
        root_agent=root_agent,
        plugins=[plugin],
    )
    ```

=== "Go"

    `agentanalytics.NewBigQueryAgentAnalyticsPlugin`으로 플러그인을 생성하고 `PluginConfig`를 통해 `runner.New`에 전달합니다. ADK Go의 러너는 플러그인을 자동으로 닫지 않으므로, 종료하기 전에 실행 함수 내에서 `defer bqPlugin.Close()`를 호출하여 버퍼링된 이벤트를 플러시하고 BigQuery 클라이언트를 해제하세요. 전제 조건은 [전제 조건](#prerequisites)을 참고하세요.

    ```go title="main.go"
    package main

    import (
    	"context"
    	"fmt"
    	"log"

    	"google.golang.org/adk/plugin/agentanalytics"
    	"google.golang.org/adk/v2/agent"
    	"google.golang.org/adk/v2/agent/llmagent"
    	"google.golang.org/adk/v2/model/gemini"
    	"google.golang.org/adk/v2/plugin"
    	"google.golang.org/adk/v2/runner"
    	"google.golang.org/adk/v2/session"
    	"google.golang.org/genai"
    )

    func run(ctx context.Context) error {
    	bqPlugin, err := agentanalytics.NewBigQueryAgentAnalyticsPlugin(
    		ctx,
    		"your-gcp-project-id",
    		"your-big-query-dataset-id",
    		"agent_events",
    	)
    	if err != nil {
    		return fmt.Errorf("create BigQuery plugin: %w", err)
    	}
    	defer bqPlugin.Close()

    	model, err := gemini.NewModel(ctx, "gemini-flash-latest", &genai.ClientConfig{
    		Project:  "your-gcp-project-id",
    		Location: "us-central1",
    		Backend:  genai.BackendVertexAI,
    	})
    	if err != nil {
    		return fmt.Errorf("create model: %w", err)
    	}

    	myAgent, err := llmagent.New(llmagent.Config{
    		Name:        "my_agent",
    		Model:       model,
    		Instruction: "You are a helpful assistant.",
    	})
    	if err != nil {
    		return fmt.Errorf("create agent: %w", err)
    	}

    	sessionService := session.InMemoryService()
    	r, err := runner.New(runner.Config{
    		AppName:        "my_agent",
    		Agent:          myAgent,
    		SessionService: sessionService,
    		PluginConfig: runner.PluginConfig{
    			Plugins: []*plugin.Plugin{bqPlugin},
    		},
    	})
    	if err != nil {
    		return fmt.Errorf("create runner: %w", err)
    	}

    	sessResp, err := sessionService.Create(ctx, &session.CreateRequest{
    		AppName: "my_agent",
    		UserID:  "demo_user",
    	})
    	if err != nil {
    		return fmt.Errorf("create session: %w", err)
    	}

    	userMsg := genai.NewContentFromText("Hello!", genai.RoleUser)
    	for _, err := range r.Run(ctx, "demo_user", sessResp.Session.ID(), userMsg, agent.RunConfig{}) {
    		if err != nil {
    			return fmt.Errorf("run error: %w", err)
    		}
    	}
    	return nil
    }

    func main() {
    	if err := run(context.Background()); err != nil {
    		log.Fatal(err)
    	}
    }
    ```

=== "Java"

    플러그인을 러너의 플러그인 목록에 추가합니다. 전제 조건은
    [전제 조건](#prerequisites)을 참고하세요.

    ```java title="Agent.java"
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.agents.RunConfig;
    import com.google.adk.models.Gemini;
    import com.google.adk.plugins.Plugin;
    import com.google.adk.plugins.agentanalytics.BigQueryAgentAnalyticsPlugin;
    import com.google.adk.plugins.agentanalytics.BigQueryLoggerConfig;
    import com.google.adk.runner.InMemoryRunner;
    import com.google.common.collect.ImmutableList;

    public final class Agent {
      public static void main(String[] args) throws Exception {
        Plugin bqLoggingPlugin = new BigQueryAgentAnalyticsPlugin(
            BigQueryLoggerConfig.builder()
                .projectId("your-gcp-project-id")
                .datasetId("your-big-query-dataset-id")
                .tableName("agent_events") // Optional; default in v1.8.0+
                .build());

        InMemoryRunner runner = new InMemoryRunner(
            LlmAgent.builder()
                .model(Gemini.builder().modelName("gemini-2.5-flash").build())
                .name("my_agent")
                .instruction("You are a helpful assistant.")
                .build(),
            "my_agent",
            ImmutableList.of(bqLoggingPlugin));

        // Use runner ...

        // Close runner to flush and close plugin
        runner.close().blockingAwait();
      }
    }
    ```

=== "Kotlin"

    플러그인을 에이전트의 `App` 객체에 추가합니다. 전제 조건은
    [전제 조건](#prerequisites)을 참고하세요. 이 플러그인은 JVM 전용이며 코어 외부에서
    제공되므로 통합(integrations) 아티팩트를 추가합니다.

    ```kotlin title="build.gradle.kts"
    implementation("com.google.adk:google-adk-kotlin-integrations:1.5.0")
    ```

    ```kotlin title="BigQueryAnalyticsExample.kt"
    --8<-- "examples/kotlin/snippets/integrations/BigQueryAnalyticsExample.kt:quickstart"
    ```

    플러그인은 처음 사용할 때 이벤트 테이블을 생성하므로 범위 내의 사용자 인증 정보에는
    행을 삽입할 권한뿐만 아니라 데이터 세트에 테이블을 생성할 권한도 필요합니다.
    `location`을 데이터 세트의 위치로 설정하세요(기본값은 `"US"`). 전체 옵션 세트는
    [구성 옵션](#configuration-options)을 참고하세요.

    로깅 실패로 인해 턴이 실패하지는 않습니다. 테이블을 생성할 수 없거나 행을 삽입할 수 없는 경우
    플러그인은 오류를 로그에 기록하고 호출은 계속 진행됩니다. 행이 누락된 경우
    `com.google.adk.kt.plugins.agentanalytics.BigQueryAgentAnalyticsPlugin`에 대한 로깅을
    활성화하세요. 로그는 플러그인의 ADK 이름(`bigquery_agent_analytics`)이 아닌 해당 클래스 이름으로
    출력됩니다.


### 에이전트 실행 및 테스트

에이전트를 실행하고 채팅 인터페이스를 통해 "무엇을 할 수 있는지 알려줘" 또는 "내 클라우드 프로젝트 `<your-gcp-project-id>`의 데이터 세트를 나열해 줘"와 같은 몇 가지 요청을 보내 플러그인을 테스트합니다. 이러한 작업은 Google Cloud 프로젝트의 BigQuery 인스턴스에 기록되는 이벤트를 생성합니다. 이벤트가 처리되면 [BigQuery 콘솔](https://console.cloud.google.com/bigquery)에서 다음 쿼리를 사용하여 데이터를 확인할 수 있습니다.

```sql
SELECT timestamp, event_type, content
FROM `your-gcp-project-id.your-big-query-dataset-id.agent_events`
ORDER BY timestamp DESC
LIMIT 20;
```

??? example "Full example with GCS offloading, OpenTelemetry, and tools"

    === "Python"

        ```python title="my_bq_agent/agent.py"
        # my_bq_agent/agent.py
        import os
        import google.auth
        from google.adk.apps import App
        from google.adk.plugins.bigquery_agent_analytics_plugin import BigQueryAgentAnalyticsPlugin, BigQueryLoggerConfig
        from google.adk.agents import Agent
        from google.adk.models.google_llm import Gemini
        from google.adk.tools.bigquery import BigQueryToolset, BigQueryCredentialsConfig


        # --- OpenTelemetry note (no setup required for BQAA) ---
        # The BQAA plugin does NOT export OTel spans of its own. It tracks the
        # parent-child hierarchy on an internal stack: the root invocation span
        # reuses the ambient OTel span's id (as a 16-hex string) when one is
        # active, and child BQAA spans are generated internally as 16-hex
        # strings. The plugin's `trace_id`
        # column inherits from whichever OpenTelemetry span is active in the
        # surrounding runtime when the agent runs:
        #   * Agent Engine wires its invocation span automatically, so
        #     `trace_id` in BigQuery joins to Cloud Trace out of the box.
        #   * Locally, framework-instrumented runners open an invocation span
        #     for you.
        #   * If neither is available, the plugin falls back to a per-invocation
        #     trace_id and the parent-child hierarchy is still preserved in
        #     BigQuery; no OTel setup needed.
        # Setting a bare `TracerProvider` with no ambient span will NOT cause
        # `trace_id` to be populated with a "real" OTel id; only an *active*
        # span does. See the "Tracing and observability" section for details.

        # --- Configuration ---
        PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "your-gcp-project-id")
        DATASET_ID = os.environ.get("BIG_QUERY_DATASET_ID", "your-big-query-dataset-id")
        # GOOGLE_CLOUD_LOCATION must be a valid Agent Platform region (e.g., "us-central1").
        # BQ_LOCATION is the BigQuery dataset location, which can be a multi-region
        # like "US" or "EU", or a single region like "us-central1".
        VERTEX_LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
        BQ_LOCATION = os.environ.get("BQ_LOCATION", "US")
        GCS_BUCKET = os.environ.get("GCS_BUCKET_NAME", "your-gcs-bucket-name") # Optional

        if PROJECT_ID == "your-gcp-project-id":
            raise ValueError("Please set GOOGLE_CLOUD_PROJECT or update the code.")

        # --- CRITICAL: Set environment variables BEFORE Gemini instantiation ---
        os.environ['GOOGLE_CLOUD_PROJECT'] = PROJECT_ID
        os.environ['GOOGLE_CLOUD_LOCATION'] = VERTEX_LOCATION
        os.environ['GOOGLE_GENAI_USE_ENTERPRISE'] = 'True'

        # --- Initialize the Plugin with Config ---
        bq_config = BigQueryLoggerConfig(
            enabled=True,
            gcs_bucket_name=GCS_BUCKET, # Enable GCS offloading for multimodal content
            log_multi_modal_content=True,
            max_content_length=500 * 1024, # 500 KB limit for inline text
            batch_size=1, # Default is 1 for low latency, increase for high throughput
            shutdown_timeout=10.0
        )

        bq_logging_plugin = BigQueryAgentAnalyticsPlugin(
            project_id=PROJECT_ID,
            dataset_id=DATASET_ID,
            table_id="agent_events", # default table name is agent_events
            config=bq_config,
            location=BQ_LOCATION
        )

        # --- Initialize Tools and Model ---
        credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        bigquery_toolset = BigQueryToolset(
            credentials_config=BigQueryCredentialsConfig(credentials=credentials)
        )

        llm = Gemini(model="gemini-flash-latest")

        root_agent = Agent(
            model=llm,
            name='my_bq_agent',
            instruction="You are a helpful assistant with access to BigQuery tools.",
            tools=[bigquery_toolset]
        )

        # --- Create the App ---
        app = App(
            name="my_bq_agent",
            root_agent=root_agent,
            plugins=[bq_logging_plugin],
        )
        ```

    === "Go"

        아래 Go 예제는 커스텀 `functiontool`(`reverse_string`)을 등록합니다. ADK Go 러너는 자체적으로 OpenTelemetry span을 열지 않으므로, `cfg.EnableOTelCorrelation = true`는 호스트 애플리케이션이 `r.Run`을 호출하기 전에 `ctx`에서 활성 OpenTelemetry span을 연 경우에만 `attributes.otel`을 기록합니다.

        ```go title="main.go"
        package main

        import (
        	"context"
        	"fmt"
        	"log"
        	"os"
        	"time"

        	"google.golang.org/adk/plugin/agentanalytics"
        	"google.golang.org/adk/v2/agent"
        	"google.golang.org/adk/v2/agent/llmagent"
        	"google.golang.org/adk/v2/model/gemini"
        	"google.golang.org/adk/v2/plugin"
        	"google.golang.org/adk/v2/runner"
        	"google.golang.org/adk/v2/session"
        	"google.golang.org/adk/v2/tool"
        	"google.golang.org/adk/v2/tool/functiontool"
        	"google.golang.org/genai"
        )

        type ReverseArgs struct {
        	Input string `json:"input" jsonschema:"Text to reverse."`
        }

        func reverseString(_ agent.Context, args ReverseArgs) (map[string]any, error) {
        	runes := []rune(args.Input)
        	for i, j := 0, len(runes)-1; i < j; i, j = i+1, j-1 {
        		runes[i], runes[j] = runes[j], runes[i]
        	}
        	return map[string]any{"reversed": string(runes)}, nil
        }

        func run(ctx context.Context) error {
        	projectID := os.Getenv("GOOGLE_CLOUD_PROJECT")
        	datasetID := os.Getenv("BIG_QUERY_DATASET_ID")
        	gcsBucket := os.Getenv("GCS_BUCKET_NAME")

        	cfg := agentanalytics.DefaultConfig()
        	cfg.ProjectID = projectID
        	cfg.DatasetID = datasetID
        	cfg.TableName = "agent_events"
        	cfg.GCSBucketName = gcsBucket
        	cfg.LogMultiModalContent = true
        	cfg.MaxContentLen = 500 * 1024
        	cfg.EnableOTelCorrelation = true
        	cfg.ShutdownTimeout = 10 * time.Second

        	bqPlugin, err := agentanalytics.NewBigQueryAgentAnalyticsPluginWithConfig(ctx, cfg)
        	if err != nil {
        		return fmt.Errorf("failed to create BigQuery plugin: %w", err)
        	}
        	defer bqPlugin.Close()

        	reverseTool, err := functiontool.New(functiontool.Config{
        		Name:        "reverse_string",
        		Description: "Reverses the provided input string.",
        	}, reverseString)
        	if err != nil {
        		return fmt.Errorf("failed to create tool: %w", err)
        	}

        	model, err := gemini.NewModel(ctx, "gemini-flash-latest", &genai.ClientConfig{
        		Project:  projectID,
        		Location: "us-central1",
        		Backend:  genai.BackendVertexAI,
        	})
        	if err != nil {
        		return fmt.Errorf("failed to create model: %w", err)
        	}

        	demoAgent, err := llmagent.New(llmagent.Config{
        		Name:        "bq_demo_agent",
        		Model:       model,
        		Instruction: "You are a helpful assistant. Use reverse_string when asked to reverse text.",
        		Tools:       []tool.Tool{reverseTool},
        	})
        	if err != nil {
        		return fmt.Errorf("failed to create agent: %w", err)
        	}

        	sessionService := session.InMemoryService()
        	r, err := runner.New(runner.Config{
        		AppName:        "bq_demo_agent",
        		Agent:          demoAgent,
        		SessionService: sessionService,
        		PluginConfig: runner.PluginConfig{
        			Plugins: []*plugin.Plugin{bqPlugin},
        		},
        	})
        	if err != nil {
        		return fmt.Errorf("failed to create runner: %w", err)
        	}

        	sessResp, err := sessionService.Create(ctx, &session.CreateRequest{
        		AppName: "bq_demo_agent",
        		UserID:  "demo_user",
        	})
        	if err != nil {
        		return fmt.Errorf("failed to create session: %w", err)
        	}

        	userMsg := genai.NewContentFromText("Please reverse the word 'analytics'.", genai.RoleUser)
        	for event, err := range r.Run(ctx, "demo_user", sessResp.Session.ID(), userMsg, agent.RunConfig{}) {
        		if err != nil {
        			return fmt.Errorf("run error: %w", err)
        		}
        		if event.IsFinalResponse() && event.Content != nil {
        			for _, part := range event.Content.Parts {
        				if part.Text != "" {
        					fmt.Printf("Agent: %s\n", part.Text)
        				}
        			}
        		}
        	}
        	return nil
        }

        func main() {
        	if err := run(context.Background()); err != nil {
        		log.Fatal(err)
        	}
        }
        ```

    === "Java"

        ```java
        package adk.plugins.agentanalytics.demo;

        import static java.nio.charset.StandardCharsets.UTF_8;
        import static java.util.Collections.singletonList;

        import com.google.adk.agents.LlmAgent;
        import com.google.adk.agents.RunConfig;
        import com.google.adk.events.Event;
        import com.google.adk.models.Gemini;
        import com.google.adk.plugins.Plugin;
        import com.google.adk.plugins.agentanalytics.BigQueryAgentAnalyticsPlugin;
        import com.google.adk.plugins.agentanalytics.BigQueryLoggerConfig;
        import com.google.adk.runner.InMemoryRunner;
        import com.google.adk.sessions.Session;
        import com.google.adk.tools.FunctionTool;
        import com.google.adk.tools.ToolContext;
        import com.google.genai.types.Content;
        import com.google.genai.types.GenerateContentConfig;
        import com.google.genai.types.Part;
        import io.opentelemetry.sdk.OpenTelemetrySdk;
        import io.opentelemetry.sdk.common.CompletableResultCode;
        import io.opentelemetry.sdk.trace.SdkTracerProvider;
        import io.opentelemetry.sdk.trace.data.SpanData;
        import io.opentelemetry.sdk.trace.export.SimpleSpanProcessor;
        import io.opentelemetry.sdk.trace.export.SpanExporter;
        import io.reactivex.rxjava3.core.Flowable;
        import java.util.Collection;
        import java.util.Scanner;

        /** Demo agent showing how to use BigQueryAgentAnalyticsPlugin. */
        public final class BqDemoAgent {
          private static final String PROJECT_ID = "your-gcp-project-id";
          private static final String DATASET_ID = "your-gcp-dataset_id";
          private static final String TABLE_ID = "your-gcp-table";
          private static final String GCS_BUCKET_NAME = "your-gcs-bucket-name";
          private static final String API_KEY = "your-api_key";

          // A simple tool to demonstrate tool execution logging
          public static String reverseString(String input, ToolContext toolContext) {
            return new StringBuilder(input).reverse().toString();
          }

          public static void main(String[] args) throws Exception {
            // 0. Initialize OpenTelemetry
            initOpenTelemetry();

            // 1. Configure the BigQuery Logger
            BigQueryLoggerConfig config =
                BigQueryLoggerConfig.builder()
                    .projectId(PROJECT_ID)
                    .datasetId(DATASET_ID)
                    .tableName(TABLE_ID)
                    .gcsBucketName(GCS_BUCKET_NAME)
                    .createViews(true)
                    .build();

            // 2. Create the plugin instance
            Plugin bqLoggingPlugin = new BigQueryAgentAnalyticsPlugin(config);

            // 3. Initialize the model (Gemini)
            Gemini model =
                Gemini.builder()
                    .modelName("gemini-3-flash-preview") // Use appropriate model
                    .apiKey(API_KEY)
                    .build();

            // 4. Create the agent with the tool and plugin
            LlmAgent agent =
                LlmAgent.builder()
                    .model(model)
                    .name("bq_demo_agent")
                    .instruction(
                        "You are a helpful assistant. You have a tool 'reverseString' that you can use to"
                            + " reverse text.")
                    .tools(FunctionTool.create(BqDemoAgent.class, "reverseString"))
                    .generateContentConfig(GenerateContentConfig.builder().temperature(0.5f).build())
                    .build();

            // 5. Initialize the runner
            InMemoryRunner runner =
                new InMemoryRunner(agent, "bq_demo_agent", singletonList(bqLoggingPlugin));

            // 6. Create a session
            Session session =
                runner.sessionService().createSession(runner.appName(), "demo_user").blockingGet();

            RunConfig runConfig = RunConfig.builder().build();

            System.out.println("Agent ready. Type 'quit' to exit.");

            try (Scanner scanner = new Scanner(System.in, UTF_8)) {
              while (true) {
                System.out.print("\nUser: ");
                String userInput = scanner.nextLine();
                if (userInput.trim().equalsIgnoreCase("quit")) {
                  break;
                }

                Content userMsg = Content.fromParts(Part.fromText(userInput));

                // Run the agent and stream events
                Flowable<Event> events =
                    runner.runAsync(session.userId(), session.id(), userMsg, runConfig);

                System.out.print("Agent: ");
                events.blockingForEach(
                    event -> {
                      if (event.finalResponse()) {
                        System.out.println(event.stringifyContent());
                      }
                    });
              }
            } finally {
              System.out.println("Closing runner (flushing remaining logs)...");
              runner.close().blockingAwait();
              System.out.println("Done.");
            }
          }

          private static void initOpenTelemetry() {
            PrintingSpanExporter exporter = new PrintingSpanExporter();
            SdkTracerProvider tracerProvider =
                SdkTracerProvider.builder().addSpanProcessor(SimpleSpanProcessor.create(exporter)).build();
            OpenTelemetrySdk.builder().setTracerProvider(tracerProvider).buildAndRegisterGlobal();
          }

          private static class PrintingSpanExporter implements SpanExporter {
            @Override
            public CompletableResultCode export(Collection<SpanData> spans) {
              for (SpanData span : spans) {
                System.out.println("--- Span: " + span.getName() + " ---");
                System.out.println("  TraceId: " + span.getTraceId());
                System.out.println("  SpanId: " + span.getSpanId());
                System.out.println("  ParentSpanId: " + span.getParentSpanId());
                System.out.println("  Attributes: " + span.getAttributes());
                System.out.println("------------------------");
              }
              return CompletableResultCode.ofSuccess();
            }

            @Override
            public CompletableResultCode flush() {
              return CompletableResultCode.ofSuccess();
            }

            @Override
            public CompletableResultCode shutdown() {
              return CompletableResultCode.ofSuccess();
            }
          }

          private BqDemoAgent() {}
        }
        ```

!!! tip "Agent Runtime에 배포하시겠습니까?"

    [Agent Runtime에 배포](#deploy-agent-runtime)를 참고하세요.

## 전제 조건 {#prerequisites}

- **BigQuery API**가 활성화된 **Google Cloud 프로젝트**.
- **BigQuery 데이터 세트:** 플러그인을 사용하기 전에 로깅 테이블을 저장할 데이터 세트를 생성하세요. 테이블이 없으면 플러그인이 데이터 세트 내에 필요한 이벤트 테이블을 자동으로 생성합니다.
- **Google Cloud Storage 버킷 (선택 사항):** 멀티모달 콘텐츠(이미지, 오디오 등)를 로깅하려는 경우 대용량 파일을 오프로드할 수 있도록 GCS 버킷을 생성하는 것이 좋습니다.
- **인증:**
    - **로컬:** `gcloud auth application-default login`을 실행합니다.
    - **클라우드:** 서비스 계정에 필요한 권한이 있는지 확인합니다.

??? note "참고: Gemini 모델 선택기 `gemini-flash-latest`"

    ADK 문서의 대부분의 코드 예제는 [최신 사용 가능한](https://ai.google.dev/gemini-api/docs/models#latest) Gemini Flash 버전을 선택하기 위해 `gemini-flash-latest`를 사용합니다. 그러나 `us-central1`과 같은 리전 엔드포인트에서 Gemini에 액세스하는 경우 이 선택 문자열이 작동하지 않을 수 있습니다. 이 경우 [Gemini 모델](https://ai.google.dev/gemini-api/docs/models) 페이지 또는 Google Cloud [Gemini 모델](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models) 목록에서 특정 모델 버전 문자열을 사용하세요.

### IAM 권한

에이전트가 제대로 작동하려면 에이전트가 실행되는 주 구성원(예: 서비스 계정, 사용자 계정)에 다음 Google Cloud 역할이 필요합니다.

- BigQuery 쿼리를 실행하기 위한 프로젝트 수준의 `roles/bigquery.jobUser`.
- 이벤트 테이블을 생성 또는 업그레이드하고, 이벤트 유형별 뷰를 생성하며(Python과 Go는 기본적으로 뷰를 생성함), 로그/이벤트 데이터를 쓰기 위한 데이터 세트 수준의 `roles/bigquery.dataEditor`(또는 이벤트 테이블이 이미 존재하고 자동 뷰 생성이 비활성화된 경우 테이블 수준).
- **GCS 오프로딩을 사용하는 경우:** 대상 버킷에 대한 `roles/storage.objectCreator` 및 `roles/storage.objectViewer`.

주 구성원에게 대상 테이블에만 `roles/bigquery.dataEditor` 권한이 있는 경우 테이블 생성 및 자동 뷰 생성(Python의 `create_views=True`, Go의 `DisableCreateViews: false`)이 실패합니다. 데이터 세트에 `roles/bigquery.dataEditor`를 부여하거나, 배포 단계에서 테이블과 뷰를 미리 생성하세요(Python의 `create_views=False`; Go의 `DisableCreateViews: true`와 함께 `bqPlugin.SyncViews(ctx)` 또는 `cfg.ViewDefinitions()` 사용). Go에서는 백그라운드 뷰 생성 실패가 `agentanalytics.Config`에 기본값이 아닌 `Logger`가 구성된 경우에만 로깅되므로 `Logger`를 설정하는 것이 좋습니다.

## 구성 옵션 {#configuration-options}

=== "Python"

    ### 생성자 매개변수

    `BigQueryAgentAnalyticsPlugin` 생성자는 다음 매개변수를 허용합니다. 또한 `**kwargs`도 허용되며, 이는 `BigQueryLoggerConfig`로 직접 전달됩니다(아래 참조).

    | 매개변수 | 유형 | 기본값 | 사용 시점 |
    | --- | --- | --- | --- |
    | `project_id` | `str` | *(필수)* | Google Cloud 프로젝트 선택 |
    | `dataset_id` | `str` | *(필수)* | BigQuery 데이터 세트 선택 |
    | `table_id` | `Optional[str]` | `None` | 커스텀 테이블 이름 사용(config의 `table_id` 재정의) |
    | `config` | `Optional[BigQueryLoggerConfig]` | `None` | 세부 조정을 위한 구성 객체 전달 |
    | `location` | `str` | `"US"` | BigQuery 데이터 세트 위치와 일치(예: `"US"`, `"EU"`, `"us-central1"`) |
    | `credentials` | `Optional[google.auth.credentials.Credentials]` | `None` | [ADC](https://cloud.google.com/docs/authentication/application-default-credentials) 대신 명시적 서비스 계정, 가장(impersonated) 또는 프로젝트 간 사용자 인증 정보 사용 |
    | `credentials_identifier` | `Optional[str]` | `None` | [공유 백그라운드 기록기](#shared-background-writer)를 공유할 플러그인 인스턴스를 명시적으로 선택합니다. 동등한 자격 증명과 기록기 설정을 가진 인스턴스에 대해서만 동일한 식별자를 사용하세요. `config`를 수정하지 않고 `config.credentials_identifier`보다 우선 적용됩니다. |

    ```python
    plugin = BigQueryAgentAnalyticsPlugin(
        project_id="my-project",
        dataset_id="my_dataset",
        batch_size=10,           # BigQueryLoggerConfig로 전달됨
        shutdown_timeout=5.0,    # BigQueryLoggerConfig로 전달됨
    )
    ```

    ### BigQueryLoggerConfig 옵션

    아래의 모든 옵션은 선택 사항이며 합리적인 기본값을 가집니다. `BigQueryLoggerConfig` 또는 플러그인 생성자의 `**kwargs`로 전달하세요.

    | 옵션 | 유형 | 기본값 | 설명 |
    | --- | --- | --- | --- |
    | `enabled` | `bool` | `True` | 로깅 임시 비활성화 |
    | `table_id` | `str` | `"agent_events"` | 커스텀 BigQuery 테이블 이름 지정 |
    | `clustering_fields` | `List[str]` | `["event_type", "agent", "user_id"]` | 생성 시 테이블 클러스터링 필드 사용자 정의 |
    | `gcs_bucket_name` | `Optional[str]` | `None` | 대용량 텍스트 및 멀티모달 콘텐츠를 GCS로 오프로드 |
    | `connection_id` | `Optional[str]` | `None` | GCS 콘텐츠를 쿼리하기 위한 BigQuery ObjectRef / 객체 테이블 사용 |
    | `max_content_length` | `int` | `500 * 1024` | 오프로드/자르기 전 인라인 페이로드 크기 제어. 제한을 두지 않으려면 `-1`을 사용하세요. 다른 값은 최소 `1` 이상이어야 합니다. |
    | `batch_size` | `int` | `1` | 쓰기 처리량 대 지연 시간 조정(기본값 1은 낮은 지연 시간용, 높은 처리량의 경우 증가) |
    | `batch_flush_interval` | `float` | `1.0` | 부분 일괄 처리를 주기적으로 플러시(초) |
    | `shutdown_timeout` | `float` | `10.0` | 종료 시 최종 플러시 대기 시간(초) |
    | `event_allowlist` | `Optional[List[str]]` | `None` | 선택한 이벤트 유형만 로깅 |
    | `event_denylist` | `Optional[List[str]]` | `None` | 민감하거나 불필요한 이벤트 유형 건너뛰기 |
    | `content_formatter` | `Optional[Callable]` | `None` | 이벤트별 커스텀 마스킹/포맷팅 적용(시크릿 수정 등) |
    | `log_multi_modal_content` | `bool` | `True` | GCS 참조를 포함한 `content_parts` 세부정보 캡처 |
    | `queue_max_size` | `int` | `10000` | 인메모리 이벤트 대기열을 제한합니다. ADK Python v2.13.0에서는 모든 이벤트 유형이 이 용량을 공유하며, 대기열이 가득 차면 종료 `INVOCATION_COMPLETED` 및 `INVOCATION_ERROR` 행도 드롭될 수 있고 `queue_full` 아래에 집계됩니다. |
    | `retry_config` | `Optional[RetryConfig]` | `None` | 재시도 동작 조정 |
    | `log_session_metadata` | `bool` | `True` | `attributes`에 세션 정보 추가(`session_id`, `app_name`, `user_id`, `state`). `temp:` 접두사가 붙은 키는 [수정(redacted)](#built-in-redaction)됨. |
    | `custom_tags` | `Dict[str, Any]` | `{}` | 모든 이벤트의 `attributes`에 정적 태그(예: `{"env": "prod"}`) 추가 |
    | `auto_schema_upgrade` | `bool` | `True` | 기존 테이블에 새 열 자동 추가(추가 전용) |
    | `create_views` | `bool` | `True` | 이벤트 유형별 BigQuery 뷰 생성 |
    | `create_eval_views` | `bool` | `False` | ADK Python v2.13.0 이상에서 설정 중에 [에이전트 평가 뷰](#agent-evaluation-views)(`{view_prefix}_eval_session` 및 `{view_prefix}_eval_turn`)도 생성 |
    | `view_prefix` | `str` | `"v"` | 여러 플러그인이 데이터 세트를 공유할 때 뷰 이름 충돌 방지(예: `"v_staging"`) |
    | `enable_otel_correlation` | `bool` | `False` | 최선형 Cloud Trace 조인 키로서 주변 OpenTelemetry span 컨텍스트를 `attributes.otel.{span_id, trace_id}`로 캡처 |
    | `custom_metadata_allowlist` | `Optional[List[str]]` | `None` | 선택된 `event.custom_metadata` 키를 `attributes.custom_metadata.*`에 캡처: 정확한 키 또는 `"prefix*"` 패턴. ADK Python v2.12.0 이상에서는 최종 `LLM_RESPONSE` 행이 `llm_response.custom_metadata`의 키를 캡처합니다. |
    | `payload_column_denylist` | `Optional[List[str]]` | `None` | 쓰기 시 테이블에서 페이로드 열(`content`, `content_parts`, `attributes`, `latency_ms`) 제외 투영 |
    | `final_response_tool_names` | `FrozenSet[str]` | `frozenset()` | 선택한 성공 도구의 호출 인수를 `AGENT_RESPONSE` 페이로드로 기록 |
    | `flush_on_run_end` | `bool` | `True` | 각 실행이 끝날 때 대기열에 있는 행 쓰기 완료 대기 |
    | `exactly_once_delivery` | `bool` | `False` | 커밋된 스트림과 명시적 오프셋을 사용하여 활성 프로세서 내에서 모호한 재시도 중복 방지 |
    | `use_dedicated_background_loop` | `Optional[bool]` | `None` | 배치 기록기가 실행되는 위치 선택: `None`은 `flush_on_run_end=False`일 때 [공유 백그라운드 기록기](#shared-background-writer) 스레드를 사용하고, `True`는 항상 이를 사용하며, `False`는 기록기를 호출자의 이벤트 루프에 유지합니다. |
    | `credentials_identifier` | `Optional[str]` | `None` | 백그라운드 기록기를 공유할 플러그인 인스턴스를 명시적으로 선택합니다. 생성자 인수가 우선합니다. 동일한 자격 증명 및 기록기 설정을 가진 인스턴스에 대해서만 동일한 식별자를 사용하세요. |
    | `debug_content_formatter_errors` | `bool` | `False` | `content_formatter`에 의해 발생한 예외의 제한된 트레이스백을 플러그인의 로컬 Python 로그 경고에 추가합니다. 트레이스백에는 포맷팅되지 않은 콘텐츠가 포함될 수 있으며 BigQuery에는 기록되지 않습니다. |
    | `on_schema_error` | `Optional[Callable[[Exception], None]]` | `None` | ADK Python v2.12.0 이상에서, [테이블 준비 상태 확인](#table-readiness-callbacks)이 테이블을 읽거나 생성하거나 업그레이드하는 데 실패할 때마다 예외와 함께 동기 콜백을 실행합니다. 동기 콜러블이 아닌 값은 플러그인 생성 시 `ValueError`를 발생시킵니다. |
    | `on_schema_ready` | `Optional[Callable[[], None]]` | `None` | ADK Python v2.12.0 이상에서, 요청된 모든 뷰를 포함하여 [테이블 준비 상태 확인](#table-readiness-callbacks)이 성공할 때마다 인수가 없는 동기 콜백을 실행합니다. 동기 콜러블이 아닌 값은 플러그인 생성 시 `ValueError`를 발생시킵니다. |
    | `tool_result_classifier` | `Optional[ToolResultClassifier]` | `None` | ADK Python v2.13.0 이상에서, `ToolResultClassification`(또는 기본 제공 MCP `isError` / `is_error` 규칙으로 폴백하기 위해 `None`)을 반환하는 동기 콜백을 통해 반환된 도구 결과를 `"ERROR"` 또는 `"OK"`로 분류합니다. 자세한 내용은 [도구 결과 오류 분류](#tool-result-error-classification)를 참고하세요. |

    다음 코드 샘플은 BigQuery Agent Analytics 플러그인 구성을 정의하는 방법을 보여줍니다.

    ```python
    import json
    import re
    from typing import Any

    from google.adk.plugins.bigquery_agent_analytics_plugin import BigQueryLoggerConfig

    def redact_dollar_amounts(event_content: Any, event_type: str) -> str:
        """
        달러 금액(예: $600, $12.50)을 수정하고
        입력이 dict인 경우 JSON 출력을 보장하는 커스텀 포맷터입니다.

        Args:
            event_content: 이벤트의 원시 콘텐츠.
            event_type: 이벤트 유형 문자열(예: "LLM_REQUEST", "LLM_RESPONSE").
        """
        text_content = ""
        if isinstance(event_content, dict):
            text_content = json.dumps(event_content)
        else:
            text_content = str(event_content)

        # 달러 금액 정규식: $ 뒤에 숫자가 오고, 선택적으로 쉼표나 소수점이 포함됨.
        # 예: $600, $1,200.50, $0.99
        redacted_content = re.sub(r'\$\d+(?:,\d{3})*(?:\.\d+)?', 'xxx', text_content)

        return redacted_content

    config = BigQueryLoggerConfig(
        enabled=True,
        event_allowlist=["LLM_REQUEST", "LLM_RESPONSE"], # 이 이벤트만 기록
        # event_denylist=["TOOL_STARTING"], # 이 이벤트 건너뛰기
        shutdown_timeout=10.0, # 종료 시 로그 플러시를 위해 최대 10초 대기
        max_content_length=500, # 콘텐츠를 500자로 자름
        content_formatter=redact_dollar_amounts, # 로깅 콘텐츠의 달러 금액 수정
        queue_max_size=10000, # 메모리에 보관할 최대 이벤트 수
        auto_schema_upgrade=True, # 기존 테이블에 새 열 자동 추가
        create_views=True, # 이벤트 유형별 뷰 자동 생성
        # retry_config=RetryConfig(max_retries=3), # 선택 사항: 재시도 구성
    )

    plugin = BigQueryAgentAnalyticsPlugin(
        project_id="my-project",
        dataset_id="my_dataset",
        config=config,
    )
    ```

    ### 추적 상관관계, 메타데이터 캡처 및 열 프로젝션

    <div class="language-support-tag">
      <span class="lst-supported">ADK 지원 버전</span><span class="lst-python">Python v2.4.0</span>
    </div>

    세 가지 옵션이 `attributes`에 들어갈 추가 컨텍스트와 페이로드 열의 작성 여부를 제어합니다. 각 옵션은 위의 `BigQueryLoggerConfig` 옵션 표에 나열되어 있으며, 아래의 참고사항은 단순 표에서 표현할 수 없는 교차 옵션 규칙을 설명합니다.

    - **`enable_otel_correlation`**: 캡처된 span 컨텍스트는 외래 키가 아니라 최선형 Cloud Trace 상관관계 키입니다. 비활성화된 경우(기본값) `attributes.otel`이 작성되지 않습니다.
    - **`custom_metadata_allowlist`**: 설정하지 않으면 기본 `a2a:*` 캡처만 실행되는 이전 동작이 유지됩니다. 키는 `event.custom_metadata`에서 읽습니다. ADK Python v2.12.0 이상에서는 최종(부분 응답이 아닌) `LLM_RESPONSE` 행이 `llm_response.custom_metadata`에서 키를 읽습니다. 캡처된 값은 다른 모든 로깅 콘텐츠와 동일한 안전 파이프라인(자르기, 민감한 키 수정, 순환 참조 처리)을 통과합니다.
    - **`payload_column_denylist`**: `content`, `content_parts`, `attributes`, `latency_ms`만 나열할 수 있습니다. 식별 및 상관관계 열은 보호되며 나열 시 `ValueError`가 발생합니다. 프로젝션은 스키마 우선으로 적용되므로 테이블 스키마, 작성된 행 및 자동 생성된 뷰가 일관성을 유지합니다(뷰는 거부된 열에 종속된 파생 열을 삭제함). `attributes`를 거부하면 `attributes.otel` 및 `attributes.custom_metadata`도 비활성화되며, 비어 있지 않은 `custom_metadata_allowlist`와 결합하면 생성 시 거부됩니다.

    ```python
    config = BigQueryLoggerConfig(
        enable_otel_correlation=True,                      # Cloud Trace와의 조인 키
        custom_metadata_allowlist=["ticket_id", "exp:*"],  # 선택한 custom_metadata 키 캡처
        # payload_column_denylist=["content_parts"],       # 멀티모달 페이로드 유지 안 함
    )
    ```

    ### 최종 답변 캡처 및 실행 종료 시 플러시

    에이전트가 일반 텍스트 최종 이벤트를 생성하는 대신 전용 도구를 호출하여 최종 답변을 제공하는 경우 `final_response_tool_names`를 사용하세요. 일치하는 도구 호출이 성공하면 플러그인은 도구의 호출 인수를 `AGENT_RESPONSE` 행으로 작성하고 `attributes`에 `source_tool`을 추가합니다.

    `flush_on_run_end` 옵션의 기본값은 `True`이며, 이는 `after_run_callback`이 현재 이벤트 루프의 쓰기 큐를 대기하도록 만듭니다. 응답 경로에서 해당 플러시를 제거하려면 `False`로 설정하세요. 백그라운드 기록기가 대기열을 계속 비우므로 실행이 반환된 후 잠시 뒤에 BigQuery에 행이 나타날 수 있습니다. Python v2.10.0 이상에서는 이 설정을 사용하면 기록기가 [공유 백그라운드 기록기](#shared-background-writer)로 이동합니다.

    ```python
    config = BigQueryLoggerConfig(
        final_response_tool_names=frozenset({"submit_final_response"}),
        flush_on_run_end=False,
    )
    ```

    ### 공유 백그라운드 기록기 {#shared-background-writer}

    <div class="language-support-tag">
      <span class="lst-supported">ADK 지원 버전</span><span class="lst-python">Python v2.10.0</span>
    </div>

    `flush_on_run_end=False`인 경우 플러그인은 호출자의 이벤트 루프 대신 프로세스 수명 주기를 갖는 전용 백그라운드 이벤트 루프 스레드에서 배치 기록기를 실행합니다. `flush_on_run_end=True`일 때도 해당 스레드를 사용하려면 `use_dedicated_background_loop=True`로 설정하고, 기록기를 호출자의 이벤트 루프에 유지하려면 `False`로 설정하세요.

    동일한 프로세스 내에서 동등한 자격 증명으로 동일한 테이블을 대상으로 하는 플러그인 인스턴스는 단일 백그라운드 기록기와 BigQuery 쓰기 클라이언트를 공유하므로, 요청당 하나와 같이 수명이 짧은 플러그인 인스턴스가 각각 새 기록기를 열지 않습니다. 동등성은 자격 증명 ID(예: 서비스 계정 이메일, 범위, 프로젝트)에서 파생됩니다. 어떤 플러그인 인스턴스가 기록기를 공유할지 명시적으로 선택하려면 `credentials_identifier`를 설정하세요. 동등한 자격 증명과 기록기 설정을 가진 인스턴스에 대해서만 동일한 식별자를 사용하세요. 공유 기록기는 이를 생성한 인스턴스의 자격 증명 및 기록기 설정(예: `batch_size`, `retry_config`)을 사용합니다.

    기본 인수로 `shutdown()` 또는 `close()`를 호출하면 플러그인 인스턴스가 공유 기록기에서 분리되지만 기록기는 계속 실행되므로 대기 중인 행이 계속 기록됩니다. 인터프리터 종료 시 플러그인은 활성 기록기를 비우기 위해 최선의 노력을 다합니다. 독립 실행형 스크립트나 테스트 종료 시 등 공유 기록기를 명시적으로 비우고 중지하려면 `close_background_transport=True`를 전달하거나 `close_shared_background_transports()`를 호출하세요.

    ```python
    # 이 플러그인의 테이블 및 자격 증명에 대한 공유 기록기를 비우고 중지합니다.
    await plugin.close(close_background_transport=True)

    # 또는 프로세스의 모든 공유 백그라운드 기록기를 비우고 중지합니다.
    await BigQueryAgentAnalyticsPlugin.close_shared_background_transports(timeout=10.0)
    ```

    ### 전송 및 중복 제거 {#delivery-and-deduplication}

    <div class="language-support-tag">
      <span class="lst-supported">ADK 지원 버전</span><span class="lst-python">Python v2.7.0</span><span class="lst-go">Go v0.1.0</span>
    </div>

    모든 행은 큐에 들어가기 전에 32자의 16진수 `event_id`를 받습니다. Storage Write API가 해당 행을 재시도할 때 동일한 ID가 재사용되므로 기본 전송 모드에서 중복 제거 키로 사용됩니다.

    ```sql
    SELECT *
    FROM `your-gcp-project-id.adk_agent_logs.agent_events`
    QUALIFY
      event_id IS NULL
      OR ROW_NUMBER() OVER (PARTITION BY event_id ORDER BY timestamp) = 1;
    ```

    `event_id IS NULL` 조건은 열이 도입되기 전에 작성된 행을 유지합니다.

    커밋된 스트림과 명시적 오프셋을 사용하려면 `exactly_once_delivery=True`(Go의 경우 `ExactlyOnceDelivery: true`)를 설정하세요. 이를 통해 첫 번째 결과가 모호했던 재시도가 해당 프로세서의 수명 내에서 중복을 생성하는 것을 방지할 수 있습니다. 스트림을 교체해야 하는 경우 추가 BigQuery `CreateWriteStream` 할당량을 소비할 수 있습니다.

    ```python
    config = BigQueryLoggerConfig(exactly_once_delivery=True)
    ```

    이름과 달리 이 옵션은 무손실 전송을 보장하지 않습니다. 재시도 소진, 오프셋 충돌 또는 교체 스트림 실패 후에도 일괄 처리가 드롭될 수 있습니다. 스트림 교체 실패 후 30초의 교체 백오프 중에 도착하는 이벤트도 드롭됩니다. `offset_conflict`(Go의 경우 `AppendFailureDrops`) 및 기타 [드롭 원인](#dropped-event-observability)을 모니터링하고 `event_id`를 소비자 중복 제거 키로 유지하세요.

    **Go**(`cfg.ExactlyOnceDelivery = true`)에서는 스트림 교체 및 재시도 분류가 Python과 약간 다릅니다:

    - `OutOfRange`, `NotFound` 또는 예상치 못한 `AlreadyExists`가 발생한 후, Go는 이전 배치에서 스트림이 교체되어 아직 커밋되지 않은 경우(이 경우 Go는 배치를 드롭하고 교체를 일시중지함)나 해당 배치의 이전 시도 결과가 알 수 없는 상태였던 경우(이 경우 `OutOfRange` 또는 `NotFound`는 중복을 방지하기 위해 배치를 드롭하고 다음 배치 전에 스트림을 교체함)가 아니라면 커밋된 스트림을 교체(배치당 최대 한 번)하고 동일한 추가(append) 작업 내에서 배치를 다시 전송합니다. Python은 세 가지 경우 모두 배치를 드롭하고 다음 배치 전에 스트림을 교체합니다.
    - 성공적인 `Send` 이후 RPC 수준 수신 오류가 발생할 때, Go는 `Unavailable`, `DeadlineExceeded`, `Canceled`, `Aborted`, `Internal`, `Unknown`을 알 수 없는 결과로 취급하는 반면, Python은 `ResourceExhausted`(`TooManyRequests`)도 알 수 없는 결과로 취급합니다.

    ### 테이블 준비 상태 콜백 {#table-readiness-callbacks}

    <div class="language-support-tag">
      <span class="lst-supported">ADK 지원 버전</span><span class="lst-python">Python v2.12.0</span>
    </div>

    플러그인이 설정 중에 실행하는 테이블 준비 상태 확인을 관찰하려면 `on_schema_error` 및 `on_schema_ready`를 사용하세요. 이 확인은 BigQuery 테이블을 읽거나 생성하거나 업그레이드하고 요청된 모든 뷰를 생성합니다.

    - `on_schema_error`: 확인 과정에서 테이블을 읽거나 생성하거나 업그레이드하는 데 실패할 때마다 예외와 함께 호출됩니다. 확인당 최대 한 번 실행되므로 설정 재시도 중에 반복적으로 호출될 수 있습니다. 뷰를 생성할 수 없거나 라벨 전용 테이블 새로고침이 실패하는 경우에는 호출되지 않습니다. 플러그인은 이러한 실패를 로그에 기록하고 계속 진행합니다.
    - `on_schema_ready`: 확인이 성공할 때마다 인수 없이 호출되며, 이는 테이블이 존재하거나 생성 또는 업그레이드되었고 요청된 모든 뷰가 생성되었음을 의미합니다.

    두 콜백 모두 이벤트 루프가 아닌 워커 스레드에서 실행되므로 빠르고 논블로킹 상태를 유지해야 합니다. 콜백에서 발생하는 예외는 로그에 기록되고 억제됩니다. 동기 콜러블이 아닌 값은 플러그인 생성 시 `ValueError`를 발생시킵니다.

    확인에 성공한 후 동일한 플러그인의 후속 설정에서는 `close()` 후, 포크 후, 그리고 나중에 피클된 복사본을 포함하여 이 확인을 건너뜁니다. 두 콜백 모두 다시 실행되지 않으며, 이후의 테이블 중단은 행이 기록될 때 [삭제된 행](#dropped-event-observability)으로만 나타납니다. 확인을 기다리던 설정이 취소되었거나 `create_analytics_views()` 호출이 뷰 생성에 실패한 경우에만 후속 설정에서 확인을 다시 실행합니다. 모든 뷰를 생성하는 `create_analytics_views()` 호출은 이후 설정에서 확인을 건너뛰게 만들며, 자체 뷰 생성은 두 콜백을 호출하지 않습니다.

    표준 `pickle` 모듈로 플러그인을 직렬화하는 경우 콜백은 모듈 수준 함수와 같이 피클 가능해야 합니다. 람다와 클로저는 `pickle`로 피클할 수 없으며 바인딩된 메서드는 인스턴스를 함께 피클합니다.

    ### 도구 결과 오류 분류 {#tool-result-error-classification}

    <div class="language-support-tag">
      <span class="lst-supported">ADK 지원 버전</span><span class="lst-python">Python v2.13.0</span>
    </div>

    많은 도구가 예외를 발생시키는 대신 구조화된 오류 페이로드를 반환합니다. ADK Python v2.13.0 이상에서는 `after_tool_callback`이 모든 도구 결과를 세 단계로 평가합니다:

    1. **`ReflectAndRetryToolPlugin` 오류 응답**(`response_type`으로 식별됨)은 항상 `error_details` 또는 `error_type`을 사용하여 `TOOL_ERROR`로 기록됩니다. 또한 도구가 `on_tool_error_callback`에서 이미 기록한 예외를 발생시킨 경우, 동일한 실패가 두 번 기록되지 않도록 이후 플러그인의 폴백 응답은 `after_tool_callback`에서 건너뜁니다. 발생하는 모든 오류를 직접 관찰할 수 있도록 `ReflectAndRetryToolPlugin`과 같은 재시도 플러그인보다 먼저 `BigQueryAgentAnalyticsPlugin`을 등록하세요.
    2. **커스텀 `tool_result_classifier`**: `BigQueryLoggerConfig`에 구성된 경우 플러그인은 `tool_result_classifier(tool=..., tool_args=..., tool_context=..., result=...)`를 호출합니다. 분류기는 동기식이어야 하며 `ToolResultClassification(status="ERROR" | "OK", error_message=...)` 또는 `None`을 반환해야 합니다:
       - `status="ERROR"`는 `status="ERROR"` 및 제공된 `error_message`(생략된 경우 고정된 기본 메시지)와 함께 호출을 `TOOL_ERROR`로 로깅합니다. 포맷되지 않은 오류 페이로드가 `content`에 작성되지 않도록 도구 결과 자체는 `TOOL_ERROR` 콘텐츠에서 생략됩니다. `content_formatter` 및 `payload_column_denylist`는 `error_message`에 적용되지 않으므로 해당 텍스트를 저장해도 괜찮은 경우에만 도구 출력을 `error_message`에 복사하세요.
       - `status="OK"`는 아래의 기본 제공 MCP 규칙이 오류로 표시했더라도 호출을 `TOOL_COMPLETED`로 로깅합니다.
       - `None`은 결정을 기본 제공 규칙에 맡깁니다.
    3. **기본 제공 MCP `isError` / `is_error` 규칙**: 최상위 `isError` 또는 `is_error`가 `True`인 모든 dict 결과 또는 MCP `CallToolResult` 모델은 고정 메시지 `"Tool returned an MCP result with isError=true."`와 함께 `TOOL_ERROR`로 기록됩니다.

    ```python
    from google.adk.plugins.bigquery_agent_analytics_plugin import (
        BigQueryLoggerConfig,
        ToolResultClassification,
    )

    def classify_tool_result(*, tool, tool_args, tool_context, result):
        if isinstance(result, dict) and result.get("status") == "ERROR":
            return ToolResultClassification(
                status="ERROR",
                error_message=result.get("error_code", "tool returned status=ERROR"),
            )
        return None  # Fall back to the built-in MCP isError / is_error check

    config = BigQueryLoggerConfig(
        tool_result_classifier=classify_tool_result,
    )
    ```

    ### 에이전트 평가 뷰 {#agent-evaluation-views}

    <div class="language-support-tag">
      <span class="lst-supported">ADK 지원 버전</span><span class="lst-python">Python v2.13.0</span>
    </div>

    `BigQueryLoggerConfig`에서 `create_eval_views=True`를 설정(또는 온디맨드로 `await plugin.create_eval_views()` 호출)하여 세션별 및 턴별 롤업 메트릭과 함께 `trace`(`JSON`) 열에 `google.cloud.aiplatform.v1beta1.AgentData` 평가 트레이스를 재구성하는 두 개의 뷰를 생성합니다:

    - **`{view_prefix}_eval_session`**(기본값 `v_eval_session`): 세션 수준 메트릭(`turn_count`, `tool_call_count`, `tool_error_count`, `llm_error_count`, `agent_error_count`, `has_error`, `has_truncated_content`, `has_tool_loop`, `max_consecutive_identical_tool_calls`, `distinct_tools_used`, `total_prompt_tokens`, `total_completion_tokens`, `total_tokens`, `total_latency_ms`, `eval_ready`) 및 멀티턴 `trace`가 포함된 `session_id`당 하나의 행.
    - **`{view_prefix}_eval_turn`**(기본값 `v_eval_turn`): `turn_index`, 턴 수준 메트릭(`turn_latency_ms`, 토큰 및 오류 수, `eval_ready`), 내부 `turn_index`가 `0`인 단일 턴 `trace`가 포함된 `(session_id, invocation_id)` 턴당 하나의 행.

    ADK Python v2.13.0에서 평가 뷰는 `content`(`payload_column_denylist`에 `"content"`를 넣으면 `ValueError`가 발생함)와 아래에 나열된 15개의 이벤트가 모두 필요합니다. `event_allowlist` / `event_denylist`에서 필수 이벤트를 필터링하여 제외하면 거부되며, 이 릴리스에는 대화 전용 평가 모드가 없습니다:

    - `USER_MESSAGE_RECEIVED`, `AGENT_STARTING`, `LLM_REQUEST`, `TOOL_STARTING`, `TOOL_COMPLETED`, `TOOL_PAUSED`, `AGENT_TRANSFER`, `HITL_CREDENTIAL_REQUEST`, `HITL_CONFIRMATION_REQUEST`, `HITL_INPUT_REQUEST`, `HITL_CREDENTIAL_REQUEST_COMPLETED`, `HITL_CONFIRMATION_REQUEST_COMPLETED`, `HITL_INPUT_REQUEST_COMPLETED`, `AGENT_RESPONSE`, `INVOCATION_COMPLETED`.

    뷰는 `session_id` / `invocation_id`별로 테이블 전체를 집계하므로 `session_start_timestamp` 또는 `turn_start_timestamp`로 필터링해도 기본 테이블의 `timestamp` 파티션이 프루닝(가지치기)되지 않습니다. 대규모 테이블의 경우 평가 작업을 실행하기 전에 날짜로 필터링된 슬라이스를 구체화(materialize)하세요.

=== "Go"

    Go(`google.golang.org/adk/plugin/agentanalytics`)에서는 세 가지 생성자 중 하나를 사용하여 플러그인을 생성할 수 있습니다:

    - **`agentanalytics.NewBigQueryAgentAnalyticsPlugin(ctx, projectID, datasetID, tableID)`**: `ProjectID`, `DatasetID`, `TableName`이 설정된 `agentanalytics.DefaultConfig()`를 사용합니다.
    - **`agentanalytics.NewBigQueryAgentAnalyticsPluginWithConfig(ctx, cfg)`**: 사용자 정의된 `agentanalytics.Config`를 사용합니다. 제로 초기화된 `agentanalytics.Config{}`는 `Enabled: false`를 가지며 아무 작업도 수행하지 않는 비활성화된 플러그인을 반환하므로, 항상 `cfg := agentanalytics.DefaultConfig()`에서 시작하거나 명시적으로 `Enabled: true`를 설정하세요.
    - **`agentanalytics.NewBigQueryAgentAnalyticsPluginWithClients(ctx, cfg, bqClient, writeClient)`**: 호출자가 제공한 `*bigquery.Client` 및 `*bqstorage.BigQueryWriteClient` 인스턴스를 사용합니다. `bqClient`가 nil이 아니고 `cfg.ProjectID`가 비어 있거나 `bigquery.DetectProjectID`인 경우 플러그인은 `bqClient.Project()`를 사용합니다. 사전 프로비저닝된 추가 전용(append-only) 배포를 위해 `bqClient == nil`을 전달하면 테이블 검사, 생성, 스키마 업그레이드 및 자동 뷰 생성을 건너뜁니다(이 모드에서는 `cfg.ProjectID`를 명시적으로 설정해야 하며, `bqPlugin.SyncViews`를 호출하면 `agentanalytics: BigQuery client is not configured for view creation`이 반환되므로 대신 `cfg.ViewDefinitions()`를 사용하여 각 뷰의 `Name`, `EventType`, `Query`를 가져오세요).

    #### `agentanalytics.Config` 필드

    | 필드 | 유형 | 기본값 (`DefaultConfig()`) | 사용 시점 |
    | --- | --- | --- | --- |
    | `Enabled` | `bool` | `true` | 플러그인을 활성화하거나 비활성화합니다. `DefaultConfig()` 없이 구조체 리터럴을 사용하는 경우 `Enabled: true`를 명시적으로 설정하세요. |
    | `ProjectID` | `string` | `""` (프로젝트 ID를 설정하거나 플러그인이 자체 클라이언트를 생성할 때 `bigquery.DetectProjectID` 사용; nil이 아닌 `bqClient`가 제공된 경우 빈 값은 `bqClient.Project()`를 사용하며, `bqClient`가 nil인 경우 명시적 프로젝트 ID 설정) | Google Cloud 프로젝트 선택 |
    | `DatasetID` | `string` | `"agent_analytics"` | BigQuery 데이터 세트 선택 |
    | `TableName` | `string` | `"agent_events"` | BigQuery 테이블 이름 선택 |
    | `MaxContentLen` | `int` | `500 * 1024` | 인라인 텍스트 값을 이 유니코드 코드 포인트(rune) 수로 자릅니다. `0`은 기본값(`500 * 1024` rune)을 사용하며 `-1`은 자르기를 비활성화합니다. |
    | `BatchSize` | `int` | `100` | 쓰기 배치당 큐에서 꺼내는 최대 행 수 |
    | `BatchFlushIntv` | `time.Duration` | `time.Second` | 부분 배치를 플러시하기 전 최대 간격 |
    | `QueueMaxSize` | `int` | `10000` | 새 이벤트가 드롭(`QueueFullDrops`)되기 전 인메모리 행 채널의 용량 |
    | `ClientOptions` | `[]option.ClientOption` | `nil` | BigQuery 및 Storage Write API 클라이언트를 위한 커스텀 Google Cloud 클라이언트 옵션(자격 증명, 엔드포인트) |
    | `ClusteringFields` | `[]string` | `[]string{"event_type", "agent", "user_id"}` | 테이블 생성 시 클러스터링 필드 사용자 정의(최대 4개 필드) |
    | `CustomTags` | `map[string]any` | `map[string]any{}` (`make(map[string]any)`) | 모든 행의 `attributes.custom_tags` 아래에 정적 키-값 태그 추가 |
    | `LogMultiModalContent` | `bool` | `true` | 사용자 메시지 및 모델 요청/응답에 대해 `content_parts` 채우기 |
    | `DisableMultiModalContent` | `bool` | `false` | `DefaultConfig()`에서 시작하더라도 `content_parts` 추출을 명시적으로 비활성화 |
    | `ShutdownTimeout` | `time.Duration` | `10 * time.Second` | 각 백그라운드 배치 쓰기(재시도 포함), 실행 종료 시 플러시, 그리고 `Close()`가 큐를 드레인할 때의 BigQuery 쓰기를 제한합니다. 이는 `Close()`에 대한 단일 월클럭(wall-clock) 제한이 아니며, GCS 업로드 및 뷰 생성이 포함되면 `Close()`에 눈에 띄게 더 오랜 시간(최대 약 2.5배의 `ShutdownTimeout`)이 걸릴 수 있습니다. |
    | `Logger` | `agentanalytics.Logger` | `log.Default()` | 경고 및 오류 진단(백그라운드 뷰 생성 실패 포함)을 위해 `Printf(format string, v ...any)`와 `Println(v ...any)`를 모두 구현하는 커스텀 로거 |
    | `RetryConfig` | `agentanalytics.RetryConfig` | `MaxRetries: 3`, `InitialDelay: 100ms`, `MaxDelay: 10s`, `Multiplier: 2.0` | 재시도 가능한 Storage Write API 추가 오류에 대한 지수 백오프 조정 |
    | `DisableSessionMetadata` | `bool` | `false` | `attributes.session_metadata`(`session_id`, `app_name`, `user_id`, `state`) 생략 |
    | `CaptureFullMessageContent` | `bool` | `false` | 텍스트 페이로드의 길이 자르기 비활성화(`MaxContentLen`은 무시되며 민감한 키 수정은 계속 실행됨) |
    | `DisableSensitiveKeyRedaction` | `bool` | `false` | 자동 민감한 키, `temp:` 값, URI, 헤더 및 자격 증명 패턴 수정을 해제합니다. 이 옵션은 `state_delta`의 최상위 소문자 `temp:` 항목을 유지하지 않으며, 해당 항목은 여전히 제거되고 `temp:`만 있는 `STATE_DELTA` 행도 여전히 억제됩니다. |
    | `ContentFormatter` | `agentanalytics.ContentFormatter` | `nil` | 직렬화 전에 적용되는 커스텀 `func(payload any, eventType string) (any, error)` |
    | `DebugContentFormatterErrors` | `bool` | `false` | `ContentFormatter`가 실패할 때 원시 오류 텍스트를 로깅하지 않고 로컬 경고 로그에 오류 형태 메타데이터(예: 바이트 길이) 포함 |
    | `EventAllowlist` | `[]string` | `nil` | 나열된 이벤트 유형만 로깅(세션 이벤트 행의 별칭으로 `"EVENT"` 지원) |
    | `EventDenylist` | `[]string` | `nil` | 나열된 이벤트 유형 건너뛰기 |
    | `PayloadColumnDenylist` | `[]string` | `nil` | 테이블 스키마, 작성된 행 및 뷰에서 선택한 페이로드 열(`"content"`, `"content_parts"`, `"attributes"`, `"latency_ms"`) 생략 |
    | `CustomMetadataAllowlist` | `[]string` | `nil` | `session.Event.CustomMetadata` 및 최종 `model.LLMResponse.CustomMetadata`에서 일치하는 키(정확한 키 또는 `"prefix*"`)를 `attributes.custom_metadata`로 캡처합니다. 또한 `AGENT_STATE_CHECKPOINT` 방출(`"adk_agent_state"` / `"agent_state"` 또는 `"end_of_agent"` / `"adk_end_of_agent"`와 같은 체크포인트 키가 일치할 때) 및 `CustomMetadata`로 전달되는 `"adk_compaction"`도 제어합니다. |
    | `FinalResponseToolNames` | `[]string` | `nil` | 나열된 도구가 완료될 때 `attributes.source_tool`과 함께 추가 `AGENT_RESPONSE` 행 방출 |
    | `DisableFlushOnRunEnd` | `bool` | `false` | 각 `AfterRun` 콜백이 끝날 때 배치 큐가 플러시될 때까지 대기하지 않음 |
    | `DisableSchemaUpgrade` | `bool` | `false` | 기존 테이블에 대한 자동 추가 전용 스키마 업그레이드 비활성화 |
    | `EnableOTelCorrelation` | `bool` | `false` | `attributes.otel` 아래에 주변 OpenTelemetry `span_id` 및 `trace_id` 캡처 |
    | `GCSBucketName` | `string` | `""` | `MaxInlineTextSize`보다 큰 인라인 텍스트와 바이너리 블롭을 이 GCS 버킷으로 오프로드 |
    | `GCSClientOptions` | `[]option.ClientOption` | `nil` | 기본 GCS 클라이언트를 위한 커스텀 클라이언트 옵션(비어 있으면 `ClientOptions`로 폴백) |
    | `GCSPathPrefix` | `string` | `""` | 오프로드된 GCS 경로 앞에 추가되는 선택적 객체 이름 접두사 |
    | `ConnectionID` | `string` | `""` | 객체 테이블 / 서명된 URL을 위해 `object_ref.authorizer`로 저장되는 BigQuery 연결 ID(`"location.connection_id"`) |
    | `MaxInlineTextSize` | `int` | `32 * 1024` | 오프로딩이 구성된 경우 텍스트 파트가 GCS로 오프로드되는 바이트 임계값(기본값 `32 KiB`) |
    | `GCSMaxConcurrentUploads` | `int` | `8` | 배치 플러시 중 최대 동시 GCS 업로드 수 |
    | `GCSUploadTimeout` | `time.Duration` | `10 * time.Second` | 해당 배치의 동시 GCS 업로드에 대한 배치당 데드라인. 시간이 초과되면 완료되지 않은 파트는 폴백되고 동일한 시간 동안 오프로딩이 일시중지됩니다. |
    | `GCSMaxPendingUploadBytes` | `int64` | `256 * 1024 * 1024` | 버퍼링된 행 전체에서 GCS 업로드를 위해 대기 중인 텍스트 및 바이너리 페이로드 바이트의 메모리 상한(기본값 `256 MiB`) |
    | `GCSOffloader` | `agentanalytics.GCSContentOffloader` | `nil` | 커스텀 오프로더 구현(`GCSBucketName`으로 생성된 기본 GCS 클라이언트를 재정의함) |
    | `DisableCreateViews` | `bool` | `false` | 25개의 이벤트 유형별 BigQuery 뷰(`v_<event_type>`)의 자동 백그라운드 생성 비활성화 |
    | `ViewPrefix` | `string` | `"v"` | 이벤트 유형별 뷰 이름의 접두사(`<ViewPrefix>_<event_type>`) |
    | `ExactlyOnceDelivery` | `bool` | `false` | 기본 스트림 대신 명시적 배치 오프셋이 있는 `COMMITTED` Storage Write 스트림을 통해 쓰기 |

    Go에서 `ContentFormatter`는 원시 타입이 지정된 콘텐츠 페이로드를 받습니다: 정적 `AGENT_STARTING` 지침의 경우 문자열, `USER_MESSAGE_RECEIVED`의 경우 `*genai.Content`, `LLM_REQUEST`의 경우 `*model.LLMRequest`, `LLM_RESPONSE`의 경우 `*model.LLMResponse`, 그리고 도구 및 기타 맵 형태 이벤트의 경우 맵을 받습니다. `NODE_OUTPUT` 및 `A2A_INTERACTION`은 슬라이스나 스칼라일 수도 있는 원래 출력/응답 값을 그대로 전달합니다. 속성은 변환하지 않습니다. 특히 `STATE_DELTA`는 페이로드를 `attributes.state_delta`에 저장하며 `ContentFormatter`를 호출하지 않습니다. 수정하는 모든 포인터, 슬라이스 또는 맵(`*genai.Content` 내부의 `Part.Text`, `Part.ExecutableCode.Code`, `Part.CodeExecutionResult.Output`, `Part.FunctionCall.Args`, `Part.FunctionResponse.Response` 포함)을 복제(clone)하고 라이브 페이로드를 직접 변경하지 마세요.

    아래 헬퍼는 편집하는 값을 복제하고 중첩 수준이 50을 넘으면 중지합니다. 과도하게 중첩되었거나 순환하는 페이로드는 오류를 반환하므로 플러그인은 프로세스 충돌 위험을 감수하는 대신 `[FORMATTER_FAILED]`를 기록합니다. 이러한 헬퍼는 JSON 형태의 `map[string]any` 및 `[]any` 값(및 `[]string`, `map[string]string`, `[]map[string]any`)을 재귀적으로 순회합니다. 도구가 반환하는 다른 구체적인 타입에 대해 제한된 케이스를 추가하거나 포맷팅 전에 해당 값을 정규화하고, 이 수정 로직에 의존하기 전에 실제 페이로드를 테스트하세요:

    ```go title="analytics.go"
    package analytics

    import (
    	"context"
    	"fmt"
    	"regexp"
    	"time"

    	"google.golang.org/adk/plugin/agentanalytics"
    	"google.golang.org/adk/v2/model"
    	"google.golang.org/genai"
    )

    var dollarPattern = regexp.MustCompile(`\$\d+(?:,\d{3})*(?:\.\d+)?`)

    func maskContent(c *genai.Content, eventType string, depth int) (*genai.Content, error) {
    	if depth >= 50 {
    		return nil, fmt.Errorf("redaction nesting limit exceeded")
    	}
    	if c == nil {
    		return nil, nil
    	}
    	cloned := *c
    	if len(c.Parts) > 0 {
    		cloned.Parts = make([]*genai.Part, len(c.Parts))
    		for i, p := range c.Parts {
    			if p == nil {
    				continue
    			}
    			partCopy := *p
    			if partCopy.Text != "" {
    				partCopy.Text = dollarPattern.ReplaceAllString(partCopy.Text, "xxx")
    			}
    			if partCopy.ExecutableCode != nil {
    				codeCopy := *partCopy.ExecutableCode
    				codeCopy.Code = dollarPattern.ReplaceAllString(codeCopy.Code, "xxx")
    				partCopy.ExecutableCode = &codeCopy
    			}
    			if partCopy.CodeExecutionResult != nil {
    				resultCopy := *partCopy.CodeExecutionResult
    				resultCopy.Output = dollarPattern.ReplaceAllString(resultCopy.Output, "xxx")
    				partCopy.CodeExecutionResult = &resultCopy
    			}
    			if partCopy.FunctionCall != nil {
    				fcCopy := *partCopy.FunctionCall
    				if fcCopy.Args != nil {
    					redactedArgs, err := redactDollarAmountsAtDepth(fcCopy.Args, eventType, depth+1)
    					if err != nil {
    						return nil, err
    					}
    					if argsMap, ok := redactedArgs.(map[string]any); ok {
    						fcCopy.Args = argsMap
    					}
    				}
    				partCopy.FunctionCall = &fcCopy
    			}
    			if partCopy.FunctionResponse != nil {
    				frCopy := *partCopy.FunctionResponse
    				if frCopy.Response != nil {
    					redactedResp, err := redactDollarAmountsAtDepth(frCopy.Response, eventType, depth+1)
    					if err != nil {
    						return nil, err
    					}
    					if respMap, ok := redactedResp.(map[string]any); ok {
    						frCopy.Response = respMap
    					}
    				}
    				partCopy.FunctionResponse = &frCopy
    			}
    			cloned.Parts[i] = &partCopy
    		}
    	}
    	return &cloned, nil
    }

    func redactDollarAmounts(payload any, eventType string) (any, error) {
    	return redactDollarAmountsAtDepth(payload, eventType, 0)
    }

    func redactDollarAmountsAtDepth(payload any, eventType string, depth int) (any, error) {
    	if depth >= 50 {
    		return nil, fmt.Errorf("redaction nesting limit exceeded")
    	}
    	switch v := payload.(type) {
    	case string:
    		return dollarPattern.ReplaceAllString(v, "xxx"), nil
    	case *genai.Content:
    		return maskContent(v, eventType, depth+1)
    	case *model.LLMRequest:
    		if v == nil {
    			return nil, nil
    		}
    		cloned := *v
    		if len(v.Contents) > 0 {
    			cloned.Contents = make([]*genai.Content, len(v.Contents))
    			for i, c := range v.Contents {
    				masked, err := maskContent(c, eventType, depth+1)
    				if err != nil {
    					return nil, err
    				}
    				cloned.Contents[i] = masked
    			}
    		}
    		if v.Config != nil && v.Config.SystemInstruction != nil {
    			maskedSys, err := maskContent(v.Config.SystemInstruction, eventType, depth+1)
    			if err != nil {
    				return nil, err
    			}
    			cfgCopy := *v.Config
    			cfgCopy.SystemInstruction = maskedSys
    			cloned.Config = &cfgCopy
    		}
    		return &cloned, nil
    	case *model.LLMResponse:
    		if v == nil {
    			return nil, nil
    		}
    		maskedContent, err := maskContent(v.Content, eventType, depth+1)
    		if err != nil {
    			return nil, err
    		}
    		cloned := *v
    		cloned.Content = maskedContent
    		return &cloned, nil
    	case map[string]any:
    		if v == nil {
    			return map[string]any(nil), nil
    		}
    		cloned := make(map[string]any, len(v))
    		for k, val := range v {
    			redacted, err := redactDollarAmountsAtDepth(val, eventType, depth+1)
    			if err != nil {
    				return nil, err
    			}
    			cloned[k] = redacted
    		}
    		return cloned, nil
    	case map[string]string:
    		if v == nil {
    			return map[string]string(nil), nil
    		}
    		cloned := make(map[string]string, len(v))
    		for k, val := range v {
    			redacted, err := redactDollarAmountsAtDepth(val, eventType, depth+1)
    			if err != nil {
    				return nil, err
    			}
    			cloned[k], _ = redacted.(string)
    		}
    		return cloned, nil
    	case []any:
    		if v == nil {
    			return []any(nil), nil
    		}
    		cloned := make([]any, len(v))
    		for i, item := range v {
    			redacted, err := redactDollarAmountsAtDepth(item, eventType, depth+1)
    			if err != nil {
    				return nil, err
    			}
    			cloned[i] = redacted
    		}
    		return cloned, nil
    	case []string:
    		if v == nil {
    			return []string(nil), nil
    		}
    		cloned := make([]string, len(v))
    		for i, item := range v {
    			redacted, err := redactDollarAmountsAtDepth(item, eventType, depth+1)
    			if err != nil {
    				return nil, err
    			}
    			cloned[i], _ = redacted.(string)
    		}
    		return cloned, nil
    	case []map[string]any:
    		if v == nil {
    			return []map[string]any(nil), nil
    		}
    		cloned := make([]map[string]any, len(v))
    		for i, item := range v {
    			redacted, err := redactDollarAmountsAtDepth(item, eventType, depth+1)
    			if err != nil {
    				return nil, err
    			}
    			cloned[i], _ = redacted.(map[string]any)
    		}
    		return cloned, nil
    	default:
    		return payload, nil
    	}
    }

    func CreatePlugin(ctx context.Context) (*agentanalytics.BigQueryAgentAnalyticsPlugin, error) {
    	cfg := agentanalytics.DefaultConfig()
    	cfg.ProjectID = "my-project"
    	cfg.DatasetID = "my_dataset"
    	cfg.TableName = "agent_events"
    	cfg.EventAllowlist = []string{
    		agentanalytics.EventUserMessageReceived,
    		agentanalytics.EventLLMRequest,
    		agentanalytics.EventLLMResponse,
    	}
    	cfg.ShutdownTimeout = 10 * time.Second
    	cfg.MaxContentLen = 500 * 1024
    	cfg.ContentFormatter = redactDollarAmounts
    	cfg.EnableOTelCorrelation = true
    	cfg.CustomMetadataAllowlist = []string{"ticket_id", "exp:*"}
    	cfg.ExactlyOnceDelivery = true

    	adkPlugin, err := agentanalytics.NewBigQueryAgentAnalyticsPluginWithConfig(ctx, cfg)
    	if err != nil {
    		return nil, err
    	}
    	bqPlugin, ok := agentanalytics.AsBigQueryAgentAnalyticsPlugin(adkPlugin)
    	if !ok {
    		return nil, fmt.Errorf("unexpected plugin wrapper")
    	}
    	return bqPlugin, nil
    }
    ```

=== "Java"

    Java에서는 모든 구성이 `BigQueryLoggerConfig` 빌더를 통해 관리됩니다.

    #### BigQueryLoggerConfig Builder 옵션

    | 빌더 메서드 | 유형 | 기본값 | 설명 |
    | --- | --- | --- | --- |
    | `enabled(boolean)` | `boolean` | `true` | 로깅 임시 비활성화 |
    | `projectId(String)` | `String` | *(필수)* | Google Cloud 프로젝트 선택 |
    | `datasetId(String)` | `String` | *(필수)* | BigQuery 데이터 세트 선택 |
    | `tableName(String)` | `String` | `"agent_events"` | 커스텀 테이블 이름 사용 |
    | `location(String)` | `String` | `"us"` | BigQuery 데이터 세트 위치와 일치 |
    | `clusteringFields(List<String>)` | `List<String>` | `["event_type", "agent", "user_id"]` | 생성 시 테이블 클러스터링 사용자 정의 |
    | `gcsBucketName(String)` | `String` | `""` | 대용량 텍스트 및 멀티모달 콘텐츠를 GCS로 오프로드 |
    | `connectionId(String)` | `String` | `null` | BigQuery ObjectRef / 객체 테이블 사용 |
    | `maxContentLength(int)` | `int` | `500 * 1024` | 오프로드/자르기 전 인라인 페이로드 크기 제어 |
    | `batchSize(int)` | `int` | `1` | 쓰기 처리량 대 지연 시간 조정 |
    | `batchFlushInterval(Duration)` | `Duration` | `Duration.ofSeconds(1)` | 부분 일괄 처리를 주기적으로 플러시 |
    | `shutdownTimeout(Duration)` | `Duration` | `Duration.ofSeconds(10)` | 종료 시 최종 플러시 대기 시간 |
    | `eventAllowlist(List<String>)` | `List<String>` | `[]` | 선택한 이벤트 유형만 로깅 |
    | `eventDenylist(List<String>)` | `List<String>` | `[]` | 민감하거나 불필요한 이벤트 유형 건너뛰기 |
    | `contentFormatter(BiFunction)` | `BiFunction<Object, String, Object>` | `null` | 이벤트별 커스텀 마스킹/포맷팅 적용 |
    | `logMultiModalContent(boolean)` | `boolean` | `true` | GCS 참조를 포함한 `content_parts` 세부정보 캡처 |
    | `queueMaxSize(int)` | `int` | `10000` | 인메모리 이벤트 대기열 제한 |
    | `retryConfig(RetryConfig)` | `RetryConfig` | `RetryConfig.builder().build()` | 재시도 동작 조정 |
    | `logSessionMetadata(boolean)` | `boolean` | `true` | `attributes`에 세션 정보 추가 |
    | `customTags(Map<String, Object>)` | `Map<String, Object>` | `{}` | 모든 이벤트의 `attributes`에 정적 태그 추가 |
    | `autoSchemaUpgrade(boolean)` | `boolean` | `true` | 기존 테이블에 새 열 자동 추가 |
    | `createViews(boolean)` | `boolean` | `false` | 이벤트 유형별 BigQuery 뷰 생성(참고: Python의 `true`와 달리 기본값은 `false`임) |
    | `viewPrefix(String)` | `String` | `"v"` | 뷰 이름 충돌 방지 |
    | `credentials(Credentials)` | `Credentials` | `null` | 명시적 서비스 계정 사용자 인증 정보 사용 |

    Java v1.8.0 이상에서는 `datasetId`가 필수이며 `tableName`의 기본값은 `"agent_events"`입니다. Java v1.7.0 이전 버전에서는 이러한 기본값이 각각 `"agent_analytics"` 및 `"events"`였습니다.

    다음 코드 샘플은 Java에서 BigQuery Agent Analytics 플러그인 구성을 정의하는 방법을 보여줍니다.

    ```java
    import com.google.adk.plugins.agentanalytics.BigQueryAgentAnalyticsPlugin;
    import com.google.adk.plugins.agentanalytics.BigQueryLoggerConfig;
    import java.time.Duration;
    import java.util.function.BiFunction;

    // 달러 금액을 수정하는 커스텀 포맷터
    BiFunction<Object, String, Object> redactDollarAmounts = (content, eventType) -> {
      String textContent = content.toString();
      return textContent.replaceAll("\$\d+(?:,\d{3})*(?:\.\d+)?", "xxx");
    };

    BigQueryLoggerConfig config = BigQueryLoggerConfig.builder()
        .enabled(true)
        .projectId("my-project")
        .datasetId("my_dataset")
        .tableName("agent_events")
        .batchSize(1)
        .batchFlushInterval(Duration.ofMillis(500))
        .contentFormatter(redactDollarAmounts)
        .autoSchemaUpgrade(true)
        .createViews(true)
        .build();

    BigQueryAgentAnalyticsPlugin plugin = new BigQueryAgentAnalyticsPlugin(config);
    ```

=== "Kotlin"

    Kotlin에서는 모든 구성이 플러그인의 유일한 필수 인수로 사용되는 `BigQueryLoggerConfig` 데이터 클래스를 통해 관리됩니다.

    #### BigQueryLoggerConfig 속성

    | 옵션 | 유형 | 기본값 | 사용 시점 |
    | --- | --- | --- | --- |
    | `projectId` | `String` | *(필수)* | Google Cloud 프로젝트 선택 |
    | `datasetId` | `String` | *(필수)* | BigQuery 데이터 세트 선택 |
    | `enabled` | `Boolean` | `true` | 로깅 임시 비활성화 |
    | `location` | `String` | `"US"` | BigQuery 데이터 세트 위치와 일치(예: `"EU"` 또는 `"us-central1"`) |
    | `tableName` | `String` | `"agent_events"` | 커스텀 테이블 이름 사용 |
    | `credentials` | `Credentials?` | `null` | [ADC](https://cloud.google.com/docs/authentication/application-default-credentials) 대신 명시적 서비스 계정 사용자 인증 정보 사용 |

    다음 코드 샘플은 Kotlin에서 BigQuery Agent Analytics 플러그인 구성을 정의하는 방법을 보여줍니다.

    ```kotlin
    import com.google.adk.kt.plugins.agentanalytics.BigQueryAgentAnalyticsPlugin
    import com.google.adk.kt.plugins.agentanalytics.BigQueryLoggerConfig

    val config =
        BigQueryLoggerConfig(
            projectId = "my-project",
            datasetId = "my_dataset",
            location = "EU",
            tableName = "agent_events",
        )

    val plugin = BigQueryAgentAnalyticsPlugin(config = config)
    ```

    일괄 처리, 콘텐츠 포맷팅, 이벤트 허용 목록, GCS 오프로딩, 뷰 생성 등 **Python**, **Go** 및 **Java** 탭 아래에 나열된 옵션은 Kotlin에 존재하지 않습니다.

## 스키마 및 프로덕션 설정

### 스키마 참조

이벤트 테이블(`agent_events`)은 유연한 스키마를 사용합니다. 다음 표는 예시 값과 함께 포괄적인 참조를 제공합니다.

| 필드 이름 | 유형 | 모드 | 설명 | 예시 값 |
| --- | --- | --- | --- | --- |
| **timestamp** | `TIMESTAMP` | `REQUIRED` | 이벤트 생성의 UTC 타임스탬프입니다. 기본 정렬 키이자 일별 파티셔닝 키 역할을 합니다. 정밀도는 마이크로초입니다. | `2026-02-03 20:52:17 UTC` |
| **event_id** | `STRING` | `NULLABLE` | 대기열 진입 전에 할당된 32자의 16진수 ID(Python 및 Go)입니다. Storage Write API 재시도 시에도 유지되므로 소비자가 중복 행을 식별할 수 있습니다. 스키마 버전 2 이전에 작성된 행은 `NULL`입니다. | `ca5e3c9d99e24e46b614f2f44f93bf6e` |
| **event_type** | `STRING` | `NULLABLE` | 표준 이벤트 카테고리입니다. 표준 값에는 [이벤트 유형 및 페이로드](#event-types)에 설명된 LLM, 도구, 에이전트, 호출, 상태, HITL, A2A, 응답, 워크플로, 노드 출력 및 노드 오류 이벤트가 포함됩니다. 상위 수준 필터링에 사용됩니다. | `LLM_REQUEST` |
| **agent** | `STRING` | `NULLABLE` | 이 이벤트를 담당하는 에이전트의 이름입니다. 에이전트 초기화 중 또는 `root_agent_name` 컨텍스트를 통해 정의됩니다. | `my_bq_agent` |
| **session_id** | `STRING` | `NULLABLE` | 전체 대화 스레드에 대한 영구 식별자입니다. 여러 턴과 하위 에이전트 호출 간에 일정하게 유지됩니다. | `04275a01-1649-4a30-b6a7-5b443c69a7bc` |
| **invocation_id** | `STRING` | `NULLABLE` | 세션 내의 각 개별 에이전트 실행 또는 턴에 대한 고유 식별자입니다. | `81014e7a-90da-4cb0-adbf-cb6d53955685` |
| **user_id** | `STRING` | `NULLABLE` | 현재 세션과 연결된 사용자의 식별자입니다. 사용자별 분석에 유용합니다. | `user_12345` |
| **trace_id** | `STRING` | `NULLABLE` | 트레이스 식별자입니다. 주변 span(예: Agent Engine의 호출 span 또는 ADK Runner span)에서 상속된 경우 32자 16진수 OpenTelemetry 트레이스 ID이므로 BigQuery 행이 기존 Cloud Trace 트레이스와 깔끔하게 조인됩니다. 주변 span이 없으면 Python은 무작위 32자 16진수 폴백을 생성합니다. 주변 span이 없을 때 Go는 `invocation_id`가 비어 있으면 무작위 32자 16진수 `trace_id`를 생성하고, 그렇지 않으면 플러그인당 무작위 시드와 호출 ID에 대해 SHA-256을 사용하여 해당 플러그인 인스턴스 내에서 안정적인 32자 16진수 ID를 생성합니다. Java는 ADK 호출 ID로 폴백합니다. 단일 분산 요청 수명 주기 내의 모든 작업을 연결합니다. | `4bf92f3577b34da6a3ce929d0e0e4736` |
| **span_id** | `STRING` | `NULLABLE` | 이 특정 원자적 작업을 식별하는 16자 16진수 Span ID입니다. **OTel span으로 내보내지지 않고 플러그인의 내부 스택에서 추적됩니다.** 플러그인은 구성된 OpenTelemetry provider에 대해 `tracer.start_span`을 호출하지 않습니다. Python 및 Java에서는 주변 OTel span이 활성화되어 있을 때 루트 호출 span이 해당 ID를 재사용하며, Go에서는 플러그인이 항상 자체 16자 16진수 루트 `span_id`를 생성하고 주변 OTel span ID를 `parent_span_id`에 기록합니다. 하위 span은 내부적으로 생성됩니다([추적 및 관측 가능성](#tracing-and-observability) 참조). | `00f067aa0ba902b7` |
| **parent_span_id** | `STRING` | `NULLABLE` | 직전 호출자의 Span ID로, 부모-자식 실행 트리(DAG)를 재구성하는 데 사용됩니다. | `5fb397be34d23b0f` |
| **content** | `JSON` | `NULLABLE` | JSON으로 저장된 이벤트별 데이터(페이로드)입니다. 구조는 이벤트 유형에 따라 다릅니다. | `{"model": "gemini-flash-latest", ...}` |
| **content_parts** | `ARRAY<STRUCT>` | `REPEATED` | 구조화된 파트의 배열입니다. 텍스트 청크, GCS에 저장된 파일에 대한 URI/ObjectRef(스토리지 오프로딩용), MIME 유형 및 파트 메타데이터를 캡처합니다. | `[{mime_type: "image/png", uri: "gs://..."}]` |
| **attributes** | `JSON` | `NULLABLE` | 추가 메타데이터(예: `root_agent_name`, `model_version`, `usage_metadata`, `session_metadata`, `custom_tags`)를 위한 임의의 키-값 쌍입니다. | `{"model_version": "gemini-flash-latest", ...}` |
| **latency_ms** | `JSON` | `NULLABLE` | 지연 시간 측정값(예: 총 소요 시간인 `total_ms`)입니다. | `{"total_ms": 1250}` |
| **status** | `STRING` | `NULLABLE` | 이벤트의 결과로, 일반적으로 'OK' 또는 'ERROR'입니다. | `OK` |
| **error_message** | `STRING` | `NULLABLE` | 예외 및 모델 종료 세부정보에 대한 정제된 진단 메시지입니다. Python 및 Go에서는 최종 `LLM_RESPONSE` 또는 커스텀 `content_formatter` / `ContentFormatter`가 실패한 행(예: `content_formatter raised ImportError` 또는 `content_formatter panicked`)과 같이 `status`가 `OK`로 유지되는 행에 채워질 수 있습니다. | `Error 404: Dataset not found` |
| **is_truncated** | `BOOLEAN` | `NULLABLE` | 구성된 `max_content_length`(Go의 경우 `MaxContentLen`), 정제기 깊이 또는 노드 예산, 진단 텍스트 정제를 포함하여 콘텐츠나 메타데이터가 안전 경계에 의해 잘리거나 대체된 경우 `true`입니다. ADK Python v2.12.0 이상에서는 모델 응답의 포맷팅된 파트에서 일반적인 자격 증명 패턴이 수정(redact)된 경우 및 응답 또는 컴팩션 콘텐츠의 기본 포맷팅 실패 시 기록되는 플레이스홀더인 `[FORMATTING FAILED]`에 의해서도 설정됩니다(커스텀 `content_formatter` 실패를 나타내는 `[FORMATTER_FAILED]`와 혼동하지 마세요). 일반적인 구조화된 민감한 키 수정은 단독으로 이 값을 설정하지 않습니다. | `false` |

Python 및 Go에서 `event_id` 열은 스키마 버전 2의 일부입니다. Python의 `auto_schema_upgrade=True`(또는 Go의 `DisableSchemaUpgrade: false`, 둘 다 기본값)를 사용하면 플러그인이 기존 테이블에 이 열을 자동으로 추가합니다. 테이블 스키마를 직접 관리하는 경우 ADK Python v2.7.0+ 또는 ADK Go를 사용하기 전에 해당 열을 추가하세요.

Java 스키마에는 `event_id`가 포함되지 않습니다. 아래의 수동 DDL로 생성된 테이블은 해당 열이 nullable이므로 Java와 계속 호환됩니다.

??? example "프로덕션 BigQuery DDL (수동 생성용)"

    플러그인이 자동으로 테이블을 생성하도록 허용하는 대신, 프로덕션 환경에 맞게 커스텀 파티셔닝, 클러스터링 및 열 수준 보안을 적용하여 테이블을 미리 프로비저닝할 수 있습니다.

    ```sql
    CREATE TABLE IF NOT EXISTS `your-gcp-project-id.your-big-query-dataset-id.agent_events`
    (
      timestamp TIMESTAMP OPTIONS(description="UTC timestamp of event creation. Acts as the primary ordering key and the daily partitioning key."),
      event_id STRING OPTIONS(description="32-char hex ID assigned before enqueue; preserved across Storage Write API retries for consumer deduplication."),
      event_type STRING OPTIONS(description="The canonical category of the event."),
      agent STRING OPTIONS(description="The name of the agent responsible for this event."),
      session_id STRING OPTIONS(description="A persistent identifier for the entire conversation thread."),
      invocation_id STRING OPTIONS(description="A unique identifier for each individual agent execution or turn within a session."),
      user_id STRING OPTIONS(description="The identifier of the user associated with the current session."),
      trace_id STRING OPTIONS(description="32-char hex trace ID. Inherited from the ambient OpenTelemetry span when one is active; otherwise generated per invocation by the plugin."),
      span_id STRING OPTIONS(description="16-char hex span ID for this specific operation. Tracked on the plugin's internal stack; the root invocation span may reuse the ambient OTel span id, while child BQAA spans are generated internally. No OpenTelemetry span is created or exported."),
      parent_span_id STRING OPTIONS(description="16-char hex span ID of the immediate caller, used to reconstruct the parent-child execution tree."),
      content JSON OPTIONS(description="The event-specific data (payload) stored as JSON."),
      content_parts ARRAY<STRUCT<
        mime_type STRING,
        uri STRING,
        object_ref STRUCT<
          uri STRING,
          version STRING,
          authorizer STRING,
          details JSON
        >,
        text STRING,
        part_index INT64,
        part_attributes STRING,
        storage_mode STRING
      >> OPTIONS(description="Detailed content parts for multi-modal data."),
      attributes JSON OPTIONS(description="Arbitrary key-value pairs for additional metadata (e.g., 'root_agent_name', 'model_version', 'usage_metadata', 'session_metadata', 'custom_tags')."),
      latency_ms JSON OPTIONS(description="Latency measurements (e.g., total_ms)."),
      status STRING OPTIONS(description="The outcome of the event, typically 'OK' or 'ERROR'."),
      error_message STRING OPTIONS(description="Diagnostic message for errors and model termination details; may be populated on rows whose status is 'OK', such as LLM_RESPONSE rows and rows whose content_formatter failed."),
      is_truncated BOOLEAN OPTIONS(description="Flag indicates if content was truncated.")
    )
    PARTITION BY DATE(timestamp)
    CLUSTER BY event_type, agent, user_id;
    ```

### 자동으로 생성되는 뷰

<div class="language-support-tag">
  <span class="lst-supported">ADK 지원 버전</span><span class="lst-python">Python v1.27.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v1.5.0</span>
</div>

Python(`create_views=True`) 및 Go(`DisableCreateViews: false`)에서 플러그인은 기본적으로 각 이벤트 유형에 대한 뷰를 자동으로 생성합니다. Java에서는 `createViews(true)`를 설정해야 합니다(기본값은 `false`). Kotlin은 뷰를 생성하지 않습니다. 뷰는 공통 JSON 구조를 평면화된 형식의 유형이 지정된 열로 변환하므로 반복적인 `JSON_VALUE` 및 `JSON_QUERY` 표현식을 피할 수 있습니다.

뷰 이름은 `{view_prefix}_{event_type_lowercase}` 규칙을 따릅니다(예: 기본 접두사 `"v"`를 사용할 경우 `LLM_REQUEST`는 `v_llm_request`가 됨). 여러 플러그인 인스턴스가 동일한 데이터 세트의 서로 다른 테이블에 쓸 때 뷰 이름 충돌을 방지하려면 `BigQueryLoggerConfig`에서 `view_prefix`(Go의 `agentanalytics.Config`에서는 `ViewPrefix`)를 고유한 값으로 설정하세요.

```python
# 동일한 데이터 세트에서 서로 다른 뷰 접두사를 사용하는 두 개의 플러그인
plugin_prod = BigQueryAgentAnalyticsPlugin(
    project_id=PROJECT_ID, dataset_id=DATASET_ID,
    table_id="agent_events_prod",
    config=BigQueryLoggerConfig(view_prefix="v_prod"),
)
# 생성되는 뷰: v_prod_llm_request, v_prod_tool_completed, ...

plugin_staging = BigQueryAgentAnalyticsPlugin(
    project_id=PROJECT_ID, dataset_id=DATASET_ID,
    table_id="agent_events_staging",
    config=BigQueryLoggerConfig(view_prefix="v_staging"),
)
# 생성되는 뷰: v_staging_llm_request, v_staging_tool_completed, ...
```

온디맨드로 뷰를 새로고침할 수도 있습니다:

- **Python**: `await plugin.create_analytics_views()`를 호출합니다(Python v2.13.0+에서 [에이전트 평가 뷰](#agent-evaluation-views)의 경우 `await plugin.create_eval_views()` 호출).
- **Go**: `bqPlugin, ok := agentanalytics.AsBigQueryAgentAnalyticsPlugin(adkPlugin)`으로 플러그인을 언래핑하고 `bqPlugin.SyncViews(ctx)`를 호출합니다. `NewBigQueryAgentAnalyticsPluginWithClients(..., nil, ...)`(`bqClient == nil`)로 플러그인을 생성한 경우 플러그인은 뷰를 자동으로 생성하지 않으며 `SyncViews`는 `agentanalytics: BigQuery client is not configured for view creation`을 반환하므로, 대신 `cfg.ViewDefinitions()`(`Name`, `EventType`, `Query` 반환)를 사용하여 뷰 DDL을 직접 검사하거나 실행하세요.

모든 Python 및 Go 뷰에는 다음 **공통 열**이 포함됩니다: `timestamp`, `event_id`, `event_type`, `agent`, `session_id`, `invocation_id`, `user_id`, `trace_id`, `span_id`, `parent_span_id`, `status`, `error_message`, `is_truncated`. Java 뷰에는 `event_id`를 제외한 동일한 공통 열이 포함됩니다.

다음 표에는 이벤트 유형별 뷰와 해당 이벤트별 열이 나열되어 있습니다.

| 뷰 이름 | 이벤트별 열 |
| --- | --- |
| **`v_user_message_received`** | *(공통 열만 해당)* |
| **`v_llm_request`** | `model` (STRING), `request_content` (JSON), `llm_config` (JSON), `tools` (JSON) |
| **`v_llm_response`** | `response` (JSON), `usage_prompt_tokens` (INT64), `usage_completion_tokens` (INT64), `usage_total_tokens` (INT64), `usage_cached_tokens` (INT64), `usage_thinking_tokens` (INT64), `usage_tool_use_tokens` (INT64), `context_cache_hit_rate` (FLOAT64), `total_ms` (INT64), `ttft_ms` (INT64), `model_version` (STRING), `usage_metadata` (JSON), `cache_metadata` (JSON), `cache_type` (STRING), `finish_reason` (STRING) |
| **`v_llm_error`** | `total_ms` (INT64) |
| **`v_tool_starting`** | `tool_name` (STRING), `tool_args` (JSON), `tool_origin` (STRING) |
| **`v_tool_completed`** | `tool_name` (STRING), `tool_result` (JSON), `tool_origin` (STRING), `total_ms` (INT64), `pause_kind` (STRING), `function_call_id` (STRING) |
| **`v_tool_error`** | `tool_name` (STRING), `tool_args` (JSON), `tool_origin` (STRING), `total_ms` (INT64) |
| **`v_agent_starting`** | `agent_instruction` (STRING); ADK Python v2.12.0+ 및 Go에서는 `instruction_source` (STRING), `static_instruction` (STRING; Go에서는 항상 `NULL`), `agent_description` (STRING), `model` (STRING), `sub_agents` (JSON)도 포함 |
| **`v_agent_completed`** | `total_ms` (INT64) |
| **`v_agent_error`** | `total_ms` (INT64), `error_traceback` (STRING) |
| **`v_invocation_starting`** | *(공통 열만 해당)* |
| **`v_invocation_completed`** | *(공통 열만 해당)* |
| **`v_invocation_error`** | `error_traceback` (STRING) |
| **`v_state_delta`** | `state_delta` (JSON) |
| **`v_hitl_credential_request`** | `tool_name` (STRING), `tool_args` (JSON) |
| **`v_hitl_confirmation_request`** | `tool_name` (STRING), `tool_args` (JSON) |
| **`v_hitl_input_request`** | `tool_name` (STRING), `tool_args` (JSON) |
| **`v_a2a_interaction`** | `response_content` (JSON), `a2a_task_id` (STRING), `a2a_context_id` (STRING), `a2a_request` (JSON), `a2a_response` (JSON) |
| **`v_agent_response`** | `response_text` (STRING), `source_event_id` (STRING), `source_event_author` (STRING), `source_event_branch` (STRING) |
| **`v_agent_transfer`** | `from_agent` (STRING), `to_agent` (STRING), `source_event_id` (STRING) |
| **`v_agent_state_checkpoint`** | `agent_state` (JSON), `agent_state_type` (STRING), `end_of_agent` (BOOL), `source_event_id` (STRING) |
| **`v_event_compaction`** | `start_seconds` (FLOAT64), `end_seconds` (FLOAT64), `window_start` (TIMESTAMP), `window_end` (TIMESTAMP), `compacted_content` (JSON, 포맷된 요약 문자열 저장) |
| **`v_tool_paused`** | `tool_name` (STRING), `tool_args` (JSON), `pause_kind` (STRING), `function_call_id` (STRING) |
| **`v_node_output`** | `node_path` (STRING), `node_run_id` (STRING), `node_parent_run_id` (STRING), `output` (JSON) |
| **`v_node_error`** | `node_path` (STRING), `node_run_id` (STRING), `node_parent_run_id` (STRING), `error_code` (STRING) |

위의 이벤트 유형별 뷰 외에도 ADK Python v2.13.0 이상에서는 `create_eval_views=True`가 설정되거나 `await plugin.create_eval_views()`가 호출될 때 두 개의 선택적 [에이전트 평가 뷰](#agent-evaluation-views)(`v_eval_session` 및 `v_eval_turn`)를 생성할 수 있습니다.

Go는 `v_user_message_received`부터 `v_node_error`까지 모든 25개의 이벤트 유형별 뷰를 생성합니다(`PayloadColumnDenylist`가 설정된 경우 동일한 열 이름과 프로젝션 인식 열 삭제 적용). 평가 뷰(`v_eval_session` 및 `v_eval_turn`)는 Python 전용(v2.13.0+)입니다.

4개의 워크플로 뷰(`v_agent_transfer`, `v_agent_state_checkpoint`, `v_event_compaction`, `v_tool_paused`)와 `v_tool_completed`의 `pause_kind` / `function_call_id` 열은 [ADK 2.0 워크플로 이벤트 지원](#adk-2-events)과 함께 제공됩니다. **Python**과 **Go**는 모두 4개의 뷰와 `v_node_output` 및 `v_node_error`를 생성합니다. **Java**(v1.7.0+)에서는 `v_tool_paused`와 `v_tool_completed`의 `pause_kind` / `function_call_id` 열만 생성되며, Java 플러그인은 `v_agent_transfer`, `v_agent_state_checkpoint`, `v_event_compaction` 이벤트를 내보내지 않으므로 해당 뷰는 Java에서 생성되지 않습니다.

기타 Java 뷰의 차이점은 다음과 같습니다.

- Java는 `v_agent_error`, `v_invocation_error`, `v_node_output`, `v_node_error` 이벤트를 내보내지 않으므로 해당 뷰를 생성하지 않습니다.
- Java의 `v_llm_response`는 `usage_metadata`에서 끝납니다. `usage_thinking_tokens`, `usage_tool_use_tokens`, `cache_metadata`, `cache_type`, `finish_reason`은 노출되지 않습니다.
- Java의 `v_agent_response`는 `response_text` 대신 `text_summary`를 노출합니다.
- Java의 `v_agent_starting`은 `agent_instruction`만 노출합니다.
- Java의 `v_a2a_interaction`은 `a2a_response`를 생략합니다. 응답은 `response_content`에서 계속 사용할 수 있습니다.

## 이벤트 유형 및 페이로드 {#event-types}

`content` 컬럼에는 이제 `event_type`별 **JSON** 객체가 포함됩니다.
`content_parts` 컬럼은 콘텐츠의 구조화된 뷰를 제공하며, 이미지나 오프로딩된
데이터에 특히 유용합니다.

!!! note "콘텐츠 자르기"

    - 가변 콘텐츠 필드는 `max_content_length`(`BigQueryLoggerConfig`에서 구성,
      기본값 500KB)로 잘립니다.
    - `gcs_bucket_name`이 구성된 경우 큰 콘텐츠는 잘리지 않고 GCS로 오프로딩되며
      참조가 `content_parts.object_ref`에 저장됩니다.

### LLM 상호작용(플러그인 수명 주기)

이 이벤트들은 LLM으로 전송되는 원시 요청과 LLM에서 받은 응답을 추적합니다.

**1. LLM_REQUEST**

대화 기록과 시스템 지침을 포함해 모델로 전송된 프롬프트를 캡처합니다.

```json
{
  "event_type": "LLM_REQUEST",
  "content": {
    "system_prompt": "You are a helpful assistant...",
    "prompt": [
      {
        "role": "user",
        "content": "hello how are you today"
      }
    ]
  },
  "attributes": {
    "root_agent_name": "my_bq_agent",
    "model": "gemini-flash-latest",
    "tools": [
      {
        "name": "list_dataset_ids",
        "description": "..."
      },
      {
        "name": "execute_sql",
        "description": "..."
      }
    ],
    "llm_config": {
      "temperature": 0.5,
      "top_p": 0.9
    }
  }
}
```

자동으로 생성되는 `v_llm_request` 뷰는 `tools` 속성을 해당 뷰의 `tools` (JSON) 열로 노출합니다. Python 및 Go에서 `tools`는 도구당 하나의 항목을 가지며, 도구의 `name`과 사용 가능한 경우 `description` 및 `parameters`(도구의 매개변수 스키마)를 포함합니다. 이러한 항목은 다른 속성과 동일한 크기 제한 및 민감한 키 수정 파이프라인을 거칩니다. Java는 도구 이름만 기록합니다(예: `["list_dataset_ids", "execute_sql"]`).

**2. LLM_RESPONSE**

모델 출력과 토큰 사용량 통계를 캡처합니다.

```json
{
  "event_type": "LLM_RESPONSE",
  "content": {
    "response": "text: 'Hello! I'm doing well...'",
    "usage": {
      "completion": 19,
      "prompt": 10129,
      "total": 10148
    }
  },
  "attributes": {
    "root_agent_name": "my_bq_agent",
    "model_version": "gemini-flash-latest",
    "usage_metadata": {
      "prompt_token_count": 10129,
      "candidates_token_count": 19,
      "total_token_count": 10148
    },
    "finish_reason": "STOP"
  },
  "latency_ms": {
    "time_to_first_token_ms": 2579,
    "total_ms": 2579
  }
}
```

Python 및 Go 플러그인은 최종(부분 응답이 아닌) 응답에만 `finish_reason`을 추가합니다. 해당 `v_llm_response` 뷰는 최종 응답의 `cache_type`과 함께 이를 `STRING`으로 노출합니다. 모델이 종료 진단 정보를 제공하는 경우, 해당 행의 `status`가 `OK`로 유지되더라도 공통 `error_message` 열에 정제된 값을 저장합니다.

Python 및 Go에서는 모델 종료 및 차단 이유가 `LLM_RESPONSE`로 계속 분류됩니다. 플러그인은 모델 호출이 오류로 실패한 경우에만 `LLM_ERROR`를 사용합니다.

Python 및 Go에서 `content.response`는 응답 파트를 `|`로 구분하여 요약합니다(예: 텍스트의 경우 `text: '...'`, 함수 호출의 경우 `call: <name>`, 함수 응답의 경우 `resp: <name>`, 기타 파트 유형의 경우 `other`). `max_content_length`(Go의 경우 `MaxContentLen`)보다 긴 텍스트는 잘리고 `is_truncated`가 설정됩니다. ADK Python v2.12.0+ 및 Go에서는 요약에 실행 가능한 코드를 `Executable code (<language>): <code>`로, 코드 실행 결과를 `Code execution result (<outcome>): <output>`으로 표시하고, 텍스트, 코드 및 출력에서 일반적인 자격 증명 패턴을 수정(redact)하며, 잘린 값은 `...[TRUNCATED]`로 끝납니다. 이 수정으로 인해 `is_truncated`도 설정됩니다. `custom_metadata_allowlist`(Go의 경우 `CustomMetadataAllowlist`)가 설정된 경우, 최종(부분 응답이 아닌) `LLM_RESPONSE` 행은 `llm_response.custom_metadata`에서 허용 목록에 있는 키를 `attributes.custom_metadata`로 캡처합니다.

**3. LLM_ERROR**

LLM 호출이 예외로 실패할 때 기록됩니다. 오류 메시지가 캡처되고 span이 닫힙니다.

```json
{
  "event_type": "LLM_ERROR",
  "content": null,
  "attributes": {
    "root_agent_name": "my_bq_agent"
  },
  "error_message": "Error 429: Resource exhausted",
  "latency_ms": {
    "total_ms": 350
  }
}
```

### 도구 사용(플러그인 수명 주기)

이 이벤트들은 에이전트의 도구 실행을 추적합니다. 각 도구 이벤트에는 도구의
출처를 분류하는 `tool_origin` 필드가 포함됩니다.

| 도구 출처 | 설명 |
| --- | --- |
| `LOCAL` | `FunctionTool` 인스턴스(로컬 함수) |
| `MCP` | Model Context Protocol 도구(`McpTool` 인스턴스) |
| `SUB_AGENT` | `AgentTool` 인스턴스(하위 에이전트) |
| `A2A` | 원격 Agent2Agent 인스턴스(`RemoteA2aAgent`) |
| `TRANSFER_AGENT` | `TransferToAgentTool`(`transfer_to_agent`) 인스턴스(일반 에이전트 transfer) |
| `TRANSFER_A2A` | Python 및 Go: 원격 A2A 에이전트로 확인되는 `transfer_to_agent` 호출(호출 수준에서 분류) |
| `TOOLBOX` | Python(v2.13.0+) 및 Go: MCP Toolbox for Databases(`ToolboxTool`) 도구 |
| `SKILL` | Python(v2.13.0+): `SkillToolset` 기본 제공 도구(`list_skills`, `load_skill`, `load_skill_resource`, `run_skill_script`, `search_skills`, `unload_skill`); Go: `SkillToolset` 기본 제공 도구(`list_skills`, `load_skill`, `load_skill_resource`) |
| `UNKNOWN` | 분류되지 않은 도구 |

**4. TOOL_STARTING**

에이전트가 도구 실행을 시작할 때 기록됩니다.

```json
{
  "event_type": "TOOL_STARTING",
  "content": {
    "tool": "list_dataset_ids",
    "args": {
      "project_id": "bigquery-public-data"
    },
    "tool_origin": "LOCAL"
  }
}
```

**5. TOOL_COMPLETED**

도구 실행이 완료될 때 기록됩니다.

```json
{
  "event_type": "TOOL_COMPLETED",
  "content": {
    "tool": "list_dataset_ids",
    "result": [
      "austin_311",
      "austin_bikeshare"
    ],
    "tool_origin": "LOCAL"
  },
  "latency_ms": {
    "total_ms": 467
  }
}
```

**6. TOOL_ERROR**

도구 실행이 예외로 실패할 때, 또는(ADK Python v2.13.0 이상에서) 반환된 도구 결과가 기본 제공 MCP `isError` / `is_error` 규칙, `ReflectAndRetryToolPlugin` 오류 응답 또는 커스텀 [`tool_result_classifier`](#tool-result-error-classification)에 의해 오류로 분류될 때 기록됩니다. 도구 이름, 인수, 도구 출처 및 오류 메시지를 캡처합니다.

```json
{
  "event_type": "TOOL_ERROR",
  "content": {
    "tool": "list_dataset_ids",
    "args": {
      "project_id": "nonexistent-project"
    },
    "tool_origin": "LOCAL"
  },
  "error_message": "Error 404: Dataset not found",
  "latency_ms": {
    "total_ms": 150
  }
}
```

### 상태 관리

이 이벤트들은 일반적으로 도구에 의해 트리거되는 에이전트 상태 변경을 추적합니다.

**7. STATE_DELTA**

에이전트의 내부 상태 변경(예: 도구가 업데이트한 커스텀 애플리케이션 상태)을
추적합니다.

!!! note "내장 마스킹"

    Python은 `temp:` 상태 값을 `[REDACTED]`로 바꿉니다. Go는 로깅 전에 `state_delta`에서 최상위 소문자 `temp:` 항목을 제거하며 아무것도 남지 않으면 `STATE_DELTA` 행을 내보내지 않습니다. 구조화된 콘텐츠 및 속성의 기타 `temp:` 값은 `[REDACTED]`로 바뀝니다. 자세한 내용은 [기본 제공 수정](#built-in-redaction)을 참고하세요.

```json
{
  "event_type": "STATE_DELTA",
  "attributes": {
    "state_delta": {
      "customer_tier": "enterprise",
      "last_query_dataset": "bigquery-public-data.samples"
    }
  }
}
```

### 에이전트 수명 주기 및 일반 이벤트

| 이벤트 유형 | 콘텐츠(JSON) 구조 |
| ---------- | ----------------- |
| `INVOCATION_STARTING` | `{}` |
| `INVOCATION_COMPLETED` | `{}` |
| `INVOCATION_ERROR` | `{"error_traceback": "..."}` |
| `AGENT_STARTING` | `"You are a helpful agent..."`, 또는 ADK Python v2.12.0+ 및 Go에서는 지침이 비어 있거나 동적 지침 제공자(instruction provider)인 경우 `null` |
| `AGENT_COMPLETED` | `{}` |
| `AGENT_ERROR` | `{"error_traceback": "..."}` |
| `USER_MESSAGE_RECEIVED` | `{"text_summary": "Help me book a flight."}` |
| `AGENT_RESPONSE` | `{"response": "Here are the flights..."}` |

Python 및 Go에서 `AGENT_ERROR` 및 `INVOCATION_ERROR` 행은 `status="ERROR"`, 정제된 `error_message`, 그리고 정제된 `content.error_traceback` 값(Python에서는 포맷팅된 트레이스백, Go에서는 스택 트레이스가 없는 정제된 `err.Error()` 메시지)을 갖습니다. 에이전트 오류 뷰는 경과된 `total_ms`도 노출합니다. Python에서 두 이벤트는 모두 에이전트 또는 러너 실행을 벗어난 처리되지 않은 예외를 나타냅니다. Go에서 `AGENT_ERROR`는 재시도되는 실패한 노드 시도나 실패한 도구로서의 에이전트 실행과 같이 ADK가 `AfterAgent` 콜백 없이 종료하고 실패를 자체적으로 처리한 활성화에 대해서도 기록됩니다.

ADK Python v2.12.0+ 및 Go에서는 `AGENT_STARTING` 행에 다음 `attributes` 키를 추가할 수도 있으며, `v_agent_starting` 뷰는 이를 열로 노출합니다:

- `instruction_source`: 에이전트의 지침이 콜러블 `InstructionProvider`에서 제공되는 경우 `"provider"`.
- `static_instruction`: 에이전트의 정적 지침 텍스트 *(Python v2.12.0+; Go 플러그인에서는 채워지지 않으므로 Go에서는 `v_agent_starting.static_instruction`이 `NULL`임)*.
- `agent_description`: 에이전트의 설명.
- `model`: 에이전트의 모델 이름. Python에서는 LLM 에이전트가 `model`을 설정하지 않은 경우 모델을 설정한 가장 가까운 조상 에이전트로부터 상속받은 모델이며, Go에서는 에이전트 자체에 설정된 경우에만 `model`이 기록됩니다.
- `sub_agents`: 에이전트의 하위 에이전트 이름들.

해당되지 않거나 값이 비어 있는 키는 생략됩니다. Python v2.12.0+ 및 Go에서 행의 콘텐츠가 지침 텍스트 대신 `<function ...>`과 같은 콜러블의 텍스트 표현인 경우 뷰의 `agent_instruction` 열은 `NULL`입니다.

**Kotlin**에서는 두 invocation 이벤트가 빈 객체 대신 요약 메시지를 전달합니다: `{"message": "Invocation started"}` 및 `{"message": "Invocation completed"}`.

**AGENT_RESPONSE**

에이전트가 사용자에게 최종 응답을 yield할 때 기록됩니다. 응답 텍스트는 `content`에
저장되고, source event metadata는 `attributes`에 저장됩니다.

```json
{
  "event_type": "AGENT_RESPONSE",
  "content": {
    "response": "Here are the available flights..."
  },
  "attributes": {
    "source_event_id": "evt-abc123",
    "source_event_author": "flight_agent",
    "source_event_branch": "main"
  }
}
```

이 예시는 Python 및 Go 페이로드를 보여줍니다. Java는 표시되는 콘텐츠 요약을 `{"text_summary": "Here are the available flights..."}`로 저장하고 `v_agent_response`에서 해당 필드를 `text_summary`로 노출합니다.

Python 및 Go에서 `final_response_tool_names`(Go의 경우 `FinalResponseToolNames`)에 성공적으로 완료된 도구의 이름이 포함되어 있으면 플러그인은 해당 도구의 호출 인수를 응답 페이로드로 하고 `attributes`에 `source_tool`을 포함하여 `AGENT_RESPONSE`도 내보냅니다. 이는 표시되는 텍스트 이벤트 대신 전용 도구를 통해 최종 답변을 전달하는 에이전트를 지원합니다.

### Human-in-the-Loop(HITL) 이벤트 {#hitl-events}

플러그인은 ADK의 synthetic HITL 도구 호출을 자동 감지하고 전용 이벤트 유형을
발행합니다. 이러한 이벤트는 일반 `TOOL_STARTING` / `TOOL_COMPLETED` 이벤트에
**추가로** 기록됩니다.

인식되는 HITL 도구 이름은 다음과 같습니다.

- `adk_request_credential`: 사용자 자격 증명 요청(예: OAuth 토큰)
- `adk_request_confirmation`: 진행 전 사용자 확인 요청
- `adk_request_input`: 자유 형식 사용자 입력 요청

| 이벤트 유형 | 트리거 | 콘텐츠(JSON) 구조 |
| ---------- | ------ | ----------------- |
| `HITL_CREDENTIAL_REQUEST` | 에이전트가 `adk_request_credential` 호출 | `{"tool": "adk_request_credential", "args": {...}}` |
| `HITL_CREDENTIAL_REQUEST_COMPLETED` | 사용자가 자격 증명 응답 제공 | `{"tool": "adk_request_credential", "result": {...}}` |
| `HITL_CONFIRMATION_REQUEST` | 에이전트가 `adk_request_confirmation` 호출 | `{"tool": "adk_request_confirmation", "args": {...}}` |
| `HITL_CONFIRMATION_REQUEST_COMPLETED` | 사용자가 확인 응답 제공 | `{"tool": "adk_request_confirmation", "result": {...}}` |
| `HITL_INPUT_REQUEST` | 에이전트가 `adk_request_input` 호출 | `{"tool": "adk_request_input", "args": {...}}` |
| `HITL_INPUT_REQUEST_COMPLETED` | 사용자가 입력 응답 제공 | `{"tool": "adk_request_input", "result": {...}}` |

HITL 요청 이벤트는 `on_event_callback`의 `function_call` 파트에서 감지됩니다.
HITL 완료 이벤트는 `on_event_callback`과 `on_user_message_callback` 모두의
`function_response` 파트에서 감지됩니다.

!!! note "HITL 이벤트용 뷰"

    자동 생성되는 뷰는 세 가지 **요청** 이벤트 유형
    (`v_hitl_credential_request`, `v_hitl_confirmation_request`,
    `v_hitl_input_request`)에만 존재합니다. 세 가지 `*_COMPLETED` 이벤트 유형은
    기본 테이블에는 기록되지만 전용 뷰는 생성되지 않습니다. `agent_events`
    테이블에서 `WHERE event_type LIKE 'HITL_%_COMPLETED'` 조건으로 직접
    조회하세요.

### A2A 상호작용 이벤트

에이전트가 Agent2Agent(A2A) 프로토콜로 원격 에이전트와 통신하면 플러그인은
요청과 응답 세부 정보를 캡처하는 `A2A_INTERACTION` 이벤트를 기록합니다.

**A2A_INTERACTION**

A2A 원격 에이전트 호출이 완료될 때 기록됩니다.

```json
{
  "event_type": "A2A_INTERACTION",
  "content": {
    "response_content": "The remote agent's response...",
    "a2a_task_id": "task-abc123",
    "a2a_context_id": "ctx-def456",
    "a2a_request": { ... },
    "a2a_response": { ... }
  }
}
```

이 예시는 Python 및 Go 페이로드를 보여줍니다. Python, Go 및 Java는 응답을 `content`에 직접 저장합니다. Python과 Go는 네임스페이스가 지정된 응답을 `attributes.a2a_metadata`에도 유지하며, Java는 해당 중복을 생략합니다. Python 및 Go의 `v_a2a_interaction` 뷰는 `response_content`, `a2a_task_id`, `a2a_context_id`, `a2a_request`, `a2a_response`를 노출합니다. Java는 마지막 열을 생략합니다.

### 에이전트 워크플로 및 일시중지/재개 이벤트 (ADK 2.0) {#adk-2-events}

<div class="language-support-tag">
  <span class="lst-supported">ADK 지원 버전</span><span class="lst-python">Python v2.3.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v1.7.0</span>
</div>

!!! note "Java 지원"

    **Java** 플러그인은 이 섹션의 일부만 지원합니다. `TOOL_PAUSED` 및 아래에 설명된 일시중지/재개 페어링을 내보내지만, `AGENT_TRANSFER`, `AGENT_STATE_CHECKPOINT` 또는 `EVENT_COMPACTION`은 내보내지 **않으며**, `attributes.adk` 엔벨로프를 작성하지 않습니다. Java 플러그인은 대신 `pause_kind` 및 `function_call_id`를 `attributes`의 **최상위 수준**에 저장합니다(아래 쿼리 참고사항 참조).

ADK 2.0에서는 멀티 에이전트 워크플로(제어권을 넘기는 에이전트, 상태 체크포인트를 수행하는 에이전트, 긴 기록을 압축하는 에이전트)와 여러 턴에 걸쳐 일시중지 및 재개되는 장기 실행 도구가 도입되었습니다. 플러그인은 네 가지 새로운 이벤트 유형과 작은 메타데이터 엔벨로프인 `attributes.adk`를 통해 이러한 흐름을 관측할 수 있도록 하여, 해당 행을 이를 생성한 ADK 이벤트와 연결합니다.

#### `attributes.adk` 엔벨로프

이 엔벨로프는 **Python** 및 **Go** 플러그인에서 작성됩니다. 모든 행에 `attributes.adk` 객체가 포함됩니다. `schema_version`은 항상 존재하며(Python에서는 `app_name`과 함께, Go에서는 `app_name`이 비어 있지 않을 때마다 함께), 이벤트에서 파생되는 필드는 ADK `Event`(수명 주기 및 워크플로 이벤트)에서 생성된 행에만 추가되므로 콜백 전용 행에서는 생략되고 쿼리 시 SQL `NULL`로 해석됩니다.

| 필드 | 유형 | 의미 |
| --- | --- | --- |
| `schema_version` | string | 엔벨로프 버전(현재 `"1"`). 엔벨로프가 발전함에 따라 다운스트림 쿼리를 이에 맞춰 제어할 수 있습니다. |
| `app_name` | string | 해당 행을 생성한 ADK 앱입니다(Go에서는 비어 있을 때 생략됨). |
| `source_event_id` | string | 원본 ADK `Event`의 ID입니다. 단일 이벤트가 생성할 수 있는 여러 행을 조인하기 위한 신뢰할 수 있는 키입니다. |
| `node` | object | 워크플로 노드 ID: `{ "path", "run_id", "parent_run_id" }`. `parent_run_id`는 상위 노드의 실행 ID입니다(루트에서는 `null`). Go에서 `node`는 `NodeInfo`에 설정된 경우 `message_as_output`(bool) 및 `output_for`(문자열 배열)도 포함합니다. |
| `branch` | string | 워크플로가 분기된 경로를 실행할 때 이벤트의 브랜치입니다. |
| `scope` | object | 격리 범위 `{ "id", "kind" }`입니다. 여기서 `kind`는 `node_run`(워크플로 노드 실행, 예: `loopA@42`), `function_call`(모델이 생성한 호출 ID) 또는 *(Python)* `unknown`입니다. |
| `route` | string 또는 array | 이벤트 액션에 의해 선택된 라우트입니다(설정된 경우; Python에서는 문자열, Go에서는 문자열 배열). |
| `render_ui_widgets` | array | 이벤트 액션에서 요청한 직렬화된 UI 위젯입니다(설정된 경우) *(Python)*. |
| `rewind_before_invocation_id` | string | 이벤트 액션이 되감기를 요청하는 기준 호출 ID입니다(설정된 경우) *(Python)*. |
| `pause_kind` | string | `TOOL_PAUSED`의 경우: 일반 장기 실행 도구는 `tool`, HITL 요청은 `hitl_credential` / `hitl_confirmation` / `hitl_input`입니다. 재개된 `TOOL_COMPLETED` 행에서는 항상 `tool`입니다. HITL 완료는 `TOOL_COMPLETED`가 아닌 `HITL_*_REQUEST_COMPLETED`로 기록됩니다. |
| `function_call_id` | string | 함수 호출 ID입니다. 둘을 페어링할 수 있도록 `TOOL_PAUSED` 및 일치하는 재개된 `TOOL_COMPLETED` 행에 설정됩니다(일반 도구만 해당). |

**Go**에서 `attributes.adk`는 또한 모든 행에 `event_id` 및 `author`를 스탬프하고, 비어 있지 않은 경우 `adk_version` 및 `invocation_id`를 스탬프하며, `DisableSessionMetadata`가 `false`이고 값이 비어 있지 않은 경우 `session_id` 및 `user_id`를 스탬프하고, 존재하는 경우 ADK `session.Event`에서 파생된 행에 `isolation_scope`, `artifact_delta`, `skip_summarization`, `escalate`를 추가합니다.

!!! tip "엔벨로프 쿼리"

    엔벨로프 필드는 `JSON_VALUE(attributes, '$.adk.<field>')` (또는 `node` / `scope` 객체의 경우 `JSON_QUERY`)로 읽습니다. 자동으로 생성된 뷰는 자주 사용되는 필드(`source_event_id`, `pause_kind`, `function_call_id`)를 이미 평면화된 열로 노출하므로 대부분의 쿼리는 뷰를 직접 사용할 수 있습니다.

#### AGENT_TRANSFER

한 에이전트가 다른 에이전트로 제어권을 넘길 때 기록됩니다(예: 코디네이터가 전문가 하위 에이전트로 라우팅).

```json
{
  "event_type": "AGENT_TRANSFER",
  "content": {
    "from_agent": "coordinator",
    "to_agent": "flight_agent"
  },
  "attributes": {
    "adk": { "source_event_id": "evt-abc123" }
  }
}
```

#### AGENT_STATE_CHECKPOINT

에이전트가 상태의 스냅샷을 생성할 때 기록됩니다. 플러그인은 또한 에이전트 실행의 끝을 표시하기 위해 `end_of_agent: true`를 포함하는 체크포인트를 내보냅니다. `v_agent_state_checkpoint` 뷰는 `agent_state_type`을 노출하므로 실제 상태 객체와 명시적 `null` 체크포인트(실행 종료 마커) 및 누락된 값을 구분할 수 있습니다. Go에서 체크포인트는 `CustomMetadata` 키인 `adk_agent_state`/`agent_state` 및 `end_of_agent`/`adk_end_of_agent`에서 가져오며, 이러한 키가 `CustomMetadataAllowlist`에 나열된 경우에만 방출됩니다.

```json
{
  "event_type": "AGENT_STATE_CHECKPOINT",
  "content": {
    "agent_state": { "step": 3, "retries": 0 },
    "end_of_agent": false
  },
  "attributes": {
    "adk": { "source_event_id": "evt-def456" }
  }
}
```

#### EVENT_COMPACTION

ADK가 이전 이벤트 윈도우를 요약으로 압축할 때 기록됩니다(긴 대화를 컨텍스트 윈도우 내로 유지하는 데 사용됨). 타임스탬프는 소수점 형태의 epoch 초 단위입니다. 뷰는 이를 BigQuery `TIMESTAMP` 열(`window_start`, `window_end`)로도 노출합니다. `compacted_content`는 구조화된 객체가 아니라 플러그인이 포맷한 압축 윈도우의 텍스트(문자열)를 보유합니다.

```json
{
  "event_type": "EVENT_COMPACTION",
  "content": {
    "start_timestamp": 1733856000.123,
    "end_timestamp": 1733856120.456,
    "compacted_content": "User booked a flight to SFO, then asked about baggage..."
  }
}
```

#### NODE_OUTPUT 및 NODE_ERROR

<div class="language-support-tag">
  <span class="lst-supported">ADK 지원 버전</span><span class="lst-python">Python v2.7.0</span><span class="lst-go">Go v0.1.0</span>
</div>

워크플로 노드 경로가 있는 최종 비부분(non-partial) 이벤트의 경우 플러그인은 해당되는 경우 노드별 종료 행을 내보냅니다.

- `NODE_OUTPUT`은 `event.output`이 존재하고 노드가 메시지를 출력으로 사용하지 않을 때 내보내집니다. 이벤트 출력은 `content`에 직접 저장됩니다.
- `NODE_ERROR`는 `event.error_code`가 존재하고 모델 완료 또는 차단 이유가 아닐 때 내보내집니다. 코드는 `content.error_code`에 저장되고, 정제된 메시지는 `error_message`에 저장되며, `status`는 `ERROR`입니다.

두 자동 생성 뷰는 모두 `attributes.adk.node`에서 `node_path`, `node_run_id`, `node_parent_run_id`를 노출합니다.

```json
{
  "event_type": "NODE_ERROR",
  "content": { "error_code": "VALIDATION_FAILED" },
  "attributes": {
    "adk": {
      "node": {
        "path": "workflow/validate@run-7",
        "run_id": "run-7",
        "parent_run_id": null
      }
    }
  },
  "status": "ERROR",
  "error_message": "Input did not satisfy the node contract"
}
```

#### TOOL_PAUSED 및 일시중지/재개 페어링

일반적인 장기 실행 도구는 양보(yield)할 때 `TOOL_PAUSED` 행을 내보내고 결과가 도착할 때(종종 이후 턴에서) `TOOL_COMPLETED` 행을 내보냅니다. 두 행 모두 동일한 `function_call_id`와 `tool`이라는 `pause_kind`를 가지므로, 일시중지와 완료를 페어링하고 도구가 일시중지된 시간을 측정할 수 있습니다. (HITL 요청도 `TOOL_PAUSED`를 내보내지만 완료는 다르게 로깅됩니다. 아래 참고사항 참조.)

```json
{
  "event_type": "TOOL_PAUSED",
  "content": {
    "tool": "request_manager_approval",
    "args": { "amount": 5000 }
  },
  "attributes": {
    "adk": { "pause_kind": "tool", "function_call_id": "call-789" }
  }
}
```

!!! note "Java 속성 위치"

    Java 플러그인은 `adk` 래퍼 없이 `attributes`의 최상위 수준에 페어 키를 작성합니다:
    `"attributes": {"pause_kind": "tool", "function_call_id": "call-789"}`.
    아래의 기본 테이블 쿼리에서
    `'$.adk.pause_kind'` / `'$.adk.function_call_id'`를 `'$.pause_kind'` /
    `'$.function_call_id'`로 바꾸세요. 뷰 기반 쿼리는 뷰가 키를 평면화된 열로 노출하므로 두 언어 모두에서 변경 없이 작동합니다.

    Java는 또한 동일한 최상위 페어 키를 `HITL_*_REQUEST_COMPLETED` 행에 스탬프하므로, 기본 테이블에서 HITL `TOOL_PAUSED` 행을 `function_call_id`로 완료 행에 직접 조인할 수 있습니다(HITL 완료를 위한 전용 뷰는 없음).

!!! note "HITL 이벤트와의 관계"

    HITL 요청(`adk_request_confirmation` 등)은 [HITL 이벤트](#hitl-events)에 설명된 대로 여전히 전용 `HITL_*_REQUEST` 이벤트를 내보냅니다. 해당 요청이 장기 실행되는 경우 플러그인은 추가로 HITL 종류(예: `hitl_confirmation`)를 식별하는 `pause_kind`를 가진 `TOOL_PAUSED` 행을 내보내므로 HITL 일시중지에도 도구 일시중지와 동일한 가시성이 부여됩니다.

    **하지만 HITL 완료는 `TOOL_COMPLETED`로 도착하지 않습니다.** 사용자의 응답은 `TOOL_COMPLETED`가 아닌 해당 `HITL_*_REQUEST_COMPLETED` 이벤트로 로깅되므로, `hitl_*` 일시중지는 아래의 도구 조인을 통해 페어링되지 않습니다. HITL 일시중지의 해결을 확인하려면 해당 `HITL_*_REQUEST_COMPLETED` 이벤트를 확인하세요([HITL 이벤트](#hitl-events) 참조). 따라서 아래의 일시중지/재개 쿼리는 일반 도구(`pause_kind = 'tool'`)로 범위가 지정됩니다.

공유 키를 사용하여 일시중지된 도구를 해당 완료와 페어링합니다. 기본 테이블 기준:

```sql
SELECT
  p.timestamp AS paused_at,
  c.timestamp AS resumed_at,
  TIMESTAMP_DIFF(c.timestamp, p.timestamp, SECOND) AS paused_seconds,
  JSON_VALUE(p.content, '$.tool') AS tool_name,
  JSON_VALUE(p.attributes, '$.adk.pause_kind') AS pause_kind
FROM `your-gcp-project-id.adk_agent_logs.agent_events` AS p
JOIN `your-gcp-project-id.adk_agent_logs.agent_events` AS c
  ON  c.event_type = 'TOOL_COMPLETED'
  AND c.session_id = p.session_id
  AND c.user_id = p.user_id
  AND JSON_VALUE(c.attributes, '$.adk.function_call_id')
      = JSON_VALUE(p.attributes, '$.adk.function_call_id')
WHERE p.event_type = 'TOOL_PAUSED'
  AND JSON_VALUE(p.attributes, '$.adk.pause_kind') = 'tool'
ORDER BY paused_at;
```

또는 `pause_kind`와 `function_call_id`를 평면 열로 노출하는 자동 생성 뷰를 대상으로 더 간단하게 쿼리할 수 있습니다.

```sql
SELECT
  p.timestamp AS paused_at,
  c.timestamp AS resumed_at,
  TIMESTAMP_DIFF(c.timestamp, p.timestamp, SECOND) AS paused_seconds,
  p.tool_name,
  p.pause_kind
FROM `your-gcp-project-id.adk_agent_logs.v_tool_paused` AS p
JOIN `your-gcp-project-id.adk_agent_logs.v_tool_completed` AS c
  USING (session_id, user_id, function_call_id)
WHERE p.pause_kind = 'tool'
ORDER BY paused_at;
```

## 저장소 동작: GCS 오프로딩

`BigQueryLoggerConfig`에 `gcs_bucket_name`(Go의 `agentanalytics.Config`에서는 `GCSBucketName` 또는 `GCSOffloader`)이 구성되면 플러그인은 큰 텍스트와 멀티모달 콘텐츠(이미지, 오디오 등)를 Google Cloud Storage로 자동 오프로딩합니다. `content` 컬럼에는 요약 또는 placeholder가 포함되고, `content_parts`에는 GCS URI를 가리키는 `object_ref`가 저장됩니다. [구성 옵션](#configuration-options)의 `connection_id`(Go의 `ConnectionID`), `max_content_length`(Go의 `MaxContentLen` 및 `MaxInlineTextSize`), 그리고 Go 업로드 동시성/메모리 상한(`GCSMaxConcurrentUploads`, `GCSUploadTimeout`, `GCSMaxPendingUploadBytes`)도 참고하세요.

Go에서 오프로드된 객체는 객체 경로에 해당 행 타임스탬프의 UTC 날짜(`[prefix/]<YYYY-MM-DD>/<trace_id>/<span_id>_<event_id>_c<ord>_p<idx><ext>`)를 사용하고, `object_ref.details.gcs_metadata`에 `"content_type"`과 함께 `"size"`를 기록하며(오프로드된 텍스트의 경우 `content_parts[].mime_type`을 `"text/plain"`으로 유지하면서 GCS 객체 `content_type`으로 `"text/plain; charset=utf-8"`을 사용), `USER_MESSAGE_RECEIVED` 및 `LLM_REQUEST` 외에도 `LLM_RESPONSE` 이벤트에 대해 `content_parts`를 채웁니다.

### 오프로딩된 텍스트 예시

```json
{
  "event_type": "LLM_REQUEST",
  "content_parts": [
    {
      "part_index": 1,
      "mime_type": "text/plain",
      "storage_mode": "GCS_REFERENCE",
      "text": "AAAA... [OFFLOADED]",
      "object_ref": {
        "uri": "gs://sample-bucket-name/2025-12-10/a2c7f13d3a3f0bbb8793692f76a6012a/3916f5762bcd4d42_ca5e3c9d99e24e46b614f2f44f93bf6e_c0_p1.txt",
        "authorizer": "us.bqml_connection",
        "details": {"gcs_metadata": {"content_type": "text/plain"}}
      }
    }
  ]
}
```

### 오프로딩된 이미지 예시

```json
{
  "event_type": "LLM_REQUEST",
  "content_parts": [
    {
      "part_index": 2,
      "mime_type": "image/png",
      "storage_mode": "GCS_REFERENCE",
      "text": "[MEDIA OFFLOADED]",
      "object_ref": {
        "uri": "gs://sample-bucket-name/2025-12-10/a2c7f13d3a3f0bbb8793692f76a6012a/3916f5762bcd4d42_ca5e3c9d99e24e46b614f2f44f93bf6e_c0_p2.png",
        "authorizer": "us.bqml_connection",
        "details": {"gcs_metadata": {"content_type": "image/png"}}
      }
    }
  ]
}
```

### 오프로딩된 콘텐츠 조회(서명된 URL 가져오기)

```sql
SELECT
  timestamp,
  event_type,
  part.mime_type,
  part.storage_mode,
  part.object_ref.uri AS gcs_uri,
  -- Generate a signed URL to read the content directly (requires connection_id configuration)
  STRING(OBJ.GET_ACCESS_URL(part.object_ref, 'r').access_urls.read_url) AS signed_url
FROM `your-gcp-project-id.your-dataset-id.agent_events`,
UNNEST(content_parts) AS part
WHERE part.storage_mode = 'GCS_REFERENCE'
ORDER BY timestamp DESC
LIMIT 10;
```

## 쿼리 레시피

### 실행 디버깅

#### `trace_id`로 특정 대화 턴 추적

```sql
SELECT timestamp, event_type, agent, JSON_VALUE(content, '$.response') as summary
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE trace_id = 'your-trace-id'
ORDER BY timestamp ASC;
```

#### Span 계층 및 지속 시간 분석

```sql
SELECT
  span_id,
  parent_span_id,
  event_type,
  timestamp,
  -- Extract duration from latency_ms for completed operations
  CAST(JSON_VALUE(latency_ms, '$.total_ms') AS INT64) as duration_ms,
  -- Identify the specific tool or operation
  COALESCE(
    JSON_VALUE(content, '$.tool'),
    'LLM_CALL'
  ) as operation
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE trace_id = 'your-trace-id'
  AND event_type IN ('LLM_RESPONSE', 'TOOL_COMPLETED')
ORDER BY timestamp ASC;
```

#### 오류 분석(LLM 및 도구 오류)

뷰 사용(권장):

```sql
-- Tool errors with provenance
SELECT timestamp, agent, tool_name, tool_origin, error_message, total_ms
FROM `your-gcp-project-id.your-dataset-id.v_tool_error`
ORDER BY timestamp DESC
LIMIT 20;

-- LLM errors
SELECT timestamp, agent, error_message, total_ms
FROM `your-gcp-project-id.your-dataset-id.v_llm_error`
ORDER BY timestamp DESC
LIMIT 20;
```

### 비용 및 성능 모니터링

#### 토큰 사용량 분석

`v_llm_response` 뷰 사용(권장):

```sql
SELECT
  AVG(usage_total_tokens) as avg_tokens,
  AVG(usage_prompt_tokens) as avg_prompt_tokens,
  AVG(usage_completion_tokens) as avg_completion_tokens
FROM `your-gcp-project-id.your-dataset-id.v_llm_response`;
```

또는 JSON 추출과 함께 기본 테이블 사용:

```sql
SELECT
  AVG(CAST(JSON_VALUE(content, '$.usage.total') AS INT64)) as avg_tokens
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE event_type = 'LLM_RESPONSE';
```

#### 지연 시간 분석(LLM 및 도구)

뷰 사용(권장):

```sql
-- LLM latency
SELECT AVG(total_ms) as avg_llm_ms, AVG(ttft_ms) as avg_ttft_ms
FROM `your-gcp-project-id.your-dataset-id.v_llm_response`;

-- Tool latency by tool name
SELECT tool_name, tool_origin, AVG(total_ms) as avg_tool_ms
FROM `your-gcp-project-id.your-dataset-id.v_tool_completed`
GROUP BY tool_name, tool_origin
ORDER BY avg_tool_ms DESC;
```

또는 기본 테이블 사용:

```sql
SELECT
  event_type,
  AVG(CAST(JSON_VALUE(latency_ms, '$.total_ms') AS INT64)) as avg_latency_ms
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE event_type IN ('LLM_RESPONSE', 'TOOL_COMPLETED')
GROUP BY event_type;
```

### 도구 및 상호작용 검사

#### Tool Provenance 분석

`v_tool_completed` 뷰 사용(권장):

```sql
SELECT
  tool_origin,
  tool_name,
  COUNT(*) as call_count,
  AVG(total_ms) as avg_latency_ms
FROM `your-gcp-project-id.your-dataset-id.v_tool_completed`
GROUP BY tool_origin, tool_name
ORDER BY call_count DESC;
```

#### HITL 상호작용 분석

```sql
SELECT
  timestamp,
  event_type,
  session_id,
  JSON_VALUE(content, '$.tool') as hitl_tool,
  content
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE event_type LIKE 'HITL_%'
ORDER BY timestamp DESC
LIMIT 20;
```

### 멀티모달 콘텐츠 분석

#### 멀티모달 콘텐츠 조회(`content_parts` 및 ObjectRef 사용)

```sql
SELECT
  timestamp,
  part.mime_type,
  part.object_ref.uri as gcs_uri
FROM `your-gcp-project-id.your-dataset-id.agent_events`,
UNNEST(content_parts) as part
WHERE part.mime_type LIKE 'image/%'
ORDER BY timestamp DESC;
```

#### BigQuery 원격 모델(Gemini)로 멀티모달 콘텐츠 분석

```sql
SELECT
  logs.session_id,
  -- Get a signed URL for the image
  STRING(OBJ.GET_ACCESS_URL(parts.object_ref, "r").access_urls.read_url) as signed_url,
  -- Analyze the image using a remote model (e.g., gemini-pro-vision)
  AI.GENERATE(
    ('Describe this image briefly. What company logo?', parts.object_ref)
  ) AS generated_result
FROM
  `your-gcp-project-id.your-dataset-id.agent_events` logs,
  UNNEST(logs.content_parts) AS parts
WHERE
  parts.mime_type LIKE 'image/%'
ORDER BY logs.timestamp DESC
LIMIT 1;
```

### AI 기반 근본 원인 분석

BigQuery ML과 Gemini를 사용해 실패한 세션을 자동으로 분석하고 오류의 근본 원인을
파악합니다.

```sql
DECLARE failed_session_id STRING;
-- Find a recent failed session
SET failed_session_id = (
    SELECT session_id
    FROM `your-gcp-project-id.your-dataset-id.agent_events`
    WHERE error_message IS NOT NULL
    ORDER BY timestamp DESC
    LIMIT 1
);

-- Reconstruct the full conversation context
WITH SessionContext AS (
    SELECT
        session_id,
        STRING_AGG(CONCAT(event_type, ': ', COALESCE(TO_JSON_STRING(content), '')), '\n' ORDER BY timestamp) as full_history
    FROM `your-gcp-project-id.your-dataset-id.agent_events`
    WHERE session_id = failed_session_id
    GROUP BY session_id
)
-- Ask Gemini to diagnose the issue
SELECT
    session_id,
    AI.GENERATE(
        ('Analyze this conversation log and explain the root cause of the failure. Log: ', full_history),
        endpoint => 'gemini-flash-latest'
    ).result AS root_cause_explanation
FROM SessionContext;
```

### 대화형 분석

[BigQuery Conversational
Analytics](https://cloud.google.com/bigquery/docs/conversational-analytics)를
사용해 자연어로 에이전트 로그를 분석할 수도 있습니다. `agent_events` 테이블에
연결된 대화형 분석 에이전트를 [BigQuery Agents
Hub](https://console.cloud.google.com/bigquery/agents_hub)에서 만든 뒤, 다음과
같이 질문할 수 있습니다.

- "Show me the error rate over time"
- "What are the most common tool calls?"
- "Identify sessions with high token usage"

## 컨텍스트 그래프 {#context-graph}

행 레벨의 `agent_events` 외에도 [BigQuery Agent Analytics SDK](https://github.com/GoogleCloudPlatform/BigQuery-Agent-Analytics-SDK)를 사용하여 **컨텍스트 그래프(context graph)**를 구체화할 수 있습니다. 이는 에이전트가 처리한 요청, 검토한 옵션, 선택한 결과 등 에이전트의 의사 결정을 쿼리할 수 있는 BigQuery [프로퍼티 그래프(property graph)](https://cloud.google.com/bigquery/docs/graph-overview)입니다. 단순히 이벤트가 로깅되었다는 사실만 기록하는 것이 아니라, 그래프 쿼리 언어(GQL)를 사용하여 의사 결정이 발생한 *이유*를 추적할 수 있도록 지원합니다.

![Context graph flow: an ADK agent's events flow through the BigQuery Agent Analytics plugin into the agent_events table; the SDK's bqaa context-graph command materializes a structured decision graph that auditors, operators, and executives consume through GQL in BigQuery Studio and Conversational Analytics — with no external graph database.](/integrations/assets/bigquery-agent-analytics-context-graph-flow.png)

그래프는 테이블 DDL과 `CREATE PROPERTY GRAPH` 스키마라는 두 개의 선언적 아티팩트로 정의되며, SDK의 `bqaa context-graph --property-graph` 명령은 이 아티팩트들과 활성 테이블 스키마로부터 추출 대상(가져올 엔티티 및 관계와 해당 열 유형)을 도출합니다. 일반적인 경우에는 별도의 온톨로지(ontology)나 바인딩(binding) 파일이 필요하지 않으며, AI 프롬프트를 조종하기 위한 설명, 엔티티 상속, 파생 속성 또는 열 이름 변경이 필요한 경우에만 명시적인 `ontology.yaml` / `binding.yaml`을 사용합니다.

로컬에서 한 번 실행하거나 Cloud Scheduler에 의해 트리거되는 Cloud Run 작업으로 예약하여 실행하세요. 이 작업은 읽기 전용 이벤트/쓰기 가능 그래프 데이터 세트 분리, 최소 권한 서비스 계정, 구조화된 JSON 로그 및 Cloud Monitoring 경고를 포함합니다. 운영 참조 정보(사전 요구사항, IAM 매트릭스, 권장 일정, JSON 로그 형태, 모니터링 및 삭제 방법)는 SDK 저장소에서 확인할 수 있습니다.

- [주기적 구체화(Periodic materialization) 코드랩](https://github.com/GoogleCloudPlatform/BigQuery-Agent-Analytics-SDK/blob/main/docs/codelabs/periodic_materialization.md) — 의사 결정 그래프를 엔드투엔드로 빌드하고 쿼리합니다.
- [예약된 배포 런북(Scheduled deploy runbook)](https://github.com/GoogleCloudPlatform/BigQuery-Agent-Analytics-SDK/blob/main/docs/guides/scheduled-context-graph-deploy.md) — 그래프를 무인 예약 배포 상태로 설정합니다.
- [배포 참조 정보(Cloud Run + Cloud Scheduler)](https://github.com/GoogleCloudPlatform/BigQuery-Agent-Analytics-SDK/blob/main/examples/context_graph/periodic_materialization/README.md) — 전체 IAM 매트릭스, 일정, 모니터링 및 Terraform 모듈입니다.

## 플러그인과 함께 Agent Runtime에 배포 {#deploy-agent-runtime}

BigQuery Agent Analytics 플러그인이 포함된 에이전트를 [Agent
Runtime](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)에
배포할 수 있습니다. 이 섹션에서는 ADK CLI를 사용한 배포 절차와, 대안으로 Agent
Platform SDK를 사용한 프로그래밍 방식 배포를 설명합니다.

!!! important "버전 요구사항"

    이 플러그인을 Agent Runtime에 배포하려면 ADK Python 버전 **1.24.0 이상**을
    사용하세요. 이전 버전에서는 플러그인의 비동기 로그 writer가 서버리스 런타임에
    의해 종료되기 전에 보류 중인 이벤트를 flush하지 못하는 문제가 있었습니다.
    1.24.0부터는 각 invocation 종료 시 동기식 flush를 수행해 모든 이벤트가
    기록되도록 합니다.

### 전제 조건

배포하기 전에 다음 항목을 포함해 일반 [Agent Runtime
설정](/ko/deploy/agent-runtime/deploy/#setup-cloud-project)을 완료하세요.

1. **Agent Platform API**와 **Cloud Resource Manager API**가 활성화된 Google Cloud 프로젝트
2. 대상 프로젝트의 **BigQuery 데이터 세트**(또는 올바른 권한이 있는 cross-project 데이터 세트)
3. 배포 아티팩트를 위한 **Cloud Storage staging 버킷**
4. 배포용 서비스 계정에 [IAM 권한](#iam-permissions)에 나열된 역할이 있어야 함
5. 코딩 환경이 `gcloud auth login` 및 `gcloud auth application-default login`으로
   [인증](/ko/deploy/agent-runtime/deploy/#prerequisites-coding-env)되어 있어야 함

### 1단계: 에이전트와 플러그인 정의

플러그인을 포함하는 `App` 객체가 있는 에이전트 프로젝트 폴더를 만듭니다. `App`
객체는 플러그인을 사용하는 Agent Runtime 배포에 필요합니다.

```
my_bq_agent/
├── __init__.py
├── agent.py
└── requirements.txt
```

```python title="my_bq_agent/__init__.py"
from . import agent
```

```python title="my_bq_agent/agent.py"
import os
import google.auth
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models.google_llm import Gemini
from google.adk.plugins.bigquery_agent_analytics_plugin import (
    BigQueryAgentAnalyticsPlugin,
    BigQueryLoggerConfig,
)
from google.adk.tools.bigquery import BigQueryToolset, BigQueryCredentialsConfig

# --- Configuration ---
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "your-gcp-project-id")
DATASET_ID = os.environ.get("BQ_DATASET", "agent_analytics")
# BQ_LOCATION is the BigQuery dataset location (multi-region "US"/"EU" or
# a single region like "us-central1"). This is separate from the Agent Platform
# region used by GOOGLE_CLOUD_LOCATION.
BQ_LOCATION = os.environ.get("BQ_LOCATION", "US")

os.environ["GOOGLE_GENAI_USE_ENTERPRISE"] = "True"

# --- Plugin ---
bq_analytics_plugin = BigQueryAgentAnalyticsPlugin(
    project_id=PROJECT_ID,
    dataset_id=DATASET_ID,
    location=BQ_LOCATION,
    config=BigQueryLoggerConfig(
        batch_size=1,
        batch_flush_interval=0.5,
        log_session_metadata=True,
    ),
)

# --- Tools ---
credentials, _ = google.auth.default(
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)
bigquery_toolset = BigQueryToolset(
    credentials_config=BigQueryCredentialsConfig(credentials=credentials)
)

# --- Agent ---
root_agent = Agent(
    model=Gemini(model="gemini-flash-latest"),
    name="my_bq_agent",
    instruction="You are a helpful assistant with access to BigQuery tools.",
    tools=[bigquery_toolset],
)

# --- App (required for Agent Runtime with plugins) ---
app = App(
    name="my_bq_agent",
    root_agent=root_agent,
    plugins=[bq_analytics_plugin],
)
```

```text title="my_bq_agent/requirements.txt"
google-adk[bigquery]
google-cloud-bigquery-storage
pyarrow
opentelemetry-api
opentelemetry-sdk
```

### 2단계: ADK CLI로 배포

`adk deploy agent_engine` 명령을 사용해 에이전트를 배포합니다. `--adk_app`
플래그는 어떤 `App` 객체를 사용할지 CLI에 알려줍니다.

```shell
PROJECT_ID=your-gcp-project-id
LOCATION=us-central1

adk deploy agent_engine \
    --project=$PROJECT_ID \
    --region=$LOCATION \
    --staging_bucket=gs://your-staging-bucket \
    --display_name="My BQ Analytics Agent" \
    --adk_app=agent.app \
    my_bq_agent
```

!!! tip "`--adk_app` 플래그"

    `--adk_app` 플래그는 `App` 객체의 모듈 경로와 변수 이름을
    `module.variable` 형식으로 지정합니다. 이 예시에서 `agent.app`은 `agent.py`의
    `app` 변수를 가리킵니다. 이를 통해 배포가 플러그인 구성을 올바르게 선택합니다.

배포가 성공하면 다음과 같은 출력이 표시됩니다.

```shell
AgentEngine created. Resource name: projects/123456789/locations/us-central1/reasoningEngines/751619551677906944
```

다음 단계에서 사용할 **Resource name**을 기록해 둡니다.

### 3단계: 배포된 에이전트 테스트

배포 후 Agent Platform SDK를 사용해 에이전트에 쿼리할 수 있습니다.

```python title="test_deployed_agent.py"
import uuid
import vertexai

PROJECT_ID = "your-gcp-project-id"
LOCATION = "us-central1"
AGENT_ID = "751619551677906944"  # from deployment output

vertexai.init(project=PROJECT_ID, location=LOCATION)
client = vertexai.Client(project=PROJECT_ID, location=LOCATION)

agent = client.agent_engines.get(
    name=f"projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{AGENT_ID}"
)

user_id = f"test_user_{uuid.uuid4().hex[:8]}"
for chunk in agent.stream_query(
    message="List datasets in my project", user_id=user_id
):
    print(chunk, end="", flush=True)
```

### 4단계: BigQuery에서 이벤트 확인

배포된 에이전트에 몇 차례 쿼리를 보낸 뒤 BigQuery 테이블을 조회해 이벤트가
기록되는지 확인합니다.

```sql
SELECT timestamp, event_type, agent, content
FROM `your-gcp-project-id.agent_analytics.agent_events`
ORDER BY timestamp DESC
LIMIT 20;
```

`INVOCATION_STARTING`, `LLM_REQUEST`, `LLM_RESPONSE`, `TOOL_STARTING`,
`TOOL_COMPLETED`, `INVOCATION_COMPLETED` 같은 이벤트가 보여야 합니다.

### 대안: Agent Platform SDK로 배포

Agent Platform SDK를 직접 사용해 프로그래밍 방식으로 배포할 수도 있습니다. 이는
CI/CD 파이프라인 또는 커스텀 배포 워크플로에 유용합니다.

```python title="deploy.py"
import vertexai
from my_bq_agent.agent import app

PROJECT_ID = "your-gcp-project-id"
LOCATION = "us-central1"
STAGING_BUCKET = "gs://your-staging-bucket"

vertexai.init(
    project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET
)
client = vertexai.Client(project=PROJECT_ID, location=LOCATION)

remote_app = client.agent_engines.create(
    agent=app,
    config={
        "display_name": "My BQ Analytics Agent",
        "staging_bucket": STAGING_BUCKET,
        "requirements": [
            "google-adk[bigquery]",
            "google-cloud-aiplatform[agent_engines]",
            "google-cloud-bigquery-storage",
            "pyarrow",
            "opentelemetry-api",
            "opentelemetry-sdk",
        ],
    },
)
print(f"Deployed agent: {remote_app.api_resource.name}")
```

### 문제 해결

배포 후 BigQuery 테이블에 이벤트가 표시되지 않으면 다음을 확인하세요.

1. **ADK 버전 확인:** requirements에 `google-adk>=1.24.0`이 있는지 확인합니다.
   이전 버전은 서버리스 런타임이 프로세스를 중단하기 전에 보류 이벤트를 flush하지
   않습니다.

2. **디버그 로깅 활성화:** 조용한 오류를 드러내려면 `agent.py` 상단에 다음을
   추가합니다.

    ```python
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("google_adk").setLevel(logging.DEBUG)
    ```

3. **IAM 권한 확인:** Agent Runtime 서비스 계정에는 대상 테이블의
   `roles/bigquery.dataEditor`와 프로젝트의 `roles/bigquery.jobUser`가 필요합니다.
   **cross-project** 로깅의 경우 원본 프로젝트에서 BigQuery API가 활성화되어
   있고, 서비스 계정에 대상 테이블의 `bigquery.tables.updateData`가 있는지도
   확인하세요.

4. **플러그인 초기화 확인:** Cloud Logging에서 `resource.type="reasoning_engine"`으로
   필터링하고 플러그인 시작 메시지나 오류 로그를 찾습니다.

5. **디버깅용 즉시 flush 사용:** 버퍼링 문제를 배제하려면
   `BigQueryLoggerConfig`에서 `batch_size=1`, `batch_flush_interval=0.1`을
   설정합니다.

## 보안: 민감한 자격 증명 로깅 방지 {#security-credentials}

!!! warning "OAuth 토큰, API 키, 클라이언트 보안 비밀을 로깅하지 마세요"

    BigQuery Agent Analytics 플러그인은 도구 인수, LLM 프롬프트, 인증 관련 이벤트(HITL 자격 증명 요청 등)를 포함하여 자세한 이벤트 페이로드를 캡처합니다. Python에서 기본 제공 수정(redaction)은 소문자 변환 및 하이픈 정규화 후 키 이름을 정확히 일치시키므로 `clientSecret` 또는 `accessToken`과 같은 카멜표기법(camelCase) 변형은 일치하지 **않습니다**. Go는 추가로 밑줄과 하이픈 구분 기호를 무시하고 이러한 변형을 일치시키며, 이 경고의 나머지 부분은 Python의 자격 증명 요청 페이로드에 관한 것입니다. ADK는 `adk_request_credential` 인수를 카멜표기법 별칭으로 직렬화하므로, `AuthenticatedFunctionTool` OAuth2 흐름에서 `client_secret` 및 `access_token` 값이 `content` 열에 기록될 수 있습니다([google/adk-python#3845](https://github.com/google/adk-python/issues/3845)). ADK Python v2.9.0 이상에서는 `adk_request_credential` 요청에서 구성된 OAuth2 클라이언트 보안 비밀(client secret)을 제거하며, ADK Python v2.12.0 이상에서는 API 키, HTTP Basic 비밀번호, HTTP bearer 토큰 및 추가 HTTP 헤더도 제거합니다. OAuth2 액세스 토큰은 여전히 제거되지 않습니다. ADK가 해당 요청에서 제거하지 않는 필드는 카멜표기법 이름을 유지하며 기본 제공 수정과 일치하지 않습니다. 자체 도구 인수의 카멜표기법 키도 마찬가지입니다. 수정 기능은 범용 데이터 손실 방지(DLP) 시스템이 아니므로 애플리케이션별 키 또는 자유 형식 텍스트에 포함된 시크릿도 BigQuery에 기록될 수 있습니다.

플러그인에는 일반적인 시크릿을 자동으로 보호하는 **기본 제공 수정** 기능이 포함되어 있습니다. 추가 제어가 필요한 경우 그 위에 커스텀 수정을 계층화할 수 있습니다.

### 기본 제공 수정(Built-in redaction) {#built-in-redaction}

<div class="language-support-tag">
  <span class="lst-supported">ADK 지원 버전</span><span class="lst-python">Python</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v1.7.0</span>
</div>

Python 플러그인은 키 이름을 소문자로 정규화하고 하이픈을 밑줄처럼 취급합니다. 구조화된 `content` 또는 `attributes`의 어디에 나타나든 다음 키의 값을 재귀적으로 `[REDACTED]`로 바꿉니다.

`client_secret`, `access_token`, `refresh_token`, `id_token`, `api_key`,
`password`, `private_key`, `proxy_authorization`, `google_access_id`, `sig`,
`signature`, `token`, `secret`, `authorization`, `x_api_key`,
`x_amz_credential`, `x_amz_signature`, `x_goog_credential`,
`x_goog_security_token`, `x_goog_signature`

Python은 **`temp:`** 상태 값을 `[REDACTED]`로 바꿉니다. Go는 로깅 전에 `state_delta`에서 최상위 소문자 **`temp:`** 항목을 제거하며 아무것도 남지 않으면 `STATE_DELTA` 행을 내보내지 않습니다. 구조화된 콘텐츠 및 속성의 기타 **`temp:`** 값은 `[REDACTED]`로 바뀝니다. `secret:` 접두사는 특별한 의미가 없습니다. 호출 로컬 민감한 상태에는 `temp:`를 사용하거나, 애플리케이션별 상태 값이 로깅에 도달하기 전에 정제하세요. 커스텀 콘텐츠 포맷터는 상태 속성을 수정하지 않습니다.

!!! warning "수정 안내: 세션 상태에서는 `temp:`만 수정됩니다"

    이전 문서에서는 `secret:` 접두사가 붙은 키도 수정된다고 잘못 명시되었습니다. 플러그인은 `temp:` 접두사만 일치시킵니다. 세션 상태에 `secret:`(예: `secret:token`) 아래에 시크릿을 저장하는 경우 커스텀 `content_formatter`로 마스킹하지 않는 한 일반 텍스트로 로깅됩니다. 해당 안내를 신뢰했던 경우 기존 `agent_events` 테이블에서 `temp:`가 아닌 키 아래에 기록된 값이 있는지 감사하세요.

플러그인은 또한 `error_message`, 에이전트 및 실행 트레이스백, 외부 URI에서 자격 증명 패턴을 정제합니다. 여기에는 인증 헤더, bearer 및 basic 자격 증명, 서명된 URL 쿼리 매개변수, 위의 민감한 이름을 사용하는 키/값 조각이 포함됩니다. 안전하게 다시 작성할 수 없는 인코딩된 자격 증명 구문은 fail-closed(차단) 처리됩니다.

!!! info "별도 구성 불필요"

    구조화된 속성 및 상태 로깅에 대해 기본 제공 수정이 항상 활성화되어 있으며, 속성 값 내의 중첩된 딕셔너리 및 JSON 인코딩 문자열에 재귀적으로 적용됩니다. 커스텀 `content_formatter`는 원시 콘텐츠에 대해 **먼저** 실행됩니다. 오류가 발생하거나 지원되지 않는 유형을 반환하는 경우 Python은 원본 콘텐츠 대신 `[FORMATTER_FAILED]`를 작성하고 `formatter_failed` 인시던트 카운터를 증가시킵니다.

    Python `content_formatter`는 `None`, `str`, `dict` 또는 `list`(또는 이들의 하위 클래스)를 반환하거나 정확한 `types.Content`, `types.Part` 또는 `LlmRequest`를 반환할 수 있습니다. ADK Python v2.11.0 이상에서는 포맷터 실패가 행의 `error_message`에도 기록되며, 예외 또는 반환 값 클래스 이름만 표시됩니다(예: `content_formatter raised ImportError`, `content_formatter raised <subclass of ValueError>`, 또는 `content_formatter returned unsupported type tuple`). 이벤트에 이미 `TOOL_ERROR`와 같은 `error_message`가 있는 경우 해당 메시지가 먼저 유지되고 그 뒤에 세미콜론과 포맷터 실패가 이어집니다. 행의 `status`는 변경되지 않으므로 성공적인 이벤트는 `status` `OK`를 유지하지만 null이 아닌 모든 `error_message`를 오류로 처리하는 쿼리에서는 해당 행이 여전히 플래그 지정됩니다.

    예외를 발생시키는 포맷터를 디버깅하려면 `debug_content_formatter_errors=True`로 설정하여 플러그인의 Python 로그 경고에 제한된 트레이스백을 추가하세요. 트레이스백에는 포맷팅되지 않은 콘텐츠가 포함될 수 있으며 구성된 모든 로그 핸들러에 도달하므로 해당 콘텐츠를 볼 수 있는 환경에서만 활성화하세요. 이는 BigQuery에는 기록되지 않습니다.

!!! note "Go의 기본 제공 수정"

    Go 플러그인(`google.golang.org/adk/plugin/agentanalytics`)은 기본적으로 기본 제공 수정을 활성화합니다(`DisableSensitiveKeyRedaction: false`). 키 이름은 소문자로 변환하고 밑줄(`_`)과 하이픈(`-`)을 제거하여 정규화되므로, `snake_case`, `kebab-case`, `camelCase` 변형(예: `api_key`, `api-key`, `apiKey`, `clientSecret`, `accessToken`, `refreshToken`, `idToken`, `privateKey`, `sessionToken`, `secretAccessKey`, `codeVerifier`, `authCode`, `passphrase`)이 일치하여 구조화된 `content` 및 `attributes` 전반에서 `"[REDACTED]"`로 바뀝니다(`DisableSensitiveKeyRedaction: true`가 아닌 경우).

    또한 Go 플러그인은 다음 작업을 수행합니다:

    - 로깅 전에 `state_delta`에서 최상위 소문자 **`temp:`** 항목을 제거하고 아무것도 남지 않으면 `STATE_DELTA` 행을 내보내지 않으며, 구조화된 콘텐츠 및 속성의 기타 **`temp:`** 값을 `"[REDACTED]"`로 바꾸고, `credential` 또는 `credentials` 아래의 전체 자격 증명 컨테이너 엔벨로프를 수정합니다.
    - 외부 URI에서 자격 증명 userinfo 및 민감한 쿼리 매개변수를 제거하고(민감한 쿼리 값을 안전하게 다시 작성할 수 없는 경우 `"[REDACTED_SENSITIVE_URI]"`로 fail-closed 처리), `error_message` 및 `uri`에서 `Authorization` 헤더, `Bearer` 및 `Basic` 토큰, 포함된 JSON 자격 증명 조각을 제거합니다.
    - 기본 제공 수정 전에 커스텀 `ContentFormatter`(`func(content any, eventType string) (any, error)`)를 실행합니다. `ContentFormatter`가 nil이 아닌 오류를 반환하거나 패닉이 발생하면 Go 플러그인은 `content`에 `"[FORMATTER_FAILED]"`를 작성하고, `content_parts`를 작성하지 않으며, `error_message`에 `content_formatter raised <error type>` 또는 `content_formatter panicked`를 추가하고, `DropStats().FormatterFailureDrops`를 증가시킵니다.

!!! note "Java의 기본 제공 수정"

    Java 플러그인은 v1.7.0 이상에서 기본 제공 수정을 포함합니다.
    세션 상태 및 상태 델타를 포함하여 조립된 `attributes` 트리 전반에서 `client_secret`, `access_token`, `refresh_token`, `id_token`, `api_key`, `password`(대소문자 구분 없음) 및 **`temp:`** 접두사가 붙은 모든 키를 재귀적으로 수정합니다. 시크릿을 다른 상태 범위에 두지 않거나 커스텀 `contentFormatter`로 마스킹하세요.

    커스텀 Java `contentFormatter`는 **스레드 안전**해야 하며(호출 간에 동시에 호출됨), **빠르고 비차단(non-blocking)**이어야 하고(이벤트 처리 경로에서 실행됨), 수신한 콘텐츠를 변경하는 대신 **새 객체**를 반환해야 합니다. 예외가 발생하는 경우 Java 플러그인은 포맷되지 않은 페이로드를 기록하는 대신 행의 콘텐츠를 드롭(fail-closed)합니다.

### `content_formatter`를 사용하여 추가 시크릿 수정

커스텀 `content_formatter` 함수(Go의 `ContentFormatter`, Java의 `contentFormatter`)를 제공하여 민감한 필드가 기록되기 전에 제거하거나 마스킹합니다.

=== "Python"

    ```python
    import json
    import re
    from typing import Any

    SENSITIVE_KEYS = {"client_secret", "access_token", "refresh_token", "api_key", "secret"}

    def redact_credentials(event_content: Any, event_type: str) -> str:
        """로깅된 콘텐츠에서 OAuth 시크릿 및 토큰을 수정합니다."""
        if isinstance(event_content, dict):
            text = json.dumps(event_content)
        else:
            text = str(event_content)

        for key in SENSITIVE_KEYS:
            # JSON 유사 문자열의 값 수정: "client_secret": "GOCSPX-xxx"
            text = re.sub(
                rf'("{key}"\s*:\s*)"[^"]*"',
                rf'\1"[REDACTED]"',
                text,
                flags=re.IGNORECASE,
            )
        return text

    config = BigQueryLoggerConfig(
        content_formatter=redact_credentials,
        # ... 기타 옵션
    )
    ```

=== "Go"

    Go에서 포맷터는 최종 JSON이 아니라 원시 타입이 지정된 콘텐츠 페이로드(예: `string`, `*genai.Content`, `*model.LLMRequest`, `*model.LLMResponse` 또는 `map[string]any`)를 받으며, `attributes.state_delta`와 같은 속성은 변환하지 않습니다. 수정하는 모든 포인터, 슬라이스 또는 맵(`*genai.Content` 내부의 `Part.Text`, `Part.ExecutableCode.Code`, `Part.CodeExecutionResult.Output`, `Part.FunctionCall.Args`, `Part.FunctionResponse.Response` 포함)을 복제(clone)하고 라이브 페이로드를 직접 변경하지 마세요.

    아래 헬퍼는 편집하는 값을 복제하고 중첩 수준이 50을 넘으면 중지합니다. 과도하게 중첩되었거나 순환하는 페이로드는 오류를 반환하므로 플러그인은 프로세스 충돌 위험을 감수하는 대신 `[FORMATTER_FAILED]`를 기록합니다. 이러한 헬퍼는 JSON 형태의 `map[string]any` 및 `[]any` 값(및 `[]string`, `map[string]string`, `[]map[string]any`)을 재귀적으로 순회합니다. 도구가 반환하는 다른 구체적인 타입에 대해 제한된 케이스를 추가하거나 포맷팅 전에 해당 값을 정규화하고, 이 수정 로직에 의존하기 전에 실제 페이로드를 테스트하세요:

    ```go
    package analytics

    import (
    	"fmt"
    	"regexp"
    	"strings"

    	"google.golang.org/adk/plugin/agentanalytics"
    	"google.golang.org/adk/v2/model"
    	"google.golang.org/genai"
    )

    var ssnPattern = regexp.MustCompile(`\b\d{3}-\d{2}-\d{4}\b`)

    func redactCustomSecrets(content any, eventType string) (any, error) {
    	return redactCustomSecretsAtDepth(content, eventType, 0)
    }

    func redactCustomSecretsAtDepth(content any, eventType string, depth int) (any, error) {
    	if depth >= 50 {
    		return nil, fmt.Errorf("redaction nesting limit exceeded")
    	}
    	switch v := content.(type) {
    	case string:
    		return ssnPattern.ReplaceAllString(v, "[REDACTED_SSN]"), nil
    	case *genai.Content:
    		return redactGenAIContentSecrets(v, eventType, depth+1)
    	case *model.LLMRequest:
    		if v == nil {
    			return nil, nil
    		}
    		cloned := *v
    		if len(v.Contents) > 0 {
    			cloned.Contents = make([]*genai.Content, len(v.Contents))
    			for i, c := range v.Contents {
    				redactedContent, err := redactGenAIContentSecrets(c, eventType, depth+1)
    				if err != nil {
    					return nil, err
    				}
    				cloned.Contents[i] = redactedContent
    			}
    		}
    		if v.Config != nil && v.Config.SystemInstruction != nil {
    			redactedSys, err := redactGenAIContentSecrets(v.Config.SystemInstruction, eventType, depth+1)
    			if err != nil {
    				return nil, err
    			}
    			cfgCopy := *v.Config
    			cfgCopy.SystemInstruction = redactedSys
    			cloned.Config = &cfgCopy
    		}
    		return &cloned, nil
    	case *model.LLMResponse:
    		if v == nil {
    			return nil, nil
    		}
    		redactedContent, err := redactGenAIContentSecrets(v.Content, eventType, depth+1)
    		if err != nil {
    			return nil, err
    		}
    		cloned := *v
    		cloned.Content = redactedContent
    		return &cloned, nil
    	case map[string]any:
    		if v == nil {
    			return map[string]any(nil), nil
    		}
    		cloned := make(map[string]any, len(v))
    		for k, val := range v {
    			if depth+1 >= 50 {
    				return nil, fmt.Errorf("redaction nesting limit exceeded")
    			}
    			if strings.EqualFold(k, "internal_token") {
    				cloned[k] = "[REDACTED]"
    				continue
    			}
    			redactedVal, err := redactCustomSecretsAtDepth(val, eventType, depth+1)
    			if err != nil {
    				return nil, err
    			}
    			cloned[k] = redactedVal
    		}
    		return cloned, nil
    	case map[string]string:
    		if v == nil {
    			return map[string]string(nil), nil
    		}
    		cloned := make(map[string]string, len(v))
    		for k, val := range v {
    			if depth+1 >= 50 {
    				return nil, fmt.Errorf("redaction nesting limit exceeded")
    			}
    			if strings.EqualFold(k, "internal_token") {
    				cloned[k] = "[REDACTED]"
    				continue
    			}
    			redactedVal, err := redactCustomSecretsAtDepth(val, eventType, depth+1)
    			if err != nil {
    				return nil, err
    			}
    			cloned[k], _ = redactedVal.(string)
    		}
    		return cloned, nil
    	case []any:
    		if v == nil {
    			return []any(nil), nil
    		}
    		cloned := make([]any, len(v))
    		for i, item := range v {
    			redactedItem, err := redactCustomSecretsAtDepth(item, eventType, depth+1)
    			if err != nil {
    				return nil, err
    			}
    			cloned[i] = redactedItem
    		}
    		return cloned, nil
    	case []string:
    		if v == nil {
    			return []string(nil), nil
    		}
    		cloned := make([]string, len(v))
    		for i, item := range v {
    			redactedItem, err := redactCustomSecretsAtDepth(item, eventType, depth+1)
    			if err != nil {
    				return nil, err
    			}
    			cloned[i], _ = redactedItem.(string)
    		}
    		return cloned, nil
    	case []map[string]any:
    		if v == nil {
    			return []map[string]any(nil), nil
    		}
    		cloned := make([]map[string]any, len(v))
    		for i, item := range v {
    			redactedItem, err := redactCustomSecretsAtDepth(item, eventType, depth+1)
    			if err != nil {
    				return nil, err
    			}
    			cloned[i], _ = redactedItem.(map[string]any)
    		}
    		return cloned, nil
    	default:
    		return content, nil
    	}
    }

    func redactGenAIContentSecrets(c *genai.Content, eventType string, depth int) (*genai.Content, error) {
    	if depth >= 50 {
    		return nil, fmt.Errorf("redaction nesting limit exceeded")
    	}
    	if c == nil {
    		return nil, nil
    	}
    	cloned := *c
    	if len(c.Parts) > 0 {
    		cloned.Parts = make([]*genai.Part, len(c.Parts))
    		for i, p := range c.Parts {
    			if p == nil {
    				continue
    			}
    			partCopy := *p
    			if partCopy.Text != "" {
    				partCopy.Text = ssnPattern.ReplaceAllString(partCopy.Text, "[REDACTED_SSN]")
    			}
    			if partCopy.ExecutableCode != nil {
    				codeCopy := *partCopy.ExecutableCode
    				codeCopy.Code = ssnPattern.ReplaceAllString(codeCopy.Code, "[REDACTED_SSN]")
    				partCopy.ExecutableCode = &codeCopy
    			}
    			if partCopy.CodeExecutionResult != nil {
    				resultCopy := *partCopy.CodeExecutionResult
    				resultCopy.Output = ssnPattern.ReplaceAllString(resultCopy.Output, "[REDACTED_SSN]")
    				partCopy.CodeExecutionResult = &resultCopy
    			}
    			if partCopy.FunctionCall != nil {
    				fcCopy := *partCopy.FunctionCall
    				if fcCopy.Args != nil {
    					redactedArgs, err := redactCustomSecretsAtDepth(fcCopy.Args, eventType, depth+1)
    					if err != nil {
    						return nil, err
    					}
    					if argsMap, ok := redactedArgs.(map[string]any); ok {
    						fcCopy.Args = argsMap
    					}
    				}
    				partCopy.FunctionCall = &fcCopy
    			}
    			if partCopy.FunctionResponse != nil {
    				frCopy := *partCopy.FunctionResponse
    				if frCopy.Response != nil {
    					redactedResp, err := redactCustomSecretsAtDepth(frCopy.Response, eventType, depth+1)
    					if err != nil {
    						return nil, err
    					}
    					if respMap, ok := redactedResp.(map[string]any); ok {
    						frCopy.Response = respMap
    					}
    				}
    				partCopy.FunctionResponse = &frCopy
    			}
    			cloned.Parts[i] = &partCopy
    		}
    	}
    	return &cloned, nil
    }

    func newRedactedConfig() agentanalytics.Config {
    	cfg := agentanalytics.DefaultConfig()
    	cfg.ProjectID = "your-gcp-project-id"
    	cfg.DatasetID = "agent_analytics"
    	cfg.TableName = "agent_events"
    	cfg.ContentFormatter = redactCustomSecrets
    	return cfg
    }
    ```

=== "Java"

    ```java
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.models.Gemini;
    import com.google.adk.models.LlmRequest;
    import com.google.adk.models.LlmResponse;
    import com.google.adk.runner.Runner;
    import com.google.genai.types.Content;
    import com.google.genai.types.GenerateContentConfig;
    import com.google.genai.types.Part;
    import java.util.ArrayList;
    import java.util.List;

    public final class AgentContentFormatter {
      private static final String PROJECT_ID = "your-gcp-project-id";
      private static final String DATASET_ID = "your-gcp-dataset_id";
      private static final String TABLE_ID = "your-gcp-table";
      private static final String API_KEY = "your-api_key";
      private static final String GCS_BUCKET_NAME = "your-gcs-bucket-name";

      /** 테스트하려는 포맷터 로직을 반환합니다. */
      private static Object formatter(Object content, String eventType) {
        if (content instanceof LlmRequest req) {
          List<Content> maskedContents = new ArrayList<>();
          for (Content c : req.contents()) {
            maskedContents.add(maskContent(c));
          }
          return req.toBuilder().contents(maskedContents).build();
        } else if (content instanceof LlmResponse res) {
          if (res.content().isPresent()) {
            return res.toBuilder().content(maskContent(res.content().get())).build();
          }
          return res;
        } else if (content instanceof Content content2) {
          return maskContent(content2);
        } else if (content instanceof Map<?, ?> map) {
          Map<Object, Object> maskedMap = new LinkedHashMap<>();
          for (Map.Entry<?, ?> entry : map.entrySet()) {
            maskedMap.put(entry.getKey(), formatter(entry.getValue(), eventType));
          }
          return maskedMap;
        }
        return content;
      }

      private static Content maskContent(Content originalContent) {
        if (originalContent.parts().isPresent()) {
          List<Part> maskedParts = new ArrayList<>();
          for (Part part : originalContent.parts().get()) {
            if (part.text().isPresent() && part.text().get().contains("secret")) {
              String maskedText = part.text().get().replace("secret", "****");
              maskedParts.add(part.toBuilder().text(maskedText).build());
            } else {
              maskedParts.add(part);
            }
          }
          return originalContent.toBuilder().parts(maskedParts).build();
        }
        return originalContent;
      }

      public static void main(String[] args) throws Exception {
        // 1. 커스텀 포맷터로 Config 설정
        BigQueryLoggerConfig config =
            BigQueryLoggerConfig.builder()
                .projectId(PROJECT_ID)
                .datasetId(DATASET_ID)
                .tableName(TABLE_ID)
                .gcsBucketName(GCS_BUCKET_NAME)
                .contentFormatter(AgentContentFormatter::formatter)
                .logMultiModalContent(true)
                .build();

        // 2. 플러그인 설정
        BigQueryAgentAnalyticsPlugin plugin = new BigQueryAgentAnalyticsPlugin(config);

        // 3. 응답하는 에이전트 설정
        LlmAgent agent =
            LlmAgent.builder()
                .model(
                    Gemini.builder()
                        .modelName("gemini-3-flash-preview") // 적절한 모델 사용
                        .apiKey(API_KEY)
                        .build())
                .name("bq_demo_agent")
                .instruction("You are a helpful assistant")
                .generateContentConfig(GenerateContentConfig.builder().temperature(0.5f).build())
                .build();

        // 4. Runner 설정
        Runner runner = Runner.builder().agent(agent).appName("test_app").plugins(plugin).build();
        // 5. runner를 사용하여 몇 가지 시나리오 실행
        ...
      }

      private AgentContentFormatter() {}
    }
    ```

### `event_denylist`를 사용하여 자격 증명 이벤트 건너뛰기

인증 관련 이벤트를 기록할 필요가 없는 경우 전체적으로 제외합니다.

=== "Python"

    ```python
    config = BigQueryLoggerConfig(
        event_denylist=[
            "HITL_CREDENTIAL_REQUEST",
            "HITL_CREDENTIAL_REQUEST_COMPLETED",
        ],
        # ... 기타 옵션
    )
    ```

=== "Go"

    ```go
    cfg := agentanalytics.DefaultConfig()
    cfg.ProjectID = "your-gcp-project-id"
    cfg.DatasetID = "agent_analytics"
    cfg.TableName = "agent_events"
    cfg.EventDenylist = []string{
    	agentanalytics.EventHITLCredentialRequest,
    	agentanalytics.EventHITLCredentialCompleted,
    }
    ```

=== "Java"

    ```java
    import com.google.common.collect.ImmutableList;

    BigQueryLoggerConfig config = BigQueryLoggerConfig.builder()
        .eventDenylist(ImmutableList.of(
            "HITL_CREDENTIAL_REQUEST",
            "HITL_CREDENTIAL_REQUEST_COMPLETED"
        ))
        // ... 기타 옵션
        .build();
    ```

### 일반적인 모범 사례

- 에이전트 소스 코드에 **시크릿을 절대 하드코딩하지 마세요**. OAuth 클라이언트 시크릿 및 API 키에는 환경 변수 또는 보안 비밀 관리자(예: Google Cloud Secret Manager)를 사용하세요.
- 기록된 이벤트 데이터를 읽을 수 있는 사용자를 제한하려면 IAM을 사용하여 **BigQuery 테이블 액세스를 제한**하세요.
- 예상치 못한 민감한 데이터가 캡처되지 않는지 확인하기 위해 정기적으로 **로그를 감사**하세요.

## 운영

### 추적 및 관측 가능성 {#tracing-and-observability}

플러그인은 부모-자식 실행 트리(에이전트 → LLM 호출 / 도구 호출)가 BigQuery에서 깔끔하게 재구성될 수 있도록 방출되는 모든 행에 `trace_id`, `span_id`, `parent_span_id` 열을 채웁니다.

- **내부 span 추적, OTel span 내보내기 없음.** 플러그인은 16자리 16진수 `span_id` 값의 자체 내부 스택에서 부모-자식 계층 구조를 추적합니다. Python 및 Java에서는 주변 OTel span이 활성화되어 있을 때 루트 호출 span이 해당 ID를 재사용하며(러너의 호출 span과 일치시킴), Go에서는 플러그인이 항상 자체 16자리 16진수 루트 `span_id`를 생성하고 주변 OTel span ID를 `parent_span_id`에 기록합니다. 하위 BQAA span은 내부적으로 생성됩니다. 구성된 OpenTelemetry `TracerProvider`에서 `tracer.start_span(...)`을 호출하지 **않으므로**, 계측이 구성된 내보내기 도구(exporter)에 전달되지 않습니다. 이는 Agent Engine 원격 분석(`GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY=true`)이 활성화되어 있거나 호스트 프로세스에 다른 Cloud Trace 내보내기 도구를 연결할 때 Cloud Trace에 중복 span이 발생하는 것을 방지합니다. 동일한 내부 ID 전용 span 추적이 Go 플러그인 및 Java 플러그인(v1.7.0+)에도 적용됩니다. 이전 Java 빌드는 프레임워크 span 옆에 중복으로 나타날 수 있는 플러그인 소유 OpenTelemetry span을 생성했습니다.
- **주변 OTel span이 있는 경우 `trace_id` 상속.** 주변 런타임이 Agent Engine의 호출 span, ADK `Runner` 호출 span(Python 및 Java) 또는 에이전트 실행 전에 시작한 임의의 span과 같은 OTel span을 이미 시작한 경우, 플러그인은 해당 `trace_id`를 읽어 모든 BigQuery 행에 스탬프합니다. 따라서 BigQuery 행은 공유된 `trace_id`를 통해 기존 Cloud Trace 트레이스와 깔끔하게 조인됩니다.
- **주변 span이 없는 경우 폴백.** 활성 주변 OTel span이 없는 경우(예: 호스트 측 트레이서가 구성되지 않은 비 Agent Engine 배포) Python은 호출당 무작위 32자리 16진수 `trace_id`를 생성합니다. 주변 span이 없을 때 Go는 `invocation_id`가 비어 있으면 무작위 32자리 16진수 `trace_id`를 생성하고, 그렇지 않으면 플러그인당 무작위 시드와 호출 ID에 대해 SHA-256을 사용하여 해당 플러그인 인스턴스 내에서 안정적인 32자리 16진수 ID를 생성합니다. Java는 `trace_id`로 ADK 호출 ID로 폴백하므로 외부 트레이서 설정 없이도 BigQuery에서 부모-자식 계층 구조가 항상 보존됩니다.
- **부모-자식 관계가 명시적으로 보존됨.** 플러그인의 내부 스택은 각 하위 작업(`LLM_REQUEST`, `TOOL_STARTING` 등)이 올바른 호출 또는 에이전트 수준 `span_id`를 `parent_span_id`로 참조하도록 보장합니다.

### 공개 메서드

=== "Python"

    플러그인은 수명 주기 관리를 위해 다음과 같은 여러 공개 메서드를 노출합니다:

    - **`await plugin.flush()`**: 현재 이벤트 루프와 연결된 보류 중인 이벤트의 쓰기가 완료될 때까지 대기합니다.
    - **`await plugin.shutdown(timeout=None, *, close_background_transport=False)`**: 보류 중인 이벤트를 플러시하고 리소스를 해제하여 플러그인을 정상적으로 종료합니다. 선택적 `timeout` 매개변수는 구성의 `shutdown_timeout`을 재정의합니다. 플러그인이 [공유 백그라운드 기록기](#shared-background-writer)를 사용하는 경우 종료 시 플러그인이 해당 기록기에서 분리되고 기록기는 계속 실행 상태로 남습니다. 이 플러그인의 테이블 및 자격 증명에 대한 공유 기록기도 비우고 중지하려면 `close_background_transport=True`를 전달하세요.
    - **`await plugin.close(timeout=None, *, close_background_transport=False)`**: 플러그인 관리자 수명 주기 계약을 실행합니다. 동일한 인수로 `shutdown()`에 위임하며 러너가 플러그인을 닫을 때 자동으로 호출됩니다.
    - **`await BigQueryAgentAnalyticsPlugin.close_shared_background_transports(timeout=10.0)`** (Python v2.10.0+): 독립 실행형 스크립트, 프로세스 종료 핸들러 또는 테스트 정리 픽스처 등 프로세스의 모든 공유 백그라운드 기록기를 비우고 중지합니다. 기록기를 드레인하지 못하거나 `timeout` 내에 완료되지 않으면 예외가 발생합니다(한 기록기가 실패한 경우 기록기의 오류 또는 `TimeoutError`, 여러 기록기가 실패한 경우 `RuntimeError`). 동일한 작업이 `google.adk.plugins.bigquery_agent_analytics_plugin`의 모듈 수준 함수 `close_shared_background_transports(timeout=10.0)`로도 제공됩니다.
    - **`await plugin.create_analytics_views()`**: 이벤트 유형별 모든 분석 뷰를 수동으로 (재)생성합니다. 스키마 업그레이드 후 또는 뷰를 새로고침해야 할 때 유용합니다.
    - **`await plugin.create_eval_views()`** (Python v2.13.0+): `create_eval_views=False`인 경우에도 에이전트 평가 뷰(`{view_prefix}_eval_session` 및 `{view_prefix}_eval_turn`)를 수동으로 (재)생성합니다. 자세한 내용은 [에이전트 평가 뷰](#agent-evaluation-views)를 참고하세요.
    - **`plugin.get_drop_stats()`**: 원인별 전송 손실 및 콘텐츠 정제 인시던트 수의 스냅샷을 반환합니다. 자세한 내용은 [드롭된 이벤트 관측 가능성](#dropped-event-observability)을 참고하세요.

=== "Go"

    Go(`google.golang.org/adk/plugin/agentanalytics`)에서는 플러그인 수명 주기 및 운영 헬퍼가 ADK `*plugin.Plugin` 핸들과 언래핑된 `*agentanalytics.BigQueryAgentAnalyticsPlugin`을 통해 노출됩니다:

    - **`adkPlugin.Close() error`**: 대기 중인 이벤트를 드레인하고, 백그라운드 배치 프로세서를 중지하며(각 플러시/업로드 단계는 `ShutdownTimeout`, 기본값 `10s`로 제한되며 총 월클럭 시간은 최대 약 2.5배 소요 가능), 플러그인 소유의 BigQuery, Storage Write 및 GCS 클라이언트를 닫습니다. ADK Go의 러너는 플러그인을 자동으로 닫지 않으므로 종료하기 전에 `adkPlugin.Close()`를 직접 호출하세요(예: 생성 직후 `defer bqPlugin.Close()`).
    - **`agentanalytics.AsBigQueryAgentAnalyticsPlugin(adkPlugin)`**: ADK `*plugin.Plugin` 핸들에서 기본 `*agentanalytics.BigQueryAgentAnalyticsPlugin`을 언래핑합니다. 언래핑된 핸들은 `adkPlugin.Close()`가 완료된 후에도 계속 액세스할 수 있습니다.
    - **`bqPlugin.DropStats() agentanalytics.DropStats`**: 드롭된 이벤트 및 포맷터 실패 수(`QueueFullDrops`, `AppendFailureDrops`, `FormatterFailureDrops`, `ShutdownDrops`, `TotalDrops`)의 스냅샷을 반환합니다. 자세한 내용은 [드롭된 이벤트 관측 가능성](#dropped-event-observability)을 참고하세요.
    - **`bqPlugin.SyncViews(ctx context.Context) error`**: `DisableCreateViews: true`인 경우에도 모든 25개의 이벤트 유형별 BigQuery 분석 뷰(`CREATE OR REPLACE VIEW`)를 수동으로 생성하거나 새로고침합니다. 플러그인이 `NewBigQueryAgentAnalyticsPluginWithClients(..., nil, ...)`(`bqClient == nil`)로 생성된 경우 `SyncViews`는 `agentanalytics: BigQuery client is not configured for view creation`을 반환합니다.
    - **`cfg.ViewDefinitions() ([]agentanalytics.ViewDefinition, error)`**: 네트워크 호출을 수행하지 않고 `cfg`에 대한 25개 뷰 정의(`Name`, `EventType`, `Query`)의 결정론적 목록을 반환하므로 Terraform이나 배포 파이프라인을 통해 외부에서 뷰를 프로비저닝할 수 있습니다.

    ```go
    // 구체적인 플러그인을 언래핑하여 드롭 통계를 검사하거나 수동으로 뷰를 동기화합니다:
    if bqPlugin, ok := agentanalytics.AsBigQueryAgentAnalyticsPlugin(adkPlugin); ok {
    	if err := bqPlugin.SyncViews(ctx); err != nil {
    		log.Printf("SyncViews failed: %v", err)
    	}
    }

    // 종료 시 보류 중인 이벤트를 플러시하고 리소스를 해제합니다:
    if err := adkPlugin.Close(); err != nil {
    	log.Printf("Close failed: %v", err)
    }
    ```

=== "Java"

    Java에서는 플러그인 수명 주기가 RxJava `Completable`을 반환하는 `close()` 메서드(`Plugin`에서 상속됨)를 통해 관리됩니다.

    - **`plugin.close()`**: 플러그인을 정상적으로 종료하여 대기 중인 이벤트를 플러시하고 리소스(BigQuery 쓰기 클라이언트 및 실행기 포함)를 해제합니다.
    - **자동 닫기**: `InMemoryRunner`를 사용하는 경우 `runner.close()`를 호출하면 BigQuery Agent Analytics 플러그인을 포함하여 등록된 모든 플러그인이 자동으로 닫힙니다.
    - **`plugin.getDropStats()`** (v1.7.0+): 드롭 원인별 드롭된 이벤트 수의 `ImmutableMap<String, Long>`을 반환합니다. 자세한 내용은 [드롭된 이벤트 관측 가능성](#dropped-event-observability)을 참고하세요.
    - **JVM 종료 훅** (v1.7.0+): 플러그인은 생성 시 종료 훅을 등록하므로 `close()`가 호출되지 않더라도 JVM 종료 시 대기 중인 이벤트가 드레인(`shutdownTimeout`에 바인딩된 최선형 방식)됩니다. 명시적으로 `close()`를 호출하면 훅이 등록 취소됩니다. 결정론적 플러시를 위해 명시적으로 `close()`를 호출하는 것이 좋습니다.

    ```java
    // 수동 종료
    plugin.close().blockingAwait();
    ```

### 드롭된 이벤트 관측 가능성 {#dropped-event-observability}

<div class="language-support-tag">
  <span class="lst-supported">ADK 지원 버전</span><span class="lst-python">Python</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v1.7.0</span>
</div>

BigQuery 로깅은 최선형(best-effort) 방식입니다. 인메모리 대기열이 넘치거나, 설정을 사용할 수 없거나, 종료가 콜백과 경쟁하거나, 쓰기가 궁극적으로 실패할 때 이벤트가 드롭될 수 있습니다. 플러그인은 또한 콘텐츠 대신 센티널을 포함하여 행이 작성되는 포맷터 및 파서 오류도 집계합니다. 이러한 카운터는 루프 정리 및 종료 전반에 걸쳐 유지됩니다.

**드롭 원인 (Python):**

| 원인 | 이유 |
|---|---|
| `queue_full` | 인메모리 이벤트 대기열을 제한합니다. ADK Python v2.13.0에서는 모든 이벤트 유형이 이 용량을 공유하며, 대기열이 가득 차면 종료 `INVOCATION_COMPLETED` 및 `INVOCATION_ERROR` 행도 드롭될 수 있고 `queue_full` 아래에 집계됩니다. `BigQueryLoggerConfig`에서 `queue_max_size`를 늘리거나, `batch_size`를 늘려 더 큰 청크로 드레인하거나, 소비자 측을 확장하세요(더 많은 동시 호출이 더 빠르게 완료되도록 함). |
| `arrow_prep_failed` | 행을 Arrow 표현으로 변환할 수 없습니다(일반적으로 스키마/유형 불일치). 문제가 되는 필드가 있는지 로그를 검사하세요. |
| `retry_exhausted` | 재시도 예산이 소진될 때까지 Storage Write API 호출이 재시도 가능한 오류(예: 일시적인 gRPC 실패)를 계속 반환했습니다. |
| `permission_denied` | *(Python v2.13.0+)* Storage Write API가 `PERMISSION_DENIED`(`google.api_core.exceptions.PermissionDenied`)를 반환했습니다. 재시도할 수 없으며, 서비스 계정에 대상 테이블에 대한 `bigquery.tables.updateData`(예: `roles/bigquery.dataEditor`) 권한이 있는지 확인하세요. |
| `not_found` | *(Python v2.13.0+)* 대상 데이터 세트, 테이블 또는 쓰기 스트림이 존재하지 않는 경우 등 기본 스트림에서 Storage Write API가 `NOT_FOUND`(`google.api_core.exceptions.NotFound`)를 반환했습니다(`exactly_once_delivery` 모드의 `NOT_FOUND`는 `offset_conflict` 아래에 집계됨). 재시도할 수 없습니다. |
| `non_retryable` | Storage Write API가 기타 재시도할 수 없는 오류(할당량, 스키마 거부, 잘못된 인수)를 반환했습니다. 일반적으로 운영자의 개입이 필요합니다. |
| `unexpected_error` | 배치를 준비하거나 작성하는 동안 발생한 기타 예외입니다. |
| `shutdown_timeout` | 바인딩된 종료 또는 닫기 시간이 초과되었을 때 대기열에 행이 남아 있었습니다. |
| `shutdown_cancelled` | 외부 닫기 시간 초과 등 호스트에 의해 종료가 취소되었을 때 대기열에 행이 남아 있었습니다. |
| `offset_conflict` | `exactly_once_delivery` 모드에서 커밋된 스트림이 오프셋을 거부했거나 교체 스트림을 사용할 수 없었습니다. |
| `setup_unavailable` | 플러그인 설정이 실패했거나 재시도 백오프 상태로 남아 행을 허용할 수 없었습니다. |
| `shutdown_race` | 종료가 시작되거나 진행 중인 동안 콜백이 행 허용을 시도했습니다. |
| `stale_loop` | 대기 중인 행이 이미 닫혀 더 이상 드레인할 수 없는 이벤트 루프에 속해 있었습니다. |
| `formatter_failed` | 커스텀 포맷터가 실패했거나 지원되지 않는 유형을 반환했습니다. 행은 여전히 `[FORMATTER_FAILED]`로 작성됩니다. 이는 드롭된 행 수가 아니라 인시던트 수입니다. |
| `content_parse_failed` | 콘텐츠 파싱에 실패했습니다. 행은 여전히 `[CONTENT_PARSE_FAILED]`로 작성됩니다. 이는 드롭된 행 수가 아니라 인시던트 수입니다. |

**드롭 카운터 (Go):**

`bqPlugin.DropStats()`는 다음 `int64` 필드가 있는 `agentanalytics.DropStats` 구조체를 반환합니다:

| 필드 | 이유 |
|---|---|
| `QueueFullDrops` | 이벤트 콜백이나 `Append`가 행을 큐에 넣으려고 했을 때 인메모리 채널(`QueueMaxSize`, 기본값 `10000`)이 가득 차서 드롭된 행입니다. `agentanalytics.Config`에서 `QueueMaxSize` 또는 `BatchSize`를 늘리세요. |
| `AppendFailureDrops` | Storage Write API 전송 중에 실패로 기록된 행입니다(`MaxRetries`를 소진한 배치, 재시도할 수 없는 쓰기 또는 스키마/디스크립터 준비 오류, 재시도가 실패하기 전에 끊어진 스트림에서 ack가 손실된 서버 커밋 추가, 복구된 콜백 패닉, `Flush`에서 배치 실패 후 건너뛴 나머지 배치 포함). |
| `FormatterFailureDrops` | nil이 아닌 오류를 반환했거나 패닉이 발생한 커스텀 `ContentFormatter` 호출입니다. 행은 여전히 `"[FORMATTER_FAILED]"`로 작성되며 `content_parts`는 없고 `error_message`에 `content_formatter raised <error type>` 또는 `content_formatter panicked`가 포함됩니다. 이는 인시던트 수이며 `TotalDrops`에는 포함되지 않습니다. |
| `ShutdownDrops` | `Close()` 중에 `ShutdownTimeout`이 만료되기 전에 드레인할 수 없어 대기열에 남아 있던 행과 `Close()`가 시작된 후 `Append`에 전달된 행입니다. |
| `TotalDrops` | 드롭된 것으로 집계된 행의 상한 합계(`QueueFullDrops + AppendFailureDrops + ShutdownDrops`)입니다. `AppendFailureDrops`에는 ack가 손실된 서버 커밋 배치가 포함될 수 있으므로 `TotalDrops`는 손실된 행의 상한값입니다. |

**드롭 원인 (Java, v1.7.0+):**

| 원인 | 이유 |
|---|---|
| `queue_full` | 인메모리 배치 큐가 오버플로되었습니다. `BigQueryLoggerConfig`에서 `queueMaxSize`를 늘리거나, `batchSize`를 늘리거나, 소비자 측을 확장하세요. |
| `append_error` | 시간 초과, 소진되었거나 재시도할 수 없는 쓰기, 예상치 못한 변환 실패를 포함하여 `AppendSerializationError` 이외의 원인으로 배치 준비 또는 추가가 실패했습니다. |
| `serialization_error` | 쓰기 스트림에 맞게 행을 직렬화할 수 없습니다(일반적으로 스키마/유형 불일치). 문제가 되는 필드가 있는지 로그를 검사하세요. |
| `after_close` | 행이 이미 닫힌 호출별 프로세서에 도달했습니다. |
| `shutdown_timeout` | 바인딩된 최종 드레인이 만료되었을 때 대기열에 행이 남아 있었습니다. |
| `writer_permit_exhausted` | 일반적으로 Storage Write 중단 또는 지연된 정리 중에 활성 기록기 안전 상한이 소진되었습니다. |
| `writer_create_error` | `StreamWriter` 생성 또는 프로세서 시작에 실패했습니다. |
| `late_after_finalize` | 비동기 작업이 호출이 완료된 후 또는 플러그인이 닫히는 동안 완료되었습니다. |

**카운트 읽기:**

=== "Python"

    ```python
    # 플러그인 시작 이후 {reason: count}의 스냅샷.
    stats = plugin.get_drop_stats()
    # 예: {"queue_full": 12, "retry_exhausted": 0,
    #      "permission_denied": 0, "not_found": 0,
    #      "formatter_failed": 1, ...}

    loss_reasons = {
        "queue_full", "arrow_prep_failed", "retry_exhausted",
        "permission_denied", "not_found", "non_retryable",
        "unexpected_error", "shutdown_timeout", "shutdown_cancelled",
        "offset_conflict", "setup_unavailable", "shutdown_race",
        "stale_loop",
    }
    total_rows_lost = sum(stats.get(reason, 0) for reason in loss_reasons)
    ```

=== "Go"

    ```go
    if bqPlugin, ok := agentanalytics.AsBigQueryAgentAnalyticsPlugin(adkPlugin); ok {
    	stats := bqPlugin.DropStats()
    	fmt.Printf(
    		"total_drops=%d (queue_full=%d append_failure=%d shutdown=%d) formatter_failures=%d\n",
    		stats.TotalDrops,
    		stats.QueueFullDrops,
    		stats.AppendFailureDrops,
    		stats.ShutdownDrops,
    		stats.FormatterFailureDrops,
    	)
    }
    ```

=== "Java"

    ```java
    // 플러그인 시작 이후 {drop_reason: count}의 스냅샷.
    ImmutableMap<String, Long> stats = plugin.getDropStats();
    // 예: {queue_full=12, append_error=0, serialization_error=0,
    //      after_close=0, shutdown_timeout=0, writer_permit_exhausted=0,
    //      writer_create_error=0, late_after_finalize=0}

    long totalDropped = stats.values().stream().mapToLong(Long::longValue).sum();
    ```

**모니터링 시스템으로 내보내기**: 주기적으로 폴링하여 증분(delta)을 전송합니다.

```python
import asyncio

async def export_loop(plugin):
    last = {}
    while True:
        current = plugin.get_drop_stats()
        for reason, count in current.items():
            delta = count - last.get(reason, 0)
            if delta:
                # 예: metric_client.write_point(
                #         metric="bqaa_dropped_events",
                #         labels={"reason": reason}, value=delta)
                ...
        last = current
        await asyncio.sleep(60)
```

0이 아닌 모든 이유에 대해 알림을 설정하세요. 대부분의 이유는 BigQuery에 도달하기 전에 행이 손실되었음을 의미합니다. 반면 `formatter_failed`(Go의 경우 `FormatterFailureDrops`) 및 `content_parse_failed` 이유는 행이 센티널 콘텐츠와 함께 기록되었음을 의미하므로 개인 정보 보호 또는 데이터 품질 인시던트로 알림을 설정하세요. `queue_full`, `retry_exhausted`, `permission_denied`, `not_found`, `non_retryable` 또는 `offset_conflict` 수가 지속적으로 높다면 일반적으로 처리량, IAM, 전송 또는 Storage Write 상태에 문제가 있음을 나타냅니다. Go에서 이에 상응하는 쓰기 오류 카운터는 `AppendFailureDrops`이며, Java에서는 `append_error`입니다.

### 멀티프로세싱 및 fork 안전성

Python 플러그인은 fork를 인식합니다. gRPC C-core 라이브러리를 로드하기 전에 `GRPC_ENABLE_FORK_SUPPORT=1`을 설정하고 하위 프로세스에서 상속된 런타임 상태(gRPC 채널, 쓰기 스트림, 이벤트 루프)를 재설정하는 `os.register_at_fork` 핸들러를 등록합니다. 즉, 플러그인은 파일 설명자를 유출하거나 부모 연결을 통해 데이터를 전송하지 않고도 `os.fork()`에서 살아남을 수 있습니다.

그러나 프로덕션 배포에는 **`spawn`이 권장되는 멀티프로세싱 시작 메서드**입니다. `fork`는 실행 중인 gRPC 상태를 포함하여 부모의 주소 공간을 복사하며 fork 후 재설정으로 인해 각 하위 프로세스의 첫 번째 쓰기에 지연 시간이 추가됩니다. `spawn`을 사용하면 각 워커가 플러그인을 깔끔하게 초기화합니다.

특히 Gunicorn 배포의 경우:

- 지연 플러그인 초기화(플러그인은 첫 번째 이벤트가 기록될 때까지 설정을 연기함)와 결합된 `--preload`를 선호하거나,
- 각 워커가 자체 클라이언트를 갖도록 `post_fork` 훅 내부에서 플러그인을 초기화하세요.

!!! note

    fork 안전 메커니즘은 런타임 상태만 재설정합니다. fork 시점에 부모 프로세스에서 대기열에 있었지만 아직 플러시되지 않은 이벤트는 **다시 재생되지 않습니다**. 전송을 보장해야 하는 경우 fork하기 전에 `await plugin.flush()`를 호출하세요.

## 기록된 데이터를 활용하는 추가 방법

### BigQuery Agent Analytics SDK

[BigQuery Agent Analytics SDK](https://github.com/GoogleCloudPlatform/BigQuery-Agent-Analytics-SDK/tree/main)는 플러그인이 기록한 데이터를 프로그래밍 방식으로 사용하고 분석할 수 있는 방법을 제공합니다. 다음 용도로 SDK를 활용할 수 있습니다.

- **에이전트 평가:** 에이전트 실행 결과를 예상 결과와 비교
- **골든 궤적(Golden trajectory) 매칭:** 에이전트 실행 경로가 승인된 시퀀스와 일치하는지 검증
- **트레이스 시각화:** 기록된 span을 기반으로 에이전트 실행 흐름 재구성 및 시각화

### 대시보드 구축

호스팅된 Looker Studio 템플릿, 즉시 사용 가능한 Looker Block 또는 예제 노트북으로 구축한 자체 대시보드를 통해 에이전트의 성능 데이터를 시각화할 수 있습니다.

#### Looker Studio 템플릿

[BigQuery Agent Analytics 대시보드 설정 페이지](https://googlecloudplatform.github.io/BigQuery-Agent-Analytics-SDK/)를 사용하면 빠르게 시작할 수 있습니다. 이벤트 테이블의 정규화된 ID(`project.dataset.table`)를 입력하면 사전 구축된 보고서 페이지가 포함된 공개 템플릿의 비공개 사본을 생성하는 Looker Studio 링크가 빌드됩니다. 이 템플릿은 생성된 뷰나 별도의 데이터 파이프라인 없이 기본 테이블을 직접 쿼리합니다. 설정 페이지는 백엔드가 없으며 클라이언트 측에서 링크를 빌드한다고 명시되어 있으므로 테이블 ID를 입력하기 전에 소스를 검토하세요.

사본은 **소유자의 사용자 인증 정보(Owner's credentials)**로 생성됩니다. 각 조회자가 자체 액세스 권한으로 BigQuery를 쿼리할 수 있도록 데이터 소스를 **조회자의 사용자 인증 정보(Viewer's credentials)**로 전환할 때까지 보고서를 비공개로 유지하고, 공유하기 전에 조회 전용 계정으로 전환을 확인하세요.

#### Looker Block

[BigQuery Agent Analytics Looker Block](https://marketplace.looker.com/marketplace/detail/agent_analytics)은 에이전트를 모니터링, 디버깅 및 최적화하기 위한 바로 사용 가능한 대시보드를 제공하며 상호작용, 도구 사용, LLM 성능 및 비용에 대한 인사이트를 제공합니다.

- **집계 메트릭:** 토큰 소비량, 사용자 참여도, 도구 실행 볼륨.
- **시스템 상태:** 병목 현상을 정확히 찾아내는 데 도움이 되는 P50–P99 지연 시간 분포 및 도구 실패 추적.
- **대화형 드릴다운:** 메트릭을 클릭하여 근본 원인 분석을 위한 컨텍스트 인식 시각화 열기.

이 블록은 기록된 JSON 페이로드를 직접 파싱하는 기본 파생 테이블(Native Derived Table) 아키텍처를 사용하므로 추가 데이터 파이프라인이 필요하지 않습니다. 시작하려면 Looker Marketplace에서 무료로 설치하고 BigQuery 프로젝트 ID, 데이터 세트 이름 및 기본 테이블 이름을 지정하세요.

#### 노트북 기반 커스텀 대시보드

BigQuery Agent Analytics SDK에는 에이전트의 성능 데이터를 쿼리하고 시각화하는 방법을 보여주는 [예제 Jupyter 노트북](https://github.com/GoogleCloudPlatform/BigQuery-Agent-Analytics-SDK/blob/main/examples/dashboard_v2.ipynb)이 포함되어 있습니다. 이를 시작점으로 삼아 BigQuery Agent Analytics 데이터 세트에 맞춘 커스텀 대시보드를 구축하세요. [Colab Data Apps](https://docs.cloud.google.com/bigquery/docs/colab-data-apps)를 사용하여 노트북을 대화형 대시보드로 게시할 수도 있습니다.

## 피드백

BigQuery Agent Analytics에 대한 여러분의 피드백을 환영합니다. 질문이나 제안 사항이 있거나 문제를 발견한 경우 [bqaa-feedback@google.com](mailto:bqaa-feedback@google.com)으로 팀에 문의해 주세요.

## 추가 리소스

- [Python 플러그인 소스](https://github.com/google/adk-python/blob/main/src/google/adk/plugins/bigquery_agent_analytics_plugin.py)
- [Go 플러그인 소스](https://github.com/google/adk-go/tree/main/plugin/agentanalytics)
- [BigQuery Storage Write API](https://cloud.google.com/bigquery/docs/write-api)
- [객체 테이블 소개](https://docs.cloud.google.com/bigquery/docs/object-table-introduction)
- [BigQuery Agent Analytics SDK 예제](https://github.com/GoogleCloudPlatform/BigQuery-Agent-Analytics-SDK/tree/main/examples)
