# イベント

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

イベントは、エージェント開発キット（ADK）内における情報フローの基本単位です。これらは、初期のユーザー入力から最終的な応答、そしてその間のすべてのステップに至るまで、エージェントのインタラクションライフサイクル中に発生するすべての重要な出来事を表します。イベントを理解することは、コンポーネントが通信し、状態が管理され、制御フローが指示される主要な方法であるため、非常に重要です。

## イベントとは何か、なぜ重要なのか

ADKにおける`Event`は、エージェント実行の特定の時点を表す不変のレコードです。ユーザーメッセージ、エージェントの返信、ツール使用リクエスト（関数呼び出し）、ツールの結果、状態の変更、制御シグナル、およびエラーをキャプチャします。

=== "Python"
    技術的には、これは`google.adk.events.Event`クラスのインスタンスであり、基本的な`LlmResponse`構造を基に、不可欠なADK固有のメタデータと`actions`ペイロードを追加して構築されています。

    ```python
    # イベントの概念的な構造 (Python)
    # from google.adk.events import Event, EventActions
    # from google.genai import types

    # class Event(LlmResponse): # 簡略化されたビュー
    #     # --- LlmResponse のフィールド ---
    #     content: Optional[types.Content]
    #     partial: Optional[bool]
    #     # ... その他の応答フィールド ...

    #     # --- ADK 固有の追加項目 ---
    #     author: str          # 'user' またはエージェント名
    #     invocation_id: str   # インタラクション実行全体の ID
    #     id: str              # この特定のイベントの一意の ID
    #     timestamp: float     # 作成時刻
    #     actions: EventActions # 副作用と制御にとって重要
    #     branch: Optional[str] # 階層パス
    #     # ...
    ```

=== "Go"
    Goでは、これは`google.golang.org/adk/session.Event`型の構造体です。

    ```go
    // イベントの概念的な構造 (Go - session/session.go を参照)
    // session.Event 構造体に基づく簡略化されたビュー
    type Event struct {
        // --- 埋め込まれた model.LLMResponse のフィールド ---
        model.LLMResponse

        // --- ADK 固有の追加項目 ---
        Author       string         // 'user' またはエージェント名
        InvocationID string         // インタラクション実行全体の ID
        ID           string         // この特定のイベントの一意の ID
        Timestamp    time.Time      // 作成時刻
        Actions      EventActions   // 副作用と制御にとって重要
        Branch       string         // 階層パス
        // ... その他のフィールド
    }

    // model.LLMResponse は Content フィールドを含む
    type LLMResponse struct {
        Content *genai.Content
        // ... その他のフィールド
    }
    ```

=== "Java"
    Javaでは、これは`com.google.adk.events.Event`クラスのインスタンスです。これもまた、基本的な応答構造を基に、不可欠なADK固有のメタデータと`actions`ペイロードを追加して構築されています。

    ```java
    // イベントの概念的な構造 (Java - com.google.adk.events.Event.java を参照)
    // 提供された com.google.adk.events.Event.java に基づく簡略化されたビュー
    // public class Event extends JsonBaseModel {
    //     // --- LlmResponse に類似したフィールド ---
    //     private Optional<Content> content;
    //     private Optional<Boolean> partial;
    //     // ... errorCode, errorMessage などのその他の応答フィールド ...

    //     // --- ADK 固有の追加項目 ---
    //     private String author;         // 'user' またはエージェント名
    //     private String invocationId;   // インタラクション実行全体の ID
    //     private String id;             // この特定のイベントの一意の ID
    //     private long timestamp;        // 作成時刻 (エポックミリ秒)
    //     private EventActions actions;  // 副作用と制御にとって重要
    //     private Optional<String> branch; // 階層パス
    //     // ... turnComplete, longRunningToolIds などのその他のフィールド ...
    // }
    ```

イベントは、以下のいくつかの重要な理由から、ADKの運用の中核をなしています：

1.  **コミュニケーション:** ユーザーインターフェース、`Runner`、エージェント、LLM、ツール間の標準的なメッセージ形式として機能します。すべてが`Event`として流れます。

2.  **状態とアーティファクトの変更のシグナリング:** イベントは状態変更の指示を伝え、アーティファクトの更新を追跡します。`SessionService`はこれらのシグナルを使用して永続性を確保します。Pythonでは、変更は`event.actions.state_delta`および`event.actions.artifact_delta`を介してシグナルされます。

3.  **制御フロー:** `event.actions.transfer_to_agent`や`event.actions.escalate`などの特定のフィールドは、フレームワークを指示するシグナルとして機能し、次に実行するエージェントやループを終了するかどうかを決定します。

4.  **履歴と可観測性:** `session.events`に記録されたイベントのシーケンスは、インタラクションの完全で時系列に沿った履歴を提供し、デバッグ、監査、エージェントの挙動を段階的に理解する上で非常に価値があります。

本質的に、ユーザーのクエリからエージェントの最終的な回答までの全プロセスは、`Event`オブジェクトの生成、解釈、処理を通じて調整されます。

## イベントの理解と使用

開発者として、あなたは主に`Runner`によって生成されるイベントのストリームと対話します。それらから情報を理解し、抽出する方法は次のとおりです：

!!! 注
    プリミティブの特定のパラメータやメソッド名は、SDKの言語によって若干異なる場合があります（例：Pythonの`event.content()`、Javaの`event.content().get().parts()`）。詳細については、言語固有のAPIドキュメントを参照してください。

### イベントの発生源とタイプの特定

以下を確認することで、イベントが何を表しているかを迅速に判断できます：

*   **誰が送信したか？ (`event.author`)**
    *   `'user'`: エンドユーザーからの直接の入力を示します。
    *   `'AgentName'`: 特定のエージェント（例：`'WeatherAgent'`、`'SummarizerAgent'`）からの出力またはアクションを示します。
*   **主なペイロードは何か？ (`event.content`および`event.content.parts`)**
    *   **テキスト:** 会話メッセージを示します。Pythonの場合、`event.content.parts[0].text`が存在するか確認します。Javaの場合、`event.content()`が存在し、その`parts()`が存在して空でなく、最初のパートの`text()`が存在するか確認します。
    *   **ツール呼び出しリクエスト:** `event.get_function_calls()`を確認します。空でない場合、LLMが1つ以上のツールの実行を要求しています。リストの各項目には`.name`と`.args`があります。
    *   **ツールの結果:** `event.get_function_responses()`を確認します。空でない場合、このイベントはツール実行の結果を保持しています。各項目には`.name`と`.response`（ツールによって返された辞書）があります。*注:* 履歴の構造化のため、`content`内の`role`はしばしば`'user'`ですが、イベントの`author`は通常、ツール呼び出しを要求したエージェントです。

*   **ストリーミング出力か？ (`event.partial`)**
    これがLLMからの不完全なテキストのチャンクであるかどうかを示します。
    *   `True`: さらにテキストが続きます。
    *   `False`または`None`/`Optional.empty()`: コンテンツのこの部分は完了しています（ただし、`turn_complete`もfalseの場合、ターン全体は終了していない可能性があります）。

=== "Python"

    ```python
    # 擬似コード: 基本的なイベントの識別 (Python)
    # async for event in runner.run_async(...):
    #     print(f"イベントの送信元: {event.author}")
    #
    #     if event.content and event.content.parts:
    #         if event.get_function_calls():
    #             print("  タイプ: ツール呼び出しリクエスト")
    #         elif event.get_function_responses():
    #             print("  タイプ: ツールの結果")
    #         elif event.content.parts[0].text:
    #             if event.partial:
    #                 print("  タイプ: ストリーミングテキストチャンク")
    #             else:
    #                 print("  タイプ: 完全なテキストメッセージ")
    #         else:
    #             print("  タイプ: その他のコンテンツ (例: コードの結果)")
    #     elif event.actions and (event.actions.state_delta or event.actions.artifact_delta):
    #         print("  タイプ: 状態/アーティファクトの更新")
    #     else:
    #         print("  タイプ: 制御シグナルまたはその他")
    ```

=== "Go"

    ```go
      // 擬似コード: 基本的なイベントの識別 (Go)
    import (
      "fmt"
      "google.golang.org/adk/session"
      "google.golang.org/genai"
    )

    func hasFunctionCalls(content *genai.Content) bool {
      if content == nil {
        return false
      }
      for _, part := range content.Parts {
        if part.FunctionCall != nil {
          return true
        }
      }
      return false
    }

    func hasFunctionResponses(content *genai.Content) bool {
      if content == nil {
        return false
      }
      for _, part := range content.Parts {
        if part.FunctionResponse != nil {
          return true
        }
      }
      return false
    }

    func processEvents(events <-chan *session.Event) {
      for event := range events {
        fmt.Printf("イベントの送信元: %s\n", event.Author)

        if event.LLMResponse != nil && event.LLMResponse.Content != nil {
          if hasFunctionCalls(event.LLMResponse.Content) {
            fmt.Println("  タイプ: ツール呼び出しリクエスト")
          } else if hasFunctionResponses(event.LLMResponse.Content) {
            fmt.Println("  タイプ: ツールの結果")
          } else if len(event.LLMResponse.Content.Parts) > 0 {
            if event.LLMResponse.Content.Parts[0].Text != "" {
              if event.LLMResponse.Partial {
                fmt.Println("  タイプ: ストリーミングテキストチャンク")
              } else {
                fmt.Println("  タイプ: 完全なテキストメッセージ")
              }
            } else {
              fmt.Println("  タイプ: その他のコンテンツ (例: コードの結果)")
            }
          }
        } else if len(event.Actions.StateDelta) > 0 {
          fmt.Println("  タイプ: 状態の更新")
        } else {
          fmt.Println("  タイプ: 制御シグナルまたはその他")
        }
      }
    }
    ```

=== "Java"

    ```java
    // 擬似コード: 基本的なイベントの識別 (Java)
    // import com.google.genai.types.Content;
    // import com.google.adk.events.Event;
    // import com.google.adk.events.EventActions;

    // runner.runAsync(...).forEach(event -> { // 同期またはリアクティブストリームを想定
    //     System.out.println("イベントの送信元: " + event.author());
    //
    //     if (event.content().isPresent()) {
    //         Content content = event.content().get();
    //         if (!event.functionCalls().isEmpty()) {
    //             System.out.println("  タイプ: ツール呼び出しリクエスト");
    //         } else if (!event.functionResponses().isEmpty()) {
    //             System.out.println("  タイプ: ツールの結果");
    //         } else if (content.parts().isPresent() && !content.parts().get().isEmpty() &&
    //                    content.parts().get().get(0).text().isPresent()) {
    //             if (event.partial().orElse(false)) {
    //                 System.out.println("  タイプ: ストリーミングテキストチャンク");
    //             } else {
    //                 System.out.println("  タイプ: 完全なテキストメッセージ");
    //             }
    //         } else {
    //             System.out.println("  タイプ: その他のコンテンツ (例: コードの結果)");
    //         }
    //     } else if (event.actions() != null &&
    //                ((event.actions().stateDelta() != null && !event.actions().stateDelta().isEmpty()) ||
    //                 (event.actions().artifactDelta() != null && !event.actions().artifactDelta().isEmpty()))) {
    //         System.out.println("  タイプ: 状態/アーティファクトの更新");
    //     } else {
    //         System.out.println("  タイプ: 制御シグナルまたはその他");
    //     }
    // });
    ```

### 主要情報の抽出

イベントのタイプがわかったら、関連データにアクセスします：

*   **テキストコンテンツ:**
    テキストにアクセスする前に、常にコンテンツとパートの存在を確認してください。Pythonでは `text = event.content.parts[0].text` です。

*   **関数呼び出しの詳細:**

    === "Python"
    
        ```python
        calls = event.get_function_calls()
        if calls:
            for call in calls:
                tool_name = call.name
                arguments = call.args # これは通常辞書です
                print(f"  ツール: {tool_name}, 引数: {arguments}")
                # アプリケーションはこれに基づいて実行をディスパッチする可能性があります
        ```

    === "Go"

        ```go
        import (
            "fmt"
            "google.golang.org/adk/session"
            "google.golang.org/genai"
        )

        func handleFunctionCalls(event *session.Event) {
            if event.LLMResponse == nil || event.LLMResponse.Content == nil {
                return
            }
            calls := event.Content.FunctionCalls()
            if len(calls) > 0 {
                for _, call := range calls {
                    toolName := call.Name
                    arguments := call.Args
                    fmt.Printf("  ツール: %s, 引数: %v\n", toolName, arguments)
                    // アプリケーションはこれに基づいて実行をディスパッチする可能性があります
                }
            }
        }
        ```

    === "Java"

        ```java
        import com.google.genai.types.FunctionCall;
        import com.google.common.collect.ImmutableList;
        import java.util.Map;

        ImmutableList<FunctionCall> calls = event.functionCalls(); // Event.java から
        if (!calls.isEmpty()) {
          for (FunctionCall call : calls) {
            String toolName = call.name().get();
            // args は Optional<Map<String, Object>>
            Map<String, Object> arguments = call.args().get();
                   System.out.println("  ツール: " + toolName + ", 引数: " + arguments);
            // アプリケーションはこれに基づいて実行をディスパッチする可能性があります
          }
        }
        ```

*   **関数応答の詳細:**

    === "Python"

        ```python
        responses = event.get_function_responses()
        if responses:
            for response in responses:
                tool_name = response.name
                result_dict = response.response # ツールによって返された辞書
                print(f"  ツールの結果: {tool_name} -> {result_dict}")
        ```

    === "Go"

        ```go
        import (
            "fmt"
            "google.golang.org/adk/session"
            "google.golang.org/genai"
        )

        func handleFunctionResponses(event *session.Event) {
            if event.LLMResponse == nil || event.LLMResponse.Content == nil {
                return
            }
            responses := event.Content.FunctionResponses()
            if len(responses) > 0 {
                for _, response := range responses {
                    toolName := response.Name
                    result := response.Response
                    fmt.Printf("  ツールの結果: %s -> %v\n", toolName, result)
                }
            }
        }
        ```

    === "Java"

        ```java
        import com.google.genai.types.FunctionResponse;
        import com.google.common.collect.ImmutableList;
        import java.util.Map;

        ImmutableList<FunctionResponse> responses = event.functionResponses(); // Event.java から
        if (!responses.isEmpty()) {
            for (FunctionResponse response : responses) {
                String toolName = response.name().get();
                Map<String, String> result= response.response().get(); // 応答を取得する前に確認
                System.out.println("  ツールの結果: " + toolName + " -> " + result);
            }
        }
        ```

*   **識別子:**
    *   `event.id`: この特定のイベントインスタンスの一意のID。
    *   `event.invocation_id`: このイベントが属する、ユーザーリクエストから最終応答までのサイクル全体のID。ロギングとトレーシングに役立ちます。

### アクションと副作用の検出

`event.actions`オブジェクトは、発生した、または発生すべき変更をシグナルします。`event.actions`とそのフィールド/メソッドにアクセスする前に、常にそれらが存在するかどうかを確認してください。

*   **状態の変更:** このイベントを生成したステップ中にセッション状態で変更されたキーと値のペアのコレクションを提供します。

    === "Python"
        `delta = event.actions.state_delta` (`{key: value}`ペアの辞書)。
        ```python
        if event.actions and event.actions.state_delta:
            print(f"  状態の変更: {event.actions.state_delta}")
            # 必要に応じてローカルUIまたはアプリケーションの状態を更新
        ```
    === "Go"
        `delta := event.Actions.StateDelta` (`map[string]any`)
        ```go
        import (
            "fmt"
            "google.golang.org/adk/session"
        )

        func handleStateChanges(event *session.Event) {
            if len(event.Actions.StateDelta) > 0 {
                fmt.Printf("  状態の変更: %v\n", event.Actions.StateDelta)
                // 必要に応じてローカルUIまたはアプリケーションの状態を更新
            }
        }
        ```

    === "Java"
        `ConcurrentMap<String, Object> delta = event.actions().stateDelta();`

        ```java
        import java.util.concurrent.ConcurrentMap;
        import com.google.adk.events.EventActions;

        EventActions actions = event.actions(); // event.actions()がnullでないと仮定
        if (actions != null && actions.stateDelta() != null && !actions.stateDelta().isEmpty()) {
            ConcurrentMap<String, Object> stateChanges = actions.stateDelta();
            System.out.println("  状態の変更: " + stateChanges);
            // 必要に応じてローカルUIまたはアプリケーションの状態を更新
        }
        ```

*   **アーティファクトの保存:** 保存されたアーティファクトとその新しいバージョン番号（または関連する`Part`情報）を示すコレクションを提供します。

    === "Python"
        `artifact_changes = event.actions.artifact_delta` (`{filename: version}`の辞書)。
        ```python
        if event.actions and event.actions.artifact_delta:
            print(f"  保存されたアーティファクト: {event.actions.artifact_delta}")
            # UIがアーティファクトリストを更新する可能性があります
        ```

    === "Go"
        `artifactChanges := event.Actions.ArtifactDelta` (`map[string]artifact.Artifact`)
        ```go
        import (
            "fmt"
            "google.golang.org/adk/artifact"
            "google.golang.org/adk/session"
        )

        func handleArtifactChanges(event *session.Event) {
            if len(event.Actions.ArtifactDelta) > 0 {
                fmt.Printf("  保存されたアーティファクト: %v\n", event.Actions.ArtifactDelta)
                // UIがアーティファクトリストを更新する可能性があります
                // event.Actions.ArtifactDeltaをループしてファイル名とartifact.Artifactの詳細を取得
                for filename, art := range event.Actions.ArtifactDelta {
                    fmt.Printf("    ファイル名: %s, バージョン: %d, MIMEタイプ: %s\n", filename, art.Version, art.MIMEType)
                }
            }
        }
        ```

    === "Java"
        `ConcurrentMap<String, Part> artifactChanges = event.actions().artifactDelta();`

        ```java
        import java.util.concurrent.ConcurrentMap;
        import com.google.genai.types.Part;
        import com.google.adk.events.EventActions;

        EventActions actions = event.actions(); // event.actions()がnullでないと仮定
        if (actions != null && actions.artifactDelta() != null && !actions.artifactDelta().isEmpty()) {
            ConcurrentMap<String, Part> artifactChanges = actions.artifactDelta();
            System.out.println("  保存されたアーティファクト: " + artifactChanges);
            // UIがアーティファクトリストを更新する可能性があります
            // artifactChanges.entrySet()をループしてファイル名とPartの詳細を取得
        }
        ```

*   **制御フローシグナル:** ブール値のフラグまたは文字列の値を確認します：

    === "Python"
        *   `event.actions.transfer_to_agent` (string): 制御が指定されたエージェントに渡されるべきです。
        *   `event.actions.escalate` (bool): ループが終了するべきです。
        *   `event.actions.skip_summarization` (bool): ツールの結果がLLMによって要約されるべきではありません。
        ```python
        if event.actions:
            if event.actions.transfer_to_agent:
                print(f"  シグナル: {event.actions.transfer_to_agent} に転送")
            if event.actions.escalate:
                print("  シグナル: エスカレート (ループ終了)")
            if event.actions.skip_summarization:
                print("  シグナル: ツール結果の要約をスキップ")
        ```

    === "Go"
        *   `event.Actions.TransferToAgent` (string): 制御が指定されたエージェントに渡されるべきです。
        *   `event.Actions.Escalate` (bool): ループが終了するべきです。
        *   `event.Actions.SkipSummarization` (bool): ツールの結果がLLMによって要約されるべきではありません。
        ```go
        import (
            "fmt"
            "google.golang.org/adk/session"
        )

        func handleControlFlow(event *session.Event) {
            if event.Actions.TransferToAgent != "" {
                fmt.Printf("  シグナル: %s に転送\n", event.Actions.TransferToAgent)
            }
            if event.Actions.Escalate {
                fmt.Println("  シグナル: エスカレート (ループ終了)")
            }
            if event.Actions.SkipSummarization {
                fmt.Println("  シグナル: ツール結果の要約をスキップ")
            }
        }
        ```

    === "Java"
        *   `event.actions().transferToAgent()` (`Optional<String>`を返す): 制御が指定されたエージェントに渡されるべきです。
        *   `event.actions().escalate()` (`Optional<Boolean>`を返す): ループが終了するべきです。
        *   `event.actions().skipSummarization()` (`Optional<Boolean>`を返す): ツールの結果がLLMによって要約されるべきではありません。

        ```java
        import com.google.adk.events.EventActions;
        import java.util.Optional;

        EventActions actions = event.actions(); // event.actions()がnullでないと仮定
        if (actions != null) {
            Optional<String> transferAgent = actions.transferToAgent();
            if (transferAgent.isPresent()) {
                System.out.println("  シグナル: " + transferAgent.get() + " に転送");
            }

            Optional<Boolean> escalate = actions.escalate();
            if (escalate.orElse(false)) { // または escalate.isPresent() && escalate.get()
                System.out.println("  シグナル: エスカレート (ループ終了)");
            }

            Optional<Boolean> skipSummarization = actions.skipSummarization();
            if (skipSummarization.orElse(false)) { // または skipSummarization.isPresent() && skipSummarization.get()
                System.out.println("  シグナル: ツール結果の要約をスキップ");
            }
        }
        ```

### イベントが「最終的な」応答であるかの判断

組み込みのヘルパーメソッド`event.is_final_response()`を使用して、ターンのエージェントの完全な出力として表示するのに適したイベントを特定します。

*   **目的:** 最終的なユーザー向けメッセージから中間ステップ（ツール呼び出し、部分的なストリーミングテキスト、内部の状態更新など）を除外します。
*   **いつ`True`になるか？**
    1.  イベントにツールの結果（`function_response`）が含まれ、`skip_summarization`が`True`の場合。
    2.  イベントに`is_long_running=True`とマークされたツールのツール呼び出し（`function_call`）が含まれる場合。Javaでは、`longRunningToolIds`リストが空でないか確認します：
        *   `event.longRunningToolIds().isPresent() && !event.longRunningToolIds().get().isEmpty()`が`true`の場合。
    3.  または、以下の**すべて**が満たされた場合：
        *   関数呼び出しがない（`get_function_calls()`が空）。
        *   関数応答がない（`get_function_responses()`が空）。
        *   部分的なストリームチャンクではない（`partial`が`True`ではない）。
        *   さらなる処理/表示が必要な可能性のあるコード実行結果で終わらない。
*   **使用法:** アプリケーションロジックでイベントストリームをフィルタリングします。

    === "Python"
        ```python
        # 擬似コード: アプリケーションでの最終応答の処理 (Python)
        # full_response_text = ""
        # async for event in runner.run_async(...):
        #     # 必要に応じてストリーミングテキストを蓄積...
        #     if event.partial and event.content and event.content.parts and event.content.parts[0].text:
        #         full_response_text += event.content.parts[0].text
        #
        #     # 表示可能な最終イベントかどうかを確認
        #     if event.is_final_response():
        #         print("\n--- 最終出力が検出されました ---")
        #         if event.content and event.content.parts and event.content.parts[0].text:
        #              # ストリームの最後の部分であれば、蓄積したテキストを使用
        #              final_text = full_response_text + (event.content.parts[0].text if not event.partial else "")
        #              print(f"ユーザーに表示: {final_text.strip()}")
        #              full_response_text = "" # アキュムレータをリセット
        #         elif event.actions and event.actions.skip_summarization and event.get_function_responses():
        #              # 必要に応じて生のツール結果の表示を処理
        #              response_data = event.get_function_responses()[0].response
        #              print(f"生のツール結果を表示: {response_data}")
        #         elif hasattr(event, 'long_running_tool_ids') and event.long_running_tool_ids:
        #              print("メッセージを表示: ツールはバックグラウンドで実行中です...")
        #         else:
        #              # 該当する場合、他のタイプの最終応答を処理
        #              print("表示: 最終的な非テキスト応答またはシグナル。")
        ```

    === "Go"

        ```go
        // 擬似コード: アプリケーションでの最終応答の処理 (Go)
        import (
            "fmt"
            "strings"
            "google.golang.org/adk/session"
            "google.golang.org/genai"
        )

        // isFinalResponse は、イベントが表示に適した最終応答であるかを確認します。
        func isFinalResponse(event *session.Event) bool {
            if event.LLMResponse != nil {
                // 条件1: 要約スキップ付きのツール結果。
                if event.LLMResponse.Content != nil && len(event.LLMResponse.Content.FunctionResponses()) > 0 && event.Actions.SkipSummarization {
                    return true
                }
                // 条件2: 長時間実行されるツール呼び出し。
                if len(event.LongRunningToolIDs) > 0 {
                    return true
                }
                // 条件3: ツール呼び出しや応答のない完全なメッセージ。
                if (event.LLMResponse.Content == nil ||
                    (len(event.LLMResponse.Content.FunctionCalls()) == 0 && len(event.LLMResponse.Content.FunctionResponses()) == 0)) &&
                    !event.LLMResponse.Partial {
                    return true
                }
            }
            return false
        }

        func handleFinalResponses() {
            var fullResponseText strings.Builder
            // for event := range runner.Run(...) { // ループの例
            // 	// 必要に応じてストリーミングテキストを蓄積...
            // 	if event.LLMResponse != nil && event.LLMResponse.Partial && event.LLMResponse.Content != nil {
            // 		if len(event.LLMResponse.Content.Parts) > 0 && event.LLMResponse.Content.Parts[0].Text != "" {
            // 			fullResponseText.WriteString(event.LLMResponse.Content.Parts[0].Text)
            // 		}
            // 	}
            //
            // 	// 表示可能な最終イベントかどうかを確認
            // 	if isFinalResponse(event) {
            // 		fmt.Println("\n--- 最終出力が検出されました ---")
            // 		if event.LLMResponse != nil && event.LLMResponse.Content != nil {
            // 			if len(event.LLMResponse.Content.Parts) > 0 && event.LLMResponse.Content.Parts[0].Text != "" {
            // 				// ストリームの最後の部分であれば、蓄積したテキストを使用
            // 				finalText := fullResponseText.String()
            // 				if !event.LLMResponse.Partial {
            // 					finalText += event.LLMResponse.Content.Parts[0].Text
            // 				}
            // 				fmt.Printf("ユーザーに表示: %s\n", strings.TrimSpace(finalText))
            // 				fullResponseText.Reset() // アキュムレータをリセット
            // 			}
            // 		} else if event.Actions.SkipSummarization && event.LLMResponse.Content != nil && len(event.LLMResponse.Content.FunctionResponses()) > 0 {
            // 			// 必要に応じて生のツール結果の表示を処理
            // 			responseData := event.LLMResponse.Content.FunctionResponses()[0].Response
            // 			fmt.Printf("生のツール結果を表示: %v\n", responseData)
            // 		} else if len(event.LongRunningToolIDs) > 0 {
            // 			fmt.Println("メッセージを表示: ツールはバックグラウンドで実行中です...")
            // 		} else {
            // 			// 該当する場合、他のタイプの最終応答を処理
            // 			fmt.Println("表示: 最終的な非テキスト応答またはシグナル。")
            // 		}
            // 	}
            // }
        }
        ```

    === "Java"
        ```java
        // 擬似コード: アプリケーションでの最終応答の処理 (Java)
        import com.google.adk.events.Event;
        import com.google.genai.types.Content;
        import com.google.genai.types.FunctionResponse;
        import java.util.Map;

        StringBuilder fullResponseText = new StringBuilder();
        runner.run(...).forEach(event -> { // イベントのストリームを想定
             // 必要に応じてストリーミングテキストを蓄積...
             if (event.partial().orElse(false) && event.content().isPresent()) {
                 event.content().flatMap(Content::parts).ifPresent(parts -> {
                     if (!parts.isEmpty() && parts.get(0).text().isPresent()) {
                         fullResponseText.append(parts.get(0).text().get());
                    }
                 });
             }

             // 表示可能な最終イベントかどうかを確認
             if (event.finalResponse()) { // Event.java のメソッドを使用
                 System.out.println("\n--- 最終出力が検出されました ---");
                 if (event.content().isPresent() &&
                     event.content().flatMap(Content::parts).map(parts -> !parts.isEmpty() && parts.get(0).text().isPresent()).orElse(false)) {
                     // ストリームの最後の部分であれば、蓄積したテキストを使用
                     String eventText = event.content().get().parts().get().get(0).text().get();
                     String finalText = fullResponseText.toString() + (event.partial().orElse(false) ? "" : eventText);
                     System.out.println("ユーザーに表示: " + finalText.trim());
                     fullResponseText.setLength(0); // アキュムレータをリセット
                 } else if (event.actions() != null && event.actions().skipSummarization().orElse(false)
                            && !event.functionResponses().isEmpty()) {
                     // 必要に応じて生のツール結果の表示を処理,
                     // 特に finalResponse() が他の条件で true であった場合、
                     // または finalResponse() に関係なく要約がスキップされた結果を表示したい場合
                     Map<String, Object> responseData = event.functionResponses().get(0).response().get();
                     System.out.println("生のツール結果を表示: " + responseData);
                 } else if (event.longRunningToolIds().isPresent() && !event.longRunningToolIds().get().isEmpty()) {
                     // このケースは event.finalResponse() でカバーされます
                     System.out.println("メッセージを表示: ツールはバックグラウンドで実行中です...");
                 } else {
                     // 該当する場合、他のタイプの最終応答を処理
                     System.out.println("表示: 最終的な非テキスト応答またはシグナル。");
                 }
             }
         });
        ```

イベントのこれらの側面を注意深く調べることで、ADKシステムを流れる豊富な情報に適切に反応する堅牢なアプリケーションを構築できます。

## イベントのフロー: 生成と処理

イベントは異なる時点で作成され、フレームワークによって体系的に処理されます。このフローを理解することは、アクションと履歴がどのように管理されるかを明確にするのに役立ちます。

*   **生成元:**
    *   **ユーザー入力:** `Runner`は通常、最初のユーザーメッセージや会話の途中の入力を`author='user'`として`Event`にラップします。
    *   **エージェントロジック:** エージェント（`BaseAgent`, `LlmAgent`）は、応答を伝えたりアクションをシグナルしたりするために、明示的に`yield Event(...)`オブジェクト（`author=self.name`と設定）を生成します。
    *   **LLM応答:** ADKモデル統合レイヤーは、生のLLM出力（テキスト、関数呼び出し、エラー）を、呼び出し元のエージェントが作成者である`Event`オブジェクトに変換します。
    *   **ツールの結果:** ツールが実行された後、フレームワークは`function_response`を含む`Event`を生成します。`author`は通常ツールをリクエストしたエージェントであり、`content`内の`role`はLLMの履歴のために`'user'`に設定されます。

*   **処理フロー:**
    1.  **生成/返却:** イベントがそのソースによって生成され、yield（Python）されるか、返却/発行（Java）されます。
    2.  **ランナーが受信:** エージェントを実行しているメインの`Runner`がイベントを受け取ります。
    3.  **SessionServiceによる処理:** `Runner`はイベントを設定済みの`SessionService`に送信します。これは重要なステップです：
        *   **デルタの適用:** サービスは`event.actions.state_delta`を`session.state`にマージし、`event.actions.artifact_delta`に基づいて内部レコードを更新します。（注：実際のアーティファクトの*保存*は、通常`context.save_artifact`が呼ばれたときにもっと早く行われています）。
        *   **メタデータの最終決定:** 存在しない場合は一意の`event.id`を割り当て、`event.timestamp`を更新することがあります。
        *   **履歴への永続化:** 処理されたイベントを`session.events`リストに追加します。
    4.  **外部への生成:** `Runner`は処理されたイベントを呼び出し元のアプリケーション（例：`runner.run_async`を呼び出したコード）にyield（Python）するか、返却/発行（Java）します。

このフローにより、状態の変更と履歴が各イベントの通信内容とともに一貫して記録されることが保証されます。

## 一般的なイベントの例（説明的なパターン）

ストリームで見られる可能性のある典型的なイベントの簡潔な例を以下に示します：

*   **ユーザー入力:**
    ```json
    {
      "author": "user",
      "invocation_id": "e-xyz...",
      "content": {"parts": [{"text": "来週の火曜日にロンドン行きのフライトを予約してください"}]}
      // actions は通常空です
    }
    ```
*   **エージェントの最終テキスト応答:** (`is_final_response() == True`)
    ```json
    {
      "author": "TravelAgent",
      "invocation_id": "e-xyz...",
      "content": {"parts": [{"text": "はい、承知いたしました。出発都市を確認していただけますか？"}]},
      "partial": false,
      "turn_complete": true
      // actions には state delta などが含まれる場合があります
    }
    ```
*   **エージェントのストリーミングテキスト応答:** (`is_final_response() == False`)
    ```json
    {
      "author": "SummaryAgent",
      "invocation_id": "e-abc...",
      "content": {"parts": [{"text": "この文書は主に3つの点について論じています："}]},
      "partial": true,
      "turn_complete": false
    }
    // ... さらに partial=True のイベントが続きます ...
    ```
*   **ツール呼び出しリクエスト (LLMによる):** (`is_final_response() == False`)
    ```json
    {
      "author": "TravelAgent",
      "invocation_id": "e-xyz...",
      "content": {"parts": [{"function_call": {"name": "find_airports", "args": {"city": "London"}}}]}
      // actions は通常空です
    }
    ```
*   **ツール結果の提供 (LLMへ):** (`is_final_response()`は`skip_summarization`に依存)
    ```json
    {
      "author": "TravelAgent", // 作成者は呼び出しをリクエストしたエージェント
      "invocation_id": "e-xyz...",
      "content": {
        "role": "user", // LLMの履歴用のロール
        "parts": [{"function_response": {"name": "find_airports", "response": {"result": ["LHR", "LGW", "STN"]}}}]
      }
      // actions に skip_summarization=True が含まれる場合があります
    }
    ```
*   **状態/アーティファクト更新のみ:** (`is_final_response() == False`)
    ```json
    {
      "author": "InternalUpdater",
      "invocation_id": "e-def...",
      "content": null,
      "actions": {
        "state_delta": {"user_status": "verified"},
        "artifact_delta": {"verification_doc.pdf": 2}
      }
    }
    ```
*   **エージェント転送シグナル:** (`is_final_response() == False`)
    ```json
    {
      "author": "OrchestratorAgent",
      "invocation_id": "e-789...",
      "content": {"parts": [{"function_call": {"name": "transfer_to_agent", "args": {"agent_name": "BillingAgent"}}}]},
      "actions": {"transfer_to_agent": "BillingAgent"} // フレームワークによって追加
    }
    ```
*   **ループエスカレーションシグナル:** (`is_final_response() == False`)
    ```json
    {
      "author": "CheckerAgent",
      "invocation_id": "e-loop...",
      "content": {"parts": [{"text": "最大リトライ回数に達しました。"}]}, // オプショナルなコンテンツ
      "actions": {"escalate": true}
    }
    ```

## 追加のコンテキストとイベントの詳細

中核となる概念に加えて、特定のユースケースで重要となるコンテキストとイベントに関するいくつかの詳細を以下に示します：

1.  **`ToolContext.function_call_id` (ツールアクションのリンク):**
    *   LLMがツール（FunctionCall）をリクエストすると、そのリクエストにはIDがあります。ツール関数に提供される`ToolContext`には、この`function_call_id`が含まれています。
    *   **重要性:** このIDは、認証などのアクションを、それを開始した特定のツールリクエストにリンクするために不可欠です。特に1ターンで複数のツールが呼び出される場合に重要です。フレームワークは内部でこのIDを使用します。

2.  **状態/アーティファクトの変更が記録される方法:**
    *   `CallbackContext`または`ToolContext`を使用して状態を変更したり、アーティファクトを保存したりしても、これらの変更はすぐに永続ストレージに書き込まれるわけではありません。
    *   代わりに、`EventActions`オブジェクト内の`state_delta`および`artifact_delta`フィールドに移入されます。
    *   この`EventActions`オブジェクトは、変更後に生成された*次のイベント*（例：エージェントの応答やツール結果イベント）にアタッチされます。
    *   `SessionService.append_event`メソッドは、入ってくるイベントからこれらのデルタを読み取り、セッションの永続的な状態とアーティファクトレコードに適用します。これにより、変更がイベントストリームと時系列で結びつけられることが保証されます。

3.  **状態スコープのプレフィックス (`app:`, `user:`, `temp:`):**
    *   `context.state`を介して状態を管理する際に、オプションでプレフィックスを使用できます：
        *   `app:my_setting`: アプリケーション全体に関連する状態を示唆します（永続的な`SessionService`が必要です）。
        *   `user:user_preference`: セッションをまたいで特定のユーザーに関連する状態を示唆します（永続的な`SessionService`が必要です）。
        *   `temp:intermediate_result`またはプレフィックスなし: 通常、現在の呼び出しに対するセッション固有または一時的な状態です。
    *   基盤となる`SessionService`が、永続性のためにこれらのプレフィックスをどのように処理するかを決定します。

4.  **エラーイベント:**
    *   `Event`はエラーを表すことができます。`event.error_code`および`event.error_message`フィールド（`LlmResponse`から継承）を確認してください。
    *   エラーはLLM（例：セーフティフィルター、リソース制限）から発生することもあれば、ツールが致命的に失敗した場合にフレームワークによってパッケージ化される可能性もあります。典型的なツール固有のエラーについては、ツールの`FunctionResponse`コンテンツを確認してください。
    ```json
    // エラーイベントの例（概念的）
    {
      "author": "LLMAgent",
      "invocation_id": "e-err...",
      "content": null,
      "error_code": "SAFETY_FILTER_TRIGGERED",
      "error_message": "セーフティ設定により応答がブロックされました。",
      "actions": {}
    }
    ```

これらの詳細は、ツールの認証、状態の永続性スコープ、イベントストリーム内のエラー処理を含む高度なユースケースのためのより完全な全体像を提供します。

## イベントを扱う際のベストプラクティス

ADKアプリケーションでイベントを効果的に使用するためには：

*   **明確な作成者:** カスタムエージェントを構築する際は、履歴内のエージェントアクションの帰属が正しいことを確認してください。フレームワークは通常、LLM/ツールイベントの作成者を正しく処理します。

    === "Python"
        `BaseAgent`のサブクラスで`yield Event(author=self.name, ...)`を使用します。

    === "Go"
        カスタムエージェントの`Run`メソッドでは、フレームワークが通常作成者を処理します。イベントを手動で作成する場合は、作成者を設定します：`yield(&session.Event{Author: a.name, ...}, nil)`

    === "Java"
        カスタムエージェントロジックで`Event`を構築する際は、作成者を設定します。例：`Event.builder().author(this.getAgentName()) // ... .build();`

*   **セマンティックなコンテンツとアクション:** 中核となるメッセージ/データ（テキスト、関数呼び出し/応答）には`event.content`を使用します。副作用（状態/アーティファクトのデルタ）や制御フロー（`transfer`, `escalate`, `skip_summarization`）のシグナリングには、`event.actions`を具体的に使用します。
*   **べき等性の認識:** `SessionService`が`event.actions`でシグナルされた状態/アーティファクトの変更を適用する責任があることを理解してください。ADKサービスは一貫性を目指していますが、アプリケーションロジックがイベントを再処理する場合の潜在的な下流への影響を考慮してください。
*   **`is_final_response()`の使用:** アプリケーション/UIレイヤーでこのヘルパーメソッドに依存して、完全なユーザー向けテキスト応答を特定してください。そのロジックを手動で複製することは避けてください。
*   **履歴の活用:** セッションのイベントリストは、主要なデバッグツールです。作成者、コンテンツ、アクションのシーケンスを調べて実行をトレースし、問題を診断してください。
*   **メタデータの使用:** `invocation_id`を使用して、単一のユーザーインタラクション内のすべてのイベントを相関させます。`event.id`を使用して、特定のユニークな発生を参照します。

イベントを、そのコンテンツとアクションに明確な目的を持つ構造化されたメッセージとして扱うことが、ADKで複雑なエージェントの挙動を構築、デバッグ、管理するための鍵です。