# ランタイム設定 (Runtime Configuration)

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span><span class="lst-kotlin">Kotlin v0.1.0</span>
</div>

`RunConfig` は、streaming mode、speech setting、LLM call limit、live agent option など、
エージェントのランタイム動作を制御します。デフォルト動作を上書きするには、
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

Long-running session では、どれだけの history を load するか、context window を圧縮するかを
制御できます。

- `get_session_config`: session を load するときに取得する event を制限します。 invocation ごとに
  event history 全体を load しないよう、`num_recent_events` または `after_timestamp` を使います。
- `context_window_compression`: LLM input の context window compression を有効にします。
  session が model context limit に近づく場合に便利です。
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

## ストリーミングの有効化

エージェントがレスポンスを配信する方法を制御するには、`streaming_mode` パラメータを
設定します。

- **`StreamingMode.NONE`** (デフォルト): runner は turn ごとに 1 つの完全なレスポンスを
  返します。CLI tool、batch processing、synchronous workflow に適しています。
- **`StreamingMode.SSE`**: Server-Sent Events streaming です。LLM が生成している間、
  runner が partial event を yield し、typewriter-style UI や real-time chat display を
  実現できます。
- **`StreamingMode.BIDI`**: bidirectional streaming 用に予約されていますが、標準の
  `run_async()` path では **使用されません**。Bidirectional streaming には
  `runner.run_live()` を使ってください。

`StreamingMode.SSE` とともに `support_cfc=True` を設定すると、Compositional Function Calling(CFC)
を有効にできます。CFC により、model は function call を動的に構成して実行でき、内部では
Live API を使用します。

!!! example "Experimental"
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
        supportCfc: true,
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

Voice-enabled agent では、speech synthesis、audio transcription、response modality を
設定します。

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

ライブ（`run_live()`）エージェントセッションには、`realtime_input_config`、`session_resumption`、`save_live_blob`、`tool_thread_pool_config`、`proactivity`、`enable_affective_dialog` などのリアルタイムパラメータが追加されます。これらはモデルごとのサポートと例とともに、ライブドキュメントの1か所にまとめられています。

- **[ライブエージェントの設定](../live/configuration.md)** — ライブエージェント用の完全な `RunConfig` リファレンス。
- **[セッション](../live/sessions.md#session-resumption)** — セッションの再開と再接続。
- **[設定: プロアクティブおよび感情的な対話](../live/configuration.md#proactivity-and-affective-dialog)** — ネイティブオーディオ会話機能とそれをサポートするモデル。

`tool_thread_pool_config` 設定は例外です。これは Live API の関心事というよりもランタイムの関心事であるため、ここに残されています。イベントループがユーザーの中断に応答し続けられるよう、ツール実行をバックグラウンドスレッドプールで実行します。

すべてのパラメータがすべての言語で利用できるわけではありません。言語別の詳細は [API reference](#api-reference) を参照してください。

=== "Python"

    ```python
    from google.adk.agents.run_config import RunConfig, ToolThreadPoolConfig

    config = RunConfig(
        save_live_blob=True,
        tool_thread_pool_config=ToolThreadPoolConfig(max_workers=8),
    )
    ```

    !!! note "Thread pool and the GIL"
        Thread pool は blocking I/O と、GIL を release する C extension(例:
        `time.sleep()`、network call、numpy)に役立ちます。純粋な Python CPU-bound code には
        役立ちません。GIL が Python bytecode の真の並列実行を妨げるためです。

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

## ランタイム制限とデバッグの設定

次のパラメータで runtime guardrail と debugging を制御します。

- `max_llm_calls`: run ごとの LLM call 合計数を制限します(デフォルト: 500)。0 または負の値は
  無制限の呼び出しを意味しますが、本番環境では推奨されません。使用する言語の最大整数(Python では
  `sys.maxsize`、Kotlin では `Int.MAX_VALUE`)を渡すとエラーになります。
- `save_input_blobs_as_artifacts`: `True` の場合、input blob(例: uploaded file)を debugging と
  auditing 用の run artifact として保存します。
- `custom_metadata`: invocation に添付される任意 metadata の `dict[str, Any]` です。tracing や
  logging に便利です。

## API reference

field、type、default の完全な一覧は、各言語の API reference を参照してください。

- [Python API reference](../api-reference/python/google-adk.html#google.adk.agents.RunConfig)
- [TypeScript API reference](../api-reference/typescript/interfaces/RunConfig.html)
- [Go API reference](https://pkg.go.dev/google.golang.org/adk/v2/agent#RunConfig)
- [Java API reference](../api-reference/java/com/google/adk/agents/RunConfig.html)
