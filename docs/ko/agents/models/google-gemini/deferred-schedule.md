# Gemini 모델을 사용한 지연 스케줄링

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원됨</span><span class="lst-python">Python v2.10.0</span><span class="lst-preview">프리뷰</span>
</div>

에이전트 워크로드마다 지연 시간(latency) 요구 사항이 다릅니다. 대화형 어시스턴트는 즉시 응답해야 하지만, 요약 작업, 대량 평가 실행 또는 문서 처리 파이프라인은 여유 용량을 기다릴 수 있습니다. 지연 스케줄링(Deferred scheduling)을 사용하면 ADK 에이전트가 대화형 용량을 두고 경쟁하는 대신 오프피크(off-peak) 용량에서 실행되도록 이러한 모델 호출을 대기열에 넣을 수 있습니다.

`RunConfig`의 `service_tier` 설정을 사용하여 실행(run) 단위로 지연 스케줄링을 요청할 수 있습니다. 이 설정은 모델이나 에이전트가 아닌 실행 설정의 일부이므로, 하나의 에이전트 정의로 대화형 요청과 배치 워크로드를 모두 처리할 수 있습니다.

!!! example "프리뷰: 지연 용량 사용에는 허용 목록(allowlist) 액세스가 필요합니다"

    이 Google Cloud 기능은 프리뷰(Preview) 기능이며, 지연 용량에서 요청을 실행하려면 Google Cloud 프로젝트가 허용 목록에 등록되어 있어야 합니다. 자세한 내용은 [자율 에이전트 스케줄링(Autonomous agent scheduling)](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/efficiency/autonomous-scheduling)을 참고하세요.

## 시작하기

지연 스케줄링을 사용하려면 Google Cloud for Gemini [Interactions API](index.md#interactions-api)로 구성된 Gemini 모델이 필요합니다. 다음 예시와 같이 모델에서 `use_interactions_api=True`를 설정한 다음, 에이전트를 실행할 때 `RunConfig(service_tier=ServiceTier.DEFERRED)`를 전달하세요.

=== "Python"

    ```python
    import asyncio

    from google.adk.agents import LlmAgent
    from google.adk.agents import RunConfig
    from google.adk.apps import App
    from google.adk.models import ServiceTier
    from google.adk.models.google_llm import Gemini
    from google.adk.runners import InMemoryRunner
    from google.genai import types

    root_agent = LlmAgent(
        name='batch_agent',
        model=Gemini(
            model='gemini-flash-latest',
            use_interactions_api=True,  # Required for deferred scheduling
        ),
        instruction='Process input documents and produce summaries.',
    )

    app = App(name='batch_app', root_agent=root_agent)
    runner = InMemoryRunner(app=app)


    async def main() -> None:
      session = await runner.session_service.create_session(
          app_name=app.name,
          user_id='user_123',
          session_id='session_456',
      )

      # Request off-peak capacity for every model call in this run.
      run_config = RunConfig(service_tier=ServiceTier.DEFERRED)

      async for event in runner.run_async(
          user_id='user_123',
          session_id=session.id,
          new_message=types.Content(
              role='user',
              parts=[types.Part.from_text(
                  text='Summarize quarterly performance metrics.'
              )],
          ),
          run_config=run_config,
      ):
        if event.content and event.content.parts:
          for part in event.content.parts:
            if part.text:
              print(part.text)


    asyncio.run(main())
    ```

러너(Runner)는 모델 호출을 제출하고 대기열에 등록된 작업이 완료될 때까지 기다린 후 응답 이벤트를 생성(yield)합니다. 코드는 표준 실행과 정확히 동일한 방식으로 이벤트를 소비합니다.

!!! warning "대기하는 동안 실행이 멈춘 것처럼 보일 수 있습니다"

    요청이 대기열에 있는 동안 `run_async()` 메서드는 이벤트를 생성하지 않습니다. 대기 시간은 백엔드 부하에 따라 달라지며 ADK는 상한선을 두지 않습니다. 웹 UI나 터미널에서는 이 지연이 멈춤(hang) 현상처럼 보일 수 있습니다. 진행률 표시기를 표시하거나 [클라이언트 측 마감 시간(deadline)을 설정](#set-a-client-side-deadline)하세요.

등급(tier)이 적용되었는지 확인하려면 애플리케이션 로그에서 다음 메시지를 확인하세요.

| 로그 메시지 | 레벨 | 의미 |
| :--- | :--- | :--- |
| `Using service_tier from run_config: deferred` | `DEBUG` | ADK가 요청에 해당 등급을 적용했습니다. |
| `Interaction <id> is queued; waiting for the result.` | `INFO` | 백엔드가 작업을 대기열에 수락했습니다. |
| `Interaction <id> reached status completed.` | `INFO` | 결과가 준비되었습니다. |
| `run_config.service_tier=... has no effect for agent <name>` | `WARNING` | ADK가 등급 설정을 제외했습니다. [문제 해결](#troubleshooting)을 참고하세요. |

## 지연 스케줄링 작동 방식

표준 모델 요청은 동기식입니다. ADK가 요청을 보내면 모델은 동일한 연결에서 응답을 반환합니다. `ServiceTier.DEFERRED`를 설정하여 지연 스케줄링을 활성화하면 ADK는 요청을 백그라운드 실행으로 표시하고, 백엔드는 이를 대기열에 추가한 뒤 결과 대신 인터랙션 ID(interaction ID)를 즉시 반환합니다.

그런 다음 ADK는 지수 백오프(exponential backoff)를 사용하여 대기열의 작업을 확인하고, 최종 상태에 도달할 때까지 일시적인 읽기 오류를 흡수하면서 결과를 기다립니다. 이후 결과를 일반 응답 이벤트로 변환하여 반환합니다. 이 루프는 내부적으로 처리되므로 인터랙션 ID가 외부에 노출되지 않으며 별도의 조회 코드를 작성할 필요가 없습니다. 다만 대기열 대기 시간 외에 몇 초의 폴링 지연이 추가되므로, 짧고 지연 시간에 민감한 호출에는 지연 스케줄링을 사용하지 않아야 합니다.

대기 동작의 다음 속성은 에이전트 설계 방식에 영향을 미칩니다.

*   **ADK는 클라이언트 측 마감 시간을 설정하지 않습니다.** 인터랙션에 대한 백엔드의 완료 타임아웃이 대기 시간의 유일한 한계입니다. 더 일찍 중단하려면 [클라이언트 측 마감 시간 설정](#set-a-client-side-deadline)을 참고하세요.
*   **각 모델 턴은 개별적으로 대기열에 등록됩니다.** 도구를 호출하는 에이전트에서는 매 턴마다 고유한 인터랙션이 생성되므로, 전체 지연 시간은 실행에 대한 단일 대기가 아니라 모든 턴의 대기열 대기 시간의 합이 됩니다.

## 설정 옵션

`RunConfig`의 `service_tier` 설정은 실행 내 모든 모델 호출에 대한 용량 풀을 선택합니다.

| 옵션 | 타입 | 기본값 | 설명 |
| :--- | :--- | :--- | :--- |
| `service_tier` | `Optional[ServiceTier \| str]` | `None` | 이 실행의 모델 호출에 대한 서빙 등급입니다. |

`ServiceTier` 열거형(enum)은 다음 등급을 정의합니다.

*   `ServiceTier.DEFERRED`: 오프피크 용량에서 실행되도록 호출을 대기열에 넣습니다. 용량이 부족할 때 실패하는 대신 여유 공간이 생길 때까지 기다립니다. 다른 등급은 ADK가 요청을 실행하는 방식을 변경하지 않으며, 이 등급은 스트리밍과 함께 사용할 수 없습니다.
*   `ServiceTier.FLEX`: 지연 시간 보장 없이 더 낮은 비용으로 제공되는 최선형(best-effort) 용량입니다.
*   `ServiceTier.STANDARD`: 기본 등급입니다.
*   `ServiceTier.PRIORITY`: 지연 시간에 민감한 호출을 위한 예약 용량입니다.

`service_tier`를 설정하지 않고 비워 두면 요청에서 해당 필드가 완전히 생략되며, 이는 `ServiceTier.STANDARD`와 동일합니다. `ServiceTier` 열거형은 `str`의 서브클래스이므로 열거형 멤버 대신 `'deferred'`와 같은 일반 문자열을 전달할 수 있습니다. 또한 문자열 형식을 사용하면 ADK에서 상수를 정의하기 전에 백엔드가 지원하는 등급을 먼저 사용할 수 있습니다.

## 고급 사용법

다음 섹션에서는 클라이언트 측 마감 시간으로 지연 실행의 대기 시간을 제한하는 방법과 HTTP를 통해 에이전트를 서빙할 때 지연 스케줄링을 요청하는 방법을 설명합니다.

### 클라이언트 측 마감 시간 설정 {#set-a-client-side-deadline}

지연 요청은 오프피크 용량을 기다리며, 소요 시간은 백엔드 부하에 따라 달라집니다. 총 경과 시간을 제한하려면 실행을 `asyncio.timeout()`으로 감싸세요(Python 3.11 이상 필요).

=== "Python"

    ```python
    import asyncio
    import logging

    from google.adk.agents import RunConfig
    from google.adk.models import ServiceTier
    from google.genai import types

    logger = logging.getLogger(__name__)

    # Continues from the Get started example, reusing runner and session.
    message = types.Content(
        role='user',
        parts=[types.Part.from_text(text='Generate a quarterly summary.')],
    )
    run_config = RunConfig(service_tier=ServiceTier.DEFERRED)

    try:
      async with asyncio.timeout(300):
        async for event in runner.run_async(
            user_id='user_123',
            session_id=session.id,
            new_message=message,
            run_config=run_config,
        ):
          if event.content and event.content.parts:
            for part in event.content.parts:
              if part.text:
                print(part.text)
    except TimeoutError:
      logger.error('Deferred run exceeded the 300 second client deadline.')
    ```

!!! danger "클라이언트 마감 시간은 요청을 취소하지 않습니다"

    타임아웃이 발생하면 ADK는 결과 폴링을 중단하지만 백엔드 작업은 중단되지 않습니다. 대기열에 등록된 요청은 완료될 때까지 실행되어 청구 가능한 사용량을 소비하며, 이후에 그 출력을 가져올 수 없습니다. 타임아웃된 턴은 폐기된 것으로 간주하고, 사용량을 제한하려는 목적으로 클라이언트 마감 시간을 사용하지 마세요.

### HTTP를 통한 지연 스케줄링 요청

`adk api_server`로 서빙하는 에이전트는 `/run` 및 `/run_sse` 엔드포인트의 요청 본문에서 `service_tier`를 허용합니다.

```json
{
  "app_name": "batch_app",
  "user_id": "user_123",
  "session_id": "session_456",
  "new_message": {
    "role": "user",
    "parts": [{"text": "Summarize batch results."}]
  },
  "service_tier": "deferred"
}
```

`/run_sse` 요청의 경우 `"streaming": false`도 함께 설정해야 합니다. `"service_tier": "deferred"`와 `"streaming": true`를 함께 사용하면 HTTP 422가 반환됩니다.
HTTP 요청은 전체 대기열 대기 시간 동안 연결을 열어 두므로, 호스팅 플랫폼의 요청 타임아웃이 지연 실행의 실질적인 제한이 됩니다.

*   **프록시 및 인그레스(ingress) 타임아웃을 늘리세요.** 로드 밸런서와 인그레스 컨트롤러는 기본적으로 장기 실행 백엔드 연결을 닫습니다. [Cloud Run 요청 타임아웃](https://cloud.google.com/run/docs/configuring/request-timeout)과 같은 플랫폼의 제한을 확인하고 예상되는 대기열 대기 시간을 감당할 수 있도록 타임아웃을 늘리세요.
*   **클라이언트 연결 해제는 실행이 아닌 결과 조회를 취소합니다.** 연결이 닫히면 서버는 폴링 작업을 취소합니다. 대기열에 있는 요청은 계속 실행되어 청구 가능한 사용량을 소비하며 출력 결과는 손실됩니다.

오랜 시간 대기할 수 있는 지연 워크로드의 경우, 대신 Google Cloud Agent Platform의 [Agent Runtime](/ko/deploy/agent-runtime/)에 배포하세요. Agent Runtime은 관리형 컨테이너에서 호출(invocation)을 실행하며 이를 위해 HTTP 연결을 열어 두지 않습니다.

## 제한 사항

지연 스케줄링에는 다음 제한 사항이 적용됩니다.

*   **허용 목록 액세스:** 지연 용량을 사용하려면 Google Cloud 프로젝트가 허용 목록에 등록되어 있어야 합니다.
*   **Gemini 및 Interactions API 전용:** 지연 스케줄링은 `use_interactions_api=True`를 설정한 `Gemini` 모델에서만 작동합니다. 커스텀 `BaseLlm` 서브클래스를 포함한 다른 모든 모델은 이 등급을 무시합니다.
*   **스트리밍과 호환되지 않음:** `RunConfig(service_tier=ServiceTier.DEFERRED, streaming_mode=StreamingMode.SSE)`를 생성하면 `pydantic.ValidationError`가 발생합니다.
*   **`ManagedAgent` 클래스는 등급을 무시함:** 자체 인터랙션 루프를 실행하며 `service_tier`를 읽지 않습니다.
*   **재시작 간 재개 불가:** ADK는 진행 중인 인터랙션 ID를 영구 저장하지 않으며, 대기열에 있는 인터랙션에 실행을 다시 연결하는 방법을 제공하지 않습니다. 클라이언트 프로세스가 중단되면 ADK는 보류 중인 작업을 포기하고 다음 실행에서 새로운 인터랙션을 생성합니다.

## 문제 해결 {#troubleshooting}

다음 섹션에서는 지연 스케줄링을 사용할 때 발생할 수 있는 일반적인 문제와 해결 방법을 설명합니다.

### ADK가 등급을 무시하고 실행은 계속 성공하는 경우

에이전트의 모델이 `use_interactions_api=True`가 설정된 `Gemini` 인스턴스가 아닌 경우, ADK는 등급을 제외하고 실행당 한 번 경고를 로깅한 후 표준 용량에서 호출을 실행합니다. 실행이 성공하므로 로그가 유일한 신호입니다.

```text
run_config.service_tier=... has no effect for agent <name>: its model does not
use the interactions API, which is the only path with a serving tier. Set
use_interactions_api=True on the model to apply the tier.
```

이 경고는 의도된 것입니다. 다중 에이전트 실행에서는 일부 에이전트만 Interactions API를 사용할 수 있으므로, 사용할 수 없는 등급에 대해 예외를 발생시키는 대신 경고를 표시합니다. 로그에서 `has no effect for agent`를 검색하여 `use_interactions_api=True`가 필요한 모델을 찾으세요.

### OpenAI `service_tier` 필드

`OpenAIResponsesLlm` 클래스에도 `service_tier` 필드가 있습니다. 이는 서로 관련이 없는 별개의 설정으로, 실행이 아닌 모델에 설정하며 `RunConfig.service_tier`가 전달되지 않습니다. 한쪽을 설정해도 다른 쪽에는 영향을 미치지 않습니다.

## 추가 리소스

*   [Gemini Interactions API](index.md#interactions-api)
*   [런타임 설정](/ko/runtime/runconfig/)
*   [Interactions API 코드 샘플](https://github.com/google/adk-python/tree/main/contributing/samples/models/interactions_api)
