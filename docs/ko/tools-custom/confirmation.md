# ADK 도구에 대한 작업 확인 (Action Confirmation)

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.14.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.3.0</span><span class="lst-preview">실험적</span>
</div>

일부 에이전트 워크플로는 의사 결정, 검증, 보안 또는 일반적인 감독을 위해 확인이 필요합니다. 이러한 경우 워크플로를 진행하기 전에 사람이나 감독 시스템으로부터 응답을 받아야 합니다. ADK(Agent Development Kit)의 *도구 확인(Tool Confirmation)* 기능을 사용하면 ADK 도구의 실행을 일시 중지하고 사용자 또는 다른 시스템과 상호작용하여 확인을 받거나 구조화된 데이터를 수집한 후 계속 진행할 수 있습니다. ADK 도구에서 도구 확인을 다음과 같은 방식으로 사용할 수 있습니다:

-   **[불리언 확인 (Boolean Confirmation)](#boolean-confirmation):** 확인 플래그 또는 프로바이더로 도구를 구성할 수 있습니다. 이 옵션은 예/아니오 확인 응답을 위해 도구를 일시 중지합니다.
-   **[고급 확인 (Advanced Confirmation)](#advanced-confirmation):** 구조화된 데이터 응답이 필요한 시나리오의 경우 확인을 설명하는 텍스트 프롬프트와 예상되는 응답을 도구에 구성할 수 있습니다.

!!! example "실험적 기능"
    도구 확인 기능은 실험적이며 몇 가지 [알려진 제한사항](#known-limitations)이 있습니다.
    여러분의 [피드백](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=tool%20confirmation)을 환영합니다!

요청이 사용자에게 전달되는 방식을 구성할 수 있으며, 시스템은 ADK 서버의 REST API를 통해 전송된 [원격 응답](#remote-response)을 사용할 수도 있습니다. ADK 웹 사용자 인터페이스에서 확인 기능을 사용할 때 에이전트 워크플로는 그림 1과 같이 입력을 요청하는 대화 상자를 사용자에게 표시합니다:

![도구 확인을 위한 기본 사용자 인터페이스 스크린샷](../assets/confirmation-ui.png)

**그림 1.** 고급 도구 응답 구현을 사용한 확인 응답 요청 대화 상자 예시.

다음 섹션에서는 확인 시나리오에 이 기능을 사용하는 방법을 설명합니다. 완전한 코드 샘플은 [human_tool_confirmation](https://github.com/google/adk-python/blob/fc90ce968f114f84b14829f8117797a4c256d710/contributing/samples/human_tool_confirmation/agent.py) 예제를 참고하세요. 에이전트 워크플로에 사람의 입력을 통합하는 추가적인 방법은 [Human-in-the-loop](../workflows/patterns.md#human-in-the-loop) 에이전트 패턴을 참고하세요.

## 불리언 확인 (Boolean confirmation) {#boolean-confirmation}

도구에 사용자의 간단한 `yes` 또는 `no`만 필요한 경우 확인 단계를 추가할 수 있습니다. Python, Go 및 Java에서는 도구를 `FunctionTool` 클래스로 래핑하고 `require_confirmation` 매개변수(또는 이에 상응하는 매개변수)를 `True`로 설정하여 이를 활성화할 수 있습니다. TypeScript에서는 `ToolContext`를 사용하여 `execute` 함수 내에서 이 로직을 수동으로 구현합니다.

다음 예시는 불리언 확인을 활성화하는 방법을 보여줍니다:

=== "Python"

    ```python
    root_agent = Agent(
        # ...
        tools = [
            # 도구 호출에 대한 사용자 확인을 요구하려면 require_confirmation을 True로 설정합니다.
            FunctionTool(reimburse, require_confirmation=True),
        ],
        # ...
    )

    # 이 구현 방법은 최소한의 코드가 필요하지만 사용자나 확인 시스템의 간단한 승인으로 제한됩니다.
    # 이 접근 방식에 대한 완전한 예제는 다음 코드 샘플을 참조하세요:
    # https://github.com/google/adk-python/blob/main/contributing/samples/human_tool_confirmation/agent.py
    ```

=== "TypeScript"

    !!! note
        현재 ADK for TypeScript에서는 도구의 `execute` 함수 내에서 확인 로직을 수동으로 구현해야 합니다.

    ```typescript
    --8<-- "examples/typescript/snippets/tools/confirmation/boolean_confirmation.ts:boolean_confirmation"
    ```

=== "Go"

    ```go
    reimburseTool, _ := functiontool.New(functiontool.Config{
        Name:        "reimburse",
        Description: "Reimburse an amount",
        // 도구 호출에 대한 사용자 확인을 요구하려면 RequireConfirmation을 true로 설정합니다.
        RequireConfirmation: true,
    }, func(ctx tool.Context, args ReimburseArgs) (ReimburseResult, error) {
        // 실제 구현
        return ReimburseResult{Status: "ok"}, nil
    })

    rootAgent, _ := llmagent.New(llmagent.Config{
        // ...
        Tools: []tool.Tool{reimburseTool},
    })
    ```

=== "Java"

    ```java
    LlmAgent rootAgent = LlmAgent.builder()
        // ...
        .tools(
            // 도구 호출에 대한 사용자 확인을 요구하려면 requireConfirmation을 true로 설정합니다.
            FunctionTool.create(myClassInstance, "reimburse", true)
        )
        // ...
        .build();
    ```

### 확인 필요 함수 (Require confirmation function)

도구의 입력에 따라 불리언 응답을 반환하는 함수를 사용하여 확인 요구사항 동작을 동적으로 수정할 수 있습니다. TypeScript에서는 `execute` 함수에 조건부 로직을 추가하여 이를 처리합니다.

=== "Python"

    ```python
    async def confirmation_threshold(
        amount: int, tool_context: ToolContext
    ) -> bool:
      """금액이 1000보다 큰 경우 True를 반환합니다."""
      return amount > 1000

    root_agent = Agent(
        # ...
        tools = [
            # 동적으로 확인을 요구하기 위해 임계값 함수 전달
            FunctionTool(reimburse, require_confirmation=confirmation_threshold),
        ],
        # ...
    )
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/typescript/snippets/tools/confirmation/boolean_confirmation.ts:dynamic_confirmation"
    ```

=== "Go"

    ```go
    reimburseTool, _ := functiontool.New(functiontool.Config{
        Name:        "reimburse",
        Description: "Reimburse an amount",
        // RequireConfirmationProvider를 사용하면 사용자 확인이 필요한지 여부를 동적으로 결정할 수 있습니다.
        RequireConfirmationProvider: func(args ReimburseArgs) bool {
            return args.Amount > 1000
        },
    }, func(ctx tool.Context, args ReimburseArgs) (ReimburseResult, error) {
        // 실제 구현
        return ReimburseResult{Status: "ok"}, nil
    })
    ```

=== "Java"

    ```java
    // ADK Java에서는 람다 매개변수 대신 ToolContext를 사용하여 도구 로직 내에서 동적 임계값 확인 로직을 직접 평가합니다.
    public Map<String, Object> reimburse(
        @Schema(name="amount") int amount, ToolContext toolContext) {

      // 1. 동적 임계값 확인
      if (amount > 1000) {
        Optional<ToolConfirmation> toolConfirmation = toolContext.toolConfirmation();
        if (toolConfirmation.isEmpty()) {
           toolContext.requestConfirmation("Amount > 1000 requires approval.");
           return Map.of("status", "Pending manager approval.");
        } else if (!toolConfirmation.get().confirmed()) {
           return Map.of("status", "Reimbursement rejected.");
        }
      }

      // 2. 실제 도구 로직 진행
      return Map.of("status", "ok", "reimbursedAmount", amount);
    }

    LlmAgent rootAgent = LlmAgent.builder()
        // ...
        .tools(
            // 사용자 정의 임계값 로직이 이미 메서드 내부에서 처리되므로 requireConfirmation 플래그가 설정되지 않습니다!
            FunctionTool.create(this, "reimburse")
        )
        // ...
        .build();
    ```

## 고급 확인 (Advanced confirmation) {#advanced-confirmation}

도구 확인에 사용자에게 더 많은 세부정보가 필요하거나 더 복잡한 응답이 필요한 경우 `tool_confirmation` 구현을 사용합니다. 이 접근 방식은 `ToolContext` 객체를 확장하여 사용자를 위한 요청에 대한 텍스트 설명을 추가하고 더 복잡한 응답 데이터를 허용합니다. 이러한 방식으로 도구 확인을 구현하면 도구 실행을 일시 중지하고 특정 정보를 요청한 다음 제공된 데이터로 도구를 재개할 수 있습니다.

이 확인 흐름에는 시스템이 사람의 응답을 위한 입력 요청을 조합하고 전송하는 요청 단계와 시스템이 반환된 데이터를 수신하고 처리하는 응답 단계가 있습니다.

### 확인 정의

고급 확인을 사용하여 도구를 만들 때는 `hint` 및 `payload` 매개변수와 함께 `Tool Context Request Confirmation` 메서드를 사용합니다:

-   `hint`: 사용자에게 필요한 내용을 설명하는 설명 메시지.
-   `payload`: 반환될 것으로 예상하는 데이터의 구조. 이는 JSON 형식의 문자열로 직렬화될 수 있어야 합니다.

이 접근 방식에 대한 완전한 예제는 [human_tool_confirmation](https://github.com/google/adk-python/blob/fc90ce968f114f84b14829f8117797a4c256d710/contributing/samples/human_tool_confirmation/agent.py) 코드 샘플을 참고하세요. 확인을 받는 동안 에이전트 워크플로 도구 실행이 일시 중지됩니다. 확인을 받은 후 `tool_confirmation.payload` 객체에서 확인 응답에 액세스한 다음 워크플로 실행을 진행할 수 있습니다.

다음 코드는 직원의 휴가 요청을 처리하는 도구의 구현 예시를 보여줍니다:

=== "Python"

    ```python
    def request_time_off(days: int, tool_context: ToolContext):
        """직원의 휴가를 요청합니다."""
        # ...
        tool_confirmation = tool_context.tool_confirmation
        if not tool_confirmation:
            tool_context.request_confirmation(
                hint=(
                    'Please approve or reject the tool call request_time_off() by'
                    ' responding with a FunctionResponse with an expected'
                    ' ToolConfirmation payload.'
                ),
                payload={
                    'approved_days': 0,
                },
            )
            # 도구가 확인 응답을 기다리고 있음을 나타내는 중간 상태 반환:
            return {'status': 'Manager approval is required.'}

        approved_days = tool_confirmation.payload['approved_days']
        approved_days = min(approved_days, days)
        if approved_days == 0:
            return {'status': 'The time off request is rejected.', 'approved_days': 0}
        return {
            'status': 'ok',
            'approved_days': approved_days,
        }
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/typescript/snippets/tools/confirmation/confirmation_example.ts:advanced_confirmation"
    ```

=== "Go"

    ```go
    func requestTimeOff(ctx tool.Context, args RequestTimeOffArgs) (map[string]any, error) {
        confirmation := ctx.ToolConfirmation()
        if confirmation == nil {
            ctx.RequestConfirmation(
                "Please approve or reject the tool call requestTimeOff() by "+
                "responding with a FunctionResponse with an expected "+
                "ToolConfirmation payload.",
                map[string]any{"approved_days": 0},
            )
            return map[string]any{"status": "Manager approval is required."}, nil
        }

        payload := confirmation.Payload.(map[string]any)
        // Go에서 JSON의 map[string]any 값은 기본적으로 float64입니다
        approvedDays := int(payload["approved_days"].(float64))
        approvedDays = min(approvedDays, args.Days)

        if approvedDays == 0 {
            return map[string]any{"status": "The time off request is rejected.", "approved_days": 0}, nil
        }

        return map[string]any{
            "status": "ok",
            "approved_days": approvedDays,
        }, nil
    }
    ```

=== "Java"

    ```java
    public Map<String, Object> requestTimeOff(
        @Schema(name="days") int days,
        ToolContext toolContext) {
        // 직원의 휴가를 요청합니다.
        // ...
        Optional<ToolConfirmation> toolConfirmation = toolContext.toolConfirmation();
        if (toolConfirmation.isEmpty()) {
            toolContext.requestConfirmation(
                "Please approve or reject the tool call requestTimeOff() by " +
                "responding with a FunctionResponse with an expected " +
                "ToolConfirmation payload.",
                Map.of("approved_days", 0)
            );
            // 도구가 확인 응답을 기다리고 있음을 나타내는 중간 상태 반환:
            return Map.of("status", "Manager approval is required.");
        }

        Map<String, Object> payload = (Map<String, Object>) toolConfirmation.get().payload();
        int approvedDays = (int) payload.get("approved_days");
        approvedDays = Math.min(approvedDays, days);

        if (approvedDays == 0) {
            return Map.of("status", "The time off request is rejected.", "approved_days", 0);
        }

        return Map.of(
            "status", "ok",
            "approved_days", approvedDays
        );
    }
    ```

## REST API를 통한 원격 확인 {#remote-response}

에이전트 워크플로의 사람 확인을 위한 활성 사용자 인터페이스가 없는 경우 명령줄 인터페이스를 통해 또는 이메일이나 채팅 애플리케이션과 같은 다른 채널을 통해 확인을 처리할 수 있습니다. 도구 호출을 확인하려면 사용자 또는 호출 애플리케이션이 도구 확인 데이터가 포함된 `FunctionResponse` 이벤트를 전송해야 합니다.

ADK API 서버의 `/run` 또는 `/run_sse` 엔드포인트로 요청을 보내거나 ADK 러너로 직접 보낼 수 있습니다. 다음 예시는 `curl` 명령을 사용하여 `/run_sse` 엔드포인트로 확인을 보냅니다:

```bash
 curl -X POST http://localhost:8000/run_sse \
 -H "Content-Type: application/json" \
 -d '{
    "app_name": "human_tool_confirmation",
    "user_id": "user",
    "session_id": "7828f575-2402-489f-8079-74ea95b6a300",
    "new_message": {
        "parts": [
            {
                "function_response": {
                    "id": "adk-13b84a8c-c95c-4d66-b006-d72b30447e35",
                    "name": "adk_request_confirmation",
                    "response": {
                        "confirmed": true,
                        "payload": {
                            "approved_days": 5
                        }
                    }
                }
            }
        ],
        "role": "user"
    }
}'
```

확인을 위한 REST 기반 응답은 다음 요구사항을 충족해야 합니다:

-   `function_response`의 `id`는 `adk_request_confirmation` `FunctionCall` 이벤트의 `function_call_id`와 일치해야 합니다.
-   `name`은 `adk_request_confirmation`이어야 합니다.
-   `response` 객체에는 `confirmed` 상태와 추가 `payload` 데이터가 포함됩니다.

    !!! note "참고: 재개(Resume) 기능과 함께 확인 사용"

        ADK 에이전트 워크플로가 [Resume](/runtime/resume/) 기능으로 구성된 경우 확인 응답과 함께 호출 ID(`invocation_id`) 매개변수도 포함해야 합니다. 제공하는 호출 ID는 확인 요청을 생성한 것과 동일한 호출이어야 하며, 그렇지 않으면 시스템이 확인 응답으로 새 호출을 시작합니다. 에이전트가 재개 기능을 사용하는 경우 응답에 포함될 수 있도록 확인 요청에 호출 ID를 매개변수로 포함하는 것을 고려하세요. 재개 기능 사용에 대한 자세한 내용은 [중단된 에이전트 재개](/runtime/resume/)를 참고하세요.

## 알려진 제한사항 {#known-limitations}

도구 확인 기능에는 다음과 같은 제한사항이 있습니다:

-   [DatabaseSessionService](/api-reference/python/google-adk.html#google.adk.sessions.DatabaseSessionService)는 이 기능에서 지원되지 않습니다.
-   [VertexAiSessionService](/api-reference/python/google-adk.html#google.adk.sessions.VertexAiSessionService)는 이 기능에서 지원되지 않습니다.

## 다음 단계

에이전트 워크플로용 ADK 도구 빌드에 대한 자세한 내용은 [함수 도구](/tools-custom/function-tools/)를 참고하세요.
