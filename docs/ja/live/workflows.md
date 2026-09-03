# ライブエージェント向けグラフワークフロー

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v2.0.0</span>
</div>

ライブエージェントは、他の ADK エージェントと同様に同じグラフワークフローに構成できます。ノードとエッジの定義、ルーティング、状態については [グラフワークフロー](../graphs/index.md) で、より広範なマルチエージェントの全体像については [ワークフロー](../workflows/index.md) で説明されています。ライブ接続下で変化するのは実行モデルです。

`run_live()` では、エージェントのパイプライン全体が*1つのオープンな接続と1つのイベントループの内部*で実行されるため、発信者は単一の継続的な会話を聞くことになります。制御が1つのエージェントから次のエージェントへと移る間も発信者は話し続けることができ、引き継ぎに気づくことはありません。

これはコードの書き方にも影響します。リクエスト/レスポンス型のエージェントでは各エージェントの遷移は制御可能な新しい呼び出しですが、ライブワークフローではエージェントがいくつ連なっていても、ワークフロー全体で1つのループと1つのキューを使用します。

## グラフでエージェントを実行する

グラフ [`Workflow`](../graphs/index.md) は、ADK 2.0 でライブエージェントを順序付ける方法です。エージェントをノードとして定義し、それらをエッジで接続すると、ランナーは単一のライブセッションにわたってグラフを走査します。

```python
from google.adk.agents.llm_agent import Agent
from google.adk.workflow import START, Workflow

LIVE_MODEL = 'gemini-live-2.5-flash-native-audio'

greeter = Agent(
    model=LIVE_MODEL,
    name='greeter',
    mode='task',  # ノードがライブ接続を使用するために必須
    instruction='Greet the caller and confirm you are speaking with John Doe. '
    'Ask one question per turn. Complete your task once the name is confirmed.',
)

verifier = Agent(
    model=LIVE_MODEL,
    name='verifier',
    mode='task',
    instruction='Verify the caller by date of birth, then complete your task.',
)

root_agent = Workflow(
    name='intake',
    edges=[
        (START, greeter),
        (greeter, verifier),
    ],
)
```

これを `adk web` で配信してライブセッションを開始するか、`Runner.run_live()` に渡します。ランナーは `Workflow` ルートを検出し、ライブ接続上でそれを駆動します。すべてのノードにわたって1つのイベントストリームを消費します。型付けされた引き継ぎとライブ評価セットを備えた3段階の音声受付フローの実行可能なサンプルについては、[`live_workflow` サンプル](https://github.com/google/adk-python/tree/main/contributing/samples/live/live_workflow) を参照してください。

**話すエージェントにはすべて `mode='task'` または `mode='chat'` が必要です。** ワークフロー内のノードとして、`mode` が設定されていない `LlmAgent` は `single_turn` にフォールバックし、ライブ接続の外部で実行され、オーディオキューを完全に無視するため、発信者にはそのエージェントの音声が全く聞こえません。話をするすべてのノードで明示的にモードを設定してください。

各ノードは、そのノードの実行期間中に独自の Live API セッションを開き、ワークフローの `LiveRequestQueue` は順次ノード間で共有されます。単一のキューから同時に2つのライブノードにフィードすることはできないため、ライブノードはファンアウト（並行分岐）させず、1つのパス上に維持してください。

## 1つのイベントストリームを読み取る

ストリームはノードの遷移をまたいで継続します。1つのループと1つのキューでストリームを消費し、`event.author` を読み取ってどのアージェントが話しているかを判別します。

```python
queue = LiveRequestQueue()

async for event in runner.run_live(
    user_id='user_123',
    session_id='session_456',
    live_request_queue=queue,
):
    if event.content and event.content.parts:
        for part in event.content.parts:
            if part.inline_data and part.inline_data.mime_type.startswith('audio/'):
                await play_audio(part.inline_data.data)
            elif part.text:
                await display_text(f'[{event.author}] {part.text}')
```

エージェントごとに新しい `run_live()` ループや新しい `LiveRequestQueue` を開かないでください。1つのループと1つのキューがワークフロー全体を処理し、ユーザー入力は現在アクティブなノードに送られます。

## 会話中の引き継ぎ（ハンドオフ）

コーディネーターエージェントは、`transfer_to_agent` を使用してセッションの途中でスペシャリストエージェントに会話を引き渡すことができます。引き継ぎは同じ `run_live()` ループ内で発生します。ADK はコーディネーターのライブ接続を閉じ、スペシャリストのための新しい接続を開き、ユーザーはそのまま会話を続けます。

```text
User: "I need help with billing"
Event: author="coordinator", function_call: transfer_to_agent(agent_name="billing")
Event: author="billing", text="I can help with your billing question..."
```

転送を行うとターゲットエージェント用の新しい Live API セッションが開始されるため、コーディネーターからのセッション再開ハンドルは引き継がれません。転送をコーディネーター自身のチーム内に制限するには、サブエージェントに `disallow_transfer_to_peers` を設定します。許可されていない兄弟間の転送は `ValueError` を発生させます。

## レガシーなワークフローエージェント

新しいコードにはグラフ `Workflow` を使用してください。`SequentialAgent`、`LoopAgent`、`ParallelAgent` は **`Workflow` の推奨に伴い非推奨（deprecated）** となっており、将来のリリースで削除される予定です。`LoopAgent` と `ParallelAgent` は `run_live()` で `NotImplementedError` を発生させ、ライブセッションをクラッシュさせるため、ライブパスには含めないでください。

`SequentialAgent` は引き続きライブモードで実行できます。その際、ADK は直接の各 `LlmAgent` サブエージェントに `task_completed` ツールを追加し、タスク完了時にそれを呼び出すよう指示を追加します。`task_completed` を呼び出すと、そのサブエージェントのライブ接続が終了し、シーケンス内の次のエージェントに進みます。

```python
# ADK はライブ実行時にこれを各 LlmAgent サブエージェントに挿入します。
def task_completed():
    """Signals that the agent has completed the user's task."""
    return 'Task completion signaled.'
```

イベントストリームは通常のライブワークフローのように見えます。エージェントごとのイベント実行の後、`task_completed` の関数レスポンスがあり、次のエージェントが始まります。

```text
Event: author="researcher", function_call: task_completed()
Event: author="writer", text="Based on the research..."
```

`task_completed` と `transfer_to_agent` は、異なる理由でエージェントのターンを終了させます。

| 関数 | パターン | 効果 |
|---|---|---|
| `task_completed` | 固定シーケンス | 現在のエージェントを終了し、シーケンス内の次のエージェントを開始する |
| `transfer_to_agent` | 動的ルーティング | 現在のライブセッションを閉じ、ターゲットエージェント用の新しいセッションを開く |
