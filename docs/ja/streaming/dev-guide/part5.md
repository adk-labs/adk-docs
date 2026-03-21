# Part 5: Audio・Image・Video の使い方

このセクションでは、ADK Live API 統合における音声・画像・動画機能を扱います。
対応モデル、音声モデルアーキテクチャ、仕様、実装ベストプラクティスを含みます。

## 音声の使い方

Live API の音声機能は双方向ストリーミングにより、
サブ秒レイテンシの自然な会話を実現します。

### 音声入力を送る

**必須フォーマット:**

- **Format**: 16-bit PCM (signed integer)
- **Sample Rate**: 16,000 Hz (16kHz)
- **Channels**: Mono

ADK は音声変換を行いません。入力は事前に正しい形式へ整えてください。

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L181-L184" target="_blank">main.py:181-184</a>'
audio_blob = types.Blob(
    mime_type="audio/pcm;rate=16000",
    data=audio_data
)
live_request_queue.send_realtime(audio_blob)
```

#### ベストプラクティス

1. 小さなチャンクで送信（10~200ms）
2. `LiveRequestQueue` はバッチ化せず即時転送
3. 自動 VAD（デフォルト）なら連続送信
4. 手動 activity シグナルは VAD を無効化した場合のみ

#### クライアント側入力処理

ブラウザでは Web Audio API + AudioWorklet でマイク音声を取得し、
16kHz PCM16 へ変換して WebSocket 送信します。

```javascript title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/static/js/audio-recorder.js#L7-L58" target="_blank">audio-recorder.js:7-58</a>'
export async function startAudioRecorderWorklet(audioRecorderHandler) {
    const audioRecorderContext = new AudioContext({ sampleRate: 16000 });
    const workletURL = new URL("./pcm-recorder-processor.js", import.meta.url);
    await audioRecorderContext.audioWorklet.addModule(workletURL);

    micStream = await navigator.mediaDevices.getUserMedia({
        audio: { channelCount: 1 }
    });
    const source = audioRecorderContext.createMediaStreamSource(micStream);

    const audioRecorderNode = new AudioWorkletNode(
        audioRecorderContext,
        "pcm-recorder-processor"
    );

    source.connect(audioRecorderNode);
    audioRecorderNode.port.onmessage = (event) => {
        const pcmData = convertFloat32ToPCM(event.data);
        audioRecorderHandler(pcmData);
    };
    return [audioRecorderNode, audioRecorderContext, micStream];
}

function convertFloat32ToPCM(inputData) {
    const pcm16 = new Int16Array(inputData.length);
    for (let i = 0; i < inputData.length; i++) {
        pcm16[i] = inputData[i] * 0x7fff;
    }
    return pcm16.buffer;
}
```

### 音声出力を受け取る

`response_modalities=["AUDIO"]` の場合、出力は `inline_data` で届きます。

- 16-bit PCM
- 24kHz（native audio モデル）
- mono
- `audio/pcm;rate=24000`

```python
from google.adk.agents.run_config import RunConfig, StreamingMode

run_config = RunConfig(
    response_modalities=["AUDIO"],
    streaming_mode=StreamingMode.BIDI
)

async for event in runner.run_live(
    user_id="user_123",
    session_id="session_456",
    live_request_queue=live_request_queue,
    run_config=run_config
):
    if event.content and event.content.parts:
        for part in event.content.parts:
            if part.inline_data and part.inline_data.mime_type.startswith("audio/pcm"):
                audio_bytes = part.inline_data.data
                await stream_audio_to_client(audio_bytes)
```

!!! note "自動 Base64 デコード"

    wire では base64 だが、google.genai types が bytes へ自動デコードします。

## 画像・動画の使い方

ADK Gemini Live API Toolkit では画像/動画を JPEG フレームとして扱います。
一般的な HLS/mp4/H.264 ではなく、フレーム単位 JPEG 送信です。

**仕様:**

- JPEG (`image/jpeg`)
- 最大推奨 1 FPS
- 推奨 768x768

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L202-L217" target="_blank">main.py:202-217</a>'
image_data = base64.b64decode(json_message["data"])
mime_type = json_message.get("mimeType", "image/jpeg")

image_blob = types.Blob(
    mime_type=mime_type,
    data=image_data
)
live_request_queue.send_realtime(image_blob)
```

**不向きな用途:**

- 高速動作のリアルタイム認識
- スポーツ解析や高速モーショントラッキング

### クライアント画像入力

`getUserMedia()` でカメラ取得、`canvas` でフレーム取得、
JPEG base64 を WebSocket 送信する構成です。
（詳細は `app.js` の camera preview / capture / sendImage を参照）

### カスタム動画ストリーミングツール

ADK は async generator ベースの streaming tool をサポートします。
`stop_streaming(function_name: str)` をツールとして提供し、
明示停止できるようにしてください。

## 音声モデルアーキテクチャ

### Native Audio

入力/出力を end-to-end 音声で処理する構成。

| Audio Model Architecture | Platform | Model | Notes |
|-------------------|----------|-------|-------|
| Native Audio | Gemini Live API | [gemini-2.5-flash-native-audio-preview-12-2025](https://ai.google.dev/gemini-api/docs/models#gemini-2.5-flash-live) |Publicly available|
| Native Audio | Vertex AI Live API | [gemini-live-2.5-flash-native-audio](https://cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/2-5-flash-live-api) | Public preview |

**特徴:**

- 高自然性 prosody
- 拡張 voice library
- 自動言語判定
- affective dialog / proactive audio など高度機能
- RunConfig では AUDIO-only

### Half-Cascade

入力音声はネイティブ処理、出力はテキスト生成後 TTS。

| Audio Model Architecture | Platform | Model | Notes |
|-------------------|----------|-------|-------|
| Half-Cascade | Gemini Live API | [gemini-2.0-flash-live-001](https://ai.google.dev/gemini-api/docs/models#gemini-2.0-flash-live) | Deprecated on December 09, 2025 |
| Half-Cascade | Vertex AI Live API | [gemini-live-2.5-flash](https://cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/2-5-flash#2.5-flash) | Private GA, not publicly available |

**特徴:**

- TEXT モダリティ対応
- `speech_config.language_code` で明示制御
- 本番運用での安定性が高い

### モデル名の扱い

環境変数でモデル名を管理する方式を推奨します。

```python
import os
from google.adk.agents import Agent

agent = Agent(
    name="my_agent",
    model=os.getenv("DEMO_AGENT_MODEL", "gemini-2.5-flash-native-audio-preview-12-2025"),
    tools=[...],
    instruction="..."
)
```

## Audio Transcription

入力音声/出力音声の文字起こしを Live API が提供します。
別 STT サービスなしでリアルタイム字幕やログ用途に使えます。

```python
from google.genai import types
from google.adk.agents.run_config import RunConfig

run_config = RunConfig(
    response_modalities=["AUDIO"]
)

run_config = RunConfig(
    response_modalities=["AUDIO"],
    input_audio_transcription=None,
    output_audio_transcription=None
)
```

```python
async for event in runner.run_live(...):
    if event.input_transcription:
        user_text = event.input_transcription.text
        is_finished = event.input_transcription.finished
        if user_text and user_text.strip():
            update_caption(user_text, is_user=True, is_final=is_finished)

    if event.output_transcription:
        model_text = event.output_transcription.text
        is_finished = event.output_transcription.finished
        if model_text and model_text.strip():
            update_caption(model_text, is_user=False, is_final=is_finished)
```

멀티エージェント（`sub_agents`）では転送のために文字起こしが自動有効化されます。

## Voice Configuration (Speech Config)

`speech_config` は agent レベルと RunConfig レベルで設定できます。
優先順位は agent レベルが上です。

```python
from google.genai import types
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search

custom_llm = Gemini(
    model="gemini-2.5-flash-native-audio-preview-12-2025",
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name="Puck"
            )
        ),
        language_code="en-US"
    )
)

agent = Agent(
    model=custom_llm,
    tools=[google_search],
    instruction="You are a helpful assistant."
)
```

Half-cascade の音声:
- Puck
- Charon
- Kore
- Fenrir
- Aoede
- Leda
- Orus
- Zephyr

Native audio はこれに加えて拡張音声を利用できます。

## Voice Activity Detection (VAD)

VAD はデフォルト有効です。
Push-to-talk など手動制御が必要な場合のみ無効化します。

```python
from google.genai import types
from google.adk.agents.run_config import RunConfig

run_config = RunConfig(
    response_modalities=["AUDIO"],
    realtime_input_config=types.RealtimeInputConfig(
        automatic_activity_detection=types.AutomaticActivityDetection(
            disabled=True
        )
    )
)
```

手動シグナル運用時は次を厳守:
- 最初の音声チャンク前に `activity_start`
- 最後の音声チャンク後に `activity_end`

## Proactivity and Affective Dialog

- **Proactive audio**: 明示的指示なしで関連提案/応答
- **Affective dialog**: 感情トーンに合わせた応答スタイル調整

```python
from google.genai import types
from google.adk.agents.run_config import RunConfig

run_config = RunConfig(
    proactivity=types.ProactivityConfig(proactive_audio=True),
    enable_affective_dialog=True
)
```

これらは主に native audio モデル向け機能です。

### Live API Models Compatibility and Availability

モデルごとに、音声入力、音声出力、転写、動画サポートの可否が異なります。

### Handling Audio Transcription at the Client

クライアント側では `input_transcription` と `output_transcription` を字幕表示やログに使います。

### Multi-Agent Transcription Requirements

`sub_agents` を使う構成では、転送のために文字起こしが重要になります。

### Agent-Level Configuration

agent レベルで `speech_config` を設定すると、その agent に専用の音声を持たせられます。

### RunConfig-Level Configuration

RunConfig 側でも `speech_config` を設定できます。

### Configuration Precedence

優先順位は agent レベルの設定が RunConfig より上です。

### Multi-Agent Voice Configuration

複数 agent の会話では、役割に応じて voice を使い分けると聞き取りやすくなります。

### Configuration Parameters

- `voice_config`
- `language_code`
- `prebuilt_voice_config`

### Available Voices

使用可能な音声はモデルやプラットフォームによって異なります。

### Platform Availability

Vertex AI と Gemini Live API で利用可能な機能に差があります。

### Important Notes

- Native audio は AUDIO-only の前提です
- Half-cascade は TEXT と TTS の組み合わせです
- 既定値はモデルごとに異なります

### Voice Activity Detection (VAD)

VAD はユーザーの発話開始/終了を自動判定するための仕組みです。

### How VAD Works

自動活動検出が有効な場合、音声入力のまとまりを ADK が判断します。

### When to Disable VAD

Push-to-talk のように自前で区切りたい場合のみ無効化します。

### VAD Configurations

- 自動 VAD
- 手動 activity signal

### Client-Side VAD Example

ブラウザ側で音声区切りを制御する場合の構成を示します。

#### Server-Side Configuration

サーバー側では `automatic_activity_detection.disabled=True` などで VAD を無効化します。

#### WebSocket Upstream Task

音声チャンクを WebSocket 経由で上流へ送る処理を担当します。

#### Client-Side VAD Implementation

クライアントで発話単位を切ると、帯域と遅延を抑えやすくなります。

#### Client-Side Coordination

UI、録音、送信を同じ状態機械で連携させます。

#### Benefits of Client-Side VAD

- 応答性が高い
- 無駄な音声送信を減らせる
- UI と発話制御を合わせやすい

### Proactivity and Affective Dialog

proactivity と affective dialog は native audio モデル向けの拡張機能です。

### Platform Compatibility

利用可否は Gemini Live API / Vertex AI Live API とモデル世代に依存します。

### How to Handle Model Names

環境変数を使うと、開発と本番でモデル名を切り替えやすくなります。

```python
import os

model_name = os.getenv("DEMO_AGENT_MODEL", "gemini-2.5-flash-native-audio-preview-12-2025")
```

### Live API Models Compatibility and Availability

| 機能 | Native Audio | Half-Cascade |
|---|---|---|
| 音声入力 | ✅ | ✅ |
| 音声出力 | ✅ | TTS 経由 |
| 文字起こし | ✅ | ✅ |
| 動画 | 条件付き | 条件付き |

### Default behavior: Audio transcription is ENABLED by default

デフォルトでは入力/出力の transcription が有効です。

```python
from google.adk.agents.run_config import RunConfig

run_config = RunConfig(
    response_modalities=["AUDIO"],
)
```

### Both input and output transcription are automatically configured

通常は明示設定がなくても、字幕用途の transcription が流れます。

### To disable transcription explicitly:

```python
run_config = RunConfig(
    response_modalities=["AUDIO"],
    input_audio_transcription=None,
    output_audio_transcription=None,
)
```

### Enable only input transcription (disable output):

```python
run_config = RunConfig(
    response_modalities=["AUDIO"],
    input_audio_transcription=types.AudioTranscriptionConfig(),
    output_audio_transcription=None,
)
```

### Enable only output transcription (disable input):

```python
run_config = RunConfig(
    response_modalities=["AUDIO"],
    input_audio_transcription=None,
    output_audio_transcription=types.AudioTranscriptionConfig(),
)
```

### ... runner setup code ...

```python
async for event in runner.run_live(...):
    if event.input_transcription:
        ...
```

### Handling Audio Transcription at the Client

クライアントは transcription を字幕やログへ流すだけでよく、別 STT を必須にしません。

### Multi-Agent Transcription Requirements

`sub_agents` を使うときは、次の agent へコンテキストを渡すため transcription が特に重要です。

### Agent-Level Configuration

agent ごとに音声設定を分けると、役割の違いを表現しやすくなります。

### RunConfig-Level Configuration

RunConfig 側の設定は全体既定値として使います。

### Configuration Precedence

agent レベル設定が RunConfig より優先されます。

### Multi-Agent Voice Configuration

複数 agent の voice を使い分けると、会話の担当が分かりやすくなります。

### Configuration Parameters

| パラメータ | 用途 |
|---|---|
| `voice_config` | 音声選択 |
| `language_code` | 言語設定 |
| `prebuilt_voice_config` | 既定 voice |

### Available Voices

Puck / Charon / Kore / Fenrir / Aoede / Leda / Orus / Zephyr などが利用できます。

### Platform Availability

利用可否はモデルと実行基盤の両方で決まります。

### Important Notes

- Native audio は音声中心
- Half-cascade は文字起こし + TTS
- 設定差分を環境変数で吸収すると運用しやすい

### Client-Side VAD Example

#### Server-Side Configuration

```python
from google.genai import types
from google.adk.agents.run_config import RunConfig

run_config = RunConfig(
    response_modalities=["AUDIO"],
    realtime_input_config=types.RealtimeInputConfig(
        automatic_activity_detection=types.AutomaticActivityDetection(
            disabled=True
        )
    )
)
```

#### WebSocket Upstream Task

音声チャンクを WebSocket で上流へ送ります。

#### Client-Side VAD Implementation

```javascript
function onSpeechBoundary(audioChunk) {
    sendChunk(audioChunk);
}
```

#### Client-Side Coordination

録音、送信、字幕表示の状態をそろえて扱います。

#### Benefits of Client-Side VAD

- レイテンシを下げやすい
- 送信量を抑えやすい
- UI と制御を同じ場所で持てる

### Platform Compatibility

機能ごとの対応可否は Gemini Live API / Vertex AI Live API で差があります。

## まとめ

このパートでは、ADK Gemini Live API Toolkit におけるマルチモーダル実装を学びました。
音声仕様、native/half-cascade の違い、入出力ストリーミング、
transcription、VAD、proactivity/affective dialog、voice 設定と互換性を理解することで、
テキスト/音声/画像/動画を統合した本番向けリアルタイム AI アプリを設計できます。

**Congratulations!**
ADK Gemini Live API Toolkit Developer Guide の学習を完了しました。

← [Previous: Part 4: Understanding RunConfig](part4.md)
