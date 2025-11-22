# 스트리밍 에이전트 구축하기

ADK(Agent Development Kit)를 사용하면 스트리밍을 통해 AI 에이전트와 실시간으로 상호작용하는 경험을 구현할 수 있습니다. 이를 통해 라이브 음성 대화, 실시간 도구(tool) 사용, 에이전트의 지속적인 상태 업데이트와 같은 기능을 사용할 수 있습니다.

이 페이지에서는 Python 및 Java ADK 환경에서 스트리밍 기능을 바로 시작할 수 있도록 돕는 퀵스타트 예제를 제공합니다.

<div class.="grid cards" markdown>

-   :fontawesome-brands-python:{ .lg .middle } **Python ADK: 스트리밍 에이전트**

    ---
    이 예제는 Python ADK를 사용하여 에이전트와 기본적인 스트리밍 상호작용을 설정하는 방법을 보여줍니다. 일반적으로 `Runner.run_live()` 메서드를 사용하고 비동기 이벤트를 처리하는 과정이 포함됩니다.

    [:octicons-arrow-right-24: Python 스트리밍 퀵스타트 보기](quickstart-streaming.md) <br>
    <!-- [:octicons-arrow-right-24: View Python Streaming Quickstart](python/quickstart-streaming.md) -->

<!-- This comment forces a block separation -->

-   :fontawesome-brands-java:{ .lg .middle } **Java ADK: 스트리밍 에이전트**

    ---
    이 예제는 Java ADK를 사용하여 에이전트와 기본적인 스트리밍 상호작용을 설정하는 방법을 보여줍니다. `Runner.runLive()` 메서드와 `LiveRequestQueue`를 사용하고, `Flowable<Event>` 스트림을 처리하는 과정이 포함됩니다.

    [:octicons-arrow-right-24: Java 스트리밍 퀵스타트 보기](quickstart-streaming-java.md) <br>
    <!-- [:octicons-arrow-right-24: View Java Streaming Quickstart](java/quickstart-streaming-java.md)) -->

</div>