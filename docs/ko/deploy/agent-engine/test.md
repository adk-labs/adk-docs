# Agent Engine에 배포된 에이전트 테스트

이 안내서는 [Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)
런타임 환경에 배포된 ADK 에이전트를 테스트하는 방법을 설명합니다.
이 안내를 사용하기 전에 [사용 가능한 방법](/adk-docs/deploy/agent-engine/) 중 하나로
에이전트를 Agent Engine 런타임 환경에 배포해 두어야 합니다.
이 가이드는 Google Cloud Console에서 배포된 에이전트를 확인하고 상호작용하는 방법,
그리고 REST API 호출 또는 Vertex AI SDK for Python으로 에이전트와 상호작용하는 방법을 다룹니다.

## Cloud Console에서 배포된 에이전트 보기

Cloud Console에서 배포된 에이전트를 확인하려면:

-   Google Cloud Console의 Agent Engine 페이지로 이동합니다.
    [https://console.cloud.google.com/vertex-ai/agents/agent-engines](https://console.cloud.google.com/vertex-ai/agents/agent-engines)

이 페이지에는 현재 선택한 Google Cloud 프로젝트에 배포된 모든 에이전트가 표시됩니다.
에이전트가 보이지 않으면 Cloud Console에서 대상 프로젝트가 선택되어 있는지 확인하세요.
기존 Google Cloud 프로젝트 선택 방법은
[프로젝트 생성 및 관리](https://cloud.google.com/resource-manager/docs/creating-managing-projects#identifying_projects)를 참고하세요.

## Google Cloud 프로젝트 정보 찾기

배포 테스트를 하려면 프로젝트의 주소 및 리소스 식별자(`PROJECT_ID`,
`LOCATION_ID`, `RESOURCE_ID`)가 필요합니다. Cloud Console 또는 `gcloud`
명령줄 도구로 이 정보를 찾을 수 있습니다.

??? note "Vertex AI express mode API key"
    Vertex AI express mode를 사용하는 경우 이 단계를 건너뛰고 API 키를 사용해도 됩니다.

Google Cloud Console에서 프로젝트 정보를 찾으려면:

1.  Google Cloud Console에서 Agent Engine 페이지로 이동합니다.
    [https://console.cloud.google.com/vertex-ai/agents/agent-engines](https://console.cloud.google.com/vertex-ai/agents/agent-engines)

1.  페이지 상단에서 **API URLs**를 선택한 뒤, 배포된 에이전트의 **Query URL** 문자열을 복사합니다.
    형식은 다음과 같습니다.

        https://$(LOCATION_ID)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION_ID)/reasoningEngines/$(RESOURCE_ID):query

`gcloud` 명령줄 도구로 프로젝트 정보를 찾으려면:

1.  개발 환경 터미널에서 Google Cloud 인증이 되어 있는지 확인하고,
    다음 명령어로 프로젝트 목록을 확인합니다.

    ```shell
    gcloud projects list
    ```

1.  배포에 사용한 Project ID로 다음 명령을 실행해 추가 정보를 조회합니다.

    ```shell
    gcloud asset search-all-resources \
        --scope=projects/$(PROJECT_ID) \
        --asset-types='aiplatform.googleapis.com/ReasoningEngine' \
        --format="table(name,assetType,location,reasoning_engine_id)"
    ```

## REST 호출로 테스트

Agent Engine에 배포된 에이전트와 상호작용하는 가장 간단한 방법은
`curl`을 이용한 REST 호출입니다. 이 섹션에서는 에이전트 연결 확인 방법과
배포된 에이전트의 요청 처리 테스트 방법을 설명합니다.

### 에이전트 연결 확인

Cloud Console의 Agent Engine 섹션에 있는 **Query URL**로 실행 중인 에이전트 연결을 확인할 수 있습니다.
이 확인은 배포된 에이전트를 실행하지 않고 에이전트 정보만 반환합니다.

REST 호출을 보내 배포된 에이전트로부터 응답을 받으려면:

-   개발 환경의 터미널에서 요청을 구성하고 실행합니다.

    === "Google Cloud Project"

        ```shell
        curl -X GET \
            -H "Authorization: Bearer $(gcloud auth print-access-token)" \
            "https://$(LOCATION_ID)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION_ID)/reasoningEngines"
        ```

    === "Vertex AI express mode"

        ```shell
        curl -X GET \
            -H "x-goog-api-key:YOUR-EXPRESS-MODE-API-KEY" \
            "https://aiplatform.googleapis.com/v1/reasoningEngines"
        ```

배포가 성공했다면 이 요청은 유효한 요청 목록과 예상 데이터 형식을 반환합니다.

!!! tip "연결 URL에서 `:query` 파라미터 제거"
    Agent Engine 섹션의 **Query URL**을 사용할 때는 주소 끝의 `:query` 파라미터를 제거하세요.

!!! tip "에이전트 연결 접근 권한"
    이 연결 테스트를 하려면 호출 사용자에게 배포된 에이전트에 대한 유효한 액세스 토큰이 있어야 합니다.
    다른 환경에서 테스트할 경우, 호출 사용자에게 해당 Google Cloud 프로젝트의 에이전트 연결 권한이 있는지 확인하세요.

### 에이전트 요청 보내기

에이전트 프로젝트에서 응답을 받으려면 먼저 세션을 생성해 Session ID를 받고,
그 Session ID를 사용해 요청을 보내야 합니다. 아래 절차를 따르세요.

REST를 통해 배포된 에이전트 상호작용을 테스트하려면:

1.  개발 환경 터미널에서 다음 템플릿으로 요청을 구성해 세션을 생성합니다.

    === "Google Cloud Project"

        ```shell
        curl \
            -H "Authorization: Bearer $(gcloud auth print-access-token)" \
            -H "Content-Type: application/json" \
            https://$(LOCATION_ID)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION_ID)/reasoningEngines/$(RESOURCE_ID):query \
            -d '{"class_method": "async_create_session", "input": {"user_id": "u_123"},}'
        ```

    === "Vertex AI express mode"

        ```shell
        curl \
            -H "x-goog-api-key:YOUR-EXPRESS-MODE-API-KEY" \
            -H "Content-Type: application/json" \
            https://aiplatform.googleapis.com/v1/reasoningEngines/$(RESOURCE_ID):query \
            -d '{"class_method": "async_create_session", "input": {"user_id": "u_123"},}'
        ```

1.  이전 명령의 응답에서 **id** 필드의 생성된 **Session ID**를 추출합니다.

    ```json
    {
        "output": {
            "userId": "u_123",
            "lastUpdateTime": 1757690426.337745,
            "state": {},
            "id": "4857885913439920384", # Session ID
            "appName": "9888888855577777776",
            "events": []
        }
    }
    ```

1.  개발 환경 터미널에서 이전 단계의 Session ID를 사용해,
    다음 템플릿으로 에이전트에 메시지를 보냅니다.

    === "Google Cloud Project"

        ```shell
        curl \
        -H "Authorization: Bearer $(gcloud auth print-access-token)" \
        -H "Content-Type: application/json" \
        https://$(LOCATION_ID)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION_ID)/reasoningEngines/$(RESOURCE_ID):query?alt=sse -d '{
        "class_method": "async_stream_query",
        "input": {
            "user_id": "u_123",
            "session_id": "4857885913439920384",
            "message": "Hey whats the weather in new york today?",
        }
        }'
        ```

    === "Vertex AI express mode"

        ```shell
        curl \
        -H "x-goog-api-key:YOUR-EXPRESS-MODE-API-KEY" \
        -H "Content-Type: application/json" \
        https://aiplatform.googleapis.com/v1/reasoningEngines/$(RESOURCE_ID):query?alt=sse -d '{
        "class_method": "async_stream_query",
        "input": {
            "user_id": "u_123",
            "session_id": "4857885913439920384",
            "message": "Hey whats the weather in new york today?",
        }
        }'
        ```

이 요청은 배포된 에이전트 코드의 JSON 응답을 생성해야 합니다.
Agent Engine에서 REST로 배포된 ADK 에이전트와 상호작용하는 자세한 내용은
Agent Engine 문서의
[배포된 에이전트 관리](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/manage/overview#console)
및
[Agent Development Kit 에이전트 사용](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/use/adk)
을 참고하세요.

## Python으로 테스트

Agent Engine에 배포된 에이전트를 더 정교하고 반복 가능하게 테스트하려면
Python 코드를 사용할 수 있습니다. 이 섹션에서는 배포된 에이전트에 세션을 생성하고,
요청을 보내 처리하는 방법을 설명합니다.

### 원격 세션 생성

`remote_app` 객체를 사용해 배포된 원격 에이전트에 연결합니다.

```py
# 새 스크립트에서 시작했거나 ADK CLI로 배포했다면 다음처럼 연결할 수 있습니다.
# remote_app = agent_engines.get("your-agent-resource-name")
remote_session = await remote_app.async_create_session(user_id="u_456")
print(remote_session)
```

`create_session`(원격) 예상 출력:

```console
{'events': [],
'user_id': 'u_456',
'state': {},
'id': '7543472750996750336',
'app_name': '7917477678498709504',
'last_update_time': 1743683353.030133}
```

`id` 값은 세션 ID이고, `app_name`은 Agent Engine에 배포된
에이전트의 리소스 ID입니다.

#### 원격 에이전트에 쿼리 보내기

```py
async for event in remote_app.async_stream_query(
    user_id="u_456",
    session_id=remote_session["id"],
    message="whats the weather in new york",
):
    print(event)
```

`async_stream_query`(원격) 예상 출력:

```console
{'parts': [{'function_call': {'id': 'af-f1906423-a531-4ecf-a1ef-723b05e85321', 'args': {'city': 'new york'}, 'name': 'get_weather'}}], 'role': 'model'}
{'parts': [{'function_response': {'id': 'af-f1906423-a531-4ecf-a1ef-723b05e85321', 'name': 'get_weather', 'response': {'status': 'success', 'report': 'The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).'}}}], 'role': 'user'}
{'parts': [{'text': 'The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).'}], 'role': 'model'}
```

Agent Engine에서 배포된 ADK 에이전트와 상호작용하는 자세한 내용은
Agent Engine 문서의
[배포된 에이전트 관리](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/manage/overview)
및
[Agent Development Kit 에이전트 사용](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/use/adk)
을 참고하세요.

### 멀티모달 쿼리 보내기

에이전트에 멀티모달 쿼리(예: 이미지 포함)를 보내려면,
`async_stream_query`의 `message` 파라미터를 `types.Part` 객체 리스트로 구성할 수 있습니다.
각 part는 텍스트 또는 이미지가 될 수 있습니다.

이미지를 포함하려면 Google Cloud Storage(GCS) URI를 제공하는
`types.Part.from_uri`를 사용할 수 있습니다.

```python
from google.genai import types

image_part = types.Part.from_uri(
    file_uri="gs://cloud-samples-data/generative-ai/image/scones.jpg",
    mime_type="image/jpeg",
)
text_part = types.Part.from_text(
    text="What is in this image?",
)

async for event in remote_app.async_stream_query(
    user_id="u_456",
    session_id=remote_session["id"],
    message=[text_part, image_part],
):
    print(event)
```

!!!note
    모델과의 내부 통신에서 이미지에 Base64 인코딩이 사용될 수 있지만,
    Agent Engine에 배포된 에이전트로 이미지 데이터를 보내는
    권장 및 지원 방식은 GCS URI를 제공하는 방법입니다.

## 배포 정리

테스트 목적으로 배포를 수행했다면, 완료 후 클라우드 리소스를 정리하는 것이 좋습니다.
예상치 못한 과금을 방지하기 위해 배포된 Agent Engine 인스턴스를 삭제할 수 있습니다.

```python
remote_app.delete(force=True)
```

`force=True`는 세션 등 배포 에이전트에서 생성된 하위 리소스도 함께 삭제합니다.
Google Cloud의
[Agent Engine UI](https://console.cloud.google.com/vertex-ai/agents/agent-engines)에서도
배포된 에이전트를 삭제할 수 있습니다.
