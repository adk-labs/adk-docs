# 停止したエージェントの再開

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.14.0</span>
</div>

ADKエージェントの実行は、ネットワーク接続の切断、停電、または必要な外部システムのオフライン化など、さまざまな要因によって中断される可能性があります。ADKの再開（Resume）機能を使用すると、エージェントのワークフローが中断したところから処理を再開でき、ワークフロー全体を再起動する必要がなくなります。ADK Python 1.16以降では、ADKワークフローを再開可能に設定し、ワークフローの実行を追跡して、予期せぬ中断の後に再開できるようにすることができます。

このガイドでは、ADKエージェントのワークフローを再開可能に設定する方法について説明します。カスタムエージェントを使用している場合は、それらを更新して再開可能にすることができます。詳細については、[カスタムエージェントに再開機能を追加する](#custom-agents)を参照してください。

## 再開可能設定の追加

次のコード例に示すように、ADKワークフローのAppオブジェクトに再開可能性（Resumabiltiy）設定を適用することで、エージェントワークフローの再開機能を有効にします。

```python
app = App(
    name='my_resumable_agent',
    root_agent=root_agent,
    # 再開設定を行い、再開機能を有効にします。
    resumability_config=ResumabilityConfig(
        is_resumable=True,
    ),
)
```

!!! warning "注意：長時間実行関数、確認、認証"
    [長時間実行関数](/adk-docs/tools/function-tools/#long-run-tool)、
    [確認](/adk-docs/tools/confirmation/)、またはユーザー入力を必要とする
    [認証](/adk-docs/tools/authentication/)を使用するエージェントに再開可能設定を追加すると、これらの機能の動作方法が変わります。
    詳細については、各機能のドキュメントを参照してください。

!!! info "注：カスタムエージェント"
    カスタムエージェントでは、デフォルトでは再開機能はサポートされていません。カスタムエージェントが再開機能をサポートするには、エージェントのコードを更新する必要があります。
    カスタムエージェントを変更してインクリメンタルな再開機能をサポートする方法については、
    [カスタムエージェントに再開機能を追加する](#custom-agents)を参照してください。

## 停止したワークフローの再開

ADKワークフローの実行が停止した場合、ワークフローインスタンスの呼び出しID（Invocation ID）を含むコマンドを使用してワークフローを再開できます。呼び出しIDは、ワークフローの[イベント](/adk-docs/events/#understanding-and-using-events)履歴で確認できます。ADK APIサーバーが中断または電源オフされていた場合は、再起動してから、次のAPIリクエスト例に示すコマンドを実行してワークフローを再開します。

```console
# 必要に応じてAPIサーバーを再起動します:
adk api_server my_resumable_agent/

# エージェントを再開します:
curl -X POST http://localhost:8000/run_sse \
 -H "Content-Type: application/json" \
 -d '{
   "app_name": "my_resumable_agent",
   "user_id": "u_123",
   "session_id": "s_abc",
   "invocation_id": "invocation-123",
 }'
```

以下のように、Runnerオブジェクトの`run_async`メソッドを使用してワークフローを再開することもできます。

```python
runner.run_async(user_id='u_123', session_id='s_abc', 
    invocation_id='invocation-123')

# new_messageが関数のレスポンスに設定されている場合、
# 長時間実行関数を再開しようとしています。
```

!!! info "注"
    ADKのWebユーザーインターフェースやADKコマンドライン（CLI）ツールを使用したワークフローの再開は、現在サポートされていません。

## 仕組み

再開機能は、[イベント](/adk-docs/events/)と[イベントアクション](/adk-docs/events/#detecting-actions-and-side-effects)を使用して、インクリメンタルなステップを含む完了したエージェントのワークフロータスクをログに記録することで機能します。再開可能なワークフロー内でエージェントタスクの完了を追跡します。ワークフローが中断され、後で再起動されると、システムは各エージェントの完了状態を設定してワークフローを再開します。エージェントが完了していなかった場合、ワークフローシステムはそのエージェントに対して完了したすべてのイベントを復元し、部分的に完了した状態からワークフローを再開します。マルチエージェントワークフローの場合、具体的な再開動作は、ワークフロー内のマルチエージェントクラスに応じて以下のように異なります。

-   **Sequential Agent（シーケンシャルエージェント）**: 保存された状態から`current_sub_agent`を読み取り、シーケンスで次に実行するサブエージェントを見つけます。
-   **Loop Agent（ループエージェント）**: `current_sub_agent`と`times_looped`の値を使用して、最後に完了したイテレーションとサブエージェントからループを続行します。
-   **Parallel Agent（パラレルエージェント）**: すでに完了したサブエージェントを特定し、まだ終了していないエージェントのみを実行します。

イベントロギングには、正常に結果を返したツール（Tool）からの結果が含まれます。したがって、エージェントが関数ツールAとBを正常に実行し、ツールCの実行中に失敗した場合、システムはツールAとBの結果を復元し、ツールCのリクエストを再実行してワークフローを再開します。

!!! warning "注意：ツールの実行動作"
    ツールを使用するワークフローを再開する場合、再開機能はエージェント内のツールが***少なくとも1回***実行されることを保証し、ワークフローを再開する際には複数回実行される可能性があります。
    エージェントが購入など、重複実行が悪影響を及ぼすツールを使用する場合は、重複実行をチェックして防ぐようにツールを修正する必要があります。

!!! note "注：再開時のワークフロー変更は非サポート"
    停止したエージェントワークフローを再開する前に変更しないでください。
    たとえば、停止したワークフローにエージェントを追加または削除してからそのワークフローを再開することはサポートされていません。

## カスタムエージェントに再開機能を追加する {#custom-agents}

カスタムエージェントが再開可能性をサポートするには、特定の実装要件があります。カスタムエージェント内で、次の処理ステップに渡す前に保持できる結果を生成するワークフローステップを決定し、定義する必要があります。以下の手順は、カスタムエージェントを修正してワークフローの再開をサポートする方法の概要です。

-   **CustomAgentStateクラスの作成**: `BaseAgentState`を継承して、エージェントの状態を保持するオブジェクトを作成します。
    -   **（任意）WorkFlowStepクラスの作成**: カスタムエージェントにシーケンシャルなステップがある場合は、エージェントの個別で保存可能なステップを定義する`WorkFlowStep`リストオブジェクトの作成を検討してください。
-   **初期エージェント状態の追加**: エージェントの`async run`関数を修正して、エージェントの初期状態を設定します。
-   **エージェント状態のチェックポイント追加**: エージェントの`async run`関数を修正して、エージェントの全体的なタスクの各完了ステップごとにエージェントの状態を生成して保存します。
-   **エージェント状態追跡のためのエージェント終了ステータスの追加**: エージェントの`async run`関数を修正して、エージェントの全タスクが正常に完了したときに`end_of_agent=True`ステータスを含めるようにします。

次の例は、[カスタムエージェント](/adk-docs/agents/custom-agents/#full-code-example)ガイドに示されている`StoryFlowAgent`クラスの例に必要なコードの修正を示しています。

```python
class WorkflowStep(int, Enum):
 INITIAL_STORY_GENERATION = 1
 CRITIC_REVISER_LOOP = 2
 POST_PROCESSING = 3
 CONDITIONAL_REGENERATION = 4

# BaseAgentStateを継承

### class StoryFlowAgentState(BaseAgentState):

###   step = WorkflowStep

@override
async def _run_async_impl(
    self, ctx: InvocationContext
) -> AsyncGenerator[Event, None]:
    """
    ストーリーワークフローのカスタムオーケストレーションロジックを実装します。
    Pydanticによって割り当てられたインスタンス属性（例：self.story_generator）を使用します。
    """
    agent_state = self._load_agent_state(ctx, WorkflowStep)

    if agent_state is None:
      # エージェントの開始を記録
      agent_state = StoryFlowAgentState(step=WorkflowStep.INITIAL_STORY_GENERATION)
      yield self._create_agent_state_event(ctx, agent_state)

    next_step = agent_state.step
    logger.info(f"[{self.name}] ストーリー生成ワークフローを開始します。")

    # ステップ1. 初期のストーリー生成
    if next_step <= WorkflowStep.INITIAL_STORY_GENERATION:
      logger.info(f"[{self.name}] StoryGeneratorを実行中...")
      async for event in self.story_generator.run_async(ctx):
          yield event

      # 続行する前にストーリーが生成されたか確認
      if "current_story" not in ctx.session.state or not ctx.session.state[
          "current_story"
      ]:
          return  # 初期のストーリーが失敗した場合、処理を停止

    agent_state = StoryFlowAgentState(step=WorkflowStep.CRITIC_REVISER_LOOP)
    yield self._create_agent_state_event(ctx, agent_state)

    # ステップ2. 批評家-修正者ループ
    if next_step <= WorkflowStep.CRITIC_REVISER_LOOP:
      logger.info(f"[{self.name}] CriticReviserLoopを実行中...")
      async for event in self.loop_agent.run_async(ctx):
          logger.info(
              f"[{self.name}] CriticReviserLoopからのイベント: "
              f"{event.model_dump_json(indent=2, exclude_none=True)}"
          )
          yield event

    agent_state = StoryFlowAgentState(step=WorkflowStep.POST_PROCESSING)
    yield self._create_agent_state_event(ctx, agent_state)

    # ステップ3. シーケンシャルな後処理（文法とトーンのチェック）
    if next_step <= WorkflowStep.POST_PROCESSING:
      logger.info(f"[{self.name}] PostProcessingを実行中...")
      async for event in self.sequential_agent.run_async(ctx):
          logger.info(
              f"[{self.name}] PostProcessingからのイベント: "
              f"{event.model_dump_json(indent=2, exclude_none=True)}"
          )
          yield event

    agent_state = StoryFlowAgentState(step=WorkflowStep.CONDITIONAL_REGENERATION)
    yield self._create_agent_state_event(ctx, agent_state)

    # ステップ4. トーンに基づく条件付きロジック
    if next_step <= WorkflowStep.CONDITIONAL_REGENERATION:
      tone_check_result = ctx.session.state.get("tone_check_result")
      if tone_check_result == "negative":
          logger.info(f"[{self.name}] トーンがネガティブです。ストーリーを再生成します...")
          async for event in self.story_generator.run_async(ctx):
              logger.info(
                  f"[{self.name}] StoryGenerator（再生成）からのイベント: "
                  f"{event.model_dump_json(indent=2, exclude_none=True)}"
              )
              yield event
      else:
          logger.info(f"[{self.name}] トーンはネガティブではありません。現在のストーリーを維持します。")

    logger.info(f"[{self.name}] ワークフローが終了しました。")
    yield self._create_agent_state_event(ctx, end_of_agent=True)
```