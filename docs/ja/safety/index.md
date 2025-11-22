# AIエージェントの安全性とセキュリティ

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span><span class="lst-go">Go</span><span class="lst-java">Java</span>
</div>

AIエージェントの能力が向上するにつれて、それらが安全かつセキュアに動作し、ブランド価値と一致することを保証することが最も重要です。制御されていないエージェントは、データ漏洩のような意図と異なる、または有害なアクションの実行や、ブランドの評判に影響を与えかねない不適切なコンテンツの生成など、リスクをもたらす可能性があります。**リスクの原因には、曖昧な指示、モデルのハルシネーション、敵対的なユーザーによるジェイルブレイクやプロンプトインジェクション、ツールの使用を介した間接的なプロンプトインジェクションなどがあります。**

[Google Cloud Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/overview)は、これらのリスクを軽減するための多層的なアプローチを提供し、強力で信頼性の高いエージェントの構築を可能にします。エージェントが明示的に許可したアクションのみを実行するように、厳格な境界線を設定するためのいくつかのメカニズムを提供します。

1. **IDと認可**: エージェントとユーザーの認証を定義することで、エージェントが**誰として振る舞うか**を制御します。
2. **入出力をスクリーニングするガードレール**: モデルとツールの呼び出しを正確に制御します。

    * *ツール内ガードレール:* 開発者が設定したツールコンテキストを使用してポリシーを強制するなど、防御的にツールを設計します（例：特定のテーブルへのクエリのみを許可）。
    * *Gemini組み込みの安全機能:* Geminiモデルを使用する場合、有害な出力をブロックするコンテンツフィルタや、モデルの振る舞いと安全ガイドラインを導くシステムインストラクションの恩恵を受けられます。
    * *コールバックとプラグイン:* 実行前または実行後にモデルとツールの呼び出しを検証し、パラメータをエージェントの状態や外部ポリシーと照合します。
    * *安全ガードレールとしてのGeminiの利用:* コールバックを介して設定された安価で高速なモデル（Gemini Flash Liteなど）を使用して入出力をスクリーニングする追加の安全層を実装します。

3. **サンドボックス化されたコード実行**: モデルが生成したコードがセキュリティ問題を引き起こさないように、環境をサンドボックス化して防ぎます。
4. **評価とトレース**: 評価ツールを使用して、エージェントの最終出力の品質、関連性、正確性を評価します。トレースを使用してエージェントのアクションを可視化し、ツールの選択、戦略、アプローチの効率性など、エージェントが解決策に到達するまでのステップを分析します。
5. **ネットワーク制御とVPC-SC**: データ漏洩を防ぎ、潜在的な影響範囲を制限するために、エージェントの活動を安全な境界（VPCサービスコントロールなど）内に閉じ込めます。

## 安全性とセキュリティのリスク

安全対策を実装する前に、エージェントの能力、ドメイン、およびデプロイメントコンテキストに特化した徹底的なリスク評価を実施してください。

**リスクの源泉**には以下が含まれます：

* 曖昧なエージェントの指示
* 敵対的なユーザーによるプロンプトインジェクションやジェイルブレイクの試み
* ツールの使用を通じた間接的なプロンプトインジェクション

**リスクのカテゴリ**には以下が含まれます：

* **意図との不一致と目標の破損**
    * 有害な結果につながる意図しない目標や代理目標の追求（「報酬ハッキング」）
    * 複雑または曖昧な指示の誤解釈
* **ブランドセーフティを含む有害なコンテンツの生成**
    * 有毒、憎悪的、偏見のある、性的に露骨な、差別的、または違法なコンテンツの生成
    * ブランド価値に反する言葉の使用や、話題から外れた会話などのブランドセーフティリスク
* **安全でないアクション**
    * システムに損害を与えるコマンドの実行
    * 未承認の購入や金融取引の実行
    * 機密性の高い個人データ（PII）の漏洩
    * データ漏洩

## ベストプラクティス

### IDと認可

*ツール*が外部システムでアクションを実行するために使用するIDは、セキュリティの観点から重要な設計上の考慮事項です。同じエージェント内の異なるツールは、異なる戦略で構成できるため、エージェントの構成について話す際には注意が必要です。

#### エージェント認証 (Agent-Auth)

**ツールはエージェント自身のID**（例：サービスアカウント）を使用して外部システムと対話します。エージェントのIDは、データベースのIAMポリシーにエージェントのサービスアカウントを読み取りアクセスとして追加するなど、外部システムのアクセスポリシーで明示的に認可される必要があります。このようなポリシーは、エージェントが開発者が意図した可能なアクションのみを実行するように制約します。リソースに読み取り専用の権限を与えることで、モデルが何を決定しようとも、ツールは書き込みアクションを実行することが禁止されます。

このアプローチは実装が簡単であり、**すべてのユーザーが同じレベルのアクセスを共有するエージェントに適しています。** すべてのユーザーが同じアクセスレベルを持たない場合、このアプローチだけでは十分な保護を提供できず、以下の他の技術で補完する必要があります。ツールの実装では、すべてのエージェントのアクションがエージェントから来ているように見えるため、ユーザーへのアクションの帰属を維持するためにログが作成されるようにしてください。

#### ユーザー認証 (User Auth)

ツールは、**「制御しているユーザー」のID**（例：Webアプリケーションのフロントエンドと対話している人間）を使用して外部システムと対話します。ADKでは、これは通常OAuthを使用して実装されます。エージェントはフロントエンドと対話してOAuthトークンを取得し、ツールはそのトークンを使用して外部アクションを実行します。外部システムは、制御しているユーザー自身がそのアクションを実行する権限を持っている場合にのみ、アクションを認可します。

ユーザー認証には、エージェントがユーザー自身が実行できたアクションしか実行しないという利点があります。これにより、悪意のあるユーザーがエージェントを悪用して追加のデータへのアクセスを得るリスクが大幅に減少します。ただし、最も一般的な委任の実装では、委任する権限のセット（つまり、OAuthスコープ）が固定されています。多くの場合、これらのスコープはエージェントが実際に必要とするアクセスよりも広いため、エージェントのアクションをさらに制約するために以下の技術が必要です。

### 入出力をスクリーニングするガードレール

#### ツール内ガードレール

ツールはセキュリティを念頭に置いて設計することができます。モデルに実行させたいアクションだけを公開し、それ以外のものは何も公開しないツールを作成できます。エージェントに提供するアクションの範囲を制限することで、エージェントに決して実行させたくない不正なアクションのクラスを決定論的に排除できます。

ツール内ガードレールは、開発者が各ツールインスタンスに制限を設定するために使用できる決定論的な制御を公開する、共通で再利用可能なツールを作成するためのアプローチです。

このアプローチは、ツールが2種類の入力を受け取るという事実に基づいています。モデルによって設定される引数（arguments）と、エージェント開発者によって決定論的に設定できる[**`ツールコンテキスト(Tool Context)`**](../tools/index.md#tool-context)です。モデルが期待どおりに振る舞っているかを検証するために、決定論的に設定された情報に依存することができます。

たとえば、クエリツールは、ツールコンテキストからポリシーを読み取ることを期待するように設計できます。

=== "Python"

    ```py
    # 概念的な例：ツールコンテキスト向けのポリシーデータを設定
    # 実際のADKアプリでは、これはInvocationContext.session.stateに設定されるか、
    # ツールの初期化時に渡され、ToolContextを介して取得される可能性があります。

    policy = {} # policyが辞書であると仮定
    policy['select_only'] = True
    policy['tables'] = ['mytable1', 'mytable2']

    # 概念的：後でToolContextを介してツールがアクセスできる場所にポリシーを保存する。
    # この特定の行は、実際には異なる見た目になる可能性があります。
    # 例：セッション状態に保存する
    invocation_context.session.state["query_tool_policy"] = policy

    # または、ツールの初期化時に渡す
    query_tool = QueryTool(policy=policy)
    # この例では、アクセス可能な場所に保存されると仮定します。
    ```

=== "Go"

    ```go
    // 概念的な例：ツールコンテキスト向けのポリシーデータを設定
    // 実際のADKアプリでは、セッション状態サービスを使用して設定される可能性があります。
    // `ctx`はコールバックまたはカスタムエージェントで利用可能な`agent.Context`です。

    policy := map[string]interface{}{
    	"select_only": true,
    	"tables":      []string{"mytable1", "mytable2"},
    }

    // 概念的：後でToolContextを介してツールがアクセスできる場所にポリシーを保存する。
    // この特定の行は、実際には異なる見た目になる可能性があります。
    // 例：セッション状態に保存する
    if err := ctx.Session().State().Set("query_tool_policy", policy); err != nil {
        // エラーを処理する、例：ログに記録する。
    }

    // または、ツールの初期化時に渡す
    // queryTool := NewQueryTool(policy)
    // この例では、アクセス可能な場所に保存されると仮定します。
    ```

=== "Java"

    ```java
    // 概念的な例：ツールコンテキスト向けのポリシーデータを設定
    // 実際のADKアプリでは、これはInvocationContext.session.stateに設定されるか、
    // ツールの初期化時に渡され、ToolContextを介して取得される可能性があります。

    policy = new HashMap<String, Object>(); // policyがMapであると仮定
    policy.put("select_only", true);
    policy.put("tables", new ArrayList<>("mytable1", "mytable2"));

    // 概念的：後でToolContextを介してツールがアクセスできる場所にポリシーを保存する。
    // この特定の行は、実際には異なる見た目になる可能性があります。
    // 例：セッション状態に保存する
    invocationContext.session().state().put("query_tool_policy", policy);

    // または、ツールの初期化時に渡す
    query_tool = QueryTool(policy);
    // この例では、アクセス可能な場所に保存されると仮定します。
    ```

ツールの実行中、[**`ツールコンテキスト(Tool Context)`**](../tools/index.md#tool-context)がツールに渡されます：

=== "Python"

    ```py
    def query(query: str, tool_context: ToolContext) -> str | dict:
      # 'policy'がコンテキストから取得されると仮定する。例：セッション状態経由
      # policy = tool_context.invocation_context.session.state.get('query_tool_policy', {})

      # --- プレースホルダーのポリシー施行 ---
      policy = tool_context.invocation_context.session.state.get('query_tool_policy', {}) # 取得例
      actual_tables = explainQuery(query) # 仮の関数呼び出し

      if not set(actual_tables).issubset(set(policy.get('tables', []))):
        # モデルにエラーメッセージを返す
        allowed = ", ".join(policy.get('tables', ['(未定義)']))
        return f"エラー：クエリが認可されていないテーブルを対象としています。許可されているテーブル：{allowed}"

      if policy.get('select_only', False):
           if not query.strip().upper().startswith("SELECT"):
               return "エラー：ポリシーはクエリをSELECT文のみに制限します。"
      # --- ポリシー施行終了 ---

      print(f"検証済みクエリを実行（仮）：{query}")
      return {"status": "success", "results": [...]} # 成功時の戻り値の例
    ```

=== "Go"

    ```go
    import (
    	"fmt"
    	"strings"

    	"google.golang.org/adk/tool"
    )

    func query(query string, toolContext *tool.Context) (any, error) {
    	// 'policy'がコンテキストから取得されると仮定する。例：セッション状態経由
    	policyAny, err := toolContext.State().Get("query_tool_policy")
    	if err != nil {
    		return nil, fmt.Errorf("ポリシーを取得できませんでした： %w", err)
    	}    	policy, _ := policyAny.(map[string]interface{})
    	actualTables := explainQuery(query) // 仮の関数呼び出し

    	// --- プレースホルダーのポリシー施行 ---
    	if tables, ok := policy["tables"].([]string); ok {
    		if !isSubset(actualTables, tables) {
    			// 失敗を通知するためにエラーを返す
    			allowed := strings.Join(tables, ", ")
    			if allowed == "" {
    				allowed = "(未定義)"
    			}
    			return nil, fmt.Errorf("クエリが認可されていないテーブルを対象としています。許可されているテーブル：%s", allowed)
    		}
    	}

    	if selectOnly, _ := policy["select_only"].(bool); selectOnly {
    		if !strings.HasPrefix(strings.ToUpper(strings.TrimSpace(query)), "SELECT") {
    			return nil, fmt.Errorf("ポリシーはクエリをSELECT文のみに制限します")
    		}
    	}
    	// --- ポリシー施行終了 ---

    	fmt.Printf("検証済みクエリを実行（仮）：%s\n", query)
    	return map[string]interface{}{"status": "success", "results": []string{"..."}}, nil
    }

    // aがbのサブセットであるかを確認するヘルパー関数
    func isSubset(a, b []string) bool {
    	set := make(map[string]bool)
    	for _, item := range b {
    		set[item] = true
    	}
    	for _, item := range a {
    		if _, found := set[item]; !found {
    			return false
    		}
    	}
    	return true
    }
    ```

=== "Java"

    ```java
    import com.google.adk.tools.ToolContext;
    import java.util.*;

    class ToolContextQuery {

      public Object query(String query, ToolContext toolContext) {

        // 'policy'がコンテキストから取得されると仮定する。例：セッション状態経由
        Map<String, Object> queryToolPolicy =
            toolContext.invocationContext.session().state().getOrDefault("query_tool_policy", null);
        List<String> actualTables = explainQuery(query);

        // --- プレースホルダーのポリシー施行 ---
        if (!queryToolPolicy.get("tables").containsAll(actualTables)) {
          List<String> allowedPolicyTables =
              (List<String>) queryToolPolicy.getOrDefault("tables", new ArrayList<String>());

          String allowedTablesString =
              allowedPolicyTables.isEmpty() ? "(未定義)" : String.join(", ", allowedPolicyTables);

          return String.format(
              "エラー：クエリが認可されていないテーブルを対象としています。許可されているテーブル：%s", allowedTablesString);
        }

        if (!queryToolPolicy.get("select_only")) {
          if (!query.trim().toUpperCase().startswith("SELECT")) {
            return "エラー：ポリシーはクエリをSELECT文のみに制限します。";
          }
        }
        // --- ポリシー施行終了 ---

        System.out.printf("検証済みクエリを実行（仮）%s：", query);
        Map<String, Object> successResult = new HashMap<>();
        successResult.put("status", "success");
        successResult.put("results", Arrays.asList("result_item1", "result_item2"));
        return successResult;
      }
    }
    ```

#### Gemini組み込みの安全機能

Geminiモデルには、コンテンツとブランドの安全性を向上させるために活用できる組み込みの安全メカニズムが備わっています。

* **コンテンツ安全フィルター**: [コンテンツフィルター](https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/configure-safety-attributes)は、有害なコンテンツの出力をブロックするのに役立ちます。これらは、モデルをジェイルブレイクしようとする脅威アクターに対する多層防御の一部として、Geminiモデルから独立して機能します。Vertex AI上のGeminiモデルは、2種類のコンテンツフィルターを使用します：
* **設定不可能な安全フィルター**は、児童性的虐待素材（CSAM）や個人を特定できる情報（PII）など、禁止されているコンテンツを含む出力を自動的にブロックします。
* **設定可能なコンテンツフィルター**では、確率と重大度のスコアに基づいて、4つの有害カテゴリ（ヘイトスピーチ、ハラスメント、性的に露骨な内容、危険なコンテンツ）のブロックしきい値を定義できます。これらのフィルターはデフォルトでオフですが、ニーズに応じて設定できます。
* **安全のためのシステムインストラクション**: Vertex AIのGeminiモデルに対する[システムインストラクション](https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/safety-system-instructions)は、モデルがどのように振る舞い、どのような種類のコンテンツを生成すべきかについて直接的なガイダンスを提供します。具体的な指示を与えることで、組織固有のニーズに合わせて、モデルが望ましくないコンテンツを生成するのを積極的に防ぐことができます。禁止されているトピックやデリケートなトピック、免責事項の文言などのコンテンツ安全ガイドラインを定義したり、モデルの出力がブランドの声、トーン、価値観、ターゲットオーディエンスと一致するようにブランドセーフティガイドラインを定義したりするシステムインストラクションを作成できます。

これらの対策はコンテンツの安全性に対しては堅牢ですが、エージェントの意図との不一致、安全でないアクション、ブランドセーフティのリスクを減らすためには追加のチェックが必要です。

#### セキュリティガードレールのためのコールバックとプラグイン

コールバックは、ツールとモデルのI/Oに事前検証を追加するためのシンプルでエージェント固有の方法を提供する一方、プラグインは複数のエージェントにわたる一般的なセキュリティポリシーを実装するための再利用可能なソリューションを提供します。

ガードレールを追加するためにツールを修正できない場合、[**`ツール実行前コールバック(Before Tool Callback)`**](../callbacks/types-of-callbacks.md#before-tool-callback)関数を使用して、呼び出しの事前検証を追加できます。コールバックは、エージェントの状態、要求されたツール、およびパラメータにアクセスできます。このアプローチは非常に一般的であり、再利用可能なツールポリシーの共通ライブラリを作成するためにも使用できます。ただし、ガードレールを施行するための情報がパラメータで直接見えない場合、すべてのツールに適用できるわけではありません。

=== "Python"

    ```py
    # 仮のコールバック関数
    def validate_tool_params(
        callback_context: CallbackContext, # 正しいコンテキストタイプ
        tool: BaseTool,
        args: Dict[str, Any],
        tool_context: ToolContext
        ) -> Optional[Dict]: # before_tool_callbackの正しい戻り値の型

      print(f"コールバックがトリガーされました。ツール：{tool.name}, 引数：{args}")

      # 検証例：状態からの必須ユーザーIDが引数と一致するか確認
      expected_user_id = callback_context.state.get("session_user_id")
      actual_user_id_in_args = args.get("user_id_param") # ツールが'user_id_param'を受け取ると仮定

      if actual_user_id_in_args != expected_user_id:
          print("検証失敗：ユーザーIDが一致しません！")
          # ツールの実行を防ぎ、フィードバックを提供するために辞書を返す
          return {"error": f"ツール呼び出しがブロックされました：ユーザーIDが一致しません。"}

      # 検証が成功した場合、ツールの呼び出しを続行するためにNoneを返す
      print("コールバックの検証が成功しました。")
      return None

    # 仮のエージェント設定
    root_agent = LlmAgent( # 特定のエージェントタイプを使用
        model='gemini-2.0-flash',
        name='root_agent',
        instruction="...",
        before_tool_callback=validate_tool_params, # コールバックを割り当て
        tools = [
          # ... ツール関数またはToolインスタンスのリスト ...
          # 例：query_tool_instance
        ]
    )
    ```

=== "Go"

    ```go
    import (
    	"fmt"
    	"reflect"

    	"google.golang.org/adk/agent/llmagent"
    	"google.golang.org/adk/tool"
    )

    // 仮のコールバック関数
    func validateToolParams(
    	ctx tool.Context,
    	t tool.Tool,
    	args map[string]any,
    ) (map[string]any, error) {
    	fmt.Printf("コールバックがトリガーされました。ツール：%s, 引数：%v\n", t.Name(), args)

    	// 検証例：状態からの必須ユーザーIDが引数と一致するか確認
    	expectedUserIDVal, err := ctx.State().Get("session_user_id")
    	if err != nil {
    		// これは予期せぬエラーです。エラーを返します。
    		return nil, fmt.Errorf("内部エラー：状態にsession_user_idが見つかりません： %w", err)
    	}
        expectedUserID, ok := expectedUserIDVal.(string)
    	if !ok {
    		return nil, fmt.Errorf("内部エラー：状態のsession_user_idが文字列ではありません、型：%T", expectedUserIDVal)
    	}


    	actualUserIDInArgs, exists := args["user_id_param"]
    	if !exists {
    		// user_id_paramが引数にない場合の処理
    		fmt.Println("検証失敗：引数にuser_id_paramがありません！")
    		return map[string]any{"error": "ツール呼び出しがブロックされました：引数にuser_id_paramがありません。"}, nil
    	}

    	actualUserID, ok := actualUserIDInArgs.(string)
    	if !ok {
    		// user_id_paramが文字列でない場合の処理
    		fmt.Println("検証失敗：user_id_paramが文字列ではありません！")
    		return map[string]any{"error": "ツール呼び出しがブロックされました：user_id_paramが文字列ではありません。"}, nil
    	}

    	if actualUserID != expectedUserID {
    		fmt.Println("検証失敗：ユーザーIDが一致しません！")
    		// ツールの実行を防ぎ、モデルにフィードバックを提供するためにマップを返す。
    		// これはGoのエラーではなく、エージェントへのメッセージです。
    		return map[string]any{"error": "ツール呼び出しがブロックされました：ユーザーIDが一致しません。"}, nil
    	}
    	// 検証が成功した場合、ツールの呼び出しを続行するためにnil, nilを返す
    	fmt.Println("コールバックの検証が成功しました。")
    	return nil, nil
    }

    // 仮のエージェント設定
    // rootAgent, err := llmagent.New(llmagent.Config{
    // 	Model: "gemini-2.0-flash",
    // 	Name: "root_agent",
    // 	Instruction: "...",
    // 	BeforeToolCallbacks: []llmagent.BeforeToolCallback{validateToolParams},
    // 	Tools: []tool.Tool{queryToolInstance},
    // })
    ```

=== "Java"

    ```java
    // 仮のコールバック関数
    public Optional<Map<String, Object>> validateToolParams(
      CallbackContext callbackContext,
      Tool baseTool,
      Map<String, Object> input,
      ToolContext toolContext) {

    System.out.printf("コールバックがトリガーされました。ツール：%s, 引数：%s", baseTool.name(), input);

    // 検証例：状態からの必須ユーザーIDが入力パラメータと一致するか確認
    Object expectedUserId = callbackContext.state().get("session_user_id");
    Object actualUserIdInput = input.get("user_id_param"); // ツールが'user_id_param'を受け取ると仮定

    if (!actualUserIdInput.equals(expectedUserId)) {
      System.out.println("検証失敗：ユーザーIDが一致しません！");
      // ツールの実行を防ぎ、フィードバックを提供するために返す
      return Optional.of(Map.of("error", "ツール呼び出しがブロックされました：ユーザーIDが一致しません。"));
    }

    // 検証が成功した場合、ツールの呼び出しを続行するために返す
    System.out.println("コールバックの検証が成功しました。");
    return Optional.empty();
    }

    // 仮のエージェント設定
    public void runAgent() {
    LlmAgent agent =
        LlmAgent.builder()
            .model("gemini-2.0-flash")
            .name("AgentWithBeforeToolCallback")
            .instruction("...")
            .beforeToolCallback(this::validateToolParams) // コールバックを割り当て
            .tools(anyToolToUse) // 使用するツールを定義
            .build();
    }
    ```

ただし、エージェントアプリケーションにセキュリティガードレールを追加する場合、単一のエージェントに特化していないポリシーを実装するにはプラグインが推奨されるアプローチです。プラグインは自己完結型でモジュール式に設計されており、特定のセキュリティポリシーごとに個別のプラグインを作成し、それらをランナーレベルでグローバルに適用できます。つまり、セキュリティプラグインを一度設定すれば、そのランナーを使用するすべてのエージェントに適用され、コードの繰り返しなしにアプリケーション全体で一貫したセキュリティガードレールを確保できます。

いくつかの例は以下の通りです：

* **Gemini as a Judgeプラグイン**: このプラグインはGemini Flash Liteを使用して、ユーザー入力、ツールの入出力、エージェントの応答の適切性、プロンプトインジェクション、ジェイルブレイクの検出を評価します。このプラグインは、コンテンツの安全性、ブランドセーフティ、エージェントの意図との不一致を緩和するために、Geminiを安全フィルターとして機能するように設定します。プラグインは、ユーザー入力、ツールの入出力、モデルの出力をGemini Flash Liteに渡し、Gemini Flash Liteがエージェントへの入力が安全か危険かを判断するように設定されています。Geminiが入力が危険だと判断した場合、エージェントは事前に定められた応答を返します：「申し訳ありませんが、お手伝いできません。他に何かお手伝いできることはありますか？」。

* **Model Armorプラグイン**: 指定されたエージェント実行時点で潜在的なコンテンツ安全違反をチェックするためにModel Armor APIをクエリするプラグイン。_Gemini as a Judge_プラグインと同様に、Model Armorが有害なコンテンツの一致を見つけた場合、ユーザーに事前に定められた応答を返します。

* **PIIリダクションプラグイン**: [ツール実行前コールバック](/adk-docs/ja/plugins/#tool-callbacks)用に設計された専門のプラグインで、個人を特定できる情報がツールによって処理されたり、外部サービスに送信されたりする前にそれを編集するために特別に作成されました。

### サンドボックス化されたコード実行

コード実行は、追加のセキュリティ上の意味合いを持つ特別なツールです。モデルが生成したコードがローカル環境を危険にさらし、潜在的なセキュリティ問題を引き起こすのを防ぐために、サンドボックス化を使用する必要があります。

GoogleとADKは、安全なコード実行のためのいくつかのオプションを提供しています。[Vertex Gemini Enterprise APIコード実行機能](https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/code-execution-api)は、`tool_execution`ツールを有効にすることで、エージェントがサーバーサイドでサンドボックス化されたコード実行を利用できるようにします。データ分析を実行するコードについては、ADKの[組み込みコード実行ツール](../tools/built-in-tools.md#code-execution)を使用して[Vertex Code Interpreter拡張機能](https://cloud.google.com/vertex-ai/generative-ai/docs/extensions/code-interpreter)を呼び出すことができます。

これらのオプションのいずれも要件を満たさない場合は、ADKが提供するビルディングブロックを使用して独自のコード実行ツールを構築できます。実行環境は、密閉型にすることをお勧めします。制御されていないデータ漏洩を避けるためにネットワーク接続やAPI呼び出しを許可せず、ユーザー間のデータ漏洩の懸念を生じさせないために実行ごとにデータを完全にクリーンアップします。

### 評価

[エージェントの評価](../evaluate/index.md)を参照してください。

### VPC-SC境界とネットワーク制御

エージェントをVPC-SC境界内で実行している場合、すべてのAPI呼び出しが境界内のリソースのみを操作することが保証され、データ漏洩の可能性が減少します。

しかし、IDと境界はエージェントのアクションに対して粗い制御しか提供しません。ツール使用のガードレールは、そのような制限を緩和し、エージェント開発者が許可するアクションを細かく制御するためのより多くの力を与えます。

### その他のセキュリティリスク

#### UIでモデルが生成したコンテンツは常にエスケープする

エージェントの出力がブラウザで視覚化される際には注意が必要です。UIでHTMLやJSのコンテンツが適切にエスケープされていないと、モデルが返したテキストが実行され、データ漏洩につながる可能性があります。たとえば、間接的なプロンプトインジェクションは、モデルをだまして、ブラウザがセッションコンテンツを第三者のサイトに送信するように仕向ける`img`タグを含ませたり、クリックされると外部サイトにデータを送信するURLを構築させたりする可能性があります。このようなコンテンツを適切にエスケープすることで、モデルが生成したテキストがブラウザによってコードとして解釈されないようにする必要があります。