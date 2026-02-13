---
catalog_title: MongoDB
catalog_description: コレクション照会、データベース管理、スキーマ分析を行います
catalog_icon: /adk-docs/integrations/assets/mongodb.png
catalog_tags: ["data","mcp"]
---

# ADK 向け MongoDB MCP ツール

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[MongoDB MCP Server](https://github.com/mongodb-js/mongodb-mcp-server) は
ADK エージェントを [MongoDB](https://www.mongodb.com/) データベースおよび
MongoDB Atlas クラスターに接続します。この連携により、エージェントは
自然言語でコレクション照会、データベース管理、MongoDB Atlas インフラ操作を実行できます。

## ユースケース

- **データ探索と分析**: 自然言語で MongoDB コレクションを照会し、
  集計を実行し、複雑なクエリを手書きせずにドキュメントスキーマを分析します。

- **データベース管理**: データベース/コレクション一覧、インデックス作成、
  ユーザー管理、統計監視を会話操作で実行します。

- **Atlas インフラ管理**: MongoDB Atlas クラスター作成/管理、
  アクセスリスト設定、性能推奨事項の確認をエージェントから直接行います。

## 前提条件

- **データベースアクセス用**: MongoDB 接続文字列 (ローカル/セルフホスト/Atlas)
- **Atlas 管理用**: API 資格情報 (client ID と secret) を持つ
  [MongoDB Atlas](https://www.mongodb.com/atlas) サービスアカウント

## エージェントで使う

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        # For database access, use a connection string:
        CONNECTION_STRING = "mongodb://localhost:27017/myDatabase"

        # For Atlas management, use API credentials:
        # ATLAS_CLIENT_ID = "YOUR_ATLAS_CLIENT_ID"
        # ATLAS_CLIENT_SECRET = "YOUR_ATLAS_CLIENT_SECRET"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="mongodb_agent",
            instruction="Help users query and manage MongoDB databases",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "mongodb-mcp-server",
                                "--readOnly",  # Remove for write operations
                            ],
                            env={
                                # For database access, use:
                                "MDB_MCP_CONNECTION_STRING": CONNECTION_STRING,
                                # For Atlas management, use:
                                # "MDB_MCP_API_CLIENT_ID": ATLAS_CLIENT_ID,
                                # "MDB_MCP_API_CLIENT_SECRET": ATLAS_CLIENT_SECRET,
                            },
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

        // For database access, use a connection string:
        const CONNECTION_STRING = "mongodb://localhost:27017/myDatabase";

        // For Atlas management, use API credentials:
        // const ATLAS_CLIENT_ID = "YOUR_ATLAS_CLIENT_ID";
        // const ATLAS_CLIENT_SECRET = "YOUR_ATLAS_CLIENT_SECRET";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "mongodb_agent",
            instruction: "Help users query and manage MongoDB databases",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: [
                            "-y",
                            "mongodb-mcp-server",
                            "--readOnly", // Remove for write operations
                        ],
                        env: {
                            // For database access, use:
                            MDB_MCP_CONNECTION_STRING: CONNECTION_STRING,
                            // For Atlas management, use:
                            // MDB_MCP_API_CLIENT_ID: ATLAS_CLIENT_ID,
                            // MDB_MCP_API_CLIENT_SECRET: ATLAS_CLIENT_SECRET,
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## 利用可能なツール

### MongoDB データベースツール

Tool | Description
---- | -----------
`find` | MongoDB コレクションに find クエリを実行
`aggregate` | MongoDB コレクションで集計を実行
`count` | コレクション内ドキュメント数を取得
`list-databases` | MongoDB 接続の全データベースを一覧表示
`list-collections` | 指定 DB の全コレクションを一覧表示
`collection-schema` | コレクションスキーマを説明
`collection-indexes` | コレクションインデックスを説明
`insert-many` | コレクションへドキュメントを挿入
`update-many` | フィルタ一致ドキュメントを更新
`delete-many` | フィルタ一致ドキュメントを削除
`create-collection` | 新規コレクション作成
`drop-collection` | DB からコレクション削除
`drop-database` | データベース削除
`create-index` | コレクションインデックス作成
`drop-index` | コレクションインデックス削除
`rename-collection` | コレクション名変更
`db-stats` | データベース統計取得
`explain` | クエリ実行統計取得
`export` | クエリ結果を EJSON 形式でエクスポート

### MongoDB Atlas ツール

!!! note

    Atlas ツールには API 資格情報が必要です。Atlas ツールを有効化するには
    `MDB_MCP_API_CLIENT_ID` と `MDB_MCP_API_CLIENT_SECRET` を設定してください。

Tool | Description
---- | -----------
`atlas-list-orgs` | MongoDB Atlas 組織一覧
`atlas-list-projects` | MongoDB Atlas プロジェクト一覧
`atlas-list-clusters` | MongoDB Atlas クラスター一覧
`atlas-inspect-cluster` | クラスターメタデータを調査
`atlas-list-db-users` | DB ユーザー一覧
`atlas-create-free-cluster` | 無料 Atlas クラスター作成
`atlas-create-project` | Atlas プロジェクト作成
`atlas-create-db-user` | DB ユーザー作成
`atlas-create-access-list` | IP アクセスリスト設定
`atlas-inspect-access-list` | IP アクセスリスト項目表示
`atlas-list-alerts` | Atlas アラート一覧
`atlas-get-performance-advisor` | パフォーマンス推奨事項取得

## 設定

### 環境変数

Variable | Description
-------- | -----------
`MDB_MCP_CONNECTION_STRING` | DB アクセス用 MongoDB 接続文字列
`MDB_MCP_API_CLIENT_ID` | Atlas ツール用 Atlas API client ID
`MDB_MCP_API_CLIENT_SECRET` | Atlas ツール用 Atlas API client secret
`MDB_MCP_READ_ONLY` | read-only モード有効化 (`true` または `false`)
`MDB_MCP_DISABLED_TOOLS` | 無効化するツールのカンマ区切り一覧
`MDB_MCP_LOG_PATH` | ログファイルディレクトリ

### Read-only モード

`--readOnly` フラグはサーバーを read、connect、metadata 操作のみに制限します。
これにより create、update、delete 操作を防止し、
意図しない変更リスクなく安全にデータ探索できます。

### ツール無効化

`MDB_MCP_DISABLED_TOOLS` で特定ツール/カテゴリを無効化できます:

- ツール名: `find`, `aggregate`, `insert-many` など
- カテゴリ: `atlas` (全 Atlas ツール)、`mongodb` (全 DB ツール)
- 操作タイプ: `create`, `update`, `delete`, `read`, `metadata`

## 追加リソース

- [MongoDB MCP Server Repository](https://github.com/mongodb-js/mongodb-mcp-server)
- [MongoDB Documentation](https://www.mongodb.com/docs/)
- [MongoDB Atlas](https://www.mongodb.com/atlas)
