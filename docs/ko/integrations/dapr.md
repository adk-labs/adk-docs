---
catalog_title: Dapr
catalog_description: 사용자 승인과 안전한 버전 관리를 지원하는 내구성 있는 장기 실행·자가 복구 에이전트
catalog_icon: /integrations/assets/dapr.png
catalog_tags: ["resilience"]
---

# ADK용 Dapr 플러그인

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span>
</div>

[Dapr](https://dapr.io)는 ADK 에이전트가 장애 상황에서도 안정적으로 동작하도록 지원하는 분산
워크플로 오케스트레이션 엔진입니다. LLM 호출과 도구 실행은 자동 재시도 및 복구가
적용되는 Dapr
[Workflow](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-overview/)
액티비티(activity)로 실행됩니다. 장애가 발생하더라도 에이전트는 중단된 바로 그 지점부터 자동으로
실행을 이어갑니다.

## 사용 사례

Dapr 플러그인은 에이전트에 다음 기능을 제공합니다.

- **내구성 있는 실행(Durable execution):** 진행 상태를 잃지 않습니다. 에이전트가 비정상 종료(crash)되거나 멈추더라도
  Dapr가 마지막으로 성공한 액티비티부터 자동 복구하므로 [수동 재개](/ko/runtime/resume/)가
  필요하지 않습니다.
- **내장 재시도 및 백오프:** LLM 제공자와 도구 API의 일시적 장애를 처리할 수
  있도록 지수 백오프(exponential backoff)가 적용된 구성 가능한 [재시도
  정책](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-features-concepts/#retry-policies)을
  제공합니다.
- **장기 실행 및 상시 동작(ambient) 에이전트:** Dapr의 영구 상태 저장소(state store)를 기반으로 몇 시간,
  며칠 또는 무기한 실행되는 에이전트와 도구를 지원합니다.
- **이식 가능한 인프라:** 에이전트 코드를 변경하지 않고 Redis, GCP Firestore,
  PostgreSQL, DynamoDB, Cosmos DB 등 15개 이상의 데이터베이스와 [다양한 상태
  저장소](https://docs.dapr.io/reference/components-reference/supported-state-stores/)를
  교체할 수 있습니다. Dapr의 플러그인형 컴포넌트 모델을 통해 로컬 개발 환경에서 어떤
  클라우드로든 손쉽게 이전할 수 있습니다.
- **관측성 및 디버깅:** Dapr 워크플로 API로 에이전트 실행의 모든 단계를 검사하고,
  Dapr의 내장 [OpenTelemetry
  연동](https://docs.dapr.io/operations/observability/tracing/tracing-overview/)을
  통해 트레이스와 메트릭을 내보냅니다.

## 사전 요구사항

- Python 3.11+
- [Gemini API 키](https://aistudio.google.com/app/api-keys) 또는 임의의
  [지원 모델](/ko/agents/models/)
- Dapr CLI 및 런타임 설치([설치
  가이드](https://docs.dapr.io/getting-started/install-dapr-cli/))
- 워크플로 영구 저장을 위한 Dapr [상태 저장소
  컴포넌트](https://docs.dapr.io/reference/components-reference/supported-state-stores/) 구성

## 설치

ADK 확장이 포함된 Dapr용 [Diagrid Agent 패키지](https://pypi.org/project/diagrid/)를
설치합니다.

```bash
pip install diagrid
```

Dapr를 초기화합니다.

```bash
dapr init
```

## 에이전트와 함께 사용하기

### 기본 설정

이 통합은 각 LLM 호출과 도구 실행이 내구성 있는 Dapr Workflow 액티비티로 실행되도록
ADK 에이전트를 래핑합니다. 러너는 워크플로 등록을 처리하고, Dapr 워크플로
런타임을 시작하며, 에이전트를 호출하기 위한 비동기 인터페이스를 제공합니다.

**에이전트와 러너 정의**

평소처럼 ADK 에이전트를 생성하고 `DaprWorkflowAgentRunner`에 전달합니다.

```python
import asyncio
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from diagrid.agent.adk import DaprWorkflowAgentRunner


def get_weather(city: str) -> str:
    """Get the current weather for a city.

    Args:
        city: The name of the city to get weather for.

    Returns:
        A string describing the weather.
    """
    # Your weather API call here
    return f"72°F and sunny in {city}"


# Define the ADK agent
agent = LlmAgent(
    name="weather_agent",
    model="gemini-flash-latest",
    instruction="You are a helpful assistant that can check the weather.",
    tools=[FunctionTool(get_weather)],
)


async def main():
    # Wrap the agent so each tool call runs as a durable Dapr activity
    runner = DaprWorkflowAgentRunner(
        agent=agent,
        name="weather-agent",
        max_iterations=10,
    )

    # Start the Dapr Workflow runtime
    runner.start()

    try:
        async for event in runner.run_async(
            user_message="What's the weather in San Francisco?",
            session_id="session-001",
        ):
            if event["type"] == "workflow_completed":
                print(event["final_response"])
    finally:
        runner.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
```

**Dapr로 에이전트 실행**

Dapr Workflow는 경량 사이드카(sidecar)와 구성된 상태 저장소를 사용합니다. 다음 명령으로
로컬에서 Dapr와 에이전트를 함께 실행합니다.

```bash
dapr run --app-id weather-agent -- python3 agent.py
```

!!! note

    기본적으로 Dapr는 함께 설치된 Redis 컴포넌트(`~/.dapr/components/statestore.yaml`)를
    사용합니다. 사용할 상태 저장소를 변경하려면
    [지원되는 상태 저장소](https://docs.dapr.io/reference/components-reference/supported-state-stores/)를
    참고하세요.

### 장애 복구(Crash recovery)

에이전트를 호스팅하는 프로세스가 실행 도중 비정상 종료되더라도, 앱이 재시작되면 Dapr가
마지막으로 성공한 액티비티부터 워크플로를 자동 재개합니다. 별도의 리플레이(replay) 로직을
구현할 필요가 없습니다.

```python
# First run: process crashes after tool 1 completes.
# Second run: Dapr automatically resumes and executes tools 2 and 3.
runner = DaprWorkflowAgentRunner(agent=agent, name="sequential-agent")
runner.start()

async for event in runner.run_async(
    user_message="Run the three-step pipeline.",
    session_id="pipeline-001",
):
    if event["type"] == "workflow_completed":
        print(event["final_response"])
```

`session_id`와 워크플로 인스턴스 ID가 일정하게 유지되므로, 동일한 앱을 Dapr와 함께 다시
실행하면 사이드카가 진행 중이던 워크플로를 이어받아 완료될 때까지 실행합니다. 수동으로
재개할 필요가 없습니다.

## 작동 방식

플러그인은 ADK 에이전트 루프를 Dapr Workflow로 변환하여 각 단계에서 체크포인트 저장,
재시도, 자동 리플레이가 가능하도록 합니다.

- **LLM 호출**은 Dapr Workflow
  [액티비티](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-features-concepts/#workflow-activities)로
  실행됩니다. 호출이 실패하거나 워커가 비정상 종료되면 Dapr는 구성된 재시도 정책에
  따라 재시도하거나 마지막으로 성공한 액티비티부터 워크플로를 리플레이하여 복원력을
  높이고 토큰 비용을 절감합니다.
- **도구 실행**은 도구 호출당 하나의 독립된 액티비티로 실행됩니다. 워크플로는 Dapr의
  `when_all` 기본 연산(primitive)을 통해 병렬 도구 호출을 팬아웃(fan out)하고, 모든 호출이 완료될 때까지 기다린 뒤
  LLM을 다시 호출합니다.
- **워크플로 상태**(메시지, 도구 호출, 도구 결과)는 매 액티비티 직후 구성된
  Dapr 상태 저장소에 직렬화되어 영구 저장되므로, 상태 저장소에 접근 가능한 어떤 복제본(replica)이든
  실행을 이어받을 수 있습니다.
- **결정론적 오케스트레이션:** `agent_workflow` 함수는 결정론적 제어
  흐름만 포함합니다. 모든 부수 효과(LLM 호출, 도구 호출)는 액티비티 내부에서
  수행되며, 이는 리플레이 안전성을 보장하기 위해 Dapr Workflow가 요구하는 모델입니다.

## 주요 기능

| 기능 | 설명 |
| --- | --- |
| 내구성 있는 도구 실행 | 각 ADK 도구가 Dapr Workflow 액티비티로 실행되며, 실패 시 자동 재시도, 백오프, 리플레이가 적용됩니다 |
| 병렬 도구 호출 | 단일 LLM 응답에서 발생한 여러 도구 호출이 액티비티로 동시에 디스패치되고 다음 LLM 단계 전에 조인(join)됩니다 |
| 이식 가능한 상태 저장소 | 코드 변경 없이 Dapr 컴포넌트를 통해 Redis, GCP Firestore, PostgreSQL, Cosmos DB 등 다양한 상태 저장소를 교체할 수 있습니다 |
| 장기 실행 에이전트 | 워크플로는 몇 시간, 며칠 또는 무기한 실행될 수 있으며, 상태는 완료될 때까지 Dapr 상태 저장소에 영구 저장됩니다 |
| 관측성 | 모든 LLM 호출과 도구 실행이 워크플로 액티비티로 처리되므로 Dapr의 OpenTelemetry 연동으로 추적하고 워크플로 API로 검사할 수 있습니다 |
| Kubernetes 네이티브 | Dapr 사이드카 주입(injection)을 사용해 동일한 에이전트를 코드 변경 없이 Kubernetes에 배포할 수 있습니다 |

## 추가 리소스

- [Dapr Workflow 문서](https://docs.dapr.io/developing-applications/building-blocks/workflow/) - Dapr 워크플로 빌딩 블록 전체 레퍼런스
- [GitHub의 Diagrid Agent SDK](https://github.com/diagridio/python-ai) - Dapr ADK 통합 소스 코드
- [Dapr 커뮤니티 Discord](https://bit.ly/dapr-discord) - 질문, 버그 제보 및 커뮤니티 토론
- [지원되는 상태 저장소](https://docs.dapr.io/reference/components-reference/supported-state-stores/) - Dapr Workflow와 호환되는 상태 저장소 컴포넌트 목록
