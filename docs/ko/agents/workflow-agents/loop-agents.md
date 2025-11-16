# 루프 에이전트

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

`LoopAgent`는 하위 에이전트를 루프(즉, 반복적으로)로 실행하는 워크플로우 에이전트입니다. 이 에이전트는 명시된 반복 횟수만큼 또는 종료 조건이 충족될 때까지 **에이전트 시퀀스를 반복적으로 실행합니다**.

코드 수정과 같이 워크플로우에 반복이나 반복적인 개선이 포함될 때 `LoopAgent`를 사용하세요.

### 예시

*   음식 이미지를 생성하는 에이전트를 구축하려는데, 특정 개수의 아이템(예: 바나나 5개)을 생성하려 할 때 다른 개수의 아이템(예: 바나나 7개가 있는 이미지)을 생성하는 경우가 있다고 가정해 봅시다. 당신에게는 `이미지 생성하기`와 `음식 아이템 개수 세기`라는 두 가지 도구가 있습니다. 명시된 개수의 아이템을 정확하게 생성하거나 특정 반복 횟수에 도달할 때까지 이미지 생성을 계속하고 싶기 때문에, `LoopAgent`를 사용하여 에이전트를 구축해야 합니다.

다른 [워크플로우 에이전트](index.md)와 마찬가지로, `LoopAgent`는 LLM으로 구동되지 않으므로 실행 방식이 결정적(deterministic)입니다. 하지만 워크플로우 에이전트는 내부 로직이 아닌 실행(즉, 루프 내 실행)에만 관여합니다. 워크플로우 에이전트의 도구나 하위 에이전트는 LLM을 활용할 수도 있고, 그렇지 않을 수도 있습니다.

### 작동 방식

`LoopAgent`의 `Run Async` 메서드가 호출되면 다음 작업을 수행합니다.

1.  **하위 에이전트 실행:** 하위 에이전트 목록을 _순서대로_ 순회합니다. _각_ 하위 에이전트에 대해 해당 에이전트의 `Run Async` 메서드를 호출합니다.
2.  **종료 확인:**

    _매우 중요한 점은_, `LoopAgent` 자체는 언제 루프를 멈출지 본질적으로 결정하지 않는다는 것입니다. 무한 루프를 방지하기 위해 _반드시_ 종료 메커니즘을 구현해야 합니다. 일반적인 전략은 다음과 같습니다.

    *   **최대 반복 횟수(Max Iterations)**: `LoopAgent`에 최대 반복 횟수를 설정합니다. **루프는 해당 횟수만큼 반복된 후 종료됩니다**.
    *   **하위 에이전트의 종료 신호(Escalation from sub-agent)**: 하나 이상의 하위 에이전트가 특정 조건("문서 품질이 충분히 좋은가?", "합의에 도달했는가?")을 평가하도록 설계합니다. 조건이 충족되면, 하위 에이전트는 종료 신호(예: 커스텀 이벤트 발생, 공유 컨텍스트에 플래그 설정, 특정 값 반환 등)를 보낼 수 있습니다.

![Loop Agent](../../assets/loop-agent.png)

### 전체 예시: 반복적인 문서 개선

문서를 반복적으로 개선하려는 시나리오를 상상해 보세요.

*   **작성 에이전트(Writer Agent):** 특정 주제에 대한 초안을 생성하거나 개선하는 `LlmAgent`입니다.
*   **비평 에이전트(Critic Agent):** 초안을 비평하고 개선할 부분을 식별하는 `LlmAgent`입니다.

    ```py
    LoopAgent(sub_agents=[WriterAgent, CriticAgent], max_iterations=5)
    ```

이 설정에서 `LoopAgent`는 반복적인 프로세스를 관리합니다. `Critic Agent`는 **문서가 만족스러운 품질 수준에 도달했을 때 "STOP" 신호를 반환하도록 설계**하여 추가적인 반복을 막을 수 있습니다. 또는, `max_iterations` 매개변수를 사용하여 프로세스를 고정된 횟수로 제한하거나, 중지 결정을 내리기 위한 외부 로직을 구현할 수도 있습니다. **루프는 최대 5번 실행**되어 반복적인 개선이 무한정 계속되지 않도록 보장합니다.

???+ "전체 코드"

    === "Python"
        ```py
        --8<-- "examples/python/snippets/agents/workflow-agents/loop_agent_doc_improv_agent.py:init"
        ```

    === "Go"
        ```go
        --8<-- "examples/go/snippets/agents/workflow-agents/loop/main.go:init"
        ```

    === "Java"
        ```java
        --8<-- "examples/java/snippets/src/main/java/agents/workflow/LoopAgentExample.java:init"
        ```
