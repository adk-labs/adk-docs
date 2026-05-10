---
catalog_title: Dapr
catalog_description: 사람 승인과 안전한 버전 관리를 갖춘 durable, long-running, self-recovering 에이전트
catalog_icon: /integrations/assets/dapr.png
catalog_tags: ["resilience"]
---

# ADK용 Dapr 플러그인

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Dapr](https://dapr.io)은 ADK 에이전트가 장애에 견고하게 동작하도록 돕는 분산
workflow orchestration engine입니다. LLM 호출과 도구 실행은 자동 재시도 및 복구가
적용되는 Dapr
[Workflow](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-overview/)
activity로 실행됩니다. 실패가 발생하면 에이전트는 중단된 바로 그 지점부터 자동으로
다시 이어서 실행합니다.

## 사용 사례

Dapr 플러그인은 에이전트에 다음 기능을 제공합니다.

- **Durable execution:** 진행 상태를 잃지 않습니다. 에이전트가 crash 또는 stall되면
  Dapr가 마지막으로 성공한 activity에서 자동 복구하며, [수동 재개](/ko/runtime/resume/)가
  필요 없습니다.
- **내장 재시도 및 backoff:** LLM provider와 tool API의 일시적 장애를 처리할 수
  있도록 exponential backoff가 적용된 구성 가능한 [retry
  policy](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-features-concepts/#retry-policies)를
  제공합니다.
- **Long-running 및 ambient agent:** Dapr의 persistent state store를 기반으로 몇 시간,
  며칠 또는 무기한 실행되는 에이전트와 도구를 지원합니다.
- **이식 가능한 인프라:** 에이전트 코드를 변경하지 않고 Redis, GCP Firestore,
  PostgreSQL, DynamoDB, Cosmos DB 등 15개 이상의 데이터베이스와 [더 많은 state
  store](https://docs.dapr.io/reference/components-reference/supported-state-stores/)를
  교체할 수 있습니다. Dapr의 pluggable component model을 통해 로컬 개발에서 어떤
  클라우드로든 이동할 수 있습니다.
- **관측성 및 디버깅:** Dapr workflow API로 에이전트 실행의 모든 단계를 검사하고,
  Dapr의 내장 [OpenTelemetry
  integration](https://docs.dapr.io/operations/observability/tracing/tracing-overview/)을
  통해 trace와 metric을 내보냅니다.

## 전제 조건

- Python 3.11+
- [Gemini API 키](https://aistudio.google.com/app/api-keys) 또는 임의의
  [지원 모델](/ko/agents/models/)
- Dapr CLI 및 runtime 설치([설치
  가이드](https://docs.dapr.io/getting-started/install-dapr-cli/))
- workflow persistence를 위한 Dapr [state store
  component](https://docs.dapr.io/reference/components-reference/supported-state-stores/) 구성

## 설치

Dapr용 [Diagrid Agent package](https://pypi.org/project/diagrid/)를 설치합니다.
이 패키지에는 ADK extension이 포함되어 있습니다.

```bash
pip install diagrid
```

Dapr를 초기화합니다.

```bash
dapr init
```

## 에이전트와 함께 사용

### 기본 설정

이 통합은 각 LLM 호출과 각 도구 실행이 durable Dapr Workflow activity로 실행되도록
ADK 에이전트를 래핑합니다. runner는 workflow 등록을 처리하고, Dapr workflow
runtime을 시작하며, 에이전트를 호출하기 위한 async 인터페이스를 노출합니다.

**에이전트와 runner 정의**

평소처럼 ADK 에이전트를 만들고 `DaprWorkflowAgentRunner`에 전달합니다.

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

Dapr Workflow는 lightweight sidecar와 구성된 state store를 사용합니다. 다음 명령으로
Dapr를 로컬에서 실행하고 에이전트를 함께 실행합니다.

```bash
dapr run --app-id weather-agent -- python3 agent.py
```

!!! note

    기본적으로 Dapr는 Dapr와 함께 설치된 Redis component를 사용하며, 위치는
    `~/.dapr/components/statestore.yaml`입니다. 사용할 state store를 바꾸려면
    [supported state
    stores](https://docs.dapr.io/reference/components-reference/supported-state-stores/)를
    참고하세요.

### Crash recovery

에이전트를 호스팅하는 프로세스가 실행 중간에 crash되면, 앱이 재시작될 때 Dapr가
마지막으로 성공한 activity부터 workflow를 자동 재개합니다. 별도의 replay 로직은
필요하지 않습니다.

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

`session_id`와 workflow instance ID가 안정적이므로, 같은 앱을 Dapr와 함께 다시
실행하면 sidecar가 진행 중인 workflow를 이어 받아 완료까지 진행합니다. 수동 재개는
필요하지 않습니다.

## 작동 방식

플러그인은 ADK 에이전트 루프를 Dapr Workflow로 변환하여 각 단계가 checkpoint,
retry, 자동 replay될 수 있게 합니다.

- **LLM 호출**은 Dapr Workflow
  [activity](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-features-concepts/#workflow-activities)로
  실행됩니다. 호출이 실패하거나 worker가 crash되면 Dapr는 구성된 retry policy에
  따라 재시도하거나 마지막으로 성공한 activity부터 workflow를 replay하여 resilience를
  높이고 token spend를 줄입니다.
- **도구 실행**은 도구 호출당 하나의 독립 activity로 실행됩니다. workflow는 Dapr의
  `when_all` primitive를 통해 병렬 도구 호출을 fan out하고, 완료될 때까지 기다린 뒤
  LLM을 다시 호출합니다.
- **Workflow state**(message, tool call, tool result)는 모든 activity 이후 구성된
  Dapr state store에 serialize되어 저장되므로, state store에 접근 가능한 어떤 replica도
  실행을 이어 받을 수 있습니다.
- **Deterministic orchestration:** `agent_workflow` 함수는 deterministic control
  flow만 포함합니다. 모든 side effect(LLM 호출, 도구 호출)는 activity 내부에서
  발생하며, 이는 replay safety를 위해 Dapr Workflow가 요구하는 모델입니다.

## 기능

| Capability | Description |
| --- | --- |
| Durable tool execution | 각 ADK 도구가 Dapr Workflow activity로 실행되며, 실패 시 자동 retry, backoff, replay가 적용됩니다 |
| Parallel tool calls | 단일 LLM 응답의 여러 도구 호출이 activity로 동시에 dispatch되고 다음 LLM 단계 전에 join됩니다 |
| Portable state stores | 코드 변경 없이 Dapr component를 통해 Redis, GCP Firestore, PostgreSQL, Cosmos DB 등 여러 state store를 교체합니다 |
| Long-running agents | workflow는 몇 시간, 며칠 또는 무기한 실행될 수 있으며, state는 완료될 때까지 Dapr state store에 남아 있습니다 |
| Observability | 모든 LLM 호출과 도구 실행은 workflow activity이며, Dapr의 OpenTelemetry integration으로 trace하고 workflow API로 검사할 수 있습니다 |
| Kubernetes-native | Dapr sidecar injection을 사용해 같은 에이전트를 코드 변경 없이 Kubernetes에 배포합니다 |

## 추가 리소스

- [Dapr Workflow documentation](https://docs.dapr.io/developing-applications/building-blocks/workflow/) - Dapr workflow building block 전체 reference
- [Diagrid Agent SDK on GitHub](https://github.com/diagridio/python-ai) - Dapr ADK 통합 소스 코드
- [Dapr Community Discord](https://bit.ly/dapr-discord) - 질문, 버그 리포트, 커뮤니티 토론
- [Supported state stores](https://docs.dapr.io/reference/components-reference/supported-state-stores/) - Dapr Workflow와 호환되는 state store component 목록
