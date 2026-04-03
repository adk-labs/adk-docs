---
hide:
  - navigation
  - toc
---

<div style="text-align: center;">
  <div class="centered-logo-text-group">
    <img src="assets/agent-development-kit.png" alt="Agent Development Kit Logo" width="100">
    <h1>Agent Development Kit</h1>
  </div>
</div>

Agent Development Kit (ADK)는 **AI 에이전트 개발 및 배포**를 위한 유연한 모듈식 프레임워크입니다. Gemini 및 Google 생태계에 최적화되어 있지만, ADK는 **모델에 구애받지 않고(model-agnostic)**, **배포 환경에 제약이 없으며(deployment-agnostic)**, **다른 프레임워크와의 호환성**을 위해 구축되었습니다. ADK는 에이전트 개발이 일반적인 소프트웨어 개발처럼 느껴지도록 설계되었으며, 개발자가 간단한 작업부터 복잡한 워크플로에 이르는 에이전트 아키텍처를 쉽게 생성, 배포 및 오케스트레이션할 수 있도록 지원합니다.

??? tip "새 소식: ADK Go 1.0.0 출시!"

    ADK Go 1.0.0 릴리스에는 OpenTelemetry 통합, 플러그인을 활용한
    자가 복구 로직, 향상된 사람 입력 지원 등 여러 주요 기능이 포함됩니다.
    자세한 내용은
    [ADK Go v1.0 발표](https://developers.googleblog.com/adk-go-10-arrives/)
    에서 확인하세요.

??? tip "새 소식: ADK Java 1.0.0 출시!"

    ADK Java 1.0.0을 이제 사용할 수 있습니다. 이번 릴리스에는 여러 버그 수정과
    개선 사항이 포함되어 있습니다. 자세한 내용은
    [블로그 발표](https://developers.googleblog.com/announcing-adk-for-java-100-building-the-future-of-ai-agents-in-java/)
    를 참고하세요. 최신 개선 사항을 활용하고 애플리케이션 성능을 최적으로 유지하려면
    ADK Java 1.0.0으로 업그레이드하세요.

<div id="centered-install-tabs" class="install-command-container" markdown="1">

<p class="get-started-text" style="text-align: center;">시작하기:</p>

=== "Python"
    <br>
    <p style="text-align: center;">
    <code>pip install google-adk</code>
    </p>

=== "Go"
    <br>
    <p style="text-align: center;">
    <code>go get google.golang.org/adk</code>
    </p>

=== "TypeScript"
    <br>
    <p style="text-align: center;">
    <code>npm install @google/adk</code>
    </p>

=== "Java"

    ```xml title="pom.xml"
    <dependency>
        <groupId>com.google.adk</groupId>
        <artifactId>google-adk</artifactId>
        <version>1.0.0</version>
    </dependency>
    ```

    ```gradle title="build.gradle"
    dependencies {
        implementation 'com.google.adk:google-adk:1.0.0'
    }
    ```

</div>

<p style="text-align:center;">
  <a href="/get-started/python/" class="md-button" style="margin:3px">Python으로 시작하기</a>
  <a href="/get-started/typescript/" class="md-button" style="margin:3px">TypeScript로 시작하기</a>
  <a href="/get-started/go/" class="md-button" style="margin:3px">Go로 시작하기</a>
  <a href="/get-started/java/" class="md-button" style="margin:3px">Java로 시작하기</a>
</p>

---

## 더 알아보기

[:fontawesome-brands-youtube:{.youtube-red-icon} "Introducing Agent Development Kit" 시청하기!](https://www.youtube.com/watch?v=zgrOwow_uTQ){:target="_blank" rel="noopener noreferrer"}

<div class="grid cards" markdown>

-   :material-transit-connection-variant: **유연한 오케스트레이션**

    ---

    예측 가능한 파이프라인을 위해 워크플로 에이전트(`Sequential`, `Parallel`, `Loop`)를 사용하여 워크플로를 정의하거나, 적응형 동작을 위해 LLM 기반의 동적 라우팅(`LlmAgent` transfer)을 활용하세요.

    [**에이전트 알아보기**](agents/index.md)

-   :material-graph: **멀티 에이전트 아키텍처**

    ---

    여러 전문 에이전트를 계층적으로 구성하여 모듈식의 확장 가능한 애플리케이션을 구축하세요. 복잡한 조정 및 위임이 가능합니다.

    [**멀티 에이전트 시스템 탐색**](agents/multi-agents.md)

-   :material-toolbox-outline: **풍부한 도구 생태계**

    ---

    에이전트에 다양한 기능을 장착하세요. 사전 구축된 도구(검색, 코드 실행)를 사용하거나, 커스텀 함수를 생성하고, 타사 라이브러리를 통합하거나, 심지어 다른 에이전트를 도구로 사용할 수도 있습니다.

    [**도구 및 통합 둘러보기**](integrations/index.md)

-   :material-rocket-launch-outline: **배포 준비 완료**

    ---

    에이전트를 컨테이너화하여 어디에든 배포하세요. 로컬에서 실행하거나, Vertex AI Agent Engine으로 확장하거나, Cloud Run 또는 Docker를 사용하여 커스텀 인프라에 통합할 수 있습니다.

    [**에이전트 배포**](deploy/index.md)

-   :material-clipboard-check-outline: **내장된 평가 기능**

    ---

    최종 응답 품질과 단계별 실행 궤적(trajectory) 모두를 사전에 정의된 테스트 케이스와 비교하여 에이전트 성능을 체계적으로 평가하세요.

    [**에이전트 평가**](evaluate/index.md)

-   :material-console-line: **안전하고 보안이 강력한 에이전트 구축**

    ---

    에이전트 설계에 보안 및 안전 패턴과 모범 사례를 구현하여 강력하고 신뢰할 수 있는 에이전트를 구축하는 방법을 알아보세요.

    [**안전 및 보안**](safety/index.md)

</div>
