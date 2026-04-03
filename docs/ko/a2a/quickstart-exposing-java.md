# 빠른 시작: A2A를 통해 원격 에이전트 노출하기

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-java">Java</span><span class="lst-preview">실험적</span>
</div>

이 빠른 시작은 모든 개발자에게 가장 일반적인 출발점인 **"에이전트가 있는데, 다른 에이전트가 A2A를 통해 내 에이전트를 사용하게 하려면 어떻게 해야 하나요?"**에 대해 다룹니다. 이는 서로 다른 에이전트가 협력하고 상호작용해야 하는 복잡한 멀티 에이전트 시스템을 구축하는 데 중요합니다.

## 개요

이 샘플은 Quarkus를 사용해 ADK 에이전트를 노출하여, 다른 에이전트가 A2A Protocol을 사용해 이를 소비할 수 있게 하는 방법을 보여 줍니다.

Java에서는 ADK A2A extension에 의존해 A2A 서버를 네이티브로 빌드합니다. 이 방식은 Quarkus 프레임워크를 사용하므로, 표준 Quarkus `@ApplicationScoped` 바인딩 안에서 에이전트를 직접 설정하기만 하면 됩니다.

```text
┌─────────────────┐                             ┌───────────────────────────────┐
│   Root Agent    │       A2A Protocol          │ A2A-Exposed Check Prime Agent │
│                 │────────────────────────────▶│       (localhost:9090)        │
└─────────────────┘                             └───────────────────────────────┘
```

## Quarkus로 원격 에이전트 노출하기

Quarkus를 사용하면 들어오는 HTTP JSON-RPC 페이로드나 세션을 수동으로 다루지 않고도 에이전트를 A2A 실행 엔드포인트에 매핑할 수 있습니다.

### 1. 샘플 코드 가져오기 { #getting-the-sample-code }

시작하는 가장 빠른 방법은 [**`adk-java`** 저장소](https://github.com/google/adk-java)의 `contrib/samples/a2a_server` 폴더 안에 있는 독립형 Quarkus 앱을 확인하는 것입니다.

```bash
cd contrib/samples/a2a_server
```

### 2. 동작 방식

핵심 런타임은 제공되는 `AgentExecutor`를 사용하며, 네이티브 `BaseAgent`를 설정하는 CDI `@Produces` 빈을 빌드하도록 요구합니다. Quarkus A2A extension은 이를 감지하고 엔드포인트를 자동으로 연결합니다.

```java title="A2aExposingSnippet.java"
--8<-- "examples/java/snippets/src/main/java/a2a/A2aExposingSnippet.java:a2a-launcher"
```

앱은 HTTP로 마운트된 `/a2a/remote/v1/message:send` 경로로 들어오는 JSON-RPC 호출을 자동으로 처리하고, 일부 내용, 기록, 컨텍스트를 직접 `BaseAgent` 흐름으로 전달합니다.

### 3. Remote A2A Agent 서버 시작하기 { #start-the-remote-a2a-agent-server }

네이티브 ADK 구조 안에서는 Quarkus 개발 모드 작업을 실행할 수 있습니다.

```bash
./mvnw -f contrib/samples/a2a_server/pom.xml quarkus:dev
```

실행되면 Quarkus가 A2A 호환 REST 경로를 자동으로 호스팅합니다. 수동 `curl`을 사용하면 네이티브 A2A 사양으로 페이로드를 즉시 스모크 테스트할 수 있습니다.

```bash
curl -X POST http://localhost:9090 \
  -H "Content-Type: application/json" \
  -d '{
        "jsonrpc": "2.0",
        "id": "cli-check",
        "method": "message/send",
        "params": {
          "message": {
            "kind": "message",
            "contextId": "cli-demo-context",
            "messageId": "cli-check-id",
            "role": "user",
            "parts": [
              { "kind": "text", "text": "Is 3 prime?" }
            ]
          }
        }
      }'
```

### 4. 원격 에이전트가 실행 중인지 확인하기 { #check-that-your-remote-agent-is-running }

적절한 에이전트 카드는 다음의 표준 경로에서 자동으로 노출됩니다.
[http://localhost:9090/.well-known/agent-card.json](http://localhost:9090/.well-known/agent-card.json)

응답 JSON 안에서 에이전트 설정값이 동적으로 반영된 이름을 볼 수 있어야 합니다.

## 다음 단계

이제 A2A를 통해 에이전트를 노출했습니다. 다음 단계는 다른 에이전트 오케스트레이터에서 이를 네이티브로 소비하는 방법을 배우는 것입니다.

- [**A2A 빠른 시작(소비) for Java**](./quickstart-consuming-java.md): 에이전트 오케스트레이터 래퍼가 노출된 서비스에 하향 연결하는 방법을 알아봅니다.
