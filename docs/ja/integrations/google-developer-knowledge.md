---
catalog_title: Google Developer Knowledge
catalog_description: Google の公式開発者ドキュメントを検索して、コードとガイダンスを探します
catalog_icon: /integrations/assets/google-developer-knowledge.png
catalog_tags: ["mcp"]
---

# ADK 向け Google Developer Knowledge MCP ツール

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Google Developer Knowledge MCP サーバー](https://developers.google.com/knowledge/mcp) は、
Google の公開開発者ドキュメントにプログラムからアクセスできるようにし、
この知識ベースを自分のアプリケーションやワークフローに統合できるようにします。
ADK エージェントを Google の公式ドキュメントライブラリに接続することで、受け取るコードやガイダンスが最新かつ
信頼できる文脈に基づいていることを保証できます。

## ユースケース

- **実装ガイダンス**: 特定の機能を実装する最適な方法を質問します(例: Firebase Cloud Messaging を使ったプッシュ通知)。
- **コード生成と説明**: たとえば Python で Cloud Storage プロジェクト内のすべてのバケットを一覧表示する例のように、ドキュメントからコード例を検索します。
- **トラブルシューティングとデバッグ**: エラーメッセージや API キーのウォーターマークを問い合わせて、問題をすばやく解決します。
- **比較分析と要約**: Cloud Run と Cloud Functions のようなサービス間の比較を作成します。

## 前提条件

- [Google Cloud プロジェクト](https://developers.google.com/workspace/guides/create-project)
- [Developer Knowledge API の有効化](https://console.cloud.google.com/start/api?id=developerknowledge.googleapis.com)
- [認証構成](https://developers.google.com/knowledge/mcp#authentication) の完了(OAuth または API キー)

## インストール

Google Cloud プロジェクトで Developer Knowledge MCP サーバーを有効にする必要があります。
正確な `gcloud` コマンドと手順については、公式の [インストールガイド](https://developers.google.com/knowledge/mcp#installation) を参照してください。

## エージェントで使う

=== "Python"

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

        DEVELOPER_KNOWLEDGE_API_KEY = "YOUR_DEVELOPER_KNOWLEDGE_API_KEY"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="google_knowledge_agent",
            instruction="Search Google developer documentation for implementation guidance.",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://developerknowledge.googleapis.com/mcp",
                        headers={"X-Goog-Api-Key": DEVELOPER_KNOWLEDGE_API_KEY},
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "Remote MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const DEVELOPER_KNOWLEDGE_API_KEY = "YOUR_DEVELOPER_KNOWLEDGE_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "google_knowledge_agent",
            instruction: "Search Google developer documentation for implementation guidance.",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://developerknowledge.googleapis.com/mcp",
                    transportOptions: {
                        requestInit: {
                            headers: {
                                "X-Goog-Api-Key": DEVELOPER_KNOWLEDGE_API_KEY,
                            },
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## 利用可能なツール

| ツール名 | 説明 |
|---|---|
| `search_documents` | Google の開発者ドキュメントを検索し、クエリに関連するページとスニペットを見つけます |
| `get_documents` | 検索結果の親参照を使って、複数のドキュメントの全文を取得します |

## 追加資料

- [Developer Knowledge MCP ドキュメント](https://developers.google.com/knowledge/mcp)
- [Developer Knowledge API リファレンス](https://developers.google.com/knowledge/api)
- [Corpus リファレンス](https://developers.google.com/knowledge/reference/corpus-reference)
