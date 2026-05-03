---
catalog_title: Database Memory Service
catalog_description: 에이전트용 SQL 지원 영구 메모리
catalog_icon: /integrations/assets/adk-database-memory.png
catalog_tags: ["data"]
---


# ADK용 데이터베이스 메모리 서비스

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[`adk-database-memory`](https://github.com/anmolg1997/adk-database-memory)는
비동기 기반의 ADK Python용 드롭인 영구 `BaseMemoryService`
SQLAlchemy. 이 통합은 ADK에 대한 지속적인 교차 세션 메모리를 제공합니다.
자체 데이터베이스를 사용하는 에이전트: 개발에는 SQLite를 사용하거나 Postgres/MySQL을 사용합니다.
생산을 위해.

## 사용 사례

- **맞춤형 비서**: 장기적인 사용자 선호도, 사실 및 정보를 축적합니다.
  세션 전반에 걸쳐 과거 결정을 내려 상담원이 필요할 때 이를 불러올 수 있습니다.
- **지원 및 작업 에이전트**: 티켓 전반에 걸쳐 대화 기록을 유지하고
  사용자가 돌아올 때마다 컨텍스트를 사용할 수 있습니다.
- **자체 호스팅 배포**: Vertex AI Memory Bank가 옵션이 아닌 경우
  (온프레미스, 에어갭, 비 GCP 클라우드), 이미 사용하고 있는 데이터베이스에 메모리를 유지하세요.
  사용.
- **로컬 개발**: 구성이 필요 없는 영구 메모리를 위해 SQLite를 도입했습니다.
  다시 시작해도 살아남은 다음 프로덕션에서 연결 문자열을 Postgres로 전환합니다.

## 전제조건

- 파이썬 3.10 이상
- 지원되는 데이터베이스: SQLite, PostgreSQL 또는 MySQL/MariaDB

## 설치

데이터베이스용 드라이버와 함께 패키지를 설치합니다.

```bash
pip install "adk-database-memory[sqlite]"    # SQLite (via aiosqlite)
pip install "adk-database-memory[postgres]"  # PostgreSQL (via asyncpg)
pip install "adk-database-memory[mysql]"     # MySQL / MariaDB (via aiomysql)
```

핵심 패키지에는 데이터베이스 드라이버가 포함되어 있지 않습니다. 추가로 선택하세요
백엔드와 일치하거나 자체 비동기 드라이버를 별도로 설치하십시오.

## 에이전트와 함께 사용

서비스는 구현
`google.adk.memory.base_memory_service.BaseMemoryService`이므로 어느 곳에나 끼워 넣을 수 있습니다.
`memory_service`를 허용하는 ADK `Runner`:

```python
import asyncio

from adk_database_memory import DatabaseMemoryService
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner

memory = DatabaseMemoryService("sqlite+aiosqlite:///memory.db")

agent = Agent(
    name="assistant",
    model="gemini-flash-latest",
    instruction="You are a helpful assistant.",
)

async def main():
    async with memory:
        # Run the agent, then persist the session to memory
        runner = InMemoryRunner(agent=agent, app_name="my_app")
        session = await runner.session_service.create_session(app_name="my_app", user_id="u1")
        # After the session completes:
        await memory.add_session_to_memory(session)

        # Later, recall relevant memories for a new query:
        result = await memory.search_memory(
            app_name="my_app",
            user_id="u1",
            query="what did we decide about the pricing model?",
        )
        for entry in result.memories:
            print(entry.author, entry.timestamp, entry.content)

asyncio.run(main())
```

## 지원되는 백엔드

| 백엔드 | 연결 URL 예시 | 추가 |
| ---- | ---- | ---- |
| SQLite | `sqlite+aiosqlite:///memory.db` | `[sqlite]` |
| SQLite(메모리 내) | `sqlite+aiosqlite:///:memory:` | `[sqlite]` |
| 포스트그레SQL | `postgresql+asyncpg://user:pass@host/db` | `[postgres]` |
| MySQL/마리아DB | `mysql+aiomysql://user:pass@host/db` | `[mysql]` |
| 모든 비동기 SQLAlchemy 방언 | 드라이버에 따라 다름 | 직접 가져오세요 |

## API

| 방법 | 설명 |
| ---- | ---- |
| `add_session_to_memory(session)` | 완료된 세션의 모든 이벤트를 색인화합니다. |
| `add_events_to_memory(app_name, user_id, events, ...)` | 명시적인 이벤트 조각을 인덱싱합니다(스트리밍 수집에 유용함). |
| `search_memory(app_name, user_id, query)` | 지정된 앱 및 사용자로 범위가 지정된 쿼리와 겹치는 색인화된 키워드가 있는 `MemoryEntry` 개체를 반환합니다. |

처음 쓰기 시 서비스는 다음을 사용하여 단일 테이블(`adk_memory_entries`)을 생성합니다.
`(app_name, user_id)`의 인덱스. JSON 콘텐츠는 `JSONB`로 저장됩니다.
PostgreSQL, MySQL의 `LONGTEXT` 및 SQLite의 `TEXT`.

검색은 검색과 동일한 키워드 추출 및 일치 접근 방식을 사용합니다.
ADK의 인메모리 및 Firestore 메모리 서비스. 임베딩 기반 리콜의 경우 쌍을 이룹니다.
Vertex AI Memory Bank 또는 벡터 저장소가 포함된 이 패키지입니다.

## 리소스

- [GitHub repository](https://github.com/anmolg1997/adk-database-memory): 소스
  코드, 문제 및 예제.
- [PyPI package](https://pypi.org/project/adk-database-memory/): 릴리스 및
  설치 지침.
- [ADK Memory overview](/sessions/memory/):
  ADK가 메모리 서비스를 사용하는 방법에 대한 배경 지식입니다.
