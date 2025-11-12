# パフォーマンスのためのエージェントコンテキストの圧縮

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.16.0</span>
</div>

ADKエージェントが実行されると、ユーザーの指示、取得されたデータ、ツールの応答、生成されたコンテンツなど、*コンテキスト*情報が収集されます。このコンテキストデータのサイズが大きくなるにつれて、エージェントの処理時間も通常増加します。エージェントが使用する生成AIモデルに送信されるデータが増え、処理時間が増加し、応答が遅くなります。ADKコンテキスト圧縮機能は、エージェントワークフローイベント履歴の古い部分を要約することで、エージェントの実行中にコンテキストのサイズを縮小するように設計されています。

コンテキスト圧縮機能は、[セッション](/adk-docs/sessions/session/)内でエージェントワークフローイベントデータを収集および要約するために、*スライディングウィンドウ*アプローチを使用します。エージェントでこの機能を構成すると、現在のセッションで特定の数のワークフローイベントまたは呼び出しのしきい値に達すると、古いイベントのデータが要約されます。

## コンテキスト圧縮の構成

ワークフローのAppオブジェクトにイベント圧縮構成設定を追加して、エージェントワークフローにコンテキスト圧縮を追加します。構成の一部として、次のサンプルコードに示すように、圧縮間隔と重複サイズを指定する必要があります。

```python
from google.adk.apps.app import App
from google.adk.apps.app import EventsCompactionConfig

app = App(
    name='my-agent',
    root_agent=root_agent,
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=3,  # 3回の新しい呼び出しごとに圧縮をトリガーします。
        overlap_size=1          # 前のウィンドウの最後の呼び出しを含めます。
    ),
)
```

構成されると、ADK `Runner`は、セッションが間隔に達するたびにバックグラウンドで圧縮プロセスを処理します。

## コンテキスト圧縮の例

`compaction_interval`を3に設定し、`overlap_size`を1に設定すると、イベント3、6、9などが完了するとイベントデータが圧縮されます。重複設定により、図1に示すように、2番目の要約圧縮とその後の各要約のサイズが大きくなります。

![コンテキスト圧縮の例の図](/adk-docs/assets/context-compaction.svg)
**図1.** 間隔3と重複1のイベント圧縮構成の図。

この構成例では、コンテキスト圧縮タスクは次のように実行されます。

1.  **イベント3が完了**: 3つのイベントすべてが要約に圧縮されます。
2.  **イベント6が完了**: 1つの前のイベントの重複を含め、イベント3から6が圧縮されます。
3.  **イベント9が完了**: 1つの前のイベントの重複を含め、イベント6から9が圧縮されます。

## 構成設定

この機能の構成設定は、イベントデータが圧縮される頻度と、エージェントワークフローの実行中に保持されるデータ量を制御します。オプションで、コンパクタオブジェクトを構成できます。

*   **`compaction_interval`**: 前のイベントデータの圧縮をトリガーする完了したイベントの数を設定します。
*   **`overlap_size`**: 新しく圧縮されたコンテキストセットに含まれる、以前に圧縮されたイベントの数を設定します。
*   **`compactor`**: (オプション) 要約に使用する特定のAIモデルを含むコンパクタオブジェクトを定義します。詳細については、[コンパクタの定義](#define-compactor)を参照してください。

### コンパクタの定義 {#define-compactor}

`SlidingWindowCompactor`クラスを使用してコンパクタオブジェクトを定義し、コンテキスト圧縮の操作をカスタマイズできます。次のコード例は、コンパクタを定義する方法を示しています。

```python
from google.adk.apps.app import App
from google.adk.apps.app import EventsCompactionConfig
from google.adk.models import Gemini
from google.adk.apps.sliding_window_compactor import SlidingWindowCompactor

# 特定のAIモデルを使用してコンパクタを定義します。
summarization_llm = Gemini(model="gemini-2.5-flash")
my_compactor = SlidingWindowCompactor(llm=summarization_llm)

app = App(
    name='my-agent',
    root_agent=root_agent,
    events_compaction_config=EventsCompactionConfig(
        compactor=my_compactor,
        compaction_interval=3, overlap_size=1
    ),
)    
```

そのクラスの`prompt_template`設定を変更するなど、サマライザクラス`LlmEventSummarizer`を変更することで、`SlidingWindowCompactor`の操作をさらに調整できます。詳細については、[`LlmEventSummarizer`コード](https://github.com/google/adk-python/blob/main/src/google/adk/apps/llm_event_summarizer.py#L60)を参照してください。
