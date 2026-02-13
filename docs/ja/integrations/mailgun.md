---
catalog_title: Mailgun
catalog_description: メール送信、配信指標追跡、メーリングリスト管理を行います
catalog_icon: /adk-docs/integrations/assets/mailgun.png
catalog_tags: ["mcp"]
---

# ADK 向け Mailgun MCP ツール

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Mailgun MCP Server](https://github.com/mailgun/mailgun-mcp-server) は
ADK エージェントをトランザクションメールサービス [Mailgun](https://www.mailgun.com/) へ接続します。
この連携により、エージェントは自然言語でメール送信、
配信メトリクス追跡、ドメイン/テンプレート管理、メーリングリスト処理を行えます。

## ユースケース

- **メール送信と管理**: トランザクション/マーケティングメールを作成・送信し、
  保存メッセージを取得し、送信済みメッセージを再送できます。

- **配信パフォーマンス監視**: 配信統計の取得、
  バウンス分類の分析、送信者評価維持のための suppression リスト確認を行います。

- **メール基盤管理**: ドメイン DNS 設定検証、追跡設定構成、
  メールテンプレート作成、受信ルーティングルール設定を行います。

## 前提条件

- [Mailgun アカウント](https://www.mailgun.com/) 作成
- [Mailgun Dashboard](https://app.mailgun.com/settings/api_security) で API キーを生成

## エージェントで使う

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        MAILGUN_API_KEY = "YOUR_MAILGUN_API_KEY"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="mailgun_agent",
            instruction="Help users send emails and manage their Mailgun account",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "@mailgun/mcp-server",
                            ],
                            env={
                                "MAILGUN_API_KEY": MAILGUN_API_KEY,
                                # "MAILGUN_API_REGION": "eu",  # Optional: defaults to "us"
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

        const MAILGUN_API_KEY = "YOUR_MAILGUN_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "mailgun_agent",
            instruction: "Help users send emails and manage their Mailgun account",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: ["-y", "@mailgun/mcp-server"],
                        env: {
                            MAILGUN_API_KEY: MAILGUN_API_KEY,
                            // MAILGUN_API_REGION: "eu",  // Optional: defaults to "us"
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## 利用可能なツール

### メッセージング

Tool | Description
---- | -----------
`send_email` | HTML コンテンツと添付に対応したメール送信
`get_stored_message` | 保存済みメールメッセージ取得
`resend_message` | 送信済みメッセージ再送

### ドメイン

Tool | Description
---- | -----------
`get_domain` | 特定ドメイン詳細を表示
`verify_domain` | ドメイン DNS 設定を検証
`get_tracking_settings` | トラッキング設定 (クリック、開封、解除) を表示
`update_tracking_settings` | ドメイントラッキング設定を更新

### Webhooks

Tool | Description
---- | -----------
`list_webhooks` | ドメインのイベント Webhook 一覧
`create_webhook` | 新規イベント Webhook 作成
`update_webhook` | 既存 Webhook 更新
`delete_webhook` | Webhook 削除

### Routes

Tool | Description
---- | -----------
`list_routes` | 受信メールルーティングルール表示
`update_route` | 受信ルーティングルール更新

### メーリングリスト

Tool | Description
---- | -----------
`create_mailing_list` | 新規メーリングリスト作成
`manage_list_members` | メーリングリストメンバー追加/削除/更新

### テンプレート

Tool | Description
---- | -----------
`create_template` | 新規メールテンプレート作成
`manage_template_versions` | テンプレートバージョン作成/管理

### 分析と統計

Tool | Description
---- | -----------
`query_metrics` | 期間指定で送信/利用メトリクス照会
`get_logs` | メールイベントログ取得
`get_stats` | ドメイン、タグ、プロバイダ、デバイス、国別の集計統計表示

### Suppressions

Tool | Description
---- | -----------
`get_bounces` | バウンスメールアドレス表示
`get_unsubscribes` | 配信停止メールアドレス表示
`get_complaints` | 苦情レコード表示
`get_allowlist` | allowlist エントリ表示

### IPs

Tool | Description
---- | -----------
`list_ips` | IP 割り当て表示
`get_ip_pools` | 専用 IP プール設定表示

### バウンス分類

Tool | Description
---- | -----------
`get_bounce_classification` | バウンスタイプと配信問題を分析

## 設定

Variable | Required | Default | Description
-------- | -------- | ------- | -----------
`MAILGUN_API_KEY` | Yes | — | Mailgun API キー
`MAILGUN_API_REGION` | No | `us` | API リージョン: `us` または `eu`

## 追加リソース

- [Mailgun MCP Server Repository](https://github.com/mailgun/mailgun-mcp-server)
- [Mailgun MCP Integration Guide](https://www.mailgun.com/resources/integrations/mcp-server/)
- [Mailgun Documentation](https://documentation.mailgun.com/)
