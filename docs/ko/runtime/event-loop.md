# ADK 실행 루프

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-kotlin">Kotlin v0.7.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

ADK(Agent Development Kit)의 핵심에는 비동기 이벤트 기반 아키텍처가 있습니다. 상위 레벨에서 `Runner`는 에이전트와 도구로 구성된 실행 로직과 협력하여 대화를 한 턴씩 진행합니다. 이 흐름을 이해하면 상태 변경, 스트리밍 출력, 비동기 작업이 어떻게 원활하게 조율되는지 파악할 수 있습니다.

## 핵심 개념: Yield-and-Resume 이벤트 루프

ADK 실행 루프의 기본 메커니즘은 **협력적 생성자/스트림(cooperative generator/stream)** 모델입니다. 에이전트가 실행될 때 모든 것을 한 번에 실행하고 단일 결과를 반환하지 않습니다. 대신 일련의 `Event` 객체를 점진적으로 **생성(yield/emit)**합니다.

### 루프 작동 방식:

1. **`Runner`가 루프를 시작합니다:** `Runner`는 사용자의 질의를 받아 세션 히스토리에 기록한 다음, 에이전트의 메인 실행 메서드(`run_async`)를 호출하여 프로세스를 시작합니다.
2. **에이전트가 이벤트를 생성(Yield)하고 일시 중지합니다:** 에이전트가 출력을 생성하거나(예: 생각, 텍스트 청크), 도구를 호출해야 하거나, 상태를 수정할 때마다 이러한 작업이 포함된 `Event` 객체를 생성(yield)합니다. **이벤트를 생성한 직후 에이전트의 실행은 일시 중지됩니다.**
3. **`Runner`가 이벤트를 처리합니다:** `Runner`는 일시 중지된 에이전트로부터 생성된 이벤트를 받습니다. 다음 작업을 수행합니다:
    * 이벤트를 세션의 `event history`에 기록합니다.
    * 이벤트에 지정된 모든 작업(예: 세션 상태에 `state_delta` 적용, 아티팩트 저장 확인)을 커밋합니다.
    * 처리된 이벤트를 상위 스트림(예: UI로 스트리밍)으로 전달합니다.
4. **`Runner`가 에이전트를 재개(Resume)합니다:** 이벤트 처리가 완료되면 `Runner`는 에이전트의 실행을 재개하도록 신호를 보냅니다.
5. **에이전트가 계속 진행합니다:** 에이전트는 중단된 지점부터 다시 실행되며, 이제 이전 이벤트에서 요청한 모든 상태 변경이나 작업이 `SessionService`에 의해 성공적으로 커밋되었음을 확신할 수 있습니다.
6. **반복:** 이 생성, 일시 중지, 처리, 재개 주기는 에이전트가 현재 사용자 질의에 대한 작업을 완료할 때까지 계속됩니다.

### 개념적 코드 예시

다음 단순화된 의사코드는 `Runner`와 에이전트의 실행 로직 간의 상호작용을 보여줍니다:

=== "Python"

    ```py
    # Runner의 메인 루프 로직 단순화
    async def run_async(new_query, ...) -> AsyncGenerator[Event, None]:
        # 1. 새 질의를 세션 이벤트 히스토리에 추가 (SessionService를 통해)
        await session_service.append_event(session, Event(author='user', content=new_query))

        # 2. 에이전트를 호출하여 이벤트 루프 시작
        agent_event_generator = agent_to_run.run_async(context)

        async for event in agent_event_generator:
            # 3. 생성된 이벤트를 처리하고 변경사항 커밋
            await session_service.append_event(session, event) # 상태/아티팩트 델타 등 커밋
            # memory_service.update_memory(...) # 해당되는 경우
            # artifact_service는 에이전트 실행 중 컨텍스트를 통해 이미 호출되었을 수 있음

            # 4. 상위 스트림 처리(예: UI 렌더링)를 위해 이벤트 yield
            yield event
            # Runner는 yield 후 에이전트 제너레이터가 계속될 수 있음을 암시적으로 신호
    ```

=== "TypeScript"

    ```typescript
    // Runner의 메인 루프 로직 단순화
    async * runAsync(newQuery: Content, ...): AsyncGenerator<Event, void, void> {
        // 1. 새 질의를 세션 이벤트 히스토리에 추가 (SessionService를 통해)
        await sessionService.appendEvent({
            session,
            event: createEvent({author: 'user', content: newQuery})
        });

        // 2. 에이전트를 호출하여 이벤트 루프 시작
        const agentEventGenerator = agentToRun.runAsync(context);

        for await (const event of agentEventGenerator) {
            // 3. 생성된 이벤트를 처리하고 변경사항 커밋
            await sessionService.appendEvent({session, event}); // 상태/아티팩트 델타 등 커밋
            // memoryService.updateMemory(...) # 해당되는 경우

            // 4. 상위 스트림 처리를 위해 이벤트 yield
            yield event;
            // Runner는 yield 후 에이전트 제너레이터가 계속될 수 있음을 암시적으로 신호
        }
    }
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/runtime/RunnerLoop.kt:conceptual_loop"
    ```

=== "Go"

    ```go
    // Go에서 에이전트 런타임은 채널이나 이터레이터를 활용합니다
    // 개념적 Runner 루프 로직
    func (r *Runner) RunAsync(ctx context.Context, session *session.Session, query *session.Content) iter.Seq2[*session.Event, error] {
        return func(yield func(*session.Event, error) bool) {
            // 1. 사용자 쿼리 이벤트 추가
            userEvent := session.NewEvent(ctx, r.invocationID)
            userEvent.Author = "user"
            userEvent.Content = query
            r.sessionService.AppendEvent(ctx, session, userEvent)

            // 2. 에이전트 실행
            for event, err := range r.agent.Run(ctx) {
                if err != nil {
                    yield(nil, err)
                    return
                }
                // 3. 상태 커밋 및 히스토리 기록
                r.sessionService.AppendEvent(ctx, session, event)

                // 4. 상위 스트림으로 전달
                if !yield(event, nil) {
                    return
                }
            }
        }
    }
    ```

=== "Java"

    ```java
    // Java에서 Flowable/Observable 기반의 리액티브 런타임 루프 단순화
    public Flowable<Event> runAsync(Session session, Content newQuery) {
        Event userEvent = Event.builder().author("user").content(newQuery).build();
        return sessionService.appendEvent(session, userEvent)
            .andThen(Flowable.defer(() -> agentToRun.runAsync(context)))
            .concatMap(event -> sessionService.appendEvent(session, event).andThen(Flowable.just(event)));
    }
    ```

### 실행 로직 관점

에이전트 구현 내부에서는 이벤트 스트림을 생성합니다:

=== "Python"

    ```py
    # 에이전트 실행 로직 내부
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # 중간 생각이나 부분 텍스트 yield
        yield Event(author=self.name, content=Content(parts=[Part.from_text("생각 중...")]), partial=True)
        # --- 일시 중지 --- Runner가 처리 후 재개 ---

        # 상태 수정 준비
        ctx.session.state['my_key'] = 'new_value'
        # 상태 델타와 함께 이벤트 yield
        yield Event(author=self.name, actions=EventActions(state_delta={'my_key': 'new_value'}))
        # --- 일시 중지 --- Runner/SessionService가 'my_key' 커밋 후 재개 ---

        # 이제 'my_key'는 확실하게 커밋됨
        yield Event(author=self.name, content=Content(parts=[Part.from_text("완료!")]))
    ```

=== "TypeScript"

    ```typescript
    // TypeScript 에이전트 실행 로직 내부
    async * _runAsyncImpl(ctx: InvocationContext): AsyncGenerator<Event, void, void> {
        yield createEvent({
            author: this.name,
            content: createContent({parts: [createPart({text: "생각 중..."})]}),
            partial: true
        });

        ctx.state.set('my_key', 'new_value');
        yield createEvent({
            author: this.name,
            actions: createEventActions({stateDelta: {'my_key': 'new_value'}})
        });

        yield createEvent({
            author: this.name,
            content: createContent({parts: [createPart({text: "완료!"})]})
        });
    }
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/runtime/RunnerLoop.kt:execution_logic"
    ```

`Event` 객체를 매개로 `Runner`와 실행 로직 간에 이루어지는 협력적인 yield/일시 중지/재개 주기는 ADK 런타임의 핵심을 형성합니다.

## 런타임의 핵심 구성요소

ADK 런타임 내에서 에이전트 호출을 실행하기 위해 여러 구성요소가 함께 작동합니다:

1. ### `Runner`

      * **역할:** 단일 사용자 질의에 대한 메인 진입점이자 오케스트레이터(`run_async`).
      * **기능:** 전반적인 이벤트 루프를 관리하고, 실행 로직에서 생성된 이벤트를 수신하며, 서비스와 협력하여 이벤트 작업(상태/아티팩트 변경)을 처리 및 커밋하고, 처리된 이벤트를 상위 스트림(예: UI)으로 전달합니다. 생성된 이벤트를 기반으로 대화를 턴별로 이끕니다(`google.adk.runners`에 정의됨).

2. ### 실행 로직 구성요소 (Execution Logic Components)

      * **역할:** 커스텀 코드와 핵심 에이전트 기능이 포함된 부분.
      * **구성요소:**
        * `Agent` (`BaseAgent`, `LlmAgent` 등): 정보를 처리하고 조치를 결정하는 기본 로직 단위. 이벤트를 생성하는 `_run_async_impl` 메서드를 구현합니다.
        * `Tools` (`BaseTool`, `FunctionTool`, `AgentTool` 등): 에이전트(주로 `LlmAgent`)가 외부 세계와 상호작용하거나 특정 작업을 수행하기 위해 사용하는 외부 함수 또는 기능. 실행되어 결과를 반환하며, 이는 이벤트로 래핑됩니다.
        * `Callbacks` (함수): 실행 흐름의 특정 지점에 연결되어 동작이나 상태를 잠재적으로 수정하는 에이전트에 연결된 사용자 정의 함수(예: `before_agent_callback`, `after_model_callback`). 그 효과는 이벤트에 캡처됩니다.
      * **기능:** 실제 사고, 계산 또는 외부 상호작용을 수행합니다. **`Event` 객체를 생성(yield)**하고 Runner가 처리할 때까지 일시 중지하여 결과나 요구사항을 전달합니다.

3. ### `Event`

      * **역할:** `Runner`와 실행 로직 사이에서 주고받는 메시지.
      * **기능:** 원자적 발생(사용자 입력, 에이전트 텍스트, 도구 호출/결과, 상태 변경 요청, 제어 신호)을 나타냅니다. 발생 내용과 의도된 부수 효과(`state_delta`와 같은 `actions`)를 모두 전달합니다.

4. ### `Services`

      * **역할:** 영구 리소스 또는 공유 리소스를 관리하는 백엔드 구성요소. 이벤트 처리 중 주로 `Runner`에 의해 사용됩니다.
      * **구성요소:**
        * `SessionService` (`BaseSessionService`, `InMemorySessionService` 등): `Session` 객체를 저장/로드하고, `state_delta`를 세션 상태에 적용하며, 이벤트를 `event history`에 추가하는 등 `Session`을 관리합니다.
        * `ArtifactService` (`BaseArtifactService`, `InMemoryArtifactService`, `GcsArtifactService` 등): 바이너리 아티팩트 데이터의 저장 및 조회를 관리합니다. 실행 로직 중에 컨텍스트를 통해 `save_artifact`가 호출되지만 이벤트의 `artifact_delta`는 Runner/SessionService에 대한 작업을 확인합니다.
        * `MemoryService` (`BaseMemoryService` 등): (선택사항) 사용자의 여러 세션에 걸친 장기 시맨틱 메모리를 관리합니다.
      * **기능:** 영속성 계층을 제공합니다. `Runner`는 이들과 상호작용하여 실행 로직이 재개되기 *전에* `event.actions`로 표시된 변경사항이 안정적으로 저장되도록 합니다.

5. ### `Session`

      * **역할:** 사용자와 애플리케이션 간의 *특정 단일 대화*에 대한 상태와 기록을 보관하는 데이터 컨테이너.
      * **기능:** 현재 `state` 딕셔너리, 모든 과거 `events` 목록(`event history`), 관련 아티팩트에 대한 참조를 저장합니다. `SessionService`에서 관리하는 상호작용의 기본 레코드입니다.

6. ### `Invocation`

      * **역할:** `Runner`가 사용자 질의를 수신한 순간부터 에이전트 로직이 해당 질의에 대한 이벤트 생성을 마칠 때까지 *단일* 질의에 대한 응답으로 발생하는 모든 것을 나타내는 개념적 용어.
      * **기능:** 호출에는 단일 `InvocationContext` 내의 `invocation_id`로 연결된 여러 에이전트 실행(에이전트 이전 또는 `AgentTool` 사용 시), 여러 LLM 호출, 도구 실행 및 콜백 실행이 포함될 수 있습니다. `temp:` 접두사가 붙은 상태 변수는 엄격하게 단일 호출로 범위가 지정되며 이후 삭제됩니다.

## 작동 방식: 단순화된 호출 흐름

LLM 에이전트가 도구를 호출하는 일반적인 사용자 질의에 대한 단순화된 흐름을 추적해 보겠습니다:

![intro_components.png](../assets/invocation-flow.png)

### 단계별 분석

1. **사용자 입력:** 사용자가 질의를 전송합니다(예: "프랑스의 수도는 어디인가요?").
2. **Runner 시작:** `Runner.run_async`가 시작됩니다. `SessionService`와 상호작용하여 관련 `Session`을 로드하고 사용자 질의를 세션 히스토리에 첫 번째 `Event`로 추가합니다. `InvocationContext`(`ctx`)가 준비됩니다.
3. **에이전트 실행:** `Runner`는 지정된 루트 에이전트(예: `LlmAgent`)에서 `agent.run_async(ctx)`를 호출합니다.
4. **LLM 호출 (예시):** `Agent_Llm`은 정보를 얻기 위해 도구를 호출해야 한다고 결정합니다. `LLM`에 대한 요청을 준비합니다. LLM이 `MyTool`을 호출하기로 결정했다고 가정합니다.
5. **FunctionCall 이벤트 Yield:** `Agent_Llm`은 LLM으로부터 `FunctionCall` 응답을 수신하고, 이를 `Event(author='Agent_Llm', content=Content(parts=[Part(function_call=...)]))`로 래핑하여 이 이벤트를 `yield` 또는 `emit`합니다.
6. **에이전트 일시 중지:** `Agent_Llm`의 실행은 `yield` 직후 일시 중지됩니다.
7. **Runner 처리:** `Runner`는 FunctionCall 이벤트를 수신합니다. 이를 `SessionService`에 전달하여 히스토리에 기록합니다. 그런 다음 `Runner`는 이벤트를 상위 스트림(`User` 또는 애플리케이션)으로 yield합니다.
8. **에이전트 재개:** `Runner`는 이벤트가 처리되었음을 신호하고 `Agent_Llm`은 실행을 재개합니다.
9. **도구 실행:** 이제 `Agent_Llm`의 내부 흐름은 요청된 `MyTool` 실행을 진행합니다. `tool.run_async(...)`를 호출합니다.
10. **도구 결과 반환:** `MyTool`이 실행되고 결과를 반환합니다(예: `{'result': 'Paris'}`).
11. **FunctionResponse 이벤트 Yield:** 에이전트(`Agent_Llm`)는 도구 결과를 `FunctionResponse` 파트가 포함된 `Event`로 래핑합니다. 도구가 상태를 수정(`state_delta`)하거나 아티팩트를 저장(`artifact_delta`)한 경우 이 이벤트에 `actions`가 포함될 수도 있습니다. 에이전트는 이 이벤트를 `yield`합니다.
12. **에이전트 일시 중지:** `Agent_Llm`이 다시 일시 중지됩니다.
13. **Runner 처리:** `Runner`는 FunctionResponse 이벤트를 수신합니다. 모든 `state_delta`/`artifact_delta`를 적용하고 이벤트를 히스토리에 추가하는 `SessionService`에 전달합니다. `Runner`는 이벤트를 상위 스트림으로 yield합니다.
14. **에이전트 재개:** `Agent_Llm`이 재개되며, 이제 도구 결과와 모든 상태 변경사항이 커밋되었음을 알 수 있습니다.
15. **최종 LLM 호출 (예시):** `Agent_Llm`은 자연어 응답을 생성하기 위해 도구 결과를 `LLM`으로 다시 보냅니다.
16. **최종 텍스트 이벤트 Yield:** `Agent_Llm`은 LLM으로부터 최종 텍스트를 받아 `Event(author='Agent_Llm', content=Content(parts=[Part(text=...)]))`로 래핑하여 `yield`합니다.
17. **에이전트 일시 중지:** `Agent_Llm`이 일시 중지됩니다.
18. **Runner 처리:** `Runner`는 최종 텍스트 이벤트를 수신하고 히스토리를 위해 `SessionService`에 전달한 후 `User`에게 상위 스트림으로 yield합니다. 이는 `is_final_response()`로 표시될 가능성이 높습니다.
19. **에이전트 재개 및 완료:** `Agent_Llm`이 재개됩니다. 이번 호출에 대한 작업을 완료했으므로 `run_async` 제너레이터가 종료됩니다.
20. **Runner 완료:** `Runner`는 에이전트의 제너레이터가 소진되었음을 확인하고 이번 호출에 대한 루프를 완료합니다.

## 중요한 런타임 동작

### 상태 업데이트 및 커밋 시점 (State Updates & Commitment Timing)

* **규칙:** 코드(에이전트, 도구 또는 콜백)가 세션 상태를 수정할 때(예: `context.state['my_key'] = 'new_value'`), 이 변경사항은 처음에 현재 `InvocationContext` 내에 로컬로 기록됩니다. 변경사항은 해당 `state_delta`를 포함하는 `Event`가 코드에 의해 `yield`되고 이후 `Runner`에 의해 처리된 *후에만* **영구 저장되는 것(SessionService에 의해 저장됨)이 보장**됩니다.
* **의미:** `yield`에서 재개된 후 실행되는 코드는 *생성된 이벤트*에 표시된 상태 변경사항이 커밋되었다고 안심하고 가정할 수 있습니다.

=== "Python"

    ```py
    # 에이전트 로직 내부 (개념적)

    # 1. 상태 수정
    ctx.session.state['status'] = 'processing'
    event1 = Event(..., actions=EventActions(state_delta={'status': 'processing'}))

    # 2. 델타와 함께 이벤트 yield
    yield event1
    # --- 일시 중지 --- Runner가 event1을 처리하고 SessionService가 'status' = 'processing'을 커밋 ---

    # 3. 실행 재개
    # 이제 커밋된 상태에 의존해도 안전합니다
    current_status = ctx.session.state['status'] # 'processing'임이 보장됨
    print(f"Status after resuming: {current_status}")
    ```

=== "TypeScript"

    ```typescript
    // 에이전트 로직 내부 (개념적)

    // 1. 상태 수정
    ctx.state.set('status', 'processing');
    const event1 = createEvent({
        actions: createEventActions({stateDelta: {'status': 'processing'}}),
        // ... 기타 이벤트 필드
    });

    // 2. 델타와 함께 이벤트 yield
    yield event1;
    // --- 일시 중지 --- Runner가 event1을 처리하고 SessionService가 'status' = 'processing'을 커밋 ---

    // 3. 실행 재개
    const currentStatus = ctx.session.state['status']; // 'processing'임이 보장됨
    console.log(`Status after resuming: ${currentStatus}`);
    ```

=== "Go"

    ```go
    // Go 에이전트 로직 내부 (개념적)
    func (a *Agent) RunConceptual(ctx agent.InvocationContext) iter.Seq2[*session.Event, error] {
      return func(yield func(*session.Event, error) bool) {
          updateData := map[string]interface{}{"field_1": "value_2"}
          eventWithStateChange := session.NewEvent(ctx, ctx.InvocationID())
          eventWithStateChange.Author = a.Name()
          eventWithStateChange.Actions = &session.EventActions{StateDelta: updateData}

          if !yield(eventWithStateChange, nil) {
              return
          }

          // Runner가 이벤트를 처리하고 커밋합니다
          finalEvent := session.NewEvent(ctx, ctx.InvocationID())
          finalEvent.Author = a.Name()
          yield(finalEvent, nil)
      }
    }
    ```

=== "Java"

    ```java
    ConcurrentHashMap<String, Object> stateChanges = new ConcurrentHashMap<>();
    stateChanges.put("status", "processing");

    EventActions actions = EventActions.builder().stateDelta(stateChanges).build();
    Event event1 = Event.builder().actions(actions).build();

    return Flowable.just(event1)
        .map(emittedEvent -> {
            String currentStatus = (String) ctx.session().state().get("status");
            System.out.println("Status after resuming: " + currentStatus);
            return emittedEvent;
        });
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/runtime/RunnerLoop.kt:state_update_timing"
    ```

### 세션 상태의 "더티 리드 (Dirty Reads)"

* **정의:** 커밋은 yield *후에* 발생하지만, *동일한 호출 내에서 나중에* 실행되지만 상태 변경 이벤트가 실제로 생성되고 처리되기 *전에* 실행되는 코드는 **로컬의 커밋되지 않은 변경사항을 볼 수 있는 경우가 많습니다**. 이를 "더티 리드(dirty read)"라고 합니다.

=== "Python"

    ```py
    # before_agent_callback의 코드
    callback_context.state['field_1'] = 'value_1'
    # 상태는 로컬에서 'value_1'로 설정되었지만 아직 Runner에 의해 커밋되지 않음

    # ... 에이전트 실행 ...

    # 동일한 호출 내에서 나중에 호출된 도구의 코드
    # 읽기 가능(더티 리드)하지만 'value_1'이 아직 영구적으로 저장되지는 않음
    val = tool_context.state['field_1'] # 여기서 'val'은 'value_1'일 가능성이 높음
    print(f"Dirty read value in tool: {val}")
    ```

=== "TypeScript"

    ```typescript
    // beforeAgentCallback의 코드
    callbackContext.state.set('field_1', 'value_1');

    // --- 에이전트 실행 ... ---

    // 동일한 호출 내에서 나중에 호출된 도구의 코드
    const val = toolContext.state.get('field_1');
    console.log(`Dirty read value in tool: ${val}`);
    ```

=== "Go"

    ```go
    // before_agent_callback의 코드
    ctx.State.Set("field_1", "value_1")

    // ... 에이전트 실행 ...

    val := ctx.State.Get("field_1")
    fmt.Printf("Dirty read value in tool: %v\n", val)
    ```

=== "Java"

    ```java
    callbackContext.state().put("field_1", "value_1");
    Object val = toolContext.state().get("field_1");
    System.out.println("Dirty read value in tool: " + val);
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/runtime/RunnerLoop.kt:dirty_read"
    ```

### 스트리밍 vs 비스트리밍 출력 (`partial=True`)

* **스트리밍:** LLM은 토큰별로 또는 작은 청크로 응답을 생성합니다. 프레임워크는 단일 응답에 대해 여러 `Event` 객체를 생성하며 대부분 `partial=True`를 가집니다. `Runner`는 `partial=True`인 이벤트를 받으면 즉시 상위 스트림으로 전달하지만 `state_delta`와 같은 `actions` 처리는 건너뜁니다. 마지막 완료 이벤트(`partial=False`)에서만 `actions`를 완전히 처리하여 상태를 커밋합니다.
* **비스트리밍:** LLM이 전체 응답을 한 번에 생성합니다. `partial=False`인 단일 이벤트를 생성하고 `Runner`가 이를 완전히 처리합니다.

## 비동기 기본 원칙 (`run_async`)

* **핵심 설계:** ADK 런타임은 비동기 패턴 및 라이브러리(Python의 `asyncio`, Java의 `RxJava`, TypeScript의 네이티브 `Promise` 및 `AsyncGenerator`)를 기반으로 구축되어 차단 없이 동시 작업을 효율적으로 처리합니다.
* **메인 진입점:** `Runner.run_async`가 에이전트 호출을 실행하는 기본 메서드입니다.
* **동기 편의 메서드 (`run`):** 동기식 `Runner.run` 메서드는 주로 편의를 위해 존재합니다(예: 간단한 스크립트 또는 테스트). 내부적으로 `Runner.run`은 `Runner.run_async`를 호출하고 비동기 이벤트 루프 실행을 대신 관리합니다.
* **동기 콜백/도구:**
    * **블로킹 I/O:** 장시간 실행되는 동기 I/O 작업의 경우, 프레임워크가 항상 지연(stall)을 방지할 수 있는 것은 아닙니다. Python ADK는 asyncio 이벤트 루프에서 동기 도구 함수를 인라인으로 호출하므로 내부의 블로킹 입출력은 루프를 멈추게 합니다. 라이브 모드에서는 `RunConfig.tool_thread_pool_config`를 설정하여 백그라운드 스레드 풀에서 도구 실행을 대신 실행할 수 있습니다. Java ADK는 종종 블로킹 호출에 적절한 RxJava 스케줄러나 래퍼를 활용합니다. TypeScript에서 프레임워크는 단순히 함수를 await하며, 동기 함수가 블로킹 I/O를 수행하면 이벤트 루프가 멈춥니다. 가능한 한 항상 비동기 I/O API(Promise 반환)를 사용해야 합니다.
    * **CPU 바운드 작업:** 순수 CPU 집약적인 동기 작업은 두 환경 모두에서 실행 스레드를 차단합니다.
