# コールバックの種類

<div class="language-support-tag">
   <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.1.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

ADK は、エージェントの実行ライフサイクルのさまざまなポイントで実行されるいくつかのタイプのコールバックを提供します。

## エージェント ライフサイクル コールバック

これらのコールバックは、`BaseAgent` を継承する*すべて*のエージェント (`LlmAgent`、`SequentialAgent`、`ParallelAgent`、`LoopAgent` など) で使用できます。

??? note "Python: コールバック パラメータ名"

    Python では、ADK はコールバック関数が受け取るパラメータ名を検査します。任意の名前 (例: `ctx`) を使用することはできず、以下にリストされている正確な名前を使用する必要があります。

    ```python
    # 正しい
    def before_agent_callback(callback_context):
        ...

    # 誤り
    def before_agent_callback(ctx):
        ...
    ```

    | コールバック | 必須パラメータ名 |
    |---|---|
    | `before_agent_callback` | `callback_context` |
    | `after_agent_callback` | `callback_context` |
    | `before_model_callback` | `callback_context`, `llm_request` |
    | `after_model_callback` | `callback_context`, `llm_response` |
    | `on_model_error_callback` | `callback_context`, `llm_request`, `error` |
    | `before_tool_callback` | `tool`, `args`, `tool_context` |
    | `after_tool_callback` | `tool`, `args`, `tool_context`, `tool_response` |
    | `on_tool_error_callback` | `tool`, `args`, `tool_context`, `error` |

    すべての `BaseAgent` 上のフィールドであるのは `before_agent_callback` と `after_agent_callback` のみです。この表の 6 つのモデルおよびツール コールバックは `LlmAgent` 専用のフィールドです。

??? note "Python: `async` コールバックとコールバック リスト"

    Python では、コールバックは通常の `def` または `async def` のいずれかを使用できます。ADK はどちらの場合も結果を await します。

    すべてのコールバック フィールドは、単一の関数の代わりに関数のリストも受け入れます。ADK はリストされた順序でそれらを呼び出し、結果を返した最初のコールバックで停止します。その値がコールバックの結果となり、残りのコールバックはスキップされます。結果と見なされるものはファミリによって異なります。エージェント、モデル、ツールの 6 つの `before_`/`after_` フックは *truthy* (真と評価される) 値でのみ停止するため、`None` や空の `dict` などのその他の falsy 値を返すコールバックは次のコールバックの実行を許可します。`on_model_error_callback` および `on_tool_error_callback` は `None` 以外の任意の値で停止するため、`on_tool_error_callback` からの空の `dict` はチェーンを終了し、例外を抑制してツールの結果になります。

    エージェントのコールバック フィールドにリストを割り当てます。

    ```python
    root_agent = LlmAgent(
        name="my_agent",
        model="gemini-flash-latest",
        before_model_callback=[check_policy, log_request],
    )
    ```

### Before Agent コールバック

**タイミング:** エージェントの `_run_async_impl` (または `_run_live_impl`) メソッドが実行される*直前*に呼び出されます。エージェントの `InvocationContext` が作成された後、コア ロジックが開始される*前*に実行されます。

**目的:** この特定の実行にのみ必要なリソースや状態の設定、実行開始前のセッション状態 (`callback_context.state`) の検証チェック、エージェントのアクティビティのエントリ ポイントのログ記録、またはコア ロジックが使用する前の呼び出しコンテキストの変更に最適です。

??? "Code"
    === "Python"

        ```python
        --8<-- "examples/python/snippets/callbacks/before_agent_callback.py"
        ```

    === "TypeScript"

        ```typescript
        --8<-- "examples/typescript/snippets/callbacks/before_agent_callback.ts"
        ```

    === "Go"

        ```go
        --8<-- "examples/go/snippets/callbacks/types_of_callbacks/main.go:imports"


        --8<-- "examples/go/snippets/callbacks/types_of_callbacks/main.go:before_agent_example"
        ```

    === "Java"

        ```java
        --8<-- "examples/java/snippets/src/main/java/callbacks/BeforeAgentCallbackExample.java:init"
        ```

**`before_agent_callback` の例に関する注意点:**

* **示している内容:** この例は `before_agent_callback` を示しています。このコールバックは、特定のリクエストに対してエージェントのメイン処理ロジックが開始される*直前*に実行されます。
* **仕組み:** コールバック関数 (`check_if_agent_should_run`) は、セッションの状態にあるフラグ (`skip_llm_agent`) を確認します。
    * フラグが `True` の場合、コールバックは `types.Content` オブジェクトを返します。これにより、ADK フレームワークはエージェントのメイン実行を完全に**スキップ**し、コールバックから返されたコンテンツを最終応答として使用します。
    * フラグが `False` (または設定されていない) の場合、コールバックは `None` または空のオブジェクトを返します。これにより、ADK フレームワークはエージェントの通常の実行 (この場合は LLM の呼び出し) を**続行**します。
* **期待される結果:** 2 つのシナリオが確認できます。
    1. `skip_llm_agent: True` 状態のセッションでは、エージェントの LLM 呼び出しがバイパスされ、出力はコールバックから直接返されます ("Agent... skipped...")。
    2. その状態フラグが*ない*セッションでは、コールバックによってエージェントの実行が許可され、LLM からの実際の応答 (例: "Hello!") が表示されます。
* **コールバックの理解:** これは、`before_` コールバックが**ゲートキーパー**として機能し、主要なステップの*前*に実行をインターセプトして、チェック (状態、入力検証、権限など) に基づいて実行を防止できることを示しています。

### After Agent コールバック

**タイミング:** エージェントの `_run_async_impl` (または `_run_live_impl`) メソッドが正常に完了した*直後*に呼び出されます。`before_agent_callback` がコンテンツを返したためにエージェントがスキップされた場合は実行されません。Python では、エージェントの実行中に `end_invocation` を設定した場合もスキップされますが、これは `run_async` パスのみです。`run_live` は `_run_live_impl` の終了後に `end_invocation` を再チェックしないため、コールバックは実行されます。

**目的:** クリーンアップ タスク、実行後の検証、エージェントのアクティビティの完了のログ記録、または最終状態の変更に役立ちます。

!!! note "After Agent コールバックの出力変更の制限事項"

    `after_agent_callback` は応答出力を完全に変更することはできません。エージェントが AI モデルを複数回呼び出し、複数のイベントを出力した可能性があるためです。したがって、出力の変更は許可されませんが、追加のコンテンツを*追加 (append)* することはできます。AI モデルの応答を変更したい場合は、`after_model_callback` を検討してください。

??? "Code"
    === "Python"

        ```python
        --8<-- "examples/python/snippets/callbacks/after_agent_callback.py"
        ```

    === "TypeScript"

        ```typescript
        --8<-- "examples/typescript/snippets/callbacks/after_agent_callback.ts"
        ```

    === "Go"

        ```go
        --8<-- "examples/go/snippets/callbacks/types_of_callbacks/main.go:imports"


        --8<-- "examples/go/snippets/callbacks/types_of_callbacks/main.go:after_agent_example"
        ```

    === "Java"

        ```java
        --8<-- "examples/java/snippets/src/main/java/callbacks/AfterAgentCallbackExample.java:init"
        ```

**`after_agent_callback` の例に関する注意点:**

* **示している内容:** この例は `after_agent_callback` を示しています。このコールバックは、エージェントのメイン処理ロジックが完了して結果が生成された*直後*、その結果が確定して返される*前*に実行されます。
* **仕組み:** コールバック関数 (`modify_output_after_agent`) は、セッションの状態にあるフラグ (`add_concluding_note`) を確認します。
    * フラグが `True` の場合、コールバックは*新しい* `types.Content` オブジェクトを返します。これにより、ADK フレームワークはエージェントの元の出力にコールバックから返されたコンテンツを**追加 (append)** します。
    * フラグが `False` (または設定されていない) の場合、コールバックは `None` または空のオブジェクトを返します。これにより、ADK フレームワークはエージェントによって生成された元の出力を**使用**します。
* **期待される結果:** 2 つのシナリオが確認できます。
    1. `add_concluding_note: True` 状態が*ない*セッションでは、コールバックによってエージェントの元の出力 ("Processing complete!") が使用されます。
    2. その状態フラグが*ある*セッションでは、コールバックがエージェントの元の出力をインターセプトし、独自のメッセージ ("Concluding note added...") を追加します。
* **コールバックの理解:** この例は、`after_` コールバックによって**後処理 (post-processing)** が可能になることを示しています。ステップの結果を検査し、そのまま通過させるか追加するかを決定できます。`after_agent_callback` はエージェントの出力を置き換えることはできず、返されたコンテンツはエージェント自身のイベントの後に*追加イベント*として出力されます。

## LLM インタラクション コールバック

これらのコールバックは `LlmAgent` 専用であり、大規模言語モデルとの対話に関するフックを提供します。Python では、`LlmAgent` はモデル呼び出しで例外が発生したときに実行される `on_model_error_callback` も受け入れます。`LlmResponse` を返すと例外は抑制され、その応答が代わりに使用されます。

### Before Model コールバック

**タイミング:** `LlmAgent` のフロー内で `generate_content_async` (または同等の) リクエストが LLM に送信される直前に呼び出されます。

**目的:** LLM に送信されるリクエストの検査と変更を可能にします。ユースケースには、動的な指示の追加、状態に基づいた few-shot の例の挿入、モデル構成の変更、ガードレール (不適切な表現のフィルタなど) の実装、リクエスト レベルのキャッシュの実装などがあります。

**戻り値の効果:**
コールバックが `None` (Java の場合は `Maybe.empty()` オブジェクト) を返した場合、LLM は通常のワークフローを続行します。コールバックが `LlmResponse` オブジェクトを返した場合、LLM への呼び出しは**スキップ**されます。返された `LlmResponse` は、モデルから直接返されたかのように直接使用されます。これはガードレールやキャッシュの実装に強力です。

??? "Code"
    === "Python"

        ```python
        --8<-- "examples/python/snippets/callbacks/before_model_callback.py"
        ```

    === "TypeScript"

        ```typescript
        --8<-- "examples/typescript/snippets/callbacks/before_model_callback.ts"
        ```

    === "Go"

        ```go
        --8<-- "examples/go/snippets/callbacks/types_of_callbacks/main.go:imports"


        --8<-- "examples/go/snippets/callbacks/types_of_callbacks/main.go:before_model_example"
        ```

    === "Java"

        ```java
        --8<-- "examples/java/snippets/src/main/java/callbacks/BeforeModelCallbackExample.java:init"
        ```

### After Model コールバック

**タイミング:** 呼び出し元のエージェントによってさらに処理される前に、LLM から応答 (`LlmResponse`) を受信した直後に呼び出されます。

**目的:** 生の LLM 応答の検査または変更を可能にします。ユースケースには以下が含まれます。

* モデル出力のログ記録
* 応答の再フォーマット
* モデルによって生成された機密情報の検閲
* LLM 応答から構造化データを解析し、それを `callback_context.state` に保存
* 特定のエラー コードの処理

??? "Code"
    === "Python"

        ```python
        --8<-- "examples/python/snippets/callbacks/after_model_callback.py"
        ```

    === "TypeScript"

        ```typescript
        --8<-- "examples/typescript/snippets/callbacks/after_model_callback.ts"
        ```

    === "Go"

        ```go
        --8<-- "examples/go/snippets/callbacks/types_of_callbacks/main.go:imports"


        --8<-- "examples/go/snippets/callbacks/types_of_callbacks/main.go:after_model_example"
        ```

    === "Java"

        ```java
        --8<-- "examples/java/snippets/src/main/java/callbacks/AfterModelCallbackExample.java:init"
        ```

## ツール実行コールバック

これらのコールバックも `LlmAgent` 専用であり、LLM が要求する可能性のあるツール (`FunctionTool` や `AgentTool` など) の実行前後にトリガーされます。Python では、`LlmAgent` はツールで例外が発生したときに実行される `on_tool_error_callback` も受け入れます。`dict` を返すと例外は抑制され、その `dict` 値がツールの結果として使用されます。

### Before Tool コールバック

**タイミング:** LLM がツールの関数呼び出しを生成した後、特定のツールの `run_async` メソッドが呼び出される直前に呼び出されます。

**目的:** ツール引数の検査と変更、実行前の認可チェックの実行、ツール使用試行のログ記録、またはツール レベルのキャッシュの実装を可能にします。

**戻り値の効果:**

1. コールバックが `None` (Java の場合は `Maybe.empty()` オブジェクト) を返した場合、ツールの `run_async` メソッドが (変更された可能性のある) `args` で実行されます。
2. 辞書 (Java の場合は `Map`) が返された場合、ツールの `run_async` メソッドは**スキップ**されます。返された辞書は、ツール呼び出しの結果として直接使用されます。これは、ツールの動作のキャッシュやオーバーライドに役立ちます。

!!! note "Python: `None` のみがツールの実行を許可します"

    ADK は返された値を `None` と比較するため、空の `dict` もオーバーライドとみなされます。ツールはスキップされ、`{}` がツールの結果になります。ツールを実行したい場合は `{}` ではなく `None` を返してください。コールバック リストを使用する場合、空の `dict` はチェーンを停止せず、後続のコールバックが別の値を返した場合は破棄されるため、これは生成された最後の値に適用されます。

??? "Code"
    === "Python"

        ```python
        --8<-- "examples/python/snippets/callbacks/before_tool_callback.py"
        ```

    === "TypeScript"

        ```typescript
        --8<-- "examples/typescript/snippets/callbacks/before_tool_callback.ts"
        ```

    === "Go"

        ```go
        --8<-- "examples/go/snippets/callbacks/types_of_callbacks/main.go:imports"
        --8<-- "examples/go/snippets/callbacks/types_of_callbacks/main.go:tool_defs"
        --8<-- "examples/go/snippets/callbacks/types_of_callbacks/main.go:before_tool_example"
        ```

    === "Java"

        ```java
        --8<-- "examples/java/snippets/src/main/java/callbacks/BeforeToolCallbackExample.java:init"
        ```

### After Tool コールバック

**タイミング:** ツールの `run_async` メソッドが正常に完了した直後に呼び出されます。

**目的:** LLM に送り返される前 (要約後など) にツールの結果を検査および変更できるようにします。ツールの結果のログ記録、結果の後処理やフォーマット、または結果の特定の部分をセッション状態に保存するのに役立ちます。

**戻り値の効果:**

1. コールバックが `None` (Java の場合は `Maybe.empty()` オブジェクト) を返した場合、元の `tool_response` が使用されます。
2. 新しい辞書が返された場合、それは元の `tool_response` を**置き換えます**。これにより、LLM に渡される結果を変更またはフィルタリングできます。

!!! note "Python: `tool_response` の型と戻り値"

    ADK はコールバックが実行された*後*にのみ、`dict` 以外の結果を `{"result": <value>}` にラップします。したがって、`-> str` とアノテーションされたツールは、`after_tool_callback` に `dict` ではなく `str` を渡します。辞書メソッドを呼び出す前に型を確認してください。

    ADK はまた、返された値を `None` と比較するため、`{}` を返すとツールの応答が `{}` に置き換えられます。元を保持するには `None` を返してください。

??? "Code"
    === "Python"

        ```python
        --8<-- "examples/python/snippets/callbacks/after_tool_callback.py"
        ```

    === "TypeScript"

        ```typescript
        --8<-- "examples/typescript/snippets/callbacks/after_tool_callback.ts"
        ```

    === "Go"

        ```go
        --8<-- "examples/go/snippets/callbacks/types_of_callbacks/main.go:imports"
        --8<-- "examples/go/snippets/callbacks/types_of_callbacks/main.go:tool_defs"
        --8<-- "examples/go/snippets/callbacks/types_of_callbacks/main.go:after_tool_example"
        ```

    === "Java"

        ```java
        --8<-- "examples/java/snippets/src/main/java/callbacks/AfterToolCallbackExample.java:init"
        ```
