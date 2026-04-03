# 협업 에이전트 팀 구축하기

<div class="language-support-tag">
  <span class="lst-supported">ADK 지원</span><span class="lst-python">Python v2.0.0</span><span class="lst-preview">Alpha</span>
</div>

일부 복잡한 작업은 특정 책임을 가진 여러 에이전트를 필요로 하며, 특히 여러 개의
크고 중요한 하위 작업이 반복적으로 이어지는 경우 덜 구조화된 절차가 더 적합할
수 있습니다. ADK의 협업 에이전트 팀에서는 조정 역할의 에이전트가 하나 이상의
서브에이전트에 작업을 위임합니다. 이 접근 방식은 특정 작업을 처리하도록
정의된 서브에이전트와, 작업 완료 후 부모로 자동 복귀하는 메커니즘을 통해,
복잡하고 자율적으로 관리되는 에이전트 시스템을 더 쉽게 구축할 수 있게 합니다.

이 자기 관리형 에이전트 팀 접근 방식을 사용할 때, 서브에이전트에는 동작을
관리하고 작업 범위를 제한하기 위한 ***mode*** 가 할당됩니다. 이 ***mode*** 는
서브에이전트에 대한 일반적인 행동 지침을 설정하고, 더 예측 가능하고 신뢰할 수
있는 멀티에이전트 워크플로를 만듭니다. 협업 모드에는 다음 설정이 있습니다.

- ***Chat***: 전체 사용자 상호작용, 부모 에이전트로의 수동 복귀
  (기본값, 현재 동작)
- ***Task***: 명확화 질문을 위한 사용자 상호작용 가능, 작업 완료 후 부모로 자동 복귀
- ***Single-turn***: 사용자 상호작용 없음, 결과와 함께 자동 복귀하며 병렬 실행 가능

이 가이드는 서브에이전트에 모드를 사용하는 방법과, 이러한 모드가 에이전트
동작에 어떤 영향을 주는지 설명합니다.

!!! example "Alpha 릴리스"

    ADK 2.0은 Alpha 릴리스이며, 이전 버전의 ADK와 함께 사용할 때 호환성이
    깨지는 변경이 발생할 수 있습니다. 프로덕션 환경처럼 하위 호환성이 필요한
    경우에는 ADK 2.0을 사용하지 마세요. 이 릴리스를 테스트해 보시고
    [피드백](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=v2)을
    보내주시기 바랍니다.

## 시작하기

다음 코드 예시는 작은 서브에이전트 팀에 운영 모드를 설정하고 이를 조정
에이전트에 할당하는 방법을 보여줍니다.

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

이 워크플로를 실행하면 `travel_planner` 조정 에이전트가 자동으로 작업을
식별하고 서브에이전트에 할당합니다. 서브에이전트가 작업을 완료하면 자동으로
조정 에이전트로 복귀합니다. 에이전트, 서브에이전트, 워크플로 노드에서
***input_schema*** 와 ***output_schema*** 를 사용해 데이터를 구조화하는 방법은
[에이전트 워크플로의 데이터 처리](/ko/workflows/data-handling/)를
참조하세요.

## 모드 구성과 동작

각 협업 모드에는 특정 동작과 제한이 있습니다. 다음 표는 각 모드로 구성된
서브에이전트의 속성을 비교합니다.

!!! warning "주의: mode는 서브에이전트 전용"

    ***mode*** 설정은 조정 부모 에이전트가 호출하는 서브에이전트에서만 사용하도록
    의도된 것입니다. 루트 에이전트에는 mode 설정을 구성하지 마세요.

<table>
  <thead>
    <tr>
      <th><strong>주제 \ 모드</strong></th>
      <th><code>chat</code> (기본값)</th>
      <th><code>task</code></th>
      <th><code>single_turn</code></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Human in the Loop</strong></td>
      <td>전체 상호작용</td>
      <td>명확화 질문만 허용</td>
      <td>허용되지 않음</td>
    </tr>
    <tr>
      <td><strong>사용자 상호작용</strong></td>
      <td>사용자가 에이전트와 자유롭게 대화</td>
      <td>필요 시 에이전트가 질문</td>
      <td>사용자 상호작용 없음</td>
    </tr>
    <tr>
      <td><strong>제어 흐름</strong></td>
      <td>수동 핸드오프 전까지 에이전트가 제어</td>
      <td>작업 완료 전까지 에이전트가 제어</td>
      <td>작업 직후 즉시 복귀</td>
    </tr>
    <tr>
      <td><strong>병렬 실행</strong></td>
      <td>지원되지 않음</td>
      <td>지원되지 않음</td>
      <td>여러 작업을 병렬 실행 가능</td>
    </tr>
    <tr>
      <td><strong>부모로 복귀</strong></td>
      <td>수동 (transfer 사용)</td>
      <td>자동 (<code>complete_task</code> 사용)</td>
      <td>자동 (결과와 함께)</td>
    </tr>
  </tbody>
</table>

**표 1.** ADK 협업 에이전트 ***mode*** 의 동작과 제한 비교.

## 운영 시 고려 사항

협업 에이전트 모드를 사용할 때는 다음 섹션에서 설명하는 것처럼 제어권 전환과
컨텍스트 관리 측면에서 몇 가지 고려해야 할 점이 있습니다.

### 워크플로 노드와 에이전트 전환

***task*** 또는 ***single-turn*** 모드로 구성된 에이전트는 Workflow Agent
그래프 노드와 ***LlmAgent*** 인스턴스에서 사용할 수 있습니다. 다만 호출하는
부모 에이전트에 따라 실행 전환 동작이 달라집니다.

**워크플로 그래프 노드로 사용할 때:** task 에이전트를 ***SequentialAgent***,
***ParallelAgent*** 같은 워크플로 그래프 안에 배치하면, 에이전트는 자신의
작업을 실행합니다. 완료되면 워크플로 에이전트 그래프 로직에 따라 제어가 다음
노드로 자동 이동합니다.

**LlmAgent에서 전환받는 경우:** 부모 ***LlmAgent*** 가 `request_task`를 통해
task 에이전트로 제어를 넘기면, task 에이전트는 `complete_task`를 호출할 때까지
실행됩니다. 그 시점에 제어는 전환을 시작한 원래 에이전트로 자동 복귀합니다.
이 동작은 제어를 되돌리기 위해 명시적인 `transfer_to_agent` 호출이 필요한
기본 chat ***mode*** 에이전트와 다릅니다.

<table>
  <thead>
    <tr>
      <th><strong>호출 컨텍스트</strong></th>
      <th><strong>작업 완료 후</strong></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>워크플로 노드</td>
      <td>그래프의 다음 노드로 진행</td>
    </tr>
    <tr>
      <td>LlmAgent에서 전환</td>
      <td>제어를 원래 에이전트로 반환</td>
    </tr>
  </tbody>
</table>

이 차이 덕분에 동일한 task 에이전트를 수정 없이 두 컨텍스트 모두에서 재사용할
수 있습니다. 런타임은 에이전트가 어떤 방식으로 호출되었는지에 따라 적절한
제어 흐름을 결정합니다.

### 에이전트 컨텍스트 격리

각 ***task*** 또는 ***single-turn*** 모드 에이전트는 자체적으로 격리된 세션
브랜치에서 동작합니다. 이 에이전트들이 병렬로 실행될 때, 각 에이전트는 AI 모델
호출용 컨텍스트를 구성할 때 자신의 브랜치 이벤트만 볼 수 있으며, 다른 동료
에이전트가 무엇을 하는지는 볼 수 없습니다. 모든 병렬 브랜치가 완료되면 부모
에이전트가 결과를 수집해 이어서 처리할 수 있습니다.

## 알려진 제한 사항

에이전트 협업 모드에는 몇 가지 알려진 제한 사항이 있습니다.

- ***Task* 모드 에이전트** 는 리프 에이전트여야 하며 서브에이전트를 가질 수
  없습니다.
