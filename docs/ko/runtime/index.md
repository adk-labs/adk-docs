# 런타임

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

ADK 런타임은 사용자 상호 작용 중에 에이전트 애플리케이션을 구동하는 기본 엔진입니다. 정의된 에이전트, 도구 및 콜백을 가져와 사용자 입력에 대한 응답으로 실행을 오케스트레이션하고 정보 흐름, 상태 변경 및 LLM 또는 스토리지와 같은 외부 서비스와의 상호 작용을 관리하는 시스템입니다.

런타임을 에이전트 애플리케이션의 **"엔진"**으로 생각하십시오. 부품(에이전트, 도구)을 정의하면 런타임은 사용자 요청을 이행하기 위해 부품이 연결되고 함께 실행되는 방식을 처리합니다.

## 핵심 아이디어: 이벤트 루프

핵심적으로 ADK 런타임은 **이벤트 루프**에서 작동합니다. 이 루프는 `Runner` 구성 요소와 정의된 "실행 논리"(에이전트, 에이전트가 만드는 LLM 호출, 콜백 및 도구 포함) 간의 양방향 통신을 용이하게 합니다.

![intro_components.png](../assets/event-loop.png)

간단히 말해서:

1. `Runner`는 사용자 쿼리를 수신하고 기본 `Agent`에 처리를 시작하도록 요청합니다.
2. `Agent`(및 관련 논리)는 보고할 내용(응답, 도구 사용 요청 또는 상태 변경 등)이 있을 때까지 실행된 다음 `Event`를 **생성**하거나 **내보냅니다**.
3. `Runner`는 이 `Event`를 수신하고 관련 작업(예: `Services`를 통해 상태 변경 저장)을 처리하고 이벤트를 계속 전달합니다(예: 사용자 인터페이스로).
4. `Runner`가 이벤트를 처리한 *후에만* `Agent`의 논리가 일시 중지된 지점에서 **재개**되며 이제 Runner가 커밋한 변경 사항의 영향을 잠재적으로 볼 수 있습니다.
5. 이 주기는 에이전트가 현재 사용자 쿼리에 대해 생성할 이벤트가 더 이상 없을 때까지 반복됩니다.

이 이벤트 기반 루프는 ADK가 에이전트 코드를 실행하는 방식을 제어하는 기본 패턴입니다.

## 심장 박동: 이벤트 루프 - 내부 작동

이벤트 루프는 `Runner`와 사용자 지정 코드(에이전트, 도구, 콜백, 통칭하여 설계 문서에서 "실행 논리" 또는 "논리 구성 요소"라고 함) 간의 상호 작용을 정의하는 핵심 운영 패턴입니다. 책임의 명확한 구분을 설정합니다.

!!! Note
    특정 메서드 이름 및 매개변수 이름은 SDK 언어에 따라 약간 다를 수 있습니다(예: Python의 `agent_to_run.run_async(...)`, Go의 `agent.Run(...)`, Java의 `agent_to_run.runAsync(...)`). 자세한 내용은 언어별 API 설명서를 참조하십시오.

### Runner의 역할(오케스트레이터)

`Runner`는 단일 사용자 호출에 대한 중앙 코디네이터 역할을 합니다. 루프에서의 책임은 다음과 같습니다.

1. **시작:** 최종 사용자의 쿼리(`new_message`)를 수신하고 일반적으로 `SessionService`를 통해 세션 기록에 추가합니다.
2. **시작:** 기본 에이전트의 실행 메서드(예: `agent_to_run.run_async(...)`)를 호출하여 이벤트 생성 프로세스를 시작합니다.
3. **수신 및 처리:** 에이전트 논리가 `Event`를 `yield` 또는 `emit`할 때까지 기다립니다. 이벤트를 수신하면 Runner는 **즉시 처리**합니다. 여기에는 다음이 포함됩니다.
      * 구성된 `Services`(`SessionService`, `ArtifactService`, `MemoryService`)를 사용하여 `event.actions`에 표시된 변경 사항(예: `state_delta`, `artifact_delta`)을 커밋합니다.
      * 기타 내부 부기 수행.
4. **업스트림 생성:** 처리된 이벤트를 계속 전달합니다(예: 호출 애플리케이션 또는 렌더링을 위한 UI로).
5. **반복:** 에이전트 논리에 생성된 이벤트에 대한 처리가 완료되었음을 알리고 재개하여 *다음* 이벤트를 생성할 수 있도록 합니다.

*개념적 Runner 루프:*

=== "Python"

    ```py
    # Runner의 기본 루프 논리의 단순화된 보기
    def run(new_query, ...) -> Generator[Event]:
        # 1. SessionService를 통해 세션 이벤트 기록에 new_query 추가
        session_service.append_event(session, Event(author='user', content=new_query))

        # 2. 에이전트를 호출하여 이벤트 루프 시작
        agent_event_generator = agent_to_run.run_async(context)

        async for event in agent_event_generator:
            # 3. 생성된 이벤트를 처리하고 변경 사항 커밋
            session_service.append_event(session, event) # 상태/아티팩트 델타 등을 커밋합니다.
            # memory_service.update_memory(...) # 해당되는 경우
            # artifact_service는 에이전트 실행 중에 컨텍스트를 통해 이미 호출되었을 수 있습니다.

            # 4. 업스트림 처리를 위해 이벤트 생성(예: UI 렌더링)
            yield event
            # Runner는 생성 후 에이전트 생성기가 계속될 수 있음을 암시적으로 신호합니다.
    ```

=== "Go"

    ```go
    // Go에서 Runner의 기본 루프 논리의 단순화된 개념적 보기
    func (r *Runner) RunConceptual(ctx context.Context, session *session.Session, newQuery *genai.Content) iter.Seq2[*Event, error] {
        return func(yield func(*Event, error) bool) {
            // 1. SessionService를 통해 세션 이벤트 기록에 new_query 추가
            // ...
            userEvent := session.NewEvent(ctx.InvocationID()) // 개념적 보기를 위해 단순화됨
            userEvent.Author = "user"
            userEvent.LLMResponse = model.LLMResponse{Content: newQuery}

            if _, err := r.sessionService.Append(ctx, &session.AppendRequest{Event: userEvent}); err != nil {
                yield(nil, err)
                return
            }

            // 2. 에이전트를 호출하여 이벤트 스트림 시작
            // agent.Run도 iter.Seq2[*Event, error]를 반환한다고 가정
            agentEventsAndErrs := r.agent.Run(ctx, &agent.RunRequest{Session: session, Input: newQuery})

            for event, err := range agentEventsAndErrs {
                if err != nil {
                    if !yield(event, err) { // 오류가 있더라도 이벤트를 생성한 다음 중지
                        return
                    }
                    return // 에이전트가 오류로 완료됨
                }

                // 3. 생성된 이벤트를 처리하고 변경 사항 커밋
                // 실제 코드에서 볼 수 있듯이 부분적이지 않은 이벤트만 세션 서비스에 커밋
                if !event.LLMResponse.Partial {
                    if _, err := r.sessionService.Append(ctx, &session.AppendRequest{Event: event}); err != nil {
                        yield(nil, err)
                        return
                    }
                }
                // memory_service.update_memory(...) // 해당되는 경우
                // artifact_service는 에이전트 실행 중에 컨텍스트를 통해 이미 호출되었을 수 있습니다.

                // 4. 업스트림 처리를 위해 이벤트 생성
                if !yield(event, nil) {
                    return // 업스트림 소비자가 중지됨
                }
            }
            // 에이전트가 성공적으로 완료됨
        }
    }
    ```

=== "Java"

    ```java
    // Java에서 Runner의 기본 루프 논리의 단순화된 개념적 보기.
    public Flowable<Event> runConceptual(
        Session session,
        InvocationContext invocationContext,
        Content newQuery
        ) {

        // 1. SessionService를 통해 세션 이벤트 기록에 new_query 추가
        // ...
        sessionService.appendEvent(session, userEvent).blockingGet();

        // 2. 에이전트를 호출하여 이벤트 스트림 시작
        Flowable<Event> agentEventStream = agentToRun.runAsync(invocationContext);

        // 3. 생성된 각 이벤트를 처리하고 변경 사항을 커밋하고 "생성" 또는 "방출"
        return agentEventStream.map(event -> {
            // 이것은 세션 객체를 변경합니다(이벤트 추가, stateDelta 적용).
            // appendEvent의 반환 값(Single<Event>)은 개념적으로
            // 처리 후 이벤트 자체입니다.
            sessionService.appendEvent(session, event).blockingGet(); // 단순화된 차단 호출

            // memory_service.update_memory(...) // 해당되는 경우 - 개념적
            // artifact_service는 에이전트 실행 중에 컨텍스트를 통해 이미 호출되었을 수 있습니다.

            // 4. 업스트림 처리를 위해 이벤트 "생성"
            //    RxJava에서 맵에서 이벤트를 반환하면 다음 연산자 또는 구독자에게 효과적으로 생성됩니다.
            return event;
        });
    }
    ```

### 실행 논리의 역할(에이전트, 도구, 콜백)

에이전트, 도구 및 콜백 내의 코드는 실제 계산 및 의사 결정을 담당합니다. 루프와의 상호 작용에는 다음이 포함됩니다.

1. **실행:** 실행이 재개되었을 때의 세션 상태를 포함하여 현재 `InvocationContext`를 기반으로 논리를 실행합니다.
2. **생성:** 논리가 통신해야 할 때(메시지 보내기, 도구 호출, 상태 변경 보고) 관련 콘텐츠 및 작업이 포함된 `Event`를 구성한 다음 이 이벤트를 `Runner`에 다시 `yield`합니다.
3. **일시 중지:** 중요하게도 에이전트 논리의 실행은 `yield` 문(또는 RxJava의 `return`) 직후에 **즉시 일시 중지**됩니다. `Runner`가 3단계(처리 및 커밋)를 완료할 때까지 기다립니다.
4. **재개:** `Runner`가 생성된 이벤트를 처리한 *후에만* 에이전트 논리가 `yield` 바로 다음 문에서 실행을 재개합니다.
5. **업데이트된 상태 보기:** 재개 시 에이전트 논리는 이제 *이전에 생성된* 이벤트에서 `Runner`가 커밋한 변경 사항을 반영하는 세션 상태(`ctx.session.state`)에 안정적으로 액세스할 수 있습니다.

*개념적 실행 논리:*

=== "Python"

    ```py
    # Agent.run_async, 콜백 또는 도구 내부의 논리의 단순화된 보기

    # ... 이전 코드는 현재 상태를 기반으로 실행됩니다 ...

    # 1. 변경 또는 출력이 필요한지 확인하고 이벤트를 구성합니다.
    # 예: 상태 업데이트
    update_data = {'field_1': 'value_2'}
    event_with_state_change = Event(
        author=self.name,
        actions=EventActions(state_delta=update_data),
        content=types.Content(parts=[types.Part(text="상태가 업데이트되었습니다.")])
        # ... 기타 이벤트 필드 ...
    )

    # 2. 처리 및 커밋을 위해 Runner에 이벤트를 생성합니다.
    yield event_with_state_change
    # <<<<<<<<<<<< 실행이 여기서 일시 중지됩니다 >>>>>>>>>>>>

    # <<<<<<<<<<<< RUNNER가 이벤트를 처리하고 커밋합니다 >>>>>>>>>>>>

    # 3. Runner가 위 이벤트를 처리한 후에만 실행을 재개합니다.
    # 이제 Runner가 커밋한 상태가 안정적으로 반영됩니다.
    # 후속 코드는 생성된 이벤트의 변경 사항이 발생했다고 안전하게 가정할 수 있습니다.
    val = ctx.session.state['field_1']
    # 여기서 `val`은 "value_2"임이 보장됩니다(Runner가 성공적으로 커밋했다고 가정).
    print(f"실행 재개. field_1의 값은 이제: {val}")

    # ... 후속 코드가 계속됩니다 ...
    # 나중에 다른 이벤트를 생성할 수 있습니다...
    ```

=== "Go"

    ```go
    # Agent.Run, 콜백 또는 도구 내부의 논리의 단순화된 보기

    # ... 이전 코드는 현재 상태를 기반으로 실행됩니다 ...

    # 1. 변경 또는 출력이 필요한지 확인하고 이벤트를 구성합니다.
    # 예: 상태 업데이트
    updateData := map[string]interface{}{"field_1": "value_2"}
    eventWithStateChange := &Event{
        Author: self.Name(),
        Actions: &EventActions{StateDelta: updateData},
        Content: genai.NewContentFromText("상태가 업데이트되었습니다.", "model"),
        # ... 기타 이벤트 필드 ...
    }

    # 2. 처리 및 커밋을 위해 Runner에 이벤트를 생성합니다.
    # Go에서는 채널에 이벤트를 보내서 이 작업을 수행합니다.
    eventsChan <- eventWithStateChange
    # <<<<<<<<<<<< 실행이 여기서 일시 중지됩니다(개념적으로) >>>>>>>>>>>>
    # 채널의 다른 쪽 끝에 있는 Runner가 이벤트를 수신하고 처리합니다.
    # 에이전트의 고루틴은 계속될 수 있지만 논리적 흐름은 다음 입력 또는 단계를 기다립니다.

    # <<<<<<<<<<<< RUNNER가 이벤트를 처리하고 커밋합니다 >>>>>>>>>>>>

    # 3. Runner가 위 이벤트를 처리한 후에만 실행을 재개합니다.
    # 실제 Go 구현에서는 에이전트가
    # 다음 단계를 나타내는 새 RunRequest 또는 컨텍스트를 수신하여 처리할 가능성이 높습니다. 업데이트된 상태는
    # 해당 새 요청의 세션 객체의 일부가 됩니다.
    # 이 개념적 예에서는 상태만 확인합니다.
    val := ctx.State.Get("field_1")
    # 여기서 `val`은 Runner가
    # 에이전트를 다시 호출하기 전에 세션 상태를 업데이트했기 때문에 "value_2"임이 보장됩니다.
    fmt.Printf("실행 재개. field_1의 값은 이제: %v\n", val)

    # ... 후속 코드가 계속됩니다 ...
    # 나중에 채널에 다른 이벤트를 보낼 수 있습니다...
    ```

=== "Java"

    ```java
    // Agent.runAsync, 콜백 또는 도구 내부의 논리의 단순화된 보기
    // ... 이전 코드는 현재 상태를 기반으로 실행됩니다 ...

    // 1. 변경 또는 출력이 필요한지 확인하고 이벤트를 구성합니다.
    // 예: 상태 업데이트
    ConcurrentMap<String, Object> updateData = new ConcurrentHashMap<>();
    updateData.put("field_1", "value_2");

    EventActions actions = EventActions.builder().stateDelta(updateData).build();
    Content eventContent = Content.builder().parts(Part.fromText("상태가 업데이트되었습니다.")).build();

    Event eventWithStateChange = Event.builder()
        .author(self.name())
        .actions(actions)
        .content(Optional.of(eventContent))
        // ... 기타 이벤트 필드 ...
        .build();

    // 2. 이벤트를 "생성"합니다. RxJava에서는 스트림으로 방출하는 것을 의미합니다.
    //    Runner(또는 업스트림 소비자)가 이 Flowable을 구독합니다.
    //    Runner가 이 이벤트를 수신하면 처리합니다(예: sessionService.appendEvent 호출).
    //    Java ADK의 'appendEvent'는 'ctx'(InvocationContext) 내에 있는 'Session' 객체를 변경합니다.

    // <<<<<<<<<<<< 개념적 일시 중지 지점 >>>>>>>>>>>>
    // RxJava에서는 'eventWithStateChange'의 방출이 발생한 다음 스트림이
    // Runner가 이 이벤트를 처리한 *후*의 논리를 나타내는 'flatMap' 또는 'concatMap' 연산자로 계속될 수 있습니다.

    // "Runner가 처리를 완료한 후에만 실행 재개"를 모델링하려면:
    // Runner의 `appendEvent`는 일반적으로 비동기 작업 자체입니다(Single<Event> 반환).
    // 에이전트의 흐름은 커밋된 상태에 의존하는 후속 논리가
    // 해당 `appendEvent`가 완료된 *후*에 실행되도록 구조화되어야 합니다.

    // 이것이 Runner가 일반적으로 오케스트레이션하는 방법입니다.
    // Runner:
    //   agent.runAsync(ctx)
    //     .concatMapEager(eventFromAgent ->
    //         sessionService.appendEvent(ctx.session(), eventFromAgent) // 이것은 ctx.session().state()를 업데이트합니다.
    //             .toFlowable() // 처리된 후 이벤트를 방출합니다.
    //     )
    //     .subscribe(processedEvent -> { /* UI가 processedEvent를 렌더링합니다 */ });

    // 따라서 에이전트 자체 논리 내에서 생성된 이벤트 *후*에
    // 처리되고 상태 변경이 ctx.session().state()에 반영된 후 무언가를 수행해야 하는 경우
    // 해당 후속 논리는 일반적으로 반응형 체인의 다른 단계에 있습니다.

    // 이 개념적 예에서는 이벤트를 방출한 다음 "재개"를
    // Flowable 체인의 후속 작업으로 시뮬레이션합니다.

    return Flowable.just(eventWithStateChange) // 2단계: 이벤트 생성
        .concatMap(yieldedEvent -> {
            // <<<<<<<<<<<< RUNNER가 개념적으로 이벤트를 처리하고 커밋합니다 >>>>>>>>>>>>
            // 이 시점에서 실제 실행기에서는 ctx.session().appendEvent(yieldedEvent)가
            // Runner에 의해 호출되었을 것이고 ctx.session().state()가 업데이트되었을 것입니다.
            // 이것을 모델링하려는 에이전트의 개념적 논리 *내부*에 있으므로
            // Runner의 작업이 암시적으로 'ctx.session()'을 업데이트했다고 가정합니다.

            // 3. 실행 재개.
            // 이제 Runner가 커밋한 상태(sessionService.appendEvent를 통해)가
            // ctx.session().state()에 안정적으로 반영됩니다.
            Object val = ctx.session().state().get("field_1");
            // 여기서 `val`은 Runner가 호출한 `sessionService.appendEvent`가
            // `ctx` 객체 내의 세션 상태를 업데이트했기 때문에 "value_2"임이 보장됩니다.

            System.out.println("실행 재개. field_1의 값은 이제: " + val);

            // ... 후속 코드가 계속됩니다 ...
            // 이 후속 코드가 다른 이벤트를 생성해야 하는 경우 여기서 수행합니다.
    ```

`Runner`와 실행 논리 간의 이 협력적인 생성/일시 중지/재개 주기는 `Event` 객체에 의해 중재되며 ADK 런타임의 핵심을 형성합니다.

## 런타임의 주요 구성 요소

여러 구성 요소가 ADK 런타임 내에서 함께 작동하여 에이전트 호출을 실행합니다. 그들의 역할을 이해하면 이벤트 루프가 어떻게 작동하는지 명확해집니다.

1. ### `Runner`

      * **역할:** 단일 사용자 쿼리(`run_async`)에 대한 기본 진입점 및 오케스트레이터입니다.
      * **기능:** 전체 이벤트 루프를 관리하고, 실행 논리에서 생성된 이벤트를 수신하고, 서비스와 협력하여 이벤트 작업(상태/아티팩트 변경)을 처리 및 커밋하고, 처리된 이벤트를 업스트림(예: UI)으로 전달합니다. 기본적으로 생성된 이벤트를 기반으로 대화를 차례로 진행합니다. (`google.adk.runners.runner`에 정의됨).

2. ### 실행 논리 구성 요소

      * **역할:** 사용자 지정 코드와 핵심 에이전트 기능이 포함된 부분입니다.
      * **구성 요소:**
      * `Agent`(`BaseAgent`, `LlmAgent` 등): 정보를 처리하고 작업을 결정하는 기본 논리 단위입니다. 이벤트를 생성하는 `_run_async_impl` 메서드를 구현합니다.
      * `Tools`(`BaseTool`, `FunctionTool`, `AgentTool` 등): 에이전트(종종 `LlmAgent`)가 외부 세계와 상호 작용하거나 특정 작업을 수행하는 데 사용하는 외부 함수 또는 기능입니다. 실행하고 결과를 반환하며, 그런 다음 이벤트로 래핑됩니다.
      * `Callbacks`(함수): 에이전트에 연결된 사용자 정의 함수(예: `before_agent_callback`, `after_model_callback`)로, 실행 흐름의 특정 지점에 연결되어 잠재적으로 동작이나 상태를 수정하며, 그 효과는 이벤트에 캡처됩니다.
      * **기능:** 실제 사고, 계산 또는 외부 상호 작용을 수행합니다. **`Event` 객체를 생성**하고 Runner가 처리할 때까지 일시 중지하여 결과나 요구 사항을 전달합니다.

3. ### `Event`

      * **역할:** `Runner`와 실행 논리 간에 주고받는 메시지입니다.
      * **기능:** 원자적 발생(사용자 입력, 에이전트 텍스트, 도구 호출/결과, 상태 변경 요청, 제어 신호)을 나타냅니다. 발생 내용과 의도된 부작용(`state_delta`와 같은 `actions`)을 모두 전달합니다.

4. ### `Services`

      * **역할:** 영구적이거나 공유된 리소스를 관리하는 백엔드 구성 요소입니다. 이벤트 처리 중에 주로 `Runner`에서 사용됩니다.
      * **구성 요소:**
      * `SessionService`(`BaseSessionService`, `InMemorySessionService` 등): `Session` 객체를 관리하며, 저장/로드, 세션 상태에 `state_delta` 적용, `event history`에 이벤트 추가 등을 포함합니다.
      * `ArtifactService`(`BaseArtifactService`, `InMemoryArtifactService`, `GcsArtifactService` 등): 이진 아티팩트 데이터의 저장 및 검색을 관리합니다. `save_artifact`는 실행 논리 중에 컨텍스트를 통해 호출되지만 이벤트의 `artifact_delta`는 Runner/SessionService에 대한 작업을 확인합니다.
      * `MemoryService`(`BaseMemoryService` 등): (선택 사항) 사용자에 대한 세션 간의 장기 의미론적 메모리를 관리합니다.
      * **기능:** 지속성 계층을 제공합니다. `Runner`는 `event.actions`에 의해 신호된 변경 사항이 실행 논리가 재개되기 *전에* 안정적으로 저장되도록 하기 위해 이들과 상호 작용합니다.

5. ### `Session`

      * **역할:** 사용자와 애플리케이션 간의 *하나의 특정 대화*에 대한 상태 및 기록을 보유하는 데이터 컨테이너입니다.
      * **기능:** 현재 `state` 사전, 모든 과거 `events`(`event history`) 목록 및 관련 아티팩트에 대한 참조를 저장합니다. `SessionService`에서 관리하는 상호 작용의 기본 레코드입니다.

6. ### `Invocation`

      * **역할:** `Runner`가 수신한 순간부터 에이전트 논리가 해당 쿼리에 대한 이벤트 생성을 마칠 때까지 *단일* 사용자 쿼리에 대한 응답으로 발생하는 모든 것을 나타내는 개념적 용어입니다.
      * **기능:** 호출에는 여러 에이전트 실행(에이전트 전송 또는 `AgentTool` 사용 시), 여러 LLM 호출, 도구 실행 및 콜백 실행이 포함될 수 있으며, 모두 `InvocationContext` 내의 단일 `invocation_id`로 연결됩니다. `temp:` 접두사가 붙은 상태 변수는 단일 호출에 엄격하게 범위가 지정되며 이후에는 삭제됩니다.

이러한 플레이어는 이벤트 루프를 통해 지속적으로 상호 작용하여 사용자 요청을 처리합니다.

## 작동 방식: 단순화된 호출

도구를 호출하는 LLM 에이전트가 포함된 일반적인 사용자 쿼리에 대한 단순화된 흐름을 추적해 보겠습니다.

![intro_components.png](../assets/invocation-flow.png)

### 단계별 분석

1. **사용자 입력:** 사용자가 쿼리를 보냅니다(예: "프랑스의 수도는 어디입니까?").
2. **Runner 시작:** `Runner.run_async`가 시작됩니다. `SessionService`와 상호 작용하여 관련 `Session`을 로드하고 사용자 쿼리를 세션 기록의 첫 번째 `Event`로 추가합니다. `InvocationContext`(`ctx`)가 준비됩니다.
3. **에이전트 실행:** `Runner`는 지정된 루트 에이전트(예: `LlmAgent`)에서 `agent.run_async(ctx)`를 호출합니다.
4. **LLM 호출(예):** `Agent_Llm`은 정보가 필요하다고 판단하고, 아마도 도구를 호출하여 정보를 얻습니다. `LLM`에 대한 요청을 준비합니다. LLM이 `MyTool`을 호출하기로 결정했다고 가정해 보겠습니다.
5. **FunctionCall 이벤트 생성:** `Agent_Llm`은 LLM에서 `FunctionCall` 응답을 수신하고 `Event(author='Agent_Llm', content=Content(parts=[Part(function_call=...)]))`로 래핑한 다음 이 이벤트를 `yield` 또는 `emit`합니다.
6. **에이전트 일시 중지:** `Agent_Llm`의 실행은 `yield` 직후에 일시 중지됩니다.
7. **Runner 처리:** `Runner`는 FunctionCall 이벤트를 수신합니다. 기록에 기록하기 위해 `SessionService`에 전달합니다. 그런 다음 `Runner`는 이벤트를 `User`(또는 애플리케이션)로 업스트림으로 생성합니다.
8. **에이전트 재개:** `Runner`는 이벤트가 처리되었음을 알리고 `Agent_Llm`은 실행을 재개합니다.
9. **도구 실행:** `Agent_Llm`의 내부 흐름은 이제 요청된 `MyTool`을 실행합니다. `tool.run_async(...)`를 호출합니다.
10. **도구 결과 반환:** `MyTool`이 실행되고 결과를 반환합니다(예: `{'result': 'Paris'}`).
11. **FunctionResponse 이벤트 생성:** 에이전트(`Agent_Llm`)는 도구 결과를 `FunctionResponse` 부분이 포함된 `Event`로 래핑합니다(예: `Event(author='Agent_Llm', content=Content(role='user', parts=[Part(function_response=...)]))`). 이 이벤트에는 도구가 상태를 수정(`state_delta`)하거나 아티팩트를 저장(`artifact_delta`)한 경우 `actions`가 포함될 수도 있습니다. 에이전트는 이 이벤트를 `yield`합니다.
12. **에이전트 일시 중지:** `Agent_Llm`이 다시 일시 중지됩니다.
13. **Runner 처리:** `Runner`는 FunctionResponse 이벤트를 수신합니다. `state_delta`/`artifact_delta`를 적용하고 기록에 이벤트를 추가하는 `SessionService`에 전달합니다. `Runner`는 이벤트를 업스트림으로 생성합니다.
14. **에이전트 재개:** `Agent_Llm`이 재개되어 이제 도구 결과와 모든 상태 변경이 커밋되었음을 알게 됩니다.
15. **최종 LLM 호출(예):** `Agent_Llm`은 자연어 응답을 생성하기 위해 도구 결과를 `LLM`에 다시 보냅니다.
16. **최종 텍스트 이벤트 생성:** `Agent_Llm`은 `LLM`에서 최종 텍스트를 수신하고 `Event(author='Agent_Llm', content=Content(parts=[Part(text=...)]))`로 래핑한 다음 `yield`합니다.
17. **에이전트 일시 중지:** `Agent_Llm`이 일시 중지됩니다.
18. **Runner 처리:** `Runner`는 최종 텍스트 이벤트를 수신하고 기록을 위해 `SessionService`에 전달하고 `User`로 업스트림으로 생성합니다. 이것은 `is_final_response()`로 표시될 가능성이 높습니다.
19. **에이전트 재개 및 완료:** `Agent_Llm`이 재개됩니다. 이 호출에 대한 작업이 완료되면 `run_async` 생성기가 완료됩니다.
20. **Runner 완료:** `Runner`는 에이전트의 생성기가 소진된 것을 확인하고 이 호출에 대한 루프를 완료합니다.

이 생성/일시 중지/처리/재개 주기는 상태 변경이 일관되게 적용되고 실행 논리가 이벤트를 생성한 후 항상 가장 최근에 커밋된 상태에서 작동하도록 보장합니다.

## 중요한 런타임 동작

ADK 런타임이 상태, 스트리밍 및 비동기 작업을 처리하는 방법에 대한 몇 가지 주요 측면을 이해하는 것은 예측 가능하고 효율적인 에이전트를 구축하는 데 중요합니다.

### 상태 업데이트 및 커밋 타이밍

* **규칙:** 코드(에이전트, 도구 또는 콜백)가 세션 상태를 수정할 때(예: `context.state['my_key'] = 'new_value'`), 이 변경 사항은 처음에 현재 `InvocationContext` 내에 로컬로 기록됩니다. 변경 사항은 해당 `state_delta`를 `actions`에 포함하는 `Event`가 코드에 의해 `yield`되고 이후에 `Runner`에 의해 처리된 *후에만* **지속되는 것이 보장**됩니다(`SessionService`에 의해 저장됨).

* **의미:** `yield`에서 재개된 *후*에 실행되는 코드는 *생성된 이벤트*에서 신호된 상태 변경이 커밋되었다고 안정적으로 가정할 수 있습니다.

=== "Python"

    ```py
    # 에이전트 논리 내부(개념적)

    # 1. 상태 수정
    ctx.session.state['status'] = 'processing'
    event1 = Event(..., actions=EventActions(state_delta={'status': 'processing'}))

    # 2. 델타와 함께 이벤트 생성
    yield event1
    # --- 일시 중지 --- Runner가 event1을 처리하고 SessionService가 'status' = 'processing'을 커밋합니다 ---

    # 3. 실행 재개
    # 이제 커밋된 상태에 의존하는 것이 안전합니다.
    current_status = ctx.session.state['status'] # 'processing'임이 보장됩니다.
    print(f"재개 후 상태: {current_status}")
    ```

=== "Go"

    ```go
      # 에이전트 논리 내부(개념적)

    func (a *Agent) RunConceptual(ctx agent.InvocationContext) iter.Seq2[*session.Event, error] {
      # 전체 논리는 반복자로 반환될 함수로 래핑됩니다.
      return func(yield func(*session.Event, error) bool) {
          # ... 이전 코드는 입력 `ctx`의 현재 상태를 기반으로 실행됩니다 ...
          # 예: val := ctx.State().Get("field_1")는 여기서 "value_1"을 반환할 수 있습니다.

          # 1. 변경 또는 출력이 필요한지 확인하고 이벤트를 구성합니다.
          updateData := map[string]interface{}{"field_1": "value_2"}
          eventWithStateChange := session.NewEvent(ctx.InvocationID())
          eventWithStateChange.Author = a.Name()
          eventWithStateChange.Actions = &session.EventActions{StateDelta: updateData}
          # ... 기타 이벤트 필드 ...


          # 2. 처리 및 커밋을 위해 Runner에 이벤트를 생성합니다.
          # 에이전트의 실행은 이 호출 직후에 계속됩니다.
          if !yield(eventWithStateChange, nil) {
              # yield가 false를 반환하면 소비자(Runner)가
              # 수신을 중지했음을 의미하므로 이벤트 생성을 중지해야 합니다.
              return
          }

          # <<<<<<<<<<<< RUNNER가 이벤트를 처리하고 커밋합니다 >>>>>>>>>>>>
          # 이것은 에이전트의 반복자가
          # 이벤트를 생성한 후 에이전트 외부에서 발생합니다.

          # 3. 에이전트는 방금 생성한 상태 변경을 즉시 볼 수 없습니다.
          # 상태는 단일 `Run` 호출 내에서 변경할 수 없습니다.
          val := ctx.State().Get("field_1")
          # 여기서 `val`은 여전히 "value_1"입니다(또는 시작 시 무엇이었든).
          # 업데이트된 상태("value_2")는 *다음* `Run` 호출의 `ctx`에서만
          # 사용할 수 있습니다.

          # ... 후속 코드가 계속되어 잠재적으로 더 많은 이벤트를 생성합니다 ...
          finalEvent := session.NewEvent(ctx.InvocationID())
          finalEvent.Author = a.Name()
          # ...
          yield(finalEvent, nil)
      }
    }
    ```

=== "Java"

    ```java
    // 에이전트 논리 내부(개념적)
    // ... 이전 코드는 현재 상태를 기반으로 실행됩니다 ...

    // 1. 상태 수정을 준비하고 이벤트를 구성합니다.
    ConcurrentHashMap<String, Object> stateChanges = new ConcurrentHashMap<>();
    stateChanges.put("status", "processing");

    EventActions actions = EventActions.builder().stateDelta(stateChanges).build();
    Content content = Content.builder().parts(Part.fromText("상태 업데이트: 처리 중")).build();

    Event event1 = Event.builder()
        .actions(actions)
        // ...
        .build();

    // 2. 델타와 함께 이벤트 생성
    return Flowable.just(event1)
        .map(
            emittedEvent -> {
                // --- 개념적 일시 중지 및 RUNNER 처리 ---
                // 3. 실행 재개(개념적)
                // 이제 커밋된 상태에 의존하는 것이 안전합니다.
                String currentStatus = (String) ctx.session().state().get("status");
                System.out.println("재개 후 상태(에이전트 논리 내부): " + currentStatus); // 'processing'임이 보장됩니다.

                // 이벤트 자체(event1)가 전달됩니다.
                // 이 에이전트 단계 내의 후속 논리가 *다른* 이벤트를 생성한 경우
                // concatMap을 사용하여 해당 새 이벤트를 방출합니다.
                return emittedEvent;
            });

    // ... 후속 에이전트 논리에는 추가 반응형 연산자
    // 또는 이제 업데이트된 `ctx.session().state()`를 기반으로 더 많은 이벤트를 방출하는 것이 포함될 수 있습니다.
    ```

### 세션 상태의 "더티 읽기"

* **정의:** 커밋은 `yield` *후*에 발생하지만 *동일한 호출 내에서 나중에* 실행되지만 상태 변경 이벤트가 실제로 생성되고 처리되기 *전에* 실행되는 코드는 **종종 로컬, 커밋되지 않은 변경 사항을 볼 수 있습니다**. 이것을 "더티 읽기"라고도 합니다.
* **예:**

=== "Python"

    ```py
    # before_agent_callback의 코드
    callback_context.state['field_1'] = 'value_1'
    # 상태는 로컬로 'value_1'로 설정되지만 아직 Runner에 의해 커밋되지 않았습니다.

    # ... 에이전트 실행 ...

    # *동일한 호출 내에서* 나중에 호출되는 도구의 코드
    # 읽기 가능(더티 읽기)하지만 'value_1'은 아직 영구적이라고 보장되지 않습니다.
    val = tool_context.state['field_1'] # 여기서 'val'은 'value_1'일 가능성이 높습니다.
    print(f"도구의 더티 읽기 값: {val}")

    # state_delta={'field_1': 'value_1'}를 전달하는 이벤트가
    # 이 도구가 실행된 *후*에 생성되고 Runner에 의해 처리된다고 가정합니다.
    ```

=== "Go"

    ```go
    # before_agent_callback의 코드
    # 콜백은 컨텍스트의 세션 상태를 직접 수정합니다.
    # 이 변경 사항은 현재 호출 컨텍스트에 로컬입니다.
    ctx.State.Set("field_1", "value_1")
    # 상태는 로컬로 'value_1'로 설정되지만 아직 Runner에 의해 커밋되지 않았습니다.

    # ... 에이전트 실행 ...

    # *동일한 호출 내에서* 나중에 호출되는 도구의 코드
    # 읽기 가능(더티 읽기)하지만 'value_1'은 아직 영구적이라고 보장되지 않습니다.
    val := ctx.State.Get("field_1") # 여기서 'val'은 'value_1'일 가능성이 높습니다.
    fmt.Printf("도구의 더티 읽기 값: %v\n", val)

    # state_delta={'field_1': 'value_1'}를 전달하는 이벤트가
    # 이 도구가 실행된 *후*에 생성되고 Runner에 의해 처리된다고 가정합니다.
    ```

=== "Java"

    ```java
    // 상태 수정 - BeforeAgentCallback의 코드
    // 그리고 이 변경 사항을 callbackContext.eventActions().stateDelta()에 준비합니다.
    callbackContext.state().put("field_1", "value_1");

    # --- 에이전트 실행 ... ---

    # --- *동일한 호출 내에서* 나중에 호출되는 도구의 코드 ---
    # 읽기 가능(더티 읽기)하지만 'value_1'은 아직 영구적이라고 보장되지 않습니다.
    Object val = toolContext.state().get("field_1"); // 여기서 'val'은 'value_1'일 가능성이 높습니다.
    System.out.println("도구의 더티 읽기 값: " + val);
    # state_delta={'field_1': 'value_1'}를 전달하는 이벤트가
    # 이 도구가 실행된 *후*에 생성되고 Runner에 의해 처리된다고 가정합니다.
    ```

* **의미:**
  * **이점:** 단일 복잡한 단계 내의 다른 논리 부분(예: 다음 LLM 턴 전의 여러 콜백 또는 도구 호출)이 전체 생성/커밋 주기를 기다리지 않고 상태를 사용하여 조정할 수 있습니다.
  * **주의:** 중요한 논리에 대해 더티 읽기에 크게 의존하는 것은 위험할 수 있습니다. `state_delta`를 전달하는 이벤트가 `Runner`에 의해 생성되고 처리되기 *전에* 호출이 실패하면 커밋되지 않은 상태 변경이 손실됩니다. 중요한 상태 전환의 경우 성공적으로 처리되는 이벤트와 연결되어 있는지 확인하십시오.

### 스트리밍 대 비스트리밍 출력(`partial=True`)

이것은 주로 LLM의 응답이 처리되는 방식, 특히 스트리밍 생성 API를 사용할 때와 관련이 있습니다.

* **스트리밍:** LLM은 응답을 토큰별 또는 작은 청크로 생성합니다.
  * 프레임워크(종종 `BaseLlmFlow` 내)는 단일 개념적 응답에 대해 여러 `Event` 객체를 생성합니다. 이러한 이벤트의 대부분은 `partial=True`를 갖습니다.
  * `Runner`는 `partial=True`인 이벤트를 수신하면 일반적으로 **즉시 업스트림으로 전달**하지만(UI 표시용) `actions`(예: `state_delta`) 처리는 **건너뜁니다**.
  * 결국 프레임워크는 해당 응답에 대한 최종 이벤트를 생성하며, 이는 비부분(`partial=False` 또는 `turn_complete=True`를 통해 암시적으로)으로 표시됩니다.
  * `Runner`는 **이 최종 이벤트만 완전히 처리**하여 관련 `state_delta` 또는 `artifact_delta`를 커밋합니다.
* **비스트리밍:** LLM은 전체 응답을 한 번에 생성합니다. 프레임워크는 `Runner`가 완전히 처리하는 비부분으로 표시된 단일 이벤트를 생성합니다.
* **중요한 이유:** 상태 변경이 원자적으로 적용되고 LLM의 *완전한* 응답을 기반으로 한 번만 적용되도록 보장하면서도 UI가 생성될 때 텍스트를 점진적으로 표시할 수 있도록 합니다.

## 비동기가 기본(`run_async`)

* **핵심 설계:** ADK 런타임은 기본적으로 비동기 라이브러리(예: Python의 `asyncio` 및 Java의 `RxJava`)를 기반으로 구축되어 동시 작업(예: LLM 응답 또는 도구 실행 대기)을 차단하지 않고 효율적으로 처리합니다.
* **기본 진입점:** `Runner.run_async`는 에이전트 호출을 실행하기 위한 기본 메서드입니다. 모든 핵심 실행 가능 구성 요소(에이전트, 특정 흐름)는 내부적으로 `비동기` 메서드를 사용합니다.
* **동기 편의성(`run`):** 동기 `Runner.run` 메서드는 주로 편의를 위해 존재합니다(예: 간단한 스크립트 또는 테스트 환경). 그러나 내부적으로 `Runner.run`은 일반적으로 `Runner.run_async`를 호출하고 비동기 이벤트 루프 실행을 관리합니다.
* **개발자 경험:** 최상의 성능을 위해 애플리케이션(예: ADK를 사용하는 웹 서버)을 비동기식으로 설계하는 것이 좋습니다. Python에서는 `asyncio`를 사용하고 Java에서는 `RxJava`의 반응형 프로그래밍 모델을 활용합니다.
* **동기 콜백/도구:** ADK 프레임워크는 도구 및 콜백에 대한 비동기 및 동기 함수를 모두 지원합니다.
    * **차단 I/O:** 장기 실행 동기 I/O 작업의 경우 프레임워크는 중단을 방지하려고 시도합니다. Python ADK는 asyncio.to_thread를 사용할 수 있으며 Java ADK는 종종 차단 호출에 대해 적절한 RxJava 스케줄러 또는 래퍼에 의존합니다.
    * **CPU 바운드 작업:** 순전히 CPU 집약적인 동기 작업은 두 환경 모두에서 실행 스레드를 계속 차단합니다.

이러한 동작을 이해하면 상태 일관성, 스트리밍 업데이트 및 비동기 실행과 관련된 문제를 디버깅하고 보다 강력한 ADK 애플리케이션을 작성하는 데 도움이 됩니다.
