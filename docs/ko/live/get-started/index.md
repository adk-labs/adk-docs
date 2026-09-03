# 라이브 에이전트 시작하기

빠른 시작에서는 이미 마이크를 캡처하고, 에이전트의 응답을 재생하며, 전사(transcript)를 렌더링하는 브라우저 클라이언트를 제공하는 `adk web`에서 에이전트를 실행합니다. 개발자는 에이전트를 작성하고 모델을 선택하기만 하면 되며, 클라이언트 코드를 작성할 필요가 없습니다.

에이전트에는 양방향 스트리밍 연결을 유지할 수 있는 모델이 필요합니다. 최신 목록과 구성 방법은 [지원 모델](../models.md)을 참고하세요.

## 언어 선택

<div class="grid cards" markdown>

-   :fontawesome-brands-python:{ .lg .middle } **Python**

    ---

    ADK를 설정하고, 음성 에이전트를 구축한 후 `adk web`에서 대화해 보세요.

    [:octicons-arrow-right-24: Python 빠른 시작](streaming-python.md)

-   :fontawesome-brands-java:{ .lg .middle } **Java**

    ---

    Maven을 설정하고, 음성 에이전트를 구축한 후 `adk web` 또는 커스텀 오디오 앱에서 실행해 보세요.

    [:octicons-arrow-right-24: Java 빠른 시작](streaming-java.md)

</div>

## 다음 단계

- **[구성](../configuration.md)** — 음성, 언어, 전사 및 턴(turn) 감지를 설정합니다.
- **[도구](../tools.md)** — 실행 중에 중간 결과를 다시 스트리밍하는 도구를 포함하여 대화 중간에 호출할 수 있는 도구를 에이전트에 부여합니다.
- **[세션](../sessions.md)** 및 **[이벤트](../events.md)** — `run_live()` 루프와 반환되는 모든 이벤트 처리.
- **[평가](../evaluation.md)** — 출시 전 음성 대화 품질 점수 측정.
- **[커스텀 서버 구축](../custom-server.md)** — `adk web`은 개발용 클라이언트이므로, 자체 서버와 클라이언트 뒤에서 라이브 에이전트를 실행하는 방법을 다룹니다.