---
catalog_title: Langfuse
catalog_description: LLM 애플리케이션을 디버깅, 분석 및 반복 개선할 수 있는 오픈소스 AI 엔지니어링 플랫폼
catalog_icon: /integrations/assets/langfuse.png
catalog_tags: ["observability", "evaluation"]
---

# ADK를 위한 Langfuse 관측 가능성(Observability)

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span>
</div>

[Langfuse](https://langfuse.com)는 관측 가능성(observability), 평가(evaluation) 및 프롬프트 관리를 위한 오픈소스 LLM 엔지니어링 플랫폼입니다. OpenTelemetry(OTel) 프로토콜을 사용해 ADK 에이전트의 상세한 트레이스(trace)를 수집하므로 개발 및 프로덕션 환경에서 에이전트 앱을 디버깅하고 평가하며 계속 개선해 나갈 수 있습니다.

## 개요

Langfuse는 OpenTelemetry를 통해 ADK의 트레이스를 수집하며 [AI 엔지니어링 루프(AI Engineering Loop)](https://langfuse.com/academy/ai-engineering-loop)를 지원합니다.

- **[트레이스(Trace)](https://langfuse.com/academy/tracing)**: 프롬프트, 검색된 컨텍스트, 도구 호출, 출력, 지연 시간(latency), 비용을 포함한 요청의 전체 실행 경로 캡처
- **[모니터링(Monitor)](https://langfuse.com/academy/monitoring)**: 평가 방법, 사용자 피드백, 비용 또는 지연 시간 이상 징후를 활용해 시간에 따른 시스템 동작을 추적하고 주의가 필요한 트레이스 감지
- **[데이터세트 구축(Build datasets)](https://langfuse.com/academy/datasets)**: 모니터링의 실제 시나리오와 개발 단계의 예상 시나리오를 재현 가능한 테스트 케이스로 전환
- **[실험(Experiment)](https://langfuse.com/academy/experiments)**: 변수(프롬프트, 모델, 검색 전략 등)를 체계적으로 변경하고 안정적인 기준선(baseline)과 각 변경 사항 비교
- **[평가(Evaluate)](https://langfuse.com/academy/evaluate)**: 수동 검토, 코드 평가기 검사 또는 LLM-as-a-judge 기법을 사용해 결과물이 배포하기에 적합한지 결정

## 설치

필요한 패키지를 설치합니다.

```bash
pip install langfuse "google-adk>=2" openinference-instrumentation-google-adk
```

`google-adk` 2.x 버전은 Python 3.10 이상이 필요합니다. `"google-adk>=2"`로 버전을 고정하면 pip가 현재 ADK 2.x 버전을 최신 상태로 설치합니다.

## 설정

[cloud.langfuse.com](https://cloud.langfuse.com)에 가입하거나 플랫폼을 [자체 호스팅(self-host)](https://langfuse.com/self-hosting)한 다음 API 키를 설정하세요. 프로젝트 설정 페이지에서 키를 발급받을 수 있습니다. 또한 [Gemini API 키](https://aistudio.google.com/app/apikey)도 설정합니다.

```bash
export LANGFUSE_PUBLIC_KEY="pk-lf-..."
export LANGFUSE_SECRET_KEY="sk-lf-..."
export LANGFUSE_BASE_URL="https://cloud.langfuse.com"  # EU 리전
# 기타 리전: https://us.cloud.langfuse.com (미국),
# https://jp.cloud.langfuse.com (일본), https://hipaa.cloud.langfuse.com (HIPAA)
export GOOGLE_API_KEY="your-gemini-api-key"
```

Langfuse 클라이언트를 초기화하고 ADK 계측(instrumentation)을 적용합니다.

```python
from langfuse import get_client
from openinference.instrumentation.google_adk import GoogleADKInstrumentor

langfuse = get_client()

# 연결 검증
if langfuse.auth_check():
    print("Langfuse client is authenticated and ready!")
else:
    print("Authentication failed. Please check your credentials and host.")

GoogleADKInstrumentor().instrument()
```

이것으로 설정이 완료되었습니다. 이제 모든 ADK 에이전트 활동이 자동으로 추적되어 Langfuse 프로젝트로 전송됩니다.

## 관측(Observe)

트레이싱이 초기화되면 평소처럼 ADK 에이전트를 실행하세요. 모든 상호작용이 Langfuse에 표시됩니다.

```python
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

def say_hello():
    return {"greeting": "Hello Langfuse 👋"}

agent = Agent(
    name="hello_agent",
    model="gemini-3.5-flash",
    instruction="Always greet using the say_hello tool.",
    tools=[say_hello],
)

APP_NAME = "hello_app"
USER_ID = "demo-user"
SESSION_ID = "demo-session"

session_service = InMemorySessionService()
# create_session은 비동기 함수이므로 노트북 환경에서는 await를 사용하세요
await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)

runner = Runner(agent=agent, app_name=APP_NAME, session_service=session_service)

user_msg = types.Content(role="user", parts=[types.Part(text="hi")])
for event in runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=user_msg):
    if event.is_final_response():
        if event.content and event.content.parts:
            print(event.content.parts[0].text)
        elif event.error_message:
            print(f"Agent error: {event.error_message}")
```

Langfuse는 `runner.run()`에 전달하는 `user_id`와 `session_id`를 트레이스의 **사용자(user)** 및 **세션(session)**에 자동으로 매핑해 줍니다. 따라서 추가 코드 없이 [사용자](https://langfuse.com/docs/observability/features/users) 및 [세션](https://langfuse.com/docs/observability/features/sessions) 추적 기능을 바로 이용할 수 있습니다.

## 이름 지정 및 필터링 가능한 트레이스

기본적으로 트레이스 이름은 ADK 앱의 이름을 따릅니다. Langfuse에서 트레이스를 편리하게 필터링할 수 있도록 [`propagate_attributes`](https://langfuse.com/docs/observability/sdk/instrumentation)를 사용해 서술적인 트레이스 이름, 태그 및 메타데이터를 설정해 보세요.

이 방식으로 속성을 설정할 때는 비동기 API인 `runner.run_async()`를 사용해야 합니다. 동기 방식의 `runner.run()`은 백그라운드 워커 스레드에서 에이전트를 실행하므로 OpenTelemetry 컨텍스트(및 `propagate_attributes`에서 전달된 속성)가 ADK 스팬에 도달하지 않기 때문입니다.

```python
from langfuse import propagate_attributes

SESSION_ID_2 = "demo-session-2"
await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID_2)

with propagate_attributes(
    trace_name="hello-agent-request",
    tags=["google-adk", "cookbook"],
    metadata={"example": "named-trace"},
):
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID_2, new_message=user_msg):
        if event.is_final_response():
            if event.content and event.content.parts:
                print(event.content.parts[0].text)
            elif event.error_message:
                print(f"Agent error: {event.error_message}")
```

## Langfuse에서 트레이스 확인하기

**Langfuse 대시보드 → Traces**를 열어 에이전트 루프, 도구 호출 및 모델 생성 내역을 점검하세요. 트레이스는 위에서 설정한 사용자, 세션 및 태그별로 필터링할 수 있습니다.

![Langfuse 내 Google ADK 예시 트레이스](https://langfuse.com/images/cookbook/integration-google-adk/google-adk-trace.png)

멀티 에이전트 파이프라인 구축, 사용자 피드백을 활용한 트레이스 점수화 등 다양한 예시는 [Langfuse ADK 통합 가이드](https://langfuse.com/integrations/frameworks/google-adk)를 참고하세요.

## 지원 및 관련 리소스

- [Langfuse 공식 문서](https://langfuse.com/docs)
- [ADK 통합 가이드](https://langfuse.com/integrations/frameworks/google-adk)
- [GitHub Langfuse 저장소](https://github.com/langfuse/langfuse)
