---
catalog_title: Data Agents
catalog_description: AI 기반 에이전트로 데이터 분석
catalog_icon: /integrations/assets/agent-platform.svg
catalog_tags: ["data", "google"]
---

# ADK용 Google Cloud Data Agents 도구

<div class="language-support-tag">
  <span class="lst-supported">ADK 지원</span><span class="lst-python">Python v1.23.0</span>
</div>

이 도구는 [Conversational Analytics API](https://docs.cloud.google.com/gemini/docs/conversational-analytics-api/overview)로 구동되는 데이터 에이전트와의 통합을 제공하는 도구 세트입니다.
데이터 에이전트는 자연어를 사용하여 데이터를 분석하는 데 도움을 주는 AI 기반 에이전트입니다. 데이터 에이전트를 구성할 때 **BigQuery**, **Looker**, **Looker Studio** 등 지원되는 데이터 소스 중에서 선택할 수 있습니다.
`DataAgentToolset`에는 기본적으로 다음과 같은 읽기 전용 도구가 포함되어 있습니다.

* **`list_accessible_data_agents`**: 지정된 Google Cloud 프로젝트에서 액세스 권한이 있는 데이터 에이전트를 나열합니다. 선택적 `location` 재정의는 물론 자동 또는 수동 페이지네이션(`page_size` 및 `page_token`)을 지원합니다.
* **`get_data_agent_info`**: 전체 리소스 이름(`projects/{project}/locations/{location}/dataAgents/{agent}`)을 기반으로 특정 데이터 에이전트에 대한 세부정보와 게시된 컨텍스트를 가져옵니다.
* **`ask_data_agent`**: 특정 데이터 에이전트에 자연어 질문을 보내고 응답을 반환합니다.

`DataAgentToolConfig`에서 `enable_data_agent_modification=True`로 설정하면 도구 세트에 다음 도구도 포함됩니다.

* **`create_data_agent`**: [`DataAgent` 리소스 스키마](https://docs.cloud.google.com/gemini/data-agents/reference/rest/v1/projects.locations.dataAgents#DataAgent)를 따르는 JSON `agent_config`에서 Google Cloud 프로젝트에 지정된 `data_agent_id`로 새 데이터 에이전트를 생성합니다. `location` 인수는 선택사항입니다.
* **`update_data_agent`**: JSON `agent_config`와 카멜 케이스(camelCase) 필드 이름의 쉼표로 구분된 `update_mask`(예: `displayName,description`)를 사용하여 기존 데이터 에이전트를 업데이트합니다. `update_mask`에 나열된 모든 필드는 `agent_config`에도 존재해야 합니다.
* **`delete_data_agent`**: 전체 리소스 이름을 기반으로 기존 데이터 에이전트를 삭제합니다.

이러한 수정 도구는 기본 장기 실행 작업이 완료될 때까지 최대 `data_agent_modification_timeout_seconds` 동안 대기합니다.

## 사전 요구사항

이 도구를 사용하기 전에 Google Cloud에서 다음 단계를 완료하세요.

* Google Cloud 프로젝트에서 Gemini Data Analytics API(`geminidataanalytics.googleapis.com`)를 사용 설정합니다.
* 도구 세트에서 사용하는 사용자 인증 정보에 데이터 에이전트 및 기본 데이터 소스에 필요한 IAM 권한이 있는지 확인합니다. 에이전트를 Google Cloud에 연결하는 방법에 대한 자세한 내용은 [Google Cloud 및 Agent Platform에 연결](/get-started/google-cloud/) 가이드를 참조하세요.
* `get_data_agent_info` 및 `ask_data_agent` 도구에는 기존 데이터 에이전트가 필요합니다. `create_data_agent`(`enable_data_agent_modification=True`인 경우)를 사용하거나 다음 가이드 중 하나를 따라 생성할 수 있습니다.
    * [HTTP 및 Python을 사용하여 데이터 에이전트 빌드](https://docs.cloud.google.com/gemini/docs/conversational-analytics-api/build-agent-http)
    * [Python SDK를 사용하여 데이터 에이전트 빌드](https://docs.cloud.google.com/gemini/docs/conversational-analytics-api/build-agent-sdk)
    * [BigQuery Studio에서 데이터 에이전트 생성](https://docs.cloud.google.com/bigquery/docs/create-data-agents#create_a_data_agent)

## 인증

`DataAgentToolset`에는 `DataAgentCredentialsConfig`가 필요하며 여러 인증 메커니즘을 지원합니다. `credentials`, `external_access_token_key` 또는 `client_id`와 `client_secret` 쌍 중 하나를 제공해야 합니다. 기본적으로 `DataAgentCredentialsConfig`는 `https://www.googleapis.com/auth/bigquery` OAuth 범위를 사용하며, OAuth 클라이언트 사용자 인증 정보를 구성할 때 `scopes`를 사용하여 이를 재정의할 수 있습니다.

!!! example "실험적 기능"
    `DataAgentCredentialsConfig` 클래스는 실험적 기능인 `BaseGoogleCredentialsConfig`를 확장하므로
    프로덕션 프로젝트에는 사용하지 않아야 합니다.

### 애플리케이션 기본 사용자 인증 정보 (ADC)

로컬 개발과 Cloud Run 및 GKE와 같은 Google Cloud 서비스에서 실행할 때 이 접근 방식을 사용해야 합니다.

```python
import google.auth
from google.adk.tools.data_agent import DataAgentToolset, DataAgentCredentialsConfig

# 애플리케이션 기본 사용자 인증 정보 로드
credentials, project_id = google.auth.default()

# 도구 세트 구성
credentials_config = DataAgentCredentialsConfig(credentials=credentials)
data_agent_toolset = DataAgentToolset(credentials_config=credentials_config)
```

### 서비스 계정

서비스 계정 파일이나 정보를 명시적으로 제공할 수 있습니다.

```python
from google.oauth2 import service_account
from google.adk.tools.data_agent import DataAgentToolset, DataAgentCredentialsConfig

# 서비스 계정 사용자 인증 정보 로드
credentials = service_account.Credentials.from_service_account_file('path/to/key.json')

# 도구 세트 구성
credentials_config = DataAgentCredentialsConfig(credentials=credentials)
data_agent_toolset = DataAgentToolset(credentials_config=credentials_config)
```

### 외부 액세스 토큰

최종 사용자를 대신하여 작동해야 하는 애플리케이션의 경우 OAuth2 흐름이나 외부 IDP 등에서 얻은 액세스 토큰으로 직접 인스턴스화된 사용자 인증 정보를 전달할 수 있습니다.

```python
from google.oauth2.credentials import Credentials
from google.adk.tools.data_agent import DataAgentToolset, DataAgentCredentialsConfig

# 외부 OAuth 흐름을 통해 'user_token'을 얻었다고 가정
credentials = Credentials(token=user_token)

# 도구 세트 구성
credentials_config = DataAgentCredentialsConfig(credentials=credentials)
data_agent_toolset = DataAgentToolset(credentials_config=credentials_config)
```

### 외부 인증 제공자

Gemini Enterprise와 같이 플랫폼에서 토큰을 관리하는 외부 인증 제공자와 통합하는 경우 `external_access_token_key`를 사용하세요.

```python
from google.adk.tools.data_agent import DataAgentToolset, DataAgentCredentialsConfig

# 세션 상태에서 액세스 토큰을 조회하는 데 사용되는 키
credentials_config = DataAgentCredentialsConfig(
    external_access_token_key="YOUR_AUTH_ID"
)
data_agent_toolset = DataAgentToolset(credentials_config=credentials_config)
```

### 대화형 인증 (ADK Web)

대화형 세션을 위해 `adk web` 인터페이스를 사용할 때 OAuth 2.0 클라이언트 사용자 인증 정보를 제공하여 로그인 흐름을 트리거할 수 있습니다. 이 메커니즘은 로컬 개발 환경과 ADK 에이전트가 Cloud Run과 같은 환경에 배포된 경우 모두에서 작동합니다.

```python
from google.adk.tools.data_agent import DataAgentToolset, DataAgentCredentialsConfig

# OAuth 2.0 클라이언트 ID 및 보안 비밀 제공
credentials_config = DataAgentCredentialsConfig(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET"
)
data_agent_toolset = DataAgentToolset(credentials_config=credentials_config)
```

## 구성

[`DataAgentToolConfig`](../api-reference/python/google-adk.html#google.adk.tools.data_agent.DataAgentToolConfig)를 사용하여 도구 동작을 맞춤설정할 수 있습니다.

* **`max_query_result_rows`** (`int`, 기본값: `50`): `ask_data_agent`가 각 데이터 결과에 대해 반환하는 최대 행 수입니다.
* **`location`** (`str | None`, 기본값: `None`): API 엔드포인트를 선택하는 데 사용되는 기본 Google Cloud 위치(예: `global`, `us` 또는 `eu`)입니다. `location` 인수를 받는 도구는 인수가 설정되지 않은 경우 이 값을 사용하며, 기본값으로 `global`로 대체됩니다. 다른 도구는 데이터 에이전트의 리소스 이름에서 위치를 사용하지만, `ask_data_agent`는 이 값이 설정된 경우 이 값을 사용합니다.
* **`api_endpoint`** (`str | None`, 기본값: `None`): Conversational Analytics API 요청을 위한 선택적 맞춤 API 엔드포인트입니다. 제공된 경우 기본 또는 위치 기반 API 엔드포인트를 재정의합니다.
* **`enable_data_agent_modification`** (`bool`, 기본값: `False`): `True`인 경우 도구 세트에 `create_data_agent`, `update_data_agent`, `delete_data_agent`도 포함됩니다. `False`인 경우 도구 세트는 읽기 전용입니다.
* **`data_agent_modification_timeout_seconds`** (`int`, 기본값: `60`): 장기 실행 생성, 업데이트 또는 삭제 작업을 폴링할 때의 총 타임아웃(초)입니다. `0`보다 커야 합니다.
* **`data_agent_modification_poll_interval_seconds`** (`int`, 기본값: `2`): 생성, 업데이트 또는 삭제 작업이 완료될 때까지 대기하는 동안의 폴링 간격(초)입니다. `0`보다 커야 합니다.

!!! warning "주의해서 사용"

    `enable_data_agent_modification=True`로 설정하면 에이전트가 Google Cloud 프로젝트에서 데이터 에이전트를 생성, 업데이트 및 삭제할 수 있습니다. 도구 세트에서 사용하는 사용자 인증 정보가 최소한의 필수 IAM 권한만 가진 승인된 프로젝트로 제한되어 있는지 확인하세요. 또한 `DataAgentToolset`에 `tool_filter`를 전달하여 특정 도구만 노출할 수도 있습니다(예: `delete_data_agent` 제외).

```python
import google.auth
from google.adk.tools.data_agent import DataAgentToolset, DataAgentCredentialsConfig
from google.adk.tools.data_agent.config import DataAgentToolConfig

credentials, _ = google.auth.default()
credentials_config = DataAgentCredentialsConfig(credentials=credentials)

tool_config = DataAgentToolConfig(
    max_query_result_rows=100,
    enable_data_agent_modification=True,
    data_agent_modification_timeout_seconds=120,
)
data_agent_toolset = DataAgentToolset(
    credentials_config=credentials_config,
    data_agent_tool_config=tool_config,
)
```

## 샘플 코드

다음 샘플 코드는 애플리케이션 기본 사용자 인증 정보(ADC)를 사용하여 ADK 에이전트에서 `DataAgentToolset`을 사용하는 방법을 보여줍니다.

```py
--8<-- "examples/python/snippets/tools/built-in-tools/data_agent.py:just_code"
```

참고: BigQuery 테이블과 데이터 세트를 도구로 직접 쿼리하려면 [ADK용 BigQuery 도구](bigquery.md)를 참조하세요.
