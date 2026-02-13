---
catalog_title: Monocle
catalog_description: Open-source observability, tracing, and debugging of LLM applications
catalog_icon: /adk-docs/integrations/assets/monocle.png
catalog_tags: ["observability"]
---
# Monocle을 사용한 에이전트 관측성

[Monocle](https://github.com/monocle2ai/monocle)은 LLM 애플리케이션 및 AI 에이전트 모니터링, 디버깅 및 개선을 위한 오픈 소스 관측성 플랫폼입니다. 자동 계측을 통해 Google ADK 애플리케이션에 대한 포괄적인 추적 기능을 제공합니다. Monocle은 로컬 파일 또는 콘솔 출력 등 다양한 대상으로 내보낼 수 있는 OpenTelemetry 호환 추적을 생성합니다.

## 개요

Monocle은 Google ADK 애플리케이션을 자동으로 계측하여 다음을 수행할 수 있도록 합니다.

- **에이전트 상호 작용 추적** - 모든 에이전트 실행, 도구 호출 및 모델 요청을 전체 컨텍스트 및 메타데이터와 함께 자동으로 캡처
- **실행 흐름 모니터링** - 상세한 추적을 통해 에이전트 상태, 위임 이벤트 및 실행 흐름 추적
- **문제 디버그** - 상세한 추적을 분석하여 병목 현상, 실패한 도구 호출 및 예기치 않은 에이전트 동작을 신속하게 식별
- **유연한 내보내기 옵션** - 분석을 위해 추적을 로컬 파일 또는 콘솔로 내보내기
- **OpenTelemetry 호환** - 모든 OTLP 호환 백엔드에서 작동하는 표준 OpenTelemetry 추적 생성

Monocle은 다음 Google ADK 구성 요소를 자동으로 계측합니다.

- **`BaseAgent.run_async`** - 에이전트 실행, 에이전트 상태 및 위임 이벤트를 캡처합니다.
- **`FunctionTool.run_async`** - 도구 이름, 매개변수 및 결과를 포함한 도구 실행을 캡처합니다.
- **`Runner.run_async`** - 요청 컨텍스트 및 실행 흐름을 포함한 Runner 실행을 캡처합니다.

## 설치

### 1. 필수 패키지 설치 { #install-required-packages }

```bash
pip install monocle_apptrace google-adk
```

## 설정

### 1. Monocle 텔레메트리 구성 { #configure-monocle-telemetry }

Monocle은 텔레메트리를 초기화할 때 Google ADK를 자동으로 계측합니다. 애플리케이션 시작 시 `setup_monocle_telemetry()`를 호출하기만 하면 됩니다.

```python
from monocle_apptrace import setup_monocle_telemetry

# Monocle 텔레메트리 초기화 - Google ADK를 자동으로 계측합니다.
setup_monocle_telemetry(workflow_name="my-adk-app")
```

이게 전부입니다! Monocle은 Google ADK 에이전트, 도구 및 러너를 자동으로 감지하고 계측합니다.

### 2. 익스포터 구성 (선택 사항) { #configure-exporters }

기본적으로 Monocle은 로컬 JSON 파일로 추적을 내보냅니다. 환경 변수를 사용하여 다른 익스포터를 구성할 수 있습니다.

#### 콘솔로 내보내기 (디버깅용)

환경 변수 설정:

```bash
export MONOCLE_EXPORTER="console"
```

#### 로컬 파일로 내보내기 (기본값)

```bash
export MONOCLE_EXPORTER="file"
```

또는 단순히 `MONOCLE_EXPORTER` 변수를 생략합니다. 기본값은 `file`입니다.

## 관찰

이제 추적 설정이 완료되었으므로 모든 Google ADK SDK 요청은 Monocle에 의해 자동으로 추적됩니다.

```python
from monocle_apptrace import setup_monocle_telemetry
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

# Monocle 텔레메트리 초기화 - ADK 사용 전에 호출해야 합니다.
setup_monocle_telemetry(workflow_name="weather_app")

# 도구 함수 정의
def get_weather(city: str) -> dict:
    """지정된 도시에 대한 현재 날씨 보고서를 검색합니다.

    Args:
        city (str): 날씨 보고서를 검색할 도시의 이름입니다.

    Returns:
        dict: 상태 및 결과 또는 오류 메시지입니다.
    """
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": (
                "뉴욕의 날씨는 섭씨 25도(화씨 77도)로 맑습니다."
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"'{city}'에 대한 날씨 정보를 사용할 수 없습니다.",
        }

# 도구가 있는 에이전트 생성
agent = Agent(
    name="weather_agent",
    model="gemini-2.0-flash-exp",
    description="날씨 도구를 사용하여 질문에 답변하는 에이전트.",
    instruction="사용 가능한 도구를 사용하여 답변을 찾아야 합니다.",
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

# 에이전트 실행 (모든 상호 작용은 자동으로 추적됩니다.)
async for event in runner.run_async(
    user_id=user_id,
    session_id=session_id,
    new_message=types.Content(role="user", parts=[
        types.Part(text="뉴욕의 날씨는 어떻습니까?")]
    )
):
    if event.is_final_response():
        print(event.content.parts[0].text.strip())
```

## 추적 액세스

기본적으로 Monocle은 로컬 디렉토리 `./monocle`에 JSON 파일로 추적을 생성합니다. 파일 이름 형식은 다음과 같습니다.

```
monocle_trace_{workflow_name}_{trace_id}_{timestamp}.json
```

각 추적 파일에는 다음을 캡처하는 OpenTelemetry 호환 스팬 배열이 포함되어 있습니다.

- **에이전트 실행 스팬** - 에이전트 상태, 위임 이벤트 및 실행 흐름
- **도구 실행 스팬** - 도구 이름, 입력 매개변수 및 출력 결과
- **LLM 상호 작용 스팬** - 모델 호출, 프롬프트, 응답 및 토큰 사용량(Gemini 또는 다른 LLM을 사용하는 경우)

이러한 추적 파일은 OpenTelemetry 호환 도구를 사용하거나 사용자 지정 분석 스크립트를 작성하여 분석할 수 있습니다.

## VS Code 확장으로 추적 시각화

[Okahu Trace Visualizer](https://marketplace.visualstudio.com/items?itemName=OkahuAI.okahu-ai-observability) VS Code 확장은 Visual Studio Code에서 Monocle이 생성한 추적을 직접 시각화하고 분석하는 대화형 방법을 제공합니다.

### 설치

1. VS Code를 엽니다.
2. `Ctrl+P`(Mac에서는 `Cmd+P`)를 눌러 빠른 열기를 엽니다.
3. 다음 명령어를 붙여넣고 Enter 키를 누릅니다.

```
ext install OkahuAI.okahu-ai-observability
```

또는 [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=OkahuAI.okahu-ai-observability)에서 설치할 수 있습니다.

### 기능

확장 기능은 다음을 제공합니다.

- **사용자 지정 활동 표시줄 패널** - 추적 파일 관리를 위한 전용 사이드바
- **대화형 파일 트리** - 사용자 지정 React UI로 추적 파일 찾아보기 및 선택
- **분할 보기 분석** - JSON 데이터 뷰어와 함께 Gantt 차트 시각화
- **실시간 통신** - VS Code와 React 구성 요소 간의 원활한 데이터 흐름
- **VS Code 테마 지정** - VS Code의 밝은/어두운 테마와 완벽하게 통합

### 사용법

1. Monocle 추적이 활성화된 ADK 애플리케이션을 실행한 후 `./monocle` 디렉토리에 추적 파일이 생성됩니다.
2. VS Code 활동 표시줄에서 Okahu Trace Visualizer 패널을 엽니다.
3. 대화형 파일 트리에서 추적 파일을 찾아보고 선택합니다.
4. 다음을 사용하여 추적을 봅니다.
   - **Gantt 차트 시각화** - 스팬의 타임라인 및 계층 구조 보기
   - **JSON 데이터 뷰어** - 상세 스팬 속성 및 이벤트 검사
   - **토큰 수** - LLM 호출에 대한 토큰 사용량 보기
   - **오류 배지** - 실패한 작업을 신속하게 식별

![Monocle VS Code 확장](../assets/monocle-vs-code-ext.png)

## 추적되는 내용

Monocle은 Google ADK에서 다음 정보를 자동으로 캡처합니다.

- **에이전트 실행**: 에이전트 상태, 위임 이벤트 및 실행 흐름
- **도구 호출**: 도구 이름, 입력 매개변수 및 출력 결과
- **러너 실행**: 요청 컨텍스트 및 전반적인 실행 흐름
- **시간 정보**: 각 작업의 시작 시간, 종료 시간 및 지속 시간
- **오류 정보**: 예외 및 오류 상태

모든 추적은 OpenTelemetry 형식으로 생성되어 모든 OTLP 호환 관측성 백엔드와 호환됩니다.

## 지원 및 리소스

- [Monocle 문서](https://docs.okahu.ai/monocle_overview/)
- [Monocle GitHub 저장소](https://github.com/monocle2ai/monocle)
- [Google ADK Travel Agent 예시](https://github.com/okahu-demos/adk-travel-agent)
- [Discord 커뮤니티](https://discord.gg/D8vDbSUhJX)
