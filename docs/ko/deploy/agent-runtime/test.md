# Agent Runtime에 배포된 에이전트 테스트하기

<div class="language-support-tag" title="Agent Runtime은 현재 Python과 Go를 지원합니다.">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span><span class="lst-go">Go v1.2.0</span>
</div>

이 문서에서는 [Agent Runtime](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview) 런타임 환경에 배포된 ADK 에이전트를 테스트하는 방법을 설명합니다. 이 지침을 따르기 전에 먼저 [지원되는 배포 방법](/deploy/agent-runtime/) 중 하나를 사용하여 에이전트를 Agent Runtime 환경에 배포해야 합니다. 이 가이드에서는 Google Cloud 콘솔을 통해 배포된 에이전트를 확인 및 테스트하고, REST API 호출이나 Python용 Agent Platform SDK를 사용하여 에이전트와 상호작용하는 방법을 안내합니다.

## Cloud 콘솔에서 배포된 에이전트 보기

Cloud 콘솔에서 배포된 에이전트를 확인하려면 다음 단계를 따르세요.

- Google Cloud 콘솔의 Agent Runtime 페이지로 이동합니다.
    [https://console.cloud.google.com/vertex-ai/agents/agent-engines](https://console.cloud.google.com/vertex-ai/agents/agent-engines)

이 페이지에는 현재 선택된 Google Cloud 프로젝트에 배포된 모든 에이전트가 표시됩니다. 목록에 에이전트가 보이지 않는다면 Google Cloud 콘솔에서 배포 대상 프로젝트가 올바르게 선택되어 있는지 확인하세요. 기존 Google Cloud 프로젝트 선택에 관한 자세한 내용은 [프로젝트 생성 및 관리](https://cloud.google.com/resource-manager/docs/creating-managing-projects#identifying_projects)를 참고하세요.

## Google Cloud 프로젝트 정보 찾기

배포를 테스트하려면 프로젝트 주소 및 리소스 식별 정보(`PROJECT_ID`, `LOCATION_ID`, `RESOURCE_ID`)가 필요합니다. Cloud 콘솔이나 `gcloud` 명령줄 도구를 사용하여 이 정보를 확인할 수 있습니다.

??? note "Agent Platform 익스프레스 모드 API 키"
    Agent Platform 익스프레스 모드를 사용하는 경우 이 단계를 건너뛰고 API 키를 바로 사용할 수 있습니다.

Google Cloud 콘솔에서 프로젝트 정보를 찾으려면 다음 단계를 따르세요.

1. Google Cloud 콘솔의 Agent Runtime 페이지로 이동합니다.
    [https://console.cloud.google.com/vertex-ai/agents/agent-engines](https://console.cloud.google.com/vertex-ai/agents/agent-engines)

1. 확인하려는 인스턴스를 선택합니다.

1. 페이지 상단에서 **쿼리 URL 복사(Copy query URL)**를 선택합니다. URL 형식은 다음과 같습니다.

        https://$(LOCATION_ID)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION_ID)/reasoningEngines/$(RESOURCE_ID):query

`gcloud` 명령줄 도구로 프로젝트 정보를 찾으려면 다음 단계를 따르세요.

1. 개발 환경에서 Google Cloud에 인증되어 있는지 확인한 뒤, 다음 명령어를 실행하여 프로젝트 목록을 조회합니다.

    ```shell
    gcloud projects list
    ```

1. 배포에 사용한 프로젝트 ID로 다음 명령어를 실행하여 추가 세부정보를 확인합니다.

    ```shell
    gcloud asset search-all-resources \
        --scope=projects/$(PROJECT_ID) \
        --asset-types='aiplatform.googleapis.com/ReasoningEngine' \
        --format="table(name,assetType,location,reasoning_engine_id)"
    ```

## REST 호출을 사용한 테스트

Agent Runtime에 배포된 에이전트와 상호작용하는 간단한 방법은 `curl` 도구를 사용한 REST 호출입니다. 이 섹션에서는 에이전트 연결을 확인하는 방법과 배포된 에이전트의 요청 처리를 테스트하는 방법을 설명합니다.

### 에이전트 연결 확인

Cloud 콘솔의 Agent Runtime 섹션에서 제공하는 **쿼리 URL(Query URL)**을 사용하여 실행 중인 에이전트와의 연결을 확인할 수 있습니다. 이 확인 요청은 배포된 에이전트를 직접 실행하지 않고 에이전트에 대한 메타데이터 정보를 반환합니다.

REST 호출을 보내 배포된 에이전트로부터 응답을 받으려면 다음 단계를 따르세요.

- 개발 환경의 터미널 창에서 요청을 작성하고 실행합니다.

    === "Google Cloud Project"

        ```shell
        curl -X GET \
            -H "Authorization: Bearer $(gcloud auth print-access-token)" \
            "https://$(LOCATION_ID)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION_ID)/reasoningEngines"
        ```

    === "Agent Platform express mode"

        ```shell
        curl -X GET \
            -H "x-goog-api-key:YOUR-EXPRESS-MODE-API-KEY" \
            "https://aiplatform.googleapis.com/v1/reasoningEngines"
        ```

배포가 성공적이었다면 유효한 요청 목록과 예상 데이터 형식이 응답으로 반환됩니다.

!!! tip "연결 확인 URL에서 `:query` 제거"
    Cloud 콘솔의 Agent Runtime 섹션에서 복사한 **Query URL**을 사용하는 경우 주소 끝에서 `:query` 부분을 제거해야 합니다.

!!! tip "에이전트 연결 접근 권한"
    이 연결 테스트를 수행하려면 호출하는 사용자에게 배포된 에이전트에 대한 유효한 액세스 토큰이 있어야 합니다. 다른 환경에서 테스트할 때는 호출하는 사용자가 Google Cloud 프로젝트의 에이전트에 연결할 권한이 있는지 확인하세요.

### 에이전트 요청 보내기

에이전트 프로젝트로부터 응답을 받으려면 먼저 세션을 생성하여 세션 ID를 발급받은 뒤, 해당 세션 ID를 사용하여 요청을 보내야 합니다. 다음 안내에 따라 진행하세요.

REST를 통해 배포된 에이전트와의 상호작용을 테스트하려면 다음 단계를 따르세요.

1. 개발 환경의 터미널 창에서 다음 템플릿으로 요청을 작성해 세션을 생성합니다.

    === "Google Cloud Project"

        ```shell
        curl \
            -H "Authorization: Bearer $(gcloud auth print-access-token)" \
            -H "Content-Type: application/json" \
            https://$(LOCATION_ID)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION_ID)/reasoningEngines/$(RESOURCE_ID):query \
            -d '{"class_method": "async_create_session", "input": {"user_id": "u_123"},}'
        ```

    === "Agent Platform express mode"

        ```shell
        curl \
            -H "x-goog-api-key:YOUR-EXPRESS-MODE-API-KEY" \
            -H "Content-Type: application/json" \
            https://aiplatform.googleapis.com/v1/reasoningEngines/$(RESOURCE_ID):query \
            -d '{"class_method": "async_create_session", "input": {"user_id": "u_123"},}'
        ```

1. 이전 명령어의 응답에서 **id** 필드에 생성된 **세션 ID(Session ID)**를 추출합니다.

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

1. 개발 환경의 터미널 창에서 이전 단계에서 생성된 세션 ID와 아래 템플릿을 사용하여 에이전트에 메시지를 보냅니다.

    === "Google Cloud Project"

        ```shell
        curl \
        -H "Authorization: Bearer $(gcloud auth print-access-token)" \
        -H "Content-Type: application/json" \
        https://$(LOCATION_ID)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION_ID)/reasoningEngines/$(RESOURCE_ID):streamQuery?alt=sse -d '{
        "class_method": "async_stream_query",
        "input": {
            "user_id": "u_123",
            "session_id": "4857885913439920384",
            "message": "Hey whats the weather in new york today?",
        }
        }'
        ```

    === "Agent Platform express mode"

        ```shell
        curl \
        -H "x-goog-api-key:YOUR-EXPRESS-MODE-API-KEY" \
        -H "Content-Type: application/json" \
        https://aiplatform.googleapis.com/v1/reasoningEngines/$(RESOURCE_ID):streamQuery?alt=sse -d '{
        "class_method": "async_stream_query",
        "input": {
            "user_id": "u_123",
            "session_id": "4857885913439920384",
            "message": "Hey whats the weather in new york today?",
        }
        }'
        ```

이 요청을 실행하면 배포된 에이전트 코드에서 JSON 형식의 응답이 반환됩니다. REST 호출을 사용하여 Agent Runtime에 배포된 ADK 에이전트와 상호작용하는 방법에 대한 자세한 내용은 Agent Runtime 문서의 [배포된 에이전트 관리](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/manage/overview#console) 및 [Agent Development Kit 에이전트 사용](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/use/adk)을 참고하세요.

## Python을 사용한 테스트

Python 코드를 사용하면 Agent Runtime에 배포된 에이전트를 더욱 정교하고 반복 가능하게 테스트할 수 있습니다. 아래 지침에서는 배포된 에이전트와 세션을 생성한 뒤 에이전트에 처리 요청을 보내는 방법을 설명합니다.

### 원격 세션 생성

`remote_app` 객체를 사용하여 배포된 원격 에이전트에 연결하고 세션을 생성합니다.

```py
# If you are in a new script or used the ADK CLI to deploy, you can connect like this:
# remote_app = agent_engines.get("your-agent-resource-name")
remote_session = await remote_app.async_create_session(user_id="u_456")
print(remote_session)
```

`create_session`(원격)의 예상 출력:

```console
{'events': [],
'user_id': 'u_456',
'state': {},
'id': '7543472750996750336',
'app_name': '7917477678498709504',
'last_update_time': 1743683353.030133}
```

`id` 값은 세션 ID이며, `app_name`은 Agent Runtime에 배포된 에이전트의 리소스 ID입니다.

#### 원격 에이전트에 쿼리 보내기

```py
async for event in remote_app.async_stream_query(
    user_id="u_456",
    session_id=remote_session["id"],
    message="whats the weather in new york",
):
    print(event)
```

`async_stream_query`(원격)의 예상 출력:

```console
{'parts': [{'function_call': {'id': 'af-f1906423-a531-4ecf-a1ef-723b05e85321', 'args': {'city': 'new york'}, 'name': 'get_weather'}}], 'role': 'model'}
{'parts': [{'function_response': {'id': 'af-f1906423-a531-4ecf-a1ef-723b05e85321', 'name': 'get_weather', 'response': {'status': 'success', 'report': 'The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).'}}}], 'role': 'user'}
{'parts': [{'text': 'The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).'}], 'role': 'model'}
```

Agent Runtime에 배포된 ADK 에이전트와의 상호작용에 대한 자세한 내용은 Agent Runtime 문서의 [배포된 에이전트 관리](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/manage/overview) 및 [Agent Development Kit 에이전트 사용](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/use/adk)을 참고하세요.

### 멀티모달 쿼리 보내기

에이전트에 멀티모달 쿼리(예: 이미지 포함)를 보내려면 `types.Part` 객체 목록으로 `async_stream_query`의 `message` 매개변수를 구성할 수 있습니다. 각 파트는 텍스트나 이미지가 될 수 있습니다.

이미지를 포함하려면 이미지의 Google Cloud Storage(GCS) URI를 전달하여 `types.Part.from_uri`를 사용하면 됩니다.

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

!!! note
    모델과의 내부 통신에서는 이미지의 Base64 인코딩이 사용될 수 있지만, Agent Runtime에 배포된 에이전트에 이미지 데이터를 전송할 때 권장되며 공식 지원되는 방법은 GCS URI를 전달하는 것입니다.

## 배포 정리

테스트 목적으로 배포를 수행했다면 작업 완료 후 클라우드 리소스를 정리하는 것이 좋습니다. Google Cloud 계정에 예상치 못한 비용이 청구되지 않도록 배포된 Agent Runtime 인스턴스를 삭제할 수 있습니다.

```python
remote_app.delete(force=True)
```

`force=True` 매개변수를 지정하면 세션과 같이 배포된 에이전트에서 생성된 모든 하위 리소스도 함께 삭제됩니다. Google Cloud의 [Agent Runtime UI](https://console.cloud.google.com/vertex-ai/agents/agent-engines)에서도 배포된 에이전트를 삭제할 수 있습니다.
