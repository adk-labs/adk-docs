---
catalog_title: DBOS
catalog_description: human approval과 안전한 versioning을 갖춘 resilient, scalable, long-running agent
catalog_icon: /integrations/assets/dbos.png
catalog_tags: ["resilience"]
---

# ADK용 DBOS 플러그인

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[DBOS](https://dbos.dev)는 신뢰할 수 있는 workflow와 AI agent를 만들기 위한 durable
execution framework입니다. ADK와 통합되어 LLM call, tool execution, agent orchestration을
fault-tolerant하고 scalable하게 만듭니다. 에이전트는 crash, deploy, restart 이후에도
정확히 중단된 위치에서 재개되며, 별도 orchestration service 없이 사용자가 소유한
database를 기반으로 동작합니다.

## 사용 사례

DBOS 플러그인은 ADK 에이전트에 production-grade reliability와 orchestration을 추가합니다.

- **Durable execution**: LLM 및 도구 출력을 영속화합니다. crash, deploy, machine failure
  이후에도 진행 상황을 잃거나 side effect를 중복하지 않고 에이전트를 자동 복구합니다. 수동
  [session resumption](/ko/runtime/resume/)은 필요하지 않습니다.
- **내장 retry 및 backoff**: LLM provider와 tool execution의 일시적 실패를 처리하기 위해
  exponential backoff가 포함된 구성 가능한 retry policy를 제공합니다.
- **Long-running agents**: 에이전트와 도구를 몇 시간, 며칠, 몇 달 동안 실행합니다.
- **Human-in-the-loop**: 실행을 일시 중지하고 외부 signal 또는 human approval을 받은 뒤
  나중에 재개합니다.
- **Rate limiting을 갖춘 scalable execution**: workflow 안에서 여러 에이전트를 조합하거나,
  durable queue와 내장 rate limiting을 사용해 분산 worker 전반으로 agent workflow를 확장합니다.
- **Observability 및 management**: [DBOS Console](https://docs.dbos.dev/production/workflow-management)에서
  agent workflow를 inspect, cancel, resume, fork합니다.

## 전제 조건

- Python 3.10+
- [Gemini API key](https://aistudio.google.com/app/api-keys) 또는 지원되는
  [모델](/ko/agents/models/)

## 설치

```bash
pip install dbos-google-adk
```

## 에이전트와 함께 사용

이 통합은 각 LLM call이 durable DBOS workflow step으로 실행되도록 ADK 에이전트를
감쌉니다. `@DBOS.step()`으로 decorate된 tool function은 구성 가능한 retry와 함께
개별적으로 checkpoint됩니다.

### 기본 설정

`Runner`에 `DBOSPlugin`을 추가하고 `@DBOS.workflow()`에서 에이전트를 구동하여
에이전트와 workflow를 정의합니다.

```python
import asyncio
import logging

from dbos import DBOS, DBOSConfig
from dbos_google_adk import DBOSPlugin
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Decorate tool calls with @DBOS.step() for durable execution
@DBOS.step()
async def get_weather(city: str) -> str:
    """Get the weather for a city."""
    return f"Sunny in {city}"

agent = LlmAgent(name="weather", model="gemini-flash-latest", tools=[get_weather])
runner = Runner(
    app_name="my-agent",
    agent=agent,
    plugins=[DBOSPlugin()],
    session_service=InMemorySessionService(),
)

# Drive the agent from a DBOS workflow for durable execution
@DBOS.workflow()
async def run_agent(user_id: str, session_id: str, message: str) -> str:
    new_message = types.Content(role="user", parts=[types.Part.from_text(text=message)])
    async for event in runner.run_async(
        user_id=user_id, session_id=session_id, new_message=new_message
    ):
        if event.is_final_response():
            return event.content.parts[0].text
    return ""


async def main():
    # DBOS checkpoints to SQLite by default. Postgres is recommended for production.
    config: DBOSConfig = {"name": "my-agent", "system_database_url": "sqlite:///dbostest.sqlite"}
    DBOS(config=config)
    DBOS.launch()

    await runner.session_service.create_session(
        app_name="my-agent", user_id="u", session_id="s"
    )
    print(await run_agent("u", "s", "How is the weather in San Francisco?"))


if __name__ == "__main__":
    asyncio.run(main())
```

### Durable event compaction

Durable event compaction을 위해 `DBOSEventSummarizer`로 summarizer를 감싸면 compaction
LLM call도 checkpoint됩니다.

```python
from dbos_google_adk import DBOSEventSummarizer
from google.adk.models.google_llm import Gemini

summarizer = DBOSEventSummarizer.from_llm(Gemini(model="gemini-flash-latest"))
```

## 동작 방식

`DBOSPlugin`과 `DBOSEventSummarizer`는 ADK 에이전트를 durable DBOS workflow 안에서
실행합니다.

- **LLM call**은 `DBOSPlugin`이 intercept하여 DBOS step으로 실행합니다. 호출이 실패하거나
  worker가 crash되면 DBOS는 마지막으로 성공한 step부터 재개하여 낭비되는 token spend를
  줄입니다.
- **Tool function**은 `@DBOS.step()`으로 decorate하면 개별적으로 checkpoint됩니다. 출력은
  database에 저장되므로 replay는 이미 완료된 tool execution을 완전히 건너뜁니다.
- **Workflow execution**은 모든 step 후에 database(SQLite 또는 Postgres)에 serialize되어
  저장됩니다. 같은 database에 접근할 수 있는 어떤 worker process도 실행을 이어받을 수 있어
  distributed failover와 horizontal scaling이 가능합니다.

## 기능

| 기능 | 설명 |
| --- | --- |
| Durable tool execution | LLM call 외에도 `@DBOS.step()`으로 decorate된 tool function이 실패 시 구성 가능한 retry와 함께 database에 checkpoint됩니다 |
| Failure recovery | process restart 시 마지막 성공 step부터 in-flight workflow를 재개하거나, [DBOS Conductor](https://docs.dbos.dev/production/conductor)를 사용하는 distributed setting에서 automatic fail-over를 수행합니다 |
| Parallel tool calls | 단일 LLM response에서 여러 tool call을 replay-safe하게 동시에 dispatch하고, 다음 LLM step 전에 join합니다 |
| Debugging | 과거 workflow execution을 step-by-step으로 replay합니다. bug fix를 위해 특정 step에서 workflow를 fork하고 restart할 수 있습니다 |
| Long-running agents | workflow는 몇 시간, 며칠, 몇 달 동안 실행될 수 있으며 state는 완료될 때까지 database에 유지됩니다 |
| Observability | 모든 LLM call과 tool execution은 기록된 step이며, [DBOS Console](https://docs.dbos.dev/production/workflow-management) dashboard 또는 OpenTelemetry에서 볼 수 있습니다 |
| Human-in-the-loop | DBOS [workflow notifications](https://docs.dbos.dev/python/tutorials/workflow-communication#workflow-messaging-and-notifications)를 통해 외부 signal 또는 human approval을 받은 뒤 실행을 재개합니다 |
| Rate limiting을 갖춘 scalable execution | workflow 안에서 여러 에이전트를 조합하거나 [durable queues](https://docs.dbos.dev/python/tutorials/queue-tutorial)를 사용해 분산 worker 전반에서 agent workflow를 실행합니다. API backpressure 처리를 위한 내장 rate limiting을 제공합니다 |
| Safe versioning | in-flight execution을 중단하지 않고 [DBOS patching or versioning](https://docs.dbos.dev/python/tutorials/upgrading-workflows)을 사용해 새 에이전트 버전을 upgrade 및 deploy합니다 |

## 추가 리소스

- [DBOS Python documentation](https://docs.dbos.dev/python/programming-guide) - DBOS workflow, step, queue 전체 reference
- [dbos-google-adk on PyPI](https://pypi.org/project/dbos-google-adk/) - Python package
- [DBOS GitHub repository](https://github.com/dbos-inc/dbos-transact-py) - Source code and examples
- [DBOS Discord](https://discord.gg/eMUHrvbu67) - Questions and community discussion
