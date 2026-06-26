# パフォーマンスのためのエージェントコンテキストの圧縮

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.16.0</span><span class="lst-java">Java v0.2.0</span><span class="lst-typescript">TypeScript v0.6.0</span>
</div>

ADK エージェントは実行されながら、ユーザーの指示、取得されたデータ、ツールの応答、生成されたコンテンツを含む*コンテキスト*情報を収集します。このコンテキストデータのサイズが大きくなるにつれて、エージェントの処理時間も通常は増加します。より多くのデータがエージェントの使用する生成 AI モデルに送信されるため、処理時間が長くなり応答が遅くなります。ADK のコンテキスト圧縮機能は、指示、入力、モデルの応答を含む古いセッション履歴を要約することで、エージェントの実行中にコンテキストのサイズを削減するように設計されています。このプロセスは、コンパクトなコンテキストウィンドウを維持することにより、重要な最近のやり取りへのエージェントのアクセスを確保しつつ、**レイテンシを最適化しコストを削減**します。

圧縮は `CompactionRequestProcessor` を介して SingleFlow に直接統合されており、`EventsCompactionConfig` で設定したルールに基づいて自動的なイベント圧縮を可能にします。

## 戦略の選択

`EventsCompactionConfig` 内で、以下の戦略を使用してセッションのデータを管理できます。

- **トークンベース (基本)**: 消費された実際のトークン量に基づいてクリーンアップをトリガーします。これは絶対的なセーフティネットとして機能し、ユーザーが大量のコードブロックを貼り付けたり大容量のファイルをアップロードしたりするような、予測不可能なワークロードに最適です。
- **スライディングウィンドウ (ターンベース)**: 固定された会話ターン数の後にクリーンアップをトリガーします。これは、規則的で予測可能なテキストチャットに有用です。

両方の圧縮戦略を構成した場合、システムはトークンベースの圧縮を優先します。セッションの長さが定義されたトークンしきい値を超えると、システムはトークンベース of 圧縮をトリガーし、そのターンにおけるスライディングウィンドウ圧縮はスキップします。

## トークンベースの圧縮

トークンベースの圧縮は、イベントやターンの数ではなく、トークンまたはデータの量に基づいてコンテキスト管理をトリガーします。

### 構成設定

App オブジェクトに `EventsCompactionConfig` 設定を追加して、エージェントワークフローにトークンベースの圧縮を追加します。以下を指定する必要があります。

- **`token_threshold`**: 到達時にテール保持（tail-retention）圧縮を自動的にトリガーするトークンの安全制限です。
- **`event_retention_size`**: 圧縮がトリガーされたときに、要約されていない「生」の形式で維持される最近のイベント/やり取りの数です。これにより、即時の会話コンテキストと代名詞の解決が維持されます。

プロジェクトにこれを実装するには、次の構成を使用します。

```python
# 1. google.adk ネームスペースを使用するようにインポートパスを修正
from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.agents import Agent

# 2. ルートエージェントの初期化（App セットアップに必須）
root_agent = Agent(
    name="my_root_agent",
    description="Main coordinating agent for the workflow."
)

# 3. トークンベースの構成: 優先/事前呼び出しレイヤーの有効化
compaction_config = EventsCompactionConfig(
    token_threshold=4000,     # 実際のトークン数がこれを超えたときに圧縮をトリガー
    event_retention_size=5    # トークン制限に達したときにそのまま維持する最近の生のイベント数
)

# 4. 必須の name および root_agent フィールド、および構成オブジェクトを使用して登録
app = App(
    name="my_compacting_agent_app",
    root_agent=root_agent,
    events_compaction_config=compaction_config
)
```

## スライディングウィンドウの圧縮

コンテキスト圧縮機能は、[セッション](/ja/sessions/session/)内でのエージェントワークフローイベントデータを収集および要約するために*スライディングウィンドウ*アプローチを使用します。エージェントでこの機能を構成すると、現在のセッション内の特定のワークフローイベントまたは呼び出しのしきい値数に達したときに、古いイベントからのデータを要約します。

```python
# （任意）補助設定としてのイベントベースのスライディングウィンドウ
compaction_config = EventsCompactionConfig(
    compaction_interval=10,   # 標準圧縮の間のターン数
    overlap_size=2,           # 重複コンテキストとして保持するイベント数
```

## コンテキスト圧縮の設定

ワークフローの App オブジェクト（Python/Java）にイベント圧縮設定を追加するか、`LlmAgent`（TypeScript）で `contextCompactors` を構成することで、エージェントワークフローにコンテキスト圧縮を追加できます。設定の一部として、次のサンプルコードのように圧縮間隔と重複サイズ（Python/Java）またはトークンしきい値とイベント保持サイズ（TypeScript）を指定する必要があります。

=== "Python"

    ```python
    from google.adk.apps.app import App
    from google.adk.apps.app import EventsCompactionConfig

    app = App(
        name='my-agent',
        root_agent=root_agent,
        events_compaction_config=EventsCompactionConfig(
            compaction_interval=3,  # 3つの新しい呼び出しごとに圧縮をトリガーします。
            overlap_size=1          # 前のウィンドウからの最後の呼び出しを含めます。
        ),
    )
    ```

=== "Java"

    ```java
    import com.google.adk.apps.App;
    import com.google.adk.summarizer.EventsCompactionConfig;

    App app = App.builder()
        .name("my-agent")
        .rootAgent(rootAgent)
        .eventsCompactionConfig(EventsCompactionConfig.builder()
            .compactionInterval(3)  // 3つの新しい呼び出しごとに圧縮をトリガーします。
            .overlapSize(1)         // 前のウィンドウからの最後の呼び出しを含めます。
            .build())
        .build();
    ```

=== "TypeScript"

    ```typescript
    import {Gemini, LlmAgent, LlmSummarizer, TokenBasedContextCompactor} from '@google/adk';

    const agent = new LlmAgent({
      name: 'my-agent',
      model: 'gemini-flash-latest',
      contextCompactors: [
        new TokenBasedContextCompactor({
          tokenThreshold: 1000, // セッションが 1000 トークンを超えると圧縮をトリガーします。
          eventRetentionSize: 1, // 生イベントを少なくとも 1 件保持します（オーバーラップ）。
          summarizer: new LlmSummarizer({
            llm: new Gemini({model: 'gemini-flash-latest'}),
          }),
        }),
      ],
    });
    ```

構成されると、ADK `Runner`はセッションが間隔に達するたびにバックグラウンドで圧縮プロセスを処理します。

## コンテキスト圧縮の例

`compaction_interval`を3に、`overlap_size`を1に設定すると、イベントデータはイベント3、6、9などが完了すると圧縮されます。重複設定は、図1に示すように、2番目の要約圧縮とそれ以降の各要約のサイズを増加させます。

![コンテキスト圧縮の例のイラスト](../assets/context-compaction.svg)
**図1.** 間隔3、重複1のイベント圧縮構成のイラスト。

この例の構成では、コンテキスト圧縮タスクは次のように行われます。

1.  **イベント3が完了**: 3つのイベントすべてが要約に圧縮されます
1.  **イベント6が完了**: 前の1つのイベントの重複を含め、イベント3から6までが圧縮されます
1.  **イベント9が完了**: 前の1つのイベントの重複を含め、イベント6から9までが圧縮されます

## 設定

この機能の設定は、イベントデータが圧縮される頻度と、エージェントワークフローの実行中に保持されるデータの量を制御します。オプションで、コンパクターオブジェクトを構成できます。

*   **`compaction_interval`**: 以前のイベントデータの圧縮をトリガーする完了したイベント数を設定します。
*   **`overlap_size`**: 新しく圧縮されたコンテキストセットに含める以前に圧縮されたイベントの数を設定します。
*   **`summarizer`**: (オプション) 要約に使用する特定のAIモデルを含むサマライザーオブジェクトを定義します。詳細については、[サマライザーの定義](#define-summarizer)を参照してください。

### サマライザーを定義する {#define-summarizer}
サマライザーを定義することで、コンテキスト圧縮プロセスをカスタマイズできます。`LlmEventSummarizer`（Python/Java）または `LlmSummarizer`（TypeScript）クラスを使うと、要約に使うモデルを指定できます。次のコード例は、カスタムサマライザーを定義して構成する方法を示しています。

=== "Python"

    ```python
    from google.adk.apps.app import App, EventsCompactionConfig
    from google.adk.apps.llm_event_summarizer import LlmEventSummarizer
    from google.adk.models import Gemini

    # 要約に使用する AI モデルを定義します。
    summarization_llm = Gemini(model="gemini-flash-latest")

    # カスタムモデルでサマライザーを作成します。
    my_summarizer = LlmEventSummarizer(llm=summarization_llm)

    # カスタムサマライザーと圧縮設定で App を構成します。
    app = App(
        name='my-agent',
        root_agent=root_agent,
        events_compaction_config=EventsCompactionConfig(
            compaction_interval=3,
            overlap_size=1,
            summarizer=my_summarizer,
        ),
    )
    ```

=== "Java"

    ```java
    import com.google.adk.apps.App;
    import com.google.adk.models.Gemini;
    import com.google.adk.summarizer.EventsCompactionConfig;
    import com.google.adk.summarizer.LlmEventSummarizer;

    // 要約に使用する AI モデルを定義します。
    Gemini summarizationLlm = Gemini.builder()
        .model("gemini-flash-latest")
        .build();

    // カスタムモデルでサマライザーを作成します。
    LlmEventSummarizer mySummarizer = new LlmEventSummarizer(summarizationLlm);

    // カスタムサマライザーと圧縮設定で App を構成します。
    App app = App.builder()
        .name("my-agent")
        .rootAgent(rootAgent)
        .eventsCompactionConfig(EventsCompactionConfig.builder()
            .compactionInterval(3)
            .overlapSize(1)
            .summarizer(mySummarizer)
            .build())
        .build();
    ```

=== "TypeScript"

    ```typescript
    import {Gemini, LlmAgent, LlmSummarizer, TokenBasedContextCompactor} from '@google/adk';

    // 要約に使用する AI モデルを定義します。
    const summarizationLlm = new Gemini({model: 'gemini-flash-latest'});

    // カスタムモデルでサマライザーを作成します。
    const mySummarizer = new LlmSummarizer({llm: summarizationLlm});

    // カスタムサマライザーと圧縮設定でエージェントを構成します。
    const agent = new LlmAgent({
      name: 'my-agent',
      model: 'gemini-flash-latest',
      contextCompactors: [
        new TokenBasedContextCompactor({
          tokenThreshold: 1000,
          eventRetentionSize: 1,
          summarizer: mySummarizer,
        }),
      ],
    });
    ```

サマライザーを調整することで、圧縮器の動作をさらに細かく制御できます。Python と Java では `LlmEventSummarizer` の `prompt_template` を、TypeScript では `LlmSummarizer` の `prompt` をカスタマイズできます。詳細については、[`LlmEventSummarizer`コード](https://github.com/google/adk-python/blob/main/src/google/adk/apps/llm_event_summarizer.py#L60) または [`LlmSummarizer` コード](https://github.com/google/adk-js/blob/main/core/src/context/summarizers/llm_summarizer.ts) を参照してください。
