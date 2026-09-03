# ライブエージェント向け設定

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

`RunConfig` は、ライブセッションの動作を形作る設定を行います。エージェントの声のトーン、音声の文字起こし方法、ターン終了の判定タイミング、保持する会話履歴の量、適用する制限などを設定します。これを [`Runner.run_live()`](https://google.github.io/adk-docs/api-reference/python/) に渡すと、そのセッションにのみ適用されます。同じエージェントの 2 人のユーザーが、まったく異なる設定でセッションを実行できます。

`RunConfig` はライブ専用ではありません。[ランタイム設定](../runtime/runconfig.md) では、クラス全体と `run_async()` に適用されるフィールドについて説明しています。以下では、`run_live()` において重要となるサブセットと、ライブセッションにのみ存在する音声関連の設定について説明します。

## RunConfig パラメータ クイックリファレンス

以下の表は、ライブエージェントにとって最も重要な `RunConfig` パラメータのクイックリファレンスです。

| パラメータ | 型 | 目的 | 参照 |
|---|---|---|---|
| **response_modalities** | list[str] | 出力形式。ライブエージェントは `AUDIO` を使用する必要がある（ライブモデルは `TEXT` をサポートしていない） | [詳細](#response-modalities) |
| **streaming_mode** | StreamingMode | `run_async()` パスでのチャンク配信または単一配信。`run_live()` では読み取られない | [詳細](#streamingmode-bidi-or-sse) |
| **session_resumption** | SessionResumptionConfig | 自動再接続を有効化 | [詳細](sessions.md#session-resumption) |
| **context_window_compression** | ContextWindowCompressionConfig | セッション期間を無制限に延長 | [詳細](sessions.md#context-window-compression) |
| **history_config** | HistoryConfig | 過去の会話履歴をライブサーバーに再生（リプレイ）する方法を制御 | [詳細](#history_config) |
| **max_llm_calls** | int | セッションあたりの LLM 呼び出し総数を制限 | [詳細](#max_llm_calls) |
| **save_live_blob** | bool | 音声/動画ストリームを永続化 | [詳細](#save_live_blob) |
| **custom_metadata** | dict[str, Any] | 呼び出しイベントにカスタムメタデータを添付 | [詳細](#custom_metadata) |
| **speech_config** | SpeechConfig | 音声と言語の設定 | [音声と言語](#voice-and-language) |
| **input_audio_transcription** | AudioTranscriptionConfig | ユーザー音声を文字起こし | [音声の文字起こし](#audio-transcription) |
| **output_audio_transcription** | AudioTranscriptionConfig | モデル音声を文字起こし | [音声の文字起こし](#audio-transcription) |
| **realtime_input_config** | RealtimeInputConfig | VAD（音声活動検出）の設定 | [音声活動検出](#voice-activity-detection-vad) |
| **explicit_vad_signal** | bool | モデルから明示的な音声活動イベントを出力 | [詳細](#other-live-related-fields) |
| **proactivity** | ProactivityConfig | プロアクティブな音声を有効化（モデル依存） | [プロアクティブおよび感情的な対話](#proactivity-and-affective-dialog) |
| **enable_affective_dialog** | bool | 感情への適応（モデル依存） | [プロアクティブおよび感情的な対話](#proactivity-and-affective-dialog) |
| **translation_config** | TranslationConfig | リアルタイムの音声間翻訳（翻訳モデル専用） | [詳細](#other-live-related-fields) |
| **avatar_config** | AvatarConfig | エージェントをアニメーションアバターとしてレンダリング | [詳細](#other-live-related-fields) |

設定オプションの詳細については、Python API リファレンスの [`RunConfig`](../api-reference/python/google-adk.html#google.adk.agents.RunConfig) を参照してください。

**インポートパス：**

上記の表で参照されているすべての構成型クラスは、`google.genai.types` からインポートされます。

```python
from google.genai import types
from google.adk.agents.run_config import RunConfig, StreamingMode

# 構成型は types モジュールからアクセスします
run_config = RunConfig(
    session_resumption=types.SessionResumptionConfig(),
    context_window_compression=types.ContextWindowCompressionConfig(...),
    speech_config=types.SpeechConfig(...),
    # など
)
```

`RunConfig` クラス自体および `StreamingMode` 列挙型は、`google.adk.agents.run_config` からインポートされます。

## レスポンスモード（Response modes）

`response_modalities` 設定は出力形式を制御し、セッションには正確に 1 つの形式が設定されます。**ライブエージェントの場合、値は常に `["AUDIO"]` です。** ADK がサポートするすべての [ライブモデル](models.md#live-models) はそれ以外のモダリティを受け付けないためです。未設定のままにすると ADK が自動的に設定するため、ほとんどのライブアプリケーションではこのフィールドを直接操作する必要はありません。

!!! warning "`response_modalities=["TEXT"]` からの移行"

    古い ADK サンプルや一部のモデルでは、テキストのみのライブセッションが許可されていました。現在ではこれは機能しません。音声のみを出力する最新のライブモデルに対して `["TEXT"]` で `run_live()` を実行すると失敗します。

    **ライブエージェントからテキストを取得するには、[`event.output_transcription`](#audio-transcription) を読み取ります。** ADK では文字起こしがデフォルトで有効になっているため、通常は `response_modalities` の行を削除するだけで修正できます。

    標準の Gemini モデルで実行される `run_async()` パスでは、`["TEXT"]` が引き続き正しい設定です。[双方向ストリーミングまたは SSE](#streamingmode-bidi-or-sse) を参照してください。

レスポンスモダリティはモデルの出力にのみ影響します。モデルがその入力モダリティをサポートしている限り、設定に関係なく**常にテキスト、音声、または動画入力を送信できます**。

## 双方向ストリーミングまたは SSE { #streamingmode-bidi-or-sse }

ADK は 2 つの異なるエンドポイントを介して Gemini に接続でき、**呼び出す `Runner` メソッドによってどちらかが選択されます**。

- **`runner.run_live()`**: ADK は **Live API**（`live.connect()` 経由の双方向ストリーミングエンドポイント）への WebSocket を開きます。本ガイドの以降で解説する内容であり、リアルタイムの音声や動画に必須です。
- **`runner.run_async()`**: ADK は **標準の Gemini API**（`generate_content_async()` 経由の単項/ストリーミングエンドポイント）に HTTP を使用します。レスポンスをチャンクごとにストリーミングするには、`RunConfig.streaming_mode = StreamingMode.SSE` を設定します。

2 つのモデルセットはほとんど重複しません。`gemini-flash-latest` などの標準 Gemini モデルは双方向接続を維持せず、[サポート対象モデル](models.md#live-models) のモデルは `run_live()` で駆動することを目的として設計されているため、モデルの選択は `Runner` メソッドの選択と密接に関係しています。

!!! warning "Python: `StreamingMode.BIDI` は ADK を Live API に切り替えません"

    **Python** では、`RunConfig.streaming_mode` は `run_async()` のコードパスでのみ読み取られ、単一の完全なレスポンス（`StreamingMode.NONE`、デフォルト）とチャンク配信（`StreamingMode.SSE`）の選択を行います。`run_live()` パスでは読み取られないため、`streaming_mode=StreamingMode.BIDI` を設定しても何の効果もなく、警告なしで無視されます。**双方向ストリーミングを利用するには `run_live()` を呼び出す必要があります。** ADK の Python `StreamingMode` の docstring でも、BIDI は「標準の実行パスでは使用されず」、実際の双方向動作は「`streaming_mode` に依存しないまったく異なるコードパスを使用する」と説明されています。

    **Java では異なります。** ADK Java のフローは実際に `StreamingMode.BIDI` を読み取り、Java クイックスタートでは `runLive()` に渡す `RunConfig` で明示的に設定します。言語間で設定をそのまま移植するのではなく、各言語のクイックスタートに従ってください。

```python
# Live API: streaming_mode は不要。run_live() の呼び出し自体がこれを選択します
run_config = RunConfig(response_modalities=["AUDIO"])
async for event in runner.run_live(..., run_config=run_config):
    ...
```

この選択は、ADK が Gemini とどのように通信するかだけに影響します。クライアント側のアーキテクチャとは独立しており、どちらのパスでも WebSocket サーバー、REST API、または SSE エンドポイントを構築できます。

`run_async()` および SSE パス（`streaming_mode` の値、プログレッシブ SSE ストリーミング、言語固有の設定）については、[ランタイム設定](../runtime/runconfig.md#enable-streaming) を参照してください。

## その他の制御設定

ADK は、セッションの動作制御、コスト管理、およびデバッグやコンプライアンス目的での音声データの保持のために、追加の RunConfig オプションを提供しています。

```python
run_config = RunConfig(
    # 呼び出しごとの合計 LLM 呼び出し回数を制限
    max_llm_calls=500,  # デフォルト: 500 (暴走ループを防止)
                        # 0 または負数 = 無制限 (注意して使用)

    # デバッグ/コンプライアンスのために音声/動画アーティファクトを保存
    save_live_blob=True,  # デフォルト: False

    # イベントにカスタムメタデータを添付
    custom_metadata={"user_tier": "premium", "session_type": "support"},  # デフォルト: None
)
```

### max_llm_calls

`max_llm_calls` は、呼び出しコンテキストごとの LLM 呼び出し回数を制限します。詳細は [ランタイム設定](../runtime/runconfig.md#configure-runtime-limits-and-debugging) で説明されています。

**これは `run_live()` には適用されません。** このパラメータは `run_async()` パスのみを保護するため、ライブセッションではこれによる自動的なコスト上限は得られません。セッション継続時間の制限、ターン数のカウント、モデルイベントの `usage_metadata`（[メタデータ](events.md#metadata)）の監視、ループの前にサーキットブレーカーを配置するなど、自前で予算を管理してください。

### save_live_blob

`save_live_blob=True` を設定すると、セッションの音声を [セッションサービス](../sessions/index.md) には参照として、[アーティファクトサービス](../artifacts/index.md) にはファイルとして永続化します。名前に反して、現在永続化されるのは**音声のみ**であり、動画は保存されません。

音声動作のデバッグや、規制された環境での監査証跡のために有効にしてください。それ以外の場合は無効のままにしておくことをお勧めします。16 kHz PCM 入力は 2 つのサービスに書き込まれるため、**セッションあたり 1 分間に約 1.92 MB** を消費し、音声ワークロードでは急速に容量が累積します。本番環境で必要な場合は、すべてのセッションではなく一部のセッションをサンプリングし、アーティファクトサービスに保持ポリシー（retention policy）を設定してください。ADK はこれらを自動的に期限切れにしません。

!!! warning "`save_live_audio` は非推奨です"

    ADK は `save_live_audio=True` を `save_live_blob=True` に自動的に移行して警告を表示しますが、このシムは将来のリリースで削除されます。`save_live_blob` に更新してください。

### history_config

すでに会話履歴があるセッションに対して ADK が**新しい** Live API 接続を開く際、その履歴をサーバーに再生（リプレイ）します。その履歴にはモデル自身の過去のターンも含まれているため、それらに対して再度応答しないようサーバーに指示する必要があります。ADK がこれを自動的に処理します。送信する履歴があり、セッション再開ハンドルが使用されていない場合、接続前に `live_connect_config.history_config.initial_history_in_client_content = True` を設定します。

```python
from google.genai import types

# ADK がこれを自動的に設定します。反対の動作が必要な場合のみオーバーライドしてください。
run_config = RunConfig(
    history_config=types.HistoryConfig(
        initial_history_in_client_content=True,
    ),
)
```

**実際の実装上の意味：**

- **通常は何もしません。** ADK は値が設定されていない場合にのみ自動補完するため、`RunConfig` に明示的に指定した `history_config` が常に優先されます。
- **再接続時は履歴の送信をスキップします。** ADK がセッション再開ハンドルを使って再接続する場合、サーバーはすでにそのセッションの状態を保持しているため、ADK は履歴を送信せず、`history_config` にも触れません。
- **設定を誤った場合の症状**: 履歴をシードする際に `initial_history_in_client_content=False` を設定すると、モデルが*リプレイされた*ターンに対して応答してしまい、接続開始時に重複した応答が一斉に生成されます。

### custom_metadata

`custom_metadata` は、呼び出し内のすべての `Event` に任意の JSON シリアライズ可能な辞書を添付します。[ランタイム設定](../runtime/runconfig.md#configure-runtime-limits-and-debugging) で説明されているとおり、ライブセッションでも同様に動作します。

```python
run_config = RunConfig(
    response_modalities=["AUDIO"],
    custom_metadata={"user_tier": "premium", "session_type": "support"},
)
```

ライブ特有の違いはスコープです。1 回の `run_live()` 呼び出しが 1 つの呼び出し（invocation）となるため、メタデータは単一のターンではなく、ストリーミングセッション全体のすべてのイベントに付与されます。`event.custom_metadata` で読み取ることができます。

!!! warning "`custom_metadata` に機密データを含めないでください"

    このメタデータを含むすべてのイベントはセッションサービスに保存されます。個人情報（PII）、認証情報、その他の機密情報は除外し、代替手段がない場合は暗号化してください。

### その他のライブ関連フィールド

`RunConfig` には、`run_live()` パスでのみ有効な追加フィールドがいくつかあります。ADK はこれらをライブ接続にそのまま渡すため、正確な動作は ADK ではなく Live API によって定義されます。

| フィールド | 型 | 動作 |
|---|---|---|
| `explicit_vad_signal` | `bool` | モデルに明示的な音声活動シグナルを出力するよう要求する。ADK はコンテンツからターン境界を推測する代わりに、`event.voice_activity` として表面化させる |
| `translation_config` | `types.TranslationConfig` | リアルタイムの音声間翻訳を有効化する。`target_language_code`（BCP-47）および `echo_target_language` を受け取る。**`gemini-3.5-live-translate-preview` などの翻訳モデルでのみサポート**（[サポート対象モデル](models.md#live-models) の一般モデルでは非対応） |
| `avatar_config` | `types.AvatarConfig` | エージェントをアニメーションアバターとしてレンダリングする。`avatar_name`（組み込みアバター）または `customized_avatar`、および `audio_bitrate_bps` / `video_bitrate_bps` を受け取る |

```python
from google.genai import types

run_config = RunConfig(
    response_modalities=["AUDIO"],
    explicit_vad_signal=True,
)
```

ライブ専用ではありませんが、ライブセッションでよく役立つフィールドがもう 1 つあります。

- **`model_input_context`**（`list[types.Content]`）：現在の呼び出しに対してのみ LLM リクエストに注入される一時的なコンテキスト。`Runner` はこれをセッションに保存しないため、会話履歴を汚染することなくターンごとのグラウンディング情報（ユーザーが開いたばかりのドキュメント、閲覧中のページなど）を安全に提供できます。

### 構成的関数呼び出し（support_cfc）

構成的関数呼び出し（Compositional Function Calling: CFC）は `run_async()` / SSE の機能であり、ライブの機能ではありません。現在のライブモデルには CFC の要件を満たすものがないため、理論上のみ適用可能です。`support_cfc` は SSE パス用として残し、ライブセッションでは標準の関数呼び出しを使用してください（[ツール](tools.md) を参照）。パラメータ自体については、[ランタイム設定](../runtime/runconfig.md) を参照してください。

## 音声の文字起こし（Audio transcription）

Live API は会話の両側を文字起こしするため、個別の Speech-to-Text サービスを導入することなく、字幕の表示、会話の記録、アクセシビリティ対応が可能になります。**ADK では、入力（ユーザーの音声）と出力（モデルの音声）の両方で文字起こしがデフォルトで有効になっています。** 特定の方向を無効にするには、対応するフィールドを `None` に設定します。

```python
from google.genai import types
from google.adk.agents.run_config import RunConfig

# デフォルトで有効。両方を AudioTranscriptionConfig() に設定するのと同等です。
run_config = RunConfig(response_modalities=["AUDIO"])

# ユーザー入力の文字起こしをオフにし、モデル出力の文字起こしを維持
run_config = RunConfig(
    response_modalities=["AUDIO"],
    input_audio_transcription=None,
)
```

文字起こしは `event.content` とは別に、`event.input_transcription` および `event.output_transcription` に `types.Transcription` オブジェクトとして届きます。フラグメント単位でストリーミングされ、`.text` は最新のフラグメントを保持し、`.finished` はターンの最後のフラグメントであることを示します。フラグメントを連結して完全な文字起こしを構築します。

```python
async for event in runner.run_live(...):
    if event.input_transcription and event.input_transcription.text:
        update_caption(
            event.input_transcription.text,
            is_user=True,
            is_final=event.input_transcription.finished,
        )
    if event.output_transcription and event.output_transcription.text:
        update_caption(
            event.output_transcription.text,
            is_user=False,
            is_final=event.output_transcription.finished,
        )
```

イベント構造については、[文字起こしイベント](events.md#transcription) を参照してください。

!!! note "マルチエージェントセッションでは常に文字起こしが有効になります"

    ルートエージェントに `sub_agents` がある場合、`run_live()` は `None` に設定されていても入力と出力の両方の文字起こしを有効にします。エージェントの引き継ぎ（転送）では次のエージェントに会話コンテキストを渡すためにテキスト文字起こしが必要となるため、無効化できません（[`runners.py`](https://github.com/google/adk-python/blob/main/src/google/adk/runners.py)）。

## 音声と言語（Voice and language）

モデルの声と言語を選択するには `speech_config` を設定します。設定場所は 2 つあります。

- **エージェントレベル**: `speech_config` を持つ `Gemini` インスタンスを渡します。マルチエージェントワークフローで各エージェントに独自の声を持たせたい場合に使用します。
- **セッションレベル**: `RunConfig.speech_config` を設定します。セッション全体で 1 つの声を使用したい場合に使用します。

両方が設定されている場合、**エージェントレベルの声が優先されます**。どちらも設定されていない場合、Live API がデフォルトの声を選択します。

```python
from google.genai import types
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.agents.run_config import RunConfig

# エージェントレベルの声（RunConfig より優先）
agent = Agent(
    model=Gemini(
        model="gemini-live-2.5-flash-native-audio",
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Puck")
            ),
            language_code="en-US",
        ),
    ),
    instruction="You are a helpful assistant.",
)

# セッションレベルのデフォルトの声（独自の声を持たないエージェントが使用）
run_config = RunConfig(
    response_modalities=["AUDIO"],
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore")
        ),
    ),
)
```

`voice_name` で組み込みの声を選択します。[ライブモデル](models.md#live-models) は 8 種類の声（Puck、Charon、Kore、Fenrir、Aoede、Leda、Orus、Zephyr）および拡張された [Text-to-Speech 音声リスト](https://cloud.google.com/text-to-speech/docs/voices) をサポートしています。現在のリストとバックエンドごとの利用可能性については、[Gemini Live API 音声ドキュメント](https://ai.google.dev/gemini-api/docs/live-api/capabilities#change-voice-and-language) を確認してください。サポートされていない声は接続時にエラーを返します。

`language_code`（例: `en-US`、`ja-JP`、`ko-KR`）は言語とアクセントを設定します。ライブモデルは会話から言語を自動推測することが多く、この設定を無視する場合があります。

## 音声活動検出（VAD）

VAD は、ユーザーが話し始めた時と話し終えた時を検出し、割り込みの処理を含めてモデルが自然にターン交代できるようにします。すべての [ライブモデル](models.md#live-models) で**デフォルトでオン**になっており、ほとんどのアプリケーションで設定は不要です。

Push-to-Talk、クライアント側の VAD、またはユーザーが発話終了をシグナルする UX など、アプリケーション自身がターン境界を決定する場合は、自動 VAD を無効にしてください。無効にした場合は、[`send_activity_start()` / `send_activity_end()`](sessions.md#liverequestqueue) を使用して手動で `ActivityStart`/`ActivityEnd` シグナルを送信する必要があり、クライアントは独自のターンシグナルをサーバー上のこれらの呼び出しに変換する必要があります。

```python
from google.genai import types
from google.adk.agents.run_config import RunConfig

run_config = RunConfig(
    response_modalities=["AUDIO"],
    realtime_input_config=types.RealtimeInputConfig(
        automatic_activity_detection=types.AutomaticActivityDetection(disabled=True)
    ),
)
```

独自の VAD を実行するクライアントは、それらのシグナルをサーバーに送信し、サーバーは `send_activity_start()` / `send_activity_end()` でそれらを転送します。[クライアントの接続](custom-server.md#connect-a-client) を参照してください。

## プロアクティブおよび感情的な対話（Proactivity and affective dialog）

一部のライブモデルは、デフォルトでオフになっている 2 つの対話機能を提供しています。

- **プロアクティブな音声**（`proactivity`）：モデルが応答するタイミングを自ら判断し、指示されなくても提案を行ったり、関係のない入力を無視したりできる。
- **感情的な対話**（`enable_affective_dialog`）：モデルがユーザーの口調から感情を検出し、それに応じて応答を適応させることができる。

```python
from google.genai import types
from google.adk.agents.run_config import RunConfig

run_config = RunConfig(
    response_modalities=["AUDIO"],
    proactivity=types.ProactivityConfig(proactive_audio=True),
    enable_affective_dialog=True,
)
```

どちらの動作も確率的であり、応答の予測可能性が低下するため、フォーマルな場面や高い精度が要求されるコンテキスト、およびデバッグ中はオフにしておくことをお勧めします。

これらの設定は `gemini-live-2.5-flash-native-audio` に適用されます。一部のライブモデルはこれらの動作が組み込まれており両方の設定を無視するため、設定する必要はありません。[サポート対象モデル](models.md#live-models) を参照してください。
