---
catalog_title: Redis
catalog_description: 에이전트를 위한 벡터, 하이브리드, SQL 검색과 세션, 메모리, 시맨틱 캐시
catalog_icon: /integrations/assets/redis.svg
catalog_tags: ["data","mcp"]
---

# ADK용 Redis 통합

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[adk-redis 통합](https://github.com/redis-developer/adk-redis)은 ADK
에이전트를 [Redis](https://redis.io/)에 연결합니다. 이를 통해 Redis
인덱스 위의 RedisVL 기반 검색 도구, [Redis Agent Memory Server](https://github.com/redis/agent-memory-server)를
통한 영구 세션 및 장기 메모리, LLM 응답과 도구 결과를 위한 시맨틱 캐시를
사용할 수 있습니다. Redis는 관리형 서비스 또는 자체 호스팅(RediSearch
모듈이 활성화된 Redis 8.4 이상)으로 실행할 수 있습니다.

이 통합을 사용하는 방법은 여러 가지입니다.

| 접근 방식 | 설명 |
|----------|------|
| **RedisVL MCP** | ADK의 네이티브 `McpToolset`을 실행 중인 [`rvl mcp`](https://docs.redisvl.com/en/latest/user_guide/how_to_guides/mcp.html) 서버에 연결합니다. 스키마 인식 필터와 반환 필드 힌트가 있는 `search-records`(vector / fulltext / hybrid) 및 `upsert-records`를 노출합니다. |
| **Session + Memory 서비스** | Agent Memory Server를 백엔드로 사용하는 ADK `BaseSessionService` 및 `BaseMemoryService` 구현인 `RedisWorkingMemorySessionService`와 `RedisLongTermMemoryService`입니다. |
| **Sessions + Memory MCP** | ADK의 네이티브 `McpToolset`을 SSE를 통해 [Agent Memory Server](https://github.com/redis/agent-memory-server)의 MCP 엔드포인트에 연결합니다. 에이전트가 `search_long_term_memory`, `create_long_term_memories`, `memory_prompt`에 직접 도구로 접근할 수 있습니다. |
| **Search tools** | RedisVL 쿼리로 바인딩된 인덱스를 검색하는 다섯 가지 `BaseTool` 하위 클래스(`RedisVectorSearchTool`, `RedisHybridSearchTool`, `RedisRangeSearchTool`, `RedisTextSearchTool`, `RedisSQLSearchTool`)입니다. |

## 사용 사례

- **데이터 기반 RAG**: Redis 인덱스에서 vector, hybrid, range, BM25 text,
  SQL 검색을 실행합니다. Hybrid 검색은 Redis 8.4 이상에서 네이티브
  `FT.HYBRID`를 사용하고, 그 외 환경에서는 클라이언트 측 집계로 폴백합니다.
- **영구 멀티턴 에이전트**: 세션 및 메모리 서비스를 ADK `Runner`에 연결해
  대화 상태를 유지하고, 컨텍스트 창이 가득 차면 자동 요약하며, 지속해야
  하는 사실을 장기 메모리로 승격합니다.
- **스키마 인식 MCP 도구**: Redis 인덱스마다 하나의 `rvl mcp` 서버를 세우고
  여러 에이전트를 `stdio`, `sse`, `streamable-http`로 연결합니다. MCP 도구
  설명에는 인덱스 스키마에서 파생된 필터와 반환 필드 힌트가 포함됩니다.
- **지연 시간과 비용 절감**: LLM 호출 지점을 시맨틱 캐시로 감싸 반복되거나
  거의 중복되는 프롬프트가 모델을 건너뛰게 합니다.

## 기본 요건

- Python 3.10 이상
- RediSearch 모듈이 활성화된 Redis 8.4 이상 또는 [Redis Cloud](https://redis.io/cloud/)
- 세션 및 메모리 서비스의 경우: 로컬 또는 환경에서 실행 중인
  [Redis Agent Memory Server](https://github.com/redis/agent-memory-server)
- LangCache 캐시 제공자의 경우: [Redis LangCache](https://redis.io/langcache)
  캐시와 API 키

## 설치

필요한 구성요소를 설치합니다.

```bash
pip install 'adk-redis[memory]'      # session + long-term memory services
pip install 'adk-redis[search]'      # RedisVL-backed search tools
pip install 'adk-redis[sql]'         # RedisSQLSearchTool (sql-redis)
pip install 'adk-redis[langcache]'   # managed semantic cache provider
pip install 'adk-redis[all]'         # everything above

# For the RedisVL MCP server (used with ADK's native McpToolset):
pip install 'redisvl[mcp]>=0.18.2'
```

## 에이전트와 함께 사용

=== "RedisVL MCP server"

    [RedisVL MCP 서버](https://docs.redisvl.com/en/latest/user_guide/how_to_guides/mcp.html)(`rvl mcp`)를
    Redis 인덱스에 연결해 시작한 다음, ADK의 네이티브 `McpToolset`을
    여기에 연결합니다. 아래 예제는 별도의 서버 프로세스가 필요 없는 stdio
    전송을 사용합니다. 장기 실행 원격 서버에 연결하려면
    `StreamableHTTPConnectionParams` 또는 `SseConnectionParams`로 교체하세요.

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from mcp import StdioServerParameters

    root_agent = Agent(
        model="gemini-flash-latest",
        name="redis_mcp_agent",
        instruction="Use the search-records tool to answer questions.",
        tools=[
            McpToolset(
                connection_params=StdioConnectionParams(
                    server_params=StdioServerParameters(
                        command="rvl",
                        args=[
                            "mcp",
                            "--config",
                            "/path/to/mcp_config.yaml",
                            "--read-only",
                        ],
                    ),
                    timeout=30,
                ),
                tool_filter=["search-records"],
            ),
        ],
    )
    ```

    !!! note

        다른 ADK 언어에서 이 MCP 서버에 연결하는 방법은
        [MCP 도구](/ko/tools-custom/mcp-tools/)를 참고하세요.

=== "Sessions + Memory"

    REST 기반 세션 및 메모리 서비스를 통해 [Agent Memory Server](https://github.com/redis/agent-memory-server)를
    ADK `Runner`에 연결합니다. Working memory는 자동 요약을 통해 세션별
    상태를 처리하고, long-term memory는 세션 간 하이브리드 검색을 제공합니다.

    ```python
    from google.adk.agents import Agent
    from google.adk.runners import Runner

    from adk_redis import (
        RedisLongTermMemoryService,
        RedisLongTermMemoryServiceConfig,
        RedisWorkingMemorySessionService,
        RedisWorkingMemorySessionServiceConfig,
    )

    session_service = RedisWorkingMemorySessionService(
        config=RedisWorkingMemorySessionServiceConfig(
            api_base_url="http://localhost:8000",
        ),
    )
    memory_service = RedisLongTermMemoryService(
        config=RedisLongTermMemoryServiceConfig(
            api_base_url="http://localhost:8000",
            recency_boost=True,
        ),
    )

    root_agent = Agent(
        model="gemini-flash-latest",
        name="redis_memory_agent",
        instruction="Use long-term memory to personalize responses.",
    )

    runner = Runner(
        app_name="redis_memory_app",
        agent=root_agent,
        session_service=session_service,
        memory_service=memory_service,
    )
    ```

=== "Sessions + Memory MCP server"

    ADK의 네이티브 `McpToolset`을 SSE를 통해
    [Agent Memory Server](https://github.com/redis/agent-memory-server)의
    MCP 엔드포인트에 연결합니다. 이렇게 하면 REST 기반 서비스를 사용하지
    않고도 에이전트가 장기 메모리 작업에 직접 도구로 접근할 수 있습니다.

    ```python
    import os

    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams

    MEMORY_MCP_URL = os.getenv("MEMORY_MCP_URL", "http://localhost:9000")

    root_agent = Agent(
        model="gemini-flash-latest",
        name="memory_mcp_agent",
        instruction="Use memory tools to personalize responses.",
        tools=[
            McpToolset(
                connection_params=SseConnectionParams(
                    url=f"{MEMORY_MCP_URL.rstrip('/')}/sse",
                ),
                tool_filter=[
                    "search_long_term_memory",
                    "create_long_term_memories",
                    "memory_prompt",
                ],
            ),
        ],
    )
    ```

    !!! note

        Agent Memory Server는 REST API와 별도의 포트에서 MCP 엔드포인트를
        노출합니다. Docker Compose를 포함한 완전한 동작 예제는
        [fitness_coach_mcp 예제](https://github.com/redis-developer/adk-redis/tree/main/examples/fitness_coach_mcp)를
        참고하세요.

=== "Search tools"

    RedisVL 기반 `BaseTool` 하위 클래스를 사용해 Redis 인덱스에서 vector,
    hybrid, range, text, SQL 검색을 실행합니다. 도구를 기존 인덱스에
    바인딩하고 에이전트에 직접 전달합니다.

    ```python
    from google.adk.agents import Agent
    from redisvl.index import SearchIndex
    from redisvl.utils.vectorize import HFTextVectorizer

    from adk_redis import RedisVectorQueryConfig, RedisVectorSearchTool

    vectorizer = HFTextVectorizer(model="redis/langcache-embed-v2")
    index = SearchIndex.from_existing("products", redis_url="redis://localhost:6379")

    search_tool = RedisVectorSearchTool(
        index=index,
        vectorizer=vectorizer,
        config=RedisVectorQueryConfig(num_results=5),
        return_fields=["title", "price", "category"],
        name="search_products",
        description="Semantic search over the product catalog.",
    )

    root_agent = Agent(
        model="gemini-flash-latest",
        name="redis_search_agent",
        instruction="Help users find products using semantic search.",
        tools=[search_tool],
    )
    ```

## 시맨틱 캐싱

반복되거나 거의 중복되는 프롬프트가 모델을 건너뛰도록 LLM 호출 지점을
시맨틱 캐시로 감쌉니다. 자체 Redis와 vectorizer를 사용하는 자체 호스팅
방식 또는 [Redis LangCache](https://redis.io/langcache)를 통한 관리형
방식을 선택할 수 있습니다.

=== "Semantic cache (self-hosted)"

    자체 호스팅 시맨틱 캐싱에는 로컬 vectorizer와 자체 Redis 인스턴스가
    포함된 `RedisVLCacheProvider`를 사용합니다.

    ```python
    from google.adk.agents import Agent
    from redisvl.utils.vectorize import HFTextVectorizer

    from adk_redis import (
        LLMResponseCache,
        RedisVLCacheProvider,
        RedisVLCacheProviderConfig,
        create_llm_cache_callbacks,
    )

    provider = RedisVLCacheProvider(
        config=RedisVLCacheProviderConfig(
            redis_url="redis://localhost:6379",
            ttl=3600,
            distance_threshold=0.1,
        ),
        vectorizer=HFTextVectorizer(
            model="redis/langcache-embed-v2",
        ),
    )

    llm_cache = LLMResponseCache(provider=provider)
    before_model_cb, after_model_cb = create_llm_cache_callbacks(llm_cache)

    root_agent = Agent(
        model="gemini-flash-latest",
        name="cached_agent",
        instruction="You are a helpful assistant with semantic caching enabled.",
        before_model_callback=before_model_cb,
        after_model_callback=after_model_cb,
    )
    ```

=== "Semantic cache (LangCache)"

    관리형 시맨틱 캐싱 서비스인 [Redis LangCache](https://redis.io/langcache)와
    함께 `LangCacheProvider`를 사용합니다. 임베딩은 서버 측에서 처리되므로
    로컬 vectorizer가 필요 없습니다.

    ```python
    import os

    from google.adk.agents import Agent

    from adk_redis import (
        LLMResponseCache,
        LangCacheProvider,
        LangCacheProviderConfig,
        create_llm_cache_callbacks,
    )

    provider = LangCacheProvider(
        config=LangCacheProviderConfig(
            cache_id=os.environ["LANGCACHE_CACHE_ID"],
            api_key=os.environ["LANGCACHE_API_KEY"],
            server_url=os.getenv(
                "LANGCACHE_SERVER_URL",
                "https://aws-us-east-1.langcache.redis.io",
            ),
            ttl=3600,
        ),
    )

    llm_cache = LLMResponseCache(provider=provider)
    before_model_cb, after_model_cb = create_llm_cache_callbacks(llm_cache)

    root_agent = Agent(
        model="gemini-flash-latest",
        name="cached_agent",
        instruction="You are a helpful assistant with semantic caching enabled.",
        before_model_callback=before_model_cb,
        after_model_callback=after_model_cb,
    )
    ```

## 사용 가능한 도구

### 검색 도구

도구 | 설명
---- | -----------
`RedisVectorSearchTool` | RedisVL `VectorQuery`를 통한 vector similarity(KNN) 검색입니다.
`RedisHybridSearchTool` | Vector + BM25 하이브리드 검색입니다. Redis 8.4 이상에서는 네이티브 `FT.HYBRID`를 사용하고, 그 외 환경에서는 클라이언트 측 집계로 폴백합니다.
`RedisRangeSearchTool` | vector 거리 임곗값 안의 모든 문서를 반환합니다.
`RedisTextSearchTool` | BM25 키워드 full-text 검색입니다. vectorizer가 필요 없습니다.
`RedisSQLSearchTool` | 바인딩된 인덱스에 대해 `redisvl.query.SQLQuery`로 SQL `SELECT`를 실행합니다. `:name` 매개변수 placeholder를 지원합니다. `adk-redis[sql]`이 필요합니다.

### MCP

소스 | 설명
---- | -----------
[RedisVL MCP server](https://docs.redisvl.com/en/latest/user_guide/how_to_guides/mcp.html) (`rvl mcp`) | ADK의 네이티브 `McpToolset`을 실행 중인 `rvl mcp` 서버에 연결합니다. 서버는 YAML에 따라 vector / fulltext / hybrid 중 하나로 선택되는 `search-records`와 `upsert-records`를 노출하고, 인덱스 스키마에서 파생된 필터 및 반환 필드 힌트를 제공합니다. `stdio`, `sse`, `streamable-http`, HTTP bearer 인증을 지원하며, 서버의 `--read-only` 또는 `McpToolset`의 `tool_filter=["search-records"]`로 쓰기를 막을 수 있습니다. |
[Sessions + Memory MCP server](https://github.com/redis/agent-memory-server) | ADK의 네이티브 `McpToolset`을 SSE를 통해 Agent Memory Server의 MCP 엔드포인트에 연결합니다. `search_long_term_memory`, `create_long_term_memories`, `edit_long_term_memory`, `delete_long_term_memories`, `memory_prompt`를 노출합니다. REST API와 별도 포트에서 실행됩니다. |

### 메모리 도구

도구 | 설명
---- | -----------
`MemoryPromptTool` | 관련 메모리로 에이전트 프롬프트를 보강합니다.
`SearchMemoryTool` | 쿼리로 장기 메모리를 검색합니다.
`CreateMemoryTool` | 새 장기 메모리를 저장합니다.
`UpdateMemoryTool` | ID로 기존 메모리를 업데이트합니다.
`DeleteMemoryTool` | ID로 메모리를 삭제합니다.
`GetMemoryTool` | ID로 단일 메모리를 가져옵니다.

### 서비스

서비스 | 설명
------- | -----------
`RedisWorkingMemorySessionService` | Agent Memory Server working memory를 백엔드로 사용하는 `BaseSessionService`입니다. 컨텍스트 창이 초과되면 자동 요약합니다.
`RedisLongTermMemoryService` | recency-boosted semantic search를 지원하는 Agent Memory Server long-term memory 기반 `BaseMemoryService`입니다.

### 캐시 제공자

제공자 | 설명
-------- | -----------
`RedisVLCacheProvider` | RedisVL `SemanticCache`를 통한 자체 호스팅 시맨틱 캐시입니다. 자체 vectorizer를 사용합니다.
`LangCacheProvider` | [Redis LangCache](https://redis.io/langcache)를 통한 관리형 시맨틱 캐시입니다. 임베딩은 서버 측에서 처리됩니다.

## 추가 리소스

- [GitHub의 adk-redis](https://github.com/redis-developer/adk-redis)
- [PyPI의 adk-redis](https://pypi.org/project/adk-redis/)
- [adk-redis 문서](https://redis-developer.github.io/adk-redis/)
- [redis.io의 ADK + Redis](https://redis.io/docs/latest/integrate/google-adk/)
- [실행 가능한 예제](https://github.com/redis-developer/adk-redis/tree/main/examples)
- [Redis Agent Memory Server](https://github.com/redis/agent-memory-server)
- [RedisVL 문서](https://docs.redisvl.com)
- [Redis LangCache](https://redis.io/langcache)
