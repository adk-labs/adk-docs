---
catalog_title: Vertex AI express mode
catalog_description: Try development with Vertex AI services at no cost
catalog_icon: /adk-docs/integrations/assets/vertex-ai.png
catalog_tags: ["google"]
---
# Vertex AI 익스프레스 모드: Vertex AI 세션 및 메모리 사용하기

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

`VertexAiSessionService` 또는 `VertexAiMemoryBankService` 사용에 관심이 있지만 Google Cloud 프로젝트가 없는 경우, Vertex AI 익스프레스 모드에 가입하여 무료로 액세스 권한을 얻고 이러한 서비스를 사용해 볼 수 있습니다! 자격 요건을 충족하는 ***gmail*** 계정으로 [여기](https://console.cloud.google.com/expressmode)에서 가입할 수 있습니다. Vertex AI 익스프레스 모드에 대한 자세한 내용은 [개요 페이지](https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview)를 참조하세요.
가입 후 [API 키](https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview#api-keys)를 발급받으면, 로컬 ADK 에이전트에서 Vertex AI 세션 및 메모리 서비스를 바로 사용할 수 있습니다!

!!! info Vertex AI 익스프레스 모드 제한 사항

    Vertex AI 익스프레스 모드는 무료 등급에 몇 가지 제한 사항이 있습니다. 무료 익스프레스 모드 프로젝트는 90일 동안만 유효하며, 제한된 할당량으로 일부 서비스만 사용할 수 있습니다. 예를 들어, 에이전트 엔진(Agent Engine)의 수는 10개로 제한되며 에이전트 엔진 배포는 유료 등급에서만 가능합니다. 할당량 제한을 해제하고 모든 Vertex AI 서비스를 사용하려면 익스프레스 모드 프로젝트에 결제 계정을 추가하세요.

## 에이전트 엔진 생성하기

`Session` 객체는 `AgentEngine`의 하위 요소입니다. Vertex AI 익스프레스 모드를 사용할 때, 모든 `Session` 및 `Memory` 객체를 관리하기 위한 부모로서 빈 `AgentEngine`을 생성할 수 있습니다.
먼저, 환경 변수가 올바르게 설정되었는지 확인하세요. 예를 들어, Python 환경에서는 다음과 같이 설정합니다:

```env title="agent/.env"
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_API_KEY=여기에_실제_익스프레스_모드_API_키를_붙여넣으세요
```

다음으로, 에이전트 엔진 인스턴스를 생성할 수 있습니다. Vertex AI SDK를 사용하면 됩니다.

=== "Vertex AI SDK"

    1. Vertex AI SDK를 가져옵니다(import).

        ```py
        import vertexai
        from vertexai import agent_engines
        ```

    2. API 키로 Vertex AI 클라이언트를 초기화하고 에이전트 엔진 인스턴스를 생성합니다.
        
        ```py
        # Gen AI SDK로 에이전트 엔진 생성
        client = vertexai.Client(
          api_key="YOUR_API_KEY",
        )

        agent_engine = client.agent_engines.create(
          config={
            "display_name": "데모 에이전트 엔진",
            "description": "세션 및 메모리용 에이전트 엔진",
          })
        ```

    3. `YOUR_AGENT_ENGINE_DISPLAY_NAME`과 `YOUR_AGENT_ENGINE_DESCRIPTION`을 사용 사례에 맞게 바꾸세요.
    4. 응답에서 에이전트 엔진의 이름과 ID를 가져와 메모리 및 세션과 함께 사용합니다.

        ```py
        APP_ID = agent_engine.api_resource.name.split('/')[-1]
        ```

## `VertexAiSessionService`로 세션 관리하기

[`VertexAiSessionService`](session.md###sessionservice-implementations)는 Vertex AI 익스프레스 모드 API 키와 호환됩니다. 우리는 프로젝트나 위치 정보 없이 세션 객체를 초기화할 수 있습니다.

```py
# 필요: pip install google-adk[vertexai]
# 추가 환경 변수 설정:
# GOOGLE_GENAI_USE_VERTEXAI=TRUE
# GOOGLE_API_KEY=여기에_실제_익스프레스_모드_API_키를_붙여넣으세요
from google.adk.sessions import VertexAiSessionService

# 이 서비스에 사용되는 app_name은 Reasoning Engine ID 또는 이름이어야 합니다.
APP_ID = "your-reasoning-engine-id"

# Vertex 익스프레스 모드로 초기화할 때는 프로젝트와 위치 정보가 필요하지 않습니다.
session_service = VertexAiSessionService(agent_engine_id=APP_ID)
# 서비스 메서드를 호출할 때 REASONING_ENGINE_APP_ID를 사용하세요. 예:
# session = await session_service.create_session(app_name=APP_ID, user_id= ...)
```

!!! info 세션 서비스 할당량

    무료 익스프레스 모드 프로젝트의 경우, `VertexAiSessionService`는 다음과 같은 할당량을 가집니다:

    - 분당 10회: Vertex AI 에이전트 엔진 세션 생성, 삭제 또는 업데이트
    - 분당 30회: Vertex AI 에이전트 엔진 세션에 이벤트 추가

## `VertexAiMemoryBankService`로 메모리 관리하기

[`VertexAiMemoryBankService`](memory.md###memoryservice-implementations)는 Vertex AI 익스프레스 모드 API 키와 호환됩니다. 우리는 프로젝트나 위치 정보 없이 메모리 객체를 초기화할 수 있습니다.

```py
# 필요: pip install google-adk[vertexai]
# 추가 환경 변수 설정:
# GOOGLE_GENAI_USE_VERTEXAI=TRUE
# GOOGLE_API_KEY=여기에_실제_익스프레스_모드_API_키를_붙여넣으세요
from google.adk.memory import VertexAiMemoryBankService

# 이 서비스에 사용되는 app_name은 Reasoning Engine ID 또는 이름이어야 합니다.
APP_ID = "your-reasoning-engine-id"

# Vertex 익스프레스 모드로 초기화할 때는 프로젝트와 위치 정보가 필요하지 않습니다.
memory_service = VertexAiMemoryBankService(agent_engine_id=APP_ID)
# 해당 세션에서 메모리를 생성하여 에이전트가 사용자에 대한 관련 세부 정보를 기억할 수 있도록 합니다.
# memory = await memory_service.add_session_to_memory(session)
```

!!! info 메모리 서비스 할당량

    무료 익스프레스 모드 프로젝트의 경우, `VertexAiMemoryBankService`는 다음과 같은 할당량을 가집니다:

    - 분당 10회: Vertex AI 에이전트 엔진 메모리 리소스 생성, 삭제 또는 업데이트
    - 분당 10회: Vertex AI 에이전트 엔진 메모리 뱅크에서 가져오기, 목록 조회 또는 검색

## 코드 샘플: Vertex AI 익스프레스 모드를 사용한 세션 및 메모리 기능이 있는 날씨 에이전트

이 샘플에서는 `VertexAiSessionService`와 `VertexAiMemoryBankService`를 모두 활용하여 컨텍스트를 관리하는 날씨 에이전트를 만듭니다. 이를 통해 에이전트는 사용자의 선호도와 대화 내용을 기억할 수 있습니다!

**[Vertex AI 익스프레스 모드를 사용한 세션 및 메모리 기능이 있는 날씨 에이전트](https://github.com/google/adk-docs/blob/main/examples/python/notebooks/express-mode-weather-agent.ipynb)**
