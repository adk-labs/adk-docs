---
catalog_title: API Registry
catalog_description: Google Cloud 서비스를 MCP 도구로 동적으로 연결합니다
catalog_icon: /adk-docs/integrations/assets/developer-tools-color.svg
catalog_tags: ["google", "mcp", "connectors"]
---

# ADK용 Google Cloud API Registry 도구

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.20.0</span><span class="lst-preview">Preview</span>
</div>

Agent Development Kit(ADK)용 Google Cloud API Registry 커넥터 도구를 사용하면
[Google Cloud API Registry](https://docs.cloud.google.com/api-registry/docs/overview)를 통해
에이전트에서 다양한 Google Cloud 서비스를
Model Context Protocol(MCP) 서버로 사용할 수 있습니다.
이 도구를 구성해 에이전트를 Google Cloud 프로젝트에 연결하고,
해당 프로젝트에서 활성화된 Cloud 서비스를 동적으로 접근할 수 있습니다.

!!! example "Preview 릴리스"
    Google Cloud API Registry 기능은 Preview 릴리스입니다.
    자세한 내용은
    [launch stage descriptions](https://cloud.google.com/products#product-launch-stages)를 참조하세요.

## 사전 준비 사항

에이전트에서 API Registry를 사용하기 전에 다음을 확인해야 합니다:

-   **Google Cloud 프로젝트:**
    기존 Google Cloud 프로젝트를 사용해 에이전트가 AI 모델에 접근하도록 구성합니다.

-   **API Registry 접근 권한:**
    에이전트가 실행되는 환경에는 사용 가능한 MCP 서버 목록 조회를 위해
    `apiregistry.viewer` 역할이 부여된 Google Cloud
    [Application Default Credentials](https://docs.cloud.google.com/docs/authentication/provide-credentials-adc)가 필요합니다.

-   **Cloud API 활성화:**
    Google Cloud 프로젝트에서
    *cloudapiregistry.googleapis.com* 및 *apihub.googleapis.com* API를 활성화합니다.

-   **MCP 서버 및 도구 접근:**
    에이전트가 접근할 Cloud 프로젝트 내 Google Cloud 서비스의 MCP 서버를
    API Registry에서 활성화해야 합니다.
    Cloud Console에서 활성화하거나 다음과 같은 gcloud 명령을 사용할 수 있습니다:
    `gcloud beta api-registry mcp enable bigquery.googleapis.com --project={PROJECT_ID}`.
    에이전트가 사용하는 자격 증명은 MCP 서버와 도구가 사용하는 기저 서비스에
    접근 권한이 있어야 합니다. 예를 들어 BigQuery 도구를 사용하려면
    서비스 계정에 `bigquery.dataViewer`, `bigquery.jobUser` 같은
    BigQuery IAM 역할이 필요합니다. 필요한 권한에 대한 자세한 내용은
    [Authentication and access](#auth)를 참조하세요.

다음 gcloud 명령으로 API Registry에서 어떤 MCP 서버가 활성화됐는지 확인할 수 있습니다:

```console
gcloud beta api-registry mcp servers list --project={PROJECT_ID}.
```

## 에이전트와 함께 사용

에이전트에서 API Registry 커넥터 도구를 구성할 때는 먼저
***ApiRegistry*** 클래스를 초기화해 Cloud 서비스 연결을 설정하고,
`get_toolset()` 함수로 API Registry에 등록된 특정 MCP 서버의 툴셋을 가져옵니다.
다음 예시는 API Registry에 등록된 MCP 서버의 도구를 사용하는 에이전트 생성 방법이며,
BigQuery와 상호작용하도록 설계되었습니다:

```python
import os
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.api_registry import ApiRegistry

# Configure with your Google Cloud Project ID and registered MCP server name
PROJECT_ID = "your-google-cloud-project-id"
MCP_SERVER_NAME = "projects/your-google-cloud-project-id/locations/global/mcpServers/your-mcp-server-name"

# Example header provider for BigQuery, a project header is required.
def header_provider(context):
    return {"x-goog-user-project": PROJECT_ID}

# Initialize ApiRegistry
api_registry = ApiRegistry(
    api_registry_project_id=PROJECT_ID,
    header_provider=header_provider
)

# Get the toolset for the specific MCP server
registry_tools = api_registry.get_toolset(
    mcp_server_name=MCP_SERVER_NAME,
    # Optionally filter tools:
    #tool_filter=["list_datasets", "run_query"]
)

# Create an agent with the tools
root_agent = LlmAgent(
    model="gemini-1.5-flash", # Or your preferred model
    name="bigquery_assistant",
    instruction="""
Help user access their BigQuery data using the available tools.
    """,
    tools=[registry_tools],
)
```

이 예제의 전체 코드는
[api_registry_agent](https://github.com/google/adk-python/tree/main/contributing/samples/api_registry_agent/)
샘플을 참조하세요. 구성 옵션은
[Configuration](#configuration),
인증 관련 내용은
[Authentication and access](#auth)를 참조하세요.

## 인증 및 접근 {#auth}

에이전트에서 API Registry를 사용하려면, 에이전트가 접근하는 서비스에 대한
인증이 필요합니다. 기본적으로 이 도구는 인증에 Google Cloud
[Application Default Credentials](https://docs.cloud.google.com/docs/authentication/provide-credentials-adc)를 사용합니다.
다음 권한/접근을 확보해야 합니다:

-   **API Registry 접근:**
    `ApiRegistry` 클래스는 Application Default Credentials(`google.auth.default()`)를 사용해
    Google Cloud API Registry 요청을 인증하고 사용 가능한 MCP 서버를 조회합니다.
    에이전트 실행 환경의 자격 증명에는 `apiregistry.viewer`와 같은
    API Registry 리소스 조회 권한이 필요합니다.

-   **MCP 서버 및 도구 접근:**
    `get_toolset`이 반환하는 `McpToolset` 역시 기본적으로
    Google Cloud Application Default Credentials를 사용해
    실제 MCP 서버 엔드포인트 호출을 인증합니다.
    이 자격 증명에는 다음 두 가지 권한이 모두 필요합니다:
    1.  MCP 서버 자체 접근 권한.
    1.  도구가 상호작용하는 기저 서비스/리소스 이용 권한.

-   **MCP 도구 사용자 역할:**
    API registry를 통해 MCP 도구를 호출할 수 있도록, 에이전트가 사용하는 계정에
    MCP tool user 역할을 부여합니다:
    `gcloud projects add-iam-policy-binding {PROJECT_ID} --member={member}
    --role="roles/mcp.toolUser"`

예를 들어 BigQuery와 상호작용하는 MCP 서버 도구를 사용한다면,
서비스 계정 같은 자격 증명 계정에는 데이터셋 접근/쿼리 실행을 위해
Google Cloud 프로젝트에서 `bigquery.dataViewer`, `bigquery.jobUser` 같은
적절한 BigQuery IAM 역할이 부여되어야 합니다. bigquery MCP 서버의 경우
도구 사용 시 `"x-goog-user-project": PROJECT_ID` 헤더가 필요합니다.
`ApiRegistry` 생성자의 `header_provider` 인수로 인증 또는 프로젝트 컨텍스트용
추가 헤더를 주입할 수 있습니다.

## 구성 {#configuration}

***APIRegistry*** 객체는 다음 구성 옵션을 가집니다:

-   **`api_registry_project_id`** (str):
    API Registry가 위치한 Google Cloud 프로젝트 ID.

-   **`location`** (str, optional):
    API Registry 리소스의 위치. 기본값은 `"global"`.

-   **`header_provider`** (Callable, optional):
    호출 컨텍스트를 받아 MCP 서버 요청에 추가할 HTTP 헤더 딕셔너리를 반환하는 함수.
    동적 인증 또는 프로젝트별 헤더에 자주 사용됩니다.

`get_toolset()` 함수는 다음 구성 옵션을 가집니다:

-   **`mcp_server_name`** (str):
    도구를 로드할 등록된 MCP 서버의 전체 이름.
    예: `projects/my-project/locations/global/mcpServers/my-server`.

-   **`tool_filter`** (Union[ToolPredicate, List[str]], optional):
    툴셋에 포함할 도구 지정.
    -   문자열 리스트인 경우, 리스트에 있는 이름의 도구만 포함.
    -   `ToolPredicate` 함수인 경우, 각 도구마다 함수가 호출되고
        `True`를 반환하는 도구만 포함.
    -   `None`이면 MCP 서버의 모든 도구 포함.

-   **`tool_name_prefix`** (str, optional):
    결과 툴셋의 각 도구 이름 앞에 붙일 접두사.

## 추가 리소스

-   [api_registry_agent](https://github.com/google/adk-python/tree/main/contributing/samples/api_registry_agent/)
    ADK 코드 샘플
-   [Google Cloud API Registry](https://docs.cloud.google.com/api-registry/docs/overview)
    문서
