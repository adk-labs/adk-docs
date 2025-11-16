# ADK용 커스텀 도구

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

ADK 에이전트 워크플로에서 도구(Tools)는 구조화된 입력/출력을 가진 프로그래밍 함수로, ADK 에이전트가 작업을 수행하기 위해 호출할 수 있는 기능입니다. ADK 도구는 Gemini 등 생성형 AI 모델의 [함수 호출(Function Call)](https://ai.google.dev/gemini-api/docs/function-calling)과 유사하게 동작합니다. ADK 도구를 사용하면 다음과 같은 다양한 작업과 프로그래밍 기능을 수행할 수 있습니다:

*   데이터베이스 질의
*   API 요청 실행: 날씨 데이터 조회, 예약 시스템 등
*   웹 검색
*   코드 스니펫 실행
*   문서에서 정보 검색(RAG)
*   기타 소프트웨어나 서비스와의 상호작용

!!! tip "[ADK Tools list](/adk-docs/tools/)"
    자체 도구를 만들기 전에 **[ADK Tools list](/adk-docs/tools/)**에서 ADK 에이전트와 함께 사용할 수 있는 미리 빌드된 도구를 확인하세요.

## 도구란 무엇인가

ADK의 맥락에서 도구는 AI 에이전트에게 제공되는 특정 기능으로, 핵심적인 텍스트 생성 및 추론 능력을 넘어 외부와 상호작용하고 행동을 수행할 수 있게 합니다. 유능한 에이전트가 기본적인 언어 모델과 구별되는 점은 종종 효과적인 도구 사용에 있습니다.

기술적으로 도구는 보통 모듈화된 코드 컴포넌트—**Python/Java 함수**, 클래스 메서드, 또는 다른 특화된 에이전트—로, 미리 정의된 특정 작업을 수행하도록 설계됩니다. 이러한 작업은 외부 시스템이나 데이터와의 상호작용을 포함하는 경우가 많습니다.

<img src="../assets/agent-tool-call.png" alt="Agent tool call">

### 주요 특징

**액션 지향:** 도구는 정보 검색, API 호출, 계산 등 에이전트를 위한 특정 작업을 수행합니다.

**에이전트 능력 확장:** 도구를 통해 에이전트는 실시간 정보에 접근하거나 외부 시스템에 영향을 미칠 수 있어, 훈련 데이터만으로는 충족할 수 없는 지식의 한계를 보완합니다.

**사전 정의된 로직 실행:** 중요한 점은, 도구는 개발자가 정의한 특정 로직을 실행한다는 것입니다. 도구 자체는 에이전트의 핵심 대규모 언어 모델(LLM)과 같은 독립적 추론 능력을 갖지 않습니다. LLM이 어떤 도구를 언제, 어떤 입력으로 사용해야 할지 추론하지만, 도구 자체는 지정된 함수를 실행할 뿐입니다.

## 에이전트가 도구를 사용하는 방법

에이전트는 종종 함수 호출과 관련된 메커니즘을 통해 동적으로 도구를 활용합니다. 이 과정은 일반적으로 다음 단계를 따릅니다:

1. **추론:** 에이전트의 LLM이 시스템 지침, 대화 기록, 사용자 요청을 분석합니다.
2. **선택:** 분석을 바탕으로, LLM은 에이전트에게 가용한 도구와 각 도구를 설명하는 도크스트링을 기반으로 어떤 도구를 실행할지 결정합니다.
3. **호출:** LLM이 선택한 도구에 필요한 인수(입력)를 생성하고 실행을 트리거합니다.
4. **관찰:** 에이전트가 도구로부터 반환된 출력(결과)을 수신합니다.
5. **최종화:** 에이전트는 도구의 출력을 지속적인 추론 과정에 통합하여 다음 응답을 생성하거나, 다음 단계를 결정하거나, 목표가 달성되었는지 판단합니다.

도구를 에이전트의 지능적 코어(LLM)가 복잡한 작업을 완수하기 위해 필요에 따라 접근하고 활용할 수 있는 특화된 도구 상자로 생각할 수 있습니다.

## ADK의 도구 유형

ADK는 여러 유형의 도구를 지원하여 유연성을 제공합니다:

1. **[함수 도구(Function Tools)](../tools/function-tools.md):** 특정 애플리케이션의 요구에 맞춰 개발자가 직접 만드는 도구.
    * **[함수/메서드](../tools/function-tools.md#1-function-tool):** 코드에서 표준 동기 함수나 메서드(예: Python `def`)를 정의합니다.
    * **[도구로서의 에이전트(Agents-as-Tools)](../tools/function-tools.md#3-agent-as-a-tool):** 다른 (잠재적으로 특화된) 에이전트를 부모 에이전트의 도구로 사용합니다.
    * **[장기 실행 함수 도구(Long Running Function Tools)](../tools/function-tools.md#2-long-running-function-tool):** 비동기 작업이나 완료에 상당한 시간이 걸리는 도구를 지원합니다.
2. **[내장 도구(Built-in Tools)](../tools/built-in-tools.md):** 프레임워크가 일반적인 작업을 위해 제공하는 즉시 사용 가능한 도구.
        예시: Google 검색, 코드 실행, 검색 증강 생성(RAG).
3. **서드파티 도구(Third-Party Tools):** 널리 사용되는 외부 라이브러리의 도구를 원활하게 통합합니다.

각 도구 유형에 대한 자세한 정보와 예시는 위 링크된 각 문서 페이지를 참조하세요.

## 에이전트 지침에서 도구 참조하기

에이전트의 지침 내에서 **함수 이름**을 사용하여 도구를 직접 참조할 수 있습니다. 도구의 **함수 이름**과 **도크스트링**이 충분히 설명적이라면, 지침은 주로 **대규모 언어 모델(LLM)이 언제 해당 도구를 사용해야 하는지**에 초점을 맞출 수 있습니다. 이는 모델이 각 도구의 의도된 사용법을 이해하는 데 도움이 됩니다.

도구가 생성할 수 있는 **다양한 반환 값에 대해 에이전트가 어떻게 처리해야 하는지 명확하게 지시하는 것이 매우 중요합니다**. 예를 들어, 도구가 에러 메시지를 반환하는 경우, 에이전트가 작업을 재시도해야 하는지, 작업을 포기해야 하는지, 또는 사용자에게 추가 정보를 요청해야 하는지를 지침에 명시해야 합니다.

또한, ADK는 한 도구의 출력이 다른 도구의 입력이 될 수 있는 순차적인 도구 사용을 지원합니다. 이러한 워크플로를 구현할 때는, 모델이 필요한 단계를 거치도록 에이전트 지침 내에서 **의도된 도구 사용 순서를 설명**하는 것이 중요합니다.

### 예시

다음 예제는 에이전트가 **지침에서 함수 이름을 참조하여** 도구를 사용하는 방법을 보여줍니다. 또한 성공 또는 에러 메시지와 같은 **도구의 다양한 반환 값을 처리하도록** 에이전트를 안내하고, 작업을 완수하기 위해 **여러 도구를 순차적으로 사용**하도록 조율하는 방법을 보여줍니다.

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/overview/weather_sentiment.py"
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/tools-custom/weather_sentiment/main.go"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/tools/WeatherSentimentAgentApp.java:full_code"
    ```

## 도구 컨텍스트(Tool Context)

더 고급 시나리오를 위해, ADK는 특별한 `tool_context: ToolContext` 매개변수를 포함하여 도구 함수 내에서 추가적인 컨텍스트 정보에 접근할 수 있게 합니다. 함수 시그니처에 이를 포함하면, 에이전트 실행 중에 도구가 호출될 때 ADK가 **자동으로** **ToolContext** 클래스의 **인스턴스를 제공**합니다.

**ToolContext**는 다음과 같은 몇 가지 주요 정보와 제어 수단에 대한 접근을 제공합니다:

* `state: State`: 현재 세션의 상태를 읽고 수정합니다. 여기서 변경된 내용은 추적되고 영속화됩니다.

* `actions: EventActions`: 도구가 실행된 후 에이전트의 후속 조치에 영향을 줍니다 (예: 요약 건너뛰기, 다른 에이전트로 전환).

* `function_call_id: str`: 프레임워크가 이 특정 도구 호출에 할당한 고유 식별자입니다. 인증 응답과의 추적 및 연관에 유용합니다. 이는 단일 모델 응답 내에서 여러 도구가 호출될 때도 도움이 될 수 있습니다.

* `function_call_event_id: str`: 이 속성은 현재 도구 호출을 트리거한 **이벤트**의 고유 식별자를 제공합니다. 이는 추적 및 로깅 목적으로 유용할 수 있습니다.

* `auth_response: Any`: 이 도구가 호출되기 전에 인증 흐름이 완료된 경우 인증 응답/자격증명을 포함합니다.

* 서비스 접근: Artifacts 및 Memory와 같은 구성된 서비스와 상호작용하는 메서드.

`tool_context` 매개변수는 도구 함수 도크스트링에 포함하지 않아야 합니다. `ToolContext`는 LLM이 도구 함수를 호출하기로 결정한 *후에* ADK 프레임워크에 의해 자동으로 주입되므로, LLM의 의사 결정과 관련이 없으며 이를 포함하면 LLM을 혼란스럽게 할 수 있습니다.

### **상태 관리(State Management)**

`tool_context.state` 속성은 현재 세션과 관련된 상태에 대한 직접적인 읽기 및 쓰기 접근을 제공합니다. 이는 딕셔너리처럼 동작하지만, 모든 수정 사항이 델타로 추적되고 세션 서비스에 의해 영속화되도록 보장합니다. 이를 통해 도구는 여러 상호작용과 에이전트 단계를 거쳐 정보를 유지하고 공유할 수 있습니다.

* **상태 읽기**: 표준 딕셔너리 접근(`tool_context.state['my_key']`) 또는 `.get()` 메서드(`tool_context.state.get('my_key', default_value)`)를 사용합니다.

* **상태 쓰기**: 값을 직접 할당합니다(`tool_context.state['new_key'] = 'new_value'`). 이러한 변경 사항은 결과 이벤트의 state_delta에 기록됩니다.

* **상태 접두사**: 표준 상태 접두사를 기억하세요:

    * `app:*`: 애플리케이션의 모든 사용자 간에 공유됩니다.

    * `user:*`: 현재 사용자의 모든 세션에 걸쳐 특정됩니다.

    * (접두사 없음): 현재 세션에만 특정됩니다.

    * `temp:*`: 임시적이며, 호출 간에 영속화되지 않습니다 (단일 `run` 호출 내에서 데이터 전달에 유용하지만, LLM 호출 사이에 작동하는 도구 컨텍스트 내에서는 일반적으로 덜 유용합니다).

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/overview/user_preference.py"
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/tools-custom/user_preference/user_preference.go:example"
    ```

=== "Java"

    ```java
    import com.google.adk.tools.FunctionTool;
    import com.google.adk.tools.ToolContext;

    // 사용자별 선호도를 업데이트합니다.
    public Map<String, String> updateUserThemePreference(String value, ToolContext toolContext) {
      String userPrefsKey = "user:preferences:theme";

      // 현재 선호도를 가져오거나 존재하지 않으면 초기화합니다.
      String preference = toolContext.state().getOrDefault(userPrefsKey, "").toString();
      if (preference.isEmpty()) {
        preference = value;
      }

      // 업데이트된 딕셔너리를 상태에 다시 씁니다.
      toolContext.state().put("user:preferences", preference);
      System.out.printf("도구: 사용자 선호도 %s를 %s로 업데이트했습니다.", userPrefsKey, preference);

      return Map.of("status", "success", "updated_preference", toolContext.state().get(userPrefsKey).toString());
      // LLM이 updateUserThemePreference("dark")를 호출할 때:
      // toolContext.state가 업데이트되고, 변경 사항은
      // 결과 도구 응답 이벤트의 actions.stateDelta의 일부가 됩니다.
    }
    ```

### **에이전트 흐름 제어(Controlling Agent Flow)**

`tool_context.actions` 속성(Java에서는 `ToolContext.actions()`, Go에서는 `tool.Context.Actions()`)은 **EventActions** 객체를 보유합니다. 이 객체의 속성을 수정하면 도구가 실행을 마친 후 에이전트나 프레임워크가 수행할 작업을 제어할 수 있습니다.

* **`skip_summarization: bool`**: (기본값: False) True로 설정하면, ADK에게 일반적으로 도구의 출력을 요약하는 LLM 호출을 건너뛰도록 지시합니다. 도구의 반환 값이 이미 사용자에게 바로 보여줄 수 있는 메시지일 경우 유용합니다.

* **`transfer_to_agent: str`**: 이 값을 다른 에이전트의 이름으로 설정합니다. 프레임워크는 현재 에이전트의 실행을 중단하고 **대화의 제어를 지정된 에이전트로 이전**합니다. 이를 통해 도구는 작업을 더 전문화된 에이전트에게 동적으로 넘길 수 있습니다.

* **`escalate: bool`**: (기본값: False) 이 값을 True로 설정하면 현재 에이전트가 요청을 처리할 수 없음을 알리고 (계층 구조에 있는 경우) 부모 에이전트로 제어를 넘깁니다. LoopAgent에서는 하위 에이전트의 도구에서 **escalate=True**로 설정하면 루프가 종료됩니다.

#### 예시

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/overview/customer_support_agent.py"
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/tools-custom/customer_support_agent/main.go"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/tools/CustomerSupportAgentApp.java:full_code"
    ```

##### 설명

* `main_agent`와 `support_agent` 두 개의 에이전트를 정의합니다. `main_agent`는 초기 접점으로 설계되었습니다.
* `main_agent`에 의해 호출될 때 `check_and_transfer` 도구는 사용자의 쿼리를 검사합니다.
* 쿼리에 "urgent"라는 단어가 포함되어 있으면, 도구는 `tool_context`, 특히 **`tool_context.actions`**에 접근하여 `transfer_to_agent` 속성을 `support_agent`로 설정합니다.
* 이 작업은 프레임워크에게 **대화의 제어를 `support_agent`라는 이름의 에이전트로 이전하도록** 신호를 보냅니다.
* `main_agent`가 긴급한 쿼리를 처리할 때, `check_and_transfer` 도구는 이전을 트리거합니다. 이후의 응답은 이상적으로 `support_agent`로부터 오게 됩니다.
* 긴급하지 않은 일반적인 쿼리의 경우, 도구는 이전을 트리거하지 않고 단순히 처리합니다.

이 예시는 도구가 ToolContext의 EventActions를 통해 대화의 흐름을 동적으로 제어하고 다른 전문화된 에이전트로 제어를 이전할 수 있음을 보여줍니다.

### **인증(Authentication)**

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span>
</div>

ToolContext는 인증된 API와 상호작용하는 도구를 위한 메커니즘을 제공합니다. 도구가 인증을 처리해야 하는 경우, 다음을 사용할 수 있습니다:

* **`auth_response`**: 도구가 호출되기 전에 프레임워크가 이미 인증을 처리한 경우 자격증명(예: 토큰)을 포함합니다(RestApiTool 및 OpenAPI 보안 스키마에서 일반적).

* **`request_credential(auth_config: dict)`**: 도구가 인증이 필요하지만 자격증명이 없다고 판단한 경우 이 메서드를 호출합니다. 이는 프레임워크에게 제공된 `auth_config`에 기반한 인증 흐름을 시작하도록 신호를 보냅니다.

* **`get_auth_response()`**: (`request_credential`이 성공적으로 처리된 후) 후속 호출에서 사용자가 제공한 자격증명을 검색하기 위해 호출합니다.

인증 흐름, 구성 및 예시에 대한 자세한 설명은 전용 도구 인증 문서 페이지를 참조하세요.

### **컨텍스트 인식 데이터 접근 메서드(Context-Aware Data Access Methods)**

이 메서드들은 구성된 서비스에 의해 관리되는, 세션 또는 사용자와 관련된 영구 데이터와 도구가 편리하게 상호작용할 수 있는 방법을 제공합니다.

* **`list_artifacts()`** (Java에서는 **`listArtifacts()`**): `artifact_service`를 통해 현재 세션에 저장된 모든 아티팩트의 파일명(또는 키) 목록을 반환합니다. 아티팩트는 일반적으로 사용자가 업로드했거나 도구/에이전트가 생성한 파일(이미지, 문서 등)입니다.

* **`load_artifact(filename: str)`**: **`artifact_service`**에서 파일명으로 특정 아티팩트를 검색합니다. 선택적으로 버전을 지정할 수 있으며, 생략하면 최신 버전이 반환됩니다. 아티팩트 데이터와 mime 유형을 포함하는 `google.genai.types.Part` 객체를 반환하거나, 찾을 수 없으면 None을 반환합니다.

* **`save_artifact(filename: str, artifact: types.Part)`**: `artifact_service`에 아티팩트의 새 버전을 저장합니다. 새 버전 번호(0부터 시작)를 반환합니다.

* **`search_memory(query: str)`**: (ADK Python 및 Go에서 지원)
    구성된 `memory_service`를 사용하여 사용자의 장기 메모리를 쿼리합니다. 이는 과거 상호작용이나 저장된 지식에서 관련 정보를 검색하는 데 유용합니다. **SearchMemoryResponse**의 구조는 특정 메모리 서비스 구현에 따라 다르지만, 일반적으로 관련 텍스트 스니펫이나 대화 발췌문을 포함합니다.

#### 예시

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/overview/doc_analysis.py"
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/tools-custom/doc_analysis/doc_analysis.go"
    ```

=== "Java"

    ```java
    // 메모리의 컨텍스트를 사용하여 문서를 분석합니다.
    // 콜백 컨텍스트나 LoadArtifacts 도구를 사용하여 아티팩트를 나열, 로드, 저장할 수도 있습니다.
    public static @NonNull Maybe<ImmutableMap<String, Object>> processDocument(
        @Annotations.Schema(description = "분석할 문서의 이름입니다.") String documentName,
        @Annotations.-Schema(description = "분석을 위한 쿼리입니다.") String analysisQuery,
        ToolContext toolContext) {

      // 1. 사용 가능한 모든 아티팩트를 나열합니다.
      System.out.printf(
          "사용 가능한 모든 아티팩트 나열 %s:", toolContext.listArtifacts().blockingGet());

      // 2. 아티팩트를 메모리에 로드합니다.
      System.out.println("도구: 아티팩트 로드 시도 중: " + documentName);
      Part documentPart = toolContext.loadArtifact(documentName, Optional.empty()).blockingGet();
      if (documentPart == null) {
        System.out.println("도구: 문서 '" + documentName + "'를 찾을 수 없습니다.");
        return Maybe.just(
            ImmutableMap.<String, Object>of(
                "status", "error", "message", "문서 '" + documentName + "'를 찾을 수 없습니다."));
      }
      String documentText = documentPart.text().orElse("");
      System.out.println(
          "도구: 문서 '" + documentName + "' 로드됨 (" + documentText.length() + " 자).");

      // 3. 분석 수행 (플레이스홀더)
      String analysisResult =
          "'" + documentName + "'에 대한 '" + analysisQuery + "' 관련 분석 [분석 결과 플레이스홀더]";
      System.out.println("도구: 분석 수행됨.");

      // 4. 분석 결과를 새 아티팩트로 저장합니다.
      Part analysisPart = Part.fromText(analysisResult);
      String newArtifactName = "analysis_" + documentName;

      toolContext.saveArtifact(newArtifactName, analysisPart);

      return Maybe.just(
          ImmutableMap.<String, Object>builder()
              .put("status", "success")
              .put("analysis_artifact", newArtifactName)
              .build());
    }
    // FunctionTool processDocumentTool =
    //      FunctionTool.create(ToolContextArtifactExample.class, "processDocument");
    // 에이전트에 이 함수 도구를 포함시킵니다.
    // LlmAgent agent = LlmAgent().builder().tools(processDocumentTool).build();
    ```

**ToolContext**를 활용함으로써, 개발자들은 ADK의 아키텍처와 원활하게 통합되고 에이전트의 전반적인 능력을 향상시키는 더 정교하고 컨텍스트를 인식하는 커스텀 도구를 만들 수 있습니다.

## 효과적인 도구 함수 정의하기

메서드나 함수를 ADK 도구로 사용할 때, 그것을 어떻게 정의하는지가 에이전트의 올바른 사용 능력에 큰 영향을 미칩니다. 에이전트의 대규모 언어 모델(LLM)은 함수의 **이름**, **파라미터(인수)**, **타입 힌트**, 그리고 **도크스트링** / **소스 코드 주석**에 크게 의존하여 그 목적을 이해하고 올바른 호출을 생성합니다.

다음은 효과적인 도구 함수를 정의하기 위한 주요 지침입니다:

* **함수 이름:**
    * 동작을 명확히 나타내는 서술적이고 동사-명사 기반의 이름을 사용하세요 (예: `get_weather`, `searchDocuments`, `schedule_meeting`).
    * `run`, `process`, `handle_data`와 같은 일반적인 이름이나 `doStuff`처럼 지나치게 모호한 이름은 피하세요. 좋은 설명이 있더라도 `do_stuff`와 같은 이름은 모델이 언제 이 도구를 사용해야 할지, 예를 들어 `cancelFlight`와 비교하여 혼란을 줄 수 있습니다.
    * LLM은 도구 선택 시 함수 이름을 주요 식별자로 사용합니다.

* **파라미터(인수):**
    * 함수는 임의의 수의 파라미터를 가질 수 있습니다.
    * 명확하고 서술적인 이름을 사용하세요 (예: `c` 대신 `city`, `q` 대신 `search_query`).
    * **Python에서는 모든 파라미터에 타입 힌트를 제공하세요** (예: `city: str`, `user_id: int`, `items: list[str]`). 이는 ADK가 LLM을 위한 올바른 스키마를 생성하는 데 필수적입니다.
    * 모든 파라미터 타입은 **JSON 직렬화 가능**해야 합니다. 모든 Java 프리미티브 타입과 `str`, `int`, `float`, `bool`, `list`, `dict`와 같은 표준 Python 타입 및 그 조합은 일반적으로 안전합니다. 명확한 JSON 표현이 없는 복잡한 커스텀 클래스 인스턴스는 직접적인 파라미터로 피하세요.
    * 파라미터에 **기본값을 설정하지 마세요**. 예: `def my_func(param1: str = "default")`. 기본값은 기본 모델이 함수 호출을 생성할 때 안정적으로 지원되거나 사용되지 않습니다. 모든 필요한 정보는 LLM이 컨텍스트에서 도출하거나, 누락된 경우 명시적으로 요청해야 합니다.
    * **`self` / `cls`는 자동으로 처리됩니다:** 인스턴스 메서드의 `self`나 클래스 메서드의 `cls`와 같은 암시적 파라미터는 ADK가 자동으로 처리하며 LLM에 표시되는 스키마에서 제외됩니다. 도구가 LLM에게 제공하도록 요구하는 논리적 파라미터에 대해서만 타입 힌트와 설명을 정의하면 됩니다.

* **반환 타입:**
    * 함수의 반환 값은 Python에서는 **딕셔너리(`dict`)**여야 하고, Java에서는 **Map**이어야 합니다.
    * 함수가 딕셔너리가 아닌 타입(예: 문자열, 숫자, 리스트)을 반환하면, ADK 프레임워크는 결과를 모델에 다시 전달하기 전에 자동으로 `{'result': your_original_return_value}`와 같이 딕셔너리/Map으로 감쌉니다.
    * 딕셔너리/Map의 키와 값은 ***LLM이* 쉽게 이해할 수 있도록** 서술적으로 설계하세요. 모델이 이 출력을 읽고 다음 단계를 결정한다는 것을 기억하세요.
    * 의미 있는 키를 포함하세요. 예를 들어, `500`과 같은 에러 코드만 반환하는 대신 `{'status': 'error', 'error_message': 'Database connection failed'}`를 반환하세요.
    * 모델에게 도구 실행의 결과를 명확하게 나타내기 위해 `status` 키(예: `'success'`, `'error'`, `'pending'`, `'ambiguous'`)를 포함하는 것이 **매우 권장되는 관행**입니다.

* **도크스트링 / 소스 코드 주석:**
    * **이것은 매우 중요합니다.** 도크스트링은 LLM을 위한 설명 정보의 주요 소스입니다.
    * **도구가 *무엇을 하는지* 명확히 기술하세요.** 그 목적과 한계에 대해 구체적으로 설명하세요.
    * **도구를 *언제* 사용해야 하는지 설명하세요.** LLM의 의사 결정을 돕기 위해 컨텍스트나 예시 시나리오를 제공하세요.
    * ***각 파라미터*를 명확하게 설명하세요.** LLM이 해당 인수에 대해 어떤 정보를 제공해야 하는지 설명하세요.
    * 예상되는 `dict` 반환 값의 **구조와 의미**, 특히 다른 `status` 값과 관련된 데이터 키를 설명하세요.
    * **주입되는 ToolContext 파라미터는 설명하지 마세요.** 선택적 `tool_context: ToolContext` 파라미터는 LLM이 알아야 할 파라미터가 아니므로 도크스트링 설명 내에 언급하지 마세요. ToolContext는 LLM이 호출하기로 결정한 *후에* ADK에 의해 주입됩니다.

    **좋은 정의의 예:**

=== "Python"

    ```python
    def lookup_order_status(order_id: str) -> dict:
      """ID를 사용하여 고객 주문의 현재 상태를 가져옵니다.

      사용자가 특정 주문의 상태를 명시적으로 묻고 주문 ID를 제공할 때만
      이 도구를 사용하세요. 일반적인 문의에는 사용하지 마세요.

      Args:
          order_id: 조회할 주문의 고유 식별자입니다.

      Returns:
          결과를 나타내는 딕셔너리입니다.
          성공 시 status는 'success'이며 'order' 딕셔너리를 포함합니다.
          실패 시 status는 'error'이며 'error_message'를 포함합니다.
          성공 예: {'status': 'success', 'order': {'state': 'shipped', 'tracking_number': '1Z9...'}}
          에러 예: {'status': 'error', 'error_message': '주문 ID를 찾을 수 없습니다.'}
      """
      # ... 상태를 가져오는 함수 구현 ...
      if status_details := fetch_status_from_backend(order_id):
        return {
            "status": "success",
            "order": {
                "state": status_details.state,
                "tracking_number": status_details.tracking,
            },
        }
      else:
        return {"status": "error", "error_message": f"주문 ID {order_id}를 찾을 수 없습니다."}

    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/tools-custom/order_status/order_status.go:snippet"
    ```

=== "Java"

    ```java
    /**
     * 지정된 도시의 현재 날씨 보고서를 검색합니다.
     *
     * @param city 날씨 보고서를 검색할 도시입니다.
     * @param toolContext 도구의 컨텍스트입니다.
     * @return 날씨 정보를 포함하는 딕셔너리입니다.
     */
    public static Map<String, Object> getWeatherReport(String city, ToolContext toolContext) {
        Map<String, Object> response = new HashMap<>();
        if (city.toLowerCase(Locale.ROOT).equals("london")) {
            response.put("status", "success");
            response.put(
                    "report",
                    "런던의 현재 날씨는 흐리고 기온은 18도이며 비 올 확률이 있습니다.");
        } else if (city.toLowerCase(Locale.ROOT).equals("paris")) {
            response.put("status", "success");
            response.put("report", "파리의 날씨는 맑고 기온은 25도입니다.");
        } else {
            response.put("status", "error");
            response.put("error_message", String.format("'%s'의 날씨 정보는 사용할 수 없습니다.", city));
        }
        return response;
    }
    ```

* **단순성과 집중:**
    * **도구는 집중적으로 유지하세요:** 각 도구는 이상적으로 하나의 잘 정의된 작업을 수행해야 합니다.
    * **파라미터는 적을수록 좋습니다:** 모델은 일반적으로 선택적이거나 복잡한 파라미터가 많은 도구보다, 명확하게 정의된 파라미터가 적은 도구를 더 안정적으로 처리합니다.
    * **단순한 데이터 타입을 사용하세요:** 가능한 경우 파라미터로 복잡한 커스텀 클래스나 깊이 중첩된 구조 대신 기본 타입(**Python**에서는 `str`, `int`, `bool`, `float`, `List[str]`, **Java**에서는 `int`, `byte`, `short`, `long`, `float`, `double`, `boolean`, `char`)을 선호하세요.
    * **복잡한 작업은 분해하세요:** 여러 개의 뚜렷한 논리적 단계를 수행하는 함수를 더 작고 집중된 도구로 나누세요. 예를 들어, 단일 `update_user_profile(profile: ProfileObject)` 도구 대신 `update_user_name(name: str)`, `update_user_address(address: str)`, `update_user_preferences(preferences: list[str])` 등과 같은 별도의 도구를 고려하세요. 이렇게 하면 LLM이 올바른 기능을 더 쉽게 선택하고 사용할 수 있습니다.

이러한 지침을 준수함으로써, LLM에게 커스텀 함수 도구를 효과적으로 활용하는 데 필요한 명확성과 구조를 제공하여 더 유능하고 신뢰할 수 있는 에이전트 행동을 이끌어낼 수 있습니다.

## 툴셋(Toolsets): 도구 그룹화 및 동적 제공

<div class="language-support-tag" title="이 기능은 현재 Python에서 사용할 수 있습니다.">
   <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.5.0</span>
</div>

개별 도구를 넘어, ADK는 `BaseToolset` 인터페이스(`google.adk.tools.base_toolset`에 정의됨)를 통해 **툴셋(Toolset)**의 개념을 도입합니다. 툴셋을 사용하면 종종 동적으로 `BaseTool` 인스턴스 컬렉션을 관리하고 에이전트에게 제공할 수 있습니다.

이 접근 방식은 다음과 같은 경우에 유용합니다:

*   **관련 도구 정리:** 공통된 목적을 가진 도구들을 그룹화합니다 (예: 모든 수학 연산용 도구, 또는 특정 API와 상호작용하는 모든 도구).
*   **동적 도구 가용성:** 에이전트가 현재 컨텍스트(예: 사용자 권한, 세션 상태 또는 기타 런타임 조건)에 따라 다른 도구를 사용할 수 있도록 합니다. 툴셋의 `get_tools` 메서드는 어떤 도구를 노출할지 결정할 수 있습니다.
*   **외부 도구 제공자 통합:** 툴셋은 OpenAPI 사양이나 MCP 서버와 같은 외부 시스템에서 오는 도구에 대한 어댑터 역할을 하여, 이를 ADK 호환 `BaseTool` 객체로 변환할 수 있습니다.

### `BaseToolset` 인터페이스

ADK에서 툴셋 역할을 하는 모든 클래스는 `BaseToolset` 추상 기본 클래스를 구현해야 합니다. 이 인터페이스는 주로 두 가지 메서드를 정의합니다:

*   **`async def get_tools(...) -> list[BaseTool]:`**
    이것은 툴셋의 핵심 메서드입니다. ADK 에이전트가 사용 가능한 도구를 알아야 할 때, `tools` 목록에 제공된 각 `BaseToolset` 인스턴스에 대해 `get_tools()`를 호출합니다.
    *   선택적으로 `readonly_context`(`ReadonlyContext`의 인스턴스)를 받습니다. 이 컨텍스트는 현재 세션 상태(`readonly_context.state`), 에이전트 이름, 호출 ID와 같은 정보에 대한 읽기 전용 접근을 제공합니다. 툴셋은 이 컨텍스트를 사용하여 어떤 도구를 반환할지 동적으로 결정할 수 있습니다.
    *   **반드시** `BaseTool` 인스턴스(예: `FunctionTool`, `RestApiTool`)의 `list`를 반환해야 합니다.

*   **`async def close(self) -> None:`**
    이 비동기 메서드는 예를 들어 에이전트 서버가 종료되거나 `Runner`가 닫힐 때와 같이 툴셋이 더 이상 필요하지 않을 때 ADK 프레임워크에 의해 호출됩니다. 네트워크 연결 닫기, 파일 핸들 해제 또는 툴셋이 관리하는 다른 리소스 정리와 같은 필요한 모든 정리 작업을 수행하려면 이 메서드를 구현하세요.

### 에이전트와 함께 툴셋 사용하기

`BaseToolset` 구현의 인스턴스를 개별 `BaseTool` 인스턴스와 함께 `LlmAgent`의 `tools` 목록에 직접 포함할 수 있습니다.

에이전트가 초기화되거나 사용 가능한 기능을 결정해야 할 때, ADK 프레임워크는 `tools` 목록을 반복합니다:

*   항목이 `BaseTool` 인스턴스이면 직접 사용됩니다.
*   항목이 `BaseToolset` 인스턴스이면, `get_tools()` 메서드가 (현재 `ReadonlyContext`와 함께) 호출되고, 반환된 `BaseTool` 목록이 에이전트의 사용 가능한 도구에 추가됩니다.

### 예시: 간단한 수학 툴셋

간단한 산술 연산을 제공하는 툴셋의 기본 예제를 만들어 보겠습니다.

```py
--8<-- "examples/python/snippets/tools/overview/toolset_example.py:init"
```

이 예제에서:

*   `SimpleMathToolset`은 `BaseToolset`을 구현하고, `get_tools()` 메서드는 `add_numbers`와 `subtract_numbers`에 대한 `FunctionTool` 인스턴스를 반환합니다. 또한 접두사를 사용하여 이름을 사용자 정의합니다.
*   `calculator_agent`는 개별 `greet_tool`과 `SimpleMathToolset`의 인스턴스로 구성됩니다.
*   `calculator_agent`가 실행될 때, ADK는 `math_toolset_instance.get_tools()`를 호출합니다. 그러면 에이전트의 LLM은 사용자 요청을 처리하기 위해 `greet_user`, `calculator_add_numbers`, `calculator_subtract_numbers`에 접근할 수 있게 됩니다.
*   `add_numbers` 도구는 `tool_context.state`에 쓰는 것을 보여주며, 에이전트의 지침은 이 상태를 읽는 것을 언급합니다.
*   `close()` 메서드는 툴셋이 보유한 모든 리소스가 해제되도록 호출됩니다.

툴셋은 ADK 에이전트에게 도구 컬렉션을 구성, 관리 및 동적으로 제공하는 강력한 방법을 제공하여, 더 모듈화되고 유지 관리 가능하며 적응성 있는 에이전트 애플리케이션을 만들 수 있게 합니다.