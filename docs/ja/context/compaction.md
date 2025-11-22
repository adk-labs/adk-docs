# パフォーマンスのためのエージェントコンテキストの圧縮

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.16.0</span>
</div>

ADKエージェントは実行されると、ユーザーの指示、取得されたデータ、ツールの応答、生成されたコンテンツを含む*コンテキスト*情報を収集します。このコンテキストデータのサイズが大きくなるにつれて、エージェントの処理時間も通常増加します。ますます多くのデータがエージェントが使用する生成AIモデルに送信され、処理時間が増加し、応答が遅くなります。ADKコンテキスト圧縮機能は、エージェントワークフローイベント履歴の古い部分を要約することにより、エージェントの実行中にコンテキストのサイズを削減するように設計されています。

コンテキスト圧縮機能は、[セッション](/adk-docs/ja/sessions/session/)内でエージェントワークフローイベントデータを収集および要約するために、*スライディングウィンドウ*アプローチを使用します。この機能をエージェントで構成すると、現在のセッションで特定の数のワークフローイベント (または呼び出し) のしきい値に達すると、古いイベントからのデータを要約します。

## コンテキスト圧縮の設定

ワークフローのAppオブジェクトにイベント圧縮構成設定を追加して、エージェントワークフローにコンテキスト圧縮を追加します。構成の一部として、次のサンプルコードに示すように、圧縮間隔と重複サイズを指定する必要があります。

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

構成されると、ADK `Runner`はセッションが間隔に達するたびにバックグラウンドで圧縮プロセスを処理します。

## コンテキスト圧縮の例

`compaction_interval`を3に、`overlap_size`を1に設定すると、イベントデータはイベント3、6、9などが完了すると圧縮されます。重複設定は、図1に示すように、2番目の要約圧縮とそれ以降の各要約のサイズを増加させます。

![コンテキスト圧縮の例のイラスト](/adk-docs/ja/assets/context-compaction.svg)
**図1.** 間隔3、重複1のイベント圧縮構成のイラスト。

この例の構成では、コンテキスト圧縮タスクは次のように行われます。

1.  **イベント3が完了**: 3つのイベントすべてが要約に圧縮されます
1.  **イベント6が完了**: 前の1つのイベントの重複を含め、イベント3から6までが圧縮されます
1.  **イベント9が完了**: 前の1つのイベントの重複を含め、イベント6から9までが圧縮されます

## 設定

この機能の設定は、イベントデータが圧縮される頻度と、エージェントワークフローの実行中に保持されるデータの量を制御します。オプションで、コンパクターオブジェクトを構成できます。

*   **`compaction_interval`**: 以前のイベントデータの圧縮をトリガーする完了したイベント数を設定します。
*   **`overlap_size`**: 新しく圧縮されたコンテキストセットに含める以前に圧縮されたイベントの数を設定します。
*   **`compactor`**: (オプション) 要約に使用する特定のAIモデルを含むコンパクターオブジェクトを定義します。詳細については、[コンパクターの定義](#define-compactor)を参照してください。

### サマライザーを定義する {#define-summarizer}
サマライザーを定義することで、コンテキスト圧縮プロセスをカスタマイズできます。LlmEventSummarizerクラスを使用すると、要約に特定のモデルを指定できます。次のコード例は、カスタムサマライザーを定義して構成する方法を示しています。

```python
from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.apps.llm_event_summarizer import LlmEventSummarizer
from google.adk.models import Gemini

# 要約に使用するAIモデルを定義します。
summarization_llm = Gemini(model="gemini-2.5-flash")

# カスタムモデルでサマライザーを作成します。
my_summarizer = LlmEventSummarizer(llm=summarization_llm)

# カスタムサマライザーと圧縮設定でAppを構成します。
app = App(
    name='my-agent',
    root_agent=root_agent,
    events_compaction_config=EventsCompactionConfig(
        summarizer=my_summarizer,
        compaction_interval=3,
        overlap_size=1
    ),
)
```

`SlidingWindowCompactor`のサマライザークラス`LlmEventSummarizer`の`prompt_template`設定を変更することを含め、その動作をさらに調整できます。詳細については、[`LlmEventSummarizer`コード](https://github.com/google/adk-python/blob/main/src/google/adk/apps/llm_event_summarizer.py#L60)を参照してください。