# 에이전트 워크플로의 데이터 처리

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v2.0.0</span><span class="lst-typescript">TypeScript v2.0.0</span><span class="lst-go">Go v2.0.0</span>
</div>

에이전트와 그래프 기반 노드 간에 데이터를 구조화하고 관리하는 것은 ADK로 신뢰할 수 있는 프로세스를 구축하는 데 매우 중요합니다. 이 가이드는 그래프 노드 간에 정보가 전송되고 수신되는 방식을 포함하여 그래프 기반 워크플로 및 협업 에이전트 내의 데이터 처리를 설명합니다. 또한 데이터, 콘텐츠 및 상태를 전달하기 위한 필수 매개변수를 다루며, 데이터 형식 스키마와 특정 지침 구문을 사용하여 함수 노드와 에이전트 노드 모두에서 구조화된 데이터 전송을 구현하는 방법을 설명합니다.

## 워크플로 데이터 흐름

그래프 기반 워크플로 내에서 노드는 이벤트를 통해 다운스트림 단계로 데이터를 전달합니다. 한 단계가 명명된 이벤트 필드에 출력을 기록하면, 다음 단계가 이를 타입이 지정된 입력으로 받습니다.

=== "Python"

    Python에서는 ***Events***를 사용하여 그래프 노드 간에 데이터를 교환합니다. 노드 데이터 처리를 위한 주요 매개변수는 다음과 같습니다:

    -   **`output`**: *노드* 간에 정보를 전달하기 위한 매개변수입니다.
    -   **`message`**: 사용자에게 응답으로 전달할 데이터입니다.
    -   **`state`**: ADK 세션 전반에 걸쳐 ***Events***를 통해 노드 간에 자동으로 유지되는 데이터입니다.

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

    ADK Go v2.0.0에서 데이터 전달 메커니즘은 사용하는 에이전트 스타일에 따라 달라집니다:

    **workflow 패키지**(`FunctionNode`, `AgentNode`, `DynamicNode`): 노드는 Python과 유사하게 `session.Event` 필드를 통해 통신합니다:

    -   **`Event.Output`**: 노드의 반환 값으로, `FunctionNode`가 `*genai.Content`가 아닌 값을 반환할 때 프레임워크에 의해 자동으로 설정됩니다. 후속 노드는 이를 타입이 지정된 `input` 매개변수로 받습니다.
    -   **`Event.Routes`**: 따라갈 조건부 에지를 선택하기 위해 방출 노드가 명시적으로 설정하는 라우팅 키로, Python의 `Event(route=...)`에 해당합니다.
    -   **`Event.NodeInfo`**: 스케줄러 메타데이터(`path`, `MessageAsOutput`, `OutputFor`)입니다. 워크플로 엔진에 의해 설정되며 노드가 직접 설정하지 않습니다.

    **사전 구축된 워크플로 에이전트**(`sequentialagent`, `parallelagent`, `loopagent`): 이 에이전트들은 세션 상태를 통해 통신합니다:

    -   `llmagent.Config`의 **`OutputKey`**: 프레임워크가 각 턴 이후 에이전트의 최종 텍스트 응답을 `state[OutputKey]`에 기록합니다.
    -   **`ctx.Session().State().Set` / `.Get`**: 커스텀 코드 내에서 상태에 임의의 값을 쓰거나 읽습니다.
    -   `Instruction`의 **`{key}`**: 프레임워크가 모델을 호출하기 전에 프롬프트에 `state["key"]`를 치환합니다.

    상태 키에는 수명과 범위를 제어하는 접두사를 붙일 수 있습니다:

    | 접두사 상수 | 접두사 문자열 | 범위 |
    |---|---|---|
    | `session.KeyPrefixApp` | `"app:"` | 앱의 모든 사용자와 세션 간에 공유됨 |
    | `session.KeyPrefixUser` | `"user:"` | 사용자에게 귀속되며 해당 사용자의 세션 간에 공유됨 |
    | `session.KeyPrefixTemp` | `"temp:"` | 현재 호출이 종료된 후 폐기됨 |
    | *(없음)* | — | 세션 수명 동안 유지됨 |

### 노드 출력

워크플로의 각 단계는 후속 노드를 위한 출력을 생성합니다.

=== "Python"

    데이터를 다음 노드로 넘기려면 ***return*** 또는 ***yield*** 구문을 사용하세요:

    ```python
    from google.adk import Event

    def my_function_node(node_input: str):
        output_value = node_input.upper()
        return Event(output=output_value) # "THE RESULT"
    ```

    추가 처리가 필요하지 않은 ***Event*** 데이터를 출력할 때는 ***return*** 구문을 사용하세요. 추가 처리가 필요한 데이터를 방출하거나 둘 이상의 데이터 항목을 생성하는 경우에는 여러 개의 ***yield*** 명령을 사용할 수 있습니다. 각 ***yield*** 호출은 그래프의 다음 노드로 전달되는 Event의 데이터 객체 목록에 추가됩니다. 매개변수 없는 ***return*** 또는 ***yield*** 명령은 다음 노드에 `None` 값을 전달합니다.

=== "TypeScript"

    노드의 출력을 생성하는 세 가지 동등한 방법이 있습니다: 값을 직접 반환하거나, `createEvent({output})`를 반환하거나, 결과와 함께 진행 상황을 스트리밍하기 위해 비동기 제너레이터(async generator)에서 이벤트를 yield하는 것입니다.

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/data-handling/node_output.ts:node-output"
    ```

    !!! warning "주의: 실행당 하나의 이벤트에서만 `output`을 방출하세요"

        노드는 `output`을 담은 이벤트를 여러 번 yield할 수 있으며, 이 경우 ADK는 오류를 발생시키지 않습니다. 각 이벤트는 이전 이벤트를 덮어쓰며, 후속 노드는 최종 값만 받게 됩니다. 진행 상황 메시지에는 `content`를 대신 사용하세요.

=== "Go"

    **workflow 패키지**: `FunctionNode`는 단순히 타입이 지정된 Go 값을 반환합니다. 프레임워크는 반환 값을 자동으로 `session.Event`로 래핑하고 `Event.Output`을 설정합니다. 후속 노드는 이 값을 타입이 지정된 `input` 매개변수로 받으므로 수동으로 이벤트를 생성할 필요가 없습니다:

    ```go
    --8<-- "examples/go/snippets/graphs/data-handling/main.go:event-output"
    ```

    **사전 구축된 워크플로 에이전트**: `llmagent.Config`에서 `OutputKey`를 사용하여 에이전트의 텍스트 응답을 세션 상태에 저장한 다음, 다운스트림 에이전트의 `Instruction` 템플릿에서 `{key}`로 참조하세요:

    ```go
    --8<-- "examples/go/snippets/graphs/data-handling/main.go:output-key"
    ```

### 노드 출력: 구조화된 데이터 전달

=== "Python"

    직렬화 가능한 형식으로 더 길고 구조화된 데이터를 전달할 수 있습니다:

    ```python
    def my_function_node_3():
        yield Event(
            output={
                "city_name": "Paris",
                "city_time": "10:10 AM",
            },
        )
    ```

    !!! warning "주의: Event.output 제한사항"

        노드는 실행당 단일 ***Event.output*** 데이터 페이로드만 방출할 수 있습니다. 즉, 노드에서 여러 개의 ***yield***를 사용할 수는 있지만 ***Event.output***이 포함된 ***yield*** 명령을 두 번 이상 사용하면 런타임 오류가 발생합니다.

=== "TypeScript"

    `output` 필드는 텍스트에만 국한되지 않습니다. 직렬화 가능한 모든 값은 다음 노드로 전달되며, JSON 파싱이나 상태 읽기 없이도 타입이 지정된 객체로 수신됩니다. 출력을 생성하는 노드에 `outputSchema`를 연결하거나, 소비하는 노드에 `inputSchema`를 연결하면 계약이 명시화되고 런타임에 유효성이 검증됩니다:

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/data-handling/structured_output.ts:structured-output"
    ```

=== "Go"

    **workflow 패키지**: `FunctionNode`는 JSON 직렬화가 가능한 모든 Go 구조체를 반환할 수 있습니다. 프레임워크는 이를 `Event.Output`으로 직렬화하고 후속 노드의 타입이 지정된 `input` 매개변수로 다시 역직렬화합니다. 단일 페이로드 제한은 없으며 각 노드는 정확히 하나의 타입이 지정된 반환 값을 가집니다:

    ```go
    --8<-- "examples/go/snippets/graphs/data-handling/main.go:structured-output"
    ```

    **사전 구축된 워크플로 에이전트**: 에이전트마다 하나씩 여러 `OutputKey` 값을 사용하여 세션 상태에 개별 필드를 저장하세요. 다운스트림 에이전트는 `Instruction`에서 `{key}`를 통해 각 필드를 독립적으로 읽습니다.

### 라우팅 출력

=== "Python"

    조건부 에지 디스패치를 수행하려면 ***Event***의 `route` 매개변수를 사용하세요:

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

    **workflow 패키지**: 이벤트를 방출하는 `FunctionNode`는 `session.Event`를 직접 생성하고, `Event.Routes`를 원하는 라우트 키로 설정하며, 페이로드를 후속 노드로 전달하기 위해 `Event.Output`을 설정합니다. 워크플로 엔진은 디스패치 시점에 `Event.Routes`를 읽어 일치하는 에지를 선택합니다:

    ```go
    --8<-- "examples/go/snippets/graphs/data-handling/main.go:routing-output"
    ```

### 사용자 대상 메시지

=== "Python"

    다음 노드로 데이터를 전달하는 대신 사용자에게 응답을 보내려면 ***Event***의 ***message*** 매개변수를 사용하세요:

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

    **workflow 패키지**: 노드의 타입이 지정된 출력을 진행시키지 않고 사용자에게 표시되는 메시지를 방출하려면, `EmittingFunctionNode`의 `emit` 콜백을 통해 방출되는 중간 이벤트에 `Event.Content`를 설정하세요. 최종 반환 값(또는 `nil`)이 `Event.Output`을 제어합니다.

    **사전 구축된 워크플로 에이전트**: 모든 `llmagent` 단계는 모델 응답을 사용자 대상 이벤트로 자동 방출합니다. 비 LLM 단계의 경우, 텍스트가 포함된 `LLMResponse.Content`를 가진 이벤트를 yield하는 커스텀 `Run` 함수를 `agent.Agent`에 작성하세요.

### 세션 상태 및 상태 범위

세션 상태는 세션 내의 여러 턴에 걸쳐 데이터를 유지합니다. 이는 사전 구축된 워크플로 에이전트의 주요 데이터 공유 메커니즘이며, 사용하는 에이전트 스타일에 관계없이 도구와 콜백 내부에서도 사용할 수 있습니다.

=== "Python"

    노드 간에 값을 유지하려면 ***Event***의 ***state*** 매개변수를 사용하세요. 노드는 상태 값을 수정할 수 있으며, 수정된 상태 값은 다운스트림 노드에서 사용할 수 있습니다:

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

    !!! warning "주의: `state` 프로퍼티 데이터 제한사항"

        state 매개변수는 노드 간에 *대량의 데이터를 유지하는 용도로 사용해서는 안 됩니다*. Workflow 수명 주기 동안 대용량 데이터 리소스를 유지하려면 아티팩트나 데이터베이스 도구와 같은 다른 데이터 영구 저장 메커니즘을 사용하세요.

=== "TypeScript"

    상태를 반환하는 대신 `ctx.state`를 통해 상태를 작성하세요. 기록된 상태는 동일한 실행 내의 모든 후속 노드에서 즉시 확인할 수 있으며, 작성 노드의 이벤트와 함께 커밋됩니다:

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/data-handling/session_state.ts:session-state"
    ```

    !!! warning "주의: `state` 데이터 제한사항"

        세션 상태는 가벼운 키-값 저장소입니다. 노드 간에 대용량 페이로드를 이동하는 데 사용하지 마세요. 대신 아티팩트나 데이터베이스 도구를 사용하세요. 다음 노드에만 값이 필요한 경우에는 노드 `output`으로 edge를 따라 전달하세요. 값이 실행 이후에도 유지되어야 하거나 도구, 콜백, 또는 `{key}` 지침 템플릿에서 읽어야 하는 경우에 상태를 사용하세요.

=== "Go"

    상태는 `ctx.Session().State().Set(key, value)`로 쓰고 `.Get(key)`로 읽습니다. `session` 패키지는 Python의 state 매개변수와 동일한 수명 범위에 매핑되는 접두사 상수를 정의합니다. 이 패턴은 사전 구축된 워크플로 에이전트와 모든 에이전트 스타일의 도구 및 콜백에 적용됩니다:

    ```go
    --8<-- "examples/go/snippets/graphs/data-handling/main.go:state-scopes"
    ```

    !!! warning "주의: 상태 데이터 제한사항"

        세션 상태는 가벼운 키-값 저장소입니다. 파일 콘텐츠나 바이너리 데이터와 같은 대용량 페이로드를 유지하는 데 사용하지 마세요. 대신 ADK 아티팩트나 외부 스토리지 도구를 사용하세요.

    !!! tip "workflow 패키지: 상태보다 Event.Output을 선호하세요"

        `workflow` 패키지(`FunctionNode`, `AgentNode`, `DynamicNode`)의 경우, 타입이 지정된 값을 반환하여 노드 간에 데이터를 전달하세요. 프레임워크가 `Event.Output`을 자동으로 설정합니다. 도구, 콜백 또는 에이전트 `Instruction` 템플릿과 값을 공유해야 할 때만 `State().Set`을 사용하세요.

## 스키마로 노드 데이터 제한하기

입력 및 출력 데이터 스키마를 설정하여 모든 에이전트 노드가 수락하고 생성하는 데이터 형식을 제한할 수 있습니다.

=== "Python"

    ***BaseModel***을 확장하는 클래스와 함께 `input_schema` 및 `output_schema`를 사용하여 에이전트의 입력과 출력을 제한하세요:

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

    **workflow 패키지**: `workflow.NewAgentNodeTyped[Input, Output]`을 사용하여 에이전트 노드에 스키마를 연결하세요. 제네릭 타입 매개변수가 `*jsonschema.Schema`에 자동으로 반영되므로 스키마를 수동으로 구성할 필요가 없습니다. 노드의 `Event.Output`이 구조화된 결과를 후속 노드로 전달하므로 `OutputKey`나 상태 쓰기가 필요하지 않습니다:

    ```go
    --8<-- "examples/go/snippets/graphs/data-handling/main.go:input-output-schema"
    ```

    **사전 구축된 워크플로 에이전트**: `llmagent.Config`에서 `InputSchema` 및 `OutputSchema`를 설정하세요. `OutputSchema`는 모델이 스키마와 일치하는 JSON 객체로 응답하도록 강제합니다(`OutputSchema`가 설정된 경우 에이전트는 도구를 사용할 수 없습니다). 다운스트림 에이전트가 `Instruction`에서 `{key}`를 통해 참조할 수 있도록 JSON 문자열을 상태에 저장하려면 `OutputKey`를 사용하세요.

## 에이전트에서 구조화된 데이터에 액세스하기

=== "Python"

    입력 스키마에서 프로퍼티를 선택하려면 중괄호 `{ }` 구문을 사용하고, 프로퍼티를 선택하면서 소스 노드의 이름으로 한정하려면 `< >`를 사용하세요:

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

    ADK Go v2.0.0에서 `FunctionNode`는 타입이 지정된 구조체를 반환하고 프레임워크는 이를 `Event.Output`으로 직렬화합니다. 후속 `AgentNode`는 구조체를 사용자 콘텐츠로 수신하므로 `{key}` 템플릿 구문 없이도 에이전트의 `Instruction`에서 필드를 사용할 수 있습니다. 이는 `{CityTime.time_info}` 템플릿 플레이스홀더와 함께 사용하는 Python의 `input_schema=CityTime`에 직접 대응되며, 구조체 필드는 상태에서 이름으로 조회되는 대신 타입이 지정된 입력으로 전달됩니다.

    ```go
    --8<-- "examples/go/snippets/graphs/data-handling/main.go:structured-output"
    ```

이 워크플로의 전체 예제는 [그래프 기반 에이전트 워크플로](/graphs/#get-started)를 참조하세요.
