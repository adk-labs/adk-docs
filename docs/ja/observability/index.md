# エージェントの可観測性

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-kotlin">Kotlin v0.1.0</span>
</div>

エージェントの可観測性は、外部テレメトリと構造化ログを分析することで、
推論トレース、ツール呼び出し、潜在モデル出力 (latent model outputs) を含む
システムの内部状態を測定できるようにします。エージェントを構築する際、
実行中の挙動をデバッグ・診断するためにこれらの機能が必要になる場合があります。
一定以上の複雑さを持つエージェントでは、基本的な入出力モニタリングだけでは
通常不十分です。

Agent Development Kit (ADK) は、エージェントの監視とデバッグのために、
[ロギング](/ja/observability/logging/)、[メトリクス](/ja/observability/metrics/)、
[トレース](/ja/observability/traces/) を組み込みで提供します。ただし、監視と
分析には、より高度な [可観測性 ADK 連携](/ja/integrations/?topic=observability)
を検討する必要がある場合があります。

## クイックスタート: Kotlinで可観測性を有効にする

Kotlinでは、トレース用にOpenTelemetryを構成し、詳細なコンソール出力に`LoggingPlugin`を使用することで、包括的な可観測性を有効にできます。

```kotlin
--8<-- "examples/kotlin/snippets/observability/SetupExample.kt:full_example"
```

!!! tip "可観測性向け ADK 連携"
    ADK 向けの事前構築済み可観測性ライブラリの一覧は
    [ツールと統合](/ja/integrations/?topic=observability) を参照してください。
