# AgentQL

[AgentQL MCPサーバー](https://github.com/tinyfish-io/agentql-mcp)は、ADKエージェントを[AgentQL](https://www.agentql.com/)に接続します。AgentQLは、CSSやXPathセレクターではなく、意味に基づいてWeb要素をクエリするセマンティック抽出エンジンです。この機能により、エージェントは自然言語の定義を使用して、Webページ、PDF、認証済みセッションから特定のデータポイントを取得できます。

## ユースケース

- **回復力のあるWeb抽出**: 自然言語の説明を使用して、動的なWebサイトからデータを抽出します。この機能により、エージェントは、レイアウトやCSSを頻繁に更新するサイトから、破損することなく確実に情報を収集できます。

- **データ正規化**: 非構造化Webページを、クリーンで予測可能なJSON形式に変換します。この機能により、エージェントは、さまざまなソース（複数の求人掲示板やショッピングサイトなど）のデータを単一のスキーマに即座に正規化できます。

## 前提条件

- AgentQLで[APIキー](https://dev.agentql.com/sign-in)を作成します。詳細については、[ドキュメント](https://docs.agentql.com/quick-start)を参照してください。

## エージェントでの使用

=== "ローカルMCPサーバー"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
    from mcp import StdioServerParameters

    AGENTQL_API_KEY = "YOUR_AGENTQL_API_KEY"

    root_agent = Agent(
        model="gemini-1.5-pro",
        name="agentql_agent",
        instruction="ユーザーがAgentQLから情報を取得するのを支援します",
        tools=[
            MCPToolset(
                connection_params=StdioConnectionParams(
                    server_params = StdioServerParameters(
                        command="npx",
                        args=[
                            "-y",
                            "agentql-mcp",
                        ],
                        env={
                            "AGENTQL_API_KEY": AGENTQL_API_KEY,
                        }
                    ),
                    timeout=300,
                ),
            )
        ],
    )
    ```

## 利用可能なツール

ツール <img width="100px"/> | 説明
---- | -----------
`extract-web-data` | 「prompt」を実際のデータとその抽出するフィールドの説明として使用して、指定された「url」から構造化データを抽出します

## ベストプラクティス

正確な抽出を確実にするために、エージェントにプロンプトを表示する際は、次のガイドラインに従ってください。

- **要素ではなくデータを記述する**: 視覚的な説明（「青いボタン」など）は避けてください。代わりに、データエンティティ（「送信ボタン」や「製品価格」など）を記述してください。

- **階層を定義する**: リストを抽出する場合は、アイテムのコレクションを探すようにエージェントに明示的に指示し、各アイテムに必要なフィールドを定義します。

- **意味的にフィルタリングする**: プロンプト自体の中で、特定のデータ型（「広告とナビゲーションリンクを除く」など）を無視するようにツールに指示できます。

## 追加リソース

- [AgentQL MCPサーバードキュメント](https://docs.exa.ai/reference/exa-mcp)
- [AgentQL MCPサーバーリポジトリ](https://github.com/tinyfish-io/agentql-mcp)
