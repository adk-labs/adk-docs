---
catalog_title: e2a
catalog_description: 人間によるレビュー承認機能を備えた AI エージェント向け認証メール ゲートウェイ
catalog_icon: /integrations/assets/e2a.png
catalog_tags: ["mcp"]
---

# ADK 向け e2a MCP ツール

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[e2a MCP Server](https://github.com/tokencanopy/e2a/tree/main/mcp) は、ADK エージェントを AI エージェント専用に構築された認証メール ゲートウェイである [e2a](https://e2a.dev) に接続します。この統合により、エージェントは同僚のように自然言語を使用してメッセージを送信、受信、返信できる専用のメール受信トレイを持つことができ、受信メールの SPF/DKIM/DMARC 検証および送信メッセージに対するオプションの人間によるレビュー保留機能を提供します。

サーバーは `https://api.e2a.dev/mcp` でホストされており、Streamable HTTP で通信するため、ローカルにインストールしたり実行したりする必要はありません。

## ユースケース

- **エージェントに専用の受信トレイを付与**: 専用のメール アドレス（例: `support-bot@your-domain.com`）をプロビジョニングし、エージェントがチームメンバーのようにメールを送受信できるようにします。

- **認証された受信メール**: すべての受信メッセージには SPF、DKIM、DMARC の証拠が付与されているため、エージェントはコンテンツに基づいてアクションを実行する前に、送信者が主張する人物であるかどうかを確認できます。

- **人間によるレビュー (Human-in-the-loop)**: レビュー保留機能を有効にすると、人間が承認するまで送信メッセージが `pending_review` として保留されます。必要に応じて、送信前に件名、本文、宛先を編集できます。

- **スレッド会話の自動化**: `In-Reply-To` および `References` ヘッダーを保持して返信するため、受信者のメール クライアントで複数のターンにわたってスレッドが維持されます。

## 前提条件

- 無料の [e2a アカウント](https://e2a.dev) およびダッシュボードからの API キー

## エージェントでの使用

=== "Python"

    === "リモート MCP サーバー"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import (
            StreamableHTTPConnectionParams,
        )

        E2A_API_KEY = "YOUR_E2A_API_KEY"

        root_agent = Agent(
            model="gemini-flash-latest",
            name="e2a_agent",
            instruction=(
                "You manage email through the e2a tools. Call whoami once to "
                "learn your identity and inbox address. Use list_messages and "
                "get_message to read; use reply_to_message when replying to an "
                "existing thread (it preserves In-Reply-To and References), and "
                "send_message only to start a new thread. Both 'accepted' and "
                "'pending_review' are successful outcomes — never re-send after "
                "either one."
            ),
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://api.e2a.dev/mcp",
                        headers={"Authorization": f"Bearer {E2A_API_KEY}"},
                        timeout=30,
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "リモート MCP サーバー"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const E2A_API_KEY = "YOUR_E2A_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "e2a_agent",
            instruction:
                "You manage email through the e2a tools. Call whoami once to " +
                "learn your identity and inbox address. Use list_messages and " +
                "get_message to read; use reply_to_message when replying to an " +
                "existing thread (it preserves In-Reply-To and References), and " +
                "send_message only to start a new thread. Both 'accepted' and " +
                "'pending_review' are successful outcomes — never re-send after " +
                "either one.",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://api.e2a.dev/mcp",
                    transportOptions: {
                        requestInit: {
                            headers: {
                                Authorization: `Bearer ${E2A_API_KEY}`,
                            },
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

!!! tip "本番環境ではツールセットを e2a SDK と組み合わせて使用"

    MCP ツールセットは受信トレイをモデルに渡します。ウェブフック署名の検証、少なくとも 1 回の配信 (at-least-once delivery) の処理、べき等な送信などの決定論的な部分は、[Python](https://pypi.org/project/e2a/) または [TypeScript](https://www.npmjs.com/package/@e2a/sdk) SDK を使用してアプリケーション コード内に保持します。以下の ADK Webhook の例は、その形式の完全な動作例です。

## 利用可能なツール

ホスト型サーバーは 60 以上のツールを露出します。決定的なセットについては、エンドポイントに対して `tools/list` を呼び出してください。表示されるツールはキーによって異なります。デプロイされたエージェントに推奨される **エージェント スコープ** キー（`e2a_agt_…`）はランタイム ツールのみを表示し、**アカウント スコープ** キー（`e2a_acct_…`）は以下の管理ツールも表示します。

### ランタイム — 受信トレイ ツール

ツール | 説明
---- | -----------
`whoami` | 認証された ID（ユーザー、資格情報スコープ、プランと使用制限、エージェント スコープの資格情報の場合は `agent_email`）を返します。
`get_agent` | 1 つのエージェントの完全なレコードを取得します。
`list_messages` | `direction`、`read_status`、検索フィルター、カーソル ページネーションを使用して受信または送信メールを一覧表示します。
`get_message` | 1 つのメッセージの完全な本文、ヘッダー、添付ファイル メタデータ、SPF/DKIM/DMARC 検証結果を取得します。
`get_message_lifecycle` | 1 つのメッセージの再構築された配信履歴を取得します。
`get_attachment` | 添付ファイルのメタデータ、または `inline: true` のバイトデータを取得します。
`send_message` | 新しいメールを送信します。レビュー保留にヒットした場合は `accepted` または `pending_review` を返します。どちらも成功であり、再送信しないでください。
`reply_to_message` | スレッド内で返信します。`In-Reply-To` および `References` を保持します。
`forward_message` | メッセージを新しい受信者に転送します。
`list_conversations` / `get_conversation` | 個々のメッセージではなくスレッドを参照します。
`update_message_labels` | メッセージのラベルを追加または削除します。
`delete_message` / `restore_message` | ゴミ箱へのソフト削除および復元を行います。

### 管理 — プロビジョニングとセットアップ

ツール | 説明
---- | -----------
`list_agents`, `create_agent`, `update_agent`, `delete_agent`, `restore_agent` | エージェントの受信トレイを管理します。
`get_protection`, `update_protection` | エージェントごとのスクリーニングおよびレビュー保留構成を管理します。
`list_domains`, `register_domain`, `get_domain`, `verify_domain`, `delete_domain` | カスタム ドメインの登録および DNS 検証を管理します。
`list_reviews`, `get_review`, `approve_review`, `reject_review` | 人間によるレビュー キューを処理します。
`list_webhooks`, `create_webhook`, `update_webhook`, `delete_webhook`, `rotate_webhook_secret`, `test_webhook`, `list_webhook_deliveries` | Webhook サブスクリプションおよび配信履歴を管理します。
`list_events`, `get_event`, `redeliver_event` | イベント ログおよび再配信を管理します。
`list_templates`, `create_template`, `update_template`, `delete_template`, `validate_template` | サーバーサイドのメール テンプレートを管理します（ベータ）。
`list_api_keys`, `create_api_key`, `delete_api_key` | API キー管理を行います。

## 構成

ホスト型エンドポイントは、上記の `Authorization` ヘッダーに渡す API キー以外の環境変数は必要ありません。セルフホストの e2a デプロイメントを使用するには、`url` をそのデプロイメントの `/mcp` エンドポイントに変更します。

インタラクティブな MCP クライアントは、キーを貼り付ける代わりに `https://api.e2a.dev/mcp` を OAuth 2.1 コネクタとして追加できます。メールを受信するには、`list_messages` をポーリングするか、SDK の `listen()` で WebSocket を開くか（公開 URL 不要）、`create_webhook` で HTTPS エンドポイントをサブスクライブします。

## 追加リソース

- [e2a MCP Server ソース コード](https://github.com/tokencanopy/e2a/tree/main/mcp)
- [実行可能な ADK サンプル](https://github.com/tokencanopy/e2a/tree/main/mcp/examples/adk)
- [ADK Webhook サンプル](https://github.com/tokencanopy/e2a/tree/main/examples/adk-cloud-webhook)
- [e2a ドキュメント](https://e2a.dev)
