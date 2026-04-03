# 協調エージェントチームを構築する

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v2.0.0</span><span class="lst-preview">Alpha</span>
</div>

複雑なタスクの中には、特定の責務を持つ複数のエージェントを必要とし、
特に大きく重要なサブタスクをいくつも含む反復的な処理では、より構造化の
少ない手順が適している場合があります。ADK の協調エージェントチームでは、
コーディネーターエージェントが 1 つ以上のサブエージェントへタスクの委譲を
行います。このアプローチにより、特定のタスクを処理するよう定義された
サブエージェントと、タスク完了後に親へ自動的に戻る仕組みを備えた、
複雑で自己管理型のエージェントシステムを構築しやすくなります。

この自己管理型エージェントチームのアプローチでは、サブエージェントに
動作 ***mode*** が割り当てられ、その挙動を管理し作業範囲を制限します。
これらの ***modes*** はサブエージェント向けの一般的な動作ガイドラインを
定め、より予測可能で信頼性の高いマルチエージェントワークフローを作ります。
協調モードでは次の設定を利用できます。

- ***Chat***: ユーザーとの完全な対話、親エージェントへの手動復帰
  （既定値、現在の動作）
- ***Task***: 明確化のためのユーザー対話を許可し、親エージェントへ自動復帰
- ***Single-turn:*** ユーザー対話なしで自動復帰し、並列実行が可能

このガイドでは、サブエージェントでモードを使う方法と、これらのモードが
エージェントの振る舞いにどう影響するかを説明します。

!!! example "Alpha リリース"

    ADK 2.0 は Alpha リリースであり、以前の ADK バージョンと併用する際に
    互換性を壊す変更が発生する可能性があります。プロダクション環境のように
    後方互換性が必要な場合は ADK 2.0 を使用しないでください。このリリースを
    ぜひ試していただき、
    [フィードバック](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=v2)
    をお寄せください。

## はじめに

次のコード例は、小規模なサブエージェントチームに動作モードを設定し、
それらをコーディネーターエージェントへ割り当てる方法を示します。

```python
from google.adk.workflow.agents.llm_agent import Agent

weather_agent = Agent(
    name="weather_checker",
    mode="single_turn",         # no user interaction
    tools=[get_weather, user_info, geocode_address],
)
flight_agent = Agent(
    name="flight_booker",
    mode="task",                # can ask user questions
    input_schema=FlightInput,
    output_schema=FlightResult,
    tools=[search_flights, book_flight],
)
root = Agent(
    name="travel_planner",      # coordinator agent
    sub_agents=[weather_agent, flight_agent],
    # Auto-injects: request_task_weather_checker, request_task_flight_booker
)
```

このワークフローを実行すると、`travel_planner` コーディネーターエージェントが
自動的にタスクを特定してサブエージェントへ割り当てます。サブエージェントが
タスクを完了すると、自動的にコーディネーターエージェントへ戻ります。
エージェント、サブエージェント、ワークフローノードで
***input_schema*** と ***output_schema*** を使ってデータを構造化する
詳細については、
[エージェントワークフローのデータ処理](/ja/workflows/data-handling/)
を参照してください。

## モード設定と挙動

各協調モードには、それぞれ固有の挙動と制限があります。次の表は、各モードで
構成されたサブエージェントの属性を比較したものです。

!!! warning "注意: mode はサブエージェント専用"

    ***mode*** 設定は、コーディネーターである親エージェントから呼び出される
    サブエージェントで使用することを意図したものです。ルートエージェントに
    mode 設定を構成しないでください。

<table>
  <thead>
    <tr>
      <th><strong>Topic \ Mode</strong></th>
      <th><code>chat</code> (default)</th>
      <th><code>task</code></th>
      <th><code>single_turn</code></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Human in the Loop</strong></td>
      <td>完全な対話</td>
      <td>明確化のみ</td>
      <td>許可されない</td>
    </tr>
    <tr>
      <td><strong>ユーザー対話</strong></td>
      <td>ユーザーが自由にエージェントと会話</td>
      <td>必要に応じてエージェントが質問</td>
      <td>ユーザー対話なし</td>
    </tr>
    <tr>
      <td><strong>制御フロー</strong></td>
      <td>手動ハンドオフまでエージェントが制御</td>
      <td>タスク完了までエージェントが制御</td>
      <td>タスク直後に即時復帰</td>
    </tr>
    <tr>
      <td><strong>並列実行</strong></td>
      <td>未サポート</td>
      <td>未サポート</td>
      <td>複数タスクを並列実行可能</td>
    </tr>
    <tr>
      <td><strong>親への復帰</strong></td>
      <td>手動 (transfer 経由)</td>
      <td>自動 (<code>complete_task</code> 経由)</td>
      <td>自動 (結果付き)</td>
    </tr>
  </tbody>
</table>

**表 1.** ADK の協調エージェント ***mode*** の挙動と制限の比較。

## 運用時の考慮事項

協調エージェントモードを使う際は、次のセクションで説明するように、
制御の移譲とコンテキスト管理に関するいくつかの考慮事項があります。

### ワークフローノードとエージェントの制御移譲

***task*** または ***single-turn*** モードで構成されたエージェントは、
Workflow Agent のグラフノードとしても、***LlmAgent*** インスタンスと
組み合わせても利用できます。ただし、呼び出し元、すなわち親エージェントに
よって実行時の制御移譲動作は異なります。

**ワークフローグラフノードとして使う場合:** task エージェントを
***SequentialAgent*** や ***ParallelAgent*** のようなワークフローグラフ内に
配置すると、そのエージェントは自身のタスクを実行します。完了すると、
ワークフローエージェントのグラフロジックに従って、制御は自動的に次のノードへ
進みます。

**LlmAgent から転送される場合:** 親の ***LlmAgent*** が `request_task` を
通じて task エージェントへ制御を移すと、task エージェントは
`complete_task` を呼び出すまで実行されます。その時点で、制御は転送を開始した
元のエージェントへ自動的に戻ります。この挙動は、制御を戻すために明示的な
`transfer_to_agent` 呼び出しを必要とする既定の chat ***mode*** エージェントと
は異なります。

<table>
  <thead>
    <tr>
      <th><strong>Invocation Context</strong></th>
      <th><strong>After Task Completion</strong></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>ワークフローノード</td>
      <td>グラフ内の次のノードへ進む</td>
    </tr>
    <tr>
      <td>LlmAgent からの転送</td>
      <td>元のエージェントへ制御を戻す</td>
    </tr>
  </tbody>
</table>

この違いにより、同じ task エージェントを修正なしで両方のコンテキストで
再利用できます。ランタイムは、エージェントがどのように呼び出されたかに
応じて適切な制御フローを決定します。

### エージェントコンテキストの分離

各 ***task*** または ***single-turn*** モードのエージェントは、自身の分離
されたセッションブランチで動作します。これらのエージェントが並列で動作する
場合、各エージェントは AI モデル呼び出し用のコンテキストを構築するときに、
自分自身のブランチ上のイベントしか参照できず、同僚エージェントが何をして
いるかは見えません。すべての並列ブランチが完了すると、親エージェントが
結果を収集して次の処理へ進めます。

## 既知の制限事項

エージェント協調モードには、いくつかの既知の制限があります。

- ***Task* mode agents** はリーフエージェントでなければならず、
  サブエージェントを持てません。
