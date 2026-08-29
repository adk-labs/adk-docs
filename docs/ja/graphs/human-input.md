# Human input for agent workflows

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v2.0.0</span><span class="lst-typescript">TypeScript v2.0.0</span><span class="lst-go">Go v2.0.0</span>
</div>

Being able to request human input for data input, decision verification, or
action permission is an important part of many agent-powered workflows.
Graph-based workflows in ADK can include human in the loop (HITL) nodes
specifically built for obtaining input from humans as part of a workflow. These
nodes do not require artificial intelligence (AI) models to run, which can make
the input process more predictable and reliable.

## はじめに

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

    ADK TypeScript v2.0.0 では、人間の入力ノードは `RequestInput` を yield します。`step1` ノードはユーザーが応答するまでワークフローを一時停止し、その返信は入力として次のノードに渡されます。ヒューマンインザループ (HITL) ノードはモデルを必要としないため、一時停止が決定論的になります。

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/human-input/get_started.ts:get-started"
    ```

    この実装は、デフォルトの `rerunOnResume: false` ハンドオフを示しています。中断されたノードは再実行されず、ユーザーの返信を出力として完了します。`ctx.runNode()` を呼び出すノードには代わりに `rerunOnResume: true` が必要です。詳細については、[動的ワークフローでの人間の入力](/graphs/dynamic/#human-input) を参照してください。

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

## 構成オプション

=== "Python"

    Human input nodes can use the ***RequestInput*** class with the following
    configuration options:

    -   **`message`:** Text provided to the user to explain the human input
        request.
    -   **`payload`:** Structured data to be used as part of the human input
        request.
    -   **`response_schema`:** A data structure the human response must conform to.

=== "TypeScript"

    `RequestInput` クラスは次の構成オプションを受け取ります。

    -   **`message`:** 尋ねられている内容を説明する、ユーザーに表示されるテキスト。
    -   **`payload`:** クライアントが追加のコンテキストをレンダリングできるようにプロンプトとともに送信される構造化データ。
    -   **`responseSchema`:** 返信に期待される形式。スキーマは `functionCall.args.response_schema` として割り込み時に渡され、クライアントはこれを読み取って返信用のフォームをレンダリングします。

    ノードの `rerunOnResume` オプションは、返信が到着したときの動作を制御します。

    -   **`false`** (リーフのデフォルト): 返信は中断されたノードをバイパスして、ノードの後続ノードに入力としてルーティングされます。
    -   **`true`**: ノード本体が最初から再実行されます。この設定は、再開時にキャッシュされた子ノードの結果を配信できるように、`ctx.runNode()` を呼び出すノードに必要です。

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

!!! note "注: 応答スキーマの入力制限"

    応答スキーマは、人間の返信を指定された構造に合わせて自動的に再フォーマットしません。返信はすでにその形式である必要があります。より良いユーザーエクスペリエンスを提供するために、クライアントインターフェースで構造化データを収集するか、一時停止の後にエージェントノードを配置して返信を必要な形式に変換してください。

## 人間の入力 (Human Input) examples

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

    次の3ノードグラフは、構造化された旅程を作成し、クライアントがそれをレンダリングできるようにプロンプトとともに `payload` として送信し、ユーザーのフィードバックに基づいて動作します。

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

## ツール確認: LLM エージェントの承認プロンプト

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

    ツールが実行される前にエージェントが承認を求めて一時停止するようにするには、`FunctionTool` で `requireConfirmation: true` を設定します。グラフのヒューマンインザループ (HITL) ノードは別の目的に役立ちます。ツール呼び出しを確認する代わりに、ユーザーに入力を求めることでワークフローを開始できます。`responseSchema: z.string()` オプションはプレーンテキストの返信を要求します。

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
