---
catalog_title: Respan
catalog_description: Respan 관측 가능성(observability)을 통해 ADK 에이전트를 트레이싱하고, 디버깅하고, 모니터링하세요
catalog_icon: /integrations/assets/respan.svg
catalog_tags: ["observability"]
---

# ADK를 위한 Respan 관측 가능성(observability) 연동

<div class="language-support-tag">
  <span class="lst-supported">ADK 지원</span><span class="lst-python">Python</span>
</div>

[Respan](https://www.respan.ai/)은 ADK runner, agent, model, tool 스팬(span)을 캡처하여 Respan 플랫폼에서 에이전트의 전체 워크플로를 검사할 수 있도록 지원합니다. ADK 연동 모듈은 OpenInference ADK 계측기(instrumentor)를 래핑하고 트레이스가 내보내지기 전에 Respan 전용 스팬 정상화를 추가하는 [`respan-instrumentation-google-adk`](https://pypi.org/project/respan-instrumentation-google-adk/)를 사용합니다.

## 개요

ADK에서 Respan을 사용하여 다음과 같은 작업을 수행할 수 있습니다:

- **에이전트 실행 트레이싱 (Trace agent runs)**: 러너 호출, 에이전트 실행, 모델 호출 및 도구 호출을 단일 트레이스 내에 캡처합니다.
- **실패 디버깅 (Debug failures)**: 중첩된 ADK 워크플로 전체에서 스팬 입력, 출력, 시간 측정 및 오류를 검사합니다.
- **프로덕션 메타데이터 추적 (Track production metadata)**: 한 요청에서 생성되는 모든 스팬에 고객, 스레드, 환경 및 맞춤형 메타데이터를 연결합니다.
- **Respan 게이트웨이를 통한 모델 라우팅 (Route models through the Respan gateway)**: 모델 라우팅을 중앙집중식으로 제어하려면 ADK의 LiteLLM 어댑터를 Respan의 OpenAI 호환 게이트웨이와 함께 사용합니다.

## 사전 요구사항

- Python 3.11, 3.12, 또는 3.13.
- Respan API 키.
- ADK 에이전트가 Gemini를 직접 호출하는 경우 Google API 키.

## 설치

Respan SDK, ADK 계측기(instrumentor) 및 ADK를 설치합니다:

```bash
pip install respan-ai respan-instrumentation-google-adk "google-adk[extensions]"
```

필요한 환경 변수를 설정합니다:

```bash
export RESPAN_API_KEY="YOUR_RESPAN_API_KEY"
export GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
```

`RESPAN_API_KEY`는 트레이스를 Respan으로 전송합니다. `GOOGLE_API_KEY`는 직접적인 Gemini 모델 호출에 사용됩니다.

## ADK 에이전트 트레이싱

ADK 에이전트를 실행하기 전에 Respan을 초기화합니다. 초기화 후 시작되는 모든 ADK 실행은 자동으로 트레이싱됩니다.

```python
import asyncio

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from respan import Respan
from respan_instrumentation_google_adk import GoogleADKInstrumentor

respan = Respan(
    instrumentations=[GoogleADKInstrumentor()],
    environment="development",
)

agent = Agent(
    name="assistant",
    model="gemini-flash-latest",
    instruction="You are a concise assistant.",
)


async def main():
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="respan-adk-demo",
        user_id="user_1",
    )
    runner = Runner(
        agent=agent,
        app_name="respan-adk-demo",
        session_service=session_service,
    )
    message = types.Content(
        role="user",
        parts=[types.Part(text="Say hello in one sentence.")],
    )

    async for event in runner.run_async(
        user_id="user_1",
        session_id=session.id,
        new_message=message,
    ):
        if event.is_final_response():
            print(event.content.parts[0].text)

    respan.flush()
    respan.shutdown()


asyncio.run(main())
```

[Respan 트레이스 페이지](https://platform.respan.ai/platform/traces)를 열어 러너, 에이전트, 모델, 도구 스팬이 포함된 ADK 워크플로를 확인하세요.

## 요청 메타데이터 추가

`propagate_attributes()`를 사용하여 컨텍스트 내부에서 생성되는 모든 스팬에 요청별 식별자 및 메타데이터를 추가합니다.

```python
from respan import Respan, propagate_attributes
from respan_instrumentation_google_adk import GoogleADKInstrumentor

respan = Respan(instrumentations=[GoogleADKInstrumentor()])


async def handle_user_request(user_id: str, message: str):
    with propagate_attributes(
        customer_identifier=user_id,
        thread_identifier="conversation_123",
        metadata={"source": "web"},
    ):
        return await run_adk_agent(message)
```

## 도구 호출 트레이싱

ADK 도구는 직렬화된 입력, 출력 및 시간 측정을 포함하여 하위 도구 스팬(span)으로 캡처됩니다.

```python
from google.adk.agents import Agent


def get_weather(city: str) -> str:
    """도시의 결정론적인 날씨 보고서 반환."""
    return f"{city}: sunny, 72F, light wind"


agent = Agent(
    name="weather_agent",
    model="gemini-flash-latest",
    instruction="Use the get_weather tool when weather is requested.",
    tools=[get_weather],
)
```

## Respan 게이트웨이 사용

ADK는 LiteLLM 어댑터를 통해 Respan 게이트웨이로 모델 호출을 라우팅할 수 있습니다. 이는 여러 모델 제공업체에 대해 하나의 OpenAI 호환 엔드포인트를 유지하려는 경우에 유용합니다.

```bash
export RESPAN_API_KEY="YOUR_RESPAN_API_KEY"
export RESPAN_BASE_URL="https://api.respan.ai/api"
export RESPAN_MODEL="openai/gpt-5-mini"
```

```python
import os

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

agent = Agent(
    name="assistant",
    model=LiteLlm(
        model=os.getenv("RESPAN_MODEL", "openai/gpt-5-mini"),
        api_key=os.environ["RESPAN_API_KEY"],
        api_base=os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api"),
    ),
    instruction="You are a concise assistant.",
)
```

## 리소스

- [Respan ADK 트레이싱 문서](https://www.respan.ai/docs/integrations/google-adk)
- [Respan ADK 게이트웨이 문서](https://www.respan.ai/docs/integrations/gateway/google-adk)
- [Respan Python 예시](https://github.com/respanai/respan-example-projects/tree/main/python/tracing/google-adk)
- [Respan 플랫폼](https://platform.respan.ai/platform/traces)
