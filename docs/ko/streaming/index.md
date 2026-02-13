# ADK의 양방향(Bidi) 스트리밍(live)

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.5.0</span><span class="lst-preview">실험적 기능</span>
</div>
  
ADK의 양방향(Bidi) 스트리밍(live)은 [Gemini Live API](https://ai.google.dev/gemini-api/docs/live)의 저지연 양방향 음성/영상 상호작용 기능을 AI 에이전트에 추가합니다.

양방향 스트리밍(라이브) 모드에서는 사용자에게 자연스럽고 사람 같은 음성 대화 경험을 제공할 수 있으며, 사용자가 음성 명령으로 에이전트 응답을 중단하는 것도 가능합니다. 스트리밍 에이전트는 텍스트, 오디오, 비디오 입력을 처리하고 텍스트와 오디오 출력을 제공합니다.

<div class="video-grid">
  <div class="video-item">
    <div class="video-container">
      <iframe src="https://www.youtube-nocookie.com/embed/vLUkAGeLR1k" title="ADK Bidi-streaming in 5 minutes" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
    </div>
  </div>
  <div class="video-item">
    <div class="video-container">
      <iframe src="https://www.youtube-nocookie.com/embed/Hwx94smxT_0" title="Shopper's Concierge 2 Demo" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
    </div>
  </div>
</div>

<div class="grid cards" markdown>

-   :material-console-line: **빠른 시작 (양방향 스트리밍)**

    ---

    이 빠른 시작에서는 간단한 에이전트를 만들고 ADK 스트리밍을 사용해 저지연 양방향 음성/영상 통신을 구현합니다.

    - [빠른 시작 (양방향 스트리밍)](../get-started/streaming/quickstart-streaming.md)

-   :material-console-line: **양방향 스트리밍 데모 애플리케이션**

    ---

    텍스트/오디오/이미지 멀티모달을 지원하는 ADK 양방향 스트리밍의 프로덕션 수준 레퍼런스 구현입니다. FastAPI 기반으로 실시간 WebSocket 통신, 자동 전사, Google Search 도구 호출, 전체 스트리밍 라이프사이클 관리를 보여줍니다. 개발 가이드 시리즈 전반에서 이 데모를 참조합니다.

    - [ADK 양방향 스트리밍 데모](https://github.com/google/adk-samples/tree/main/python/agents/bidi-demo)

-   :material-console-line: **블로그 게시물: ADK 양방향 스트리밍 비주얼 가이드**

    ---

    ADK 양방향 스트리밍 기반 실시간 멀티모달 AI 에이전트 개발을 시각적으로 설명한 가이드입니다. 직관적인 다이어그램과 일러스트를 통해 Bidi-streaming의 동작 방식과 인터랙티브 AI 에이전트 구축 방법을 이해할 수 있습니다.

    - [블로그 게시물: ADK 양방향 스트리밍 비주얼 가이드](https://medium.com/google-cloud/adk-bidi-streaming-a-visual-guide-to-real-time-multimodal-ai-agent-development-62dd08c81399)

-   :material-console-line: **양방향 스트리밍 개발 가이드 시리즈**

    ---

    ADK 기반 양방향 스트리밍 개발을 더 깊게 다루는 시리즈입니다. 기본 개념과 사용 사례, 핵심 API, 엔드투엔드 애플리케이션 설계를 배울 수 있습니다.

    - [1부: ADK 양방향 스트리밍 소개](dev-guide/part1.md) - Bidi-streaming 기초, Live API 기술, ADK 아키텍처 구성 요소, FastAPI 예제를 통한 전체 라이프사이클
    - [2부: LiveRequestQueue로 메시지 전송](dev-guide/part2.md) - 업스트림 메시지 흐름, 텍스트/오디오/비디오 전송, 활동 신호, 동시성 패턴
    - [3부: run_live() 이벤트 처리](dev-guide/part3.md) - 이벤트 처리, 텍스트/오디오/전사 처리, 자동 도구 실행, 멀티 에이전트 워크플로
    - [4부: RunConfig 이해하기](dev-guide/part4.md) - 응답 모달리티, 스트리밍 모드, 세션 관리/재개, 컨텍스트 윈도우 압축, 쿼터 관리
    - [5부: 오디오/이미지/비디오 사용 방법](dev-guide/part5.md) - 오디오 스펙, 모델 아키텍처, 오디오 전사, VAD(음성 활동 감지), 능동/감성 대화 기능

-   :material-console-line: **스트리밍 도구**

    ---

    스트리밍 도구를 사용하면 도구(함수)가 중간 결과를 에이전트로 스트리밍할 수 있고, 에이전트는 그 중간 결과에 반응할 수 있습니다. 예를 들어 주가 변화를 모니터링해 에이전트가 반응하도록 하거나, 비디오 스트림 변화를 감지해 보고하도록 만들 수 있습니다.

    - [스트리밍 도구](streaming-tools.md)

-   :material-console-line: **블로그 게시물: Google ADK + Vertex AI Live API**

    ---

    이 글은 ADK의 양방향 스트리밍(live)을 사용해 실시간 오디오/비디오 스트리밍을 구현하는 방법을 보여줍니다. `LiveRequestQueue`를 사용해 사용자 정의 대화형 AI 에이전트를 구축하는 Python 서버 예제를 제공합니다.

    - [블로그 게시물: Google ADK + Vertex AI Live API](https://medium.com/google-cloud/google-adk-vertex-ai-live-api-125238982d5e)

-   :material-console-line: **블로그 게시물: Claude Code Skills로 ADK 개발 가속화**

    ---

    Claude Code Skills를 사용해 ADK 개발을 가속하는 방법을 설명하며, 양방향 스트리밍 채팅 앱 구축 예제를 제공합니다. AI 기반 코딩 보조를 활용해 더 좋은 에이전트를 더 빠르게 개발하는 방법을 다룹니다.

    - [블로그 게시물: Claude Code Skills로 ADK 개발 가속화](https://medium.com/@kazunori279/supercharge-adk-development-with-claude-code-skills-d192481cbe72)

</div>
