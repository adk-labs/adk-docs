# ストリーミングツール

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.5.0</span><span class="lst-java">Java v0.2.0</span><span class="lst-preview">実験的機能</span>
</div>

ストリーミングツールを使用すると、ツール（関数）が中間結果をエージェントにストリーミングで送り返すことができ、エージェントはそれらの中間結果に応答できます。
例えば、ストリーミングツールを使用して株価の変動を監視し、エージェントにそれに反応させることができます。別の例として、エージェントにビデオストリームを監視させ、ビデオストリームに変化があった場合にエージェントがその変化を報告するようにすることもできます。

!!! info

    これは ADK Gemini Live API でのみサポートされています。

ストリーミングツールを定義するには、次の要件に従う必要があります：

1.  **非同期関数:** ツールは `async` Python関数でなければなりません。
2.  **AsyncGeneratorの戻り値の型:** 関数は `AsyncGenerator` を返すように型付けされている必要があります。`AsyncGenerator` の最初の型パラメータは `yield` するデータの型です（例：テキストメッセージの場合は `str`、構造化データの場合はカスタムオブジェクト）。ジェネレータが `send()` を介して値を受け取らない場合、2番目の型パラメータは通常 `None` です。


私たちは2種類のストリーミングツールをサポートしています：
- シンプルタイプ。これは、ビデオ/オーディオではないストリーム（ADK WebやADKランナーに供給するストリーム）のみを入力として受け取るストリーミングツールの一種です。
- ビデオストリーミングツール。これはビデオストリーミングでのみ機能し、ビデオストリーム（ADK WebやADKランナーに供給するストリーム）がこの関数に渡されます。

それでは、株価の変動を監視し、ビデオストリームの変化を監視できるエージェントを定義してみましょう。

```python
import asyncio
from typing import AsyncGenerator

from google.adk.agents import LiveRequestQueue
from google.adk.agents.llm_agent import Agent
from google.adk.tools.function_tool import FunctionTool
from google.genai import Client
from google.genai import types as genai_types


async def monitor_stock_price(stock_symbol: str) -> AsyncGenerator[str, None]:
  """この関数は、指定されたstock_symbolの価格を継続的、ストリーミング、非同期的に監視します。"""
  print(f"{stock_symbol}の株価監視を開始します！")

  # 株価の変動をモックします。
  await asyncio.sleep(4)
  price_alert1 = f"{stock_symbol}の価格は300です"
  yield price_alert1
  print(price_alert1)

  await asyncio.sleep(4)
  price_alert1 = f"{stock_symbol}の価格は400です"
  yield price_alert1
  print(price_alert1)

  await asyncio.sleep(20)
  price_alert1 = f"{stock_symbol}の価格は900です"
  yield price_alert1
  print(price_alert1)

  await asyncio.sleep(20)
  price_alert1 = f"{stock_symbol}の価格は500です"
  yield price_alert1
  print(price_alert1)


# ビデオストリーミングの場合、`input_stream: LiveRequestQueue`はADKがビデオストリームを渡すために必要かつ予約されたキーパラメータです。
async def monitor_video_stream(
    input_stream: LiveRequestQueue,
) -> AsyncGenerator[str, None]:
  """ビデオストリームに何人の人がいるかを監視します。"""
  print("monitor_video_streamを開始します！")
  client = Client(vertexai=False)
  prompt_text = (
      "この画像に写っている人数を数えてください。数字のみで応答してください。"
  )
  last_count = None
  while True:
    last_valid_req = None
    print("監視ループを開始します")

    # このループを使用して最新の画像を取得し、古いものは破棄します
    while input_stream._queue.qsize() != 0:
      live_req = await input_stream.get()

      if live_req.blob is not None and live_req.blob.mime_type == "image/jpeg":
        last_valid_req = live_req

    # 有効な画像が見つかった場合は処理します
    if last_valid_req is not None:
      print("キューから最新のフレームを処理しています")

      # blobのデータとMIMEタイプを使用して画像パートを作成します
      image_part = genai_types.Part.from_bytes(
          data=last_valid_req.blob.data, mime_type=last_valid_req.blob.mime_type
      )

      contents = genai_types.Content(
          role="user",
          parts=[image_part, genai_types.Part.from_text(prompt_text)],
      )

      # 提供された画像とプロンプトに基づいてコンテンツを生成するためにモデルを呼び出します
      response = client.models.generate_content(
          model="gemini-2.0-flash-exp",
          contents=contents,
          config=genai_types.GenerateContentConfig(
              system_instruction=(
                  "あなたは役立つビデオ分析アシスタントです。この画像やビデオに"
                  "写っている人数を数えることができます。数字のみで応答してください。"
              )
          ),
      )
      if not last_count:
        last_count = response.candidates[0].content.parts[0].text
      elif last_count != response.candidates[0].content.parts[0].text:
        last_count = response.candidates[0].content.parts[0].text
        yield response
        print("response:", response)

    # 新しい画像をチェックする前に少し待ちます
    await asyncio.sleep(0.5)


# 要求されたときにストリーミングツールを停止させるために、この関数をそのまま使用してください。
# 例えば、`monitor_stock_price`を停止したい場合、エージェントは
# stop_streaming(function_name=monitor_stock_price)でこの関数を呼び出します。
def stop_streaming(function_name: str):
  """ストリーミングを停止します

  Args:
    function_name: 停止するストリーミング関数の名前。
  """
  pass


root_agent = Agent(
    model="gemini-2.0-flash-exp",
    name="video_streaming_agent",
    instruction="""
      あなたは監視エージェントです。提供されたツール/関数を使用して、ビデオ監視と株価監視ができます。
      ユーザーがビデオストリームを監視したい場合、
      monitor_video_stream関数を使用してそれを行うことができます。monitor_video_streamが
      アラートを返した場合、ユーザーに伝える必要があります。
      ユーザーが株価を監視したい場合、monitor_stock_priceを使用できます。
      あまり多くの質問をしないでください。おしゃべりにならないでください。
    """,
    tools=[
        monitor_video_stream,
        monitor_stock_price,
        FunctionTool(stop_streaming),
    ]
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
    import com.google.genai.types.GenerateContentResponse;
    import com.google.genai.types.Part;
    import io.reactivex.rxjava3.core.Flowable;
    import java.util.Arrays;
    import java.util.Collections;
    import java.util.Map;
    import java.util.concurrent.TimeUnit;

    public class StreamingTools {

      @Schema(description = "この関数は、指定されたstock_symbolの価格を継続的、ストリーミング、非同期的に監視します。")
      public static Flowable<Map<String, Object>> monitorStockPrice(@Schema(name = "stockSymbol") String stockSymbol) {
        System.out.println(stockSymbol + "の株価監視を開始します！");

        return Flowable.concat(
            Flowable.<Map<String, Object>>just(Collections.singletonMap("result", "the price for " + stockSymbol + " is 300")).delay(4, TimeUnit.SECONDS),
            Flowable.<Map<String, Object>>just(Collections.singletonMap("result", "the price for " + stockSymbol + " is 400")).delay(4, TimeUnit.SECONDS),
            Flowable.<Map<String, Object>>just(Collections.singletonMap("result", "the price for " + stockSymbol + " is 900")).delay(20, TimeUnit.SECONDS),
            Flowable.<Map<String, Object>>just(Collections.singletonMap("result", "the price for " + stockSymbol + " is 500")).delay(20, TimeUnit.SECONDS)
        );
      }

      // ビデオストリーミングの場合、`inputStream`はADKがビデオストリームを渡すために必要かつ予約されたパラメータです。
      @Schema(description = "ビデオストリームに何人の人がいるかを監視します。")
      public static Flowable<Map<String, Object>> monitorVideoStream(@Schema(name = "inputStream") LiveRequestQueue inputStream) {
        System.out.println("monitor_video_streamを開始します！");
        Client client = Client.builder().build();
        String promptText = "この画像に写っている人数を数えてください。数字のみで応答してください。";

        // RxJavaを使用してストリームを処理します
        return inputStream.get()
            .filter(req -> req.blob().isPresent() && "image/jpeg".equals(req.blob().get().mimeType()))
            .sample(500, TimeUnit.MILLISECONDS) // 0.5秒ごとに1フレーム処理します
            .map(req -> {
              System.out.println("キューから最新のフレームを処理しています");
              Part imagePart = Part.builder().inlineData(req.blob().get()).build();
              Content contents = Content.builder()
                  .role("user")
                  .parts(Arrays.asList(imagePart, Part.fromText(promptText)))
                  .build();

              GenerateContentResponse response = client.models().generateContent(
                  "gemini-2.5-flash",
                  contents,
                  GenerateContentConfig.builder()
                      .systemInstruction(Content.builder().parts(Arrays.asList(
                          Part.fromText("あなたは役立つビデオ分析アシスタントです。この画像やビデオに写っている人数を数えることができます。数字のみで応答してください。")
                      )).build())
                      .build()
              );
              return (Map<String, Object>) Collections.<String, Object>singletonMap("result", response.text());
            })
            .distinctUntilChanged()
            .doOnNext(res -> System.out.println("応答: " + res));
      }

      // 要求されたときにストリーミングツールを停止させるために、この関数をそのまま使用してください。
      @Schema(description = "ストリーミングを停止します")
      public static void stopStreaming(
          @Schema(name = "functionName", description = "停止するストリーミング関数の名前。") String functionName) {
        // ストリーミング停止ロジック
      }

      public static void main(String[] args) {
        LlmAgent rootAgent = LlmAgent.builder()
            .model("gemini-2.0-flash-exp")
            .name("video_streaming_agent")
            .instruction(
                "あなたは監視エージェントです。提供されたツール/関数を使用して、ビデオ監視と株価監視ができます。\n" +
                "ユーザーがビデオストリームを監視したい場合、\n" +
                "monitorVideoStream関数を使用してそれを行うことができます。monitorVideoStreamが\n" +
                "アラートを返した場合、ユーザーに伝える必要があります。\n" +
                "ユーザーが株価を監視したい場合、monitorStockPriceを使用できます。\n" +
                "あまり多くの質問をしないでください。おしゃべりにならないでください。"
            )
            .tools(Arrays.asList(
                FunctionTool.create(StreamingTools.class, "monitorVideoStream"),
                FunctionTool.create(StreamingTools.class, "monitorStockPrice"),
                FunctionTool.create(StreamingTools.class, "stopStreaming")
            ))
            .build();
      }
    }
    ```

テスト用のサンプルクエリは以下の通りです：
- XYZ株の株価を監視するのを手伝ってください。
- ビデオストリームに何人の人がいるかを監視するのを手伝ってください。
