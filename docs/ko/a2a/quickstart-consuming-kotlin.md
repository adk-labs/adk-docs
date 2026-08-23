# 빠른 시작: A2A를 통해 원격 에이전트 사용하기

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-kotlin">Kotlin</span><span class="lst-preview">실험적 기능</span>
</div>

이 빠른 시작에서는 모든 개발자가 가장 흔하게 마주하는 질문인 **"원격 에이전트가 있을 때 내 ADK 에이전트가 A2A로 이를 활용하려면 어떻게 해야 할까?"**를 다룹니다. 이는 여러 에이전트가 협업하는 복잡한 다중 에이전트 시스템을 구축할 때 핵심적인 구성 요소입니다.

## 개요

이 샘플은 Kotlin용 Agent Development Kit (ADK)에서 **Agent2Agent (A2A)** 아키텍처를 활용해, 로컬 에이전트가 외부에서 실행 중인 다른 에이전트에 작업을 위임하는 방법을 보여줍니다.

```text
┌─────────────────┐         ┌────────────────────────┐
│   Root Agent    │────────▶│   Remote Prime Agent   │
│   (Local)       │◀────────│   (localhost:8001)     │
└─────────────────┘         └────────────────────────┘
```

- **Root Agent** (`root_agent`): 하위 에이전트에게 작업을 위임하는 로컬 오케스트레이터
- **Prime Agent** (`prime_agent`): 숫자가 소수인지 확인하는 원격 A2A 에이전트로, 별도의 A2A 서버에서 실행됨

## A2A 종속 항목 추가

A2A 지원은 별도의 아티팩트로 제공됩니다. `A2AAgent`의 `httpClient` 매개변수는 기본적으로 `JdkA2AHttpClient()`로 설정되므로 컴파일 클래스패스에 A2A SDK 클라이언트도 필요합니다.

```kotlin title="build.gradle.kts"
implementation("com.google.adk:google-adk-kotlin-a2a:0.8.0")
implementation("org.a2aproject.sdk:a2a-java-sdk-client:1.0.0.Final")
```

## 원격 에이전트 서버 시작

원격 에이전트를 사용하려면 먼저 실행 중인 에이전트가 필요합니다. adk-kotlin은 아직 A2A를 통해 에이전트를 외부에 노출할 수 없으므로 서버는 다른 곳에서 실행해야 합니다. A2A는 유선 프로토콜(wire protocol)이므로 어떤 언어든 사용할 수 있습니다.

adk-python의 `a2a_basic` 샘플은 이 페이지에서 위임하는 소수 판별 에이전트를 제공합니다. adk-python 체크아웃 디렉토리에서 다음 명령어를 실행합니다.

```bash
adk api_server --a2a --port 8001 contributing/samples/a2a/a2a_basic/remote_a2a
```

A2A 프로토콜에서는 각 에이전트가 수행하는 작업을 설명하는 **에이전트 카드(Agent card)**를 해당 에이전트 자체 접두사 아래의 잘 알려진(well-known) 경로에 게시해야 합니다.

```text
http://localhost:8001/a2a/check_prime_agent/.well-known/agent-card.json
```

계속하기 전에 카드가 접근 가능한지 확인하세요.

```bash
curl http://localhost:8001/a2a/check_prime_agent/.well-known/agent-card.json
```

!!! note "이 클라이언트가 통신할 수 있는 서버"

    Kotlin 클라이언트는 **A2A 1.0** 카드를 읽으므로 카드는 각 항목에 `protocolBinding`이 있는 `supportedInterfaces` 배열을 포함해야 합니다. A2A 0.3용으로 작성된 카드는 대신 최상위 `url` 및 `preferredTransport`를 선언하며, `A2AAgent`는 이를 `AgentCardResolutionError: Failed to parse agent card` 오류와 함께 거부합니다.

    샘플의 체크인된 `agent.json`은 0.3 스타일 카드이지만, adk-python은 해당 파일을 그대로 제공하지 않습니다. 시작 시 카드를 파싱하며, a2a-sdk 1.x 환경에서는 이 파싱 과정에서 `url` 및 `preferredTransport`가 `supportedInterfaces`로 승격됩니다. adk-python에는 `a2a-sdk>=0.3.4,<2`가 필요하므로 최신 설치 시 1.x로 확인되어 유선상의 카드는 A2A 1.0 형식이 됩니다.

    adk-java의 `a2a_server` 샘플은 0.3.x A2A SDK에 고정되어 0.3 카드를 제공하므로 이 페이지의 서버로는 작동하지 않습니다.

??? note "대신 자체 카드 제공하기"

    A2A 1.0 카드를 게시하는 모든 서버를 사용할 수 있습니다. 클라이언트가 허용하는 최소 카드는 `<your-base-url>/.well-known/agent-card.json`에서 제공됩니다.

    ```json title=".well-known/agent-card.json"
    {
      "name": "check_prime_agent",
      "description": "Checks whether numbers are prime.",
      "version": "1.0.0",
      "url": "http://localhost:9090",
      "preferredTransport": "JSONRPC",
      "capabilities": { "streaming": true },
      "defaultInputModes": ["text/plain"],
      "defaultOutputModes": ["application/json"],
      "skills": [],
      "supportedInterfaces": [
        { "protocolBinding": "JSONRPC", "url": "http://localhost:9090" }
      ]
    }
    ```

    해당 기본 URL(`http://localhost:9090`)을 아래의 `agentCardUrl`로 전달하세요.

## 원격 에이전트 연결
 
`A2AAgent`는 해당 카드를 가져와 원격 에이전트의 설명과 스트리밍 지원 여부를 확인합니다. 전달하는 `name`은 카드에 적힌 이름과 별개로 내 에이전트 트리 안에서 이 에이전트를 식별하는 고유 이름이 됩니다. `suspend` 함수이므로 코루틴 안에서 호출하세요.
 
```kotlin title="A2AConsumer.kt"
--8<-- "examples/kotlin/snippets/a2a/A2AConsumer.kt:remote_agent"
```
 
이미 `AgentCard`가 있는 경우(예: 직접 생성했거나 정적 카드로 관리하는 경우), 카드를 바로 전달하는 비동기(non-suspending) 생성자 `A2AAgent(name = ..., agentCard = ...)`를 사용할 수 있습니다.

## 하위 에이전트로 사용

반환된 에이전트는 `BaseAgent`이므로 로컬 에이전트와 똑같이 `subAgents`에 들어갑니다. ADK는 네트워크를 통한 A2A 프로토콜을 처리합니다.

```kotlin title="A2AConsumer.kt"
--8<-- "examples/kotlin/snippets/a2a/A2AConsumer.kt:root_agent"
```

## 다음 단계

Kotlin 에이전트를 A2A를 통해 노출하는 기능은 아직 지원되지 않습니다. adk-kotlin은 현재 소비(consuming) 측만 제공합니다. 에이전트를 노출하려면 다른 언어용 빠른 시작 가이드를 참조하세요.

- [**Python용 A2A 빠른 시작 (에이전트 노출)**](./quickstart-exposing.md)
- [**Java용 A2A 빠른 시작 (에이전트 노출)**](./quickstart-exposing-java.md)
