# 状態（State）：セッションのスクラッチパッド

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

各`Session`（私たちの会話スレッド）内で、**`state`**属性は、その特定のインタラクションのためのエージェント専用のスクラッチパッド（一時的な作業スペース）のように機能します。`session.events`が完全な履歴を保持するのに対し、`session.state`はエージェントが会話の*最中に*必要な動的な詳細を保存し、更新する場所です。

## `session.state`とは何か？

概念的に、`session.state`はキーと値のペアを保持するコレクション（辞書またはMap）です。エージェントが現在の会話を効果的にするために思い出す、または追跡する必要がある情報のために設計されています。

* **インタラクションのパーソナライズ：** 以前に言及されたユーザーの好みを記憶する（例：`'user_preference_theme': 'dark'`）。
* **タスクの進捗追跡：** 複数ターンにわたるプロセスのステップを把握する（例：`'booking_step': 'confirm_payment'`）。
* **情報の蓄積：** リストや要約を構築する（例：`'shopping_cart_items': ['book', 'pen']`）。
* **情報に基づいた意思決定：** 次の応答に影響を与えるフラグや値を保存する（例：`'user_is_authenticated': True`）。

### `State`の主な特徴

1. **構造：シリアライズ可能なキーと値のペア**

    * データは`key: value`として保存されます。
    * **キー（Keys）：** 常に文字列（`str`）です。明確な名前を使用してください（例：`'departure_city'`、`'user:language_preference'`）。
    * **値（Values）：** **シリアライズ可能**である必要があります。これは、`SessionService`によって簡単に保存およびロードできることを意味します。文字列、数値、ブール値、そして*これらの基本型のみ*を含む単純なリストや辞書など、特定の言語（Python/Go/Java）の基本型に固執してください。（正確な詳細についてはAPIドキュメントを参照してください）。
    * **⚠️ 複雑なオブジェクトを避ける：** **シリアライズ不可能なオブジェクト**（カスタムクラスのインスタンス、関数、接続など）を状態に直接保存しないでください。必要であれば、単純な識別子を保存し、複雑なオブジェクトは他の場所で取得してください。

2. **可変性：変化する**

    * `state`の内容は、会話が進むにつれて変化することが期待されます。

3. **永続性：`SessionService`に依存**

    * 状態がアプリケーションの再起動後も存続するかどうかは、選択したサービスによって異なります。

      * `InMemorySessionService`：**永続的ではない。** 再起動時に状態は失われます。
      * `DatabaseSessionService` / `VertexAiSessionService`：**永続的。** 状態は確実に保存されます。

!!! 注
    プリミティブの特定のパラメータやメソッド名は、SDK言語によって若干異なる場合があります（例：Pythonでは`session.state['current_intent'] = 'book_flight'`、Goでは`context.State().Set("current_intent", "book_flight")`、Javaでは`session.state().put("current_intent", "book_flight)`）。詳細については、言語固有のAPIドキュメントを参照してください。

### プレフィックスによる状態の整理：スコープが重要

状態キーのプレフィックスは、特に永続的なサービスを使用する場合、そのスコープと永続性の振る舞いを定義します。

* **プレフィックスなし（セッション状態）：**

    * **スコープ：** *現在の*セッション（`id`）に固有です。
    * **永続性：** `SessionService`が永続的（`Database`、`VertexAI`）である場合にのみ永続します。
    * **ユースケース：** 現在のタスク内の進捗追跡（例：`'current_booking_step'`）、このインタラクションのための一時的なフラグ（例：`'needs_clarification'`）。
    * **例：** `session.state['current_intent'] = 'book_flight'`

* **`user:` プレフィックス（ユーザー状態）：**

    * **スコープ：** `user_id`に関連付けられ、そのユーザーの（同じ`app_name`内の）*すべての*セッションで共有されます。
    * **永続性：** `Database`または`VertexAI`で永続的です。（`InMemory`によって保存されますが、再起動時に失われます）。
    * **ユースケース：** ユーザーの好み（例：`'user:theme'`）、プロファイルの詳細（例：`'user:name'`）。
    * **例：** `session.state['user:preferred_language'] = 'fr'`

* **`app:` プレフィックス（アプリ状態）：**

    * **スコープ：** `app_name`に関連付けられ、そのアプリケーションの*すべての*ユーザーとセッションで共有されます。
    * **永続性：** `Database`または`VertexAI`で永続的です。（`InMemory`によって保存されますが、再起動時に失われます）。
    * **ユースケース：** グローバル設定（例：`'app:api_endpoint'`）、共有テンプレート。
    * **例：** `session.state['app:global_discount_code'] = 'SAVE10'`

* **`temp:` プレフィックス（一時的な呼び出し状態）：**

    * **スコープ：** 現在の**呼び出し（invocation）**に固有です（エージェントがユーザー入力を受け取ってから、その入力に対する最終的な出力を生成するまでの全プロセス）。
    * **永続性：** **永続的ではない。** 呼び出しが完了した後に破棄され、次の呼び出しには引き継がれません。
    * **ユースケース：** 単一の呼び出し内でツール呼び出し間で渡される中間計算、フラグ、またはデータの保存。
    * **使用すべきでない場合：** ユーザーの好み、会話履歴の要約、蓄積されたデータなど、異なる呼び出しにわたって永続する必要がある情報。
    * **例：** `session.state['temp:raw_api_response'] = {...}`

!!! note "サブエージェントと呼び出しコンテキスト"
    親エージェントがサブエージェントを呼び出す場合（例：`SequentialAgent`や`ParallelAgent`を使用）、その`InvocationContext`をサブエージェントに渡します。これは、エージェント呼び出しのチェーン全体が同じ呼び出しIDを共有し、したがって同じ`temp:`状態を共有することを意味します。

**エージェントから見た状態：** エージェントのコードは、単一の`session.state`コレクション（dict/Map）を介して*結合された*状態と対話します。`SessionService`は、プレフィックスに基づいて正しい基盤となるストレージから状態を取得/マージする処理を行います。

### エージェントの指示におけるセッション状態へのアクセス

`LlmAgent`インスタンスを扱う際、簡単なテンプレート構文を使用して、セッション状態の値をエージェントの指示文字列に直接挿入できます。これにより、自然言語の指示だけに頼らず、動的でコンテキストを認識する指示を作成できます。

#### `{key}` テンプレートの使用

セッション状態から値を挿入するには、目的の状態変数のキーを波括弧で囲みます：`{key}`。フレームワークは、指示をLLMに渡す前に、このプレースホルダーを`session.state`の対応する値で自動的に置き換えます。

**例：**

=== "Python"

    ```python
    from google.adk.agents import LlmAgent

    story_generator = LlmAgent(
        name="StoryGenerator",
        model="gemini-2.0-flash",
        instruction="""猫についての短い物語を、テーマ：{topic}に焦点を当てて書いてください。"""
    )

    # session.state['topic']が"friendship"に設定されていると仮定すると、LLMは
    # 次の指示を受け取ります：
    # "猫についての短い物語を、テーマ：friendshipに焦点を当てて書いてください。"
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/sessions/instruction_template/instruction_template_example.go:key_template"
    ```

#### 重要な考慮事項

* キーの存在：指示文字列で参照するキーがsession.stateに存在することを確認してください。キーが見つからない場合、エージェントはエラーをスローします。存在するかもしれないし、しないかもしれないキーを使用するには、キーの後に疑問符(?)を含めることができます(例: {topic?})。
* データ型：キーに関連付けられた値は、文字列または簡単に文字列に変換できる型である必要があります。
* エスケープ：指示にリテラルの波括弧を使用する必要がある場合（例：JSONのフォーマット）、それらをエスケープする必要があります。

#### `InstructionProvider`による状態の挿入のバイパス

場合によっては、状態挿入メカニズムをトリガーせずに、指示で`{{`と`}}`を文字通り使用したいことがあります。たとえば、同じ構文を使用するテンプレート言語を扱うエージェントの指示を書いている場合などです。

これを実現するには、`instruction`パラメータに文字列の代わりに関数を提供します。この関数は`InstructionProvider`と呼ばれます。`InstructionProvider`を使用すると、ADKは状態の挿入を試みず、指示文字列はそのままモデルに渡されます。

`InstructionProvider`関数は`ReadonlyContext`オブジェクトを受け取ります。これを使用して、指示を動的に構築する必要がある場合にセッション状態やその他のコンテキスト情報にアクセスできます。

=== "Python"

    ```python
    from google.adk.agents import LlmAgent
    from google.adk.agents.readonly_context import ReadonlyContext

    # これはInstructionProviderです
    def my_instruction_provider(context: ReadonlyContext) -> str:
        # オプションでコンテキストを使用して指示を構築できます
        # この例では、リテラルの波括弧を持つ静的な文字列を返します。
        return "これは置換されない{{リテラルの波括弧}}を持つ指示です。"

    agent = LlmAgent(
        model="gemini-2.0-flash",
        name="template_helper_agent",
        instruction=my_instruction_provider
    )
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/sessions/instruction_provider/instruction_provider_example.go:bypass_state_injection"
    ```

`InstructionProvider`を使用し、*かつ*指示に状態を挿入したい場合は、`inject_session_state`ユーティリティ関数を使用できます。

=== "Python"

    ```python
    from google.adk.agents import LlmAgent
    from google.adk.agents.readonly_context import ReadonlyContext
    from google.adk.utils import instructions_utils

    async def my_dynamic_instruction_provider(context: ReadonlyContext) -> str:
        template = "これは{adjective}な指示で、{{リテラルの波括弧}}を含みます。"
        # これは'adjective'状態変数を挿入しますが、リテラルの波括弧はそのままにします。
        return await instructions_utils.inject_session_state(template, context)

    agent = LlmAgent(
        model="gemini-2.0-flash",
        name="dynamic_template_helper_agent",
        instruction=my_dynamic_instruction_provider
    )
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/sessions/instruction_provider/instruction_provider_example.go:manual_state_injection"
    ```

**直接挿入の利点**

* 明確さ：指示のどの部分が動的でセッション状態に基づいているかを明示的にします。
* 信頼性：LLMが状態にアクセスするために自然言語の指示を正しく解釈することに依存するのを避けます。
* 保守性：指示文字列を単純化し、状態変数名を更新する際のエラーのリスクを減らします。

**他の状態アクセス方法との関係**

この直接挿入方法は、LlmAgentの指示に特有のものです。他の状態アクセス方法の詳細については、次のセクションを参照してください。

### 状態の更新方法：推奨される方法

!!! note "状態を修正する正しい方法"
    セッション状態を変更する必要がある場合、正しく最も安全な方法は、関数に提供された**`Context`上の`state`オブジェクトを直接変更する**ことです（例：`callback_context.state['my_key'] = 'new_value'`）。フレームワークがこれらの変更を自動的に追跡するため、これは正しい方法での「直接的な状態操作」と見なされます。

    これは、`SessionService`から取得した`Session`オブジェクト上の`state`を直接変更すること（例：`my_session.state['my_key'] = 'new_value'`）とは決定的に異なります。**これは避けるべきです**。ADKのイベント追跡をバイパスし、データの損失につながる可能性があるためです。このページの最後にある「警告」セクションで、この重要な違いについて詳しく説明します。

状態は**常に**、`session_service.append_event()`を使用してセッション履歴に`Event`を追加する一環として更新されるべきです。これにより、変更が追跡され、永続性が正しく機能し、更新がスレッドセーフであることが保証されます。

**1. 簡単な方法：`output_key`（エージェントのテキスト応答用）**

これは、エージェントの最終的なテキスト応答を状態に直接保存する最も簡単な方法です。`LlmAgent`を定義する際に、`output_key`を指定します。

=== "Python"

    ```py
    from google.adk.agents import LlmAgent
    from google.adk.sessions import InMemorySessionService, Session
    from google.adk.runners import Runner
    from google.genai.types import Content, Part

    # output_keyでエージェントを定義
    greeting_agent = LlmAgent(
        name="Greeter",
        model="gemini-2.0-flash", # 有効なモデルを使用
        instruction="短く、親しみやすい挨拶を生成してください。",
        output_key="last_greeting" # 応答をstate['last_greeting']に保存
    )

    # --- RunnerとSessionのセットアップ ---
    app_name, user_id, session_id = "state_app", "user1", "session1"
    session_service = InMemorySessionService()
    runner = Runner(
        agent=greeting_agent,
        app_name=app_name,
        session_service=session_service
    )
    session = await session_service.create_session(app_name=app_name,
                                        user_id=user_id,
                                        session_id=session_id)
    print(f"初期状態: {session.state}")

    # --- エージェントの実行 ---
    # Runnerがappend_eventの呼び出しを処理し、output_keyを使用して
    # state_deltaを自動的に作成します。
    user_message = Content(parts=[Part(text="Hello")])
    for event in runner.run(user_id=user_id,
                            session_id=session_id,
                            new_message=user_message):
        if event.is_final_response():
          print(f"エージェントが応答しました。") # 応答テキストはevent.contentにもあります

    # --- 更新された状態の確認 ---
    updated_session = await session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=session_id)
    print(f"エージェント実行後の状態: {updated_session.state}")
    # 期待される出力例: {'last_greeting': 'こんにちは！何かお手伝いできることはありますか？'}
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/state/GreetingAgentExample.java:full_code"
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/sessions/state_example/state_example.go:greeting"
    ```

裏側では、`Runner`は`output_key`を使用して、`state_delta`を持つ必要な`EventActions`を作成し、`append_event`を呼び出します。

**2. 標準的な方法：`EventActions.state_delta`（複雑な更新用）**

より複雑なシナリオ（複数のキーの更新、文字列以外の値、`user:`や`app:`のような特定のスコープ、またはエージェントの最終的なテキストに直接関連しない更新）の場合、`EventActions`内で手動で`state_delta`を構築します。

=== "Python"

    ```py
    from google.adk.sessions import InMemorySessionService, Session
    from google.adk.events import Event, EventActions
    from google.genai.types import Part, Content
    import time

    # --- セットアップ ---
    session_service = InMemorySessionService()
    app_name, user_id, session_id = "state_app_manual", "user2", "session2"
    session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        state={"user:login_count": 0, "task_status": "idle"}
    )
    print(f"初期状態: {session.state}")

    # --- 状態変更の定義 ---
    current_time = time.time()
    state_changes = {
        "task_status": "active",              # セッション状態を更新
        "user:login_count": session.state.get("user:login_count", 0) + 1, # ユーザー状態を更新
        "user:last_login_ts": current_time,   # ユーザー状態を追加
        "temp:validation_needed": True        # 一時的な状態を追加（破棄されます）
    }

    # --- アクション付きのイベントを作成 ---
    actions_with_update = EventActions(state_delta=state_changes)
    # このイベントはエージェントの応答だけでなく、内部システムのアクションを表す場合があります
    system_event = Event(
        invocation_id="inv_login_update",
        author="system", # または 'agent', 'tool' など
        actions=actions_with_update,
        timestamp=current_time
        # contentはNoneであるか、実行されたアクションを表す場合があります
    )

    # --- イベントの追加（これにより状態が更新されます） ---
    await session_service.append_event(session, system_event)
    print("明示的なstate deltaで`append_event`が呼び出されました。")

    # --- 更新された状態の確認 ---
    updated_session = await session_service.get_session(app_name=app_name,
                                                user_id=user_id,
                                                session_id=session_id)
    print(f"イベント後の状態: {updated_session.state}")
    # 期待される出力: {'user:login_count': 1, 'task_status': 'active', 'user:last_login_ts': <timestamp>}
    # 注: 'temp:validation_needed'は存在しません。
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/sessions/state_example/state_example.go:manual"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/state/ManualStateUpdateExample.java:full_code"
    ```

**3. `CallbackContext`または`ToolContext`経由（コールバックとツールに推奨）**

エージェントのコールバック（例：`on_before_agent_call`、`on_after_agent_call`）やツール関数内で状態を変更する場合、関数に提供される`CallbackContext`または`ToolContext`の`state`属性を使用するのが最善です。

*   `callback_context.state['my_key'] = my_value`
*   `tool_context.state['my_key'] = my_value`

これらのコンテキストオブジェクトは、それぞれの実行スコープ内で状態の変更を管理するように特別に設計されています。`context.state`を変更すると、ADKフレームワークはこれらの変更が自動的にキャプチャされ、コールバックまたはツールによって生成されるイベントの`EventActions.state_delta`に正しくルーティングされることを保証します。このデルタは、イベントが追加される際に`SessionService`によって処理され、適切な永続性と追跡が保証されます。

この方法は、コールバックやツール内での最も一般的な状態更新シナリオにおいて、`EventActions`と`state_delta`の手動作成を抽象化し、コードをよりクリーンでエラーが発生しにくくします。

コンテキストオブジェクトに関するより包括的な詳細については、[コンテキストのドキュメント](../context/index.md)を参照してください。

=== "Python"

    ```python
    # エージェントのコールバックまたはツール関数内
    from google.adk.agents import CallbackContext # または ToolContext

    def my_callback_or_tool_function(context: CallbackContext, # または ToolContext
                                     # ... その他のパラメータ ...
                                    ):
        # 既存の状態を更新
        count = context.state.get("user_action_count", 0)
        context.state["user_action_count"] = count + 1

        # 新しい状態を追加
        context.state["temp:last_operation_status"] = "success"

        # 状態の変更はイベントのstate_deltaに自動的に含まれます
        # ... コールバック/ツールの残りのロジック ...
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/sessions/state_example/state_example.go:context"
    ```

=== "Java"

    ```java
    // エージェントのコールバックまたはツールメソッド内
    import com.google.adk.agents.CallbackContext; // または ToolContext
    // ... その他のインポート ...

    public class MyAgentCallbacks {
        public void onAfterAgent(CallbackContext callbackContext) {
            // 既存の状態を更新
            Integer count = (Integer) callbackContext.state().getOrDefault("user_action_count", 0);
            callbackContext.state().put("user_action_count", count + 1);

            // 新しい状態を追加
            callbackContext.state().put("temp:last_operation_status", "success");

            // 状態の変更はイベントのstate_deltaに自動的に含まれます
            // ... コールバックの残りのロジック ...
        }
    }
    ```

**`append_event`の役割：**

* `Event`を`session.events`に追加します。
* イベントの`actions`から`state_delta`を読み取ります。
* サービスの種類に基づいてプレフィックスと永続性を正しく処理しながら、これらの変更を`SessionService`によって管理される状態に適用します。
* セッションの`last_update_time`を更新します。
* 同時更新に対するスレッドセーフティを保証します。

### ⚠️ 直接的な状態変更に関する警告

`SessionService`から直接取得した`Session`オブジェクト（例：`session_service.get_session()`や`session_service.create_session()`経由）上の`session.state`コレクション（辞書/Map）を、エージェント呼び出しの管理されたライフサイクルの*外部で*（つまり、`CallbackContext`や`ToolContext`を介さずに）直接変更することは避けてください。たとえば、`retrieved_session = await session_service.get_session(...); retrieved_session.state['key'] = value`のようなコードは問題があります。

コールバックやツール*内での*`CallbackContext.state`や`ToolContext.state`を使用した状態の変更は、変更が追跡されることを保証する正しい方法です。なぜなら、これらのコンテキストオブジェクトはイベントシステムとの必要な統合を処理するからです。

**直接的な変更（コンテキスト外で）が強く推奨されない理由：**

1. **イベント履歴をバイパスする：** 変更が`Event`として記録されないため、監査可能性が失われます。
2. **永続性を破壊する：** この方法で行われた変更は、`DatabaseSessionService`や`VertexAiSessionService`によって**保存されない可能性が高い**です。これらは保存をトリガーするために`append_event`に依存しています。
3. **スレッドセーフではない：** 競合状態や更新の損失につながる可能性があります。
4. **タイムスタンプ/ロジックを無視する：** `last_update_time`を更新したり、関連するイベントロジックをトリガーしたりしません。

**推奨事項：** `output_key`、`EventActions.state_delta`（イベントを手動で作成する場合）、またはそれぞれのスコープ内にあるときに`CallbackContext`や`ToolContext`オブジェクトの`state`プロパティを変更することで状態を更新する方法に固執してください。これらの方法は、信頼性が高く、追跡可能で、永続的な状態管理を保証します。`session.state`への直接アクセス（`SessionService`から取得したセッションから）は、状態を*読み取る*場合にのみ使用してください。

### 状態設計のベストプラクティス再確認

* **ミニマリズム：** 不可欠で動的なデータのみを保存してください。
* **シリアライゼーション：** 基本的でシリアライズ可能な型を使用してください。
* **記述的なキーとプレフィックス：** 明確な名前と適切なプレフィックス（`user:`、`app:`、`temp:`、またはなし）を使用してください。
* **浅い構造：** 可能な限り深いネストは避けてください。
* **標準的な更新フロー：** `append_event`に依存してください。