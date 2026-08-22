# Geminiによるコンテキストキャッシュ

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.15.0</span><span class="lst-java">Java v0.1.0</span><span class="lst-kotlin">Kotlin v0.7.0</span>
</div>

エージェントを使用してタスクを完了する場合、拡張された指示や大規模なデータセットを複数のエージェントリクエストにわたって生成AIモデルに再利用したい場合があります。エージェントリクエストごとにこのデータを再送信すると、時間がかかり、非効率的で、コストがかかる可能性があります。生成AIモデルでコンテキストキャッシュ機能を使用すると、応答を大幅に高速化し、リクエストごとにモデルに送信されるトークンの数を減らすことができます。

ADKコンテキストキャッシュ機能を使用すると、Gemini 2.0以降のモデルを含む、それをサポートする生成AIモデルでリクエストデータをキャッシュできます。このドキュメントでは、この機能の構成方法と使用方法について説明します。

## コンテキストキャッシュの構成

エージェントをラップするADK `App`オブジェクトレベルでコンテキストキャッシュ機能を構成します。次のコードサンプルに示すように、`ContextCacheConfig`クラスを使用してこれらの設定を構成します。

=== "Python"

    ```python
    from google.adk import Agent
    from google.adk.apps.app import App
    from google.adk.agents.context_cache_config import ContextCacheConfig

    root_agent = Agent(
      # Gemini 2.0以降を使用するエージェントを構成する
    )

    # コンテキストキャッシュ構成でアプリを作成する
    app = App(
        name='my-caching-agent-app',
        root_agent=root_agent,
        context_cache_config=ContextCacheConfig(
            min_tokens=2048,    # キャッシュをトリガーする最小トークン
            ttl_seconds=600,    # 最大10分間保存
            cache_intervals=5,  # 5回使用後に更新
        ),
    )
    ```

=== "Java"

    ```java
    import com.google.adk.agents.BaseAgent;
    import com.google.adk.agents.ContextCacheConfig;
    import com.google.adk.apps.App;
    import java.time.Duration;

    // コンテキストキャッシュ構成で App を作成する
    App app = App.builder()
                 .name("my-caching-agent-app")
                 .rootAgent(rootAgent)
                 .contextCacheConfig(
                     new ContextCacheConfig(
                         5, /* cache_intervals（最大呼び出し回数） */
                         Duration.ofMinutes(10), /* ttl */
                         2048 /* min_tokens */))
                 .build();
    ```

=== "Kotlin"

    ```kotlin
    @file:OptIn(ExperimentalContextCachingFeature::class)

    import com.google.adk.kt.agents.ContextCacheConfig
    import com.google.adk.kt.agents.LlmAgent
    import com.google.adk.kt.annotations.ExperimentalContextCachingFeature
    import com.google.adk.kt.apps.App
    import com.google.adk.kt.models.Gemini
    import kotlin.time.Duration.Companion.minutes

    val rootAgent =
        LlmAgent(
            name = "my_caching_agent",
            // configure an agent using Gemini 2.0 or higher
            model = Gemini(name = "gemini-flash-latest"),
        )

    // Create the app with context caching configuration
    @OptIn(ExperimentalContextCachingFeature::class)
    val app =
        App(
            appName = "my-caching-agent-app",
            rootAgent = rootAgent,
            contextCacheConfig =
                ContextCacheConfig(
                    // Gemini はモデルごとに固有の最小キャッシュ可能サイズを適用します
                    minTokens = 8192,
                    ttl = 10.minutes, // 最大 10 分間保存
                    cacheIntervals = 5, // 5 回使用後に更新
                    // タイムアウト時には作成が失敗し、リクエストはキャッシュなしで進行します
                    createHttpOptions = HttpOptions(timeout = 10.seconds),
                ),
        )
    ```

## 構成設定

`ContextCacheConfig`クラスには、エージェントのキャッシュの動作を制御する次の設定があります。これらの設定を構成すると、アプリ内のすべてのエージェントに適用されます。

-   **`min_tokens`**（int）：キャッシュを有効にするためにリクエストで必要な最小トークン数。この設定により、パフォーマンス上の利点がごくわずかである非常に小さなリクエストのキャッシュのオーバーヘッドを回避できます。デフォルトは`0`です。
-   **`ttl_seconds`**（int）：キャッシュの存続時間（TTL）（秒）。この設定は、キャッシュされたコンテンツが更新される前に保存される期間を決定します。デフォルトは`1800`（30分）です。
-   **`cache_intervals`**（int）：同じキャッシュされたコンテンツが期限切れになる前に使用できる最大回数。この設定により、TTLが期限切れになっていなくても、キャッシュが更新される頻度を制御できます。デフォルトは`10`です。
-   **`create_http_options`** (HttpOptions): キャッシュ作成呼び出しの HTTP オプション。タイムアウトを設定できます。呼び出しがタイムアウトした場合、作成は失敗し、リクエストはキャッシュなしで進行します。Python および Kotlin で利用可能。デフォルトはなしです。

## キャッシュが使用されているかの確認

<div class="language-support-tag">
   <span class="lst-supported">ADKでサポート</span><span class="lst-kotlin">Kotlin v0.6.0</span>
</div>

キャッシュが有効になっている場合、LLM レスポンスに基づくイベントには、その呼び出しに対してキャッシュが何を行ったかを報告する `CacheMetadata` を含めることができます。キャッシュが無効になっている場合や、呼び出しでキャッシュ情報が生成されなかった場合は null になるため、読み取る前に確認してください。存在する場合、2 つの状態があります。`cacheName`、`expireTime`、`invocationsUsed` がすべて設定されている **アクティブ キャッシュ (active cache)** 状態と、3 つすべてが null の **フィンガープリントのみ (fingerprint-only)** 状態です。

```kotlin
--8<-- "examples/kotlin/snippets/context/CacheMetadataExample.kt:cache_metadata"
```

`expireSoon` は、キャッシュが約 2 分以内に期限切れになるか、すでに期限切れになっていることを意味します。これは自身のコードへのシグナルであり、ADK がこれに対してアクションを実行するわけではありません。ADK は、実際に `expireTime` を過ぎるか、`cacheIntervals` を超過するか、キャッシュされたプレフィックスが変更されるまで、キャッシュを再利用し続けます。

トークン数は `CacheMetadata` には含まれません。`LlmResponse.usageMetadata` から読み取ってください。

## 次のステップ

コンテキストキャッシュ機能の使用方法とテスト方法の完全な実装については、次のサンプルを参照してください。

-   [`cache_analysis`](https://github.com/google/adk-python/tree/main/contributing/samples/cache_analysis)：
    コンテキストキャッシュのパフォーマンスを分析する方法を示すコードサンプル。

ユースケースでセッション全体で使用される指示を提供する必要がある場合は、エージェントの`static_instruction`パラメータの使用を検討してください。これにより、生成モデルのシステム指示を修正できます。詳細については、次のサンプルコードを参照してください。

-   [`static_instruction`](https://github.com/google/adk-python/tree/main/contributing/samples/context_management/static_instruction)：
    静的な指示を使用したデジタルペットエージェントの実装。
