# Part 3: run_live() でイベントを処理する

`run_live()` は ADK ストリーミング会話の主要エントリポイントです。
会話進行に合わせてイベントをリアルタイムで `yield` する async generator を提供します。
このパートでは、テキスト/音声/文字起こし/ツール呼び出し/エラーイベントを扱い、
interruption や turn completion で会話フローを制御する方法を説明します。

!!! note "Async Context Required"

    `run_live()` は async コンテキストで実行する必要があります。
    [Part 1: FastAPI Application Example](part1.md#fastapi-application-example) を参照してください。

## run_live() の仕組み

`run_live()` は内部バッファなしでイベントを逐次返します。
メモリ使用量はセッション永続化方式（in-memory / DB）に依存します。

### メソッドシグネチャ

```python title='Source reference: <a href="https://github.com/google/adk-python/blob/427a983b18088bdc22272d02714393b0a779ecdf/src/google/adk/runners.py" target="_blank">runners.py</a>'
async def run_live(
    self,
    *,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    live_request_queue: LiveRequestQueue,
    run_config: Optional[RunConfig] = None,
    session: Optional[Session] = None,
) -> AsyncGenerator[Event, None]:
```

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L225-L233" target="_blank">main.py:225-233</a>'
async for event in runner.run_live(
    user_id=user_id,
    session_id=session_id,
    live_request_queue=live_request_queue,
    run_config=run_config
):
    event_json = event.model_dump_json(exclude_none=True, by_alias=True)
    await websocket.send_text(event_json)
```

### 接続ライフサイクル

1. 初期化: `run_live()` 呼び出しで接続開始
2. アクティブ: 上流（`LiveRequestQueue`）と下流（`run_live()`）を同時処理
3. 正常終了: `LiveRequestQueue.close()`
4. 復旧: `RunConfig.session_resumption` による透過再開

### run_live() が返すイベント

| Event Type | Description |
|------------|-------------|
| **Text Events** | `response_modalities=["TEXT"]` のテキスト応答 |
| **Audio Events with Inline Data** | `response_modalities=["AUDIO"]` のリアルタイム音声 |
| **Audio Events with File Data** | `file_data` 参照を持つ保存済み音声 |
| **Metadata Events** | トークン使用量などのメタ情報 |
| **Transcription Events** | 入力/出力音声の文字起こし |
| **Tool Call Events** | function call / response |
| **Error Events** | モデル/接続エラー |

### run_live() の終了条件

| Exit Condition | Trigger | Graceful? | Description |
|---|---|---|---|
| **Manual close** | `live_request_queue.close()` | ✅ | 明示終了 |
| **All agents complete** | SequentialAgent 最終 `task_completed()` | ✅ | シーケンス完了 |
| **Session timeout** | Live API 制限到達 | ⚠️ | 接続終了 |
| **Early exit** | `end_invocation=True` | ✅ | 早期終了 |
| **Empty event** | 内部終了シグナル | ✅ | ストリーム終了 |
| **Errors** | 例外/接続障害 | ❌ | 異常終了 |

### ADK Session に保存されるイベント

**保存される:**

- `save_live_blob=True` 時の file_data 音声
- usage metadata
- non-partial transcription
- function call / function response
- 主要 control イベント

**保存されない（ストリーミング中のみ）:**

- inline_data 音声
- partial transcription

## イベント理解

### Event クラス

`Event` はストリーミング中のあらゆる状態変化を運ぶ Pydantic モデルです。

### Event の主要フィールド

- `content`
- `author`
- `partial`
- `turn_complete`
- `interrupted`
- `input_transcription` / `output_transcription`
- `usage_metadata`
- `error_code` / `error_message`

#### Event Identity

`event.id` はイベントごとに一意、`event.invocation_id` は同一 invocation 内で共通です。

### event.id と invocation_id

- `event.id`: イベントごとに一意
- `event.invocation_id`: 同一 invocation 内で共通

```python
async for event in runner.run_live(...):
    print(event.id)
    print(event.invocation_id)
```

### author の意味

- モデル応答は `"model"` ではなく agent 名
- ユーザー音声文字起こしイベントは `author="user"`

### Event Authorship

`author` は「誰がそのイベントを出したか」を表す属性です。

## イベントタイプ別処理

### Text Events

```python
async for event in runner.run_live(...):
    if event.content and event.content.parts:
        if event.content.parts[0].text:
            text = event.content.parts[0].text
            if not event.partial:
                update_streaming_display(text)
```

`response_modalities` 未指定時はデフォルト `AUDIO`。
テキスト専用なら `response_modalities=["TEXT"]` を明示してください。

### Audio Events

```python
run_config = RunConfig(
    response_modalities=["AUDIO"],
    streaming_mode=StreamingMode.BIDI
)

async for event in runner.run_live(..., run_config=run_config):
    if event.content and event.content.parts:
        part = event.content.parts[0]
        if part.inline_data:
            await play_audio(part.inline_data.data)
```

### File Data 音声

```python
async for event in runner.run_live(...):
    if event.content and event.content.parts:
        for part in event.content.parts:
            if part.file_data:
                print(part.file_data.file_uri, part.file_data.mime_type)
```

### Metadata / Transcription / Tool / Error

```python
if event.usage_metadata:
    print(event.usage_metadata.total_token_count)

if event.input_transcription:
    display_user_transcription(event.input_transcription)

if event.output_transcription:
    display_model_transcription(event.output_transcription)
```

```python
if event.content and event.content.parts:
    for part in event.content.parts:
        if part.function_call:
            tool_name = part.function_call.name
```

```python
try:
    async for event in runner.run_live(...):
        if event.error_code:
            if event.error_code in ["SAFETY", "PROHIBITED_CONTENT", "BLOCKLIST", "MAX_TOKENS"]:
                break
            continue
finally:
    queue.close()
```

**break / continue 指針:**

- コンテンツポリシー違反や MAX_TOKENS は通常 `break`
- 一時的障害（UNAVAILABLE など）は `continue` + リトライ検討
- `finally` で必ず `queue.close()`

## テキストフラグ処理

### `partial`

- `partial=True`: 増分テキスト
- `partial=False`: マージ済み完全テキスト

### `interrupted`

ユーザー割り込み時は表示/音声再生を即停止します。

### `turn_complete`

モデルのターン完了シグナル。入力 UI 再有効化に使います。

## JSON シリアライズ

### Using event.model_dump_json()

`Event` は Pydantic モデルなので `model_dump_json()` で送信できます。

```python
event_json = event.model_dump_json(exclude_none=True, by_alias=True)
```

### Serialization options

- `exclude_none=True` で不要なフィールドを省く
- `by_alias=True` でクライアント互換の JSON にする

### Deserializing the Client Side

受信側は JSON から `Event` 相当の構造へ戻して UI を更新します。

### Audio Transmission Optimization

音声はバイナリフレーム、メタデータは JSON として分けると効率的です。

音声 `inline_data` は JSON 化で base64 になりサイズ増。
本番では音声をバイナリフレーム、メタデータをテキストで分離送信する方法が有効です。

## run_live() の自動ツール実行

### The Challenge with Raw Live API

生の Live API では、ストリーミング中のツール実行を自前で調停する必要があります。

### How ADK Simplifies Tool Use

ADK はツール呼び出し、応答、順序制御をまとめて面倒見ます。

ADK は Live API 生利用で必要なツール実行オーケストレーションを自動化します。

```python
import os
from google.adk.agents import Agent
from google.adk.tools import google_search

agent = Agent(
    name="google_search_agent",
    model=os.getenv("DEMO_AGENT_MODEL", "gemini-2.5-flash-native-audio-preview-12-2025"),
    tools=[google_search],
    instruction="You are a helpful assistant that can search the web."
)
```

```python
async for event in runner.run_live(...):
    if event.get_function_calls():
        print(event.get_function_calls()[0].name)
    if event.get_function_responses():
        print(event.get_function_responses()[0].response)
```

long-running tool / streaming tool も `run_live()` 内で連携できます。

### Tool Execution Events

イベントを監視するだけで、どのツールが呼ばれたかを把握できます。

### Long-Running and Streaming Tools

長時間ツールや streaming tool も `run_live()` の流れに組み込めます。

### Key Takeaway

アプリケーションはループに集中し、ツールの制御は ADK に任せるのが基本です。

## InvocationContext

`run_live()` 1 回につき 1 つの `InvocationContext` が生成されます。
ツール/コールバックで次の情報にアクセスできます。

- `context.invocation_id`
- `context.session.events`
- `context.session.state`
- `context.session.user_id`
- `context.run_config`
- `context.end_invocation`

### What is an Invocation?

1 回の `run_live()` 実行を 1 つの invocation として扱います。

### Who Uses InvocationContext?

ツール、コールバック、エージェント内部ロジックが invocation 情報を参照します。

#### What InvocationContext Contains

- `context.invocation_id`
- `context.session.events`
- `context.session.state`
- `context.session.user_id`
- `context.run_config`
- `context.end_invocation`

## マルチエージェントのベストプラクティス

Gemini Live API Toolkit での代表パターン:

- 単一エージェント
- coordinator + sub-agent（`transfer_to_agent`）
- SequentialAgent パイプライン（`task_completed`）

### SequentialAgent と BIDI streaming

SequentialAgent は `run_live()` の単一ループを保ったまま、担当エージェントを順番に引き継ぎます。

### 推奨パターン: 透過的な Sequential Flow

アプリ側は現在の agent を表示するだけにして、遷移の制御は ADK に任せます。

### エージェント遷移中のイベントフロー

- Researcher が入力を受け取る
- Writer が中間成果をまとめる
- Reviewer が最終確認する

### 設計原則

#### 1. 単一イベントループ

1 つの async for ループで全エージェントを処理します。

#### 2. Persistent Queue

入力キューは workflow 全体で共有し、エージェントごとに作り直しません。

#### 3. Agent-Aware UI (Optional)

表示層が現在の agent 名を把握すると、会話の進行が理解しやすくなります。

#### 4. Transition Notifications

必要に応じて agent 切り替え時の通知を UI に出します。

### transfer_to_agent と task_completed の違い

- `transfer_to_agent`: coordinator が次の担当を選ぶ
- `task_completed`: 現在の agent が完了し、シーケンスが次へ進む

### ベストプラクティス要約

- ループは 1 つに保つ
- queue は 1 つに保つ
- agent 遷移はアプリロジックで複製しない

## まとめ

このパートでは ADK Gemini Live API Toolkit のイベント処理全体を学びました。
各イベントタイプ処理、`partial`/`interrupted`/`turn_complete` による UI 制御、
JSON 直列化、ADK の自動ツール実行、InvocationContext による状態アクセス、
マルチエージェント運用まで理解できれば、
リアルタイムで自然なストリーミング体験を提供するアプリを構築できます。

---

← [Previous: Part 2: Sending Messages with LiveRequestQueue](part2.md) | [Next: Part 4: Understanding RunConfig](part4.md) →
