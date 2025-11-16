# 停止したエージェントを再開する

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.14.0</span>
</div>

ADKエージェントの実行は、ネットワーク接続の切断、停電、または必要な外部システムのオフラインなど、さまざまな要因によって中断される可能性があります。ADKの再開機能を使用すると、エージェントワークフローが中断したところから再開できるため、ワークフロー全体を再起動する必要がありません。ADK Python 1.16以降では、ADKワークフローを再開可能に構成して、ワークフローの実行を追跡し、予期しない中断の後に再開できるようにすることができます。

このガイドでは、ADKエージェントワークフローを再開可能に構成する方法について説明します。カスタムエージェントを使用している場合は、それらを再開可能に更新できます。詳細については、[カスタムエージェントに再開を追加する](#custom-agents)を参照してください。

## 再開可能な構成を追加する

次のコード例に示すように、ADKワークフローのAppオブジェクトに再開可能性構成を適用して、エージェントワークフローの再開機能を有効にします。

```python
app = App(
    name='my_resumable_agent',
    root_agent=root_agent,
    # 再開可能性を有効にするには、再開可能性構成を設定します。
    resumability_config=ResumabilityConfig(
        is_resumable=True,
    ),
)
```

!!! warning "注意：長時間実行される関数、確認、認証"
    [長時間実行される関数](/adk-docs/ja/tools-custom/function-tools/#long-run-tool)、
    [確認](/adk-docs/ja/tools-custom/confirmation/)、または
    [認証](/adk-docs/ja/tools-custom/authentication/)を使用するエージェントの場合、
    ユーザー入力が必要な場合、再開可能な確認を追加すると、これらの機能の動作方法が変更されます。
    詳細については、これらの機能のドキュメントを参照してください。

!!! info "注：カスタムエージェント"
    カスタムエージェントでは、デフォルトで再開はサポートされていません。
    再開機能をサポートするには、カスタムエージェントのエージェントコードを更新する必要があります。
    増分再開機能をサポートするようにカスタムエージェントを変更する方法については、
    [カスタムエージェントに再開を追加する](#custom-agents)を参照してください。

## 停止したワークフローを再開する

ADKワークフローの実行が停止した場合、ワークフローインスタンスの呼び出しIDを含むコマンドを使用してワークフローを再開できます。呼び出しIDは、ワークフローの[イベント](/adk-docs/ja/events/#understanding-and-using-events)履歴にあります。ADK APIサーバーが中断または電源オフになった場合は実行されていることを確認し、次のAPIリクエストの例に示すように、次のコマンドを実行してワークフローを再開します。

```console
# 必要に応じてAPIサーバーを再起動します。
adk api_server my_resumable_agent/

# エージェントを再開します。
curl -X POST http://localhost:8000/run_sse \
 -H "Content-Type: application/json" \
 -d '{ 
   "app_name": "my_resumable_agent",
   "user_id": "u_123",
   "session_id": "s_abc",
   "invocation_id": "invocation-123",
 }'
```

以下に示すように、RunnerオブジェクトのRun Asyncメソッドを使用してワークフローを再開することもできます。

```python
runner.run_async(user_id='u_123', session_id='s_abc', 
    invocation_id='invocation-123')

# new_messageが関数応答に設定されている場合、
# 長時間実行される関数を再開しようとしています。
```

!!! info "注"
    ADK Webユーザーインターフェイスからワークフローを再開したり、ADK
    コマンドライン（CLI）ツールを使用したりすることは現在サポートされていません。

## 仕組み

再開機能は、[イベント](/adk-docs/ja/events/)および[イベントアクション](/adk-docs/ja/events/#detecting-actions-and-side-effects)を使用して増分ステップを含む、完了したエージェントワークフロータスクをログに記録することで機能します。再開可能なワークフロー内でエージェントタスクの完了を追跡します。ワークフローが中断され、後で再開されると、システムは各エージェントの完了状態を設定してワークフローを再開します。エージェントが完了しなかった場合、ワークフローシステムはそのエージェントの完了したすべてのイベントを復元し、部分的に完了した状態からワークフローを再開します。マルチエージェントワークフローの場合、特定の再開動作は、以下で説明するように、ワークフローのマルチエージェントクラスに基づいて異なります。

-   **シーケンシャルエージェント**：保存された状態からcurrent_sub_agentを読み取り、シーケンスで実行する次のサブエージェントを見つけます。
-   **ループエージェント**：current_sub_agentとtimes_loopedの値を使用して、最後に完了した反復とサブエージェントからループを続行します。
-   **パラレルエージェント**：すでに完了したサブエージェントを判別し、完了していないサブエージェントのみを実行します。

イベントログには、正常に結果を返したツールからの結果が含まれます。したがって、エージェントが関数ツールAとBを正常に実行し、ツールCの実行中に失敗した場合、システムはツールAとBからの結果を復元し、ツールCリクエストを再実行してワークフローを再開します。

!!! warning "注意：ツールの実行動作"
    ツールを使用してワークフローを再開する場合、再開機能により、エージェントのツールが***少なくとも1回***実行され、ワークフローを再開するときに複数回実行される可能性があります。エージェントが、購入など、重複した実行が悪影響を及ぼすツールを使用する場合は、重複した実行をチェックして防止するようにツールを変更する必要があります。

!!! note "注：再開によるワークフローの変更はサポートされていません"
    停止したエージェントワークフローを再開する前に変更しないでください。
    たとえば、停止したワークフローからエージェントを追加または削除してからそのワークフローを再開することはサポートされていません。

## カスタムエージェントに再開を追加する {#custom-agents}

カスタムエージェントには、再開可能性をサポートするための特定の実装要件があります。次の処理ステップに渡す前に保持できる結果を生成するカスタムエージェント内でワークフローステップを決定して定義する必要があります。次の手順では、ワークフローの再開をサポートするようにカスタムエージェントを変更する方法の概要を説明します。

-   **CustomAgentStateクラスの作成**：BaseAgentStateを拡張して、エージェントの状態を保持するオブジェクトを作成します。
    -   **オプションで、WorkFlowStepクラスの作成**：カスタムエージェントにシーケンシャルステップがある場合は、エージェントの個別で保存可能なステップを定義するWorkFlowStepリストオブジェクトを作成することを検討してください。
-   **初期エージェント状態の追加：** エージェントの非同期実行関数を変更して、エージェントの初期状態を設定します。
-   **エージェント状態チェックポイントの追加**：エージェントの非同期実行関数を変更して、エージェントの全体的なタスクの各完了ステップのエージェNT状態を生成して保存します。
-   **エージェント状態を追跡するためにエージェント状態の最後に追加：** エージェントの全体的なタスクが正常に完了したら、`end_of_agent=True`状態を含むようにエージェントの非同期実行関数を変更します。

次の例は、[カスタムエージェント](/adk-docs/ja/agents/custom-agents/#full-code-example)ガイドに示されているStoryFlowAgentクラスの例に必要なコード変更を示しています。

```python
class WorkflowStep(int, Enum):
 INITIAL_STORY_GENERATION = 1
 CRITIC_REVISER_LOOP = 2
 POST_PROCESSING = 3
CONDITIONAL_REGENERATION = 4

# BaseAgentStateを拡張

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
      # エージェントの開始を記録します
      agent_state = StoryFlowAgentState(step=WorkflowStep.INITIAL_STORY_GENERATION)
      yield self._create_agent_state_event(ctx, agent_state)

    next_step = agent_state.step
    logger.info(f"[{self.name}] ストーリー生成ワークフローを開始しています。")

    # ステップ1. 初期ストーリー生成
    if next_step <= WorkflowStep.INITIAL_STORY_GENERATION:
      logger.info(f"[{self.name}] StoryGeneratorを実行しています...")
      async for event in self.story_generator.run_async(ctx):
          yield event

      # 続行する前にストーリーが生成されたかどうかを確認します
      if "current_story" not in ctx.session.state or not ctx.session.state[
          "current_story"
      ]:
          return  # 初期ストーリーが失敗した場合は処理を停止します

    agent_state = StoryFlowAgentState(step=WorkflowStep.CRITIC_REVISER_LOOP)
    yield self._create_agent_state_event(ctx, agent_state)

    # ステップ2. 批評家-改訂者ループ
    if next_step <= WorkflowStep.CRITIC_REVISER_LOOP:
      logger.info(f"[{self.name}] CriticReviserLoopを実行しています...")
      async for event in self.loop_agent.run_async(ctx):
          logger.info(
              f"[{self.name}] CriticReviserLoopからのイベント： "
              f"{event.model_dump_json(indent=2, exclude_none=True)}"
          )
          yield event

    agent_state = StoryFlowAgentState(step=WorkflowStep.POST_PROCESSING)
    yield self._create_agent_state_event(ctx, agent_state)

    # ステップ3. シーケンシャル後処理（文法とトーンのチェック）
    if next_step <= WorkflowStep.POST_PROCESSING:
      logger.info(f"[{self.name}] 後処理を実行しています...")
      async for event in self.sequential_agent.run_async(ctx):
          logger.info(
              f"[{self.name}] 後処理からのイベント： "
              f"{event.model_dump_json(indent=2, exclude_none=True)}"
          )
          yield event

    agent_state = StoryFlowAgentState(step=WorkflowStep.CONDITIONAL_REGENERATION)
    yield self._create_agent_state_event(ctx, agent_state)

    # ステップ4. トーンベースの条件付きロジック
    if next_step <= WorkflowStep.CONDITIONAL_REGENERATION:
      tone_check_result = ctx.session.state.get("tone_check_result")
      if tone_check_result == "negative":
          logger.info(f"[{self.name}] トーンが否定的です。ストーリーを再生成しています...")
          async for event in self.story_generator.run_async(ctx):
              logger.info(
                  f"[{self.name}] StoryGeneratorからのイベント（再生成）： "
                  f"{event.model_dump_json(indent=2, exclude_none=True)}"
              )
              yield event
      else:
          logger.info(f"[{self.name}] トーンは否定的ではありません。現在のストーリーを維持します。")

    logger.info(f"[{self.name}] ワークフローが終了しました。")
    yield self._create_agent_state_event(ctx, end_of_agent=True)
