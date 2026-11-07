# 動的エージェントワークフロー

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v2.0.0</span><span class="lst-typescript">TypeScript v2.0.0</span><span class="lst-go">Go v2.0.0</span>
</div>

ADK フレームワークは、[グラフベースワークフロー](/graphs/)に代わるより柔軟で強力な選択肢として、プログラムによってワークフローを定義する方法を提供します。グラフベースのアプローチを使用すると、ワークフローノードを使ってマルチステップの静的なプロセス構造を便利に構成できます。しかし、反復ループや複雑な分岐ロジックなど、ワークフローのロジックパスがより複雑な場合、グラフベースのアプローチはニーズに合わないか、管理が煩雑になりすぎることがあります。

ADK の動的ワークフローを使用すると、グラフベースのパス構造にとらわれず、選択したプログラミング言語の機能を最大限に活用してワークフローを構築できます。動的ワークフローでは、シンプルなデコレータ（Python）やコンストラクタ関数（Go）でワークフローを作成し、ワークフローノードを関数として呼び出し、複雑なルーティングロジックを構築できます。ADK における動的ワークフローの主な利点は次のとおりです:

-   **柔軟な制御フロー:** 静的グラフでは表現が困難または不可能なループ、条件分岐、再帰を使用して、実行順序を動的に定義できます。
-   **プログラム的な開発体験:** グラフベースのルーティングの代わりに、`while` ループや `async/await`（Python）、または `for` ループや `workflow.RunNode`（Go）などの馴染みのある構文を使用できます。
-   **自動チェックポイント:** 動的ワークフローは各ノードの実行を追跡します。ワークフローの再開時には成功したサブノードが自動的にスキップされるため、複雑なロジックがデフォルトで永続的かつ再開可能になります。
-   **カプセル化:** 内部で下位レベルのノードを構成する*親*ノードにビジネスロジックをラップすることで、ワークフロー全体をクリーンで管理しやすい状態に保ちます。

## はじめに

次の動的ワークフローのコード例は、関数を持つ単一ノードを含む基本的なワークフローを定義する方法を示しています:

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

    この例では、利便性と記述するコードを可能な限りシンプルに保つために [***@node***](#node) アノテーションを使用しています。このアノテーションは、コードを ADK 動的ワークフローのコンテキスト内で実行できるようにするラッパーを生成します。

=== "TypeScript"

    TypeScript には `@node` デコレータはありません。代わりに `node(fn, options)` ファクトリ関数を使用してください。`ctx.runNode()` メソッドは `ctx.run_node()` に相当します。

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/dynamic/get_started.ts:get-started"
    ```

    オーケストレーターノードを記述する際、結果の読み取り方と一時停止後のワークフローの動作に影響する2つの詳細があります。

    -   `ctx.runNode()` メソッドは出力値ではなくノード結果 (node result) に解決されます。値を取得するには `.output` プロパティを読み取ります。
    -   `ctx.runNode()` を呼び出すオーケストレーターは `rerunOnResume: true` を設定する必要があります。この設定により、再開時にノード本体が再実行されるため、完了済みの子ノードは再実行されずにチェックポイントから再生されます。

=== "Go"

    Go では、`workflow.NewFunctionNode` が `@node` デコレータに代わり、`workflow.NewDynamicNode` が `@node(rerun_on_resume=True)` 非同期オーケストレーターに代わります。`workflow.RunNode` は `ctx.run_node()` に直接相当します。`workflow.Chain` を伴う `workflowagent.New` は `Workflow(edges=[...])` に代わります。

    Human-in-the-Loop の一時停止後の再開動作は `NodeConfig.RerunOnResume` によって制御されます（詳細については以下の[ノード](#node)を参照してください）。

    ```go
    --8<-- "examples/go/snippets/graphs/dynamic/main.go:get-started"
    ```

## ビルディング ブロック: ノードとワークフロー

ノードとワークフローは、ADK の動的ワークフローの基本的なビルディングブロックを表します。これらの型と関数は、コードを ADK のコードベースワークフローに統合できるようにラップするために必要な機能を提供します。

### ノード {#node}

ADK の動的ワークフローは*ノード*で構成されます。使用可能なワークフローノードのシンプルなバージョンは、ワークフロー内で実行するために必要なメタデータで通常の関数をラップします。

=== "Python"

    Python では、***@node*** アノテーションがノードラッパーを生成し、ボイラープレートを最小限に抑えます:

    ```python
    @node(name="hello_node")
    def my_function_node(node_input: Any):
        return "Hello World"
    ```

    次のコードスニペットは、***@node*** アノテーションを*使用しない*同等のコードを示しています:

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

    外部ライブラリの関数をラップする場合や、同じ関数から異なる構成で複数のノードを作成する必要がある場合、または高度なオーケストレーションのためにレジストリ内でノード参照を管理している場合には、ノードラッパーコードを自分で作成すると便利です。

=== "TypeScript"

    ノードを構築するには、`node(fn, options)` ファクトリ関数と、明示的な `new FunctionNode(name, fn, config)` コンストラクタの2つの方法があります。別のライブラリの関数をラップする場合、1つの関数から異なる構成の複数のノードが必要な場合、または高度なオーケストレーションのためにレジストリでノード参照を保持する場合は、コンストラクタを使用してください。

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/dynamic/nodes.ts:node-forms"
    ```

    このコードサンプルで最も重要なオプションは `rerunOnResume` であり、ヒューマンインザループ (human-in-the-loop) による一時停止後にワークフローが再開したときの動作を制御します。

    -   **`true` (再エントリ):** ノード本体が最初から再実行されます。`ctx.runNode()` を呼び出すオーケストレーターにはこの設定を使用します。本体が再実行され、完了済みの子アクティベーションは自動的にスキップされます。
    -   **`false` (ハンドオフ、リーフのデフォルト):** 再開ペイロードは中断されたノードをバイパスして、ノードの後続ノードに入力としてルーティングされます。

=== "Go"

    Go では、`workflow.NewFunctionNode[IN, OUT]` がジェネリックパラメータから入力型と出力型を推論して通常の関数をワークフローノードとしてラップします。デコレータ構文はなく、ノードは動的オーケストレーター内の `workflow.RunNode` に子として渡す値です:

    ```go
    --8<-- "examples/go/snippets/graphs/dynamic/main.go:building-blocks-nodes"
    ```

    `NodeConfig` は Python の `@node` 引数と同じオプションを保持します。最も重要なフィールドは `RerunOnResume *bool` で、Human-in-the-Loop の一時停止後にワークフローが再開するときに何が起こるかを制御します:

    -   **`&true`（再エントリモード）**: 中断されたノードは再開時に最初から再実行されます。ループ内で `workflow.RunNode` を呼び出す動的オーケストレーターノードにこれを使用します。本体が再実行され、すでに完了した子のアクティベーションは自動的にスキップされます（チェックポイント）。これは Python の `@node(rerun_on_resume=True)` に対応します。
    -   **`&false`（ハンドオフモード）**: 再開ペイロードは中断されたノードを完全にバイパスし、入力としてノードの後続に直接ルーティングされます。単に一時停止イベントを発行し、人間の応答が次のステップに流れることを期待するリーフノードにこれを使用します。
    -   **`nil`**: デフォルトはノードタイプによって異なります。オーケストレーター本体はキャッシュされた子の結果を配信するために再開時に再エントリする必要があるため、`workflow.NewDynamicNode` は自動的に `nil → &true`（再エントリモード）を設定します。`workflow.NewFunctionNode` およびその他のリーフノードコンストラクタは `nil` をそのままにし、エンジンはそれをハンドオフ（`&false`）として扱います。明示的な `&false` はどのノードタイプでも常に尊重されます。

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


### ワークフロー

ADK の動的ワークフローでは、ノードの主要なオーケストレーターとして動的ノードを使用します。動的ノードは、子ノードの実行とそれらのノードの実行ロジック（順序とパス）を管理します。

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

    オーケストレーターは、各子ステップに対して `ctx.runNode()` を await する非同期関数です。これを `rerunOnResume: true` を指定してノードとしてラップし、グラフの唯一の edge として使用します。

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/dynamic/nodes.ts:workflows"
    ```

=== "Go"

    `workflow.NewDynamicNode` は、本体が各子ステップに対して `workflow.RunNode` を呼び出すオーケストレーターを作成します。`workflow.Chain(workflow.Start, myWorkflow)` を伴う `workflowagent.New` は、`Workflow(edges=[("START", my_workflow)])` に相当します:

    ```go
    --8<-- "examples/go/snippets/graphs/dynamic/main.go:building-blocks-workflow"
    ```

## データ処理

ADK で動的ワークフローを使用する場合、`ctx.run_node`（Go では `workflow.RunNode`）が子ノードの出力を直接返すため、データ転送のためにセッション状態キーを手動で読み書きする必要がなく、[グラフベースワークフロー](/graphs/)よりもデータの受け渡しがシンプルになります。

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

    また、グラフベースワークフローのノードと同様に、定義されたクラスを使用して特定のデータスキーマを渡し、入力および出力スキーマを構成することもできます:

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

    `ctx.runNode()` 関数は子ノードの結果を直接返すため、値を1ステップダウンストリームに移動するためにセッション状態キーを読み書きする必要はありません。この関数は、`LlmAgent` を含む任意のノードライクな値を、最初に `node()` でラップすることなく受け入れます。

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/dynamic/data_handling.ts:data-handling"
    ```

    スキーマはグラフ内と同じように機能します。[シーケンスルート](#sequence-route) セクションに示すように、実行するノードにスキーマをアタッチします。

=== "Go"

    Go では、動的オーケストレーター内で `workflow.RunNode` を介して呼び出せるように、`workflow.NewAgentNode` が `agent.Agent` をラップします。各 `RunNode` 呼び出しの出力は型付きの値として返されるため、セッション状態の読み取りは不要です:

    ```go
    --8<-- "examples/go/snippets/graphs/dynamic/main.go:data-handling"
    ```

ワークフローノード間のデータ処理の詳細については、[エージェントワークフローのデータ処理](/graphs/data-handling/)を参照してください。

## ワークフロー ルート

ADK の動的ワークフローは、反復ループやより複雑な分岐ロジックなど、[グラフベースワークフロー](/graphs/)と比較してルーティングロジックの面でより高い柔軟性を提供します。このセクションでは、ルーティングに使用できるいくつかの手法について説明します。

### シーケンスルート {#sequence-route}

グラフベースワークフローと同様に、ADK の動的ワークフローでも順次的なタスク処理を作成できます。

=== "Python"

    次のコードスニペットは、エージェント、関数ノード、および 2 番目のエージェントを含む動的ワークフローを示しています:

    ```python
    @node # workflow node
    async def city_workflow(ctx: Context):
        city = await ctx.run_node(city_generator_agent)
        city_time = await ctx.run_node(city_time_function, city)
        report_text = await ctx.run_node(city_report_agent, city_time)

        return report_text
    ```

=== "TypeScript"

    シーケンシャルルートは `ctx.runNode()` の呼び出しを1つずつ順番に await します。各呼び出しは次の呼び出しが開始される前に完了します。

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/dynamic/sequence_route.ts:sequence-route"
    ```

=== "Go"

    `NewDynamicNode` の本体内で `workflow.RunNode` を順番に呼び出します。各呼び出しは、次の呼び出しが始まる前に子の完了を待機します。[上記のデータ処理の例](#data-handling)はまさにこのパターンを示しており、`cityWorkflow` は `cityTimeNode`、次に `cityReportNode` の順で `workflow.RunNode` を呼び出し、各ノードの型付き出力を次のノードに渡しています。

### ループルート {#loop-route}

タスクに反復ループを使用したいワークフローでは、動的ワークフローを使用することで、必要なルーティングロジックをより柔軟に定義できます。

=== "Python"

    次のコード例は、動的ワークフローを使用してコードの生成、レビュー、更新を行うワークフローループを構築する方法を示しています:

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

    動的ワークフローは、グラフのバックエッジではなく通常のループとして反復を定義することで、ワークフローロジックをシンプルに保つのに役立ちます。値はローカル変数に保持され、エージェントの命令テンプレートが読み取る必要がある場合にのみ状態が書き込まれます。グラフサイクルとは異なり、ループはそのループ条件によって制限されます。

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/dynamic/loop_route.ts:loop-route"
    ```

=== "Go"

    Go では、ループは動的ノード本体内の通常の `for` ループです。lint チェックノードは問題が見つからない場合に空文字列を返し、ループの終了を知らせます:

    ```go
    --8<-- "examples/go/snippets/graphs/dynamic/main.go:loop-route"
    ```

### 並列実行ルート

ADK の動的ワークフローは並列実行をサポートできます。

=== "Python"

    Python では、`asyncio.gather` を使用して並列実行を構築できます:

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

    !!! tip "ヒント: 並列ノードの再開"

        ワークフローフレームワークは、動的ワークフローが再開された場合、並列ワーカーノードを含め、失敗または中断されたワーカーノードのみが再実行されることを保証します。

=== "TypeScript"

    `ctx.runNode()` メソッドは Promise を返すため、いずれかを await する前にすべての子ノードを開始すると子ノードが並行して実行され、`Promise.all` が結果を収集します。実行 ID (Run ID) は呼び出し順に割り当てられるため、再開時にも ID の決定性を保つために、同期ループ内で子ノードを開始してください。

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/dynamic/parallel_route.ts:parallel-route"
    ```

    !!! tip "ヒント: 組み込みの並列ワーカーを推奨"

        リスト内の各アイテムに対して1つのノードを実行するには、`node(worker, {parallelWorker: true, maxParallelWorkers: 4})` を使用します。このオプションはファンアウトを実行し、並行性を制限します (デフォルトは 8)。カスタムスケジューリングや部分的な障害処理が必要な場合は、上記の手動アプローチを使用してください。どちらの場合も、再開時には失敗または中断されたワーカーのみが再実行されます。

=== "Go"

    Go では、`workflow.NewParallelWorker` が子ノードをラップし、リスト入力の各要素に対して並行して実行し、結果を単一の出力スライスに収集します。`maxConcurrency` パラメータは同時に実行できる並行アクティベーションの上限を指定し、`0` は無制限を意味します:

    ```go
    --8<-- "examples/go/snippets/graphs/dynamic/main.go:parallel-route"
    ```

    !!! tip "ヒント: 並列ノードの再開"

        ワークフローフレームワークは、動的ワークフローが再開された場合、`NewParallelWorker` によって管理される並列ワーカーノードを含め、失敗または中断されたワーカーノードのみが再実行されることを保証します。

## 人間の入力 (Human Input)

ADK の動的ワークフローには、人間の入力または Human-in-the-Loop（HITL）ステップを含めることもできます。

=== "Python"

    ノードから ***RequestInput*** を yield することでワークフローに人間の入力を組み込みます。これによりワークフローが一時停止し、ユーザーの入力を待機します。次のコード例は、人間の入力ノードを構築してワークフローに含める方法を示しています:

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

    !!! important "重要: `ctx.run_node` を使用する親ノード"

        `ctx.run_node` を呼び出す動的ワークフロー内の親ノードは、中断を適切に処理するために `rerun_on_resume=True` を設定する必要があります。

=== "TypeScript"

    リーフノードはワークフローを一時停止するために `RequestInput` を返し、デフォルトの `rerunOnResume: false` を維持して返信が出力になるようにします。これを呼び出すオーケストレーターは `rerunOnResume: true` を設定する必要があります。

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/dynamic/human_input.ts:human-input"
    ```

    !!! important "重要: 判断を下す前に `interruptIds` を確認してください"

        `ctx.runNode()` メソッドは、子ノードが中断してもエラーをスロー**しません**。正常に返され、結果の `interruptIds` プロパティが設定され、`output` プロパティは `undefined` のままになります。結果を使用する前に `interruptIds` を確認してください。このチェックをスキップしたオーケストレーターは、欠落している出力を回答として扱い、ユーザーが指定していない値で処理を続行してしまいます。

=== "Go"

    Go では、再エントリ HITL パターンを実装するために `workflow.ResumeOrRequestInput` とともに `workflow.NewEmittingFunctionNode` を使用します。最初のパスで `ResumeOrRequestInput` は `session.RequestInput` イベントを発行して `ErrNodeInterrupted` を返し、ワークフローを一時停止します。人間が応答した後、ノードは先頭から再実行され（`RerunOnResume: &true`）、`ResumeOrRequestInput` は人間の応答を直接返します:

    ```go
    --8<-- "examples/go/snippets/graphs/dynamic/main.go:human-input"
    ```

## 高度な機能

動的ワークフローは、より複雑な開発シナリオに対処するために設計されたいくつかの高度な機能を提供します。これらの機能により、実行のよりきめ細かな制御や既存の技術インフラストラクチャとのより良い統合が可能になります。

### 実行 ID（Execution IDs）

ADK フレームワークは、親 ID とカウンターに基づいて子ノード実行の決定論的な識別子（ID）を生成します。ADK ワークフローは、以前の結果を識別するためにスケジュールされた各ノードに決定論的な ID を使用します。これらの ID は動的ノードのスケジュール順序に基づいて生成され、ワークフローが再開または再実行された場合のチェックポイント処理や正しい順序でのタスクの再実行に使用されます。

#### カスタム実行 ID

順序変更可能なリストを処理する場合など、まれなケースでは安定した識別子が必要になることがあります。一般的には、ワークフロータスクの再試行やプロセスの再開に影響を与えるため、これは避けるべきです。具体的には、これらの ID はノードの状態を確認し、ノードがすでに実行されている場合は実行をスキップするために使用されます。カスタム ID を指定する場合は、ワークフローの再実行に対して決定論的であり、入力に対して論理的に同一のままであることを確認してください。

!!! warning "警告: カスタム実行 ID"

    カスタム実行 ID の作成は避けてください。実行 ID はノードの実行順序を決定するために使用されるため、カスタム実行 ID を使用すると、システムがワークフロー内のそれらのノードを再実行しようとしたときに問題が発生する可能性があります。

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

    デフォルトでは、自動生成される実行 ID は `"1"` から始まる連番の整数（文字列として表現）です。カスタムの `run_id` 値は、これらの自動生成 ID との衝突を避けるために、少なくとも 1 つの非数値文字を含む必要があります。

=== "TypeScript"

    末尾のオプションとして `runId` を `ctx.runNode()` に渡します。自動生成されるシーケンシャル ID との衝突を避けるため、ID には少なくとも1つの非数値文字を含める必要があります。

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/dynamic/custom_run_ids.ts:custom-execution-ids"
    ```

=== "Go"

    Go では、`workflow.RunNode` の末尾のオプションとして `workflow.WithRunID("order-x")` を渡します。自動生成される連番カウンター ID との衝突を避けるため、ID には少なくとも 1 つの非数値文字を含める必要があります:

    ```go
    --8<-- "examples/go/snippets/graphs/dynamic/main.go:custom-execution-ids"
    ```
