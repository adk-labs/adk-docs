# 중지된 에이전트 재개

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.14.0</span>
</div>

ADK 에이전트의 실행은 네트워크 연결 끊김, 정전 또는 필요한 외부 시스템 오프라인과 같은 다양한 요인으로 인해 중단될 수 있습니다. ADK의 재개 기능을 사용하면 에이전트 워크플로가 중단된 지점부터 다시 시작하여 전체 워크플로를 다시 시작할 필요가 없습니다. ADK Python 1.16 이상에서는 ADK 워크플로를 재개 가능하도록 구성하여 워크플로 실행을 추적한 다음 예기치 않은 중단 후 재개할 수 있습니다.

이 가이드에서는 ADK 에이전트 워크플로를 재개 가능하도록 구성하는 방법을 설명합니다. 사용자 지정 에이전트를 사용하는 경우 재개 가능하도록 업데이트할 수 있습니다. 자세한 내용은 [사용자 지정 에이전트에 재개 추가](#custom-agents)를 참조하십시오.

## 재개 가능 구성 추가

다음 코드 예제와 같이 ADK 워크플로의 앱 개체에 재개 가능성 구성을 적용하여 에이전트 워크플로에 대한 재개 기능을 활성화합니다.

```python
app = App(
    name='my_resumable_agent',
    root_agent=root_agent,
    # 재개 가능성을 활성화하려면 재개 가능성 구성을 설정합니다.
    resumability_config=ResumabilityConfig(
        is_resumable=True,
    ),
)
```

!!! warning "주의: 장기 실행 함수, 확인, 인증"
    [장기 실행 함수](/adk-docs/ko/tools-custom/function-tools/#long-run-tool),
    [확인](/adk-docs/ko/tools-custom/confirmation/) 또는
    [인증](/adk-docs/ko/tools-custom/authentication/)을 사용하는 에이전트의 경우
    사용자 입력이 필요한 경우 재개 가능한 확인을 추가하면 이러한 기능의 작동 방식이 변경됩니다.
    자세한 내용은 해당 기능에 대한 설명서를 참조하십시오.

!!! info "참고: 사용자 지정 에이전트"
    사용자 지정 에이전트의 경우 기본적으로 재개가 지원되지 않습니다.
    재개 기능을 지원하려면 사용자 지정 에이전트에 대한 에이전트 코드를 업데이트해야 합니다.
    증분 재개 기능을 지원하도록 사용자 지정 에이전트를 수정하는 방법에 대한 정보는
    [사용자 지정 에이전트에 재개 추가](#custom-agents)를 참조하십시오.

## 중지된 워크플로 재개

ADK 워크플로 실행이 중지되면 워크플로 인스턴스에 대한 호출 ID가 포함된 명령을 사용하여 워크플로를 재개할 수 있습니다. 호출 ID는 워크플로의 [이벤트](/adk-docs/ko/events/#understanding-and-using-events) 기록에서 찾을 수 있습니다. ADK API 서버가 중단되거나 전원이 꺼진 경우 실행 중인지 확인한 다음 다음 API 요청 예제와 같이 다음 명령을 실행하여 워크플로를 재개합니다.

```console
# 필요한 경우 API 서버 다시 시작:
adk api_server my_resumable_agent/

# 에이전트 재개:
curl -X POST http://localhost:8000/run_sse \
 -H "Content-Type: application/json" \
 -d '{ 
   "app_name": "my_resumable_agent",
   "user_id": "u_123",
   "session_id": "s_abc",
   "invocation_id": "invocation-123",
 }'
```

아래와 같이 Runner 개체 Run Async 메서드를 사용하여 워크플로를 재개할 수도 있습니다.

```python
runner.run_async(user_id='u_123', session_id='s_abc', 
    invocation_id='invocation-123')

# new_message가 함수 응답으로 설정되면
# 장기 실행 함수를 재개하려고 합니다.
```

!!! info "참고"
    ADK 웹 사용자 인터페이스에서 워크플로를 재개하거나 ADK
    명령줄(CLI) 도구를 사용하는 것은 현재 지원되지 않습니다.

## 작동 방식

재개 기능은 [이벤트](/adk-docs/ko/events/) 및 [이벤트 작업](/adk-docs/ko/events/#detecting-actions-and-side-effects)을 사용하여 증분 단계를 포함하여 완료된 에이전트 워크플로 작업을 기록하여 작동합니다. 재개 가능한 워크플로 내에서 에이전트 작업의 완료를 추적합니다. 워크플로가 중단된 후 나중에 다시 시작되면 시스템은 각 에이전트의 완료 상태를 설정하여 워크플로를 재개합니다. 에이전트가 완료되지 않은 경우 워크플로 시스템은 해당 에이전트에 대해 완료된 모든 이벤트를 복원하고 부분적으로 완료된 상태에서 워크플로를 다시 시작합니다. 다중 에이전트 워크플로의 경우 특정 재개 동작은 아래에 설명된 대로 워크플로의 다중 에이전트 클래스에 따라 다릅니다.

-   **순차 에이전트**: 저장된 상태에서 current_sub_agent를 읽어 시퀀스에서 실행할 다음 하위 에이전트를 찾습니다.
-   **루프 에이전트**: current_sub_agent 및 times_looped 값을 사용하여 마지막으로 완료된 반복 및 하위 에이전트에서 루프를 계속합니다.
-   **병렬 에이전트**: 이미 완료된 하위 에이전트를 결정하고 완료되지 않은 하위 에이전트만 실행합니다.

이벤트 로깅에는 성공적으로 결과를 반환한 도구의 결과가 포함됩니다. 따라서 에이전트가 함수 도구 A와 B를 성공적으로 실행한 다음 도구 C를 실행하는 동안 실패하면 시스템은 도구 A와 B의 결과를 복원하고 도구 C 요청을 다시 실행하여 워크플로를 재개합니다.

!!! warning "주의: 도구 실행 동작"
    도구가 있는 워크플로를 재개할 때 재개 기능은 에이전트의 도구가 ***최소 한 번*** 실행되고 워크플로를 재개할 때 두 번 이상 실행될 수 있도록 합니다. 에이전트가 구매와 같이 중복 실행이 부정적인 영향을 미치는 도구를 사용하는 경우 중복 실행을 확인하고 방지하도록 도구를 수정해야 합니다.

!!! note "참고: 재개를 사용한 워크플로 수정은 지원되지 않음"
    중지된 에이전트 워크플로를 재개하기 전에 수정하지 마십시오.
    예를 들어 중지된 워크플로에서 에이전트를 추가하거나 제거한 다음 해당 워크플로를 재개하는 것은 지원되지 않습니다.

## 사용자 지정 에이전트에 재개 추가 {#custom-agents}

사용자 지정 에이전트에는 재개 가능성을 지원하기 위한 특정 구현 요구 사항이 있습니다. 다음 처리 단계로 넘기기 전에 보존할 수 있는 결과를 생성하는 사용자 지정 에이전트 내에서 워크플로 단계를 결정하고 정의해야 합니다. 다음 단계에서는 워크플로 재개를 지원하도록 사용자 지정 에이전트를 수정하는 방법을 간략하게 설명합니다.

-   **CustomAgentState 클래스 만들기**: BaseAgentState를 확장하여 에이전트의 상태를 보존하는 개체를 만듭니다.
    -   **선택적으로 WorkFlowStep 클래스 만들기**: 사용자 지정 에이전트에 순차적 단계가 있는 경우 에이전트의 개별적이고 저장 가능한 단계를 정의하는 WorkFlowStep 목록 개체를 만드는 것을 고려하십시오.
-   **초기 에이전트 상태 추가:** 에이전트의 비동기 실행 함수를 수정하여 에이전트의 초기 상태를 설정합니다.
-   **에이전트 상태 검사점 추가**: 에이전트의 비동기 실행 함수를 수정하여 에이전트의 전체 작업의 각 완료된 단계에 대한 에이전트 상태를 생성하고 저장합니다.
-   **에이전트 상태를 추적하기 위해 에이전트 상태 끝 추가:** 에이전트의 전체 작업이 성공적으로 완료되면 `end_of_agent=True` 상태를 포함하도록 에이전트의 비동기 실행 함수를 수정합니다.

다음 예제는 [사용자 지정 에이전트](/adk-docs/ko/agents/custom-agents/#full-code-example) 가이드에 표시된 예제 StoryFlowAgent 클래스에 필요한 코드 수정을 보여줍니다.

```python
class WorkflowStep(int, Enum):
 INITIAL_STORY_GENERATION = 1
 CRITIC_REVISER_LOOP = 2
 POST_PROCESSING = 3
CONDITIONAL_REGENERATION = 4

# BaseAgentState 확장

### class StoryFlowAgentState(BaseAgentState):

###   step = WorkflowStep

@override
async def _run_async_impl(
    self, ctx: InvocationContext
) -> AsyncGenerator[Event, None]:
    """
    스토리 워크플로에 대한 사용자 지정 오케스트레이션 논리를 구현합니다.
    Pydantic에서 할당한 인스턴스 속성(예: self.story_generator)을 사용합니다.
    """
    agent_state = self._load_agent_state(ctx, WorkflowStep)

    if agent_state is None:
      # 에이전트 시작 기록
      agent_state = StoryFlowAgentState(step=WorkflowStep.INITIAL_STORY_GENERATION)
      yield self._create_agent_state_event(ctx, agent_state)

    next_step = agent_state.step
    logger.info(f"[{self.name}] 스토리 생성 워크플로 시작.")

    # 1단계. 초기 스토리 생성
    if next_step <= WorkflowStep.INITIAL_STORY_GENERATION:
      logger.info(f"[{self.name}] StoryGenerator 실행 중...")
      async for event in self.story_generator.run_async(ctx):
          yield event

      # 진행하기 전에 스토리가 생성되었는지 확인
      if "current_story" not in ctx.session.state or not ctx.session.state[
          "current_story"
      ]:
          return  # 초기 스토리가 실패하면 처리 중지

    agent_state = StoryFlowAgentState(step=WorkflowStep.CRITIC_REVISER_LOOP)
    yield self._create_agent_state_event(ctx, agent_state)

    # 2단계. 비평가-수정자 루프
    if next_step <= WorkflowStep.CRITIC_REVISER_LOOP:
      logger.info(f"[{self.name}] CriticReviserLoop 실행 중...")
      async for event in self.loop_agent.run_async(ctx):
          logger.info(
              f"[{self.name}] CriticReviserLoop의 이벤트: "
              f"{event.model_dump_json(indent=2, exclude_none=True)}"
          )
          yield event

    agent_state = StoryFlowAgentState(step=WorkflowStep.POST_PROCESSING)
    yield self._create_agent_state_event(ctx, agent_state)

    # 3단계. 순차적 후처리(문법 및 어조 확인)
    if next_step <= WorkflowStep.POST_PROCESSING:
      logger.info(f"[{self.name}] 후처리 실행 중...")
      async for event in self.sequential_agent.run_async(ctx):
          logger.info(
              f"[{self.name}] 후처리의 이벤트: "
              f"{event.model_dump_json(indent=2, exclude_none=True)}"
          )
          yield event

    agent_state = StoryFlowAgentState(step=WorkflowStep.CONDITIONAL_REGENERATION)
    yield self._create_agent_state_event(ctx, agent_state)

    # 4단계. 어조 기반 조건부 논리
    if next_step <= WorkflowStep.CONDITIONAL_REGENERATION:
      tone_check_result = ctx.session.state.get("tone_check_result")
      if tone_check_result == "negative":
          logger.info(f"[{self.name}] 어조가 부정적입니다. 스토리 다시 생성 중...")
          async for event in self.story_generator.run_async(ctx):
              logger.info(
                  f"[{self.name}] StoryGenerator(재생성)의 이벤트: "
                  f"{event.model_dump_json(indent=2, exclude_none=True)}"
              )
              yield event
      else:
          logger.info(f"[{self.name}] 어조가 부정적이지 않습니다. 현재 스토리 유지.")

    logger.info(f"[{self.name}] 워크플로 완료.")
    yield self._create_agent_state_event(ctx, end_of_agent=True)
```