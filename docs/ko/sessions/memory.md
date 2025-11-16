# 메모리: `MemoryService`를 사용한 장기 지식

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

`Session`이 *단일, 진행 중인 대화*에 대한 기록(`events`) 및 임시 데이터(`state`)를 추적하는 방법을 살펴보았습니다. 하지만 에이전트가 *과거* 대화의 정보를 기억해야 하는 경우는 어떻게 해야 할까요? 이것이 바로 **장기 지식**과 **`MemoryService`**의 개념이 필요한 부분입니다.

다음과 같이 생각할 수 있습니다.

* **`Session` / `State`:** 특정 채팅 중 단기 기억과 같습니다.
* **장기 지식(`MemoryService`)**: 에이전트가 참조할 수 있는 검색 가능한 아카이브 또는 지식 라이브러리와 같으며, 잠재적으로 많은 과거 채팅 또는 기타 소스의 정보를 포함합니다.

## `MemoryService` 역할

`BaseMemoryService`는 이 검색 가능한 장기 지식 저장소를 관리하기 위한 인터페이스를 정의합니다. 주요 책임은 다음과 같습니다.

1. **정보 수집(`add_session_to_memory`):** (일반적으로 완료된) `Session`의 내용을 가져와 관련 정보를 장기 지식 저장소에 추가합니다.
2. **정보 검색(`search_memory`):** 에이전트(`Tool`을 통해 일반적으로)가 지식 저장소를 쿼리하고 검색 쿼리를 기반으로 관련 스니펫 또는 컨텍스트를 검색할 수 있도록 합니다.

## 올바른 메모리 서비스 선택

ADK는 각각 다른 사용 사례에 맞게 조정된 두 가지 고유한 `MemoryService` 구현을 제공합니다. 아래 표를 사용하여 에이전트에 가장 적합한 것을 결정하십시오.

| **기능** | **InMemoryMemoryService** | **VertexAiMemoryBankService** |
| :--- | :--- | :--- |
| **지속성** | 없음(다시 시작하면 데이터가 손실됨) | 예(Vertex AI에서 관리) |
| **주요 사용 사례** | 프로토타이핑, 로컬 개발 및 간단한 테스트. | 사용자 대화에서 의미 있는 진화하는 기억을 구축합니다. |
| **메모리 추출** | 전체 대화 저장 | 대화에서 [의미 있는 정보](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/generate-memories)를 추출하고 기존 기억과 통합합니다(LLM 기반). |
| **검색 기능** | 기본 키워드 일치. | 고급 의미 검색. |
| **설정 복잡성** | 없음. 기본값입니다. | 낮음. Vertex AI의 [에이전트 엔진](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/overview) 인스턴스가 필요합니다. |
| **종속성** | 없음. | Google Cloud 프로젝트, Vertex AI API |
| **사용 시기** | 프로토타이핑을 위해 여러 세션의 채팅 기록을 검색하려는 경우. | 에이전트가 과거 상호 작용에서 기억하고 배우기를 원하는 경우. |

## 인메모리 메모리

`InMemoryMemoryService`는 애플리케이션의 메모리에 세션 정보를 저장하고 검색을 위해 기본 키워드 일치를 수행합니다. 설정이 필요 없으며 지속성이 필요하지 않은 프로토타이핑 및 간단한 테스트 시나리오에 가장 적합합니다.

=== "Python"

    ```py
    from google.adk.memory import InMemoryMemoryService
    memory_service = InMemoryMemoryService()
    ```

=== "Go"
    ```go
    import (
      "google.golang.org/adk/memory"
      "google.golang.org/adk/session"
    )

    // 상태와 메모리를 공유하려면 실행기 간에 서비스를 공유해야 합니다.
    sessionService := session.InMemoryService()
    memoryService := memory.InMemoryService()
    ```


**예: 메모리 추가 및 검색**

이 예는 단순성을 위해 `InMemoryMemoryService`를 사용하는 기본 흐름을 보여줍니다.

=== "Python"

    ```py
    import asyncio
    from google.adk.agents import LlmAgent
    from google.adk.sessions import InMemorySessionService, Session
    from google.adk.memory import InMemoryMemoryService # MemoryService 가져오기
    from google.adk.runners import Runner
    from google.adk.tools import load_memory # 메모리 쿼리 도구
    from google.genai.types import Content, Part

    # --- 상수 ---
    APP_NAME = "memory_example_app"
    USER_ID = "mem_user"
    MODEL = "gemini-1.5-flash" # 유효한 모델 사용

    # --- 에이전트 정의 ---
    # 에이전트 1: 정보 캡처를 위한 간단한 에이전트
    info_capture_agent = LlmAgent(
        model=MODEL,
        name="InfoCaptureAgent",
        instruction="사용자의 진술을 인정합니다.",
    )

    # 에이전트 2: 메모리를 사용할 수 있는 에이전트
    memory_recall_agent = LlmAgent(
        model=MODEL,
        name="MemoryRecallAgent",
        instruction="사용자의 질문에 답합니다. 답변이 과거 대화에 있을 수 있는 경우 'load_memory' 도구를 사용하십시오.",
        tools=[load_memory] # 에이전트에 도구 제공
    )

    # --- 서비스 ---
    # 상태와 메모리를 공유하려면 실행기 간에 서비스를 공유해야 합니다.
    session_service = InMemorySessionService()
    memory_service = InMemoryMemoryService() # 데모용 인메모리 사용

    async def run_scenario():
        # --- 시나리오 ---

        # 1단계: 세션에서 일부 정보 캡처
        print("--- 1단계: 정보 캡처 ---")
        runner1 = Runner(
            # 정보 캡처 에이전트로 시작
            agent=info_capture_agent,
            app_name=APP_NAME,
            session_service=session_service,
            memory_service=memory_service # 실행기에 메모리 서비스 제공
        )
        session1_id = "session_info"
        await runner1.session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=session1_id)
        user_input1 = Content(parts=[Part(text="제가 가장 좋아하는 프로젝트는 알파 프로젝트입니다.")], role="user")

        # 에이전트 실행
        final_response_text = "(최종 응답 없음)"
        async for event in runner1.run_async(user_id=USER_ID, session_id=session1_id, new_message=user_input1):
            if event.is_final_response() and event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
        print(f"에이전트 1 응답: {final_response_text}")

        # 완료된 세션 가져오기
        completed_session1 = await runner1.session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=session1_id)

        # 이 세션의 내용을 메모리 서비스에 추가
        print("\n--- 세션 1을 메모리에 추가 ---")
        await memory_service.add_session_to_memory(completed_session1)
        print("세션이 메모리에 추가되었습니다.")

        # 2단계: 새 세션에서 정보 회상
        print("\n--- 2단계: 정보 회상 ---")
        runner2 = Runner(
            # 메모리 도구가 있는 두 번째 에이전트 사용
            agent=memory_recall_agent,
            app_name=APP_NAME,
            session_service=session_service, # 동일한 서비스 재사용
            memory_service=memory_service   # 동일한 서비스 재사용
        )
        session2_id = "session_recall"
        await runner2.session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=session2_id)
        user_input2 = Content(parts=[Part(text="제가 가장 좋아하는 프로젝트는 무엇입니까?")], role="user")

        # 두 번째 에이전트 실행
        final_response_text_2 = "(최종 응답 없음)"
        async for event in runner2.run_async(user_id=USER_ID, session_id=session2_id, new_message=user_input2):
            if event.is_final_response() and event.content and event.content.parts:
                final_response_text_2 = event.content.parts[0].text
        print(f"에이전트 2 응답: {final_response_text_2}")

    # 이 예제를 실행하려면 다음 스니펫을 사용할 수 있습니다.
    # asyncio.run(run_scenario())

    # await run_scenario()
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/sessions/memory_example/memory_example.go:full_example"
    ```


### 도구 내에서 메모리 검색

`tool.Context`를 사용하여 사용자 지정 도구 내에서 메모리를 검색할 수도 있습니다.

=== "Go"

    ```go
    --8<-- "examples/go/snippets/sessions/memory_example/memory_example.go:tool_search"
    ```

## Vertex AI 메모리 뱅크

`VertexAiMemoryBankService`는 에이전트를 [Vertex AI 메모리 뱅크](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/overview)에 연결합니다. Vertex AI 메모리 뱅크는 대화형 에이전트를 위한 정교하고 지속적인 메모리 기능을 제공하는 완전 관리형 Google Cloud 서비스입니다.

### 작동 방식

이 서비스는 두 가지 주요 작업을 처리합니다.

*   **메모리 생성:** 대화가 끝나면 세션의 이벤트를 메모리 뱅크로 보낼 수 있으며, 메모리 뱅크는 정보를 지능적으로 처리하고 "메모리"로 저장합니다.
*   **메모리 검색:** 에이전트 코드는 메모리 뱅크에 대해 검색 쿼리를 실행하여 과거 대화에서 관련 메모리를 검색할 수 있습니다.

### 전제 조건

이 기능을 사용하려면 다음이 있어야 합니다.

1.  **Google Cloud 프로젝트:** Vertex AI API가 활성화되어 있습니다.
2.  **에이전트 엔진:** Vertex AI에서 에이전트 엔진을 만들어야 합니다. 메모리 뱅크를 사용하기 위해 에이전트를 에이전트 엔진 런타임에 배포할 필요는 없습니다. 이렇게 하면 구성에 필요한 **에이전트 엔진 ID**가 제공됩니다.
3.  **인증:** 로컬 환경이 Google Cloud 서비스에 액세스하도록 인증되었는지 확인합니다. 가장 간단한 방법은 다음을 실행하는 것입니다.
    ```bash
    gcloud auth application-default login
    ```
4.  **환경 변수:** 이 서비스에는 Google Cloud 프로젝트 ID와 위치가 필요합니다. 환경 변수로 설정하십시오.
    ```bash
    export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
    export GOOGLE_CLOUD_LOCATION="your-gcp-location"
    ```

### 구성

에이전트를 메모리 뱅크에 연결하려면 ADK 서버(`adk web` 또는 `adk api_server`)를 시작할 때 `--memory_service_uri` 플래그를 사용합니다. URI는 `agentengine://<agent_engine_id>` 형식이어야 합니다.

```bash title="bash"
adk web path/to/your/agents_dir --memory_service_uri="agentengine://1234567890"
```

또는 `VertexAiMemoryBankService`를 수동으로 인스턴스화하고 `Runner`에 전달하여 메모리 뱅크를 사용하도록 에이전트를 구성할 수 있습니다.

=== "Python"
  ```py
  from google.adk.memory import VertexAiMemoryBankService

  agent_engine_id = agent_engine.api_resource.name.split("/")[-1]

  memory_service = VertexAiMemoryBankService(
      project="PROJECT_ID",
      location="LOCATION",
      agent_engine_id=agent_engine_id
  )

  runner = adk.Runner(
      ...
      memory_service=memory_service
  )
  ```

## 에이전트에서 메모리 사용

메모리 서비스가 구성되면 에이전트는 도구 또는 콜백을 사용하여 메모리를 검색할 수 있습니다. ADK에는 메모리 검색을 위한 두 가지 기본 제공 도구가 포함되어 있습니다.

* `PreloadMemory`: 각 턴이 시작될 때 항상 메모리를 검색합니다(콜백과 유사).
* `LoadMemory`: 에이전트가 도움이 될 것이라고 판단할 때 메모리를 검색합니다.

**예:**

=== "Python"
```python
from google.adk.agents import Agent
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

agent = Agent(
    model=MODEL_ID,
    name='weather_sentiment_agent',
    instruction="...",
    tools=[PreloadMemoryTool()]
)
```

세션에서 메모리를 추출하려면 `add_session_to_memory`를 호출해야 합니다. 예를 들어 콜백을 통해 이를 자동화할 수 있습니다.

=== "Python"
```python
from google import adk

async def auto_save_session_to_memory_callback(callback_context):
    await callback_context._invocation_context.memory_service.add_session_to_memory(
        callback_context._invocation_context.session)

agent = Agent(
    model=MODEL,
    name="Generic_QA_Agent",
    instruction="사용자의 질문에 답합니다.",
    tools=[adk.tools.preload_memory_tool.PreloadMemoryTool()],
    after_agent_callback=auto_save_session_to_memory_callback,
)
```

## 고급 개념

### 메모리 작동 방식

메모리 워크플로는 내부적으로 다음 단계를 포함합니다.

1. **세션 상호 작용:** 사용자는 `SessionService`에서 관리하는 `Session`을 통해 에이전트와 상호 작용합니다. 이벤트가 추가되고 상태가 업데이트될 수 있습니다.
2. **메모리에 수집:** 특정 시점(종종 세션이 완료되었거나 중요한 정보를 생성한 경우)에 애플리케이션은 `memory_service.add_session_to_memory(session)`을 호출합니다. 이렇게 하면 세션의 이벤트에서 관련 정보를 추출하여 장기 지식 저장소(인메모리 사전 또는 에이전트 엔진 메모리 뱅크)에 추가합니다.
3. **나중에 쿼리:** *다른*(또는 동일한) 세션에서 사용자는 과거 컨텍스트가 필요한 질문을 할 수 있습니다(예: "지난주에 X 프로젝트에 대해 무엇을 논의했습니까?").
4. **에이전트가 메모리 도구 사용:** 메모리 검색 도구(기본 제공 `load_memory` 도구 등)가 장착된 에이전트는 과거 컨텍스트의 필요성을 인식합니다. 도구를 호출하여 검색 쿼리(예: "지난주 X 프로젝트 논의")를 제공합니다.
5. **검색 실행:** 도구는 내부적으로 `memory_service.search_memory(app_name, user_id, query)`를 호출합니다.
6. **결과 반환:** `MemoryService`는 저장소(키워드 일치 또는 의미 검색 사용)를 검색하고 관련 스니펫을 `MemoryResult` 객체 목록을 포함하는 `SearchMemoryResponse`로 반환합니다(각각 관련 과거 세션의 이벤트를 잠재적으로 보유).
7. **에이전트가 결과 사용:** 도구는 이러한 결과를 에이전트에 반환하며, 일반적으로 컨텍스트 또는 함수 응답의 일부입니다. 그런 다음 에이전트는 이 검색된 정보를 사용하여 사용자에 대한 최종 답변을 공식화할 수 있습니다.

### 에이전트가 둘 이상의 메모리 서비스에 액세스할 수 있습니까?

*   **표준 구성을 통해: 아니요.** 프레임워크(`adk web`, `adk api_server`)는 `--memory_service_uri` 플래그를 통해 한 번에 하나의 메모리 서비스로 구성되도록 설계되었습니다. 이 단일 서비스는 에이전트에 제공되고 기본 제공 `self.search_memory()` 메서드를 통해 액세스됩니다. 구성 관점에서 해당 프로세스에서 제공하는 모든 에이전트에 대해 하나의 백엔드(`InMemory`, `VertexAiMemoryBankService`)만 선택할 수 있습니다.

*   **에이전트 코드 내에서: 예, 물론입니다.** 에이전트 코드 내에서 다른 메모리 서비스를 수동으로 가져오고 인스턴스화하는 것을 막는 것은 없습니다. 이를 통해 단일 에이전트 턴 내에서 여러 메모리 소스에 액세스할 수 있습니다.

예를 들어 에이전트는 프레임워크에서 구성한 `InMemoryMemoryService`를 사용하여 대화 기록을 회상하고 `VertexAiMemoryBankService`를 수동으로 인스턴스화하여 기술 설명서에서 정보를 조회할 수 있습니다.

#### 예: 두 개의 메모리 서비스 사용

다음은 에이전트 코드에서 이를 구현하는 방법입니다.

=== "Python"
```python
from google.adk.agents import Agent
from google.adk.memory import InMemoryMemoryService, VertexAiMemoryBankService
from google.genai import types

class MultiMemoryAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.memory_service = InMemoryMemoryService()
        # 문서 조회를 위해 두 번째 메모리 서비스를 수동으로 인스턴스화합니다.
        self.vertexai_memorybank_service = VertexAiMemoryBankService(
            project="PROJECT_ID",
            location="LOCATION",
            agent_engine_id="AGENT_ENGINE_ID"
        )

    async def run(self, request: types.Content, **kwargs) -> types.Content:
        user_query = request.parts[0].text

        # 1. 프레임워크에서 제공하는 메모리를 사용하여 대화 기록 검색
        #    (구성된 경우 InMemoryMemoryService가 됩니다)
        conversation_context = await self.memory_service.search_memory(query=user_query)

        # 2. 수동으로 만든 서비스를 사용하여 문서 지식 기반 검색
        document_context = await self.vertexai_memorybank_service.search_memory(query=user_query)

        # 두 소스의 컨텍스트를 결합하여 더 나은 응답 생성
        prompt = "과거 대화에서 기억나는 것은 다음과 같습니다.\n"
        prompt += f"{conversation_context.memories}\n\n"
        prompt += "기술 설명서에서 찾은 내용은 다음과 같습니다.\n"
        prompt += f"{document_context.memories}\n\n"
        prompt += f"이 모든 것을 바탕으로 '{user_query}'에 대한 제 답변은 다음과 같습니다."

        return await self.llm.generate_content_async(prompt)
```
