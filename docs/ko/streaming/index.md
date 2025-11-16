# ADK의 양방향(Bidi) 스트리밍 (live)

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.5.0</span><span class="lst-preview">실험적 기능</span>
</div>
  
ADK의 양방향(Bidi) 스트리밍(live)은 [Gemini Live API](https://ai.google.dev/gemini-api/docs/live)의 저지연 양방향 음성 및 영상 상호작용 기능을 AI 에이전트에 추가합니다.

!!! example "실험적 프리뷰 릴리스"

    양방향(Bidi) 스트리밍 기능은 실험적 기능입니다.

양방향 스트리밍 또는 라이브 모드를 사용하면, 최종 사용자에게 자연스럽고 사람과 유사한 음성 대화 경험을 제공할 수 있습니다. 여기에는 사용자가 음성 명령으로 에이전트의 응답을 중단시키는 기능도 포함됩니다. 스트리밍 기능을 갖춘 에이전트는 텍스트, 오디오, 비디오 입력을 처리할 수 있으며, 텍스트 및 오디오 출력을 제공할 수 있습니다.

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

!!! info

    이는 서버 측 스트리밍이나 토큰 수준 스트리밍과는 다릅니다.
    토큰 수준 스트리밍은 언어 모델이 응답을 생성하여 토큰 단위로 사용자에게 다시 보내는 단방향 프로세스입니다. 이는 '타이핑' 효과를 만들어 즉각적인 응답이라는 인상을 주고 답변의 시작 부분을 보기까지 걸리는 시간을 줄여줍니다. 사용자가 전체 프롬프트를 보내면 모델이 이를 처리한 다음, 응답을 조금씩 생성하여 다시 보내기 시작합니다. 이 섹션은 양방향 스트리밍(live)에 대한 내용입니다.

<div class="grid cards" markdown>

-   :material-console-line: **빠른 시작 (양방향 스트리밍)**

    ---

    이 빠른 시작에서는 간단한 에이전트를 구축하고 ADK의 스트리밍을 사용하여 저지연 양방향 음성 및 영상 통신을 구현합니다.

    - [빠른 시작 (양방향 스트리밍)](../get-started/streaming/quickstart-streaming.md)

-   :material-console-line: **사용자 정의 오디오 스트리밍 앱 샘플**

    ---

    이 문서는 ADK Streaming과 FastAPI로 구축된 사용자 정의 비동기 웹 앱의 서버 및 클라이언트 코드 개요를 다룹니다. WebSockets를 통해 실시간 양방향 오디오 및 텍스트 통신을 가능하게 합니다.

    - [사용자 정의 오디오 스트리밍 앱 샘플 (WebSockets)](custom-streaming-ws.md)

-   :material-console-line: **양방향 스트리밍 개발 가이드 시리즈**

    ---

    ADK를 사용한 양방향 스트리밍 개발에 대해 더 깊이 알아보기 위한 시리즈 문서입니다. 기본 개념과 사용 사례, 핵심 API, 그리고 엔드투엔드 애플리케이션 설계를 배울 수 있습니다.

    - [양방향 스트리밍 개발 가이드 시리즈: 1부 - 소개](dev-guide/part1.md)

-   :material-console-line: **스트리밍 도구**

    ---

    스트리밍 도구를 사용하면 도구(함수)가 중간 결과를 에이전트에게 스트리밍으로 반환할 수 있으며, 에이전트는 이러한 중간 결과에 응답할 수 있습니다. 예를 들어, 스트리밍 도구를 사용하여 주가 변동을 모니터링하고 에이전트가 이에 반응하도록 할 수 있습니다. 또 다른 예로, 에이전트가 비디오 스트림을 모니터링하다가 비디오 스트림에 변화가 있을 때 이를 보고하도록 할 수 있습니다.

    - [스트리밍 도구](streaming-tools.md)

-   :material-console-line: **사용자 정의 오디오 스트리밍 앱 샘플**

    ---

    이 문서는 ADK Streaming과 FastAPI로 구축된 사용자 정의 비동기 웹 앱의 서버 및 클라이언트 코드 개요를 다룹니다. SSE(Server Sent Events)와 WebSockets를 모두 사용하여 실시간 양방향 오디오 및 텍스트 통신을 가능하게 합니다.

    - [스트리밍 구성](configuration.md)

-   :material-console-line: **블로그 게시물: Google ADK + Vertex AI Live API**

    ---

    이 문서는 실시간 오디오/비디오 스트리밍을 위해 ADK에서 양방향 스트리밍(live)을 사용하는 방법을 보여줍니다. `LiveRequestQueue`를 사용하여 사용자 정의 대화형 AI 에이전트를 구축하는 Python 서버 예제를 제공합니다.

    - [블로그 게시물: Google ADK + Vertex AI Live API](https://medium.com/google-cloud/google-adk-vertex-ai-live-api-125238982d5e)

-   :material-console-line: **블로그 게시물: Claude Code Skills로 ADK 개발 가속화하기**

    ---

    이 문서는 Claude Code Skills를 사용하여 ADK 개발을 가속화하는 방법을 보여주며, 양방향 스트리밍 채팅 앱을 구축하는 예제를 제공합니다. AI 기반 코딩 지원을 활용하여 더 나은 에이전트를 더 빠르게 구축하는 방법을 배우세요.

    - [블로그 게시물: Claude Code Skills로 ADK 개발 가속화하기](https://medium.com/@kazunori279/supercharge-adk-development-with-claude-code-skills-d192481cbe72)

</div>