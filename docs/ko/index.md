---
hide:
  - toc
---

<div style="text-align: center;">
  <div class="centered-logo-text-group">
    <img src="assets/agent-development-kit.png" alt="에이전트 개발 키트 로고" width="100">
    <h1>에이전트 개발 키트</h1>
  </div>
</div>

에이전트 개발 키트(ADK)는 **AI 에이전트를 개발하고 배포**하기 위한 유연하고 모듈화된 프레임워크입니다. ADK는 Gemini 및 Google 생태계에 최적화되어 있지만, **특정 모델이나 배포 환경에 종속되지 않으며(model-agnostic, deployment-agnostic)**, **다른 프레임워크와의 호환성**을 고려하여 설계되었습니다. ADK는 에이전트 개발을 소프트웨어 개발처럼 자연스럽게 만들어, 개발자가 간단한 작업부터 복잡한 워크플로우에 이르는 다양한 에이전트 아키텍처를 더 쉽게 만들고, 배포하고, 오케스트레이션할 수 있도록 돕습니다.

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

=== "Java"

    ```xml title="pom.xml"
    <dependency>
        <groupId>com.google.adk</groupId>
        <artifactId>google-adk</artifactId>
        <version>0.3.0</version>
    </dependency>
    ```

    ```gradle title="build.gradle"
    dependencies {
        implementation 'com.google.adk:google-adk:0.3.0'
    }
    ```

</div>

<p style="text-align:center;">
  <a href="/adk-docs/get-started/python/" class="md-button" style="margin:3px">Python으로 시작하기</a>
  <a href="/adk-docs/get-started/go/" class="md-button" style="margin:3px">Go로 시작하기</a>
  <a href="/adk-docs/get-started/java/" class="md-button" style="margin:3px">Java로 시작하기</a>
</p>

---

## 더 알아보기

[:fontawesome-brands-youtube:{.youtube-red-icon} "에이전트 개발 키트 소개" 영상 보기!](https://www.youtube.com/watch?v=zgrOwow_uTQ){:target="_blank" rel="noopener noreferrer"}

<div class="grid cards" markdown>

-   :material-transit-connection-variant: **유연한 오케스트레이션**

    ---

    워크플로우 에이전트(`Sequential`, `Parallel`, `Loop`)를 사용하여 예측 가능한 파이프라인을 정의하거나, LLM 기반의 동적 라우팅(`LlmAgent` 전송)을 활용하여 적응형 동작을 구현할 수 있습니다.

    [**에이전트에 대해 알아보기**](agents/index.md)

-   :material-graph: **다중 에이전트 아키텍처**

    ---

    계층 구조로 여러 전문 에이전트를 구성하여 모듈화되고 확장 가능한 애플리케이션을 구축하세요. 복잡한 조정 및 위임이 가능해집니다.

    [**다중 에이전트 시스템 살펴보기**](agents/multi-agents.md)

-   :material-toolbox-outline: **풍부한 도구 생태계**

    ---

    다양한 기능으로 에이전트를 강화하세요: 사전 빌드된 도구(검색, 코드 실행)를 사용하거나, 커스텀 함수를 만들고, 서드파티 라이브러리를 통합하거나, 다른 에이전트를 도구로 사용할 수도 있습니다.

    [**도구 둘러보기**](tools/index.md)

-   :material-rocket-launch-outline: **배포 준비 완료**

    ---

    에이전트를 컨테이너화하여 어디에나 배포하세요 – 로컬에서 실행하거나, Vertex AI 에이전트 엔진으로 확장하거나, Cloud Run 또는 Docker를 사용하여 커스텀 인프라에 통합할 수 있습니다.

    [**에이전트 배포하기**](deploy/index.md)

-   :material-clipboard-check-outline: **내장된 평가 기능**

    ---

    사전에 정의된 테스트 케이스를 바탕으로 최종 응답 품질과 단계별 실행 궤적을 모두 평가하여 에이전트 성능을 체계적으로 측정합니다.

    [**에이전트 평가하기**](evaluate/index.md)

-   :material-console-line: **안전하고 보안이 강화된 에이전트 구축**

    ---

    에이전트 설계에 보안 및 안전 패턴과 모범 사례를 구현하여 강력하고 신뢰할 수 있는 에이전트를 구축하는 방법을 알아보세요.

    [**안전 및 보안**](safety/index.md)

</div>