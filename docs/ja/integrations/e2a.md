---
catalog_title: e2a
catalog_description: AI エージェント向けの認証済みメールゲートウェイと human-in-the-loop 承認
catalog_icon: /integrations/assets/e2a.png
catalog_tags: ["mcp"]
---

# ADK 向け e2a MCP ツール

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[e2a MCP Server](https://github.com/Mnexa-AI/e2a/tree/main/mcp) は、ADK
エージェントを AI エージェント向けに構築された認証済みメール
ゲートウェイ [e2a](https://e2a.dev) に接続します。この統合により、
エージェントは専用のメール受信箱を持ち、自然言語でメッセージの送信、
受信、返信を行えます。また、SPF/DKIM で検証された受信メールと、
送信メッセージに対する任意の human-in-the-loop 承認を利用できます。

## ユースケース

- **エージェントに専用の受信箱を持たせる**: `support-bot@your-domain.com`
  のような専用メールアドレスをプロビジョニングし、チームメイトのように
  メールを送受信させます。
- **認証済みの受信メール**: すべての受信メッセージには SPF と DKIM の
  検証結果が含まれるため、エージェントは送信者が本人であるかを判断
  できます。
- **Human-in-the-loop 承認**: 任意のエージェントで HITL を設定すると、
  送信メッセージはレビュー担当者が承認するまで保留キューに保持されます。
  承認前に件名、本文、宛先を編集することもできます。
- **スレッド会話の自動化**: 受信メールへ返信するときに In-Reply-To と
  References ヘッダーを保持するため、複数ターンにわたってスレッドが
  維持されます。

## 前提条件

- 無料の [e2a アカウント](https://e2a.dev) とダッシュボードの API キー
- Node.js 18 以降（ローカル MCP サーバーを使う場合のみ必要）

## エージェントで使用する

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        E2A_API_KEY = "YOUR_E2A_API_KEY"
        E2A_AGENT_EMAIL = "your-bot@your-domain.com"  # optional default inbox

        root_agent = Agent(
            model="gemini-flash-latest",
            name="e2a_agent",
            instruction=(
                "You manage email through the e2a tools. Call whoami once "
                "to find your inbox address. Use list_messages and "
                "get_message to read; use reply_to_message (not "
                "send_email) when replying to an existing thread so "
                "threading headers are preserved."
            ),
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=["-y", "@e2a/mcp-server"],
                            env={
                                "E2A_API_KEY": E2A_API_KEY,
                                "E2A_AGENT_EMAIL": E2A_AGENT_EMAIL,
                            },
                        ),
                        timeout=30,
                    ),
                )
            ],
        )
        ```

    === "Remote MCP Server"

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
                "You manage email through the e2a tools. Call whoami once "
                "to find your inbox address. Use list_messages and "
                "get_message to read; use reply_to_message (not "
                "send_email) when replying to an existing thread so "
                "threading headers are preserved."
            ),
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://mcp.e2a.dev/mcp",
                        headers={"Authorization": f"Bearer {E2A_API_KEY}"},
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

        const E2A_API_KEY = "YOUR_E2A_API_KEY";
        const E2A_AGENT_EMAIL = "your-bot@your-domain.com"; // optional default inbox

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "e2a_agent",
            instruction:
                "You manage email through the e2a tools. Call whoami once " +
                "to find your inbox address. Use list_messages and " +
                "get_message to read; use reply_to_message (not " +
                "send_email) when replying to an existing thread so " +
                "threading headers are preserved.",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: ["-y", "@e2a/mcp-server"],
                        env: {
                            E2A_API_KEY: E2A_API_KEY,
                            E2A_AGENT_EMAIL: E2A_AGENT_EMAIL,
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

    === "Remote MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const E2A_API_KEY = "YOUR_E2A_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "e2a_agent",
            instruction:
                "You manage email through the e2a tools. Call whoami once " +
                "to find your inbox address. Use list_messages and " +
                "get_message to read; use reply_to_message (not " +
                "send_email) when replying to an existing thread so " +
                "threading headers are preserved.",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://mcp.e2a.dev/mcp",
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

## 利用可能なツール

### ID

ツール | 説明
---- | -----------
`whoami` | デフォルトエージェントの完全なレコードを返します。アカウントに複数のエージェントがある場合は `E2A_AGENT_EMAIL` が必要です。
`list_agents` | 認証済みユーザーが所有するすべてのエージェント受信箱を一覧表示します。
`create_agent` | 共有ドメイン上の slug を使って新しい受信箱を登録します。デフォルトは `local` モードで、エージェントはポーリングでメールを受信し、webhook は不要です。
`update_agent` | 既存エージェントの webhook URL、モード、HITL 設定を更新します。
`delete_agent` | エージェントを完全に削除し、そのアドレスでのメール受信を停止します。`confirm: true` が必要です。

!!! warning "Cloud モードのエージェントは webhook 署名を検証する必要があります"

    `agent_mode: "cloud"` で作成されたエージェントは、ポーリングではなく
    webhook でメールを受信します。webhook ハンドラーは、すべての配信で
    HMAC 署名を検証する必要があります。署名検証を含む完全な設定は
    [cloud-mode webhook の例](https://github.com/Mnexa-AI/e2a/tree/main/examples/adk-cloud-webhook)
    を参照してください。

### メッセージ

ツール | 説明
---- | -----------
`send_email` | 新しいメールを送信します。HITL が有効な場合は `sent` ではなく `status: pending_approval` を返します。
`reply_to_message` | 受信メッセージに返信し、In-Reply-To と References ヘッダーを保持します。
`list_messages` | `status` フィルター（unread / read / all）とページネーションで受信メールを一覧表示します。
`get_message` | 1 件のメッセージの本文、ヘッダー、添付ファイルメタデータを取得します。
`get_attachment_data` | メッセージ ID と 0 始まりの添付ファイルインデックスで添付ファイルのバイト列をダウンロードします（base64 で返されます）。

### Human-in-the-loop 承認

ツール | 説明
---- | -----------
`list_pending_messages` | human 承認待ちの送信メールを、有効期限が近い順に一覧表示します。
`get_pending_message` | 保留中メッセージの完全な下書き（件名、宛先、本文）を取得します。
`approve_pending_message` | レビュー担当者が任意で件名、本文、宛先を編集したうえで保留メッセージを送信します。
`reject_pending_message` | 保留メッセージを破棄します。任意の `reason` は監査用に保存されます。

### ドメイン

ツール | 説明
---- | -----------
`list_domains` | 認証済みユーザーに登録されたすべてのカスタムドメインと検証状態を一覧表示します。
`register_domain` | カスタムドメインを追加し、所有権を証明するために必要な DNS レコードを返します。
`verify_domain` | DNS レコードを設定した後、登録済みドメインの DNS 検証を再実行します。
`delete_domain` | カスタムドメインを削除します。`confirm: true` が必要で、共有ドメイン上のエージェントには影響しません。

## 設定

変数 | 必須 | デフォルト | 説明
---- | ---- | ------ | -----------
`E2A_API_KEY` | はい | — | e2a API キーです。
`E2A_AGENT_EMAIL` | いいえ | — | デフォルトのエージェント受信箱です。ツールのスコープを制限するため、LLM が毎回指定する必要がありません。
`E2A_BASE_URL` | いいえ | `https://e2a.dev` | セルフホストデプロイ URL です（ローカル MCP サーバーのみ）。

## 追加リソース

- [e2a MCP Server ソース](https://github.com/Mnexa-AI/e2a/tree/main/mcp)
- [実行可能な ADK サンプル](https://github.com/Mnexa-AI/e2a/tree/main/mcp/examples/adk)
- [Cloud-mode webhook の例](https://github.com/Mnexa-AI/e2a/tree/main/examples/adk-cloud-webhook)
- [e2a ドキュメント](https://e2a.dev)
- [npm パッケージ](https://www.npmjs.com/package/@e2a/mcp-server)
