---
catalog_title: ClickHouse Cloud
catalog_description: データのクエリ、スキーマ探索、サービスとコストの監視
catalog_tags: ["data", "mcp"]
---

# ADK 向け ClickHouse Cloud MCP ツール

<div class="language-support-tag">
  <span class="lst-supported">ADK でサポート</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[ClickHouse Cloud リモート MCP サーバー](https://clickhouse.com/docs/cloud/features/ai-ml/remote-mcp)は、ADK エージェントをご利用の ClickHouse Cloud サービスに直接接続します。エージェントはデータベースやテーブルの一覧表示、スキーマの確認、読み取り専用 SQL クエリの実行、サービス・バックアップ・ClickPipes・課金情報の可視化、そして多くの追加ツールへのアクセスが可能になります。

このサーバーはフルマネージドで提供され、ローカルへのインストールや Docker コンテナ、API キーの設定は不要です。認証には OAuth 2.0 を使用し、アクセス権限は認証されたユーザーがアクセスを許可されている組織やサービスにスコープされます。

## ユースケース

- **データの探索と分析**: データベースやテーブルを検出してカラム定義を確認し、自然言語で分析用 SELECT クエリを実行します。「過去 7 日間の国別の平均セッション時間は？」と質問すると、エージェントがそれを SQL に変換して実行します。
- **インサイトとレポートの生成**: カスタム データ パイプラインを構築することなく、分析結果をサマリー、ビジュアライゼーション、またはダウンストリームのワークフローに取り込みます。
- **インフラストラクチャの監視**: 組織内のサービス一覧の取得、サービス ステータスや詳細の確認、バックアップ スケジュールや最新のバックアップの確認、構成された ClickPipes の検査を行います。
- **コストの追跡**: 日付範囲における日別のエンティティごとにかかったコスト記録など、組織の請求データや使用量データを取得します。

## 前提条件

- 稼働中の ClickHouse インスタンス（[ClickHouse Cloud](https://clickhouse.com/cloud) またはセルフホスト）
- **ローカル MCP サーバー**: [uv](https://docs.astral.sh/uv/) がインストールされていること（[mcp-clickhouse](https://github.com/ClickHouse/mcp-clickhouse) の実行に `uvx` を使用）、およびエージェントに必要な最小限の権限を持つ ClickHouse ユーザー
- **リモート MCP サーバー**（ClickHouse Cloud のみ）: サービスでリモート MCP サーバーが有効になっていること。ClickHouse Cloud コンソールでサービスを開き、**Connect** をクリックして **Connect with MCP** を選択し、トグルをオンにします。

## エージェントでの使用

=== "Python"

    === "ローカル MCP サーバー"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        clickhouse_tools = McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="uvx",
                    args=["mcp-clickhouse"],
                    env={
                        "CLICKHOUSE_HOST": "<your-instance>.clickhouse.cloud",
                        "CLICKHOUSE_USER": "<clickhouse-user>",
                        "CLICKHOUSE_PASSWORD": "<clickhouse-password>",
                        "CLICKHOUSE_PORT": "8443",
                    },
                ),
                timeout=60,
            )
        )

        root_agent = Agent(
            model="gemini-flash-latest",
            name="clickhouse_agent",
            instruction="Help users explore and analyze data in ClickHouse. "
            "Use the ClickHouse tools to query the data before answering. "
            "Always ground your answer in actual query results, not assumptions.",
            tools=[clickhouse_tools],
        )
        ```

        `CLICKHOUSE_HOST` をインスタンスのホスト名に置き換えます（ClickHouse Cloud でもセルフホストでも機能します）。エージェントに必要な権限のみを持つ専用のデータベース ユーザーを使用してください。`default` や管理者ユーザーの使用は避けてください。クエリはデフォルトで読み取り専用として実行されます。

    === "リモート MCP サーバー"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

        root_agent = Agent(
            model="gemini-flash-latest",
            name="clickhouse_agent",
            instruction="Help users explore and analyze data in ClickHouse Cloud",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://mcp.clickhouse.cloud/mcp",
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "リモート MCP サーバー"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "clickhouse_agent",
            instruction: "Help users explore and analyze data in ClickHouse Cloud",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://mcp.clickhouse.cloud/mcp",
                }),
            ],
        });

        export { rootAgent };
        ```

!!! note

    リモート MCP サーバーの場合、エージェントが最初に接続したときにブラウザが開き、ClickHouse Cloud の認証情報でログインして接続を承認するよう求められます。アクセスは、ユーザーが権限を持つ組織およびサービスにスコープされます。一方、ローカル MCP サーバーは OAuth フローを使用せず、環境変数のデータベース認証情報で認証します。

## セキュリティ (Safety)

リモート MCP サーバーによって公開されるすべてのツールは**読み取り専用 (read-only)** です。各ツールには、MCP メタデータに `readOnlyHint: true` の注釈が付けられています。データを変更したり、サービス設定を変更したり、破壊的な操作を実行できるツールはありません。`run_select_query` ツールは `SELECT` ステートメントのみを許可します。

ローカル MCP サーバーもデフォルトで読み取り専用です。書き込みアクセスを許可するには、明示的に `CLICKHOUSE_ALLOW_WRITE_ACCESS=true` を設定する必要があり、破壊的操作（DROP, TRUNCATE）にはさらに `CLICKHOUSE_ALLOW_DROP=true` が必要です。

## 利用可能なツール

### ローカル MCP サーバー

ツール | 説明
---- | -----------
`run_query` | SQL クエリの実行（デフォルトで読み取り専用）
`list_databases` | ClickHouse インスタンス上のすべてのデータベースを一覧表示
`list_tables` | ページネーションおよびオプションの `like`/`not_like` フィルターを使用してデータベース内のテーブルを一覧表示

### リモート MCP サーバー (ClickHouse Cloud)

リモート サーバーは、以下のカテゴリの読み取り専用ツールを公開します。

### クエリおよびスキーマの探索

ツール | 説明
---- | -----------
`run_select_query` | ClickHouse サービスに対して読み取り専用の SELECT クエリを実行
`list_databases` | ClickHouse サービスで利用可能なすべてのデータベースを一覧表示
`list_tables` | カラム定義を含むデータベース内のすべてのテーブルを一覧表示（オプションで `like`/`notLike` フィルター利用可能）

### 組織 (Organizations)

ツール | 説明
---- | -----------
`get_organizations` | 認証されたユーザーがアクセス可能なすべての ClickHouse Cloud 組織を取得
`get_organization_details` | 単一の組織の詳細を返す

### サービス (Services)

ツール | 説明
---- | -----------
`get_services_list` | ClickHouse Cloud 組織内のすべてのサービスを一覧表示
`get_service_details` | 特定のサービスの詳細を返す

### バックアップ (Backups)

ツール | 説明
---- | -----------
`list_service_backups` | サービスのすべてのバックアップを最新順に一覧表示
`get_service_backup_details` | 単一のバックアップの詳細を返す
`get_service_backup_configuration` | サービスのバックアップ構成（スケジュールと保持設定）を返す

### ClickPipes

ツール | 説明
---- | -----------
`list_clickpipes` | サービスに構成されているすべての ClickPipes を一覧表示
`get_clickpipe` | 特定の ClickPipe の詳細を返す

### 請求 (Billing)

ツール | 説明
---- | -----------
`get_organization_cost` | 組織の請求および利用コスト データを取得（オプションで `from_date`/`to_date`、最大 31 日間の範囲）

## ローカルとリモートの選択

|                    | ローカル MCP サーバー                                                      | リモート MCP サーバー                                                                      |
| ------------------ | -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| **ソース**         | [mcp-clickhouse](https://github.com/ClickHouse/mcp-clickhouse)（オープンソース） | ClickHouse Cloud による完全マネージド                                                      |
| **トランスポート** | `uvx` 経由のローカル stdio                                                  | ストリーミング可能な HTTP (`https://mcp.clickhouse.cloud/mcp`)                              |
| **対応環境**       | すべての ClickHouse インスタンス（セルフホストまたは Cloud）               | ClickHouse Cloud サービスのみ                                                              |
| **認証**           | 環境変数（データベース ユーザー）                                          | Cloud 認証情報による OAuth 2.0                                                             |
| **ツール**         | 3 ツール: クエリおよびスキーマ探索                                         | クエリ、スキーマ探索、サービス管理、バックアップ、ClickPipes、請求関連ツール               |

## その他のリソース

- [GitHub の mcp-clickhouse](https://github.com/ClickHouse/mcp-clickhouse)
- [ClickHouse Cloud リモート MCP ドキュメント](https://clickhouse.com/docs/cloud/features/ai-ml/remote-mcp)
- [リモート MCP セットアップ ガイド](https://clickhouse.com/docs/products/cloud/features/ai-ml/mcp/remote-mcp)
- [ClickHouse Cloud](https://clickhouse.com/cloud)
