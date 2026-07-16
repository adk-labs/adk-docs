---
catalog_title: Milvus
catalog_description: ADK エージェントのための Milvus ベースのメモリおよび RAG 検索
catalog_icon: /integrations/assets/milvus.svg
catalog_tags: ["data"]
---

# ADK 用 Milvus 統合

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span>
</div>

[`adk-milvus`](https://github.com/zilliztech/adk-milvus) パッケージは、ADK Python エージェントをオープンソースのベクトルデータベースである [Milvus](https://milvus.io/) に接続します。`MilvusMemoryService` を介して永続的なセッションメモリとして使用したり、`MilvusToolset` を介して RAG ワークフロー用の `milvus_similarity_search` 検索ツールを提供したりできます。

Milvus は、同じ構成フィールドを使用して、ローカルで Milvus Lite として実行することも、自己ホスト型 Milvus サーバーまたは管理された [Zilliz Cloud](https://zilliz.com/cloud) デプロイメントとして実行することもできます。

## ユースケース

- **エージェント用の意味的メモリ(Semantic Memory)**: セッションイベントを Milvus に永続化し、後の会話で関連するメモリを検索します。
- **プライベートコンテンツ全体の RAG**: ドキュメントやスニペットをインデックスに登録し、エージェントがツール呼び出しを介して関連するコンテキストを取得できるようにします。
- **ローカルからクラウドへの開発**: ローカル開発用の Milvus Lite で開始し、URI とトークンを変更して Milvus サーバーまたは Zilliz Cloud に切り替えます。

## 前提条件

- Python 3.10 以降
- ADK for Python および `adk-milvus`
- 埋め込み（embedding）関数は、入力テキストごとに 1 つのベクトルを返します
- 次のいずれかの Milvus デプロイメント:
    - ローカル開発用の Milvus Lite
    - Milvus サーバー（例: `http://localhost:19530`）
    - Zilliz Cloud エンドポイントおよびトークン

## インストール

```bash
pip install adk-milvus
```

これにより、ADK 運行時依存関係、PyMilvus、および Milvus Lite のサポートがインストールされます。

## 構成

すべてのデプロイモードで `MILVUS_URI` と `MILVUS_TOKEN` を使用します。

```bash
# Milvus Lite
export MILVUS_URI="./adk_milvus.db"

# Milvus server
export MILVUS_URI="http://localhost:19530"

# Zilliz Cloud
export MILVUS_URI="https://your-endpoint.api.gcp-us-west1.zillizcloud.com"
export MILVUS_TOKEN="your-token"
```

`MILVUS_TOKEN` は、Zilliz Cloud のような認証されたデプロイメントにのみ必要です。デフォルト以外の Milvus データベースを使用する場合は、`MILVUS_DB_NAME` を設定してください。

## エージェントとの連携

=== "メモリサービス"

    `MilvusMemoryService` を `Runner` に接続して、セッション間メモリを維持および検索します。

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
        instruction="関連性がある場合に回答をパーソナライズするためにメモリを使用してください。",
    )

    runner = Runner(
        app_name="milvus_memory_app",
        agent=agent,
        session_service=InMemorySessionService(),
        memory_service=memory_service,
    )
    ```

    有意義なセッションの後に、それをメモリに追加して後で検索します。

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
        query="データベースの好みについてユーザーは何と言いましたか？",
    )
    for memory in result.memories:
        print(memory.content.parts[0].text)
    ```

=== "RAG ツールセット"

    `MilvusVectorStore` を使用してテキストにインデックスを付け、`MilvusToolset` を介して公開します。

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
            "Milvus Liteはローカルの RAG 開発に役立ちます。",
            "Zilliz Cloudは本番ワークロード用に管理された Milvus を提供します。",
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
        instruction="質問に答えるときは検索コンテキスト（retrieval context）を使用してください。",
        tools=tools,
    )
    ```

## 利用可能なツールと操作

### RAG ツールセット

ツール | 説明
---- | -----------
`milvus_similarity_search` | Milvus でインデックスされたテキストを検索し、コンテンツ、ソース、メタデータ、距離を含む一致する行を返します。

### メモリサービス

メソッド | 説明
---- | -----------
`add_session_to_memory(session)` | ADK セッションからテキストを含むイベントを永続化します。
`search_memory(app_name, user_id, query)` | ADK アプリとユーザーの範囲にスコープされたメモリを検索します。

## 注意事項

- `dimension` は埋め込みモデルの出力次元と一致する必要があります。
- `MilvusMemoryService` は `app_name` と `user_id` によって検索範囲を設定します。
- `MilvusVectorStore` は、コレクションが存在しない場合は作成し、再利用する前に既存のスキーマを検証します。
- コレクションの一貫性レベル（consistency level）とデータベース名は、より強力な read-after-write 動作や複数の Milvus データベースを必要とするデプロイメント向けに構成できます。

## リソース

- [ADK Milvus パッケージ](https://github.com/zilliztech/adk-milvus)
- [PyPI の ADK Milvus](https://pypi.org/project/adk-milvus/)
- [Milvus ドキュメント](https://milvus.io/docs)
- [Milvus Lite ドキュメント](https://milvus.io/docs/milvus_lite.md)
- [Zilliz Cloud](https://zilliz.com/cloud)
