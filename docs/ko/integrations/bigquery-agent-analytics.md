---
catalog_title: BigQuery Agent Analytics Plugin
catalog_description: 에이전트 동작 분석과 로깅을 위한 심층 분석 기능을 제공합니다
catalog_icon: /integrations/assets/bigquery.png
catalog_tags: ["observability", "google"]
---

# ADK용 BigQuery Agent Analytics 플러그인

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.21.0</span>
</div>

!!! important "버전 요구사항"

    auto-schema-upgrade, tool provenance 추적, HITL 이벤트 추적을 포함해 이
    문서의 기능을 온전히 활용하려면 ADK Python 버전 1.26.0 이상을 사용하세요.

BigQuery Agent Analytics Plugin은 심층적인 에이전트 동작 분석을 위한 견고한
솔루션을 제공하여 Agent Development Kit(ADK)를 크게 확장합니다. ADK Plugin
아키텍처와 **BigQuery Storage Write API**를 사용해 중요한 운영 이벤트를 Google
BigQuery 테이블에 직접 캡처하고 기록하므로, 디버깅, 실시간 모니터링, 포괄적인
오프라인 성능 평가를 위한 고급 기능을 활용할 수 있습니다.

버전 1.26.0에서는 **Auto Schema Upgrade**(기존 테이블에 새 컬럼을 안전하게
추가), **Tool Provenance** 추적(LOCAL, MCP, SUB_AGENT, A2A, TRANSFER_AGENT,
TRANSFER_A2A), 사람-개입형 상호작용을 위한 **HITL Event Tracing**이
추가되었습니다. 버전 1.27.0에서는 **Automatic View Creation**(평탄화된 쿼리
친화적 이벤트 뷰 생성)이 추가되었습니다.

!!! warning "BigQuery Storage Write API"

    이 기능은 유료 서비스인 **BigQuery Storage Write API**를 사용합니다. 비용
    정보는 [BigQuery
    문서](https://cloud.google.com/bigquery/pricing?e=48754805&hl=en#data-ingestion-pricing)를
    참고하세요.

## 사용 사례

- **에이전트 워크플로 디버깅 및 분석:** 다양한 *플러그인 수명 주기 이벤트*
  (LLM 호출, 도구 사용)와 *에이전트가 생성한 이벤트*(사용자 입력, 모델 응답)를
  잘 정의된 스키마에 캡처합니다.
- **대량 분석 및 디버깅:** 로깅 작업은 Storage Write API를 사용해 비동기적으로
  수행되므로 높은 처리량과 낮은 지연 시간을 동시에 달성할 수 있습니다.
- **멀티모달 분석:** 텍스트, 이미지, 기타 modality를 기록하고 분석합니다. 대용량
  파일은 GCS로 오프로딩되어 Object Table을 통해 BigQuery ML에서 활용할 수
  있습니다.
- **분산 추적:** `trace_id`, `span_id` 기반 OpenTelemetry 스타일 추적을 기본
  지원하여 에이전트 실행 흐름을 시각화할 수 있습니다.
- **Tool Provenance:** 각 도구 호출의 출처(로컬 함수, MCP 서버, 하위 에이전트,
  A2A 원격 에이전트, transfer agent)를 추적합니다.
- **Human-in-the-Loop(HITL) 추적:** 자격 증명 요청, 확인 프롬프트, 사용자 입력
  요청을 위한 전용 이벤트 유형을 제공합니다.
- **쿼리 가능한 이벤트 뷰:** 이벤트 유형별 평탄화 BigQuery 뷰(예:
  `v_llm_request`, `v_tool_completed`)를 자동 생성하여 JSON 페이로드 데이터를
  펼친 다운스트림 분석을 단순화합니다.

### 캡처되는 이벤트 요약

다음 표는 플러그인이 기록하는 모든 이벤트 유형을 보여줍니다. 자세한 페이로드
예시는 [이벤트 유형 및 페이로드](#event-types)를 참고하세요. **View** 컬럼은
[`create_views`](#configuration-options)가 활성화된 경우(기본값) 선택적으로
생성되는 BigQuery 뷰를 보여줍니다.

| 이벤트 유형 | 캡처 시점 | 주요 페이로드 필드 | 뷰 |
| --- | --- | --- | --- |
| `USER_MESSAGE_RECEIVED` | 사용자 메시지가 invocation에 들어올 때 | 텍스트 요약 / content parts | `v_user_message_received` |
| `INVOCATION_STARTING` | invocation이 시작될 때 | *(공통 컬럼만)* | `v_invocation_starting` |
| `INVOCATION_COMPLETED` | invocation이 끝날 때 | *(공통 컬럼만)* | `v_invocation_completed` |
| `AGENT_STARTING` | 에이전트 실행이 시작될 때 | instruction 요약 | `v_agent_starting` |
| `AGENT_COMPLETED` | 에이전트 실행이 끝날 때 | 지연 시간 | `v_agent_completed` |
| `LLM_REQUEST` | 모델 요청이 전송될 때 | 모델, 프롬프트, 설정, 도구 | `v_llm_request` |
| `LLM_RESPONSE` | 모델 응답을 받을 때 | 응답, 사용 토큰, 캐시 메타데이터, 지연 시간, TTFT | `v_llm_response` |
| `LLM_ERROR` | 모델 호출이 실패할 때 | 오류 메시지, 지연 시간 | `v_llm_error` |
| `TOOL_STARTING` | 도구 실행이 시작될 때 | 도구 이름, 인수, 출처 | `v_tool_starting` |
| `TOOL_COMPLETED` | 도구 실행이 성공할 때 | 도구 이름, 결과, 출처, 지연 시간 | `v_tool_completed` |
| `TOOL_ERROR` | 도구 실행이 실패할 때 | 도구 이름, 인수, 출처, 오류, 지연 시간 | `v_tool_error` |
| `STATE_DELTA` | 세션 상태가 변경될 때 | 상태 delta | `v_state_delta` |
| `HITL_CREDENTIAL_REQUEST` | 자격 증명 요청이 발생할 때 | synthetic 도구 이름, 인수 | `v_hitl_credential_request` |
| `HITL_CONFIRMATION_REQUEST` | 확인 요청이 발생할 때 | synthetic 도구 이름, 인수 | `v_hitl_confirmation_request` |
| `HITL_INPUT_REQUEST` | 사용자 입력 요청이 발생할 때 | synthetic 도구 이름, 인수 | `v_hitl_input_request` |
| `HITL_CREDENTIAL_REQUEST_COMPLETED` | 사용자가 자격 증명 응답을 제공할 때 | synthetic 도구 이름, 결과 | *(기본 테이블만)* |
| `HITL_CONFIRMATION_REQUEST_COMPLETED` | 사용자가 확인 응답을 제공할 때 | synthetic 도구 이름, 결과 | *(기본 테이블만)* |
| `HITL_INPUT_REQUEST_COMPLETED` | 사용자가 입력 응답을 제공할 때 | synthetic 도구 이름, 결과 | *(기본 테이블만)* |
| `A2A_INTERACTION` | 원격 A2A 호출이 완료될 때 | 응답, task ID, context ID, request/response | `v_a2a_interaction` |
| `AGENT_RESPONSE` | 최종 에이전트 응답이 yield될 때 | 응답(content), source event ID/author/branch(attributes) | `v_agent_response` |

## 빠른 시작

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
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'True'

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

### 에이전트 실행 및 테스트

채팅 인터페이스에서 에이전트를 실행하고 `"tell me what you can do"` 또는
`"List datasets in my cloud project <your-gcp-project-id>"` 같은 요청을 몇 번
보내 플러그인을 테스트합니다. 이러한 동작은 Google Cloud 프로젝트의 BigQuery
인스턴스에 기록되는 이벤트를 생성합니다. 이벤트가 처리된 뒤에는 [BigQuery
Console](https://console.cloud.google.com/bigquery)에서 다음 쿼리로 데이터를
확인할 수 있습니다.

```sql
SELECT timestamp, event_type, content
FROM `your-gcp-project-id.your-big-query-dataset-id.agent_events`
ORDER BY timestamp DESC
LIMIT 20;
```

??? example "GCS 오프로딩, OpenTelemetry, BigQuery 도구를 포함한 전체 예시"

    ```python title="my_bq_agent/agent.py"
    # my_bq_agent/agent.py
    import os
    import google.auth
    from google.adk.apps import App
    from google.adk.plugins.bigquery_agent_analytics_plugin import BigQueryAgentAnalyticsPlugin, BigQueryLoggerConfig
    from google.adk.agents import Agent
    from google.adk.models.google_llm import Gemini
    from google.adk.tools.bigquery import BigQueryToolset, BigQueryCredentialsConfig


    # --- OpenTelemetry TracerProvider Setup (Optional) ---
    # ADK includes OpenTelemetry as a core dependency.
    # Configuring a TracerProvider enables full distributed tracing
    # (populates trace_id, span_id with standard OTel identifiers).
    # If no TracerProvider is configured, the plugin falls back to internal
    # UUIDs for span correlation while still preserving the parent-child hierarchy.
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    trace.set_tracer_provider(TracerProvider())

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
    os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'True'

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

!!! tip "Agent Runtime에 배포하나요?"

    [Agent Runtime에 배포](#deploy-agent-runtime)를 참고하세요.

## 전제 조건 {#prerequisites}

- **BigQuery API**가 활성화된 **Google Cloud 프로젝트**
- **BigQuery 데이터 세트:** 플러그인을 사용하기 전에 로깅 테이블을 저장할 데이터
  세트를 만듭니다. 테이블이 없으면 플러그인이 데이터 세트 안에 필요한 이벤트
  테이블을 자동으로 생성합니다.
- **Google Cloud Storage 버킷(선택 사항):** 멀티모달 콘텐츠(이미지, 오디오 등)를
  기록할 계획이라면 대용량 파일 오프로딩을 위해 GCS 버킷을 만들어 두는 것이
  좋습니다.
- **인증:**
    - **로컬:** `gcloud auth application-default login`을 실행합니다.
    - **클라우드:** 서비스 계정에 필요한 권한이 있는지 확인합니다.

??? note "참고: Gemini 모델 선택자 `gemini-flash-latest`"

    ADK 문서의 대부분 코드 예제는 `gemini-flash-latest`를 사용해
    [최신 사용 가능](https://ai.google.dev/gemini-api/docs/models#latest)
    Gemini Flash 버전을 선택합니다. 다만 `us-central1` 같은 지역 엔드포인트에서
    Gemini에 접근하는 경우 이 선택 문자열이 동작하지 않을 수 있습니다. 그런
    경우 [Gemini 모델](https://ai.google.dev/gemini-api/docs/models) 페이지나
    Google Cloud [Gemini
    모델](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models)
    목록에서 구체적인 모델 버전 문자열을 사용하세요.

### IAM 권한 {#iam-permissions}

에이전트가 정상적으로 동작하려면 에이전트가 실행되는 주체(예: 서비스 계정,
사용자 계정)에 다음 Google Cloud 역할이 필요합니다.

- `roles/bigquery.jobUser`: 프로젝트 수준에서 BigQuery 쿼리를 실행하기 위한 권한
- `roles/bigquery.dataEditor`: 테이블 수준에서 로그/이벤트 데이터를 쓰기 위한 권한
- **GCS 오프로딩 사용 시:** 대상 버킷에 대한 `roles/storage.objectCreator` 및
  `roles/storage.objectViewer`

## 구성 옵션 {#configuration-options}

### 생성자 파라미터

`BigQueryAgentAnalyticsPlugin` 생성자는 다음 파라미터를 받습니다. 또한 아래의
`BigQueryLoggerConfig`로 직접 전달되는 `**kwargs`도 받을 수 있습니다.

| 파라미터 | 타입 | 기본값 | 사용 시점 |
| --- | --- | --- | --- |
| `project_id` | `str` | *(필수)* | Google Cloud 프로젝트를 선택합니다 |
| `dataset_id` | `str` | *(필수)* | BigQuery 데이터 세트를 선택합니다 |
| `table_id` | `Optional[str]` | `None` | 사용자 지정 테이블 이름을 사용합니다(config `table_id`를 재정의) |
| `config` | `Optional[BigQueryLoggerConfig]` | `None` | 세부 튜닝을 위한 config 객체를 전달합니다 |
| `location` | `str` | `"US"` | BigQuery 데이터 세트 위치와 맞춥니다(예: `"US"`, `"EU"`, `"us-central1"`) |
| `credentials` | `Optional[google.auth.credentials.Credentials]` | `None` | [ADC](https://cloud.google.com/docs/authentication/application-default-credentials) 대신 명시적 서비스 계정, impersonated, cross-project 자격 증명을 사용합니다 |

```python
plugin = BigQueryAgentAnalyticsPlugin(
    project_id="my-project",
    dataset_id="my_dataset",
    batch_size=10,           # forwarded to BigQueryLoggerConfig
    shutdown_timeout=5.0,    # forwarded to BigQueryLoggerConfig
)
```

### BigQueryLoggerConfig 옵션

아래 옵션은 모두 선택 사항이며 합리적인 기본값을 제공합니다.
`BigQueryLoggerConfig`에 전달하거나 플러그인 생성자의 `**kwargs`로 전달하세요.

| 옵션 | 타입 | 기본값 | 사용 시점 |
| --- | --- | --- | --- |
| `enabled` | `bool` | `True` | 로깅을 일시적으로 비활성화합니다 |
| `table_id` | `str` | `"agent_events"` | 사용자 지정 테이블 이름을 사용합니다(생성자 값이 우선) |
| `clustering_fields` | `List[str]` | `["event_type", "agent", "user_id"]` | 테이블 생성 시 클러스터링을 맞춤설정합니다 |
| `gcs_bucket_name` | `Optional[str]` | `None` | 큰 텍스트와 멀티모달 콘텐츠를 GCS로 오프로딩합니다 |
| `connection_id` | `Optional[str]` | `None` | BigQuery ObjectRef / object table을 사용합니다(예: `us.my-connection`) |
| `max_content_length` | `int` | `500 * 1024` | 오프로딩/자르기 전 인라인 페이로드 크기를 제어합니다 |
| `batch_size` | `int` | `1` | 쓰기 처리량과 지연 시간의 균형을 조정합니다 |
| `batch_flush_interval` | `float` | `1.0` | 부분 batch를 주기적으로 flush합니다(초) |
| `shutdown_timeout` | `float` | `10.0` | 종료 시 최종 flush를 기다립니다(초) |
| `event_allowlist` | `Optional[List[str]]` | `None` | 선택한 [이벤트 유형](#event-types)만 기록합니다 |
| `event_denylist` | `Optional[List[str]]` | `None` | 민감하거나 노이즈가 큰 [이벤트 유형](#event-types)을 건너뜁니다 |
| `content_formatter` | `Optional[Callable]` | `None` | 이벤트별 맞춤 마스킹/포맷팅을 적용합니다(`(content, event_type)` 수신) |
| `log_multi_modal_content` | `bool` | `True` | GCS 참조를 포함해 `content_parts` 세부 정보를 캡처합니다 |
| `queue_max_size` | `int` | `10000` | 메모리 내 이벤트 큐 크기를 제한합니다 |
| `retry_config` | `RetryConfig` | `RetryConfig()` | 재시도 동작을 조정합니다(`max_retries=3`, `initial_delay=1.0`, `multiplier=2.0`, `max_delay=10.0`) |
| `log_session_metadata` | `bool` | `True` | `attributes`에 세션 정보(`session_id`, `app_name`, `user_id`, `state`)를 추가합니다. `temp:` 또는 `secret:` 접두사가 붙은 키는 [마스킹](#built-in-redaction)됩니다. |
| `custom_tags` | `Dict[str, Any]` | `{}` | 모든 이벤트의 `attributes`에 정적 태그(예: `{"env": "prod"}`)를 추가합니다 |
| `auto_schema_upgrade` | `bool` | `True` | 기존 테이블에 새 컬럼을 자동 추가합니다(추가 변경만) |
| `create_views` | `bool` | `True` | 이벤트 유형별 BigQuery 뷰를 생성합니다(1.27.0+) |
| `view_prefix` | `str` | `"v"` | 여러 플러그인이 같은 데이터 세트를 공유할 때 뷰 이름 충돌을 피합니다(예: `"v_staging"`) |

다음 코드는 BigQuery Agent Analytics 플러그인용 구성을 정의하는 방법을 보여줍니다.

```python
import json
import re

from google.adk.plugins.bigquery_agent_analytics_plugin import BigQueryLoggerConfig

def redact_dollar_amounts(event_content: Any, event_type: str) -> str:
    """
    Custom formatter to redact dollar amounts (e.g., $600, $12.50)
    and ensure JSON output if the input is a dict.

    Args:
        event_content: The raw content of the event.
        event_type: The event type string (e.g., "LLM_REQUEST", "LLM_RESPONSE").
    """
    text_content = ""
    if isinstance(event_content, dict):
        text_content = json.dumps(event_content)
    else:
        text_content = str(event_content)

    # Regex to find dollar amounts: $ followed by digits, optionally with commas or decimals.
    # Examples: $600, $1,200.50, $0.99
    redacted_content = re.sub(r'\$\d+(?:,\d{3})*(?:\.\d+)?', 'xxx', text_content)

    return redacted_content

config = BigQueryLoggerConfig(
    enabled=True,
    event_allowlist=["LLM_REQUEST", "LLM_RESPONSE"], # Only log these events
    # event_denylist=["TOOL_STARTING"], # Skip these events
    shutdown_timeout=10.0, # Wait up to 10s for logs to flush on exit
    max_content_length=500, # Truncate content to 500 chars
    content_formatter=redact_dollar_amounts, # Redact the dollar amounts in the logging content
    queue_max_size=10000, # Max events to hold in memory
    auto_schema_upgrade=True, # Automatically add new columns to existing tables
    create_views=True, # Automatically create per-event-type views
    # retry_config=RetryConfig(max_retries=3), # Optional: Configure retries
)

plugin = BigQueryAgentAnalyticsPlugin(
    project_id="my-project",
    dataset_id="my_dataset",
    config=config,
)
```

## 스키마 및 프로덕션 설정

### 스키마 참조

이벤트 테이블(`agent_events`)은 유연한 스키마를 사용합니다. 다음 표는 예시 값이
포함된 포괄적인 참조를 제공합니다.

| 필드 이름 | 타입 | 모드 | 설명 | 예시 값 |
| --- | --- | --- | --- | --- |
| **timestamp** | `TIMESTAMP` | `REQUIRED` | 이벤트 생성의 UTC 타임스탬프입니다. 기본 정렬 키이자 일별 파티션 키입니다. 정밀도는 마이크로초입니다. | `2026-02-03 20:52:17 UTC` |
| **event_type** | `STRING` | `NULLABLE` | 정규화된 이벤트 범주입니다. 표준 값에는 `LLM_REQUEST`, `LLM_RESPONSE`, `LLM_ERROR`, `TOOL_STARTING`, `TOOL_COMPLETED`, `TOOL_ERROR`, `AGENT_STARTING`, `AGENT_COMPLETED`, `STATE_DELTA`, `INVOCATION_STARTING`, `INVOCATION_COMPLETED`, `USER_MESSAGE_RECEIVED`, HITL 이벤트([HITL 이벤트](#hitl-events) 참고)가 포함됩니다. 상위 수준 필터링에 사용됩니다. | `LLM_REQUEST` |
| **agent** | `STRING` | `NULLABLE` | 이 이벤트를 담당하는 에이전트 이름입니다. 에이전트 초기화 또는 `root_agent_name` 컨텍스트를 통해 정의됩니다. | `my_bq_agent` |
| **session_id** | `STRING` | `NULLABLE` | 전체 대화 스레드의 지속 식별자입니다. 여러 턴과 하위 에이전트 호출 전반에서 일정하게 유지됩니다. | `04275a01-1649-4a30-b6a7-5b443c69a7bc` |
| **invocation_id** | `STRING` | `NULLABLE` | 단일 실행 턴 또는 요청 주기의 고유 식별자입니다. 많은 컨텍스트에서 `trace_id`에 해당합니다. | `e-b55b2000-68c6-4e8b-b3b3-ffb454a92e40` |
| **user_id** | `STRING` | `NULLABLE` | 세션을 시작한 사용자(사람 또는 시스템)의 식별자입니다. `User` 객체 또는 메타데이터에서 추출됩니다. | `test_user` |
| **trace_id** | `STRING` | `NULLABLE` | **OpenTelemetry** Trace ID(32자 hex)입니다. 단일 분산 요청 수명 주기 안의 모든 작업을 연결합니다. | `e-b55b2000-68c6-4e8b-b3b3-ffb454a92e40` |
| **span_id** | `STRING` | `NULLABLE` | **OpenTelemetry** Span ID(16자 hex)입니다. 이 특정 원자적 작업을 고유하게 식별합니다. | `69867a836cd94798be2759d8e0d70215` |
| **parent_span_id** | `STRING` | `NULLABLE` | 바로 위 호출자의 Span ID입니다. 부모-자식 실행 트리(DAG)를 재구성하는 데 사용됩니다. | `ef5843fe40764b4b8afec44e78044205` |
| **content** | `JSON` | `NULLABLE` | 기본 이벤트 페이로드입니다. 구조는 `event_type`에 따라 다형적입니다. | `{"system_prompt": "You are...", "prompt": [{"role": "user", "content": "hello"}], "response": "Hi", "usage": {"total": 15}}` |
| **attributes** | `JSON` | `NULLABLE` | 메타데이터/보강 정보(사용량 통계, 모델 정보, 도구 출처, 커스텀 태그)입니다. | `{"model": "gemini-flash-latest", "usage_metadata": {"total_token_count": 15}, "session_metadata": {"session_id": "...", "app_name": "...", "user_id": "...", "state": {}}, "custom_tags": {"env": "prod"}}` |
| **latency_ms** | `JSON` | `NULLABLE` | 성능 지표입니다. 표준 키는 `total_ms`(wall-clock duration)와 `time_to_first_token_ms`(스트리밍 지연 시간)입니다. | `{"total_ms": 1250, "time_to_first_token_ms": 450}` |
| **status** | `STRING` | `NULLABLE` | 상위 수준 결과입니다. 값은 `OK`(성공) 또는 `ERROR`(실패)입니다. | `OK` |
| **error_message** | `STRING` | `NULLABLE` | 사람이 읽을 수 있는 예외 메시지 또는 스택 트레이스 조각입니다. `status`가 `ERROR`일 때만 채워집니다. | `Error 404: Dataset not found` |
| **is_truncated** | `BOOLEAN` | `NULLABLE` | `content` 또는 `attributes`가 BigQuery 셀 크기 제한(기본 10MB)을 초과하여 일부가 제거되면 `true`입니다. | `false` |
| **content_parts** | `RECORD` | `REPEATED` | 멀티모달 세그먼트(Text, Image, Blob)의 배열입니다. 대용량 바이너리나 GCS 참조처럼 content를 단순 JSON으로 직렬화할 수 없을 때 사용됩니다. | `[{"mime_type": "text/plain", "text": "hello"}]` |

테이블이 없으면 플러그인이 자동으로 생성합니다. 프로덕션에서는 아래 DDL을 사용해
테이블을 수동으로 만들 수도 있습니다.

??? example "프로덕션 설정용 수동 DDL"

    ```sql
    CREATE TABLE `your-gcp-project-id.adk_agent_logs.agent_events`
    (
      timestamp TIMESTAMP NOT NULL OPTIONS(description="The UTC time at which the event was logged."),
      event_type STRING OPTIONS(description="Indicates the type of event being logged (e.g., 'LLM_REQUEST', 'TOOL_COMPLETED')."),
      agent STRING OPTIONS(description="The name of the ADK agent or author associated with the event."),
      session_id STRING OPTIONS(description="A unique identifier to group events within a single conversation or user session."),
      invocation_id STRING OPTIONS(description="A unique identifier for each individual agent execution or turn within a session."),
      user_id STRING OPTIONS(description="The identifier of the user associated with the current session."),
      trace_id STRING OPTIONS(description="OpenTelemetry trace ID for distributed tracing."),
      span_id STRING OPTIONS(description="OpenTelemetry span ID for this specific operation."),
      parent_span_id STRING OPTIONS(description="OpenTelemetry parent span ID to reconstruct hierarchy."),
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
      error_message STRING OPTIONS(description="Populated if an error occurs."),
      is_truncated BOOLEAN OPTIONS(description="Flag indicates if content was truncated.")
    )
    PARTITION BY DATE(timestamp)
    CLUSTER BY event_type, agent, user_id;
    ```

### 자동 생성 뷰(1.27.0+)

`create_views=True`(1.27.0 이상에서 기본값)이면 플러그인은 각 이벤트 유형에
대해 공통 JSON 구조를 평탄화된 타입 컬럼으로 펼친 뷰를 자동 생성합니다. 따라서
복잡한 `JSON_VALUE` 또는 `JSON_QUERY` 함수를 직접 작성하지 않아도 SQL을 훨씬
간단하게 쓸 수 있습니다.

뷰 이름은 `{view_prefix}_{event_type_lowercase}` 규칙을 따릅니다. 예를 들어 기본
접두사 `"v"`를 사용하면 `LLM_REQUEST`는 `v_llm_request`가 됩니다. 같은 데이터
세트 안에서 여러 플러그인 인스턴스가 서로 다른 테이블에 기록하는 경우,
`BigQueryLoggerConfig`의 `view_prefix`를 별도 값으로 설정하여 뷰 이름 충돌을
방지하세요.

```python
# Two plugins in the same dataset with distinct view prefixes
plugin_prod = BigQueryAgentAnalyticsPlugin(
    project_id=PROJECT_ID, dataset_id=DATASET_ID,
    table_id="agent_events_prod",
    config=BigQueryLoggerConfig(view_prefix="v_prod"),
)
# Creates views: v_prod_llm_request, v_prod_tool_completed, ...

plugin_staging = BigQueryAgentAnalyticsPlugin(
    project_id=PROJECT_ID, dataset_id=DATASET_ID,
    table_id="agent_events_staging",
    config=BigQueryLoggerConfig(view_prefix="v_staging"),
)
# Creates views: v_staging_llm_request, v_staging_tool_completed, ...
```

예를 들어 스키마 업그레이드 후 뷰를 새로 고쳐야 할 때는 public async 메서드
`await plugin.create_analytics_views()`를 직접 호출할 수도 있습니다.

모든 뷰에는 다음 **공통 컬럼**이 포함됩니다. `timestamp`, `event_type`,
`agent`, `session_id`, `invocation_id`, `user_id`, `trace_id`, `span_id`,
`parent_span_id`, `status`, `error_message`, `is_truncated`.

다음 표는 자동 생성되는 모든 뷰와 이벤트별 컬럼을 보여줍니다.

| 뷰 이름 | 이벤트별 컬럼 |
| --- | --- |
| **`v_user_message_received`** | *(공통 컬럼만)* |
| **`v_llm_request`** | `model` (STRING), `request_content` (JSON), `llm_config` (JSON), `tools` (JSON) |
| **`v_llm_response`** | `response` (JSON), `usage_prompt_tokens` (INT64), `usage_completion_tokens` (INT64), `usage_total_tokens` (INT64), `usage_cached_tokens` (INT64), `total_ms` (INT64), `ttft_ms` (INT64), `model_version` (STRING), `usage_metadata` (JSON), `cache_metadata` (JSON), `context_cache_hit_rate` (FLOAT64) |
| **`v_llm_error`** | `total_ms` (INT64) |
| **`v_tool_starting`** | `tool_name` (STRING), `tool_args` (JSON), `tool_origin` (STRING) |
| **`v_tool_completed`** | `tool_name` (STRING), `tool_result` (JSON), `tool_origin` (STRING), `total_ms` (INT64) |
| **`v_tool_error`** | `tool_name` (STRING), `tool_args` (JSON), `tool_origin` (STRING), `total_ms` (INT64) |
| **`v_agent_starting`** | `agent_instruction` (STRING) |
| **`v_agent_completed`** | `total_ms` (INT64) |
| **`v_invocation_starting`** | *(공통 컬럼만)* |
| **`v_invocation_completed`** | *(공통 컬럼만)* |
| **`v_state_delta`** | `state_delta` (JSON) |
| **`v_hitl_credential_request`** | `tool_name` (STRING), `tool_args` (JSON) |
| **`v_hitl_confirmation_request`** | `tool_name` (STRING), `tool_args` (JSON) |
| **`v_hitl_input_request`** | `tool_name` (STRING), `tool_args` (JSON) |
| **`v_a2a_interaction`** | `response_content` (JSON), `a2a_task_id` (STRING), `a2a_context_id` (STRING), `a2a_request` (JSON), `a2a_response` (JSON) |
| **`v_agent_response`** | `response_text` (STRING), `source_event_id` (STRING), `source_event_author` (STRING), `source_event_branch` (STRING) |

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

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

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

!!! warning "OAuth 토큰, API 키, 클라이언트 보안 비밀을 기록하지 마세요"

    BigQuery Agent Analytics 플러그인은 도구 인수, LLM 프롬프트, 인증 관련
    이벤트(HITL 자격 증명 요청 등)를 포함해 상세한 이벤트 페이로드를 캡처합니다.
    에이전트가 **인증된 도구**(예: OAuth2를 사용하는 `AuthenticatedFunctionTool`)를
    사용하는 경우 플러그인이 `client_secret`, `access_token`, API 키 같은 민감한
    값을 BigQuery 테이블의 `content` 컬럼에 기록할 수 있습니다.

    이는 알려진 우려 사항
    ([google/adk-python#3845](https://github.com/google/adk-python/issues/3845))이며,
    분석 데이터에서 자격 증명이 노출될 수 있습니다.

플러그인은 일반적인 비밀 값을 자동 보호하는 **내장 마스킹**을 포함합니다. 추가
제어가 필요하면 커스텀 마스킹을 그 위에 계층화할 수 있습니다.

### 내장 마스킹 {#built-in-redaction}

플러그인은 `content` 또는 `attributes` JSON 어디에 있든 다음 잘 알려진 키 이름의
값을 자동으로 마스킹합니다(대소문자 구분 없음).

`client_secret`, `access_token`, `refresh_token`, `id_token`, `api_key`,
`password`

또한 **`temp:`** 또는 **`secret:`** 접두사가 붙은 상태 키는 기록되는
`state_delta`에서 자동으로 `[REDACTED]`로 대체됩니다. 즉 credential service가
캐시한 OAuth 토큰처럼 `secret:` scope에 저장된 ADK 세션 상태는 BigQuery에
영구 저장되지 않습니다.

!!! info "구성 불필요"

    내장 마스킹은 구조화된 attributes와 state 로깅에 항상 활성화되어 있으며,
    중첩 dictionary와 attribute 값 안의 JSON 인코딩 문자열에도 재귀적으로
    적용됩니다. 커스텀 `content_formatter`는 원시 content에 **먼저** 실행되므로,
    자유 형식 페이로드에 나타날 수 있는 비밀 값을 추가로 마스킹할 때 사용하세요.

### `content_formatter`로 추가 비밀 값 마스킹

`BigQueryLoggerConfig`에 커스텀 `content_formatter` 함수를 제공해 기록 전에 민감한
필드를 제거하거나 마스킹할 수 있습니다.

```python
import json
import re
from typing import Any

SENSITIVE_KEYS = {"client_secret", "access_token", "refresh_token", "api_key", "secret"}

def redact_credentials(event_content: Any, event_type: str) -> str:
    """Redact OAuth secrets and tokens from logged content."""
    if isinstance(event_content, dict):
        text = json.dumps(event_content)
    else:
        text = str(event_content)

    for key in SENSITIVE_KEYS:
        # Redact values in JSON-like strings: "client_secret": "GOCSPX-xxx"
        text = re.sub(
            rf'("{key}"\s*:\s*)"[^"]*"',
            rf'\1"[REDACTED]"',
            text,
            flags=re.IGNORECASE,
        )
    return text

config = BigQueryLoggerConfig(
    content_formatter=redact_credentials,
    # ... other options
)
```

### `event_denylist`로 자격 증명 이벤트 제외

인증 관련 이벤트를 기록할 필요가 없다면 완전히 제외합니다.

```python
config = BigQueryLoggerConfig(
    event_denylist=[
        "HITL_CREDENTIAL_REQUEST",
        "HITL_CREDENTIAL_REQUEST_COMPLETED",
    ],
    # ... other options
)
```

### 일반적인 모범 사례

- 에이전트 소스 코드에 비밀 값을 하드코딩하지 마세요. OAuth 클라이언트 보안 비밀과
  API 키에는 환경 변수 또는 Google Cloud Secret Manager 같은 secret manager를
  사용하세요.
- IAM을 사용해 BigQuery 테이블 접근을 제한하고 기록된 이벤트 데이터를 읽을 수 있는
  사람을 제한하세요.
- 예기치 않은 민감 데이터가 캡처되지 않았는지 로그를 주기적으로 감사하세요.

## 운영

### 추적 및 관측 가능성

플러그인은 분산 추적을 위해 **OpenTelemetry**를 지원합니다. OpenTelemetry는 ADK의
core dependency에 포함되어 있으며 항상 사용할 수 있습니다.

- **자동 Span 관리:** 플러그인은 에이전트 실행, LLM 호출, 도구 실행에 대해 span을
  자동 생성합니다.
- **OpenTelemetry 통합:** 위 예시처럼 `TracerProvider`가 구성된 경우 플러그인은
  유효한 OTel span을 사용하여 `trace_id`, `span_id`, `parent_span_id`를 표준 OTel
  식별자로 채웁니다. 이를 통해 에이전트 로그를 분산 시스템의 다른 서비스와
  상호 연관시킬 수 있습니다.
- **Fallback 메커니즘:** `TracerProvider`가 구성되지 않은 경우(즉, 기본 no-op
  provider만 활성 상태인 경우) 플러그인은 span에 내부 UUID를 자동 생성하고
  `invocation_id`를 trace ID로 사용합니다. 따라서 구성된 `TracerProvider`가 없어도
  부모-자식 계층(Agent -> Span -> Tool/LLM)이 BigQuery 로그에 *항상* 보존됩니다.

### 공개 메서드

플러그인은 수명 주기 관리를 위해 여러 public 메서드를 제공합니다.

- **`await plugin.flush()`**: 보류 중인 모든 이벤트를 BigQuery로 flush합니다. 데이터
  손실을 피하려면 종료 전에 호출하세요.
- **`await plugin.shutdown(timeout=None)`**: 플러그인을 정상 종료하고 보류 중인
  이벤트를 flush하며 리소스를 해제합니다. 선택적 `timeout` 파라미터는 config의
  `shutdown_timeout`을 재정의합니다.
- **`await plugin.create_analytics_views()`**: 이벤트 유형별 analytics view를 모두
  수동으로 다시 생성합니다. 스키마 업그레이드 후 또는 뷰를 새로 고쳐야 할 때
  유용합니다.
- **비동기 context manager:** 플러그인은 자동 시작 및 종료를 위해 `async with`를
  지원합니다.

    ```python
    async with BigQueryAgentAnalyticsPlugin(
        project_id=PROJECT_ID, dataset_id=DATASET_ID
    ) as plugin:
        # plugin is initialized and ready to use
        ...
    # plugin.shutdown() is called automatically on exit
    ```

### Multiprocessing 및 fork 안전성

플러그인은 fork-aware입니다. gRPC C-core 라이브러리를 로드하기 전에
`GRPC_ENABLE_FORK_SUPPORT=1`을 설정하고, 자식 프로세스에서 상속된 런타임 상태
(gRPC channel, write stream, event loop)를 재설정하는 `os.register_at_fork`
handler를 등록합니다. 따라서 플러그인은 `os.fork()` 이후에도 파일 descriptor를
누수하거나 부모 연결로 데이터를 보내지 않고 동작할 수 있습니다.

하지만 프로덕션 배포에는 **`spawn` multiprocessing 시작 방식**을 권장합니다.
`fork`는 진행 중인 gRPC 상태를 포함해 부모 주소 공간을 복사하고, fork 후 재설정은
각 자식의 첫 write에 지연 시간을 추가합니다. `spawn`을 사용하면 각 worker가
플러그인을 깨끗하게 초기화합니다.

Gunicorn 배포에서는 특히 다음을 권장합니다.

- lazy plugin initialization과 함께 `--preload`를 사용합니다(플러그인은 첫 이벤트가
  기록될 때까지 설정을 지연합니다).
- 또는 `post_fork` hook 안에서 플러그인을 초기화하여 각 worker가 자체 client를
  갖게 합니다.

!!! note

    fork-safety 메커니즘은 런타임 상태만 재설정합니다. fork 시점에 부모 프로세스에서
    queue에 있었지만 아직 flush되지 않은 이벤트를 replay하지는 않습니다. 전달 보장이
    필요하다면 fork 전에 `await plugin.flush()`를 호출하세요.

## 기록된 데이터를 활용하는 추가 방법

### BigQuery Agent Analytics SDK

[BigQuery Agent Analytics
SDK](https://github.com/GoogleCloudPlatform/BigQuery-Agent-Analytics-SDK/tree/main)는
플러그인이 기록한 데이터를 프로그래밍 방식으로 소비하고 분석할 수 있게 합니다.
SDK는 다음에 사용할 수 있습니다.

- **에이전트 평가:** 에이전트 실행을 기대 결과와 비교합니다.
- **Golden trajectory matching:** 에이전트 실행 경로가 승인된 시퀀스와 일치하는지
  검증합니다.
- **Trace 시각화:** 기록된 span에서 에이전트 실행 흐름을 재구성하고 시각화합니다.

### 대시보드 빌드

BigQuery Agent Analytics SDK에는 에이전트 성능 데이터를 쿼리하고 시각화하는 방법을
보여주는 [예시 Jupyter
notebook](https://github.com/GoogleCloudPlatform/BigQuery-Agent-Analytics-SDK/blob/main/examples/dashboard_v2.ipynb)이
포함되어 있습니다. 이를 시작점으로 사용해 BigQuery Agent Analytics 데이터 세트에
맞는 맞춤 대시보드를 만들 수 있습니다. 또한 [Colab Data
Apps](https://docs.cloud.google.com/bigquery/docs/colab-data-apps)를 사용해
notebook을 interactive dashboard로 게시할 수도 있습니다.

## 피드백

BigQuery Agent Analytics에 대한 피드백을 환영합니다. 질문, 제안 또는 문제가 있으면
[bqaa-feedback@google.com](mailto:bqaa-feedback@google.com)으로 연락해 주세요.

## 추가 리소스

- [BigQuery Storage Write API](https://cloud.google.com/bigquery/docs/write-api)
- [Introduction to Object Tables](https://docs.cloud.google.com/bigquery/docs/object-table-introduction)
- [Interactive Demo Notebook](https://github.com/haiyuan-eng-google/demo_BQ_agent_analytics_plugin_notebook)
