# 에이전트 워크플로의 인간 입력(Human input)

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v2.0.0</span><span class="lst-typescript">TypeScript v2.0.0</span><span class="lst-go">Go v2.0.0</span>
</div>

데이터 입력, 의사결정 검증 또는 작업 권한 승인을 위해 인간 입력을 요청할 수 있는 기능은 많은 에이전트 기반 워크플로에서 중요한 부분입니다. ADK의 그래프 기반 워크플로에는 워크플로의 일부로 사람으로부터 입력을 받기 위해 특별히 구축된 인간 참여형(HITL, Human-in-the-Loop) 노드를 포함할 수 있습니다. 이러한 노드는 실행하는 데 인공지능(AI) 모델이 필요하지 않으므로 입력 프로세스를 더 예측 가능하고 안정적으로 만들 수 있습니다.

## 시작하기

=== "Python"

    ***RequestInput*** 클래스와 사용자에게 표시할 텍스트 프롬프트를 사용하여 그래프에서 인간 입력 노드를 구현할 수 있습니다. 다음 코드 예시는 워크플로 그래프에 인간 입력 노드를 추가하는 방법을 보여줍니다:

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

    이 코드 예시에서 `step1`은 시스템이 사용자로부터 입력을 받을 때까지 에이전트의 실행을 일시 중지합니다. 시스템이 사용자로부터 입력을 받으면 해당 입력은 다음 노드로 전달됩니다.

=== "TypeScript"

    ADK TypeScript에서 인간 입력 노드는 `RequestInput`을 yield합니다. `step1` 노드는 사용자가 응답할 때까지 워크플로를 일시 중지하고, 사용자의 응답은 다음 노드의 입력으로 전달됩니다. 인간 참여형(HITL) 노드는 모델을 필요로 하지 않으므로 일시 중지가 결정론적입니다.

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/human-input/get_started.ts:get-started"
    ```

    이 구현은 기본값인 `rerunOnResume: false` 핸드오프를 보여줍니다. 중단된 노드는 다시 실행되지 않으며, 사용자의 응답을 출력으로 삼아 완료됩니다. `ctx.runNode()`를 호출하는 노드는 대신 `rerunOnResume: true`가 필요합니다. 자세한 내용은 [동적 워크플로에서의 인간 입력](/ko/graphs/dynamic/#human-input)을 참조하세요.

=== "Go"

    ADK Go에서 인간 입력 노드는 `workflow.NewRequestInputEvent`로 요청을 방출하고 `workflow.ErrNodeInterrupted`를 반환합니다. `step1` 노드는 사용자가 응답할 때까지 워크플로를 일시 중지합니다. 해당 노드는 다시 실행되지 않으며, 응답이 그 출력이 되어 다음 노드로 전달됩니다.

    ```go
    --8<-- "examples/go/snippets/graphs/human-input/main.go:graph-hitl-handoff"
    ```

    응답 후에 다시 실행되어야 하는 노드는 대신 `RerunOnResume`을 설정하고 `workflow.ResumeOrRequestInput`을 호출합니다. 자세한 내용은 [동적 워크플로에서의 인간 입력](/ko/graphs/dynamic/#human-input)을 참조하세요.

## 구성 옵션

=== "Python"

    인간 입력 노드는 다음 구성 옵션과 함께 ***RequestInput*** 클래스를 사용할 수 있습니다:

    -   **`message`:** 인간 입력 요청을 설명하기 위해 사용자에게 제공되는 텍스트입니다.
    -   **`payload`:** 인간 입력 요청의 일부로 사용될 구조화된 데이터입니다.
    -   **`response_schema`:** 사람의 응답이 준수해야 하는 데이터 구조입니다.

=== "TypeScript"

    `RequestInput` 클래스는 다음 구성 옵션을 사용합니다:

    -   **`message`:** 사용자에게 질문 내용을 설명하는 텍스트입니다.
    -   **`payload`:** 클라이언트가 추가 컨텍스트를 렌더링할 수 있도록 프롬프트와 함께 전송되는 구조화된 데이터입니다.
    -   **`responseSchema`:** 응답이 취할 것으로 예상되는 형태입니다. 스키마는 인터럽트 시 `functionCall.args.response_schema`로 전달되며, 클라이언트는 이를 읽어 응답용 양식을 렌더링합니다.

    노드의 `rerunOnResume` 옵션은 응답이 도착했을 때 일어나는 동작을 제어합니다:

    -   **`false`** (리프 노드 기본값): 응답이 중단된 노드를 우회하여 해당 노드의 후속 노드에 입력으로 라우팅됩니다.
    -   **`true`**: 노드 본문이 처음부터 다시 실행됩니다. 이 설정은 `ctx.runNode()`를 호출하는 모든 노드에 필요하며, 재개 시 캐시된 하위 결과를 전달할 수 있습니다.

=== "Go"

    `session.RequestInput`은 Python의 `RequestInput` 매개변수에 직접 매핑되는 다음 필드를 포함합니다:

    -   **`InterruptID`** (`string`): 이 일시 중지 지점에 대한 고유 식별자입니다. 워크플로 실행 간 충돌을 방지하려면 고정 접두사와 UUID를 함께 사용하세요. Python의 암시적 인터럽트 ID에 해당합니다.
    -   **`Message`** (`string`): 사용자에게 표시되는 사람이 읽을 수 있는 프롬프트입니다. Python의 `message` 매개변수에 해당합니다.
    -   **`Payload`** (`any`): 클라이언트가 추가 컨텍스트를 렌더링할 수 있도록 프롬프트와 함께 전송되는 선택적 구조화 데이터입니다. Python의 `payload` 매개변수에 해당합니다.
    -   **`ResponseSchema`** (`*jsonschema.Schema`): 응답이 준수해야 하는 선택적 JSON 스키마입니다. Python의 `response_schema` 매개변수에 해당합니다.

    `workflow.NodeConfig.RerunOnResume` 필드는 재개 시 동작을 제어합니다:

    -   **`&true`**: 노드 본문이 처음부터 다시 실행되며, 두 번째 패스에서 `ResumeOrRequestInput`이 사용자의 응답을 반환합니다. `ResumeOrRequestInput`을 사용하는 노드에 필수입니다.
    -   **`&false`** 또는 **`nil`** (리프 기본값): 응답이 중단된 노드를 우회하여 해당 노드의 후속 노드에 입력으로 라우팅됩니다.

!!! note "참고: 응답 스키마 입력 제한사항"

    응답 스키마는 사람의 응답을 지정된 구조에 맞게 자동으로 재구성하지 않습니다. 응답은 이미 해당 형식이어야 합니다. 더 나은 사용자 경험을 위해 클라이언트 인터페이스에서 구조화된 데이터를 수집하거나, 일시 중지 뒤에 에이전트 노드를 배치하여 응답을 필요한 형식으로 변환하세요.

## 인간 입력 예시

다음 코드 예시는 보다 상세한 인간 입력 요청을 보여줍니다.

### 메시지 및 페이로드와 함께 입력 요청하기

=== "Python"

    다음 코드 샘플은 ***payload*** 및 ***response schema***를 포함하여 워크플로 노드에서 ***RequestInput*** 객체를 생성하는 방법을 보여줍니다. 이 예시에서 `ActivitiesList`는 활동 목록을 구성하는 에이전트 노드에 의해 완성될 것으로 예상되며, `get_user_feedback()` 노드는 사용자에게 피드백을 요청합니다.

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

    다음 코드 샘플은 3개 노드 그래프를 보여줍니다. 빌더 노드가 구조화된 여행 일정을 생성하고, HITL 노드가 이를 프롬프트와 함께 `Payload`로 전송하며, 마지막 노드가 사용자의 피드백에 따라 작동합니다. `Payload` 필드를 사용하면 클라이언트가 사용자가 응답하기 전에 전체 여행 일정을 렌더링할 수 있습니다:

    ```go
    --8<-- "examples/go/snippets/graphs/human-input/main.go:graph-hitl-with-payload"
    ```

## 도구 확인: LLM 에이전트의 승인 프롬프트

도구 확인(Tool-confirmation)은 예/아니요 승인 프롬프트를 위한 별도의 LLM 에이전트 수준 메커니즘입니다. 그래프 HITL 노드와 달리 도구 확인은 독립형 그래프 노드가 아니라 `llmagent` 도구 함수 내부에서 작동합니다. LLM 에이전트가 특정 도구 호출을 실행하기 전에 일시 중지하고 승인을 요청하도록 할 때 유용합니다.

=== "Python"

    다음 코드 샘플은 ***response schema***를 포함하여 워크플로 노드에서 ***RequestInput*** 객체를 생성하는 방법을 보여줍니다:

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

    도구가 실행되기 전에 정적 예/아니요 승인을 받으려면 `functiontool.Config`에서 `RequireConfirmation: true`를 설정하거나, 사용자 지정 힌트 메시지를 위해 도구 내부에서 `ctx.RequestConfirmation`을 호출하세요:

    ```go
    --8<-- "examples/go/snippets/graphs/human-input/main.go:simple-hitl"
    ```

    수동 재진입 처리가 포함된 사용자 지정 힌트의 경우:

    ```go
    --8<-- "examples/go/snippets/graphs/human-input/main.go:hitl-with-hint"
    ```
