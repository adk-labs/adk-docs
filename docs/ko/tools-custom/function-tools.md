# 함수 도구

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

사전 빌드된 ADK 도구가 요구 사항을 충족하지 않는 경우 사용자 지정 *함수 도구*를 만들 수 있습니다. 함수 도구를 빌드하면 독점 데이터베이스에 연결하거나 고유한 알고리즘을 구현하는 등 맞춤형 기능을 만들 수 있습니다.
예를 들어 함수 도구 `myfinancetool`은 특정 재무 지표를 계산하는 함수일 수 있습니다. ADK는 또한 장기 실행 함수를 지원하므로 해당 계산에 시간이 걸리는 경우 에이전트는 다른 작업을 계속할 수 있습니다.

ADK는 각각 다른 수준의 복잡성과 제어에 적합한 여러 가지 방법으로 함수 도구를 만들 수 있습니다.

*  [함수 도구](#function-tool)
*  [장기 실행 함수 도구](#long-run-tool)
*  [도구로서의 에이전트](#agent-tool)

## 함수 도구 {#function-tool}

Python 함수를 도구로 변환하는 것은 사용자 지정 논리를 에이전트에 통합하는 간단한 방법입니다. 에이전트의 `tools` 목록에 함수를 할당하면 프레임워크가 자동으로 `FunctionTool`로 래핑합니다.

### 작동 방식

ADK 프레임워크는 이름, docstring, 매개변수, 유형 힌트 및 기본값을 포함하여 Python 함수의 서명을 자동으로 검사하여 스키마를 생성합니다. 이 스키마는 LLM이 도구의 목적, 사용 시기 및 필요한 인수를 이해하는 데 사용하는 것입니다.

### 함수 서명 정의

잘 정의된 함수 서명은 LLM이 도구를 올바르게 사용하는 데 중요합니다.

#### 매개변수

##### 필수 매개변수

=== "Python"
    매개변수는 유형 힌트가 있지만 **기본값이 없는** 경우 **필수**로 간주됩니다. LLM은 도구를 호출할 때 이 인수에 대한 값을 제공해야 합니다. 매개변수의 설명은 함수의 docstring에서 가져옵니다.

    ???+ "예: 필수 매개변수"
        ```python
        def get_weather(city: str, unit: str):
            """
            지정된 단위로 도시의 날씨를 검색합니다.

            인수:
                city (str): 도시 이름입니다.
                unit (str): '섭씨' 또는 '화씨' 중 하나인 온도 단위입니다.
            """
            # ... 함수 논리 ...
            return {"status": "success", "report": f"{city}의 날씨는 맑습니다."}
        ```
    이 예에서 `city`와 `unit`은 모두 필수입니다. LLM이 둘 중 하나 없이 `get_weather`를 호출하려고 하면 ADK는 LLM에 오류를 반환하여 호출을 수정하도록 유도합니다.

=== "Go"
    Go에서는 구조체 태그를 사용하여 JSON 스키마를 제어합니다. 두 가지 기본 태그는 `json`과 `jsonschema`입니다.

    매개변수는 구조체 필드의 `json` 태그에 `omitempty` 또는 `omitzero` 옵션이 **없는** 경우 **필수**로 간주됩니다.

    `jsonschema` 태그는 인수의 설명을 제공하는 데 사용됩니다. 이는 LLM이 인수가 무엇인지 이해하는 데 중요합니다.

    ???+ "예: 필수 매개변수"
        ```go
        // GetWeatherParams는 getWeather 도구의 인수를 정의합니다.
        type GetWeatherParams struct {
            // 이 필드는 필수입니다("omitempty" 없음).
            // jsonschema 태그는 설명을 제공합니다.
            Location string `json:"location" jsonschema:"도시 및 주, 예: 샌프란시스코, CA"`

            // 이 필드도 필수입니다.
            Unit     string `json:"unit" jsonschema:"'섭씨' 또는 '화씨' 중 하나인 온도 단위"`
        }
        ```
    이 예에서 `location`과 `unit`은 모두 필수입니다.

##### 선택적 매개변수

=== "Python"
    매개변수는 **기본값**을 제공하는 경우 **선택 사항**으로 간주됩니다. 이것이 선택적 인수를 정의하는 표준 Python 방식입니다. `typing.Optional[SomeType]` 또는 `| None` 구문(Python 3.10 이상)을 사용하여 매개변수를 선택 사항으로 표시할 수도 있습니다.

    ???+ "예: 선택적 매개변수"
        ```python
        def search_flights(destination: str, departure_date: str, flexible_days: int = 0):
            """
            항공편을 검색합니다.

            인수:
                destination (str): 목적지 도시입니다.
                departure_date (str): 원하는 출발일입니다.
                flexible_days (int, optional): 검색에 대한 유연한 일수입니다. 기본값은 0입니다.
            """
            # ... 함수 논리 ...
            if flexible_days > 0:
                return {"status": "success", "report": f"{destination}으로 가는 유연한 항공편을 찾았습니다."}
            return {"status": "success", "report": f"{departure_date}에 {destination}으로 가는 항공편을 찾았습니다."}
        ```
    여기서 `flexible_days`는 선택 사항입니다. LLM은 이를 제공하도록 선택할 수 있지만 필수는 아닙니다.

=== "Go"
    매개변수는 구조체 필드의 `json` 태그에 `omitempty` 또는 `omitzero` 옵션이 있는 경우 **선택 사항**으로 간주됩니다.

    ???+ "예: 선택적 매개변수"
        ```go
        // GetWeatherParams는 getWeather 도구의 인수를 정의합니다.
        type GetWeatherParams struct {
            // 위치는 필수입니다.
            Location string `json:"location" jsonschema:"도시 및 주, 예: 샌프란시스코, CA"`

            // 단위는 선택 사항입니다.
            Unit string `json:"unit,omitempty" jsonschema:"'섭씨' 또는 '화씨' 중 하나인 온도 단위"`

            // 일수는 선택 사항입니다.
            Days int `json:"days,omitzero" jsonschema:"반환할 예보 일수(기본값은 1)"`
        }
        ```
    여기서 `unit`과 `days`는 선택 사항입니다. LLM은 이를 제공하도록 선택할 수 있지만 필수는 아닙니다.

##### `typing.Optional`을 사용한 선택적 매개변수
`typing.Optional[SomeType]` 또는 `| None` 구문(Python 3.10 이상)을 사용하여 매개변수를 선택 사항으로 표시할 수도 있습니다. 이는 매개변수가 `None`일 수 있음을 나타냅니다. `None`의 기본값과 결합하면 표준 선택적 매개변수처럼 동작합니다.

???+ "예: `typing.Optional`"
    === "Python"
        ```python
        from typing import Optional

        def create_user_profile(username: str, bio: Optional[str] = None):
            """
            새 사용자 프로필을 만듭니다.

            인수:
                username (str): 사용자의 고유한 사용자 이름입니다.
                bio (str, optional): 사용자에 대한 짧은 약력입니다. 기본값은 None입니다.
            """
            # ... 함수 논리 ...
            if bio:
                return {"status": "success", "message": f"{username}에 대한 프로필이 약력과 함께 생성되었습니다."}
            return {"status": "success", "message": f"{username}에 대한 프로필이 생성되었습니다."}
        ```

##### 가변 매개변수(`*args` 및 `**kwargs`)
다른 목적으로 함수 서명에 `*args`(가변 위치 인수) 및 `**kwargs`(가변 키워드 인수)를 포함할 수 있지만 LLM에 대한 도구 스키마를 생성할 때 **ADK 프레임워크에서 무시**됩니다. LLM은 이를 인식하지 못하며 인수를 전달할 수 없습니다. LLM에서 예상하는 모든 데이터에 대해 명시적으로 정의된 매개변수를 사용하는 것이 가장 좋습니다.

#### 반환 유형

함수 도구의 기본 반환 유형은 Python에서는 **사전**이고 Java에서는 **맵**입니다. 이를 통해 키-값 쌍으로 응답을 구조화하여 LLM에 컨텍스트와 명확성을 제공할 수 있습니다. 함수가 사전 이외의 유형을 반환하는 경우 프레임워크는 자동으로 **"result"**라는 단일 키를 가진 사전으로 래핑합니다.

반환 값을 가능한 한 설명적으로 만드십시오. *예를 들어,* 숫자 오류 코드를 반환하는 대신 사람이 읽을 수 있는 설명이 포함된 "error_message" 키가 있는 사전을 반환합니다. 코드가 아닌 **LLM**이 결과를 이해해야 한다는 점을 기억하십시오. 모범 사례로 반환 사전에 "status" 키를 포함하여 전체 결과(예: "success", "error", "pending")를 나타내어 LLM에 작업 상태에 대한 명확한 신호를 제공합니다.

#### Docstrings

함수의 docstring은 도구의 **설명** 역할을 하며 LLM으로 전송됩니다. 따라서 잘 작성되고 포괄적인 docstring은 LLM이 도구를 효과적으로 사용하는 방법을 이해하는 데 중요합니다. 함수의 목적, 매개변수의 의미 및 예상 반환 값을 명확하게 설명하십시오.

### 도구 간 데이터 전달

에이전트가 여러 도구를 순서대로 호출할 때 한 도구에서 다른 도구로 데이터를 전달해야 할 수 있습니다. 권장되는 방법은 세션 상태에서 `temp:` 접두사를 사용하는 것입니다.

도구는 `temp:` 변수에 데이터를 쓸 수 있고 후속 도구는 이를 읽을 수 있습니다. 이 데이터는 현재 호출에만 사용할 수 있으며 이후에는 삭제됩니다.

!!! note "공유 호출 컨텍스트"
    단일 에이전트 턴 내의 모든 도구 호출은 동일한 `InvocationContext`를 공유합니다. 즉, 동일한 임시(`temp:`) 상태를 공유하므로 도구 간에 데이터를 전달할 수 있습니다.

### 예

??? "예"

    === "Python"
    
        이 도구는 주어진 주식 시세/기호의 주가를 가져오는 파이썬 함수입니다.
    
        <u>참고</u>: 이 도구를 사용하기 전에 `pip install yfinance` 라이브러리를 설치해야 합니다.
    
        ```py
        --8<-- "examples/python/snippets/tools/function-tools/func_tool.py"
        ```
    
        이 도구의 반환 값은 사전으로 래핑됩니다.
    
        ```json
        {"result": "$123"}
        ```
    
    === "Go"

        이 도구는 주가의 모의 값을 검색합니다.

        ```go
        import (
            "google.golang.org/adk/agent"
            "google.golang.org/adk/agent/llmagent"
            "google.golang.org/adk/model/gemini"
            "google.golang.org/adk/runner"
            "google.golang.org/adk/session"
            "google.golang.org/adk/tool"
            "google.golang.org/adk/tool/functiontool"
            "google.golang.org/genai"
        )

        --8<-- "examples/go/snippets/tools/function-tools/func_tool.go"
        ```

        이 도구의 반환 값은 `getStockPriceResults` 인스턴스가 됩니다.

        ```json
        입력 `{"symbol": "GOOG"}`의 경우: {"price":300.6,"symbol":"GOOG"}
        ```

    === "Java"
    
        이 도구는 주가의 모의 값을 검색합니다.
    
        ```java
        --8<-- "examples/java/snippets/src/main/java/tools/StockPriceAgent.java:full_code"
        ```
    
        이 도구의 반환 값은 Map<String, Object>으로 래핑됩니다.
    
        ```json
        입력 `GOOG`의 경우: {"symbol": "GOOG", "price": "1.0"}
        ```

### 모범 사례

함수를 정의하는 데 상당한 유연성이 있지만 단순성이 LLM의 사용성을 향상시킨다는 점을 기억하십시오. 다음 지침을 고려하십시오.

* **매개변수가 적을수록 좋습니다:** 복잡성을 줄이기 위해 매개변수 수를 최소화하십시오.  
* **단순한 데이터 유형:** 가능한 경우 사용자 지정 클래스보다 `str` 및 `int`와 같은 기본 데이터 유형을 선호하십시오.  
* **의미 있는 이름:** 함수의 이름과 매개변수 이름은 LLM이 도구를 해석하고 활용하는 방식에 큰 영향을 미칩니다. 함수의 목적과 입력의 의미를 명확하게 반영하는 이름을 선택하십시오. `do_stuff()` 또는 `beAgent()`와 같은 일반적인 이름은 피하십시오.
* **병렬 실행을 위한 빌드:** 여러 도구가 실행될 때 비동기 작업을 위해 빌드하여 함수 호출 성능을 향상시킵니다. 도구에 대한 병렬 실행을 활성화하는 방법에 대한 정보는
[병렬 실행으로 도구 성능 향상](/adk-docs/ko/tools-custom/performance/)을 참조하십시오.

## 장기 실행 함수 도구 {#long-run-tool}

이 도구는 에이전트 워크플로 작업 외부에서 처리되고 에이전트 실행을 차단하지 않고 상당한 처리 시간이 필요한 작업을 시작하고 관리하는 데 도움이 되도록 설계되었습니다. 이 도구는 `FunctionTool`의 하위 클래스입니다.

`LongRunningFunctionTool`을 사용할 때 함수는 장기 실행 작업을 시작하고 선택적으로 장기 실행 작업 ID와 같은 **초기 결과**를 반환할 수 있습니다. 장기 실행 함수 도구가 호출되면 에이전트 실행기는 에이전트 실행을 일시 중지하고 에이전트 클라이언트가 장기 실행 작업이 완료될 때까지 계속할지 또는 기다릴지 결정하도록 합니다. 에이전트 클라이언트는 장기 실행 작업의 진행 상황을 쿼리하고 중간 또는 최종 응답을 다시 보낼 수 있습니다. 그러면 에이전트는 다른 작업을 계속할 수 있습니다. 예를 들어 에이전트가 작업을 진행하기 전에 사람의 승인이 필요한 인간 참여 시나리오가 있습니다.

!!! warning "경고: 실행 처리"
    장기 실행 함수 도구는 에이전트 워크플로의 일부로 장기 실행 작업을 시작하고 *관리*하는 데 도움이 되도록 설계되었지만 실제 장기 작업을 ***수행***하지는 않습니다.
    완료하는 데 상당한 시간이 필요한 작업의 경우 작업을 수행할 별도의 서버를 구현해야 합니다.

!!! tip "팁: 병렬 실행"
    빌드하는 도구 유형에 따라 비동기 작업을 위해 설계하는 것이 장기 실행 도구를 만드는 것보다 더 나은 솔루션일 수 있습니다.
    자세한 내용은
    [병렬 실행으로 도구 성능 향상](/adk-docs/ko/tools-custom/performance/)을 참조하십시오.

### 작동 방식

Python에서는 함수를 `LongRunningFunctionTool`로 래핑합니다. Java에서는 메서드 이름을 `LongRunningFunctionTool.create()`에 전달합니다.


1. **시작:** LLM이 도구를 호출하면 함수가 장기 실행 작업을 시작합니다.

2. **초기 업데이트:** 함수는 선택적으로 초기 결과(예: 장기 실행 작업 ID)를 반환해야 합니다. ADK 프레임워크는 결과를 가져와 `FunctionResponse` 내에 패키징하여 LLM에 다시 보냅니다. 이를 통해 LLM은 사용자에게 알릴 수 있습니다(예: 상태, 완료율, 메시지). 그런 다음 에이전트 실행이 종료/일시 중지됩니다.

3. **계속 또는 대기:** 각 에이전트 실행이 완료된 후. 에이전트 클라이언트는 장기 실행 작업의 진행 상황을 쿼리하고 중간 응답으로 에이전트 실행을 계속할지(진행 상황을 업데이트하기 위해) 또는 최종 응답이 검색될 때까지 기다릴지 결정할 수 있습니다. 에이전트 클라이언트는 다음 실행을 위해 중간 또는 최종 응답을 에이전트에 다시 보내야 합니다.

4. **프레임워크 처리:** ADK 프레임워크는 실행을 관리합니다. 에이전트 클라이언트가 보낸 중간 또는 최종 `FunctionResponse`를 LLM에 보내 사용자 친화적인 메시지를 생성합니다.

### 도구 만들기

도구 함수를 정의하고 `LongRunningFunctionTool` 클래스를 사용하여 래핑합니다.

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/function-tools/human_in_the_loop.py:define_long_running_function"
    ```

=== "Go"

    ```go
    import (
        "google.golang.org/adk/agent"
        "google.golang.org/adk/agent/llmagent"
        "google.golang.org/adk/model/gemini"
        "google.golang.org/adk/tool"
        "google.golang.org/adk/tool/functiontool"
        "google.golang.org/genai"
    )

    --8<-- "examples/go/snippets/tools/function-tools/long-running-tool/long_running_tool.go:create_long_running_tool"
    ```

=== "Java"

    ```java
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.tools.LongRunningFunctionTool;
    import java.util.HashMap;
    import java.util.Map;
    
    public class ExampleLongRunningFunction {
    
      // 장기 실행 함수를 정의합니다.
      // 상환에 대한 승인을 요청합니다.
      public static Map<String, Object> askForApproval(String purpose, double amount) {
        // 티켓 생성 및 알림 전송 시뮬레이션
        System.out.println(
            "목적에 대한 티켓 생성 시뮬레이션: " + purpose + ", 금액: " + amount);
    
        // 티켓 링크와 함께 승인자에게 알림 보내기
        Map<String, Object> result = new HashMap<>();
        result.put("status", "pending");
        result.put("approver", "Sean Zhou");
        result.put("purpose", purpose);
        result.put("amount", amount);
        result.put("ticket-id", "approval-ticket-1");
        return result;
      }
    
      public static void main(String[] args) throws NoSuchMethodException {
        // 메서드를 LongRunningFunctionTool.create에 전달
        LongRunningFunctionTool approveTool =
            LongRunningFunctionTool.create(ExampleLongRunningFunction.class, "askForApproval");
    
        // 에이전트에 도구 포함
        LlmAgent approverAgent =
            LlmAgent.builder()
                // ...
                .tools(approveTool)
                .build();
      }
    }
    ```

### 중간/최종 결과 업데이트

에이전트 클라이언트는 장기 실행 함수 호출과 함께 이벤트를 수신하고 티켓 상태를 확인합니다. 그런 다음 에이전트 클라이언트는 중간 또는 최종 응답을 다시 보내 진행 상황을 업데이트할 수 있습니다. 프레임워크는 이 값(None인 경우에도)을 LLM에 다시 보내는 `FunctionResponse`의 내용에 패키징합니다.

!!! note "참고: 재개 기능이 있는 장기 실행 함수 응답"

    ADK 에이전트 워크플로가 
    [재개](/adk-docs/ko/runtime/resume/) 기능으로 구성된 경우 장기 실행 
    함수 응답과 함께 호출 ID(`invocation_id`) 매개변수도 포함해야 합니다. 
    제공하는 호출 ID는 장기 실행 함수 요청을 생성한 것과 동일한 
    호출이어야 합니다. 그렇지 않으면 시스템이 응답으로 새 호출을 시작합니다. 
    에이전트가 재개 기능을 사용하는 경우 응답에 포함될 수 있도록 
    장기 실행 함수 요청과 함께 호출 ID를 매개변수로 포함하는 것을 고려하십시오. 
    재개 기능 사용에 대한 자세한 내용은 
    [중지된 에이전트 재개](/adk-docs/ko/runtime/resume/)를 참조하십시오.

??? Tip "Java ADK에만 적용"

    함수 도구와 함께 `ToolContext`를 전달할 때 다음 중 하나가 참인지 확인하십시오.

    * 스키마가 함수 서명의 ToolContext 매개변수와 함께 전달됩니다. 예:
      ```
      @com.google.adk.tools.Annotations.Schema(name = "toolContext") ToolContext toolContext
      ```
    또는

    * 다음 `-parameters` 플래그가 mvn 컴파일러 플러그인에 설정됩니다.

    ```
    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.14.0</version> <!-- 또는 최신 버전 -->
                <configuration>
                    <compilerArgs>
                        <arg>-parameters</arg>
                    </compilerArgs>
                </configuration>
            </plugin>
        </plugins>
    </build>
    ```
    이 제약 조건은 일시적이며 제거될 예정입니다.


=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/function-tools/human_in_the_loop.py:call_reimbursement_tool"
    ```

=== "Go"

    다음 예는 다중 턴 워크플로를 보여줍니다. 먼저 사용자는 에이전트에게 티켓을 만들도록 요청합니다. 에이전트는 장기 실행 도구를 호출하고 클라이언트는 `FunctionCall` ID를 캡처합니다. 그런 다음 클라이언트는 티켓 ID와 최종 상태를 제공하기 위해 후속 `FunctionResponse` 메시지를 에이전트에 다시 보내 비동기 작업 완료를 시뮬레이션합니다.

    ```go
    --8<-- "examples/go/snippets/tools/function-tools/long-running-tool/long_running_tool.go:run_long_running_tool"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/tools/LongRunningFunctionExample.java:full_code"
    ```

??? "Python 전체 예: 파일 처리 시뮬레이션"

    ```py
    --8<-- "examples/python/snippets/tools/function-tools/human_in_the_loop.py"
    ```

#### 이 예의 주요 측면

* **`LongRunningFunctionTool`**: 제공된 메서드/함수를 래핑합니다. 프레임워크는 생성된 업데이트와 최종 반환 값을 순차적인 FunctionResponses로 보내는 것을 처리합니다.

* **에이전트 지침**: LLM에 도구를 사용하고 사용자 업데이트를 위해 들어오는 FunctionResponse 스트림(진행률 대 완료)을 이해하도록 지시합니다.

* **최종 반환**: 함수는 최종 결과 사전을 반환하며, 이는 완료를 나타내기 위해 마지막 FunctionResponse에서 전송됩니다.

## 도구로서의 에이전트 {#agent-tool}

이 강력한 기능을 사용하면 시스템 내의 다른 에이전트의 기능을 도구로 호출하여 활용할 수 있습니다. 도구로서의 에이전트를 사용하면 다른 에이전트를 호출하여 특정 작업을 수행하도록 하여 효과적으로 **책임을 위임**할 수 있습니다. 이는 개념적으로 다른 에이전트를 호출하고 에이전트의 응답을 함수의 반환 값으로 사용하는 Python 함수를 만드는 것과 유사합니다.

### 하위 에이전트와의 주요 차이점

도구로서의 에이전트와 하위 에이전트를 구별하는 것이 중요합니다.

* **도구로서의 에이전트:** 에이전트 A가 에이전트 B를 도구로 호출하면(도구로서의 에이전트 사용) 에이전트 B의 답변은 에이전트 A로 **다시 전달**되며, 에이전트 A는 답변을 요약하고 사용자에게 응답을 생성합니다. 에이전트 A는 제어권을 유지하고 향후 사용자 입력을 계속 처리합니다.  

* **하위 에이전트:** 에이전트 A가 에이전트 B를 하위 에이전트로 호출하면 사용자에게 응답하는 책임이 완전히 **에이전트 B로 이전**됩니다. 에이전트 A는 사실상 루프에서 벗어납니다. 모든 후속 사용자 입력은 에이전트 B에서 응답합니다.

### 사용법

에이전트를 도구로 사용하려면 AgentTool 클래스로 에이전트를 래핑합니다.

=== "Python"

    ```py
    tools=[AgentTool(agent=agent_b)]
    ```

=== "Go"

    ```go
    agenttool.New(agent, &agenttool.Config{...})
    ```

=== "Java"

    ```java
    AgentTool.create(agent)
    ```


### 사용자 지정

`AgentTool` 클래스는 동작을 사용자 지정하기 위한 다음 속성을 제공합니다.

* **skip_summarization: bool:** True로 설정하면 프레임워크는 도구 에이전트의 응답에 대한 **LLM 기반 요약을 건너뜁니다**. 이는 도구의 응답이 이미 잘 형식화되어 있고 추가 처리가 필요하지 않은 경우에 유용할 수 있습니다.

??? "예"

    === "Python"

        ```py
        --8<-- "examples/python/snippets/tools/function-tools/summarizer.py"
        ```
  
    === "Go"

        ```go
        import (
            "google.golang.org/adk/agent"
            "google.golang.org/adk/agent/llmagent"
            "google.golang.org/adk/model/gemini"
            "google.golang.org/adk/tool"
            "google.golang.org/adk/tool/agenttool"
            "google.golang.org/genai"
        )

        --8<-- "examples/go/snippets/tools/function-tools/func_tool.go:agent_tool_example"
        ```

    === "Java"

        ```java
        --8<-- "examples/java/snippets/src/main/java/tools/AgentToolCustomization.java:full_code"
        ```

### 작동 방식

1. `main_agent`가 긴 텍스트를 받으면 지침에 따라 긴 텍스트에 대해 'summarize' 도구를 사용하도록 지시합니다.  
2. 프레임워크는 'summarize'를 `summary_agent`를 래핑하는 `AgentTool`로 인식합니다.  
3. 내부적으로 `main_agent`는 긴 텍스트를 입력으로 `summary_agent`를 호출합니다.  
4. `summary_agent`는 지침에 따라 텍스트를 처리하고 요약을 생성합니다.  
5. **`summary_agent`의 응답은 `main_agent`로 다시 전달됩니다.**  
6. 그런 다음 `main_agent`는 요약을 가져와 사용자에게 최종 응답을 공식화할 수 있습니다(예: "텍스트 요약은 다음과 같습니다. ...")
