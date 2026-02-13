---
catalog_title: Qdrant
catalog_description: セマンティックベクトル検索で情報を保存・取得します
catalog_icon: /adk-docs/integrations/assets/qdrant.png
catalog_tags: ["data","mcp"]
---

# ADK 向け Qdrant MCP ツール

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Qdrant MCP Server](https://github.com/qdrant/mcp-server-qdrant) は
ADK エージェントをオープンソースのベクトル検索エンジン
[Qdrant](https://qdrant.tech/) に接続します。この連携により、
エージェントはセマンティック検索で情報を保存・取得できます。

## ユースケース

- **エージェント向けセマンティックメモリ**: 会話コンテキスト、事実、学習情報を保存し、
  後で自然言語クエリで取得できます。

- **コードリポジトリ検索**: コードスニペット、ドキュメント、実装パターンの検索可能インデックスを作り、
  セマンティックに問い合わせできます。

- **ナレッジベース検索**: 文書を保存し、応答に必要な関連コンテキストを取得する
  RAG システムを構築します。

## 前提条件

- 実行中の Qdrant インスタンス。次のいずれかを利用できます:
    - [Qdrant Cloud](https://cloud.qdrant.io/) (マネージドサービス)
    - Docker でローカル実行: `docker run -p 6333:6333 qdrant/qdrant`
- (任意) 認証用の Qdrant API キー

## エージェントで使う

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        QDRANT_URL = "http://localhost:6333"  # Or your Qdrant Cloud URL
        COLLECTION_NAME = "my_collection"
        # QDRANT_API_KEY = "YOUR_QDRANT_API_KEY"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="qdrant_agent",
            instruction="Help users store and retrieve information using semantic search",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="uvx",
                            args=["mcp-server-qdrant"],
                            env={
                                "QDRANT_URL": QDRANT_URL,
                                "COLLECTION_NAME": COLLECTION_NAME,
                                # "QDRANT_API_KEY": QDRANT_API_KEY,
                            }
                        ),
                        timeout=30,
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "Local MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const QDRANT_URL = "http://localhost:6333"; // Or your Qdrant Cloud URL
        const COLLECTION_NAME = "my_collection";
        // const QDRANT_API_KEY = "YOUR_QDRANT_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "qdrant_agent",
            instruction: "Help users store and retrieve information using semantic search",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "uvx",
                        args: ["mcp-server-qdrant"],
                        env: {
                            QDRANT_URL: QDRANT_URL,
                            COLLECTION_NAME: COLLECTION_NAME,
                            // QDRANT_API_KEY: QDRANT_API_KEY,
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## 利用可能なツール

Tool | Description
---- | -----------
`qdrant-store` | 任意メタデータ付きで情報を Qdrant に保存
`qdrant-find` | 自然言語クエリで関連情報を検索

## 設定

Qdrant MCP サーバーは環境変数で設定できます:

Variable | Description | Default
-------- | ----------- | -------
`QDRANT_URL` | Qdrant サーバー URL | `None` (required)
`QDRANT_API_KEY` | Qdrant Cloud 認証 API キー | `None`
`COLLECTION_NAME` | 使用するコレクション名 | `None`
`QDRANT_LOCAL_PATH` | ローカル永続ストレージパス (URL の代替) | `None`
`EMBEDDING_MODEL` | 使用する埋め込みモデル | `sentence-transformers/all-MiniLM-L6-v2`
`EMBEDDING_PROVIDER` | 埋め込みプロバイダー (`fastembed` または `ollama`) | `fastembed`
`TOOL_STORE_DESCRIPTION` | 保存ツールのカスタム説明 | 既定説明
`TOOL_FIND_DESCRIPTION` | 検索ツールのカスタム説明 | 既定説明

### カスタムツール説明

ツール説明をカスタマイズしてエージェントの挙動を誘導できます:

```python
env={
    "QDRANT_URL": "http://localhost:6333",
    "COLLECTION_NAME": "code-snippets",
    "TOOL_STORE_DESCRIPTION": "Store code snippets with descriptions. The 'information' parameter should contain a description of what the code does, while the actual code should be in 'metadata.code'.",
    "TOOL_FIND_DESCRIPTION": "Search for relevant code snippets using natural language. Describe the functionality you're looking for.",
}
```

## 追加リソース

- [Qdrant MCP Server Repository](https://github.com/qdrant/mcp-server-qdrant)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Qdrant Cloud](https://cloud.qdrant.io/)
