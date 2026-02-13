---
catalog_title: Phoenix
catalog_description: LLM 애플리케이션을 위한 오픈소스·셀프호스팅 관측성, 추적, 평가를 제공합니다
catalog_icon: /adk-docs/integrations/assets/phoenix.png
catalog_tags: ["observability"]
---
# Phoenix를 사용한 에이전트 관측성(Observability)

[Phoenix](https://arize.com/docs/phoenix)는 대규모 LLM 애플리케이션 및 AI 에이전트를 모니터링, 디버깅, 개선하기 위한 오픈소스 셀프 호스팅 관측성 플랫폼입니다. Google ADK 애플리케이션을 위한 포괄적인 추적 및 평가 기능을 제공합니다. 시작하려면 [무료 계정](https://phoenix.arize.com/)에 가입하세요.

## 개요

Phoenix는 [OpenInference 계측](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-google-adk)을 사용하여 Google ADK에서 트레이스를 자동으로 수집할 수 있으며, 이를 통해 다음을 수행할 수 있습니다.

-   **에이전트 상호작용 추적** - 모든 에이전트 실행, 툴 호출, 모델 요청 및 응답을 전체 컨텍스트 및 메타데이터와 함께 자동으로 캡처
-   **성능 평가** - 사용자 지정 또는 사전 빌드된 평가기를 사용하여 에이전트 동작을 평가하고, 에이전트 구성을 테스트하기 위한 실험 실행
-   **문제 디버깅** - 상세한 트레이스를 분석하여 병목 현상, 실패한 툴 호출 및 예기치 않은 에이전트 동작을 신속하게 식별
-   **셀프 호스팅 제어** - 자체 인프라에 데이터를 보관

## 설치

### 1. 필요한 패키지 설치

```bash
pip install openinference-instrumentation-google-adk google-adk arize-phoenix-otel
```

## 설정

### 1. Phoenix 실행

이 지침은 Phoenix Cloud를 사용하는 방법을 보여줍니다. 노트북, 터미널 또는 컨테이너를 사용한 셀프 호스팅을 통해 [Phoenix를 실행](https://arize.com/docs/phoenix/integrations/llm-providers/google-gen-ai/google-adk-tracing)할 수도 있습니다.

먼저, [무료 Phoenix 계정](https://phoenix.arize.com/)에 가입하세요.

**Phoenix 엔드포인트와 API 키를 설정하세요:**

```python
import os

# 추적을 위한 Phoenix API 키 추가
PHOENIX_API_KEY = "YOUR_API_KEY_HERE"
os.environ["PHOENIX_CLIENT_HEADERS"] = f"api_key={PHOENIX_API_KEY}"
os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = "https://app.phoenix.arize.com"
```

**Phoenix API 키**는 대시보드의 Keys 섹션에서 찾을 수 있습니다.

### 2. 애플리케이션을 Phoenix에 연결

```python
from phoenix.otel import register

# Phoenix 트레이서 구성
tracer_provider = register(
    project_name="my-llm-app",  # 기본값은 'default'입니다
    auto_instrument=True        # 설치된 OI 의존성에 기반하여 앱을 자동으로 계측합니다
)
```

## 관찰

이제 추적 설정이 완료되었으므로, 모든 Google ADK SDK 요청은 관측성 및 평가를 위해 Phoenix로 스트리밍됩니다.

```python
import nest_asyncio
nest_asyncio.apply()

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

# 툴 함수 정의
def get_weather(city: str) -> dict:
    """지정된 도시의 현재 날씨 보고서를 검색합니다.

    매개변수:
        city (str): 날씨 보고서를 검색할 도시의 이름.

    반환값:
        dict: 상태와 결과 또는 오류 메시지.
    """
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": (
                "뉴욕의 날씨는 맑고 기온은 섭씨 25도(화씨 77도)입니다."
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"'{city}'의 날씨 정보는 제공되지 않습니다.",
        }

# 툴을 사용하여 에이전트 생성
agent = Agent(
    name="weather_agent",
    model="gemini-2.0-flash-exp",
    description="날씨 툴을 사용하여 질문에 답변하는 에이전트.",
    instruction="답을 찾으려면 사용 가능한 툴을 사용해야 합니다.",
    tools=[get_weather]
)

app_name = "weather_app"
user_id = "test_user"
session_id = "test_session"
runner = InMemoryRunner(agent=agent, app_name=app_name)
session_service = runner.session_service

await session_service.create_session(
    app_name=app_name,
    user_id=user_id,
    session_id=session_id
)

# 에이전트 실행 (모든 상호작용이 추적됩니다)
async for event in runner.run_async(
    user_id=user_id,
    session_id=session_id,
    new_message=types.Content(role="user", parts=[
        types.Part(text="뉴욕의 날씨는 어떤가요?")]
    )
):
    if event.is_final_response():
        print(event.content.parts[0].text.strip())
```

## 지원 및 리소스
-   [Phoenix 문서](https://arize.com/docs/phoenix/integrations/llm-providers/google-gen-ai/google-adk-tracing)
-   [커뮤니티 슬랙](https://arize-ai.slack.com/join/shared_invite/zt-11t1vbu4x-xkBIHmOREQnYnYDH1GDfCg#/shared-invite/email)
-   [OpenInference 패키지](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-google-adk)
