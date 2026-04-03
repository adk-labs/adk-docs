# 빠른 시작: A2A를 통해 원격 에이전트 사용하기

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-java">Java</span><span class="lst-preview">실험적</span>
</div>

이 빠른 시작은 모든 개발자에게 가장 일반적인 출발점인 **"원격 에이전트가 있는데, 내 ADK 에이전트가 A2A를 통해 이를 사용하게 하려면 어떻게 해야 하나요?"**에 대해 다룹니다. 이는 서로 다른 에이전트가 협력하고 상호작용해야 하는 복잡한 멀티 에이전트 시스템을 구축하는 데 중요합니다.

## 개요

이 샘플은 Agent Development Kit(ADK) for Java의 **Agent2Agent(A2A)** 아키텍처를 보여 주며, 여러 에이전트가 함께 복잡한 작업을 처리하는 방법을 소개합니다.

```text
┌─────────────────┐    ┌─────────────────┐    ┌────────────────────────┐
│   Root Agent    │───▶│   Roll Agent    │    │   Remote Prime Agent   │
│   (Local)       │    │   (Local)       │    │   (localhost:8001)     │
│                 │───▶│                 │◀───│                        │
└─────────────────┘    └─────────────────┘    └────────────────────────┘
```

A2A Basic 샘플은 다음으로 구성됩니다.

- **Root Agent** (`root_agent`): 전문화된 하위 에이전트에 작업을 위임하는 메인 오케스트레이터
- **Roll Agent** (`roll_agent`): 주사위 굴리기 작업을 처리하는 로컬 하위 에이전트
- **Prime Agent** (`prime_agent`): 숫자가 소수인지 확인하는 원격 A2A 에이전트이며, 별도의 A2A 서버에서 실행됩니다

## ADK Java SDK로 에이전트 사용하기

Java에서는 요청을 수동으로 생성하는 대신, ADK가 공식 A2A SDK `Client`를 `RemoteA2AAgent` 엔터티 위에 정확히 래핑하여 사용합니다. 현재 Java SDK는 A2A Protocol 0.3을 사용합니다.

### 1. 샘플 코드 가져오기 { #getting-the-sample-code }

이 빠른 시작과 일치하는 Java 네이티브 샘플은 `adk-java` 소스 코드의 `contrib/samples/a2a_basic` 아래에서 찾을 수 있습니다.

[**`a2a_basic`** 샘플](https://github.com/google/adk-java/tree/main/contrib/samples/a2a_basic)로 이동할 수 있습니다.

```bash
cd contrib/samples/a2a_basic
```

### 2. 원격 Prime Agent 서버 시작하기 { #start-the-remote-prime-agent-server }

ADK 에이전트가 A2A를 통해 원격 에이전트를 사용할 수 있음을 보여 주려면 먼저 원격 에이전트 서버가 실행 중이어야 합니다. 원하는 언어로 직접 커스텀 A2A 서버를 작성할 수도 있지만, ADK는 `a2a_server` 샘플을 제공하며, 이 샘플은 `:9090`에서 에이전트를 호스팅하는 Quarkus 서비스를 시작합니다.

```bash
# adk-java 루트에서, 9090 포트의 사전 구성된 Quarkus 원격 서비스를 시작
./mvnw -f contrib/samples/a2a_server/pom.xml quarkus:dev
```

정상적으로 실행되면 에이전트는 로컬 HTTP 엔드포인트로 접근할 수 있습니다.

### 3. 원격 에이전트에 필요한 에이전트 카드 확인하기 { #look-out-for-the-required-agent-card-of-the-remote-agent }

A2A Protocol에서는 각 에이전트가 네트워크의 다른 노드에 자신이 하는 일을 설명하는 에이전트 카드를 가져야 합니다. A2A 서버에서는 에이전트 카드가 부팅 시 동적으로 생성되어 정적으로 호스팅됩니다.

ADK Java 웹서비스의 경우, 에이전트 카드는 일반적으로 기본 URL을 기준으로 표준 [`.well-known/agent-card.json`](http://localhost:9090/.well-known/agent-card.json) 엔드포인트 형식을 사용해 동적으로 접근할 수 있습니다.

### 4. 메인(소비) 에이전트 실행하기 { #run-the-main-consuming-agent }

다른 터미널에서 클라이언트 에이전트를 실행할 수 있습니다.

```bash
./mvnw -f contrib/samples/a2a_basic/pom.xml exec:java -Dexec.args="http://localhost:9090"
```

#### 동작 방식

메인 에이전트는 원격 에이전트(`prime_agent` 예시)를 사용하기 위해 필요한 A2A JSON-RPC 전송 래퍼에 접근합니다. 아래에서 볼 수 있듯이, 대상 호스트에서 `AgentCard`를 조회하여 공식 A2A `Client` 내부에 로컬로 등록합니다.

```java title="A2aConsumerSnippet.java"
--8<-- "examples/java/snippets/src/main/java/a2a/A2aConsumerSnippet.java:new-prime-agent"
```

그런 다음 원격 에이전트 인스턴스를 자연스럽게 에이전트 빌더에 전달할 수 있으며, 다른 표준 ADK 하위 에이전트처럼 작동합니다. ADK가 전송 계층의 모든 변환 로직을 내부적으로 처리합니다.

```java title="A2aConsumerSnippet.java"
--8<-- "examples/java/snippets/src/main/java/a2a/A2aConsumerSnippet.java:new-root-agent"
```

## 다음 단계

이제 원격 에이전트를 A2A 서버를 통해 사용하는 에이전트를 만들었습니다. 다음 단계는 자신의 Java 에이전트를 노출하는 방법을 배우는 것입니다.

- [**A2A 빠른 시작(노출) for Java**](./quickstart-exposing-java.md): 기존 에이전트를 노출하여 다른 에이전트가 A2A Protocol을 통해 사용할 수 있도록 하는 방법을 알아봅니다.
