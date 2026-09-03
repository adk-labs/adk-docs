# ライブエージェント向けカスタムサーバー

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span>
</div>

`adk web` ツールは開発目的でライブエージェントを実行します。マイクとカメラをキャプチャし、モデルの音声を再生し、文字起こしをレンダリングするブラウザクライアントが付属しているため、独自のコードを書くことなくエージェントと対話できます。本番環境にリリースするということは、これを置き換えることを意味します。起動時にランナーとセッションサービスを一度初期化し、接続されたユーザーごとに 1 つの `LiveRequestQueue` を用意して、クライアントと `run_live()` を中継する独自のサーバーを実行します。

以下は、そのブリッジの完全な FastAPI 実装と、クライアントがそれと通信するために知っておくべき内容です。この例が実践しているライフサイクルを扱った [セッション](sessions.md) をすでに読んでいることを前提としています。

## FastAPI アプリケーションの例

この FastAPI アプリケーションはブリッジを実装しています。WebSocket メッセージを `LiveRequestQueue` に転送するアップストリーム（upstream）タスクと、`run_live()` イベントをクライアントに送り返すダウンストリーム（downstream）タスクという 2 つの並行タスクを実行します。

```python
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from google.adk.runners import Runner
from google.adk.agents.run_config import RunConfig
from google.adk.agents.live_request_queue import LiveRequestQueue
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google_search_agent.agent import agent

# アプリケーションのセットアップ（起動時に 1 回）
APP_NAME = "live-agent"

app = FastAPI()

# セッションサービスの定義
session_service = InMemorySessionService()

# ランナーの定義
runner = Runner(
    app_name=APP_NAME,
    agent=agent,
    session_service=session_service
)

@app.websocket("/ws/{user_id}/{session_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, session_id: str) -> None:
    await websocket.accept()

    # セッションごとの設定: RunConfig、セッション、キュー
    response_modalities = ["AUDIO"]
    run_config = RunConfig(
        response_modalities=response_modalities,
        input_audio_transcription=types.AudioTranscriptionConfig(),
        output_audio_transcription=types.AudioTranscriptionConfig(),
        session_resumption=types.SessionResumptionConfig()
    )

    session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id
    )
    if not session:
        await session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id
        )

    live_request_queue = LiveRequestQueue()

    async def upstream_task() -> None:
        """WebSocket からメッセージを受信し、LiveRequestQueue に送信します。"""
        try:
            while True:
                # WebSocket からテキストメッセージを受信
                data: str = await websocket.receive_text()

                # LiveRequestQueue に送信
                content = types.Content(parts=[types.Part(text=data)])
                live_request_queue.send_content(content)
        except WebSocketDisconnect:
            # クライアントが切断 - キューのクローズをシグナル
            pass

    async def downstream_task() -> None:
        """run_live() から Event を受信し、WebSocket に送信します。"""
        async for event in runner.run_live(
            user_id=user_id,
            session_id=session_id,
            live_request_queue=live_request_queue,
            run_config=run_config
        ):
            # イベントを JSON として WebSocket に送信
            await websocket.send_text(
                event.model_dump_json(exclude_none=True, by_alias=True)
            )

    # 両方のタスクを並行実行
    try:
        await asyncio.gather(
            upstream_task(),
            downstream_task(),
            return_exceptions=True
        )
    finally:
        live_request_queue.close()  # エラー時も含め、常にクローズする
```

!!! note "非同期コンテキストが必須"

    すべての ADK 双方向ストリーミングアプリケーションは、**非同期コンテキストで実行する必要があります**。この要件は複数のコンポーネントに起因します。

    - **`run_live()`**: ADK のストリーミングメソッドは同期ラッパーを持たない非同期ジェネレータです（`run()` とは異なります）。
    - **セッション操作**: `get_session()` と `create_session()` は非同期メソッドです。
    - **WebSocket 操作**: FastAPI の `websocket.accept()`、`receive_text()`、`send_text()` はすべて非同期です。
    - **並行タスク**: アップストリーム/ダウンストリームのパターンには、並行実行のための `asyncio.gather()` が必要です。

    すべてのコード例は、非同期コンテキスト（`async def` 内またはコルーチン内）を前提としています。

## なぜ 2 つのタスクなのか

このブリッジは同時に実行される 2 つのループであり、これによって真の双方向性が実現されます。

- **アップストリーム** は WebSocket から読み取り `LiveRequestQueue` にプッシュするため、エージェントが発話の途中であっても、ユーザーはいつでも入力を送信できます。
- **ダウンストリーム** は `run_live()` からイベントを読み取り WebSocket に書き込むため、応答、文字起こし、ツールの動作が発生すると同時にストリーミングされます。

これらを逐次的に実行すると、割り込み（インターラプト）機能が失われます。ユーザーがエージェントの発話を遮って話しかけようとしている間、サーバーがエージェントの出力を読み取るためにブロックされてしまうためです。`asyncio.gather()` により、両方向が同時にライブ状態に保たれます。

`live_request_queue.close()` は、例外を含むすべての終了パスで実行される必要があります。キューが閉じられていないと Live API に終了シグナルが送信されず、セッションがタイムアウトするまで [同時実行セッションの割り当て](sessions.md#concurrent-sessions) が占有されたままになる可能性があるため、`try/finally` を使用して確実にクローズします。

`gather(..., return_exceptions=True)` は例外を発生させずに収集するため、正常な切断と障害を区別する必要がある場合は、返された値をチェックしてください。

### 本番環境での考慮事項

この例はコアパターンを示しています。本番アプリケーションでは以下を考慮してください。

- **エラー処理（ADK）**: ADK ストリーミングイベントに適切なエラー処理を追加します。エラーイベント処理の詳細については、[エラーイベント](events.md#handling-errors) を参照してください。
    - シャットダウン時に `asyncio.CancelledError` をキャッチしてタスクのキャンセルを適切に処理します。
    - `return_exceptions=True` を指定した `asyncio.gather()` からの例外を確認します（例外は自動的には伝播しません）。
- **エラー処理（Web）**: アップストリーム/ダウンストリームタスクで Web アプリケーション固有のエラーを処理します。たとえば FastAPI の場合：
    - `WebSocketDisconnect`（クライアント切断）、`ConnectionClosedError`（接続喪失）、`RuntimeError`（閉じた接続への送信）をキャッチします。
    - 送信前に `websocket.client_state` で WebSocket の接続状態を検証し、接続が閉じている場合のエラーを防ぎます。
- **認証と認可**: エンドポイントの認証と認可を実装します。
- **レート制限と割り当て**: レート制限とタイムアウト制御を追加します。同時セッションと割り当て管理のガイダンスについては、[同時実行セッション](sessions.md#concurrent-sessions) を参照してください。
- **構造化ロギング**: デバッグには構造化ロギングを使用します。
- **永続的セッションサービス**: 永続的なセッションサービス（`DatabaseSessionService` または `VertexAiSessionService`）の使用を検討してください。詳細については、[ADK セッションサービスドキュメント](../sessions/index.md) を参照してください。

## クライアントの接続

サーバーが WebSocket を公開したら、何らかのクライアントがそれと通信する必要があります。開発中はその役割を `adk web` が果たします。本番環境では、ブラウザアプリ、モバイルアプリ、または電話や WebRTC のブリッジなど、開発者が作成するクライアントになります。何を構築するにしても同じ規約を継承するため、`adk web` が何を行い、どこまでを担当しているかを把握しておくことが有益です。

**`adk web` が自動的に処理すること：**

| 機能 | 組み込みクライアントが行うこと |
|---|---|
| マイク | 16 kHz モノラル PCM としてキャプチャおよびリサンプリングし、`audio/pcm;rate=16000` としてストリーミング |
| 再生 | モデルの音声を 24 kHz モノラル PCM としてギャップレスで再生 |
| カメラ | 約 1 fps の JPEG フレームを `image/jpeg` として送信 |
| 文字起こし | 部分フラグメントをマージして、ユーザーとモデル両方の文字起こしをレンダリング |
| 割り込み（Barge-in） | `interrupted` が設定されたイベントが到着したときに再生を停止 |

**`adk web` が行わないこと**（本番クライアントで必要になる場合あり）：

- 画面共有は非対応。アクティブな音声通話なしの動画は非対応。
- モダリティの選択は不可（レスポンスは常に `AUDIO`）。
- プロアクティブ性、感情的な対話、セッション再開、`save_live_blob`、明示的な VAD シグナルの UI はなし（サーバー側の [`RunConfig`](configuration.md) で設定）。
- 手動の [VAD](configuration.md#voice-activity-detection-vad) は非対応（デフォルトで有効なサーバー側の自動検出に依存）。

`adk web` と `adk api_server` はどちらも同じ `/run_live` WebSocket を提供します。`adk api_server` は `--with_ui` を渡さない限りブラウザクライアントを同梱しません。したがって、`adk web` に対して開発を行い、カスタムクライアントをどちらかに向けることができます。

### ワイヤプロトコルとデータ形式

`/run_live` エンドポイントは **JSON テキストフレームのみ** を扱います。クライアントはシリアル化された [`LiveRequest`](sessions.md#liverequestqueue) オブジェクトを送信し、シリアル化された [`Event`](events.md) オブジェクトを受信します。バイナリデータ（音声や画像のバイト列）は、バイナリ WebSocket フレームとしてではなく、JSON の*内部*で base64 エンコードされて送信されます。

クライアント側では、キャメルケースのフィールド名を使用して、Python と同様のイベントフィールドに応じて分岐処理を行います。

```javascript
websocket.onmessage = (message) => {
    const adkEvent = JSON.parse(message.data);
    if (adkEvent.interrupted) {
        stopAudioPlayback();   // ユーザーが割り込んだため、キューに入っている音声を破棄
        finishCurrentBubble();
        return;
    }
    if (adkEvent.turnComplete) {
        finishCurrentBubble();
        return;
    }
    for (const part of adkEvent.content?.parts ?? []) {
        if (part.text) appendText(part.text);
        if (part.inlineData) enqueueAudio(part.inlineData.data);
    }
};
```

クライアントが生成および消費する必要があるメディアフォーマット（サンプルレート、エンコーディング、チャンクサイズ）については、[音声と動画](audio-video.md) を参照してください。分岐処理に使用するストリーミングフラグ（`partial`、`turnComplete`、`interrupted`）や文字起こしのフラグメント化については、[イベント](events.md) を参照してください。

## イベントのシリアル化

ADK と Live API の間の `/run_live` エンドポイントは JSON テキストのみですが、*開発者のサーバー* と *クライアント* の間のトランスポートは自由に設計できるため、base64 のオーバーヘッドを避けるために音声をバイナリフレームとして送信できます。

`Event` は Pydantic モデルであるため、`model_dump_json()` を使用して WebSocket や SSE トランスポート用の JSON 文字列に変換できます。クライアント側のキャメルケースのフィールド名には `by_alias=True` を、空のフィールドを削除するには `exclude_none=True` を使用します。

```python
async for event in runner.run_live(...):
    await websocket.send_text(event.model_dump_json(exclude_none=True, by_alias=True))
```

`inline_data` のバイナリ音声は JSON 内で base64 エンコードされるため、ペイロードが約 33% 肥大化します。音声のやり取りが多いストリームの場合は、音声をバイナリフレームとして送信し、メタデータを JSON として送信することをお勧めします。

```python
async for event in runner.run_live(...):
    parts = event.content.parts if event.content else []
    audio_parts = [p for p in parts if p.inline_data]
    if audio_parts:
        for part in audio_parts:
            await websocket.send_bytes(part.inline_data.data)
        # 音声バイト列を除いたメタデータ
        await websocket.send_text(event.model_dump_json(
            exclude={"content": {"parts": {"__all__": {"inline_data"}}}},
            by_alias=True,
        ))
    else:
        await websocket.send_text(event.model_dump_json(exclude_none=True, by_alias=True))
```
