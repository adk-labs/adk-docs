# ライブエージェント向けツール

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

ツールは、ADK の他のエージェントと同様にライブエージェントでも基本的に同じように機能します。エージェントに関数を渡し、モデルがそれらを呼び出します。ライブ接続下でもツールの記述方法は変わらないため、ツールの定義、ツールコンテキスト、コールバック、認証はすべて [カスタムツール](../tools-custom/index.md) に従います。

ライブ接続では、さらに 2 つの機能が追加されます。ADK は `run_live()` ループ内でツール呼び出しを自動的に実行するため、生の Live API が必要とするような関数呼び出しの配線コードを記述する必要がありません。また、ライブエージェントは*ストリーミングツール*を使用できます。これは実行を維持しながらエージェントに中間結果をプッシュする関数であり、ユーザーが再度質問しなくても、株価の変動や動画フレーム内の人物の出現などにエージェントが自発的に反応できます。

## 自動ツール実行

エージェントにツールを定義すると、ADK は `run_live()` ループ内で自動的にそれらを呼び出します。モデルの関数呼び出しを検出し、ツールを実行し（事前/事後コールバックを含め並行して）、レスポンスをフォーマットし、呼び出しとレスポンスの両方をイベントとして出力します。配線ではなく、関数のロジックのみを記述します。

```python
import os
from google.adk.agents import Agent
from google.adk.tools import google_search

agent = Agent(
    name="google_search_agent",
    model=os.getenv("DEMO_AGENT_MODEL", "gemini-live-2.5-flash-native-audio"),
    tools=[google_search],
    instruction="You are a helpful assistant that can search the web.",
)
```

ツールの動作はイベントストリームを通じて観察します。開発者が自らそれを駆動する必要はありません。

```python
async for event in runner.run_live(...):
    if event.get_function_calls():
        print(f"Model calling: {event.get_function_calls()[0].name}")
    if event.get_function_responses():
        print(f"Tool result: {event.get_function_responses()[0].response}")
```

## エージェントの応答性の維持

チャットウィンドウではユーザーはスピナーを見るため低速なツールでも耐えられますが、リアルタイムの音声会話ではそうはいきません。エージェントが 10 秒かかる API を呼び出して沈黙してしまうと、ユーザーは接続が切れたと思い込みます。そのため、実行中に会話をブロックしないツールが必要です。ADK は、高速なケース向けの通常のブロッキング実行に加えて、2 つの方法を提供しています。

| 状況 | 使用するもの | 方法 |
|---|---|---|
| 1 秒未満で返る高速なツール | **ブロッキング**（デフォルト） | 通常の 1 回 `return` するツール |
| ユーザーに話す内容がない長い待機時間 | **[ノンブロッキングツール](#non-blocking-tools)** | ツールに `response_scheduling` を設定 |
| ユーザーに実況・進捗を伝える価値がある長い待機時間 | **[ストリーミングツール](#streaming-tools)** | 非同期ジェネレータから進捗を `yield` |

## ノンブロッキングツール

大規模な分析クエリ、一括エクスポート、メディア生成ジョブなど、ユーザーに逐一伝える必要のない長い待機処理があります。ユーザーが求めていない進捗更新は、メリットなく会話を邪魔してしまいます。通常の 1 回 `return` するツールを維持したまま、`response_scheduling` を設定してバックグラウンド処理に移行させます。

```python
from google.adk.tools import FunctionTool
from google.genai import types

async def export_report(region: str) -> dict:
    """Generate and store the quarterly report. Returns when the export finishes."""
    await run_export(region)  # 時間のかかる通常の 1 回返却処理
    return {"status": "done", "region": region}

report_tool = FunctionTool(export_report)
report_tool.response_scheduling = types.FunctionResponseScheduling.WHEN_IDLE
```

エージェントはツールが実行されている間も自由に応答でき、ユーザーが投げかける他の質問に答え、準備が整った時点で結果を会話に組み込みます。実行可能な例は、[`live_non_blocking_tool_agent` サンプル](https://github.com/google/adk-python/tree/main/contributing/samples/live/live_non_blocking_tool_agent) として提供されています。

!!! note "Python 2.4+ が必要"

    `response_scheduling` は adk-python 2.4 で追加され、モデルごとにサポートが異なります。[サポート対象モデル](models.md#live-models) を参照してください。

`response_scheduling` は、完了した結果がユーザーに届く*タイミング*も制御します。

| 値 | 動作 | 主な用途 |
|---|---|---|
| `WHEN_IDLE` | 会話の自然な合間を待つ | レポートや検索など、通常の選択肢 |
| `INTERRUPT` | 即座に割り込んで伝える | アラーム、障害、「送金が失敗しました」などの緊急事態 |
| `SILENT` | コンテキストにのみ追加され、関連がある場合のみ発話 | モデルが後で参照できる背景情報 |

## ストリーミングツール

ストリーミングツールは実行を維持しながらエージェントに中間結果をプッシュするため、ユーザーが再度質問しなくても、エージェントが進捗を伝えたり、変化する入力（株価、動画フレームに現れた人物など）に反応したりできます。ツールをストリーミングにするのは簡単です。`return` の代わりに `yield` を行う `async` 関数にするだけです。ADK は、すべての非同期ジェネレータツールを自動的にノンブロッキングとして扱います。

```python
import asyncio
from typing import AsyncGenerator

async def query_sales_database(region: str) -> AsyncGenerator[str, None]:
    """Run the quarterly sales report. Call this once; it streams its own updates."""
    yield "Connecting to the warehouse..."
    await asyncio.sleep(4)
    yield "Aggregating by product line..."
    await asyncio.sleep(4)
    yield f"Done. {summarise(region)}"
```

他のツールと同様に `tools=[...]` に渡します。モデルは各 `yield` をライブアップデートとして受信するため、沈黙する代わりに「データを取得しています... 集計中です... 完了しました。EMEA の売上は 481 万ドルで、12.4% 増加しました」のようにユーザーに伝えます。これは、RAG パイプライン、多段階の集計、ビルドとテストの実行など、進捗を知らせる価値があるあらゆるケースに適しています。

ユーザーが途中でキャンセルできるように（例:「やっぱりキャンセルして」）、ADK の予約済み `stop_streaming` ツール（ADK が名前でインターセプトする空の関数）を追加してください。

### 動画ストリーミングツール

`input_stream: LiveRequestQueue` パラメータを追加すると、ADK はそのツール専用のキューにユーザーのリアルタイム入力を供給し、動画フレームを取り出して反応できるようにします。

ストリーミングツールの要件：

- `yield` する型を `T` とした場合、`AsyncGenerator[T, None]` を返すように型付けされた `async` 関数である必要があります。
- 動画の場合、`input_stream: LiveRequestQueue` を追加します。ADK が自動的に値を注入します。

以下のパターンでは、キューを最新のフレームまで排出し、古いフレームを破棄して、回答が変化したときにのみ `yield` するため、エージェントはそれ以外のときは静かに待機します。

=== "Python"

    ```python
    import asyncio
    import os
    from typing import AsyncGenerator

    from google.adk.agents import LiveRequestQueue
    from google.adk.agents.llm_agent import Agent
    from google.adk.tools.function_tool import FunctionTool
    from google.genai import Client
    from google.genai import types as genai_types

    PROMPT = "How many people are in this image? Reply with a number only."


    async def monitor_video_stream(
        input_stream: LiveRequestQueue,
    ) -> AsyncGenerator[str, None]:
      """Report how many people are visible, whenever that number changes."""
      client = Client()
      last_count = None

      while True:
        # キューをフラッシュして最新のフレームのみを保持。古いフレームは破棄。
        latest = None
        while input_stream._queue.qsize() != 0:
          req = await input_stream.get()
          if req.blob and req.blob.mime_type == "image/jpeg":
            latest = req

        if latest is not None:
          response = client.models.generate_content(
              model="gemini-flash-latest",
              contents=genai_types.Content(
                  role="user",
                  parts=[
                      genai_types.Part.from_bytes(
                          data=latest.blob.data, mime_type=latest.blob.mime_type
                      ),
                      genai_types.Part.from_text(text=PROMPT),
                  ],
              ),
          )
          count = response.candidates[0].content.parts[0].text.strip()
          if count != last_count:
            last_count = count
            yield count

        await asyncio.sleep(0.5)


    # ADK が名前でこれをインターセプトします。中身は空のままで構いません。
    def stop_streaming(function_name: str):
      """Stop a running streaming tool.

      Args:
        function_name: The name of the streaming function to stop.
      """


    root_agent = Agent(
        # ストリーミングツールは run_live() の下で実行されるため、ルートエージェントにはライブモデルが必要です。
        # 上記の gemini-flash-latest はツール内の 1 回限りの呼び出し専用です。
        model=os.getenv("DEMO_AGENT_MODEL", "gemini-live-2.5-flash-native-audio"),
        name="video_monitoring_agent",
        instruction=(
            "You monitor the user's video stream. Call monitor_video_stream once when"
            " asked, then report each update it sends. Never call it again to poll."
        ),
        tools=[monitor_video_stream, FunctionTool(stop_streaming)],
    )
    ```

=== "Java"

    ```java
    import com.google.adk.agents.LiveRequestQueue;
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.tools.Annotations.Schema;
    import com.google.adk.tools.FunctionTool;
    import com.google.genai.Client;
    import com.google.genai.types.Content;
    import com.google.genai.types.GenerateContentConfig;
    import com.google.genai.types.Part;
    import io.reactivex.rxjava3.core.Flowable;
    import java.util.Arrays;
    import java.util.Map;
    import java.util.concurrent.TimeUnit;

    public class StreamingTools {

      private static final String PROMPT =
          "How many people are in this image? Reply with a number only.";

      // `inputStream` は予約済みのパラメータ名です。ADK がビデオストリームを渡します。
      @Schema(description = "Report how many people are visible, whenever that number changes.")
      public static Flowable<Map<String, Object>> monitorVideoStream(
          @Schema(name = "inputStream") LiveRequestQueue inputStream) {
        Client client = Client.builder().build();

        return inputStream
            .get()
            .filter(req -> req.blob().isPresent()
                && "image/jpeg".equals(req.blob().get().mimeType()))
            .sample(500, TimeUnit.MILLISECONDS)  // 0.5秒ごとに最新フレームを取得
            .map(req -> client.models().generateContent(
                    "gemini-flash-latest",
                    Content.builder()
                        .role("user")
                        .parts(Arrays.asList(
                            Part.builder().inlineData(req.blob().get()).build(),
                            Part.fromText(PROMPT)))
                        .build(),
                    GenerateContentConfig.builder().build())
                .text())
            .distinctUntilChanged()  // カウントが変化したときにのみ yield
            .map(count -> Map.of("result", count));
      }

      // ADK が名前でこれをインターセプトします。中身は空のままで構いません。
      @Schema(description = "Stop a running streaming tool.")
      public static void stopStreaming(
          @Schema(name = "functionName", description = "The streaming function to stop.")
          String functionName) {}

      public static void main(String[] args) {
        LlmAgent rootAgent =
            LlmAgent.builder()
                .model("gemini-live-2.5-flash-native-audio")
                .name("video_monitoring_agent")
                .instruction(
                    "You monitor the user's video stream. Call monitorVideoStream once when"
                        + " asked, then report each update it sends. Never call it again to poll.")
                .tools(Arrays.asList(
                    FunctionTool.create(StreamingTools.class, "monitorVideoStream"),
                    FunctionTool.create(StreamingTools.class, "stopStreaming")))
                .build();
      }
    }
    ```

エージェントに動画ストリーム内の人数を監視するよう依頼し、カメラのフレーム内を出入りして試してみてください。

## ツール実行コンテキスト

ツールやコールバックは、状態、履歴、アーティファクトのために `InvocationContext` を受け取ります。[エージェントコンテキスト](../context/index.md) で解説されているように、これはすべての ADK エージェントで同様に機能しますが、ライブセッションでは重要な違いが 1 つあります。**1 つの `InvocationContext` が `run_live()` ループ全体にわたって存続します**。これは `run_live()` を呼び出したときに作成され、セッションが終了するまですべてのエージェントやすべてのターンにわたって存続します。リクエスト/レスポンス型のエージェントでは呼び出し（invocation）は単一のターンですが、ライブセッションでは会話全体を指します。

ライブツールで最も頻繁に使用される 2 つのフィールドは次のとおりです。

| フィールド | 取得できる内容 |
| :---- | :---- |
| `context.run_config` | セッションの [設定](configuration.md) — レスポンスモダリティ、文字起こし、制限 |
| `context.end_invocation` | `True` に設定すると、ストリーミングセッション全体を即座に終了 |
