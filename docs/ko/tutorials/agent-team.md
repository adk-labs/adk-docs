# ADK로 첫 번째 지능형 에이전트 팀 구축하기: 점진적 날씨 봇

<!-- Optional outer container for overall padding/spacing -->
<div style="padding: 10px 0;">

  <!-- Line 1: Open in Colab -->
  <!-- This div ensures the link takes up its own line and adds space below -->
  <div style="margin-bottom: 10px;">
    <a href="https://colab.research.google.com/github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb" target="_blank" style="display: inline-flex; align-items: center; gap: 5px; text-decoration: none; color: #4285F4;">
      <img width="32px" src="https://www.gstatic.com/pantheon/images/bigquery/welcome_page/colab-logo.svg" alt="Google Colaboratory logo">
      <span>Colab에서 열기</span>
    </a>
  </div>

  <!-- Line 2: Share Links -->
  <!-- This div acts as a flex container for the "Share to" text and icons -->
  <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
    <!-- Share Text -->
    <span style="font-weight: bold;">공유하기:</span>

    <!-- Social Media Links -->
    <a href="https://www.linkedin.com/sharing/share-offsite/?url=https%3A//github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb" target="_blank" title="Share on LinkedIn">
      <img width="20px" src="https://upload.wikimedia.org/wikipedia/commons/8/81/LinkedIn_icon.svg" alt="LinkedIn logo" style="vertical-align: middle;">
    </a>
    <a href="https://bsky.app/intent/compose?text=https%3A//github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb" target="_blank" title="Share on Bluesky">
      <img width="20px" src="https://upload.wikimedia.org/wikipedia/commons/7/7a/Bluesky_Logo.svg" alt="Bluesky logo" style="vertical-align: middle;">
    </a>
    <a href="https://twitter.com/intent/tweet?url=https%3A//github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb" target="_blank" title="Share on X (Twitter)">
      <img width="20px" src="https://upload.wikimedia.org/wikipedia/commons/5/5a/X_icon_2.svg" alt="X logo" style="vertical-align: middle;">
    </a>
    <a href="https://reddit.com/submit?url=https%3A//github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb" target="_blank" title="Share on Reddit">
      <img width="20px" src="https://redditinc.com/hubfs/Reddit%20Inc/Brand/Reddit_Logo.png" alt="Reddit logo" style="vertical-align: middle;">
    </a>
    <a href="https://www.facebook.com/sharer/sharer.php?u=https%3A//github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb" target="_blank" title="Share on Facebook">
      <img width="20px" src="https://upload.wikimedia.org/wikipedia/commons/5/51/Facebook_f_logo_%282019%29.svg" alt="Facebook logo" style="vertical-align: middle;">
    </a>
  </div>

</div>

이 튜토리얼은 [Agent Development Kit](https://google.github.io/adk-docs/get-started/)를 위한 [빠른 시작 예제(Quickstart example)](https://google.github.io/adk-docs/get-started/quickstart/)에서 확장된 내용입니다. 이제 더 깊이 파고들어 더욱 정교한 **다중 에이전트 시스템(multi-agent system)**을 구축할 준비가 되었습니다.

우리는 단순한 기초 위에 고급 기능을 점진적으로 쌓아 올리며 **날씨 봇 에이전트 팀**을 구축하는 여정을 시작할 것입니다. 날씨를 조회할 수 있는 단일 에이전트로 시작하여 다음과 같은 기능들을 점차 추가할 것입니다:

*   다양한 AI 모델 활용 (Gemini, GPT, Claude).
*   별도의 작업(인사 및 작별 인사 등)을 위한 전문 하위 에이전트 설계.
*   에이전트 간의 지능적인 위임(delegation) 활성화.
*   영구 세션 상태(session state)를 사용하여 에이전트에게 기억력 부여.
*   콜백(callbacks)을 사용하여 중요한 안전 가드레일 구현.

**왜 날씨 봇 팀인가요?**

이 사용 사례는 겉보기에는 단순해 보이지만, 복잡한 실제 에이전트 기반 애플리케이션을 구축하는 데 필수적인 ADK 핵심 개념을 탐구하기 위한 실용적이고 친숙한 캔버스를 제공합니다. 상호 작용을 구조화하고, 상태를 관리하고, 안전을 보장하며, 여러 AI "두뇌"가 함께 작동하도록 조정하는 방법을 배우게 될 것입니다.

**ADK란 무엇이었죠?**

다시 상기하자면, ADK는 대규모 언어 모델(LLM)로 구동되는 애플리케이션 개발을 간소화하기 위해 설계된 Python 프레임워크입니다. 추론하고, 계획을 세우고, 도구를 활용하고, 사용자와 동적으로 상호 작용하며, 팀 내에서 효과적으로 협업할 수 있는 에이전트를 만들기 위한 강력한 구성 요소를 제공합니다.

**이 고급 튜토리얼에서 마스터할 내용:**

*   ✅ **도구(Tool) 정의 및 사용:** 에이전트에게 특정 능력(데이터 가져오기 등)을 부여하는 Python 함수(`tools`)를 만들고, 에이전트에게 이를 효과적으로 사용하는 방법을 지시합니다.
*   ✅ **다중 LLM 유연성:** LiteLLM 통합을 통해 다양한 최신 LLM(Gemini, GPT-4o, Claude Sonnet)을 활용하도록 에이전트를 구성하여 각 작업에 가장 적합한 모델을 선택할 수 있게 합니다.
*   ✅ **에이전트 위임 및 협업:** 전문 하위 에이전트를 설계하고 팀 내에서 가장 적절한 에이전트에게 사용자 요청을 자동으로 라우팅(`auto flow`)하도록 활성화합니다.
*   ✅ **기억을 위한 세션 상태:** `Session State`와 `ToolContext`를 활용하여 에이전트가 대화 턴(turn) 간에 정보를 기억하게 하여 더 맥락 있는 상호 작용을 이끌어냅니다.
*   ✅ **콜백을 이용한 안전 가드레일:** `before_model_callback` 및 `before_tool_callback`을 구현하여 사전 정의된 규칙에 따라 요청/도구 사용을 검사, 수정 또는 차단함으로써 애플리케이션의 안전성과 제어력을 향상시킵니다.

**최종 상태 기대치:**

이 튜토리얼을 완료하면 기능적인 다중 에이전트 날씨 봇 시스템을 구축하게 됩니다. 이 시스템은 날씨 정보를 제공할 뿐만 아니라 대화의 뉘앙스를 처리하고, 마지막으로 확인한 도시를 기억하며, 정의된 안전 경계 내에서 작동하며, 이 모든 것이 ADK를 사용하여 조정됩니다.

**사전 요구 사항:**

*   ✅ **Python 프로그래밍에 대한 확실한 이해.**
*   ✅ **대규모 언어 모델(LLM), API 및 에이전트 개념에 대한 친숙함.**
*   ❗ **중요: ADK 빠른 시작(Quickstart) 튜토리얼 완료 또는 이에 상응하는 ADK 기초 지식(Agent, Runner, SessionService, 기본 Tool 사용법) 보유.** 이 튜토리얼은 해당 개념들을 직접적인 기반으로 합니다.
*   ✅ 사용하려는 LLM에 대한 **API 키** (예: Gemini용 Google AI Studio, OpenAI Platform, Anthropic Console).

---

**실행 환경에 대한 참고 사항:**

이 튜토리얼은 Google Colab, Colab Enterprise 또는 Jupyter 노트북과 같은 대화형 노트북 환경에 맞춰 구성되어 있습니다. 다음 사항을 유념해 주세요:

*   **비동기(Async) 코드 실행:** 노트북 환경은 비동기 코드를 다르게 처리합니다. `await`를 사용하는 예제(이벤트 루프가 이미 실행 중인 경우에 적합, 노트북에서 일반적) 또는 `asyncio.run()`을 사용하는 예제(독립 실행형 `.py` 스크립트나 특정 노트북 설정에서 자주 필요)를 보게 될 것입니다. 코드 블록은 두 가지 시나리오 모두에 대한 가이드를 제공합니다.
*   **수동 Runner/Session 설정:** 단계에는 `Runner` 및 `SessionService` 인스턴스를 명시적으로 생성하는 과정이 포함됩니다. 이 방식은 에이전트의 실행 수명 주기, 세션 관리 및 상태 지속성에 대한 세밀한 제어 권한을 제공하기 때문에 여기서 보여집니다.

**대안: ADK 내장 도구 사용 (Web UI / CLI / API Server)**

ADK의 표준 도구를 사용하여 러너 및 세션 관리를 자동으로 처리하는 설정을 선호하는 경우, [여기](https://github.com/google/adk-docs/tree/main/examples/python/tutorial/agent_team/adk-tutorial)에서 해당 목적에 맞게 구성된 코드를 찾을 수 있습니다. 해당 버전은 `adk web`(웹 UI용), `adk run`(CLI 상호 작용용) 또는 `adk api_server`(API 노출용)와 같은 명령어로 직접 실행되도록 설계되었습니다. 해당 대체 리소스에 제공된 `README.md` 지침을 따르세요.

---

**에이전트 팀을 구축할 준비가 되셨나요? 시작해 봅시다!**

> **참고:** 이 튜토리얼은 adk 버전 1.0.0 이상에서 작동합니다.

```python
# @title 0단계: 설정 및 설치
# 다중 모델 지원을 위해 ADK와 LiteLLM 설치

!pip install google-adk -q
!pip install litellm -q

print("Installation complete.")
```

```python
# @title 필수 라이브러리 가져오기
import os
import asyncio
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm # 다중 모델 지원용
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types # 메시지 Content/Parts 생성용

import warnings
# 모든 경고 무시
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.ERROR)

print("Libraries imported.")
```

```python
# @title API 키 구성 (실제 키로 교체하세요!)

# --- 중요: 플레이스홀더를 실제 API 키로 교체하세요 ---

# Gemini API 키 (Google AI Studio에서 발급: https://aistudio.google.com/app/apikey)
os.environ["GOOGLE_API_KEY"] = "YOUR_GOOGLE_API_KEY" # <--- 교체

# [선택 사항]
# OpenAI API 키 (OpenAI Platform에서 발급: https://platform.openai.com/api-keys)
os.environ['OPENAI_API_KEY'] = 'YOUR_OPENAI_API_KEY' # <--- 교체

# [선택 사항]
# Anthropic API 키 (Anthropic Console에서 발급: https://console.anthropic.com/settings/keys)
os.environ['ANTHROPIC_API_KEY'] = 'YOUR_ANTHROPIC_API_KEY' # <--- 교체

# --- 키 확인 (선택적 체크) ---
print("API Keys Set:")
print(f"Google API Key set: {'Yes' if os.environ.get('GOOGLE_API_KEY') and os.environ['GOOGLE_API_KEY'] != 'YOUR_GOOGLE_API_KEY' else 'No (REPLACE PLACEHOLDER!)'}")
print(f"OpenAI API Key set: {'Yes' if os.environ.get('OPENAI_API_KEY') and os.environ['OPENAI_API_KEY'] != 'YOUR_OPENAI_API_KEY' else 'No (REPLACE PLACEHOLDER!)'}")
print(f"Anthropic API Key set: {'Yes' if os.environ.get('ANTHROPIC_API_KEY') and os.environ['ANTHROPIC_API_KEY'] != 'YOUR_ANTHROPIC_API_KEY' else 'No (REPLACE PLACEHOLDER!)'}")

# 이 다중 모델 설정에서는 Vertex AI가 아닌 API 키를 직접 사용하도록 ADK 구성
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"


# @markdown **보안 참고:** 노트북에 API 키를 직접 하드코딩하는 것보다 보안적으로 관리(예: Colab Secrets 또는 환경 변수 사용)하는 것이 모범 사례입니다. 위의 플레이스홀더 문자열을 교체하세요.
```

```python
# --- 쉬운 사용을 위해 모델 상수 정의 ---

# 더 많은 지원 모델은 여기서 참조 가능: https://ai.google.dev/gemini-api/docs/models#model-variations
MODEL_GEMINI_2_5_FLASH = "gemini-2.5-flash"

# 더 많은 지원 모델은 여기서 참조 가능: https://docs.litellm.ai/docs/providers/openai#openai-chat-completion-models
MODEL_GPT_4O = "openai/gpt-4.1" # 시도 가능: gpt-4.1-mini, gpt-4o 등

# 더 많은 지원 모델은 여기서 참조 가능: https://docs.litellm.ai/docs/providers/anthropic
MODEL_CLAUDE_SONNET = "anthropic/claude-sonnet-4-20250514" # 시도 가능: claude-opus-4-20250514 , claude-3-7-sonnet-20250219 등

print("\nEnvironment configured.")
```

---

## 1단계: 첫 번째 에이전트 - 기본 날씨 조회

날씨 봇의 가장 기본적인 구성 요소인 특정 작업(날씨 정보 조회)을 수행할 수 있는 단일 에이전트를 구축하는 것으로 시작하겠습니다. 여기에는 두 가지 핵심 요소가 포함됩니다:

1.  **도구(Tool):** 에이전트에게 날씨 데이터를 가져올 수 있는 *능력*을 부여하는 Python 함수.
2.  **에이전트(Agent):** 사용자의 요청을 이해하고, 날씨 도구가 있음을 알고, 언제 어떻게 사용할지 결정하는 AI "두뇌".

---

**1\. 도구 정의 (`get_weather`)**

ADK에서 **도구(Tools)**는 단순한 텍스트 생성을 넘어 에이전트에게 구체적인 기능을 제공하는 구성 요소입니다. 이는 일반적으로 API 호출, 데이터베이스 쿼리 또는 계산 수행과 같은 특정 작업을 수행하는 일반 Python 함수입니다.

첫 번째 도구는 *모의(mock)* 날씨 보고서를 제공할 것입니다. 이를 통해 아직 외부 API 키 없이 에이전트 구조에 집중할 수 있습니다. 나중에 이 모의 함수를 실제 날씨 서비스를 호출하는 함수로 쉽게 교체할 수 있습니다.

**핵심 개념: 독스트링(Docstrings)은 매우 중요합니다!** 에이전트의 LLM은 다음을 이해하기 위해 함수의 **독스트링**에 크게 의존합니다:

*   도구가 *무엇*을 하는지.
*   *언제* 사용해야 하는지.
*   *어떤 인수*가 필요한지 (`city: str`).
*   *어떤 정보*를 반환하는지.

**모범 사례:** 도구에 명확하고 설명적이며 정확한 독스트링을 작성하세요. 이는 LLM이 도구를 올바르게 사용하는 데 필수적입니다.

```python
# @title get_weather 도구 정의
def get_weather(city: str) -> dict:
    """지정된 도시의 현재 날씨 보고서를 가져옵니다.

    Args:
        city (str): 도시의 이름 (예: "New York", "London", "Tokyo").

    Returns:
        dict: 날씨 정보를 포함하는 딕셔너리.
              'status' 키('success' 또는 'error')를 포함합니다.
              'success'인 경우 날씨 세부 정보가 있는 'report' 키를 포함합니다.
              'error'인 경우 'error_message' 키를 포함합니다.
    """
    print(f"--- Tool: get_weather called for city: {city} ---") # 도구 실행 로그
    city_normalized = city.lower().replace(" ", "") # 기본 정규화

    # 모의 날씨 데이터
    mock_weather_db = {
        "newyork": {"status": "success", "report": "The weather in New York is sunny with a temperature of 25°C."},
        "london": {"status": "success", "report": "It's cloudy in London with a temperature of 15°C."},
        "tokyo": {"status": "success", "report": "Tokyo is experiencing light rain and a temperature of 18°C."},
    }

    if city_normalized in mock_weather_db:
        return mock_weather_db[city_normalized]
    else:
        return {"status": "error", "error_message": f"Sorry, I don't have weather information for '{city}'."}

# 도구 사용 예시 (선택적 테스트)
print(get_weather("New York"))
print(get_weather("Paris"))
```

---

**2\. 에이전트 정의 (`weather_agent`)**

이제 **에이전트** 자체를 만들어 봅시다. ADK의 `Agent`는 사용자, LLM, 사용 가능한 도구 간의 상호 작용을 조정합니다.

몇 가지 주요 매개변수로 구성합니다:

*   `name`: 이 에이전트의 고유 식별자 (예: "weather\_agent\_v1").
*   `model`: 사용할 LLM을 지정합니다 (예: `MODEL_GEMINI_2_5_FLASH`). 특정 Gemini 모델로 시작합니다.
*   `description`: 에이전트의 전반적인 목적에 대한 간결한 요약입니다. 이는 나중에 다른 에이전트가 작업을 *이* 에이전트에게 위임할지 여부를 결정할 때 매우 중요해집니다.
*   `instruction`: 행동 방식, 페르소나, 목표, 그리고 구체적으로 할당된 `tools`를 *어떻게 그리고 언제* 활용해야 하는지에 대한 LLM을 위한 상세 지침입니다.
*   `tools`: 에이전트가 사용할 수 있는 실제 Python 도구 함수 목록 (예: `[get_weather]`).

**모범 사례:** 명확하고 구체적인 `instruction` 프롬프트를 제공하세요. 지침이 상세할수록 LLM이 자신의 역할과 도구를 효과적으로 사용하는 방법을 더 잘 이해할 수 있습니다. 필요한 경우 오류 처리에 대해 명시하십시오.

**모범 사례:** 설명적인 `name`과 `description` 값을 선택하세요. 이는 ADK 내부에서 사용되며 자동 위임(나중에 다룸)과 같은 기능에 필수적입니다.

```python
# @title 날씨 에이전트 정의
# 앞서 정의한 모델 상수 중 하나 사용
AGENT_MODEL = MODEL_GEMINI_2_5_FLASH # Gemini로 시작

weather_agent = Agent(
    name="weather_agent_v1",
    model=AGENT_MODEL, # Gemini용 문자열 또는 LiteLlm 객체 가능
    description="Provides weather information for specific cities.",
    instruction="You are a helpful weather assistant. "
                "When the user asks for the weather in a specific city, "
                "use the 'get_weather' tool to find the information. "
                "If the tool returns an error, inform the user politely. "
                "If the tool is successful, present the weather report clearly.",
    tools=[get_weather], # 함수를 직접 전달
)

print(f"Agent '{weather_agent.name}' created using model '{AGENT_MODEL}'.")
```

---

**3\. Runner 및 세션 서비스 설정**

대화를 관리하고 에이전트를 실행하려면 두 가지 구성 요소가 더 필요합니다:

*   `SessionService`: 다양한 사용자와 세션에 대한 대화 기록 및 상태를 관리하는 역할을 합니다. `InMemorySessionService`는 모든 것을 메모리에 저장하는 간단한 구현으로, 테스트 및 간단한 애플리케이션에 적합합니다. 주고받은 메시지를 추적합니다. 4단계에서 상태 지속성에 대해 더 자세히 살펴보겠습니다.
*   `Runner`: 상호 작용 흐름을 조정하는 엔진입니다. 사용자 입력을 받아 적절한 에이전트에게 라우팅하고, 에이전트의 논리에 따라 LLM 및 도구 호출을 관리하고, `SessionService`를 통해 세션 업데이트를 처리하고, 상호 작용의 진행 상황을 나타내는 이벤트를 생성(yield)합니다.

```python
# @title 세션 서비스 및 Runner 설정

# --- 세션 관리 ---
# 핵심 개념: SessionService는 대화 기록 및 상태를 저장합니다.
# InMemorySessionService는 이 튜토리얼을 위한 간단한 비영구 저장소입니다.
session_service = InMemorySessionService()

# 상호 작용 컨텍스트 식별을 위한 상수 정의
APP_NAME = "weather_tutorial_app"
USER_ID = "user_1"
SESSION_ID = "session_001" # 단순화를 위해 고정 ID 사용

# 대화가 일어날 특정 세션 생성
session = await session_service.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID
)
print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")

# --- 또는 ---

# 표준 Python 스크립트(.py 파일)로 실행하는 경우 다음 줄의 주석을 제거하세요:

# async def init_session(app_name:str,user_id:str,session_id:str) -> InMemorySessionService:
#     session = await session_service.create_session(
#         app_name=app_name,
#         user_id=user_id,
#         session_id=session_id
#     )
#     print(f"Session created: App='{app_name}', User='{user_id}', Session='{session_id}'")
#     return session
# 
# session = asyncio.run(init_session(APP_NAME,USER_ID,SESSION_ID))

# --- Runner ---
# 핵심 개념: Runner는 에이전트 실행 루프를 조정합니다.
runner = Runner(
    agent=weather_agent, # 실행하려는 에이전트
    app_name=APP_NAME,   # 실행을 우리 앱과 연관시킴
    session_service=session_service # 우리의 세션 관리자 사용
)
print(f"Runner created for agent '{runner.agent.name}'.")
```

---

**4\. 에이전트와 상호 작용하기**

에이전트에게 메시지를 보내고 응답을 받을 방법이 필요합니다. LLM 호출 및 도구 실행에는 시간이 걸릴 수 있으므로 ADK의 `Runner`는 비동기적으로 작동합니다.

다음과 같은 `async` 도우미 함수(`call_agent_async`)를 정의합니다:

1.  사용자 쿼리 문자열을 받습니다.
2.  이를 ADK `Content` 형식으로 패키징합니다.
3.  사용자/세션 컨텍스트와 새 메시지를 제공하여 `runner.run_async`를 호출합니다.
4.  러너가 생성(yield)하는 **이벤트(Events)**를 반복합니다. 이벤트는 에이전트 실행 단계(예: 도구 호출 요청됨, 도구 결과 수신됨, 중간 LLM 생각, 최종 응답)를 나타냅니다.
5.  `event.is_final_response()`를 사용하여 **최종 응답** 이벤트를 식별하고 출력합니다.

**왜 `async`인가요?** LLM 및 잠재적인 도구(외부 API 등)와의 상호 작용은 I/O 바운드 작업입니다. `asyncio`를 사용하면 프로그램이 실행을 차단하지 않고 이러한 작업을 효율적으로 처리할 수 있습니다.

```python
# @title 에이전트 상호 작용 함수 정의

from google.genai import types # 메시지 Content/Parts 생성용

async def call_agent_async(query: str, runner, user_id, session_id):
  """에이전트에 쿼리를 보내고 최종 응답을 출력합니다."""
  print(f"\n>>> User Query: {query}")

  # ADK 형식으로 사용자 메시지 준비
  content = types.Content(role='user', parts=[types.Part(text=query)])

  final_response_text = "Agent did not produce a final response." # 기본값

  # 핵심 개념: run_async는 에이전트 로직을 실행하고 이벤트를 생성합니다.
  # 이벤트를 반복하여 최종 답변을 찾습니다.
  async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
      # 실행 중 *모든* 이벤트를 보려면 아래 줄의 주석을 제거하세요.
      # print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")

      # 핵심 개념: is_final_response()는 턴의 종료 메시지를 표시합니다.
      if event.is_final_response():
          if event.content and event.content.parts:
             # 첫 번째 파트에 텍스트 응답이 있다고 가정
             final_response_text = event.content.parts[0].text
          elif event.actions and event.actions.escalate: # 잠재적 오류/에스컬레이션 처리
             final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
          # 필요한 경우 여기에 더 많은 확인 추가 (예: 특정 오류 코드)
          break # 최종 응답을 찾으면 이벤트 처리 중단

  print(f"<<< Agent Response: {final_response_text}")
```

---

**5\. 대화 실행**

마지막으로 에이전트에게 몇 가지 쿼리를 보내어 설정을 테스트해 보겠습니다. `async` 호출을 기본 `async` 함수에 래핑하고 `await`를 사용하여 실행합니다.

출력을 확인하세요:

*   사용자 쿼리를 확인합니다.
*   에이전트가 도구를 사용할 때 `--- Tool: get_weather called... ---` 로그를 확인합니다.
*   날씨 데이터를 사용할 수 없는 경우(파리)를 처리하는 방법을 포함하여 에이전트의 최종 응답을 관찰합니다.

```python
# @title 초기 대화 실행

# 상호 작용 도우미를 await하기 위해 비동기 함수가 필요합니다
async def run_conversation():
    await call_agent_async("What is the weather like in London?",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID)

    await call_agent_async("How about Paris?",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID) # 도구의 오류 메시지 예상

    await call_agent_async("Tell me the weather in New York",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID)

# 비동기 컨텍스트(Colab/Jupyter 등)에서 await를 사용하여 대화 실행
await run_conversation()

# --- 또는 ---

# 표준 Python 스크립트(.py 파일)로 실행하는 경우 다음 줄의 주석을 제거하세요:
# import asyncio
# if __name__ == "__main__":
#     try:
#         asyncio.run(run_conversation())
#     except Exception as e:
#         print(f"An error occurred: {e}")
```

---

축하합니다! 첫 번째 ADK 에이전트를 성공적으로 구축하고 상호 작용했습니다. 에이전트는 사용자의 요청을 이해하고, 정보를 찾기 위해 도구를 사용하며, 도구의 결과를 기반으로 적절하게 응답합니다.

다음 단계에서는 이 에이전트를 구동하는 기본 언어 모델을 쉽게 전환하는 방법을 살펴보겠습니다.

## 2단계: LiteLLM으로 다중 모델 지원 [선택 사항]

1단계에서는 특정 Gemini 모델로 구동되는 기능적인 날씨 에이전트를 구축했습니다. 효과적이긴 하지만 실제 애플리케이션은 *다른* 대규모 언어 모델(LLM)을 사용할 수 있는 유연성으로부터 이점을 얻는 경우가 많습니다. 그 이유는 무엇일까요?

*   **성능:** 일부 모델은 특정 작업(예: 코딩, 추론, 창의적 글쓰기)에 탁월합니다.
*   **비용:** 모델마다 가격대가 다릅니다.
*   **기능:** 모델은 다양한 기능, 컨텍스트 창 크기 및 미세 조정 옵션을 제공합니다.
*   **가용성/이중화:** 대안을 마련해 두면 한 공급자에 문제가 발생하더라도 애플리케이션이 기능을 유지할 수 있습니다.

ADK는 [**LiteLLM**](https://github.com/BerriAI/litellm) 라이브러리와의 통합을 통해 모델 간 전환을 원활하게 만듭니다. LiteLLM은 100개 이상의 다양한 LLM에 대한 일관된 인터페이스 역할을 합니다.

**이 단계에서는 다음을 수행합니다:**

1.  `LiteLlm` 래퍼를 사용하여 OpenAI(GPT) 및 Anthropic(Claude)과 같은 공급자의 모델을 사용하도록 ADK `Agent`를 구성하는 방법을 배웁니다.
2.  각각 다른 LLM으로 지원되는 날씨 에이전트 인스턴스를 정의, 구성(자체 세션 및 러너 포함) 및 즉시 테스트합니다.
3.  이러한 서로 다른 에이전트와 상호 작용하여 동일한 기본 도구를 사용하는 경우에도 응답의 잠재적 차이를 관찰합니다.

---

**1\. `LiteLlm` 가져오기**

초기 설정(0단계) 중에 이것을 가져왔지만, 다중 모델 지원의 핵심 구성 요소입니다:

```python
# @title 1. LiteLlm 가져오기
from google.adk.models.lite_llm import LiteLlm
```

**2\. 다중 모델 에이전트 정의 및 테스트**

모델 이름 문자열(기본값은 Google의 Gemini 모델)만 전달하는 대신, 원하는 모델 식별자 문자열을 `LiteLlm` 클래스 내에 래핑합니다.

*   **핵심 개념: `LiteLlm` 래퍼:** `LiteLlm(model="provider/model_name")` 구문은 ADK가 이 에이전트에 대한 요청을 LiteLLM 라이브러리를 통해 지정된 모델 공급자에게 라우팅하도록 지시합니다.

0단계에서 OpenAI 및 Anthropic에 필요한 API 키를 구성했는지 확인하세요. `call_agent_async` 함수(앞서 정의됨, 이제 `runner`, `user_id`, `session_id`를 허용함)를 사용하여 설정 직후 각 에이전트와 상호 작용할 것입니다.

아래의 각 블록은 다음을 수행합니다:

*   특정 LiteLLM 모델(`MODEL_GPT_4O` 또는 `MODEL_CLAUDE_SONNET`)을 사용하여 에이전트를 정의합니다.
*   해당 에이전트의 테스트 실행을 위해 *새롭고 별도의* `InMemorySessionService` 및 세션을 만듭니다. 이는 이 데모를 위해 대화 기록을 격리 상태로 유지합니다.
*   특정 에이전트 및 세션 서비스에 대해 구성된 `Runner`를 만듭니다.
*   즉시 `call_agent_async`를 호출하여 쿼리를 보내고 에이전트를 테스트합니다.

**모범 사례:** 오타를 방지하고 코드를 관리하기 쉽게 만들기 위해 모델 이름에 상수(0단계에서 정의된 `MODEL_GPT_4O`, `MODEL_CLAUDE_SONNET` 등)를 사용하세요.

**오류 처리:** 에이전트 정의를 `try...except` 블록으로 감쌉니다. 이렇게 하면 특정 공급자의 API 키가 누락되거나 유효하지 않은 경우에도 전체 코드 셀이 실패하는 것을 방지하고, *구성된* 모델로 튜토리얼을 진행할 수 있습니다.

먼저 OpenAI의 GPT-4o를 사용하는 에이전트를 만들고 테스트해 봅시다.

```python
# @title GPT 에이전트 정의 및 테스트

# 1단계의 'get_weather' 함수가 환경에 정의되어 있는지 확인하세요.
# 앞서 정의한 'call_agent_async'가 있는지 확인하세요.

# --- GPT-4o를 사용하는 에이전트 ---
weather_agent_gpt = None # None으로 초기화
runner_gpt = None      # runner를 None으로 초기화

try:
    weather_agent_gpt = Agent(
        name="weather_agent_gpt",
        # 주요 변경 사항: LiteLLM 모델 식별자 래핑
        model=LiteLlm(model=MODEL_GPT_4O),
        description="Provides weather information (using GPT-4o).",
        instruction="You are a helpful weather assistant powered by GPT-4o. "
                    "Use the 'get_weather' tool for city weather requests. "
                    "Clearly present successful reports or polite error messages based on the tool's output status.",
        tools=[get_weather], # 동일한 도구 재사용
    )
    print(f"Agent '{weather_agent_gpt.name}' created using model '{MODEL_GPT_4O}'.")

    # InMemorySessionService는 이 튜토리얼을 위한 간단한 비영구 저장소입니다.
    session_service_gpt = InMemorySessionService() # 전용 서비스 생성

    # 상호 작용 컨텍스트 식별을 위한 상수 정의
    APP_NAME_GPT = "weather_tutorial_app_gpt" # 이 테스트를 위한 고유 앱 이름
    USER_ID_GPT = "user_1_gpt"
    SESSION_ID_GPT = "session_001_gpt" # 단순화를 위해 고정 ID 사용

    # 대화가 일어날 특정 세션 생성
    session_gpt = await session_service_gpt.create_session(
        app_name=APP_NAME_GPT,
        user_id=USER_ID_GPT,
        session_id=SESSION_ID_GPT
    )
    print(f"Session created: App='{APP_NAME_GPT}', User='{USER_ID_GPT}', Session='{SESSION_ID_GPT}'")

    # 이 에이전트 및 세션 서비스에 특정한 러너 생성
    runner_gpt = Runner(
        agent=weather_agent_gpt,
        app_name=APP_NAME_GPT,       # 특정 앱 이름 사용
        session_service=session_service_gpt # 특정 세션 서비스 사용
        )
    print(f"Runner created for agent '{runner_gpt.agent.name}'.")

    # --- GPT 에이전트 테스트 ---
    print("\n--- Testing GPT Agent ---")
    # call_agent_async가 올바른 runner, user_id, session_id를 사용하는지 확인
    await call_agent_async(query = "What's the weather in Tokyo?",
                           runner=runner_gpt,
                           user_id=USER_ID_GPT,
                           session_id=SESSION_ID_GPT)
    # --- 또는 ---

    # 표준 Python 스크립트(.py 파일)로 실행하는 경우 다음 줄의 주석을 제거하세요:
    # import asyncio
    # if __name__ == "__main__":
    #     try:
    #         asyncio.run(call_agent_async(query = "What's the weather in Tokyo?",
    #                      runner=runner_gpt,
    #                       user_id=USER_ID_GPT,
    #                       session_id=SESSION_ID_GPT)
    #     except Exception as e:
    #         print(f"An error occurred: {e}")

except Exception as e:
    print(f"❌ Could not create or run GPT agent '{MODEL_GPT_4O}'. Check API Key and model name. Error: {e}")

```

다음으로 Anthropic의 Claude Sonnet에 대해 동일한 작업을 수행합니다.

```python
# @title Claude 에이전트 정의 및 테스트

# 1단계의 'get_weather' 함수가 환경에 정의되어 있는지 확인하세요.
# 앞서 정의한 'call_agent_async'가 있는지 확인하세요.

# --- Claude Sonnet을 사용하는 에이전트 ---
weather_agent_claude = None # None으로 초기화
runner_claude = None      # runner를 None으로 초기화

try:
    weather_agent_claude = Agent(
        name="weather_agent_claude",
        # 주요 변경 사항: LiteLLM 모델 식별자 래핑
        model=LiteLlm(model=MODEL_CLAUDE_SONNET),
        description="Provides weather information (using Claude Sonnet).",
        instruction="You are a helpful weather assistant powered by Claude Sonnet. "
                    "Use the 'get_weather' tool for city weather requests. "
                    "Analyze the tool's dictionary output ('status', 'report'/'error_message'). "
                    "Clearly present successful reports or polite error messages.",
        tools=[get_weather], # 동일한 도구 재사용
    )
    print(f"Agent '{weather_agent_claude.name}' created using model '{MODEL_CLAUDE_SONNET}'.")

    # InMemorySessionService는 이 튜토리얼을 위한 간단한 비영구 저장소입니다.
    session_service_claude = InMemorySessionService() # 전용 서비스 생성

    # 상호 작용 컨텍스트 식별을 위한 상수 정의
    APP_NAME_CLAUDE = "weather_tutorial_app_claude" # 고유 앱 이름
    USER_ID_CLAUDE = "user_1_claude"
    SESSION_ID_CLAUDE = "session_001_claude" # 단순화를 위해 고정 ID 사용

    # 대화가 일어날 특정 세션 생성
    session_claude = await session_service_claude.create_session(
        app_name=APP_NAME_CLAUDE,
        user_id=USER_ID_CLAUDE,
        session_id=SESSION_ID_CLAUDE
    )
    print(f"Session created: App='{APP_NAME_CLAUDE}', User='{USER_ID_CLAUDE}', Session='{SESSION_ID_CLAUDE}'")

    # 이 에이전트 및 세션 서비스에 특정한 러너 생성
    runner_claude = Runner(
        agent=weather_agent_claude,
        app_name=APP_NAME_CLAUDE,       # 특정 앱 이름 사용
        session_service=session_service_claude # 특정 세션 서비스 사용
        )
    print(f"Runner created for agent '{runner_claude.agent.name}'.")

    # --- Claude 에이전트 테스트 ---
    print("\n--- Testing Claude Agent ---")
    # call_agent_async가 올바른 runner, user_id, session_id를 사용하는지 확인
    await call_agent_async(query = "Weather in London please.",
                           runner=runner_claude,
                           user_id=USER_ID_CLAUDE,
                           session_id=SESSION_ID_CLAUDE)

    # --- 또는 ---

    # 표준 Python 스크립트(.py 파일)로 실행하는 경우 다음 줄의 주석을 제거하세요:
    # import asyncio
    # if __name__ == "__main__":
    #     try:
    #         asyncio.run(call_agent_async(query = "Weather in London please.",
    #                      runner=runner_claude,
    #                       user_id=USER_ID_CLAUDE,
    #                       session_id=SESSION_ID_CLAUDE)
    #     except Exception as e:
    #         print(f"An error occurred: {e}")


except Exception as e:
    print(f"❌ Could not create or run Claude agent '{MODEL_CLAUDE_SONNET}'. Check API Key and model name. Error: {e}")
```

두 코드 블록의 출력을 주의 깊게 살펴보세요. 다음을 확인할 수 있습니다:

1.  각 에이전트(`weather_agent_gpt`, `weather_agent_claude`)가 성공적으로 생성됩니다(API 키가 유효한 경우).
2.  각각에 대해 전용 세션과 러너가 설정됩니다.
3.  각 에이전트는 쿼리를 처리할 때 `get_weather` 도구를 사용해야 할 필요성을 올바르게 식별합니다 (`--- Tool: get_weather called... ---` 로그 확인).
4.  *기본 도구 로직*은 동일하게 유지되며 항상 모의 데이터를 반환합니다.
5.  그러나 각 에이전트가 생성한 **최종 텍스트 응답**은 표현, 어조 또는 서식이 약간 다를 수 있습니다. 이는 지침 프롬프트가 서로 다른 LLM(GPT-4o 대 Claude Sonnet)에 의해 해석되고 실행되기 때문입니다.

이 단계는 ADK + LiteLLM이 제공하는 강력함과 유연성을 보여줍니다. 핵심 애플리케이션 로직(도구, 기본 에이전트 구조)을 일관되게 유지하면서 다양한 LLM을 사용하여 에이전트를 쉽게 실험하고 배포할 수 있습니다.

다음 단계에서는 단일 에이전트를 넘어 서로 작업을 위임할 수 있는 작은 팀을 구축해 보겠습니다!

---

## 3단계: 에이전트 팀 구축 - 인사 및 작별 인사 위임

1단계와 2단계에서는 날씨 조회에만 집중된 단일 에이전트를 구축하고 실험했습니다. 특정 작업에는 효과적이지만 실제 애플리케이션은 종종 더 다양한 사용자 상호 작용을 처리해야 합니다. 단일 날씨 에이전트에 더 많은 도구와 복잡한 지침을 계속 추가할 *수도* 있지만, 이는 금방 관리하기 어렵고 비효율적이 될 수 있습니다.

더 강력한 접근 방식은 **에이전트 팀**을 구축하는 것입니다. 여기에는 다음이 포함됩니다:

1.  각각 특정 기능(예: 날씨, 인사, 계산)을 위해 설계된 여러 개의 **전문 에이전트** 생성.
2.  초기 사용자 요청을 수신하는 **루트 에이전트**(또는 오케스트레이터) 지정.
3.  사용자의 의도에 따라 루트 에이전트가 요청을 가장 적절한 전문 하위 에이전트에게 **위임(delegate)**할 수 있도록 설정.

**왜 에이전트 팀을 구축하나요?**

*   **모듈성:** 개별 에이전트를 개발, 테스트 및 유지 관리하기가 더 쉽습니다.
*   **전문화:** 각 에이전트는 특정 작업에 대해 미세 조정(지침, 모델 선택)될 수 있습니다.
*   **확장성:** 새 에이전트를 추가하여 새 기능을 간단히 추가할 수 있습니다.
*   **효율성:** 더 간단한 작업(인사 등)에는 잠재적으로 더 간단하고 저렴한 모델을 사용할 수 있습니다.

**이 단계에서는 다음을 수행합니다:**

1.  인사(`say_hello`) 및 작별 인사(`say_goodbye`) 처리를 위한 간단한 도구를 정의합니다.
2.  두 개의 새로운 전문 하위 에이전트인 `greeting_agent`와 `farewell_agent`를 만듭니다.
3.  기본 날씨 에이전트(`weather_agent_v2`)를 **루트 에이전트**로 업데이트합니다.
4.  하위 에이전트로 루트 에이전트를 구성하여 **자동 위임**을 활성화합니다.
5.  다양한 유형의 요청을 루트 에이전트에 보내 위임 흐름을 테스트합니다.

---

**1\. 하위 에이전트용 도구 정의**

먼저 새로운 전문가 에이전트를 위한 도구 역할을 할 간단한 Python 함수를 만들어 봅시다. 명확한 독스트링은 이를 사용할 에이전트에게 필수적이라는 점을 기억하세요.

```python
# @title 인사 및 작별 인사 에이전트를 위한 도구 정의
from typing import Optional # Optional 가져오기

# 이 단계를 독립적으로 실행하는 경우 1단계의 'get_weather'를 사용할 수 있어야 합니다.
# def get_weather(city: str) -> dict: ... (1단계 참조)

def say_hello(name: Optional[str] = None) -> str:
    """간단한 인사를 제공합니다. 이름이 제공되면 사용됩니다.

    Args:
        name (str, optional): 인사할 사람의 이름입니다. 제공되지 않으면 일반적인 인사를 기본값으로 사용합니다.

    Returns:
        str: 친근한 인사 메시지입니다.
    """
    if name:
        greeting = f"Hello, {name}!"
        print(f"--- Tool: say_hello called with name: {name} ---")
    else:
        greeting = "Hello there!" # 이름이 None이거나 명시적으로 전달되지 않은 경우 기본 인사
        print(f"--- Tool: say_hello called without a specific name (name_arg_value: {name}) ---")
    return greeting

def say_goodbye() -> str:
    """대화를 마무리하기 위한 간단한 작별 메시지를 제공합니다."""
    print(f"--- Tool: say_goodbye called ---")
    return "Goodbye! Have a great day."

print("Greeting and Farewell tools defined.")

# 선택적 자체 테스트
print(say_hello("Alice"))
print(say_hello()) # 인수 없이 테스트 (기본값 "Hello there!" 사용해야 함)
print(say_hello(name=None)) # 이름을 명시적으로 None으로 테스트 (기본값 "Hello there!" 사용해야 함)
```

---

**2\. 하위 에이전트 정의 (인사 및 작별)**

이제 전문가를 위한 `Agent` 인스턴스를 만듭니다. 매우 집중된 `instruction`과 결정적으로 명확한 `description`에 주목하세요. `description`은 *루트 에이전트*가 *언제* 이러한 하위 에이전트에게 위임할지 결정하는 데 사용하는 기본 정보입니다.

**모범 사례:** 하위 에이전트 `description` 필드는 특정 기능을 정확하고 간결하게 요약해야 합니다. 이는 효과적인 자동 위임에 매우 중요합니다.

**모범 사례:** 하위 에이전트 `instruction` 필드는 제한된 범위에 맞춰 조정되어야 하며 정확히 무엇을 해야 하고 *무엇을 하지 말아야 하는지*(예: "당신의 *유일한* 작업은...") 알려야 합니다.

```python
# @title 인사 및 작별 인사 하위 에이전트 정의

# Gemini 이외의 모델을 사용하려는 경우 LiteLlm을 가져오고 API 키가 설정되어 있는지 확인하세요(0/2단계).
# from google.adk.models.lite_llm import LiteLlm
# MODEL_GPT_4O, MODEL_CLAUDE_SONNET 등이 정의되어 있어야 합니다.
# 그렇지 않으면 계속해서 다음을 사용하세요: model = MODEL_GEMINI_2_5_FLASH

# --- 인사 에이전트 ---
greeting_agent = None
try:
    greeting_agent = Agent(
        # 간단한 작업을 위해 잠재적으로 다르거나 저렴한 모델 사용
        model = MODEL_GEMINI_2_5_FLASH,
        # model=LiteLlm(model=MODEL_GPT_4O), # 다른 모델을 실험하고 싶은 경우
        name="greeting_agent",
        instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting to the user. "
                    "Use the 'say_hello' tool to generate the greeting. "
                    "If the user provides their name, make sure to pass it to the tool. "
                    "Do not engage in any other conversation or tasks.",
        description="Handles simple greetings and hellos using the 'say_hello' tool.", # 위임에 중요
        tools=[say_hello],
    )
    print(f"✅ Agent '{greeting_agent.name}' created using model '{greeting_agent.model}'.")
except Exception as e:
    print(f"❌ Could not create Greeting agent. Check API Key ({greeting_agent.model}). Error: {e}")

# --- 작별 인사 에이전트 ---
farewell_agent = None
try:
    farewell_agent = Agent(
        # 동일하거나 다른 모델 사용 가능
        model = MODEL_GEMINI_2_5_FLASH,
        # model=LiteLlm(model=MODEL_GPT_4O), # 다른 모델을 실험하고 싶은 경우
        name="farewell_agent",
        instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message. "
                    "Use the 'say_goodbye' tool when the user indicates they are leaving or ending the conversation "
                    "(e.g., using words like 'bye', 'goodbye', 'thanks bye', 'see you'). "
                    "Do not perform any other actions.",
        description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.", # 위임에 중요
        tools=[say_goodbye],
    )
    print(f"✅ Agent '{farewell_agent.name}' created using model '{farewell_agent.model}'.")
except Exception as e:
    print(f"❌ Could not create Farewell agent. Check API Key ({farewell_agent.model}). Error: {e}")
```

---

**3\. 하위 에이전트와 함께 루트 에이전트(날씨 에이전트 v2) 정의**

이제 `weather_agent`를 업그레이드합니다. 주요 변경 사항은 다음과 같습니다:

*   `sub_agents` 매개변수 추가: 방금 생성한 `greeting_agent` 및 `farewell_agent` 인스턴스를 포함하는 목록을 전달합니다.
*   `instruction` 업데이트: 루트 에이전트에게 하위 에이전트 *에 대해* 그리고 *언제* 작업을 위임해야 하는지 명시적으로 알려줍니다.

**핵심 개념: 자동 위임(Automatic Delegation/Auto Flow)** `sub_agents` 목록을 제공함으로써 ADK는 자동 위임을 활성화합니다. 루트 에이전트가 사용자 쿼리를 수신하면 LLM은 자신의 지침과 도구뿐만 아니라 각 하위 에이전트의 `description`도 고려합니다. LLM이 쿼리가 하위 에이전트의 설명된 기능(예: "간단한 인사 처리")과 더 잘 일치한다고 판단하면, 해당 턴에 대해 해당 하위 에이전트로 *제어권을 이전*하는 특별한 내부 작업을 자동으로 생성합니다. 그런 다음 하위 에이전트는 자체 모델, 지침 및 도구를 사용하여 쿼리를 처리합니다.

**모범 사례:** 루트 에이전트의 지침이 위임 결정을 명확하게 안내하도록 하세요. 하위 에이전트를 이름으로 언급하고 위임이 발생해야 하는 조건을 설명하세요.

```python
# @title 하위 에이전트가 있는 루트 에이전트 정의

# 루트 에이전트를 정의하기 전에 하위 에이전트가 성공적으로 생성되었는지 확인하세요.
# 또한 원래 'get_weather' 도구가 정의되어 있는지 확인하세요.
root_agent = None
runner_root = None # runner 초기화

if greeting_agent and farewell_agent and 'get_weather' in globals():
    # 오케스트레이션 처리를 위해 루트 에이전트에 유능한 Gemini 모델 사용
    root_agent_model = MODEL_GEMINI_2_5_FLASH

    weather_agent_team = Agent(
        name="weather_agent_v2", # 새 버전 이름 부여
        model=root_agent_model,
        description="The main coordinator agent. Handles weather requests and delegates greetings/farewells to specialists.",
        instruction="You are the main Weather Agent coordinating a team. Your primary responsibility is to provide weather information. "
                    "Use the 'get_weather' tool ONLY for specific weather requests (e.g., 'weather in London'). "
                    "You have specialized sub-agents: "
                    "1. 'greeting_agent': Handles simple greetings like 'Hi', 'Hello'. Delegate to it for these. "
                    "2. 'farewell_agent': Handles simple farewells like 'Bye', 'See you'. Delegate to it for these. "
                    "Analyze the user's query. If it's a greeting, delegate to 'greeting_agent'. If it's a farewell, delegate to 'farewell_agent'. "
                    "If it's a weather request, handle it yourself using 'get_weather'. "
                    "For anything else, respond appropriately or state you cannot handle it.",
        tools=[get_weather], # 루트 에이전트는 핵심 작업을 위해 여전히 날씨 도구가 필요함
        # 주요 변경 사항: 여기에 하위 에이전트 연결!
        sub_agents=[greeting_agent, farewell_agent]
    )
    print(f"✅ Root Agent '{weather_agent_team.name}' created using model '{root_agent_model}' with sub-agents: {[sa.name for sa in weather_agent_team.sub_agents]}")

else:
    print("❌ Cannot create root agent because one or more sub-agents failed to initialize or 'get_weather' tool is missing.")
    if not greeting_agent: print(" - Greeting Agent is missing.")
    if not farewell_agent: print(" - Farewell Agent is missing.")
    if 'get_weather' not in globals(): print(" - get_weather function is missing.")


```

---

**4\. 에이전트 팀과 상호 작용하기**

이제 전문 하위 에이전트와 함께 루트 에이전트(`weather_agent_team` - *참고: 이 변수 이름이 이전 코드 블록 `# @title 하위 에이전트가 있는 루트 에이전트 정의`에서 정의된 이름과 일치하는지 확인하세요. 아마 `weather_agent_team`일 것입니다*)를 정의했으므로 위임 메커니즘을 테스트해 보겠습니다.

다음 코드 블록은 다음을 수행합니다:

1.  `async` 함수 `run_team_conversation`을 정의합니다.
2.  이 함수 내부에서 이 테스트 실행을 위해 *새로운 전용* `InMemorySessionService`와 특정 세션(`session_001_agent_team`)을 만듭니다. 이는 팀 역학을 테스트하기 위해 대화 기록을 격리합니다.
3.  `weather_agent_team`(루트 에이전트)과 전용 세션 서비스를 사용하도록 구성된 `Runner`(`runner_agent_team`)를 만듭니다.
4.  업데이트된 `call_agent_async` 함수를 사용하여 `runner_agent_team`에 다양한 유형의 쿼리(인사, 날씨 요청, 작별 인사)를 보냅니다. 이 특정 테스트를 위해 러너, 사용자 ID, 세션 ID를 명시적으로 전달합니다.
5.  `run_team_conversation` 함수를 즉시 실행합니다.

다음과 같은 흐름을 예상합니다:

1.  "Hello there!" 쿼리가 `runner_agent_team`으로 이동합니다.
2.  루트 에이전트(`weather_agent_team`)가 이를 수신하고, 지침과 `greeting_agent`의 설명에 따라 작업을 위임합니다.
3.  `greeting_agent`가 쿼리를 처리하고, `say_hello` 도구를 호출하고, 응답을 생성합니다.
4.  "What is the weather in New York?" 쿼리는 위임되지 *않고* 루트 에이전트가 `get_weather` 도구를 사용하여 직접 처리합니다.
5.  "Thanks, bye!" 쿼리는 `farewell_agent`로 위임되며, 이 에이전트는 `say_goodbye` 도구를 사용합니다.

```python
# @title 에이전트 팀과 상호 작용하기
import asyncio # asyncio 가져오기

# 루트 에이전트(예: 'weather_agent_team' 또는 이전 셀의 'root_agent')가 정의되어 있는지 확인.
# call_agent_async 함수가 정의되어 있는지 확인.

# 대화 함수를 정의하기 전에 루트 에이전트 변수가 존재하는지 확인
root_agent_var_name = 'root_agent' # 3단계 가이드의 기본 이름
if 'weather_agent_team' in globals(): # 사용자가 이 이름을 대신 사용했는지 확인
    root_agent_var_name = 'weather_agent_team'
elif 'root_agent' not in globals():
    print("⚠️ Root agent ('root_agent' or 'weather_agent_team') not found. Cannot define run_team_conversation.")
    # 나중에 코드 블록이 실행되더라도 NameError를 방지하기 위해 더미 값 할당
    root_agent = None # 또는 실행 방지를 위한 플래그 설정

# 루트 에이전트가 존재하는 경우에만 정의 및 실행
if root_agent_var_name in globals() and globals()[root_agent_var_name]:
    # 대화 로직을 위한 메인 비동기 함수 정의.
    # 이 함수 내부의 'await' 키워드는 비동기 작업에 필요합니다.
    async def run_team_conversation():
        print("\n--- Testing Agent Team Delegation ---")
        session_service = InMemorySessionService()
        APP_NAME = "weather_tutorial_agent_team"
        USER_ID = "user_1_agent_team"
        SESSION_ID = "session_001_agent_team"
        session = await session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
        )
        print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")

        actual_root_agent = globals()[root_agent_var_name]
        runner_agent_team = Runner( # 또는 InMemoryRunner 사용
            agent=actual_root_agent,
            app_name=APP_NAME,
            session_service=session_service
        )
        print(f"Runner created for agent '{actual_root_agent.name}'.")

        # --- await를 사용한 상호 작용 (async def 내에서 올바름) ---
        await call_agent_async(query = "Hello there!",
                               runner=runner_agent_team,
                               user_id=USER_ID,
                               session_id=SESSION_ID)
        await call_agent_async(query = "What is the weather in New York?",
                               runner=runner_agent_team,
                               user_id=USER_ID,
                               session_id=SESSION_ID)
        await call_agent_async(query = "Thanks, bye!",
                               runner=runner_agent_team,
                               user_id=USER_ID,
                               session_id=SESSION_ID)

    # --- `run_team_conversation` 비동기 함수 실행 ---
    # 환경에 따라 아래 방법 중 하나를 선택하세요.
    # 참고: 사용된 모델에 대한 API 키가 필요할 수 있습니다!

    # 방법 1: 직접 await (노트북/비동기 REPL 기본값)
    # 환경이 최상위 레벨 await를 지원하는 경우(Colab/Jupyter 노트북 등),
    # 이벤트 루프가 이미 실행 중이므로 함수를 직접 await할 수 있습니다.
    print("Attempting execution using 'await' (default for notebooks)...")
    await run_team_conversation()

    # 방법 2: asyncio.run (표준 Python 스크립트 [.py]용)
    # 터미널에서 표준 Python 스크립트로 이 코드를 실행하는 경우,
    # 스크립트 컨텍스트는 동기식입니다. `asyncio.run()`이 필요합니다.
    # 비동기 함수를 실행할 이벤트 루프를 만들고 관리하려면 이 방법을 사용하세요.
    # 이 방법을 사용하려면:
    # 1. 위의 `await run_team_conversation()` 줄을 주석 처리합니다.
    # 2. 다음 블록의 주석을 제거합니다:
    """
    import asyncio
    if __name__ == "__main__": # 스크립트가 직접 실행될 때만 실행되도록 보장
        print("Executing using 'asyncio.run()' (for standard Python scripts)...")
        try:
            # 이벤트 루프를 생성하고, 비동기 함수를 실행하고, 루프를 닫습니다.
            asyncio.run(run_team_conversation())
        except Exception as e:
            print(f"An error occurred: {e}")
    """

else:
    # 루트 에이전트 변수가 이전에 발견되지 않은 경우 이 메시지가 출력됩니다.
    print("\n⚠️ Skipping agent team conversation execution as the root agent was not successfully defined in a previous step.")
```

---

출력 로그, 특히 `--- Tool: ... called ---` 메시지를 주의 깊게 살펴보세요. 다음을 관찰해야 합니다:

*   "Hello there!"의 경우 `say_hello` 도구가 호출되었습니다 (`greeting_agent`가 처리했음을 나타냄).
*   "What is the weather in New York?"의 경우 `get_weather` 도구가 호출되었습니다 (루트 에이전트가 처리했음을 나타냄).
*   "Thanks, bye!"의 경우 `say_goodbye` 도구가 호출되었습니다 (`farewell_agent`가 처리했음을 나타냄).

이것으로 성공적인 **자동 위임**을 확인했습니다! 지침과 `sub_agents`의 `description`에 따라 루트 에이전트는 사용자 요청을 팀 내의 적절한 전문 에이전트에게 올바르게 라우팅했습니다.

이제 여러 협업 에이전트로 애플리케이션을 구조화했습니다. 이 모듈식 설계는 더 복잡하고 유능한 에이전트 시스템을 구축하는 데 기본이 됩니다. 다음 단계에서는 에이전트에게 세션 상태를 사용하여 턴 간에 정보를 기억할 수 있는 능력을 부여하겠습니다.

## 4단계: 세션 상태(Session State)로 기억 및 개인화 추가하기

지금까지 우리의 에이전트 팀은 위임을 통해 다양한 작업을 처리할 수 있었지만, 각 상호 작용은 새로 시작됩니다. 에이전트는 세션 내에서 과거 대화나 사용자 기본 설정을 기억하지 못합니다. 보다 정교하고 맥락을 인식하는 경험을 만들기 위해 에이전트는 **기억**이 필요합니다. ADK는 **세션 상태(Session State)**를 통해 이를 제공합니다.

**세션 상태란 무엇인가요?**

*   특정 사용자 세션(`APP_NAME`, `USER_ID`, `SESSION_ID`로 식별됨)에 연결된 Python 딕셔너리(`session.state`)입니다.
*   해당 세션 내의 *여러 대화 턴(turn)에 걸쳐* 정보를 유지합니다.
*   에이전트와 도구는 이 상태를 읽고 쓸 수 있어 세부 정보를 기억하고, 행동을 조정하고, 응답을 개인화할 수 있습니다.

**에이전트가 상태와 상호 작용하는 방법:**

1.  **`ToolContext` (기본 방법):** 도구는 `ToolContext` 객체(마지막 인수로 선언된 경우 ADK가 자동으로 제공)를 받을 수 있습니다. 이 객체는 `tool_context.state`를 통해 세션 상태에 직접 액세스할 수 있게 하여 도구가 실행 *중에* 기본 설정을 읽거나 결과를 저장할 수 있게 합니다.
2.  **`output_key` (에이전트 응답 자동 저장):** `Agent`는 `output_key="your_key"`로 구성할 수 있습니다. 그러면 ADK는 에이전트의 턴에 대한 최종 텍스트 응답을 자동으로 `session.state["your_key"]`에 저장합니다.

**이 단계에서는 다음을 통해 날씨 봇 팀을 향상시킬 것입니다:**

1.  이전 단계의 간섭 없이 상태를 명확하게 보여주기 위해 **새로운** `InMemorySessionService`를 사용합니다.
2.  `temperature_unit`에 대한 사용자 기본 설정으로 세션 상태를 초기화합니다.
3.  `ToolContext`를 통해 이 기본 설정을 읽고 출력 형식(섭씨/화씨)을 조정하는 상태 인식 버전의 날씨 도구(`get_weather_stateful`)를 만듭니다.
4.  이 상태 인식 도구를 사용하도록 루트 에이전트를 업데이트하고 `output_key`를 구성하여 최종 날씨 보고서를 세션 상태에 자동으로 저장하도록 합니다.
5.  대화를 실행하여 초기 상태가 도구에 어떤 영향을 미치는지, 수동 상태 변경이 후속 동작을 어떻게 변경하는지, `output_key`가 에이전트의 응답을 어떻게 유지하는지 관찰합니다.

---

**1\. 새 세션 서비스 및 상태 초기화**

이전 단계의 간섭 없이 상태 관리를 명확하게 보여주기 위해 새로운 `InMemorySessionService`를 인스턴스화합니다. 또한 사용자가 선호하는 온도 단위를 정의하는 초기 상태로 세션을 만들 것입니다.

```python
# @title 1. 새 세션 서비스 및 상태 초기화

# 필요한 세션 구성 요소 가져오기
from google.adk.sessions import InMemorySessionService

# 상태 데모를 위한 새로운 세션 서비스 인스턴스 생성
session_service_stateful = InMemorySessionService()
print("✅ New InMemorySessionService created for state demonstration.")

# 이 튜토리얼 부분을 위한 새로운 세션 ID 정의
SESSION_ID_STATEFUL = "session_state_demo_001"
USER_ID_STATEFUL = "user_state_demo"

# 초기 상태 데이터 정의 - 사용자는 초기에 섭씨를 선호함
initial_state = {
    "user_preference_temperature_unit": "Celsius"
}

# 초기 상태를 제공하여 세션 생성
session_stateful = await session_service_stateful.create_session(
    app_name=APP_NAME, # 일관된 앱 이름 사용
    user_id=USER_ID_STATEFUL,
    session_id=SESSION_ID_STATEFUL,
    state=initial_state # <<< 생성 중 상태 초기화
)
print(f"✅ Session '{SESSION_ID_STATEFUL}' created for user '{USER_ID_STATEFUL}'.")

# 초기 상태가 올바르게 설정되었는지 확인
retrieved_session = await session_service_stateful.get_session(app_name=APP_NAME,
                                                         user_id=USER_ID_STATEFUL,
                                                         session_id = SESSION_ID_STATEFUL)
print("\n--- Initial Session State ---")
if retrieved_session:
    print(retrieved_session.state)
else:
    print("Error: Could not retrieve session.")
```

---

**2\. 상태 인식 날씨 도구 생성 (`get_weather_stateful`)**

이제 새로운 버전의 날씨 도구를 만듭니다. 주요 특징은 `tool_context: ToolContext`를 받아 `tool_context.state`에 액세스할 수 있다는 것입니다. `user_preference_temperature_unit`을 읽고 온도를 그에 맞게 포맷팅합니다.

*   **핵심 개념: `ToolContext`** 이 객체는 도구 로직이 상태 변수를 읽고 쓰는 것을 포함하여 세션의 컨텍스트와 상호 작용할 수 있게 해주는 다리입니다. 도구 함수의 마지막 매개변수로 정의하면 ADK가 자동으로 주입합니다.

*   **모범 사례:** 상태에서 읽을 때 `dictionary.get('key', default_value)`를 사용하여 키가 아직 존재하지 않을 수 있는 경우를 처리하여 도구가 중단되지 않도록 하세요.

```python
from google.adk.tools.tool_context import ToolContext

def get_weather_stateful(city: str, tool_context: ToolContext) -> dict:
    """날씨를 검색하고 세션 상태에 따라 온도 단위를 변환합니다."""
    print(f"--- Tool: get_weather_stateful called for {city} ---")

    # --- 상태에서 기본 설정 읽기 ---
    preferred_unit = tool_context.state.get("user_preference_temperature_unit", "Celsius") # 기본값 섭씨
    print(f"--- Tool: Reading state 'user_preference_temperature_unit': {preferred_unit} ---")

    city_normalized = city.lower().replace(" ", "")

    # 모의 날씨 데이터 (내부적으로 항상 섭씨로 저장됨)
    mock_weather_db = {
        "newyork": {"temp_c": 25, "condition": "sunny"},
        "london": {"temp_c": 15, "condition": "cloudy"},
        "tokyo": {"temp_c": 18, "condition": "light rain"},
    }

    if city_normalized in mock_weather_db:
        data = mock_weather_db[city_normalized]
        temp_c = data["temp_c"]
        condition = data["condition"]

        # 상태 기본 설정에 따라 온도 포맷팅
        if preferred_unit == "Fahrenheit":
            temp_value = (temp_c * 9/5) + 32 # 화씨 계산
            temp_unit = "°F"
        else: # 기본값 섭씨
            temp_value = temp_c
            temp_unit = "°C"

        report = f"The weather in {city.capitalize()} is {condition} with a temperature of {temp_value:.0f}{temp_unit}."
        result = {"status": "success", "report": report}
        print(f"--- Tool: Generated report in {preferred_unit}. Result: {result} ---")

        # 상태에 다시 쓰기 예시 (이 도구의 경우 선택 사항)
        tool_context.state["last_city_checked_stateful"] = city
        print(f"--- Tool: Updated state 'last_city_checked_stateful': {city} ---")

        return result
    else:
        # 도시를 찾을 수 없음 처리
        error_msg = f"Sorry, I don't have weather information for '{city}'."
        print(f"--- Tool: City '{city}' not found. ---")
        return {"status": "error", "error_message": error_msg}

print("✅ State-aware 'get_weather_stateful' tool defined.")

```

---

**3\. 하위 에이전트 재정의 및 루트 에이전트 업데이트**

이 단계가 독립적으로 올바르게 빌드되도록 하기 위해 먼저 `greeting_agent`와 `farewell_agent`를 3단계와 동일하게 재정의합니다. 그런 다음 새로운 루트 에이전트(`weather_agent_v4_stateful`)를 정의합니다:

*   새로운 `get_weather_stateful` 도구를 사용합니다.
*   위임을 위해 인사 및 작별 인사 하위 에이전트를 포함합니다.
*   **결정적으로**, `output_key="last_weather_report"`를 설정하여 최종 날씨 응답을 세션 상태에 자동으로 저장합니다.

```python
# @title 3. 하위 에이전트 재정의 및 output_key로 루트 에이전트 업데이트

# 필수 가져오기 확인: Agent, LiteLlm, Runner
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
# 'say_hello', 'say_goodbye' 도구가 정의되어 있는지 확인 (3단계 참조)
# 모델 상수 MODEL_GPT_4O, MODEL_GEMINI_2_5_FLASH 등이 정의되어 있는지 확인

# --- 인사 에이전트 재정의 (3단계에서) ---
greeting_agent = None
try:
    greeting_agent = Agent(
        model=MODEL_GEMINI_2_5_FLASH,
        name="greeting_agent",
        instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting using the 'say_hello' tool. Do nothing else.",
        description="Handles simple greetings and hellos using the 'say_hello' tool.",
        tools=[say_hello],
    )
    print(f"✅ Agent '{greeting_agent.name}' redefined.")
except Exception as e:
    print(f"❌ Could not redefine Greeting agent. Error: {e}")

# --- 작별 인사 에이전트 재정의 (3단계에서) ---
farewell_agent = None
try:
    farewell_agent = Agent(
        model=MODEL_GEMINI_2_5_FLASH,
        name="farewell_agent",
        instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message using the 'say_goodbye' tool. Do not perform any other actions.",
        description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.",
        tools=[say_goodbye],
    )
    print(f"✅ Agent '{farewell_agent.name}' redefined.")
except Exception as e:
    print(f"❌ Could not redefine Farewell agent. Error: {e}")

# --- 업데이트된 루트 에이전트 정의 ---
root_agent_stateful = None
runner_root_stateful = None # runner 초기화

# 루트 에이전트를 생성하기 전에 전제 조건 확인
if greeting_agent and farewell_agent and 'get_weather_stateful' in globals():

    root_agent_model = MODEL_GEMINI_2_5_FLASH # 오케스트레이션 모델 선택

    root_agent_stateful = Agent(
        name="weather_agent_v4_stateful", # 새 버전 이름
        model=root_agent_model,
        description="Main agent: Provides weather (state-aware unit), delegates greetings/farewells, saves report to state.",
        instruction="You are the main Weather Agent. Your job is to provide weather using 'get_weather_stateful'. "
                    "The tool will format the temperature based on user preference stored in state. "
                    "Delegate simple greetings to 'greeting_agent' and farewells to 'farewell_agent'. "
                    "Handle only weather requests, greetings, and farewells.",
        tools=[get_weather_stateful], # 상태 인식 도구 사용
        sub_agents=[greeting_agent, farewell_agent], # 하위 에이전트 포함
        output_key="last_weather_report" # <<< 에이전트의 최종 날씨 응답 자동 저장
    )
    print(f"✅ Root Agent '{root_agent_stateful.name}' created using stateful tool and output_key.")

    # --- 이 루트 에이전트 및 새로운 세션 서비스에 대한 Runner 생성 ---
    runner_root_stateful = Runner(
        agent=root_agent_stateful,
        app_name=APP_NAME,
        session_service=session_service_stateful # 새로운 상태 저장 세션 서비스 사용
    )
    print(f"✅ Runner created for stateful root agent '{runner_root_stateful.agent.name}' using stateful session service.")

else:
    print("❌ Cannot create stateful root agent. Prerequisites missing.")
    if not greeting_agent: print(" - greeting_agent definition missing.")
    if not farewell_agent: print(" - farewell_agent definition missing.")
    if 'get_weather_stateful' not in globals(): print(" - get_weather_stateful tool missing.")

```

---

**4\. 상호 작용 및 상태 흐름 테스트**

이제 `runner_root_stateful`(상태 저장 에이전트 및 `session_service_stateful`과 연결됨)을 사용하여 상태 상호 작용을 테스트하도록 설계된 대화를 실행해 보겠습니다. 앞서 정의한 `call_agent_async` 함수를 사용하여 올바른 러너, 사용자 ID(`USER_ID_STATEFUL`), 세션 ID(`SESSION_ID_STATEFUL`)를 전달하는지 확인합니다.

대화 흐름은 다음과 같습니다:

1.  **날씨 확인(런던):** `get_weather_stateful` 도구는 1섹션에서 초기화된 세션 상태에서 초기 "Celsius" 기본 설정을 읽어야 합니다. 루트 에이전트의 최종 응답(섭씨 날씨 보고서)은 `output_key` 구성을 통해 `state['last_weather_report']`에 저장되어야 합니다.
2.  **수동으로 상태 업데이트:** `InMemorySessionService` 인스턴스(`session_service_stateful`) 내에 저장된 상태를 *직접 수정*합니다.
    *   **왜 직접 수정인가요?** `session_service.get_session()` 메서드는 세션의 *사본*을 반환합니다. 그 사본을 수정해도 후속 에이전트 실행에 사용되는 상태에는 영향을 미치지 않습니다. `InMemorySessionService`를 사용하는 이 테스트 시나리오에서는 내부 `sessions` 딕셔너리에 액세스하여 `user_preference_temperature_unit`의 *실제* 저장된 상태 값을 "Fahrenheit"로 변경합니다. *참고: 실제 애플리케이션에서 상태 변경은 일반적으로 내부 저장소의 직접 조작이 아니라 `EventActions(state_delta=...)`를 반환하는 도구 또는 에이전트 로직에 의해 트리거됩니다.*
3.  **날씨 다시 확인(뉴욕):** `get_weather_stateful` 도구는 이제 상태에서 업데이트된 "Fahrenheit" 기본 설정을 읽고 그에 따라 온도를 변환해야 합니다. 루트 에이전트의 *새로운* 응답(화씨 날씨)은 `output_key`로 인해 `state['last_weather_report']`의 이전 값을 덮어씁니다.
4.  **에이전트에게 인사:** 상태 저장 작업과 함께 `greeting_agent`로의 위임이 여전히 올바르게 작동하는지 확인합니다. 이 상호 작용은 이 특정 시퀀스에서 `output_key`에 의해 저장되는 *마지막* 응답이 됩니다.
5.  **최종 상태 검사:** 대화 후 세션을 마지막으로 검색(사본 가져오기)하고 상태를 출력하여 `user_preference_temperature_unit`이 실제로 "Fahrenheit"인지 확인하고, `output_key`에 의해 저장된 최종 값(이 실행에서는 인사가 됨)을 관찰하며, 도구가 작성한 `last_city_checked_stateful` 값을 확인합니다.

```python
# @title 4. 상태 흐름 및 output_key 테스트를 위한 상호 작용
import asyncio # asyncio 가져오기

# 이전 셀에서 상태 저장 runner(runner_root_stateful)를 사용할 수 있는지 확인
# call_agent_async, USER_ID_STATEFUL, SESSION_ID_STATEFUL, APP_NAME이 정의되어 있는지 확인

if 'runner_root_stateful' in globals() and runner_root_stateful:
    # 상태 저장 대화 로직을 위한 메인 비동기 함수 정의.
    # 이 함수 내부의 'await' 키워드는 비동기 작업에 필요합니다.
    async def run_stateful_conversation():
        print("\n--- Testing State: Temp Unit Conversion & output_key ---")

        # 1. 날씨 확인 (초기 상태 사용: 섭씨)
        print("--- Turn 1: Requesting weather in London (expect Celsius) ---")
        await call_agent_async(query= "What's the weather in London?",
                               runner=runner_root_stateful,
                               user_id=USER_ID_STATEFUL,
                               session_id=SESSION_ID_STATEFUL
                              )

        # 2. 수동으로 상태 기본 설정을 화씨로 업데이트 - 저장소 직접 수정
        print("\n--- Manually Updating State: Setting unit to Fahrenheit ---")
        try:
            # 내부 저장소에 직접 액세스 - 이는 테스트용 InMemorySessionService에만 해당됨
            # 참고: 영구 서비스(Database, VertexAI)가 있는 프로덕션 환경에서는
            # 일반적으로 내부 저장소를 직접 조작하는 것이 아니라 에이전트 작업이나
            # 사용 가능한 경우 특정 서비스 API를 통해 상태를 업데이트합니다.
            stored_session = session_service_stateful.sessions[APP_NAME][USER_ID_STATEFUL][SESSION_ID_STATEFUL]
            stored_session.state["user_preference_temperature_unit"] = "Fahrenheit"
            # 선택 사항: 로직이 의존하는 경우 타임스탬프도 업데이트할 수 있습니다.
            # import time
            # stored_session.last_update_time = time.time()
            print(f"--- Stored session state updated. Current 'user_preference_temperature_unit': {stored_session.state.get('user_preference_temperature_unit', 'Not Set')} ---") # 안전을 위해 .get 추가
        except KeyError:
            print(f"--- Error: Could not retrieve session '{SESSION_ID_STATEFUL}' from internal storage for user '{USER_ID_STATEFUL}' in app '{APP_NAME}' to update state. Check IDs and if session was created. ---")
        except Exception as e:
             print(f"--- Error updating internal session state: {e} ---")

        # 3. 날씨 다시 확인 (이제 도구가 화씨를 사용해야 함)
        # 또한 output_key를 통해 'last_weather_report'를 업데이트합니다.
        print("\n--- Turn 2: Requesting weather in New York (expect Fahrenheit) ---")
        await call_agent_async(query= "Tell me the weather in New York.",
                               runner=runner_root_stateful,
                               user_id=USER_ID_STATEFUL,
                               session_id=SESSION_ID_STATEFUL
                              )

        # 4. 기본 위임 테스트 (여전히 작동해야 함)
        # 이는 'last_weather_report'를 다시 업데이트하여 NY 날씨 보고서를 덮어씁니다.
        print("\n--- Turn 3: Sending a greeting ---")
        await call_agent_async(query= "Hi!",
                               runner=runner_root_stateful,
                               user_id=USER_ID_STATEFUL,
                               session_id=SESSION_ID_STATEFUL
                              )

    # --- `run_stateful_conversation` 비동기 함수 실행 ---
    # 환경에 따라 아래 방법 중 하나를 선택하세요.

    # 방법 1: 직접 await (노트북/비동기 REPL 기본값)
    # 환경이 최상위 레벨 await를 지원하는 경우(Colab/Jupyter 노트북 등),
    # 이벤트 루프가 이미 실행 중이므로 함수를 직접 await할 수 있습니다.
    print("Attempting execution using 'await' (default for notebooks)...")
    await run_stateful_conversation()

    # 방법 2: asyncio.run (표준 Python 스크립트 [.py]용)
    # 터미널에서 표준 Python 스크립트로 이 코드를 실행하는 경우,
    # 스크립트 컨텍스트는 동기식입니다. `asyncio.run()`이 필요합니다.
    # 이 방법을 사용하려면:
    # 1. 위의 `await run_stateful_conversation()` 줄을 주석 처리합니다.
    # 2. 다음 블록의 주석을 제거합니다:
    """
    import asyncio
    if __name__ == "__main__": # 스크립트가 직접 실행될 때만 실행되도록 보장
        print("Executing using 'asyncio.run()' (for standard Python scripts)...")
        try:
            # 이벤트 루프를 생성하고, 비동기 함수를 실행하고, 루프를 닫습니다.
            asyncio.run(run_stateful_conversation())
        except Exception as e:
            print(f"An error occurred: {e}")
    """

    # --- 대화 후 최종 세션 상태 검사 ---
    # 이 블록은 실행 방법 중 하나가 완료된 후 실행됩니다.
    print("\n--- Inspecting Final Session State ---")
    final_session = await session_service_stateful.get_session(app_name=APP_NAME,
                                                         user_id= USER_ID_STATEFUL,
                                                         session_id=SESSION_ID_STATEFUL)
    if final_session:
        # 잠재적으로 누락된 키에 대한 안전한 액세스를 위해 .get() 사용
        print(f"Final Preference: {final_session.state.get('user_preference_temperature_unit', 'Not Set')}")
        print(f"Final Last Weather Report (from output_key): {final_session.state.get('last_weather_report', 'Not Set')}")
        print(f"Final Last City Checked (by tool): {final_session.state.get('last_city_checked_stateful', 'Not Set')}")
        # 자세한 보기를 위해 전체 상태 출력
        # print(f"Full State Dict: {final_session.state}") # 자세한 보기용
    else:
        print("\n❌ Error: Could not retrieve final session state.")

else:
    print("\n⚠️ Skipping state test conversation. Stateful root agent runner ('runner_root_stateful') is not available.")
```

---

대화 흐름과 최종 세션 상태 출력물을 검토하여 다음을 확인할 수 있습니다:

*   **상태 읽기:** 날씨 도구(`get_weather_stateful`)가 상태에서 `user_preference_temperature_unit`을 올바르게 읽어 런던에 대해 초기에 "Celsius"를 사용했습니다.
*   **상태 업데이트:** 직접 수정을 통해 저장된 기본 설정을 "Fahrenheit"로 성공적으로 변경했습니다.
*   **상태 읽기(업데이트됨):** 도구는 이후 뉴욕 날씨를 요청받았을 때 "Fahrenheit"를 읽고 변환을 수행했습니다.
*   **도구 상태 쓰기:** 도구가 `last_city_checked_stateful`("New York", 두 번째 날씨 확인 후)을 `tool_context.state`를 통해 상태에 성공적으로 썼습니다.
*   **위임:** "Hi!"에 대한 `greeting_agent`로의 위임은 상태 수정 후에도 올바르게 작동했습니다.
*   **`output_key`:** `output_key="last_weather_report"`는 루트 에이전트가 궁극적으로 응답하는 *각 턴*에 대해 루트 에이전트의 *최종* 응답을 성공적으로 저장했습니다. 이 시퀀스에서 마지막 응답은 인사("Hello, there!")였으므로 상태 키의 날씨 보고서를 덮어썼습니다.
*   **최종 상태:** 최종 확인 결과 기본 설정이 "Fahrenheit"로 유지되었음을 확인했습니다.

이제 `ToolContext`를 사용하여 에이전트 동작을 개인화하기 위해 세션 상태를 성공적으로 통합하고, `InMemorySessionService` 테스트를 위해 수동으로 상태를 조작했으며, `output_key`가 에이전트의 마지막 응답을 상태에 저장하는 간단한 메커니즘을 제공하는 방법을 관찰했습니다. 상태 관리에 대한 이 기초적인 이해는 다음 단계에서 콜백을 사용하여 안전 가드레일을 구현하는 데 핵심적입니다.

---

## 5단계: 안전 추가 - `before_model_callback`을 사용한 입력 가드레일

우리의 에이전트 팀은 선호도를 기억하고 도구를 효과적으로 사용하면서 점점 더 능력이 향상되고 있습니다. 그러나 실제 시나리오에서는 잠재적으로 문제가 있는 요청이 핵심 대규모 언어 모델(LLM)에 도달하기 *전에* 에이전트의 동작을 제어하는 안전 메커니즘이 필요한 경우가 많습니다.

ADK는 **콜백(Callbacks)**을 제공합니다. 이는 에이전트 실행 수명 주기의 특정 지점에 연결할 수 있는 함수입니다. `before_model_callback`은 입력 안전에 특히 유용합니다.

**`before_model_callback`이란 무엇인가요?**

*   에이전트가 컴파일된 요청(대화 기록, 지침 및 최신 사용자 메시지 포함)을 기본 LLM에 보내기 *직전에* ADK가 실행하는 Python 함수입니다.
*   **목적:** 사전 정의된 규칙에 따라 요청을 검사하고, 필요한 경우 수정하거나, 완전히 차단합니다.

**일반적인 사용 사례:**

*   **입력 유효성 검사/필터링:** 사용자 입력이 기준을 충족하는지 또는 허용되지 않는 콘텐츠(PII 또는 키워드 등)를 포함하는지 확인합니다.
*   **가드레일:** 유해하거나 주제를 벗어나거나 정책을 위반하는 요청이 LLM에 의해 처리되는 것을 방지합니다.
*   **동적 프롬프트 수정:** 전송 직전에 적절한 정보(예: 세션 상태에서)를 LLM 요청 컨텍스트에 추가합니다.

**작동 방식:**

1.  `callback_context: CallbackContext` 및 `llm_request: LlmRequest`를 허용하는 함수를 정의합니다.

    *   `callback_context`: 에이전트 정보, 세션 상태(`callback_context.state`) 등에 대한 액세스를 제공합니다.
    *   `llm_request`: LLM에 전달될 전체 페이로드(`contents`, `config`)를 포함합니다.

2.  함수 내부:

    *   **검사:** `llm_request.contents`(특히 마지막 사용자 메시지)를 검사합니다.
    *   **수정 (주의해서 사용):** `llm_request`의 일부를 변경할 *수 있습니다*.
    *   **차단 (가드레일):** `LlmResponse` 객체를 반환합니다. ADK는 즉시 이 응답을 반환하고 해당 턴에 대한 LLM 호출을 *건너뜁니다*.
    *   **허용:** `None`을 반환합니다. ADK는 (잠재적으로 수정된) 요청으로 LLM을 호출합니다.

**이 단계에서는 다음을 수행합니다:**

1.  사용자 입력에서 특정 키워드("BLOCK")를 확인하는 `before_model_callback` 함수(`block_keyword_guardrail`)를 정의합니다.
2.  이 콜백을 사용하도록 상태 인식 루트 에이전트(4단계의 `weather_agent_v4_stateful`)를 업데이트합니다.
3.  이 업데이트된 에이전트와 연결되지만 *동일한 상태 저장 세션 서비스*를 사용하는 새 러너를 만들어 상태 연속성을 유지합니다.
4.  일반 요청과 키워드가 포함된 요청을 모두 보내어 가드레일을 테스트합니다.

---

**1\. 가드레일 콜백 함수 정의**

이 함수는 `llm_request` 콘텐츠 내의 마지막 사용자 메시지를 검사합니다. "BLOCK"(대소문자 구분 없음)을 찾으면 흐름을 차단하기 위해 `LlmResponse`를 구성하고 반환합니다. 그렇지 않으면 `None`을 반환합니다.

```python
# @title 1. before_model_callback 가드레일 정의

# 필요한 가져오기가 있는지 확인
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types # 응답 내용 생성용
from typing import Optional

def block_keyword_guardrail(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """
    최신 사용자 메시지에서 'BLOCK'을 검사합니다. 발견되면 LLM 호출을 차단하고
    사전 정의된 LlmResponse를 반환합니다. 그렇지 않으면 계속 진행하기 위해 None을 반환합니다.
    """
    agent_name = callback_context.agent_name # 모델 호출이 가로채지는 에이전트 이름 가져오기
    print(f"--- Callback: block_keyword_guardrail running for agent: {agent_name} ---")

    # 요청 기록의 최신 사용자 메시지에서 텍스트 추출
    last_user_message_text = ""
    if llm_request.contents:
        # 역할이 'user'인 가장 최근 메시지 찾기
        for content in reversed(llm_request.contents):
            if content.role == 'user' and content.parts:
                # 간단하게 텍스트가 첫 번째 파트에 있다고 가정
                if content.parts[0].text:
                    last_user_message_text = content.parts[0].text
                    break # 마지막 사용자 메시지 텍스트 찾음

    print(f"--- Callback: Inspecting last user message: '{last_user_message_text[:100]}...' ---") # 처음 100자 로그

    # --- 가드레일 로직 ---
    keyword_to_block = "BLOCK"
    if keyword_to_block in last_user_message_text.upper(): # 대소문자 구분 없는 체크
        print(f"--- Callback: Found '{keyword_to_block}'. Blocking LLM call! ---")
        # 선택적으로 차단 이벤트를 기록하기 위해 상태에 플래그 설정
        callback_context.state["guardrail_block_keyword_triggered"] = True
        print(f"--- Callback: Set state 'guardrail_block_keyword_triggered': True ---")

        # 흐름을 중지하고 대신 이 응답을 보내기 위해 LlmResponse 구성 및 반환
        return LlmResponse(
            content=types.Content(
                role="model", # 에이전트 관점의 응답 흉내
                parts=[types.Part(text=f"I cannot process this request because it contains the blocked keyword '{keyword_to_block}'.")],
            )
            # 참고: 필요한 경우 여기에 error_message 필드를 설정할 수도 있습니다.
        )
    else:
        # 키워드를 찾을 수 없음, 요청이 LLM으로 진행되도록 허용
        print(f"--- Callback: Keyword not found. Allowing LLM call for {agent_name}. ---")
        return None # None을 반환하면 ADK가 정상적으로 계속하도록 신호를 보냄

print("✅ block_keyword_guardrail function defined.")

```

---

**2\. 콜백을 사용하도록 루트 에이전트 업데이트**

루트 에이전트를 재정의하여 `before_model_callback` 매개변수를 추가하고 새 가드레일 함수를 가리킵니다. 명확성을 위해 새 버전 이름을 부여합니다.

*중요:* 루트 에이전트 정의가 모든 구성 요소에 액세스할 수 있도록 하려면, 이전 단계에서 이미 사용할 수 없는 경우 이 컨텍스트 내에서 하위 에이전트(`greeting_agent`, `farewell_agent`)와 상태 인식 도구(`get_weather_stateful`)를 재정의해야 합니다.

```python
# @title 2. before_model_callback으로 루트 에이전트 업데이트


# --- 하위 에이전트 재정의 (이 컨텍스트에 존재하는지 확인) ---
greeting_agent = None
try:
    # 정의된 모델 상수 사용
    greeting_agent = Agent(
        model=MODEL_GEMINI_2_5_FLASH,
        name="greeting_agent", # 일관성을 위해 원래 이름 유지
        instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting using the 'say_hello' tool. Do nothing else.",
        description="Handles simple greetings and hellos using the 'say_hello' tool.",
        tools=[say_hello],
    )
    print(f"✅ Sub-Agent '{greeting_agent.name}' redefined.")
except Exception as e:
    print(f"❌ Could not redefine Greeting agent. Check Model/API Key ({greeting_agent.model}). Error: {e}")

farewell_agent = None
try:
    # 정의된 모델 상수 사용
    farewell_agent = Agent(
        model=MODEL_GEMINI_2_5_FLASH,
        name="farewell_agent", # 원래 이름 유지
        instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message using the 'say_goodbye' tool. Do not perform any other actions.",
        description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.",
        tools=[say_goodbye],
    )
    print(f"✅ Sub-Agent '{farewell_agent.name}' redefined.")
except Exception as e:
    print(f"❌ Could not redefine Farewell agent. Check Model/API Key ({farewell_agent.model}). Error: {e}")


# --- 콜백이 있는 루트 에이전트 정의 ---
root_agent_model_guardrail = None
runner_root_model_guardrail = None

# 진행하기 전에 모든 구성 요소 확인
if greeting_agent and farewell_agent and 'get_weather_stateful' in globals() and 'block_keyword_guardrail' in globals():

    # 정의된 모델 상수 사용
    root_agent_model = MODEL_GEMINI_2_5_FLASH

    root_agent_model_guardrail = Agent(
        name="weather_agent_v5_model_guardrail", # 명확성을 위해 새 버전 이름
        model=root_agent_model,
        description="Main agent: Handles weather, delegates greetings/farewells, includes input keyword guardrail.",
        instruction="You are the main Weather Agent. Provide weather using 'get_weather_stateful'. "
                    "Delegate simple greetings to 'greeting_agent' and farewells to 'farewell_agent'. "
                    "Handle only weather requests, greetings, and farewells.",
        tools=[get_weather_stateful],
        sub_agents=[greeting_agent, farewell_agent], # 재정의된 하위 에이전트 참조
        output_key="last_weather_report", # 4단계의 output_key 유지
        before_model_callback=block_keyword_guardrail # <<< 가드레일 콜백 할당
    )
    print(f"✅ Root Agent '{root_agent_model_guardrail.name}' created with before_model_callback.")

    # --- 이 에이전트를 위한 Runner 생성, 동일한 상태 저장 세션 서비스 사용 ---
    # 4단계의 session_service_stateful이 존재하는지 확인
    if 'session_service_stateful' in globals():
        runner_root_model_guardrail = Runner(
            agent=root_agent_model_guardrail,
            app_name=APP_NAME, # 일관된 APP_NAME 사용
            session_service=session_service_stateful # <<< 4단계의 서비스 사용
        )
        print(f"✅ Runner created for guardrail agent '{runner_root_model_guardrail.agent.name}', using stateful session service.")
    else:
        print("❌ Cannot create runner. 'session_service_stateful' from Step 4 is missing.")

else:
    print("❌ Cannot create root agent with model guardrail. One or more prerequisites are missing or failed initialization:")
    if not greeting_agent: print("   - Greeting Agent")
    if not farewell_agent: print("   - Farewell Agent")
    if 'get_weather_stateful' not in globals(): print("   - 'get_weather_stateful' tool")
    if 'block_keyword_guardrail' not in globals(): print("   - 'block_keyword_guardrail' callback")
```

---

**3\. 가드레일 테스트를 위한 상호 작용**

가드레일의 동작을 테스트해 보겠습니다. 4단계와 *동일한 세션*(`SESSION_ID_STATEFUL`)을 사용하여 상태가 변경 사항 전반에 걸쳐 지속됨을 보여줄 것입니다.

1.  일반 날씨 요청을 보냅니다 (가드레일을 통과하고 실행되어야 함).
2.  "BLOCK"이 포함된 요청을 보냅니다 (콜백에 의해 가로채여야 함).
3.  인사를 보냅니다 (루트 에이전트의 가드레일을 통과하고, 위임되고, 정상적으로 실행되어야 함).

```python
# @title 3. 모델 입력 가드레일 테스트를 위한 상호 작용
import asyncio # asyncio 가져오기

# 가드레일 에이전트를 위한 runner를 사용할 수 있는지 확인
if 'runner_root_model_guardrail' in globals() and runner_root_model_guardrail:
    # 가드레일 테스트 대화를 위한 메인 비동기 함수 정의.
    # 이 함수 내부의 'await' 키워드는 비동기 작업에 필요합니다.
    async def run_guardrail_test_conversation():
        print("\n--- Testing Model Input Guardrail ---")

        # 콜백이 있는 에이전트의 러너와 기존 상태 저장 세션 ID 사용
        # 더 깔끔한 상호 작용 호출을 위한 도우미 람다 정의
        interaction_func = lambda query: call_agent_async(query,
                                                         runner_root_model_guardrail,
                                                         USER_ID_STATEFUL, # 기존 사용자 ID 사용
                                                         SESSION_ID_STATEFUL # 기존 세션 ID 사용
                                                        )
        # 1. 일반 요청 (콜백 허용, 이전 상태 변경에서 화씨를 사용해야 함)
        print("--- Turn 1: Requesting weather in London (expect allowed, Fahrenheit) ---")
        await interaction_func("What is the weather in London?")

        # 2. 차단된 키워드가 포함된 요청 (콜백 가로채기)
        print("\n--- Turn 2: Requesting with blocked keyword (expect blocked) ---")
        await interaction_func("BLOCK the request for weather in Tokyo") # 콜백이 "BLOCK"을 포착해야 함

        # 3. 일반 인사 (콜백이 루트 에이전트를 허용, 위임 발생)
        print("\n--- Turn 3: Sending a greeting (expect allowed) ---")
        await interaction_func("Hello again")

    # --- `run_guardrail_test_conversation` 비동기 함수 실행 ---
    # 환경에 따라 아래 방법 중 하나를 선택하세요.

    # 방법 1: 직접 await (노트북/비동기 REPL 기본값)
    # 환경이 최상위 레벨 await를 지원하는 경우(Colab/Jupyter 노트북 등),
    # 이벤트 루프가 이미 실행 중이므로 함수를 직접 await할 수 있습니다.
    print("Attempting execution using 'await' (default for notebooks)...")
    await run_guardrail_test_conversation()

    # 방법 2: asyncio.run (표준 Python 스크립트 [.py]용)
    # 터미널에서 표준 Python 스크립트로 이 코드를 실행하는 경우,
    # 스크립트 컨텍스트는 동기식입니다. `asyncio.run()`이 필요합니다.
    # 이 방법을 사용하려면:
    # 1. 위의 `await run_guardrail_test_conversation()` 줄을 주석 처리합니다.
    # 2. 다음 블록의 주석을 제거합니다:
    """
    import asyncio
    if __name__ == "__main__": # 스크립트가 직접 실행될 때만 실행되도록 보장
        print("Executing using 'asyncio.run()' (for standard Python scripts)...")
        try:
            # 이벤트 루프를 생성하고, 비동기 함수를 실행하고, 루프를 닫습니다.
            asyncio.run(run_guardrail_test_conversation())
        except Exception as e:
            print(f"An error occurred: {e}")
    """

    # --- 대화 후 최종 세션 상태 검사 ---
    # 이 블록은 실행 방법 중 하나가 완료된 후 실행됩니다.
    # 선택 사항: 콜백에 의해 설정된 트리거 플래그에 대한 상태 확인
    print("\n--- Inspecting Final Session State (After Guardrail Test) ---")
    # 이 상태 저장 세션과 관련된 세션 서비스 인스턴스 사용
    final_session = await session_service_stateful.get_session(app_name=APP_NAME,
                                                         user_id=USER_ID_STATEFUL,
                                                         session_id=SESSION_ID_STATEFUL)
    if final_session:
        # 더 안전한 액세스를 위해 .get() 사용
        print(f"Guardrail Triggered Flag: {final_session.state.get('guardrail_block_keyword_triggered', 'Not Set (or False)')}")
        print(f"Last Weather Report: {final_session.state.get('last_weather_report', 'Not Set')}") # 성공한 경우 런던 날씨여야 함
        print(f"Temperature Unit: {final_session.state.get('user_preference_temperature_unit', 'Not Set')}") # 화씨여야 함
        # print(f"Full State Dict: {final_session.state}") # 자세한 보기용
    else:
        print("\n❌ Error: Could not retrieve final session state.")

else:
    print("\n⚠️ Skipping model guardrail test. Runner ('runner_root_model_guardrail') is not available.")
```

---

실행 흐름을 관찰하세요:

1.  **런던 날씨:** `weather_agent_v5_model_guardrail`에 대해 콜백이 실행되고, 메시지를 검사하고, "Keyword not found. Allowing LLM call."을 출력하고, `None`을 반환합니다. 에이전트가 진행하여 `get_weather_stateful` 도구(4단계의 상태 변경에서 "Fahrenheit" 기본 설정 사용)를 호출하고 날씨를 반환합니다. 이 응답은 `output_key`를 통해 `last_weather_report`를 업데이트합니다.
2.  **BLOCK 요청:** `weather_agent_v5_model_guardrail`에 대해 콜백이 다시 실행되고, 메시지를 검사하고, "BLOCK"을 찾고, "Blocking LLM call!"을 출력하고, 상태 플래그를 설정하고, 사전 정의된 `LlmResponse`를 반환합니다. 에이전트의 기본 LLM은 이 턴에 대해 *절대 호출되지 않습니다*. 사용자는 콜백의 차단 메시지를 봅니다.
3.  **Hello Again:** 콜백이 `weather_agent_v5_model_guardrail`에 대해 실행되고 요청을 허용합니다. 그런 다음 루트 에이전트는 `greeting_agent`에 위임합니다. *참고: 루트 에이전트에 정의된 `before_model_callback`은 하위 에이전트에 자동으로 적용되지 않습니다.* `greeting_agent`는 정상적으로 진행되어 `say_hello` 도구를 호출하고 인사를 반환합니다.

입력 안전 계층을 성공적으로 구현했습니다! `before_model_callback`은 비용이 많이 들거나 잠재적으로 위험한 LLM 호출이 이루어지기 *전에* 규칙을 시행하고 에이전트 동작을 제어하는 강력한 메커니즘을 제공합니다. 다음으로 유사한 개념을 적용하여 도구 사용 자체에 가드레일을 추가하겠습니다.

## 6단계: 안전 추가 - `before_tool_callback`을 사용한 도구 인수 가드레일

5단계에서는 입력이 LLM에 도달하기 *전에* 사용자 입력을 검사하고 잠재적으로 차단하는 가드레일을 추가했습니다. 이제 LLM이 도구를 사용하기로 결정한 *후*이지만 도구가 실제로 실행되기 *전*에 또 다른 제어 계층을 추가하겠습니다. 이는 LLM이 도구에 전달하려는 *인수(arguments)*를 검증하는 데 유용합니다.

ADK는 바로 이 목적을 위해 `before_tool_callback`을 제공합니다.

**`before_tool_callback`이란 무엇인가요?**

*   LLM이 사용을 요청하고 인수를 결정한 후, 특정 도구 함수가 실행되기 *직전*에 실행되는 Python 함수입니다.
*   **목적:** 도구 인수를 검증하고, 특정 입력을 기반으로 도구 실행을 방지하고, 인수를 동적으로 수정하거나, 리소스 사용 정책을 시행합니다.

**일반적인 사용 사례:**

*   **인수 유효성 검사:** LLM이 제공한 인수가 유효한지, 허용된 범위 내에 있는지 또는 예상 형식과 일치하는지 확인합니다.
*   **리소스 보호:** 비용이 많이 들거나, 제한된 데이터에 액세스하거나, 원치 않는 부작용을 일으킬 수 있는 입력(예: 특정 매개변수에 대한 API 호출 차단)으로 도구가 호출되는 것을 방지합니다.
*   **동적 인수 수정:** 도구가 실행되기 전에 세션 상태 또는 기타 컨텍스트 정보를 기반으로 인수를 조정합니다.

**작동 방식:**

1.  `tool: BaseTool`, `args: Dict[str, Any]`, `tool_context: ToolContext`를 허용하는 함수를 정의합니다.

    *   `tool`: 호출되려는 도구 객체 (`tool.name` 검사).
    *   `args`: LLM이 도구에 대해 생성한 인수 딕셔너리.
    *   `tool_context`: 세션 상태(`tool_context.state`), 에이전트 정보 등에 대한 액세스 제공.

2.  함수 내부:

    *   **검사:** `tool.name`과 `args` 딕셔너리를 검사합니다.
    *   **수정:** `args` 딕셔너리 내의 값을 *직접* 변경합니다. `None`을 반환하면 도구가 이 수정된 인수로 실행됩니다.
    *   **차단/재정의 (가드레일):** **딕셔너리**를 반환합니다. ADK는 이 딕셔너리를 도구 호출의 *결과*로 취급하여 원래 도구 함수의 실행을 완전히 *건너뜁니다*. 딕셔너리는 차단하는 도구의 예상 반환 형식과 일치하는 것이 이상적입니다.
    *   **허용:** `None`을 반환합니다. ADK는 (잠재적으로 수정된) 인수로 실제 도구 함수를 실행합니다.

**이 단계에서는 다음을 수행합니다:**

1.  `get_weather_stateful` 도구가 "Paris" 도시와 함께 호출되는지 구체적으로 확인하는 `before_tool_callback` 함수(`block_paris_tool_guardrail`)를 정의합니다.
2.  "Paris"가 감지되면 콜백은 도구를 차단하고 사용자 정의 오류 딕셔너리를 반환합니다.
3.  `before_model_callback`과 이 새로운 `before_tool_callback`을 *모두* 포함하도록 루트 에이전트(`weather_agent_v6_tool_guardrail`)를 업데이트합니다.
4.  동일한 상태 저장 세션 서비스를 사용하여 이 에이전트에 대한 새 러너를 만듭니다.
5.  허용된 도시와 차단된 도시("Paris")에 대한 날씨를 요청하여 흐름을 테스트합니다.

---

**1\. 도구 가드레일 콜백 함수 정의**

이 함수는 `get_weather_stateful` 도구를 대상으로 합니다. `city` 인수를 확인합니다. "Paris"인 경우 도구 자체 오류 응답과 유사한 오류 딕셔너리를 반환합니다. 그렇지 않으면 `None`을 반환하여 도구 실행을 허용합니다.

```python
# @title 1. before_tool_callback 가드레일 정의

# 필요한 가져오기가 있는지 확인
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from typing import Optional, Dict, Any # 타입 힌트용

def block_paris_tool_guardrail(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict]:
    """
    'get_weather_stateful'이 'Paris'에 대해 호출되는지 확인합니다.
    그렇다면 도구 실행을 차단하고 특정 오류 딕셔너리를 반환합니다.
    그렇지 않으면 None을 반환하여 도구 호출을 진행하도록 허용합니다.
    """
    tool_name = tool.name
    agent_name = tool_context.agent_name # 도구 호출을 시도하는 에이전트
    print(f"--- Callback: block_paris_tool_guardrail running for tool '{tool_name}' in agent '{agent_name}' ---")
    print(f"--- Callback: Inspecting args: {args} ---")

    # --- 가드레일 로직 ---
    target_tool_name = "get_weather_stateful" # FunctionTool이 사용하는 함수 이름과 일치
    blocked_city = "paris"

    # 올바른 도구인지 그리고 city 인수가 차단된 도시와 일치하는지 확인
    if tool_name == target_tool_name:
        city_argument = args.get("city", "") # 'city' 인수를 안전하게 가져오기
        if city_argument and city_argument.lower() == blocked_city:
            print(f"--- Callback: Detected blocked city '{city_argument}'. Blocking tool execution! ---")
            # 선택적으로 상태 업데이트
            tool_context.state["guardrail_tool_block_triggered"] = True
            print(f"--- Callback: Set state 'guardrail_tool_block_triggered': True ---")

            # 오류에 대한 도구의 예상 출력 형식과 일치하는 딕셔너리 반환
            # 이 딕셔너리는 도구의 결과가 되어 실제 도구 실행을 건너뜁니다.
            return {
                "status": "error",
                "error_message": f"Policy restriction: Weather checks for '{city_argument.capitalize()}' are currently disabled by a tool guardrail."
            }
        else:
             print(f"--- Callback: City '{city_argument}' is allowed for tool '{tool_name}'. ---")
    else:
        print(f"--- Callback: Tool '{tool_name}' is not the target tool. Allowing. ---")


    # 위의 검사에서 딕셔너리를 반환하지 않은 경우 도구 실행 허용
    print(f"--- Callback: Allowing tool '{tool_name}' to proceed. ---")
    return None # None을 반환하면 실제 도구 함수 실행 허용

print("✅ block_paris_tool_guardrail function defined.")


```

---

**2\. 두 콜백을 모두 사용하도록 루트 에이전트 업데이트**

루트 에이전트(`weather_agent_v6_tool_guardrail`)를 다시 재정의합니다. 이번에는 5단계의 `before_model_callback`과 함께 `before_tool_callback` 매개변수를 추가합니다.

*자체 포함 실행 참고:* 5단계와 마찬가지로, 이 에이전트를 정의하기 전에 실행 컨텍스트에서 모든 전제 조건(하위 에이전트, 도구, `before_model_callback`)이 정의되거나 사용 가능한지 확인하세요.

```python
# @title 2. 두 콜백으로 루트 에이전트 업데이트 (자체 포함)

# --- 전제 조건이 정의되어 있는지 확인 ---
# (다음에 대한 정의 포함 또는 실행 확인: Agent, LiteLlm, Runner, ToolContext,
#  MODEL constants, say_hello, say_goodbye, greeting_agent, farewell_agent,
#  get_weather_stateful, block_keyword_guardrail, block_paris_tool_guardrail)

# --- 하위 에이전트 재정의 (이 컨텍스트에 존재하는지 확인) ---
greeting_agent = None
try:
    # 정의된 모델 상수 사용
    greeting_agent = Agent(
        model=MODEL_GEMINI_2_5_FLASH,
        name="greeting_agent", # 일관성을 위해 원래 이름 유지
        instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting using the 'say_hello' tool. Do nothing else.",
        description="Handles simple greetings and hellos using the 'say_hello' tool.",
        tools=[say_hello],
    )
    print(f"✅ Sub-Agent '{greeting_agent.name}' redefined.")
except Exception as e:
    print(f"❌ Could not redefine Greeting agent. Check Model/API Key ({greeting_agent.model}). Error: {e}")

farewell_agent = None
try:
    # 정의된 모델 상수 사용
    farewell_agent = Agent(
        model=MODEL_GEMINI_2_5_FLASH,
        name="farewell_agent", # 원래 이름 유지
        instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message using the 'say_goodbye' tool. Do not perform any other actions.",
        description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.",
        tools=[say_goodbye],
    )
    print(f"✅ Sub-Agent '{farewell_agent.name}' redefined.")
except Exception as e:
    print(f"❌ Could not redefine Farewell agent. Check Model/API Key ({farewell_agent.model}). Error: {e}")

# --- 두 콜백이 모두 있는 루트 에이전트 정의 ---
root_agent_tool_guardrail = None
runner_root_tool_guardrail = None

if ('greeting_agent' in globals() and greeting_agent and
    'farewell_agent' in globals() and farewell_agent and
    'get_weather_stateful' in globals() and
    'block_keyword_guardrail' in globals() and
    'block_paris_tool_guardrail' in globals()):

    root_agent_model = MODEL_GEMINI_2_5_FLASH

    root_agent_tool_guardrail = Agent(
        name="weather_agent_v6_tool_guardrail", # 새 버전 이름
        model=root_agent_model,
        description="Main agent: Handles weather, delegates, includes input AND tool guardrails.",
        instruction="You are the main Weather Agent. Provide weather using 'get_weather_stateful'. "
                    "Delegate greetings to 'greeting_agent' and farewells to 'farewell_agent'. "
                    "Handle only weather, greetings, and farewells.",
        tools=[get_weather_stateful],
        sub_agents=[greeting_agent, farewell_agent],
        output_key="last_weather_report",
        before_model_callback=block_keyword_guardrail, # 모델 가드레일 유지
        before_tool_callback=block_paris_tool_guardrail # <<< 도구 가드레일 추가
    )
    print(f"✅ Root Agent '{root_agent_tool_guardrail.name}' created with BOTH callbacks.")

    # --- Runner 생성, 동일한 상태 저장 세션 서비스 사용 ---
    if 'session_service_stateful' in globals():
        runner_root_tool_guardrail = Runner(
            agent=root_agent_tool_guardrail,
            app_name=APP_NAME,
            session_service=session_service_stateful # <<< 4/5단계의 서비스 사용
        )
        print(f"✅ Runner created for tool guardrail agent '{runner_root_tool_guardrail.agent.name}', using stateful session service.")
    else:
        print("❌ Cannot create runner. 'session_service_stateful' from Step 4/5 is missing.")

else:
    print("❌ Cannot create root agent with tool guardrail. Prerequisites missing.")


```

---

**3\. 도구 가드레일 테스트를 위한 상호 작용**

다시 이전 단계와 동일한 상태 저장 세션(`SESSION_ID_STATEFUL`)을 사용하여 상호 작용 흐름을 테스트해 보겠습니다.

1.  "New York"에 대한 날씨 요청: 두 콜백을 모두 통과하고 도구가 실행됩니다 (상태의 화씨 기본 설정 사용).
2.  "Paris"에 대한 날씨 요청: `before_model_callback`을 통과합니다. LLM이 `get_weather_stateful(city='Paris')` 호출을 결정합니다. `before_tool_callback`이 가로채서 도구를 차단하고 오류 딕셔너리를 반환합니다. 에이전트는 이 오류를 전달합니다.
3.  "London"에 대한 날씨 요청: 두 콜백을 모두 통과하고 도구가 정상적으로 실행됩니다.

```python
# @title 3. 도구 인수 가드레일 테스트를 위한 상호 작용
import asyncio # asyncio 가져오기

# 도구 가드레일 에이전트를 위한 runner를 사용할 수 있는지 확인
if 'runner_root_tool_guardrail' in globals() and runner_root_tool_guardrail:
    # 도구 가드레일 테스트 대화를 위한 메인 비동기 함수 정의.
    # 이 함수 내부의 'await' 키워드는 비동기 작업에 필요합니다.
    async def run_tool_guardrail_test():
        print("\n--- Testing Tool Argument Guardrail ('Paris' blocked) ---")

        # 두 콜백이 모두 있는 에이전트의 러너와 기존 상태 저장 세션 사용
        # 더 깔끔한 상호 작용 호출을 위한 도우미 람다 정의
        interaction_func = lambda query: call_agent_async(query,
                                                         runner_root_tool_guardrail,
                                                         USER_ID_STATEFUL, # 기존 사용자 ID 사용
                                                         SESSION_ID_STATEFUL # 기존 세션 ID 사용
                                                        )
        # 1. 허용된 도시 (두 콜백 모두 통과, 화씨 상태 사용해야 함)
        print("--- Turn 1: Requesting weather in New York (expect allowed) ---")
        await interaction_func("What's the weather in New York?")

        # 2. 차단된 도시 (모델 콜백은 통과하지만 도구 콜백에 의해 차단되어야 함)
        print("\n--- Turn 2: Requesting weather in Paris (expect blocked by tool guardrail) ---")
        await interaction_func("How about Paris?") # 도구 콜백이 이것을 가로채야 함

        # 3. 다른 허용된 도시 (다시 정상 작동해야 함)
        print("\n--- Turn 3: Requesting weather in London (expect allowed) ---")
        await interaction_func("Tell me the weather in London.")

    # --- `run_tool_guardrail_test` 비동기 함수 실행 ---
    # 환경에 따라 아래 방법 중 하나를 선택하세요.

    # 방법 1: 직접 await (노트북/비동기 REPL 기본값)
    # 환경이 최상위 레벨 await를 지원하는 경우(Colab/Jupyter 노트북 등),
    # 이벤트 루프가 이미 실행 중이므로 함수를 직접 await할 수 있습니다.
    print("Attempting execution using 'await' (default for notebooks)...")
    await run_tool_guardrail_test()

    # 방법 2: asyncio.run (표준 Python 스크립트 [.py]용)
    # 터미널에서 표준 Python 스크립트로 이 코드를 실행하는 경우,
    # 스크립트 컨텍스트는 동기식입니다. `asyncio.run()`이 필요합니다.
    # 이 방법을 사용하려면:
    # 1. 위의 `await run_tool_guardrail_test()` 줄을 주석 처리합니다.
    # 2. 다음 블록의 주석을 제거합니다:
    """
    import asyncio
    if __name__ == "__main__": # 스크립트가 직접 실행될 때만 실행되도록 보장
        print("Executing using 'asyncio.run()' (for standard Python scripts)...")
        try:
            # 이벤트 루프를 생성하고, 비동기 함수를 실행하고, 루프를 닫습니다.
            asyncio.run(run_tool_guardrail_test())
        except Exception as e:
            print(f"An error occurred: {e}")
    """

    # --- 대화 후 최종 세션 상태 검사 ---
    # 이 블록은 실행 방법 중 하나가 완료된 후 실행됩니다.
    # 선택 사항: 도구 차단 트리거 플래그에 대한 상태 확인
    print("\n--- Inspecting Final Session State (After Tool Guardrail Test) ---")
    # 이 상태 저장 세션과 관련된 세션 서비스 인스턴스 사용
    final_session = await session_service_stateful.get_session(app_name=APP_NAME,
                                                         user_id=USER_ID_STATEFUL,
                                                         session_id= SESSION_ID_STATEFUL)
    if final_session:
        # 더 안전한 액세스를 위해 .get() 사용
        print(f"Tool Guardrail Triggered Flag: {final_session.state.get('guardrail_tool_block_triggered', 'Not Set (or False)')}")
        print(f"Last Weather Report: {final_session.state.get('last_weather_report', 'Not Set')}") # 성공한 경우 런던 날씨여야 함
        print(f"Temperature Unit: {final_session.state.get('user_preference_temperature_unit', 'Not Set')}") # 화씨여야 함
        # print(f"Full State Dict: {final_session.state}") # 자세한 보기용
    else:
        print("\n❌ Error: Could not retrieve final session state.")

else:
    print("\n⚠️ Skipping tool guardrail test. Runner ('runner_root_tool_guardrail') is not available.")
```

---

출력을 분석해 봅시다:

1.  **New York:** `before_model_callback`이 요청을 허용합니다. LLM이 `get_weather_stateful`을 요청합니다. `before_tool_callback`이 실행되고 인수(`{'city': 'New York'}`)를 검사하고 "Paris"가 아님을 확인한 후 "Allowing tool..."을 출력하고 `None`을 반환합니다. 실제 `get_weather_stateful` 함수가 실행되어 상태에서 "Fahrenheit"를 읽고 날씨 보고서를 반환합니다. 에이전트가 이를 전달하고 `output_key`를 통해 저장됩니다.
2.  **Paris:** `before_model_callback`이 요청을 허용합니다. LLM이 `get_weather_stateful(city='Paris')`를 요청합니다. `before_tool_callback`이 실행되고 인수를 검사하고 "Paris"를 감지한 후 "Blocking tool execution!"을 출력하고 상태 플래그를 설정하며 오류 딕셔너리 `{'status': 'error', 'error_message': 'Policy restriction...'}`를 반환합니다. 실제 `get_weather_stateful` 함수는 **실행되지 않습니다**. 에이전트는 *도구의 출력인 것처럼* 오류 딕셔너리를 수신하고 해당 오류 메시지를 기반으로 응답을 작성합니다.
3.  **London:** New York과 동일하게 작동하여 두 콜백을 모두 통과하고 도구를 성공적으로 실행합니다. 새로운 런던 날씨 보고서는 상태의 `last_weather_report`를 덮어씁니다.

이제 LLM에 도달하는 *것*뿐만 아니라 LLM이 생성한 특정 인수를 기반으로 에이전트의 도구를 사용하는 *방법*을 제어하는 중요한 안전 계층을 추가했습니다. `before_model_callback` 및 `before_tool_callback`과 같은 콜백은 강력하고 안전하며 정책을 준수하는 에이전트 애플리케이션을 구축하는 데 필수적입니다.

---

## 결론: 에이전트 팀이 준비되었습니다!

축하합니다! 단일 기본 날씨 에이전트 구축에서 시작하여 ADK(Agent Development Kit)를 사용하여 정교한 다중 에이전트 팀을 구성하는 여정을 성공적으로 마쳤습니다.

**달성한 내용을 요약해 봅시다:**

*   단일 도구(`get_weather`)를 갖춘 **기본 에이전트**로 시작했습니다.
*   LiteLLM을 사용하여 ADK의 **다중 모델 유연성**을 탐색하고, Gemini, GPT-4o, Claude와 같은 다른 LLM으로 동일한 핵심 로직을 실행했습니다.
*   전문 하위 에이전트(`greeting_agent`, `farewell_agent`)를 만들고 루트 에이전트로부터 **자동 위임**을 활성화하여 **모듈성**을 수용했습니다.
*   **세션 상태(Session State)**를 사용하여 에이전트에게 **기억**을 부여하여 사용자 기본 설정(`temperature_unit`)과 과거 상호 작용(`output_key`)을 기억할 수 있게 했습니다.
*   `before_model_callback`(특정 입력 키워드 차단)과 `before_tool_callback`(도시 "Paris"와 같은 인수를 기반으로 도구 실행 차단)을 모두 사용하여 중요한 **안전 가드레일**을 구현했습니다.

이 점진적인 날씨 봇 팀 구축을 통해 복잡한 지능형 애플리케이션을 개발하는 데 필수적인 핵심 ADK 개념에 대한 실무 경험을 얻었습니다.

**핵심 사항:**

*   **에이전트 및 도구:** 기능과 추론을 정의하기 위한 기본 구성 요소입니다. 명확한 지침과 독스트링이 가장 중요합니다.
*   **Runner 및 세션 서비스:** 에이전트 실행을 조정하고 대화 컨텍스트를 유지 관리하는 엔진 및 메모리 관리 시스템입니다.
*   **위임:** 다중 에이전트 팀을 설계하면 전문화, 모듈성 및 복잡한 작업 관리가 향상됩니다. 에이전트 `description`은 자동 흐름(auto-flow)의 핵심입니다.
*   **세션 상태 (`ToolContext`, `output_key`):** 상황을 인식하고 개인화된 다중 턴 대화형 에이전트를 만드는 데 필수적입니다.
*   **콜백 (`before_model`, `before_tool`):** 중요한 작업(LLM 호출 또는 도구 실행) *전에* 안전, 유효성 검사, 정책 시행 및 동적 수정을 구현하기 위한 강력한 후크입니다.
*   **유연성 (`LiteLlm`):** ADK는 성능, 비용 및 기능의 균형을 맞춰 작업에 가장 적합한 LLM을 선택할 수 있도록 지원합니다.

**다음 단계는 무엇인가요?**

여러분의 날씨 봇 팀은 훌륭한 출발점입니다. ADK를 더 깊이 탐구하고 애플리케이션을 향상시키기 위한 몇 가지 아이디어는 다음과 같습니다:

1.  **실제 날씨 API:** `get_weather` 도구의 `mock_weather_db`를 실제 날씨 API(OpenWeatherMap, WeatherAPI 등) 호출로 교체하세요.
2.  **더 복잡한 상태:** 더 많은 사용자 기본 설정(예: 선호하는 위치, 알림 설정)이나 대화 요약을 세션 상태에 저장하세요.
3.  **위임 개선:** 다른 루트 에이전트 지침이나 하위 에이전트 설명으로 실험하여 위임 로직을 미세 조정하세요. "예보" 에이전트를 추가할 수 있을까요?
4.  **고급 콜백:**
    *   `after_model_callback`을 사용하여 LLM의 응답이 생성된 *후* 잠재적으로 다시 포맷팅하거나 정리하세요.
    *   `after_tool_callback`을 사용하여 도구에서 반환된 결과를 처리하거나 기록하세요.
    *   에이전트 수준의 진입/종료 로직을 위해 `before_agent_callback` 또는 `after_agent_callback`을 구현하세요.
5.  **오류 처리:** 에이전트가 도구 오류나 예상치 못한 API 응답을 처리하는 방법을 개선하세요. 도구 내에 재시도 로직을 추가할 수도 있습니다.
6.  **영구 세션 저장소:** 세션 상태를 영구적으로 저장하기 위해 `InMemorySessionService`의 대안을 탐색하세요(예: Firestore 또는 Cloud SQL과 같은 데이터베이스 사용 - 사용자 정의 구현 또는 향후 ADK 통합 필요).
7.  **스트리밍 UI:** 에이전트 팀을 웹 프레임워크(ADK 스트리밍 빠른 시작에서 보여지는 FastAPI 등)와 통합하여 실시간 채팅 인터페이스를 만드세요.

Agent Development Kit는 정교한 LLM 기반 애플리케이션을 구축하기 위한 견고한 기반을 제공합니다. 도구, 상태, 위임 및 콜백과 같이 이 튜토리얼에서 다룬 개념을 마스터하면 점점 더 복잡해지는 에이전트 시스템을 다룰 준비가 된 것입니다.

즐거운 개발 되세요!