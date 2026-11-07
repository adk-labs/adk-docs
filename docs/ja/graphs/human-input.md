# エージェントワークフローでの人間の入力 (Human input)

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v2.0.0</span><span class="lst-typescript">TypeScript v2.0.0</span><span class="lst-go">Go v2.0.0</span>
</div>

データ入力、意思決定の検証、またはアクションの許可のために人間の入力を要求できることは、多くのエージェントを活用したワークフローにおいて重要な要素です。ADK のグラフベースのワークフローには、ワークフローの一部として人間から入力を取得するために特別に構築されたヒューマンインザループ (HITL) ノードを含めることができます。これらのノードは実行に人工知能 (AI) モデルを必要としないため、入力プロセスをより予測可能で信頼性の高いものにすることができます。

## はじめに

=== "Python"

    ***RequestInput*** クラスとユーザー向けのテキストプロンプトを使用して、グラフ内に人間の入力ノードを実装できます。次のコード例は、Workflow グラフに人間の入力ノードを追加する方法を示しています。

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

    このコード例では、システムがユーザーからの入力を受け取るまで、`step1` がエージェントの実行を一時停止します。システムがユーザーから入力を受け取ると、その入力は次のノードに渡されます。

=== "TypeScript"

    ADK TypeScript では、人間の入力ノードは `RequestInput` を yield します。`step1` ノードはユーザーが応答するまでワークフローを一時停止し、その返信は入力として次のノードに渡されます。ヒューマンインザループ (HITL) ノードはモデルを必要としないため、一時停止が決定論的になります。

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/human-input/get_started.ts:get-started"
    ```

    この実装は、デフォルトの `rerunOnResume: false` ハンドオフを示しています。中断されたノードは再実行されず、ユーザーの返信を出力として完了します。`ctx.runNode()` を呼び出すノードには代わりに `rerunOnResume: true` が必要です。詳細については、[動的ワークフローでの人間の入力](/ja/graphs/dynamic/#human-input) を参照してください。

=== "Go"

    ADK Go では、人間の入力ノードは `workflow.NewRequestInputEvent` でリクエストを発行し、`workflow.ErrNodeInterrupted` を返します。`step1` ノードはユーザーが応答するまでワークフローを一時停止します。このノードは再実行されません。返信がその出力となり、次のノードに渡されます。

    ```go
    --8<-- "examples/go/snippets/graphs/human-input/main.go:graph-hitl-handoff"
    ```

    返信後に再実行する必要があるノードは、代わりに `RerunOnResume` を設定し、`workflow.ResumeOrRequestInput` を呼び出します。詳細については、[動的ワークフローでの人間の入力](/ja/graphs/dynamic/#human-input) を参照してください。

## 構成オプション

=== "Python"

    人間の入力ノードでは、次の構成オプションとともに ***RequestInput*** クラスを使用できます。

    -   **`message`:** 人間の入力リクエストを説明するためにユーザーに提供されるテキスト。
    -   **`payload`:** 人間の入力リクエストの一部として使用される構造化データ。
    -   **`response_schema`:** 人間の応答が準拠しなければならないデータ構造。

=== "TypeScript"

    `RequestInput` クラスは次の構成オプションを受け取ります。

    -   **`message`:** 尋ねられている内容を説明する、ユーザーに表示されるテキスト。
    -   **`payload`:** クライアントが追加のコンテキストをレンダリングできるようにプロンプトとともに送信される構造化データ。
    -   **`responseSchema`:** 返信に期待される形式。スキーマは `functionCall.args.response_schema` として割り込み時に渡され、クライアントはこれを読み取って返信用のフォームをレンダリングします。

    ノードの `rerunOnResume` オプションは、返信が到着したときの動作を制御します。

    -   **`false`** (リーフのデフォルト): 返信は中断されたノードをバイパスして、ノードの後続ノードに入力としてルーティングされます。
    -   **`true`**: ノード本体が最初から再実行されます。この設定は、再開時にキャッシュされた子ノードの結果を配信できるように、`ctx.runNode()` を呼び出すノードに必要です。

=== "Go"

    `session.RequestInput` には次のフィールドがあり、Python の `RequestInput` パラメータに直接マッピングされます。

    -   **`InterruptID`** (`string`): この一時停止ポイントの一意の識別子。ワークフロー実行間での衝突を避けるため、固定のプレフィックスと UUID を組み合わせて使用してください。Python の暗黙的な割り込み ID に相当します。
    -   **`Message`** (`string`): ユーザーに表示される人間が読めるプロンプト。Python の `message` パラメータに相当します。
    -   **`Payload`** (`any`): クライアントが追加のコンテキストをレンダリングできるようにプロンプトとともに送信されるオプションの構造化データ。Python の `payload` パラメータに相当します。
    -   **`ResponseSchema`** (`*jsonschema.Schema`): 返信が準拠しなければならないオプションの JSON スキーマ。Python の `response_schema` パラメータに相当します。

    `workflow.NodeConfig.RerunOnResume` フィールドは再開時の動作を制御します。

    -   **`&true`**: ノード本体が最初から再実行され、2 回目のパスで `ResumeOrRequestInput` が人間の返信を返します。`ResumeOrRequestInput` を使用するノードで必須です。
    -   **`&false`** または **`nil`** (リーフのデフォルト): 返信は中断されたノードをバイパスして、ノードの後続ノードに入力としてルーティングされます。

!!! note "注: 応答スキーマの入力制限"

    応答スキーマは、人間の返信を指定された構造に合わせて自動的に再フォーマットしません。返信はすでにその形式である必要があります。より良いユーザーエクスペリエンスを提供するために、クライアントインターフェースで構造化データを収集するか、一時停止の後にエージェントノードを配置して返信を必要な形式に変換してください。

## 人間の入力の例

次のコード例は、より詳細な人間の入力リクエストを示しています。

### メッセージとペイロードを指定して入力を要求する

=== "Python"

    次のコードサンプルは、***payload*** と ***response schema*** を含む ***RequestInput*** オブジェクトをワークフローノード内で構築する方法を示しています。この例では、`ActivitiesList` はアクティビティのリストを作成するエージェントノードによって完成されることが想定されており、`get_user_feedback()` ノードがユーザーにフィードバックを要求します。

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

    次のコードサンプルは3ノードグラフを示しています。ビルダーノードが構造化された旅程を生成し、HITL ノードがプロンプトとともに `Payload` として送信し、最後のノードがユーザーのフィードバックに基づいて動作します。`Payload` フィールドにより、クライアントはユーザーが応答する前に旅程全体をレンダリングできます。

    ```go
    --8<-- "examples/go/snippets/graphs/human-input/main.go:graph-hitl-with-payload"
    ```

## ツール確認: LLM エージェントの承認プロンプト

ツール確認 (Tool-confirmation) は、はい/いいえの承認プロンプトのための独立した LLM エージェントレベルのメカニズムです。グラフの HITL ノードとは異なり、ツール確認はスタンドアロンのグラフノードとしてではなく、`llmagent` のツール関数内で動作します。特定のツール呼び出しを実行する前に LLM エージェントを一時停止して承認を求めたい場合に便利です。

=== "Python"

    次のコードサンプルは、***response schema*** を含む ***RequestInput*** オブジェクトをワークフローノード内で構築する方法を示しています。

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

    ツールが実行される前に静的なはい/いいえの承認を求めるには `functiontool.Config` で `RequireConfirmation: true` を設定するか、カスタムヒントメッセージを表示するにはツール内から `ctx.RequestConfirmation` を呼び出します。

    ```go
    --8<-- "examples/go/snippets/graphs/human-input/main.go:simple-hitl"
    ```

    手動の再エントリ処理を伴うカスタムヒントの場合:

    ```go
    --8<-- "examples/go/snippets/graphs/human-input/main.go:hitl-with-hint"
    ```
