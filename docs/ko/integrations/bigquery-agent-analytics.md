---
catalog_title: BigQuery Agent Analytics Plugin
catalog_description: 에이전트 동작 분석과 로깅을 위한 심층 분석 기능을 제공합니다
catalog_icon: /integrations/assets/bigquery.png
catalog_tags: ["observability", "google"]
---

# ADK용 BigQuery Agent Analytics 플러그인

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.21.0</span><span class="lst-preview">미리보기</span>
</div>

!!! important "버전 요구사항"

    auto-schema-upgrade, tool provenance 추적, HITL 이벤트 추적을 포함해 이 문서의 기능을 온전히 활용하려면 ADK Python 버전 1.26.0 이상을 사용하세요.

BigQuery Agent Analytics 플러그인은 심층적인 에이전트 동작 분석을 위한 견고한 솔루션을 제공하여 Agent Development Kit(ADK)를 크게 확장합니다. ADK 플러그인 아키텍처와 **BigQuery Storage Write API**를 사용해 중요한 운영 이벤트를 Google BigQuery 테이블에 직접 캡처하고 기록하므로, 디버깅, 실시간 모니터링, 포괄적인 오프라인 성능 평가를 위한 고급 기능을 활용할 수 있습니다.

버전 1.26.0에서는 **Auto Schema Upgrade**(기존 테이블에 새 컬럼을 안전하게 추가), **Tool Provenance** 추적(`LOCAL`, `MCP`, `SUB_AGENT`, `A2A`, `TRANSFER_AGENT`), 그리고 사람-개입형 상호작용을 위한 **HITL Event Tracing**이 추가되었습니다. 버전 1.27.0에서는 **Automatic View Creation**(평탄화된 쿼리 친화적 이벤트 뷰 생성)이 추가되었습니다.

!!! example "미리보기 릴리스"

    BigQuery Agent Analytics 플러그인은 미리보기 릴리스 상태입니다. 자세한 내용은 [출시 단계 설명](https://cloud.google.com/products#product-launch-stages)을 참고하세요.

!!! warning "BigQuery Storage Write API"

    이 기능은 유료 서비스인 **BigQuery Storage Write API**를 사용합니다. 비용 정보는 [BigQuery 문서](https://cloud.google.com/bigquery/pricing?e=48754805&hl=en#data-ingestion-pricing)를 참고하세요.

## 사용 사례

-   **에이전트 워크플로 디버깅 및 분석:** 다양한 *플러그인 수명 주기 이벤트*(LLM 호출, 도구 사용)와 *에이전트가 생성한 이벤트*(사용자 입력, 모델 응답)를 잘 정의된 스키마에 캡처합니다.
-   **대량 분석 및 디버깅:** 로깅 작업은 Storage Write API를 사용해 비동기적으로 수행되므로, 높은 처리량과 낮은 지연 시간을 동시에 달성할 수 있습니다.
-   **멀티모달 분석:** 텍스트, 이미지, 기타 modality를 기록하고 분석할 수 있습니다. 대용량 파일은 GCS로 오프로딩되어 Object Table을 통해 BigQuery ML에서 활용할 수 있습니다.
-   **분산 추적:** `trace_id`, `span_id` 기반의 OpenTelemetry 스타일 추적을 기본 지원하여 에이전트 실행 흐름을 시각화할 수 있습니다.
-   **Tool Provenance:** 각 도구 호출이 어디서 왔는지(로컬 함수, MCP 서버, 하위 에이전트, A2A 원격 에이전트, transfer agent)를 추적합니다.
-   **Human-in-the-Loop(HITL) 추적:** 자격 증명 요청, 확인 프롬프트, 사용자 입력 요청을 위한 전용 이벤트 유형을 제공합니다.
-   **쿼리 가능한 이벤트 뷰(Queryable Event Views):** 이벤트 유형별 평탄화 BigQuery 뷰(예: `v_llm_request`, `v_tool_completed`)를 자동 생성하여 JSON 페이로드를 펼친 다운스트림 분석을 단순화합니다.

기록되는 에이전트 이벤트 데이터는 ADK 이벤트 유형에 따라 달라집니다. 자세한 내용은 [이벤트 유형 및 페이로드](#event-types)를 참고하세요.

## 전제 조건

-   **BigQuery API**가 활성화된 **Google Cloud 프로젝트**
-   **BigQuery 데이터 세트:** 플러그인을 사용하기 전에 로깅 테이블을 저장할 데이터 세트를 생성합니다. 테이블이 없으면 플러그인이 해당 데이터 세트 안에 필요한 이벤트 테이블을 자동으로 생성합니다.
-   **Google Cloud Storage 버킷(선택 사항):** 멀티모달 콘텐츠(이미지, 오디오 등)를 기록하려면 대용량 파일 오프로딩을 위해 GCS 버킷을 만들어 두는 것이 좋습니다.
-   **인증**
    -   **로컬:** `gcloud auth application-default login` 실행
    -   **클라우드:** 서비스 계정에 필요한 권한이 있는지 확인

??? note "Gemini 모델 선택자 `gemini-flash-latest`"

    ADK 문서의 대부분 코드 예제는 `gemini-flash-latest`를 사용해
    [최신 사용 가능](https://ai.google.dev/gemini-api/docs/models#latest)
    Gemini Flash 버전을 선택합니다. 다만 `us-central1` 같은 지역 엔드포인트에서 Gemini를
    사용하는 경우 이 선택 문자열이 동작하지 않을 수 있습니다.
    그런 경우 [Gemini models](https://ai.google.dev/gemini-api/docs/models) 페이지나
    Google Cloud [Gemini models](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models) 목록에서
    구체적인 모델 버전 문자열을 사용하세요.

### IAM 권한

에이전트가 정상적으로 동작하려면, 에이전트가 실행되는 주체(예: 서비스 계정, 사용자 계정)에 다음 Google Cloud 역할이 필요합니다.

* `roles/bigquery.jobUser`: 프로젝트 수준에서 BigQuery 쿼리를 실행하기 위한 권한
* `roles/bigquery.dataEditor`: 테이블 수준에서 로그/이벤트 데이터를 쓰기 위한 권한
* **GCS 오프로딩 사용 시:** 대상 버킷에 대한 `roles/storage.objectCreator` 및 `roles/storage.objectViewer`

## 에이전트와 함께 사용

BigQuery Agent Analytics 플러그인은 ADK 에이전트의 `App` 객체에 구성하고 등록하여 사용합니다. 다음 예시는 GCS 오프로딩을 포함하여 이 플러그인을 사용하는 에이전트 구현 예입니다.

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
# GOOGLE_CLOUD_LOCATION은 유효한 Vertex AI 리전(예: "us-central1")이어야 합니다.
# BQ_LOCATION은 BigQuery 데이터세트 위치로, "US" 또는 "EU" 같은 멀티 리전이거나
# "us-central1" 같은 단일 리전일 수 있습니다.
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

### 에이전트 실행 및 테스트

채팅 인터페이스를 통해 에이전트를 실행하고 `"tell me what you can do"` 또는 `"List datasets in my cloud project <your-gcp-project-id> "` 같은 요청을 몇 번 보내 플러그인을 테스트해 보세요. 이러한 동작은 Google Cloud 프로젝트의 BigQuery 인스턴스에 이벤트를 생성합니다. 이벤트가 처리된 뒤에는 [BigQuery Console](https://console.cloud.google.com/bigquery)에서 다음 쿼리를 사용해 데이터를 확인할 수 있습니다.

```sql
SELECT timestamp, event_type, content
FROM `your-gcp-project-id.your-big-query-dataset-id.agent_events`
ORDER BY timestamp DESC
LIMIT 20;
```

## 플러그인과 함께 Agent Engine에 배포 {#deploy-agent-engine}

이 플러그인이 포함된 에이전트를
[Vertex AI Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)에 배포할 수 있습니다.
이 섹션에서는 ADK CLI를 사용한 배포 절차와, 대안으로 Vertex AI SDK를 사용한 방법을 설명합니다.

!!! important "버전 요구사항"

    이 플러그인을 Agent Engine에 배포하려면 ADK Python 버전 **1.24.0 이상**을 사용하세요.
    이전 버전에서는 플러그인의 비동기 로그 writer가 서버리스 런타임에 의해 종료되기 전에
    보류 중인 이벤트를 flush하지 못하는 문제가 있었습니다. 1.24.0부터는 각 invocation 종료 시
    동기식 flush를 수행해 모든 이벤트가 기록되도록 합니다.

### 사전 준비 사항

배포하기 전에 일반 [Agent Engine 설정](/ko/deploy/agent-engine/deploy/#setup-cloud-project)을 완료해야 합니다.
다음 항목을 포함합니다.

1.  **Vertex AI API**와 **Cloud Resource Manager API**가 활성화된 Google Cloud 프로젝트
2.  대상 프로젝트의 **BigQuery 데이터세트**(또는 올바른 권한이 있는 교차 프로젝트 데이터세트)
3.  배포 아티팩트를 위한 **Cloud Storage 스테이징 버킷**
4.  배포용 서비스 계정에 [IAM 권한](#iam-권한)에서 나열한 역할이 부여되어 있어야 함
5.  코딩 환경이
    [인증됨](/ko/deploy/agent-engine/deploy/#prerequisites-coding-env)
    상태여야 하며 `gcloud auth login`과 `gcloud auth application-default login`을 실행해야 함

### 1단계: 에이전트와 플러그인 정의

플러그인을 포함하는 `App` 객체가 있는 에이전트 프로젝트 폴더를 만듭니다.
`App` 객체는 플러그인을 사용하는 Agent Engine 배포에 필요합니다.

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
# BQ_LOCATION은 BigQuery 데이터세트 위치입니다. "US"/"EU" 같은 멀티 리전이거나
# "us-central1" 같은 단일 리전일 수 있습니다. 이는 GOOGLE_CLOUD_LOCATION으로
# 지정하는 Vertex AI 리전과는 별개입니다.
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

# --- App (required for Agent Engine with plugins) ---
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

`adk deploy agent_engine` 명령으로 에이전트를 배포합니다. `--adk_app`
플래그는 CLI가 사용할 `App` 객체를 지정합니다.

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

    `--adk_app` 플래그는 `App` 객체의 모듈 경로와 변수 이름을 지정합니다.
    이 예제에서 `agent.app`은 `agent.py` 안의 `app` 변수를 가리킵니다.
    이를 통해 배포가 플러그인 구성을 올바르게 인식합니다.

배포가 성공하면 다음과 비슷한 출력이 표시됩니다.

```shell
AgentEngine created. Resource name: projects/123456789/locations/us-central1/reasoningEngines/751619551677906944
```

다음 단계에서 사용할 **Resource name**을 기록해 두세요.

### 3단계: 배포된 에이전트 테스트

배포 후에는 Vertex AI SDK로 에이전트를 조회할 수 있습니다.

```python title="test_deployed_agent.py"
import uuid
import vertexai

PROJECT_ID = "your-gcp-project-id"
LOCATION = "us-central1"
AGENT_ID = "751619551677906944"  # deployment output에서 확인

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

배포된 에이전트에 몇 번 쿼리를 보낸 뒤, BigQuery 테이블을 조회해 이벤트가 기록되는지 확인합니다.

```sql
SELECT timestamp, event_type, agent, content
FROM `your-gcp-project-id.agent_analytics.agent_events`
ORDER BY timestamp DESC
LIMIT 20;
```

`INVOCATION_STARTING`, `LLM_REQUEST`, `LLM_RESPONSE`, `TOOL_STARTING`,
`TOOL_COMPLETED`, `INVOCATION_COMPLETED` 같은 이벤트가 보여야 합니다.

### 대안: Vertex AI SDK로 배포

Vertex AI SDK를 직접 사용해 프로그램 방식으로 배포할 수도 있습니다. CI/CD 파이프라인이나
맞춤형 배포 워크플로에 유용합니다.

```python title="deploy.py"
import vertexai
from vertexai import agent_engines
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

배포 후 BigQuery 테이블에 이벤트가 나타나지 않으면 다음을 확인하세요.

1.  **ADK 버전 확인**: `google-adk>=1.24.0`이 요구사항에 포함되어 있는지 확인합니다.
    이전 버전은 서버리스 런타임이 프로세스를 일시 중단하기 전에 보류된 이벤트를 flush하지 못합니다.

2.  **디버그 로깅 활성화**: `agent.py` 상단에 다음을 추가해 조용히 발생하는 오류를 표면화합니다.

    ```python
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("google_adk").setLevel(logging.DEBUG)
    ```

3.  **IAM 권한 확인**: Agent Engine 서비스 계정에는 대상 테이블에 대한 `roles/bigquery.dataEditor`와
    프로젝트에 대한 `roles/bigquery.jobUser`가 필요합니다. **교차 프로젝트** 로깅의 경우,
    소스 프로젝트에서 BigQuery API가 활성화되어 있고 대상 테이블에 대해 서비스 계정에
    `bigquery.tables.updateData` 권한이 있는지도 확인하세요.

4.  **플러그인 초기화 확인**: Cloud Logging에서 `resource.type="reasoning_engine"`으로 필터링하고
    플러그인 시작 메시지 또는 오류 로그를 확인합니다.

5.  **디버깅용 즉시 flush 사용**: 버퍼링 문제를 배제하려면 `BigQueryLoggerConfig`에서
    `batch_size=1`과 `batch_flush_interval=0.1`을 설정하세요.

## 추적 및 관측 가능성

이 플러그인은 분산 추적을 위한 **OpenTelemetry**를 지원합니다. OpenTelemetry는 ADK의 핵심 의존성에 포함되어 있으므로 항상 사용할 수 있습니다.

- **자동 Span 관리:** 플러그인이 에이전트 실행, LLM 호출, 도구 실행에 대한 span을 자동으로 생성합니다.
- **OpenTelemetry 통합:** 예시처럼 `TracerProvider`가 구성되어 있으면, 플러그인은 유효한 OTel span을 사용하여 `trace_id`, `span_id`, `parent_span_id`를 표준 OTel 식별자로 채웁니다. 이를 통해 분산 시스템의 다른 서비스와 에이전트 로그를 상관 분석할 수 있습니다.
- **Fallback 메커니즘:** `TracerProvider`가 구성되지 않은 경우(즉, 기본 no-op provider만 활성화된 경우), 플러그인은 내부 UUID 기반 span 생성으로 자동 폴백하고 `invocation_id`를 trace ID로 사용합니다. 따라서 OTel `TracerProvider`를 구성하지 않아도 BigQuery 로그에서 부모-자식 계층(Agent -> Span -> Tool/LLM)은 항상 유지됩니다.

## 구성 옵션

`BigQueryLoggerConfig`를 사용해 플러그인을 사용자 지정할 수 있습니다.

-   **`enabled`** (`bool`, 기본값: `True`): 플러그인의 BigQuery 테이블 로깅을 비활성화하려면 `False`로 설정합니다.
-   **`table_id`** (`str`, 기본값: `"agent_events"`): 데이터 세트 내의 BigQuery 테이블 ID입니다. `BigQueryAgentAnalyticsPlugin` 생성자의 `table_id` 인수로도 덮어쓸 수 있으며, 이 값이 우선합니다.
-   **`clustering_fields`** (`List[str]`, 기본값: `["event_type", "agent", "user_id"]`): 테이블을 자동 생성할 때 클러스터링에 사용하는 필드입니다.
-   **`gcs_bucket_name`** (`Optional[str]`, 기본값: `None`): 대용량 콘텐츠(이미지, blob, 긴 텍스트)를 오프로딩할 GCS 버킷 이름입니다. 지정하지 않으면 큰 콘텐츠는 잘리거나 placeholder로 대체될 수 있습니다.
-   **`connection_id`** (`Optional[str]`, 기본값: `None`): `ObjectRef` 컬럼의 authorizer로 사용할 BigQuery connection ID(예: `us.my-connection`)입니다. BigQuery ML에서 `ObjectRef`를 사용하려면 필요합니다.
-   **`max_content_length`** (`int`, 기본값: `500 * 1024`): BigQuery에 **inline**으로 저장할 텍스트 콘텐츠의 최대 길이(문자 수)입니다. 이를 넘기면(GCS가 구성된 경우) GCS로 오프로딩되거나, 그렇지 않으면 잘립니다. 기본값은 500KB입니다.
-   **`batch_size`** (`int`, 기본값: `1`): BigQuery에 쓰기 전에 묶는 이벤트 수입니다.
-   **`batch_flush_interval`** (`float`, 기본값: `1.0`): 부분 배치를 flush하기 전까지 기다리는 최대 시간(초)입니다.
-   **`shutdown_timeout`** (`float`, 기본값: `10.0`): 종료 시 로그가 flush될 때까지 기다리는 시간(초)입니다.
-   **`event_allowlist`** (`Optional[List[str]]`, 기본값: `None`): 기록할 이벤트 유형 목록입니다. `None`이면 `event_denylist`에 포함된 이벤트를 제외한 모든 이벤트를 기록합니다. 지원되는 이벤트 유형 전체 목록은 [이벤트 유형 및 페이로드](#event-types) 섹션을 참고하세요.
-   **`event_denylist`** (`Optional[List[str]]`, 기본값: `None`): 기록에서 제외할 이벤트 유형 목록입니다. 지원되는 이벤트 유형 전체 목록은 [이벤트 유형 및 페이로드](#event-types) 섹션을 참고하세요.
-   **`content_formatter`** (`Optional[Callable[[Any, str], Any]]`, 기본값: `None`): 로깅 전에 이벤트 콘텐츠를 포맷하는 선택적 함수입니다. 이 함수는 원시 콘텐츠와 이벤트 유형 문자열(예: `"LLM_REQUEST"`) 두 인수를 받습니다.
-   **`log_multi_modal_content`** (`bool`, 기본값: `True`): 상세 콘텐츠 파트(`GCS_REFERENCE` 포함)를 기록할지 여부입니다.
-   **`queue_max_size`** (`int`, 기본값: `10000`): 메모리 내 큐에 보관할 수 있는 최대 이벤트 수입니다. 이를 초과하면 새 이벤트가 삭제됩니다.
-   **`retry_config`** (`RetryConfig`, 기본값: `RetryConfig()`): 실패한 BigQuery 쓰기를 재시도하기 위한 설정입니다(`max_retries`, `initial_delay`, `multiplier`, `max_delay` 포함).
-   **`log_session_metadata`** (`bool`, 기본값: `True`): `True`이면 `session_id`, `app_name`, `user_id`, 그리고 세션 `state` 딕셔너리(예: gchat thread-id, customer_id 같은 커스텀 상태)를 포함한 세션 정보를 `attributes` 컬럼에 기록합니다.
-   **`custom_tags`** (`Dict[str, Any]`, 기본값: `{}`): 모든 이벤트의 `attributes` 컬럼에 포함할 정적 태그 딕셔너리입니다(예: `{"env": "prod", "version": "1.0"}`).
-   **`auto_schema_upgrade`** (`bool`, 기본값: `True`): 활성화하면 플러그인 스키마가 진화할 때 기존 테이블에 새 컬럼을 자동으로 추가합니다. 컬럼 삭제나 변경 없이 additive change만 수행합니다. 테이블의 버전 레이블(`adk_schema_version`) 덕분에 스키마 버전당 한 번만 diff가 수행됩니다. 기본적으로 켜 둬도 안전합니다.
-   **`create_views`** (`bool`, 기본값: `True`): 1.27.0에서 추가되었습니다. 활성화하면 `content`나 `attributes` 같은 구조화된 JSON 데이터를 평탄한 타입 컬럼으로 펼치는 이벤트 유형별 BigQuery 뷰를 자동 생성하여 SQL 쿼리를 크게 단순화합니다.

다음 코드는 BigQuery Agent Analytics 플러그인용 구성을 정의하는 예시입니다.

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

plugin = BigQueryAgentAnalyticsPlugin(..., config=config)
```


## 스키마 및 프로덕션 설정

### 스키마 참조

이벤트 테이블(`agent_events`)은 유연한 스키마를 사용합니다. 아래 표는 예시 값을 포함한 포괄적인 참조입니다.

| 필드명 | 유형 | 모드 | 설명 | 예시 값 |
|:---|:---|:---|:---|:---|
| **timestamp** | `TIMESTAMP` | `REQUIRED` | 이벤트 생성 시점의 UTC 타임스탬프입니다. 기본 정렬 키이자 일별 파티셔닝 키 역할을 합니다. 마이크로초 정밀도를 가집니다. | `2026-02-03 20:52:17 UTC` |
| **event_type** | `STRING` | `NULLABLE` | 정규화된 이벤트 범주입니다. 표준 값에는 `LLM_REQUEST`, `LLM_RESPONSE`, `LLM_ERROR`, `TOOL_STARTING`, `TOOL_COMPLETED`, `TOOL_ERROR`, `AGENT_STARTING`, `AGENT_COMPLETED`, `STATE_DELTA`, `INVOCATION_STARTING`, `INVOCATION_COMPLETED`, `USER_MESSAGE_RECEIVED`, 그리고 HITL 이벤트([HITL events](#hitl-events) 참조)가 포함됩니다. 상위 수준 필터링에 사용됩니다. | `LLM_REQUEST` |
| **agent** | `STRING` | `NULLABLE` | 이 이벤트를 발생시킨 에이전트 이름입니다. 에이전트 초기화 시 또는 `root_agent_name` 컨텍스트를 통해 정의됩니다. | `my_bq_agent` |
| **session_id** | `STRING` | `NULLABLE` | 전체 대화 스레드를 식별하는 영속적인 식별자입니다. 여러 turn과 하위 에이전트 호출을 거쳐도 동일하게 유지됩니다. | `04275a01-1649-4a30-b6a7-5b443c69a7bc` |
| **invocation_id** | `STRING` | `NULLABLE` | 단일 실행 turn 또는 요청 사이클의 고유 식별자입니다. 많은 맥락에서 `trace_id`와 대응됩니다. | `e-b55b2000-68c6-4e8b-b3b3-ffb454a92e40` |
| **user_id** | `STRING` | `NULLABLE` | 세션을 시작한 사용자(사람 또는 시스템)의 식별자입니다. `User` 객체나 메타데이터에서 추출됩니다. | `test_user` |
| **trace_id** | `STRING` | `NULLABLE` | **OpenTelemetry** Trace ID(32자 16진수)입니다. 하나의 분산 요청 수명 주기 내 모든 작업을 연결합니다. | `e-b55b2000-68c6-4e8b-b3b3-ffb454a92e40` |
| **span_id** | `STRING` | `NULLABLE` | **OpenTelemetry** Span ID(16자 16진수)입니다. 이 특정 원자적 작업을 고유하게 식별합니다. | `69867a836cd94798be2759d8e0d70215` |
| **parent_span_id** | `STRING` | `NULLABLE` | 직전 호출자의 Span ID입니다. 부모-자식 실행 트리(DAG)를 재구성하는 데 사용됩니다. | `ef5843fe40764b4b8afec44e78044205` |
| **content** | `JSON` | `NULLABLE` | 기본 이벤트 페이로드입니다. 구조는 `event_type`에 따라 달라집니다. | `{"system_prompt": "You are...", "prompt": [{"role": "user", "content": "hello"}], "response": "Hi", "usage": {"total": 15}}` |
| **attributes** | `JSON` | `NULLABLE` | 메타데이터/보강 정보(사용량 통계, 모델 정보, tool provenance, custom tags)입니다. | `{"model": "gemini-flash-latest", "usage_metadata": {"total_token_count": 15}, "session_metadata": {"session_id": "...", "app_name": "...", "user_id": "...", "state": {}}, "custom_tags": {"env": "prod"}}` |
| **latency_ms** | `JSON` | `NULLABLE` | 성능 메트릭입니다. 표준 키는 `total_ms`(총 경과 시간)와 `time_to_first_token_ms`(스트리밍 지연 시간)입니다. | `{"total_ms": 1250, "time_to_first_token_ms": 450}` |
| **status** | `STRING` | `NULLABLE` | 상위 수준 결과입니다. 값은 `OK`(성공) 또는 `ERROR`(실패)입니다. | `OK` |
| **error_message** | `STRING` | `NULLABLE` | 사람이 읽을 수 있는 예외 메시지 또는 스택 트레이스 일부입니다. `status`가 `ERROR`일 때만 채워집니다. | `Error 404: Dataset not found` |
| **is_truncated** | `BOOLEAN` | `NULLABLE` | `content`나 `attributes`가 BigQuery 셀 크기 제한(기본 10MB)을 초과해 일부 드롭되었으면 `true`입니다. | `false` |
| **content_parts** | `RECORD` | `REPEATED` | 멀티모달 세그먼트(Text, Image, Blob) 배열입니다. 콘텐츠를 단순 JSON으로 직렬화할 수 없을 때(예: 큰 바이너리나 GCS 참조) 사용됩니다. | `[{"mime_type": "text/plain", "text": "hello"}]` |

플러그인은 테이블이 없으면 자동으로 생성합니다. 하지만 프로덕션에서는 유연성을 위한 **JSON** 타입과 멀티모달 콘텐츠를 위한 **REPEATED RECORD**를 활용하는 다음 DDL로 테이블을 수동 생성하는 것을 권장합니다.

**권장 DDL:**

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

### 자동 생성 뷰 (1.27.0+)

`create_views=True`(1.27.0 이상에서 기본값)이면 플러그인이 각 이벤트 유형에 대해,
공통 JSON 구조를 평탄한 타입 컬럼으로 펼친 뷰를 자동 생성합니다. 따라서 복잡한
`JSON_VALUE` 또는 `JSON_QUERY` 함수를 직접 작성하지 않고도 SQL을 훨씬 단순하게
작성할 수 있습니다.

예를 들어 `v_llm_request` 뷰는 다음 스키마를 포함합니다.

| 필드명 | 유형 | 설명 |
|:---|:---|:---|
| **(공통 컬럼)** | `VARIES` | `timestamp`, `event_type`, `agent`, `session_id`, `invocation_id`, `user_id`, `trace_id`, `span_id`, `parent_span_id`, `status`, `error_message`, `is_truncated` 같은 표준 메타데이터를 포함합니다. |
| **model** | `STRING` | 요청에 사용된 LLM 모델 이름입니다. |
| **request_content** | `JSON` | 원시 LLM 요청 페이로드입니다. |
| **llm_config** | `JSON` | LLM에 전달된 구성 매개변수(temperature, top_p 등)입니다. |
| **tools** | `JSON` | 요청 시 사용 가능했던 도구 배열입니다. |

### 이벤트 유형 및 페이로드 {#event-types}

이제 `content` 컬럼은 `event_type`별 **JSON** 객체를 담습니다. `content_parts` 컬럼은 콘텐츠를 구조화해 보여주며, 특히 이미지나 오프로딩된 데이터에 유용합니다.

!!! note "콘텐츠 잘림"

    - 가변 콘텐츠 필드는 `max_content_length`까지 잘립니다(`BigQueryLoggerConfig`에서 구성, 기본 500KB).
    - `gcs_bucket_name`이 구성되어 있으면, 큰 콘텐츠는 잘리는 대신 GCS로 오프로딩되고 참조가 `content_parts.object_ref`에 저장됩니다.

#### LLM 상호작용(플러그인 수명 주기)

이 이벤트들은 LLM에 전송된 원시 요청과 LLM으로부터 받은 응답을 추적합니다.

**1. LLM_REQUEST**

대화 이력과 시스템 지침을 포함하여 모델에 전송된 프롬프트를 캡처합니다.

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

모델 출력과 토큰 사용 통계를 캡처합니다.

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

LLM 호출이 예외로 실패했을 때 기록됩니다. 오류 메시지가 캡처되고 span이 종료됩니다.

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

#### 도구 사용(플러그인 수명 주기)

이 이벤트들은 에이전트의 도구 실행을 추적합니다. 각 도구 이벤트에는 도구 출처를 분류하는 `tool_origin` 필드가 포함됩니다.

| 도구 출처 | 설명 |
|:---|:---|
| `LOCAL` | `FunctionTool` 인스턴스(로컬 Python 함수) |
| `MCP` | Model Context Protocol 도구(`McpTool` 인스턴스) |
| `SUB_AGENT` | `AgentTool` 인스턴스(하위 에이전트) |
| `A2A` | 원격 Agent-to-Agent 인스턴스(`RemoteA2aAgent`) |
| `TRANSFER_AGENT` | `TransferToAgentTool` 인스턴스 |
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

도구 실행이 끝났을 때 기록됩니다.

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

도구 실행이 예외로 실패했을 때 기록됩니다. 도구 이름, 인수, tool origin, 오류 메시지를 함께 캡처합니다.

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

#### 상태 관리

이 이벤트들은 일반적으로 도구에 의해 발생하는 에이전트 상태 변경을 추적합니다.

**7. STATE_DELTA**

에이전트 내부 상태의 변경(예: 토큰 캐시 업데이트)을 추적합니다.

```json
{
  "event_type": "STATE_DELTA",
  "attributes": {
    "state_delta": {
      "bigquery_token_cache": "{\"token\": \"ya29...\", \"expiry\": \"...\"}"
    }
  }
}
```

#### 에이전트 수명 주기 및 일반 이벤트

<table>
  <thead>
    <tr>
      <th><strong>이벤트 유형</strong></th>
      <th><strong>콘텐츠(JSON) 구조</strong></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><pre>INVOCATION_STARTING</pre></p></td>
      <td><p><pre>{}</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>INVOCATION_COMPLETED</pre></p></td>
      <td><p><pre>{}</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>AGENT_STARTING</pre></p></td>
      <td><p><pre>"You are a helpful agent..."</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>AGENT_COMPLETED</pre></p></td>
      <td><p><pre>{}</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>USER_MESSAGE_RECEIVED</pre></p></td>
      <td><p><pre>{"text_summary": "Help me book a flight."}</pre></p></td>
    </tr>

  </tbody>
</table>

#### Human-in-the-Loop (HITL) 이벤트 {#hitl-events}

이 플러그인은 ADK의 synthetic HITL 도구 호출을 자동 감지하고 전용 이벤트 유형을 발행합니다. 이러한 이벤트는 일반 `TOOL_STARTING` / `TOOL_COMPLETED` 이벤트에 **추가로** 기록됩니다.

다음 HITL 도구 이름이 인식됩니다.

- `adk_request_credential` — 사용자 자격 증명 요청(예: OAuth 토큰)
- `adk_request_confirmation` — 진행 전 사용자 확인 요청
- `adk_request_input` — 자유 형식 사용자 입력 요청

<table>
  <thead>
    <tr>
      <th><strong>이벤트 유형</strong></th>
      <th><strong>트리거</strong></th>
      <th><strong>콘텐츠(JSON) 구조</strong></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><pre>HITL_CREDENTIAL_REQUEST</pre></p></td>
      <td>에이전트가 <code>adk_request_credential</code>를 호출함</td>
      <td><p><pre>{"tool": "adk_request_credential", "args": {...}}</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>HITL_CREDENTIAL_REQUEST_COMPLETED</pre></p></td>
      <td>사용자가 자격 증명 응답을 제공함</td>
      <td><p><pre>{"tool": "adk_request_credential", "result": {...}}</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>HITL_CONFIRMATION_REQUEST</pre></p></td>
      <td>에이전트가 <code>adk_request_confirmation</code>를 호출함</td>
      <td><p><pre>{"tool": "adk_request_confirmation", "args": {...}}</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>HITL_CONFIRMATION_REQUEST_COMPLETED</pre></p></td>
      <td>사용자가 확인 응답을 제공함</td>
      <td><p><pre>{"tool": "adk_request_confirmation", "result": {...}}</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>HITL_INPUT_REQUEST</pre></p></td>
      <td>에이전트가 <code>adk_request_input</code>를 호출함</td>
      <td><p><pre>{"tool": "adk_request_input", "args": {...}}</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>HITL_INPUT_REQUEST_COMPLETED</pre></p></td>
      <td>사용자가 입력 응답을 제공함</td>
      <td><p><pre>{"tool": "adk_request_input", "result": {...}}</pre></p></td>
    </tr>
  </tbody>
</table>

HITL 요청 이벤트는 `on_event_callback`의 `function_call` 파트에서 감지됩니다. HITL 완료 이벤트는 `on_event_callback`과 `on_user_message_callback`의 `function_response` 파트에서 감지됩니다.

#### GCS 오프로딩 예시(멀티모달 및 대용량 텍스트)

`gcs_bucket_name`이 구성되어 있으면, 대용량 텍스트와 멀티모달 콘텐츠(이미지, 오디오 등)는 자동으로 GCS로 오프로딩됩니다. `content` 컬럼에는 요약 또는 placeholder가 저장되고, `content_parts`에는 GCS URI를 가리키는 `object_ref`가 저장됩니다.

**오프로딩된 텍스트 예시**

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
        "uri": "gs://haiyuan-adk-debug-verification-1765319132/2025-12-10/e-f9545d6d/ae5235e6_p1.txt",
        "authorizer": "us.bqml_connection",
        "details": {"gcs_metadata": {"content_type": "text/plain"}}
      }
    }
  ]
}
```

**오프로딩된 이미지 예시**

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
        "uri": "gs://haiyuan-adk-debug-verification-1765319132/2025-12-10/e-f9545d6d/ae5235e6_p2.png",
        "authorizer": "us.bqml_connection",
        "details": {"gcs_metadata": {"content_type": "image/png"}}
      }
    }
  ]
}
```

**오프로딩 콘텐츠 조회(서명 URL 얻기)**

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

## 고급 분석 쿼리

### `trace_id`로 특정 대화 턴 추적

```sql
SELECT timestamp, event_type, agent, JSON_VALUE(content, '$.response') as summary
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE trace_id = 'your-trace-id'
ORDER BY timestamp ASC;
```

### 토큰 사용량 분석(JSON 필드 접근)

```sql
SELECT
  AVG(CAST(JSON_VALUE(content, '$.usage.total') AS INT64)) as avg_tokens
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE event_type = 'LLM_RESPONSE';
```

### 멀티모달 콘텐츠 조회(`content_parts` 및 `ObjectRef` 사용)

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

### BigQuery 원격 모델(Gemini)로 멀티모달 콘텐츠 분석

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

### 지연 시간 분석(LLM 및 도구)

```sql
SELECT
  event_type,
  AVG(CAST(JSON_VALUE(latency_ms, '$.total_ms') AS INT64)) as avg_latency_ms
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE event_type IN ('LLM_RESPONSE', 'TOOL_COMPLETED')
GROUP BY event_type;
```

### Span 계층 및 지속 시간 분석

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

### 오류 분석(LLM 및 도구 오류)

```sql
SELECT
  timestamp,
  event_type,
  agent,
  error_message,
  JSON_VALUE(content, '$.tool') as tool_name,
  CAST(JSON_VALUE(latency_ms, '$.total_ms') AS INT64) as latency_ms
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE event_type IN ('LLM_ERROR', 'TOOL_ERROR')
ORDER BY timestamp DESC
LIMIT 20;
```

### Tool Provenance 분석

```sql
SELECT
  JSON_VALUE(content, '$.tool_origin') as tool_origin,
  JSON_VALUE(content, '$.tool') as tool_name,
  COUNT(*) as call_count,
  AVG(CAST(JSON_VALUE(latency_ms, '$.total_ms') AS INT64)) as avg_latency_ms
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE event_type = 'TOOL_COMPLETED'
GROUP BY tool_origin, tool_name
ORDER BY call_count DESC;
```

### HITL 상호작용 분석

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


### 7. AI 기반 근본 원인 분석 (Agent Ops)

BigQuery ML과 Gemini를 사용해 실패한 세션을 자동 분석하고 오류의 근본 원인을 파악합니다.

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


## BigQuery의 대화형 분석

[BigQuery Conversational Analytics](https://cloud.google.com/bigquery/docs/conversational-analytics)를 사용하면 자연어로 에이전트 로그를 분석할 수 있습니다. 이 도구를 사용해 다음과 같은 질문에 답할 수 있습니다.

*   "Show me the error rate over time"
*   "What are the most common tool calls?"
*   "Identify sessions with high token usage"

## Looker Studio 대시보드

미리 준비된 [Looker Studio Dashboard template](https://lookerstudio.google.com/c/reporting/f1c5b513-3095-44f8-90a2-54953d41b125/page/8YdhF)을 사용해 에이전트 성능을 시각화할 수 있습니다.

이 대시보드를 자신의 BigQuery 테이블에 연결하려면, 아래 링크 형식에서 프로젝트, 데이터 세트, 테이블 ID placeholder를 실제 값으로 바꿔 사용하세요.

```text
https://lookerstudio.google.com/reporting/create?c.reportId=f1c5b513-3095-44f8-90a2-54953d41b125&ds.ds3.connector=bigQuery&ds.ds3.type=TABLE&ds.ds3.projectId=<your-project-id>&ds.ds3.datasetId=<your-dataset-id>&ds.ds3.tableId=<your-table-id>
```

## 민감한 자격 증명 로깅 방지 {#security-credentials}

!!! warning "OAuth 토큰, API 키, 클라이언트 비밀을 로그에 남기지 마세요"

    BigQuery Agent Analytics 플러그인은 도구 인수, LLM 프롬프트, HITL 자격 증명 요청과 같은
    인증 관련 이벤트를 포함해 상세한 이벤트 페이로드를 캡처합니다. 에이전트가
    **인증된 도구**(예: OAuth2를 사용하는 `AuthenticatedFunctionTool`)를 사용하면 플러그인이
    `client_secret`, `access_token`, API 키 같은 민감한 값을 BigQuery 테이블의 `content` 컬럼에
    기록할 수 있습니다.

    이는 알려진 문제입니다
    ([google/adk-python#3845](https://github.com/google/adk-python/issues/3845))
    이며 분석 데이터에서 자격 증명 노출로 이어질 수 있습니다.

BigQuery에 민감한 자격 증명이 저장되지 않도록 하려면 다음 접근법 중 하나 이상을 사용하세요.

### `content_formatter`로 비밀 값 마스킹

`BigQueryLoggerConfig`에 사용자 지정 `content_formatter` 함수를 제공해,
기록되기 전에 민감한 필드를 제거하거나 가립니다.

```python
import json
import re
from typing import Any

SENSITIVE_KEYS = {"client_secret", "access_token", "refresh_token", "api_key", "secret"}

def redact_credentials(event_content: Any, event_type: str) -> str:
    """로그된 콘텐츠에서 OAuth 비밀 값과 토큰을 마스킹합니다."""
    if isinstance(event_content, dict):
        text = json.dumps(event_content)
    else:
        text = str(event_content)

    for key in SENSITIVE_KEYS:
        # JSON 유사 문자열의 값을 마스킹합니다: "client_secret": "GOCSPX-xxx"
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

인증 관련 이벤트를 기록할 필요가 없다면, 해당 이벤트를 완전히 제외할 수 있습니다.

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

-   **비밀 값을 코드에 하드코딩하지 마세요.** OAuth 클라이언트 비밀과 API 키는 환경 변수나
    Google Cloud Secret Manager 같은 비밀 관리자에 저장하세요.
-   **BigQuery 테이블 접근을 제한**해 로그 데이터에 접근할 수 있는 사용자를 최소화하세요.
-   **로그를 주기적으로 감사**해 예상치 못한 민감 정보가 수집되지 않는지 확인하세요.

## 피드백

BigQuery Agent Analytics에 대한 피드백을 환영합니다. 질문, 제안, 또는 문제를 발견했다면 bqaa-feedback@google.com 으로 연락해 주세요.

## 추가 리소스

-   [BigQuery Storage Write API](https://cloud.google.com/bigquery/docs/write-api)
-   [Introduction to Object Tables](https://docs.cloud.google.com/bigquery/docs/object-table-introduction)
-   [Interactive Demo Notebook](https://github.com/haiyuan-eng-google/demo_BQ_agent_analytics_plugin_notebook)
