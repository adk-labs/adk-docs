# エージェントワークフローのデータ処理

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v2.0.0</span><span class="lst-typescript">TypeScript v2.0.0</span><span class="lst-go">Go v2.0.0</span>
</div>

エージェントとグラフベースのノード間でデータを構造化して管理することは、ADK で信頼性の高いプロセスを構築するうえで不可欠です。このガイドでは、グラフノード間で情報がどのように送受信されるかを含め、グラフベースワークフローおよび協調エージェント内のデータ処理について説明します。また、データ、コンテンツ、状態を渡すための必須パラメータを取り上げ、データ形式スキーマと特定の instruction 構文を使用して関数ノードとエージェントノードの両方で構造化データ転送を実装する方法を説明します。

## ワークフローのデータフロー

グラフベースワークフロー内では、ノードはイベントを通じてダウンストリームのステップにデータを渡します。あるステップが名前付きイベントフィールドに出力を書き込み、次のステップがそれを型付き入力として受け取ります。

=== "Python"

    Python では、***Events*** を使用してグラフノード間でデータが交換されます。ノードのデータ処理における主なパラメータは次のとおりです:

    -   **`output`**: *ノード*間で情報を渡すためのパラメータ。
    -   **`message`**: ユーザーへの応答として意図されたデータ。
    -   **`state`**: ADK セッション全体を通じて ***Events*** によりノード間で自動的に永続化されるデータ。

=== "TypeScript"

    ADK TypeScript v2.0.0 では、ノードはイベントを通じてデータを交換します。ノードのデータ処理における主なフィールドは次のとおりです。

    -   **`output`**: 次のノードに渡される値。値を直接返すと ADK がそれをイベントにラップします。または `createEvent({output})` で明示的にフィールドを設定します。
    -   **`content`**: ユーザー向けのメッセージ。ランタイムはこのフィールドをレンダリングしますが、グラフはこれを次のノードに渡しません。
    -   **`route`**: 追従する条件付き edge を選択するルーティングキー。

    セッション状態 (Session state) はイベントから分離されています。ノードは `ctx.state` を介して状態の読み書きを行い、累積された差分はそのノードのイベントに添付されます。状態キーには有効期間とスコープを制御するプレフィックスを付けることができます。

    | プレフィックス | スコープ |
    |---|---|
    | `app:` | アプリのすべてのユーザーおよびセッション間で共有 |
    | `user:` | ユーザーに関連付けられ、そのセッション間で共有 |
    | `temp:` | 現在の呼び出しが終了した後に破棄 |
    | *(なし)* | セッションの有効期間中保持 |

=== "Go"

    ADK Go v2.0.0 では、データ受け渡しのメカニズムは使用するエージェントスタイルによって異なります:

    **workflow パッケージ**（`FunctionNode`、`AgentNode`、`DynamicNode`）: ノードは Python と同様に `session.Event` フィールドを介して通信します:

    -   **`Event.Output`**: ノードの戻り値であり、`FunctionNode` が `*genai.Content` 以外の値を返したときにフレームワークによって自動的に設定されます。後続ノードはこれを型付き `input` パラメータとして受け取ります。
    -   **`Event.Routes`**: どの条件付きエッジをたどるかを選択するために発行ノードが明示的に設定するルーティングキーであり、Python の `Event(route=...)` に相当します。
    -   **`Event.NodeInfo`**: スケジューラメタデータ（`path`、`MessageAsOutput`、`OutputFor`）。ワークフローエンジンによって設定され、ノードが直接設定することはありません。

    **事前構築済みワークフローエージェント**（`sequentialagent`、`parallelagent`、`loopagent`）: これらのエージェントはセッション状態を介して通信します:

    -   `llmagent.Config` の **`OutputKey`**: フレームワークは各ターンの後にエージェントの最終テキスト応答を `state[OutputKey]` に書き込みます。
    -   **`ctx.Session().State().Set` / `.Get`**: カスタムコード内で状態に対して任意の値を読み書きします。
    -   `Instruction` 内の **`{key}`**: フレームワークはモデルを呼び出す前に `state["key"]` をプロンプトに置換します。

    状態キーには、その有効期間とスコープを制御するプレフィックスを付けることができます:

    | プレフィックス定数 | プレフィックス文字列 | スコープ |
    |---|---|---|
    | `session.KeyPrefixApp` | `"app:"` | アプリのすべてのユーザーとセッション間で共有される |
    | `session.KeyPrefixUser` | `"user:"` | ユーザーに紐付き、そのユーザーのセッション間で共有される |
    | `session.KeyPrefixTemp` | `"temp:"` | 現在の呼び出しが終了した後に破棄される |
    | *（なし）* | — | セッションの有効期間中保持される |

### ノード出力

ワークフローの各ステップは、後続ステップへの出力を生成します。

=== "Python"

    次のノードにデータを引き渡すには、***return*** または ***yield*** 構文を使用します:

    ```python
    from google.adk import Event

    def my_function_node(node_input: str):
        output_value = node_input.upper()
        return Event(output=output_value) # "THE RESULT"
    ```

    追加処理を必要としない ***Event*** データを出力する場合は、***return*** 構文を使用します。追加処理が必要なデータを発行する場合や、複数のデータ項目を生成する場合は、複数の ***yield*** コマンドを使用できます。各 ***yield*** 呼び出しは、グラフの次のノードに渡される Event 上のデータオブジェクトのリストに追加されます。パラメータなしの ***return*** または ***yield*** コマンドは、次のノードに `None` 値を渡します。

=== "TypeScript"

    ノードの出力を生成するには、同等の3つの方法があります。値を直接返すか、`createEvent({output})` を返すか、結果とともに進行状況をストリーミングするために非同期ジェネレーター (async generator) からイベントを yield します。

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/data-handling/node_output.ts:node-output"
    ```

    !!! warning "警告: 1回の実行につき1つのイベントから `output` を出力してください"

        ノードは `output` を持つイベントをいくつでも yield できますが、この場合 ADK はエラーを発生させません。各イベントは前のイベントを上書きし、後続ノードは最終値のみを受け取ります。進行状況メッセージには代わりに `content` を使用してください。

=== "Go"

    **workflow パッケージ**: `FunctionNode` は単に型付きの Go 値を返します。フレームワークは戻り値を自動的に `session.Event` でラップし、`Event.Output` を設定します。後続ノードはこの値を型付き `input` パラメータとして受け取るため、手動でのイベント構築は不要です:

    ```go
    --8<-- "examples/go/snippets/graphs/data-handling/main.go:event-output"
    ```

    **事前構築済みワークフローエージェント**: `llmagent.Config` の `OutputKey` を使用してエージェントのテキスト応答をセッション状態に保存し、ダウンストリームエージェントの `Instruction` テンプレート内で `{key}` として参照します:

    ```go
    --8<-- "examples/go/snippets/graphs/data-handling/main.go:output-key"
    ```

### ノード出力: 構造化データの受け渡し

=== "Python"

    シリアライズ可能な形式で、より長く構造化されたデータを渡すことができます:

    ```python
    def my_function_node_3():
        yield Event(
            output={
                "city_name": "Paris",
                "city_time": "10:10 AM",
            },
        )
    ```

    !!! warning "注意: Event.output の制限"

        ノードは 1 回の実行につき 1 つの ***Event.output*** データペイロードしか発行できません。つまり、ノード内で複数の ***yield*** を使用することはできますが、***Event.output*** を伴う ***yield*** コマンドが 2 つ以上あるとランタイムエラーになります。

=== "TypeScript"

    `output` フィールドはテキストに限定されません。シリアライズ可能な任意の値が次のノードに渡され、JSON の解析や状態の読み取りを必要とせず、型付きオブジェクトとして受け取ることができます。生成側のノードに `outputSchema` をアタッチするか、消費側のノードに `inputSchema` をアタッチすることで、契約が明示的になり、実行時に検証されます。

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/data-handling/structured_output.ts:structured-output"
    ```

=== "Go"

    **workflow パッケージ**: `FunctionNode` は JSON シリアライズ可能な任意の Go 構造体を返すことができます。フレームワークはそれを `Event.Output` にシリアライズし、後続ノードの型付き `input` パラメータにデシリアライズします。単一ペイロードの制限はなく、各ノードは厳密に 1 つの型付き戻り値を持ちます:

    ```go
    --8<-- "examples/go/snippets/graphs/data-handling/main.go:structured-output"
    ```

    **事前構築済みワークフローエージェント**: エージェントごとに 1 つずつ、複数の `OutputKey` 値を使用して個々のフィールドをセッション状態に保存します。ダウンストリームエージェントは、`Instruction` 内の `{key}` を介して各フィールドを個別に読み取ります。

### ルーティング出力

=== "Python"

    条件付きエッジのディスパッチを行うには、***Event*** の `route` パラメータを使用します:

    ```python
    def router(node_input: str):
        return Event(route="BUG")
    ```

=== "TypeScript"

    `route` 値は `output` と独立しているため、1つのイベントでブランチを選択し、同時にペイロードを転送することができます。`DEFAULT_ROUTE` 設定は、他のブランチと一致しなかったすべての値をキャッチします。

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/data-handling/routing_output.ts:routing-output"
    ```

=== "Go"

    **workflow パッケージ**: イベントを発行する `FunctionNode` は `session.Event` を直接構築し、`Event.Routes` に目的のルートキーを設定し、ペイロードを後続に転送するために `Event.Output` を設定します。ワークフローエンジンはディスパッチ時に `Event.Routes` を読み取って一致するエッジを選択します:

    ```go
    --8<-- "examples/go/snippets/graphs/data-handling/main.go:routing-output"
    ```

### ユーザー向けメッセージ

=== "Python"

    次のノードにデータを渡すのではなくユーザーに応答を送信するには、***Event*** の ***message*** パラメータを使用します:

    ```python
    async def user_message(node_input: str):
      """Tell user research process is starting."""
      yield Event(message="Beginning research process...")
    ```

=== "TypeScript"

    ユーザー向けのメッセージはイベントの `content` フィールドです。ランタイムは `content` をレンダリングしますが、グラフはこれを次のノードに渡しません。ユーザー向けには `content` を、次のノード向けには `output` を使用してください。ノードは2つのイベントを送信することで両方を出力でき、そのうちの1つにのみ `output` を含めます。

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/data-handling/user_message.ts:user-message"
    ```

=== "Go"

    **workflow パッケージ**: ノードの型付き出力を進めずにユーザーに表示されるメッセージを発行するには、`EmittingFunctionNode` の `emit` コールバックを介して発行される中間イベントで `Event.Content` を設定します。最終的な戻り値（または `nil`）が `Event.Output` を制御します。

    **事前構築済みワークフローエージェント**: すべての `llmagent` ステップは、モデル応答をユーザー向けイベントとして自動的に発行します。非 LLM ステップの場合は、テキストを含む `LLMResponse.Content` を持つイベントを yield するカスタム `Run` 関数を `agent.Agent` に記述します。

### セッション状態と状態スコープ

セッション状態は、セッション内のターンをまたいでデータを永続化します。これは事前構築済みワークフローエージェントの主要なデータ共有メカニズムであり、使用するエージェントスタイルに関係なくツールやコールバック内でも利用できます。

=== "Python"

    ノード間で値を維持するには、***Event*** の ***state*** パラメータを使用します。ノードは状態の値を変更でき、変更された状態の値はダウンストリームノードで利用できます:

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

    !!! warning "注意: `state` プロパティのデータ制限"

        state パラメータは、ノード間で*大量のデータを永続化する用途には使用しないでください*。Workflow のライフサイクル中に大容量のデータリソースを永続化するには、アーティファクトやデータベースツールなどの他のデータ永続化メカニズムを使用してください。

=== "TypeScript"

    状態は戻り値として返すのではなく、`ctx.state` を介して書き込みます。書き込みは同じ実行内の以降のすべてのノードから参照でき、書き込みを行ったノードのイベントとともにコミットされます。

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/data-handling/session_state.ts:session-state"
    ```

    !!! warning "警告: `state` データの制限事項"

        セッション状態は軽量な Key-Value ストアです。ノード間で大きなペイロードを移動するために使用しないでください。代わりにアーティファクトまたはデータベースツールを使用してください。次のノードのみが値を必要とする場合は、ノードの `output` として edge に沿って渡します。値が実行後も存続する必要がある場合や、ツール、コールバック、または `{key}` 命令テンプレートによって読み取られる必要がある場合に状態を使用してください。

=== "Go"

    状態は `ctx.Session().State().Set(key, value)` で書き込み、`.Get(key)` で読み取ります。`session` パッケージは、Python の state パラメータと同じ有効期間スコープにマッピングされるプレフィックス定数を定義しています。このパターンは、事前構築済みワークフローエージェント、およびあらゆるエージェントスタイルのツールやコールバックに適用されます:

    ```go
    --8<-- "examples/go/snippets/graphs/data-handling/main.go:state-scopes"
    ```

    !!! warning "注意: 状態データの制限"

        セッション状態は軽量なキーバリューストアです。ファイルコンテンツやバイナリデータなどの大きなペイロードを永続化するために使用しないでください。代わりに ADK アーティファクトまたは外部ストレージツールを使用してください。

    !!! tip "workflow パッケージ: state よりも Event.Output を優先する"

        `workflow` パッケージ（`FunctionNode`、`AgentNode`、`DynamicNode`）では、型付きの値を返すことでノード間にデータを渡してください（フレームワークが `Event.Output` を自動的に設定します）。ツール、コールバック、またはエージェントの `Instruction` テンプレートと値を共有する必要がある場合にのみ `State().Set` を使用してください。

## スキーマでノードデータを制約する

入力および出力データスキーマを設定して、任意のエージェントノードが受け入れおよび生成するデータ形式を制約できます。

=== "Python"

    ***BaseModel*** を拡張するクラスとともに `input_schema` と `output_schema` を使用して、エージェントの入力と出力を制約します:

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

    スキーマには Zod オブジェクトまたは genai の `Schema` を使用します。スキーマの場所によってその効果が決まります。

    -   `LlmAgent.outputSchema` オプションは、モデルがその形式で応答することを要求します。
    -   `LlmAgent.inputSchema` オプションは、エージェントがツールとして公開されている場合にのみ適用されます。グラフ内では、`node(agent, {inputSchema})` を使用してノード自体にノードの入力を検証するスキーマを設定します。

    グラフ内のエージェントは、デフォルトである `single_turn` モードまたは `task` モードで実行する必要があります。

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/data-handling/schemas.ts:schemas"
    ```

=== "Go"

    **workflow パッケージ**: `workflow.NewAgentNodeTyped[Input, Output]` を使用してエージェントノードにスキーマをアタッチします。ジェネリック型パラメータは自動的に `*jsonschema.Schema` にリフレクションされるため、手動でのスキーマ構築は不要です。ノードの `Event.Output` が構造化された結果を後続に運ぶため、`OutputKey` や状態の書き込みは不要です:

    ```go
    --8<-- "examples/go/snippets/graphs/data-handling/main.go:input-output-schema"
    ```

    **事前構築済みワークフローエージェント**: `llmagent.Config` で `InputSchema` と `OutputSchema` を設定します。`OutputSchema` は、スキーマに一致する JSON オブジェクトで応答するようモデルに強制します（`OutputSchema` が設定されている場合、エージェントはツールを使用できません）。ダウンストリームエージェントが `Instruction` 内の `{key}` を介して参照できるように JSON 文字列を状態に保存するには、`OutputKey` を使用します。

## エージェントで構造化データにアクセスする

=== "Python"

    入力スキーマからプロパティを選択するには中括弧 `{ }` 構文を使用し、プロパティを選択しつつソースノードの名前で修飾するには `< >` を使用します:

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

    エージェントの命令内では、2つのデータ選択形式を使用できます。

    -   `{Class.field}` 形式は、このノードの入力からフィールドを読み取ります。
    -   `<Class.field from source_node>` 形式は、名前付きの先行ノードの出力からフィールドを読み取ります。複数のアップストリームノードが同じフィールド名を共有している場合にこの形式を使用します。

    どちらの形式も、セッション状態を読み取る `{state_key}` とは異なります。`Class.` プレフィックスはドキュメント用のみであり、解決にはドットの後のフィールド名が使用されます。

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/data-handling/structured_access.ts:structured-access"
    ```

=== "Go"

    ADK Go v2.0.0 では、`FunctionNode` が型付き構造体を返し、フレームワークがそれを `Event.Output` にシリアライズします。後続の `AgentNode` はその構造体をユーザーコンテンツとして受け取るため、`{key}` テンプレート構文なしでエージェントの `Instruction` からフィールドを利用できます。これは `{CityTime.time_info}` テンプレートプレースホルダを伴う Python の `input_schema=CityTime` に直接相当し、構造体フィールドは状態から名前で検索されるのではなく、型付き入力として配信されます。

    ```go
    --8<-- "examples/go/snippets/graphs/data-handling/main.go:structured-output"
    ```

このワークフローの完全な例については、[グラフベースのエージェントワークフロー](/graphs/#get-started)を参照してください。
