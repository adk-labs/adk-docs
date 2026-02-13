---
catalog_title: Hugging Face
catalog_description: Access models, datasets, research papers, and AI tools
catalog_icon: /adk-docs/integrations/assets/hugging-face.png
catalog_tags: ["mcp"]
---
# Hugging Face

[Hugging Face MCP Server](https://github.com/huggingface/hf-mcp-server)を使用して、ADKエージェントをHugging Face Hubおよび何千ものGradio AIアプリケーションに接続できます。

## ユースケース

- **AI/MLアセットの発見**: タスク、ライブラリ、またはキーワードに基づいて、Hubでモデル、データセット、および論文を検索およびフィルタリングします。
- **多段階ワークフローの構築**: あるツールでオーディオを文字起こしし、別のツールで結果のテキストを要約するなど、ツールを連携させます。
- **AIアプリケーションの検索**: 背景の削除やテキスト読み上げなど、特定のタスクを実行できるGradio Spacesを検索します。

## 前提条件

- Hugging Faceで[ユーザーアクセストークン](https://huggingface.co/settings/tokens)を作成します。詳細については、[ドキュメント](https://huggingface.co/docs/hub/en/security-tokens)を参照してください。

## エージェントでの使用

=== "ローカルMCPサーバー"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from google.adk.tools.mcp_tool import McpToolset
    from mcp import StdioServerParameters

    HUGGING_FACE_TOKEN = "YOUR_HUGGING_FACE_TOKEN"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="hugging_face_agent",
        instruction="ユーザーがHugging Faceから情報を取得するのを支援します",
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

=== "リモートMCPサーバー"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
    from google.adk.tools.mcp_tool import McpToolset

    HUGGING_FACE_TOKEN = "YOUR_HUGGING_FACE_TOKEN"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="hugging_face_agent",
        instruction="""ユーザーがHugging Faceから情報を取得するのを支援します""",
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

## 利用可能なツール

ツール | 説明
---- | -----------
Spacesセマンティック検索 | 自然言語クエリを介して最高のAIアプリを検索
論文セマンティック検索 | 自然言語クエリを介してML研究論文を検索
モデル検索 | タスク、ライブラリなどでフィルタリングしてMLモデルを検索
データセット検索 | 作成者、タグなどでフィルタリングしてデータセットを検索
ドキュメントセマンティック検索 | Hugging Faceドキュメントライブラリを検索
Hubリポジトリの詳細 | モデル、データセット、スペースに関する詳細情報を取得

## 構成

Hugging Face Hub MCPサーバーで利用可能なツールを構成するには、Hugging Faceアカウントの[MCP設定ページ](https://huggingface.co/settings/mcp)にアクセスしてください。


ローカルMCPサーバーを構成するには、次の環境変数を使用できます。

- `TRANSPORT`: 使用するトランスポートタイプ（`stdio`、`sse`、`streamableHttp`、または`streamableHttpJson`）
- `DEFAULT_HF_TOKEN`: ⚠️ リクエストは`Authorization: Bearer`ヘッダーで受信した`HF_TOKEN`で処理されます。ヘッダーが送信されなかった場合は`DEFAULT_HF_TOKEN`が使用されます。開発/テスト環境またはローカルSTDIOデプロイメントでのみ設定してください。⚠️
- stdioトランスポートで実行している場合、`DEFAULT_HF_TOKEN`が設定されていない場合は`HF_TOKEN`が使用されます。
- `HF_API_TIMEOUT`: Hugging Face APIリクエストのタイムアウト（ミリ秒）（デフォルト：12500ms / 12.5秒）
- `USER_CONFIG_API`: ユーザー設定に使用するURL（デフォルトはローカルフロントエンド）
- `MCP_STRICT_COMPLIANCE`: JSONモードでのGET 405拒否に対してTrueに設定（デフォルトはウェルカムページを提供）
- `AUTHENTICATE_TOOL`: 呼び出されたときにOAuthチャレンジを発行する認証ツールを含めるかどうか
- `SEARCH_ENABLES_FETCH`: trueに設定すると、hf_doc_searchが有効になっているときはいつでもhf_doc_fetchツールが自動的に有効になります。


## 追加リソース

- [Hugging Face MCPサーバーリポジトリ](https://github.com/huggingface/hf-mcp-server)
- [Hugging Face MCPサーバードキュメント](https://huggingface.co/docs/hub/en/hf-mcp-server)
