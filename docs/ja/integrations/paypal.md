---
catalog_title: Paypal
catalog_description: 決済管理、請求書送信、サブスクリプション管理を行います
catalog_icon: /adk-docs/integrations/assets/paypal.png
catalog_tags: ["mcp"]
---

# ADK 向け PayPal MCP ツール

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[PayPal MCP Server](https://github.com/paypal/paypal-mcp-server) は
ADK エージェントを [PayPal](https://www.paypal.com/) エコシステムへ接続します。
この連携により、エージェントは自然言語で決済、請求書、
サブスクリプション、紛争 (dispute) を管理でき、
自動化されたコマースワークフローとビジネス洞察を実現できます。

## ユースケース

- **財務オペレーションの効率化**: コンテキストを切り替えずにチャットから
  注文作成、請求書送信、返金処理を直接実行できます。
  例: "クライアント X に請求"、"注文 Y を返金"。

- **サブスクリプションと商品管理**: 商品作成、プラン設定、
  購読者管理まで、継続課金ライフサイクル全体を自然言語で処理します。

- **課題解決とパフォーマンス追跡**: 紛争請求の要約/承認、
  配送状況追跡、マーチャントインサイト取得により、その場でデータ駆動の意思決定を行えます。

## 前提条件

- [PayPal Developer account](https://developer.paypal.com/) を作成
- [PayPal Developer Dashboard](https://developer.paypal.com/) でアプリを作成し資格情報を取得
- 資格情報から [access token を生成](https://developer.paypal.com/reference/get-an-access-token/)

## エージェントで使う

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        PAYPAL_ENVIRONMENT = "SANDBOX"  # Options: "SANDBOX" or "PRODUCTION"
        PAYPAL_ACCESS_TOKEN = "YOUR_PAYPAL_ACCESS_TOKEN"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="paypal_agent",
            instruction="Help users manage their PayPal account",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "@paypal/mcp",
                                "--tools=all",
                                # (Optional) Specify which tools to enable
                                # "--tools=subscriptionPlans.list,subscriptionPlans.show",
                            ],
                            env={
                                "PAYPAL_ACCESS_TOKEN": PAYPAL_ACCESS_TOKEN,
                                "PAYPAL_ENVIRONMENT": PAYPAL_ENVIRONMENT,
                            }
                        ),
                        timeout=300,
                    ),
                )
            ],
        )
        ```

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams

        PAYPAL_MCP_ENDPOINT = "https://mcp.sandbox.paypal.com/sse"  # Production: https://mcp.paypal.com/sse
        PAYPAL_ACCESS_TOKEN = "YOUR_PAYPAL_ACCESS_TOKEN"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="paypal_agent",
            instruction="Help users manage their PayPal account",
            tools=[
                McpToolset(
                    connection_params=SseConnectionParams(
                        url=PAYPAL_MCP_ENDPOINT,
                        headers={
                            "Authorization": f"Bearer {PAYPAL_ACCESS_TOKEN}",
                        },
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "Local MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const PAYPAL_ENVIRONMENT = "SANDBOX"; // Options: "SANDBOX" or "PRODUCTION"
        const PAYPAL_ACCESS_TOKEN = "YOUR_PAYPAL_ACCESS_TOKEN";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "paypal_agent",
            instruction: "Help users manage their PayPal account",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: [
                            "-y",
                            "@paypal/mcp",
                            "--tools=all",
                            // (Optional) Specify which tools to enable
                            // "--tools=subscriptionPlans.list,subscriptionPlans.show",
                        ],
                        env: {
                            PAYPAL_ACCESS_TOKEN: PAYPAL_ACCESS_TOKEN,
                            PAYPAL_ENVIRONMENT: PAYPAL_ENVIRONMENT,
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

!!! note

    **トークン有効期限**: PayPal Access Token の有効時間は 3〜8 時間です。
    エージェントが動作しない場合はトークン失効を確認し、必要に応じて再発行してください。
    有効期限に対応するトークン更新ロジックの実装を推奨します。

## 利用可能なツール

### カタログ管理

Tool | Description
---- | -----------
`create_product` | PayPal カタログに新規商品を作成
`list_products` | PayPal カタログ商品一覧
`show_product_details` | 特定商品の詳細表示
`update_product` | 既存商品を更新

### 紛争管理

Tool | Description
---- | -----------
`list_disputes` | フィルタ付きで全紛争の要約を取得
`get_dispute` | 特定紛争の詳細取得
`accept_dispute_claim` | 紛争請求を承認し購入者有利で解決

### 請求書

Tool | Description
---- | -----------
`create_invoice` | PayPal システムで新規請求書作成
`list_invoices` | 請求書一覧
`get_invoice` | 特定請求書の詳細取得
`send_invoice` | 指定受信者に既存請求書を送信
`send_invoice_reminder` | 既存請求書のリマインダー送信
`cancel_sent_invoice` | 送信済み請求書をキャンセル
`generate_invoice_qr_code` | 請求書 QR コードを生成

### 支払い

Tool | Description
---- | -----------
`create_order` | 指定詳細に基づく注文を作成
`create_refund` | 取得済み支払いの返金処理
`get_order` | 特定支払いの詳細取得
`get_refund` | 特定返金の詳細取得
`pay_order` | 承認済み注文の支払いをキャプチャ

### レポートとインサイト

Tool | Description
---- | -----------
`get_merchant_insights` | マーチャント向け BI 指標と分析を取得
`list_transactions` | 全取引一覧を取得

### 配送追跡

Tool | Description
---- | -----------
`create_shipment_tracking` | PayPal 取引の配送追跡情報を作成
`get_shipment_tracking` | 特定配送の追跡情報を取得
`update_shipment_tracking` | 特定配送の追跡情報を更新

### サブスクリプション管理

Tool | Description
---- | -----------
`cancel_subscription` | 有効サブスクリプションを解約
`create_subscription` | 新規サブスクリプション作成
`create_subscription_plan` | 新規サブスクリプションプラン作成
`update_subscription` | 既存サブスクリプション更新
`list_subscription_plans` | サブスクリプションプラン一覧
`show_subscription_details` | 特定サブスクリプション詳細表示
`show_subscription_plan_details` | 特定サブスクリプションプラン詳細表示

## 設定

`--tools` コマンドライン引数で有効化ツールを制御できます。
これはエージェント権限範囲を制限する際に有用です。

`--tools=all` で全ツール有効化、または
特定ツール識別子をカンマ区切りで指定できます。

**注意**: 以下の設定識別子はドット記法 (例: `invoices.create`) を使用し、
エージェントに公開されるツール名 (例: `create_invoice`) とは異なります。

**Products**: `products.create`, `products.list`, `products.update`,
`products.show`

**Disputes**:
`disputes.list`, `disputes.get`, `disputes.create`

**Invoices**: `invoices.create`, `invoices.list`, `invoices.get`,
`invoices.send`, `invoices.sendReminder`, `invoices.cancel`,
`invoices.generateQRC`

**Orders & Payments**: `orders.create`, `orders.get`, `orders.capture`,
`payments.createRefund`, `payments.getRefunds`

**Transactions**:
`transactions.list`

**Shipment**:
`shipment.create`, `shipment.get`

**Subscriptions**: `subscriptionPlans.create`, `subscriptionPlans.list`,
`subscriptionPlans.show`, `subscriptions.create`, `subscriptions.show`,
`subscriptions.cancel`

## 追加リソース

- [PayPal MCP Server Documentation](https://docs.paypal.ai/developer/tools/ai/mcp-quickstart)
- [PayPal MCP Server Repository](https://github.com/paypal/paypal-mcp-server)
- [PayPal Agent Tools Reference](https://docs.paypal.ai/developer/tools/ai/agent-tools-ref)
