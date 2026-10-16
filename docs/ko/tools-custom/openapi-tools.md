# OpenAPI를 사용하여 REST API 통합하기

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span>
</div>

ADK는 [OpenAPI 사양(v3.x)](https://swagger.io/specification/)에서 직접 호출 가능한 도구를 자동으로 생성하여 외부 REST API와의 상호작용을 간소화합니다. 이를 통해 각 API 엔드포인트에 대한 개별 함수 도구를 수동으로 정의할 필요가 없어집니다.

!!! tip "핵심 이점"
    `OpenAPIToolset`을 사용하여 기존 API 문서(OpenAPI 사양)에서 에이전트 도구(`RestApiTool`)를 즉시 생성하고, 에이전트가 웹 서비스를 원활하게 호출할 수 있도록 하세요.

## 주요 구성 요소

*   **`OpenAPIToolset`**: 주로 사용하게 될 기본 클래스입니다. OpenAPI 사양으로 이 클래스를 초기화하면, 사양을 파싱하고 도구를 생성하는 작업을 처리합니다.
*   **`RestApiTool`**: `GET /pets/{petId}`나 `POST /pets`와 같이 호출 가능한 단일 API 작업을 나타내는 클래스입니다. `OpenAPIToolset`은 사양에 정의된 각 작업에 대해 하나의 `RestApiTool` 인스턴스를 생성합니다.

## 작동 방식

`OpenAPIToolset`을 사용할 때의 과정은 다음과 같은 주요 단계로 이루어집니다.

1.  **초기화 및 파싱**:
    *   OpenAPI 사양을 Python 딕셔너리, JSON 문자열 또는 YAML 문자열 형태로 `OpenAPIToolset`에 제공합니다.
    *   툴셋은 내부적으로 사양을 파싱하고 내부 참조(`$ref`)를 해석하여 전체 API 구조를 이해합니다.

2.  **작업 탐색**:
    *   사양의 `paths` 객체 내에 정의된 모든 유효한 API 작업(예: `GET`, `POST`, `PUT`, `DELETE`)을 식별합니다.

3.  **도구 생성**:
    *   탐색된 각 작업에 대해 `OpenAPIToolset`은 해당하는 `RestApiTool` 인스턴스를 자동으로 생성합니다.
    *   **도구 이름**: 사양의 `operationId`에서 파생됩니다 (`snake_case`로 변환, 최대 60자). `operationId`가 없는 경우, 메서드와 경로를 기반으로 이름이 생성됩니다.
    *   **도구 설명**: LLM을 위해 작업의 `summary`나 `description`을 사용합니다.
    *   **API 세부 정보**: 필요한 HTTP 메서드, 경로, 서버 기본 URL, 파라미터(경로, 쿼리, 헤더, 쿠키) 및 요청 본문 스키마를 내부적으로 저장합니다.

4.  **`RestApiTool` 기능**: 생성된 각 `RestApiTool`은 다음을 수행합니다.
    *   **스키마 생성**: 작업의 파라미터와 요청 본문을 기반으로 `FunctionDeclaration`을 동적으로 생성합니다. 이 스키마는 LLM에게 도구를 호출하는 방법(예상되는 인수)을 알려줍니다.
    *   **실행**: LLM에 의해 호출되면, LLM이 제공한 인수와 OpenAPI 사양의 세부 정보를 사용하여 올바른 HTTP 요청(URL, 헤더, 쿼리 파라미터, 본문)을 구성합니다. 인증이 설정된 경우 이를 처리하고 600초 읽기/쓰기 타임아웃(`httpx_client_factory`로 맞춤설정 가능)과 함께 `httpx` 라이브러리를 사용하여 비동기적으로 API 호출을 실행합니다.

5.  **인증**: `OpenAPIToolset`을 초기화할 때 전역 인증(예: API 키 또는 OAuth - 자세한 내용은 [인증](/ko/tools/authentication/) 참조)을 구성할 수 있습니다. 이 인증 구성은 생성된 모든 `RestApiTool` 인스턴스에 자동으로 적용됩니다.

## 사용 워크플로

OpenAPI 사양을 에이전트에 통합하려면 다음 단계를 따르세요.

1.  **사양 확보**: OpenAPI 사양 문서(예: `.json` 또는 `.yaml` 파일에서 로드, URL에서 가져오기)를 준비합니다.
2.  **툴셋 인스턴스화**: 사양 내용과 타입(`spec_str`/`spec_dict`, `spec_str_type`)을 전달하여 `OpenAPIToolset` 인스턴스를 생성합니다. API에 필요한 경우 인증 정보(`auth_scheme`, `auth_credential`)를 제공합니다.

    ```python
    from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import OpenAPIToolset

    # JSON 문자열 예시
    openapi_spec_json = '...' # OpenAPI JSON 문자열
    toolset = OpenAPIToolset(spec_str=openapi_spec_json, spec_str_type="json")

    # 딕셔너리 예시
    # openapi_spec_dict = {...} # OpenAPI 사양 딕셔너리
    # toolset = OpenAPIToolset(spec_dict=openapi_spec_dict)
    ```

3.  **에이전트에 추가**: 가져온 도구들을 `LlmAgent`의 `tools` 목록에 포함시킵니다.

    ```python
    from google.adk.agents import LlmAgent

    my_agent = LlmAgent(
        name="api_interacting_agent",
        model="gemini-flash-latest", # 또는 선호하는 모델
        tools=[toolset], # 툴셋 전달
        # ... 기타 에이전트 설정 ...
    )
    ```

4.  **에이전트에게 지시**: 에이전트의 지침을 업데이트하여 새로운 API 기능과 사용할 수 있는 도구 이름(예: `list_pets`, `create_pet`)을 알려줍니다. 사양에서 생성된 도구 설명도 LLM에게 도움이 됩니다.
5.  **에이전트 실행**: `Runner`를 사용하여 에이전트를 실행합니다. LLM이 API 중 하나를 호출해야 한다고 판단하면, 적절한 `RestApiTool`을 대상으로 하는 함수 호출을 생성하고, 해당 도구가 자동으로 HTTP 요청을 처리합니다.

## 예제

이 예제는 간단한 펫 스토어 OpenAPI 사양(모의 응답을 위해 `httpbin.org` 사용)에서 도구를 생성하고 에이전트를 통해 상호작용하는 방법을 보여줍니다.

???+ "코드: 펫 스토어 API"

    ```python title="openapi_example.py"
    --8<-- "examples/python/snippets/tools/openapi_tool.py"
    ```


## 고급 구성

!!! note
    이 섹션의 매개변수는 ADK Python v2.0.0 이상이 필요합니다.

### `header_provider`를 사용한 커스텀 헤더

모든 API 요청에 커스텀 헤더를 동적으로 추가하려면 `header_provider`에 호출 가능한 객체(callable)를 제공하세요. 다음 예제와 같이 callable은 `ReadonlyContext`를 전달받아 헤더 딕셔너리를 반환합니다.

```python
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import OpenAPIToolset

openapi_spec = {...}  # OpenAPI 파일에서 로드됨.


def my_header_provider(context: ReadonlyContext) -> dict[str, str]:
    return {"X-Request-ID": context.invocation_id}


toolset = OpenAPIToolset(
    spec_dict=openapi_spec,
    header_provider=my_header_provider,
)
```

### `ssl_verify`를 사용한 SSL 인증서 검증

도구 세트의 모든 도구에 대한 SSL 인증서 검증을 구성하려면 `ssl_verify` 매개변수를 사용하세요. 다음 예제는 커스텀 CA 인증서가 있는 환경에서 SSL 검증을 구성하는 방법을 보여줍니다.

```python
from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import OpenAPIToolset

openapi_spec = {...}  # OpenAPI 파일에서 로드됨.

toolset = OpenAPIToolset(
    spec_dict=openapi_spec,
    ssl_verify="/path/to/ca.pem",
)
```

!!! warning "검증을 비활성화하지 마세요"
    `ssl_verify`는 `True`, `False` 또는 `ssl.SSLContext`도 허용합니다. `ssl_verify=False`로 설정하면 인증서 검증이 완전히 비활성화되어 요청이 가로채기(인터셉트) 위험에 노출됩니다. 대신 CA 번들 경로 또는 커스텀 `SSLContext`를 사용하세요.

### `tool_name_prefix`를 사용한 도구 이름 접두사

도구 세트에서 생성된 모든 도구 이름에 접두사를 추가하려면 `tool_name_prefix` 매개변수를 사용하세요. 다음 예제는 여러 OpenAPI 사양을 사용할 때 이름 충돌을 방지하는 방법을 보여줍니다.

```python
from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import OpenAPIToolset

openapi_spec = {...}  # OpenAPI 파일에서 로드됨.

toolset = OpenAPIToolset(
    spec_dict=openapi_spec,
    tool_name_prefix="my_api",
)
```
