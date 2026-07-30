---
catalog_title: Unstructured
catalog_description: PDF、Office ドキュメント、画像、および 40 種類以上のファイル形式を構造化され AI ですぐに使用できるデータに解析します。
catalog_icon: /integrations/assets/unstructured.png
catalog_tags: ["mcp"]
---

# ADK 向け Unstructured Transform MCP ツール

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span>
</div>

[Unstructured Transform MCP サーバー](https://docs.unstructured.io/transform/overview) は、ADK エージェントを未加工のファイルを構造化された AI 対応データに変換するドキュメント処理プラットフォームである [Unstructured](https://unstructured.io) に接続します。この統合により、エージェントは自然言語を使用して PDF、Office ドキュメント、メール、画像、およびスキャンされたファイル（合計 40 種類以上の [サポートされているファイル形式](https://docs.unstructured.io/transform/supported-file-types)）を分割、補強、チャンク化、埋め込み処理された出力に解析できます。Transform はホスト型リモート MCP サーバーであるため、ローカルにインストールしたり実行したりする必要はありません。

## ユースケース

- **RAG インジェスチョン**: 異種ドキュメントのコレクションを、ベクトル ストアおよび検索パイプライン用にきれいに整理され、チャンク化され、埋め込み準備が整った出力に解析します。
- **ドキュメント Q&A エージェント**: エージェントが必要に応じて契約書、レポート、または論文を取得して解析し、解析されたコンテンツに基づいて質問に回答できるようにします。
- **形式の正規化**: 混合された入力（スキャンされた PDF、スプレッドシート、プレゼンテーション、メール スレッド）を 1 つの一貫した構造化表現に変換します。
- **エージェント ランタイム時の OCR**: より大きなエージェント ワークフロー内の 1 ステップとして、画像やスキャンされたドキュメントからテキストと構造を抽出します。
- **構造化データの抽出**: フォーム、請求書、契約書から、提供されたスキーマまたはサーバーがドキュメントから作成したスキーマに一致する JSON 形式で名前付きフィールドを抽出します。

## 前提条件

- [Unstructured アカウント](https://transform.unstructured.io) および API キー。[API キーの取得](https://docs.unstructured.io/transform/code#get-your-unstructured-api-key-and-url) を参照してください。
- エージェント モデル用の [Gemini API キー](https://aistudio.google.com/apikey)。
- Python 3.10 以降。

## インストール

`mcp` エクストラが含まれる ADK をインストールします。このエクストラは必須であり、これがないと ADK の MCP クラスをインポートできません。

```bash
pip install "google-adk[mcp]"
```

## エージェントでの使用

環境変数で API キーを設定します。

```bash
export UNSTRUCTURED_API_KEY="<your-unstructured-api-key>"
export GOOGLE_API_KEY="<your-gemini-api-key>"
export GOOGLE_GENAI_USE_VERTEXAI=FALSE
```

サーバーは初期ハンドシェイクを含め、すべてのリクエストで Unstructured API キーを Bearer トークンとして認証します。解析ジョブは非同期で実行されるため、`wait_seconds` ヘルパー関数を使用して、エージェントがステータス確認の間に一時停止できるようにします。

=== "Python"

    === "リモート MCP サーバー"

        ```python
        import asyncio
        import os

        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams


        async def wait_seconds(seconds: int) -> dict:
            """次のステータス確認に進む前に待機します。指定がない限り 30 秒間待機します。

            Args:
                seconds: 待機する時間（秒）。

            Returns:
                待機したことを確認する dict。
            """
            seconds = max(1, min(int(seconds), 120))
            await asyncio.sleep(seconds)
            return {"waited_seconds": seconds}


        root_agent = Agent(
            model="gemini-flash-latest",
            name="transform_agent",
            instruction=(
                "You parse documents with the Unstructured Transform MCP server. "
                "Pass public https:// file URLs straight to start_transform_job. It "
                "returns a job_id; poll with check_job_status, calling "
                "wait_seconds(30) between checks (jobs take 30 seconds to a few "
                "minutes). When the job completes, call get_job_results and "
                "report the parsed content back to the user. start_transform_job "
                "accepts an optional stages config; it auto-selects a parse "
                "strategy by default, but if the output looks low quality "
                "(garbled text or lost tables), re-run the file with a hi_res "
                "partition strategy for a cleaner result. If the user wants "
                "specific fields rather than the whole document, extract "
                "instead of just parsing. The extraction tools read the element "
                "JSON a parse produces, so parse the file first and keep the "
                "output_ref that get_job_results returns for it. Call "
                "suggest_extraction_schema_for_file with that output_ref when "
                "you need a schema, then start_extraction_job with "
                "element_json_refs set to the output_refs and schema_to_extract "
                "set to a JSON Schema passed as a JSON string. Poll and read an "
                "extraction job with check_job_status and get_job_results like "
                "any other job; its results come back inline, wrapped with the "
                "source filename, so report that filename with each object. If "
                "asked to parse a local file, explain that this requires the "
                "upload helper from the Unstructured ADK guide."
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
                        "start_transform_job",
                        "suggest_extraction_schema_for_file",
                        "start_extraction_job",
                        "check_job_status",
                        "get_job_results",
                    ],
                )
            ],
        )
        ```

!!! note

    ドキュメントの変換は非同期で行われます。`start_transform_job` がジョブを開始し、エージェントが `check_job_status` をポーリングし、完了すると `get_job_results` が出力に対する署名付きダウンロード URL を返します。モデルのレート制限を無駄に超えないように、上記のようにステータス確認の間に一時停止するようエージェントに指示してください。

    構造化データの抽出は、各ファイルに対して `get_job_results` が返す `output_ref` によって識別される要素 JSON に対して実行される 2 つ目の非同期ジョブです。解析後に抽出するプロンプトは 2 つのポーリング ループを実行するため、追加の時間とモデル ステップを考慮してください。

    **ローカル** ファイルを解析するには、エージェントに `request_file_upload_url` によって返された署名付き URL にファイル バイトを HTTP `PUT` する通常の関数ツールも必要です（このアップロードは MCP 呼び出しではなく、`Authorization` ヘッダーを送信してはなりません）。アップロードと待機ヘルパーを含む完全なエージェントについては、[Unstructured Transform ADK ガイド](https://docs.unstructured.io/transform/install/google-adk) を参照してください。

## 利用可能なツール

ツール | 説明
---- | -----------
`request_file_upload_url` | ローカル ファイルに対して署名付きアップロード URL とファイル参照を返します。
`start_transform_job` | アップロードされたファイルまたは公開 HTTP(S) URL に対する解析ジョブを開始し、`job_id` を返します。
`suggest_extraction_schema_for_file` | まだスキーマがない場合に、1 つの解析済みドキュメント要素 JSON から JSON スキマのドラフトを作成します。
`start_extraction_job` | JSON スキーマに対する解析済み要素 JSON の構造化データ抽出ジョブを開始し、`job_id` を返します。
`check_job_status` | ジョブが `SCHEDULED`、`IN_PROGRESS`、または `COMPLETED` かどうかを報告します。解析ジョブと抽出ジョブの両方に使用されます。
`get_job_results` | 完了したジョブの出力を返します（解析ジョブの場合は署名付きダウンロード URL、抽出ジョブの場合はインライン抽出データ）。

## リソース

- [Unstructured Transform ドキュメント](https://docs.unstructured.io/transform/overview)
- [Unstructured Transform 用 ADK インストール ガイド](https://docs.unstructured.io/transform/install/google-adk)
- [サポートされているファイル形式](https://docs.unstructured.io/transform/supported-file-types)
