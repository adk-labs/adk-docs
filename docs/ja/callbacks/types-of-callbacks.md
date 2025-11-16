# コールバックの種類

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

フレームワークは、エージェントの実行における様々な段階でトリガーされる、異なる種類のコールバックを提供します。各コールバックがいつ発火し、どのコンテキストを受け取るかを理解することが、効果的に使用するための鍵となります。

## エージェントのライフサイクルコールバック

これらのコールバックは、`BaseAgent`から継承する*すべて*のエージェント（`LlmAgent`, `SequentialAgent`, `ParallelAgent`, `LoopAgent`などを含む）で利用可能です。

!!! Note
    特定のメソッド名や戻り値の型は、SDKの言語によって若干異なる場合があります（例：Pythonでは`None`を返す、Javaでは`Optional.empty()`や`Maybe.empty()`を返す）。詳細は各言語のAPIドキュメントを参照してください。

### Before Agent コールバック

**タイミング：** エージェントの `_run_async_impl` (または `_run_live_impl`) メソッドが実行される*直前に*呼び出されます。エージェントの `InvocationContext` が作成された後、しかしそのコアロジックが開始される*前に*実行されます。

**目的：** この特定のエージェント実行にのみ必要なリソースや状態のセットアップ、実行開始前のセッション状態（`callback_context.state`）のバリデーションチェック、エージェント活動のエントリーポイントのロギング、あるいはコアロジックが使用する前に呼び出しコンテキストを修正するのに最適です。

??? "Code"
    === "Python"
    
        ```python
        --8<-- "examples/python/snippets/callbacks/before_agent_callback.py"
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

**`before_agent_callback` の例に関する注意：**

*   **この例が示すこと：** この例は`before_agent_callback`を実演します。このコールバックは、与えられたリクエストに対してエージェントのメイン処理ロジックが開始される*直前に*実行されます。
*   **仕組み：** コールバック関数（`check_if_agent_should_run`）は、セッションの状態にある`skip_llm_agent`フラグを確認します。
    *   フラグが`True`の場合、コールバックは`types.Content`オブジェクトを返します。これはADKフレームワークに対し、エージェントのメイン実行を**完全にスキップ**し、コールバックが返したコンテンツを最終レスポンスとして使用するよう指示します。
    *   フラグが`False`（または未設定）の場合、コールバックは`None`または空のオブジェクトを返します。これはADKフレームワークに対し、エージェントの通常の実行（この場合はLLMの呼び出し）を**続行する**よう指示します。
*   **期待される結果：** 2つのシナリオが見られます：
    1. `skip_llm_agent: True`の状態を持つセッションでは、エージェントのLLM呼び出しはバイパスされ、出力はコールバックから直接得られます（"Agent... skipped..."）。
    2. その状態フラグがないセッションでは、コールバックはエージェントの実行を許可し、LLMからの実際のレスポンス（例："Hello!"）が表示されます。
*   **コールバックの理解：** これは、`before_`コールバックが、主要なステップの*前に*実行をインターセプトし、（状態、入力バリデーション、権限などの）チェックに基づいてそれを防ぐことを可能にする**ゲートキーパー**として機能することを示しています。

### After Agent コールバック

**タイミング：** エージェントの `_run_async_impl` (または `_run_live_impl`) メソッドが正常に完了した*直後に*呼び出されます。`before_agent_callback`がコンテンツを返してエージェントがスキップされた場合や、エージェントの実行中に`end_invocation`が設定された場合は実行*されません*。

**目的：** クリーンアップタスク、実行後のバリデーション、エージェント活動の完了ロギング、最終状態の変更、またはエージェントの最終出力の補強・置換に役立ちます。

??? "Code"
    === "Python"
    
        ```python
        --8<-- "examples/python/snippets/callbacks/after_agent_callback.py"
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

**`after_agent_callback` の例に関する注意：**

*   **この例が示すこと：** この例は`after_agent_callback`を実演します。このコールバックは、エージェントのメイン処理ロジックが完了し、その結果を生成した*直後*、しかしその結果が最終決定されて返される*前に*実行されます。
*   **仕組み：** コールバック関数（`modify_output_after_agent`）は、セッションの状態にある`add_concluding_note`フラグを確認します。
    *   フラグが`True`の場合、コールバックは*新しい*`types.Content`オブジェクトを返します。これはADKフレームワークに対し、エージェントの元の出力をコールバックが返したコンテンツで**置き換える**よう指示します。
    *   フラグが`False`（または未設定）の場合、コールバックは`None`または空のオブジェクトを返します。これはADKフレームワークに対し、エージェントが生成した元の出力を**使用する**よう指示します。
*   **期待される結果：** 2つのシナリオが見られます：
    1. `add_concluding_note: True`の状態がないセッションでは、コールバックはエージェントの元の出力（"Processing complete!"）が使用されることを許可します。
    2. その状態フラグがあるセッションでは、コールバックはエージェントの元の出力をインターセプトし、自身のメッセージ（"Concluding note added..."）に置き換えます。
*   **コールバックの理解：** これは、`after_`コールバックが**後処理**や**変更**を可能にすることを示しています。あるステップ（エージェントの実行）の結果を検査し、ロジックに基づいてそれをそのまま通すか、変更するか、あるいは完全に置き換えるかを決定できます。

## LLMインタラクションコールバック

これらのコールバックは`LlmAgent`に特有のもので、大規模言語モデルとのインタラクションの前後でフックを提供します。

### Before Model コールバック

**タイミング：** `LlmAgent`のフロー内で、`generate_content_async`（または同等の）リクエストがLLMに送信される直前に呼び出されます。

**目的：** LLMに送られるリクエストの検査と変更を可能にします。ユースケースには、動的な指示の追加、状態に基づいてfew-shotの例を注入、モデル設定の変更、ガードレール（不適切な表現のフィルタなど）の実装、またはリクエストレベルのキャッシングの実装などがあります。

**戻り値の効果：**  
コールバックが`None`（Javaの場合は`Maybe.empty()`オブジェクト）を返した場合、LLMは通常のワークフローを続行します。コールバックが`LlmResponse`オブジェクトを返した場合、LLMへの呼び出しは**スキップされます**。返された`LlmResponse`は、あたかもモデルから直接来たかのように使用されます。これはガードレールやキャッシングを実装する際に非常に強力です。

??? "Code"
    === "Python"
    
        ```python
        --8<-- "examples/python/snippets/callbacks/before_model_callback.py"
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

**タイミング：** LLMからレスポンス（`LlmResponse`）を受け取った直後、呼び出し元のエージェントによってさらに処理される前に呼び出されます。

**目的：** 生のLLMレスポンスの検査や変更を可能にします。ユースケースには以下が含まれます：

*   モデル出力のロギング
*   レスポンスの再フォーマット
*   モデルによって生成された機密情報の検閲
*   LLMレスポンスから構造化データを解析し、`callback_context.state`に保存する
*   または特定のエラーコードの処理

??? "Code"
    === "Python"
    
        ```python
        --8<-- "examples/python/snippets/callbacks/after_model_callback.py"
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

これらのコールバックも`LlmAgent`に特有のもので、LLMがリクエストする可能性のあるツール（`FunctionTool`, `AgentTool`などを含む）の実行を巡ってトリガーされます。

### Before Tool コールバック

**タイミング：** LLMが特定のツールに関数呼び出しを生成した後、そのツールの`run_async`メソッドが呼び出される直前に呼び出されます。

**目的：** ツールの引数の検査と変更、実行前の認可チェック、ツール使用試行のロギング、またはツールレベルのキャッシングの実装を可能にします。

**戻り値の効果：**

1.  コールバックが`None`（Javaの場合は`Maybe.empty()`オブジェクト）を返した場合、ツールの`run_async`メソッドは（変更された可能性のある）`args`で実行されます。
2.  辞書（Javaの場合は`Map`）が返された場合、ツールの`run_async`メソッドは**スキップされます**。返された辞書は、ツール呼び出しの結果として直接使用されます。これはキャッシングやツールの振る舞いを上書きするのに便利です。

??? "Code"
    === "Python"
    
        ```python
        --8<-- "examples/python/snippets/callbacks/before_tool_callback.py"
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

**タイミング：** ツールの`run_async`メソッドが正常に完了した直後に呼び出されます。

**目的：** ツールからの結果を（要約後などの処理を経て）LLMに送り返す前に、その結果を検査および変更できます。ツールの結果のロギング、結果の後処理やフォーマット、または結果の特定部分をセッション状態に保存するのに役立ちます。

**戻り値の効果：**

1.  コールバックが`None`（Javaの場合は`Maybe.empty()`オブジェクト）を返した場合、元の`tool_response`が使用されます。
2.  新しい辞書が返された場合、それは元の`tool_response`を**置き換え**ます。これにより、LLMが見る結果を変更したりフィルタリングしたりできます。

??? "Code"
    === "Python"
    
        ```python
        --8<-- "examples/python/snippets/callbacks/after_tool_callback.py"
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