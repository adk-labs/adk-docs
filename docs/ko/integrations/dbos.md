---
catalog_title: DBOS
catalog_description: 사용자 승인과 안전한 버전 관리를 지원하는 복원력 있고 확장 가능한 장기 실행 에이전트
catalog_icon: /integrations/assets/dbos.png
catalog_tags: ["resilience"]
---

# ADK용 DBOS 플러그인

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span>
</div>

[DBOS](https://dbos.dev)는 신뢰할 수 있는 워크플로와 AI 에이전트를 구축하기 위한 내구성 있는 실행(durable
execution) 프레임워크입니다. ADK와 통합되어 LLM 호출, 도구 실행, 에이전트 오케스트레이션에
내결함성(fault tolerance)과 확장성을 부여합니다. 비정상 종료(crash), 배포, 재시작 이후에도 에이전트가
중단된 지점부터 정확히 다시 실행되며, 별도의 오케스트레이션 서비스 없이 사용자가 직접 소유한
데이터베이스만으로 동작합니다.

## 사용 사례

DBOS 플러그인은 ADK 에이전트에 프로덕션급 안정성과 오케스트레이션 기능을 추가합니다.

- **내구성 있는 실행(Durable execution)**: LLM 및 도구 출력을 영구 저장합니다. 비정상 종료, 배포, 머신 장애
  이후에도 진행 상태를 잃거나 부수 효과(side effect)를 중복 실행하지 않고 에이전트를 자동 복구하므로 수동
  [세션 재개](/ko/runtime/resume/)가 필요하지 않습니다.
- **내장 재시도 및 백오프**: LLM 제공자와 도구 실행의 일시적 장애를 처리하기 위해
  지수 백오프(exponential backoff)가 적용된 구성 가능한 재시도 정책을 제공합니다.
- **장기 실행 에이전트**: 에이전트와 도구를 몇 시간, 며칠, 몇 달 동안 안정적으로 실행합니다.
- **Human-in-the-loop**: 실행을 일시 중지하고 외부 신호(signal)나 사용자 승인을 받은 뒤
  나중에 다시 재개합니다.
- **속도 제한(Rate limiting)을 갖춘 확장 가능한 실행**: 하나의 워크플로 안에서 여러 에이전트를 조합하거나,
  내구성 있는 큐와 내장 속도 제한 기능을 사용해 분산 워커 전반으로 에이전트 워크플로를 확장합니다.
- **관측성 및 관리**: [DBOS Console](https://docs.dbos.dev/production/workflow-management)에서
  에이전트 워크플로를 검사, 취소, 재개 및 포크(fork)할 수 있습니다.

## 사전 요구사항

- Python 3.10+
- [Gemini API 키](https://aistudio.google.com/app/api-keys) 또는 지원되는
  [모델](/ko/agents/models/)

## 설치

```bash
pip install dbos-google-adk
```

## 에이전트와 함께 사용하기

이 통합은 각 LLM 호출이 내구성 있는 DBOS 워크플로 단계(step)로 실행되도록 ADK 에이전트를
래핑합니다. `@DBOS.step()` 데코레이터가 적용된 도구 함수는 구성 가능한 재시도 정책과 함께
개별적으로 체크포인트에 저장됩니다.

### 기본 설정

`Runner`에 `DBOSPlugin`을 추가하고 `@DBOS.workflow()`에서 에이전트를 실행하여
에이전트와 워크플로를 정의합니다.

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

### 내구성 있는 이벤트 압축(Durable event compaction)

내구성 있는 이벤트 압축을 위해 요약기(summarizer)를 `DBOSEventSummarizer`로 래핑하면 압축용
LLM 호출도 체크포인트에 저장됩니다.

```python
from dbos_google_adk import DBOSEventSummarizer
from google.adk.models.google_llm import Gemini

summarizer = DBOSEventSummarizer.from_llm(Gemini(model="gemini-flash-latest"))
```

## 작동 방식

`DBOSPlugin`과 `DBOSEventSummarizer`는 내구성 있는 DBOS 워크플로 안에서 ADK 에이전트를
실행합니다.

- **LLM 호출**은 `DBOSPlugin`이 가로채서 DBOS 단계(step)로 실행합니다. 호출이 실패하거나
  워커가 비정상 종료되면 DBOS는 마지막으로 성공한 단계부터 실행을 재개하여 불필요한 토큰 소모를
  줄입니다.
- **도구 함수**는 `@DBOS.step()` 데코레이터를 적용하면 개별적으로 체크포인트에 저장됩니다. 출력 결과가
  데이터베이스에 영구 저장되므로 리플레이 시 이미 완료된 도구 실행은 완전히 건너뜁니다.
- **워크플로 실행 상태**는 모든 단계 직후 데이터베이스(SQLite 또는 Postgres)에 직렬화되어
  영구 저장됩니다. 동일한 데이터베이스에 접근할 수 있는 어떤 워커 프로세스든 실행을 이어받을 수 있어
  분산 장애 조치(failover)와 수평 확장이 가능합니다.

## 주요 기능

| 기능 | 설명 |
| --- | --- |
| 내구성 있는 도구 실행 | LLM 호출 외에도 `@DBOS.step()` 데코레이터가 적용된 도구 함수가 실패 시 구성 가능한 재시도와 함께 데이터베이스에 체크포인트로 저장됩니다 |
| 장애 복구 | 프로세스 재시작 시 마지막으로 성공한 단계부터 진행 중인 워크플로를 재개하거나, [DBOS Conductor](https://docs.dbos.dev/production/conductor)를 사용하는 분산 환경에서 자동 장애 조치(failover)를 수행합니다 |
| 병렬 도구 호출 | 단일 LLM 응답에서 발생한 여러 도구 호출을 리플레이 안전성(replay safety)을 보장하며 동시에 디스패치하고, 다음 LLM 단계 전에 조인(join)합니다 |
| 디버깅 | 과거 워크플로 실행을 단계별로 리플레이합니다. 버그 수정을 위해 특정 단계에서 워크플로를 포크(fork)하고 다시 시작할 수 있습니다 |
| 장기 실행 에이전트 | 워크플로는 몇 시간, 며칠, 몇 달 동안 실행될 수 있으며 상태는 완료될 때까지 데이터베이스에 영구 저장됩니다 |
| 관측성 | 모든 LLM 호출과 도구 실행이 단계별로 기록되며, [DBOS Console](https://docs.dbos.dev/production/workflow-management) 대시보드 또는 OpenTelemetry를 통해 확인할 수 있습니다 |
| Human-in-the-loop | 실행을 일시 중지하고 DBOS [워크플로 알림](https://docs.dbos.dev/python/tutorials/workflow-communication#workflow-messaging-and-notifications)을 통해 외부 신호나 사용자 승인을 받은 뒤 실행을 재개합니다 |
| 속도 제한을 갖춘 확장 가능한 실행 | 하나의 워크플로 안에서 여러 에이전트를 조합하거나 [내구성 있는 큐](https://docs.dbos.dev/python/tutorials/queue-tutorial)를 사용해 분산 워커 전반에서 에이전트 워크플로를 실행합니다. API 백프레셔(backpressure) 처리를 위한 내장 속도 제한 기능을 제공합니다 |
| 안전한 버전 관리 | 실행 중인 워크플로를 중단하지 않고 [DBOS 패치 또는 버전 관리](https://docs.dbos.dev/python/tutorials/upgrading-workflows)를 사용해 새 에이전트 버전으로 업그레이드 및 배포합니다 |

## 추가 리소스

- [DBOS Python 문서](https://docs.dbos.dev/python/programming-guide) - DBOS 워크플로, 단계(step), 큐 전체 레퍼런스
- [PyPI의 dbos-google-adk](https://pypi.org/project/dbos-google-adk/) - Python 패키지
- [DBOS GitHub 저장소](https://github.com/dbos-inc/dbos-transact-py) - 소스 코드 및 예제
- [DBOS Discord](https://discord.gg/eMUHrvbu67) - 질문 및 커뮤니티 토론
