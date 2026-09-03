# ライブエージェント向け音声と動画

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span>
</div>

音声と動画は、ライブエージェントを真にリアルタイムでインタラクティブなものにする要素であり、正確なフォーマットが重要です。Live API は音声に対して特定の PCM サンプルレートを要求し、画像や動画フレームはテキストとは異なる送信メソッドを使用します。

**ADK はメディアの変換を行いません。** サンプルレート、エンコーディング、MIME タイプを正しく合わせることは開発者の責任であり、間違ったフォーマットを渡すと、わかりやすいエラーメッセージではなく、無音、ノイズ、または接続エラーが発生します。以下にその仕様を示します。

これらのモダリティをサポートするモデルについては、[サポート対象モデル](models.md) を参照してください。音声、文字起こし、ターン検出については、[設定](configuration.md) を参照してください。これらをすべてすでに実装しているクライアントで試すには、`adk web` でエージェントを実行してください。独自に作成する場合は、[カスタムサーバーの構築](custom-server.md#connect-a-client) を参照してください。

## 音声入力

マイクの音声は、[`send_realtime()`](sessions.md#liverequestqueue) を介して生のバイト（raw bytes）として送信します。バイト列は Live API が期待するフォーマットである必要があり、ADK はそれをそのまま透過的に渡します。

| プロパティ | 値 |
| :--- | :--- |
| エンコーディング | 16-bit PCM, signed, little-endian |
| サンプルレート | 16,000 Hz (16 kHz) |
| チャンネル | モノラル (Mono) |
| MIME タイプ | `audio/pcm;rate=16000` |

```python
from google.genai import types

live_request_queue.send_realtime(
    types.Blob(mime_type="audio/pcm;rate=16000", data=audio_data)
)
```

低遅延を実現するために、小さなチャンク単位で音声をストリーミングしてください。`LiveRequestQueue` は結合（coalescing）を行わずに各チャンクを即座に転送するため、送信するチャンクサイズがモデルが受信する粒度になります。

- **超低遅延**（リアルタイム会話）: チャンクあたり 10〜20 ms。
- **バランス**（推奨）: チャンクあたり 50〜100 ms。16 kHz では 100 ms は `16000 × 0.1 × 2 = 3200` バイトです。
- **低オーバーヘッド**: チャンクあたり 100〜200 ms。

セッション中は一貫したチャンクサイズを使用し、次のチャンクを送信する前にモデルの応答を待たないでください。モデルはターンごとではなく、連続的に音声を処理します。[音声活動検出（VAD）](configuration.md#voice-activity-detection-vad) が有効な場合（デフォルト）、連続的にストリーミングして API に音声を検出させます。[アクティビティシグナル](sessions.md#liverequestqueue) は、VAD を無効にした場合にのみ送信します。

## 音声出力

`response_modalities=["AUDIO"]`（ライブのデフォルト）の場合、モデルはイベントストリーム上の `inline_data` パートとして音声を返します。

| プロパティ | 値 |
| :--- | :--- |
| エンコーディング | 16-bit PCM, signed, little-endian |
| サンプルレート | 24,000 Hz (24 kHz) — 入力の 16 kHz と異なる点に注意 |
| チャンネル | モノラル (Mono) |
| MIME タイプ | `audio/pcm;rate=24000` |

```python
async for event in runner.run_live(...):
    if event.content and event.content.parts:
        for part in event.content.parts:
            if part.inline_data and part.inline_data.mime_type.startswith("audio/pcm"):
                await play_audio(part.inline_data.data)  # 生の 24 kHz PCM バイト
```

バイト列はすぐに再生できる状態で到着するため、クライアント側でのデコードは不要です。Live API はネットワーク経由で音声を base64 として送信しますが、`google.genai` が自動的にデコードするため、`part.inline_data.data` はすでに `bytes` です。どのイベントが音声を保持し、文字起こしとどのようにインターリーブされるかについては、[イベント](events.md#audio) を参照してください。音声をアーティファクトサービスに永続化するには、[`save_live_blob=True`](configuration.md#save_live_blob) を設定します。

## 画像と動画

画像と動画は、音声と同じ [`send_realtime()`](sessions.md#liverequestqueue) メソッドを介して個別の JPEG フレームとして送信されます。動画コーデックは使用されず、動画ストリームは個々の blob として送信される静止画フレームの連続です。

| プロパティ | 値 |
| :--- | :--- |
| フォーマット | JPEG (`image/jpeg`) |
| フレームレート | 約 1 フレーム/秒（推奨最大値） |
| 解像度 | 768×768 ピクセル（推奨） |

```python
from google.genai import types

live_request_queue.send_realtime(
    types.Blob(mime_type="image/jpeg", data=jpeg_bytes)
)
```

約 1 FPS であれば、モデルはユーザーがカメラを向けている対象や話している内容を確認できますが、動きに依存するものは認識できません。アクション認識、スポーツ分析、動体追跡には、この方法では提供されない時間的解像度が必要です。

[Shopper's Concierge のデモ](https://youtu.be/LwHPYyw7u6U?si=lG9gl9aSIuu-F4ME&t=40) では、アプリはユーザーがアップロードした画像を `send_realtime()` で送信します。エージェントはコンテキストを認識し、EC カタログから一致する商品を検索します。

<div class="video-grid">
  <div class="video-item">
    <div class="video-container">
<iframe width="560" height="315" src="https://www.youtube.com/embed/LwHPYyw7u6U?si=lG9gl9aSIuu-F4ME&amp;start=40" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
    </div>
  </div>
</div>

フレームが到着したときにエージェントが反応できるように、ライブ動画ストリームをツールに供給する方法については、[ストリーミングツール](tools.md#streaming-tools) を参照してください。
