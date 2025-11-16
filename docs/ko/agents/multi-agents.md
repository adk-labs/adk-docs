# ADK의 다중 에이전트 시스템

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

에이전트 기반 애플리케이션이 복잡해짐에 따라, 단일 모놀리식 에이전트로 구조화하는 것은 개발, 유지보수 및 추론이 어려워질 수 있습니다. 에이전트 개발 키트(ADK)는 여러 개의 고유한 `BaseAgent` 인스턴스를 **다중 에이전트 시스템(MAS)**으로 구성하여 정교한 애플리케이션을 구축하는 것을 지원합니다.

ADK에서 다중 에이전트 시스템은 종종 계층 구조를 형성하는 여러 에이전트가 더 큰 목표를 달성하기 위해 협력하거나 조정하는 애플리케이션입니다. 애플리케이션을 이런 방식으로 구조화하면 향상된 모듈성, 전문화, 재사용성, 유지보수성 및 전용 워크플로 에이전트를 사용한 구조적 제어 흐름 정의 능력 등 상당한 이점을 얻을 수 있습니다.

`BaseAgent`에서 파생된 다양한 유형의 에이전트를 구성하여 이러한 시스템을 구축할 수 있습니다.

* **LLM 에이전트:** 대규모 언어 모델로 구동되는 에이전트. ([LLM 에이전트](llm-agents.md) 참조)
* **워크플로 에이전트:** 하위 에이전트의 실행 흐름을 관리하도록 설계된 특수 에이전트(`SequentialAgent`, `ParallelAgent`, `LoopAgent`). ([워크플로 에이전트](workflow-agents/index.md) 참조)
* **커스텀 에이전트:** `BaseAgent`를 상속받아 비-LLM 로직을 가진 자체 특수 에이전트. ([커스텀 에이전트](custom-agents.md) 참조)

다음 섹션에서는 이러한 다중 에이전트 시스템을 효과적으로 구축하고 관리할 수 있게 해주는 에이전트 계층 구조, 워크플로 에이전트, 상호작용 메커니즘과 같은 핵심 ADK 기본 요소(primitives)를 자세히 설명합니다.

## 1. 에이전트 구성을 위한 ADK 기본 요소 { #adk-primitives-for-agent-composition }

ADK는 다중 에이전트 시스템 내에서 상호작용을 구조화하고 관리할 수 있도록 하는 핵심 구성 요소인 기본 요소(primitives)를 제공합니다.

!!! Note
    기본 요소에 대한 특정 매개변수나 메서드 이름은 SDK 언어에 따라 약간 다를 수 있습니다(예: Python의 `sub_agents`, Java의 `subAgents`). 자세한 내용은 언어별 API 문서를 참조하세요.

### 1.1. 에이전트 계층 구조 (부모 에이전트, 하위 에이전트) { #agent-hierarchy-parent-agent-sub-agents }

다중 에이전트 시스템을 구조화하는 기반은 `BaseAgent`에 정의된 부모-자식 관계입니다.

* **계층 구조 설정:** 부모 에이전트를 초기화할 때 `sub_agents` 인수에 에이전트 인스턴스 목록을 전달하여 트리 구조를 만듭니다. ADK는 초기화 중에 각 자식 에이전트에 `parent_agent` 속성을 자동으로 설정합니다.
* **단일 부모 규칙:** 에이전트 인스턴스는 한 번만 하위 에이전트로 추가될 수 있습니다. 두 번째 부모를 할당하려고 하면 `ValueError`가 발생합니다.
* **중요성:** 이 계층 구조는 [워크플로 에이전트](#12-workflow-agents-as-orchestrators)의 범위를 정의하고 LLM 기반 위임의 잠재적 대상을 결정하는 데 영향을 줍니다. `agent.parent_agent`를 사용하여 계층 구조를 탐색하거나 `agent.find_agent(name)`를 사용하여 하위 에이전트를 찾을 수 있습니다.

=== "Python"

    ```python
    # 개념 예시: 계층 구조 정의
    from google.adk.agents import LlmAgent, BaseAgent
    
    # 개별 에이전트 정의
    greeter = LlmAgent(name="Greeter", model="gemini-2.0-flash")
    task_doer = BaseAgent(name="TaskExecutor") # 커스텀 비-LLM 에이전트
    
    # 부모 에이전트를 생성하고 sub_agents를 통해 자식 할당
    coordinator = LlmAgent(
        name="Coordinator",
        model="gemini-2.0-flash",
        description="인사와 작업을 조정합니다.",
        sub_agents=[ # 여기에 sub_agents 할당
            greeter,
            task_doer
        ]
    )
    
    # 프레임워크가 자동으로 설정:
    # assert greeter.parent_agent == coordinator
    # assert task_doer.parent_agent == coordinator
    ```

=== "Java"

    ```java
    // 개념 예시: 계층 구조 정의
    import com.google.adk.agents.SequentialAgent;
    import com.google.adk.agents.LlmAgent;
    
    // 개별 에이전트 정의
    LlmAgent greeter = LlmAgent.builder().name("Greeter").model("gemini-2.0-flash").build();
    SequentialAgent taskDoer = SequentialAgent.builder().name("TaskExecutor").subAgents(...).build(); // 순차 에이전트
    
    // 부모 에이전트를 생성하고 sub_agents 할당
    LlmAgent coordinator = LlmAgent.builder()
        .name("Coordinator")
        .model("gemini-2.0-flash")
        .description("인사와 작업을 조정합니다.")
        .subAgents(greeter, taskDoer) // 여기에 sub_agents 할당
        .build();
    
    // 프레임워크가 자동으로 설정:
    // assert greeter.parentAgent().equals(coordinator);
    // assert taskDoer.parentAgent().equals(coordinator);
    ```

=== "Go"

    ```go
    import (
        "google.golang.org/adk/agent"
        "google.golang.org/adk/agent/llmagent"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:hierarchy"
    ```

### 1.2. 오케스트레이터로서의 워크플로 에이전트 { #workflow-agents-as-orchestrators }

ADK는 자체적으로 작업을 수행하지 않고 `sub_agents`의 실행 흐름을 조율(orchestrate)하는 `BaseAgent`에서 파생된 특수 에이전트를 포함합니다.

* **[`SequentialAgent`](workflow-agents/sequential-agents.md):** `sub_agents`를 나열된 순서대로 하나씩 실행합니다.
    * **컨텍스트:** *동일한* [`InvocationContext`](../runtime/index.md)를 순차적으로 전달하여 에이전트가 공유 상태를 통해 쉽게 결과를 전달할 수 있도록 합니다.

=== "Python"

    ```python
    # 개념 예시: 순차 파이프라인
    from google.adk.agents import SequentialAgent, LlmAgent

    step1 = LlmAgent(name="Step1_Fetch", output_key="data") # 출력을 state['data']에 저장
    step2 = LlmAgent(name="Step2_Process", instruction="{data}에서 데이터를 처리합니다.")

    pipeline = SequentialAgent(name="MyPipeline", sub_agents=[step1, step2])
    # pipeline이 실행되면 Step2는 Step1이 설정한 state['data']에 접근할 수 있습니다.
    ```

=== "Java"

    ```java
    // 개념 예시: 순차 파이프라인
    import com.google.adk.agents.SequentialAgent;
    import com.google.adk.agents.LlmAgent;

    LlmAgent step1 = LlmAgent.builder().name("Step1_Fetch").outputKey("data").build(); // 출력을 state.get("data")에 저장
    LlmAgent step2 = LlmAgent.builder().name("Step2_Process").instruction("Process data from {data}.").build();

    SequentialAgent pipeline = SequentialAgent.builder().name("MyPipeline").subAgents(step1, step2).build();
    // pipeline이 실행되면 Step2는 Step1이 설정한 state.get("data")에 접근할 수 있습니다.
    ```

=== "Go"

    ```go
    import (
        "google.golang.org/adk/agent"
        "google.golang.org/adk/agent/llmagent"
        "google.golang.org/adk/agent/workflowagents/sequentialagent"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:sequential-pipeline"
    ```

* **[`ParallelAgent`](workflow-agents/parallel-agents.md):** `sub_agents`를 병렬로 실행합니다. 하위 에이전트의 이벤트는 서로 섞여 발생할 수 있습니다.
    * **컨텍스트:** 각 자식 에이전트에 대해 `InvocationContext.branch`를 수정하여(예: `ParentBranch.ChildName`) 고유한 컨텍스트 경로를 제공하며, 이는 일부 메모리 구현에서 히스토리를 격리하는 데 유용할 수 있습니다.
    * **상태:** 브랜치가 다르더라도 모든 병렬 자식은 *동일한 공유* `session.state`에 접근하여 초기 상태를 읽고 결과를 쓸 수 있습니다(경쟁 조건을 피하기 위해 고유한 키 사용).

=== "Python"

    ```python
    # 개념 예시: 병렬 실행
    from google.adk.agents import ParallelAgent, LlmAgent

    fetch_weather = LlmAgent(name="WeatherFetcher", output_key="weather")
    fetch_news = LlmAgent(name="NewsFetcher", output_key="news")

    gatherer = ParallelAgent(name="InfoGatherer", sub_agents=[fetch_weather, fetch_news])
    # gatherer가 실행되면 WeatherFetcher와 NewsFetcher가 동시에 실행됩니다.
    # 후속 에이전트는 state['weather']와 state['news']를 읽을 수 있습니다.
    ```
  
=== "Java"

    ```java
    // 개념 예시: 병렬 실행
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.agents.ParallelAgent;
   
    LlmAgent fetchWeather = LlmAgent.builder()
        .name("WeatherFetcher")
        .outputKey("weather")
        .build();
    
    LlmAgent fetchNews = LlmAgent.builder()
        .name("NewsFetcher")
        .instruction("news")
        .build();
    
    ParallelAgent gatherer = ParallelAgent.builder()
        .name("InfoGatherer")
        .subAgents(fetchWeather, fetchNews)
        .build();
    
    // gatherer가 실행되면 WeatherFetcher와 NewsFetcher가 동시에 실행됩니다.
    // 후속 에이전트는 state['weather']와 state['news']를 읽을 수 있습니다.
    ```

=== "Go"

    ```go
    import (
        "google.golang.org/adk/agent"
        "google.golang.org/adk/agent/llmagent"
        "google.golang.org/adk/agent/workflowagents/parallelagent"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:parallel-execution"
    ```

  * **[`LoopAgent`](workflow-agents/loop-agents.md):** `sub_agents`를 루프 안에서 순차적으로 실행합니다.
      * **종료:** 선택적 `max_iterations`에 도달하거나, 하위 에이전트가 `Event Actions`에 `escalate=True`를 포함한 [`Event`](../events/index.md)를 반환하면 루프가 중지됩니다.
      * **컨텍스트 및 상태:** 각 반복에서 *동일한* `InvocationContext`를 전달하여 상태 변경(예: 카운터, 플래그)이 루프 간에 유지되도록 합니다.

=== "Python"

      ```python
      # 개념 예시: 조건부 루프
      from google.adk.agents import LoopAgent, LlmAgent, BaseAgent
      from google.adk.events import Event, EventActions
      from google.adk.agents.invocation_context import InvocationContext
      from typing import AsyncGenerator

      class CheckCondition(BaseAgent): # 상태를 확인하는 커스텀 에이전트
          async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
              status = ctx.session.state.get("status", "pending")
              is_done = (status == "completed")
              yield Event(author=self.name, actions=EventActions(escalate=is_done)) # 완료되면 escalate

      process_step = LlmAgent(name="ProcessingStep") # state['status']를 업데이트할 수 있는 에이전트

      poller = LoopAgent(
          name="StatusPoller",
          max_iterations=10,
          sub_agents=[process_step, CheckCondition(name="Checker")]
      )
      # poller가 실행되면 Checker가 escalate할 때(state['status'] == 'completed')까지 또는 10회 반복될 때까지
      # process_step과 Checker를 반복적으로 실행합니다.
      ```
    
=== "Java"

    ```java
    // 개념 예시: 조건부 루프
    // 상태를 확인하고 잠재적으로 escalate하는 커스텀 에이전트
    public static class CheckConditionAgent extends BaseAgent {
      public CheckConditionAgent(String name, String description) {
        super(name, description, List.of(), null, null);
      }
  
      @Override
      protected Flowable<Event> runAsyncImpl(InvocationContext ctx) {
        String status = (String) ctx.session().state().getOrDefault("status", "pending");
        boolean isDone = "completed".equalsIgnoreCase(status);

        // 조건이 충족되면 escalate(루프 종료) 신호를 보내는 이벤트를 발행합니다.
        // 완료되지 않으면 escalate 플래그는 false이거나 없어 루프가 계속됩니다.
        Event checkEvent = Event.builder()
                .author(name())
                .id(Event.generateEventId()) // 이벤트에 고유 ID를 부여하는 것이 중요합니다
                .actions(EventActions.builder().escalate(isDone).build()) // 완료되면 escalate
                .build();
        return Flowable.just(checkEvent);
      }
    }
  
    // state.put("status")를 업데이트할 수 있는 에이전트
    LlmAgent processingStepAgent = LlmAgent.builder().name("ProcessingStep").build();
    // 조건 확인을 위한 커스텀 에이전트 인스턴스
    CheckConditionAgent conditionCheckerAgent = new CheckConditionAgent(
        "ConditionChecker",
        "상태가 'completed'인지 확인합니다."
    );
    LoopAgent poller = LoopAgent.builder().name("StatusPoller").maxIterations(10).subAgents(processingStepAgent, conditionCheckerAgent).build();
    // poller가 실행되면 Checker가 escalate할 때(state.get("status") == "completed")까지 또는 10회 반복될 때까지
    // processingStepAgent와 conditionCheckerAgent를 반복적으로 실행합니다.
    ```

=== "Go"

    ```go
    import (
        "iter"
        "google.golang.org/adk/agent"
        "google.golang.org/adk/agent/llmagent"
        "google.golang.org/adk/agent/workflowagents/loopagent"
        "google.golang.org/adk/session"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:loop-with-condition"
    ```

### 1.3. 상호작용 및 통신 메커니즘 { #interaction-communication-mechanisms }

시스템 내의 에이전트는 종종 서로 데이터를 교환하거나 동작을 트리거해야 합니다. ADK는 이를 다음과 같이 지원합니다.

#### a) 공유 세션 상태 (`session.state`)

동일한 호출 내에서 작동하여 `InvocationContext`를 통해 동일한 [`Session`](../sessions/session.md) 객체를 공유하는 에이전트들이 수동적으로 통신하는 가장 기본적인 방법입니다.

* **메커니즘:** 한 에이전트(또는 그 도구/콜백)가 값을 쓰고(`context.state['data_key'] = processed_data`), 후속 에이전트가 이를 읽습니다(`data = context.state.get('data_key')`). 상태 변경은 [`CallbackContext`](../callbacks/index.md)를 통해 추적됩니다.
* **편의성:** [`LlmAgent`](llm-agents.md)의 `output_key` 속성은 에이전트의 최종 응답 텍스트(또는 구조화된 출력)를 지정된 상태 키에 자동으로 저장합니다.
* **특성:** 비동기적, 수동적 통신. `SequentialAgent`에 의해 조율되는 파이프라인이나 `LoopAgent` 반복 간 데이터 전달에 이상적입니다.
* **참고:** [상태 관리](../sessions/state.md)

!!! note "호출 컨텍스트와 `temp:` 상태"
    부모 에이전트가 하위 에이전트를 호출할 때 동일한 `InvocationContext`를 전달합니다. 이는 그들이 동일한 임시(`temp:`) 상태를 공유한다는 것을 의미하며, 현재 턴에만 관련된 데이터를 전달하는 데 이상적입니다.

=== "Python"

    ```python
    # 개념 예시: output_key 사용 및 상태 읽기
    from google.adk.agents import LlmAgent, SequentialAgent
    
    agent_A = LlmAgent(name="AgentA", instruction="프랑스의 수도를 찾으세요.", output_key="capital_city")
    agent_B = LlmAgent(name="AgentB", instruction="{capital_city}에 저장된 도시에 대해 알려주세요.")
    
    pipeline = SequentialAgent(name="CityInfo", sub_agents=[agent_A, agent_B])
    # AgentA가 실행되어 "Paris"를 state['capital_city']에 저장합니다.
    # AgentB가 실행되어 instruction 프로세서가 state['capital_city']를 읽어 "Paris"를 가져옵니다.
    ```

=== "Java"

    ```java
    // 개념 예시: outputKey 사용 및 상태 읽기
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.agents.SequentialAgent;
    
    LlmAgent agentA = LlmAgent.builder()
        .name("AgentA")
        .instruction("Find the capital of France.")
        .outputKey("capital_city")
        .build();
    
    LlmAgent agentB = LlmAgent.builder()
        .name("AgentB")
        .instruction("Tell me about the city stored in {capital_city}.")
        .outputKey("capital_city")
        .build();
    
    SequentialAgent pipeline = SequentialAgent.builder().name("CityInfo").subAgents(agentA, agentB).build();
    // AgentA가 실행되어 "Paris"를 state('capital_city')에 저장합니다.
    // AgentB가 실행되어 instruction 프로세서가 state.get("capital_city")를 읽어 "Paris"를 가져옵니다.
    ```

=== "Go"

    ```go
    import (
        "google.golang.org/adk/agent"
        "google.golang.org/adk/agent/llmagent"
        "google.golang.org/adk/agent/workflowagents/sequentialagent"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:output-key-state"
    ```

#### b) LLM 기반 위임 (에이전트 전환)

[`LlmAgent`](llm-agents.md)의 이해 능력을 활용하여 계층 구조 내의 다른 적합한 에이전트로 작업을 동적으로 라우팅합니다.

* **메커니즘:** 에이전트의 LLM이 특정 함수 호출을 생성합니다: `transfer_to_agent(agent_name='target_agent_name')`.
* **처리:** 하위 에이전트가 존재하거나 전환이 금지되지 않은 경우 기본적으로 사용되는 `AutoFlow`가 이 호출을 가로챕니다. `root_agent.find_agent()`를 사용하여 대상 에이전트를 식별하고 `InvocationContext`를 업데이트하여 실행 초점을 전환합니다.
* **요구사항:** 호출하는 `LlmAgent`는 언제 전환할지에 대한 명확한 `instructions`이 필요하며, 잠재적 대상 에이전트는 LLM이 정보에 입각한 결정을 내릴 수 있도록 고유한 `description`이 필요합니다. 전환 범위(부모, 하위 에이전트, 형제)는 `LlmAgent`에서 구성할 수 있습니다.
* **특성:** LLM 해석에 기반한 동적이고 유연한 라우팅.

=== "Python"

    ```python
    # 개념 설정: LLM 전환
    from google.adk.agents import LlmAgent
    
    booking_agent = LlmAgent(name="Booker", description="항공편 및 호텔 예약을 처리합니다.")
    info_agent = LlmAgent(name="Info", description="일반 정보 제공 및 질문에 답변합니다.")
    
    coordinator = LlmAgent(
        name="Coordinator",
        model="gemini-2.0-flash",
        instruction="당신은 어시스턴트입니다. 예약 작업은 Booker에게, 정보 요청은 Info에게 위임하세요.",
        description="메인 코디네이터.",
        # AutoFlow는 일반적으로 여기에 암시적으로 사용됩니다
        sub_agents=[booking_agent, info_agent]
    )
    # coordinator가 "항공편 예약해줘"라는 요청을 받으면, LLM은 다음을 생성해야 합니다:
    # FunctionCall(name='transfer_to_agent', args={'agent_name': 'Booker'})
    # 그러면 ADK 프레임워크가 실행을 booking_agent로 라우팅합니다.
    ```

=== "Java"

    ```java
    // 개념 설정: LLM 전환
    import com.google.adk.agents.LlmAgent;
    
    LlmAgent bookingAgent = LlmAgent.builder()
        .name("Booker")
        .description("항공편 및 호텔 예약을 처리합니다.")
        .build();
    
    LlmAgent infoAgent = LlmAgent.builder()
        .name("Info")
        .description("일반 정보 제공 및 질문에 답변합니다.")
        .build();
    
    // 코디네이터 에이전트 정의
    LlmAgent coordinator = LlmAgent.builder()
        .name("Coordinator")
        .model("gemini-2.0-flash") // 또는 원하는 모델
        .instruction("당신은 어시스턴트입니다. 예약 작업은 Booker에게, 정보 요청은 Info에게 위임하세요.")
        .description("메인 코디네이터.")
        // AutoFlow는 하위 에이전트가 있고 전환이 금지되지 않았기 때문에
        // 기본적으로 (암시적으로) 사용됩니다.
        .subAgents(bookingAgent, infoAgent)
        .build();

    // coordinator가 "항공편 예약해줘"라는 요청을 받으면, LLM은 다음을 생성해야 합니다:
    // FunctionCall.builder.name("transferToAgent").args(ImmutableMap.of("agent_name", "Booker")).build()
    // 그러면 ADK 프레임워크가 실행을 bookingAgent로 라우팅합니다.
    ```

=== "Go"

    ```go
    import (
        "google.golang.org/adk/agent/llmagent"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:llm-transfer"
    ```

#### c) 명시적 호출 (`AgentTool`)

[`LlmAgent`](llm-agents.md)가 다른 `BaseAgent` 인스턴스를 호출 가능한 함수나 [도구](../tools/index.md)로 취급할 수 있게 합니다.

* **메커니즘:** 대상 에이전트 인스턴스를 `AgentTool`로 감싸고 부모 `LlmAgent`의 `tools` 목록에 포함시킵니다. `AgentTool`은 LLM을 위한 해당 함수 선언을 생성합니다.
* **처리:** 부모 LLM이 `AgentTool`을 대상으로 하는 함수 호출을 생성하면, 프레임워크는 `AgentTool.run_async`를 실행합니다. 이 메서드는 대상 에이전트를 실행하고, 최종 응답을 캡처하고, 모든 상태/아티팩트 변경 사항을 부모의 컨텍스트로 다시 전달하며, 응답을 도구의 결과로 반환합니다.
* **특성:** 다른 도구와 마찬가지로 동기적(부모의 흐름 내에서), 명시적이고 제어된 호출.
* **(참고:** `AgentTool`은 명시적으로 가져와서 사용해야 합니다).

=== "Python"

    ```python
    # 개념 설정: 도구로서의 에이전트
    from google.adk.agents import LlmAgent, BaseAgent
    from google.adk.tools import agent_tool
    from pydantic import BaseModel
    
    # 대상 에이전트 정의 (LlmAgent 또는 커스텀 BaseAgent 가능)
    class ImageGeneratorAgent(BaseAgent): # 예제 커스텀 에이전트
        name: str = "ImageGen"
        description: str = "프롬프트를 기반으로 이미지를 생성합니다."
        # ... 내부 로직 ...
        async def _run_async_impl(self, ctx): # 단순화된 실행 로직
            prompt = ctx.session.state.get("image_prompt", "기본 프롬프트")
            # ... 이미지 바이트 생성 ...
            image_bytes = b"..."
            yield Event(author=self.name, content=types.Content(parts=[types.Part.from_bytes(image_bytes, "image/png")]))
    
    image_agent = ImageGeneratorAgent()
    image_tool = agent_tool.AgentTool(agent=image_agent) # 에이전트 래핑
    
    # 부모 에이전트가 AgentTool 사용
    artist_agent = LlmAgent(
        name="Artist",
        model="gemini-2.0-flash",
        instruction="프롬프트를 만들고 ImageGen 도구를 사용하여 이미지를 생성하세요.",
        tools=[image_tool] # AgentTool 포함
    )
    # Artist LLM이 프롬프트를 생성한 후 다음을 호출합니다:
    # FunctionCall(name='ImageGen', args={'image_prompt': '모자를 쓴 고양이'})
    # 프레임워크가 image_tool.run_async(...)를 호출하고, 이는 ImageGeneratorAgent를 실행합니다.
    # 결과 이미지는 도구 결과로 Artist 에이전트에게 반환됩니다.
    ```

=== "Java"

    ```java
    // 개념 설정: 도구로서의 에이전트
    import com.google.adk.agents.BaseAgent;
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.tools.AgentTool;

    // 예제 커스텀 에이전트 (LlmAgent 또는 커스텀 BaseAgent 가능)
    public class ImageGeneratorAgent extends BaseAgent  {
    
      public ImageGeneratorAgent(String name, String description) {
        super(name, description, List.of(), null, null);
      }
    
      // ... 내부 로직 ...
      @Override
      protected Flowable<Event> runAsyncImpl(InvocationContext invocationContext) { // 단순화된 실행 로직
        invocationContext.session().state().get("image_prompt");
        // 이미지 바이트 생성
        // ...
    
        Event responseEvent = Event.builder()
            .author(this.name())
            .content(Content.fromParts(Part.fromText("\b...")))
            .build();
    
        return Flowable.just(responseEvent);
      }
    
      @Override
      protected Flowable<Event> runLiveImpl(InvocationContext invocationContext) {
        return null;
      }
    }

    // AgentTool을 사용하여 에이전트 래핑
    ImageGeneratorAgent imageAgent = new ImageGeneratorAgent("image_agent", "이미지를 생성합니다");
    AgentTool imageTool = AgentTool.create(imageAgent);
    
    // 부모 에이전트가 AgentTool 사용
    LlmAgent artistAgent = LlmAgent.builder()
            .name("Artist")
            .model("gemini-2.0-flash")
            .instruction(
                    "당신은 예술가입니다. 이미지에 대한 상세한 프롬프트를 만든 다음 " +
                            "'ImageGen' 도구를 사용하여 이미지를 생성하세요. " +
                            "'ImageGen' 도구는 이미지 프롬프트를 포함하는 'request'라는 단일 문자열 인수를 기대합니다. " +
                            "도구는 'result' 필드에 'image_base64', 'mime_type', 'status'를 포함하는 JSON 문자열을 반환합니다."
            )
            .description("생성 도구를 사용하여 이미지를 만들 수 있는 에이전트입니다.")
            .tools(imageTool) // AgentTool 포함
            .build();
    
    // Artist LLM이 프롬프트를 생성한 후 다음을 호출합니다:
    // FunctionCall(name='ImageGen', args={'imagePrompt': '모자를 쓴 고양이'})
    // 프레임워크가 imageTool.runAsync(...)를 호출하고, 이는 ImageGeneratorAgent를 실행합니다.
    // 결과 이미지는 도구 결과로 Artist 에이전트에게 반환됩니다.
    ```

=== "Go"

    ```go
    import (
        "fmt"
        "iter"
        "google.golang.org/adk/agent"
        "google.golang.org/adk/agent/llmagent"
        "google.golang.org/adk/model"
        "google.golang.org/adk/session"
        "google.golang.org/adk/tool"
        "google.golang.org/adk/tool/agenttool"
        "google.golang.org/genai"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:agent-as-tool"
    ```

이러한 기본 요소들은 긴밀하게 연결된 순차 워크플로에서부터 동적인 LLM 기반 위임 네트워크에 이르기까지 다중 에이전트 상호작용을 설계할 수 있는 유연성을 제공합니다.

## 2. ADK 기본 요소를 사용한 일반적인 다중 에이전트 패턴 { #common-multi-agent-patterns-using-adk-primitives }

ADK의 구성 기본 요소를 결합하여 다중 에이전트 협업을 위한 다양한 기존 패턴을 구현할 수 있습니다.

### 코디네이터/디스패처 패턴

* **구조:** 중앙 [`LlmAgent`](llm-agents.md)(코디네이터)가 여러 전문화된 `sub_agents`를 관리합니다.
* **목표:** 들어오는 요청을 적절한 전문가 에이전트로 라우팅합니다.
* **사용된 ADK 기본 요소:**
    * **계층 구조:** 코디네이터는 `sub_agents`에 전문가를 나열합니다.
    * **상호작용:** 주로 **LLM 기반 위임**(하위 에이전트에 대한 명확한 `description`과 코디네이터에 대한 적절한 `instruction` 필요) 또는 **명시적 호출 (`AgentTool`)**(코디네이터가 `AgentTool`로 래핑된 전문가를 `tools`에 포함)을 사용합니다.

=== "Python"

    ```python
    # 개념 코드: LLM 전환을 사용하는 코디네이터
    from google.adk.agents import LlmAgent
    
    billing_agent = LlmAgent(name="Billing", description="청구 관련 문의를 처리합니다.")
    support_agent = LlmAgent(name="Support", description="기술 지원 요청을 처리합니다.")
    
    coordinator = LlmAgent(
        name="HelpDeskCoordinator",
        model="gemini-2.0-flash",
        instruction="사용자 요청을 라우팅하세요: 결제 문제는 Billing 에이전트를, 기술 문제는 Support 에이전트를 사용하세요.",
        description="메인 헬프데스크 라우터.",
        # allow_transfer=True는 AutoFlow의 sub_agents와 함께 암시적으로 설정되는 경우가 많습니다
        sub_agents=[billing_agent, support_agent]
    )
    # 사용자 질문: "결제가 실패했습니다" -> 코디네이터의 LLM은 transfer_to_agent(agent_name='Billing')을 호출해야 합니다.
    # 사용자 질문: "로그인할 수 없습니다" -> 코디네이터의 LLM은 transfer_to_agent(agent_name='Support')를 호출해야 합니다.
    ```

=== "Java"

    ```java
    // 개념 코드: LLM 전환을 사용하는 코디네이터
    import com.google.adk.agents.LlmAgent;

    LlmAgent billingAgent = LlmAgent.builder()
        .name("Billing")
        .description("청구 관련 문의 및 결제 문제를 처리합니다.")
        .build();

    LlmAgent supportAgent = LlmAgent.builder()
        .name("Support")
        .description("기술 지원 요청 및 로그인 문제를 처리합니다.")
        .build();

    LlmAgent coordinator = LlmAgent.builder()
        .name("HelpDeskCoordinator")
        .model("gemini-2.0-flash")
        .instruction("사용자 요청을 라우팅하세요: 결제 문제는 Billing 에이전트를, 기술 문제는 Support 에이전트를 사용하세요.")
        .description("메인 헬프데스크 라우터.")
        .subAgents(billingAgent, supportAgent)
        // 에이전트 전환은 Autoflow에서 하위 에이전트와 함께 암시적으로 이루어집니다.
        // .disallowTransferToParent 또는 disallowTransferToPeers를 사용하여 지정하지 않는 한.
        .build();

    // 사용자 질문: "결제가 실패했습니다" -> 코디네이터의 LLM은
    // transferToAgent(agentName='Billing')을 호출해야 합니다.
    // 사용자 질문: "로그인할 수 없습니다" -> 코디네이터의 LLM은
    // transferToAgent(agentName='Support')를 호출해야 합니다.
    ```

=== "Go"

    ```go
    import (
        "google.golang.org/adk/agent"
        "google.golang.org/adk/agent/llmagent"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:coordinator-pattern"
    ```

### 순차 파이프라인 패턴

* **구조:** [`SequentialAgent`](workflow-agents/sequential-agents.md)가 고정된 순서로 실행되는 `sub_agents`를 포함합니다.
* **목표:** 한 단계의 출력이 다음 단계의 입력으로 사용되는 다단계 프로세스를 구현합니다.
* **사용된 ADK 기본 요소:**
    * **워크플로:** `SequentialAgent`가 순서를 정의합니다.
    * **통신:** 주로 **공유 세션 상태**를 사용합니다. 이전 에이전트가 결과(`output_key`를 통해)를 쓰고, 이후 에이전트가 `context.state`에서 해당 결과를 읽습니다.

=== "Python"

    ```python
    # 개념 코드: 순차 데이터 파이프라인
    from google.adk.agents import SequentialAgent, LlmAgent
    
    validator = LlmAgent(name="ValidateInput", instruction="입력을 검증하세요.", output_key="validation_status")
    processor = LlmAgent(name="ProcessData", instruction="{validation_status}가 'valid'이면 데이터를 처리하세요.", output_key="result")
    reporter = LlmAgent(name="ReportResult", instruction="{result}에서 결과를 보고하세요.")
    
    data_pipeline = SequentialAgent(
        name="DataPipeline",
        sub_agents=[validator, processor, reporter]
    )
    # validator 실행 -> state['validation_status']에 저장
    # processor 실행 -> state['validation_status'] 읽고 state['result']에 저장
    # reporter 실행 -> state['result'] 읽음
    ```

=== "Java"

    ```java
    // 개념 코드: 순차 데이터 파이프라인
    import com.google.adk.agents.SequentialAgent;
    
    LlmAgent validator = LlmAgent.builder()
        .name("ValidateInput")
        .instruction("입력을 검증하세요")
        .outputKey("validation_status") // 주 텍스트 출력을 session.state["validation_status"]에 저장
        .build();
    
    LlmAgent processor = LlmAgent.builder()
        .name("ProcessData")
        .instruction("{validation_status}가 'valid'이면 데이터를 처리하세요")
        .outputKey("result") // 주 텍스트 출력을 session.state["result"]에 저장
        .build();
    
    LlmAgent reporter = LlmAgent.builder()
        .name("ReportResult")
        .instruction("{result}에서 결과를 보고하세요")
        .build();
    
    SequentialAgent dataPipeline = SequentialAgent.builder()
        .name("DataPipeline")
        .subAgents(validator, processor, reporter)
        .build();
    
    // validator 실행 -> state['validation_status']에 저장
    // processor 실행 -> state['validation_status'] 읽고 state['result']에 저장
    // reporter 실행 -> state['result'] 읽음
    ```

=== "Go"

    ```go
    import (
        "google.golang.org/adk/agent"
        "google.golang.org/adk/agent/llmagent"
        "google.golang.org/adk/agent/workflowagents/sequentialagent"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:sequential-pipeline-pattern"
    ```

### 병렬 분산/수집 패턴 (Fan-Out/Gather)

* **구조:** [`ParallelAgent`](workflow-agents/parallel-agents.md)가 여러 `sub_agents`를 동시에 실행하고, 종종 (`SequentialAgent` 내의) 후속 에이전트가 결과를 집계합니다.
* **목표:** 독립적인 작업을 동시에 실행하여 지연 시간을 줄인 다음 출력을 결합합니다.
* **사용된 ADK 기본 요소:**
    * **워크플로:** 동시 실행을 위한 `ParallelAgent`(Fan-Out). 종종 후속 집계 단계(Gather)를 처리하기 위해 `SequentialAgent` 내에 중첩됩니다.
    * **통신:** 하위 에이전트가 **공유 세션 상태**의 고유한 키에 결과를 씁니다. 후속 "Gather" 에이전트는 여러 상태 키를 읽습니다.

=== "Python"

    ```python
    # 개념 코드: 병렬 정보 수집
    from google.adk.agents import SequentialAgent, ParallelAgent, LlmAgent
    
    fetch_api1 = LlmAgent(name="API1Fetcher", instruction="API 1에서 데이터를 가져오세요.", output_key="api1_data")
    fetch_api2 = LlmAgent(name="API2Fetcher", instruction="API 2에서 데이터를 가져오세요.", output_key="api2_data")
    
    gather_concurrently = ParallelAgent(
        name="ConcurrentFetch",
        sub_agents=[fetch_api1, fetch_api2]
    )
    
    synthesizer = LlmAgent(
        name="Synthesizer",
        instruction="{api1_data}와 {api2_data}의 결과를 결합하세요."
    )
    
    overall_workflow = SequentialAgent(
        name="FetchAndSynthesize",
        sub_agents=[gather_concurrently, synthesizer] # 병렬 가져오기 후 종합
    )
    # fetch_api1과 fetch_api2가 동시에 실행되어 상태에 저장합니다.
    # synthesizer가 이후에 실행되어 state['api1_data']와 state['api2_data']를 읽습니다.
    ```
=== "Java"

    ```java
    // 개념 코드: 병렬 정보 수집
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.agents.ParallelAgent;
    import com.google.adk.agents.SequentialAgent;

    LlmAgent fetchApi1 = LlmAgent.builder()
        .name("API1Fetcher")
        .instruction("API 1에서 데이터를 가져오세요.")
        .outputKey("api1_data")
        .build();

    LlmAgent fetchApi2 = LlmAgent.builder()
        .name("API2Fetcher")
        .instruction("API 2에서 데이터를 가져오세요.")
        .outputKey("api2_data")
        .build();

    ParallelAgent gatherConcurrently = ParallelAgent.builder()
        .name("ConcurrentFetcher")
        .subAgents(fetchApi2, fetchApi1)
        .build();

    LlmAgent synthesizer = LlmAgent.builder()
        .name("Synthesizer")
        .instruction("{api1_data}와 {api2_data}의 결과를 결합하세요.")
        .build();

    SequentialAgent overallWorfklow = SequentialAgent.builder()
        .name("FetchAndSynthesize") // 병렬 가져오기 후 종합
        .subAgents(gatherConcurrently, synthesizer)
        .build();

    // fetch_api1과 fetch_api2가 동시에 실행되어 상태에 저장합니다.
    // synthesizer가 이후에 실행되어 state['api1_data']와 state['api2_data']를 읽습니다.
    ```

=== "Go"

    ```go
    import (
        "google.golang.org/adk/agent"
        "google.golang.org/adk/agent/llmagent"
        "google.golang.org/adk/agent/workflowagents/parallelagent"
        "google.golang.org/adk/agent/workflowagents/sequentialagent"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:parallel-gather-pattern"
    ```

### 계층적 작업 분해

* **구조:** 상위 수준 에이전트가 복잡한 목표를 분해하고 하위 작업을 하위 수준 에이전트에게 위임하는 다단계 에이전트 트리.
* **목표:** 복잡한 문제를 재귀적으로 더 간단하고 실행 가능한 단계로 분해하여 해결합니다.
* **사용된 ADK 기본 요소:**
    * **계층 구조:** 다단계 `parent_agent`/`sub_agents` 구조.
    * **상호작용:** 주로 부모 에이전트가 하위 에이전트에게 작업을 할당하는 데 사용하는 **LLM 기반 위임** 또는 **명시적 호출 (`AgentTool`)**. 결과는 계층 구조 위로 반환됩니다 (도구 응답 또는 상태를 통해).

=== "Python"

    ```python
    # 개념 코드: 계층적 연구 작업
    from google.adk.agents import LlmAgent
    from google.adk.tools import agent_tool
    
    # 저수준 도구형 에이전트
    web_searcher = LlmAgent(name="WebSearch", description="사실에 대한 웹 검색을 수행합니다.")
    summarizer = LlmAgent(name="Summarizer", description="텍스트를 요약합니다.")
    
    # 도구를 결합하는 중간 수준 에이전트
    research_assistant = LlmAgent(
        name="ResearchAssistant",
        model="gemini-2.0-flash",
        description="주제에 대한 정보를 찾고 요약합니다.",
        tools=[agent_tool.AgentTool(agent=web_searcher), agent_tool.AgentTool(agent=summarizer)]
    )
    
    # 연구를 위임하는 고수준 에이전트
    report_writer = LlmAgent(
        name="ReportWriter",
        model="gemini-2.0-flash",
        instruction="X 주제에 대한 보고서를 작성하세요. ResearchAssistant를 사용하여 정보를 수집하세요.",
        tools=[agent_tool.AgentTool(agent=research_assistant)]
        # 또는 research_assistant가 sub_agent인 경우 LLM 전환을 사용할 수 있습니다
    )
    # 사용자는 ReportWriter와 상호작용합니다.
    # ReportWriter는 ResearchAssistant 도구를 호출합니다.
    # ResearchAssistant는 WebSearch와 Summarizer 도구를 호출합니다.
    # 결과는 위로 다시 전달됩니다.
    ```

=== "Java"

    ```java
    // 개념 코드: 계층적 연구 작업
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.tools.AgentTool;
    
    // 저수준 도구형 에이전트
    LlmAgent webSearcher = LlmAgent.builder()
        .name("WebSearch")
        .description("사실에 대한 웹 검색을 수행합니다.")
        .build();
    
    LlmAgent summarizer = LlmAgent.builder()
        .name("Summarizer")
        .description("텍스트를 요약합니다.")
        .build();
    
    // 도구를 결합하는 중간 수준 에이전트
    LlmAgent researchAssistant = LlmAgent.builder()
        .name("ResearchAssistant")
        .model("gemini-2.0-flash")
        .description("주제에 대한 정보를 찾고 요약합니다.")
        .tools(AgentTool.create(webSearcher), AgentTool.create(summarizer))
        .build();
    
    // 연구를 위임하는 고수준 에이전트
    LlmAgent reportWriter = LlmAgent.builder()
        .name("ReportWriter")
        .model("gemini-2.0-flash")
        .instruction("X 주제에 대한 보고서를 작성하세요. ResearchAssistant를 사용하여 정보를 수집하세요.")
        .tools(AgentTool.create(researchAssistant))
        // 또는 research_assistant가 subAgent인 경우 LLM 전환을 사용할 수 있습니다
        .build();
    
    // 사용자는 ReportWriter와 상호작용합니다.
    // ReportWriter는 ResearchAssistant 도구를 호출합니다.
    // ResearchAssistant는 WebSearch와 Summarizer 도구를 호출합니다.
    // 결과는 위로 다시 전달됩니다.
    ```

=== "Go"

    ```go
    import (
        "google.golang.org/adk/agent/llmagent"
        "google.golang.org/adk/tool"
        "google.golang.org/adk/tool/agenttool"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:hierarchical-pattern"
    ```

### 검토/비평 패턴 (생성자-비평가)

* **구조:** 일반적으로 [`SequentialAgent`](workflow-agents/sequential-agents.md) 내에 두 개의 에이전트(생성자 및 비평가/검토자)를 포함합니다.
* **목표:** 전담 에이전트가 생성된 출력을 검토하여 품질이나 유효성을 향상시킵니다.
* **사용된 ADK 기본 요소:**
    * **워크플로:** `SequentialAgent`가 검토 전에 생성이 이루어지도록 보장합니다.
    * **통신:** **공유 세션 상태**(생성자는 `output_key`를 사용하여 출력을 저장하고, 검토자는 해당 상태 키를 읽음). 검토자는 후속 단계를 위해 피드백을 다른 상태 키에 저장할 수 있습니다.

=== "Python"

    ```python
    # 개념 코드: 생성자-비평가
    from google.adk.agents import SequentialAgent, LlmAgent
    
    generator = LlmAgent(
        name="DraftWriter",
        instruction="X 주제에 대한 짧은 단락을 작성하세요.",
        output_key="draft_text"
    )
    
    reviewer = LlmAgent(
        name="FactChecker",
        instruction="{draft_text}의 텍스트를 사실 정확도에 대해 검토하세요. 'valid' 또는 'invalid'와 이유를 출력하세요.",
        output_key="review_status"
    )
    
    # 선택 사항: review_status에 기반한 추가 단계
    
    review_pipeline = SequentialAgent(
        name="WriteAndReview",
        sub_agents=[generator, reviewer]
    )
    # generator 실행 -> 초안을 state['draft_text']에 저장
    # reviewer 실행 -> state['draft_text'] 읽고 상태를 state['review_status']에 저장
    ```

=== "Java"

    ```java
    // 개념 코드: 생성자-비평가
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.agents.SequentialAgent;
    
    LlmAgent generator = LlmAgent.builder()
        .name("DraftWriter")
        .instruction("X 주제에 대한 짧은 단락을 작성하세요.")
        .outputKey("draft_text")
        .build();
    
    LlmAgent reviewer = LlmAgent.builder()
        .name("FactChecker")
        .instruction("{draft_text}의 텍스트를 사실 정확도에 대해 검토하세요. 'valid' 또는 'invalid'와 이유를 출력하세요.")
        .outputKey("review_status")
        .build();
    
    // 선택 사항: review_status에 기반한 추가 단계
    
    SequentialAgent reviewPipeline = SequentialAgent.builder()
        .name("WriteAndReview")
        .subAgents(generator, reviewer)
        .build();
    
    // generator 실행 -> 초안을 state['draft_text']에 저장
    // reviewer 실행 -> state['draft_text'] 읽고 상태를 state['review_status']에 저장
    ```

=== "Go"

    ```go
    import (
        "google.golang.org/adk/agent"
        "google.golang.org/adk/agent/llmagent"
        "google.golang.org/adk/agent/workflowagents/sequentialagent"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:generator-critic-pattern"
    ```

### 반복적 개선 패턴

* **구조:** 여러 반복에 걸쳐 작업을 수행하는 하나 이상의 에이전트를 포함하는 [`LoopAgent`](workflow-agents/loop-agents.md)를 사용합니다.
* **목표:** 품질 임계값에 도달하거나 최대 반복 횟수에 도달할 때까지 세션 상태에 저장된 결과(예: 코드, 텍스트, 계획)를 점진적으로 개선합니다.
* **사용된 ADK 기본 요소:**
    * **워크플로:** `LoopAgent`가 반복을 관리합니다.
    * **통신:** 에이전트가 이전 반복의 출력을 읽고 개선된 버전을 저장하기 위해 **공유 세션 상태**가 필수적입니다.
    * **종료:** 루프는 일반적으로 `max_iterations`에 기반하거나, 결과가 만족스러울 때 `Event Actions`에서 `escalate=True`를 설정하는 전담 확인 에이전트에 의해 종료됩니다.

=== "Python"

    ```python
    # 개념 코드: 반복적 코드 개선
    from google.adk.agents import LoopAgent, LlmAgent, BaseAgent
    from google.adk.events import Event, EventActions
    from google.adk.agents.invocation_context import InvocationContext
    from typing import AsyncGenerator
    
    # state['current_code']와 state['requirements']를 기반으로 코드를 생성/개선하는 에이전트
    code_refiner = LlmAgent(
        name="CodeRefiner",
        instruction="state['current_code'](있는 경우)와 state['requirements']를 읽으세요. 요구사항을 충족하도록 Python 코드를 생성/개선하세요. state['current_code']에 저장하세요.",
        output_key="current_code" # 상태의 이전 코드를 덮어씁니다
    )
    
    # 코드가 품질 표준을 충족하는지 확인하는 에이전트
    quality_checker = LlmAgent(
        name="QualityChecker",
        instruction="state['current_code']의 코드를 state['requirements']에 대해 평가하세요. 'pass' 또는 'fail'을 출력하세요.",
        output_key="quality_status"
    )
    
    # 상태를 확인하고 'pass'인 경우 escalate하는 커스텀 에이전트
    class CheckStatusAndEscalate(BaseAgent):
        async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
            status = ctx.session.state.get("quality_status", "fail")
            should_stop = (status == "pass")
            yield Event(author=self.name, actions=EventActions(escalate=should_stop))
    
    refinement_loop = LoopAgent(
        name="CodeRefinementLoop",
        max_iterations=5,
        sub_agents=[code_refiner, quality_checker, CheckStatusAndEscalate(name="StopChecker")]
    )
    # 루프 실행: Refiner -> Checker -> StopChecker
    # State['current_code']는 각 반복마다 업데이트됩니다.
    # QualityChecker가 'pass'를 출력하거나(StopChecker가 escalate하도록 함) 5회 반복 후 루프가 중지됩니다.
    ```

=== "Java"

    ```java
    // 개념 코드: 반복적 코드 개선
    import com.google.adk.agents.BaseAgent;
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.agents.LoopAgent;
    import com.google.adk.events.Event;
    import com.google.adk.events.EventActions;
    import com.google.adk.agents.InvocationContext;
    import io.reactivex.rxjava3.core.Flowable;
    import java.util.List;
    
    // state['current_code']와 state['requirements']를 기반으로 코드를 생성/개선하는 에이전트
    LlmAgent codeRefiner = LlmAgent.builder()
        .name("CodeRefiner")
        .instruction("state['current_code'](있는 경우)와 state['requirements']를 읽으세요. 요구사항을 충족하도록 Java 코드를 생성/개선하세요. state['current_code']에 저장하세요.")
        .outputKey("current_code") // 상태의 이전 코드를 덮어씁니다
        .build();
    
    // 코드가 품질 표준을 충족하는지 확인하는 에이전트
    LlmAgent qualityChecker = LlmAgent.builder()
        .name("QualityChecker")
        .instruction("state['current_code']의 코드를 state['requirements']에 대해 평가하세요. 'pass' 또는 'fail'을 출력하세요.")
        .outputKey("quality_status")
        .build();
    
    BaseAgent checkStatusAndEscalate = new BaseAgent(
        "StopChecker","quality_status를 확인하고 'pass'인 경우 escalate합니다.", List.of(), null, null) {
    
      @Override
      protected Flowable<Event> runAsyncImpl(InvocationContext invocationContext) {
        String status = (String) invocationContext.session().state().getOrDefault("quality_status", "fail");
        boolean shouldStop = "pass".equals(status);
    
        EventActions actions = EventActions.builder().escalate(shouldStop).build();
        Event event = Event.builder()
            .author(this.name())
            .actions(actions)
            .build();
        return Flowable.just(event);
      }
    };
    
    LoopAgent refinementLoop = LoopAgent.builder()
        .name("CodeRefinementLoop")
        .maxIterations(5)
        .subAgents(codeRefiner, qualityChecker, checkStatusAndEscalate)
        .build();
    
    // 루프 실행: Refiner -> Checker -> StopChecker
    // State['current_code']는 각 반복마다 업데이트됩니다.
    // QualityChecker가 'pass'를 출력하거나(StopChecker가 escalate하도록 함) 5회 반복 후 루프가 중지됩니다.
    ```

=== "Go"

    ```go
    import (
        "iter"
        "google.golang.org/adk/agent"
        "google.golang.org/adk/agent/llmagent"
        "google.golang.org/adk/agent/workflowagents/loopagent"
        "google.golang.org/adk/session"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:iterative-refinement-pattern"
    ```

### 인간 참여 루프(Human-in-the-Loop) 패턴

* **구조:** 에이전트 워크플로 내에 인간 개입 지점을 통합합니다.
* **목표:** 인간의 감독, 승인, 수정 또는 AI가 수행할 수 없는 작업을 허용합니다.
* **사용된 ADK 기본 요소 (개념적):**
    * **상호작용:** 실행을 일시 중지하고 외부 시스템(예: UI, 티켓팅 시스템)에 요청을 보내 인간의 입력을 기다리는 커스텀 **도구**를 사용하여 구현할 수 있습니다. 그런 다음 도구는 인간의 응답을 에이전트에게 반환합니다.
    * **워크플로:** **LLM 기반 위임**(`transfer_to_agent`)을 사용하여 외부 워크플로를 트리거하는 개념적 "인간 에이전트"를 대상으로 하거나, `LlmAgent` 내에서 커스텀 도구를 사용할 수 있습니다.
    * **상태/콜백:** 상태는 인간을 위한 작업 세부 정보를 보유할 수 있으며, 콜백은 상호작용 흐름을 관리할 수 있습니다.
    * **참고:** ADK에는 내장된 "인간 에이전트" 유형이 없으므로 커스텀 통합이 필요합니다.

=== "Python"

    ```python
    # 개념 코드: 인간 승인을 위한 도구 사용
    from google.adk.agents import LlmAgent, SequentialAgent
    from google.adk.tools import FunctionTool
    
    # --- external_approval_tool이 존재한다고 가정 ---
    # 이 도구는 다음을 수행합니다:
    # 1. 세부 정보(예: request_id, 금액, 사유)를 받습니다.
    # 2. 이 세부 정보를 인간 검토 시스템(예: API를 통해)으로 보냅니다.
    # 3. 인간의 응답(승인/거절)을 폴링하거나 기다립니다.
    # 4. 인간의 결정을 반환합니다.
    # async def external_approval_tool(amount: float, reason: str) -> str: ...
    approval_tool = FunctionTool(func=external_approval_tool)
    
    # 요청을 준비하는 에이전트
    prepare_request = LlmAgent(
        name="PrepareApproval",
        instruction="사용자 입력을 기반으로 승인 요청 세부 정보를 준비하세요. 상태에 금액과 사유를 저장하세요.",
        # ... 아마도 state['approval_amount']와 state['approval_reason']을 설정할 것입니다 ...
    )
    
    # 인간 승인 도구를 호출하는 에이전트
    request_approval = LlmAgent(
        name="RequestHumanApproval",
        instruction="state['approval_amount']의 금액과 state['approval_reason']의 사유로 external_approval_tool을 사용하세요.",
        tools=[approval_tool],
        output_key="human_decision"
    )
    
    # 인간의 결정에 따라 진행하는 에이전트
    process_decision = LlmAgent(
        name="ProcessDecision",
        instruction="{human_decision}을 확인하세요. 'approved'이면 진행하고, 'rejected'이면 사용자에게 알리세요."
    )
    
    approval_workflow = SequentialAgent(
        name="HumanApprovalWorkflow",
        sub_agents=[prepare_request, request_approval, process_decision]
    )
    ```

=== "Java"

    ```java
    // 개념 코드: 인간 승인을 위한 도구 사용
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.agents.SequentialAgent;
    import com.google.adk.tools.FunctionTool;
    
    // --- external_approval_tool이 존재한다고 가정 ---
    // 이 도구는 다음을 수행합니다:
    // 1. 세부 정보(예: request_id, 금액, 사유)를 받습니다.
    // 2. 이 세부 정보를 인간 검토 시스템(예: API를 통해)으로 보냅니다.
    // 3. 인간의 응답(승인/거절)을 폴링하거나 기다립니다.
    // 4. 인간의 결정을 반환합니다.
    // public boolean externalApprovalTool(float amount, String reason) { ... }
    FunctionTool approvalTool = FunctionTool.create(externalApprovalTool);
    
    // 요청을 준비하는 에이전트
    LlmAgent prepareRequest = LlmAgent.builder()
        .name("PrepareApproval")
        .instruction("사용자 입력을 기반으로 승인 요청 세부 정보를 준비하세요. 상태에 금액과 사유를 저장하세요.")
        // ... 아마도 state['approval_amount']와 state['approval_reason']을 설정할 것입니다 ...
        .build();
    
    // 인간 승인 도구를 호출하는 에이전트
    LlmAgent requestApproval = LlmAgent.builder()
        .name("RequestHumanApproval")
        .instruction("state['approval_amount']의 금액과 state['approval_reason']의 사유로 external_approval_tool을 사용하세요.")
        .tools(approvalTool)
        .outputKey("human_decision")
        .build();
    
    // 인간의 결정에 따라 진행하는 에이전트
    LlmAgent processDecision = LlmAgent.builder()
        .name("ProcessDecision")
        .instruction("{human_decision}을 확인하세요. 'approved'이면 진행하고, 'rejected'이면 사용자에게 알리세요.")
        .build();
    
    SequentialAgent approvalWorkflow = SequentialAgent.builder()
        .name("HumanApprovalWorkflow")
        .subAgents(prepareRequest, requestApproval, processDecision)
        .build();
    ```

=== "Go"

    ```go
    import (
        "google.golang.org/adk/agent"
        "google.golang.org/adk/agent/llmagent"
        "google.golang.org/adk/agent/workflowagents/sequentialagent"
        "google.golang.org/adk/tool"
    )
    
    --8<-- "examples/go/snippets/agents/multi-agent/main.go:human-in-loop-pattern"
    ```

이러한 패턴들은 다중 에이전트 시스템을 구조화하기 위한 시작점을 제공합니다. 특정 애플리케이션에 가장 효과적인 아키텍처를 만들기 위해 필요에 따라 혼합하여 사용할 수 있습니다.