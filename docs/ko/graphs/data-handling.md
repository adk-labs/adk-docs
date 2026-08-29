# Data handling for agent workflows

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v2.0.0</span><span class="lst-typescript">TypeScript v2.0.0</span><span class="lst-go">Go v2.0.0</span>
</div>

Structuring and managing data between agents and graph-based nodes is critical
for building reliable processes with ADK. This guide explains data handling
within graph-based workflows and collaboration agents, including how information
is transmitted and received between graph nodes. It covers the essential
parameters for passing data, content, and state, and explains how to implement
structured data transfer for both function and agent nodes using data format
schemas and specific instruction syntax.

## Workflow data flow

Within a graph-based workflow, nodes pass data to downstream steps through
events. A step writes its output to a named event field, and the next step
receives it as its typed input.

=== "Python"

    In Python, data is exchanged between graph nodes using ***Events***. The key
    parameters for node data handling are:

    -   **`output`**: Parameter for passing information between *nodes*.
    -   **`message`**: Data intended as a response to a user.
    -   **`state`**: Data automatically persisted across nodes via ***Events***
        throughout an ADK session.

=== "TypeScript"

    ADK TypeScript v2.0.0에서 노드는 이벤트를 통해 데이터를 교환합니다. 노드 데이터 처리를 위한 주요 필드는 다음과 같습니다:

    -   **`output`**: 다음 노드로 전달되는 값입니다. 값을 직접 반환하면 ADK가 이를 이벤트로 래핑하거나, `createEvent({output})`를 사용하여 명시적으로 필드를 설정할 수 있습니다.
    -   **`content`**: 사용자를 위한 메시지입니다. 런타임은 이 필드를 렌더링하지만 그래프는 이를 다음 노드로 전달하지 않습니다.
    -   **`route`**: 따라갈 조건부 edge를 선택하는 라우팅 키입니다.

    세션 상태(Session state)는 이벤트와 별개입니다. 노드는 `ctx.state`를 통해 상태를 읽고 쓰며, 누적된 델타는 해당 노드의 이벤트에 첨부됩니다. 상태 키에는 수명과 범위를 제어하는 접두사를 붙일 수 있습니다:

    | 접두사 | 범위 |
    |---|---|
    | `app:` | 앱의 모든 사용자와 세션 간에 공유됨 |
    | `user:` | 사용자에게 귀속되며 해당 사용자의 여러 세션 간에 공유됨 |
    | `temp:` | 현재 호출이 종료된 후 폐기됨 |
    | *(없음)* | 세션 수명 동안 유지됨 |

=== "Go"

    In ADK Go v2.0.0, the data-passing mechanism depends on which agent style
    you use:

    **workflow package** (`FunctionNode`, `AgentNode`, `DynamicNode`): nodes
    communicate through `session.Event` fields, mirroring Python closely:

    -   **`Event.Output`**: the node's return value, set automatically by the
        framework when a `FunctionNode` returns a non-`*genai.Content` value.
        The successor node receives this as its typed `input` parameter.
    -   **`Event.Routes`**: routing keys set explicitly by an emitting node to
        select which conditional edge to follow — the Go equivalent of
        Python's `Event(route=...)`.
    -   **`Event.NodeInfo`**: scheduler metadata (`path`, `MessageAsOutput`,
        `OutputFor`). Set by the workflow engine; nodes do not set this
        directly.

    **Prebuilt workflow agents** (`sequentialagent`, `parallelagent`,
    `loopagent`): these agents communicate through session state:

    -   **`OutputKey`** on `llmagent.Config`: the framework writes the agent's
        final text response to `state[OutputKey]` after each turn.
    -   **`ctx.Session().State().Set` / `.Get`**: write or read arbitrary
        values from state inside custom code.
    -   **`{key}` in `Instruction`**: the framework substitutes `state["key"]`
        into the prompt before calling the model.

    State keys may carry a prefix that controls their lifetime and scope:

    | Prefix constant | Prefix string | Scope |
    |---|---|---|
    | `session.KeyPrefixApp` | `"app:"` | Shared across all users and sessions for the app |
    | `session.KeyPrefixUser` | `"user:"` | Tied to the user, shared across their sessions |
    | `session.KeyPrefixTemp` | `"temp:"` | Discarded after the current invocation ends |
    | *(none)* | — | Persists for the lifetime of the session |

### Node output

Each step in a workflow produces output for its successor.

=== "Python"

    Use the ***return*** or ***yield*** syntax to hand off data to the next node:

    ```python
    from google.adk import Event

    def my_function_node(node_input: str):
        output_value = node_input.upper()
        return Event(output=output_value) # "THE RESULT"
    ```

    Use the ***return*** syntax when outputting ***Event*** data that does not
    require additional processing. When emitting data that requires additional
    processing, or if you are generating more than one data item, you can use
    more than one ***yield*** command. Each ***yield*** call adds to a list of
    data objects on the Event which is passed to the next node of a graph. A
    ***return*** or ***yield*** command without a parameter passes a `None` value
    to the next node.

=== "TypeScript"

    노드의 출력을 생성하는 세 가지 동등한 방법이 있습니다: 값을 직접 반환하거나, `createEvent({output})`를 반환하거나, 결과와 함께 진행 상황을 스트리밍하기 위해 비동기 제너레이터(async generator)에서 이벤트를 yield하는 것입니다.

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/data-handling/node_output.ts:node-output"
    ```

    !!! warning "주의: 실행당 하나의 이벤트에서만 `output`을 방출하세요"

        노드는 `output`을 담은 이벤트를 여러 번 yield할 수 있으며, 이 경우 ADK는 오류를 발생시키지 않습니다. 각 이벤트는 이전 이벤트를 덮어쓰며, 후속 노드는 최종 값만 받게 됩니다. 진행 상황 메시지에는 `content`를 대신 사용하세요.

=== "Go"

    **workflow package**: a `FunctionNode` simply returns a typed Go value.
    The framework automatically wraps the return value in a `session.Event`
    and sets `Event.Output`. The successor node receives this value as its
    typed `input` parameter — no manual event construction needed:

    ```go
    --8<-- "examples/go/snippets/graphs/data-handling/main.go:event-output"
    ```

    **Prebuilt workflow agents**: use `OutputKey` on `llmagent.Config` to
    save an agent's text response to session state, then reference it with
    `{key}` in downstream agents' `Instruction` templates:

    ```go
    --8<-- "examples/go/snippets/graphs/data-handling/main.go:output-key"
    ```

### Node output: passing structured data

=== "Python"

    You can pass longer, structured data in a serializable format:

    ```python
    def my_function_node_3():
        yield Event(
            output={
                "city_name": "Paris",
                "city_time": "10:10 AM",
            },
        )
    ```

    !!! warning "Caution: Event.output limitation"

        Nodes are only allowed to emit a single ***Event.output*** data payload
        per execution. This limitation means that while you can use more than
        one ***yield*** in a node, having two or more ***yield*** commands with
        an ***Event.output*** results in a runtime error.

=== "TypeScript"

    `output` 필드는 텍스트에만 국한되지 않습니다. 직렬화 가능한 모든 값은 다음 노드로 전달되며, JSON 파싱이나 상태 읽기 없이도 타입이 지정된 객체로 수신됩니다. 출력을 생성하는 노드에 `outputSchema`를 연결하거나, 소비하는 노드에 `inputSchema`를 연결하면 계약이 명시화되고 런타임에 유효성이 검증됩니다:

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/data-handling/structured_output.ts:structured-output"
    ```

=== "Go"

    **workflow package**: a `FunctionNode` can return any JSON-serializable
    Go struct. The framework serializes it into `Event.Output` and
    deserializes it back into the successor node's typed `input` parameter.
    There is no single-payload restriction — each node has exactly one typed
    return value:

    ```go
    --8<-- "examples/go/snippets/graphs/data-handling/main.go:structured-output"
    ```

    **Prebuilt workflow agents**: use multiple `OutputKey` values, one per
    agent, to store individual fields in session state. Downstream agents
    read each field independently via `{key}` in their `Instruction`.

### Routing output

=== "Python"

    Use the `route` parameter of an ***Event*** to drive conditional edge
    dispatch:

    ```python
    def router(node_input: str):
        return Event(route="BUG")
    ```

=== "TypeScript"

    `route` 값은 `output`과 독립적이므로, 하나의 이벤트로 브랜치를 선택함과 동시에 페이로드를 전달할 수 있습니다. `DEFAULT_ROUTE` 설정은 다른 어떤 브랜치와도 일치하지 않는 모든 값을 처리합니다:

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/data-handling/routing_output.ts:routing-output"
    ```

=== "Go"

    **workflow package**: an emitting `FunctionNode` constructs a
    `session.Event` directly, sets `Event.Routes` to the desired route keys,
    and sets `Event.Output` to forward the payload to the successor. The
    workflow engine reads `Event.Routes` at dispatch time to select the
    matching edge:

    ```go
    --8<-- "examples/go/snippets/graphs/data-handling/main.go:routing-output"
    ```

### User-facing messages

=== "Python"

    Use the ***message*** parameter of an ***Event*** to send a response to a
    user rather than pass data to the next node:

    ```python
    async def user_message(node_input: str):
      """Tell user research process is starting."""
      yield Event(message="Beginning research process...")
    ```

=== "TypeScript"

    사용자를 위한 메시지는 이벤트의 `content` 필드입니다. 런타임은 `content`를 렌더링하지만 그래프는 이를 다음 노드로 전달하지 않습니다. 사용자를 위해서는 `content`를, 다음 노드를 위해서는 `output`을 사용하세요. 노드는 두 개의 이벤트를 전송하여 둘 다 방출할 수 있으며, 이때 하나에만 `output`을 포함합니다:

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/data-handling/user_message.ts:user-message"
    ```

=== "Go"

    **workflow package**: to emit a user-visible message without advancing
    the node's typed output, set `Event.Content` on an intermediate event
    emitted via the `emit` callback in an `EmittingFunctionNode`. The
    terminal return value (or `nil`) controls `Event.Output`.

    **Prebuilt workflow agents**: any `llmagent` step automatically emits its
    model response as a user-facing event. For non-LLM steps, write a custom
    `Run` function on an `agent.Agent` that yields events whose
    `LLMResponse.Content` contains the text.

### Session state and state scopes

Session state persists data across turns within a session. It is the primary
data-sharing mechanism for the prebuilt workflow agents, and is also available
inside tools and callbacks regardless of which agent style you use.

=== "Python"

    Use the ***state*** parameter of an ***Event*** to maintain values across
    nodes. Nodes can modify state values, and the modified state values are
    available to downstream nodes:

    ```python
    async def init_state_node(attempts: int = 0):
      yield Event(
          state={
              "attempts": attempts,
          },
      )

    async def task_attempt_node(node_input: Content, attempts: int):
      yield Event(
          state={
              "attempts": attempts + 1,
          },
      )

    async def read_state_node(ctx: Context):
      print(f"attempts state: {ctx.state}") # attempts state: attempts: 1

    root_agent = Workflow(
        name="root_agent",
        edges=[("START", init_state_node, task_attempt_node, read_state_node)],
    )
    ```

    !!! warning "Caution: `state` property data limitations"

        The state parameter *should not be used to persist large amounts of
        data* between nodes. Use artifacts or other data persistence mechanisms,
        such as database Tools, to persist large data resources during the life
        cycle of a Workflow.

=== "TypeScript"

    상태를 반환하는 대신 `ctx.state`를 통해 상태를 작성하세요. 기록된 상태는 동일한 실행 내의 모든 후속 노드에서 즉시 확인할 수 있으며, 작성 노드의 이벤트와 함께 커밋됩니다:

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/data-handling/session_state.ts:session-state"
    ```

    !!! warning "주의: `state` 데이터 제한사항"

        세션 상태는 가벼운 키-값 저장소입니다. 노드 간에 대용량 페이로드를 이동하는 데 사용하지 마세요. 대신 아티팩트나 데이터베이스 도구를 사용하세요. 다음 노드에만 값이 필요한 경우에는 노드 `output`으로 edge를 따라 전달하세요. 값이 실행 이후에도 유지되어야 하거나 도구, 콜백, 또는 `{key}` 지침 템플릿에서 읽어야 하는 경우에 상태를 사용하세요.

=== "Go"

    State is written with `ctx.Session().State().Set(key, value)` and read
    with `.Get(key)`. The `session` package defines prefix constants that map
    to the same lifetime scopes as Python's state parameter. This pattern
    applies to prebuilt workflow agents and to tools and callbacks in any
    agent style:

    ```go
    --8<-- "examples/go/snippets/graphs/data-handling/main.go:state-scopes"
    ```

    !!! warning "Caution: state data limitations"

        Session state is a lightweight key-value store. Do not use it to persist
        large payloads such as file contents or binary data. Use ADK artifacts
        or external storage tools instead.

    !!! tip "workflow package: prefer Event.Output over state"

        For the `workflow` package (`FunctionNode`, `AgentNode`, `DynamicNode`),
        pass data between nodes by returning typed values — the framework sets
        `Event.Output` automatically. Only use `State().Set` when you need to
        share values with tools, callbacks, or agent `Instruction` templates.

## Constrain node data with schemas

You can set input and output data schemas to constrain the data formats
accepted and produced by any agent node.

=== "Python"

    Use `input_schema` and `output_schema` with a class that extends
    ***BaseModel*** to constrain any agent's input and output:

    ```python
    from google.adk import Agent
    from pydantic import BaseModel

    class FlightSearchInput(BaseModel):
        origin: str           # Airport code "SFO"
        destination: str      # Airport code "CDG"
        departure_date: date  # date(2026, 3, 15)
        passengers: int = 1   # Number of passengers

    class FlightSearchOutput(BaseModel):
        flights: list[Flight]
        cheapest_price: float

    flight_searcher = Agent(
        name="flight_searcher",
        instruction="Search for available flights.",
        input_schema=FlightSearchInput,
        output_schema=FlightSearchOutput,
        tools=[search_flights_api],
        mode="single_turn",
        ...
    )

    assistant = Agent(
        name="assistant",
        instruction="You help users plan trips.",
        sub_agents=[flight_searcher],
        ...
    )
    ```

=== "TypeScript"

    스키마는 Zod 객체 또는 genai `Schema`입니다. 스키마의 위치에 따라 그 효과가 결정됩니다:

    -   `LlmAgent.outputSchema` 옵션은 모델이 해당 형태로 응답하도록 요구합니다.
    -   `LlmAgent.inputSchema` 옵션은 에이전트가 도구로 노출될 때만 적용됩니다. 그래프 내부에서는 `node(agent, {inputSchema})`를 사용하여 노드 자체에서 노드의 입력을 검증하는 스키마를 설정하세요.

    그래프 내의 에이전트는 기본값인 `single_turn` 모드 또는 `task` 모드로 실행되어야 합니다.

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/data-handling/schemas.ts:schemas"
    ```

=== "Go"

    **workflow package**: use `workflow.NewAgentNodeTyped[Input, Output]` to
    attach schemas to an agent node. The generic type parameters are reflected
    into `*jsonschema.Schema` automatically — no hand-built schema construction
    needed. The node's `Event.Output` carries the structured result to the
    successor — no `OutputKey` or state write is needed:

    ```go
    --8<-- "examples/go/snippets/graphs/data-handling/main.go:input-output-schema"
    ```

    **Prebuilt workflow agents**: set `InputSchema` and `OutputSchema` on
    `llmagent.Config`. `OutputSchema` forces the model to reply with a JSON
    object matching the schema (the agent cannot use tools when `OutputSchema`
    is set). Use `OutputKey` to save the JSON string to state for downstream
    agents to reference via `{key}` in their `Instruction`.

## Access structured data in agents

=== "Python"

    Use the curly-brace `{ }` syntax to select properties from the input
    schema, or `< >` to select a property and also qualify it by the name
    of the source node:

    ```python
    class CityTime(BaseModel):
        time_info: str  # time information
        city: str       # city name

    def lookup_time_function(city: str):
        """Simulate returning the current time in the specified city."""
        return Event(output=CityTime(time_info='10:10 AM', city=city))

    city_report_agent = Agent(
        name="city_report_agent",
        model="gemini-flash-latest",
        input_schema=CityTime,

        # data selection based on class and parameter
        # instruction="""
        #     Return a sentence in the following format:
        #     It is {CityTime.time_info} in {CityTime.city} right now.
        # """,

        # more restrictive data selection based on source node name
        instruction="""
            Return a sentence in the following format:
            It is <CityTime.time_info from lookup_time_function> in
            <CityTime.city from lookup_time_function> right now.
        """,
    )

    root_agent = Workflow(
        name="root_agent",
        edges=[
            (START, city_generator_agent, lookup_time_function, city_report_agent)
        ],
    )
    ```

=== "TypeScript"

    에이전트 지침 내에서 두 가지 데이터 선택 양식을 사용할 수 있습니다:

    -   `{Class.field}` 양식은 이 노드의 입력에서 필드를 읽습니다.
    -   `<Class.field from source_node>` 양식은 지정된 이전 노드의 출력에서 필드를 읽습니다. 여러 업스트림 노드가 동일한 필드 이름을 공유할 때 이 양식을 사용하세요.

    두 양식 모두 세션 상태를 읽는 `{state_key}`와 구별됩니다. `Class.` 접두사는 문서화 용도일 뿐이며, 확인(resolution) 시 점(.) 뒤의 필드 이름을 사용합니다.

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/data-handling/structured_access.ts:structured-access"
    ```

=== "Go"

    In ADK Go v2.0.0, a `FunctionNode` returns a typed struct and the
    framework serializes it into `Event.Output`. The successor `AgentNode`
    receives the struct as its user content — the fields are available to the
    agent's `Instruction` without any `{key}` template syntax. This is the
    direct equivalent of Python's `input_schema=CityTime` with
    `{CityTime.time_info}` template placeholders: the struct fields are
    delivered as typed input rather than looked up by name from state.

    ```go
    --8<-- "examples/go/snippets/graphs/data-handling/main.go:structured-output"
    ```

For a complete example of this workflow, see
[Graph-based agent workflows](/graphs/#get-started).
