# LLMエージェント

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

`LlmAgent`（しばしば`Agent`と略されます）はADKにおけるコアコンポーネントであり、アプリケーションの「思考」部分として機能します。大規模言語モデル（LLM）の能力を活用して、推論、自然言語の理解、意思決定、応答の生成、ツールとの対話を行います。

事前に定義された実行パスに従う決定論的な[ワークフローエージェント](workflow-agents/index.md)とは異なり、`LlmAgent`の振る舞いは非決定的です。LLMを使用して指示とコンテキストを解釈し、動的に処理方法を決定したり、どのツールを使用するか（もし使用する場合）、あるいは他のエージェントに制御を移すかを判断します。

効果的な`LlmAgent`を構築するには、そのアイデンティティを定義し、指示を通じてその振る舞いを明確にガイドし、必要なツールと能力を備えさせることが含まれます。

## エージェントのアイデンティティと目的の定義

まず、エージェントが*何であるか*、そして*何のためにあるのか*を確立する必要があります。

*   **`name` (必須):** 全てのエージェントには一意の文字列識別子が必要です。この`name`は内部操作、特にエージェント同士が互いを参照したりタスクを委任したりする必要があるマルチエージェントシステムにおいて非常に重要です。エージェントの機能を反映した説明的な名前（例: `customer_support_router`, `billing_inquiry_agent`）を選択してください。`user`のような予約名は避けてください。

*   **`description` (任意、マルチエージェントで推奨):** エージェントの能力に関する簡潔な要約を提供します。この説明は主に、*他の*LLMエージェントがこのエージェントにタスクをルーティングすべきかどうかを判断するために使用されます。同僚と区別できるように、具体的に記述してください（例: 「請求エージェント」ではなく、「現在の請求書に関する問い合わせを処理します」）。

*   **`model` (必須):** このエージェントの推論を支える基盤となるLLMを指定します。これは`"gemini-2.0-flash"`のような文字列識別子です。モデルの選択は、エージェントの能力、コスト、パフォーマンスに影響します。利用可能なオプションと考慮事項については、[モデル](models.md)ページを参照してください。

=== "Python"

    ```python
    # 例: 基本的なアイデンティティの定義
    capital_agent = LlmAgent(
        model="gemini-2.0-flash",
        name="capital_agent",
        description="与えられた国の首都に関するユーザーの質問に答えます。"
        # instruction と tools は次に追加します
    )
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/agents/llm-agents/snippets/main.go:identity"
    ```

=== "Java"

    ```java
    // 例: 基本的なアイデンティティの定義
    LlmAgent capitalAgent =
        LlmAgent.builder()
            .model("gemini-2.0-flash")
            .name("capital_agent")
            .description("与えられた国の首都に関するユーザーの質問に答えます。")
            // instruction と tools は次に追加します
            .build();
    ```

## エージェントのガイド：指示 (`instruction`)

`instruction`パラメータは、`LlmAgent`の振る舞いを形成する上で、おそらく最も重要な要素です。これは、エージェントに以下のことを伝える文字列（または文字列を返す関数）です：

*   その中核となるタスクや目標。
*   その性格やペルソナ（例：「あなたは親切なアシスタントです」、「あなたは機知に富んだ海賊です」）。
*   その振る舞いに対する制約（例：「Xに関する質問にのみ答えてください」、「Yは決して明かさないでください」）。
*   `tools`をどのように、いつ使用するか。各ツールの目的と、それが呼び出されるべき状況を説明し、ツール自体の説明を補足する必要があります。
*   望ましい出力フォーマット（例：「JSONで応答してください」、「箇条書きリストで提供してください」）。

**効果的な指示のためのヒント:**

*   **明確かつ具体的に:** 曖昧さを避けてください。望ましい行動と結果を明確に記述します。
*   **マークダウンを使用:** 複雑な指示の可読性を向上させるために、見出しやリストなどを使用します。
*   **例を提供する (Few-Shot):** 複雑なタスクや特定の出力フォーマットの場合、指示の中に直接例を含めます。
*   **ツールの使用をガイド:** ツールをリストアップするだけでなく、エージェントが*いつ*、*なぜ*それらを使用すべきかを説明します。

**状態 (State):**

*   指示は文字列テンプレートであり、`{var}`構文を使用して動的な値を指示に挿入できます。
*   `{var}`は、`var`という名前の状態変数の値を挿入するために使用されます。
*   `{artifact.var}`は、`var`という名前のアーティファクトのテキストコンテンツを挿入するために使用されます。
*   状態変数またはアーティファクトが存在しない場合、エージェントはエラーを発生させます。エラーを無視したい場合は、変数名の末尾に`?`を付けて`{var?}`のようにすることができます。

=== "Python"

    ```python
    # 例: 指示の追加
    capital_agent = LlmAgent(
        model="gemini-2.0-flash",
        name="capital_agent",
        description="与えられた国の首都に関するユーザーの質問に答えます。",
        instruction="""あなたは国の首都を提供するエージェントです。
    ユーザーが国の首都を尋ねたら:
    1. ユーザーのクエリから国名を特定します。
    2. `get_capital_city` ツールを使用して首都を見つけます。
    3. ユーザーに首都を明確に述べて応答します。
    クエリ例: 「{country}の首都は何ですか？」
    応答例: 「フランスの首都はパリです。」
    """,
        # tools は次に追加します
    )
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/agents/llm-agents/snippets/main.go:instruction"
    ```

=== "Java"

    ```java
    // 例: 指示の追加
    LlmAgent capitalAgent =
        LlmAgent.builder()
            .model("gemini-2.0-flash")
            .name("capital_agent")
            .description("与えられた国の首都に関するユーザーの質問に答えます。")
            .instruction(
                """
                あなたは国の首都を提供するエージェントです。
                ユーザーが国の首都を尋ねたら:
                1. ユーザーのクエリから国名を特定します。
                2. `get_capital_city` ツールを使用して首都を見つけます。
                3. ユーザーに首都を明確に述べて応答します。
                クエリ例: 「{country}の首都は何ですか？」
                応答例: 「フランスの首都はパリです。」
                """)
            // tools は次に追加します
            .build();
    ```

*（注：システムの*すべて*のエージェントに適用される指示については、ルートエージェントの`global_instruction`の使用を検討してください。詳細は[マルチエージェント](multi-agents.md)セクションで説明します。）*

## エージェントの装備：ツール (`tools`)

ツールは、`LlmAgent`にLLMに組み込まれた知識や推論能力を超える機能を与えます。ツールにより、エージェントは外部世界と対話したり、計算を実行したり、リアルタイムデータを取得したり、特定のアクションを実行したりできます。

*   **`tools` (任意):** エージェントが使用できるツールのリストを提供します。リストの各項目は、次のいずれかです：
    *   ネイティブ関数またはメソッド（`FunctionTool`としてラップ）。Python ADKはネイティブ関数を自動的に`FunctionTool`にラップしますが、Javaでは`FunctionTool.create(...)`を使用してメソッドを明示的にラップする必要があります。
    *   `BaseTool`を継承するクラスのインスタンス。
    *   別のエージェントのインスタンス（`AgentTool`、エージェント間の委任を可能にする - [マルチエージェント](multi-agents.md)参照）。

LLMは、関数/ツール名、説明（docstringや`description`フィールドから）、およびパラメータスキーマを使用して、会話と指示に基づいてどのツールを呼び出すかを決定します。

=== "Python"

    ```python
    # ツール関数を定義
    def get_capital_city(country: str) -> str:
      """指定された国の首都を取得します。"""
      # 実際のロジックに置き換えてください (例: API呼び出し, データベース検索)
      capitals = {"france": "Paris", "japan": "Tokyo", "canada": "Ottawa"}
      return capitals.get(country.lower(), f"申し訳ありませんが、{country}の首都はわかりません。")
    
    # エージェントにツールを追加
    capital_agent = LlmAgent(
        model="gemini-2.0-flash",
        name="capital_agent",
        description="与えられた国の首都に関するユーザーの質問に答えます。",
        instruction="""あなたは国の首都を提供するエージェントです... (前の指示テキスト)""",
        tools=[get_capital_city] # 関数を直接提供
    )
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/agents/llm-agents/snippets/main.go:tool_example"
    ```

=== "Java"

    ```java
    
    // ツール関数を定義
    // 指定された国の首都を取得します。
    public static Map<String, Object> getCapitalCity(
            @Schema(name = "country", description = "首都を取得する国")
            String country) {
      // 実際のロジックに置き換えてください (例: API呼び出し, データベース検索)
      Map<String, String> countryCapitals = new HashMap<>();
      countryCapitals.put("canada", "Ottawa");
      countryCapitals.put("france", "Paris");
      countryCapitals.put("japan", "Tokyo");
    
      String result =
              countryCapitals.getOrDefault(
                      country.toLowerCase(), "申し訳ありませんが、" + country + "の首都は見つかりませんでした。");
      return Map.of("result", result); // ツールはMapを返す必要があります
    }
    
    // エージェントにツールを追加
    FunctionTool capitalTool = FunctionTool.create(experiment.getClass(), "getCapitalCity");
    LlmAgent capitalAgent =
        LlmAgent.builder()
            .model("gemini-2.0-flash")
            .name("capital_agent")
            .description("与えられた国の首都に関するユーザーの質問に答えます。")
            .instruction("あなたは国の首都を提供するエージェントです... (前の指示テキスト)")
            .tools(capitalTool) // FunctionToolとしてラップされた関数を提供
            .build();
    ```

ツールについての詳細は、[ツール](../tools/index.md)セクションをご覧ください。

## 高度な設定と制御

主要なパラメータに加えて、`LlmAgent`はより詳細な制御のためのいくつかのオプションを提供します。

### LLM生成の設定 (`generate_content_config`) {#fine-tuning-llm-generation-generate_content_config}

`generate_content_config`を使用して、基盤となるLLMが応答を生成する方法を調整できます。

*   **`generate_content_config` (任意):** [`google.genai.types.GenerateContentConfig`](https://googleapis.github.io/python-genai/genai.html#genai.types.GenerateContentConfig)のインスタンスを渡して、`temperature`（ランダム性）、`max_output_tokens`（応答の長さ）、`top_p`、`top_k`、およびセーフティセッティングなどのパラメータを制御します。

=== "Python"

    ```python
    from google.genai import types

    agent = LlmAgent(
        # ... その他のパラメータ
        generate_content_config=types.GenerateContentConfig(
            temperature=0.2, # より決定論的な出力
            max_output_tokens=250,
            safety_settings=[
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                    threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                )
            ]
        )
    )
    ```

=== "Go"

    ```go
    import "google.golang.org/genai"

    --8<-- "examples/go/snippets/agents/llm-agents/snippets/main.go:gen_config"
    ```

=== "Java"

    ```java
    import com.google.genai.types.GenerateContentConfig;

    LlmAgent agent =
        LlmAgent.builder()
            // ... その他のパラメータ
            .generateContentConfig(GenerateContentConfig.builder()
                .temperature(0.2F) // より決定論的な出力
                .maxOutputTokens(250)
                .build())
            .build();
    ```

### データの構造化 (`input_schema`, `output_schema`, `output_key`)

`LLM Agent`との構造化されたデータ交換を必要とするシナリオのために、ADKはスキーマ定義を使用して期待される入力と望ましい出力フォーマットを定義するメカニズムを提供します。

*   **`input_schema` (任意):** 期待される入力構造を表すスキーマを定義します。設定されている場合、このエージェントに渡されるユーザーメッセージの内容は、このスキーマに準拠したJSON文字列でなければなりません。あなたの指示は、ユーザーまたは先行するエージェントをそれに従ってガイドする必要があります。

*   **`output_schema` (任意):** 望ましい出力構造を表すスキーマを定義します。設定されている場合、エージェントの最終応答は、このスキーマに準拠したJSON文字列でなければなりません。

*   **`output_key` (任意):** 文字列キーを提供します。設定されている場合、エージェントの*最終*応答のテキスト内容は、このキーの下でセッションの状態辞書に自動的に保存されます。これは、エージェント間やワークフローのステップ間で結果を渡すのに便利です。
    *   Pythonでは、`session.state[output_key] = agent_response_text`のようになります。
    *   Javaでは、`session.state().put(outputKey, agentResponseText)`です。
    *   Golangでは、コールバックハンドラ内で`ctx.State().Set(output_key, agentResponseText)`となります。

=== "Python"

    入力および出力スキーマは、通常`Pydantic`のBaseModelです。

    ```python
    from pydantic import BaseModel, Field
    
    class CapitalOutput(BaseModel):
        capital: str = Field(description="その国の首都。")
    
    structured_capital_agent = LlmAgent(
        # ... name, model, description
        instruction="""あなたは首都情報エージェントです。国が与えられたら、首都を含むJSONオブジェクトのみで応答してください。フォーマット: {"capital": "capital_name"}""",
        output_schema=CapitalOutput, # JSON出力を強制
        output_key="found_capital"  # 結果を state['found_capital'] に保存
        # ここでは tools=[get_capital_city] を効果的に使用できない
    )
    ```

=== "Go"

    入力および出力スキーマは、`google.genai.types.Schema`オブジェクトです。

    ```go
    --8<-- "examples/go/snippets/agents/llm-agents/snippets/main.go:schema_example"
    ```

=== "Java"

     入力および出力スキーマは、`google.genai.types.Schema`オブジェクトです。

    ```java
    private static final Schema CAPITAL_OUTPUT =
        Schema.builder()
            .type("OBJECT")
            .description("首都情報のためのスキーマ。")
            .properties(
                Map.of(
                    "capital",
                    Schema.builder()
                        .type("STRING")
                        .description("その国の首都。")
                        .build()))
            .build();
    
    LlmAgent structuredCapitalAgent =
        LlmAgent.builder()
            // ... name, model, description
            .instruction(
                    "あなたは首都情報エージェントです。国が与えられたら、首都を含むJSONオブジェクトのみで応答してください。フォーマット: {\"capital\": \"capital_name\"}")
            .outputSchema(capitalOutput) // JSON出力を強制
            .outputKey("found_capital") // 結果を state.get("found_capital") に保存
            // ここでは tools(getCapitalCity) を効果的に使用できない
            .build();
    ```

### コンテキストの管理 (`include_contents`)

エージェントが以前の会話履歴を受け取るかどうかを制御します。

*   **`include_contents` (任意、デフォルト: `'default'`):** `contents`（履歴）がLLMに送信されるかどうかを決定します。
    *   `'default'`: エージェントは関連する会話履歴を受け取ります。
    *   `'none'`: エージェントは以前の`contents`を受け取りません。現在の指示と*現在*のターンで提供された入力のみに基づいて動作します（ステートレスなタスクや特定のコンテキストを強制する場合に便利です）。

=== "Python"

    ```python
    stateless_agent = LlmAgent(
        # ... その他のパラメータ
        include_contents='none'
    )
    ```

=== "Go"

    ```go
    import "google.golang.org/adk/agent/llmagent"

    --8<-- "examples/go/snippets/agents/llm-agents/snippets/main.go:include_contents"
    ```

=== "Java"

    ```java
    import com.google.adk.agents.LlmAgent.IncludeContents;
    
    LlmAgent statelessAgent =
        LlmAgent.builder()
            // ... その他のパラメータ
            .includeContents(IncludeContents.NONE)
            .build();
    ```

### プランナー

<div class="language-support-tag" title="">
   <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span>
</div>

**`planner` (任意):** `BasePlanner`インスタンスを割り当てて、実行前の複数ステップの推論と計画を有効にします。主なプランナーは2つあります：

*   **`BuiltInPlanner`:** モデルの組み込み計画機能（例: Geminiの思考機能）を活用します。詳細と例については、[Gemini Thinking](https://ai.google.dev/gemini-api/docs/thinking)を参照してください。

    ここで、`thinking_budget`パラメータは、応答を生成する際に使用する思考トークンの数をモデルにガイドします。`include_thoughts`パラメータは、モデルが応答に生の思考や内部の推論プロセスを含めるべきかどうかを制御します。

    ```python
    from google.adk import Agent
    from google.adk.planners import BuiltInPlanner
    from google.genai import types

    my_agent = Agent(
        model="gemini-2.5-flash",
        planner=BuiltInPlanner(
            thinking_config=types.ThinkingConfig(
                include_thoughts=True,
                thinking_budget=1024,
            )
        ),
        # ... ここにツールを記述
    )
    ```
    
*   **`PlanReActPlanner`:** このプランナーは、モデルに出力で特定の構造に従うように指示します：まず計画を立て、次に行動（ツールの呼び出しなど）を実行し、そのステップの推論を提供します。*特に、組み込みの「思考」機能を持たないモデルに役立ちます*。

    ```python
    from google.adk import Agent
    from google.adk.planners import PlanReActPlanner

    my_agent = Agent(
        model="gemini-2.0-flash",
        planner=PlanReActPlanner(),
        # ... ここにツールを記述
    )
    ```

    エージェントの応答は、構造化されたフォーマットに従います：

    ```
    [user]: ai news
    [google_search_agent]: /*PLANNING*/
    1. 人工知能に関する最新の更新とヘッドラインを得るために、「最新のAIニュース」でGoogle検索を実行する。
    2. 検索結果からの情報を統合して、最近のAIニュースの要約を提供する。

    /*ACTION*/
    /*REASONING*/
    検索結果は、企業の動向、研究のブレークスルー、応用など、さまざまな側面をカバーする最近のAIニュースの包括的な概要を提供しています。ユーザーの要求に答えるのに十分な情報があります。

    /*FINAL_ANSWER*/
    最近のAIニュースの要約はこちらです：
    ....
    ```

### コード実行

<div class="language-support-tag">
   <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span>
</div>

*   **`code_executor` (任意):** `BaseCodeExecutor`インスタンスを提供して、エージェントがLLMの応答で見つかったコードブロックを実行できるようにします。（[ツール/組み込みツール](../tools/built-in-tools.md)参照）。

組み込みプランナーの使用例：
```python
# (コメント省略、原文コードと同じ)
...
```

## まとめ：例

??? "コード"
    これが完全な基本的な`capital_agent`です：

    === "Python"
    
        ```python
        --8<-- "examples/python/snippets/agents/llm-agent/capital_agent.py"
        ```
    
    === "Go"

        ```go
        --8<-- "examples/go/snippets/agents/llm-agents/main.go:full_code"
        ```

    === "Java"
    
        ```java
        --8<-- "examples/java/snippets/src/main/java/agents/LlmAgentExample.java:full_code"
        ```

*（この例は基本的な概念を示しています。より複雑なエージェントは、スキーマ、コンテキスト制御、計画などを組み込むことがあります。）*

## 関連概念（後続のトピック）

このページでは`LlmAgent`の基本的な設定について説明しましたが、いくつかの関連概念はより高度な制御を提供し、他の場所で詳しく説明されています：

*   **コールバック:** `before_model_callback`、`after_model_callback`などを使用して、実行ポイント（モデル呼び出しの前後、ツール呼び出しの前後）をインターセプトします。[コールバック](../callbacks/types-of-callbacks.md)を参照してください。
*   **マルチエージェント制御:** 計画（`planner`）、エージェント転送の制御（`disallow_transfer_to_parent`, `disallow_transfer_to_peers`）、およびシステム全体の指示（`global_instruction`）を含む、エージェント対話の高度な戦略。[マルチエージェント](multi-agents.md)を参照してください。