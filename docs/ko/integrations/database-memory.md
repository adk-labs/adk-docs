---
catalog_title: Database Memory Service
catalog_description: 에이전트용 SQL 지원 영구 메모리
catalog_icon: /integrations/assets/adk-database-memory.png
catalog_tags: ["data"]
---


# ADK용 데이터베이스 메모리 서비스

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span>
</div>

[`adk-database-memory`](https://github.com/anmolg1997/adk-database-memory)는
비동기 SQLAlchemy 기반의 ADK Python용 드롭인(drop-in) 영구 `BaseMemoryService` 구현체입니다. 이 통합을 사용하면 자체 데이터베이스를 활용해 ADK 에이전트에 세션 간 지속되는 메모리를 제공할 수 있습니다. 개발 환경에서는 SQLite를, 프로덕션 환경에서는 PostgreSQL이나 MySQL을 사용하세요.

## 사용 사례

- **개인화된 어시스턴트**: 여러 세션에 걸쳐 장기적인 사용자 선호도, 사실 정보, 과거 의사결정을 축적하여 에이전트가 필요할 때 언제든 불러올 수 있습니다.
- **고객 지원 및 작업 에이전트**: 티켓과 기기 전반에 걸쳐 대화 기록을 영구 저장하여 사용자가 다시 방문할 때마다 이전 컨텍스트를 이어갈 수 있습니다.
- **자체 호스팅 배포**: 온프레미스, 폐쇄망(air-gapped), 비 GCP 클라우드 환경 등 Vertex AI Memory Bank를 사용할 수 없는 경우, 이미 운영 중인 데이터베이스에 메모리를 저장할 수 있습니다.
- **로컬 개발**: 별도 설정 없이 재시작 후에도 유지되는 영구 메모리로 SQLite를 바로 적용한 뒤, 프로덕션에서는 연결 문자열만 PostgreSQL로 전환할 수 있습니다.

## 사전 요구사항

- Python 3.10 이상
- 지원되는 데이터베이스: SQLite, PostgreSQL 또는 MySQL / MariaDB

## 설치

사용할 데이터베이스 드라이버와 함께 패키지를 설치합니다:

```bash
pip install "adk-database-memory[sqlite]"    # SQLite (via aiosqlite)
pip install "adk-database-memory[postgres]"  # PostgreSQL (via asyncpg)
pip install "adk-database-memory[mysql]"     # MySQL / MariaDB (via aiomysql)
```

코어 패키지에는 데이터베이스 드라이버가 포함되어 있지 않습니다. 백엔드에 맞는 엑스트라(extra) 옵션을 선택하거나 비동기 드라이버를 별도로 직접 설치하세요.

## 에이전트와 함께 사용

이 서비스는 `google.adk.memory.base_memory_service.BaseMemoryService`를 구현하므로 `memory_service`를 받는 모든 ADK `Runner`에 바로 연결할 수 있습니다:

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

| 백엔드 | 연결 URL 예시 | 엑스트라(Extra) |
| ---- | ---- | ---- |
| SQLite | `sqlite+aiosqlite:///memory.db` | `[sqlite]` |
| SQLite (인메모리) | `sqlite+aiosqlite:///:memory:` | `[sqlite]` |
| PostgreSQL | `postgresql+asyncpg://user:pass@host/db` | `[postgres]` |
| MySQL / MariaDB | `mysql+aiomysql://user:pass@host/db` | `[mysql]` |
| 모든 비동기 SQLAlchemy 방언(dialect) | 드라이버에 따라 다름 | 직접 설치 |

## API

| 메서드 | 설명 |
| ---- | ---- |
| `add_session_to_memory(session)` | 완료된 세션의 모든 이벤트를 인덱싱합니다. |
| `add_events_to_memory(app_name, user_id, events, ...)` | 지정한 이벤트 슬라이스를 인덱싱합니다(스트리밍 수집 시 유용). |
| `search_memory(app_name, user_id, query)` | 지정된 앱과 사용자로 범위를 제한하여, 쿼리와 키워드가 일치하는 `MemoryEntry` 객체를 반환합니다. |

첫 쓰기 작업 시 서비스는 `(app_name, user_id)` 인덱스가 포함된 단일 테이블(`adk_memory_entries`)을 생성합니다. JSON 콘텐츠는 PostgreSQL에서는 `JSONB`, MySQL에서는 `LONGTEXT`, SQLite에서는 `TEXT`로 저장됩니다.

메모리 조회는 ADK의 인메모리 및 Firestore 메모리 서비스와 동일한 키워드 추출 및 매칭 방식을 사용합니다. 임베딩 기반 시맨틱 검색이 필요한 경우 이 패키지를 Vertex AI Memory Bank 또는 벡터 스토어와 함께 사용하세요.

## 리소스

- [GitHub repository](https://github.com/anmolg1997/adk-database-memory): 소스 코드, 이슈 및 예제
- [PyPI package](https://pypi.org/project/adk-database-memory/): 릴리스 및 설치 안내
- [ADK Memory overview](/sessions/memory/): ADK의 메모리 서비스 활용 방식 개요
