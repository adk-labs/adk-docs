# 에이전트 런타임

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

ADK는 개발 중 에이전트를 실행하고 테스트하는 여러 방법을 제공합니다. 개발 워크플로에 가장 잘 맞는 방법을 선택하세요.

## 에이전트 실행 방법

<div class="grid cards" markdown>

-   :material-web:{ .lg .middle } **Dev UI**

    ---

    `adk web`을 사용해 브라우저 기반 인터페이스에서 에이전트와 상호작용할 수 있습니다.

    [:octicons-arrow-right-24: 웹 인터페이스 사용하기](web-interface.md)

-   :material-console:{ .lg .middle } **Command Line**

    ---

    `adk run`을 사용해 터미널에서 직접 에이전트와 상호작용할 수 있습니다.

    [:octicons-arrow-right-24: 명령줄 사용하기](command-line.md)

-   :material-api:{ .lg .middle } **API Server**

    ---

    `adk api_server`를 사용해 에이전트를 RESTful API로 노출할 수 있습니다.

    [:octicons-arrow-right-24: API 서버 사용하기](api-server.md)

-   :material-access-point:{ .lg .middle } **앰비언트 에이전트**

    ---

    이벤트를 처리하고, 시스템을 모니터링하며, 사람의 개입 없이 비동기적으로
    응답하는 자율 에이전트를 빌드합니다.

    [:octicons-arrow-right-24: 앰비언트 에이전트 사용하기](ambient-agents.md)

</div>

## 기술 레퍼런스

런타임 구성과 동작에 대한 더 자세한 정보는 다음 페이지를 참조하세요.

- **[Event Loop](event-loop.md)**: ADK를 구동하는 핵심 이벤트 루프와 yield/pause/resume 사이클을 이해합니다.
- **[Resume Agents](resume.md)**: 이전 상태에서 에이전트 실행을 재개하는 방법을 배웁니다.
- **[Cancel Agent Runs](cancel.md)**: AbortSignal(TypeScript)을 사용해 실행 중인 에이전트 호출을 정상적으로 취소합니다.
- **[Runtime Config](runconfig.md)**: RunConfig로 런타임 동작을 구성합니다.
