# ランタイム

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

ADKランタイムは、ユーザーとの対話中にエージェントアプリケーションを動かす基盤となるエンジンです。定義されたエージェント、ツール、コールバックを受け取り、ユーザーの入力に応じてそれらの実行を調整し、情報の流れ、状態の変化、LLMやストレージなどの外部サービスとの対話を管理するシステムです。

ランタイムをエージェントアプリケーションの**「エンジン」**と考えてください。部品（エージェント、ツール）を定義すると、ランタイムはそれらがどのように接続され、ユーザーの要求を満たすために一緒に実行されるかを処理します。

## コアアイデア：イベントループ

ADKランタイムは、その中心で**イベントループ**上で動作します。このループは、`Runner`コンポーネントと定義された「実行ロジック」（エージェント、それらが作成するLLM呼び出し、コールバック、ツールを含む）との間の双方向通信を容易にします。

![intro_components.png](../assets/event-loop.png)

簡単に言うと：

1. `Runner`はユーザーのクエリを受信し、メインの`Agent`に処理を開始するように依頼します。
2. `Agent`（および関連するロジック）は、報告するもの（応答、ツールの使用要求、状態の変更など）があるまで実行され、その後`Event`を**生成**または**発行**します。
3. `Runner`はこの`Event`を受信し、関連するアクション（`Services`を介した状態変更の保存など）を処理し、イベントを आगे（ユーザーインターフェイスなど）に転送します。
4. `Runner`がイベントを処理した*後*にのみ、`Agent`のロジックは一時停止した場所から**再開**し、Runnerによってコミットされた変更の影響を潜在的に確認します。
5. このサイクルは、エージェントが現在のユーザーのクエリに対して生成するイベントがなくなるまで繰り返されます。

このイベント駆動型ループは、ADKがエージェントコードを実行する方法を支配する基本的なパターンです。

## ハートビート：イベントループ - 内部の仕組み

イベントループは、`Runner`とカスタムコード（エージェント、ツール、コールバック、設計ドキュメントではまとめて「実行ロジック」または「ロジックコンポーネント」と呼ばれる）との間の相互作用を定義するコアの運用パターンです。責任の明確な分担を確立します。

!!! Note
    特定のメソッド名とパラメータ名は、SDK言語によって若干異なる場合があります（例：Pythonの`agent_to_run.run_async(...)`、Goの`agent.Run(...)`、Javaの`agent_to_run.runAsync(...)`）。詳細については、言語固有のAPIドキュメントを参照してください。

### Runnerの役割（オーケストレーター）

`Runner`は、単一のユーザー呼び出しの中心的なコーディネーターとして機能します。ループにおけるその責任は次のとおりです。

1. **開始：** エンドユーザーのクエリ（`new_message`）を受信し、通常は`SessionService`を介してセッション履歴に追加します。
2. **キックオフ：** メインエージェントの実行メソッド（例：`agent_to_run.run_async(...)`）を呼び出して、イベント生成プロセスを開始します。
3. **受信と処理：** エージェントロジックが`Event`を`yield`または`emit`するのを待ちます。イベントを受信すると、Runnerは**迅速に処理**します。これには次のものが含まれます。
      * 構成済みの`Services`（`SessionService`、`ArtifactService`、`MemoryService`）を使用して、`event.actions`に示されている変更（`state_delta`、`artifact_delta`など）をコミットします。
      * その他の内部的な簿記を実行します。
4. **アップストリームへの生成：** 処理されたイベントを आगे（呼び出し元のアプリケーションやレンダリング用のUIなど）に転送します。
5. **反復：** 生成されたイベントの処理が完了したことをエージェントロジックに通知し、再開して*次の*イベントを生成できるようにします。

*概念的なRunnerループ：*

=== "Python"

    ```py
    # Runnerのメインループのロジックの簡略化されたビュー
    def run(new_query, ...) -> Generator[Event]:
        # 1. SessionServiceを介してセッションイベント履歴にnew_queryを追加します
        session_service.append_event(session, Event(author='user', content=new_query))

        # 2. エージェントを呼び出してイベントループを開始します
        agent_event_generator = agent_to_run.run_async(context)

        async for event in agent_event_generator:
            # 3. 生成されたイベントを処理し、変更をコミットします
            session_service.append_event(session, event) # 状態/アーティファクトのデルタなどをコミットします
            # memory_service.update_memory(...) # 該当する場合
            # artifact_serviceは、エージェントの実行中にコンテキストを介してすでに呼び出されている可能性があります

            # 4. アップストリーム処理のためにイベントを生成します（例：UIレンダリング）
            yield event
            # Runnerは、生成後にエージェントジェネレーターが続行できることを暗黙的に通知します
    ```

=== "Go"

    ```go
    // GoでのRunnerのメインループのロジックの簡略化された概念的なビュー
    func (r *Runner) RunConceptual(ctx context.Context, session *session.Session, newQuery *genai.Content) iter.Seq2[*Event, error] {
        return func(yield func(*Event, error) bool) {
            // 1. SessionServiceを介してセッションイベント履歴にnew_queryを追加します
            // ...
            userEvent := session.NewEvent(ctx.InvocationID()) // 概念的なビューのために簡略化
            userEvent.Author = "user"
            userEvent.LLMResponse = model.LLMResponse{Content: newQuery}

            if _, err := r.sessionService.Append(ctx, &session.AppendRequest{Event: userEvent}); err != nil {
                yield(nil, err)
                return
            }

            // 2. エージェントを呼び出してイベントストリームを開始します
            // agent.Runもiter.Seq2[*Event, error]を返すと仮定します
            agentEventsAndErrs := r.agent.Run(ctx, &agent.RunRequest{Session: session, Input: newQuery})

            for event, err := range agentEventsAndErrs {
                if err != nil {
                    if !yield(event, err) { // エラーがあってもイベントを生成してから停止します
                        return
                    }
                    return // エージェントがエラーで終了しました
                }

                // 3. 生成されたイベントを処理し、変更をコミットします
                // 実際のコードで見られるように、部分的なイベントのみをセッションサービスにコミットします
                if !event.LLMResponse.Partial {
                    if _, err := r.sessionService.Append(ctx, &session.AppendRequest{Event: event}); err != nil {
                        yield(nil, err)
                        return
                    }
                }
                // memory_service.update_memory(...) // 該当する場合
                // artifact_serviceは、エージェントの実行中にコンテキストを介してすでに呼び出されている可能性があります

                // 4. アップストリーム処理のためにイベントを生成します
                if !yield(event, nil) {
                    return // アップストリームのコンシューマーが停止しました
                }
            }
            // エージェントは正常に終了しました
        }
    }
    ```

=== "Java"

    ```java
    // JavaでのRunnerのメインループのロジックの簡略化された概念的なビュー。
    public Flowable<Event> runConceptual(
        Session session,                  
        InvocationContext invocationContext, 
        Content newQuery                
        ) {

        // 1. SessionServiceを介してセッションイベント履歴にnew_queryを追加します
        // ...
        sessionService.appendEvent(session, userEvent).blockingGet();

        // 2. エージェントを呼び出してイベントストリームを開始します
        Flowable<Event> agentEventStream = agentToRun.runAsync(invocationContext);

        // 3. 生成された各イベントを処理し、変更をコミットし、「生成」または「発行」します
        return agentEventStream.map(event -> {
            // これにより、セッションオブジェクトが変更されます（イベントが追加され、stateDeltaが適用されます）。
            // appendEventの戻り値（Single<Event>）は、概念的には
            // 処理後のイベント自体です。
            sessionService.appendEvent(session, event).blockingGet(); // 簡略化されたブロッキング呼び出し

            // memory_service.update_memory(...) // 該当する場合 - 概念的
            // artifact_serviceは、エージェントの実行中にコンテキストを介してすでに呼び出されている可能性があります

            // 4. アップストリーム処理のためにイベントを「生成」します
            //    RxJavaでは、マップでイベントを返すと、次の演算子またはサブスクライバーに効果的に生成されます。
            return event;
        });
    }
    ```

### 実行ロジックの役割（エージェント、ツール、コールバック）

エージェント、ツール、コールバック内のコードは、実際の計算と意思決定を担当します。ループとの相互作用には、次のものが含まれます。

1. **実行：** 実行が再開されたときのセッション状態を含む、現在の`InvocationContext`に基づいてロジックを実行します。
2. **生成：** ロジックが通信する必要がある場合（メッセージの送信、ツールの呼び出し、状態の変更の報告）、関連するコンテンツとアクションを含む`Event`を構築し、このイベントを`Runner`に`yield`します。
3. **一時停止：** 重要なことに、エージェントロジックの実行は、`yield`ステートメント（またはRxJavaの`return`）の直後に**即座に一時停止**します。`Runner`がステップ3（処理とコミット）を完了するのを待ちます。
4. **再開：** `Runner`が生成されたイベントを処理した*後*にのみ、エージェントロジックは`yield`の直後のステートメントから実行を再開します。
5. **更新された状態の確認：** 再開すると、エージェントロジックは、*以前に生成された*イベントから`Runner`によってコミットされた変更を反映するセッション状態（`ctx.session.state`）に確実にアクセスできます。

*概念的な実行ロジック：*

=== "Python"

    ```py
    # Agent.run_async、コールバック、またはツール内のロジックの簡略化されたビュー

    # ... 以前のコードは現在の状態に基づいて実行されます ...

    # 1. 変更または出力が必要かどうかを判断し、イベントを構築します
    # 例：状態の更新
    update_data = {'field_1': 'value_2'}
    event_with_state_change = Event(
        author=self.name,
        actions=EventActions(state_delta=update_data),
        content=types.Content(parts=[types.Part(text="状態が更新されました。")])
        # ... その他のイベントフィールド ...
    )

    # 2. 処理とコミットのためにRunnerにイベントを生成します
    yield event_with_state_change
    # <<<<<<<<<<<< 実行はここで一時停止します >>>>>>>>>>>>

    # <<<<<<<<<<<< RUNNERがイベントを処理してコミットします >>>>>>>>>>>>

    # 3. 上記のイベントの処理が完了した後にのみ実行を再開します。
    # これで、Runnerによってコミットされた状態が確実に反映されます。
    # 後続のコードは、生成されたイベントからの変更が発生したと安全に想定できます。
    val = ctx.session.state['field_1']
    # ここで`val`は「value_2」であることが保証されます（Runnerが正常にコミットしたと仮定）
    print(f"実行を再開しました。field_1の値は現在：{val}")

    # ... 後続のコードは続行されます ...
    # 後で別のイベントを生成する可能性があります...
    ```

=== "Go"

    ```go
    # Agent.Run、コールバック、またはツール内のロジックの簡略化されたビュー

    # ... 以前のコードは現在の状態に基づいて実行されます ...

    # 1. 変更または出力が必要かどうかを判断し、イベントを構築します
    # 例：状態の更新
    updateData := map[string]interface{}{"field_1": "value_2"}
    eventWithStateChange := &Event{
        Author: self.Name(),
        Actions: &EventActions{StateDelta: updateData},
        Content: genai.NewContentFromText("状態が更新されました。", "model"),
        // ... その他のイベントフィールド ...
    }

    # 2. 処理とコミットのためにRunnerにイベントを生成します
    # Goでは、これはイベントをチャネルに送信することによって行われます。
    eventsChan <- eventWithStateChange
    # <<<<<<<<<<<< 実行はここで一時停止します（概念的に） >>>>>>>>>>>>
    # チャネルの反対側のRunnerがイベントを受信して処理します。
    # エージェントのゴルーチンは続行する可能性がありますが、論理フローは次の入力またはステップを待ちます。

    # <<<<<<<<<<<< RUNNERがイベントを処理してコミットします >>>>>>>>>>>>

    # 3. 上記のイベントの処理が完了した後にのみ実行を再開します。
    # 実際のGo実装では、これはおそらくエージェントが
    # 次のステップを示す新しいRunRequestまたはコンテキストを受信することによって処理されます。
    # 更新された状態は、その新しいリクエストのセッションオブジェクトの一部になります。
    # この概念的な例では、状態を確認するだけです。
    val := ctx.State.Get("field_1")
    # ここで`val`は、Runnerが
    # エージェントを再度呼び出す前にセッション状態を更新したため、「value_2」であることが保証されます。
    fmt.Printf("実行を再開しました。field_1の値は現在： %v\n", val)

    # ... 後続のコードは続行されます ...
    # 後でチャネルに別のイベントを送信する可能性があります...
    ```

=== "Java"

    ```java
    // Agent.runAsync、コールバック、またはツール内のロジックの簡略化されたビュー
    // ... 以前のコードは現在の状態に基づいて実行されます ...

    // 1. 変更または出力が必要かどうかを判断し、イベントを構築します
    // 例：状態の更新
    ConcurrentMap<String, Object> updateData = new ConcurrentHashMap<>();
    updateData.put("field_1", "value_2");

    EventActions actions = EventActions.builder().stateDelta(updateData).build();
    Content eventContent = Content.builder().parts(Part.fromText("状態が更新されました。")).build();

    Event eventWithStateChange = Event.builder()
        .author(self.name())
        .actions(actions)
        .content(Optional.of(eventContent))
        // ... その他のイベントフィールド ...
        .build();

    // 2. イベントを「生成」します。RxJavaでは、これはストリームに発行することを意味します。
    //    Runner（またはアップストリームのコンシューマー）がこのFlowableをサブスクライブします。
    //    Runnerがこのイベントを受信すると、それを処理します（例：sessionService.appendEventを呼び出します）。
    //    Java ADKの「appendEvent」は、「ctx」（InvocationContext）内に保持されている「Session」オブジェクトを変更します。

    // <<<<<<<<<<<< 概念的な一時停止ポイント >>>>>>>>>>>>
    // RxJavaでは、「eventWithStateChange」の発行が発生し、その後ストリームは
    // Runnerがこのイベントを処理した*後*のロジックを表す「flatMap」または「concatMap」演算子で続行する可能性があります。

    // 「Runnerが処理を完了した後にのみ実行を再開する」をモデル化するには：
    // Runnerの`appendEvent`は通常、非同期操作自体です（Single<Event>を返します）。
    // エージェントのフローは、コミットされた状態に依存する後続のロジックが
    // その`appendEvent`が完了した*後*に実行されるように構成する必要があります。

    // これは、Runnerが通常それを調整する方法です。
    // Runner：
    //   agent.runAsync(ctx)
    //     .concatMapEager(eventFromAgent ->
    //         sessionService.appendEvent(ctx.session(), eventFromAgent) // これによりctx.session().state()が更新されます
    //             .toFlowable() // 処理後にイベントを発行します
    //     )
    //     .subscribe(processedEvent -> { /* UIがprocessedEventをレンダリングします */ });

    // したがって、エージェント自身のロジック内で、生成されたイベント*後*に何かを行う必要がある場合
    // 処理され、その状態の変更がctx.session().state()に反映されると、
    // その後続のロジックは通常、リアクティブチェーンの別のステップになります。

    // この概念的な例では、イベントを発行し、その後「再開」を
    // Flowableチェーンの後続の操作としてシミュレートします。

    return Flowable.just(eventWithStateChange) // ステップ2：イベントを生成します
        .concatMap(yieldedEvent -> {
            // <<<<<<<<<<<< RUNNERが概念的にイベントを処理してコミットします >>>>>>>>>>>>
            // この時点で、実際のランナーでは、ctx.session().appendEvent(yieldedEvent)が
            // Runnerによって呼び出され、ctx.session().state()が更新されます。
            // これをモデル化しようとしているエージェントの概念的なロジックの*内部*にいるため、
            // Runnerのアクションが暗黙的に「ctx.session()」を更新したと仮定します。

            // 3. 実行を再開します。
            // これで、Runnerによってコミットされた状態（sessionService.appendEventを介して）が
            // ctx.session().state()に確実に反映されます。
            Object val = ctx.session().state().get("field_1");
            // ここで`val`は、Runnerによって呼び出された`sessionService.appendEvent`が
            // `ctx`オブジェクト内のセッション状態を更新したため、「value_2」であることが保証されます。

            System.out.println("実行を再開しました。field_1の値は現在：" + val);

            // ... 後続のコードは続行されます ...
            // この後続のコードが別のイベントを生成する必要がある場合は、ここでそれを行います。
    ```

`Runner`と実行ロジック間のこの協調的な生成/一時停止/再開サイクルは、`Event`オブジェクトによって仲介され、ADKランタイムの中核を形成します。

## ランタイムの主要コンポーネント

ADKランタイム内でいくつかのコンポーネントが連携してエージェントの呼び出しを実行します。それらの役割を理解すると、イベントループがどのように機能するかが明確になります。

1. ### `Runner`

      * **役割：** 単一のユーザーのクエリ（`run_async`）のメインエントリポイントおよびオーケストレーター。
      * **機能：** 全体的なイベントループを管理し、実行ロジックによって生成されたイベントを受信し、サービスと連携してイベントアクション（状態/アーティファクトの変更）を処理およびコミットし、処理されたイベントをアップストリーム（UIなど）に転送します。基本的には、生成されたイベントに基づいて会話をターンごとに進めます。（`google.adk.runners.runner`で定義）。

2. ### 実行ロジックコンポーネント

      * **役割：** カスタムコードとコアエージェント機能を含む部分。
      * **コンポーネント：**
      * `Agent`（`BaseAgent`、`LlmAgent`など）：情報を処理し、アクションを決定する主要なロジックユニット。イベントを生成する`_run_async_impl`メソッドを実装します。
      * `Tools`（`BaseTool`、`FunctionTool`、`AgentTool`など）：エージェント（多くの場合`LlmAgent`）が外部の世界と対話したり、特定のタスクを実行したりするために使用する外部関数または機能。実行して結果を返し、その後イベントにラップされます。
      * `Callbacks`（関数）：エージェントにアタッチされたユーザー定義関数（`before_agent_callback`、`after_model_callback`など）で、実行フローの特定のポイントにフックし、潜在的に動作や状態を変更し、その影響がイベントにキャプチャされます。
      * **機能：** 実際の思考、計算、または外部との対話を実行します。**`Event`オブジェクトを生成**し、Runnerがそれらを処理するまで一時停止することで、結果やニーズを伝えます。

3. ### `Event`

      * **役割：** `Runner`と実行ロジックの間でやり取りされるメッセージ。
      * **機能：** アトミックな発生（ユーザー入力、エージェントテキスト、ツール呼び出し/結果、状態変更要求、制御信号）を表します。発生のコンテンツと意図された副作用（`state_delta`などの`actions`）の両方を伝えます。

4. ### `Services`

      * **役割：** 永続的または共有リソースの管理を担当するバックエンドコンポーネント。イベント処理中に主に`Runner`によって使用されます。
      * **コンポーネント：**
      * `SessionService`（`BaseSessionService`、`InMemorySessionService`など）：`Session`オブジェクトを管理します。これには、保存/読み込み、セッション状態への`state_delta`の適用、`event history`へのイベントの追加などが含まれます。
      * `ArtifactService`（`BaseArtifactService`、`InMemoryArtifactService`、`GcsArtifactService`など）：バイナリアーティファクトデータの保存と取得を管理します。`save_artifact`は実行ロジック中にコンテキストを介して呼び出されますが、イベントの`artifact_delta`はRunner/SessionServiceのアクションを確認します。
      * `MemoryService`（`BaseMemoryService`など）：（オプション）ユーザーのセッション間で長期的なセマンティックメモリを管理します。
      * **機能：** 永続層を提供します。`Runner`は、`event.actions`によって通知された変更が、実行ロジックが再開される*前*に確実に保存されるように、それらと対話します。

5. ### `Session`

      * **役割：** ユーザーとアプリケーション間の*1つの特定の会話*の状態と履歴を保持するデータコンテナ。
      * **機能：** 現在の`state`辞書、過去のすべての`events`（`event history`）のリスト、および関連するアーティファクトへの参照を保存します。これは、`SessionService`によって管理される対話の主要な記録です。

6. ### `Invocation`

      * **役割：** `Runner`がそれを受信した瞬間から、エージェントロジックがそのクエリのイベントの生成を終了するまで、*単一*のユーザーのクエリに応答して発生するすべてのものを表す概念的な用語。
      * **機能：** 呼び出しには、複数のエージェントの実行（エージェント転送または`AgentTool`を使用する場合）、複数のLLM呼び出し、ツールの実行、およびコールバックの実行が含まれる場合があり、すべて`InvocationContext`内の単一の`invocation_id`によって結び付けられます。`temp:`で始まる状態変数は、単一の呼び出しに厳密にスコープされ、その後破棄されます。

これらのプレーヤーは、イベントループを介して継続的に対話し、ユーザーの要求を処理します。

## 仕組み：簡略化された呼び出し

ツールを呼び出すLLMエージェントを含む、一般的なユーザーのクエリの簡略化されたフローを追跡してみましょう。

![intro_components.png](../assets/invocation-flow.png)

### ステップバイステップの内訳

1. **ユーザー入力：** ユーザーがクエリを送信します（例：「フランスの首都はどこですか？」）。
2. **Runnerの開始：** `Runner.run_async`が開始されます。`SessionService`と対話して関連する`Session`をロードし、ユーザーのクエリをセッション履歴の最初の`Event`として追加します。`InvocationContext`（`ctx`）が準備されます。
3. **エージェントの実行：** `Runner`は、指定されたルートエージェント（`LlmAgent`など）で`agent.run_async(ctx)`を呼び出します。
4. **LLM呼び出し（例）：** `Agent_Llm`は、おそらくツールを呼び出すことによって、情報が必要であると判断します。`LLM`のリクエストを準備します。LLMが`MyTool`を呼び出すことを決定したと仮定しましょう。
5. **FunctionCallイベントの生成：** `Agent_Llm`はLLMから`FunctionCall`応答を受信し、それを`Event(author='Agent_Llm', content=Content(parts=[Part(function_call=...)]))`でラップし、このイベントを`yield`または`emit`します。
6. **エージェントの一時停止：** `Agent_Llm`の実行は`yield`の直後に一時停止します。
7. **Runnerの処理：** `Runner`はFunctionCallイベントを受信します。履歴に記録するために`SessionService`に渡します。`Runner`はその後、イベントを`User`（またはアプリケーション）にアップストリームで生成します。
8. **エージェントの再開：** `Runner`はイベントが処理されたことを通知し、`Agent_Llm`は実行を再開します。
9. **ツールの実行：** `Agent_Llm`の内部フローは、要求された`MyTool`を実行に進みます。`tool.run_async(...)`を呼び出します。
10. **ツールの結果の返却：** `MyTool`が実行され、その結果を返します（例：`{'result': 'Paris'}`）。
11. **FunctionResponseイベントの生成：** エージェント（`Agent_Llm`）は、ツールの結果を`FunctionResponse`部分を含む`Event`にラップします（例：`Event(author='Agent_Llm', content=Content(role='user', parts=[Part(function_response=...)]))`）。このイベントには、ツールが状態を変更した場合（`state_delta`）またはアーティファクトを保存した場合（`artifact_delta`）の`actions`も含まれる場合があります。エージェントはこのイベントを`yield`します。
12. **エージェントの一時停止：** `Agent_Llm`は再び一時停止します。
13. **Runnerの処理：** `Runner`はFunctionResponseイベントを受信します。`state_delta`/`artifact_delta`を適用し、履歴にイベントを追加する`SessionService`に渡します。`Runner`はイベントをアップストリームで生成します。
14. **エージェントの再開：** `Agent_Llm`は再開し、ツールの結果と状態の変更がコミットされたことを認識します。
15. **最終的なLLM呼び出し（例）：** `Agent_Llm`は、自然言語の応答を生成するために、ツールの結果を`LLM`に返します。
16. **最終的なテキストイベントの生成：** `Agent_Llm`は`LLM`から最終的なテキストを受信し、それを`Event(author='Agent_Llm', content=Content(parts=[Part(text=...)]))`でラップし、`yield`します。
17. **エージェントの一時停止：** `Agent_Llm`は一時停止します。
18. **Runnerの処理：** `Runner`は最終的なテキストイベントを受信し、履歴のために`SessionService`に渡し、`User`にアップストリームで生成します。これはおそらく`is_final_response()`としてマークされます。
19. **エージェントの再開と終了：** `Agent_Llm`は再開します。この呼び出しのタスクが完了すると、その`run_async`ジェネレーターは終了します。
20. **Runnerの完了：** `Runner`はエージェントのジェネレーターが使い果たされたことを確認し、この呼び出しのループを終了します。

この生成/一時停止/処理/再開サイクルにより、状態の変更が一貫して適用され、実行ロジックがイベントを生成した後に常に最新のコミットされた状態で動作することが保証されます。

## 重要なランタイムの動作

ADKランタイムが状態、ストリーミング、および非同期操作をどのように処理するかに関するいくつかの重要な側面を理解することは、予測可能で効率的なエージェントを構築するために不可欠です。

### 状態の更新とコミットのタイミング

* **ルール：** コード（エージェント、ツール、またはコールバック内）がセッション状態を変更する場合（例：`context.state['my_key'] = 'new_value'`）、この変更は最初に現在の`InvocationContext`内にローカルに記録されます。変更は、対応する`state_delta`を`actions`に含む`Event`がコードによって`yield`され、その後`Runner`によって処理された*後*にのみ、**永続化されることが保証**されます（`SessionService`によって保存されます）。

* **意味：** `yield`から再開した*後*に実行されるコードは、*生成されたイベント*で通知された状態の変更がコミットされたと確実に想定できます。

=== "Python"

    ```py
    # エージェントロジック内（概念的）

    # 1. 状態を変更します
    ctx.session.state['status'] = 'processing'
    event1 = Event(..., actions=EventActions(state_delta={'status': 'processing'}))

    # 2. デルタを含むイベントを生成します
    yield event1
    # --- 一時停止 --- Runnerがevent1を処理し、SessionServiceが'status' = 'processing'をコミットします ---

    # 3. 実行を再開します
    # これで、コミットされた状態に安全に依存できます
    current_status = ctx.session.state['status'] # 'processing'であることが保証されます
    print(f"再開後のステータス：{current_status}")
    ```

=== "Go"

    ```go
      # エージェントロジック内（概念的）

    func (a *Agent) RunConceptual(ctx agent.InvocationContext) iter.Seq2[*session.Event, error] {
      # ロジック全体がイテレータとして返される関数でラップされます。
      return func(yield func(*session.Event, error) bool) {
          # ... 以前のコードは入力`ctx`の現在の状態に基づいて実行されます ...
          # 例：val := ctx.State().Get("field_1")はここで「value_1」を返す可能性があります。

          # 1. 変更または出力が必要かどうかを判断し、イベントを構築します
          updateData := map[string]interface{}{"field_1": "value_2"}
          eventWithStateChange := session.NewEvent(ctx.InvocationID())
          eventWithStateChange.Author = a.Name()
          eventWithStateChange.Actions = &session.EventActions{StateDelta: updateData}
          # ... その他のイベントフィールド ...


          # 2. 処理とコミットのためにRunnerにイベントを生成します。
          # エージェントの実行はこの呼び出しの直後に続行されます。
          if !yield(eventWithStateChange, nil) {
              # yieldがfalseを返した場合、コンシューマー（Runner）が
              # リッスンを停止したことを意味するため、イベントの生成を停止する必要があります。
              return
          }

          # <<<<<<<<<<<< RUNNERがイベントを処理してコミットします >>>>>>>>>>>>
          # これは、エージェントのイテレータが
          # イベントを生成した後、エージェントの外部で発生します。

          # 3. エージェントは、生成したばかりの状態の変更をすぐには確認できません。
          # 状態は、単一の`Run`呼び出し内で不変です。
          val := ctx.State().Get("field_1")
          # ここでの`val`は、まだ「value_1」です（または開始時に何であったか）。
          # 更新された状態（「value_2」）は、*次*の`Run`呼び出しの`ctx`でのみ
          # 利用可能になります。

          # ... 後続のコードは続行され、潜在的にさらに多くのイベントを生成します ...
          finalEvent := session.NewEvent(ctx.InvocationID())
          finalEvent.Author = a.Name()
          # ...
          yield(finalEvent, nil)
      }
    }
    ```

=== "Java"

    ```java
    // エージェントロジック内（概念的）
    // ... 以前のコードは現在の状態に基づいて実行されます ...

    // 1. 状態の変更を準備し、イベントを構築します
    ConcurrentHashMap<String, Object> stateChanges = new ConcurrentHashMap<>();
    stateChanges.put("status", "processing");

    EventActions actions = EventActions.builder().stateDelta(stateChanges).build();
    Content content = Content.builder().parts(Part.fromText("ステータスの更新：処理中")).build();

    Event event1 = Event.builder()
        .actions(actions)
        // ...
        .build();

    // 2. デルタを含むイベントを生成します
    return Flowable.just(event1)
        .map(
            emittedEvent -> {
                // --- 概念的な一時停止とRUNNERの処理 ---
                // 3. 実行を再開します（概念的に）
                // これで、コミットされた状態に安全に依存できます。
                String currentStatus = (String) ctx.session().state().get("status");
                System.out.println("再開後のステータス（エージェントロジック内）：" + currentStatus); // 'processing'であることが保証されます

                // イベント自体（event1）が渡されます。
                // このエージェントステップ内の後続のロジックが*別*のイベントを生成した場合、
                // concatMapを使用してその新しいイベントを発行します。
                return emittedEvent;
            });

    // ... 後続のエージェントロジックには、さらにリアクティブな演算子
    // または、更新された`ctx.session().state()`に基づいてさらに多くのイベントを発行することが含まれる場合があります。
    ```

### セッション状態の「ダーティリード」

* **定義：** コミットは`yield`の*後*に行われますが、*同じ呼び出し内で後で*実行され、状態変更イベントが実際に生成されて処理される*前*に実行されるコードは、**多くの場合、ローカルでコミットされていない変更を確認できます**。これは「ダーティリード」と呼ばれることもあります。
* **例：**

=== "Python"

    ```py
    # before_agent_callbackのコード
    callback_context.state['field_1'] = 'value_1'
    # 状態はローカルで'value_1'に設定されますが、まだRunnerによってコミットされていません

    # ... エージェントが実行されます ...

    # *同じ呼び出し内で*後で呼び出されるツールのコード
    # 読み取り可能（ダーティリード）ですが、'value_1'はまだ永続的であることが保証されていません。
    val = tool_context.state['field_1'] # ここで'val'は'value_1'になる可能性が高いです
    print(f"ツールのダーティリード値：{val}")

    # state_delta={'field_1': 'value_1'}を運ぶイベントが
    # このツールが実行された*後*に生成され、Runnerによって処理されると仮定します。
    ```

=== "Go"

    ```go
    // before_agent_callbackのコード
    // コールバックはコンテキストのセッション状態を直接変更します。
    // この変更は現在の呼び出しコンテキストに対してローカルです。
    ctx.State.Set("field_1", "value_1")
    # 状態はローカルで'value_1'に設定されますが、まだRunnerによってコミットされていません

    # ... エージェントが実行されます ...

    # *同じ呼び出し内で*後で呼び出されるツールのコード
    # 読み取り可能（ダーティリード）ですが、'value_1'はまだ永続的であることが保証されていません。
    val := ctx.State.Get("field_1") # ここで'val'は'value_1'になる可能性が高いです
    fmt.Printf("ツールのダーティリード値： %v\n", val)

    # state_delta={'field_1': 'value_1'}を運ぶイベントが
    # このツールが実行された*後*に生成され、Runnerによって処理されると仮定します。
    ```

=== "Java"

    ```java
    // 状態を変更 - BeforeAgentCallbackのコード
    // ANDは、この変更をcallbackContext.eventActions().stateDelta()でステージングします。
    callbackContext.state().put("field_1", "value_1");

    // --- エージェントが実行されます ... ---

    // --- *同じ呼び出し内で*後で呼び出されるツールのコード ---
    // 読み取り可能（ダーティリード）ですが、'value_1'はまだ永続的であることが保証されていません。
    Object val = toolContext.state().get("field_1"); // ここで'val'は'value_1'になる可能性が高いです
    System.out.println("ツールのダーティリード値：" + val);
    // state_delta={'field_1': 'value_1'}を運ぶイベントが
    // このツールが実行された*後*に生成され、Runnerによって処理されると仮定します。
    ```

* **意味：**
  * **利点：** 単一の複雑なステップ内のロジックのさまざまな部分（次のLLMターンの前の複数のコールバックやツール呼び出しなど）が、完全な生成/コミットサイクルを待たずに状態を使用して調整できます。
  * **注意：** 重要なロジックでダーティリードに大きく依存すると、リスクが高くなる可能性があります。`state_delta`を運ぶイベントが`Runner`によって生成されて処理される*前*に呼び出しが失敗した場合、コミットされていない状態の変更は失われます。重要な状態遷移については、正常に処理されるイベントに関連付けられていることを確認してください。

### ストリーミングと非ストリーミングの出力（`partial=True`）

これは主に、特にストリーミング生成APIを使用する場合に、LLMからの応答がどのように処理されるかに関連しています。

* **ストリーミング：** LLMは、トークンごとまたは小さなチャンクで応答を生成します。
  * フレームワーク（多くの場合`BaseLlmFlow`内）は、単一の概念的な応答に対して複数の`Event`オブジェクトを生成します。これらのイベントのほとんどは`partial=True`になります。
  * `Runner`は、`partial=True`のイベントを受信すると、通常は**すぐにアップストリームに転送**しますが（UI表示用）、`actions`（`state_delta`など）の処理は**スキップ**します。
  * 最終的に、フレームワークはその応答の最終イベントを生成し、非部分的（`partial=False`または`turn_complete=True`を介して暗黙的に）としてマークされます。
  * `Runner`は**この最終イベントのみを完全に処理**し、関連する`state_delta`または`artifact_delta`をコミットします。
* **非ストリーミング：** LLMは応答全体を一度に生成します。フレームワークは、`Runner`が完全に処理する非部分的な単一のイベントを生成します。
* **重要な理由：** 状態の変更がアトミックに適用され、LLMからの*完全な*応答に基づいて一度だけ適用されるようにしながら、UIが生成されるにつれてテキストを段階的に表示できるようにします。

## 非同期がプライマリ（`run_async`）

* **コア設計：** ADKランタイムは、基本的に非同期ライブラリ（Pythonの`asyncio`やJavaの`RxJava`など）に基づいて構築されており、同時操作（LLM応答やツール実行の待機など）をブロックせずに効率的に処理します。
* **メインエントリポイント：** `Runner.run_async`は、エージェントの呼び出しを実行するための主要なメソッドです。すべてのコアの実行可能なコンポーネント（エージェント、特定のフロー）は、内部的に`非同期`メソッドを使用します。
* **同期の利便性（`run`）：** 同期`Runner.run`メソッドは、主に利便性のために存在します（単純なスクリプトやテスト環境など）。ただし、内部的には、`Runner.run`は通常、`Runner.run_async`を呼び出し、非同期イベントループの実行を管理します。
* **開発者エクスペリエンス：** 最高のパフォーマンスを得るには、アプリケーション（ADKを使用するWebサーバーなど）を非同期で設計することをお勧めします。Pythonでは、これは`asyncio`を使用することを意味します。Javaでは、`RxJava`のリアクティブプログラミングモデルを活用します。
* **同期コールバック/ツール：** ADKフレームワークは、ツールとコールバックの両方に非同期関数と同期関数をサポートしています。
    * **ブロッキングI/O：** 長時間実行される同期I/O操作の場合、フレームワークは停止を防ごうとします。Python ADKはasyncio.to_threadを使用する場合がありますが、Java ADKは多くの場合、ブロッキング呼び出しに適切なRxJavaスケジューラまたはラッパーに依存します。
    * **CPUバウンドワーク：** 純粋にCPU集約的な同期タスクは、両方の環境で実行スレッドをブロックします。

これらの動作を理解すると、状態の一貫性、ストリーミングの更新、および非同期実行に関連する問題をデバッグし、より堅牢なADKアプリケーションを作成するのに役立ちます。
