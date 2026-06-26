---
catalog_title: Aerospike
catalog_description: 단일 Aerospike 클러스터에 ADK 에이전트의 세션, 메모리, 아티팩트를 저장하세요
catalog_icon: /integrations/assets/aerospike.png
catalog_tags: ["data"]
---

# ADK를 위한 Aerospike 연동

<div class="language-support-tag">
  <span class="lst-supported">ADK 지원</span><span class="lst-python">Python</span>
</div>

[`adk-aerospike`](https://github.com/aerospike-community/adk-aerospike) 연동은 ADK 에이전트를 분산 실시간 키-값 데이터베이스인 [Aerospike](https://aerospike.com/)에 연결해 줍니다. 이 연동 모듈은 애플리케이션 프로세스에서 기본 Aerospike 클라이언트를 사용하여 단일 클러스터에서 3가지 ADK Python 저장소 인터페이스를 모두 구현합니다. `aerospike://` URI 스키마를 한 번 등록하면 `adk` CLI에서 세션, 아티팩트, 메모리에 Aerospike를 사용할 수 있습니다.

이 연동을 사용하는 데는 여러 가지 방법이 있습니다:

| 접근 방식 | 설명 |
| -------- | ----------- |
| **세션 서비스** | `AerospikeSessionService`: 범위 지정 상태(`app:`, `user:`, session), 청크 스토리지 기반 이벤트 기록, 원자적(atomic) `append_event`. |
| **메모리 서비스** | `AerospikeMemoryService`: 토큰별 게시 목록(posting-list) 키를 통한 어휘적 단어 중복 검색. `InMemoryMemoryService`와 동일한 시맨틱을 가집니다. |
| **아티팩트 서비스** | `AerospikeArtifactService`: 세션별 또는 `user:` 네임스페이스별 버전 관리 블롭(blob) 저장. |
| **전체 스택** | 세 서비스를 하나의 `Runner`에 모두 연결하거나, 일치하는 `aerospike://` URI를 `adk web` / `adk run`에 전달하여 사용합니다. |

## 주요 사용 사례

- **프로덕션 에이전트 영속성 (Production agent persistence)**: 별도의 메모리 서비스를 운영하지 않고도 대화 상태, 도구 출력, 사용자 범위 데이터를 여러 에이전트 인스턴스(replica)나 재시작 간에 안전하게 보존합니다.
- **고처리량 에이전트 (High-throughput agents)**: 세션 추가 지연 시간이 중요한 채팅, 음성 및 실시간 오케스트레이션에서 1밀리초 미만의 속도로 읽기 및 쓰기를 처리합니다.
- **어휘 장기 메모리 (Lexical long-term memory)**: 쓰기 시점에 텍스트를 토큰화하고, 게시 목록 키(`app:user:kw:<token>`)에 대한 포인트 읽기(point read) 방식으로 검색하여 메모리 행을 복원합니다. 임베딩 모델이 필요하지 않습니다.
- **멀티모달 아티팩트 (Multimodal artifacts)**: 이미지, 파일 및 생성된 결과물을 버전 기록과 함께 저장합니다. `user:` 파일 이름은 여러 세션에 걸쳐 표시됩니다 (ADK 사양).
- **자체 호스팅 및 다중 테넌트 (Self-hosted and multi-tenant)**: 하나의 네임스페이스 내에서 테넌트 범위의 아티팩트 및 메모리 작업을 처리할 수 있는 복합 보조 인덱스(composite secondary index)를 제공합니다. 커뮤니티(Community) 또는 엔터프라이즈(Enterprise) 에디션, 온프레미스 또는 클라우드를 모두 지원합니다.

## 사전 요구사항

- Python 3.11 이상
- [Python용 ADK](/get-started/python/) (`google-adk`)
- Aerospike Database 7.x 또는 8.x (Community 또는 Enterprise)
- 연결 가능한 클러스터 (아래의 로컬 Docker 예시 참조)

개발용 로컬 Aerospike 실행:

```bash
docker run --rm -d --name aerospike -p 3000-3003:3000-3003 aerospike/aerospike-server:latest
```

실행 가능한 예시에서 모델 호출을 위해 `GOOGLE_API_KEY`(또는 해당 모델 제공업체의 자격 증명)를 설정합니다.

## 설치

```bash
pip install google-adk adk-aerospike
```

## 에이전트와 함께 사용하기

=== "세션 + Runner"

    persisted 세션을 지원하는 완전한 멀티턴 에이전트를 구성하기 위해 `AerospikeSessionService`를 ADK `Runner`에 연결합니다.

    ```python
    import asyncio

    from adk_aerospike import AerospikeSessionService
    from google.adk.agents import LlmAgent
    from google.adk.runners import Runner
    from google.genai import types

    async def main() -> None:
        session_service = AerospikeSessionService.from_uri(
            "aerospike://localhost:3000/adk"
        )
        agent = LlmAgent(
            name="assistant",
            model="gemini-flash-latest",
            instruction="Be helpful. Keep replies under 30 words.",
        )
        runner = Runner(
            agent=agent,
            app_name="myapp",
            session_service=session_service,
        )

        session = await session_service.create_session(
            app_name="myapp", user_id="user-1"
        )
        async for event in runner.run_async(
            user_id="user-1",
            session_id=session.id,
            new_message=types.Content(
                role="user", parts=[types.Part(text="Hello")]
            ),
        ):
            if event.content:
                for part in event.content.parts or []:
                    if part.text:
                        print(part.text)

        session_service.close()

    asyncio.run(main())
    ```

=== "세션 API"

    상태, 이벤트, 목록 조회를 위해 세션 서비스를 직접 사용합니다. 범위 지정 키는 ADK 규칙(`app:`, `user:`, `temp:`)을 따릅니다.

    ```python
    import asyncio

    from adk_aerospike import AerospikeSessionService
    from google.adk.events import Event, EventActions
    from google.genai import types

    async def main() -> None:
        svc = AerospikeSessionService.from_uri("aerospike://localhost:3000/adk")

        session = await svc.create_session(
            app_name="support_bot",
            user_id="alice",
            state={
                "topic": "billing",
                "app:tenant": "acme-corp",
                "user:nickname": "Allie",
                "temp:scratch": "throwaway",
            },
        )

        await svc.append_event(
            session,
            Event(
                invocation_id="i1",
                author="user",
                content=types.Content(
                    role="user",
                    parts=[types.Part(text="Where is my invoice?")],
                ),
                actions=EventActions(state_delta={"turn": 1}),
            ),
        )

        fetched = await svc.get_session(
            app_name="support_bot",
            user_id="alice",
            session_id=session.id,
        )
        print(fetched.state)
        # topic, turn, app:tenant, user:nickname — temp: 키는 영속화되지 않습니다.

        svc.close()

    asyncio.run(main())
    ```

=== "메모리 서비스"

    텍스트를 포함하는 세션 이벤트를 영속화하고 벡터 인덱스 없이 단어 중복으로 검색합니다.

    ```python
    import asyncio

    from adk_aerospike import AerospikeMemoryService
    from google.adk.events import Event, EventActions
    from google.adk.sessions import Session
    from google.genai import types

    async def main() -> None:
        memory = AerospikeMemoryService.from_uri(
            "aerospike://localhost:3000/adk", top_k=10
        )

        session = Session(
            id="s-1",
            app_name="support_bot",
            user_id="alice",
            events=[
                Event(
                    invocation_id="i",
                    author="user",
                    content=types.Content(
                        role="user",
                        parts=[types.Part(text="Python uses duck typing.")],
                    ),
                    actions=EventActions(),
                ),
            ],
        )
        await memory.add_session_to_memory(session)

        resp = await memory.search_memory(
            app_name="support_bot",
            user_id="alice",
            query="python duck typing",
        )
        for m in resp.memories:
            print(m.content.parts[0].text)

        memory.close()

    asyncio.run(main())
    ```

=== "아티팩트 서비스"

    세션별로 버전 관리되는 아티팩트를 저장합니다. 교차 세션 가시성을 확보하려면 `user:` 파일 이름 접두사를 사용하세요.

    ```python
    import asyncio

    from adk_aerospike import AerospikeArtifactService
    from google.genai import types

    async def main() -> None:
        svc = AerospikeArtifactService.from_uri(
            "aerospike://localhost:3000/adk"
        )

        await svc.save_artifact(
            app_name="support_bot",
            user_id="alice",
            session_id="s-1",
            filename="report.pdf",
            artifact=types.Part(
                inline_data=types.Blob(
                    mime_type="application/pdf", data=b"%PDF-1.4..."
                ),
            ),
        )

        latest = await svc.load_artifact(
            app_name="support_bot",
            user_id="alice",
            session_id="s-1",
            filename="report.pdf",
        )
        print(latest.inline_data.mime_type)

        svc.close()

    asyncio.run(main())
    ```

=== "세 가지 서비스 결합"

    ```python
    from adk_aerospike import (
        AerospikeArtifactService,
        AerospikeMemoryService,
        AerospikeSessionService,
    )
    from google.adk.agents import LlmAgent
    from google.adk.runners import Runner

    uri = "aerospike://localhost:3000/adk"

    session_service = AerospikeSessionService.from_uri(uri)
    artifact_service = AerospikeArtifactService.from_uri(uri)
    memory_service = AerospikeMemoryService.from_uri(uri)

    agent = LlmAgent(name="assistant", model="gemini-flash-latest")
    runner = Runner(
        agent=agent,
        app_name="myapp",
        session_service=session_service,
        artifact_service=artifact_service,
        memory_service=memory_service,
    )
    ```

=== "`adk web` 및 `adk run`"

    URI 스키마를 한 번 등록합니다(예: 에이전트 옆의 `services.py`에 등록):

    ```python
    import adk_aerospike

    adk_aerospike.register()
    ```

    그런 다음 각 저장소 역할에 대해 동일한 네임스페이스를 향하도록 CLI에 지정합니다:

    ```bash
    adk web \
      --session_service_uri=aerospike://localhost:3000/adk \
      --artifact_service_uri=aerospike://localhost:3000/adk \
      --memory_service_uri=aerospike://localhost:3000/adk
    ```

    !!! note

        `register()`는 `aerospike://`를 ADK의 서비스 레지스트리에 연결하여 개발 UI와 CLI가 별도의 커스텀 팩토리 코드 없이도 이 URL들을 해석할 수 있도록 지원합니다.

## 구성

### 연결 URI

세 서비스 모두 하나의 URI 형식을 공유합니다:

```text
aerospike://[user:pass@]host[:port][,host2[:port],…]/<namespace>[?option=value]
```

예시:

```text
aerospike://localhost:3000/adk
aerospike://user:pass@node1:3000,node2:3000/prod?set_prefix=prod_&tls=true
```

| 쿼리 매개변수 | 설명 |
| --------------- | ----------- |
| `set_prefix` | Aerospike 세트 이름의 접두사 (기본값은 `adk_`). 여러 앱이 하나의 네임스페이스를 공유할 수 있습니다. |
| `tls=true` | TLS 활성화. mTLS 관련 세부 정보는 `from_uri`에 `tls_config={...}`를 전달하여 구성합니다. |
| `auth_mode` | `INTERNAL` (기본값), `EXTERNAL`, `EXTERNAL_INSECURE` 또는 `PKI`. |

서비스 간에 연결 풀을 공유하기 위해 기존 `aerospike.Client` 및 `Schema`를 사용하여 서비스를 빌드할 수도 있습니다.

### 상태 범위 지정

세션 `state`는 접두사(Prefix) 키를 사용합니다 ([`google.adk.sessions.state.State`](https://github.com/google/adk-python)와 동일):

| 접두사 | 저장 위치 | 가시성 |
| ------ | --------- | ---------- |
| `app:foo` | `adk_app_state` | 해당 앱의 모든 사용자 |
| `user:foo` | `adk_user_state` | 여러 세션에 걸친 현재 사용자 |
| `temp:foo` | 저장되지 않음 | 현재 호출(invocation)로 제한 |
| _(접두사 없음)_ | 세션 레코드 | 현재 세션으로 제한 |

`get_session`은 ADK 호환성을 위해 접두사가 복원된 단일 사전(dict)으로 모든 범위를 병합하여 반환합니다.

## 사용 가능한 서비스

### 서비스

| 서비스 | ADK 인터페이스 | 설명 |
| ------- | ------------- | ----------- |
| `AerospikeSessionService` | `BaseSessionService` | 세션, 이벤트, 범위 지정 상태. 세션 레코드에 대한 실시간 이벤트 추가(Hot event tail), 256KiB 크기의 청크 분할 저장. 대부분의 이벤트 추가는 단일 원자적 `operate()`로 처리됩니다. `get_session`은 단일 RTT로 세션+앱+사용자 상태를 조회하기 위해 `batch_read`를 활용합니다. |
| `AerospikeArtifactService` | `BaseArtifactService` | `(app, user, session, filename)` 기준 버전 관리 아티팩트. 버전당 최대 8MiB까지 인라인 페이로드 저장 지원. `user:` 파일 이름은 ADK 사용자 네임스페이스 센티널을 사용합니다. |
| `AerospikeMemoryService` | `BaseMemoryService` | 텍스트가 포함된 이벤트당 하나의 메모리 행 저장. 토큰별 게시 목록(posting-list) 기본 키(PK) 사용. `search_memory`는 쿼리 토큰 중복에 따라 랭킹을 지정합니다. |

### URI 등록

| 함수 | 설명 |
| -------- | ----------- |
| `adk_aerospike.register()` | CLI 및 `adk web`에서 사용할 수 있도록 ADK 서비스 레지스트리에 `aerospike://`를 등록합니다. |

## 저장 레이아웃

네임스페이스 내의 기본 세트 접두사 `adk_`:

| 세트 | 키 패턴 | 용도 |
| --- | ----------- | ------- |
| `adk_sessions` | `app:user:session` | 세션 레코드 (상태 + 실시간 이벤트 꼬리) |
| `adk_sessions` | `app:user:session:c:NNNNNNNN` | 분할된 이벤트 청크 |
| `adk_sessions` | `app:user:sl` | `list_sessions`를 위한 세션 목록 매니페스트 |
| `adk_app_state` | `app` | 앱 범위 상태 |
| `adk_user_state` | `app:user` | 사용자 범위 상태 |
| `adk_artifacts` | `app:user:session:fname:ver` | 아티팩트 버전 |
| `adk_memory` | `app:user:session:event_id` | 메모리 행 |
| `adk_memory` | `app:user:kw:token` | 어휘 검색을 위한 게시 목록 |

인덱스, 청크 인바리언트(chunking invariants) 및 운영 참고사항은 저장소의 [데이터 모델](https://github.com/aerospike-community/adk-aerospike/blob/main/docs/data-model.md)을 참조하세요.

## 추가 자료

- [adk-aerospike GitHub 저장소](https://github.com/aerospike-community/adk-aerospike)
- [adk-aerospike PyPI 페이지](https://pypi.org/project/adk-aerospike/)
- [실행 가능한 예시](https://github.com/aerospike-community/adk-aerospike/tree/main/examples)
- [Aerospike 공식 문서](https://aerospike.com/docs/)
- [ADK 세션 및 메모리](/sessions/)
