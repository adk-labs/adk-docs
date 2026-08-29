# Human input for agent workflows

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v2.0.0</span><span class="lst-typescript">TypeScript v2.0.0</span><span class="lst-go">Go v2.0.0</span>
</div>

Being able to request human input for data input, decision verification, or
action permission is an important part of many agent-powered workflows.
Graph-based workflows in ADK can include human in the loop (HITL) nodes
specifically built for obtaining input from humans as part of a workflow. These
nodes do not require artificial intelligence (AI) models to run, which can make
the input process more predictable and reliable.

## 시작하기

=== "Python"

    You can implement a human input node in a graph using the ***RequestInput***
    class and a text prompt for the user. The following code example shows how to
    add a human input node to a Workflow graph:

    ```python
    from google.adk.events import RequestInput
    from google.adk import Workflow

    def step1(): # Human input step
      yield RequestInput(message="Enter a number:")

    def step2(node_input):
      return node_input * 2

    root_agent = Workflow(
        name="root_agent",
        edges=[('START', step1, step2)],
    )
    ```

    In this code example, `step1` pauses the execution of the agent until the
    system receives an input from a user. Once the system receives input from the
    user, that input is passed to the next node.

=== "TypeScript"

    ADK TypeScript v2.0.0에서 인간 입력 노드는 `RequestInput`을 yield합니다. `step1` 노드는 사용자가 응답할 때까지 워크플로를 일시 중지하고, 사용자의 응답은 다음 노드의 입력으로 전달됩니다. 인간 참여형(HITL) 노드는 모델을 필요로 하지 않으므로 일시 중지가 결정론적입니다.

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/human-input/get_started.ts:get-started"
    ```

    이 구현은 기본값인 `rerunOnResume: false` 핸드오프를 보여줍니다. 중단된 노드는 다시 실행되지 않으며, 사용자의 응답을 출력으로 삼아 완료됩니다. `ctx.runNode()`를 호출하는 노드는 대신 `rerunOnResume: true`가 필요합니다. 자세한 내용은 [동적 워크플로에서의 인간 입력](/graphs/dynamic/#human-input)을 참조하세요.

=== "Go"

    In ADK Go v2.0.0, a HITL graph node is built with
    `workflow.NewEmittingFunctionNode` and `workflow.ResumeOrRequestInput`.
    This is the direct equivalent of Python's `RequestInput` node:

    -   On the **first pass**, `workflow.ResumeOrRequestInput` emits a
        `session.RequestInput` event (surfaced as `Event.RequestedInput`) and
        returns `ErrNodeInterrupted`, pausing the workflow.
    -   After the human replies, the node is **re-invoked from the top**
        (`RerunOnResume: &true`) and `ResumeOrRequestInput` returns the reply
        payload, which flows as typed input to the next node via `event.Output`.

    ```go
    --8<-- "examples/go/snippets/graphs/human-input/main.go:graph-hitl-get-started"
    ```

## 구성 옵션

=== "Python"

    Human input nodes can use the ***RequestInput*** class with the following
    configuration options:

    -   **`message`:** Text provided to the user to explain the human input
        request.
    -   **`payload`:** Structured data to be used as part of the human input
        request.
    -   **`response_schema`:** A data structure the human response must conform to.

=== "TypeScript"

    `RequestInput` 클래스는 다음 구성 옵션을 사용합니다:

    -   **`message`:** 사용자에게 질문 내용을 설명하는 텍스트입니다.
    -   **`payload`:** 클라이언트가 추가 컨텍스트를 렌더링할 수 있도록 프롬프트와 함께 전송되는 구조화된 데이터입니다.
    -   **`responseSchema`:** 응답이 취할 것으로 예상되는 형태입니다. 스키마는 인터럽트 시 `functionCall.args.response_schema`로 전달되며, 클라이언트는 이를 읽어 응답용 양식을 렌더링합니다.

    노드의 `rerunOnResume` 옵션은 응답이 도착했을 때 일어나는 동작을 제어합니다:

    -   **`false`** (리프 노드 기본값): 응답이 중단된 노드를 우회하여 해당 노드의 후속 노드에 입력으로 라우팅됩니다.
    -   **`true`**: 노드 본문이 처음부터 다시 실행됩니다. 이 설정은 `ctx.runNode()`를 호출하는 모든 노드에 필요하며, 재개 시 캐시된 하위 결과를 전달할 수 있습니다.

=== "Go"

    `session.RequestInput` carries the following fields, which map directly to
    Python's `RequestInput` parameters:

    -   **`InterruptID`** (`string`): A unique identifier for this pause point.
        Use a stable prefix plus a UUID to avoid collision across workflow runs.
        Equivalent to the implicit interrupt ID in Python.
    -   **`Message`** (`string`): Human-readable prompt displayed to the user.
        Equivalent to Python's `message` parameter.
    -   **`Payload`** (`any`): Optional structured data sent alongside the
        prompt so the client can render additional context. Equivalent to
        Python's `payload` parameter.

    `workflow.NodeConfig.RerunOnResume` controls what happens on resume:

    -   **`&true`**: the node body is re-run from the top; `ResumeOrRequestInput`
        returns the human's reply on the second pass. Required for nodes that
        use `ResumeOrRequestInput`.
    -   **`&false`** or **`nil`** (leaf default): the reply is routed to the
        node's successor as input, bypassing the interrupted node.

    !!! note "Note: Structured response from the client"

        ADK Go does not automatically parse or validate the structure of the
        human's reply payload. If your workflow needs structured feedback,
        include a UI or a downstream agent node to validate the response before
        acting on it.

!!! note "참고: 응답 스키마 입력 제한사항"

    응답 스키마는 사람의 응답을 지정된 구조에 맞게 자동으로 재구성하지 않습니다. 응답은 이미 해당 형식이어야 합니다. 더 나은 사용자 경험을 위해 클라이언트 인터페이스에서 구조화된 데이터를 수집하거나, 일시 중지 뒤에 에이전트 노드를 배치하여 응답을 필요한 형식으로 변환하세요.

## 사람의 입력 (Human Input) examples

The following code examples demonstrate more detailed human input requests.

### Request input with a message and payload

=== "Python"

    The following code sample shows how to construct a ***RequestInput*** object
    in a workflow node, including a ***payload*** and ***response schema***. In
    this example, the `ActivitiesList` is expected to be completed by an agent
    node that composes a list of activities, and the `get_user_feedback()` node
    requests feedback from the user.

    ```python
    class ActivitiesList(BaseModel):
       """Itinerary should be a list of dictionaries for each activity. Each
       activity has a name and a description"""
       itinerary: List[Dict[str, str]]

    class UserFeedback(BaseModel):
       """Expected response structure from the user."""
       user_response: str

    async def get_user_feedback(node_input: ActivitiesList):
       """
       Retrieves the user's thoughts on the agents initial itinerary in order to
       either expand on, change the list, or exit the loop
       """
       message = (
           f"""
           Here is your recommended base itinerary:\n{node_input}\n\n
           Which of these items appeal to you (if any)?
           """
       )

       yield RequestInput(
           message=message,
           payload=node_input,
            response_schema=UserFeedback,
       )
    ```

=== "TypeScript"

    다음 3개 노드 그래프는 구조화된 여행 일정을 작성하고, 클라이언트가 이를 렌더링할 수 있도록 프롬프트와 함께 `payload`로 전송한 다음 사용자의 피드백에 따라 작동합니다:

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/human-input/payload_and_schema.ts:payload-and-schema"
    ```

=== "Go"

    The following code sample shows a three-node graph: a builder node generates
    a structured itinerary, a HITL node sends it as `Payload` alongside the
    prompt, and a final node acts on the user's feedback. The `Payload` field
    lets the client render the full itinerary for the user before they respond:

    ```go
    --8<-- "examples/go/snippets/graphs/human-input/main.go:graph-hitl-with-payload"
    ```

## 도구 확인: LLM 에이전트의 승인 프롬프트

Tool-confirmation is a separate, LLM-agent–level mechanism for yes/no
approval prompts. Unlike graph HITL nodes, tool-confirmation works inside an
`llmagent` tool function rather than as a standalone graph node. It is useful
when you want an LLM agent to pause and ask for approval before executing a
specific tool call.

=== "Python"

    The following code sample shows how to construct a ***RequestInput*** object
    in a workflow node, including a ***response schema***:

    ```python
    async def initial_prompt(ctx: Context):
       """Ask the user for itinerary information"""
       input_message = """
           This is an interactive concierge workflow tasked with making you a great
           itinerary for you in your city of choice. If you give some details about
           yourself or what you are generally looking for I can better personalize
           your itinerary.
           For example, input your:
               City (Required),
               Age,
               Hobby,
               Example of attraction you liked
       """
        yield RequestInput(message=input_message, response_schema=str)
    ```

=== "TypeScript"

    도구가 실행되기 전에 에이전트가 승인을 위해 일시 중지하도록 하려면 `FunctionTool`에 `requireConfirmation: true`를 설정하세요. 그래프의 인간 참여형(HITL) 노드는 다른 목적으로 사용됩니다. 도구 호출을 확인하는 대신 사용자에게 입력을 요청하여 워크플로를 시작할 수 있습니다. `responseSchema: z.string()` 옵션은 일반 텍스트 응답을 요청합니다:

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/human-input/initial_prompt.ts:initial-prompt"
    ```

=== "Go"

    Set `RequireConfirmation: true` in `functiontool.Config` for a static
    yes/no approval before a tool executes, or call `ctx.RequestConfirmation`
    from inside the tool for a custom hint message:

    ```go
    --8<-- "examples/go/snippets/graphs/human-input/main.go:simple-hitl"
    ```

    For a custom hint with manual re-entry handling:

    ```go
    --8<-- "examples/go/snippets/graphs/human-input/main.go:hitl-with-hint"
    ```
