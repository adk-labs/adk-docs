---
catalog_title: Hugging Face
catalog_description: モデル、データセット、研究論文、AI ツールにアクセスします
catalog_icon: /adk-docs/integrations/assets/hugging-face.png
catalog_tags: ["mcp"]
---

# ADK 向け Hugging Face MCP ツール

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Hugging Face MCP Server](https://github.com/huggingface/hf-mcp-server) を使うと、
ADK エージェントを Hugging Face Hub と何千もの Gradio AI アプリケーションに
接続できます。

## ユースケース

- **AI/ML アセットの発見:** タスク、ライブラリ、キーワードを基に Hub 内の
  モデル、データセット、論文を検索・フィルタリングします。
- **マルチステップワークフローの構築:** あるツールで音声を文字起こしし、
  別のツールでその結果テキストを要約する、といった連携ができます。
- **AI アプリケーションの検索:** 背景除去や音声合成など、特定のタスクを
  実行できる Gradio Spaces を探します。

## 前提条件

- Hugging Face で [user access token](https://huggingface.co/settings/tokens) を
  作成してください。詳細は
  [ドキュメント](https://huggingface.co/docs/hub/en/security-tokens) を参照してください。

## エージェントでの使用

=== "Python"

    === "ローカル MCP サーバー"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        HUGGING_FACE_TOKEN = "YOUR_HUGGING_FACE_TOKEN"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="hugging_face_agent",
            instruction="ユーザーが Hugging Face から情報を取得するのを支援します",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params = StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "@llmindset/hf-mcp-server",
                            ],
                            env={
                                "HF_TOKEN": HUGGING_FACE_TOKEN,
                            }
                        ),
                        timeout=30,
                    ),
                )
            ],
        )
        ```

    === "リモート MCP サーバー"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

        HUGGING_FACE_TOKEN = "YOUR_HUGGING_FACE_TOKEN"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="hugging_face_agent",
            instruction="ユーザーが Hugging Face から情報を取得するのを支援します",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPServerParams(
                        url="https://huggingface.co/mcp",
                        headers={
                            "Authorization": f"Bearer {HUGGING_FACE_TOKEN}",
                        },
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "ローカル MCP サーバー"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const HUGGING_FACE_TOKEN = "YOUR_HUGGING_FACE_TOKEN";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "hugging_face_agent",
            instruction: "Help users get information from Hugging Face",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: ["-y", "@llmindset/hf-mcp-server"],
                        env: {
                            HF_TOKEN: HUGGING_FACE_TOKEN,
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

    === "リモート MCP サーバー"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const HUGGING_FACE_TOKEN = "YOUR_HUGGING_FACE_TOKEN";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "hugging_face_agent",
            instruction: "Help users get information from Hugging Face",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://huggingface.co/mcp",
                    transportOptions: {
                        requestInit: {
                            headers: {
                                Authorization: `Bearer ${HUGGING_FACE_TOKEN}`,
                            },
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## 利用可能なツール

Tool | Description
---- | -----------
Spaces Semantic Search | 自然言語クエリで最適な AI アプリを探す
Papers Semantic Search | 自然言語クエリで ML 研究論文を探す
Model Search | タスク、ライブラリなどで絞り込んで ML モデルを検索
Dataset Search | 作成者、タグなどで絞り込んでデータセットを検索
Documentation Semantic Search | Hugging Face ドキュメントライブラリを検索
Hub Repository Details | Models、Datasets、Spaces の詳細情報を取得

## 構成

Hugging Face Hub MCP サーバーで利用可能なツールを構成するには、
Hugging Face アカウントの
[MCP Settings Page](https://huggingface.co/settings/mcp) を開いてください。

ローカル MCP サーバーを構成するには、次の環境変数を使用できます。

- `TRANSPORT`: 使用するトランスポートタイプ（`stdio`、`sse`、
  `streamableHttp`、`streamableHttpJson`）
- `DEFAULT_HF_TOKEN`: ⚠️ リクエストは `Authorization: Bearer` ヘッダーで受け取った
  `HF_TOKEN` で処理されます。ヘッダーが送信されなかった場合は
  `DEFAULT_HF_TOKEN` が使われます。この値は開発/テスト環境またはローカル
  STDIO デプロイメントでのみ設定してください。⚠️
- stdio トランスポートで実行している場合、`DEFAULT_HF_TOKEN` が未設定なら
  `HF_TOKEN` が使用されます。
- `HF_API_TIMEOUT`: Hugging Face API リクエストのタイムアウト（ミリ秒）
  （デフォルト: 12500ms / 12.5 秒）
- `USER_CONFIG_API`: ユーザー設定に使う URL（デフォルトはローカルフロントエンド）
- `MCP_STRICT_COMPLIANCE`: JSON モードで GET 405 を拒否する場合は True に設定
  （デフォルトは welcome page を返します）
- `AUTHENTICATE_TOOL`: 呼び出されたときに OAuth チャレンジを発行する
  Authenticate ツールを含めるかどうか
- `SEARCH_ENABLES_FETCH`: true にすると、hf_doc_search が有効なときに
  hf_doc_fetch ツールも自動で有効化

## 追加リソース

- [Hugging Face MCP Server Repository](https://github.com/huggingface/hf-mcp-server)
- [Hugging Face MCP Server Documentation](https://huggingface.co/docs/hub/en/hf-mcp-server)
