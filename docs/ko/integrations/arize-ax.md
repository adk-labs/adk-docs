---
catalog_title: Arize AX
catalog_description: LLM 애플리케이션을 위한 프로덕션급 관측성, 디버깅, 성능 개선을 지원합니다
catalog_icon: /adk-docs/integrations/assets/arize.png
catalog_tags: ["observability"]
---
# Arize AX를 사용한 에이전트 관측성(Observability)

[Arize AX](https://arize.com/docs/ax)는 대규모 LLM 애플리케이션 및 AI 에이전트를 모니터링, 디버깅, 개선하기 위한 프로덕션 등급의 관측성 플랫폼입니다. Google ADK 애플리케이션을 위한 포괄적인 추적, 평가, 모니터링 기능을 제공합니다. 시작하려면 [무료 계정](https://app.arize.com/auth/join)에 가입하세요.

오픈소스, 셀프 호스팅 대안으로는 [Phoenix](https://arize.com/docs/phoenix)를 확인해보세요.

## 개요

Arize AX는 [OpenInference 계측](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-google-adk)을 사용하여 Google ADK에서 트레이스를 자동으로 수집할 수 있으며, 이를 통해 다음을 수행할 수 있습니다.

-   **에이전트 상호작용 추적** - 모든 에이전트 실행, 툴 호출, 모델 요청 및 응답을 컨텍스트 및 메타데이터와 함께 자동으로 캡처
-   **성능 평가** - 사용자 지정 또는 사전 빌드된 평가기를 사용하여 에이전트 동작을 평가하고, 에이전트 구성을 테스트하기 위한 실험 실행
-   **프로덕션 환경에서 모니터링** - 실시간 대시보드 및 알림을 설정하여 성능 추적
-   **문제 디버깅** - 상세한 트레이스를 분석하여 병목 현상, 실패한 툴 호출 및 예기치 않은 에이전트 동작을 신속하게 식별

![에이전트 트레이스](https://storage.googleapis.com/arize-phoenix-assets/assets/images/google-adk-traces.png)

## 설치

필요한 패키지를 설치합니다.

```bash
pip install openinference-instrumentation-google-adk google-adk arize-otel
```

## 설정

### 1. 환경 변수 구성

Google API 키를 설정합니다.

```bash
export GOOGLE_API_KEY=[your_key_here]
```

### 2. 애플리케이션을 Arize AX에 연결

```python
from arize.otel import register

# Arize AX에 등록
tracer_provider = register(
    space_id="your-space-id",      # 앱 스페이스 설정 페이지에서 찾을 수 있습니다
    api_key="your-api-key",        # 앱 스페이스 설정 페이지에서 찾을 수 있습니다
    project_name="your-project-name"  # 원하는 이름으로 지정하세요
)

# OpenInference에서 자동 계측기를 가져와 구성합니다
from openinference.instrumentation.google_adk import GoogleADKInstrumentor

# 자동 계측 완료
GoogleADKInstrumentor().instrument(tracer_provider=tracer_provider)
```

## 관찰

이제 추적 설정이 완료되었으므로, 모든 Google ADK SDK 요청은 관측성 및 평가를 위해 Arize AX로 스트리밍됩니다.

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
## Arize AX에서 결과 보기
![Arize AX의 트레이스](https://storage.googleapis.com/arize-phoenix-assets/assets/images/google-adk-dashboard.png)
![에이전트 시각화](https://storage.googleapis.com/arize-phoenix-assets/assets/images/google-adk-agent.png)
![에이전트 실험](https://storage.googleapis.com/arize-phoenix-assets/assets/images/google-adk-experiments.png)

## 지원 및 리소스
- [Arize AX 문서](https://arize.com/docs/ax/observe/tracing-integrations-auto/google-adk)
- [Arize 커뮤니티 슬랙](https://arize-ai.slack.com/join/shared_invite/zt-11t1vbu4x-xkBIHmOREQnYnYDH1GDfCg#/shared-invite/email)
- [OpenInference 패키지](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-google-adk)
