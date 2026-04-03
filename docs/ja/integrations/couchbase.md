---
catalog_title: Couchbase
catalog_description: コレクションを検索し、スキーマを調べ、SQL++ クエリを実行します
catalog_icon: /integrations/assets/couchbase.png
catalog_tags: ["data", "mcp"]
---

# ADK 向け Couchbase MCP ツール

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Couchbase MCP Server](https://github.com/Couchbase-Ecosystem/mcp-server-couchbase) は、
ADK エージェントを [Couchbase](https://www.couchbase.com/) クラスターに接続します。
この統合により、エージェントは自然言語で Couchbase データを探索し、
クエリを実行し、パフォーマンスの問題を分析できるようになります。

## ユースケース

- **データ探索**: バケット、スコープ、コレクション、ドキュメントスキーマを見つけ、自然言語のクエリでデータを検索します。

- **データベース管理**: 対話形式のコマンドを通じて、クラスターの状態を監視し、実行中のサービスを確認し、バケット、スコープ、コレクションの構造を管理します。

- **クエリ性能分析**: インデックスの推奨を取得し、クエリプランを分析し、遅いクエリや選択性の低いクエリを調べて性能を最適化します。

## 前提条件

- 稼働中の Couchbase クラスター。次のいずれかを使用できます。
    - [Couchbase Capella](https://cloud.couchbase.com/) を利用する(マネージドクラウドサービス)
    - Couchbase Server 7.x 以降をローカルまたはセルフホストで実行する
- クラスター用の接続文字列と認証情報(ユーザー名/パスワード、または mTLS 用のクライアント証明書)
- [`uv`](https://docs.astral.sh/uv/) パッケージマネージャーのインストール(`uvx` コマンド用)

## エージェントで使う

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        CB_CONNECTION_STRING = "couchbase://localhost"
        CB_USERNAME = "Administrator"
        CB_PASSWORD = "password"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="couchbase_agent",
            instruction="Help users explore and query Couchbase databases",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="uvx",
                            args=["couchbase-mcp-server"],
                            env={
                                "CB_CONNECTION_STRING": CB_CONNECTION_STRING,
                                "CB_USERNAME": CB_USERNAME,
                                "CB_PASSWORD": CB_PASSWORD,
                                "CB_MCP_READ_ONLY_MODE": "true",  # 書き込み操作を防ぎます
                            },
                        ),
                        timeout=60,
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "Local MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const CB_CONNECTION_STRING = "couchbase://localhost";
        const CB_USERNAME = "Administrator";
        const CB_PASSWORD = "password";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "couchbase_agent",
            instruction: "Help users explore and query Couchbase databases",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "uvx",
                        args: ["couchbase-mcp-server"],
                        env: {
                            CB_CONNECTION_STRING: CB_CONNECTION_STRING,
                            CB_USERNAME: CB_USERNAME,
                            CB_PASSWORD: CB_PASSWORD,
                            CB_MCP_READ_ONLY_MODE: "true", // 書き込み操作を防ぎます
                        },
                    },
                })
            ],
        });

        export { rootAgent };
        ```

## 利用可能なツール

### クラスター設定とヘルスツール

ツール | 説明
---- | -----------
`get_server_configuration_status` | MCP サーバーの状態を取得します
`test_cluster_connection` | クラスターに接続して、クラスター認証情報を確認します
`get_cluster_health_and_services` | クラスターのヘルス状態と、稼働中のすべてのサービス一覧を取得します

### データモデルとスキーマ探索ツール

ツール | 説明
---- | -----------
`get_buckets_in_cluster` | クラスター内のすべてのバケット一覧を取得します
`get_scopes_in_bucket` | 指定したバケット内のすべてのスコープ一覧を取得します
`get_collections_in_scope` | 指定したバケットとスコープ内のすべてのコレクション一覧を取得します
`get_scopes_and_collections_in_bucket` | 指定したバケット内のすべてのスコープとコレクション一覧を取得します
`get_schema_for_collection` | コレクションの構造を取得します

### ドキュメント KV 操作ツール

ツール | 説明
---- | -----------
`get_document_by_id` | 指定したスコープとコレクションから ID でドキュメントを取得します
`upsert_document_by_id` | 指定したスコープとコレクションに ID でドキュメントを upsert します。**`CB_MCP_READ_ONLY_MODE=true` では無効です。**
`insert_document_by_id` | 新しいドキュメントを ID で挿入します(ドキュメントが存在する場合は失敗します)。**`CB_MCP_READ_ONLY_MODE=true` では無効です。**
`replace_document_by_id` | 既存のドキュメントを ID で置き換えます(ドキュメントが存在しない場合は失敗します)。**`CB_MCP_READ_ONLY_MODE=true` では無効です。**
`delete_document_by_id` | 指定したスコープとコレクションから ID でドキュメントを削除します。**`CB_MCP_READ_ONLY_MODE=true` では無効です。**

### クエリとインデックスツール

ツール | 説明
---- | -----------
`run_sql_plus_plus_query` | 指定したスコープで [SQL++ クエリ](https://www.couchbase.com/sqlplusplus/) を実行します
`list_indexes` | バケット、スコープ、コレクション、インデックス名で任意に絞り込みながら、クラスター内のすべてのインデックスとその定義を一覧表示します
`get_index_advisor_recommendations` | 与えられた SQL++ クエリに対して Couchbase Index Advisor からインデックス推奨を取得し、クエリ性能を最適化します

### クエリ性能分析ツール

ツール | 説明
---- | -----------
`get_longest_running_queries` | 平均サービス時間が最も長いクエリを取得します
`get_most_frequent_queries` | 最も頻繁に実行されるクエリを取得します
`get_queries_with_largest_response_sizes` | レスポンスサイズが最も大きいクエリを取得します
`get_queries_with_large_result_count` | 結果数が最も多いクエリを取得します
`get_queries_using_primary_index` | プライマリインデックスを使用しているクエリを取得します(性能上の懸念がある可能性があります)
`get_queries_not_using_covering_index` | カバリングインデックスを使用していないクエリを取得します
`get_queries_not_selective` | 選択性が低いクエリを取得します(インデックススキャンが最終結果よりはるかに多くのドキュメントを返します)

## 設定

### 環境変数

変数 | 説明 | デフォルト
-------- | ----------- | -------
`CB_CONNECTION_STRING` | Couchbase クラスターへの接続文字列 | 必須
`CB_USERNAME` | 基本認証用のユーザー名 | 必須(mTLS 用のクライアント証明書も可)
`CB_PASSWORD` | 基本認証用のパスワード | 必須(mTLS 用のクライアント証明書も可)
`CB_CLIENT_CERT_PATH` | mTLS 認証用のクライアント証明書ファイルのパス | なし
`CB_CLIENT_KEY_PATH` | mTLS 認証用のクライアントキー ファイルのパス | なし
`CB_CA_CERT_PATH` | TLS 用のサーバールート証明書のパス(Capella では不要) | なし
`CB_MCP_READ_ONLY_MODE` | すべてのデータ変更(KV とクエリ)を防止します | `true`
`CB_MCP_DISABLED_TOOLS` | 無効化するツールをカンマ区切りで指定します | なし

### 読み取り専用モード

`CB_MCP_READ_ONLY_MODE` 設定(既定では有効)は、サーバーを読み取り専用操作に制限します。
有効にすると、KV 書き込みツール(`upsert_document_by_id`、`insert_document_by_id`、
`replace_document_by_id`、`delete_document_by_id`)は読み込まれず、データを変更する SQL++ クエリはブロックされます。
これにより、誤って変更するリスクなく安全にデータ探索できます。

### ツールの無効化

`CB_MCP_DISABLED_TOOLS` を使って特定のツールを無効化できます:

```python
env={
    "CB_CONNECTION_STRING": "couchbase://localhost",
    "CB_USERNAME": "Administrator",
    "CB_PASSWORD": "password",
    "CB_MCP_DISABLED_TOOLS": "get_index_advisor_recommendations,get_queries_not_selective",
}
```

## 追加資料

- [Couchbase MCP Server リポジトリ](https://github.com/Couchbase-Ecosystem/mcp-server-couchbase)
- [Couchbase ドキュメント](https://docs.couchbase.com/)
- [Couchbase Capella](https://cloud.couchbase.com/)
