# 에이전트 세션 되감기(Rewind)

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.17.0</span>
</div>

ADK 세션 Rewind 기능을 사용하면 세션을 이전 요청 상태로 되돌릴 수 있어,
실수를 되돌리거나, 대체 경로를 탐색하거나, 정상 동작 지점에서 프로세스를
다시 시작할 수 있습니다. 이 문서는 기능 개요, 사용 방법,
제한 사항을 설명합니다.

## 세션 되감기

세션을 되감을 때는 되돌리고 싶은 사용자 요청(***invocation***)을 지정하면,
해당 요청과 그 이후 요청이 함께 취소됩니다.
예를 들어 요청이 세 개(A, B, C)이고 A 시점 상태로 돌아가고 싶다면
B를 지정해야 하며, 그러면 B와 C의 변경 사항이 취소됩니다. 세션은
***Runner*** 인스턴스의 rewind 메서드를 사용해 되감을 수 있으며,
아래 코드 스니펫처럼 사용자, 세션, invocation id를 지정합니다:

```python
# Create runner
runner = InMemoryRunner(
    agent=agent.root_agent,
    app_name=APP_NAME,
)

# Create a session
session = await runner.session_service.create_session(
    app_name=APP_NAME, user_id=USER_ID
)
# call agent with wrapper function "call_agent_async()"
await call_agent_async(
    runner, USER_ID, session.id, "set state color to red"
)
# ... more agent calls ...
events_list = await call_agent_async(
    runner, USER_ID, session.id, "update state color to blue"
)

# get invocation id
rewind_invocation_id=events_list[1].invocation_id

# rewind invocations (state color: red)
await runner.rewind_async(
    user_id=USER_ID,
    session_id=session.id,
    rewind_before_invocation_id=rewind_invocation_id,
)
```

***rewind*** 메서드를 호출하면, ADK가 관리하는 모든 세션 레벨 리소스는
지정한 ***invocation id*** 이전 상태로 복원됩니다. 다만 앱 레벨/사용자 레벨
상태 및 아티팩트 같은 전역 리소스는 복원되지 않습니다. 전체 예시는
[rewind_session](https://github.com/google/adk-python/tree/main/contributing/samples/rewind_session)
샘플 코드를 참고하세요. Rewind 기능 제한 사항에 대한 자세한 내용은
[제한 사항](#limitations)을 참조하세요.

## 동작 방식

Rewind 기능은 지정한 invocation id의 되감기 지점 *이전* 상태로
세션 상태와 아티팩트를 복원하는 특수한 ***rewind*** 요청을 생성합니다.
이 접근 방식은 되감긴 요청을 포함해 모든 요청이 이후 디버깅, 분석,
감사를 위해 로그에 보존됨을 의미합니다. 되감기 이후에는 시스템이
AI 모델에 다음 요청을 준비할 때 되감긴 요청을 무시합니다. 따라서 에이전트가
사용하는 AI 모델은 되감기 지점부터 다음 요청 직전까지의 상호작용을
사실상 잊게 됩니다.

## 제한 사항 {#limitations}

Rewind 기능을 에이전트 워크플로우에서 사용할 때 알아두어야 할 제한 사항:

*   **전역 에이전트 리소스:** 앱 레벨 및 사용자 레벨 상태/아티팩트는
    되감기 기능으로 *복원되지 않습니다*. 세션 레벨 상태/아티팩트만
    복원됩니다.
*   **외부 의존성:** 되감기 기능은 외부 의존성을 관리하지 않습니다.
    에이전트 도구가 외부 시스템과 상호작용한다면,
    해당 시스템을 이전 상태로 복원하는 책임은 사용자에게 있습니다.
*   **원자성(Atomicity):** 상태 업데이트, 아티팩트 업데이트, 이벤트 영속화는
    단일 원자 트랜잭션으로 수행되지 않습니다.
    따라서 불일치를 방지하려면 활성 세션을 되감거나,
    되감기 중에 세션 아티팩트를 동시에 조작하는 것을 피해야 합니다.
