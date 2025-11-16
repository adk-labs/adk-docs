# 이벤트

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

이벤트는 에이전트 개발 키트(ADK) 내 정보 흐름의 기본 단위입니다. 이벤트는 초기 사용자 입력부터 최종 응답 및 그 사이의 모든 단계에 이르기까지, 에이전트의 상호작용 라이프사이클 동안 발생하는 모든 중요한 발생을 나타냅니다. 이벤트를 이해하는 것은 구성 요소가 통신하고, 상태를 관리하며, 제어 흐름을 지시하는 주요 방법이기 때문에 매우 중요합니다.

## 이벤트란 무엇이며 왜 중요한가

ADK에서 `Event`는 에이전트 실행의 특정 시점을 나타내는 불변의 기록입니다. 사용자 메시지, 에이전트 응답, 도구 사용 요청(함수 호출), 도구 결과, 상태 변경, 제어 신호 및 오류를 캡처합니다.

=== "Python"
    기술적으로 이는 `google.adk.events.Event` 클래스의 인스턴스로, 기본 `LlmResponse` 구조 위에 필수적인 ADK 관련 메타데이터와 `actions` 페이로드를 추가하여 구축됩니다.

    ```python
    # 이벤트의 개념적 구조 (Python)
    # from google.adk.events import Event, EventActions
    # from google.genai import types

    # class Event(LlmResponse): # 단순화된 보기
    #     # --- LlmResponse 필드 ---
    #     content: Optional[types.Content]
    #     partial: Optional[bool]
    #     # ... 기타 응답 필드 ...

    #     # --- ADK 특정 추가 사항 ---
    #     author: str          # 'user' 또는 에이전트 이름
    #     invocation_id: str   # 전체 상호작용 실행 ID
    #     id: str              # 이 특정 이벤트의 고유 ID
    #     timestamp: float     # 생성 시간
    #     actions: EventActions # 부수 효과 및 제어에 중요
    #     branch: Optional[str] # 계층 구조 경로
    #     # ...
    ```

=== "Go"
    Go에서는 `google.golang.org/adk/session.Event` 타입의 구조체입니다.

    ```go
    // 이벤트의 개념적 구조 (Go - session/session.go 참조)
    // session.Event 구조체를 기반으로 한 단순화된 보기
    type Event struct {
        // --- 내장된 model.LLMResponse의 필드 ---
        model.LLMResponse

        // --- ADK 특정 추가 사항 ---
        Author       string         // 'user' 또는 에이전트 이름
        InvocationID string         // 전체 상호작용 실행 ID
        ID           string         // 이 특정 이벤트의 고유 ID
        Timestamp    time.Time      // 생성 시간
        Actions      EventActions   // 부수 효과 및 제어에 중요
        Branch       string         // 계층 구조 경로
        // ... 기타 필드
    }

    // model.LLMResponse는 Content 필드를 포함
    type LLMResponse struct {
        Content *genai.Content
        // ... 기타 필드
    }
    ```

=== "Java"
    Java에서는 `com.google.adk.events.Event` 클래스의 인스턴스입니다. 이 역시 기본 응답 구조 위에 필수적인 ADK 관련 메타데이터와 `actions` 페이로드를 추가하여 구축됩니다.

    ```java
    // 이벤트의 개념적 구조 (Java - com.google.adk.events.Event.java 참조)
    // 제공된 com.google.adk.events.Event.java를 기반으로 한 단순화된 보기
    // public class Event extends JsonBaseModel {
    //     // --- LlmResponse에 상응하는 필드 ---
    //     private Optional<Content> content;
    //     private Optional<Boolean> partial;
    //     // ... errorCode, errorMessage 같은 기타 응답 필드 ...

    //     // --- ADK 특정 추가 사항 ---
    //     private String author;         // 'user' 또는 에이전트 이름
    //     private String invocationId;   // 전체 상호작용 실행 ID
    //     private String id;             // 이 특정 이벤트의 고유 ID
    //     private long timestamp;        // 생성 시간 (epoch 밀리초)
    //     private EventActions actions;  // 부수 효과 및 제어에 중요
    //     private Optional<String> branch; // 계층 구조 경로
    //     // ... turnComplete, longRunningToolIds 같은 기타 필드 ...
    // }
    ```

이벤트는 다음과 같은 몇 가지 주요 이유로 ADK 운영의 중심에 있습니다:

1.  **통신:** 사용자 인터페이스, `Runner`, 에이전트, LLM, 도구 간의 표준 메시지 형식 역할을 합니다. 모든 것이 `Event`로 흐릅니다.

2.  **상태 및 아티팩트 변경 신호:** 이벤트는 상태 수정을 위한 지침을 전달하고 아티팩트 업데이트를 추적합니다. `SessionService`는 이러한 신호를 사용하여 영속성을 보장합니다. Python에서는 `event.actions.state_delta` 및 `event.actions.artifact_delta`를 통해 변경 사항을 신호합니다.

3.  **제어 흐름:** `event.actions.transfer_to_agent` 또는 `event.actions.escalate`와 같은 특정 필드는 프레임워크를 지시하는 신호 역할을 하여, 다음에 실행할 에이전트나 루프 종료 여부를 결정합니다.

4.  **기록 및 관찰 가능성:** `session.events`에 기록된 이벤트 시퀀스는 상호작용의 완전하고 시간순으로 정리된 기록을 제공하여 디버깅, 감사 및 에이전트 행동을 단계별로 이해하는 데 매우 유용합니다.

본질적으로, 사용자 쿼리부터 에이전트의 최종 답변까지의 전체 프로세스는 `Event` 객체의 생성, 해석, 처리를 통해 조율됩니다.

## 이벤트 이해 및 사용하기

개발자로서 여러분은 주로 `Runner`가 생성하는 이벤트 스트림과 상호작용하게 됩니다. 이벤트를 이해하고 정보를 추출하는 방법은 다음과 같습니다:

!!! 참고
    기본 요소에 대한 특정 매개변수나 메서드 이름은 SDK 언어에 따라 약간 다를 수 있습니다(예: Python의 `event.content()`, Java의 `event.content().get().parts()`). 자세한 내용은 언어별 API 문서를 참조하세요.

### 이벤트 출처 및 유형 식별하기

다음을 확인하여 이벤트가 무엇을 나타내는지 빠르게 파악할 수 있습니다:

*   **누가 보냈는가? (`event.author`)**
    *   `'user'`: 최종 사용자로부터 직접 온 입력을 나타냅니다.
    *   `'AgentName'`: 특정 에이전트(예: `'WeatherAgent'`, `'SummarizerAgent'`)의 출력 또는 작업을 나타냅니다.
*   **주요 페이로드는 무엇인가? (`event.content` 및 `event.content.parts`)**
    *   **텍스트:** 대화 메시지를 나타냅니다. Python의 경우 `event.content.parts[0].text`가 있는지 확인합니다. Java의 경우 `event.content()`가 있고, `parts()`가 있으며 비어 있지 않고, 첫 번째 파트의 `text()`가 있는지 확인합니다.
    *   **도구 호출 요청:** `event.get_function_calls()`를 확인합니다. 비어 있지 않으면 LLM이 하나 이상의 도구 실행을 요청하는 것입니다. 목록의 각 항목에는 `.name`과 `.args`가 있습니다.
    *   **도구 결과:** `event.get_function_responses()`를 확인합니다. 비어 있지 않으면 이 이벤트는 도구 실행의 결과를 담고 있습니다. 각 항목에는 `.name`과 `.response`(도구가 반환한 딕셔너리)가 있습니다. *참고:* 기록 구조화를 위해 `content` 내부의 `role`은 종종 `'user'`이지만, 이벤트 `author`는 일반적으로 도구 호출을 요청한 에이전트입니다.

*   **스트리밍 출력인가? (`event.partial`)**
    이것이 LLM에서 온 불완전한 텍스트 덩어리인지 여부를 나타냅니다.
    *   `True`: 더 많은 텍스트가 이어집니다.
    *   `False` 또는 `None`/`Optional.empty()`: 콘텐츠의 이 부분은 완료되었습니다 (단, `turn_complete`가 false인 경우 전체 턴이 끝나지 않았을 수 있습니다).

=== "Python"

    ```python
    # 의사 코드: 기본 이벤트 식별 (Python)
    # async for event in runner.run_async(...):
    #     print(f"이벤트 출처: {event.author}")
    #
    #     if event.content and event.content.parts:
    #         if event.get_function_calls():
    #             print("  유형: 도구 호출 요청")
    #         elif event.get_function_responses():
    #             print("  유형: 도구 결과")
    #         elif event.content.parts[0].text:
    #             if event.partial:
    #                 print("  유형: 스트리밍 텍스트 청크")
    #             else:
    #                 print("  유형: 완전한 텍스트 메시지")
    #         else:
    #             print("  유형: 기타 콘텐츠 (예: 코드 결과)")
    #     elif event.actions and (event.actions.state_delta or event.actions.artifact_delta):
    #         print("  유형: 상태/아티팩트 업데이트")
    #     else:
    #         print("  유형: 제어 신호 또는 기타")
    ```

=== "Go"

    ```go
      // 의사 코드: 기본 이벤트 식별 (Go)
    import (
      "fmt"
      "google.golang.org/adk/session"
      "google.golang.org/genai"
    )

    func hasFunctionCalls(content *genai.Content) bool {
      if content == nil {
        return false
      }
      for _, part := range content.Parts {
        if part.FunctionCall != nil {
          return true
        }
      }
      return false
    }

    func hasFunctionResponses(content *genai.Content) bool {
      if content == nil {
        return false
      }
      for _, part := range content.Parts {
        if part.FunctionResponse != nil {
          return true
        }
      }
      return false
    }

    func processEvents(events <-chan *session.Event) {
      for event := range events {
        fmt.Printf("이벤트 출처: %s\n", event.Author)

        if event.LLMResponse != nil && event.LLMResponse.Content != nil {
          if hasFunctionCalls(event.LLMResponse.Content) {
            fmt.Println("  유형: 도구 호출 요청")
          } else if hasFunctionResponses(event.LLMResponse.Content) {
            fmt.Println("  유형: 도구 결과")
          } else if len(event.LLMResponse.Content.Parts) > 0 {
            if event.LLMResponse.Content.Parts[0].Text != "" {
              if event.LLMResponse.Partial {
                fmt.Println("  유형: 스트리밍 텍스트 청크")
              } else {
                fmt.Println("  유형: 완전한 텍스트 메시지")
              }
            } else {
              fmt.Println("  유형: 기타 콘텐츠 (예: 코드 결과)")
            }
          }
        } else if len(event.Actions.StateDelta) > 0 {
          fmt.Println("  유형: 상태 업데이트")
        } else {
          fmt.Println("  유형: 제어 신호 또는 기타")
        }
      }
    }
    ```

=== "Java"

    ```java
    // 의사 코드: 기본 이벤트 식별 (Java)
    // import com.google.genai.types.Content;
    // import com.google.adk.events.Event;
    // import com.google.adk.events.EventActions;

    // runner.runAsync(...).forEach(event -> { // 동기식 또는 리액티브 스트림을 가정
    //     System.out.println("이벤트 출처: " + event.author());
    //
    //     if (event.content().isPresent()) {
    //         Content content = event.content().get();
    //         if (!event.functionCalls().isEmpty()) {
    //             System.out.println("  유형: 도구 호출 요청");
    //         } else if (!event.functionResponses().isEmpty()) {
    //             System.out.println("  유형: 도구 결과");
    //         } else if (content.parts().isPresent() && !content.parts().get().isEmpty() &&
    //                    content.parts().get().get(0).text().isPresent()) {
    //             if (event.partial().orElse(false)) {
    //                 System.out.println("  유형: 스트리밍 텍스트 청크");
    //             } else {
    //                 System.out.println("  유형: 완전한 텍스트 메시지");
    //             }
    //         } else {
    //             System.out.println("  유형: 기타 콘텐츠 (예: 코드 결과)");
    //         }
    //     } else if (event.actions() != null &&
    //                ((event.actions().stateDelta() != null && !event.actions().stateDelta().isEmpty()) ||
    //                 (event.actions().artifactDelta() != null && !event.actions().artifactDelta().isEmpty()))) {
    //         System.out.println("  유형: 상태/아티팩트 업데이트");
    //     } else {
    //         System.out.println("  유형: 제어 신호 또는 기타");
    //     }
    // });
    ```

### 핵심 정보 추출하기

이벤트 유형을 파악했다면 관련 데이터에 접근합니다:

*   **텍스트 콘텐츠:**
    텍스트에 접근하기 전에 항상 콘텐츠와 파트가 있는지 확인하세요. Python에서는 `text = event.content.parts[0].text`입니다.

*   **함수 호출 세부 정보:**

    === "Python"
    
        ```python
        calls = event.get_function_calls()
        if calls:
            for call in calls:
                tool_name = call.name
                arguments = call.args # 보통 딕셔너리
                print(f"  도구: {tool_name}, 인수: {arguments}")
                # 애플리케이션은 이를 기반으로 실행을 디스패치할 수 있습니다
        ```

    === "Go"

        ```go
        import (
            "fmt"
            "google.golang.org/adk/session"
            "google.golang.org/genai"
        )

        func handleFunctionCalls(event *session.Event) {
            if event.LLMResponse == nil || event.LLMResponse.Content == nil {
                return
            }
            calls := event.Content.FunctionCalls()
            if len(calls) > 0 {
                for _, call := range calls {
                    toolName := call.Name
                    arguments := call.Args
                    fmt.Printf("  도구: %s, 인수: %v\n", toolName, arguments)
                    // 애플리케이션은 이를 기반으로 실행을 디스패치할 수 있습니다
                }
            }
        }
        ```

    === "Java"

        ```java
        import com.google.genai.types.FunctionCall;
        import com.google.common.collect.ImmutableList;
        import java.util.Map;

        ImmutableList<FunctionCall> calls = event.functionCalls(); // Event.java에서
        if (!calls.isEmpty()) {
          for (FunctionCall call : calls) {
            String toolName = call.name().get();
            // args는 Optional<Map<String, Object>>
            Map<String, Object> arguments = call.args().get();
                   System.out.println("  도구: " + toolName + ", 인수: " + arguments);
            // 애플리케이션은 이를 기반으로 실행을 디스패치할 수 있습니다
          }
        }
        ```

*   **함수 응답 세부 정보:**

    === "Python"

        ```python
        responses = event.get_function_responses()
        if responses:
            for response in responses:
                tool_name = response.name
                result_dict = response.response # 도구가 반환한 딕셔너리
                print(f"  도구 결과: {tool_name} -> {result_dict}")
        ```

    === "Go"

        ```go
        import (
            "fmt"
            "google.golang.org/adk/session"
            "google.golang.org/genai"
        )

        func handleFunctionResponses(event *session.Event) {
            if event.LLMResponse == nil || event.LLMResponse.Content == nil {
                return
            }
            responses := event.Content.FunctionResponses()
            if len(responses) > 0 {
                for _, response := range responses {
                    toolName := response.Name
                    result := response.Response
                    fmt.Printf("  도구 결과: %s -> %v\n", toolName, result)
                }
            }
        }
        ```

    === "Java"

        ```java
        import com.google.genai.types.FunctionResponse;
        import com.google.common.collect.ImmutableList;
        import java.util.Map;

        ImmutableList<FunctionResponse> responses = event.functionResponses(); // Event.java에서
        if (!responses.isEmpty()) {
            for (FunctionResponse response : responses) {
                String toolName = response.name().get();
                Map<String, String> result= response.response().get(); // 응답을 가져오기 전에 확인
                System.out.println("  도구 결과: " + toolName + " -> " + result);
            }
        }
        ```

*   **식별자:**
    *   `event.id`: 이 특정 이벤트 인스턴스의 고유 ID.
    *   `event.invocation_id`: 이 이벤트가 속한 전체 사용자-요청-최종-응답 사이클의 ID. 로깅 및 추적에 유용합니다.

### 액션 및 부수 효과 감지하기

`event.actions` 객체는 발생했거나 발생해야 할 변경 사항을 신호합니다. `event.actions` 및 그 필드/메서드에 접근하기 전에 항상 존재하는지 확인하세요.

*   **상태 변경:** 이 이벤트를 생성한 단계 동안 세션 상태에서 수정된 키-값 쌍의 컬렉션을 제공합니다.

    === "Python"
        `delta = event.actions.state_delta` (`{key: value}` 쌍의 딕셔너리).
        ```python
        if event.actions and event.actions.state_delta:
            print(f"  상태 변경: {event.actions.state_delta}")
            # 필요한 경우 로컬 UI 또는 애플리케이션 상태 업데이트
        ```
    === "Go"
        `delta := event.Actions.StateDelta` (`map[string]any`).
        ```go
        import (
            "fmt"
            "google.golang.org/adk/session"
        )

        func handleStateChanges(event *session.Event) {
            if len(event.Actions.StateDelta) > 0 {
                fmt.Printf("  상태 변경: %v\n", event.Actions.StateDelta)
                // 필요한 경우 로컬 UI 또는 애플리케이션 상태 업데이트
            }
        }
        ```

    === "Java"
        `ConcurrentMap<String, Object> delta = event.actions().stateDelta();`

        ```java
        import java.util.concurrent.ConcurrentMap;
        import com.google.adk.events.EventActions;

        EventActions actions = event.actions(); // event.actions()가 null이 아니라고 가정
        if (actions != null && actions.stateDelta() != null && !actions.stateDelta().isEmpty()) {
            ConcurrentMap<String, Object> stateChanges = actions.stateDelta();
            System.out.println("  상태 변경: " + stateChanges);
            // 필요한 경우 로컬 UI 또는 애플리케이션 상태 업데이트
        }
        ```

*   **아티팩트 저장:** 어떤 아티팩트가 저장되었고 그들의 새 버전 번호(또는 관련 `Part` 정보)를 나타내는 컬렉션을 제공합니다.

    === "Python"
        `artifact_changes = event.actions.artifact_delta` (`{filename: version}`의 딕셔너리).
        ```python
        if event.actions and event.actions.artifact_delta:
            print(f"  저장된 아티팩트: {event.actions.artifact_delta}")
            # UI가 아티팩트 목록을 새로 고칠 수 있음
        ```

    === "Go"
        `artifactChanges := event.Actions.ArtifactDelta` (`map[string]artifact.Artifact`).
        ```go
        import (
            "fmt"
            "google.golang.org/adk/artifact"
            "google.golang.org/adk/session"
        )

        func handleArtifactChanges(event *session.Event) {
            if len(event.Actions.ArtifactDelta) > 0 {
                fmt.Printf("  저장된 아티팩트: %v\n", event.Actions.ArtifactDelta)
                // UI가 아티팩트 목록을 새로 고칠 수 있음
                // event.Actions.ArtifactDelta를 순회하여 파일명과 artifact.Artifact 세부 정보 가져오기
                for filename, art := range event.Actions.ArtifactDelta {
                    fmt.Printf("    파일명: %s, 버전: %d, MIME 타입: %s\n", filename, art.Version, art.MIMEType)
                }
            }
        }
        ```

    === "Java"
        `ConcurrentMap<String, Part> artifactChanges = event.actions().artifactDelta();`

        ```java
        import java.util.concurrent.ConcurrentMap;
        import com.google.genai.types.Part;
        import com.google.adk.events.EventActions;

        EventActions actions = event.actions(); // event.actions()가 null이 아니라고 가정
        if (actions != null && actions.artifactDelta() != null && !actions.artifactDelta().isEmpty()) {
            ConcurrentMap<String, Part> artifactChanges = actions.artifactDelta();
            System.out.println("  저장된 아티팩트: " + artifactChanges);
            // UI가 아티팩트 목록을 새로 고칠 수 있음
            // artifactChanges.entrySet()을 순회하여 파일명과 Part 세부 정보 가져오기
        }
        ```

*   **제어 흐름 신호:** 불리언 플래그나 문자열 값을 확인합니다:

    === "Python"
        *   `event.actions.transfer_to_agent` (string): 제어가 명명된 에이전트로 넘어가야 합니다.
        *   `event.actions.escalate` (bool): 루프가 종료되어야 합니다.
        *   `event.actions.skip_summarization` (bool): 도구 결과가 LLM에 의해 요약되어서는 안 됩니다.
        ```python
        if event.actions:
            if event.actions.transfer_to_agent:
                print(f"  신호: {event.actions.transfer_to_agent}로 제어 이전")
            if event.actions.escalate:
                print("  신호: 에스컬레이션 (루프 종료)")
            if event.actions.skip_summarization:
                print("  신호: 도구 결과 요약 건너뛰기")
        ```

    === "Go"
        *   `event.Actions.TransferToAgent` (string): 제어가 명명된 에이전트로 넘어가야 합니다.
        *   `event.Actions.Escalate` (bool): 루프가 종료되어야 합니다.
        *   `event.Actions.SkipSummarization` (bool): 도구 결과가 LLM에 의해 요약되어서는 안 됩니다.
        ```go
        import (
            "fmt"
            "google.golang.org/adk/session"
        )

        func handleControlFlow(event *session.Event) {
            if event.Actions.TransferToAgent != "" {
                fmt.Printf("  신호: %s로 제어 이전\n", event.Actions.TransferToAgent)
            }
            if event.Actions.Escalate {
                fmt.Println("  신호: 에스컬레이션 (루프 종료)")
            }
            if event.Actions.SkipSummarization {
                fmt.Println("  신호: 도구 결과 요약 건너뛰기")
            }
        }
        ```

    === "Java"
        *   `event.actions().transferToAgent()` (`Optional<String>` 반환): 제어가 명명된 에이전트로 넘어가야 합니다.
        *   `event.actions().escalate()` (`Optional<Boolean>` 반환): 루프가 종료되어야 합니다.
        *   `event.actions().skipSummarization()` (`Optional<Boolean>` 반환): 도구 결과가 LLM에 의해 요약되어서는 안 됩니다.

        ```java
        import com.google.adk.events.EventActions;
        import java.util.Optional;

        EventActions actions = event.actions(); // event.actions()가 null이 아니라고 가정
        if (actions != null) {
            Optional<String> transferAgent = actions.transferToAgent();
            if (transferAgent.isPresent()) {
                System.out.println("  신호: " + transferAgent.get() + "로 제어 이전");
            }

            Optional<Boolean> escalate = actions.escalate();
            if (escalate.orElse(false)) { // 또는 escalate.isPresent() && escalate.get()
                System.out.println("  신호: 에스컬레이션 (루프 종료)");
            }

            Optional<Boolean> skipSummarization = actions.skipSummarization();
            if (skipSummarization.orElse(false)) { // 또는 skipSummarization.isPresent() && skipSummarization.get()
                System.out.println("  신호: 도구 결과 요약 건너뛰기");
            }
        }
        ```

### 이벤트가 "최종" 응답인지 확인하기

내장된 헬퍼 메서드 `event.is_final_response()`를 사용하여 턴의 완전한 에이전트 출력으로 표시에 적합한 이벤트를 식별하세요.

*   **목적:** 최종 사용자 대면 메시지에서 중간 단계(도구 호출, 부분 스트리밍 텍스트, 내부 상태 업데이트 등)를 걸러냅니다.
*   **언제 `True`인가?**
    1.  이벤트에 도구 결과(`function_response`)가 포함되어 있고 `skip_summarization`이 `True`인 경우.
    2.  이벤트에 `is_long_running=True`로 표시된 도구에 대한 도구 호출(`function_call`)이 포함된 경우. Java에서는 `longRunningToolIds` 목록이 비어 있는지 확인합니다:
        *   `event.longRunningToolIds().isPresent() && !event.longRunningToolIds().get().isEmpty()`가 `true`인 경우.
    3.  또는, 다음 **모든** 조건이 충족될 경우:
        *   함수 호출이 없음 (`get_function_calls()`가 비어 있음).
        *   함수 응답이 없음 (`get_function_responses()`가 비어 있음).
        *   부분 스트림 청크가 아님 (`partial`이 `True`가 아님).
        *   추가 처리/표시가 필요할 수 있는 코드 실행 결과로 끝나지 않음.
*   **사용법:** 애플리케이션 로직에서 이벤트 스트림을 필터링합니다.

    === "Python"
        ```python
        # 의사 코드: 애플리케이션에서 최종 응답 처리하기 (Python)
        # full_response_text = ""
        # async for event in runner.run_async(...):
        #     # 필요한 경우 스트리밍 텍스트 누적...
        #     if event.partial and event.content and event.content.parts and event.content.parts[0].text:
        #         full_response_text += event.content.parts[0].text
        #
        #     # 표시 가능한 최종 이벤트인지 확인
        #     if event.is_final_response():
        #         print("\n--- 최종 출력 감지 ---")
        #         if event.content and event.content.parts and event.content.parts[0].text:
        #              # 스트림의 마지막 부분인 경우 누적된 텍스트 사용
        #              final_text = full_response_text + (event.content.parts[0].text if not event.partial else "")
        #              print(f"사용자에게 표시: {final_text.strip()}")
        #              full_response_text = "" # 누적기 리셋
        #         elif event.actions and event.actions.skip_summarization and event.get_function_responses():
        #              # 필요한 경우 원시 도구 결과 표시 처리
        #              response_data = event.get_function_responses()[0].response
        #              print(f"원시 도구 결과 표시: {response_data}")
        #         elif hasattr(event, 'long_running_tool_ids') and event.long_running_tool_ids:
        #              print("메시지 표시: 도구가 백그라운드에서 실행 중입니다...")
        #         else:
        #              # 해당되는 경우 다른 유형의 최종 응답 처리
        #              print("표시: 최종 비텍스트 응답 또는 신호.")
        ```

    === "Go"

        ```go
        // 의사 코드: 애플리케이션에서 최종 응답 처리하기 (Go)
        import (
            "fmt"
            "strings"
            "google.golang.org/adk/session"
            "google.golang.org/genai"
        )

        // isFinalResponse는 이벤트가 표시에 적합한 최종 응답인지 확인합니다.
        func isFinalResponse(event *session.Event) bool {
            if event.LLMResponse != nil {
                // 조건 1: 요약 건너뛰기가 있는 도구 결과.
                if event.LLMResponse.Content != nil && len(event.LLMResponse.Content.FunctionResponses()) > 0 && event.Actions.SkipSummarization {
                    return true
                }
                // 조건 2: 장기 실행 도구 호출.
                if len(event.LongRunningToolIDs) > 0 {
                    return true
                }
                // 조건 3: 도구 호출이나 응답이 없는 완전한 메시지.
                if (event.LLMResponse.Content == nil ||
                    (len(event.LLMResponse.Content.FunctionCalls()) == 0 && len(event.LLMResponse.Content.FunctionResponses()) == 0)) &&
                    !event.LLMResponse.Partial {
                    return true
                }
            }
            return false
        }

        func handleFinalResponses() {
            var fullResponseText strings.Builder
            // for event := range runner.Run(...) { // 예시 루프
            // 	// 필요한 경우 스트리밍 텍스트 누적...
            // 	if event.LLMResponse != nil && event.LLMResponse.Partial && event.LLMResponse.Content != nil {
            // 		if len(event.LLMResponse.Content.Parts) > 0 && event.LLMResponse.Content.Parts[0].Text != "" {
            // 			fullResponseText.WriteString(event.LLMResponse.Content.Parts[0].Text)
            // 		}
            // 	}
            //
            // 	// 표시 가능한 최종 이벤트인지 확인
            // 	if isFinalResponse(event) {
            // 		fmt.Println("\n--- 최종 출력 감지 ---")
            // 		if event.LLMResponse != nil && event.LLMResponse.Content != nil {
            // 			if len(event.LLMResponse.Content.Parts) > 0 && event.LLMResponse.Content.Parts[0].Text != "" {
            // 				// 스트림의 마지막 부분인 경우 누적된 텍스트 사용
            // 				finalText := fullResponseText.String()
            // 				if !event.LLMResponse.Partial {
            // 					finalText += event.LLMResponse.Content.Parts[0].Text
            // 				}
            // 				fmt.Printf("사용자에게 표시: %s\n", strings.TrimSpace(finalText))
            // 				fullResponseText.Reset() // 누적기 리셋
            // 			}
            // 		} else if event.Actions.SkipSummarization && event.LLMResponse.Content != nil && len(event.LLMResponse.Content.FunctionResponses()) > 0 {
            // 			// 필요한 경우 원시 도구 결과 표시 처리
            // 			responseData := event.LLMResponse.Content.FunctionResponses()[0].Response
            // 			fmt.Printf("원시 도구 결과 표시: %v\n", responseData)
            // 		} else if len(event.LongRunningToolIDs) > 0 {
            // 			fmt.Println("메시지 표시: 도구가 백그라운드에서 실행 중입니다...")
            // 		} else {
            // 			// 해당되는 경우 다른 유형의 최종 응답 처리
            // 			fmt.Println("표시: 최종 비텍스트 응답 또는 신호.")
            // 		}
            // 	}
            // }
        }
        ```

    === "Java"
        ```java
        // 의사 코드: 애플리케이션에서 최종 응답 처리하기 (Java)
        import com.google.adk.events.Event;
        import com.google.genai.types.Content;
        import com.google.genai.types.FunctionResponse;
        import java.util.Map;

        StringBuilder fullResponseText = new StringBuilder();
        runner.run(...).forEach(event -> { // 이벤트 스트림을 가정
             // 필요한 경우 스트리밍 텍스트 누적...
             if (event.partial().orElse(false) && event.content().isPresent()) {
                 event.content().flatMap(Content::parts).ifPresent(parts -> {
                     if (!parts.isEmpty() && parts.get(0).text().isPresent()) {
                         fullResponseText.append(parts.get(0).text().get());
                    }
                 });
             }

             // 표시 가능한 최종 이벤트인지 확인
             if (event.finalResponse()) { // Event.java의 메서드 사용
                 System.out.println("\n--- 최종 출력 감지 ---");
                 if (event.content().isPresent() &&
                     event.content().flatMap(Content::parts).map(parts -> !parts.isEmpty() && parts.get(0).text().isPresent()).orElse(false)) {
                     // 스트림의 마지막 부분인 경우 누적된 텍스트 사용
                     String eventText = event.content().get().parts().get().get(0).text().get();
                     String finalText = fullResponseText.toString() + (event.partial().orElse(false) ? "" : eventText);
                     System.out.println("사용자에게 표시: " + finalText.trim());
                     fullResponseText.setLength(0); // 누적기 리셋
                 } else if (event.actions() != null && event.actions().skipSummarization().orElse(false)
                            && !event.functionResponses().isEmpty()) {
                     // 필요한 경우 원시 도구 결과 표시 처리,
                     // 특히 finalResponse()가 다른 조건 때문에 true였거나
                     // finalResponse()와 관계없이 요약 건너뛰기 결과를 표시하고 싶을 때
                     Map<String, Object> responseData = event.functionResponses().get(0).response().get();
                     System.out.println("원시 도구 결과 표시: " + responseData);
                 } else if (event.longRunningToolIds().isPresent() && !event.longRunningToolIds().get().isEmpty()) {
                     // 이 경우는 event.finalResponse()에 의해 처리됨
                     System.out.println("메시지 표시: 도구가 백그라운드에서 실행 중입니다...");
                 } else {
                     // 해당되는 경우 다른 유형의 최종 응답 처리
                     System.out.println("표시: 최종 비텍스트 응답 또는 신호.");
                 }
             }
         });
        ```

이벤트의 이러한 측면을 주의 깊게 검토함으로써 ADK 시스템을 통해 흐르는 풍부한 정보에 적절하게 반응하는 견고한 애플리케이션을 구축할 수 있습니다.

## 이벤트 흐름: 생성 및 처리

이벤트는 다른 시점에서 생성되고 프레임워크에 의해 체계적으로 처리됩니다. 이 흐름을 이해하면 작업과 기록이 어떻게 관리되는지 명확히 하는 데 도움이 됩니다.

*   **생성 소스:**
    *   **사용자 입력:** `Runner`는 일반적으로 초기 사용자 메시지나 대화 중간 입력을 `author='user'`로 설정하여 `Event`로 래핑합니다.
    *   **에이전트 로직:** 에이전트(`BaseAgent`, `LlmAgent`)는 응답을 전달하거나 작업을 신호하기 위해 명시적으로 `yield Event(...)` 객체(`author=self.name`으로 설정)를 생성합니다.
    *   **LLM 응답:** ADK 모델 통합 계층은 원시 LLM 출력(텍스트, 함수 호출, 오류)을 호출 에이전트가 작성한 `Event` 객체로 변환합니다.
    *   **도구 결과:** 도구가 실행된 후 프레임워크는 `function_response`를 포함하는 `Event`를 생성합니다. `author`는 일반적으로 도구를 요청한 에이전트이며, `content` 내부의 `role`은 LLM 기록을 위해 `'user'`로 설정됩니다.

*   **처리 흐름:**
    1.  **생성/반환:** 이벤트가 소스에 의해 생성되어 `yield`(Python)되거나 반환/방출(Java)됩니다.
    2.  **러너 수신:** 에이전트를 실행하는 메인 `Runner`가 이벤트를 받습니다.
    3.  **SessionService 처리:** `Runner`는 이벤트를 구성된 `SessionService`로 보냅니다. 이는 중요한 단계입니다:
        *   **델타 적용:** 서비스는 `event.actions.state_delta`를 `session.state`에 병합하고 `event.actions.artifact_delta`를 기반으로 내부 기록을 업데이트합니다. (참고: 실제 아티팩트 *저장*은 보통 `context.save_artifact`가 호출될 때 더 일찍 발생했습니다).
        *   **메타데이터 최종화:** 없는 경우 고유한 `event.id`를 할당하고, `event.timestamp`를 업데이트할 수 있습니다.
        *   **기록에 영속화:** 처리된 이벤트를 `session.events` 목록에 추가합니다.
    4.  **외부로 생성:** `Runner`는 처리된 이벤트를 호출 애플리케이션(예: `runner.run_async`를 호출한 코드)으로 `yield`(Python)하거나 반환/방출(Java)합니다.

이 흐름은 상태 변경과 기록이 각 이벤트의 통신 내용과 함께 일관되게 기록되도록 보장합니다.

## 일반적인 이벤트 예시 (설명 패턴)

스트림에서 볼 수 있는 일반적인 이벤트의 간결한 예시는 다음과 같습니다:

*   **사용자 입력:**
    ```json
    {
      "author": "user",
      "invocation_id": "e-xyz...",
      "content": {"parts": [{"text": "다음 주 화요일 런던행 비행편 예약해 줘"}]}
      // actions는 보통 비어 있음
    }
    ```
*   **에이전트 최종 텍스트 응답:** (`is_final_response() == True`)
    ```json
    {
      "author": "TravelAgent",
      "invocation_id": "e-xyz...",
      "content": {"parts": [{"text": "네, 도와드릴 수 있습니다. 출발 도시를 확인해 주시겠어요?"}]},
      "partial": false,
      "turn_complete": true
      // actions에 상태 델타 등이 있을 수 있음
    }
    ```
*   **에이전트 스트리밍 텍스트 응답:** (`is_final_response() == False`)
    ```json
    {
      "author": "SummaryAgent",
      "invocation_id": "e-abc...",
      "content": {"parts": [{"text": "이 문서는 세 가지 주요 사항을 논의합니다:"}]},
      "partial": true,
      "turn_complete": false
    }
    // ... 더 많은 partial=True 이벤트가 이어짐 ...
    ```
*   **도구 호출 요청 (LLM에 의해):** (`is_final_response() == False`)
    ```json
    {
      "author": "TravelAgent",
      "invocation_id": "e-xyz...",
      "content": {"parts": [{"function_call": {"name": "find_airports", "args": {"city": "London"}}}]}
      // actions는 보통 비어 있음
    }
    ```
*   **도구 결과 제공 (LLM에게):** (`is_final_response()`는 `skip_summarization`에 따라 다름)
    ```json
    {
      "author": "TravelAgent", // 작성자는 호출을 요청한 에이전트
      "invocation_id": "e-xyz...",
      "content": {
        "role": "user", // LLM 기록을 위한 역할
        "parts": [{"function_response": {"name": "find_airports", "response": {"result": ["LHR", "LGW", "STN"]}}}]
      }
      // actions에 skip_summarization=True가 있을 수 있음
    }
    ```
*   **상태/아티팩트 업데이트만:** (`is_final_response() == False`)
    ```json
    {
      "author": "InternalUpdater",
      "invocation_id": "e-def...",
      "content": null,
      "actions": {
        "state_delta": {"user_status": "verified"},
        "artifact_delta": {"verification_doc.pdf": 2}
      }
    }
    ```
*   **에이전트 이전 신호:** (`is_final_response() == False`)
    ```json
    {
      "author": "OrchestratorAgent",
      "invocation_id": "e-789...",
      "content": {"parts": [{"function_call": {"name": "transfer_to_agent", "args": {"agent_name": "BillingAgent"}}}]},
      "actions": {"transfer_to_agent": "BillingAgent"} // 프레임워크에 의해 추가됨
    }
    ```
*   **루프 에스컬레이션 신호:** (`is_final_response() == False`)
    ```json
    {
      "author": "CheckerAgent",
      "invocation_id": "e-loop...",
      "content": {"parts": [{"text": "최대 재시도 횟수에 도달했습니다."}]}, // 선택적 콘텐츠
      "actions": {"escalate": true}
    }
    ```

## 추가 컨텍스트 및 이벤트 세부 정보

핵심 개념 외에, 특정 사용 사례에 중요한 컨텍스트 및 이벤트에 대한 몇 가지 세부 정보는 다음과 같습니다:

1.  **`ToolContext.function_call_id` (도구 작업 연결):**
    *   LLM이 도구(FunctionCall)를 요청할 때 해당 요청에는 ID가 있습니다. 도구 함수에 제공된 `ToolContext`에는 이 `function_call_id`가 포함됩니다.
    *   **중요성:** 이 ID는 인증과 같은 작업을 시작한 특정 도구 요청에 다시 연결하는 데 중요하며, 특히 한 턴에 여러 도구가 호출될 때 더욱 그렇습니다. 프레임워크는 이 ID를 내부적으로 사용합니다.

2.  **상태/아티팩트 변경 기록 방식:**
    *   `CallbackContext` 또는 `ToolContext`를 사용하여 상태를 수정하거나 아티팩트를 저장할 때 이러한 변경 사항은 영구 저장소에 즉시 기록되지 않습니다.
    *   대신, `EventActions` 객체 내의 `state_delta` 및 `artifact_delta` 필드를 채웁니다.
    *   이 `EventActions` 객체는 변경 후 생성된 *다음 이벤트*(예: 에이전트의 응답 또는 도구 결과 이벤트)에 첨부됩니다.
    *   `SessionService.append_event` 메서드는 들어오는 이벤트에서 이러한 델타를 읽어 세션의 영구 상태 및 아티팩트 기록에 적용합니다. 이는 변경 사항이 이벤트 스트림에 시간순으로 연결되도록 보장합니다.

3.  **상태 범위 접두사 (`app:`, `user:`, `temp:`):**
    *   `context.state`를 통해 상태를 관리할 때 선택적으로 접두사를 사용할 수 있습니다:
        *   `app:my_setting`: 전체 애플리케이션과 관련된 상태를 제안합니다 (영구적인 `SessionService` 필요).
        *   `user:user_preference`: 여러 세션에 걸쳐 특정 사용자와 관련된 상태를 제안합니다 (영구적인 `SessionService` 필요).
        *   `temp:intermediate_result` 또는 접두사 없음: 일반적으로 현재 호출에 대한 세션별 또는 임시 상태입니다.
    *   기본 `SessionService`가 영속성을 위해 이러한 접두사를 처리하는 방법을 결정합니다.

4.  **오류 이벤트:**
    *   `Event`는 오류를 나타낼 수 있습니다. `event.error_code` 및 `event.error_message` 필드(`LlmResponse`에서 상속됨)를 확인하세요.
    *   오류는 LLM(예: 안전 필터, 리소스 제한)에서 발생하거나, 도구가 심각하게 실패할 경우 프레임워크에 의해 패키징될 수 있습니다. 일반적인 도구별 오류는 도구 `FunctionResponse` 콘텐츠를 확인하세요.
    ```json
    // 예시 오류 이벤트 (개념적)
    {
      "author": "LLMAgent",
      "invocation_id": "e-err...",
      "content": null,
      "error_code": "SAFETY_FILTER_TRIGGERED",
      "error_message": "안전 설정으로 인해 응답이 차단되었습니다.",
      "actions": {}
    }
    ```

이러한 세부 정보는 도구 인증, 상태 영속성 범위, 이벤트 스트림 내 오류 처리를 포함하는 고급 사용 사례에 대한 더 완전한 그림을 제공합니다.

## 이벤트 작업 모범 사례

ADK 애플리케이션에서 이벤트를 효과적으로 사용하려면 다음을 따르세요:

*   **명확한 작성자:** 커스텀 에이전트를 구축할 때 기록에서 에이전트 작업에 대한 정확한 귀속을 보장하세요. 프레임워크는 일반적으로 LLM/도구 이벤트에 대한 작성자를 올바르게 처리합니다.

    === "Python"
        `BaseAgent` 하위 클래스에서 `yield Event(author=self.name, ...)`를 사용하세요.

    === "Go"
        커스텀 에이전트 `Run` 메서드에서 프레임워크가 일반적으로 작성자를 처리합니다. 이벤트를 수동으로 생성하는 경우 작성자를 설정하세요: `yield(&session.Event{Author: a.name, ...}, nil)`

    === "Java"
        커스텀 에이전트 로직에서 `Event`를 구성할 때 작성자를 설정하세요. 예: `Event.builder().author(this.getAgentName()) // ... .build();`

*   **의미 있는 콘텐츠 및 액션:** 핵심 메시지/데이터(텍스트, 함수 호출/응답)에는 `event.content`를 사용하세요. 부수 효과(상태/아티팩트 델타)나 제어 흐름(`transfer`, `escalate`, `skip_summarization`)을 신호하는 데는 `event.actions`를 구체적으로 사용하세요.
*   **멱등성 인식:** `SessionService`가 `event.actions`에 신호된 상태/아티팩트 변경을 적용할 책임이 있음을 이해하세요. ADK 서비스는 일관성을 목표로 하지만, 애플리케이션 로직이 이벤트를 재처리할 경우 잠재적인 다운스트림 효과를 고려하세요.
*   **`is_final_response()` 사용:** 애플리케이션/UI 계층에서 이 헬퍼 메서드를 사용하여 완전하고 사용자 대면 텍스트 응답을 식별하세요. 수동으로 그 로직을 복제하지 마세요.
*   **기록 활용:** 세션의 이벤트 목록은 주요 디버깅 도구입니다. 작성자, 콘텐츠, 액션의 순서를 검토하여 실행을 추적하고 문제를 진단하세요.
*   **메타데이터 사용:** `invocation_id`를 사용하여 단일 사용자 상호작용 내의 모든 이벤트를 상호 연관시키세요. `event.id`를 사용하여 특정하고 고유한 발생을 참조하세요.

이벤트를 콘텐츠와 액션에 대한 명확한 목적을 가진 구조화된 메시지로 취급하는 것이 ADK에서 복잡한 에이전트 행동을 구축, 디버깅 및 관리하는 핵심입니다.