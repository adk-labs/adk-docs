# 再試行とタイムアウトによるノード障害の処理

<div class="language-support-tag">
  <span class="lst-supported">ADK でのサポート</span><span class="lst-python">Python v2.0.0</span><span class="lst-typescript">TypeScript v2.0.0</span><span class="lst-go">Go v2.0.0</span><span class="lst-java">Java v1.14.0</span><span class="lst-kotlin">Kotlin v1.2.0</span>
</div>

グラフベースのワークフロー内のノードは、モデル API、リモートツール、データベースなど、断続的に失敗したり応答が遅くなったりするサービスを呼び出すことがよくあります。Agent Development Kit（ADK）を使用すると、各ノードに再試行ポリシー（retry policy）とタイムアウト（timeout）を設定できるため、ノードはワークフロー全体を失敗させることなく一時的な障害から回復でき、停滞したノードはワークフローをブロックする代わりに一定時間後に失敗させることができます。再試行とタイムアウト機能を使用すると、次のことが可能になります。

-   接続エラーで失敗したツール呼び出しを再試行し、リモートサービスが回復する時間を確保するために試行間の待機時間を徐々に長くする。
-   30 秒以内に応答しないモデル呼び出しを停止し、再試行する。
-   2 回目の試行で成功する可能性が高いエラーのみを再試行し、その他のすべてのエラーでは即座に失敗させる。

再試行ポリシーを持つノードは、失敗すると試行が成功するか最大試行回数に達するまで再実行されます。最大試行回数に達した時点で初めて、障害が残りのワークフローに伝わります。再試行ポリシーを持たないノードは再試行されません。

!!! example "TypeScript、Java、および Kotlin では実験的機能"
    ADK TypeScript、ADK Java、および ADK Kotlin では、ノードの再試行とタイムアウトが依存するワークフロー API は実験的リリースです。これらの API には制限がある場合があり、これらの言語での本番環境での使用は推奨されません。

## はじめに {#get-started}

次の例では、2 つのノードからなるワークフローを構築します。最初のノードは不安定な天気予報サービスを呼び出し、合計 3 回の試行を許可し、最初の再試行の前に 1 秒待機し、サービスエラーとタイムアウトのみを再試行し、各試行を 10 秒に制限するように設定されています。2 番目のノードは結果を報告します。

=== "Python"

    ```python
    import random

    from google.adk import Context
    from google.adk import Event
    from google.adk import Workflow
    from google.adk.workflow import NodeTimeoutError
    from google.adk.workflow import RetryConfig
    from google.adk.workflow import node


    class ServiceUnavailableError(Exception):
      """Stands in for a transient failure from a remote service."""


    @node(
        retry_config=RetryConfig(
            max_attempts=3,  # 1 original attempt + 2 retries
            initial_delay=1.0,  # seconds before the first retry
            exceptions=[ServiceUnavailableError, NodeTimeoutError],
        ),
        timeout=10.0,  # seconds allowed for each attempt
    )
    async def fetch_forecast(ctx: Context):
      """Simulates an unreliable call to a forecast service."""
      yield Event(message=f"Fetching forecast, attempt {ctx.attempt_count}")
      if random.random() < 0.5:
        raise ServiceUnavailableError("Forecast service unavailable")
      yield "sunny"


    def report_forecast(node_input: str):
      return Event(message=f"The forecast is {node_input}.")


    root_agent = Workflow(
        name="forecast_workflow",
        edges=[("START", fetch_forecast, report_forecast)],
    )
    ```

=== "TypeScript"

    `node()` のオプションとして `retryConfig` と `timeout` を渡します。遅延とタイムアウトの単位は秒です。

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/retry/get_started.ts:get-started"
    ```

=== "Go"

    ノードのコンストラクタに渡す `workflow.NodeConfig` で `RetryConfig` と `Timeout` を設定します。`workflow.DefaultRetryConfig()` から開始し、必要なフィールドのみを変更してください。

    ```go
    --8<-- "examples/go/snippets/graphs/retry/main.go:get-started"
    ```

=== "Java"

    `Node` 実装の `config()` メソッドから `NodeConfig` を返します。

    ```java
    import com.google.adk.agents.Context;
    import com.google.adk.workflow.Edge;
    import com.google.adk.workflow.Node;
    import com.google.adk.workflow.NodeConfig;
    import com.google.adk.workflow.NodeTimeoutException;
    import com.google.adk.workflow.RetryConfig;
    import com.google.adk.workflow.Start;
    import com.google.adk.workflow.Workflow;
    import io.reactivex.rxjava3.core.Flowable;
    import java.time.Duration;
    import java.util.concurrent.ThreadLocalRandom;

    public final class ForecastWorkflow {

      /** Stands in for a transient failure from a remote service. */
      static final class ServiceUnavailableException extends RuntimeException {
        ServiceUnavailableException(String message) {
          super(message);
        }
      }

      /** Simulates an unreliable call to a forecast service. */
      static final class FetchForecastNode implements Node {
        private static final NodeConfig CONFIG =
            NodeConfig.builder()
                .retryConfig(
                    RetryConfig.builder()
                        .maxAttempts(3) // 1 original attempt + 2 retries
                        .initialDelay(Duration.ofSeconds(1))
                        .exceptionClasses(
                            ServiceUnavailableException.class, NodeTimeoutException.class)
                        .build())
                .timeout(Duration.ofSeconds(10)) // limit for each attempt
                .build();

        @Override
        public String name() {
          return "fetch_forecast";
        }

        @Override
        public NodeConfig config() {
          return CONFIG;
        }

        @Override
        public Flowable<?> runNode(Context context, Object nodeInput) {
          if (ThreadLocalRandom.current().nextDouble() < 0.5) {
            return Flowable.error(
                new ServiceUnavailableException(
                    "Forecast service unavailable, attempt " + context.attemptCount()));
          }
          return Flowable.just("sunny");
        }
      }

      public static Workflow create() {
        return Workflow.builder()
            .name("forecast_workflow")
            .edges(new Edge(Start.INSTANCE, new FetchForecastNode()))
            .build();
      }
    }
    ```

=== "Kotlin"

    `node()` に `NodeConfig` を渡します。ワークフロー API を使用するには、`ExperimentalWorkflowApi` をオプトインする必要があります。

    ```kotlin
    --8<-- "examples/kotlin/snippets/graphs/RetryExample.kt:get-started"
    ```

`fetch_forecast` がサービスエラーで失敗するかタイムアウトを超過すると、ADK エージェントは待機してから同じ入力でノードを再実行します。次のノードである `report_forecast` は、試行が成功した後にのみ実行されます。3 回の試行がすべて失敗した場合、ノードは最後の試行のエラーで失敗し、ワークフローもそれに伴って失敗します。Go を除くすべての言語では、ノードコンテキストが 1 から始まる試行回数（attempt count）を提供するため、コード内で何回目の試行が実行中であるかを判別できます。

## 再試行の構成

再試行ポリシーは、ノードの実行回数、試行間の ADK の待機時間、および再試行を開始するエラーの 3 つを制御します。

-   **試行回数（Attempts）:** 最大試行回数の値には最初の試行が含まれるため、値を 3 にすると 2 回の再試行が許可されます。値を 0 または 1 にすると再試行は無効になります。
-   **遅延（Delay）:** 最初の再試行前の待機時間が初期遅延（initial delay）です。ADK はそれ以降の各待機時間にバックオフ係数（backoff factor）を乗算するため、デフォルトの 1 秒と 2.0 では、ジッター（jitter）適用前の基本待機時間は 1、2、4、8 秒になります。最大遅延（maximum delay）は各待機時間の上限を制限します。
-   **ジッター（Jitter）:** 同時に失敗した多数のノードがすべて同じ瞬間に再試行するのを防ぐため、システムは各待機時間に対して最大で「ジッター係数 × 遅延」のランダムな値を加算または減算します。テストなどで固定の遅延にするには、ジッターを 0 に設定してください。

ワークフローで再試行がどれだけ効果的に機能するかには、次の設計上の判断が最も大きく影響します。

-   **一時的なエラーのみを再試行する。** デフォルトでは、再試行ポリシーはほぼすべてのエラーを再試行します。不正な入力やバグが原因のエラーは何度試行しても同じように失敗するため、再試行しても失敗が遅れるだけです。接続エラー、レート制限エラー、タイムアウトなど、後の試行で成功する可能性があるエラータイプのみを指定してください。各言語でのエラーの一致方法の詳細については、[構成オプション](#configuration-options)をご覧ください。
-   **失敗する可能性のあるノードにポリシーを設定する。** Python、Java、および Kotlin では、ネストされたワークフローに再試行ポリシーを設定することもでき、その場合は内部のどのノードが失敗してもネストされたワークフロー全体が再試行されます。不安定なサービスを呼び出す個別のノードにポリシーを設定する方が、再試行される処理が少なくなり、より細かく制御できます。
-   **再試行される処理を繰り返し実行しても安全（べき等）にする。** 再試行ではノード全体が再度実行されます。ノードが失敗する前に外部システムに書き込みを行っている場合、その書き込みが複数回発生する可能性があります。繰り返しても追加の影響が出ないように操作を設計するか、副作用を伴う処理を不安定な呼び出しが成功した後に実行される別のノードに移動してください。

## ノードのタイムアウトを設定する

タイムアウトは、ノードの 1 回の試行が実行できる時間を制限します。この制限は再試行全体の合計時間ではなく各試行に個別に適用され、試行間の待機時間はカウントされません。試行がタイムアウトを超えて実行されると、ADK はその試行を停止し、失敗として扱います。

-   Python、TypeScript、Java、および Kotlin では、次の表に示すノードタイムアウトエラーで試行が失敗します。
-   Go では、ノードのコンテキストがデッドラインに達し、`context.DeadlineExceeded` で試行が失敗します。

ノードにタイムアウトエラーを対象とする再試行ポリシーがある場合、ADK はタイムアウトした試行を他の障害と同様に再試行します。ポリシーで特定のエラータイプを指定する場合は、[はじめに](#get-started)の例のようにタイムアウトエラーも含めてください。再試行ポリシーのないタイムアウトは、最初に発生した時点でノードを失敗させます。

| 言語 | タイムアウト設定 | タイムアウトエラー | 再試行ポリシーに指定する名前 |
| :--- | :--- | :--- | :--- |
| Python | 秒単位の `timeout` | `NodeTimeoutError` | `NodeTimeoutError` |
| TypeScript | 秒単位の `timeout` | `NodeTimeoutError` | `NodeTimeoutError` |
| Go | `time.Duration` としての `NodeConfig.Timeout` | `context.DeadlineExceeded` | `ShouldRetry` 内で `errors.Is` を使用して一致させる |
| Java | `Duration` としての `NodeConfig.timeout` | `NodeTimeoutException` | `NodeTimeoutException` |
| Kotlin | `Duration` としての `NodeConfig.timeout` | `NodeTimeoutError` | `NodeTimeoutError` |

試行の停止はキャンセル処理に依存しており、キャンセルがコードに伝わる仕組みは言語によって異なります。

-   **Go:** ノードの `agent.Context` がデッドラインを保持します。デッドラインが過ぎたときにノードが戻るよう、ノードが行う呼び出しにコンテキストを渡すか、`ctx.Done()` を確認してください。
-   **TypeScript:** タイムアウトが発生すると、ADK はノードからのイベント読み取りを停止します。HTTP リクエストなど、ノードが開始した処理もキャンセルするには、その処理に `ctx.abortSignal` を渡してください。
-   **Kotlin:** ADK はコルーチン内で試行を実行し、タイムアウトが発生するとそのコルーチンをキャンセルします。中断ポイント（suspension point）に到達しないコードは、到達するまで実行され続けます。

## 構成オプション {#configuration-options}

再試行ポリシーには、すべての言語で同じオプションがあります。期間の単位は、Python と TypeScript では秒であり、Go、Java、および Kotlin では各言語の期間（duration）型を使用します。

| オプション | デフォルト | 説明 |
| :--- | :--- | :--- |
| 最大試行回数（Maximum attempts） | `5` | 最初の試行を含む試行回数。0 または 1 を指定すると再試行が無効になります。 |
| 初期遅延（Initial delay） | 1 秒 | 最初の再試行までの待機時間。 |
| 最大遅延（Maximum delay） | 60 秒 | 試行間の待機時間の上限。 |
| バックオフ係数（Backoff factor） | `2.0` | 各試行後の待機時間に適用される乗数。 |
| ジッター（Jitter） | `1.0` | 各待機時間に対する割合として適用されるランダムなばらつき。`0` にすると固定の待機時間になります。 |
| 再試行するエラー（Errors to retry） | すべてのエラー | 再試行を開始するエラー。次のリストをご覧ください。 |

再試行するエラーの選択方法は言語ごとに異なります。

-   **Python:** `exceptions` 設定には例外クラスまたはクラス名を指定します。指定されたクラスはそのサブクラスにも一致します。
-   **TypeScript:** `exceptions` 設定にはエラークラスまたはクラス名を指定します。エラーのクラス名または `name` プロパティがリストに含まれている場合に一致します。ADK はクラス階層を確認しません。
-   **Go:** `ShouldRetry` 設定は、エラーを受け取り、再試行する場合に `true` を返す関数です。デフォルトでは、`workflow.ErrInputValidation` を除くすべてのエラーを再試行します。
-   **Java:** `exceptions` 設定には単純クラス名（simple class name）を指定し、完全一致で判定されます。`exceptionClasses` 設定にはクラスを指定し、そのサブクラスにも一致します。ADK は `WorkflowConfigurationException` を決して再試行しません。
-   **Kotlin:** `exceptions` 設定には単純クラス名を指定し、完全一致で判定されます。ADK は `WorkflowConfigurationException` を決して再試行しません。

!!! warning "Go: 未設定のフィールドはデフォルト値ではなくゼロ値になります"
    Go では、構造体リテラルとして構築された `RetryConfig` は、設定していないすべてのフィールドにデフォルト値ではなくゼロ値を使用します。たとえば、`&workflow.RetryConfig{MaxAttempts: 3}` は試行間に遅延なしで再試行します。代わりに `workflow.DefaultRetryConfig()` から開始し、必要なフィールドを上書きしてください。また、Go は `MaxDelay` を適用した後にジッターを適用するため、1 回の待機時間がジッターの割合分だけ `MaxDelay` より長くなる場合があります。

## 制限事項

-   **試行回数は保存されません。** ADK は、ノードの現在の実行に対してのみ試行回数をメモリ内に保持します。たとえば[人間入力](/ja/graphs/human-input/)のためにワークフローが一時停止した場合や、アプリケーションが再起動した場合、ワークフローの再開後に再実行されるノードは、すべての試行回数が利用可能な状態で試行 1 から開始されます。

## 次のステップ

-   [エージェントワークフローのグラフルートを構築する](/ja/graphs/routes/): シーケンス、分岐、並列パスでノードを接続します。
-   [エージェントワークフローのデータ処理](/ja/graphs/data-handling/): ノード間でデータを受け渡します。
-   [エージェントワークフローの人間入力](/ja/graphs/human-input/): ワークフローを一時停止して人間に入力を求めます。
