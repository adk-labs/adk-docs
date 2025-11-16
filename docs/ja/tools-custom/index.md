# ADK用のカスタムツール

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

ADKエージェントワークフローにおいて、ツールとは、ADKエージェントがアクションを実行するために呼び出すことができる、構造化された入出力を持つプログラミング関数です。ADKツールは、Geminiや他の生成AIモデルで[関数呼び出し（Function Call）](https://ai.google.dev/gemini-api/docs/function-calling)を使用するのと同様に機能します。ADKツールを使用すると、次のようなさまざまなアクションやプログラミング機能を実行できます。

*   データベースのクエリ
*   APIリクエストの実行：天気データの取得、予約システムなど
*   ウェブ検索
*   コードスニペットの実行
*   ドキュメントからの情報取得（RAG）
*   他のソフトウェアやサービスとの連携

!!! tip "[ADKツール一覧](/adk-docs/tools/)"
    独自のツールを構築する前に、**[ADKツール一覧](/adk-docs/tools/)**で、ADKエージェントで使用できるビルド済みツールを確認してください。

## ツールとは何か？

ADKの文脈において、ツールとはAIエージェントに提供される特定の能力を表し、中核となるテキスト生成や推論能力を超えて、アクションを実行し、外部世界と対話することを可能にします。有能なエージェントと基本的な言語モデルを区別するのは、しばしばツールの効果的な使用です。

技術的には、ツールは通常、モジュール化されたコードコンポーネントです。例えば、**Python/Javaの関数**、クラスメソッド、あるいは別の特化したエージェントなどであり、明確に定義された事前定義タスクを実行するように設計されています。これらのタスクは、多くの場合、外部システムやデータとの対話を伴います。

<img src="../assets/agent-tool-call.png" alt="Agent tool call">

### 主な特徴

**アクション指向:** ツールは、情報の検索、APIの呼び出し、計算の実行など、エージェントのために特定のアクションを実行します。

**エージェントの能力を拡張:** ツールはエージェントがリアルタイム情報にアクセスしたり、外部システムに影響を与えたり、トレーニングデータに内在する知識の限界を克服したりすることを可能にします。

**事前定義されたロジックの実行:** 重要な点として、ツールは開発者が定義した特定のロジックを実行します。ツール自体は、エージェントの中核となる大規模言語モデル（LLM）のような独立した推論能力を持ちません。LLMはどのツールを、いつ、どのような入力で使用するかを推論しますが、ツール自体は指定された関数を実行するだけです。

## エージェントによるツールの使用方法

エージェントは、多くの場合、関数呼び出しを伴うメカニズムを通じて動的にツールを活用します。プロセスは一般的に次のステップに従います。

1. **推論:** エージェントのLLMが、システム指示、会話履歴、ユーザーのリクエストを分析します。
2. **選択:** 分析に基づき、LLMはエージェントが利用可能なツールと各ツールを説明するdocstringを基に、実行するツール（もしあれば）を決定します。
3. **呼び出し:** LLMは選択したツールに必要な引数（入力）を生成し、その実行をトリガーします。
4. **観察:** エージェントはツールから返された出力（結果）を受け取ります。
5. **最終化:** エージェントはツールの出力を進行中の推論プロセスに組み込み、次の応答を作成したり、後続のステップを決定したり、目標が達成されたかどうかを判断したりします。

ツールは、エージェントの知的コア（LLM）が複雑なタスクを達成するために必要に応じてアクセスし利用できる、専門的なツールキットだと考えてください。

## ADKにおけるツールの種類

ADKは、いくつかの種類のツールをサポートすることで柔軟性を提供します。

1. **[関数ツール（Function Tools）](../tools/function-tools.md):** 特定のアプリケーションのニーズに合わせて、開発者が作成するツール。
    * **[関数/メソッド](../tools/function-tools.md#1-function-tool):** コードで標準の同期関数またはメソッド（例: Pythonの`def`）を定義します。
    * **[ツールとしてのエージェント（Agents-as-Tools）](../tools/function-tools.md#3-agent-as-a-tool):** 別の（潜在的に特化した）エージェントを親エージェントのツールとして使用します。
    * **[長時間実行関数ツール（Long Running Function Tools）](../tools/function-tools.md#2-long-running-function-tool):** 非同期操作や完了にかなりの時間を要するツールをサポートします。
2. **[組み込みツール（Built-in Tools）](../tools/built-in-tools.md):** 一般的なタスクのためにフレームワークが提供する、すぐに使えるツール。
        例: Google検索、コード実行、検索拡張生成（RAG）。
3. **サードパーティ製ツール（Third-Party Tools):** 一般的な外部ライブラリのツールをシームレスに統合します。

各ツールタイプの詳細情報と例については、上記でリンクされている各ドキュメントページを参照してください。

## エージェントの指示におけるツールの参照

エージェントの指示の中で、**関数名**を使用してツールを直接参照することができます。ツールの**関数名**と**docstring**が十分に説明的であれば、指示は主に**大規模言語モデル（LLM）がいつそのツールを利用すべきか**に焦点を当てることができます。これにより、モデルが各ツールの意図された使用法を理解するのに役立ちます。

ツールが生成する可能性のある**さまざまな戻り値に対してエージェントがどのように対処すべきかを明確に指示することが非常に重要です**。たとえば、ツールがエラーメッセージを返す場合、エージェントが操作を再試行すべきか、タスクを断念すべきか、またはユーザーに追加情報を要求すべきかを指示に明記する必要があります。

さらに、ADKは、あるツールの出力が別のツールの入力として機能する、ツールの連続使用をサポートしています。このようなワークフローを実装する際には、モデルが必要なステップを順に実行できるよう、エージェントの指示内で**意図されたツールの使用順序を記述する**ことが重要です。

### 例

次の例は、エージェントが**指示で関数名を参照して**ツールを使用する方法を示しています。また、成功またはエラーメッセージなど、**ツールからのさまざまな戻り値を処理するよう**エージェントをガイドする方法や、タスクを達成するために**複数のツールを連続して使用する**よう調整する方法も示しています。

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/overview/weather_sentiment.py"
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/tools-custom/weather_sentiment/main.go"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/tools/WeatherSentimentAgentApp.java:full_code"
    ```

## ツールコンテキスト (Tool Context)

より高度なシナリオのために、ADKでは特別なパラメータ`tool_context: ToolContext`を含めることで、ツール関数内から追加のコンテキスト情報にアクセスできます。これを関数シグネチャに含めることで、エージェントの実行中にツールが呼び出されると、ADKは**自動的に** **ToolContext**クラスの**インスタンスを提供**します。

**ToolContext**は、いくつかの主要な情報と制御手段へのアクセスを提供します。

* `state: State`: 現在のセッションの状態を読み書きします。ここで行われた変更は追跡され、永続化されます。

* `actions: EventActions`: ツール実行後のエージェントの後続アクションに影響を与えます（例: 要約のスキップ、別のエージェントへの転送）。

* `function_call_id: str`: この特定のツール呼び出しに対してフレームワークによって割り当てられた一意の識別子。認証応答との追跡や関連付けに役立ちます。これは、単一のモデル応答内で複数のツールが呼び出される場合にも役立ちます。

* `function_call_event_id: str`: この属性は、現在のツール呼び出しをトリガーした**イベント**の一意の識別子を提供します。これは追跡やロギングの目的で役立ちます。

* `auth_response: Any`: このツール呼び出しの前に認証フローが完了した場合に、認証応答/資格情報を含みます。

* サービスへのアクセス: ArtifactsやMemoryなどの設定済みサービスと対話するためのメソッド。

`tool_context`パラメータはツール関数のdocstringに含めるべきではないことに注意してください。`ToolContext`はLLMがツール関数を呼び出すことを決定した*後*にADKフレームワークによって自動的にインジェクトされるため、LLMの意思決定には関係なく、これを含めるとLLMを混乱させる可能性があります。

### **状態管理 (State Management)**

`tool_context.state`属性は、現在のセッションに関連付けられた状態への直接的な読み書きアクセスを提供します。これは辞書のように動作しますが、すべての変更が差分として追跡され、セッションサービスによって永続化されることを保証します。これにより、ツールは複数の対話やエージェントのステップをまたいで情報を維持し、共有することができます。

* **状態の読み取り**: 標準的な辞書アクセス（`tool_context.state['my_key']`）または`.get()`メソッド（`tool_context.state.get('my_key', default_value)`）を使用します。

* **状態への書き込み**: 値を直接代入します（`tool_context.state['new_key'] = 'new_value'`）。これらの変更は、結果として得られるイベントの`state_delta`に記録されます。

* **状態のプレフィックス**: 標準の状態プレフィックスを覚えておいてください。

    * `app:*`: アプリケーションのすべてのユーザー間で共有されます。

    * `user:*`: 現在のユーザーのすべてのセッションにわたって固有です。

    * （プレフィックスなし）: 現在のセッションに固有です。

    * `temp:*`: 一時的で、呼び出し間で永続化されません（単一の`run`コール内でデータを渡すのに役立ちますが、通常、LLM呼び出し間で動作するツールコンテキスト内ではあまり役立ちません）。

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/overview/user_preference.py"
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/tools-custom/user_preference/user_preference.go:example"
    ```

=== "Java"

    ```java
    import com.google.adk.tools.FunctionTool;
    import com.google.adk.tools.ToolContext;

    // ユーザー固有の設定を更新します。
    public Map<String, String> updateUserThemePreference(String value, ToolContext toolContext) {
      String userPrefsKey = "user:preferences:theme";

      // 現在の設定を取得するか、存在しない場合は初期化します。
      String preference = toolContext.state().getOrDefault(userPrefsKey, "").toString();
      if (preference.isEmpty()) {
        preference = value;
      }

      // 更新された辞書を状態に書き戻します。
      toolContext.state().put("user:preferences", preference);
      System.out.printf("ツール: ユーザー設定 %s を %s に更新しました", userPrefsKey, preference);

      return Map.of("status", "success", "updated_preference", toolContext.state().get(userPrefsKey).toString());
      // LLMが updateUserThemePreference("dark") を呼び出すと:
      // toolContext.stateが更新され、その変更は
      // 結果として得られるツール応答イベントの actions.stateDelta の一部になります。
    }
    ```

### **エージェントフローの制御 (Controlling Agent Flow)**

`tool_context.actions`属性（Javaでは`ToolContext.actions()`、Goでは`tool.Context.Actions()`）は**EventActions**オブジェクトを保持します。このオブジェクトの属性を変更することで、ツールが実行を終了した後にエージェントやフレームワークが何をするかに影響を与えることができます。

* **`skip_summarization: bool`**: （デフォルト: False）Trueに設定すると、通常ツールの出力を要約するLLM呼び出しをバイパスするようADKに指示します。ツールの戻り値がすでにユーザー向けのメッセージである場合に便利です。

* **`transfer_to_agent: str`**: これを別のエージェントの名前に設定します。フレームワークは現在のエージェントの実行を停止し、**対話の制御を指定されたエージェントに移行**します。これにより、ツールはタスクをより専門的なエージェントに動的に引き継ぐことができます。

* **`escalate: bool`**: （デフォルト: False）これをTrueに設定すると、現在のエージェントがリクエストを処理できず、制御を（階層内にある場合）親エージェントに渡すべきであることを示します。LoopAgentでは、サブエージェントのツールで**escalate=True**を設定するとループが終了します。

#### 例

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/overview/customer_support_agent.py"
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/tools-custom/customer_support_agent/main.go"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/tools/CustomerSupportAgentApp.java:full_code"
    ```

##### 説明

* `main_agent`と`support_agent`という2つのエージェントを定義します。`main_agent`は最初の接点として設計されています。
* `main_agent`によって呼び出されると、`check_and_transfer`ツールはユーザーのクエリを調べます。
* クエリに「urgent」という単語が含まれている場合、ツールは`tool_context`、具体的には**`tool_context.actions`**にアクセスし、`transfer_to_agent`属性を`support_agent`に設定します。
* このアクションは、フレームワークに対して**対話の制御を`support_agent`という名前のエージェントに移行する**よう信号を送ります。
* `main_agent`が緊急のクエリを処理すると、`check_and_transfer`ツールが移行をトリガーします。その後の応答は、理想的には`support_agent`から来ることになります。
* 緊急性のない通常のクエリの場合、ツールは移行をトリガーせずに単にそれを処理します。

この例は、ツールがToolContextのEventActionsを通じて、対話の流れを動的に変更し、別の専門エージェントに制御を移行できることを示しています。

### **認証 (Authentication)**

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span>
</div>

ToolContextは、認証が必要なAPIと対話するツールのためのにメカニズムを提供します。ツールが認証を処理する必要がある場合、以下を使用することがあります。

* **`auth_response`**: ツールが呼び出される前にフレームワークによって認証がすでに処理されていた場合、資格情報（例: トークン）を含みます（RestApiToolやOpenAPIセキュリティスキームで一般的）。

* **`request_credential(auth_config: dict)`**: ツールが認証が必要だと判断したが資格情報が利用できない場合にこのメソッドを呼び出します。これは、提供された`auth_config`に基づいて認証フローを開始するようフレームワークに信号を送ります。

* **`get_auth_response()`**: （`request_credential`が正常に処理された後の）後続の呼び出しで、ユーザーが提供した資格情報を取得するために呼び出します。

認証フロー、設定、および例に関する詳細な説明については、専用のツール認証ドキュメントページを参照してください。

### **コンテキスト認識データアクセス メソッド (Context-Aware Data Access Methods)**

これらのメソッドは、ツールが設定済みサービスによって管理される、セッションやユーザーに関連付けられた永続データと便利に対話する方法を提供します。

* **`list_artifacts()`** (Javaでは **`listArtifacts()`**): `artifact_service`を介して現在セッションに保存されているすべてのアーティファクトのファイル名（またはキー）のリストを返します。アーティファクトは通常、ユーザーによってアップロードされたり、ツール/エージェントによって生成されたりするファイル（画像、ドキュメントなど）です。

* **`load_artifact(filename: str)`**: **`artifact_service`**からファイル名で特定のアーティファクトを取得します。オプションでバージョンを指定できます。省略した場合は最新バージョンが返されます。アーティファクトのデータとMIMEタイプを含む`google.genai.types.Part`オブジェクトを返します。見つからない場合はNoneを返します。

* **`save_artifact(filename: str, artifact: types.Part)`**: `artifact_service`にアーティファクトの新しいバージョンを保存します。新しいバージョン番号（0から始まる）を返します。

* **`search_memory(query: str)`**: (ADK PythonおよびGoでサポート)
    設定済みの`memory_service`を使用してユーザーの長期記憶をクエリします。これは、過去の対話や保存された知識から関連情報を取得するのに役立ちます。**SearchMemoryResponse**の構造は特定のメモリサービスの実装に依存しますが、通常は関連するテキストのスニペットや会話の抜粋が含まれます。

#### 例

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/overview/doc_analysis.py"
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/tools-custom/doc_analysis/doc_analysis.go"
    ```

=== "Java"

    ```java
    // メモリのコンテキストを使用してドキュメントを分析します。
    // コールバックコンテキストまたはLoadArtifactsツールを使用して、アーティファクトの一覧表示、読み込み、保存も可能です。
    public static @NonNull Maybe<ImmutableMap<String, Object>> processDocument(
        @Annotations.Schema(description = "分析するドキュメントの名前。") String documentName,
        @Annotations.Schema(description = "分析のためのクエリ。") String analysisQuery,
        ToolContext toolContext) {

      // 1. 利用可能なすべてのアーティファクトを一覧表示
      System.out.printf(
          "利用可能なすべてのアーティファクトを一覧表示 %s:", toolContext.listArtifacts().blockingGet());

      // 2. アーティファクトをメモリに読み込む
      System.out.println("ツール: アーティファクトの読み込み試行: " + documentName);
      Part documentPart = toolContext.loadArtifact(documentName, Optional.empty()).blockingGet();
      if (documentPart == null) {
        System.out.println("ツール: ドキュメント '" + documentName + "' が見つかりません。");
        return Maybe.just(
            ImmutableMap.<String, Object>of(
                "status", "error", "message", "ドキュメント '" + documentName + "' が見つかりません。"));
      }
      String documentText = documentPart.text().orElse("");
      System.out.println(
          "ツール: ドキュメント '" + documentName + "' を読み込みました (" + documentText.length() + " 文字)。");

      // 3. 分析を実行 (プレースホルダー)
      String analysisResult =
          "'" + documentName + "' に関する '" + analysisQuery + "' の分析 [プレースホルダー分析結果]";
      System.out.println("ツール: 分析を実行しました。");

      // 4. 分析結果を新しいアーティファクトとして保存
      Part analysisPart = Part.fromText(analysisResult);
      String newArtifactName = "analysis_" + documentName;

      toolContext.saveArtifact(newArtifactName, analysisPart);

      return Maybe.just(
          ImmutableMap.<String, Object>builder()
              .put("status", "success")
              .put("analysis_artifact", newArtifactName)
              .build());
    }
    // FunctionTool processDocumentTool =
    //      FunctionTool.create(ToolContextArtifactExample.class, "processDocument");
    // エージェントにこの関数ツールを含めます。
    // LlmAgent agent = LlmAgent().builder().tools(processDocumentTool).build();
    ```

**ToolContext**を活用することで、開発者はADKのアーキテクチャとシームレスに統合し、エージェントの全体的な能力を向上させる、より洗練されたコンテキスト認識型のカスタムツールを作成できます。

## 効果的なツール関数の定義

メソッドや関数をADKツールとして使用する場合、その定義方法がエージェントの正しい使用能力に大きく影響します。エージェントの大規模言語モデル（LLM）は、関数の**名前**、**パラメータ（引数）**、**型ヒント**、そして**docstring** / **ソースコードコメント**に大きく依存して、その目的を理解し、正しい呼び出しを生成します。

以下は、効果的なツール関数を定義するための主要なガイドラインです。

* **関数名:**
    * `get_weather`、`searchDocuments`、`schedule_meeting`など、アクションを明確に示す、記述的で動詞-名詞ベースの名前を使用します。
    * `run`、`process`、`handle_data`などの一般的な名前や、`doStuff`などの過度に曖昧な名前は避けてください。良い説明があっても、`do_stuff`のような名前は、例えば`cancelFlight`と比較して、いつこのツールを使うべきかモデルを混乱させる可能性があります。
    * LLMはツール選択時に主要な識別子として関数名を使用します。

* **パラメータ（引数）:**
    * 関数には任意の数のパラメータを設定できます。
    * `c`の代わりに`city`、`q`の代わりに`search_query`など、明確で記述的な名前を使用します。
    * **Pythonではすべてのパラメータに型ヒントを提供します**（例: `city: str`, `user_id: int`, `items: list[str]`）。これはADKがLLM用の正しいスキーマを生成するために不可欠です。
    * すべてのパラメータ型が**JSONシリアライズ可能**であることを確認してください。すべてのJavaプリミティブ型、および`str`、`int`、`float`、`bool`、`list`、`dict`などの標準的なPython型とその組み合わせは一般的に安全です。明確なJSON表現がない限り、複雑なカスタムクラスインスタンスを直接のパラメータとして使用することは避けてください。
    * パラメータに**デフォルト値を設定しないでください**。例: `def my_func(param1: str = "default")`。デフォルト値は、基盤となるモデルが関数呼び出しを生成する際に確実にはサポートまたは使用されません。必要なすべての情報は、LLMがコンテキストから導き出すか、不足している場合は明示的に要求する必要があります。
    * **`self` / `cls`は自動的に処理されます:** インスタンスメソッドの`self`やクラスメソッドの`cls`のような暗黙のパラメータはADKによって自動的に処理され、LLMに表示されるスキーマから除外されます。ツールがLLMに提供を要求する論理的なパラメータに対してのみ、型ヒントと説明を定義する必要があります。

* **戻り値の型:**
    * 関数の戻り値は、Pythonでは**辞書（`dict`）**、Javaでは**Map**でなければなりません。
    * 関数が辞書以外の型（例: 文字列、数値、リスト）を返す場合、ADKフレームワークは結果をモデルに返す前に、自動的に`{'result': your_original_return_value}`のような辞書/Mapでラップします。
    * 辞書/Mapのキーと値は、***LLMが*簡単に理解できるように**記述的に設計してください。モデルがこの出力を読んで次のステップを決定することを忘れないでください。
    * 意味のあるキーを含めてください。例えば、`500`のようなエラーコードだけを返すのではなく、`{'status': 'error', 'error_message': 'Database connection failed'}`を返してください。
    * モデルにツール実行の結果を明確に示すために、`status`キー（例: `'success'`, `'error'`, `'pending'`, `'ambiguous'`）を含めることは**強く推奨される実践**です。

* **Docstring / ソースコードコメント:**
    * **これは非常に重要です。** docstringはLLMにとって主要な説明情報源です。
    * **ツールが*何をするのか*を明確に記述してください。** その目的と制限について具体的に記述してください。
    * **ツールを*いつ*使用すべきかを説明してください。** LLMの意思決定を導くためのコンテキストや使用例のシナリオを提供してください。
    * ***各パラメータ*を明確に説明してください。** LLMがその引数に対してどのような情報を提供する必要があるかを説明してください。
    * 期待される`dict`の戻り値の**構造と意味**、特にさまざまな`status`値と関連するデータキーを説明してください。
    * **インジェクトされるToolContextパラメータを記述しないでください。** オプションの`tool_context: ToolContext`パラメータはLLMが知る必要のあるパラメータではないため、docstringの説明内に記述することは避けてください。ToolContextは、LLMがそれを呼び出すことを決定した*後*にADKによってインジェクトされます。

    **良い定義の例:**

=== "Python"

    ```python
    def lookup_order_status(order_id: str) -> dict:
      """IDを使用して顧客の注文の現在のステータスを取得します。

      ユーザーが特定の注文のステータスを明示的に尋ね、注文IDを提供した場合にのみ
      このツールを使用してください。一般的な問い合わせには使用しないでください。

      Args:
          order_id: 検索する注文の一意の識別子。

      Returns:
          結果を示す辞書。
          成功した場合、ステータスは 'success' で、'order' 辞書が含まれます。
          失敗した場合、ステータスは 'error' で、'error_message' が含まれます。
          成功例: {'status': 'success', 'order': {'state': 'shipped', 'tracking_number': '1Z9...'}}
          エラー例: {'status': 'error', 'error_message': '注文IDが見つかりません。'}
      """
      # ... ステータスを取得するための関数実装 ...
      if status_details := fetch_status_from_backend(order_id):
        return {
            "status": "success",
            "order": {
                "state": status_details.state,
                "tracking_number": status_details.tracking,
            },
        }
      else:
        return {"status": "error", "error_message": f"注文ID {order_id} が見つかりません。"}

    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/tools-custom/order_status/order_status.go:snippet"
    ```

=== "Java"

    ```java
    /**
     * 指定された都市の現在の天気予報を取得します。
     *
     * @param city 天気予報を取得する都市。
     * @param toolContext ツールのコンテキスト。
     * @return 天気情報を含む辞書。
     */
    public static Map<String, Object> getWeatherReport(String city, ToolContext toolContext) {
        Map<String, Object> response = new HashMap<>();
        if (city.toLowerCase(Locale.ROOT).equals("london")) {
            response.put("status", "success");
            response.put(
                    "report",
                    "ロンドンの現在の天気は曇りで、気温は18度、雨の可能性があります。");
        } else if (city.toLowerCase(Locale.ROOT).equals("paris")) {
            response.put("status", "success");
            response.put("report", "パリの天気は晴れで、気温は25度です。");
        } else {
            response.put("status", "error");
            response.put("error_message", String.format("'%s' の天気情報は利用できません。", city));
        }
        return response;
    }
    ```

* **単純さと焦点:**
    * **ツールは焦点を絞る:** 各ツールは理想的には1つの明確に定義されたタスクを実行すべきです。
    * **パラメータは少ない方が良い:** モデルは一般的に、多くのオプションまたは複雑なパラメータを持つツールよりも、明確に定義された少数のパラメータを持つツールをより確実に処理します。
    * **単純なデータ型を使用する:** 可能な場合は、パラメータとして複雑なカスタムクラスや深くネストされた構造よりも、基本的な型（**Python**では`str`, `int`, `bool`, `float`, `List[str]`、**Java**では`int`, `byte`, `short`, `long`, `float`, `double`, `boolean`, `char`）を優先します。
    * **複雑なタスクを分解する:** 複数の異なる論理ステップを実行する関数を、より小さく、より焦点の合ったツールに分割します。例えば、単一の`update_user_profile(profile: ProfileObject)`ツールの代わりに、`update_user_name(name: str)`、`update_user_address(address: str)`、`update_user_preferences(preferences: list[str])`などの個別のツールを検討します。これにより、LLMが正しい能力を選択して使用するのが容易になります。

これらのガイドラインに従うことで、LLMがカスタム関数ツールを効果的に利用するために必要な明確さと構造を提供し、より有能で信頼性の高いエージェントの振る舞いにつながります。

## ツールセット (Toolsets): ツールのグループ化と動的な提供

<div class="language-support-tag" title="この機能は現在Pythonで利用可能です。">
   <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.5.0</span>
</div>

個々のツールを超えて、ADKは`BaseToolset`インターフェース（`google.adk.tools.base_toolset`で定義）を介して**ツールセット (Toolset)**の概念を導入します。ツールセットを使用すると、`BaseTool`インスタンスのコレクションを、しばしば動的に、管理してエージェントに提供することができます。

このアプローチは、以下の場合に有益です。

*   **関連ツールの整理:** 共通の目的を持つツールをグループ化します（例: すべての数学演算用ツール、または特定のAPIと対話するすべてのツール）。
*   **動的なツールの可用性:** エージェントが現在のコンテキスト（例: ユーザー権限、セッション状態、またはその他の実行時条件）に基づいて異なるツールを利用できるようにします。ツールセットの`get_tools`メソッドが、どのツールを公開するかを決定できます。
*   **外部ツールプロバイダーの統合:** ツールセットは、OpenAPI仕様やMCPサーバーなどの外部システムから来るツールのアダプターとして機能し、それらをADK互換の`BaseTool`オブジェクトに変換できます。

### `BaseToolset`インターフェース

ADKでツールセットとして機能するクラスは、`BaseToolset`抽象基底クラスを実装する必要があります。このインターフェースは主に2つのメソッドを定義します。

*   **`async def get_tools(...) -> list[BaseTool]:`**
    これはツールセットの中核となるメソッドです。ADKエージェントが利用可能なツールを知る必要がある場合、その`tools`リストで提供される各`BaseToolset`インスタンスに対して`get_tools()`を呼び出します。
    *   オプションの`readonly_context`（`ReadonlyContext`のインスタンス）を受け取ります。このコンテキストは、現在のセッション状態（`readonly_context.state`）、エージェント名、呼び出しIDなどの情報への読み取り専用アクセスを提供します。ツールセットはこのコンテキストを使用して、どのツールを返すかを動的に決定できます。
    *   **必ず** `BaseTool`インスタンス（例: `FunctionTool`, `RestApiTool`）の`list`を返す必要があります。

*   **`async def close(self) -> None:`**
    この非同期メソッドは、例えばエージェントサーバーがシャットダウンするときや`Runner`が閉じられるときなど、ツールセットが不要になったときにADKフレームワークによって呼び出されます。ネットワーク接続を閉じる、ファイルハンドルを解放する、またはツールセットが管理する他のリソースをクリーンアップするなど、必要なクリーンアップ処理を実行するためにこのメソッドを実装します。

### エージェントでのツールセットの使用

`BaseToolset`実装のインスタンスを、個々の`BaseTool`インスタンスと共に、`LlmAgent`の`tools`リストに直接含めることができます。

エージェントが初期化されるか、利用可能な能力を決定する必要がある場合、ADKフレームワークは`tools`リストを反復処理します。

*   アイテムが`BaseTool`インスタンスの場合、それは直接使用されます。
*   アイテムが`BaseToolset`インスタンスの場合、その`get_tools()`メソッドが（現在の`ReadonlyContext`と共に）呼び出され、返された`BaseTool`のリストがエージェントの利用可能なツールに追加されます。

### 例: シンプルな数学ツールセット

簡単な算術演算を提供するツールセットの基本的な例を作成しましょう。

```py
--8<-- "examples/python/snippets/tools/overview/toolset_example.py:init"
```

この例では:

*   `SimpleMathToolset`は`BaseToolset`を実装し、その`get_tools()`メソッドは`add_numbers`と`subtract_numbers`のための`FunctionTool`インスタンスを返します。また、プレフィックスを使用してそれらの名前をカスタマイズします。
*   `calculator_agent`は、個々の`greet_tool`と`SimpleMathToolset`のインスタンスの両方で構成されています。
*   `calculator_agent`が実行されると、ADKは`math_toolset_instance.get_tools()`を呼び出します。エージェントのLLMは、ユーザーリクエストを処理するために`greet_user`、`calculator_add_numbers`、および`calculator_subtract_numbers`にアクセスできるようになります。
*   `add_numbers`ツールは`tool_context.state`への書き込みを実演し、エージェントの指示ではこの状態の読み取りについて言及しています。
*   `close()`メソッドは、ツールセットが保持するリソースが確実に解放されるように呼び出されます。

ツールセットは、ADKエージェントにツールのコレクションを整理、管理、動的に提供する強力な方法を提供し、よりモジュール化され、保守可能で、適応性のあるエージェントアプリケーションにつながります。