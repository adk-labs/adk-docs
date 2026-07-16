---
catalog_title: Unstructured
catalog_description: PDF、Office ドキュメント、画像、および 40 種類以上のファイルタイプを、構造化され、AI がすぐに利用できるデータにパースします
catalog_icon: /integrations/assets/unstructured.png
catalog_tags: ["mcp"]
---

# ADK 用 Unstructured Transform MCP ツール

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span>
</div>

[Unstructured Transform MCP サーバー](https://docs.unstructured.io/transform/overview) は、ADK エージェントを、生ファイルを構造化され AI が利用可能なデータに変換するドキュメント処理プラットフォームである [Unstructured](https://unstructured.io) に接続します。この統合により、エージェントは自然言語を使用して、PDF、Office ドキュメント、電子メール、画像、およびスキャンされたファイル（合計 40 以上の [サポートされているファイルタイプ](https://docs.unstructured.io/transform/supported-file-types)）を分割、拡張、チャンク、および埋め込み（embedding）処理された出力にパースする機能を得ることができます。Transform はホスト型のリモート MCP サーバーであるため、ローカルにインストールしたり実行したりするものはありません。

## ユースケース

- **RAG インジェスチョン**: 異種ドキュメントコレクションを、ベクトルストアや検索パイプライン用に、クリーンでチャンク処理され、埋め込み可能な出力にパースします。
- **ドキュメント Q&A エージェント**: エージェントがオンデマンドで契約書、レポート、または論文を取得してパースし、パースされたコンテンツに基づいて質問に回答できるようにします。
- **フォーマットの正規化**: 混合された入力（スキャンされた PDF、スプレッドシート、プレゼンテーション、電子メールスレッド）を 1 つの一貫した構造化表現に変換します。
- **エージェント実行時の OCR**: 大規模なエージェントワークフロー内の 1 つのステップとして、画像やスキャンされたドキュメントからテキストと構造を抽出します。

## 前提条件

- [Unstructured アカウント](https://transform.unstructured.io) と API キー。[API キーの取得](https://docs.unstructured.io/transform/code#get-your-unstructured-api-key-and-url) を参照してください。
- エージェントのモデル用の [Gemini API キー](https://aistudio.google.com/apikey)。
- Python 3.10 以降。

## インストール

`mcp` エクストラを指定して ADK をインストールします。このエクストラは必須です。これがないと、ADK の MCP クラスをインポートできません。

```bash
pip install "google-adk[mcp]"
```

## エージェントとの連携

環境変数として API キーを設定します。

```bash
export UNSTRUCTURED_API_KEY="<your-unstructured-api-key>"
export GOOGLE_API_KEY="<your-gemini-api-key>"
export GOOGLE_GENAI_USE_VERTEXAI=FALSE
```

サーバーは、初期ハンドシェイクを含むすべてのリクエストにおいて、Unstructured API キーを Bearer トークンとして認証します。パースジョブは非同期で実行されるため、エージェントがステータス確認の間に一時停止できるように、`wait_seconds` ヘルパーを使用します。

=== "Python"

    === "リモート MCP サーバー"

        ```python
        import asyncio
        import os

        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams


        async def wait_seconds(seconds: int) -> dict:
            """次のステータスチェックの前に一時停止します。特に指示がない限り、30秒間使用します。

            Args:
                seconds: 待機する秒数。

            Returns:
                待機を確認する dict。
            """
            seconds = max(1, min(int(seconds), 120))
            await asyncio.sleep(seconds)
            return {"waited_seconds": seconds}


        root_agent = Agent(
            model="gemini-flash-latest",
            name="transform_agent",
            instruction=(
                "You parse documents with the Unstructured Transform MCP server. "
                "Pass public https:// file URLs straight to transform_files. It "
                "returns a job_id; poll with check_transform_status, calling "
                "wait_seconds(30) between checks (jobs take 30 seconds to a few "
                "minutes). When the job completes, call get_transform_results and "
                "report the parsed content back to the user. transform_files "
                "accepts an optional stages config; it auto-selects a parse "
                "strategy by default, but if the output looks low quality "
                "(garbled text or lost tables), re-run the file with a hi_res "
                "partition strategy for a cleaner result. If asked to parse a "
                "local file, explain that this requires the upload helper from the "
                "Unstructured ADK guide."
            ),
            tools=[
                wait_seconds,
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://mcp.transform.unstructured.io",  # root URL; do not append /mcp
                        headers={
                            "Authorization": f"Bearer {os.environ['UNSTRUCTURED_API_KEY']}",
                        },
                        timeout=30.0,  # ADK's 5s default is too short for a remote handshake
                        sse_read_timeout=300.0,
                    ),
                    tool_filter=[
                        "request_file_upload_url",
                        "transform_files",
                        "check_transform_status",
                        "get_transform_results",
                    ],
                )
            ],
        )
        ```

!!! note

    ドキュメントの変換は非同期で行われます。`transform_files` がジョブを開始し、エージェントが `check_transform_status` をポーリングし、完了すると `get_transform_results` が出力用の事前署名付きダウンロード URL を返します。ポーリングループがモデルのレート制限を消費しすぎないように、上記のようにステータス確認の間に一時停止するようエージェントに指示してください。

    **ローカル**ファイルをパースするには、エージェントに `request_file_upload_url` によって返される事前署名付き URL にファイルバイトを HTTP `PUT` するプレーンな関数ツールも必要です（このアップロードは MCP 呼び出しではなく、`Authorization` ヘッダーを送信してはなりません）。アップロードと待機ヘルパーを備えた完全なエージェントは、[Unstructured Transform ADK ガイド](https://docs.unstructured.io/transform/install/google-adk) にあります。

## 利用可能なツール

ツール | 説明
---- | -----------
`request_file_upload_url` | ローカルファイル用の事前署名付きアップロード URL とファイル参照を返します。
`transform_files` | アップロードされたファイルまたはパブリック HTTP(S) URL のパースジョブを開始し、`job_id` を返します。
`check_transform_status` | ジョブが `SCHEDULED`、`IN_PROGRESS`、または `COMPLETED` であるかどうかを報告します。
`get_transform_results` | 完了したジョブのパースされた出力と事前署名付きダウンロード URL を返します。

## リソース

- [Unstructured Transform ドキュメント](https://docs.unstructured.io/transform/overview)
- [Unstructured Transform 用の ADK インストールガイド](https://docs.unstructured.io/transform/install/google-adk)
- [サポートされているファイルタイプ](https://docs.unstructured.io/transform/supported-file-types)
