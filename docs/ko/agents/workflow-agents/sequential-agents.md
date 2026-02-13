# 순차적 에이전트

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

`SequentialAgent`는 하위 에이전트를 목록에 명시된 순서대로 실행하는 [워크플로우 에이전트](index.md)입니다.
실행이 고정된, 엄격한 순서로 이루어져야 할 때 `SequentialAgent`를 사용하세요.

### 예시

*   두 가지 도구, 즉 `페이지 콘텐츠 가져오기(Get Page Contents)`와 `페이지 요약하기(Summarize Page)`를 사용하여 모든 웹페이지를 요약할 수 있는 에이전트를 구축한다고 가정해 봅시다. 에이전트는 항상 `페이지 요약하기`를 호출하기 전에 `페이지 콘텐츠 가져오기`를 호출해야 하므로(`아무것도 없는 상태에서 요약할 수는 없으므로!`), `SequentialAgent`를 사용하여 에이전트를 구축해야 합니다.

다른 [워크플로우 에이전트](index.md)와 마찬가지로 `SequentialAgent`는 LLM으로 구동되지 않으므로 실행 방식이 결정적(deterministic)입니다. 하지만 워크플로우 에이전트는 내부 로직이 아닌 실행(즉, 순차 실행)에만 관여합니다. 워크플로우 에이전트의 도구나 하위 에이전트는 LLM을 활용할 수도 있고, 그렇지 않을 수도 있습니다.

### 작동 방식

`SequentialAgent`의 `Run Async` 메서드가 호출되면 다음 작업을 수행합니다.

1.  **반복(Iteration):** 제공된 순서대로 하위 에이전트 목록을 순회합니다.
2.  **하위 에이전트 실행(Sub-Agent Execution):** 목록의 각 하위 에이전트에 대해 해당 하위 에이전트의 `Run Async` 메서드를 호출합니다.

![Sequential Agent](../../assets/sequential-agent.png){: width="600"}

### 전체 예시: 코드 개발 파이프라인

단순화된 코드 개발 파이프라인을 생각해 봅시다.

*   **코드 작성 에이전트(Code Writer Agent):** 명세를 기반으로 초기 코드를 생성하는 LLM 에이전트입니다.
*   **코드 검토 에이전트(Code Reviewer Agent):** 생성된 코드의 오류, 스타일 문제, 모범 사례 준수 여부를 검토하는 LLM 에이전트입니다. 이 에이전트는 코드 작성 에이전트의 출력을 입력으로 받습니다.
*   **코드 리팩터링 에이전트(Code Refactorer Agent):** 검토된 코드(와 검토자의 의견)를 받아 품질을 개선하고 문제를 해결하기 위해 리팩터링하는 LLM 에이전트입니다.

이런 경우 `SequentialAgent`가 완벽하게 들어맞습니다.

```py
SequentialAgent(sub_agents=[CodeWriterAgent, CodeReviewerAgent, CodeRefactorerAgent])
```

이를 통해 코드가 작성되고, *그 다음* 검토되고, *마지막으로* 리팩터링되는 엄격하고 신뢰할 수 있는 순서를 보장합니다. **각 하위 에이전트의 출력은 [출력 키(Output Key)](../llm-agents.md#structuring-data-input_schema-output_schema-output_key)를 통해 상태(state)에 저장되어 다음 에이전트로 전달됩니다.**

!!! note "공유된 Invocation Context"
    `SequentialAgent`는 각 하위 에이전트에 동일한 `InvocationContext`를 전달합니다. 이는 모든 하위 에이전트가 임시 (`temp:`) 네임스페이스를 포함한 동일한 세션 상태를 공유한다는 것을 의미하며, 단일 턴 내에서 단계 간 데이터 전달을 용이하게 합니다.

???+ "코드"

    === "Python"
        ```py
        --8<-- "examples/python/snippets/agents/workflow-agents/sequential_agent_code_development_agent.py:init"
        ```

    === "Go"
        ```go
        --8<-- "examples/go/snippets/agents/workflow-agents/sequential/main.go:init"
        ```

    === "Java"
        ```java
        --8<-- "examples/java/snippets/src/main/java/agents/workflow/SequentialAgentExample.java:init"
        ```