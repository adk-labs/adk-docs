---
catalog_title: Latitude
catalog_description: ADK 에이전트를 위한 오픈 소스 관측 가능성(observability) 및 성능 평가
catalog_icon: /integrations/assets/latitude.png
catalog_tags: ["observability", "evaluation"]
---

# ADK를 위한 Latitude 관측 가능성(observability) 연동

<div class="language-support-tag">
  <span class="lst-supported">ADK 지원</span><span class="lst-python">Python</span>
</div>

[Latitude](https://latitude.so)는 LLM 애플리케이션을 위한 오픈 소스 관측 가능성(observability) 및 성능 평가 플랫폼입니다. Latitude의 [`latitude-telemetry`](https://pypi.org/project/latitude-telemetry/) Python SDK는 Agent Development Kit 전용 계측(instrumentation)을 제공하므로, 모든 에이전트 실행, 모델 생성, 도구 호출이 OpenTelemetry 트레이스(trace)로 내보내져 직접 검사, 검색, 평가할 수 있습니다.

## ADK용으로 Latitude를 사용하는 이유

ADK는 자체적인 OpenTelemetry 기반 트레이싱을 포함하고 있습니다. Latitude는 에이전트용으로 특별히 설계된 호스팅(또는 자체 호스팅) 플랫폼을 제공하여 이를 확장합니다:

- **전체 에이전트 트레이스**: 중첩된 에이전트, 생성 및 도구 호출 계층 구조를 ADK 호출 방식 변경 없이 자동으로 캡처합니다.
- **비용, 토큰 및 지연 시간**: 트레이스의 모든 레벨에서 집계됩니다.
- **세션 (Sessions)**: 다중 턴(multi-turn) 대화와 다단계 에이전트 실행을 단일 세션으로 그룹화합니다.
- **평가 (Evaluations)**: LLM-as-judge 또는 코드 기반 평가기를 사용하여 에이전트의 출력을 오프라인 또는 프로덕션 환경에서 평가(scoring)합니다.
- **오픈 소스**: 완전히 자체 호스팅(self-hosted)으로 운영하거나 관리형 클라우드 서비스를 사용할 수 있습니다.

## 사전 요구사항

- **Latitude 계정** 및 **API 키** ([console.latitude.so](https://console.latitude.so/login)에서 가입 또는 자체 호스팅).
- **Latitude 프로젝트 슬러그 (project slug)**.
- `GOOGLE_API_KEY`로 설정된 **Gemini API 키**.

## 설치

```bash
pip install latitude-telemetry google-adk
```

필요한 환경 변수를 설정합니다:

```bash
export LATITUDE_API_KEY="your-api-key"
export LATITUDE_PROJECT="your-project-slug"
export GOOGLE_API_KEY="your-gemini-api-key"
```

`LATITUDE_API_KEY`와 `LATITUDE_PROJECT`는 트레이스를 Latitude 프로젝트로 전송합니다. `GOOGLE_API_KEY`는 ADK의 Gemini 모델 호출에 사용됩니다.

## 에이전트와 함께 사용하기

Latitude SDK의 `google_adk` 계측 키 아래에 `google.adk` 모듈을 전달합니다. Latitude는 OpenTelemetry 트레이서 공급자(tracer provider)를 등록하고 ADK를 계측합니다. 여러분은 지금처럼 ADK를 그대로 호출하시면 됩니다.

```python
import asyncio
import os

import google.adk
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

from latitude_telemetry import Latitude, capture

latitude = Latitude(
    api_key=os.environ["LATITUDE_API_KEY"],
    project=os.environ["LATITUDE_PROJECT"],
    instrumentations={"google_adk": google.adk},
)


def get_weather(city: str) -> dict:
    """Returns the current weather for a city."""
    return {"status": "success", "report": f"The weather in {city} is sunny."}


agent = Agent(
    name="weather_agent",
    model="gemini-flash-latest",
    description="Agent that answers weather questions using tools.",
    instruction="Answer weather questions using get_weather.",
    tools=[get_weather],
)


async def weather_agent_run():
    runner = InMemoryRunner(agent=agent, app_name="weather_app")
    await runner.session_service.create_session(
        app_name="weather_app",
        user_id="user_123",
        session_id="session_abc",
    )

    async for event in runner.run_async(
        user_id="user_123",
        session_id="session_abc",
        new_message=types.Content(
            role="user",
            parts=[types.Part(text="What's the weather in Barcelona?")],
        ),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            return event.content.parts[0].text


# capture()를 사용해 요청이나 작업을 래핑하여 생성되는 모든 스팬(span)에 user_id, session_id, 태그 또는 메타데이터를 연결합니다.
capture("weather-agent-run", lambda: asyncio.run(weather_agent_run()))

# 프로세스가 종료되기 전에 대기 중인 모든 스팬(span)을 플러시(flush)하고 종료합니다.
latitude.shutdown()
```

## 제공되는 혜택

각 에이전트 실행은 Latitude에서 중첩된 스팬(span)을 가진 트레이스(trace)로 나타납니다:

- **에이전트 스팬 (Agent spans)**: 에이전트 이름, 지시사항(instruction) 및 구성된 도구
- **생성 스팬 (Generation spans)**: 모델, 입력/출력 메시지 및 토큰 사용량
- **도구 스팬 (Tool spans)**: 입력 인자 및 출력을 포함하는 도구 호출

[Latitude 대시보드](https://console.latitude.so/login)에서 프로젝트를 열어 토큰 사용량과 지연 시간이 모든 레벨에서 집계된 전체 에이전트, 생성, 도구 계층 구조를 확인하세요.

## 리소스

- [Latitude 공식 문서](https://docs.latitude.so)
- [Latitude ADK 연동 가이드](https://docs.latitude.so/telemetry/frameworks/google-adk)
- [GitHub의 Latitude 저장소](https://github.com/latitude-dev/latitude-llm)
