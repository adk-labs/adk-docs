---
catalog_title: Chroma
catalog_description: セマンティックベクトル検索で情報を保存・取得します
catalog_icon: /integrations/assets/chroma.png
catalog_tags: ["data","mcp"]
---

# ADK 向け Chroma MCP ツール

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Chroma MCP Server](https://github.com/chroma-core/chroma-mcp) は
ADK エージェントをオープンソース埋め込みデータベース
[Chroma](https://www.trychroma.com/) に接続します。
この連携により、エージェントはコレクション作成、ドキュメント保存、
セマンティック検索、全文検索、メタデータフィルタリングを使った情報取得を行えます。

## ユースケース

- **エージェント向けセマンティックメモリ**: 会話コンテキスト、事実、学習情報を保存し、
  後で自然言語クエリで取得できます。

- **ナレッジベースからの情報取得**: ドキュメントを保存し、
  応答に必要な関連コンテキストを取得する RAG（検索拡張生成）システムを構築します。

- **セッション横断の永続コンテキスト**: 会話をまたいで長期記憶を維持し、
  過去のやり取りや蓄積された知識を参照できるようにします。

## 前提条件

- **ローカル保存の場合**: データを永続化するディレクトリのパス
- **Chroma Cloud の場合**: テナント ID、データベース名、API キーを持つ
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

ツール | 説明
---- | -----------
`chroma_list_collections` | ページネーション対応ですべてのコレクションを一覧表示します
`chroma_create_collection` | 任意の HNSW 設定を指定して新しいコレクションを作成します
`chroma_get_collection_info` | コレクションの詳細情報を取得します
`chroma_get_collection_count` | コレクション内のドキュメント数を取得します
`chroma_modify_collection` | コレクションの名前またはメタデータを更新します
`chroma_delete_collection` | コレクションを削除します
`chroma_peek_collection` | コレクション内のドキュメントのサンプルを表示します

### ドキュメント操作

ツール | 説明
---- | -----------
`chroma_add_documents` | 任意のメタデータとカスタム ID を指定してドキュメントを追加します
`chroma_query_documents` | 高度なフィルタリングを用いたセマンティック検索でドキュメントをクエリします
`chroma_get_documents` | ID またはフィルタでドキュメントを取得します（ページネーション対応）
`chroma_update_documents` | 既存ドキュメントのコンテンツ、メタデータ、または埋め込みを更新します
`chroma_delete_documents` | コレクションから特定のドキュメントを削除します

## 設定

Chroma MCP サーバーは要件に応じて複数のクライアントタイプをサポートします:

### クライアントタイプ

クライアントタイプ | 説明 | 主な引数
----------- | ----------- | -------------
`ephemeral` | インメモリ保存（再起動時に消去）。テスト向け。 | なし（デフォルト）
`persistent` | ローカルマシンのファイルベース保存 | `--data-dir`
`http` | セルフホスト型 Chroma サーバーへ接続 | `--host`, `--port`, `--ssl`, `--custom-auth-credentials`
`cloud` | Chroma Cloud（api.trychroma.com）へ接続 | `--tenant`, `--database`, `--api-key`

### 環境変数

環境変数を使用してクライアントを設定することもできます。
コマンドライン引数は環境変数より優先されます。

変数 | 説明
-------- | -----------
`CHROMA_CLIENT_TYPE` | クライアントタイプ: `ephemeral`、`persistent`、`http`、または `cloud`
`CHROMA_DATA_DIR` | 永続ローカルストレージのパス
`CHROMA_TENANT` | Chroma Cloud のテナント ID
`CHROMA_DATABASE` | Chroma Cloud のデータベース名
`CHROMA_API_KEY` | Chroma Cloud の API キー
`CHROMA_HOST` | セルフホスト HTTP クライアントのホスト
`CHROMA_PORT` | セルフホスト HTTP クライアントのポート
`CHROMA_SSL` | HTTP クライアントの SSL 有効化（`true` または `false`）
`CHROMA_DOTENV_PATH` | `.env` ファイルのパス（デフォルトは `.chroma_env`）

## 追加リソース

- [Chroma MCP Server Repository](https://github.com/chroma-core/chroma-mcp)
- [Chroma Documentation](https://docs.trychroma.com/)
- [Chroma Cloud](https://www.trychroma.com/)
