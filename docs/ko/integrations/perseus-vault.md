---
catalog_title: Perseus Vault Memory
catalog_description: ADK 에이전트에 영구적이고 로컬 암호화된 세션 간 메모리를 추가합니다
catalog_icon: /integrations/assets/perseus-vault.svg
catalog_tags: ["data"]
---

# ADK용 Perseus Vault Memory 통합

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span>
</div>

[`adk-perseus-vault-memory`](https://github.com/Perseus-Computing-LLC/adk-mimir-memory) 통합은 ADK 에이전트를 영구적인 세션 간 메모리 백엔드인 [Perseus Vault](https://github.com/Perseus-Computing-LLC/perseus-vault)에 연결합니다. SQLite 데이터베이스가 내장된 단일 Rust 바이너리로 지원되며, **클라우드 의존성이 전혀 없고** 모든 것이 로컬에서 실행됩니다. 메모리는 AES-256-GCM으로 유휴 상태일 때 암호화되며, 검색은 FTS5 키워드 매칭과 밀집 벡터(dense vector) 검색을 결합합니다.

## 사용 사례

- **재시작 시에도 유지되는 영구 에이전트 메모리**: 프로세스 재시작 후에도 세션이 유지되며, 에이전트가 이전 대화를 자동으로 기억합니다.

- **비공개 및 에어갭(air-gapped) 배포**: 클라우드 의존성이 없으며, Perseus Vault는 로컬 컴퓨터에서 완전히 실행되며 선택적으로 AES-256-GCM 암호화를 적용할 수 있습니다.

- **메모리 전반에 걸친 하이브리드 검색**: 관련 이전 상호작용을 찾기 위해 키워드(FTS5/BM25) 및 의미론적(밀집 벡터) 검색을 결합합니다.

- **워크스페이스 인식 에이전트**: 프로젝트 파일, git 상태 및 구성을 파악하는 에이전트를 위해 Perseus와 페어링합니다.

## 사전 준비 사항

- Python 3.10+
- `perseus-vault` 바이너리 ([설치](#설치) 참조)
- `google-adk>=1.0.0`

## 설치

Python 패키지를 설치합니다.

```bash
pip install adk-perseus-vault-memory
```

그 후 `perseus-vault` 바이너리를 설치합니다: [릴리스 페이지](https://github.com/Perseus-Computing-LLC/perseus-vault/releases)에서 플랫폼에 맞는 빌드를 다운로드하여 `PATH`에 배치합니다. 서비스는 기본적으로 `perseus-vault`를 찾으며, 그렇지 않으면 `PerseusVaultMemoryService`에 `vault_binary="/absolute/path/to/perseus-vault"`를 전달할 수 있습니다.

## 에이전트와 함께 사용

`PerseusVaultMemoryService`를 생성하여 `Runner`에 전달하고, 에이전트에 `load_memory` 도구를 제공하여 이전 세션을 기억할 수 있도록 합니다.

```python
from adk_perseus_vault_memory import PerseusVaultMemoryService
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import load_memory

agent = Agent(
    name="memory_assistant",
    model="gemini-flash-latest",
    instruction="You are a helpful assistant with long-term memory.",
    tools=[load_memory],
)

runner = Runner(
    agent=agent,
    app_name="perseus_vault_app",
    session_service=InMemorySessionService(),
    memory_service=PerseusVaultMemoryService(db_path="~/.adk/vault.db"),
)
```

세션이 완료된 후 `await memory_service.add_session_to_memory(session)`을 호출하여 세션을 보존합니다. 에이전트는 나중 세션에서 `load_memory` 도구를 통해 기억을 검색합니다. 전체 입력 및 검색 흐름은 [ADK 메모리](/ko/sessions/memory/)를 참고하세요.

### Perseus 라이브 컨텍스트 (선택사항)

실시간 워크스페이스 인식을 하려면 `perseus` extra를 설치하세요.

```bash
pip install adk-perseus-vault-memory[perseus]
```

추론 시에 `@file`, `@search` 및 `@memory` 지시어를 확인하는 사전 구축된 `perseus_context_agent`를 사용하세요.

```python
from adk_perseus_vault_memory.perseus_context import perseus_context_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# 사전 빌드된 에이전트에는 모델이 포함되어 있지 않으므로 사용 전에 모델을 설정해야 합니다.
perseus_context_agent.model = "gemini-flash-latest"

runner = Runner(
    agent=perseus_context_agent,
    app_name="perseus_app",
    session_service=InMemorySessionService(),
    memory_service=PerseusVaultMemoryService(db_path="~/.adk/vault.db"),
)
```

세션을 생성할 때 세션 상태를 통해 Perseus 지시어를 설정합니다(비동기 함수 내부).

```python
session = await runner.session_service.create_session(
    app_name="perseus_app",
    user_id="user",
    state={
        "_perseus_directives": "@file AGENTS.md @file README.md @memory deployment",
        "_perseus_workspace": "/path/to/project",
    },
)
```

## 사용 가능한 메모리 작업

| 메서드 | 설명 |
|---|---|
| `add_session_to_memory(session)` | 전체 세션의 이벤트를 유지 보존 |
| `add_events_to_memory(...)` | 증분 이벤트 델타 추가 |
| `add_memory(...)` | 명시적인 메모리 엔트리 저장 |
| `search_memory(...)` | 메모리 전반에 걸친 FTS5 키워드 검색 |

## 백엔드 비교

| 백엔드 | 의존성 | 유휴 암호화 | 검색 | 호스팅 |
|---|---|---|---|---|
| **InMemoryMemoryService** | 없음 | 영구 저장되지 않음 | 키워드 | 로컬 (임시) |
| **VertexAiMemoryBankService** | Google Cloud | Google 관리형 | 시맨틱 (Gemini) | Google Cloud |
| **VertexAiRagMemoryService** | Google Cloud | Google 관리형 | 벡터 유사도 | Google Cloud |
| **PerseusVaultMemoryService** | `perseus-vault` 바이너리 | 로컬 AES-256-GCM | 하이브리드 (FTS5 + 밀집 벡터) | 로컬 |

## 리소스

- [GitHub의 adk-perseus-vault-memory](https://github.com/Perseus-Computing-LLC/adk-mimir-memory)
- [PyPI의 adk-perseus-vault-memory](https://pypi.org/project/adk-perseus-vault-memory/)
- [Perseus Vault (백업 서비스)](https://github.com/Perseus-Computing-LLC/perseus-vault)
- [Perseus Context 통합 가이드](/ko/integrations/perseus/)
