# Geminiによるコンテキストキャッシュ

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.15.0</span>
</div>

エージェントを使用してタスクを完了する場合、拡張された指示や大規模なデータセットを複数のエージェントリクエストにわたって生成AIモデルに再利用したい場合があります。エージェントリクエストごとにこのデータを再送信すると、時間がかかり、非効率的で、コストがかかる可能性があります。生成AIモデルでコンテキストキャッシュ機能を使用すると、応答を大幅に高速化し、リクエストごとにモデルに送信されるトークンの数を減らすことができます。

ADKコンテキストキャッシュ機能を使用すると、Gemini 2.0以降のモデルを含む、それをサポートする生成AIモデルでリクエストデータをキャッシュできます。このドキュメントでは、この機能の構成方法と使用方法について説明します。

## コンテキストキャッシュの構成

エージェントをラップするADK `App`オブジェクトレベルでコンテキストキャッシュ機能を構成します。次のコードサンプルに示すように、`ContextCacheConfig`クラスを使用してこれらの設定を構成します。

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

## 構成設定

`ContextCacheConfig`クラスには、エージェントのキャッシュの動作を制御する次の設定があります。これらの設定を構成すると、アプリ内のすべてのエージェントに適用されます。

-   **`min_tokens`**（int）：キャッシュを有効にするためにリクエストで必要な最小トークン数。この設定により、パフォーマンス上の利点がごくわずかである非常に小さなリクエストのキャッシュのオーバーヘッドを回避できます。デフォルトは`0`です。
-   **`ttl_seconds`**（int）：キャッシュの存続時間（TTL）（秒）。この設定は、キャッシュされたコンテンツが更新される前に保存される期間を決定します。デフォルトは`1800`（30分）です。
-   **`cache_intervals`**（int）：同じキャッシュされたコンテンツが期限切れになる前に使用できる最大回数。この設定により、TTLが期限切れになっていなくても、キャッシュが更新される頻度を制御できます。デフォルトは`10`です。

## 次のステップ

コンテキストキャッシュ機能の使用方法とテスト方法の完全な実装については、次のサンプルを参照してください。

-   [`cache_analysis`](https://github.com/google/adk-python/tree/main/contributing/samples/cache_analysis)：
    コンテキストキャッシュのパフォーマンスを分析する方法を示すコードサンプル。

ユースケースでセッション全体で使用される指示を提供する必要がある場合は、エージェントの`static_instruction`パラメータの使用を検討してください。これにより、生成モデルのシステム指示を修正できます。詳細については、次のサンプルコードを参照してください。

-   [`static_instruction`](https://github.com/google/adk-python/tree/main/contributing/samples/static_instruction)：
    静的な指示を使用したデジタルペットエージェントの実装。
