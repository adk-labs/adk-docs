---
catalog_title: AgentPhone
catalog_description: 電話発信、SMS 送信、番号管理、AI 音声エージェントの構築
catalog_icon: /integrations/assets/agentphone.png
catalog_tags: ["mcp"]
---

# ADK 向け AgentPhone MCP ツール

<div class="language-support-tag">
  <span class="lst-supported">ADK でサポート</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[AgentPhone MCP Server](https://github.com/AgentPhone-AI/agentphone-mcp) は、
ADK エージェントを [AgentPhone](https://agentphone.to/) に接続します。
AgentPhone は AI エージェント向けの通信プラットフォームで、電話の発信と着信、
SMS の送受信、電話番号の管理、自然言語で動作する自律型 AI 音声エージェントの
作成を支援します。

## ユースケース

- **自律的な電話発信**: エージェントが電話番号に発信し、指定したトピックについて
  AI を使った会話を最後まで進め、完了時に完全な書き起こしを返します。

- **SMS メッセージング**: テキストメッセージの送受信、複数の電話番号にまたがる
  会話スレッドの管理、メッセージ履歴の取得を行います。

- **電話番号管理**: 特定の市外局番付き番号をプロビジョニングし、エージェントに
  割り当てたり、不要になったら解放したりします。

- **AI 音声エージェント**: Webhook を使わずに、受信・発信の通話を自律的に処理する、
  音声とシステムプロンプトを柔軟に設定できるエージェントを作成します。

- **Webhook 連携**: プロジェクト単位またはエージェント単位の Webhook を設定して、
  受信メッセージや通話イベントのリアルタイム通知を受け取ります。

## 前提条件

- [AgentPhone アカウント](https://agentphone.to/) を作成します。
- [AgentPhone 設定](https://agentphone.to/) から API キーを生成します。

## エージェントと一緒に使う

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        AGENTPHONE_API_KEY = "YOUR_AGENTPHONE_API_KEY"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="agentphone_agent",
            instruction="Help users make phone calls, send SMS, and manage phone numbers",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "agentphone-mcp",
                            ],
                            env={
                                "AGENTPHONE_API_KEY": AGENTPHONE_API_KEY,
                            }
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
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

        AGENTPHONE_API_KEY = "YOUR_AGENTPHONE_API_KEY"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="agentphone_agent",
            instruction="Help users make phone calls, send SMS, and manage phone numbers",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://mcp.agentphone.to/mcp",
                        headers={
                            "Authorization": f"Bearer {AGENTPHONE_API_KEY}",
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

        const AGENTPHONE_API_KEY = "YOUR_AGENTPHONE_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "agentphone_agent",
            instruction: "Help users make phone calls, send SMS, and manage phone numbers",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: ["-y", "agentphone-mcp"],
                        env: {
                            AGENTPHONE_API_KEY: AGENTPHONE_API_KEY,
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

        const AGENTPHONE_API_KEY = "YOUR_AGENTPHONE_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "agentphone_agent",
            instruction: "Help users make phone calls, send SMS, and manage phone numbers",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://mcp.agentphone.to/mcp",
                    transportOptions: {
                        requestInit: {
                            headers: {
                                Authorization: `Bearer ${AGENTPHONE_API_KEY}`,
                            },
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## 利用可能なツール

### アカウント

Tool | Description
---- | -----------
`account_overview` | アカウント全体のスナップショット: エージェント、番号、Webhook 状態、利用上限
`get_usage` | 詳細な利用状況: プラン上限、番号クォータ、メッセージ/通話量

### 電話番号

Tool | Description
---- | -----------
`list_numbers` | アカウント内の全電話番号を一覧表示
`buy_number` | 国や市外局番を指定して新しい電話番号を購入
`release_number` | 電話番号をキャリアプールへ恒久的に返却

### SMS / メッセージ

Tool | Description
---- | -----------
`get_messages` | 特定の電話番号の SMS メッセージを取得
`list_conversations` | すべての番号にまたがる SMS 会話スレッドを一覧表示
`get_conversation` | 完全なメッセージ履歴を含む会話を取得

### 音声通話

Tool | Description
---- | -----------
`list_calls` | すべての番号に対する最近の通話を一覧表示
`list_calls_for_number` | 特定の電話番号の通話を一覧表示
`get_call` | オプションの長時間ポーリング付きで通話詳細と書き起こしを取得
`make_call` | Webhook を使って会話処理のための発信通話を開始
`make_conversation_call` | 完全な書き起こしを返す自律型 AI 通話を開始

### エージェント

Tool | Description
---- | -----------
`list_agents` | 電話番号と音声設定を含む全エージェントを一覧表示
`create_agent` | 設定可能な音声とシステムプロンプトで新しいエージェントを作成
`update_agent` | エージェント設定を更新
`delete_agent` | エージェントを削除
`get_agent` | 番号と音声設定を含むエージェント詳細を取得
`attach_number` | 電話番号をエージェントに割り当て
`list_voices` | 利用可能な音声オプションを一覧表示

### Webhook

Tool | Description
---- | -----------
`get_webhook` | プロジェクトレベルの Webhook 設定を取得
`set_webhook` | 受信メッセージと通話イベント用のプロジェクトレベル Webhook を設定
`delete_webhook` | プロジェクトレベルの Webhook を削除
`get_agent_webhook` | 特定エージェントの Webhook を取得
`set_agent_webhook` | エージェント固有の Webhook を設定（プロジェクトレベル設定を上書き）
`delete_agent_webhook` | エージェント固有の Webhook を削除

## 構成

AgentPhone MCP Server は環境変数で構成できます。

Variable | Description | Default
-------- | ----------- | -------
`AGENTPHONE_API_KEY` | AgentPhone API キー | Required (stdio mode)
`AGENTPHONE_BASE_URL` | API ベース URL を上書き | `https://api.agentphone.to`

リモート HTTP モードでは、環境変数ではなく `Authorization: Bearer` ヘッダーで API キーを渡します。

## 追加リソース

- [GitHub の AgentPhone MCP Server](https://github.com/AgentPhone-AI/agentphone-mcp)
- [npm の agentphone-mcp](https://www.npmjs.com/package/agentphone-mcp)
- [AgentPhone Web サイト](https://agentphone.to/)
