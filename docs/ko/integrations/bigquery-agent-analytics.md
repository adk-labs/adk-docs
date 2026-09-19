---
catalog_title: BigQuery Agent Analytics Plugin
catalog_description: 심층적인 에이전트 동작 분석 및 로깅을 위한 플러그인
catalog_icon: /integrations/assets/bigquery.png
catalog_tags: ["observability", "google"]
---

# ADK용 BigQuery Agent Analytics 플러그인

<div class="language-support-tag">
  <span class="lst-supported">ADK 지원 버전</span><span class="lst-python">Python v1.21.0</span><span class="lst-java">Java v1.5.0</span><span class="lst-kotlin">Kotlin v0.8.0</span>
</div>

BigQuery Agent Analytics 플러그인은 심층적인 에이전트 동작 분석을 위한 강력한 솔루션을 제공하여 Agent Development Kit(ADK)를 크게 향상시킵니다. ADK 플러그인 아키텍처와 **BigQuery Storage Write API**를 사용하여 중요한 운영 이벤트를 Google BigQuery 테이블에 직접 캡처하고 기록함으로써, 디버깅, 실시간 모니터링 및 종합적인 오프라인 성능 평가를 위한 고급 기능을 제공합니다.

또한 이 플러그인은 **자동 스키마 업그레이드(Auto Schema Upgrade)**(기존 테이블에 새 열을 안전하게 추가), **도구 출처(Tool Provenance)** 추적(LOCAL, MCP, SUB_AGENT, A2A, TRANSFER_AGENT, TRANSFER_A2A), human-in-the-loop 상호작용을 위한 **HITL 이벤트 추적**, **자동 뷰 생성(Automatic View Creation)**(쿼리하기 쉬운 평면화된 이벤트 뷰 생성)을 제공합니다.

**ADK 2.0** 멀티 에이전트 워크플로에 대한 지원을 통해 에이전트 핸드오프, 상태 체크포인트, 이벤트 압축(compaction) 및 장기 실행 도구로 추적 기능을 확장합니다. 네 가지 새로운 이벤트 유형인 `AGENT_TRANSFER`, `AGENT_STATE_CHECKPOINT`, `EVENT_COMPACTION`, `TOOL_PAUSED`가 추가되었습니다. 또한 모든 행에 `attributes.adk` 엔벨로프를 스탬프하여 에이전트 실행 그래프를 재구성하고 일시중지된 도구를 이를 재개하는 행과 조인할 수 있도록 합니다. **Java**의 경우 현재 `TOOL_PAUSED` 이벤트 및 일시중지/재개 페어링 키만 지원하며 `attributes.adk` 엔벨로프는 지원하지 않습니다. 자세한 내용은 [에이전트 워크플로 및 일시중지/재개 이벤트(ADK 2.0)](#adk-2-events)를 참고하세요.

이 플러그인에는 세 가지 안정성 및 관측 가능성 수정사항이 포함되어 있습니다(Java: v1.7.0 이상):

- **리전 간 Storage Write API 라우팅:** `US` 멀티 리전 외부(예: `EU` 또는 `northamerica-northeast1`)의 BigQuery 데이터 세트에 대한 쓰기가 이제 쓰기 스트림을 소유한 리전으로 라우팅됩니다. 이전에는 "session not found" / stream-not-found 오류로 실패하고 모든 행이 조용히 누락될 수 있었습니다.
- **전송 및 콘텐츠 인시던트 관측 가능성:** 전송 손실이 원인별로 추적됩니다. 또한 Python에서는 센티널(sentinel) 행이 기록되는 포맷터 및 파서 오류도 집계합니다. 이러한 카운터는 `BigQueryAgentAnalyticsPlugin.get_drop_stats()`(Python) 또는 `getDropStats()`(Java)를 통해 노출되므로, 호스트에서 이를 폴링하여 자체 모니터링 시스템으로 내보낼 수 있습니다. 원인 키 및 시맨틱은 언어마다 다르며, 자세한 내용은 [드롭된 이벤트 관측 가능성](#dropped-event-observability)을 참고하세요.
- **Cloud Trace에서 중복 span 제거:** Agent Engine 원격 분석(`GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY=true`) 또는 기타 Cloud Trace 내보내기 도구가 전역 tracer provider에 연결되어 있을 때, 플러그인이 각 프레임워크 span 옆에 중복 span을 생성하지 않습니다. 플러그인은 여전히 주변 OTel span에서 `trace_id`를 상속하므로 BigQuery 행이 Cloud Trace 트레이스와 원활하게 조인됩니다.

Python v2.7.0 이상에서는 모든 행이 쓰기 큐에 들어가기 전에 고유한 `event_id`를 부여받습니다. 이 ID는 Storage Write API 재시도 전반에서 유지되므로 소비자가 재시도 중복을 식별할 수 있습니다. 선택적 `exactly_once_delivery` 모드는 커밋된 스트림과 명시적 오프셋을 사용하여 활성 프로세서 내에서 모호한 재시도로 인한 중복을 방지합니다. 이 모드는 무손실 전송을 보장하지 않으므로 자세한 내용은 [전송 및 중복 제거](#delivery-and-deduplication)를 참고하세요.

동일한 Python 릴리스에 모델 및 워크플로 종료 세부정보가 추가되었습니다. 최종 `LLM_RESPONSE` 행에는 `finish_reason`과 모델에서 제공한 경우 정제된 `error_message`가 포함됩니다. 워크플로 노드는 `NODE_OUTPUT` 및 `NODE_ERROR`를 내보낼 수 있으며, 처리되지 않은 에이전트 또는 실행 예외는 `AGENT_ERROR` 및 `INVOCATION_ERROR`를 내보냅니다.

!!! warning "BigQuery Storage Write API"

    이 기능은 유료 서비스인 **BigQuery Storage Write API**를 사용합니다. 비용에 대한 자세한 내용은 [BigQuery 문서](https://cloud.google.com/bigquery/pricing?e=48754805&hl=ko#data-ingestion-pricing)를 참고하세요.

??? note "Kotlin 지원"

    **Kotlin** 플러그인은 호출 수명 주기 이벤트를 로깅합니다. 호출이 시작될 때 `INVOCATION_STARTING` 행을 작성하고 종료될 때 `INVOCATION_COMPLETED` 행을 작성하며, 아직 존재하지 않는 경우 처음 사용할 때 파티셔닝 및 클러스터링된 이벤트 테이블을 생성합니다.

    행은 Python 및 Java에서 사용하는 Storage Write API 대신 호출 경로에서 동기적으로 `tabledata.insertAll`을 통해 한 번에 하나씩 삽입됩니다.

    Kotlin에서는 LLM, 도구, 에이전트, 상태, HITL 및 A2A 이벤트, ADK 2.0 워크플로 이벤트, 자동 뷰 생성, 자동 스키마 업그레이드, 도구 출처, GCS 오프로딩, 드롭 통계가 구현되어 있지 않습니다.

## 사용 사례

- **에이전트 워크플로 디버깅 및 분석:** 광범위한 *플러그인 수명 주기 이벤트*(LLM 호출, 도구 사용) 및 *에이전트 생성 이벤트*(사용자 입력, 모델 응답)를 명확하게 정의된 스키마로 캡처합니다.
- **대용량 분석 및 디버깅:** 높은 처리량과 짧은 지연 시간을 지원하기 위해 Storage Write API를 사용하여 비동기식으로 로깅 작업을 수행합니다.
- **멀티모달 분석:** 텍스트, 이미지 및 기타 양식을 기록하고 분석합니다. 대용량 파일은 GCS로 오프로드되어 Object Tables를 통해 BigQuery ML에서 액세스할 수 있습니다.
- **분산 추적(Distributed Tracing):** 에이전트 실행 흐름을 시각화하기 위해 OpenTelemetry 스타일의 추적(`trace_id`, `span_id`)을 기본적으로 지원합니다.
- **도구 출처(Tool Provenance):** 각 도구 호출의 출처(로컬 함수, MCP 서버, 하위 에이전트, A2A 원격 에이전트 또는 전송 에이전트)를 추적합니다.
- **Human-in-the-Loop(HITL) 추적:** 자격 증명 요청, 확인 프롬프트 및 사용자 입력 요청을 위한 전용 이벤트 유형을 제공합니다.
- **에이전트 워크플로 추적(ADK 2.0):** 실행 그래프를 재구성하기 위한 `attributes.adk` 엔벨로프와 함께 에이전트 전송, 상태 체크포인트, 이벤트 압축 및 장기 실행 도구 일시중지/재개를 캡처합니다.
- **쿼리 가능한 이벤트 뷰:** JSON 페이로드 데이터를 unnest하여 다운스트림 분석을 간소화하는 평면화된 이벤트 유형별 BigQuery 뷰(예: `v_llm_request`, `v_tool_completed`)를 자동으로 생성합니다.

### 캡처된 이벤트 요약

다음 표에는 플러그인이 기록하는 모든 이벤트 유형이 나열되어 있습니다. 자세한 페이로드 예시는 [이벤트 유형 및 페이로드](#event-types)를 참고하세요. **뷰(View)** 열은 선택적 BigQuery 뷰를 보여줍니다. Python은 기본적으로 뷰를 생성하며, Java는 `createViews(true)`가 구성된 경우에만 뷰를 생성합니다.

**Kotlin**의 경우 플러그인은 `INVOCATION_STARTING` 및 `INVOCATION_COMPLETED`만 기록하고 뷰를 생성하지 않으므로 다른 행과 전체 **뷰** 열은 Python 및 Java에 적용됩니다.

이 표는 Python과 Java 이벤트 세트의 합집합입니다. `INVOCATION_ERROR`, `AGENT_ERROR`, `AGENT_TRANSFER`, `AGENT_STATE_CHECKPOINT`, `EVENT_COMPACTION`, `NODE_OUTPUT`, `NODE_ERROR`는 Python 전용입니다. Java는 `TOOL_PAUSED`를 내보내지만 다른 워크플로별 이벤트는 내보내지 않습니다. 나머지 행은 두 언어 모두에 적용됩니다.

| 이벤트 유형 | 캡처 시점 | 주요 페이로드 필드 | 뷰 |
| --- | --- | --- | --- |
| `USER_MESSAGE_RECEIVED` | 사용자 메시지가 호출에 입력될 때 | 텍스트 요약 / 콘텐츠 파트 | `v_user_message_received` |
| `INVOCATION_STARTING` | 호출이 시작될 때 | *(공통 열만 해당)* | `v_invocation_starting` |
| `INVOCATION_COMPLETED` | 호출이 끝날 때 | *(공통 열만 해당)* | `v_invocation_completed` |
| `INVOCATION_ERROR` | 호출이 처리되지 않은 예외로 실패할 때 | 오류 메시지, 정제된 트레이스백 | `v_invocation_error` |
| `AGENT_STARTING` | 에이전트 실행이 시작될 때 | 지침 요약 | `v_agent_starting` |
| `AGENT_COMPLETED` | 에이전트 실행이 끝날 때 | 지연 시간 | `v_agent_completed` |
| `AGENT_ERROR` | 에이전트 실행이 처리되지 않은 예외로 실패할 때 | 오류 메시지, 정제된 트레이스백, 지연 시간 | `v_agent_error` |
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
| `AGENT_STATE_CHECKPOINT` | 에이전트가 상태의 스냅샷을 생성할 때(또는 실행 종료를 표시할 때) | 에이전트 상태, 에이전트 종료 플래그, 소스 이벤트 ID | `v_agent_state_checkpoint` |
| `EVENT_COMPACTION` | 일련의 이벤트 기간이 요약으로 압축될 때 | 윈도우 시작/종료 타임스탬프, 압축된 콘텐츠 | `v_event_compaction` |
| `TOOL_PAUSED` | 장기 실행 도구(또는 HITL 요청)가 일시중지되어 재개를 기다릴 때 | 도구 이름, 인수, 일시중지 종류, 함수 호출 ID | `v_tool_paused` |
| `NODE_OUTPUT` | 워크플로 노드가 최종 구조화된 출력을 내보낼 때 | 출력, 노드 경로, 실행 ID, 부모 실행 ID | `v_node_output` |
| `NODE_ERROR` | 워크플로 노드가 비모델 오류로 종료될 때 | 오류 코드, 오류 메시지, 노드 경로, 실행 ID, 부모 실행 ID | `v_node_error` |

## 설치

Python의 경우 전용 BigQuery Agent Analytics 엑스트라(extra)를 사용하여 ADK를 설치합니다. 이 엑스트라에는 플러그인에 필요한 BigQuery 클라이언트, Cloud Storage 클라이언트 및 `pyarrow`가 포함되어 있습니다.

```bash
pip install "google-adk[bigquery-analytics]>=2.7.0"
```

`pyarrow` 종속 항목은 더 이상 일반 `gcp` 엑스트라에 포함되지 않습니다. `pyarrow`가 누락된 경우 플러그인의 import 오류를 통해 설치해야 할 `bigquery-analytics` 엑스트라를 안내합니다.

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
    [전제 조건](#prerequisites)을 참고하세요. The plugin is JVM-only and ships outside
    core, so add the integrations artifact:

    ```kotlin title="build.gradle.kts"
    implementation("com.google.adk:google-adk-kotlin-integrations:1.0.0")
    ```

    ```kotlin title="BigQueryAnalyticsExample.kt"
    --8<-- "examples/kotlin/snippets/integrations/BigQueryAnalyticsExample.kt:quickstart"
    ```

    The plugin creates the events table on first use, so the credentials in
    scope need permission to create a table in the dataset, not only to insert
    rows. Set `location` to your dataset's location; it defaults to `"US"`. For
    the full set of options, see [Configuration
    options](#configuration-options).

    Logging never fails the turn: if the table cannot be created or a row cannot
    be inserted, the plugin logs the error and the invocation continues. When
    rows are missing, enable logging for
    `com.google.adk.kt.plugins.agentanalytics.BigQueryAgentAnalyticsPlugin` —
    logs are emitted under that class name, not under the plugin's ADK name
    (`bigquery_agent_analytics`).


### 에이전트 실행 및 테스트

Test the plugin by running the agent and making a few requests through the chat
interface, such as "tell me what you can do" or "List datasets in my cloud
project <your-gcp-project-id>". These actions create events which are recorded
in your Google Cloud project BigQuery instance. Once these events have been
processed, you can view the data for them in the [BigQuery
Console](https://console.cloud.google.com/bigquery), using this query:

```sql
SELECT timestamp, event_type, content
FROM `your-gcp-project-id.your-big-query-dataset-id.agent_events`
ORDER BY timestamp DESC
LIMIT 20;
```

??? example "Full example with GCS offloading, OpenTelemetry, and BigQuery tools"

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
- 로그/이벤트 데이터를 쓰기 위한 테이블 수준의 `roles/bigquery.dataEditor`.
- **GCS 오프로딩을 사용하는 경우:** 대상 버킷에 대한 `roles/storage.objectCreator` 및 `roles/storage.objectViewer`.

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
    | `max_content_length` | `int` | `500 * 1024` | 오프로드/자르기 전 인라인 페이로드 크기 제어(바이트) |
    | `batch_size` | `int` | `1` | 쓰기 처리량 대 지연 시간 조정(기본값 1은 낮은 지연 시간용, 높은 처리량의 경우 증가) |
    | `batch_flush_interval` | `float` | `1.0` | 부분 일괄 처리를 주기적으로 플러시(초) |
    | `shutdown_timeout` | `float` | `10.0` | 종료 시 최종 플러시 대기 시간(초) |
    | `event_allowlist` | `Optional[List[str]]` | `None` | 선택한 이벤트 유형만 로깅 |
    | `event_denylist` | `Optional[List[str]]` | `None` | 민감하거나 불필요한 이벤트 유형 건너뛰기 |
    | `content_formatter` | `Optional[Callable]` | `None` | 이벤트별 커스텀 마스킹/포맷팅 적용(시크릿 수정 등) |
    | `log_multi_modal_content` | `bool` | `True` | GCS 참조를 포함한 `content_parts` 세부정보 캡처 |
    | `queue_max_size` | `int` | `10000` | 인메모리 이벤트 대기열 제한 |
    | `retry_config` | `Optional[RetryConfig]` | `None` | 재시도 동작 조정 |
    | `log_session_metadata` | `bool` | `True` | `attributes`에 세션 정보 추가(`session_id`, `app_name`, `user_id`, `state`). `temp:` 접두사가 붙은 키는 [수정(redacted)](#built-in-redaction)됨. |
    | `custom_tags` | `Dict[str, Any]` | `{}` | 모든 이벤트의 `attributes`에 정적 태그(예: `{"env": "prod"}`) 추가 |
    | `auto_schema_upgrade` | `bool` | `True` | 기존 테이블에 새 열 자동 추가(추가 전용) |
    | `create_views` | `bool` | `True` | 이벤트 유형별 BigQuery 뷰 생성 |
    | `view_prefix` | `str` | `"v"` | 여러 플러그인이 데이터 세트를 공유할 때 뷰 이름 충돌 방지(예: `"v_staging"`) |
    | `enable_otel_correlation` | `bool` | `False` | 최선형 Cloud Trace 조인 키로서 주변 OpenTelemetry span 컨텍스트를 `attributes.otel.{span_id, trace_id}`로 캡처 |
    | `custom_metadata_allowlist` | `Optional[List[str]]` | `None` | 선택된 `event.custom_metadata` 키를 `attributes.custom_metadata.*`에 캡처: 정확한 키 또는 `"prefix*"` 패턴 |
    | `payload_column_denylist` | `Optional[List[str]]` | `None` | 쓰기 시 테이블에서 페이로드 열(`content`, `content_parts`, `attributes`, `latency_ms`) 제외 투영 |
    | `final_response_tool_names` | `FrozenSet[str]` | `frozenset()` | 선택한 성공 도구의 호출 인수를 `AGENT_RESPONSE` 페이로드로 기록 |
    | `flush_on_run_end` | `bool` | `True` | 각 실행이 끝날 때 대기열에 있는 행 쓰기 완료 대기 |
    | `exactly_once_delivery` | `bool` | `False` | 커밋된 스트림과 명시적 오프셋을 사용하여 활성 프로세서 내에서 모호한 재시도 중복 방지 |

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
    - **`custom_metadata_allowlist`**: 설정하지 않으면 기본 `a2a:*` 캡처만 실행되는 이전 동작이 유지됩니다. 캡처된 값은 다른 모든 로깅 콘텐츠와 동일한 안전 파이프라인(자르기, 민감한 키 수정, 순환 참조 처리)을 통과합니다.
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

    `flush_on_run_end` 옵션의 기본값은 `True`이며, 이는 `after_run_callback`이 현재 이벤트 루프의 쓰기 큐를 대기하도록 만듭니다. 응답 경로에서 해당 플러시를 제거하려면 `False`로 설정하세요. 백그라운드 기록기가 대기열을 계속 비우므로 실행이 반환된 후 잠시 뒤에 BigQuery에 행이 나타날 수 있습니다.

    ```python
    config = BigQueryLoggerConfig(
        final_response_tool_names=frozenset({"submit_final_response"}),
        flush_on_run_end=False,
    )
    ```

    ### 전송 및 중복 제거 {#delivery-and-deduplication}

    <div class="language-support-tag">
      <span class="lst-supported">ADK 지원 버전</span><span class="lst-python">Python v2.7.0</span>
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

    루프 로컬 커밋 스트림과 명시적 오프셋을 사용하려면 `exactly_once_delivery=True`를 설정하세요. 이를 통해 첫 번째 결과가 모호했던 재시도가 해당 프로세서의 수명 내에서 중복을 생성하는 것을 방지할 수 있습니다. 스트림을 교체해야 하는 경우 추가 BigQuery `CreateWriteStream` 할당량을 소비할 수 있습니다.

    ```python
    config = BigQueryLoggerConfig(exactly_once_delivery=True)
    ```

    이름과 달리 이 옵션은 무손실 전송을 보장하지 않습니다. 재시도 소진, 오프셋 충돌 또는 교체 스트림 실패 후에도 일괄 처리가 드롭될 수 있습니다. 스트림 교체 실패 후 30초의 교체 백오프 중에 도착하는 이벤트도 드롭됩니다. `offset_conflict` 및 기타 [드롭 원인](#dropped-event-observability)을 모니터링하고 `event_id`를 소비자 중복 제거 키로 유지하세요.

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

    일괄 처리, 콘텐츠 포맷팅, 이벤트 허용 목록, GCS 오프로딩, 뷰 생성 등 **Python** 및 **Java** 탭 아래에 나열된 옵션은 Kotlin에 존재하지 않습니다.

## 스키마 및 프로덕션 설정

### 스키마 참조

이벤트 테이블(`agent_events`)은 유연한 스키마를 사용합니다. 다음 표는 예시 값과 함께 포괄적인 참조를 제공합니다.

| 필드 이름 | 유형 | 모드 | 설명 | 예시 값 |
| --- | --- | --- | --- | --- |
| **timestamp** | `TIMESTAMP` | `REQUIRED` | 이벤트 생성의 UTC 타임스탬프입니다. 기본 정렬 키이자 일별 파티셔닝 키 역할을 합니다. 정밀도는 마이크로초입니다. | `2026-02-03 20:52:17 UTC` |
| **event_id** | `STRING` | `NULLABLE` | 대기열 진입 전에 할당된 32자의 16진수 ID입니다. Storage Write API 재시도 시에도 유지되므로 소비자가 중복 행을 식별할 수 있습니다. 스키마 버전 2 이전에 작성된 행은 `NULL`입니다. | `ca5e3c9d99e24e46b614f2f44f93bf6e` |
| **event_type** | `STRING` | `NULLABLE` | 표준 이벤트 카테고리입니다. 표준 값에는 [이벤트 유형 및 페이로드](#event-types)에 설명된 LLM, 도구, 에이전트, 호출, 상태, HITL, A2A, 응답, 워크플로, 노드 출력 및 노드 오류 이벤트가 포함됩니다. 상위 수준 필터링에 사용됩니다. | `LLM_REQUEST` |
| **agent** | `STRING` | `NULLABLE` | 이 이벤트를 담당하는 에이전트의 이름입니다. 에이전트 초기화 중 또는 `root_agent_name` 컨텍스트를 통해 정의됩니다. | `my_bq_agent` |
| **session_id** | `STRING` | `NULLABLE` | 전체 대화 스레드에 대한 영구 식별자입니다. 여러 턴과 하위 에이전트 호출 간에 일정하게 유지됩니다. | `04275a01-1649-4a30-b6a7-5b443c69a7bc` |
| **invocation_id** | `STRING` | `NULLABLE` | 세션 내의 각 개별 에이전트 실행 또는 턴에 대한 고유 식별자입니다. | `81014e7a-90da-4cb0-adbf-cb6d53955685` |
| **user_id** | `STRING` | `NULLABLE` | 현재 세션과 연결된 사용자의 식별자입니다. 사용자별 분석에 유용합니다. | `user_12345` |
| **trace_id** | `STRING` | `NULLABLE` | 32자 16진수 트레이스 ID입니다. 활성화된 경우 주변 OpenTelemetry span에서 상속되며, 그렇지 않은 경우 플러그인에 의해 호출당 생성됩니다. | `4bf92f3577b34da6a3ce929d0e0e4736` |
| **span_id** | `STRING` | `NULLABLE` | 이 특정 작업에 대한 16자 16진수 span ID입니다. 플러그인의 내부 스택에서 추적됩니다. 루트 호출 span은 주변 OTel span ID를 재사용할 수 있으며 하위 BQAA span은 내부적으로 생성됩니다. OpenTelemetry span이 생성되거나 내보내지지 않습니다. | `00f067aa0ba902b7` |
| **parent_span_id** | `STRING` | `NULLABLE` | 직전 호출자의 16자 16진수 span ID로, 부모-자식 실행 트리를 재구성하는 데 사용됩니다. | `5fb397be34d23b0f` |
| **content** | `JSON` | `NULLABLE` | JSON으로 저장된 이벤트별 데이터(페이로드)입니다. 구조는 이벤트 유형에 따라 다릅니다. | `{"model": "gemini-flash-latest", ...}` |
| **content_parts** | `ARRAY<STRUCT>` | `REPEATED` | 구조화된 파트의 배열입니다. 텍스트 청크, GCS에 저장된 파일에 대한 URI/ObjectRef(스토리지 오프로딩용), MIME 유형 및 파트 메타데이터를 캡처합니다. | `[{mime_type: "image/png", uri: "gs://..."}]` |
| **attributes** | `JSON` | `NULLABLE` | 추가 메타데이터(예: `root_agent_name`, `model_version`, `usage_metadata`, `session_metadata`, `custom_tags`)를 위한 임의의 키-값 쌍입니다. | `{"model_version": "gemini-flash-latest", ...}` |
| **latency_ms** | `JSON` | `NULLABLE` | 지연 시간 측정값(예: 총 소요 시간인 `total_ms`)입니다. | `{"total_ms": 1250}` |
| **status** | `STRING` | `NULLABLE` | 이벤트의 결과로, 일반적으로 'OK' 또는 'ERROR'입니다. | `OK` |
| **error_message** | `STRING` | `NULLABLE` | 정제된 오류 또는 모델 종료 진단 정보입니다. | `ResourceExhausted: Quota exceeded` |
| **is_truncated** | `BOOLEAN` | `NULLABLE` | 인라인 콘텐츠가 `max_content_length` 제한을 초과하여 잘렸는지 여부를 나타내는 플래그입니다. | `false` |

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
      error_message STRING OPTIONS(description="Sanitized error or model termination diagnostic."),
      is_truncated BOOLEAN OPTIONS(description="Flag indicates if content was truncated.")
    )
    PARTITION BY DATE(timestamp)
    CLUSTER BY event_type, agent, user_id;
    ```

### 자동으로 생성되는 뷰

<div class="language-support-tag">
  <span class="lst-supported">ADK 지원 버전</span><span class="lst-python">Python v1.27.0</span><span class="lst-java">Java v1.5.0</span>
</div>

Python에서는 `create_views=True`(기본값)가 각 이벤트 유형에 대한 뷰를 자동으로 생성합니다. Java에서는 `createViews(true)`를 설정해야 합니다(기본값은 `false`). Kotlin은 뷰를 생성하지 않습니다. 뷰는 공통 JSON 구조를 평면화된 형식의 유형이 지정된 열로 변환하므로 반복적인 `JSON_VALUE` 및 `JSON_QUERY` 표현식을 피할 수 있습니다.

뷰 이름은 `{view_prefix}_{event_type_lowercase}` 규칙을 따릅니다(예: 기본 접두사 `"v"`를 사용할 경우 `LLM_REQUEST`는 `v_llm_request`가 됨). 여러 플러그인 인스턴스가 동일한 데이터 세트의 서로 다른 테이블에 쓸 때 뷰 이름 충돌을 방지하려면 `BigQueryLoggerConfig`에서 `view_prefix`를 고유한 값으로 설정하세요.

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

공개 비동기 메서드인 `await plugin.create_analytics_views()`를 호출하여 스키마 업그레이드 후 수동으로 뷰를 새로고침할 수도 있습니다.

모든 Python 뷰에는 다음 **공통 열**이 포함됩니다: `timestamp`, `event_id`, `event_type`, `agent`, `session_id`, `invocation_id`, `user_id`, `trace_id`, `span_id`, `parent_span_id`, `status`, `error_message`, `is_truncated`. Java 뷰에는 `event_id`를 제외한 동일한 공통 열이 포함됩니다.

다음 표에는 Python 뷰와 해당 이벤트별 열이 나열되어 있습니다.

| 뷰 이름 | 이벤트별 열 |
| --- | --- |
| **`v_user_message_received`** | *(공통 열만 해당)* |
| **`v_llm_request`** | `model` (STRING), `request_content` (JSON), `llm_config` (JSON), `tools` (JSON) |
| **`v_llm_response`** | `response` (JSON), `usage_prompt_tokens` (INT64), `usage_completion_tokens` (INT64), `usage_total_tokens` (INT64), `usage_cached_tokens` (INT64), `usage_thinking_tokens` (INT64), `usage_tool_use_tokens` (INT64), `context_cache_hit_rate` (FLOAT64), `total_ms` (INT64), `ttft_ms` (INT64), `model_version` (STRING), `usage_metadata` (JSON), `cache_metadata` (JSON), `cache_type` (STRING), `finish_reason` (STRING) |
| **`v_llm_error`** | `total_ms` (INT64) |
| **`v_tool_starting`** | `tool_name` (STRING), `tool_args` (JSON), `tool_origin` (STRING) |
| **`v_tool_completed`** | `tool_name` (STRING), `tool_result` (JSON), `tool_origin` (STRING), `total_ms` (INT64), `pause_kind` (STRING), `function_call_id` (STRING) |
| **`v_tool_error`** | `tool_name` (STRING), `tool_args` (JSON), `tool_origin` (STRING), `total_ms` (INT64) |
| **`v_agent_starting`** | `agent_instruction` (STRING) |
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

4개의 워크플로 뷰(`v_agent_transfer`, `v_agent_state_checkpoint`, `v_event_compaction`, `v_tool_paused`)와 `v_tool_completed`의 `pause_kind` / `function_call_id` 열은 [ADK 2.0 워크플로 이벤트 지원](#adk-2-events)과 함께 제공됩니다. **Java**(v1.7.0+)에서는 `v_tool_paused`와 `v_tool_completed`의 `pause_kind` / `function_call_id` 열만 생성됩니다. `v_agent_transfer`, `v_agent_state_checkpoint`, `v_event_compaction`은 Python 전용입니다(Java 플러그인은 해당 이벤트를 내보내지 않음). `v_node_output` 및 `v_node_error` 뷰는 Python v2.7.0 이상에서 사용할 수 있습니다.

기타 Java 뷰의 차이점은 다음과 같습니다.

- Java는 `v_agent_error`, `v_invocation_error`, `v_node_output`, `v_node_error` 이벤트를 내보내지 않으므로 해당 뷰를 생성하지 않습니다.
- Java의 `v_llm_response`는 `usage_metadata`에서 끝납니다. `usage_thinking_tokens`, `usage_tool_use_tokens`, `cache_metadata`, `cache_type`, `finish_reason`은 노출되지 않습니다.
- Java의 `v_agent_response`는 `response_text` 대신 `text_summary`를 노출합니다.
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
    "tools": ["list_dataset_ids", "execute_sql"],
    "llm_config": {
      "temperature": 0.5,
      "top_p": 0.9
    }
  }
}
```

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
    }
  },
  "latency_ms": {
    "time_to_first_token_ms": 2579,
    "total_ms": 2579
  }
}
```

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
| `LOCAL` | `FunctionTool` 인스턴스(로컬 Python 함수) |
| `MCP` | Model Context Protocol 도구(`McpTool` 인스턴스) |
| `SUB_AGENT` | `AgentTool` 인스턴스(하위 에이전트) |
| `A2A` | 원격 Agent2Agent 인스턴스(`RemoteA2aAgent`) |
| `TRANSFER_AGENT` | `TransferToAgentTool` 인스턴스(일반 에이전트 transfer) |
| `TRANSFER_A2A` | `RemoteA2aAgent`로 transfer하는 `TransferToAgentTool` 인스턴스(호출 수준에서 분류) |
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

도구 실행이 예외로 실패할 때 기록됩니다. 도구 이름, 인수, 도구 출처, 오류
메시지를 캡처합니다.

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

    `temp:` 또는 `secret:` 접두사가 붙은 상태 키는 기록되는 `state_delta`에서
    자동으로 `[REDACTED]`로 마스킹됩니다. 자세한 내용은 [내장
    마스킹](#built-in-redaction)을 참고하세요.

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
| `AGENT_STARTING` | `"You are a helpful agent..."` |
| `AGENT_COMPLETED` | `{}` |
| `USER_MESSAGE_RECEIVED` | `{"text_summary": "Help me book a flight."}` |
| `AGENT_RESPONSE` | `{"response": "Here are the flights..."}` |

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

### 에이전트 워크플로 및 일시중지/재개 이벤트 (ADK 2.0) {#adk-2-events}

<div class="language-support-tag">
  <span class="lst-supported">ADK 지원 버전</span><span class="lst-python">Python v2.3.0</span><span class="lst-java">Java v1.7.0</span>
</div>

!!! note "Java 지원"

    **Java** 플러그인은 이 섹션의 일부만 지원합니다. `TOOL_PAUSED` 및 아래에 설명된 일시중지/재개 페어링을 내보내지만, `AGENT_TRANSFER`, `AGENT_STATE_CHECKPOINT` 또는 `EVENT_COMPACTION`은 내보내지 **않으며**, `attributes.adk` 엔벨로프를 작성하지 않습니다. Java 플러그인은 대신 `pause_kind` 및 `function_call_id`를 `attributes`의 **최상위 수준**에 저장합니다(아래 쿼리 참고사항 참조).

ADK 2.0에서는 멀티 에이전트 워크플로(제어권을 넘기는 에이전트, 상태 체크포인트를 수행하는 에이전트, 긴 기록을 압축하는 에이전트)와 여러 턴에 걸쳐 일시중지 및 재개되는 장기 실행 도구가 도입되었습니다. 플러그인은 네 가지 새로운 이벤트 유형과 작은 메타데이터 엔벨로프인 `attributes.adk`를 통해 이러한 흐름을 관측할 수 있도록 하여, 해당 행을 이를 생성한 ADK 이벤트와 연결합니다.

#### `attributes.adk` 엔벨로프

이 엔벨로프는 **Python** 플러그인에서만 작성됩니다. 이제 모든 행에 `attributes.adk` 객체가 포함됩니다. `schema_version`과 `app_name`은 항상 존재합니다. 나머지 필드는 ADK 이벤트(수명 주기 및 워크플로 이벤트)에서 생성된 행에만 추가되므로, 콜백 전용 행에는 단순히 존재하지 않습니다(쿼리 시 SQL `NULL`로 해석됨).

| 필드 | 유형 | 의미 |
| --- | --- | --- |
| `schema_version` | string | 엔벨로프 버전(현재 `"1"`). 엔벨로프가 발전함에 따라 다운스트림 쿼리를 이에 맞춰 제어할 수 있습니다. |
| `app_name` | string | 해당 행을 생성한 ADK 앱입니다. |
| `source_event_id` | string | 원본 ADK `Event`의 ID입니다. 단일 이벤트가 생성할 수 있는 여러 행을 조인하기 위한 신뢰할 수 있는 키입니다. |
| `node` | object | 워크플로 노드 ID: `{ "path", "run_id", "parent_run_id" }`. `parent_run_id`는 상위 노드의 실행 ID입니다(루트에서는 `null`). |
| `branch` | string | 워크플로가 분기된 경로를 실행할 때 이벤트의 브랜치입니다. |
| `scope` | object | 격리 범위 `{ "id", "kind" }`입니다. 여기서 `kind`는 `node_run`(워크플로 노드 실행, 예: `loopA@42`), `function_call`(모델이 생성한 호출 ID) 또는 `unknown`입니다. |
| `route` | string | 이벤트 액션에 의해 선택된 라우트입니다(설정된 경우). |
| `render_ui_widgets` | array | 이벤트 액션에서 요청한 직렬화된 UI 위젯입니다(설정된 경우). |
| `rewind_before_invocation_id` | string | 이벤트 액션이 되감기를 요청하는 기준 호출 ID입니다(설정된 경우). |
| `pause_kind` | string | `TOOL_PAUSED`의 경우: 일반 장기 실행 도구는 `tool`, HITL 요청은 `hitl_credential` / `hitl_confirmation` / `hitl_input`입니다. 재개된 `TOOL_COMPLETED` 행에서는 항상 `tool`입니다. HITL 완료는 `TOOL_COMPLETED`가 아닌 `HITL_*_REQUEST_COMPLETED`로 기록됩니다. |
| `function_call_id` | string | 함수 호출 ID입니다. 둘을 페어링할 수 있도록 `TOOL_PAUSED` 및 일치하는 재개된 `TOOL_COMPLETED` 행에 설정됩니다(일반 도구만 해당). |

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

에이전트가 상태의 스냅샷을 생성할 때 기록됩니다. 플러그인은 또한 에이전트 실행의 끝을 표시하기 위해 `end_of_agent: true`를 포함하는 체크포인트를 내보냅니다. `v_agent_state_checkpoint` 뷰는 `agent_state_type`을 노출하므로 실제 상태 객체와 명시적 `null` 체크포인트(실행 종료 마커) 및 누락된 값을 구분할 수 있습니다.

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
  <span class="lst-supported">ADK 지원 버전</span><span class="lst-python">Python v2.7.0</span>
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

`BigQueryLoggerConfig`에 `gcs_bucket_name`이 구성되면 플러그인은 큰 텍스트와
멀티모달 콘텐츠(이미지, 오디오 등)를 Google Cloud Storage로 자동 오프로딩합니다.
`content` 컬럼에는 요약 또는 placeholder가 포함되고, `content_parts`에는 GCS URI를
가리키는 `object_ref`가 저장됩니다. [구성 옵션](#configuration-options)의
`connection_id`와 `max_content_length`도 참고하세요.

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
        "uri": "gs://sample-bucket-name/2025-12-10/e-f9545d6d/ae5235e6_p1.txt",
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
        "uri": "gs://sample-bucket-name/2025-12-10/e-f9545d6d/ae5235e6_p2.png",
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

    BigQuery Agent Analytics 플러그인은 도구 인수, LLM 프롬프트, 인증 관련 이벤트(HITL 자격 증명 요청 등)를 포함하여 자세한 이벤트 페이로드를 캡처합니다. 기본 제공 수정(redaction)은 소문자 변환 및 하이픈 정규화 후 키 이름을 정확히 일치시키므로 `clientSecret` 또는 `accessToken`과 같은 카멜표기법(camelCase) 변형은 일치하지 **않습니다**. ADK는 `adk_request_credential` 인수를 카멜표기법 별칭으로 직렬화하므로, `AuthenticatedFunctionTool` OAuth2 흐름에서 `client_secret` 및 `access_token` 값이 여전히 `content` 열에 기록될 수 있습니다([google/adk-python#3845](https://github.com/google/adk-python/issues/3845), 현재 열려 있음). 수정 기능은 범용 데이터 손실 방지(DLP) 시스템이 아니므로 애플리케이션별 키 또는 자유 형식 텍스트에 포함된 시크릿도 BigQuery에 기록될 수 있습니다.

플러그인에는 일반적인 시크릿을 자동으로 보호하는 **기본 제공 수정** 기능이 포함되어 있습니다. 추가 제어가 필요한 경우 그 위에 커스텀 수정을 계층화할 수 있습니다.

### 기본 제공 수정(Built-in redaction) {#built-in-redaction}

<div class="language-support-tag">
  <span class="lst-supported">ADK 지원 버전</span><span class="lst-python">Python</span><span class="lst-java">Java v1.7.0</span>
</div>

Python 플러그인은 키 이름을 소문자로 정규화하고 하이픈을 밑줄처럼 취급합니다. 구조화된 `content` 또는 `attributes`의 어디에 나타나든 다음 키의 값을 재귀적으로 `[REDACTED]`로 바꿉니다.

`client_secret`, `access_token`, `refresh_token`, `id_token`, `api_key`,
`password`, `private_key`, `proxy_authorization`, `google_access_id`, `sig`,
`signature`, `token`, `secret`, `authorization`, `x_api_key`,
`x_amz_credential`, `x_amz_signature`, `x_goog_credential`,
`x_goog_security_token`, `x_goog_signature`

세션 상태 및 `state_delta` 행을 포함하여 **`temp:`** 접두사가 붙은 모든 키도 `[REDACTED]`로 바뀝니다.

!!! warning "수정 안내: 세션 상태에서는 `temp:`만 수정됩니다"

    이전 문서에서는 `secret:` 접두사가 붙은 키도 수정된다고 잘못 명시되었습니다. 플러그인은 `temp:` 접두사만 일치시킵니다. 세션 상태에 `secret:`(예: `secret:token`) 아래에 시크릿을 저장하는 경우 커스텀 `content_formatter`로 마스킹하지 않는 한 일반 텍스트로 로깅됩니다. 해당 안내를 신뢰했던 경우 기존 `agent_events` 테이블에서 `temp:`가 아닌 키 아래에 기록된 값이 있는지 감사하세요.

플러그인은 또한 `error_message`, 에이전트 및 실행 트레이스백, 외부 URI에서 자격 증명 패턴을 정제합니다. 여기에는 인증 헤더, bearer 및 basic 자격 증명, 서명된 URL 쿼리 매개변수, 위의 민감한 이름을 사용하는 키/값 조각이 포함됩니다. 안전하게 다시 작성할 수 없는 인코딩된 자격 증명 구문은 fail-closed(차단) 처리됩니다.

!!! info "별도 구성 불필요"

    구조화된 속성 및 상태 로깅에 대해 기본 제공 수정이 항상 활성화되어 있으며, 속성 값 내의 중첩된 딕셔너리 및 JSON 인코딩 문자열에 재귀적으로 적용됩니다. 커스텀 `content_formatter`는 원시 콘텐츠에 대해 **먼저** 실행됩니다. 오류가 발생하거나 지원되지 않는 유형을 반환하는 경우 Python은 원본 콘텐츠 대신 `[FORMATTER_FAILED]`를 작성하고 `formatter_failed` 인시던트 카운터를 증가시킵니다.

!!! note "Java의 기본 제공 수정"

    Java 플러그인은 v1.7.0 이상에서 기본 제공 수정을 포함합니다.
    세션 상태 및 상태 델타를 포함하여 조립된 `attributes` 트리 전반에서 `client_secret`, `access_token`, `refresh_token`, `id_token`, `api_key`, `password`(대소문자 구분 없음) 및 **`temp:`** 접두사가 붙은 모든 키를 재귀적으로 수정합니다. 시크릿을 다른 상태 범위에 두지 않거나 커스텀 `contentFormatter`로 마스킹하세요.

    커스텀 Java `contentFormatter`는 **스레드 안전**해야 하며(호출 간에 동시에 호출됨), **빠르고 비차단(non-blocking)**이어야 하고(이벤트 처리 경로에서 실행됨), 수신한 콘텐츠를 변경하는 대신 **새 객체**를 반환해야 합니다. 예외가 발생하는 경우 Java 플러그인은 포맷되지 않은 페이로드를 기록하는 대신 행의 콘텐츠를 드롭(fail-closed)합니다.

### `content_formatter`를 사용하여 추가 시크릿 수정

`BigQueryLoggerConfig`에서 커스텀 `content_formatter` 함수를 제공하여 민감한 필드가 기록되기 전에 제거하거나 마스킹합니다.

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

### 추적 및 관측 가능성

플러그인은 부모-자식 실행 트리(에이전트 → LLM 호출 / 도구 호출)가 BigQuery에서 깔끔하게 재구성될 수 있도록 방출되는 모든 행에 `trace_id`, `span_id`, `parent_span_id` 열을 채웁니다.

- **내부 span 추적, OTel span 내보내기 없음.** 플러그인은 16자리 16진수 `span_id` 값의 자체 내부 스택에서 부모-자식 계층 구조를 추적합니다. 루트 호출 span은 주변 OTel span이 활성화되어 있을 때 해당 ID를 재사용합니다(러너의 호출 span과 일치시킴). 하위 BQAA span은 내부적으로 생성됩니다. 구성된 OpenTelemetry `TracerProvider`에서 `tracer.start_span(...)`을 호출하지 **않으므로**, 계측이 구성된 내보내기 도구(exporter)에 전달되지 않습니다. 이는 Agent Engine 원격 분석(`GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY=true`)이 활성화되어 있거나 호스트 프로세스에 다른 Cloud Trace 내보내기 도구를 연결할 때 Cloud Trace에 중복 span이 발생하는 것을 방지합니다. 동일한 내부 ID 전용 span 추적이 v1.7.0 이상의 Java 플러그인에도 적용됩니다. 이전 Java 빌드는 프레임워크 span 옆에 중복으로 나타날 수 있는 플러그인 소유 OpenTelemetry span을 생성했습니다.
- **주변 OTel span이 있는 경우 `trace_id` 상속.** 주변 런타임이 Agent Engine의 호출 span, ADK `Runner` 호출 span 또는 에이전트 실행 전에 시작한 임의의 span과 같은 OTel span을 이미 시작한 경우, 플러그인은 해당 `trace_id`를 읽어 모든 BigQuery 행에 스탬프합니다. 이를 통해 BigQuery 테이블과 외부 분산 트레이스 간에 일대일 상관관계가 설정됩니다. 주변 span이 없으면 플러그인은 호출당 고유한 32자리 16진수 `trace_id`를 생성하여 해당 호출 내의 모든 작업에 적용합니다.
- **부모-자식 관계가 명시적으로 보존됨.** 플러그인의 내부 스택은 각 하위 작업(`LLM_REQUEST`, `TOOL_STARTING` 등)이 올바른 호출 또는 에이전트 수준 `span_id`를 `parent_span_id`로 참조하도록 보장합니다.

### 공개 메서드

=== "Python"

    `BigQueryAgentAnalyticsPlugin`은 수명 주기 및 유지보수 제어를 위해 다음 공개 메서드를 노출합니다.

    - **`await plugin.flush()`**: 백그라운드 쓰기 큐가 비워질 때까지 대기합니다. 기본 제공 `after_run_callback`은 실행마다 이를 자동으로 수행합니다. 프로세스 종료 전에 명시적으로 호출하거나 턴 간에 조기 지속성을 보장하기 위해 호출할 수 있습니다.
    - **`await plugin.close()`**: 큐를 플러그인 종료 타임스탬프(`shutdown_timeout`에 바인딩됨)까지 비우고, 백그라운드 워커를 취소하며, BigQuery 쓰기 클라이언트 세션을 닫습니다. `App` 종료 시 호출해야 합니다.
    - **`await plugin.create_analytics_views()`**: BigQuery에서 분석 뷰 세트를 멱등원(idempotent) 방식으로 다시 생성하거나 새로고침합니다. 일반적으로 `create_views=True`를 통해 초기화 시 자동으로 호출되지만 수동 스키마 업그레이드 후 명시적으로 호출할 수도 있습니다.
    - **`plugin.get_drop_stats()`** (v2.7.0+): 플러그인 시작 이후 드롭된 이벤트 수에 대한 스냅샷인 딕셔너리(`{reason: count}`)를 반환합니다. 자세한 내용은 [드롭된 이벤트 관측 가능성](#dropped-event-observability)을 참고하세요.

    ```python
    # 수동 플러시 및 정상 종료
    await plugin.flush()
    await plugin.close()
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
  <span class="lst-supported">ADK 지원 버전</span><span class="lst-python">Python</span><span class="lst-java">Java v1.7.0</span>
</div>

BigQuery 로깅은 최선형(best-effort) 방식입니다. 인메모리 대기열이 넘치거나, 설정을 사용할 수 없거나, 종료가 콜백과 경쟁하거나, 쓰기가 궁극적으로 실패할 때 이벤트가 드롭될 수 있습니다. 플러그인은 또한 콘텐츠 대신 센티널을 포함하여 행이 작성되는 포맷터 및 파서 오류도 집계합니다. 이러한 카운터는 루프 정리 및 종료 전반에 걸쳐 유지됩니다.

**드롭 원인 (Python):**

| 원인 | 이유 |
|---|---|
| `queue_full` | 인메모리 일괄 큐가 오버플로되었습니다(호스트가 드레이너가 전송할 수 있는 것보다 빠르게 이벤트를 생성함). `BigQueryLoggerConfig`에서 `queue_max_size`를 늘리거나, `batch_size`를 늘려 더 큰 청크로 드레인하거나, 소비자 측을 확장하세요(더 많은 동시 호출이 더 빠르게 완료되도록 함). |
| `arrow_prep_failed` | 행을 Arrow 표현으로 변환할 수 없습니다(일반적으로 스키마/유형 불일치). 문제가 되는 필드가 있는지 로그를 검사하세요. |
| `retry_exhausted` | 재시도 예산이 소진될 때까지 Storage Write API 호출이 재시도 가능한 오류(예: 일시적인 gRPC 실패)를 계속 반환했습니다. |
| `non_retryable` | Storage Write API가 재시도할 수 없는 오류(권한, 할당량, 스키마 거부)를 반환했습니다. 일반적으로 운영자의 개입이 필요합니다. |
| `unexpected_error` | 배치를 준비하거나 작성하는 동안 발생한 기타 예외입니다. |
| `shutdown_timeout` | 바인딩된 종료 또는 닫기 시간이 초과되었을 때 대기열에 행이 남아 있었습니다. |
| `shutdown_cancelled` | 외부 닫기 시간 초과 등 호스트에 의해 종료가 취소되었을 때 대기열에 행이 남아 있었습니다. |
| `offset_conflict` | `exactly_once_delivery` 모드에서 커밋된 스트림이 오프셋을 거부했거나 교체 스트림을 사용할 수 없었습니다. |
| `setup_unavailable` | 플러그인 설정이 실패했거나 재시도 백오프 상태로 남아 행을 허용할 수 없었습니다. |
| `shutdown_race` | 종료가 시작되거나 진행 중인 동안 콜백이 행 허용을 시도했습니다. |
| `stale_loop` | 대기 중인 행이 이미 닫혀 더 이상 드레인할 수 없는 이벤트 루프에 속해 있었습니다. |
| `formatter_failed` | 커스텀 포맷터가 실패했거나 지원되지 않는 유형을 반환했습니다. 행은 여전히 `[FORMATTER_FAILED]`로 작성됩니다. 이는 드롭된 행 수가 아니라 인시던트 수입니다. |
| `content_parse_failed` | 콘텐츠 파싱에 실패했습니다. 행은 여전히 `[CONTENT_PARSE_FAILED]`로 작성됩니다. 이는 드롭된 행 수가 아니라 인시던트 수입니다. |

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
    #      "formatter_failed": 1, ...}

    loss_reasons = {
        "queue_full", "arrow_prep_failed", "retry_exhausted",
        "non_retryable", "unexpected_error", "shutdown_timeout",
        "shutdown_cancelled", "offset_conflict", "setup_unavailable",
        "shutdown_race", "stale_loop",
    }
    total_rows_lost = sum(stats.get(reason, 0) for reason in loss_reasons)
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

0이 아닌 모든 이유에 대해 알림을 설정하세요. 대부분의 이유는 BigQuery에 도달하기 전에 행이 손실되었음을 의미합니다. 반면 `formatter_failed` 및 `content_parse_failed` 이유는 행이 센티널 콘텐츠와 함께 기록되었음을 의미하므로 개인 정보 보호 또는 데이터 품질 인시던트로 알림을 설정하세요. `queue_full`, `retry_exhausted`, `non_retryable` 또는 `offset_conflict` 수가 지속적으로 높다면 일반적으로 처리량, 전송 또는 Storage Write 상태에 문제가 있음을 나타냅니다. Java에서 이에 상응하는 쓰기 오류 버킷은 `append_error`입니다.

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
- [BigQuery Storage Write API](https://cloud.google.com/bigquery/docs/write-api)
- [객체 테이블 소개](https://docs.cloud.google.com/bigquery/docs/object-table-introduction)
- [BigQuery Agent Analytics SDK 예제](https://github.com/GoogleCloudPlatform/BigQuery-Agent-Analytics-SDK/tree/main/examples)
