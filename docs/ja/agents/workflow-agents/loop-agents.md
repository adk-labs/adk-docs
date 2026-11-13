# ループエージェント

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.2.0</span><span class="lst-kotlin">Kotlin v0.1.0</span>
</div>

`LoopAgent`は、サブエージェントをループ（つまり反復的）で実行するワークフローエージェントです。指定された反復回数、または終了条件が満たされるまで、**一連のエージェントを繰り返し実行します**。

コードの修正など、ワークフローに繰り返しや反復的な改善が含まれる場合に`LoopAgent`を使用します。

!!! warning "非推奨: グラフベース ワークフローを使用してください"

    ADK Python、TypeScript、Go、および Kotlin では、テンプレート ワークフローは
    [グラフベース ワークフロー](/ja/graphs/) や
    [動的ワークフロー](/ja/graphs/dynamic/) などのより柔軟なワークフロー構造に置き換えられました。

### 例

*   食べ物の画像を生成するエージェントを構築したいが、特定の数のアイテム（例：5本のバナナ）を生成したいときに、画像内に異なる数のアイテム（例：7本のバナナの画像）が生成されることがあるとします。あなたには`画像を生成`と`食品アイテムを数える`という2つのツールがあります。指定された数のアイテムを正しく生成するか、一定の反復回数に達するまで画像の生成を続けたいので、`LoopAgent`を使用してエージェントを構築すべきです。

他の[ワークフローエージェント](index.md)と同様に、`LoopAgent`はLLMによって駆動されないため、その実行方法は決定論的（deterministic）です。ただし、ワークフローエージェントが関与するのはその実行（つまりループ内での実行）のみであり、内部ロジックではありません。ワークフローエージェントのツールやサブエージェントは、LLMを利用する場合もあれば、しない場合もあります。

### 仕組み

`LoopAgent`の`Run Async`メソッドが呼び出されると、以下の処理を実行します。

1.  **サブエージェントの実行:**  サブエージェントのリストを_順番に_反復処理します。_各_サブエージェントに対して、そのエージェントの`Run Async`メソッドを呼び出します。
2.  **終了チェック:**

    _重要なのは_、`LoopAgent`自体はいつループを停止するかを本質的に決定_しない_ということです。無限ループを防ぐために、終了メカニズムを実装する_必要があります_。一般的な戦略は次のとおりです。

    *   **最大反復回数 (Max Iterations)**: `LoopAgent`に最大反復回数を設定します。**ループはその回数だけ反復した後に終了します**。Pythonでは、`max_iterations`のデフォルトは`None`であり、これはエスカレーションが発生した場合にのみループが停止することを意味します。
    *   **サブエージェントからの通知 (Escalation from sub-agent)**: 1つ以上のサブエージェントが条件（例：「ドキュメントの品質は十分か？」「合意に達したか？」）を評価するように設計します。条件が満たされた場合、サブエージェントはアクションで`escalate`を`true`に設定したイベントを送出することで終了を通知します。Pythonでは、カスタムエージェントが`actions=EventActions(escalate=True)`を指定した`Event`をyieldし、コールバックでは`callback_context.actions.escalate = True`を設定し、ツールでは`tool_context.actions.escalate = True`を設定します。組み込みの`exit_loop`ツールは、このフラグを自動的に設定します。

![Loop Agent](../../assets/loop-agent.png)

### 完全な例：反復的なドキュメント改善

ドキュメントを反復的に改善するシナリオを想像してみてください。

*   **ライターエージェント (Writer Agent):** あるトピックに関する下書きを生成または改善する`LlmAgent`です。
*   **批評家エージェント (Critic Agent):** 下書きを批評し、改善点を特定する`LlmAgent`です。

    ```py
    LoopAgent(name="RefinementLoop", sub_agents=[WriterAgent, CriticAgent], max_iterations=5)
    ```

この設定では、`LoopAgent`が反復プロセスを管理します。`CriticAgent`には**`exit_loop`などのエスカレーションツールを付与し、ドキュメントが満足のいく品質レベルに達した時点でそれを呼び出す**ようにすることで、それ以上の反復を防ぐことができます。あるいは、`max_iterations`パラメータを使用してプロセスを固定回数に制限したり、停止決定を行うための外部ロジックを実装したりすることもできます。**ループは最大5回実行**され、反復的な改善が無限に続かないように保証します。

???+ "全コード"

    === "Python"
        ```py
        --8<-- "examples/python/snippets/agents/workflow-agents/loop_agent_doc_improv_agent.py:init"
        ```

    === "TypeScript"
        ```typescript
        --8<-- "examples/typescript/snippets/agents/workflow-agents/loop_agent_doc_improv_agent.ts:init"
        ```

    === "Go"
        ```go
        --8<-- "examples/go/snippets/agents/workflow-agents/loop/main.go:init"
        ```

    === "Java"
        ```java
        --8<-- "examples/java/snippets/src/main/java/agents/workflow/LoopAgentExample.java:init"
        ```

    === "Kotlin"
        ```kotlin
        --8<-- "examples/kotlin/snippets/agents/workflow-agents/LoopAgentDocImprovAgent.kt:init"
        ```

!!! tip "すべてのエージェントに対するグローバル指示"

    `App` の `GlobalInstructionPlugin`（[Python](https://github.com/google/adk-python/blob/main/src/google/adk/plugins/global_instruction_plugin.py)、[TypeScript](https://github.com/google/adk-js/blob/main/core/src/plugins/global_instruction_plugin.ts)、[Java](https://github.com/google/adk-java/blob/main/core/src/main/java/com/google/adk/plugins/GlobalInstructionPlugin.java)）またはエージェントの `GlobalInstruction` パラメータ（[Go](https://github.com/google/adk-go/blob/main/agent/llmagent/llmagent.go)）を使用して、ワークフロー全体に一貫したルールを適用します。
