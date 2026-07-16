---
catalog_title: Milvus
catalog_description: ADK 에이전트를 위한 Milvus 기반 메모리 및 RAG 검색
catalog_icon: /integrations/assets/milvus.svg
catalog_tags: ["data"]
---

# ADK용 Milvus 통합

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span>
</div>

[`adk-milvus`](https://github.com/zilliztech/adk-milvus) 패키지는 ADK Python 에이전트를 오픈 소스 벡터 데이터베이스인 [Milvus](https://milvus.io/)에 연결합니다. `MilvusMemoryService`를 통해 영구 세션 메모리로 사용하거나, `MilvusToolset`을 통해 RAG 워크플로를 위한 `milvus_similarity_search` 검색 도구를 제공할 수 있습니다.

Milvus는 동일한 구성 필드를 사용하여 로컬에서 Milvus Lite로 실행하거나, 자체 호스팅 Milvus 서버 또는 관리형 [Zilliz Cloud](https://zilliz.com/cloud) 배포판으로 실행할 수 있습니다.

## 사용 사례

- **에이전트용 의미론적 메모리(Semantic Memory)**: 세션 이벤트를 Milvus에 영구 저장하고 이후 대화에서 관련 메모리를 검색합니다.
- **비공개 콘텐츠 RAG**: 문서 또는 코드 스니펫을 인덱싱하고 에이전트가 도구 호출을 통해 관련 컨텍스트를 검색하도록 합니다.
- **로컬에서 클라우드로 개발**: 로컬 개발을 위해 Milvus Lite로 시작한 다음, URI와 토큰을 변경하여 Milvus 서버나 Zilliz Cloud로 전환합니다.

## 사전 준비 사항

- Python 3.10 이상
- ADK for Python 및 `adk-milvus`
- 입력 텍스트당 하나의 벡터를 반환하는 임베딩 함수
- 다음 중 하나의 Milvus 배포:
    - 로컬 개발을 위한 Milvus Lite
    - Milvus 서버 (예: `http://localhost:19530`)
    - Zilliz Cloud 엔드포인트 및 토큰

## 설치

```bash
pip install adk-milvus
```

이를 통해 ADK 런타임 종속성, PyMilvus 및 Milvus Lite 지원이 설치됩니다.

## 구성

모든 배포 모드에 `MILVUS_URI` 및 `MILVUS_TOKEN`을 사용합니다.

```bash
# Milvus Lite
export MILVUS_URI="./adk_milvus.db"

# Milvus server
export MILVUS_URI="http://localhost:19530"

# Zilliz Cloud
export MILVUS_URI="https://your-endpoint.api.gcp-us-west1.zillizcloud.com"
export MILVUS_TOKEN="your-token"
```

`MILVUS_TOKEN`은 Zilliz Cloud와 같이 인증이 필요한 배포에만 필요합니다. 기본값이 아닌 다른 Milvus 데이터베이스를 사용하는 경우 `MILVUS_DB_NAME`을 설정하십시오.

## 에이전트와 함께 사용

=== "메모리 서비스"

    `MilvusMemoryService`를 `Runner`에 연결하여 세션 간 메모리를 유지하고 검색합니다.

    ```python
    from adk_milvus import MilvusMemoryService
    from google.adk.agents import Agent
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import Client

    genai_client = Client()

    def embedding_function(texts):
        response = genai_client.models.embed_content(
            model="gemini-embedding-001",
            contents=list(texts),
        )
        return [list(embedding.values) for embedding in response.embeddings]

    memory_service = MilvusMemoryService(
        embedding_function=embedding_function,
        dimension=3072,
        collection_name="adk_memory",
    )

    agent = Agent(
        name="memory_agent",
        model="gemini-flash-latest",
        instruction="관련이 있을 때 응답을 개인화하기 위해 메모리를 사용하십시오.",
    )

    runner = Runner(
        app_name="milvus_memory_app",
        agent=agent,
        session_service=InMemorySessionService(),
        memory_service=memory_service,
    )
    ```

    의미 있는 세션이 끝나면 이를 메모리에 추가하고 나중에 검색할 수 있습니다.

    ```python
    session = await runner.session_service.get_session(
        app_name="milvus_memory_app",
        user_id="user-1",
        session_id="session-1",
    )
    await memory_service.add_session_to_memory(session)

    result = await memory_service.search_memory(
        app_name="milvus_memory_app",
        user_id="user-1",
        query="데이터베이스 선호도에 대해 사용자가 뭐라고 말했습니까?",
    )
    for memory in result.memories:
        print(memory.content.parts[0].text)
    ```

=== "RAG 도구 세트"

    `MilvusVectorStore`를 사용하여 텍스트를 인덱싱한 다음 `MilvusToolset`을 통해 노출시킵니다.

    ```python
    from adk_milvus import MilvusToolset
    from adk_milvus import MilvusVectorStore
    from adk_milvus import MilvusVectorStoreSettings
    from google.adk.agents import Agent
    from google.genai import Client

    genai_client = Client()

    def embedding_function(texts):
        response = genai_client.models.embed_content(
            model="gemini-embedding-001",
            contents=list(texts),
        )
        return [list(embedding.values) for embedding in response.embeddings]

    vector_store = MilvusVectorStore(
        embedding_function=embedding_function,
        settings=MilvusVectorStoreSettings(
            collection_name="adk_rag",
            dimension=3072,
        ),
    )

    vector_store.add_texts(
        [
            "Milvus Lite는 로컬 RAG 개발에 유용합니다.",
            "Zilliz Cloud는 프로덕션 워크로드를 위한 관리형 Milvus를 제공합니다.",
        ],
        metadatas=[
            {"source": "milvus-lite"},
            {"source": "zilliz-cloud"},
        ],
    )

    milvus_toolset = MilvusToolset(vector_store=vector_store)
    tools = await milvus_toolset.get_tools_with_prefix()

    agent = Agent(
        name="rag_agent",
        model="gemini-flash-latest",
        instruction="질문에 답할 때 검색 컨텍스트(retrieval context)를 사용하십시오.",
        tools=tools,
    )
    ```

## 사용 가능한 도구 및 작업

### RAG 도구 세트

도구 | 설명
---- | -----------
`milvus_similarity_search` | Milvus에서 인덱싱된 텍스트를 검색하고 내용, 출처, 메타데이터, 거리가 포함된 일치하는 행을 반환합니다.

### 메모리 서비스

메서드 | 설명
---- | -----------
`add_session_to_memory(session)` | ADK 세션에서 텍스트를 포함하는 이벤트를 영구 저장합니다.
`search_memory(app_name, user_id, query)` | ADK 앱 및 사용자 범위로 제한된 메모리를 검색합니다.

## 주의 사항

- `dimension`은 임베딩 모델의 출력 차원과 일치해야 합니다.
- `MilvusMemoryService`는 `app_name` 및 `user_id`를 기반으로 검색 범위를 제한합니다.
- `MilvusVectorStore`는 컬렉션이 없는 경우 새로 생성하며, 재사용하기 전에 기존 스키마를 검증합니다.
- 읽기 쓰기 일관성(read-after-write)이 더 강력하게 요구되거나 여러 Milvus 데이터베이스가 필요한 배포를 위해 컬렉션 일관성 수준(consistency level) 및 데이터베이스 이름을 구성할 수 있습니다.

## 리소스

- [ADK Milvus 패키지](https://github.com/zilliztech/adk-milvus)
- [PyPI의 ADK Milvus](https://pypi.org/project/adk-milvus/)
- [Milvus 문서](https://milvus.io/docs)
- [Milvus Lite 문서](https://milvus.io/docs/milvus_lite.md)
- [Zilliz Cloud](https://zilliz.com/cloud)
