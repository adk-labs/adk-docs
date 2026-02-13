---
catalog_title: Pinecone
catalog_description: データ保存、セマンティック検索、結果のリランキングを行います
catalog_icon: /adk-docs/integrations/assets/pinecone.png
catalog_tags: ["data","mcp"]
---

# ADK 向け Pinecone MCP ツール

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Pinecone MCP Server](https://github.com/pinecone-io/pinecone-mcp) は
ADK エージェントを AI アプリ向けベクターデータベース
[Pinecone](https://www.pinecone.io/) に接続します。この連携により
エージェントはインデックス管理、メタデータフィルタ付きセマンティック検索による
データ保存/検索、複数インデックス横断検索とリランキングを実行できます。

## ユースケース

- **セマンティック検索とリトリーバル**: 自然言語クエリ、
  メタデータフィルタ、リランキングを使って保存データを検索します。

- **ナレッジベース管理**: データを保存・管理して
  RAG (retrieval-augmented generation) システムを構築・維持します。

- **クロスインデックス検索**: 複数 Pinecone インデックスを同時検索し、
  結果を自動重複排除・リランキングします。

## 前提条件

- [Pinecone](https://www.pinecone.io/) アカウント
- [Pinecone Console](https://app.pinecone.io) の API キー

## エージェントで使う

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        PINECONE_API_KEY = "YOUR_PINECONE_API_KEY"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="pinecone_agent",
            instruction="Help users manage and search their Pinecone vector indexes",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "@pinecone-database/mcp",
                            ],
                            env={
                                "PINECONE_API_KEY": PINECONE_API_KEY,
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

        const PINECONE_API_KEY = "YOUR_PINECONE_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "pinecone_agent",
            instruction: "Help users manage and search their Pinecone vector indexes",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: ["-y", "@pinecone-database/mcp"],
                        env: {
                            PINECONE_API_KEY: PINECONE_API_KEY,
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

!!! note

    [integrated inference](https://docs.pinecone.io/guides/inference/understanding-inference)
    対応インデックスのみサポートされます。統合埋め込みモデルがないインデックスは
    この MCP サーバーではサポートされません。

## 利用可能なツール

### ドキュメント

Tool | Description
---- | -----------
`search-docs` | 公式 Pinecone ドキュメントを検索

### インデックス管理

Tool | Description
---- | -----------
`list-indexes` | すべての Pinecone インデックスを一覧表示
`describe-index` | インデックス設定を表示
`describe-index-stats` | レコード数や利用可能 namespace などの統計を取得
`create-index-for-model` | 統合推論モデル付き新規インデックスを作成

### データ操作

Tool | Description
---- | -----------
`upsert-records` | 統合推論対応インデックスにレコードを挿入/更新
`search-records` | メタデータフィルタとリランキング付きテキスト検索
`cascading-search` | 複数インデックスを検索し重複排除/リランキング
`rerank-documents` | 専用リランキングモデルでレコード/文書群を再順位付け

## 追加リソース

- [Pinecone MCP Server Repository](https://github.com/pinecone-io/pinecone-mcp)
- [Pinecone MCP Documentation](https://docs.pinecone.io/guides/operations/mcp-server)
- [Pinecone Documentation](https://docs.pinecone.io)
