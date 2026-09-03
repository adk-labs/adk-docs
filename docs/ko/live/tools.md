# 라이브 에이전트를 위한 도구

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

도구는 ADK의 다른 에이전트와 마찬가지로 라이브 에이전트에서도 동일하게 작동합니다. 에이전트에 함수를 전달하면 모델이 이를 호출합니다. 라이브 연결 상태라고 해서 도구 작성 방식이 달라지지 않으므로 도구 정의, 도구 컨텍스트, 콜백 및 인증은 모두 [사용자 정의 도구](../tools-custom/index.md)를 따릅니다.

라이브 연결에는 두 가지 추가 기능이 제공됩니다. ADK는 `run_live()` 루프 내부에서 도구 호출을 자동으로 실행하므로 순수 Live API에서 요구하는 복잡한 함수 호출 배선 코드를 직접 작성할 필요가 없습니다. 또한 라이브 에이전트는 계속 실행되면서 에이전트로 중간 결과를 푸시하는 *스트리밍 도구*를 사용할 수 있습니다. 이를 통해 사용자가 다시 묻지 않아도 주가 변동이나 비디오 프레임에 사람이 나타나는 등의 이벤트에 에이전트가 즉각 반응할 수 있습니다.

## 자동 도구 실행

에이전트에 도구를 정의하면 ADK가 `run_live()` 루프 내에서 자동으로 도구를 호출합니다. 모델의 함수 호출을 감지하고, 도구를 실행하며(전/후 콜백 포함, 병렬 실행), 응답 형식을 지정하고 호출 및 응답 모두를 이벤트로 전달합니다. 배선 작업이 아닌 함수 로직 자체만 작성하면 됩니다.

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

이벤트 스트림을 통해 도구 활동을 관찰할 수 있으며, 개발자가 직접 도구 실행을 구동할 필요가 없습니다:

```python
async for event in runner.run_live(...):
    if event.get_function_calls():
        print(f"Model calling: {event.get_function_calls()[0].name}")
    if event.get_function_responses():
        print(f"Tool result: {event.get_function_responses()[0].response}")
```

## 에이전트의 응답성 유지하기

채팅 창에서는 사용자가 로딩 스피너를 보기 때문에 느린 도구도 감수할 수 있습니다. 하지만 실시간 음성 대화에서는 그렇지 않습니다. 에이전트가 10초 걸리는 API를 호출하고 침묵에 빠지면 사용자는 통화가 끊어졌다고 생각합니다. 따라서 실행 중에 대화를 차단(block)하지 않는 도구가 필요합니다. ADK는 빠른 케이스를 위한 일반적인 블로킹 방식 외에 두 가지 방법을 제공합니다:

| 상황 | 사용 방식 | 구현 방법 |
|---|---|---|
| 1초 이내에 반환되는 빠른 도구 | **블로킹** (기본값) | 일반적인 단일 `return` 도구 |
| 중계할 내용이 없는 긴 대기 작업 | **[비차단(Non-blocking) 도구](#non-blocking-tools)** | 도구에 `response_scheduling` 설정 |
| 사용자에게 중계할 가치가 있는 긴 대기 작업 | **[스트리밍 도구](#streaming-tools)** | 비동기 제너레이터에서 진행 상황 `yield` |

## 비차단(Non-blocking) 도구

대규모 분석 쿼리, 일괄 내보내기, 미디어 생성 작업처럼 굳이 사용자에게 중계할 필요가 없는 긴 대기 작업이 있습니다. 사용자가 요청하지 않은 진행 상황 업데이트는 이점 없이 대화를 방해할 뿐입니다. 일반적인 단일 `return` 도구를 유지하면서 `response_scheduling`을 설정하여 백그라운드로 이동시키세요:

```python
from google.adk.tools import FunctionTool
from google.genai import types

async def export_report(region: str) -> dict:
    """Generate and store the quarterly report. Returns when the export finishes."""
    await run_export(region)  # 오래 걸리는 일반적인 단일 반환 작업
    return {"status": "done", "region": region}

report_tool = FunctionTool(export_report)
report_tool.response_scheduling = types.FunctionResponseScheduling.WHEN_IDLE
```

에이전트는 도구가 실행되는 동안에도 자유롭게 사용자의 다른 질문에 답변하며, 결과가 준비되면 대화에 자연스럽게 반영합니다. 실행 가능한 예제는 [`live_non_blocking_tool_agent` 샘플](https://github.com/google/adk-python/tree/main/contributing/samples/live/live_non_blocking_tool_agent)에서 제공됩니다.

!!! note "Python 2.4 이상 필요"

    `response_scheduling`은 adk-python 2.4에서 추가되었으며, 모델별로 지원 여부가 다릅니다. [지원 모델](models.md#live-models)을 참고하세요.

`response_scheduling`은 완료된 결과가 사용자에게 도달하는 *시점*도 제어합니다:

| 값 | 동작 | 사용 사례 |
|---|---|---|
| `WHEN_IDLE` | 자연스러운 대화 휴지기를 기다림 | 일반적인 보고서 및 조회 작업 (권장 선택) |
| `INTERRUPT` | 즉시 전달 (끼어들기) | 알람, 장애 알림, "송금 실패" 등 긴급 상황 |
| `SILENT` | 컨텍스트에만 입력되며 관련이 있을 때만 언급 | 모델이 나중에 사용할 수 있는 배경 정보 |

## 스트리밍 도구

스트리밍 도구는 백그라운드에서 계속 실행되면서 에이전트로 중간 결과를 푸시하므로, 사용자가 다시 묻지 않아도 에이전트가 진행 상황을 설명하거나 변화하는 입력(주가, 비디오 프레임에 나타난 사람 등)에 반응할 수 있습니다. 도구를 스트리밍으로 전환하는 것은 간단합니다. `return` 대신 `yield`를 사용하는 `async` 함수로 작성하면 됩니다. ADK는 모든 비동기 제너레이터 도구를 자동으로 비차단(non-blocking)으로 처리합니다.

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

다른 도구와 마찬가지로 `tools=[...]`에 전달하세요. 모델은 각 `yield`를 실시간 업데이트로 수신하므로, 침묵 대신 "데이터를 가져오는 중입니다... 집계 중입니다... 완료되었습니다: EMEA 지역 매출은 481만 달러로 12.4% 상승했습니다"와 같이 사용자에게 안내합니다. 이는 RAG 파이프라인, 다단계 데이터 집계, 빌드 및 테스트 실행 등 진행 상황을 알릴 가치가 있는 모든 곳에 적합합니다.

사용자가 취소할 수 있도록(예: "그만둬, 취소해줘") ADK의 예약된 `stop_streaming` 도구(ADK가 이름으로 가로채는 빈 함수)를 추가하세요.

### 비디오 스트리밍 도구

`input_stream: LiveRequestQueue` 매개변수를 추가하면 ADK는 해당 도구 전용 큐에 사용자의 실시간 입력을 공급하여 비디오 프레임을 가져와 반응할 수 있게 합니다.

모든 스트리밍 도구의 요구 사항:

- `yield`하는 타입이 `T`일 때 `AsyncGenerator[T, None]`을 반환하는 타입이 지정된 `async` 함수여야 합니다.
- 비디오의 경우 `input_stream: LiveRequestQueue`를 추가하면 ADK가 이를 채워줍니다.

아래 패턴은 오래된 프레임을 버리고 최신 프레임만 큐에서 가져오며, 답변이 변경될 때만 `yield`하여 에이전트가 불필요하게 말을 하지 않도록 유지합니다.

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
        # 큐를 비우고 최신 프레임만 유지합니다. 이전 프레임은 오래된 것입니다.
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


    # ADK가 이름으로 이를 가로챕니다. 함수 본문은 비워둡니다.
    def stop_streaming(function_name: str):
      """Stop a running streaming tool.

      Args:
        function_name: The name of the streaming function to stop.
      """


    root_agent = Agent(
        # 스트리밍 도구는 run_live() 아래에서 실행되므로 루트 에이전트에는 라이브 모델이 필요합니다.
        # 위의 gemini-flash-latest는 도구 내의 일회성 호출 전용입니다.
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

      // `inputStream`은 예약된 매개변수 이름입니다. ADK가 비디오 스트림을 전달합니다.
      @Schema(description = "Report how many people are visible, whenever that number changes.")
      public static Flowable<Map<String, Object>> monitorVideoStream(
          @Schema(name = "inputStream") LiveRequestQueue inputStream) {
        Client client = Client.builder().build();

        return inputStream
            .get()
            .filter(req -> req.blob().isPresent()
                && "image/jpeg".equals(req.blob().get().mimeType()))
            .sample(500, TimeUnit.MILLISECONDS)  // 0.5초마다 최신 프레임 샘플링
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
            .distinctUntilChanged()  // 인원수가 변경될 때만 yield
            .map(count -> Map.of("result", count));
      }

      // ADK가 이름으로 이를 가로챕니다. 본문은 비워둡니다.
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

에이전트에게 비디오 스트림에 몇 명의 사람이 있는지 모니터링해 달라고 요청한 다음 프레임 안팎으로 걸어 다니면서 테스트해 보세요.

## 도구 실행 컨텍스트

도구 또는 콜백은 상태, 기록, 아티팩트를 위해 `InvocationContext`를 수신합니다. 이는 [에이전트 컨텍스트](../context/index.md)에 설명된 대로 모든 ADK 에이전트에서 동일하게 작동하지만, 라이브 세션에서는 중요한 차이점이 있습니다: **하나의 `InvocationContext`가 전체 `run_live()` 루프에 걸쳐 유지됩니다**. `run_live()`를 호출할 때 생성되어 세션이 끝날 때까지 모든 에이전트와 모든 턴에 걸쳐 유지됩니다. 요청/응답 에이전트에서 호출(invocation)은 단일 턴이지만, 라이브 세션에서는 대화 전체를 의미합니다.

라이브 도구에서 가장 자주 사용되는 두 필드는 다음과 같습니다:

| 필드 | 제공 내용 |
|---|---|
| `context.run_config` | 세션의 [구성](configuration.md) — 응답 모달리티, 전사, 제한 |
| `context.end_invocation` | `True`로 설정하면 전체 스트리밍 세션이 즉시 종료됨 |
