---
catalog_title: Temporal
catalog_description: 복원력 있고 확장 가능한 에이전트, 장기 실행 에이전트와 도구, 사람 승인, 안전한 버전 관리
catalog_icon: /integrations/assets/temporal.png
catalog_tags: ["resilience"]
---

# ADK용 Temporal 플러그인

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Temporal](https://temporal.io)는 ADK 에이전트를 복원력 있고 확장 가능하며 프로덕션에 적합하게 만들어 주는 범용 지속 실행 플랫폼입니다.
LLM 호출과 도구 실행은 자동 재시도와 복구가 포함된 Temporal [Activity](https://docs.temporal.io/activities)로 실행됩니다.
어떤 일이 실패하더라도 에이전트는 정확히 중단된 지점에서 다시 이어서 실행되며, 수동 세션 관리나 외부 데이터베이스가 필요하지 않습니다.

## 사용 사례

Temporal 플러그인은 에이전트에 다음 기능을 제공합니다.

- **지속 실행**: 진행 상황을 절대 잃지 않습니다. 에이전트가 충돌하거나 멈추더라도 Temporal은 마지막으로 성공한 단계에서 자동으로 복구하며, 수동 [세션 재개](/runtime/resume/#resume-a-stopped-workflow)가 필요하지 않습니다.
- **내장 재시도 및 속도 제한**: 백오프가 포함된 구성 가능한 [재시도 정책](https://docs.temporal.io/encyclopedia/retry-policies)과 LLM 제공업체의 백프레셔를 처리하는 메커니즘을 제공합니다.
- **장기 실행 및 상시 실행 에이전트**: 블로킹 await를 사용해 몇 시간, 며칠 또는 무기한 실행되는 에이전트와 도구를 지원합니다.
- **Human-in-the-loop**: 사람이 승인할 때까지 실행을 일시 중지한 뒤 중단한 지점에서 다시 시작합니다. Temporal의 [작업 라우팅](https://docs.temporal.io/task-routing)은 들어오는 신호(예: 사용자 채팅이나 승인)를 올바른 워크플로로 확장성 있게 전달합니다.
- **관찰 가능성 및 디버깅**: 에이전트 실행의 모든 단계를 검사하고, 워크플로를 결정론적으로 재생하며, [Temporal UI](https://docs.temporal.io/web-ui)를 사용해 실패 지점을 정확히 찾아낼 수 있습니다.

## 사전 요구 사항

- Python 3.10+
- [Gemini API 키](https://aistudio.google.com/app/api-keys)(또는 [지원되는 모델](/agents/models/) 중 하나)
- 실행 중인 Temporal 서버([로컬 개발 서버](https://docs.temporal.io/cli#start-dev-server), [자가 호스팅](https://docs.temporal.io/self-hosted-guide), 또는 [Temporal Cloud](https://temporal.io/cloud))
- Temporal Python SDK [1.24.0](https://github.com/temporalio/sdk-python/releases/tag/1.24.0)

Temporal Python 1.24.0 기준으로 이 통합은 실험 단계이며, 향후 호환성이 깨지는 변경이 있을 수 있습니다.


## 설치

google-adk extra와 함께 Temporal Python SDK를 설치합니다:

```bash
pip install "temporalio[google-adk]"
```

## 에이전트에서 사용

### 기본 설정

이 통합은 **워크플로 측**(에이전트가 실행되는 곳)과 **워커 측**(실행 환경을 호스팅하는 곳)의 두 부분으로 나뉩니다.

**1. 에이전트와 워크플로 정의**

ADK 에이전트를 만들고 Temporal Workflow로 감쌉니다. `TemporalModel`을 사용해 LLM 호출을 Temporal Activity를 통해 라우팅합니다.

```python
from contextlib import aclosing
from datetime import timedelta
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types
from temporalio import activity, workflow
from temporalio.common import RetryPolicy
from temporalio.contrib.google_adk_agents import TemporalModel
from temporalio.contrib.google_adk_agents.workflow import activity_tool
from temporalio.workflow import ActivityConfig

# Temporal 작업을 정의합니다

@activity.defn
async def get_weather(city: str) -> str:
    """도시의 현재 날씨를 가져옵니다."""
    # 여기에 날씨 API 호출을 넣습니다.
    return f"72°F and sunny in {city}"

# Activity를 ADK 도구로 감쌉니다. 이 도구는 memoization, retry, timeout이 적용됩니다.
weather_tool = activity_tool(
    get_weather,
    start_to_close_timeout=timedelta(seconds=30),
    retry_policy=RetryPolicy(maximum_attempts=3),
)

# 에이전트 사용
agent = Agent(
    name="weather_agent",
    model=TemporalModel(
      "gemini-2.5-pro",
      activity_config=ActivityConfig(summary="Weather Agent")),
    tools=[weather_tool],
)

# 에이전트를 Workflow에 넣어 지속 실행을 제공합니다.

@workflow.defn
class WeatherAgentWorkflow:
    @workflow.run
    async def run(self, user_message: str) -> str:
        # 테스트용이며, 프로덕션에서는 Runner()를 사용합니다.
        runner = InMemoryRunner(agent=agent, app_name="weather_app")
        session = await runner.session_service.create_session(
            user_id="user", app_name="weather_app"
        )
        result = ""
        async with aclosing(runner.run_async(
            user_id="user",
            session_id=session.id,
            new_message=types.Content(
                role="user", parts=[types.Part.from_text(text=user_message)]
            ),
        )) as events:
            async for event in events:
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            result = part.text
        return result
```

**2. 워커 구성 및 시작**

`GoogleAdkPlugin`을 사용해 워커를 구성하면, 분산 시스템의 Workflow 안에서 ADK를 실행할 준비가 됩니다:

```python
import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from temporalio.contrib.google_adk_agents import GoogleAdkPlugin

async def main():
    client = await Client.connect(
        "localhost:7233",
        plugins=[GoogleAdkPlugin()]
    )

    worker = Worker(
        client,
        task_queue="my-agent-task-queue",
        workflows=[WeatherAgentWorkflow],
        activities=[get_weather],
    )
    await worker.run()

asyncio.run(main())
```

**3. Workflow 실행 시작**

```python
import asyncio
from temporalio.client import Client
from temporalio.contrib.google_adk_agents import GoogleAdkPlugin

async def start():
    client = await Client.connect(
        "localhost:7233",
        plugins=[GoogleAdkPlugin()]
    )
    result = await client.execute_workflow(
        WeatherAgentWorkflow.run,
        "What's the weather in San Francisco?",
        id="weather-agent-1",
        task_queue="my-agent-task-queue",
    )
    print(result)

asyncio.run(start())
```


### MCP 도구 사용

[MCP](/mcp/) 도구를 Temporal Activity로 실행합니다:

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from temporalio.client import Client
from temporalio.contrib.google_adk_agents import (
    GoogleAdkPlugin,
    TemporalModel,
    TemporalMcpToolSet,
    TemporalMcpToolSetProvider,
)

# 필요할 때 Temporal이 MCPToolset을 인스턴스화할 수 있도록 팩토리를 정의합니다.
toolset_provider = TemporalMcpToolSetProvider(
    "my-tools",
    lambda _: McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"],
            ),
        ),
    ),
)

# 도구 세트 프로바이더로 클라이언트를 구성합니다.
client = await Client.connect(
    "localhost:7233",
    plugins=[GoogleAdkPlugin(toolset_providers=[toolset_provider])]
)

# Agent를 선언할 때( @workflow.run 내부) 이름으로 도구 세트를 참조합니다.
agent = Agent(
    name="tool_agent",
    model=TemporalModel("gemini-2.5-pro"),
    tools=[TemporalMcpToolSet("my-tools")],
)
```

## 동작 방식

이 플러그인은 ADK 에이전트가 Temporal Workflow 코드 안에서 결정론적으로 실행되도록 보장하고,
견고한 복구를 위해 입력과 출력을 직렬화하고 기록합니다. 예를 들면 다음과 같습니다.

- **LLM 호출**은 `TemporalModel`을 통해 Temporal Activity로 실행됩니다. 호출이 실패하거나 워커가 충돌하면 Temporal은 마지막으로 성공한 단계에서 재시도하거나 재생하여 복원력을 높이고 토큰 사용량을 줄입니다.
- **비결정적 연산**(`time.time()`, `uuid.uuid4()` 등)은 Workflow 코드에서 실행될 때 Temporal의 결정론적 대체 함수(`workflow.now()`, `workflow.uuid4()`)로 자동 교체됩니다(단, Activity 코드에서는 해당되지 않음).
- **ADK 및 Gemini 모듈**은 자동 passthrough가 적용된 Temporal의 [sandbox](https://docs.temporal.io/develop/python/sandbox-environment) 환경에 맞게 구성됩니다.
- **Pydantic 직렬화**는 ADK의 데이터 타입에 대해 자동으로 구성됩니다.

## 추가 기능

| 기능 | 설명 |
| --- | --- |
| 지속 가능한 도구 실행 | `activity_tool`은 도구 함수를 Activity로 감싸 장기 실행 도구, 자동 재시도, 하트비트를 지원합니다 |
| MCP 도구 지원 | `TemporalMcpToolSet`은 전체 이벤트 전파를 유지하면서 MCP 도구를 Activity로 실행합니다 |
| Human-in-the-loop | Agent Workflow는 [Signals](https://docs.temporal.io/signals)와 [Updates](https://docs.temporal.io/messages#updates)를 기다렸다가 사람 입력을 받을 수 있으며, 클라이언트는 이를 보내 에이전트를 재개할 수 있습니다 |
| 결정론적 런타임 | `GoogleAdkPlugin`은 비결정적 호출을 Temporal-safe 대체 함수로 바꿉니다 |
| 디버깅 용이성 | 모든 LLM 호출과 도구 실행이 Temporal UI에서 Activity로 보이므로 오류를 쉽게 디버깅할 수 있습니다 |
| 관찰 가능성 | OpenTelemetry를 사용해 즐겨 쓰는 관찰 가능성 솔루션과 연동할 수 있으며, 프로세스 간 span은 충돌에도 복원력을 가집니다 |
| 안전한 버전 관리 | 진행 중인 실행을 방해하지 않고 [Temporal Worker Versioning](https://docs.temporal.io/production-deployment/worker-deployments/worker-versioning)을 사용해 새 에이전트 버전을 배포할 수 있습니다 |
| 다중 에이전트 오케스트레이션 | Workflow 안에서 여러 에이전트를 구성하거나, [Child Workflows](https://docs.temporal.io/child-workflows) 또는 [Nexus](https://docs.temporal.io/nexus)를 사용해 더 복잡한 사용 사례로 확장할 수 있습니다 |


## 추가 자료

- [Temporal Python SDK 문서](https://docs.temporal.io/develop/python) - Temporal Python SDK의 전체 참조 문서
- [PyPI의 Temporal Python SDK](https://pypi.org/project/temporalio/) - Python 패키지
- [Temporal Cloud](https://temporal.io/cloud) - 관리형 Temporal 서비스
- [Temporal로 ambient agent 오케스트레이션하기](https://temporal.io/blog/orchestrating-ambient-agents-with-temporal) - 장기 실행 에이전트 패턴에 관한 블로그 글
