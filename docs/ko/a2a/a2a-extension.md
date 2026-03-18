# 안정성 향상을 위한 A2A 확장

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python 1.27.0</span>
</div>

ADK는 업데이트된 [A2aAgentExecutor](https://github.com/google/adk-python/blob/main/src/google/adk/a2a/executor/a2a_agent_executor_impl.py)
클래스를 통해 Agent2Agent(A2A) 지원을 위한 확장을 제공하며, 이를 통해 메시지와 데이터 처리를 개선합니다.
업데이트된 버전에는 핵심 에이전트 실행 로직의 아키텍처 변경사항과 A2A의 데이터 처리 개선을 위한 확장이 포함되어 있으며,
기존 A2A 에이전트와의 하위 호환성도 유지합니다.

A2A 확장 옵션을 활성화하면 서버가 업데이트된 agent executor 구현을 사용하도록 지시합니다.
이 업데이트는 여러 일반적인 장점을 제공하지만, 특히 A2A와 ADK가 모두 스트리밍 모드로 동작할 때
레거시 A2A-ADK 구현에서 발견된 중요한 한계를 해결합니다. 새 구현은 다음 문제를 해결합니다.

-   **메시지 중복:** 사용자 메시지가 작업 히스토리에 중복 저장되는 것을 방지합니다.
-   **출력 오분류:** 원격 에이전트의 ADK 출력이 이벤트 thought로 잘못 변환되는 것을 막습니다.
-   **하위 에이전트 데이터 손실:** 원격 에이전트의 하위 에이전트 트리에 여러 에이전트가 중첩되어 있어도 원격 에이전트의 ADK 출력이 안정적으로 보존되도록 하여 데이터 손실을 없앱니다.

## 클라이언트 측 확장 활성화

클라이언트는 전송 계층에서 정의한 [A2A 확장](https://a2a-protocol.org/latest/topics/extensions/) 활성화 메커니즘을 통해 이 확장을 사용하겠다는 의사를 표시합니다.
JSON-RPC 및 HTTP 전송에서는 `X-A2A-Extensions` HTTP 헤더를 통해 이를 지정합니다.
gRPC에서는 `X-A2A-Extensions` 메타데이터 값을 통해 이를 지정합니다.

확장을 활성화하려면 클라이언트가 `use_legacy=False`로 `RemoteA2aAgent`를 생성하면 됩니다.
이렇게 하면 전송되는 요청의 요청 확장 목록에 `https://google.github.io/adk-docs/a2a/a2a-extension/`가 추가됩니다.
이 확장을 활성화한다는 것은 서버가 새 agent executor 구현을 사용한다는 뜻입니다.

```python
from google.adk.agents import RemoteA2aAgent

remote_agent = RemoteA2aAgent(
    name="remote_agent",
    url="http://localhost:8000/a2a/remote_agent",
    use_legacy=False,
)
```

요청에서 a2a 확장이 감지되면 `A2aAgentExecutor`는 기본적으로 새 구현을 사용합니다.
새 agent executor 구현을 사용하지 않으려면, 클라이언트가 이 확장을 보내지 않도록 하면 됩니다(`use_legacy=True`로 `RemoteA2aAgent`를 생성).
또는 서버의 `A2aAgentExecutor`를 `use_legacy=True`로 생성할 수도 있습니다.

## 동작 방식

요청을 받으면 [A2aAgentExecutor](https://github.com/google/adk-python/blob/main/src/google/adk/a2a/executor/a2a_agent_executor.py)가 확장을 감지합니다.
클라이언트가 새 agent executor 로직 사용을 요청하고 있음을 이해하고, 요청을 그에 맞는 새 구현으로 라우팅합니다.
요청이 실제로 반영되었는지 확인할 수 있도록, 이 확장은 클라이언트에게 되돌려 보내는 응답 메타데이터의 "activated extensions" 목록과 A2A 이벤트의 메타데이터에 포함됩니다.

## Agent Card 정의

에이전트는 AgentCapabilities.extensions 목록 안의 AgentCard를 통해 이 확장 기능을 광고합니다.

예시 AgentExtension 블록:

```json
{
  "uri": "https://google.github.io/adk-docs/a2a/a2a-extension/",
  "description": "새 agent executor 구현을 사용할 수 있는 기능",
  "required": false
}
```
