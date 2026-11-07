# 동적 에이전트 워크플로

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v2.0.0</span><span class="lst-typescript">TypeScript v2.0.0</span><span class="lst-go">Go v2.0.0</span>
</div>

ADK 프레임워크는 [그래프 기반 워크플로](/graphs/)에 대한 보다 유연하고 강력한 대안으로 워크플로를 프로그래밍 방식으로 정의하는 방법을 제공합니다. 그래프 기반 접근 방식을 사용하면 워크플로 노드로 다단계 정적 프로세스 구조를 편리하게 구성할 수 있습니다. 그러나 반복 루프나 복잡한 분기 로직 등으로 인해 워크플로의 로직 경로가 더 복잡한 경우, 그래프 기반 접근 방식이 요구 사항에 맞지 않거나 관리하기에 너무 번거로워질 수 있습니다.

ADK의 동적 워크플로를 사용하면 그래프 기반 경로 구조를 제쳐두고 선택한 프로그래밍 언어의 모든 기능을 활용하여 워크플로를 구축할 수 있습니다. 동적 워크플로를 사용하면 간단한 데코레이터(Python)나 생성자 함수(Go)로 워크플로를 생성하고, 워크플로 노드를 함수처럼 호출하며, 복잡한 라우팅 로직을 구축할 수 있습니다. ADK 동적 워크플로의 주요 장점은 다음과 같습니다:

-   **유연한 제어 흐름:** 정적 그래프에서는 표현하기 어렵거나 불가능한 루프, 조건문 및 재귀를 사용하여 실행 순서를 동적으로 정의합니다.
-   **프로그래밍 방식의 경험:** 그래프 기반 라우팅 대신 `while` 루프 및 `async/await`(Python) 또는 `for` 루프 및 `workflow.RunNode`(Go)와 같은 익숙한 구문을 사용합니다.
-   **자동 체크포인팅:** 동적 워크플로는 각 노드 실행을 추적합니다. 워크플로를 재개할 때 성공한 하위 노드는 자동으로 건너뛰므로 복잡한 로직이 기본적으로 내구성을 갖추고 재개 가능해집니다.
-   **캡슐화:** 내부적으로 하위 수준 노드를 조합하는 *상위* 노드에 비즈니스 로직을 래핑하여 전체 워크플로를 깔끔하고 관리하기 쉽게 유지합니다.

## 시작하기

다음 동적 워크플로 코드 예제는 함수를 가진 단일 노드를 포함하는 기본 워크플로를 정의하는 방법을 보여줍니다:

=== "Python"

    ```python
    from google.adk import Context
    from google.adk import Workflow
    from google.adk.workflow import node
    from typing import Any

    @node(name="hello_node")
    def my_node(node_input: Any):
        return "Hello World"

    # define a dynamic workflow node
    @node(rerun_on_resume=True)
    async def my_workflow(ctx: Context, node_input: str) -> str:
        # run_node executes a node and returns its output
        result = await ctx.run_node(my_node, node_input="hello")
        return result

    # Run the workflow
    root_agent = Workflow(
        name="root_agent",
        edges=[("START", my_workflow)],
    )
    ```

    이 예제는 편의성과 작성 코드를 최대한 단순하게 유지하기 위해 [***@node***](#node) 어노테이션을 사용합니다. 이 어노테이션은 코드가 ADK 동적 워크플로 컨텍스트에서 실행될 수 있도록 래퍼를 생성합니다.

=== "TypeScript"

    TypeScript에는 `@node` 데코레이터가 없습니다. 대신 `node(fn, options)` 팩토리 함수를 사용하세요. `ctx.runNode()` 메서드는 `ctx.run_node()`에 해당합니다:

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/dynamic/get_started.ts:get-started"
    ```

    오케스트레이터 노드를 작성할 때, 결과를 읽는 방법과 일시 중지 후 워크플로가 작동하는 방식에 영향을 미치는 두 가지 세부사항이 있습니다:

    -   `ctx.runNode()` 메서드는 출력 값이 아닌 노드 결과(node result)로 확인(resolve)됩니다. 값을 가져오려면 `.output` 프로퍼티를 읽으세요.
    -   `ctx.runNode()`를 호출하는 오케스트레이터는 반드시 `rerunOnResume: true`를 설정해야 합니다. 이 설정은 재개 시 노드 본문을 다시 실행하므로, 이미 완료된 하위 노드는 다시 실행되지 않고 체크포인트에서 재생됩니다.

=== "Go"

    Go에서는 `workflow.NewFunctionNode`가 `@node` 데코레이터를 대체하고 `workflow.NewDynamicNode`가 `@node(rerun_on_resume=True)` 비동기 오케스트레이터를 대체합니다. `workflow.RunNode`는 `ctx.run_node()`에 직접 대응됩니다. `workflow.Chain`과 함께 사용하는 `workflowagent.New`는 `Workflow(edges=[...])`를 대체합니다.

    인간 참여형(human-in-the-loop) 일시 중지 후의 재개 동작은 `NodeConfig.RerunOnResume`에 의해 제어됩니다(자세한 내용은 아래의 [노드](#node) 참조).

    ```go
    --8<-- "examples/go/snippets/graphs/dynamic/main.go:get-started"
    ```

## 빌딩 블록: 노드 및 워크플로

노드와 워크플로는 ADK 동적 워크플로의 기본 빌딩 블록을 나타냅니다. 이러한 타입과 함수는 코드를 ADK의 코드 기반 워크플로에 통합할 수 있도록 래핑하는 데 필요한 기능을 제공합니다.

### 노드 {#node}

ADK의 동적 워크플로는 *노드*로 구성됩니다. 사용 가능한 워크플로 노드의 간단한 버전은 워크플로 내에서 실행하는 데 필요한 메타데이터로 일반 함수를 래핑합니다.

=== "Python"

    Python에서는 ***@node*** 어노테이션이 노드 래퍼를 생성하여 보일러플레이트를 최소화합니다:

    ```python
    @node(name="hello_node")
    def my_function_node(node_input: Any):
        return "Hello World"
    ```

    다음 코드 스니펫은 ***@node*** 어노테이션 *없이* 작성한 동일한 코드를 보여줍니다:

    ```python
    # base function
    def my_function_node(node_input: Any):
        return "Hello World"

    # FunctionNode wrapper with options
    success_node = FunctionNode(
        my_function_node,
        name="hello",
        rerun_on_resume=True,
    )
    ```

    외부 라이브러리의 함수를 래핑하거나, 동일한 함수에서 서로 다른 구성을 가진 여러 노드를 생성해야 하거나, 고급 오케스트레이션을 위해 레지스트리에서 노드 참조를 관리하는 경우 노드 래퍼 코드를 직접 생성하는 것이 유용할 수 있습니다.

=== "TypeScript"

    노드를 빌드하는 데는 `node(fn, options)` 팩토리 함수와 명시적인 `new FunctionNode(name, fn, config)` 생성자의 두 가지 방법이 있습니다. 다른 라이브러리의 함수를 래핑하거나, 하나의 함수에서 서로 다르게 구성된 여러 노드가 필요하거나, 고급 오케스트레이션을 위해 레지스트리에서 노드 참조를 관리할 때는 생성자를 사용하세요.

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/dynamic/nodes.ts:node-forms"
    ```

    이 코드 샘플에서 가장 중요한 옵션은 `rerunOnResume`이며, 이는 인간 참여형(human-in-the-loop) 일시 중지 후 워크플로가 재개될 때 발생하는 동작을 제어합니다:

    -   **`true` (재진입, re-entry):** 노드 본문이 처음부터 다시 실행됩니다. `ctx.runNode()`를 호출하는 모든 오케스트레이터에 이 설정을 사용하세요. 본문이 다시 실행되며 이미 완료된 하위 노드 활성화는 자동으로 건너뜁니다.
    -   **`false` (핸드오프, 리프 노드 기본값):** 재개 페이로드가 중단된 노드를 우회하여 해당 노드의 후속 노드에 입력으로 라우팅됩니다.

=== "Go"

    Go에서는 `workflow.NewFunctionNode[IN, OUT]`이 제네릭 매개변수에서 입력 및 출력 타입을 추론하여 일반 함수를 워크플로 노드로 래핑합니다. 데코레이터 구문은 없으며, 노드는 동적 오케스트레이터 내부의 `workflow.RunNode`에 하위 요소로 전달하는 값입니다:

    ```go
    --8<-- "examples/go/snippets/graphs/dynamic/main.go:building-blocks-nodes"
    ```

    `NodeConfig`는 Python의 `@node` 인수와 동일한 옵션을 보유합니다. 가장 중요한 필드는 `RerunOnResume *bool`이며, 인간 참여형(human-in-the-loop) 일시 중지 후 워크플로가 재개될 때 발생하는 동작을 제어합니다:

    -   **`&true` (재진입 모드)**: 중단된 노드가 재개 시 처음부터 다시 실행됩니다. 루프에서 `workflow.RunNode`를 호출하는 동적 오케스트레이터 노드에 이 설정을 사용하세요. 본문이 다시 실행되고 이미 완료된 하위 활성화는 자동으로 건너뜁니다(체크포인팅). 이는 Python의 `@node(rerun_on_resume=True)`와 동일합니다.
    -   **`&false` (핸드오프 모드)**: 재개 페이로드가 중단된 노드를 완전히 우회하여 노드의 후속 노드에 입력으로 직접 라우팅됩니다. 단순히 일시 중지 이벤트를 방출하고 사람의 응답이 다음 단계로 흐르기를 기대하는 리프 노드에 이 설정을 사용하세요.
    -   **`nil`**: 기본값은 노드 유형에 따라 다릅니다. 오케스트레이터 본문은 캐시된 하위 결과를 전달하기 위해 재개 시 다시 진입해야 하므로 `workflow.NewDynamicNode`는 자동으로 `nil → &true`(재진입 모드)를 설정합니다. `workflow.NewFunctionNode` 및 기타 리프 노드 생성자는 `nil`을 그대로 유지하며, 엔진은 이를 핸드오프(`&false`)로 처리합니다. 명시적 `&false`는 모든 노드 유형에서 항상 존중됩니다.

    ```go
    // NewDynamicNode: nil RerunOnResume is automatically set to &true.
    // Passing &rerun explicitly is equivalent and makes the intent clear.
    rerun := true
    orchestratorNode := workflow.NewDynamicNode[string, string]("my_workflow",
        myOrchestratorfn,
        workflow.NodeConfig{RerunOnResume: &rerun}, // re-entry: node body re-runs on resume
    )

    // NewFunctionNode: nil RerunOnResume stays nil → engine treats as handoff.
    handoffNode := workflow.NewFunctionNode("leaf_node",
        myLeafFn,
        workflow.NodeConfig{}, // nil RerunOnResume → handoff for FunctionNode
    )
    ```


### 워크플로

ADK 동적 워크플로에서는 동적 노드를 노드들의 기본 오케스트레이터로 사용합니다. 동적 노드는 하위 노드 실행과 해당 노드들의 실행 로직(순서 및 경로)을 관리합니다.

=== "Python"

    ```python
    @node(rerun_on_resume=True)
    async def my_workflow(ctx):
        # run_node executes a node and returns its output
        result = await ctx.run_node(my_function_node, node_input="Hello")
        result_formatted = await ctx.run_node(my_formatting_node, node_input=result)
        return result_formatted

    # Run the workflow
    root_agent = Workflow(
        name="root_agent",
        edges=[("START", my_workflow)],
    )
    ```

=== "TypeScript"

    오케스트레이터는 각 하위 단계에 대해 `ctx.runNode()`를 await하는 비동기 함수입니다. 이를 `rerunOnResume: true`로 노드로 래핑하고 그래프의 유일한 edge로 사용합니다:

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/dynamic/nodes.ts:workflows"
    ```

=== "Go"

    `workflow.NewDynamicNode`는 본문에서 각 하위 단계에 대해 `workflow.RunNode`를 호출하는 오케스트레이터를 생성합니다. `workflow.Chain(workflow.Start, myWorkflow)`와 함께 사용하는 `workflowagent.New`는 `Workflow(edges=[("START", my_workflow)])`에 해당합니다:

    ```go
    --8<-- "examples/go/snippets/graphs/dynamic/main.go:building-blocks-workflow"
    ```

## 데이터 처리

ADK에서 동적 워크플로를 사용할 때 데이터 전달은 [그래프 기반 워크플로](/graphs/)보다 더 간단합니다. `ctx.run_node`(Go에서는 `workflow.RunNode`)가 하위 노드의 출력을 직접 반환하므로 데이터 전송을 위해 세션 상태 키를 수동으로 읽고 쓸 필요가 없기 때문입니다.

=== "Python"

    ```python
    from google.adk import Context
    from google.adk.workflow import node

    @node(rerun_on_resume=True)
    async def editorial_workflow(ctx: Context, user_request: str):
        # Agent Node generates output
        raw_draft = await ctx.run_node(draft_agent, user_request)

        # Function Node formats text
        formatted_text = await ctx.run_node(format_function_node, raw_draft)

        return formatted_text
    ```

    또한 그래프 기반 워크플로 노드와 유사하게, 정의된 클래스를 사용하여 특정 데이터 스키마를 전달하고 입력 및 출력 스키마를 구성할 수도 있습니다:

    ```python
    from google.adk import Agent
    from google.adk import Context
    from google.adk.workflow import node
    from pydantic import BaseModel

    class CityTime(BaseModel):
        time_info: str  # time information
        city: str       # city name

    @node
    def city_time_function(city: str):
        """Simulate returning the current time in a specified city."""
        return CityTime(time_info="10:10 AM", city=city)

    city_report_agent = Agent(
        name="city_report_agent",
        model="gemini-flash-latest",
        input_schema=CityTime,
        instruction="""output the data provided by the previous node.""",
    )

    @node # workflow node
    async def city_workflow(ctx: Context):
        city_time = await ctx.run_node(city_time_function, "Paris")
        report_text = await ctx.run_node(city_report_agent, city_time)

        return report_text
    ```

=== "TypeScript"

    `ctx.runNode()` 함수는 하위 노드의 결과를 직접 반환하므로, 값을 한 단계 다운스트림으로 이동하기 위해 세션 상태 키를 읽고 쓸 필요가 없습니다. 이 함수는 `LlmAgent`를 포함하여 노드 유사(node-like) 값을 먼저 `node()`로 래핑하지 않고도 허용합니다:

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/dynamic/data_handling.ts:data-handling"
    ```

    스키마는 그래프에서와 동일하게 작동합니다. [순차 라우트](#sequence-route) 섹션에 표시된 것처럼 실행하는 노드에 스키마를 연결하세요.

=== "Go"

    Go에서는 동적 오케스트레이터 내부에서 `workflow.RunNode`를 통해 호출할 수 있도록 `workflow.NewAgentNode`가 `agent.Agent`를 래핑합니다. 각 `RunNode` 호출의 출력은 타입이 지정된 값으로 반환되므로 세션 상태 읽기가 필요하지 않습니다:

    ```go
    --8<-- "examples/go/snippets/graphs/dynamic/main.go:data-handling"
    ```

워크플로 노드 간의 데이터 처리에 대한 자세한 내용은 [에이전트 워크플로의 데이터 처리](/graphs/data-handling/)를 참조하세요.

## 워크플로 경로

ADK의 동적 워크플로는 반복 루프나 더 복잡한 분기 로직을 포함하여 [그래프 기반 워크플로](/graphs/)에 비해 라우팅 로직 측면에서 더 많은 유연성을 제공합니다. 이 섹션에서는 라우팅에 사용할 수 있는 몇 가지 기법을 설명합니다.

### 순차 라우트 {#sequence-route}

그래프 기반 워크플로에서와 마찬가지로 ADK의 동적 워크플로를 사용하여 순차적인 작업 처리를 만들 수 있습니다.

=== "Python"

    다음 코드 스니펫은 에이전트, 함수 노드 및 두 번째 에이전트로 구성된 동적 워크플로를 보여줍니다:

    ```python
    @node # workflow node
    async def city_workflow(ctx: Context):
        city = await ctx.run_node(city_generator_agent)
        city_time = await ctx.run_node(city_time_function, city)
        report_text = await ctx.run_node(city_report_agent, city_time)

        return report_text
    ```

=== "TypeScript"

    순차 라우트는 `ctx.runNode()` 호출을 차례로 await합니다. 각 호출은 다음 호출이 시작되기 전에 완료됩니다:

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/dynamic/sequence_route.ts:sequence-route"
    ```

=== "Go"

    `NewDynamicNode` 본문 내부에서 `workflow.RunNode`를 순차적으로 호출하세요. 각 호출은 다음 호출이 시작되기 전에 하위 노드가 완료될 때까지 기다립니다. [위의 데이터 처리 예제](#data-handling)가 바로 이 패턴을 보여주며, `cityWorkflow`는 `cityTimeNode`와 `cityReportNode`에 대해 순서대로 `workflow.RunNode`를 호출하여 각 노드의 타입이 지정된 출력을 다음 노드로 전달합니다.

### 루프 라우트 {#loop-route}

작업에 반복 루프를 사용하려는 워크플로의 경우, 동적 워크플로는 필요한 라우팅 로직을 정의할 수 있는 훨씬 더 많은 유연성을 제공합니다.

=== "Python"

    다음 코드 예제는 동적 워크플로를 사용하여 코드를 생성, 검토 및 업데이트하는 워크플로 루프를 구성하는 방법을 보여줍니다:

    ```python
    from google.adk import Context
    from google.adk import Event
    from google.adk.agents import LlmAgent
    from google.adk.workflow import node

    coder_agent = LlmAgent(
        name="generator_agent",
        model="gemini-flash-latest",
        instruction="Write python code for user request.",
    )

    @node(name="lint_reviewer")
    async def compile_lint_check(ctx: Context, code: str):
        # Simulate API call or lint check
        class Response:
            findings = ""
        return Response()

    fixer_agent = LlmAgent(
        name="fixer_agent",
        model="gemini-flash-latest",
        instruction="""Refactor current code {code}.
            Based on compile & lint review: {findings}""",
    )

    @node # workflow node
    async def code_workflow(ctx: Context, user_request: str):
      code = await ctx.run_node(coder_agent, user_request)
      check_resp = await ctx.run_node(compile_lint_check, code)

      while check_resp.findings:
        yield Event(state={"code": code, "findings": check_resp.findings})
        code = await ctx.run_node(fixer_agent, {"code": code, "findings": check_resp.findings})

        check_resp = await ctx.run_node(compile_lint_check, code)

      yield Event(output=code)
    ```

=== "TypeScript"

    동적 워크플로는 그래프의 역방향 에지 대신 일반 루프로 반복을 정의하여 워크플로 로직을 단순하게 유지하는 데 도움이 됩니다. 값은 로컬 변수에 유지되며, 상태는 에이전트의 지침 템플릿에서 다시 읽어야 하는 경우에만 기록됩니다. 그래프 사이클과 달리 루프는 루프 조건에 의해 바운딩(제한)됩니다:

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/dynamic/loop_route.ts:loop-route"
    ```

=== "Go"

    Go에서 루프는 동적 노드 본문 내부의 일반 `for` 루프입니다. 린트 검사 노드는 발견된 문제가 없을 때 빈 문자열을 반환하여 루프 종료를 알립니다:

    ```go
    --8<-- "examples/go/snippets/graphs/dynamic/main.go:loop-route"
    ```

### 병렬 실행 라우트

ADK의 동적 워크플로는 병렬 실행을 지원할 수 있습니다.

=== "Python"

    Python에서는 `asyncio.gather`를 사용하여 병렬 실행을 구축할 수 있습니다:

    ```python
    import asyncio
    from typing import Any
    from google.adk import Context
    from google.adk.workflow import BaseNode, node


    @node(rerun_on_resume=True)
    async def parallel_supervisor(
        ctx: Context, node_input: list[Any], real_node: BaseNode
    ):
        """Runs a worker node in parallel for each item in the input list."""
        tasks = []
        for item in node_input:
            # ctx.run_node returns a future. Append instead of awaiting immediately.
            tasks.append(ctx.run_node(real_node, item))

        # Collect all results in parallel
        results = await asyncio.gather(*tasks)
        return results
    ```

    !!! tip "팁: 병렬 노드 재개하기"

        워크플로 프레임워크는 동적 워크플로가 재개될 때 병렬 워커 노드를 포함하여 실패했거나 중단된 워커 노드만 다시 실행되도록 보장합니다.

=== "TypeScript"

    `ctx.runNode()` 메서드는 Promise를 반환하므로, 어떤 하위 노드도 await하기 전에 모든 하위 노드를 시작하면 하위 노드들이 동시에 실행되고 `Promise.all`이 결과를 수집합니다. 실행 ID(Run ID)는 호출 순서대로 할당되므로 재개 전반에서 ID를 결정론적으로 유지하려면 동기 루프에서 하위 노드를 시작하세요:

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/dynamic/parallel_route.ts:parallel-route"
    ```

    !!! tip "팁: 내장 병렬 워커를 선호하세요"

        목록의 각 항목에 대해 하나의 노드를 실행하려면 `node(worker, {parallelWorker: true, maxParallelWorkers: 4})`를 사용하세요. 이 옵션은 팬아웃을 수행하고 동시성을 제한하며 기본값은 8입니다. 커스텀 스케줄링이나 부분 실패 처리가 필요한 경우 위에 표시된 수동 방식을 사용하세요. 재개 시 두 경우 모두 실패하거나 중단된 워커만 다시 실행됩니다.

=== "Go"

    Go에서 `workflow.NewParallelWorker`는 하위 노드를 래핑하고 리스트 입력의 각 요소에 대해 동시에 실행하여 결과를 단일 출력 슬라이스로 수집합니다. `maxConcurrency` 매개변수는 동시에 실행할 수 있는 최대 동시 활성화 수를 제한하며, `0`은 무제한을 의미합니다:

    ```go
    --8<-- "examples/go/snippets/graphs/dynamic/main.go:parallel-route"
    ```

    !!! tip "팁: 병렬 노드 재개하기"

        워크플로 프레임워크는 동적 워크플로가 재개될 때 `NewParallelWorker`가 관리하는 병렬 워커 노드를 포함하여 실패했거나 중단된 워커 노드만 다시 실행되도록 보장합니다.

## 사람의 입력 (Human Input)

ADK의 동적 워크플로에는 사람 입력 또는 인간 참여형(HITL) 단계도 포함할 수 있습니다.

=== "Python"

    노드에서 ***RequestInput***을 yield하여 워크플로에 사람 입력을 구축하며, 이는 워크플로를 일시 중지하고 사용자 입력을 기다립니다. 다음 코드 예제는 사람 입력 노드를 구축하고 이를 워크플로에 포함하는 방법을 보여줍니다:

    ```python
    from typing import Any
    from google.adk import Context
    from google.adk.events import RequestInput
    from google.adk.workflow import node


    @node(rerun_on_resume=False)
    async def get_user_approval(ctx: Context, node_input: Any):
        """Yields a RequestInput to pause the workflow and wait for user input."""
        yield RequestInput(message="Please approve this request (Yes/No)")


    @node(rerun_on_resume=True)
    async def handle_process(ctx: Context, node_input: Any):
        """The orchestrator calling the interactive step."""
        user_response = await ctx.run_node(get_user_approval)

        if user_response.lower() == "yes":
            return "Approved"
        return "Denied"
    ```

    !!! important "중요: `ctx.run_node`를 사용하는 상위 노드"

        `ctx.run_node`를 호출하는 동적 워크플로의 상위 노드는 중단을 올바르게 처리하기 위해 반드시 `rerun_on_resume=True`를 설정해야 합니다.

=== "TypeScript"

    리프 노드는 워크플로를 일시 중지하기 위해 `RequestInput`을 반환하고 기본값인 `rerunOnResume: false`를 유지하여 응답이 출력이 되도록 합니다. 이를 호출하는 오케스트레이터는 반드시 `rerunOnResume: true`를 설정해야 합니다:

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/dynamic/human_input.ts:human-input"
    ```

    !!! important "중요: 결정을 내리기 전에 `interruptIds`를 확인하세요"

        `ctx.runNode()` 메서드는 하위 노드가 중단될 때 오류를 발생시키지 **않습니다**. 정상적으로 반환되며 결과의 `interruptIds` 프로퍼티가 채워지고 `output` 프로퍼티는 여전히 `undefined` 상태로 남습니다. 결과를 사용하기 전에 `interruptIds`를 확인하세요. 이 검사를 건너뛰는 오케스트레이터는 누락된 출력을 답변으로 취급하고 사용자가 제공하지 않은 값으로 계속 진행합니다.

=== "Go"

    Go에서는 재진입 HITL 패턴을 구현하기 위해 `workflow.ResumeOrRequestInput`과 함께 `workflow.NewEmittingFunctionNode`를 사용하세요. 첫 번째 패스에서 `ResumeOrRequestInput`은 `session.RequestInput` 이벤트를 방출하고 `ErrNodeInterrupted`를 반환하여 워크플로를 일시 중지합니다. 사람이 응답한 후 노드는 처음부터 다시 실행(`RerunOnResume: &true`)되며 `ResumeOrRequestInput`은 사람의 응답을 직접 반환합니다:

    ```go
    --8<-- "examples/go/snippets/graphs/dynamic/main.go:human-input"
    ```

## 고급 기능

동적 워크플로는 더 복잡한 개발 시나리오를 처리하도록 설계된 몇 가지 고급 기능을 제공합니다. 이러한 기능을 통해 실행을 더 세밀하게 제어하고 기존 기술 인프라와 더 잘 통합할 수 있습니다.

### 실행 ID (Execution IDs)

ADK 프레임워크는 상위 ID와 카운터를 기반으로 하위 노드 실행에 대한 결정론적 식별자(ID)를 생성합니다. ADK 워크플로는 이전 결과를 식별하기 위해 예약된 각 노드에 결정론적 ID를 사용합니다. 이러한 ID는 동적 노드 스케줄 순서에 따라 생성되며, 워크플로가 재개되거나 다시 실행되는 경우 체크포인팅 및 올바른 순서로 작업을 다시 실행하는 데 사용됩니다.

#### 커스텀 실행 ID

순서를 변경할 수 있는 리스트를 처리할 때와 같이 드문 경우에 안정적인 식별자가 필요할 수 있습니다. 일반적으로는 워크플로 작업 재시도 및 프로세스 재개에 미치는 영향 때문에 이를 피해야 합니다. 구체적으로 이 ID들은 노드 상태를 확인하고 노드가 이미 실행된 경우 실행을 건너뛰는 데 사용됩니다. 커스텀 ID를 제공하는 경우 워크플로 재실행에 대해 결정론적이어야 하며 입력에 대해 논리적으로 동일하게 유지되는지 확인하세요.

!!! warning "경고: 커스텀 실행 ID"

    커스텀 실행 ID 생성을 피하세요. 실행 ID는 노드의 실행 순서를 결정하는 데 사용되므로, 커스텀 실행 ID를 사용하면 시스템이 워크플로에서 해당 노드를 다시 실행하려고 시도할 때 문제가 발생할 수 있습니다.

=== "Python"

    ```python
    from google.adk import Context
    from google.adk.workflow import node
    from pydantic import BaseModel
    from typing import Any
    import asyncio

    class Order(BaseModel):
      order_id: str
      cart_items: list[Product]

    @node(rerun_on_resume=True)
    async def process_all_orders(ctx: Context, node_input: Any):
      orders = await get_orders()

      process_tasks = []
      for order in orders:
        # Use run_id to provide a custom identifier.
        # Custom run_ids must contain at least one non-numeric character
        # to avoid collision with auto-generated sequential numeric IDs.
        task = ctx.run_node(process_order, order, run_id=f"order-{order.order_id}")
        process_tasks.append(task)

      results = await asyncio.gather(*process_tasks)
      return results
    ```

    기본적으로 자동 생성되는 실행 ID는 `"1"`부터 시작하는 순차적 정수(문자열로 표현됨)입니다. 커스텀 `run_id` 값은 이러한 자동 생성 ID와의 충돌을 피하기 위해 하나 이상의 숫자가 아닌 문자를 포함해야 합니다.

=== "TypeScript"

    후행 옵션으로 `ctx.runNode()`에 `runId`를 전달하세요. 이 ID는 자동 생성되는 순차 ID와 충돌하지 않도록 하나 이상의 숫자가 아닌 문자를 포함해야 합니다:

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/dynamic/custom_run_ids.ts:custom-execution-ids"
    ```

=== "Go"

    Go에서는 `workflow.RunNode`에 후행 옵션으로 `workflow.WithRunID("order-x")`를 전달하세요. 자동 생성되는 순차 카운터 ID와의 충돌을 피하기 위해 ID에는 하나 이상의 숫자가 아닌 문자가 포함되어야 합니다:

    ```go
    --8<-- "examples/go/snippets/graphs/dynamic/main.go:custom-execution-ids"
    ```
