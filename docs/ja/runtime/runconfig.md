# ランタイム設定 (Runtime Configuration)

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span><span class="lst-kotlin">Kotlin v0.1.0</span>
</div>

`RunConfig` は、ストリーミングモード、音声設定、LLM 呼び出し回数の上限、ライブエージェントのオプションなど、
エージェントのランタイム動作を制御します。デフォルトの動作を上書きするには、
`RunConfig` を `runner.run_async()` または `runner.run_live()` に渡します。

=== "Python"

    ```python
    from google.adk.agents.run_config import RunConfig, StreamingMode

    config = RunConfig(
        streaming_mode=StreamingMode.SSE,
        max_llm_calls=200,
    )

    async for event in runner.run_async(
        ...,
        run_config=config,
    ):
        ...
    ```

=== "TypeScript"

    ```typescript
    import { RunConfig, StreamingMode } from '@google/adk';

    const config: RunConfig = {
      streamingMode: StreamingMode.SSE,
      maxLlmCalls: 200,
    };
    ```

=== "Go"

    ```go
    import "google.golang.org/adk/v2/agent"

    config := agent.RunConfig{
        StreamingMode: agent.StreamingModeSSE,
    }
    ```

=== "Java"

    ```java
    import com.google.adk.agents.RunConfig;
    import com.google.adk.agents.RunConfig.StreamingMode;

    RunConfig config = RunConfig.builder()
        .streamingMode(StreamingMode.SSE)
        .maxLlmCalls(200)
        .build();
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/runtime/RunConfigExample.kt:basic_usage"
    ```

## セッションとコンテキストの管理

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span>
</div>

長時間実行されるセッションでは、読み込む履歴の量やコンテキストウィンドウを圧縮するかどうかを制御できます。

- `get_session_config`: セッションの読み込み時に取得するイベントを制限します。呼び出し（invocation）のたびにイベント履歴全体を読み込まないよう、`num_recent_events` または `after_timestamp` を使用します。これらのフィルターは保存されたイベントを削除することなく、読み込まれるビューのみを制限します。新しいイベントは保存された履歴に追加され、読み込まれたビューから除外された過去のイベントもそのまま保持されます。
- `context_window_compression`: LLM 入力に対するコンテキストウィンドウ圧縮を有効にします。セッションがモデルのコンテキスト上限に近づく場合に便利です。
- `model_input_context`: 今回の呼び出しにのみ LLM リクエストに追加される `types.Content` のリスト。ランナーはこれをセッションに永続化しないため、会話履歴を変更せずにターンごとのコンテキストを提供できます。
- `include_thoughts_from_other_agents`: 他のエージェントの思考（thought）パートを LLM コンテキストに含めるかどうかを制御します。デフォルトでは無効です。

=== "Python"

    ```python
    from google.adk.agents.run_config import RunConfig
    from google.adk.sessions.base_session_service import GetSessionConfig

    config = RunConfig(
        get_session_config=GetSessionConfig(num_recent_events=50),
    )
    ```

## テキスト応答オプション { #enable-streaming }

エージェントがテキストモードで応答する方法（生成されるにつれて順次配信するか、1 つの完全なレスポンスとして配信するか）を、以下で説明する `streaming_mode` パラメータで制御できます:

- **`StreamingMode.NONE`**（デフォルト）: ランナーはターンごとに 1 つの完全なレスポンスを返します。CLI ツール、バッチ処理、同期ワークフローに適しています。
- **`StreamingMode.SSE`**: Server-Sent Events（SSE）ストリーミングです。LLM が生成している間にランナーが部分的なイベント（partial event）を順次返すため、タイプライター風の UI やリアルタイムのチャット表示を実現できます。

`streaming_mode` パラメータには、音声の入出力を含むデータの双方向ストリーミングを有効にするもう 1 つの設定（`StreamingMode.BIDI`）もあります。この機能には、シンプルなエージェント以上の追加設定が必要です。詳細については、[ライブおよび音声エージェント](../live/index.md)を参照してください。

`StreamingMode.SSE` と併せて `support_cfc=True` を設定すると、Compositional Function Calling（CFC）を有効にできます。CFC により、モデルは関数呼び出し（Function Calling）を動的に構成して実行でき、内部では Live API を使用します。

!!! example "実験的機能（Experimental）"
    CFC サポートは実験的であり、将来のリリースで API や動作が変更される可能性があります。

=== "Python"

    ```python
    from google.adk.agents.run_config import RunConfig, StreamingMode

    config = RunConfig(
        streaming_mode=StreamingMode.SSE,
        support_cfc=True,
        max_llm_calls=150,
    )
    ```

=== "TypeScript"

    ```typescript
    import { RunConfig, StreamingMode } from '@google/adk';

    const config: RunConfig = {
        streamingMode: StreamingMode.SSE,
        maxLlmCalls: 150,
    };
    ```

=== "Go"

    ```go
    import "google.golang.org/adk/v2/agent"

    config := agent.RunConfig{
        StreamingMode: agent.StreamingModeSSE,
    }
    ```

=== "Java"

    ```java
    import com.google.adk.agents.RunConfig;
    import com.google.adk.agents.RunConfig.StreamingMode;

    RunConfig config = RunConfig.builder()
        .streamingMode(StreamingMode.SSE)
        .maxLlmCalls(150)
        .build();
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/runtime/RunConfigExample.kt:streaming_config"
    ```

## 音声と発話の設定

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span><span class="lst-java">Java</span>
</div>

音声対応エージェントでは、音声合成、音声の文字起こし（トランスクリプション）、およびレスポンスモダリティを設定します。

!!! tip "ライブエージェント"

    このセクションでは、言語共通のオーディオフィールドを扱います。文字起こしストリーミング、音声選択、音声活動検出（VAD）、プロアクティブ/感情的対話など、完全なライブ（`run_live()`）構成リファレンスについては、[ライブエージェントの設定](../live/configuration.md) を参照してください。

- `speech_config`: 音声出力の音声と言語を設定します（例: `en-US` と "Kore" 音声）。
- `response_modalities`: 出力形式を制御します。セッションは厳密に1つのモダリティのみを受け入れるため、音声エージェントには `["AUDIO"]` を、テキストのみのエージェントには `["TEXT"]` を使用します。音声とテキストの両方を取得するには、`["AUDIO"]` に設定し、出力音声の文字起こし（transcription）からテキストを読み取ります。
- `output_audio_transcription` / `input_audio_transcription`: モデルの音声出力とユーザーの音声入力の文字起こしを有効にします。Python ではどちらもデフォルトが `AudioTranscriptionConfig()` です。

=== "Python"

    ```python
    from google.adk.agents.run_config import RunConfig, StreamingMode
    from google.genai import types

    config = RunConfig(
        speech_config=types.SpeechConfig(
            language_code="en-US",
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name="Kore"
                )
            ),
        ),
        response_modalities=["AUDIO"],
        streaming_mode=StreamingMode.SSE,
        max_llm_calls=1000,
    )
    ```

=== "TypeScript"

    ```typescript
    import { RunConfig, StreamingMode } from '@google/adk';
    import { Modality } from '@google/genai';

    const config: RunConfig = {
        speechConfig: {
            languageCode: "en-US",
            voiceConfig: {
                prebuiltVoiceConfig: {
                    voiceName: "Kore"
                }
            },
        },
        responseModalities: [Modality.AUDIO],
        streamingMode: StreamingMode.SSE,
        maxLlmCalls: 1000,
    };
    ```

=== "Java"

    ```java
    import com.google.adk.agents.RunConfig;
    import com.google.adk.agents.RunConfig.StreamingMode;
    import com.google.common.collect.ImmutableList;
    import com.google.genai.types.Modality;
    import com.google.genai.types.PrebuiltVoiceConfig;
    import com.google.genai.types.SpeechConfig;
    import com.google.genai.types.VoiceConfig;

    RunConfig runConfig =
        RunConfig.builder()
            .streamingMode(StreamingMode.SSE)
            .maxLlmCalls(1000)
            .responseModalities(ImmutableList.of(new Modality(Modality.Known.AUDIO)))
            .speechConfig(
                SpeechConfig.builder()
                    .voiceConfig(
                        VoiceConfig.builder()
                            .prebuiltVoiceConfig(
                                PrebuiltVoiceConfig.builder().voiceName("Kore").build())
                            .build())
                    .languageCode("en-US")
                    .build())
            .build();
    ```

## ライブエージェントの設定

<div class="language-support-tag">
  <span class="lst-supported">ADK でサポート</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span><span class="lst-java">Java</span>
</div>

ADK エージェントは、対話型のエージェント体験を作成するために [ライブおよび音声エージェント](../live/index.md) をサポートできます。`runner.run_live()` メソッドを使用して、この機能をサポートするエージェントを設定します。
ライブエージェント（`run_live()`）セッションには、`realtime_input_config`、`session_resumption`、`save_live_blob`、`tool_thread_pool_config`、`proactivity`、`enable_affective_dialog` などのリアルタイム パラメータが追加されます。詳細については、ライブエージェントのドキュメントを参照してください:

- **[ライブエージェントの設定](../live/configuration.md)**: ライブエージェント用の完全な `RunConfig` リファレンス。
- **[セッション](../live/sessions.md#session-resumption)**: セッションの再開と再接続。
- **[設定: プロアクティブおよび感情的な対話](../live/configuration.md#proactivity-and-affective-dialog)**: ネイティブ オーディオ会話機能とそれをサポートするモデル。

`tool_thread_pool_config` 設定は例外です。これは Live API の関心事というよりもランタイムの関心事であるため、ここに残されています。イベントループがユーザーの中断に応答し続けられるよう、ツール実行をバックグラウンドスレッドプールで実行します。
すべてのパラメータがすべての言語で利用できるわけではありません。言語別の詳細は [API リファレンス](#api-reference) を参照してください。

=== "Python"

    ```python
    from google.adk.agents.run_config import RunConfig, ToolThreadPoolConfig

    config = RunConfig(
        save_live_blob=True,
        tool_thread_pool_config=ToolThreadPoolConfig(max_workers=8),
    )
    ```

    !!! note "スレッドプールと GIL"
        スレッドプールは、ブロッキング I/O や GIL を解放する C 拡張機能（例:
        `time.sleep()`、ネットワーク呼び出し、NumPy）に対して有効です。一方、GIL が
        Python バイトコードの真の並列実行を妨げるため、純粋な Python の CPU バウンドなコードには効果がありません。

=== "TypeScript"

    ```typescript
    import { RunConfig } from '@google/adk';

    const config: RunConfig = {
        enableAffectiveDialog: true,
        proactivity: {
            proactiveAudio: true,
        },
    };
    ```

=== "Java"

    ```java
    import com.google.adk.agents.RunConfig;
    import com.google.genai.types.AvatarConfig;

    RunConfig config = RunConfig.builder()
        .avatarConfig(
            AvatarConfig.builder()
                .avatarName("PREBUILT_AVATAR_ID")
                .build())
        .build();
    ```

## ランタイム制限とデバッグの設定

次のパラメータでランタイムのガードレールとデバッグを制御します。

- `max_llm_calls`: 1 回の実行あたりの LLM 呼び出しの合計数を制限します（デフォルト: 500）。0 または負の値を指定すると無制限になりますが、本番環境では推奨されません。使用する言語の最大整数値（Python では `sys.maxsize`、Kotlin では `Int.MAX_VALUE`）を渡すとエラーが発生します。
- `save_input_blobs_as_artifacts`: `True` の場合、入力 Blob（アップロードされたファイルなど）をデバッグおよび監査用の実行アーティファクトとして保存します。Python では `SaveFilesAsArtifactsPlugin` の使用が推奨されるため、非推奨（deprecated）となっています。Go では、`agent.RunConfig` の `SaveInputBlobsAsArtifacts` フィールドを `true` に設定します。この設定を有効にするには、ランナーにアーティファクトサービスが構成されている必要があります。
- `custom_metadata`: 呼び出し（invocation）に添付される任意のメタデータの `dict[str, Any]` です。トレーシングやロギングに便利です。
- `service_tier`: 実行時のモデル呼び出しに対するサービング容量を選択します。ADK Python のみに対応しており、Interactions API を使用する Gemini モデルにのみ適用されます。`ServiceTier.DEFERRED` は各モデル呼び出しをオフピーク容量で実行するようにキューに入れ、`StreamingMode.SSE` と組み合わせることはできません。詳細については、[遅延スケジューリング（Deferred scheduling）](/agents/models/google-gemini/deferred-schedule/)をご覧ください。

## API リファレンス {#api-reference}

フィールド、型、デフォルト値の完全な一覧については、各言語の API リファレンスを参照してください。

- [Python API リファレンス](../api-reference/python/google-adk.html#google.adk.agents.RunConfig)
- [TypeScript API リファレンス](../api-reference/typescript/interfaces/RunConfig.html)
- [Go API リファレンス](https://pkg.go.dev/google.golang.org/adk/v2/agent#RunConfig)
- [Java API リファレンス](../api-reference/java/com/google/adk/agents/RunConfig.html)
- [Kotlin API リファレンス](../api-reference/kotlin/google-adk-kotlin-core/com.google.adk.kt.agents/-run-config/index.html)
