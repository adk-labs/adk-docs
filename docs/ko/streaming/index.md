# ADK의 양방향 스트리밍(live)

!!! info

    이것은 실험적인 기능입니다. 현재 Python에서 사용할 수 있습니다.

!!! info

    이는 서버 측 스트리밍이나 토큰 수준 스트리밍과는 다릅니다. 이 섹션은 양방향 스트리밍(live)에 대한 내용입니다.

ADK의 양방향 스트리밍(live)은 [Gemini Live API](https://ai.google.dev/gemini-api/docs/live)의 저지연 양방향 음성 및 영상 상호작용 기능을 AI 에이전트에 추가합니다.

양방향 스트리밍(live) 모드를 사용하면, 사용자가 음성 명령으로 에이전트의 응답을 중단시키는 기능을 포함하여 자연스럽고 인간과 유사한 음성 대화 경험을 최종 사용자에게 제공할 수 있습니다. 스트리밍을 사용하는 에이전트는 텍스트, 오디오, 영상 입력을 처리할 수 있으며, 텍스트와 오디오 출력을 제공할 수 있습니다.

<div class="video-grid">
  <div class="video-item">
    <div class="video-container">
      <iframe src="https://www.youtube-nocookie.com/embed/Tu7-voU7nnw?si=RKs7EWKjx0bL96i5" title="Shopper's Concierge" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
    </div>
  </div>

  <div class="video-item">
    <div class="video-container">
      <iframe src="https://www.youtube-nocookie.com/embed/LwHPYyw7u6U?si=xxIEhnKBapzQA6VV" title="Shopper's Concierge" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
    </div>
  </div>
</div>

<div class="grid cards" markdown>

-   :material-console-line: **빠른 시작 (양방향 스트리밍)**

    ---

    이 빠른 시작 가이드에서는 간단한 에이전트를 빌드하고 ADK의 스트리밍을 사용하여 저지연 양방향 음성 및 영상 통신을 구현합니다.

    - [빠른 시작 (양방향 스트리밍)](../get-started/streaming/quickstart-streaming.md)

-   :material-console-line: **커스텀 오디오 스트리밍 앱 샘플**

    ---

    이 글에서는 ADK 스트리밍과 FastAPI로 빌드된 커스텀 비동기 웹 앱의 서버 및 클라이언트 코드를 개괄적으로 설명합니다. 이 앱은 SSE(Server Sent Events)와 웹소켓(WebSockets)을 모두 사용하여 실시간 양방향 오디오 및 텍스트 통신을 지원합니다.

    - [커스텀 오디오 스트리밍 앱 샘플 (SSE)](custom-streaming.md)
    - [커스텀 오디오 스트리밍 앱 샘플 (웹소켓)](custom-streaming-ws.md)

-   :material-console-line: **양방향 스트리밍 개발 가이드 시리즈**

    ---

    ADK를 사용한 양방향 스트리밍 개발을 더 깊이 다루는 시리즈 글입니다. 기본 개념과 사용 사례, 핵심 API, 엔드투엔드 애플리케이션 설계를 배울 수 있습니다.

    - [양방향 스트리밍 개발 가이드 시리즈: 파트 1 - 소개](dev-guide/part1.md)

-   :material-console-line: **스트리밍 툴**

    ---

    스트리밍 툴을 사용하면 툴(함수)이 중간 결과를 에이전트에게 스트리밍으로 다시 보낼 수 있고, 에이전트는 이러한 중간 결과에 응답할 수 있습니다. 예를 들어, 스트리밍 툴을 사용하여 주가 변동을 모니터링하고 에이전트가 이에 반응하도록 할 수 있습니다. 또 다른 예로, 에이전트가 비디오 스트림을 모니터링하다가 스트림에 변화가 생기면 그 변화를 보고하도록 할 수 있습니다.

    - [스트리밍 툴](streaming-tools.md)

-   :material-console-line: **커스텀 오디오 스트리밍 앱 샘플**

    ---

    이 글에서는 ADK 스트리밍과 FastAPI로 빌드된 커스텀 비동기 웹 앱의 서버 및 클라이언트 코드를 개괄적으로 설명합니다. 이 앱은 SSE(Server Sent Events)와 웹소켓(WebSockets)을 모두 사용하여 실시간 양방향 오디오 및 텍스트 통신을 지원합니다.

    - [스트리밍 구성](configuration.md)

-   :material-console-line: **블로그 게시물: Google ADK + Vertex AI Live API**

    ---

    이 글은 ADK에서 양방향 스트리밍(live)을 사용하여 실시간 오디오/비디오 스트리밍을 구현하는 방법을 보여줍니다. LiveRequestQueue를 사용하여 커스텀 대화형 AI 에이전트를 구축하는 Python 서버 예제를 제공합니다.

    - [블로그 게시물: Google ADK + Vertex AI Live API](https://medium.com/google-cloud/google-adk-vertex-ai-live-api-125238982d5e)

</div>