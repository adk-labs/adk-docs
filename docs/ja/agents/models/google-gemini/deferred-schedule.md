# Gemini モデルでの遅延スケジューリング

<div class="language-support-tag">
  <span class="lst-supported">ADK でのサポート</span><span class="lst-python">Python v2.10.0</span><span class="lst-preview">プレビュー</span>
</div>

エージェントのワークロードによって、レイテンシの要件は異なります。対話型アシスタントは即座に応答する必要がありますが、要約ジョブ、一括評価の実行、ドキュメント処理パイプラインなどは、空き容量を待つことができます。遅延スケジューリング（Deferred scheduling）を使用すると、ADK エージェントは対話用の容量を奪い合うのではなく、オフピーク容量で実行されるようにモデル呼び出しをキューに入れることができます。

`RunConfig` の `service_tier` 設定を使用して、実行（run）ごとに遅延スケジューリングをリクエストできます。この設定はモデルやエージェントではなく実行設定の一部であるため、1 つのエージェント定義で対話型リクエストとバッチワークロードの両方に対応できます。

!!! example "プレビュー: 遅延容量の利用には許可リスト（allowlist）への登録が必要です"

    この Google Cloud 機能はプレビュー機能であり、遅延容量でリクエストを実行するには Google Cloud プロジェクトが許可リストに登録されている必要があります。詳細については、[自律型エージェントのスケジューリング（Autonomous agent scheduling）](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/efficiency/autonomous-scheduling)をご覧ください。

## はじめに

遅延スケジューリングには、Google Cloud for Gemini の [Interactions API](index.md#interactions-api) で構成された Gemini モデルが必要です。次の例に示すように、モデルで `use_interactions_api=True` を設定し、エージェントの実行時に `RunConfig(service_tier=ServiceTier.DEFERRED)` を渡します。

=== "Python"

    ```python
    import asyncio

    from google.adk.agents import LlmAgent
    from google.adk.agents import RunConfig
    from google.adk.apps import App
    from google.adk.models import ServiceTier
    from google.adk.models.google_llm import Gemini
    from google.adk.runners import InMemoryRunner
    from google.genai import types

    root_agent = LlmAgent(
        name='batch_agent',
        model=Gemini(
            model='gemini-flash-latest',
            use_interactions_api=True,  # Required for deferred scheduling
        ),
        instruction='Process input documents and produce summaries.',
    )

    app = App(name='batch_app', root_agent=root_agent)
    runner = InMemoryRunner(app=app)


    async def main() -> None:
      session = await runner.session_service.create_session(
          app_name=app.name,
          user_id='user_123',
          session_id='session_456',
      )

      # Request off-peak capacity for every model call in this run.
      run_config = RunConfig(service_tier=ServiceTier.DEFERRED)

      async for event in runner.run_async(
          user_id='user_123',
          session_id=session.id,
          new_message=types.Content(
              role='user',
              parts=[types.Part.from_text(
                  text='Summarize quarterly performance metrics.'
              )],
          ),
          run_config=run_config,
      ):
        if event.content and event.content.parts:
          for part in event.content.parts:
            if part.text:
              print(part.text)


    asyncio.run(main())
    ```

ランナー（Runner）はモデル呼び出しを送信し、キューに入れられた処理が完了するのを待ってから、レスポンスイベントを生成（yield）します。コード側では、標準の実行とまったく同じ方法でイベントを処理できます。

!!! warning "待機中は実行がハングしているように見えます"

    リクエストがキューに入っている間、`run_async()` メソッドはイベントを生成しません。待機時間はバックエンドの負荷によって異なり、ADK は上限を設けません。Web UI やターミナルでは、この遅延がハングしているように見えることがあります。進行状況インジケーターを表示するか、[クライアント側のデッドラインを設定](#set-a-client-side-deadline)してください。

ティア（tier）が適用されたことを確認するには、アプリケーションログで次のメッセージを確認してください。

| ログメッセージ | レベル | 意味 |
| :--- | :--- | :--- |
| `Using service_tier from run_config: deferred` | `DEBUG` | ADK がリクエストにティアを適用しました。 |
| `Interaction <id> is queued; waiting for the result.` | `INFO` | バックエンドが処理をキューに受け入れました。 |
| `Interaction <id> reached status completed.` | `INFO` | 結果の準備ができました。 |
| `run_config.service_tier=... has no effect for agent <name>` | `WARNING` | ADK がティアを破棄しました。[トラブルシューティング](#troubleshooting)をご覧ください。 |

## 遅延スケジューリングの仕組み

標準のモデルリクエストは同期的です。ADK がリクエストを送信すると、モデルは同じ接続上でレスポンスを返します。`ServiceTier.DEFERRED` を設定して遅延スケジューリングを有効にすると、ADK はリクエストをバックグラウンド実行としてマークし、バックエンドはそれをキューに入れて、結果の代わりにインタラクション ID（interaction ID）を即座に返します。

その後、ADK はエクスポネンシャルバックオフ（指数バックオフ）を使用してキュー内の処理を確認し、最終ステータスに到達するまで一時的な読み取りエラーを吸収しながら結果を待機します。結果が返されると通常のレスポンスイベントに変換して生成します。このループは内部的に行われるため、インタラクション ID が外部に露出することはなく、取得用のコードを記述する必要もありません。ただし、キューの待機時間に加えて数秒のポーリング遅延が発生するため、短時間でレイテンシの影響を受けやすい呼び出しには遅延スケジューリングを使用しないでください。

待機動作の次の特性は、エージェントの設計方法に影響します。

*   **ADK はクライアント側のデッドラインを設定しません。** インタラクションに対するバックエンドの完了タイムアウトが待機時間の唯一の上限となります。より早く停止するには、[クライアント側のデッドラインを設定する](#set-a-client-side-deadline)をご覧ください。
*   **モデルの各ターンは個別にキューに入れられます。** ツールを呼び出すエージェントでは、ターンごとに独自のインタラクションが作成されるため、合計レイテンシは実行全体の 1 回の待機ではなく、すべてのターンのキュー待機時間の合計になります。

## 設定オプション

`RunConfig` の `service_tier` 設定は、実行内のすべてのモデル呼び出しに対する容量プールを選択します。

| オプション | 型 | デフォルト | 説明 |
| :--- | :--- | :--- | :--- |
| `service_tier` | `Optional[ServiceTier \| str]` | `None` | この実行のモデル呼び出しに対するサービングティア。 |

`ServiceTier` 列挙型（enum）は次のティアを定義しています。

*   `ServiceTier.DEFERRED`: オフピーク容量で実行されるように呼び出しをキューに入れます。容量が逼迫している場合でも失敗せず、空きができるまで待機します。他のティアは ADK のリクエスト実行方法を変更しません。また、このティアはストリーミングと併用できません。
*   `ServiceTier.FLEX`: レイテンシ保証のない、低コストのベストエフォート容量です。
*   `ServiceTier.STANDARD`: デフォルトのティアです。
*   `ServiceTier.PRIORITY`: レイテンシの影響を受けやすい呼び出し向けの予約容量です。

`service_tier` を未設定のままにするとリクエストからフィールドが完全に省略され、`ServiceTier.STANDARD` と同等になります。`ServiceTier` 列挙型は `str` のサブクラスであるため、列挙型メンバーの代わりに `'deferred'` のような通常の文字列を渡すこともできます。文字列形式を使用すると、ADK で定数が定義される前にバックエンドがサポートする新しいティアを利用することもできます。

## 高度な使用方法

次のセクションでは、クライアント側のデッドラインによって遅延実行の待機時間に上限を設ける方法と、HTTP 経由でエージェントを提供する際に遅延スケジューリングをリクエストする方法について説明します。

### クライアント側のデッドラインを設定する {#set-a-client-side-deadline}

遅延リクエストはオフピーク容量を待機するため、その所要時間はバックエンドの負荷に依存します。合計経過時間に上限を設けるには、実行を `asyncio.timeout()` でラップします（Python 3.11 以降が必要）。

=== "Python"

    ```python
    import asyncio
    import logging

    from google.adk.agents import RunConfig
    from google.adk.models import ServiceTier
    from google.genai import types

    logger = logging.getLogger(__name__)

    # Continues from the Get started example, reusing runner and session.
    message = types.Content(
        role='user',
        parts=[types.Part.from_text(text='Generate a quarterly summary.')],
    )
    run_config = RunConfig(service_tier=ServiceTier.DEFERRED)

    try:
      async with asyncio.timeout(300):
        async for event in runner.run_async(
            user_id='user_123',
            session_id=session.id,
            new_message=message,
            run_config=run_config,
        ):
          if event.content and event.content.parts:
            for part in event.content.parts:
              if part.text:
                print(part.text)
    except TimeoutError:
      logger.error('Deferred run exceeded the 300 second client deadline.')
    ```

!!! danger "クライアントのデッドラインはリクエストをキャンセルしません"

    タイムアウトになると ADK は結果のポーリングを停止しますが、バックエンドの処理は停止しません。キューに入れられたリクエストは完了するまで実行されて課金対象の使用量を消費し、その後の出力を取得することもできなくなります。タイムアウトしたターンは破棄されたものとして扱い、使用量を制限する目的でクライアントのデッドラインを使用しないでください。

### HTTP 経由で遅延スケジューリングをリクエストする

`adk api_server` で提供するエージェントは、`/run` および `/run_sse` エンドポイントのリクエストボディで `service_tier` を受け付けます。

```json
{
  "app_name": "batch_app",
  "user_id": "user_123",
  "session_id": "session_456",
  "new_message": {
    "role": "user",
    "parts": [{"text": "Summarize batch results."}]
  },
  "service_tier": "deferred"
}
```

`/run_sse` リクエストの場合は、`"streaming": false` も設定する必要があります。`"service_tier": "deferred"` と `"streaming": true` を組み合わせると、HTTP 422 が返されます。
HTTP リクエストはキューの待機時間全体にわたって接続を開いたままにするため、ホスティングプラットフォームのリクエストタイムアウトが遅延実行の実質的な上限となります。

*   **プロキシと Ingress のタイムアウトを引き上げてください。** ロードバランサや Ingress コントローラは、デフォルトで長時間実行されるバックエンド接続を閉じます。[Cloud Run のリクエストタイムアウト](https://cloud.google.com/run/docs/configuring/request-timeout)など、ご使用のプラットフォームの上限を確認し、想定されるキュー待機時間をカバーできるように引き上げてください。
*   **クライアントの切断は結果の取得をキャンセルしますが、実行自体はキャンセルしません。** 接続が閉じられると、サーバーはポーリングタスクをキャンセルします。キュー内のリクエストは引き続き実行されて課金対象の使用量を消費し、出力は失われます。

長時間待機する可能性がある遅延ワークロードの場合は、代わりに Google Cloud Agent Platform の [Agent Runtime](/ja/deploy/agent-runtime/) にデプロイしてください。Agent Runtime はマネージドコンテナ内で呼び出し（invocation）を実行し、そのために HTTP 接続を開いたままにしません。

## 制限事項

遅延スケジューリングには次の制限事項が適用されます。

*   **許可リストによるアクセス:** 遅延容量を使用するには、Google Cloud プロジェクトが許可リストに登録されている必要があります。
*   **Gemini および Interactions API のみ:** 遅延スケジューリングは、`use_interactions_api=True` を設定した `Gemini` モデルでのみ機能します。カスタム `BaseLlm` サブクラスを含む他のすべてのモデルでは、ティアは無視されます。
*   **ストリーミングとの非互換性:** `RunConfig(service_tier=ServiceTier.DEFERRED, streaming_mode=StreamingMode.SSE)` を構築すると、`pydantic.ValidationError` が発生します。
*   **`ManagedAgent` クラスはティアを無視します:** 独自のインタラクションループを実行するため、`service_tier` を読み取りません。
*   **再起動をまたぐ再開は不可:** ADK は実行中のインタラクション ID を永続化せず、キュー内のインタラクションに実行を再接続する手段も提供しません。クライアントプロセスが停止した場合、ADK は保留中の処理を破棄し、次の実行で新しいインタラクションを作成します。

## トラブルシューティング {#troubleshooting}

次のセクションでは、遅延スケジューリングを使用する際の一般的な問題とその解決方法について説明します。

### ADK がティアを無視し、実行自体は成功する場合

エージェントのモデルが `use_interactions_api=True` を設定した `Gemini` インスタンスでない場合、ADK はティアを破棄し、実行ごとに 1 回警告をログに記録して、標準容量で呼び出しを実行します。実行は成功するため、ログが唯一のシグナルとなります。

```text
run_config.service_tier=... has no effect for agent <name>: its model does not
use the interactions API, which is the only path with a serving tier. Set
use_interactions_api=True on the model to apply the tier.
```

この警告は意図的なものです。マルチエージェントの実行では一部のエージェントのみが Interactions API を使用している場合があるため、使用できないティアに対して例外を発生させるのではなく警告を出します。ログで `has no effect for agent` を検索し、`use_interactions_api=True` が必要なモデルを特定してください。

### OpenAI の `service_tier` フィールド

`OpenAIResponsesLlm` クラスにも `service_tier` フィールドがあります。これは無関係の設定であり、実行ではなくモデルに設定するもので、`RunConfig.service_tier` の値は反映されません。一方を設定しても、もう一方には影響しません。

## 追加リソース

*   [Gemini Interactions API](index.md#interactions-api)
*   [ランタイム設定](/ja/runtime/runconfig/)
*   [Interactions API コードサンプル](https://github.com/google/adk-python/tree/main/contributing/samples/models/interactions_api)
