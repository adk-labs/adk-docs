---
catalog_title: LangWatch
catalog_description: ADK 에이전트를 위한 관찰성, 추적, 평가, 프롬프트 최적화
catalog_icon: /integrations/assets/langwatch.png
catalog_tags: ["observability"]
---

# ADK용 LangWatch 관찰성

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[LangWatch](https://langwatch.ai)는 관찰성, 평가, 프롬프트 최적화를 위한 오픈소스 LLMOps 플랫폼입니다.
[OpenInference 계측](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-google-adk)을
사용해 ADK 에이전트에 대한 포괄적인 추적을 제공하며, 개발과 운영 환경에서 에이전트를 모니터링하고,
디버깅하고, 개선할 수 있게 해줍니다.

## 개요

LangWatch는 내장된 OpenTelemetry 지원을 사용해 ADK의 추적 정보를 수집하며, 다음과 같은 기능을 제공합니다.

- **자동 추적** - 모든 에이전트 실행, 도구 호출, 모델 요청을 전체 컨텍스트와 함께 캡처합니다
- **온라인 평가** - 프로덕션 트래픽의 품질과 안전성을 지속적으로 점수화합니다
- **가드레일** - 유해한 응답을 실시간으로 차단하거나 수정합니다
- **프롬프트 관리** - 내장된 A/B 테스트로 프롬프트를 버전 관리, 테스트, 최적화합니다
- **데이터셋과 실험** - 실제 추적 정보에서 평가 세트를 만들고 배치 실험을 실행합니다

## 설치

필요한 패키지를 설치합니다:

```bash
pip install langwatch openinference-instrumentation-google-adk google-adk
```

## 설정

[langwatch.ai](https://langwatch.ai)에서 가입하거나 플랫폼을
[자가 호스팅](https://langwatch.ai/docs/self-hosting/overview)한 뒤 API 키를 설정합니다:

```bash
export LANGWATCH_API_KEY="your-langwatch-api-key"
export GOOGLE_API_KEY="your-gemini-api-key"
```

추적을 초기화합니다:

```python
import langwatch
from openinference.instrumentation.google_adk import GoogleADKInstrumentor

langwatch.setup(
    instrumentors=[GoogleADKInstrumentor()]
)
```

이제 끝입니다. 모든 ADK 에이전트 활동이 자동으로 추적되어 LangWatch 대시보드로 전송됩니다.

## 관찰하기

추적을 초기화한 뒤 평소처럼 ADK 에이전트를 실행하면 모든 상호작용이 LangWatch에 나타납니다:

```python
import langwatch
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types
from openinference.instrumentation.google_adk import GoogleADKInstrumentor

langwatch.setup(
    instrumentors=[GoogleADKInstrumentor()]
)

# 도구 정의
def get_weather(city: str) -> dict:
    """지정한 도시의 현재 날씨 보고서를 가져옵니다.

    Args:
        city (str): 도시 이름입니다.

    Returns:
        dict: 상태와 결과 또는 오류 메시지입니다.
    """
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": (
                "The weather in New York is sunny with a temperature of 25 degrees"
                " Celsius (77 degrees Fahrenheit)."
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available.",
        }

# 도구가 포함된 에이전트 생성
agent = Agent(
    name="weather_agent",
    model="gemini-flash-latest",
    description="날씨 관련 질문에 답하는 에이전트입니다.",
    instruction="사용 가능한 도구를 반드시 사용해 답을 찾아야 합니다.",
    tools=[get_weather],
)

app_name = "weather_app"
user_id = "test_user"
session_id = "test_session"
runner = InMemoryRunner(agent=agent, app_name=app_name)
session_service = runner.session_service

await session_service.create_session(
    app_name=app_name,
    user_id=user_id,
    session_id=session_id,
)

# 에이전트 실행 - 모든 상호작용이 추적됩니다
async for event in runner.run_async(
    user_id=user_id,
    session_id=session_id,
    new_message=types.Content(
        role="user",
        parts=[types.Part(text="What is the weather in New York?")],
    ),
):
    if event.is_final_response():
        print(event.content.parts[0].text.strip())
```

## 사용자 지정 메타데이터 추가

`@langwatch.trace()` 데코레이터를 사용해 추적에 추가 컨텍스트를 연결합니다:

```python
@langwatch.trace(name="ADK Weather Agent")
def run_agent(user_message: str):
    current_trace = langwatch.get_current_trace()
    if current_trace:
        current_trace.update(
            metadata={
                "user_id": "user_123",
                "agent_name": "weather_agent",
                "environment": "production",
            }
        )

    user_msg = types.Content(
        role="user", parts=[types.Part(text=user_message)]
    )
    for event in runner.run(
        user_id="demo-user",
        session_id="demo-session",
        new_message=user_msg,
    ):
        if event.is_final_response():
            return event.content.parts[0].text

    return "No response generated"
```

## 지원 및 자료

- [LangWatch 문서](https://langwatch.ai/docs)
- [ADK 통합 가이드](https://langwatch.ai/docs/integration/python/integrations/google-ai)
- [GitHub의 LangWatch 저장소](https://github.com/langwatch/langwatch)
- [커뮤니티 Discord](https://discord.gg/langwatch)
