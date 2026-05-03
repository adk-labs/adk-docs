# 에이전트 런타임에서 배포된 에이전트를 테스트합니다.

이 지침에서는 다음에 배포된 ADK 에이전트를 테스트하는 방법을 설명합니다.
[Agent Runtime](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)
런타임 환경. 이 지침을 사용하기 전에 다음 사항을 완료해야 합니다.
하나를 사용하여 Agent Runtime 런타임 환경에 에이전트를 배포합니다.
[available methods](/deploy/agent-runtime/)의. 이 가이드에서는
Google Cloud를 통해 배포된 에이전트를 보고, 상호작용하고, 테스트하는 방법
콘솔을 사용하고 REST API 호출 또는 Agent Platform SDK를 사용하여 에이전트와 상호 작용합니다.
파이썬의 경우.

## Cloud Console에서 배포된 에이전트 보기

Cloud Console에서 배포된 에이전트를 보려면 다음 안내를 따르세요.

- Google Cloud Console에서 에이전트 런타임 페이지로 이동합니다.
    [https://console.cloud.google.com/vertex-ai/agents/agent-engines](https://console.cloud.google.com/vertex-ai/agents/agent-engines)

이 페이지에는 현재 선택한 Google Cloud에 배포된 모든 에이전트가 나열되어 있습니다.
프로젝트. 귀하의 대리인이 목록에 표시되지 않으면 귀하의 대리인이 있는지 확인하십시오.
Google Cloud Console에서 선택된 대상 프로젝트입니다. 자세한 내용은
기존 Google Cloud 프로젝트 선택, 참조
[Creating and managing projects](https://cloud.google.com/resource-manager/docs/creating-managing-projects#identifying_projects).

## Google Cloud 프로젝트 정보 찾기

프로젝트에 대한 주소와 리소스 식별이 필요합니다(`PROJECT_ID`,
`LOCATION_ID`, `RESOURCE_ID`) 배포를 테스트할 수 있습니다. 클라우드를 사용할 수 있습니다.
이 정보를 찾으려면 콘솔이나 `gcloud` 명령줄 도구를 사용하세요.

??? note "에이전트 플랫폼 익스프레스 모드 API 키"
    에이전트 플랫폼 익스프레스 모드를 사용하는 경우 이 단계를 건너뛰고 API 키를 사용할 수 있습니다.

Google Cloud Console로 프로젝트 정보를 찾으려면 다음 안내를 따르세요.

1. Google Cloud Console에서 에이전트 런타임 페이지로 이동합니다.
    [https://console.cloud.google.com/vertex-ai/agents/agent-engines](https://console.cloud.google.com/vertex-ai/agents/agent-engines)

1. 페이지 상단에서 **API URL**을 선택한 후 **Query
    배포된 에이전트의 URL** 문자열은 다음 형식이어야 합니다.

        https://$(LOCATION_ID)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION_ID)/reasoningEngines/$(RESOURCE_ID):query

`gcloud` 명령줄 도구를 사용하여 프로젝트 정보를 찾으려면:

1. 개발 환경에서 인증을 받았는지 확인하세요.
    Google Cloud를 열고 다음 명령어를 실행하여 프로젝트를 나열합니다.

    ```shell
    gcloud projects list
    ```

1. 배포에 사용한 프로젝트 ID로 이 명령을 실행하여
    추가 세부정보:

    ```shell
    gcloud asset search-all-resources \
        --scope=projects/$(PROJECT_ID) \
        --asset-types='aiplatform.googleapis.com/ReasoningEngine' \
        --format="table(name,assetType,location,reasoning_engine_id)"
    ```

## REST 호출을 사용하여 테스트

Agent Runtime에서 배포된 에이전트와 상호 작용하는 간단한 방법은 REST를 사용하는 것입니다.
`curl` 도구를 사용하여 호출합니다. 이 섹션에서는 확인 방법에 대해 설명합니다.
에이전트에 연결하고 배포된 요청 처리를 테스트합니다.
대리인.

### 에이전트 연결 확인

**쿼리 URL**을 사용하여 실행 중인 에이전트에 대한 연결을 확인할 수 있습니다.
Cloud Console의 에이전트 런타임 섹션에서 사용할 수 있습니다. 이 수표는 그렇지 않습니다
배포된 에이전트를 실행하지만 에이전트에 대한 정보를 반환합니다.

REST 호출을 보내고 배포된 에이전트로부터 응답을 받으려면 다음 안내를 따르세요.

- 개발 환경의 터미널 창에서 요청을 작성합니다.
    그리고 그것을 실행하세요:

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

배포가 성공한 경우 이 요청은 유효한 목록으로 응답합니다.
요청 및 예상 데이터 형식.

!!! tip "연결 URL에 대한 `:query` 매개변수 제거"
    클라우드의 Agent Runtime 섹션에서 제공되는 **Query URL**을 사용하는 경우
    콘솔의 경우 주소 끝에서 `:query` 매개변수를 제거했는지 확인하세요.

!!! tip "에이전트 연결을 위한 액세스"
    이 연결 테스트에서는 호출 사용자에게 유효한 액세스 토큰이 필요합니다.
    배포된 에이전트. 다른 환경에서 테스트할 때 호출하는 사용자가
    Google Cloud 프로젝트의 에이전트에 연결할 수 있는 액세스 권한이 있습니다.

### 에이전트 요청 보내기

에이전트 프로젝트에서 응답을 받을 때 먼저
세션을 실행하고 세션 ID를 받은 다음 해당 세션을 사용하여 요청을 보냅니다.
신분증. 이 프로세스는 다음 지침에 설명되어 있습니다.

REST를 통해 배포된 에이전트와의 상호 작용을 테스트하려면 다음 안내를 따르세요.

1. 개발 환경의 터미널 창에서 세션을 생성합니다.
    이 템플릿을 사용하여 요청을 작성하면:

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

1. 이전 명령의 응답에서 생성된 **세션 ID**를 추출합니다.
    **id** 필드에서:

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

1. 개발 환경의 터미널 창에서 다음으로 메시지를 보냅니다.
    이 템플릿과 세션 ID를 사용하여 요청을 작성하여 에이전트
    이전 단계에서 생성됨:

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

이 요청은 배포된 에이전트 코드에서 JSON으로 응답을 생성해야 합니다.
형식. 배포된 ADK 에이전트와의 상호작용에 대한 자세한 내용은
REST 호출을 사용하는 에이전트 런타임은 다음을 참조하세요.
[Manage deployed agents](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/manage/overview#console)
그리고
[Use an Agent Development Kit agent](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/use/adk)
에이전트 런타임 문서에서.

## Python을 사용하여 테스트

보다 정교하고 반복 가능한 테스트를 위해 Python 코드를 사용할 수 있습니다.
에이전트 런타임에 에이전트가 배포되었습니다. 이 지침에서는 생성 방법을 설명합니다.
배포된 에이전트와의 세션을 연결한 다음 에이전트에 요청을 보냅니다.
처리.

### 원격 세션 생성

`remote_app` 개체를 사용하여 배포된 원격 에이전트에 대한 연결을 만듭니다.

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

`id` 값은 세션 ID이고 `app_name`는 리소스 ID입니다.
에이전트 런타임에 에이전트를 배포했습니다.

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

배포된 ADK 에이전트와의 상호작용에 대한 자세한 내용은
에이전트 런타임, 참조
[Manage deployed agents](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/manage/overview)
그리고
[Use a Agent Development Kit agent](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/use/adk)
에이전트 런타임 문서에서.

### 다중 모드 쿼리 보내기

다중 모달 쿼리(예: 이미지 포함)를 에이전트에 보내려면 `types.Part` 개체 목록을 사용하여 `async_stream_query`의 `message` 매개 변수를 구성할 수 있습니다. 각 부분은 텍스트나 이미지일 수 있습니다.

이미지를 포함하려면 `types.Part.from_uri`를 사용하여 이미지에 대한 Google Cloud Storage(GCS) URI를 제공하면 됩니다.

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
    모델과의 기본 통신에는 Base64가 포함될 수 있습니다.
    이미지 인코딩, 이미지 전송에 권장되고 지원되는 방법
    에이전트 런타임에 배포된 에이전트에 대한 데이터는 GCS URI를 제공하여 이루어집니다.

## 배포 정리

테스트로 배포를 수행한 경우 정리하는 것이 좋습니다.
완료한 후 클라우드 리소스를 확인하세요. 배포된 Agent를 삭제할 수 있습니다.
Google Cloud 계정에 예상치 못한 비용이 청구되는 것을 방지하기 위한 런타임 인스턴스입니다.

```python
remote_app.delete(force=True)
```

`force=True` 매개변수는 생성된 모든 하위 리소스도 삭제합니다.
세션과 같은 배포된 에이전트에서. 배포된 항목을 삭제할 수도 있습니다.
에이전트를 통해
[Agent Runtime UI](https://console.cloud.google.com/vertex-ai/agents/agent-engines)
Google 클라우드에서
