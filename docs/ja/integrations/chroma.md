---
catalog_title: Chroma
catalog_description: セマンティックベクトル検索で情報を保存・取得します
catalog_icon: /adk-docs/integrations/assets/chroma.png
catalog_tags: ["data","mcp"]
---

# ADK 向け Chroma MCP ツール

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Chroma MCP Server](https://github.com/chroma-core/chroma-mcp) は
ADK エージェントをオープンソース埋め込みデータベース
[Chroma](https://www.trychroma.com/) に接続します。
この連携により、エージェントはコレクション作成、ドキュメント保存、
セマンティック検索、全文検索、メタデータフィルタリングを使った情報取得を行えます。

## ユースケース

- **エージェント向けセマンティックメモリ**: 会話コンテキスト、事実、学習情報を保存し、
  後で自然言語クエリで取得できます。

- **ナレッジベース検索**: 文書を保存し、
  応答に必要な関連コンテキストを取得する RAG システムを構築します。

- **セッション横断の永続コンテキスト**: 会話をまたいで長期記憶を維持し、
  過去やり取りと蓄積知識を参照できるようにします。

## 前提条件

- **ローカル保存の場合**: データ永続化用ディレクトリパス
- **Chroma Cloud の場合**: tenant ID、database name、API key を持つ
  [Chroma Cloud](https://www.trychroma.com/) アカウント

## エージェントで使う

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        # For local storage, use:
        DATA_DIR = "/path/to/your/data/directory"

        # For Chroma Cloud, use:
        # CHROMA_TENANT = "your-tenant-id"
        # CHROMA_DATABASE = "your-database-name"
        # CHROMA_API_KEY = "your-api-key"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="chroma_agent",
            instruction="Help users store and retrieve information using semantic search",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="uvx",
                            args=[
                                "chroma-mcp",
                                # For local storage, use:
                                "--client-type",
                                "persistent",
                                "--data-dir",
                                DATA_DIR,
                                # For Chroma Cloud, use:
                                # "--client-type",
                                # "cloud",
                                # "--tenant",
                                # CHROMA_TENANT,
                                # "--database",
                                # CHROMA_DATABASE,
                                # "--api-key",
                                # CHROMA_API_KEY,
                            ],
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

        // For local storage, use:
        const DATA_DIR = "/path/to/your/data/directory";

        // For Chroma Cloud, use:
        // const CHROMA_TENANT = "your-tenant-id";
        // const CHROMA_DATABASE = "your-database-name";
        // const CHROMA_API_KEY = "your-api-key";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "chroma_agent",
            instruction: "Help users store and retrieve information using semantic search",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "uvx",
                        args: [
                            "chroma-mcp",
                            // For local storage, use:
                            "--client-type",
                            "persistent",
                            "--data-dir",
                            DATA_DIR,
                            // For Chroma Cloud, use:
                            // "--client-type",
                            // "cloud",
                            // "--tenant",
                            // CHROMA_TENANT,
                            // "--database",
                            // CHROMA_DATABASE,
                            // "--api-key",
                            // CHROMA_API_KEY,
                        ],
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## 利用可能なツール

### コレクション管理

Tool | Description
---- | -----------
`chroma_list_collections` | ページネーション対応ですべてのコレクションを一覧表示
`chroma_create_collection` | 任意 HNSW 設定付きで新規コレクション作成
`chroma_get_collection_info` | コレクション詳細取得
`chroma_get_collection_count` | コレクション内ドキュメント数取得
`chroma_modify_collection` | コレクション名またはメタデータ更新
`chroma_delete_collection` | コレクション削除
`chroma_peek_collection` | コレクション内ドキュメントのサンプル表示

### ドキュメント操作

Tool | Description
---- | -----------
`chroma_add_documents` | 任意メタデータとカスタム ID 付きでドキュメント追加
`chroma_query_documents` | 高度フィルタ付きセマンティック検索クエリ
`chroma_get_documents` | ID またはフィルタでドキュメント取得 (ページネーション対応)
`chroma_update_documents` | 既存ドキュメント内容/メタデータ/埋め込み更新
`chroma_delete_documents` | コレクションから特定ドキュメント削除

## 設定

Chroma MCP サーバーは要件に応じて複数クライアントタイプをサポートします:

### Client types

Client Type | Description | Key Arguments
----------- | ----------- | -------------
`ephemeral` | インメモリ保存。再起動で消去。テスト向け。 | None (default)
`persistent` | ローカルマシンのファイルベース保存 | `--data-dir`
`http` | セルフホスト Chroma サーバーへ接続 | `--host`, `--port`, `--ssl`, `--custom-auth-credentials`
`cloud` | Chroma Cloud (api.trychroma.com) へ接続 | `--tenant`, `--database`, `--api-key`

### 環境変数

環境変数でもクライアント設定可能です。
コマンドライン引数は環境変数より優先されます。

Variable | Description
-------- | -----------
`CHROMA_CLIENT_TYPE` | クライアント種別: `ephemeral`, `persistent`, `http`, `cloud`
`CHROMA_DATA_DIR` | 永続ローカル保存パス
`CHROMA_TENANT` | Chroma Cloud tenant ID
`CHROMA_DATABASE` | Chroma Cloud database name
`CHROMA_API_KEY` | Chroma Cloud API key
`CHROMA_HOST` | セルフホスト HTTP client host
`CHROMA_PORT` | セルフホスト HTTP client port
`CHROMA_SSL` | HTTP client の SSL 有効化 (`true` or `false`)
`CHROMA_DOTENV_PATH` | `.env` ファイルパス (デフォルト `.chroma_env`)

## 追加リソース

- [Chroma MCP Server Repository](https://github.com/chroma-core/chroma-mcp)
- [Chroma Documentation](https://docs.trychroma.com/)
- [Chroma Cloud](https://www.trychroma.com/)
