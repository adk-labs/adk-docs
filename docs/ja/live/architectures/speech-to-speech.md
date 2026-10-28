# Speech-to-speech アーキテクチャ

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

Speech-to-speech アーキテクチャでは、単一のマルチモーダルモデルが、入力と出力の間で音声をテキストに変換することなく、永続的な [Gemini Live API](https://ai.google.dev/gemini-api/docs/live-api) 接続を介して受信音声を処理し、推論やツール呼び出しを実行して、音声出力を直接生成します。

連結された STT-LLM-TTS パイプラインとの比較については、[音声アーキテクチャの選択](index.md)をご覧ください。

## Speech-to-speech エージェントの設定

サポートされている[ネイティブ音声 Live モデル](../models.md#live-models)をエージェントに渡します。

=== "Python"

    ```python
    import os
    from google.adk.agents import Agent

    root_agent = Agent(
        name="voice_assistant",
        model=os.getenv("DEMO_AGENT_MODEL", "gemini-live-2.5-flash-native-audio"),
        instruction="You are a helpful voice assistant.",
        tools=[...],
    )
    ```

=== "Java"

    ```java
    import com.google.adk.agents.LlmAgent;

    LlmAgent rootAgent =
        LlmAgent.builder()
            .name("voice_assistant")
            .model("gemini-live-2.5-flash-native-audio")
            .instruction("You are a helpful voice assistant.")
            .build();
    ```

`adk web` でエージェントを実行するか、[`Runner.run_live()`](../sessions.md#the-run_live-loop) に渡します。

## Speech-to-speech 固有の機能

以下の機能は、ネイティブ音声モデルに固有のものです。

- **ライブ動画と画像入力**: 音声とともにライブカメラや画面のフレームをストリーミングし、ユーザーが提示しているものをエージェントが視覚的に認識できるようにします。[音声と動画](../audio-video.md#images-and-video)をご覧ください。
- **感情対話（Affective dialog）とプロアクティブ音声（Proactive audio）**: サポートされているネイティブ音声モデルは、ユーザーの感情表現に合わせて話すトーンを調整したり、いつ話し、いつ黙っているかを判断したりできます。[プロアクティブ機能と感情対話](../configuration.md#proactivity-and-affective-dialog)をご覧ください。
- **ステートフルなセッション再開とコンテキスト圧縮**: Live API はステートフルな WebSocket セッション内で会話状態を保持するため、ADK は接続タイムアウトをまたぐ自動[セッション再開](../sessions.md#session-resumption)や、長時間実行されるセッション向けの[コンテキストウィンドウ圧縮](../sessions.md#context-window-compression)をサポートしています。
- **セッションレベルの音声および VAD 制御**: [`RunConfig`](../configuration.md) またはモデルインスタンスを通じて、セッションレベルで音声の選択や自動音声アクティビティ検出（VAD）を設定できます。

## 考慮事項と制限事項

- **固定されたモデル選択**: Speech-to-speech には、Gemini Live API をサポートするモデル（[サポートされているモデル](../models.md#live-models)）が必要です。ライブ音声セッションで標準の Gemini テキストモデルやサードパーティの LLM を使用する場合は、[カスケードアーキテクチャ](cascade.md)を使用してください。
- **音声のみの出力**: ネイティブ音声モデルは音声のみを出力し、`Runner.run_async()` では実行できません。会話のテキストが必要な場合は、[音声文字起こし](../configuration.md#audio-transcription)を読み取ってください。
- **ガードレールは音声と並行して文字起こしを評価する**: モデルは中間のテキストステージを介さずに直接音声を生成するため、[会話検証コールバック](../guardrails.md#conversation-validation)は合成前にテキストをインターセプトするのではなく、入力および出力の文字起こしを検査します。音声が生成される前にテキストのフィルタリングや墨消し（リダクション）を行う必要がある場合は、[カスケード](cascade.md#custom-speech-transforms)を使用してください。
