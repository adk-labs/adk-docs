# 라이브 에이전트를 위한 그래프 워크플로

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v2.0.0</span>
</div>

라이브 에이전트는 다른 ADK 에이전트와 마찬가지로 동일한 그래프 워크플로로 구성할 수 있습니다. 노드와 엣지 정의, 라우팅, 상태 관리는 [그래프 워크플로](../graphs/index.md)에서 다루며, 더 넓은 멀티 에이전트 개념은 [워크플로](../workflows/index.md)에서 다룹니다. 라이브 연결에서 변경되는 것은 실행 모델입니다.

`run_live()` 환경에서는 전체 에이전트 파이프라인이 *하나의 열린 연결과 하나의 이벤트 루프 내부*에서 실행되므로, 발신자는 하나의 끊김 없는 연속적인 대화를 경험하게 됩니다. 제어권이 한 에이전트에서 다음 에이전트로 넘어가는 동안에도 사용자는 계속해서 말할 수 있으며, 전환 과정을 전혀 의식하지 못합니다.

이는 코드 작성 방식에도 영향을 미칩니다. 요청/응답 에이전트에서는 각 에이전트 전환이 직접 제어하는 새로운 호출이지만, 라이브 워크플로에서는 몇 개의 에이전트를 거치든 전체 워크플로에 대해 하나의 루프와 하나의 큐만 사용합니다.

## 그래프에서 에이전트 실행하기

그래프 [`Workflow`](../graphs/index.md)는 ADK 2.0에서 라이브 에이전트의 실행 순서를 지정하는 방법입니다. 에이전트를 노드로 정의하고 엣지로 연결하면 러너가 단일 라이브 세션에 걸쳐 그래프를 순회합니다:

```python
from google.adk.agents.llm_agent import Agent
from google.adk.workflow import START, Workflow

LIVE_MODEL = 'gemini-live-2.5-flash-native-audio'

greeter = Agent(
    model=LIVE_MODEL,
    name='greeter',
    mode='task',  # 노드가 라이브 연결을 사용하기 위해 필수적임
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

`adk web`으로 이를 제공하고 라이브 세션을 시작하거나, `Runner.run_live()`에 전달합니다. 러너는 `Workflow` 루트를 감지하고 라이브 연결을 통해 이를 구동하며, 개발자는 모든 노드에 걸쳐 단일 이벤트 스트림을 소비합니다. 타입이 지정된 핸드오프와 라이브 평가 세트를 포함하는 3단계 음성 접수 흐름에 대한 실행 가능한 샘플은 [`live_workflow` 샘플](https://github.com/google/adk-python/tree/main/contributing/samples/live/live_workflow)을 참고하세요.

**말을 하는 모든 에이전트에는 `mode='task'` 또는 `mode='chat'`이 필요합니다.** 워크플로의 노드로서 `mode`가 없는 `LlmAgent`는 `single_turn`으로 폴백되어 라이브 연결 외부에서 실행되고 오디오 큐를 완전히 무시하므로, 발신자는 해당 에이전트의 음성을 전혀 들을 수 없습니다. 대화하는 모든 노드에 모드를 명시적으로 설정하세요.

각 노드는 해당 노드가 실행되는 동안 자체 Live API 세션을 열며, 워크플로의 `LiveRequestQueue`는 순차적으로 노드 간에 공유됩니다. 단일 큐는 동시에 두 개의 라이브 노드에 데이터를 공급할 수 없으므로 라이브 노드를 팬아웃(병렬 분기)하지 말고 하나의 경로에 유지하세요.

## 단일 이벤트 스트림 읽기

노드가 전환되더라도 스트림은 끊김 없이 이어집니다. 하나의 루프와 하나의 큐로 스트림을 소비하고, `event.author`를 읽어 현재 말하고 있는 에이전트를 구분합니다.

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

에이전트마다 새로운 `run_live()` 루프나 새로운 `LiveRequestQueue`를 열지 마세요. 하나의 루프와 하나의 큐가 전체 워크플로를 처리하며, 사용자 입력은 현재 활성화된 노드로 전달됩니다.

## 대화 도중 핸드오프(인계)

코디네이터 에이전트는 `transfer_to_agent`를 통해 세션 도중 전문 에이전트에게 대화를 전달할 수 있습니다. 핸드오프는 동일한 `run_live()` 루프 내에서 발생합니다. ADK는 코디네이터의 라이브 연결을 닫고 전문 에이전트를 위한 새로운 연결을 열며, 사용자는 끊김 없이 계속 대화합니다.

```text
User: "I need help with billing"
Event: author="coordinator", function_call: transfer_to_agent(agent_name="billing")
Event: author="billing", text="I can help with your billing question..."
```

전송 시 대상 에이전트를 위한 새 Live API 세션이 시작되므로 코디네이터의 세션 재개 핸들은 이어지지 않습니다. 전송을 코디네이터 자체 팀 내로 제한하려면 서브 에이전트에 `disallow_transfer_to_peers`를 설정하세요. 허용되지 않은 형제 에이전트 간 전송은 `ValueError`를 발생시킵니다.

## 레거시 워크플로 에이전트

새 코드에는 그래프 `Workflow`를 사용하세요. `SequentialAgent`, `LoopAgent`, `ParallelAgent`는 **`Workflow`로 대체되어 더 이상 권장되지 않으며(deprecated)** 향후 릴리스에서 제거될 예정입니다. `LoopAgent`와 `ParallelAgent`는 `run_live()`에서 `NotImplementedError`를 발생시켜 라이브 세션을 중단시키므로 라이브 경로에 두지 마세요.

`SequentialAgent`는 라이브 모드에서 계속 실행할 수 있습니다. 이때 ADK는 각 직접 `LlmAgent` 서브 에이전트에 `task_completed` 도구를 추가하고, 작업이 완료되었을 때 이를 호출하도록 모델에 지침을 추가합니다. `task_completed`를 호출하면 해당 서브 에이전트의 라이브 연결이 종료되고 시퀀스의 다음 에이전트로 진행합니다.

```python
# ADK는 라이브 실행 시점에 각 LlmAgent 서브 에이전트에 이를 주입합니다.
def task_completed():
    """Signals that the agent has completed the user's task."""
    return 'Task completion signaled.'
```

이벤트 스트림은 일반적인 라이브 워크플로처럼 보입니다. 에이전트별 이벤트 실행 후 `task_completed` 함수 응답이 오고, 다음 에이전트가 시작됩니다:

```text
Event: author="researcher", function_call: task_completed()
Event: author="writer", text="Based on the research..."
```

`task_completed`와 `transfer_to_agent`는 서로 다른 이유로 에이전트의 턴을 종료합니다:

| 함수 | 패턴 | 효과 |
|---|---|---|
| `task_completed` | 고정된 시퀀스 | 현재 에이전트를 종료하고, 시퀀스의 다음 에이전트가 시작됨 |
| `transfer_to_agent` | 동적 라우팅 | 현재 라이브 세션을 닫고, 대상 에이전트를 위한 새 세션이 열림 |
