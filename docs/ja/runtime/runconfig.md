# ランタイム設定 (Runtime Configuration)

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

`RunConfig`は、ADKにおけるエージェントのランタイムの動作とオプションを定義します。これにより、音声およびストリーミングの設定、関数呼び出し、アーティファクトの保存、LLM呼び出しの制限などを制御します。

エージェントの実行を構築する際、`RunConfig`を渡すことで、エージェントがモデルと対話し、音声を処理し、レスポンスをストリーミングする方法をカスタマイズできます。デフォルトでは、ストリーミングは有効になっておらず、入力はアーティファクトとして保持されません。これらのデフォルト値を上書きするには`RunConfig`を使用してください。

## クラス定義

`RunConfig`クラスは、エージェントのランタイム動作に関する設定パラメータを保持します。

-   Python ADKは、このバリデーションにPydanticを使用します。
-   Go ADKは、デフォルトで可変な構造体（mutable struct）です。
-   Java ADKは、通常、不変のデータクラス（immutable data class）を使用します。


=== "Python"

    ```python
    class RunConfig(BaseModel):
        """Configs for runtime behavior of agents."""

        model_config = ConfigDict(
            extra='forbid',
        )

        speech_config: Optional[types.SpeechConfig] = None
        response_modalities: Optional[list[str]] = None
        save_input_blobs_as_artifacts: bool = False
        support_cfc: bool = False
        streaming_mode: StreamingMode = StreamingMode.NONE
        output_audio_transcription: Optional[types.AudioTranscriptionConfig] = None
        max_llm_calls: int = 500
    ```

=== "Go"

    ```go
    type StreamingMode string

    const (
    	StreamingModeNone StreamingMode = "none"
    	StreamingModeSSE  StreamingMode = "sse"
    )

    // RunConfig controls runtime behavior.
    type RunConfig struct {
    	// Streaming mode, None or StreamingMode.SSE.
    	StreamingMode StreamingMode
    	// Whether or not to save the input blobs as artifacts
    	SaveInputBlobsAsArtifacts bool
    }
    ```

=== "Java"

    ```java
    public abstract class RunConfig {

      public enum StreamingMode {
        NONE,
        SSE,
        BIDI
      }

      public abstract @Nullable SpeechConfig speechConfig();

      public abstract ImmutableList<Modality> responseModalities();

      public abstract boolean saveInputBlobsAsArtifacts();

      public abstract @Nullable AudioTranscriptionConfig outputAudioTranscription();

      public abstract int maxLlmCalls();

      // ...
    }
    ```

## ランタイムパラメータ

| パラメータ                        | Python型                                     | Go型            | Java型                                                | デフォルト (Py / Go / Java )            | 説明                                                                                                                                |
| :-------------------------------- | :------------------------------------------- |:----------------|:------------------------------------------------------|:----------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------|
| `speech_config`                   | `Optional[types.SpeechConfig]`               | N/A             | `SpeechConfig` (`@Nullable`経由でnullable)           | `None` / N/A / `null`                   | `SpeechConfig`型を使用して、音声合成（ボイス、言語）を設定します。                                                                 |
| `response_modalities`             | `Optional[list[str]]`                        | N/A             | `ImmutableList<Modality>`                             | `None` / N/A / 空の`ImmutableList`      | 望ましい出力モダリティのリストです（例: Python: `["TEXT", "AUDIO"]`; Java: 構造化された`Modality`オブジェクトを使用）。              |
| `save_input_blobs_as_artifacts`   | `bool`                                       | `bool`          | `boolean`                                             | `False` / `false` / `false`             | `true`の場合、デバッグ/監査のために、入力blob（例: アップロードされたファイル）を実行アーティファクトとして保存します。            |
| `streaming_mode`                  | `StreamingMode`                              | `StreamingMode` | `StreamingMode`                                       | `StreamingMode.NONE` / `agent.StreamingModeNone` / `StreamingMode.NONE` | ストリーミングの動作を設定します: `NONE`(デフォルト)、`SSE`(サーバーセントイベント)、または`BIDI`(双方向) (**Python/Java**)。          |
| `output_audio_transcription`      | `Optional[types.AudioTranscriptionConfig]`   | N/A             | `AudioTranscriptionConfig` (`@Nullable`経由でnullable) | `None` / N/A / `null`                   | `AudioTranscriptionConfig`型を使用して、生成された音声出力の文字起こしを設定します。                                           |
| `max_llm_calls`                   | `int`                                        | N/A             | `int`                                                 | `500` / N/A / `500`                     | 実行ごとの合計LLM呼び出しを制限します。`0`以下の値は無制限（警告表示）を意味し、`sys.maxsize`は`ValueError`を発生させます。         |
| `support_cfc`                     | `bool`                                       | N/A             | `bool`                                                | `False` / N/A / `false`                 | **Python:** 構成的関数呼び出し(Compositional Function Calling)を有効にします。`streaming_mode=SSE`が必要で、LIVE APIを使用します。**実験的機能。** |

### `speech_config`

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

!!! Note
    `SpeechConfig`のインターフェースや定義は、言語に関係なく同じです。

音声機能を備えたライブエージェントのための音声設定です。
`SpeechConfig`クラスは以下の構造を持ちます:

```python
class SpeechConfig(_common.BaseModel):
    """The speech generation configuration."""

    voice_config: Optional[VoiceConfig] = Field(
        default=None,
        description="""The configuration for the speaker to use.""",
    )
    language_code: Optional[str] = Field(
        default=None,
        description="""Language code (ISO 639. e.g. en-US) for the speech synthesization.
        Only available for Live API.""",
    )
```

`voice_config`パラメータは`VoiceConfig`クラスを使用します:

```python
class VoiceConfig(_common.BaseModel):
    """The configuration for the voice to use."""

    prebuilt_voice_config: Optional[PrebuiltVoiceConfig] = Field(
        default=None,
        description="""The configuration for the speaker to use.""",
    )
```

そして`PrebuiltVoiceConfig`は以下の構造を持ちます:

```python
class PrebuiltVoiceConfig(_common.BaseModel):
    """The configuration for the prebuilt speaker to use."""

    voice_name: Optional[str] = Field(
        default=None,
        description="""The name of the prebuilt voice to use.""",
    )
```

これらのネストされた設定クラスにより、以下を指定できます:

* `voice_config`: 使用する事前ビルド済みのボイスの名前（`PrebuiltVoiceConfig`内）
* `language_code`: 音声合成のためのISO 639言語コード（例: "en-US"）

音声対応エージェントを実装する際には、これらのパラメータを設定して、エージェントが話すときの音声を制御します。

### `response_modalities`

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

エージェントの出力モダリティを定義します。設定されていない場合、デフォルトはAUDIOになります。
レスポンスモダリティは、エージェントがさまざまなチャネル（例: テキスト、音声）を通じてユーザーとどのように通信するかを決定します。

### `save_input_blobs_as_artifacts`

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

有効にすると、入力blobはエージェントの実行中にアーティファクトとして保存されます。
これは、開発者がエージェントによって受信された正確なデータを確認できるため、デバッグや監査の目的で役立ちます。

### `support_cfc`

<div class="language-support-tag" title="この機能は実験的なプレビューリリースです。">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-preview">実験的</span>
</div>

構成的関数呼び出し（Compositional Function Calling, CFC）のサポートを有効にします。StreamingMode.SSEを使用している場合にのみ適用されます。有効にすると、CFC機能はLIVE APIでのみサポートされているため、そのAPIが呼び出されます。

!!! example "実験的リリース"

    `support_cfc`機能は実験的なものであり、将来のリリースでAPIや動作が変更される可能性があります。

### `streaming_mode`

<div class="language-support-tag" title="この機能は実験的なプレビューリリースです。">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-go">Go v0.1.0</span>
</div>

エージェントのストリーミング動作を設定します。指定可能な値:

* `StreamingMode.NONE`: ストリーミングなし。レスポンスは完全な単位で配信される
* `StreamingMode.SSE`: サーバーセントイベント（Server-Sent Events）ストリーミング。サーバーからクライアントへの一方向ストリーミング
* `StreamingMode.BIDI`: 双方向（Bidirectional）ストリーミング。両方向での同時通信

ストリーミングモードは、パフォーマンスとユーザーエクスペリエンスの両方に影響します。SSEストリーミングにより、ユーザーは生成中の部分的なレスポンスを見ることができ、BIDIストリーミングはリアルタイムの対話型エクスペリエンスを可能にします。

### `output_audio_transcription`

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

音声応答機能を備えたライブエージェントからの音声出力を文字起こしするための設定です。これにより、アクセシビリティ、記録保持、およびマルチモーダルアプリケーションのために、音声応答の自動文字起こしが可能になります。

### `max_llm_calls`

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

特定のエージェント実行に対するLLM呼び出しの総数に制限を設定します。

* 0より大きく `sys.maxsize` 未満の値: LLM呼び出しに上限を強制
* 0以下の値: 無制限のLLM呼び出しを許可 *(本番環境では非推奨)*

このパラメータは、過剰なAPI使用と潜在的なプロセスの暴走を防ぎます。LLM呼び出しはコストが発生し、リソースを消費することが多いため、適切な制限を設定することが重要です。

## バリデーションルール

`RunConfig`クラスは、エージェントが適切に動作することを保証するために、そのパラメータを検証します。Python ADKは自動的な型検証のために`Pydantic`を使用しますが、Java ADKは静的型付けに依存し、`RunConfig`の構築時に明示的なチェックを含む場合があります。
特に`max_llm_calls`パラメータについては:

1. 極端に大きな値（Pythonの`sys.maxsize`やJavaの`Integer.MAX_VALUE`など）は、問題を避けるために通常許可されません。

2. 0以下の値は、通常、無制限のLLMインタラクションに関する警告をトリガーします。

## 使用例

### 基本的なランタイム設定

=== "Python"

    ```python
    from google.genai.adk import RunConfig, StreamingMode

    config = RunConfig(
        streaming_mode=StreamingMode.NONE,
        max_llm_calls=100
    )
    ```

=== "Go"

    ```go
    import "google.golang.org/adk/agent"

    config := agent.RunConfig{
        StreamingMode: agent.StreamingModeNone,
    }
    ```

=== "Java"

    ```java
    import com.google.adk.agents.RunConfig;
    import com.google.adk.agents.RunConfig.StreamingMode;

    RunConfig config = RunConfig.builder()
            .setStreamingMode(StreamingMode.NONE)
            .setMaxLlmCalls(100)
            .build();
    ```

この設定は、100回のLLM呼び出し制限を持つ非ストリーミングエージェントを作成します。これは、完全なレスポンスが望ましい単純なタスク指向のエージェントに適しています。

### ストリーミングの有効化

=== "Python"

    ```python
    from google.genai.adk import RunConfig, StreamingMode

    config = RunConfig(
        streaming_mode=StreamingMode.SSE,
        max_llm_calls=200
    )
    ```

=== "Go"

    ```go
    import "google.golang.org/adk/agent"

    config := agent.RunConfig{
        StreamingMode: agent.StreamingModeSSE,
    }
    ```

=== "Java"

    ```java
    import com.google.adk.agents.RunConfig;
    import com.google.adk.agents.RunConfig.StreamingMode;

    RunConfig config = RunConfig.builder()
        .setStreamingMode(StreamingMode.SSE)
        .setMaxLlmCalls(200)
        .build();
    ```

SSEストリーミングを使用すると、ユーザーはレスポンスが生成されるのを見ることができるため、チャットボットやアシスタントでより応答性の高い感覚を提供できます。

### 音声サポートの有効化

=== "Python"

    ```python
    from google.genai.adk import RunConfig, StreamingMode
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
        response_modalities=["AUDIO", "TEXT"],
        save_input_blobs_as_artifacts=True,
        support_cfc=True,
        streaming_mode=StreamingMode.SSE,
        max_llm_calls=1000,
    )
    ```

=== "Java"

    ```java
    import com.google.adk.agents.RunConfig;
    import com.google.adk.agents.RunConfig.StreamingMode;
    import com.google.common.collect.ImmutableList;
    import com.google.genai.types.Content;
    import com.google.genai.types.Modality;
    import com.google.genai.types.Part;
    import com.google.genai.types.PrebuiltVoiceConfig;
    import com.google.genai.types.SpeechConfig;
    import com.google.genai.types.VoiceConfig;

    RunConfig runConfig =
        RunConfig.builder()
            .setStreamingMode(StreamingMode.SSE)
            .setMaxLlmCalls(1000)
            .setSaveInputBlobsAsArtifacts(true)
            .setResponseModalities(ImmutableList.of(new Modality("AUDIO"), new Modality("TEXT")))
            .setSpeechConfig(
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

この包括的な例では、以下の機能を備えたエージェントを設定します:

* "Kore"ボイス（米国英語）を使用した音声機能
* 音声とテキストの両方の出力モダリティ
* 入力blobのアーティファクト保存（デバッグに便利）
* 応答性の高い対話のためのSSEストリーミング
* 1000回のLLM呼び出し制限

### 実験的なCFCサポートの有効化

<div class="language-support-tag" title="この機能は実験的なプレビューリリースです。">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-preview">実験的</span>
</div>

    ```python
        from google.genai.adk import RunConfig, StreamingMode

        config = RunConfig(
            streaming_mode=StreamingMode.SSE,
            support_cfc=True,
            max_llm_calls=150
        )
    ```

構成的関数呼び出しを有効にすると、モデルの出力に基づいて動的に関数を実行できるエージェントが作成され、複雑なワークフローを必要とするアプリケーションに強力です。