---
catalog_title: Redis
catalog_description: エージェント向けのベクトル、ハイブリッド、SQL 検索とセッション、メモリ、セマンティックキャッシュ
catalog_icon: /integrations/assets/redis.svg
catalog_tags: ["data","mcp"]
---

# ADK 向け Redis 統合

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span>
</div>

[adk-redis 統合](https://github.com/redis-developer/adk-redis) は、ADK
エージェントを [Redis](https://redis.io/) に接続します。Redis インデックス
上の RedisVL ベース検索ツール、[Redis Agent Memory Server](https://github.com/redis/agent-memory-server)
を通じた永続セッションと長期メモリ、LLM レスポンスとツール結果のための
セマンティックキャッシュを利用できます。Redis はマネージドサービスまたは
セルフホスト（RediSearch モジュールを有効化した Redis 8.4 以降）で
実行できます。

この統合にはいくつかの使い方があります。

| アプローチ | 説明 |
|----------|------|
| **RedisVL MCP** | ADK のネイティブ `McpToolset` を実行中の [`rvl mcp`](https://docs.redisvl.com/en/latest/user_guide/how_to_guides/mcp.html) サーバーに接続します。スキーマ対応フィルターと返却フィールドヒントを備えた `search-records`（vector / fulltext / hybrid）と `upsert-records` を公開します。 |
| **Session + Memory サービス** | Agent Memory Server をバックエンドとする ADK `BaseSessionService` と `BaseMemoryService` の実装、`RedisWorkingMemorySessionService` と `RedisLongTermMemoryService` です。 |
| **Sessions + Memory MCP** | ADK のネイティブ `McpToolset` を SSE 経由で [Agent Memory Server](https://github.com/redis/agent-memory-server) の MCP エンドポイントに接続します。エージェントは `search_long_term_memory`、`create_long_term_memories`、`memory_prompt` に直接ツールとしてアクセスできます。 |
| **Search tools** | RedisVL クエリでバインド済みインデックスを検索する 5 つの `BaseTool` サブクラス（`RedisVectorSearchTool`、`RedisHybridSearchTool`、`RedisRangeSearchTool`、`RedisTextSearchTool`、`RedisSQLSearchTool`）です。 |

## ユースケース

- **データに対する RAG**: Redis インデックスに対して vector、hybrid、
  range、BM25 text、SQL 検索を実行します。Hybrid 検索は Redis 8.4 以降で
  ネイティブ `FT.HYBRID` を使い、それ以外ではクライアント側集約へ
  フォールバックします。
- **永続的なマルチターンエージェント**: セッションサービスとメモリサービスを
  任意の ADK `Runner` に接続し、会話状態を保持し、コンテキストウィンドウが
  埋まったら自動要約し、永続化すべき事実を長期メモリへ昇格します。
- **スキーマ対応 MCP ツール**: Redis インデックスごとに 1 つの `rvl mcp`
  サーバーを立て、複数のエージェントを `stdio`、`sse`、`streamable-http` で
  接続します。MCP ツール説明には、インデックススキーマから派生した
  フィルターと返却フィールドヒントが含まれます。
- **レイテンシとコストの削減**: LLM 呼び出し箇所をセマンティックキャッシュで
  包み、繰り返しまたはほぼ重複するプロンプトがモデルをスキップするようにします。

## 前提条件

- Python 3.10 以降
- RediSearch モジュールを有効化した Redis 8.4 以降、または
  [Redis Cloud](https://redis.io/cloud/)
- セッションとメモリサービスの場合: ローカルまたは環境で実行中の
  [Redis Agent Memory Server](https://github.com/redis/agent-memory-server)
- LangCache キャッシュプロバイダーの場合:
  [Redis LangCache](https://redis.io/langcache) キャッシュと API キー

## インストール

必要なコンポーネントをインストールします。

```bash
pip install 'adk-redis[memory]'      # session + long-term memory services
pip install 'adk-redis[search]'      # RedisVL-backed search tools
pip install 'adk-redis[sql]'         # RedisSQLSearchTool (sql-redis)
pip install 'adk-redis[langcache]'   # managed semantic cache provider
pip install 'adk-redis[all]'         # everything above

# For the RedisVL MCP server (used with ADK's native McpToolset):
pip install 'redisvl[mcp]>=0.18.2'
```

## エージェントで使用する

=== "RedisVL MCP server"

    [RedisVL MCP サーバー](https://docs.redisvl.com/en/latest/user_guide/how_to_guides/mcp.html)
    （`rvl mcp`）を Redis インデックスに向けて起動し、ADK のネイティブ
    `McpToolset` を接続します。次の例は stdio トランスポートを使うため、
    別のサーバープロセスは不要です。長時間実行されるリモートサーバーへ
    接続する場合は、`StreamableHTTPConnectionParams` または
    `SseConnectionParams` に置き換えてください。

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

        他の ADK 言語からこの MCP サーバーへ接続する方法については
        [MCP ツール](/ja/tools-custom/mcp-tools/)を参照してください。

=== "Sessions + Memory"

    REST ベースのセッションサービスとメモリサービスを通じて
    [Agent Memory Server](https://github.com/redis/agent-memory-server) を
    任意の ADK `Runner` に接続します。Working memory はセッションごとの
    状態を自動要約で処理し、long-term memory はセッション横断の
    ハイブリッド検索を提供します。

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

    ADK のネイティブ `McpToolset` を SSE 経由で
    [Agent Memory Server](https://github.com/redis/agent-memory-server) の
    MCP エンドポイントへ接続します。これにより、REST ベースサービスを
    使わずに、エージェントが長期メモリ操作へ直接ツールとしてアクセス
    できます。

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

        Agent Memory Server は REST API とは別のポートで MCP エンドポイントを
        公開します。Docker Compose を含む完全な動作例は
        [fitness_coach_mcp の例](https://github.com/redis-developer/adk-redis/tree/main/examples/fitness_coach_mcp)
        を参照してください。

=== "Search tools"

    RedisVL ベースの `BaseTool` サブクラスを使って、Redis インデックスに
    対して vector、hybrid、range、text、SQL 検索を実行します。ツールを
    既存インデックスにバインドし、エージェントへ直接渡します。

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

## セマンティックキャッシュ

繰り返しまたはほぼ重複するプロンプトがモデルをスキップするように、LLM
呼び出し箇所をセマンティックキャッシュで包みます。自分の Redis と
vectorizer を使うセルフホスト方式、または [Redis LangCache](https://redis.io/langcache)
によるマネージド方式を選択できます。

=== "Semantic cache (self-hosted)"

    セルフホストのセマンティックキャッシュには、ローカル vectorizer と
    自分の Redis インスタンスを使う `RedisVLCacheProvider` を使用します。

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

    マネージドのセマンティックキャッシュサービスである
    [Redis LangCache](https://redis.io/langcache) と `LangCacheProvider` を
    使用します。埋め込みはサーバー側で処理されるため、ローカル vectorizer
    は不要です。

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

## 利用可能なツール

### 検索ツール

ツール | 説明
---- | -----------
`RedisVectorSearchTool` | RedisVL `VectorQuery` による vector similarity（KNN）検索です。
`RedisHybridSearchTool` | Vector + BM25 ハイブリッド検索です。Redis 8.4 以降ではネイティブ `FT.HYBRID` を使い、それ以外ではクライアント側集約にフォールバックします。
`RedisRangeSearchTool` | vector 距離しきい値内のすべてのドキュメントを返します。
`RedisTextSearchTool` | BM25 キーワード全文検索です。vectorizer は不要です。
`RedisSQLSearchTool` | バインド済みインデックスに対して `redisvl.query.SQLQuery` で SQL `SELECT` を実行します。`:name` パラメータプレースホルダーをサポートします。`adk-redis[sql]` が必要です。

### MCP

ソース | 説明
---- | -----------
[RedisVL MCP server](https://docs.redisvl.com/en/latest/user_guide/how_to_guides/mcp.html) (`rvl mcp`) | ADK のネイティブ `McpToolset` を実行中の `rvl mcp` サーバーに接続します。サーバーは YAML に応じて vector / fulltext / hybrid のいずれかを使う `search-records` と `upsert-records` を公開し、インデックススキーマから派生したフィルターと返却フィールドヒントを提供します。`stdio`、`sse`、`streamable-http`、HTTP bearer 認証をサポートし、サーバー側の `--read-only` または `McpToolset` の `tool_filter=["search-records"]` で書き込みを抑制できます。 |
[Sessions + Memory MCP server](https://github.com/redis/agent-memory-server) | ADK のネイティブ `McpToolset` を SSE 経由で Agent Memory Server の MCP エンドポイントに接続します。`search_long_term_memory`、`create_long_term_memories`、`edit_long_term_memory`、`delete_long_term_memories`、`memory_prompt` を公開します。REST API とは別のポートで実行されます。 |

### メモリツール

ツール | 説明
---- | -----------
`MemoryPromptTool` | 関連メモリでエージェントプロンプトを拡張します。
`SearchMemoryTool` | クエリで長期メモリを検索します。
`CreateMemoryTool` | 新しい長期メモリを保存します。
`UpdateMemoryTool` | ID で既存メモリを更新します。
`DeleteMemoryTool` | ID でメモリを削除します。
`GetMemoryTool` | ID で単一メモリを取得します。

### サービス

サービス | 説明
------- | -----------
`RedisWorkingMemorySessionService` | Agent Memory Server working memory をバックエンドとする `BaseSessionService` です。コンテキストウィンドウを超えると自動要約します。
`RedisLongTermMemoryService` | recency-boosted semantic search を備えた Agent Memory Server long-term memory ベースの `BaseMemoryService` です。

### キャッシュプロバイダー

プロバイダー | 説明
-------- | -----------
`RedisVLCacheProvider` | RedisVL `SemanticCache` によるセルフホストのセマンティックキャッシュです。自分の vectorizer を使います。
`LangCacheProvider` | [Redis LangCache](https://redis.io/langcache) によるマネージドのセマンティックキャッシュです。埋め込みはサーバー側で処理されます。

## 追加リソース

- [GitHub の adk-redis](https://github.com/redis-developer/adk-redis)
- [PyPI の adk-redis](https://pypi.org/project/adk-redis/)
- [adk-redis ドキュメント](https://redis-developer.github.io/adk-redis/)
- [redis.io の ADK + Redis](https://redis.io/docs/latest/integrate/google-adk/)
- [実行可能なサンプル](https://github.com/redis-developer/adk-redis/tree/main/examples)
- [Redis Agent Memory Server](https://github.com/redis/agent-memory-server)
- [RedisVL ドキュメント](https://docs.redisvl.com)
- [Redis LangCache](https://redis.io/langcache)
