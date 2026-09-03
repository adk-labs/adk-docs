# ライブエージェント向けイベント

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span>
</div>

ライブエージェントが生成するすべての出力は `Event` としてアプリケーションに届きます。モデルが生成する部分テキスト、生の音声バイト列、会話の両側の文字起こし、ツール呼び出し、トークン数、エラーなどが含まれます。単一の発話応答でも数十個のイベントに分かれて届くことがあり、それらを適切に処理することが、遅延のない即時性のある音声インターフェースを実現する鍵となります。

`Event` は、[イベント](../events/index.md) で解説されている ADK 共通のクラスと同じです。ライブセッションでは、リクエスト/レスポンス型エージェントがアクセスしないフィールド（オーディオ Blob、文字起こし、中断フラグなど）が入力され、1回限りではなく継続的なストリームとして配信されます。これらを生成するループについては、[セッション](sessions.md) を参照してください。

## ライブエージェントのイベントデータ

[`Event`](../api-reference/python/google-adk.html#google.adk.events.Event) は、`LlmResponse` を拡張した Pydantic モデルです。ライブセッションでは以下のフィールドを使用します。

| フィールド | 内容 |
|---|---|
| `content.parts[].text` | テキストパート — ライブセッションでは思考の要約（thought summary）やその他の非発話コンテンツ |
| `content.parts[].inline_data` | 再生用の一時的な生オーディオバイト列 |
| `content.parts[].file_data` | アーティファクトに保存された音声への参照（`save_live_blob=True` の場合） |
| `content.parts[].function_call` / `function_response` | ツール呼び出しと結果（ADK が自動的に実行） |
| `input_transcription` / `output_transcription` | テキストとしてのユーザーおよびモデルの発話 |
| `partial` | 増分チャンクの場合は `True`、マージされた結果の場合は `False` |
| `turn_complete` | モデルが応答全体を完了したときに `True` |
| `interrupted` | 応答の途中でユーザーが割り込んだ（barge-in）ときに `True` |
| `usage_metadata` | コストと割り当て追跡のためのトークン数 |
| `error_code` / `error_message` | 障害診断情報 |
| `author` | イベントを生成した主体（下記参照） |

### 作成者（Authorship）

ライブセッションにおいて、`event.author` は文字起こしされたユーザー音声の場合は `"user"`、モデル自体の出力の場合はリテラルの `"model"` ではなく**エージェント名**になります。レスポンスに `input_transcription` が含まれるか、`content.role == 'user'` である場合、ADK は常に `author="user"` を設定します。入力文字起こしレスポンスに必ずしも `role == 'user'` が含まれるとは限らないため、文字起こしを確認することで確実な属性判定が行われます（[`base_llm_flow.py`](https://github.com/google/adk-python/blob/main/src/google/adk/flows/llm_flows/base_llm_flow.py)）。

エージェント名を使用することで、マルチエージェントセッションで作成者別にイベントをフィルタリングできます。

```python
events = [e for e in stream if e.author == "billing_agent"]
```

## イベントの種類

ライブセッション中、エージェントは部分テキスト、音声、発話の文字起こし、ツール呼び出し、トークン使用量メタデータなど、複数の異なるイベントタイプを通じて継続的な出力を配信します。以下のセクションでは、これらのイベントタイプについて説明します。

### テキスト

テキストは `event.content.parts[].text` に届きます。ライブセッションでは、これは思考の要約やその他の非発話コンテンツです。ADK がサポートするすべての [ライブモデル](models.md#live-models) は音声を入力として受け取り音声を出力するため、**モデルの発話応答はテキストパートではなく、[出力文字起こし（output transcription）](configuration.md#audio-transcription) として返されます**。

```python
async for event in runner.run_live(...):
    if event.content and event.content.parts:
        for part in event.content.parts:
            if part.text and not event.partial:
                update_display(part.text)
```

!!! warning "`parts` をループ処理し、決して `parts[0]` だけを想定しないでください"

    1つのイベントに複数のパートが含まれることがあり、ライブモデルはこれを日常的に行います。`event.content.parts[0].text` は残りのパートを暗黙的に無視し、最初のパートがテキストでない場合（思考の要約、関数呼び出し、オーディオ Blob など）にエラーになります。パートのリストを反復処理し、設定されているフィールドに応じて分岐してください。

### 音声

`response_modalities=["AUDIO"]`（ライブのデフォルト）の場合、モデルは音声を `inline_data` として返します。

```python
async for event in runner.run_live(...):
    if event.content and event.content.parts:
        for part in event.content.parts:
            if part.inline_data:  # 生の PCM バイト
                await play_audio(part.inline_data.data)
```

`inline_data` は一時的なものであり、永続化されません。[`save_live_blob=True`](configuration.md#save_live_blob) を設定すると、ADK はアーティファクトサービス内のファイルに音声をまとめ、後から音声を取得できるように生バイトの代わりに（追加ではなく）`file_data` 参照を提供します。フォーマットと再生方法については、[音声と動画](audio-video.md) を参照してください。

### 文字起こし（Transcription）

文字起こしが有効になっている場合（デフォルトでオン）、ユーザーとモデルの発話は `event.input_transcription` および `event.output_transcription` に届きます。これらはフラグメント単位でストリーミングされます。`.text` は最新のフラグメントを保持し、`.finished` はターンの最後のフラグメントであることを示します（`event.partial` と連動）。フラグメントを連結して完全な文字起こしを構築します。[音声の文字起こし](configuration.md#audio-transcription) を参照してください。

```python
async for event in runner.run_live(...):
    if event.input_transcription and event.input_transcription.text:
        show_caption(event.input_transcription.text, is_user=True)
    if event.output_transcription and event.output_transcription.text:
        show_caption(event.output_transcription.text, is_user=False)
```

### ツール呼び出し

モデルは `part.function_call` を通じてツールを要求します。ADK は登録されたツールを自動的に実行するため、通常これを直接処理することはありません。[自動ツール実行](tools.md#automatic-tool-execution) を参照してください。

### メタデータ

`event.usage_metadata` には、リアルタイムのコストおよびクォータ追跡のためのトークン数（`prompt_token_count`、`candidates_token_count`、`total_token_count`、`cached_content_token_count`）が含まれます。

## ストリーミングフラグ

ライブ UI は、`partial`、`turn_complete`、`interrupted` の 3 つのフラグによって制御されます。
`partial` フラグは、増分チャンクとマージされた結果を区別します。

- `partial=True`: 直前のイベント以降の新しいテキストのみ。
- `partial=False`: このセグメントのマージされた完全なテキスト。

ADK がチャンクを自動的に蓄積するため（`StreamingResponseAggregator`）、`partial=False` イベントには直前の `partial=True` チャンクの合計がすでに含まれています。リアルタイムのタイピング効果が不要な場合は、partial イベントを無視して `partial=False` のみで処理できます。

```text
Event 1: partial=True,  text="Hello",       turn_complete=False
Event 2: partial=True,  text=" world",      turn_complete=False
Event 3: partial=False, text="Hello world", turn_complete=False
Event 4: partial=False, text="",            turn_complete=True
```

`partial=False` 状態はターンごとに複数回（文ごとに1回など）発生することがあり、`turn_complete=True` は最後のセグメントの後に独自のイベントとして1回だけ届きます。

`turn_complete` と `interrupted` は、UI がどの状態に入るべきかを示します。

| turn_complete | interrupted | アプリケーションの動作 |
|---|---|---|
| True | False | 入力を有効化、「準備完了」を表示 |
| False | True | 再生を停止、部分テキストをクリア |
| True | True | ターン終了。通常の完了と同じ |
| False | False | ストリーミングテキストの表示を継続 |

```python
async for event in runner.run_live(...):
    if event.interrupted:
        stop_audio_playback()   # ユーザーが割り込んだためキュー内の音声を破棄
        clear_streaming_text()
    if event.turn_complete:
        enable_microphone()     # 次のターンの準備
```

`interrupted` を処理しないと、すでにバッファリングされた音声がユーザーの発話に被さって再生され続けます。

## エラー処理

エラーは `event.error_code` と `event.error_message` に現れます。判断すべき決定事項は、モデルの応答を継続できるかどうかです。モデルが停止した場合は `break` し、一時的な障害の場合は `continue` します。

```python
try:
    async for event in runner.run_live(...):
        if event.error_code:
            logger.error("Model error: %s - %s", event.error_code, event.error_message)
            if event.error_code in ("SAFETY", "PROHIBITED_CONTENT", "BLOCKLIST", "MAX_TOKENS"):
                break       # モデルが終了したため、このターンにはこれ以上イベントはない
            continue        # 一時的な障害。ストリームが回復する可能性がある
        # ... コンテンツの処理 ...
finally:
    live_request_queue.close()  # break した場合でも完了した場合でも必ず実行
```

| エラーコード | カテゴリ | アクション |
|---|---|---|
| `SAFETY`, `PROHIBITED_CONTENT`, `BLOCKLIST` | コンテンツポリシー | `break` — モデルが応答を終了 |
| `MAX_TOKENS` | 制限 | `break` — モデルが生成を完了 |
| `UNAVAILABLE`, `DEADLINE_EXCEEDED` | 一時的 | `continue` — ネットワークまたはタイムアウト、自動解決の可能性あり |
| `RESOURCE_EXHAUSTED` | レート制限 | 指数バックオフを伴う `continue` |
| `CANCELLED` | クライアント | `break` — クリーンアップ |
| `UNKNOWN` | システム | ロギングして `continue` |

1秒未満の一時的なエラーについてはユーザーに通知しないでください。`RESOURCE_EXHAUSTED` の場合は、無限ループに陥らないようリトライ回数に上限を設け、バックオフを行ってください。エラーコードは Gemini API に由来します。[FinishReason](https://ai.google.dev/api/python/google/ai/generativelanguage/Candidate/FinishReason) および [Agent Platform リファレンス](https://docs.cloud.google.com/gemini-enterprise-agent-platform/reference/models/inference) を参照してください。

## クライアントへのイベント送信

ブラウザやモバイルクライアントにイベントをストリーミングするには、それらをシリアル化してトランスポート経由で送信します。`Event` は Pydantic モデルであるため、`model_dump_json()` で処理できます。base64 でエンコードされた音声は JSON サイズを約 33% 膨張させるため、音声はバイナリフレームとして送信することをお勧めします。シリアル化パターンと対応するクライアント側の処理については、[カスタムサーバー](custom-server.md#serializing-events) を参照してください。
