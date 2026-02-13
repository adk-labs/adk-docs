# 関数ツール

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

事前に構築されたADKツールが要件を満たさない場合は、カスタムの*関数ツール*を作成できます。関数ツールを構築すると、独自のデータベースへの接続や独自のアルゴリズムの実装など、カスタマイズされた機能を作成できます。
たとえば、関数ツール`myfinancetool`は、特定の財務指標を計算する関数である可能性があります。ADKは長時間実行される関数もサポートしているため、その計算に時間がかかる場合でも、エージェントは他のタスクを続行できます。

ADKは、それぞれ異なるレベルの複雑さと制御に適した、関数ツールを作成するためのいくつかの方法を提供します。

*  [関数ツール](#function-tool)
*  [長時間実行関数ツール](#long-run-tool)
*  [ツールとしてのエージェント](#agent-tool)

## 関数ツール {#function-tool}

Python関数をツールに変換することは、カスタムロジックをエージェントに統合する簡単な方法です。エージェントの`tools`リストに関数を割り当てると、フレームワークは自動的にそれを`FunctionTool`としてラップします。

### 仕組み

ADKフレームワークは、名前、docstring、パラメーター、型ヒント、デフォルト値など、Python関数のシグネチャを自動的に検査してスキーマを生成します。このスキーマは、LLMがツールの目的、使用時期、および必要な引数を理解するために使用するものです。

### 関数シグネチャの定義

LLMがツールを正しく使用するには、明確に定義された関数シグネチャが重要です。

#### パラメーター

##### 必須パラメーター

=== "Python"
    パラメーターは、型ヒントがあるが**デフォルト値がない**場合に**必須**と見なされます。LLMは、ツールを呼び出すときにこの引数の値を指定する必要があります。パラメーターの説明は、関数のdocstringから取得されます。

    ???+ "例：必須パラメーター"
        ```python
        def get_weather(city: str, unit: str):
            """
            指定された単位で都市の天気を取得します。

            引数：
                city (str): 都市名。
                unit (str): 温度単位。「摂氏」または「華氏」のいずれか。
            """
            # ... 関数のロジック ...
            return {"status": "success", "report": f"{city}の天気は晴れです。"}
        ```
    この例では、`city`と`unit`の両方が必須です。LLMがどちらか一方なしで`get_weather`を呼び出そうとすると、ADKはLLMにエラーを返し、呼び出しを修正するように促します。

=== "Go"
    Goでは、構造体タグを使用してJSONスキーマを制御します。2つの主要なタグは`json`と`jsonschema`です。

    パラメーターは、構造体フィールドの`json`タグに`omitempty`または`omitzero`オプションが**ない**場合に**必須**と見なされます。

    `jsonschema`タグは、引数の説明を提供するために使用されます。これは、LLMが引数が何であるかを理解するために重要です。

    ???+ "例：必須パラメーター"
        ```go
        // GetWeatherParamsは、getWeatherツールの引数を定義します。
        type GetWeatherParams struct {
            // このフィールドは必須です（「omitempty」なし）。
            // jsonschemaタグは説明を提供します。
            Location string `json:"location" jsonschema:"都市と州、例：カリフォルニア州サンフランシスコ"`

            // このフィールドも必須です。
            Unit     string `json:"unit" jsonschema:"温度単位。「摂氏」または「華氏」のいずれか"`
        }
        ```
    この例では、`location`と`unit`の両方が必須です。

##### オプションのパラメーター

=== "Python"
    パラメーターは、**デフォルト値**を指定した場合に**オプション**と見なされます。これは、オプションの引数を定義するための標準的なPythonの方法です。`typing.Optional[SomeType]`または`| None`構文（Python 3.10以降）を使用して、パラメーターをオプションとしてマークすることもできます。

    ???+ "例：オプションのパラメーター"
        ```python
        def search_flights(destination: str, departure_date: str, flexible_days: int = 0):
            """
            フライトを検索します。

            引数：
                destination (str): 目的地の都市。
                departure_date (str): 希望する出発日。
                flexible_days (int, optional): 検索の柔軟な日数。デフォルトは0です。
            """
            # ... 関数のロジック ...
            if flexible_days > 0:
                return {"status": "success", "report": f"{destination}への柔軟なフライトが見つかりました。"}
            return {"status": "success", "report": f"{departure_date}に{destination}へのフライトが見つかりました。"}
        ```
    ここでは、`flexible_days`はオプションです。LLMはそれを提供することを選択できますが、必須ではありません。

=== "Go"
    パラメーターは、構造体フィールドの`json`タグに`omitempty`または`omitzero`オプションがある場合に**オプション**と見なされます。

    ???+ "例：オプションのパラメーター"
        ```go
        // GetWeatherParamsは、getWeatherツールの引数を定義します。
        type GetWeatherParams struct {
            // 場所は必須です。
            Location string `json:"location" jsonschema:"都市と州、例：カリフォルニア州サンフランシスコ"`

            // 単位はオプションです。
            Unit string `json:"unit,omitempty" jsonschema:"温度単位。「摂氏」または「華氏」のいずれか"`

            // 日数はオプションです。
            Days int `json:"days,omitzero" jsonschema:"返す予報日数（デフォルトは1）"`
        }
        ```
    ここでは、`unit`と`days`はオプションです。LLMはそれらを提供することを選択できますが、必須ではありません。

##### `typing.Optional`を使用したオプションのパラメーター
`typing.Optional[SomeType]`または`| None`構文（Python 3.10以降）を使用して、パラメーターをオプションとしてマークすることもできます。これは、パラメーターが`None`になる可能性があることを示します。`None`のデフォルト値と組み合わせると、標準のオプションパラメーターのように動作します。

???+ "例：`typing.Optional`"
    === "Python"
        ```python
        from typing import Optional

        def create_user_profile(username: str, bio: Optional[str] = None):
            """
            新しいユーザープロファイルを作成します。

            引数：
                username (str): ユーザーの一意のユーザー名。
                bio (str, optional): ユーザーの短い経歴。デフォルトはNoneです。
            """
            # ... 関数のロジック ...
            if bio:
                return {"status": "success", "message": f"{username}のプロファイルが経歴付きで作成されました。"}
            return {"status": "success", "message": f"{username}のプロファイルが作成されました。"}
        ```

##### 可変長引数（`*args`および`**kwargs`）
他の目的で関数シグネチャに`*args`（可変長位置引数）および`**kwargs`（可変長キーワード引数）を含めることはできますが、LLMのツールスキーマを生成する際に**ADKフレームワークによって無視されます**。LLMはそれらを認識せず、引数を渡すことはできません。LLMから期待するすべてのデータについては、明示的に定義されたパラメーターに依存するのが最善です。

#### 戻り値の型

関数ツールの推奨される戻り値の型は、Pythonでは**辞書**、Javaでは**Map**です。これにより、キーと値のペアで応答を構造化し、LLMにコンテキストと明確さを提供できます。関数が辞書以外の型を返す場合、フレームワークは自動的にそれを**"result"**という名前の単一のキーを持つ辞書にラップします。

戻り値をできるだけ説明的にするように努めてください。*たとえば、*数値のエラーコードを返す代わりに、人間が読める説明を含む「error_message」キーを持つ辞書を返します。コードではなく**LLM**が結果を理解する必要があることを忘れないでください。ベストプラクティスとして、戻り値の辞書に「status」キーを含めて、全体的な結果（「success」、「error」、「pending」など）を示し、LLMに操作の状態に関する明確なシグナルを提供します。

#### Docstrings

関数のdocstringは、ツールの**説明**として機能し、LLMに送信されます。したがって、LLMがツールを効果的に使用する方法を理解するには、よく書かれた包括的なdocstringが不可欠です。関数の目的、パラメーターの意味、および期待される戻り値を明確に説明してください。

### ツール間のデータ受け渡し

エージェントが複数のツールを順番に呼び出す場合、あるツールから別のツールにデータを渡す必要がある場合があります。推奨される方法は、セッション状態で`temp:`プレフィックスを使用することです。

ツールは`temp:`変数にデータを書き込むことができ、後続のツールはそれを読み取ることができます。このデータは現在の呼び出しでのみ使用でき、その後は破棄されます。

!!! note "共有呼び出しコンテキスト"
    単一のエージェントターン内のすべてのツール呼び出しは、同じ`InvocationContext`を共有します。つまり、同じ一時的な（`temp:`）状態も共有するため、ツール間でデータを渡すことができます。

### 例

??? "例"

    === "Python"
    
        このツールは、指定された株式ティッカー/シンボルの株価を取得するPython関数です。
    
        <u>注</u>：このツールを使用する前に、`pip install yfinance`ライブラリをインストールする必要があります。
    
        ```py
        --8<-- "examples/python/snippets/tools/function-tools/func_tool.py"
        ```
    
        このツールからの戻り値は辞書にラップされます。
    
        ```json
        {"result": "$123"}
        ```
    
    === "Go"

        このツールは、株価のモック値を取得します。

        ```go
        import (
            "google.golang.org/adk/agent"
            "google.golang.org/adk/agent/llmagent"
            "google.golang.org/adk/model/gemini"
            "google.golang.org/adk/runner"
            "google.golang.org/adk/session"
            "google.golang.org/adk/tool"
            "google.golang.org/adk/tool/functiontool"
            "google.golang.org/genai"
        )

        --8<-- "examples/go/snippets/tools/function-tools/func_tool.go"
        ```

        このツールからの戻り値は`getStockPriceResults`インスタンスになります。

        ```json
        入力`{"symbol": "GOOG"}`の場合：{"price":300.6,"symbol":"GOOG"}
        ```

    === "Java"
    
        このツールは、株価のモック値を取得します。
    
        ```java
        --8<-- "examples/java/snippets/src/main/java/tools/StockPriceAgent.java:full_code"
        ```
    
        このツールからの戻り値はMap<String, Object>にラップされます。
    
        ```json
        入力`GOOG`の場合：{"symbol": "GOOG", "price": "1.0"}
        ```

### ベストプラクティス

関数を定義する際にはかなりの柔軟性がありますが、シンプルさがLLMの使いやすさを向上させることを忘れないでください。次のガイドラインを検討してください。

* **パラメーターは少ない方が良い：** 複雑さを減らすためにパラメーターの数を最小限に抑えます。  
* **単純なデータ型：** 可能な場合は、カスタムクラスよりも`str`や`int`などのプリミティブデータ型を優先します。  
* **意味のある名前：** 関数の名前とパラメーター名は、LLMがツールを解釈して利用する方法に大きく影響します。関数の目的と入力の意味を明確に反映する名前を選択してください。`do_stuff()`や`beAgent()`などの一般的な名前は避けてください。
* **並列実行用に構築：** 複数のツールが実行されるときに非同期操作用に構築することで、関数呼び出しのパフォーマンスを向上させます。ツールの並列実行を有効にする方法については、
[並列実行によるツールパフォーマンスの向上](/adk-docs/ja/tools-custom/performance/)を参照してください。

## 長時間実行関数ツール {#long-run-tool}

このツールは、エージェントの実行をブロックすることなく、エージェントワークフローの操作の外部で処理され、かなりの処理時間を必要とするタスクを開始および管理するのに役立つように設計されています。このツールは`FunctionTool`のサブクラスです。

`LongRunningFunctionTool`を使用する場合、関数は長時間実行操作を開始し、オプションで長時間実行操作IDなどの**初期結果**を返すことができます。長時間実行関数ツールが呼び出されると、エージェントランナーはエージェントの実行を一時停止し、エージェントクライアントが長時間実行操作が終了するまで続行するか待機するかを決定できるようにします。エージェントクライアントは、長時間実行操作の進行状況をクエリし、中間または最終応答を返信できます。その後、エージェントは他のタスクを続行できます。例としては、エージェントがタスクを続行する前に人間の承認が必要なヒューマンインザループシナリオがあります。

!!! warning "警告：実行処理"
    長時間実行関数ツールは、エージェントワークフローの一部として長時間実行タスクを開始および*管理*するのに役立つように設計されていますが、実際の長時間タスクを***実行***するわけではありません。
    完了にかなりの時間が必要なタスクの場合は、タスクを実行する別のサーバーを実装する必要があります。

!!! tip "ヒント：並列実行"
    構築しているツールの種類によっては、非同期操作用に設計する方が、長時間実行ツールを作成するよりも優れたソリューションになる場合があります。
    詳細については、
    [並列実行によるツールパフォーマンスの向上](/adk-docs/ja/tools-custom/performance/)を参照してください。

### 仕組み

Pythonでは、関数を`LongRunningFunctionTool`でラップします。Javaでは、メソッド名を`LongRunningFunctionTool.create()`に渡します。


1. **開始：** LLMがツールを呼び出すと、関数は長時間実行操作を開始します。

2. **初期更新：** 関数はオプションで初期結果（長時間実行操作IDなど）を返す必要があります。ADKフレームワークは結果を受け取り、`FunctionResponse`内にパッケージ化してLLMに返します。これにより、LLMはユーザーに通知できます（ステータス、完了率、メッセージなど）。その後、エージェントの実行は終了/一時停止されます。

3. **続行または待機：** 各エージェントの実行が完了した後。エージェントクライアントは、長時間実行操作の進行状況をクエリし、中間応答でエージェントの実行を続行するか（進行状況を更新するため）、最終応答が取得されるまで待機するかを決定できます。エージェントクライアントは、次回の実行のために中間または最終応答をエージェントに返信する必要があります。

4. **フレームワーク処理：** ADKフレームワークは実行を管理します。エージェントクライアントから送信された中間または最終`FunctionResponse`をLLMに送信して、ユーザーフレンドリーなメッセージを生成します。

### ツールの作成

ツール関数を定義し、`LongRunningFunctionTool`クラスを使用してラップします。

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/function-tools/human_in_the_loop.py:define_long_running_function"
    ```

=== "Go"

    ```go
    import (
        "google.golang.org/adk/agent"
        "google.golang.org/adk/agent/llmagent"
        "google.golang.org/adk/model/gemini"
        "google.golang.org/adk/tool"
        "google.golang.org/adk/tool/functiontool"
        "google.golang.org/genai"
    )

    --8<-- "examples/go/snippets/tools/function-tools/long-running-tool/long_running_tool.go:create_long_running_tool"
    ```

=== "Java"

    ```java
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.tools.LongRunningFunctionTool;
    import java.util.HashMap;
    import java.util.Map;
    
    public class ExampleLongRunningFunction {
    
      // 長時間実行関数を定義します。
      // 払い戻しの承認を求めます。
      public static Map<String, Object> askForApproval(String purpose, double amount) {
        // チケットの作成と通知の送信をシミュレートします
        System.out.println(
            "目的のためのチケット作成をシミュレートしています： " + purpose + ", 金額： " + amount);
    
        // チケットのリンクを付けて承認者に通知を送信します
        Map<String, Object> result = new HashMap<>();
        result.put("status", "pending");
        result.put("approver", "Sean Zhou");
        result.put("purpose", purpose);
        result.put("amount", amount);
        result.put("ticket-id", "approval-ticket-1");
        return result;
      }
    
      public static void main(String[] args) throws NoSuchMethodException {
        // メソッドをLongRunningFunctionTool.createに渡します
        LongRunningFunctionTool approveTool =
            LongRunningFunctionTool.create(ExampleLongRunningFunction.class, "askForApproval");
    
        // エージェントにツールを含めます
        LlmAgent approverAgent =
            LlmAgent.builder()
                // ...
                .tools(approveTool)
                .build();
      }
    }
    ```

### 中間/最終結果の更新

エージェントクライアントは、長時間実行関数呼び出しでイベントを受信し、チケットのステータスを確認します。その後、エージェントクライアントは中間または最終応答を返信して進行状況を更新できます。フレームワークは、この値（Noneであっても）をLLMに返される`FunctionResponse`のコンテンツにパッケージ化します。

!!! note "注：再開機能付きの長時間実行関数応答"

    ADKエージェントワークフローが
    [再開](/adk-docs/ja/runtime/resume/)機能で構成されている場合は、長時間実行
    関数応答とともに呼び出しID（`invocation_id`）パラメーターも指定する必要があります。
    指定する呼び出しIDは、長時間実行関数リクエストを生成した呼び出しと同じでなければなりません。
    そうしないと、システムは応答で新しい呼び出しを開始します。
    エージェントが再開機能を使用する場合は、応答に含めることができるように、
    長時間実行関数リクエストとともに呼び出しIDをパラメーターとして含めることを検討してください。
    再開機能の使用方法の詳細については、
    [停止したエージェントの再開](/adk-docs/ja/runtime/resume/)を参照してください。

??? Tip "Java ADKにのみ適用"

    関数ツールで`ToolContext`を渡す場合は、次のいずれかが当てはまることを確認してください。

    * スキーマが関数シグネチャのToolContextパラメーターとともに渡されます。例：
      ```
      @com.google.adk.tools.Annotations.Schema(name = "toolContext") ToolContext toolContext
      ```
    または

    * 次の`-parameters`フラグがmvnコンパイラプラグインに設定されています

    ```
    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.14.0</version> <!-- またはそれ以降 -->
                <configuration>
                    <compilerArgs>
                        <arg>-parameters</arg>
                    </compilerArgs>
                </configuration>
            </plugin>
        </plugins>
    </build>
    ```
    この制約は一時的なものであり、削除されます。


=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/function-tools/human_in_the_loop.py:call_reimbursement_tool"
    ```

=== "Go"

    次の例は、マルチターンワークフローを示しています。まず、ユーザーはエージェントにチケットを作成するように依頼します。エージェントは長時間実行ツールを呼び出し、クライアントは`FunctionCall` IDをキャプチャします。次に、クライアントは、チケットIDと最終ステータスを提供するために後続の`FunctionResponse`メッセージをエージェントに返信することで、非同期作業の完了をシミュレートします。

    ```go
    --8<-- "examples/go/snippets/tools/function-tools/long-running-tool/long_running_tool.go:run_long_running_tool"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/tools/LongRunningFunctionExample.java:full_code"
    ```

??? "Pythonの完全な例：ファイル処理シミュレーション"

    ```py
    --8<-- "examples/python/snippets/tools/function-tools/human_in_the_loop.py"
    ```

#### この例の主な側面

* **`LongRunningFunctionTool`**: 提供されたメソッド/関数をラップします。フレームワークは、生成された更新と最終的な戻り値を連続したFunctionResponsesとして送信することを処理します。

* **エージェントの指示**: LLMにツールを使用し、ユーザーの更新のために受信するFunctionResponseストリーム（進行状況と完了）を理解するように指示します。

* **最終的な戻り値**: 関数は最終的な結果の辞書を返し、完了を示すために最後のFunctionResponseで送信されます。

## ツールとしてのエージェント {#agent-tool}

この強力な機能により、システム内の他のエージェントの機能をツールとして呼び出すことで活用できます。ツールとしてのエージェントを使用すると、別のエージェントを呼び出して特定のタスクを実行させ、効果的に**責任を委任**できます。これは、概念的には、別のエージェントを呼び出し、エージェントの応答を関数の戻り値として使用するPython関数を作成することに似ています。

### サブエージェントとの主な違い

ツールとしてのエージェントとサブエージェントを区別することが重要です。

* **ツールとしてのエージェント：** エージェントAがエージェントBをツールとして呼び出すと（ツールとしてのエージェントを使用）、エージェントBの回答はエージェントAに**返され**、エージェントAは回答を要約してユーザーに応答を生成します。エージェントAは制御を維持し、将来のユーザー入力を引き続き処理します。  

* **サブエージェント：** エージェントAがエージェントBをサブエージェントとして呼び出すと、ユーザーに応答する責任は完全に**エージェントBに移管**されます。エージェントAは事実上ループから外れます。後続のすべてのユーザー入力はエージェントBによって応答されます。

### 使用法

エージェントをツールとして使用するには、エージェントをAgentToolクラスでラップします。

=== "Python"

    ```py
    tools=[AgentTool(agent=agent_b)]
    ```

=== "Go"

    ```go
    agenttool.New(agent, &agenttool.Config{...})
    ```

=== "Java"

    ```java
    AgentTool.create(agent)
    ```


### カスタマイズ

`AgentTool`クラスは、その動作をカスタマイズするための次の属性を提供します。

* **skip_summarization: bool:** Trueに設定すると、フレームワークはツールエージェントの応答の**LLMベースの要約をバイパス**します。これは、ツールの応答がすでに適切にフォーマットされており、それ以上の処理が必要ない場合に役立ちます。

??? "例"

    === "Python"

        ```py
        --8<-- "examples/python/snippets/tools/function-tools/summarizer.py"
        ```
  
    === "Go"

        ```go
        import (
            "google.golang.org/adk/agent"
            "google.golang.org/adk/agent/llmagent"
            "google.golang.org/adk/model/gemini"
            "google.golang.org/adk/tool"
            "google.golang.org/adk/tool/agenttool"
            "google.golang.org/genai"
        )

        --8<-- "examples/go/snippets/tools/function-tools/func_tool.go:agent_tool_example"
        ```

    === "Java"

        ```java
        --8<-- "examples/java/snippets/src/main/java/tools/AgentToolCustomization.java:full_code"
        ```

### 仕組み

1. `main_agent`が長いテキストを受信すると、その指示により、長いテキストには「summarize」ツールを使用するように指示されます。  
2. フレームワークは、「summarize」を`summary_agent`をラップする`AgentTool`として認識します。  
3. 舞台裏では、`main_agent`は長いテキストを入力として`summary_agent`を呼び出します。  
4. `summary_agent`は、その指示に従ってテキストを処理し、要約を生成します。  
5. **`summary_agent`からの応答は、`main_agent`に返されます。**  
6. `main_agent`は、要約を取得して、ユーザーへの最終的な応答を作成できます（例：「テキストの要約は次のとおりです...」）
