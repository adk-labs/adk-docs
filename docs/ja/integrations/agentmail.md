---
catalog_title: AgentMail
catalog_description: AIエージェントがメールを送受信し、管理するための受信トレイを作成
catalog_icon: /adk-docs/integrations/assets/agentmail.png
catalog_tags: ["mcp"]
---

# ADK 用 AgentMail MCP ツール

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[AgentMail MCP Server](https://github.com/agentmail-to/agentmail-mcp) は
AI エージェント用に構築されたメールインボックス API である
[AgentMail](https://agentmail.to/) を ADK エージェントに接続します。
この統合により、エージェントは自然言語で送受信、返信、転送を行える独自のメール
インボックスを持てます。

## 使用ケース

- **エージェント専用インボックスを提供**: エージェント向けに専用メールアドレスを作成し、
  人間のチームメンバーのようにメールの送受信を独自で行えるようにします。

- **メールワークフローの自動化**: 初期コンタクト送信、返信の読み取り、スレッド追跡を含め、
  メール会話をエンドツーエンドで処理させます。

- **インボックス横断で会話を管理**: スレッドとメッセージを検索・一覧表示し、メール転送や添付ファイル取得を行って
  エージェントが常時最新の状態を維持できるようにします。

## 前提条件

- [AgentMail アカウント](https://agentmail.to/)を作成
- [AgentMail ダッシュボード](https://agentmail.to/)から API キーを発行

## エージェントでの使用

=== "Python"

    === "ローカル MCP サーバー"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        AGENTMAIL_API_KEY = "YOUR_AGENTMAIL_API_KEY"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="agentmail_agent",
            instruction="Help users manage email inboxes and send messages",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "agentmail-mcp",
                            ],
                            env={
                                "AGENTMAIL_API_KEY": AGENTMAIL_API_KEY,
                            }
                        ),
                        timeout=30,
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "ローカル MCP サーバー"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const AGENTMAIL_API_KEY = "YOUR_AGENTMAIL_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "agentmail_agent",
            instruction: "Help users manage email inboxes and send messages",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: ["-y", "agentmail-mcp"],
                        env: {
                            AGENTMAIL_API_KEY: AGENTMAIL_API_KEY,
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## 利用可能なツール

### インボックス管理

ツール | 説明
---- | -----------
`list_inboxes` | すべてのインボックスを一覧表示します。
`get_inbox` | 特定のインボックスの詳細を取得します。
`create_inbox` | ユーザー名とドメインを指定して新しいインボックスを作成します。
`delete_inbox` | インボックスを削除します。

### スレッド管理

ツール | 説明
---- | -----------
`list_threads` | インボックス内のスレッドを一覧します。
`get_thread` | 特定のスレッドとメッセージを取得します。
`get_attachment` | メッセージから添付ファイルをダウンロードします。

### メッセージ操作

ツール | 説明
---- | -----------
`send_message` | 新しいメールをインボックスから送信します。
`reply_to_message` | 既存メッセージへ返信します。
`forward_message` | メッセージを別の受信者へ転送します。
`update_message` | 既読状態などのメッセージ属性を更新します。

## 追加リソース

- [AgentMail MCP サーバーリポジトリ](https://github.com/agentmail-to/agentmail-mcp)
- [AgentMail ドキュメント](https://docs.agentmail.to/)
- [AgentMail Toolkit](https://github.com/agentmail-to/agentmail-toolkit)
