# LLMエージェント

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">Typescript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span><span class="lst-kotlin">Kotlin v0.1.0</span>
</div>

`LlmAgent`（しばしば`Agent`と略されます）はADKにおけるコアコンポーネントであり、アプリケーションの「思考」部分として機能します。大規模言語モデル（LLM）の能力を活用して、推論、自然言語の理解、意思決定、応答の生成、ツールとの対話を行います。

事前に定義された実行パスに従う決定論的な[ワークフローエージェント](workflow-agents/index.md)とは異なり、`LlmAgent`の振る舞いは非決定的です。LLMを使用して指示とコンテキストを解釈し、動的に処理方法を決定したり、どのツールを使用するか（もし使用する場合）、あるいは他のエージェントに制御を移すかを判断します。

効果的な`LlmAgent`を構築するには、そのアイデンティティを定義し、指示を通じてその振る舞いを明確にガイドし、必要なツールと能力を備えさせることが含まれます。

## エージェントのアイデンティティと目的の定義

まず、エージェントが*何であるか*、そして*何のためにあるのか*を確立する必要があります。

*   **`name` (必須):** 全てのエージェントには一意の文字列識別子が必要です。この`name`は内部操作、特にエージェント同士が互いを参照したりタスクを委任したりする必要があるマルチエージェントシステムにおいて非常に重要です。エージェントの機能を反映した説明的な名前（例: `customer_support_router`, `billing_inquiry_agent`）を選択してください。Pythonでは、名前は有効なPython識別子である必要があり、ADKは予約名の`user`を拒否します。

*   **`description` (任意、マルチエージェントで推奨):** エージェントの能力に関する簡潔な要約を提供します。この説明は主に、*他の*LLMエージェントがこのエージェントにタスクをルーティングすべきかどうかを判断するために使用されます。同僚と区別できるように、具体的に記述してください（例: 「請求エージェント」ではなく、「現在の請求書に関する問い合わせを処理します」）。

*   **`model` (Pythonでは任意):** このエージェントの推論を支える基盤となるLLMを指定します。これは`"gemini-flash-latest"`のような文字列識別子、または`BaseLlm`インスタンスのいずれかです。`model`を省略すると、エージェントは`SequentialAgent`、`ParallelAgent`、`LoopAgent`、カスタム`BaseAgent`など、`LlmAgent`ではない親をスキップして、最も近い`LlmAgent`の祖先のモデルを継承します。どの祖先もモデルを設定していない場合、エージェントは[デフォルトモデルの設定](#configure-a-default-model)で説明されている組み込みのデフォルトモデルにフォールバックします。モデルの選択は、エージェントの能力、コスト、パフォーマンスに影響します。利用可能なオプションと考慮事項については、[モデル](/ja/agents/models/)ページを参照してください。

=== "Python"

    ```python
    # 例: 基本的なアイデンティティの定義
    capital_agent = LlmAgent(
        model="gemini-flash-latest",
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
            .model("gemini-flash-latest")
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
*   状態変数またはアーティファクトが存在しない場合、エージェントはエラーを発生させます。エラーを無視したい場合は、変数名の末尾に`?`を付けて`{var?}`のようにできます。

=== "Python"

    ```python
    # 例: 指示の追加
    capital_agent = LlmAgent(
        model="gemini-flash-latest",
        name="capital_agent",
        description="与えられた国の首都に関するユーザーの質問に答えます。",
        instruction="""あなたは国の首都を提供するエージェントです。
    ユーザーが国の首都を尋ねたら:
    1. ユーザーのクエリから国名を特定します。
    2. `get_capital_city` ツールを使用して首都を見つけます。
    3. ユーザーに首都を明確に述べて応答します。
    クエリ例: 「フランスの首都は何ですか？」
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
            .model("gemini-flash-latest")
            .name("capital_agent")
            .description("与えられた国の首都に関するユーザーの質問に答えます。")
            .instruction(
                """
                あなたは国の首都を提供するエージェントです。
                ユーザーが国の首都を尋ねたら:
                1. ユーザーのクエリから国名を特定します。
                2. `get_capital_city` ツールを使用して首都を見つけます。
                3. ユーザーに首都を明確に述べて応答します。
                クエリ例: 「フランスの首都は何ですか？」
                応答例: 「フランスの首都はパリです。」
                """)
            // tools は次に追加します
            .build();
    ```

Python で Model Context Protocol（MCP）サーバーからエージェントの指示を動的に取得するには、[`McpInstructionProvider` による動的な指示](/ja/tools-custom/mcp-tools/advanced/#dynamic-instructions-with-mcpinstructionprovider)を参照してください。

!!! note "GlobalInstructionPlugin"

    システム内の*すべて*のエージェントに共通のルールや一貫したペルソナを適用するには、非推奨となった `global_instruction` パラメータの代わりに `GlobalInstructionPlugin` を使用してください。
    ADK Go の場合は、`llmagent.Config` で `GlobalInstruction` または `GlobalInstructionProvider` を設定してください。

## エージェントの装備：ツール (`tools`)

ツールは、`LlmAgent`にLLMに組み込まれた知識や推論能力を超える機能を与えます。ツールにより、エージェントは外部世界と対話したり、計算を実行したり、リアルタイムデータを取得したり、特定のアクションを実行したりできます。

*   **`tools` (任意):** エージェントが使用できるツールのリストを提供します。リストの各項目は、次のいずれかです：
    *   ネイティブ関数またはメソッド（`FunctionTool`としてラップ）。Python ADKはネイティブ関数を自動的に`FunctionTool`にラップしますが、Javaでは`FunctionTool.create(...)`を使用してメソッドを明示的にラップする必要があります。
    *   `BaseTool`を継承するクラスのインスタンス。
    *   別のエージェントをラップしてエージェント間の委任を可能にする`AgentTool`。詳細については、[カスタムエージェントワークフロー](/ja/agents/custom-agents/#delegation)を参照してください。Pythonでは、`AgentTool(agent=...)`構文を直接使用する代わりに、エージェントに`mode='single_turn'`を設定して`sub_agents`に追加し、インラインツールとして自動的に公開する方法が推奨されます。

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
        model="gemini-flash-latest",
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
            .model("gemini-flash-latest")
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

*   **`generate_content_config` (任意):** [`google.genai.types.GenerateContentConfig`](https://googleapis.github.io/python-genai/genai.html#genai.types.GenerateContentConfig)のインスタンスを渡して、`temperature`（ランダム性）、`max_output_tokens`（応答の長さ）、`top_p`、`top_k`、およびセーフティセッティングなどのパラメータを制御します。Pythonでは、`generate_content_config`に`tools`、`system_instruction`、`response_schema`、または`http_options.base_url`を設定すると、ADKは`ValueError`を送出します。最初の3つは代わりにエージェントの`tools`、`instruction`、`output_schema`フィールドを通じて設定し、ベースURLはモデルまたはそのクライアントに設定してください。

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

=== "TypeScript"

    ```typescript
    import { GenerateContentConfig } from '@google/genai';

    const generateContentConfig: GenerateContentConfig = {
        temperature: 0.2, // より決定論的な出力
        maxOutputTokens: 250,
    };

    const agent = new LlmAgent({
        // ... other params
        generateContentConfig,
    });
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

### デフォルトモデルの設定 {#configure-a-default-model}

<div class="language-support-tag" title="">
   <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.22.0</span>
</div>

`set_default_model`クラスメソッドを使用して、すべての`LlmAgent`インスタンスに対してシステム全体のデフォルトモデルを設定できます。エージェントの作成時にモデルを指定しない場合、ADKの組み込みのデフォルトモデルにフォールバックします。この設定により、重複するモデル指定を省き、すべてのエージェントのモデルを一度に簡単に変更できます。

=== "Python"

    ```python
    from google.adk.agents import LlmAgent

    # すべてのエージェントに新しいデフォルトモデルを設定
    LlmAgent.set_default_model("gemini-flash-latest")

    # このエージェントはデフォルトで "gemini-flash-latest" を使用します
    agent_with_default_model = LlmAgent(
        name="default_model_agent",
        instruction="あなたは親切なアシスタントです。"
    )

    # 特定のエージェントに対してデフォルトを上書きすることも可能です
    specific_agent = LlmAgent(
        name="specific_model_agent",
        model="gemini-pro-latest",
        instruction="あなたは創造的な作家です。"
    )
    ```

### データの構造化 (`input_schema`, `output_schema`, `output_key`) {#data-handling}

`LLM Agent`との構造化されたデータ交換を必要とするシナリオのために、ADKはスキーマ定義を使用して期待される入力と望ましい出力フォーマットを定義するメカニズムを提供します。

*   **`input_schema` (任意):** このエージェントが*ツールとして*呼び出されたときに期待される入力構造を表すスキーマを定義します。Pythonでは、`AgentTool`が呼び出し元エージェントの引数をスキーマに照らして検証し、その結果をこのエージェントの入力として渡します。このスキーマは、エージェントに直接送信されるユーザーメッセージには適用されません。

*   **`output_schema` (任意):** 望ましい出力構造を表すスキーマを定義します。設定されている場合、エージェントの最終応答は、このスキーマに準拠したJSON文字列でなければなりません。
    *   Python でサポートされているスキーマタイプは次のとおりです。
        *   Pydantic モデルクラス（例: `MySchema`）
        *   プリミティブのリスト（例: `list[str]`, `list[int]`, `list[bool]`, `list[float]`）
        *   `dict`
        *   `google.genai.types.Schema`

!!! note "`output_schema` と `tools` の併用"

    Pythonでは、ADKは同じエージェント上での`output_schema`と`tools`の併用をサポートしています。エージェントの動作中はツールを引き続き利用でき、スキーマは最終応答にのみ適用されます。Google Cloud上のGeminiモデルや、レスポンススキーマをサポートするプロバイダの`LiteLlm`モデルなど、一部のモデルは1回のリクエストで両方を受け入れるため、ADKはそれらをそのまま渡します。それ以外のモデルでは、ADKは[`set_model_response` 関数ツール](https://github.com/google/adk-python/blob/main/src/google/adk/tools/set_model_response_tool.py)を追加し、そのツールを通じて最終回答を返すようにモデルに指示しますが、安定して動作しない場合があります。そのような場合は、出力フォーマットを別途処理するサブエージェントの利用を検討してください。

*   **`output_key` (任意):** 文字列キーを提供します。設定されている場合、エージェントの*最終*応答が、このキーの下でセッションの状態辞書に自動的に保存されます。これは、エージェント間やワークフローのステップ間で結果を渡すのに便利です。
    *   Pythonでは、`session.state[output_key] = agent_response_text`のようになります。`output_schema`も設定されている場合、ADKはまず応答をスキーマに照らしてパースし、応答テキストの代わりにパースされた値を保存します。`BaseModel`スキーマは`dict`として保存され、`list[BaseModel]`スキーマは`list[dict]`として保存されます。
    *   Javaでは、`session.state().put(outputKey, agentResponseText)`です。
    *   Golangでは、コールバックハンドラ内で`ctx.State().Set(output_key, agentResponseText)`となります。

    JavaおよびKotlinでは、`output_schema`も設定されている場合、テキストの代わりに*パースされた*応答が`Map`として保存されます。

!!! note "Java および Kotlin でのスキーマ検証"

    Java および Kotlin は、スキーマの*構造*（`type`、`required`、`nullable`、`anyOf`、`items`）に照らして応答を検証します（[`SchemaUtils`](https://github.com/google/adk-kotlin/blob/v1.0.0/core/src/commonMain/kotlin/com/google/adk/kt/SchemaUtils.kt) を参照）。
    `pattern`、`minLength`、`minimum` などの制約フィールドはスキーマの一部としてモデルに送信されますが、ADK がそれらを再検証することはなく、従うかどうかはモデルに委ねられます。Python は、宣言された制約を強制する Pydantic モデルに対して検証を行います。

    Java および Kotlin は最上位のオブジェクト スキーマのみを受け入れ、最上位の配列やプリミティブは検証に失敗します。Python はリストおよびプリミティブの出力スキーマもサポートしています。

    応答の検証に失敗した場合、ADK はエラーをログに記録し、パースされたオブジェクトの代わりに生の応答文字列を `output_key` の下に保存します（[`LlmAgent`](https://github.com/google/adk-kotlin/blob/v1.0.0/core/src/commonMain/kotlin/com/google/adk/kt/agents/LlmAgent.kt) を参照）。

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
        # tools=[...] は output_schema と併用可能です。上記の注記を参照してください
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
            .outputSchema(CAPITAL_OUTPUT) // JSON出力を強制
            .outputKey("found_capital") // 結果を state.get("found_capital") に保存
            // ここでは tools(getCapitalCity) を効果的に使用できない
            .build();
    ```

=== "Kotlin"

    入力および出力スキーマは、GenAI SDK の同名型ではなく、ADK 独自の `com.google.adk.kt.types.Schema` です。ADK Kotlin v0.8.0 以降、JSON スキーマには `pattern`、`minLength`、`maxLength`、`minimum`、`maximum`、`minItems`、`maxItems`、`format`、`nullable`、`default`、`anyOf`、`title` の各フィールドに対する制約が含まれます。

    ```kotlin
    --8<-- "examples/kotlin/snippets/agents/llm-agent/CapitalAgent.kt:schema_example"
    ```

    `format` フィールドは、モデルがそのフィールドの型に対して許可する値のみを受け入れます。許可される値については、Gemini [`Schema` リファレンス](https://ai.google.dev/api/caching#Schema) を参照してください。

    `default` フィールドには JSON ネイティブ値を含める必要があります。ADK 独自の `Json` はこれをシリアライズしますが、コンテキストに応じた `Any` シリアライザーを持たないカスタム シリアライザーではシリアライズできません。

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
    import "google.golang.org/adk/v2/agent/llmagent"

    --8<-- "examples/go/snippets/agents/llm-agents/snippets/main.go:include_contents"
    ```

    ワークフロー ノードのように `ModeSingleTurn` ノードとして実行されるエージェントは、`IncludeContents` が `IncludeContentsNone` であるかのように現在のターンのみを参照します。ADK Go v2.4.0 以降では、`IncludeContents` を明示的に `llmagent.IncludeContentsDefault` に設定することで会話履歴を保持できます。それ以前のバージョンでは、シングルターン ノードに対するこの設定は無視されます。

=== "Java"

    ```java
    import com.google.adk.agents.LlmAgent.IncludeContents;
    
    LlmAgent statelessAgent =
        LlmAgent.builder()
            // ... その他のパラメータ
            .includeContents(IncludeContents.NONE)
            .build();
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/agents/llm-agent/CapitalAgent.kt:include_contents"
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
        name="my_agent",
        model="gemini-flash-latest",
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
        name="my_agent",
        model="gemini-flash-latest",
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

組み込みプランナーの使用例：

```python
from dotenv import load_dotenv


import asyncio
import os

from google.genai import types
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService # Optional
from google.adk.planners import BasePlanner, BuiltInPlanner, PlanReActPlanner
from google.adk.models import LlmRequest

from google.genai.types import ThinkingConfig
from google.genai.types import GenerateContentConfig

import datetime
from zoneinfo import ZoneInfo

APP_NAME = "weather_app"
USER_ID = "1234"
SESSION_ID = "session1234"

def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city for which to retrieve the weather report.

    Returns:
        dict: status and result or error msg.
    """
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": (
                "The weather in New York is sunny with a temperature of 25 degrees"
                " Celsius (77 degrees Fahrenheit)."
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available.",
        }


def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city.

    Args:
        city (str): The name of the city for which to retrieve the current time.

    Returns:
        dict: status and result or error msg.
    """

    if city.lower() == "new york":
        tz_identifier = "America/New_York"
    else:
        return {
            "status": "error",
            "error_message": (
                f"Sorry, I don't have timezone information for {city}."
            ),
        }

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    report = (
        f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
    )
    return {"status": "success", "report": report}

# Step 1: Create a ThinkingConfig
thinking_config = ThinkingConfig(
    include_thoughts=True,   # Ask the model to include its thoughts in the response
    thinking_budget=256      # Limit the 'thinking' to 256 tokens (adjust as needed)
)
print("ThinkingConfig:", thinking_config)

# Step 2: Instantiate BuiltInPlanner
planner = BuiltInPlanner(
    thinking_config=thinking_config
)
print("BuiltInPlanner created.")

# Step 3: Wrap the planner in an LlmAgent
agent = LlmAgent(
    model="gemini-flash-latest",  # Set your model name
    name="weather_and_time_agent",
    instruction="You are an agent that returns time and weather",
    planner=planner,
    tools=[get_weather, get_current_time]
)

# Session and Runner
session_service = InMemorySessionService()
session = asyncio.run(
    session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
)
runner = Runner(agent=agent, app_name=APP_NAME, session_service=session_service)

# Agent Interaction
def call_agent(query):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    for event in events:
        print(f"\nDEBUG EVENT: {event}\n")
        if event.is_final_response() and event.content and event.content.parts:
            final_answer = event.content.parts[0].text.strip()
            print("\n🟢 FINAL ANSWER\n", final_answer, "\n")

call_agent("If it's raining in New York right now, what is the current temperature?")
```

### コード実行

<div class="language-support-tag">
   <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

*   **`code_executor` (任意):** `BaseCodeExecutor`インスタンスを提供して、エージェントがLLMの応答で見つかったコードブロックを実行できるようにします。（[ツール/組み込みツール](../tools/built-in-tools.md)参照）。

## まとめ：例

??? "コード"
    これが完全な基本的な`capital_agent`です：

    === "Python"
    
        ```python
        --8<-- "examples/python/snippets/agents/llm-agent/capital_agent.py"
        ```

    === "TypeScript"

        ```typescript
        --8<-- "examples/typescript/snippets/agents/llm-agent/capital_agent.ts"
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
*   **マルチエージェント制御:** 計画（`planner`）、エージェント転送の制御（`disallow_transfer_to_parent`, `disallow_transfer_to_peers`）、およびアプリ内のすべてのエージェントに対する一貫したアイデンティティとルール（`GlobalInstructionPlugin`、または Go の `GlobalInstruction`）を含む、エージェント対話の高度な戦略。[マルチエージェント](../workflows/patterns.md)を参照してください。

## Kotlin の例の補足

英語原文に追加された Kotlin の `LlmAgent` 例を以下にも掲載します。

### 基本的な識別情報

```kotlin
--8<-- "examples/kotlin/snippets/agents/llm-agent/CapitalAgent.kt:identity"
```

### 指示文の構成

```kotlin
--8<-- "examples/kotlin/snippets/agents/llm-agent/CapitalAgent.kt:instruction"
```

### ツール定義

```kotlin
--8<-- "examples/kotlin/snippets/agents/llm-agent/CapitalAgent.kt:tool_definition"
```

### ツールの使用

```kotlin
--8<-- "examples/kotlin/snippets/agents/llm-agent/CapitalAgent.kt:tool_usage"
```

### 生成設定

```kotlin
--8<-- "examples/kotlin/snippets/agents/llm-agent/CapitalAgent.kt:gen_config"
```

### 完全な例

```kotlin
--8<-- "examples/kotlin/snippets/agents/llm-agent/CapitalAgent.kt:full_example"
```

## コード実行例の補足

英語原文に含まれているコード実行例を以下にも掲載します。

### Python

```python
--8<-- "examples/python/snippets/tools/built-in-tools/code_execution.py"
```

### Java

```java
--8<-- "examples/java/snippets/src/main/java/tools/CodeExecutionAgentApp.java:full_code"
```
