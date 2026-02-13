---
catalog_title: BigQuery Agent Analytics Plugin
catalog_description: In-depth agent analytics for behavior analysis and logging
catalog_icon: /adk-docs/integrations/assets/bigquery.png
catalog_tags: ["observability", "google"]
---
# BigQuery 에이전트 분석 플러그인

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.18.0</span><span class="lst-preview">미리보기</span>
</div>

!!! note "가용성"

    이 플러그인을 사용하려면 트리 상단에서 ADK를 빌드하거나 버전 1.19의 공식 릴리스를 기다리는 것이 좋습니다. 버전 1.19가 출시되면 이 참고 사항은 제거됩니다.

BigQuery 에이전트 분석 플러그인은 심층적인 에이전트 동작 분석을 위한 강력한 솔루션을 제공하여 에이전트 개발 키트(ADK)를 크게 향상시킵니다. ADK 플러그인 아키텍처와 BigQuery Storage Write API를 사용하여 중요한 운영 이벤트를 Google BigQuery 테이블에 직접 캡처하고 기록하여 디버깅, 실시간 모니터링 및 포괄적인 오프라인 성능 평가를 위한 고급 기능을 제공합니다.

!!! example "미리보기 릴리스"

    BigQuery 에이전트 분석 플러그인은 미리보기 릴리스입니다. 자세한 내용은 [출시 단계 설명](https://cloud.google.com/products#product-launch-stages)을 참조하세요.

!!! warning "BigQuery Storage Write API"

    이 기능은 유료 서비스인 **BigQuery Storage Write API**를 사용합니다. 비용에 대한 정보는 [BigQuery 설명서](https://cloud.google.com/bigquery/pricing?e=48754805&hl=en#data-ingestion-pricing)를 참조하세요.

## 사용 사례

-   **에이전트 워크플로 디버깅 및 분석:** 잘 정의된 스키마에 광범위한 *플러그인 수명 주기 이벤트*(LLM 호출, 도구 사용) 및 *에이전트 생성 이벤트*(사용자 입력, 모델 응답)를 캡처합니다.
-   **대용량 분석 및 디버깅:** 로깅 작업은 기본 에이전트 실행을 차단하지 않도록 별도의 스레드에서 비동기적으로 수행됩니다. 높은 이벤트 볼륨을 처리하도록 설계된 이 플러그인은 타임스탬프를 통해 이벤트 순서를 유지합니다.

기록된 에이전트 이벤트 데이터는 ADK 이벤트 유형에 따라 다릅니다. 자세한 내용은 [이벤트 유형 및 페이로드](#event-types)를 참조하세요.

## 전제 조건

-   **BigQuery API**가 활성화된 **Google Cloud 프로젝트**.
-   **BigQuery 데이터 세트:** 플러그인을 사용하기 전에 로깅 테이블을 저장할 데이터 세트를 만듭니다. 테이블이 없는 경우 플러그인이 데이터 세트 내에 필요한 이벤트 테이블을 자동으로 만듭니다. 기본적으로 이 테이블의 이름은 agent_events이지만 플러그인 구성의 table_id 매개변수를 사용하여 사용자 지정할 수 있습니다.
-   **인증:**
    -   **로컬:** `gcloud auth application-default login`을 실행합니다.
    -   **클라우드:** 서비스 계정에 필요한 권한이 있는지 확인합니다.

### IAM 권한

에이전트가 제대로 작동하려면 에이전트가 실행 중인 보안 주체(예: 서비스 계정, 사용자 계정)에 다음과 같은 Google Cloud 역할이 필요합니다.
*   프로젝트에서 BigQuery 쿼리를 실행하려면 프로젝트 수준에서 `roles/bigquery.jobUser`. 이 역할만으로는 데이터에 대한 액세스 권한을 부여하지 않습니다.
*   선택한 BigQuery 테이블에 로그/이벤트 데이터를 쓰려면 테이블 수준에서 `roles/bigquery.dataEditor`.
에이전트가 이 테이블을 만들어야 하는 경우 테이블을 만들려는 BigQuery 데이터 세트에 `roles/bigquery.dataEditor`를 부여해야 합니다.

## 에이전트와 함께 사용

ADK 에이전트의 App 개체에 BigQuery 분석 플러그인을 구성하고 등록하여 사용합니다. 다음 예는 이 플러그인과 BigQuery 도구가 활성화된 에이전트의 구현을 보여줍니다.

```python title="my_bq_agent/agent.py"
# my_bq_agent/agent.py
import os
import google.auth
from google.adk.apps import App
from google.adk.plugins.bigquery_agent_analytics_plugin import BigQueryAgentAnalyticsPlugin
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools.bigquery import BigQueryToolset, BigQueryCredentialsConfig

# --- 구성 ---
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "your-gcp-project-id")
DATASET_ID = os.environ.get("BIG_QUERY_DATASET_ID", "your-big-query-dataset-id")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "your-gcp-project-location") # Google Cloud 프로젝트의 위치 사용

if PROJECT_ID == "your-gcp-project-id":
    raise ValueError("GOOGLE_CLOUD_PROJECT를 설정하거나 코드를 업데이트하세요.")
if DATASET_ID == "your-big-query-dataset-id":
    raise ValueError("BIG_QUERY_DATASET_ID를 설정하거나 코드를 업데이트하세요.")
if LOCATION == "your-gcp-project-location":
    raise ValueError("GOOGLE_CLOUD_LOCATION을 설정하거나 코드를 업데이트하세요.")

# --- 중요: Gemini 인스턴스화 전에 환경 변수 설정 ---
os.environ['GOOGLE_CLOUD_PROJECT'] = PROJECT_ID
os.environ['GOOGLE_CLOUD_LOCATION'] = LOCATION
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'True' # Vertex AI API가 활성화되어 있는지 확인

# --- 플러그인 초기화 ---
bq_logging_plugin = BigQueryAgentAnalyticsPlugin(
    project_id=PROJECT_ID, # project_id는 사용자로부터 필수 입력
    dataset_id=DATASET_ID, # dataset_id는 사용자로부터 필수 입력
    table_id="agent_events" # 선택 사항: 기본값은 "agent_events". 테이블이 없으면 플러그인이 자동으로 이 테이블을 만듭니다.
)

# --- 도구 및 모델 초기화 ---
credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
bigquery_toolset = BigQueryToolset(
    credentials_config=BigQueryCredentialsConfig(credentials=credentials)
)

llm = Gemini(
    model="gemini-1.5-flash",
)

root_agent = Agent(
    model=llm,
    name='my_bq_agent',
    instruction="당신은 BigQuery 도구에 액세스할 수 있는 유용한 도우미입니다.",
    tools=[bigquery_toolset]
)

# --- 앱 만들기 ---
app = App(
    name="my_bq_agent",
    root_agent=root_agent,
    plugins=[bq_logging_plugin], # 여기에 플러그인 등록
)
```

### 에이전트 실행 및 테스트

"무엇을 할 수 있는지 알려주세요" 또는 "내 클라우드 프로젝트 <your-gcp-project-id>의 데이터 세트 나열"과 같은 채팅 인터페이스를 통해 에이전트를 실행하고 몇 가지 요청을 하여 플러그인을 테스트합니다. 이러한 작업은 Google Cloud 프로젝트 BigQuery 인스턴스에 기록되는 이벤트를 만듭니다. 이러한 이벤트가 처리되면 이 쿼리를 사용하여 [BigQuery 콘솔](https://console.cloud.google.com/bigquery)에서 해당 데이터를 볼 수 있습니다.

```sql
SELECT timestamp, event_type, content
FROM `your-gcp-project-id.your-big-query-dataset-id.agent_events`
ORDER BY timestamp DESC
LIMIT 20;
```

## 구성 옵션

`BigQueryLoggerConfig`를 사용하여 플러그인을 사용자 지정할 수 있습니다.

-   **`enabled`** (`bool`, 기본값: `True`): 플러그인이 에이전트 데이터를 BigQuery 테이블에 로깅하지 못하도록 하려면 이 매개변수를 False로 설정합니다.
-   **`event_allowlist`** (`Optional[List[str]]`, 기본값: `None`): 로깅할 이벤트 유형 목록입니다. `None`이면 `event_denylist`에 있는 이벤트를 제외한 모든 이벤트가 로깅됩니다. 지원되는 이벤트 유형의 전체 목록은 [이벤트 유형 및 페이로드](#event-types) 섹션을 참조하세요.
-   **`event_denylist`** (`Optional[List[str]]`, 기본값: `None`): 로깅을 건너뛸 이벤트 유형 목록입니다. 지원되는 이벤트 유형의 전체 목록은 [이벤트 유형 및 페이로드](#event-types) 섹션을 참조하세요.
-   **`content_formatter`** (`Optional[Callable[[Any], str]]`, 기본값: `None`): 로깅 전에 이벤트 콘텐츠를 형식화하는 선택적 함수입니다. 다음 코드는 콘텐츠 포맷터를 구현하는 방법을 보여줍니다.
-   **`shutdown_timeout`** (`float`, 기본값: `5.0`): 종료 중에 로그가 플러시될 때까지 기다리는 시간(초)입니다.
-   **`client_close_timeout`** (`float`, 기본값: `2.0`): BigQuery 클라이언트가 닫힐 때까지 기다리는 시간(초)입니다.
-   **`max_content_length`** (`int`, 기본값: `500`): 잘라내기 전 콘텐츠 부분의 최대 길이입니다.

다음 코드 샘플은 BigQuery 에이전트 분석 플러그인에 대한 구성을 정의하는 방법을 보여줍니다.

```python
import json
import re

from google.adk.plugins.bigquery_agent_analytics_plugin import BigQueryLoggerConfig

def redact_dollar_amounts(event_content: Any) -> str:
    """
    달러 금액(예: $600, $12.50)을 수정하고
    입력이 dict인 경우 JSON 출력을 보장하는 사용자 지정 포맷터입니다.
    """
    text_content = ""
    if isinstance(event_content, dict):
        text_content = json.dumps(event_content)
    else:
        text_content = str(event_content)

    # 달러 금액을 찾는 정규식: $ 다음에 숫자가 오고 쉼표나 소수점이 선택적으로 포함될 수 있습니다.
    # 예: $600, $1,200.50, $0.99
    redacted_content = re.sub(r'\$\d+(?:,\d{3})*(?:\.\d+)?', 'xxx', text_content)

    return redacted_content

config = BigQueryLoggerConfig(
    enabled=True,
    event_allowlist=["LLM_REQUEST", "LLM_RESPONSE"], # 이러한 이벤트만 로깅
    # event_denylist=["TOOL_STARTING"], # 이러한 이벤트 건너뛰기
    shutdown_timeout=10.0, # 종료 시 로그가 플러시될 때까지 최대 10초 대기
    client_close_timeout=2.0, # BQ 클라이언트가 닫힐 때까지 최대 2초 대기
    max_content_length=500, # 콘텐츠를 500자로 자르기(기본값)
    content_formatter=redact_dollar_amounts, # 로깅 콘텐츠에서 달러 금액 수정

)

plugin = BigQueryAgentAnalyticsPlugin(..., config=config)
```

## 스키마 및 프로덕션 설정

테이블이 없으면 플러그인이 자동으로 테이블을 만듭니다. 그러나 프로덕션의 경우 성능 및 비용 최적화를 위해 **파티셔닝** 및 **클러스터링**을 사용하여 테이블을 수동으로 만드는 것이 좋습니다.

**권장 DDL:**

```sql
CREATE TABLE `your-gcp-project-id.adk_agent_logs.agent_events`
(
  timestamp TIMESTAMP NOT NULL OPTIONS(description="이벤트가 기록된 UTC 시간입니다."),
  event_type STRING OPTIONS(description="기록되는 이벤트 유형을 나타냅니다(예: 'LLM_REQUEST', 'TOOL_COMPLETED')."),
  agent STRING OPTIONS(description="이벤트와 관련된 ADK 에이전트 또는 작성자의 이름입니다."),
  session_id STRING OPTIONS(description="단일 대화 또는 사용자 세션 내에서 이벤트를 그룹화하는 고유 식별자입니다."),
  invocation_id STRING OPTIONS(description="세션 내의 각 개별 에이전트 실행 또는 차례에 대한 고유 식별자입니다."),
  user_id STRING OPTIONS(description="현재 세션과 관련된 사용자의 식별자입니다."),
  content STRING OPTIONS(description="이벤트별 데이터(페이로드)입니다. 형식은 event_type에 따라 다릅니다."),
  error_message STRING OPTIONS(description="이벤트 처리 중에 오류가 발생하면 채워집니다."),
  is_truncated STRING OPTIONS(description="콘텐츠 필드가 크기 제한으로 인해 잘렸는지 여부를 나타냅니다.")
)
PARTITION BY DATE(timestamp)
CLUSTER BY event_type, agent, user_id;
```
### 이벤트 유형 및 페이로드 {#event-types}

`content` 열에는 `event_type`에 특정한 형식화된 문자열이 포함되어 있습니다. 다음 표에서는 이러한 이벤트와 해당 콘텐츠에 대해 설명합니다.

!!! note

    - 모든 가변 콘텐츠 필드(예: 사용자 입력, 모델 응답, 도구 인수, 시스템 프롬프트)
    - 로그 크기를 관리하기 위해 `max_content_length` 문자로 잘립니다.
    - (`BigQueryLoggerConfig`에서 구성, 기본값 500)

#### LLM 상호 작용(플러그인 수명 주기)

이러한 이벤트는 LLM으로 전송되고 LLM에서 수신된 원시 요청을 추적합니다.

<table>
  <thead>
    <tr>
      <th><strong>이벤트 유형</strong></th>
      <th><strong>트리거 조건</strong></th>
      <th><strong>콘텐츠 형식 논리</strong></th>
      <th><strong>콘텐츠 예</strong></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><pre>
LLM_REQUEST
</pre></p></td>
      <td><p><pre>
before_model_callback
</pre></p></td>
      <td><p><pre>
Model: {model} | Prompt: {prompt} | System Prompt: Model: {model} | Prompt: {formatted_contents} | System Prompt: {system_prompt} | Params: {params} | Available Tools: {tool_names}
</pre></p></td>
      <td><p><pre>
Model: gemini-1.5-flash | Prompt: user: Model: gemini-flash-1.5| Prompt: user: text: 'Hello'| System Prompt: You are a helpful assistant. | Params: {temperature=1.0} | Available Tools: ['bigquery_tool']
</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>
LLM_RESPONSE
</pre></p></td>
      <td><p><pre>
after_model_callback
</pre></p></td>
      <td><strong>도구 호출인 경우:</strong> <code>Tool Name: {func_names} | Token Usage: {usage}</code><br>
<br>
**텍스트인 경우:** `Tool Name: text_response, text: '{text}' | Token Usage:
{usage}`</td>
      <td><p><pre>
Tool Name: text_response, text: 'Here is the data.' | Token Usage: {prompt: 10, candidates: 5, total: 15}
</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>
LLM_ERROR
</pre></p></td>
      <td><p><pre>
on_model_error_callback
</pre></p></td>
      <td><code>None</code> (오류 세부 정보는 <code>error_message</code>
열에 있음)</td>
      <td><p><pre>
None
</pre></p></td>
    </tr>
  </tbody>
</table>

#### 도구 사용(플러그인 수명 주기)

이러한 이벤트는 에이전트에 의한 도구 실행을 추적합니다.

<table>
  <thead>
    <tr>
      <th><strong>이벤트 유형</strong></th>
      <th><strong>트리거 조건</strong></th>
      <th><strong>콘텐츠 형식 논리</strong></th>
      <th><strong>콘텐츠 예</strong></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><pre>
TOOL_STARTING
</pre></p></td>
      <td><p><pre>
before_tool_callback
</pre></p></td>
      <td><p><pre>
Tool Name: {name}, Description: {desc}, Arguments: {args}
</pre></p></td>
      <td><p><pre>
Tool Name: list_datasets, Description: Lists datasets..., Arguments: {'project_id': 'my-project'}
</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>
TOOL_COMPLETED
</pre></p></td>
      <td><p><pre>
after_tool_callback
</pre></p></td>
      <td><p><pre>
Tool Name: {name}, Result: {result}
</pre></p></td>
      <td><p><pre>
Tool Name: list_datasets, Result: ['dataset_1', 'dataset_2']
</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>
TOOL_ERROR
</pre></p></td>
      <td><p><pre>
on_tool_error_callback
</pre></p></td>
      <td><code>Tool Name: {name}, Arguments: {args}</code> (오류 세부 정보는
<code>error_message</code>에 있음)</td>
      <td><p><pre>
Tool Name: list_datasets, Arguments: {}
</pre></p></td>
    </tr>
  </tbody>
</table>

#### 에이전트 수명 주기(플러그인 수명 주기)

이러한 이벤트는 하위 에이전트를 포함한 에이전트 실행의 시작과 끝을 추적합니다.

<table>
  <thead>
    <tr>
      <th><strong>이벤트 유형</strong></th>
      <th><strong>트리거 조건</strong></th>
      <th><strong>콘텐츠 형식 논리</strong></th>
      <th><strong>콘텐츠 예</strong></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><pre>
INVOCATION_STARTING
</pre></p></td>
      <td><p><pre>
before_run_callback
</pre></p></td>
      <td><p><pre>
None
</pre></p></td>
      <td><p><pre>
None
</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>
INVOCATION_COMPLETED
</pre></p></td>
      <td><p><pre>
after_run_callback
</pre></p></td>
      <td><p><pre>
None
</pre></p></td>
      <td><p><pre>
None
</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>
AGENT_STARTING
</pre></p></td>
      <td><p><pre>
before_agent_callback
</pre></p></td>
      <td><p><pre>
Agent Name: {agent_name}
</pre></p></td>
      <td><p><pre>
Agent Name: sub_agent_researcher
</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>
AGENT_COMPLETED
</pre></p></td>
      <td><p><pre>
after_agent_callback
</pre></p></td>
      <td><p><pre>
Agent Name: {agent_name}
</pre></p></td>
      <td><p><pre>
Agent Name: sub_agent_researcher
</pre></p></td>
    </tr>
  </tbody>
</table>

#### 사용자 및 일반 이벤트(이벤트 스트림)

이러한 이벤트는 에이전트 또는 실행기에서 생성된 `Event` 개체에서 파생됩니다.

<table>
  <thead>
    <tr>
      <th><strong>이벤트 유형</strong></th>
      <th><strong>트리거 조건</strong></th>
      <th><strong>콘텐츠 형식 논리</strong></th>
      <th><strong>콘텐츠 예</strong></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><pre>
USER_MESSAGE_RECEIVED
</pre></p></td>
      <td><p><pre>
on_user_message_callback
</pre></p></td>
      <td><p><pre>
User Content: {formatted_message}
</pre></p></td>
      <td><p><pre>
User Content: text: 'Show me the sales data.'
</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>
TOOL_CALL
</pre></p></td>
      <td><code>event.get_function_calls()</code>가 true임</td>
      <td><p><pre>
call: {func_name}
</pre></p></td>
      <td><p><pre>
call: list_datasets
</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>
TOOL_RESULT
</pre></p></td>
      <td><code>event.get_function_responses()</code>가 true임</td>
      <td><p><pre>
resp: {func_name}
</pre></p></td>
      <td><p><pre>
resp: list_datasets
</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>
MODEL_RESPONSE
</pre></p></td>
      <td><code>event.content</code>에 파트가 있음</td>
      <td><p><pre>
text: '{text}'
</pre></p></td>
      <td><p><pre>
text: 'I found 2 datasets.'
</pre></p></td>
    </tr>
  </tbody>
</table>

## 고급 분석 쿼리

다음 예제 쿼리는 BigQuery에 기록된 ADK 에이전트 이벤트 분석 데이터에서 정보를 추출하는 방법을 보여줍니다. [BigQuery 콘솔](https://console.cloud.google.com/bigquery)을 사용하여 이러한 쿼리를 실행할 수 있습니다.

이러한 쿼리를 실행하기 전에 제공된 SQL 내에서 GCP 프로젝트 ID, BigQuery 데이터 세트 ID 및 테이블 ID(지정하지 않은 경우 기본값은 "agent_events")를 업데이트해야 합니다.

**특정 대화 차례 추적**

```sql
SELECT timestamp, event_type, agent, content
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE invocation_id = 'your-invocation-id'
ORDER BY timestamp ASC;
```

**일일 호출 볼륨**

```sql
SELECT DATE(timestamp) as log_date, COUNT(DISTINCT invocation_id) as count
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE event_type = 'INVOCATION_STARTING'
GROUP BY log_date ORDER BY log_date DESC;
```

**토큰 사용량 분석**

```sql
SELECT
  AVG(CAST(REGEXP_EXTRACT(content, r"Token Usage:.*total: ([0-9]+)") AS INT64)) as avg_tokens
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE event_type = 'LLM_RESPONSE';
```

**오류 모니터링**

```sql
SELECT timestamp, event_type, error_message
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE error_message IS NOT NULL
ORDER BY timestamp DESC LIMIT 50;
```

## 추가 리소스

-   [BigQuery Storage Write API](https://cloud.google.com/bigquery/docs/write-api)
-   [BigQuery 제품 설명서](https://cloud.google.com/bigquery/docs)
