# AI 에이전트의 안전 및 보안

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span><span class="lst-go">Go</span><span class="lst-java">Java</span>
</div>

AI 에이전트의 기능이 발전함에 따라, 안전하고 보안이 유지되며 브랜드 가치에 부합하도록 운영하는 것이 무엇보다 중요합니다. 제어되지 않는 에이전트는 데이터 유출과 같이 의도와 다르거나 유해한 작업을 실행하거나, 브랜드 평판에 영향을 미칠 수 있는 부적절한 콘텐츠를 생성하는 등 여러 위험을 초래할 수 있습니다. **위험의 원인으로는 모호한 지침, 모델 환각, 적대적인 사용자의 탈옥 및 프롬프트 인젝션, 도구 사용을 통한 간접적인 프롬프트 인젝션 등이 있습니다.**

[Google Cloud Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/overview)는 이러한 위험을 완화하기 위한 다계층 접근 방식을 제공하여, 강력하면서도 신뢰할 수 있는 에이전트를 구축할 수 있도록 지원합니다. 에이전트가 명시적으로 허용한 작업만 수행하도록 엄격한 경계를 설정하는 여러 메커니즘을 제공합니다:

1. **ID 및 권한 부여**: 에이전트 및 사용자 인증을 정의하여 에이전트가 **누구의 역할로 행동하는지** 제어합니다.
2. **입력 및 출력을 스크리닝하는 가드레일**: 모델 및 도구 호출을 정밀하게 제어합니다.

    * *도구 내 가드레일:* 개발자가 설정한 도구 컨텍스트를 사용하여 정책을 강제하는 등(예: 특정 테이블에 대해서만 쿼리 허용) 방어적으로 도구를 설계합니다.
    * *Gemini 내장 안전 기능:* Gemini 모델을 사용하는 경우, 유해한 출력을 차단하는 콘텐츠 필터와 모델의 행동 및 안전 가이드라인을 안내하는 시스템 지침의 이점을 활용할 수 있습니다.
    * *콜백 및 플러그인:* 실행 전후에 모델 및 도구 호출을 검증하고, 매개변수를 에이전트 상태 또는 외부 정책과 대조하여 확인합니다.
    * *Gemini를 안전 가드레일로 사용:* 콜백을 통해 구성된 저렴하고 빠른 모델(예: Gemini Flash Lite)을 사용하여 입력과 출력을 스크리닝하는 추가적인 안전 계층을 구현합니다.

3. **샌드박스화된 코드 실행**: 모델이 생성한 코드가 보안 문제를 일으키지 않도록 환경을 샌드박스화하여 방지합니다.
4. **평가 및 추적**: 평가 도구를 사용하여 에이전트의 최종 출력의 품질, 관련성, 정확성을 평가합니다. 추적을 사용하여 에이전트의 작업에 대한 가시성을 확보하고, 도구 선택, 전략, 접근 방식의 효율성 등 에이전트가 해결책에 도달하기까지의 단계를 분석합니다.
5. **네트워크 제어 및 VPC-SC**: 데이터 유출을 방지하고 잠재적 영향 범위를 제한하기 위해 에이전트 활동을 보안 경계(예: VPC 서비스 제어) 내로 제한합니다.

## 안전 및 보안 위험

안전 조치를 구현하기 전에, 에이전트의 기능, 도메인, 배포 컨텍스트에 특화된 철저한 위험 평가를 수행해야 합니다.

**위험의 원인**은 다음과 같습니다:

* 모호한 에이전트 지침
* 적대적인 사용자의 프롬프트 인젝션 및 탈옥 시도
* 도구 사용을 통한 간접적인 프롬프트 인젝션

**위험 범주**는 다음과 같습니다:

* **의도 불일치 및 목표 손상**
    * 유해한 결과로 이어지는 의도하지 않은 목표나 대리 목표 추구("보상 해킹")
    * 복잡하거나 모호한 지침의 오해석
* **브랜드 안전성을 포함한 유해 콘텐츠 생성**
    * 유독성, 증오, 편향, 성적으로 노골적이거나 차별적이거나 불법적인 콘텐츠 생성
    * 브랜드 가치에 반하는 언어 사용이나 주제를 벗어난 대화와 같은 브랜드 안전성 위험
* **안전하지 않은 작업**
    * 시스템을 손상시키는 명령어 실행
    * 승인되지 않은 구매 또는 금융 거래 수행
    * 민감한 개인 식별 정보(PII) 유출
    * 데이터 유출

## 모범 사례

### ID 및 권한 부여

*도구*가 외부 시스템에서 작업을 수행하는 데 사용하는 ID는 보안 관점에서 중요한 설계 고려 사항입니다. 동일한 에이전트 내의 다른 도구들은 서로 다른 전략으로 구성될 수 있으므로, 에이전트 구성에 대해 논의할 때 주의가 필요합니다.

#### 에이전트 인증 (Agent-Auth)

**도구는 에이전트 자체의 ID**(예: 서비스 계정)를 사용하여 외부 시스템과 상호작용합니다. 에이전트의 ID는 데이터베이스의 IAM 정책에 에이전트의 서비스 계정을 읽기 접근 권한으로 추가하는 것처럼 외부 시스템의 접근 정책에 명시적으로 승인되어야 합니다. 이러한 정책은 에이전트가 개발자가 의도한 작업만 수행하도록 제한합니다. 리소스에 읽기 전용 권한을 부여함으로써, 모델이 어떤 결정을 내리든 도구는 쓰기 작업을 수행할 수 없게 됩니다.

이 접근 방식은 구현이 간단하며, **모든 사용자가 동일한 수준의 접근 권한을 공유하는 에이전트에 적합합니다.** 모든 사용자가 동일한 접근 수준을 갖지 않는 경우, 이러한 접근 방식만으로는 충분한 보호를 제공하지 못하므로 아래의 다른 기술들과 보완해야 합니다. 도구 구현 시, 모든 에이전트의 작업이 에이전트로부터 오는 것처럼 보이므로, 사용자에 대한 작업 귀속을 유지하기 위해 로그가 생성되도록 해야 합니다.

#### 사용자 인증 (User Auth)

도구는 **"제어하는 사용자"의 ID**(예: 웹 애플리케이션의 프론트엔드와 상호작용하는 사람)를 사용하여 외부 시스템과 상호작용합니다. ADK에서는 일반적으로 OAuth를 사용하여 구현됩니다. 에이전트는 프론트엔드와 상호작용하여 OAuth 토큰을 획득한 다음, 도구는 외부 작업을 수행할 때 이 토큰을 사용합니다. 외부 시스템은 제어하는 사용자 자신이 해당 작업을 수행할 권한이 있는 경우에만 작업을 승인합니다.

사용자 인증은 에이전트가 사용자 자신이 수행할 수 있었던 작업만 수행한다는 장점이 있습니다. 이는 악의적인 사용자가 에이전트를 남용하여 추가 데이터에 접근할 위험을 크게 줄여줍니다. 그러나 대부분의 일반적인 위임 구현은 위임할 권한 집합(즉, OAuth 스코프)이 고정되어 있습니다. 종종 이러한 스코프는 에이전트가 실제로 필요로 하는 접근 권한보다 넓기 때문에, 에이전트 작업을 더욱 제한하기 위해 아래의 기술들이 필요합니다.

### 입력 및 출력을 스크리닝하는 가드레일

#### 도구 내 가드레일

도구는 보안을 염두에 두고 설계할 수 있습니다. 모델이 수행하기를 원하는 작업만 노출하고 그 외에는 아무것도 노출하지 않는 도구를 만들 수 있습니다. 에이전트에 제공하는 작업 범위를 제한함으로써, 에이전트가 절대로 수행해서는 안 되는 악성 작업의 유형을 결정론적으로 제거할 수 있습니다.

도구 내 가드레일은 개발자가 각 도구 인스턴스에 대한 제한을 설정하는 데 사용할 수 있는 결정론적 제어를 노출하는, 공통적이고 재사용 가능한 도구를 만드는 접근 방식입니다.

이 접근 방식은 도구가 두 가지 유형의 입력을 받는다는 사실에 의존합니다: 모델에 의해 설정되는 인수(arguments)와, 에이전트 개발자에 의해 결정론적으로 설정될 수 있는 [**`도구 컨텍스트(Tool Context)`**](../tools/index.md#tool-context)입니다. 우리는 모델이 예상대로 작동하는지 검증하기 위해 결정론적으로 설정된 정보에 의존할 수 있습니다.

예를 들어, 쿼리 도구는 도구 컨텍스트에서 정책을 읽도록 설계될 수 있습니다.

=== "Python"

    ```py
    # 개념적 예시: 도구 컨텍스트를 위한 정책 데이터 설정
    # 실제 ADK 앱에서는 InvocationContext.session.state에 설정되거나
    # 도구 초기화 중에 전달된 후 ToolContext를 통해 검색될 수 있습니다.

    policy = {} # policy가 딕셔너리라고 가정
    policy['select_only'] = True
    policy['tables'] = ['mytable1', 'mytable2']

    # 개념적: 나중에 ToolContext를 통해 도구가 접근할 수 있는 곳에 정책 저장.
    # 이 특정 줄은 실제로는 다르게 보일 수 있습니다.
    # 예를 들어, 세션 상태에 저장:
    invocation_context.session.state["query_tool_policy"] = policy

    # 또는 도구 초기화 시 전달:
    query_tool = QueryTool(policy=policy)
    # 이 예시에서는 접근 가능한 곳에 저장된다고 가정합니다.
    ```

=== "Go"

    ```go
    // 개념적 예시: 도구 컨텍스트를 위한 정책 데이터 설정
    // 실제 ADK 앱에서는 세션 상태 서비스를 사용하여 설정될 수 있습니다.
    // `ctx`는 콜백이나 커스텀 에이전트에서 사용 가능한 `agent.Context`입니다.

    policy := map[string]interface{}{
    	"select_only": true,
    	"tables":      []string{"mytable1", "mytable2"},
    }

    // 개념적: 나중에 ToolContext를 통해 도구가 접근할 수 있는 곳에 정책 저장.
    // 이 특정 줄은 실제로는 다르게 보일 수 있습니다.
    // 예를 들어, 세션 상태에 저장:
    if err := ctx.Session().State().Set("query_tool_policy", policy); err != nil {
        // 오류 처리, 예: 로깅.
    }

    // 또는 도구 초기화 시 전달:
    // queryTool := NewQueryTool(policy)
    // 이 예시에서는 접근 가능한 곳에 저장된다고 가정합니다.
    ```

=== "Java"

    ```java
    // 개념적 예시: 도구 컨텍스트를 위한 정책 데이터 설정
    // 실제 ADK 앱에서는 InvocationContext.session.state에 설정되거나
    // 도구 초기화 중에 전달된 후 ToolContext를 통해 검색될 수 있습니다.

    policy = new HashMap<String, Object>(); // policy가 Map이라고 가정
    policy.put("select_only", true);
    policy.put("tables", new ArrayList<>("mytable1", "mytable2"));

    // 개념적: 나중에 ToolContext를 통해 도구가 접근할 수 있는 곳에 정책 저장.
    // 이 특정 줄은 실제로는 다르게 보일 수 있습니다.
    // 예를 들어, 세션 상태에 저장:
    invocationContext.session().state().put("query_tool_policy", policy);

    // 또는 도구 초기화 시 전달:
    query_tool = QueryTool(policy);
    // 이 예시에서는 접근 가능한 곳에 저장된다고 가정합니다.
    ```

도구 실행 중에, [**`도구 컨텍스트(Tool Context)`**](../tools/index.md#tool-context)가 도구에 전달됩니다:

=== "Python"

    ```py
    def query(query: str, tool_context: ToolContext) -> str | dict:
      # 'policy'가 컨텍스트에서 검색된다고 가정, 예: 세션 상태를 통해:
      # policy = tool_context.invocation_context.session.state.get('query_tool_policy', {})

      # --- 플레이스홀더 정책 강제 ---
      policy = tool_context.invocation_context.session.state.get('query_tool_policy', {}) # 검색 예시
      actual_tables = explainQuery(query) # 가상 함수 호출

      if not set(actual_tables).issubset(set(policy.get('tables', []))):
        # 모델에 오류 메시지 반환
        allowed = ", ".join(policy.get('tables', ['(정의되지 않음)']))
        return f"오류: 쿼리가 승인되지 않은 테이블을 대상으로 합니다. 허용됨: {allowed}"

      if policy.get('select_only', False):
           if not query.strip().upper().startswith("SELECT"):
               return "오류: 정책은 쿼리를 SELECT 문으로만 제한합니다."
      # --- 정책 강제 종료 ---

      print(f"검증된 쿼리 실행 (가상): {query}")
      return {"status": "success", "results": [...]} # 성공적인 반환 예시
    ```

=== "Go"

    ```go
    import (
    	"fmt"
    	"strings"

    	"google.golang.org/adk/tool"
    )

    func query(query string, toolContext *tool.Context) (any, error) {
    	// 'policy'가 컨텍스트에서 검색된다고 가정, 예: 세션 상태를 통해:
    	policyAny, err := toolContext.State().Get("query_tool_policy")
    	if err != nil {
    		return nil, fmt.Errorf("정책을 검색할 수 없음: %w", err)
    	}    	policy, _ := policyAny.(map[string]interface{})
    	actualTables := explainQuery(query) // 가상 함수 호출

    	// --- 플레이스홀더 정책 강제 ---
    	if tables, ok := policy["tables"].([]string); ok {
    		if !isSubset(actualTables, tables) {
    			// 실패를 알리는 오류 반환
    			allowed := strings.Join(tables, ", ")
    			if allowed == "" {
    				allowed = "(정의되지 않음)"
    			}
    			return nil, fmt.Errorf("쿼리가 승인되지 않은 테이블을 대상으로 합니다. 허용됨: %s", allowed)
    		}
    	}

    	if selectOnly, _ := policy["select_only"].(bool); selectOnly {
    		if !strings.HasPrefix(strings.ToUpper(strings.TrimSpace(query)), "SELECT") {
    			return nil, fmt.Errorf("정책은 쿼리를 SELECT 문으로만 제한합니다")
    		}
    	}
    	// --- 정책 강제 종료 ---

    	fmt.Printf("검증된 쿼리 실행 (가상): %s\n", query)
    	return map[string]interface{}{"status": "success", "results": []string{"..."}}, nil
    }

    // a가 b의 부분 집합인지 확인하는 헬퍼 함수
    func isSubset(a, b []string) bool {
    	set := make(map[string]bool)
    	for _, item := range b {
    		set[item] = true
    	}
    	for _, item := range a {
    		if _, found := set[item]; !found {
    			return false
    		}
    	}
    	return true
    }
    ```

=== "Java"

    ```java
    import com.google.adk.tools.ToolContext;
    import java.util.*;

    class ToolContextQuery {

      public Object query(String query, ToolContext toolContext) {

        // 'policy'가 컨텍스트에서 검색된다고 가정, 예: 세션 상태를 통해:
        Map<String, Object> queryToolPolicy =
            toolContext.invocationContext.session().state().getOrDefault("query_tool_policy", null);
        List<String> actualTables = explainQuery(query);

        // --- 플레이스홀더 정책 강제 ---
        if (!queryToolPolicy.get("tables").containsAll(actualTables)) {
          List<String> allowedPolicyTables =
              (List<String>) queryToolPolicy.getOrDefault("tables", new ArrayList<String>());

          String allowedTablesString =
              allowedPolicyTables.isEmpty() ? "(정의되지 않음)" : String.join(", ", allowedPolicyTables);

          return String.format(
              "오류: 쿼리가 승인되지 않은 테이블을 대상으로 합니다. 허용됨: %s", allowedTablesString);
        }

        if (!queryToolPolicy.get("select_only")) {
          if (!query.trim().toUpperCase().startswith("SELECT")) {
            return "오류: 정책은 쿼리를 SELECT 문으로만 제한합니다.";
          }
        }
        // --- 정책 강제 종료 ---

        System.out.printf("검증된 쿼리 실행 (가상) %s:", query);
        Map<String, Object> successResult = new HashMap<>();
        successResult.put("status", "success");
        successResult.put("results", Arrays.asList("result_item1", "result_item2"));
        return successResult;
      }
    }
    ```

#### Gemini 내장 안전 기능

Gemini 모델은 콘텐츠 및 브랜드 안전성을 향상시키는 데 활용할 수 있는 내장된 안전 메커니즘을 갖추고 있습니다.

* **콘텐츠 안전 필터**: [콘텐츠 필터](https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/configure-safety-attributes)는 유해 콘텐츠의 출력을 차단하는 데 도움이 됩니다. 이 필터들은 모델을 탈옥하려는 위협 행위자에 대한 다계층 방어의 일부로서 Gemini 모델과 독립적으로 작동합니다. Vertex AI의 Gemini 모델은 두 가지 유형의 콘텐츠 필터를 사용합니다:
* **구성 불가 안전 필터**는 아동 성 학대 자료(CSAM) 및 개인 식별 정보(PII)와 같은 금지된 콘텐츠를 포함하는 출력을 자동으로 차단합니다.
* **구성 가능 콘텐츠 필터**는 확률 및 심각도 점수를 기반으로 네 가지 유해 범주(증오심 표현, 괴롭힘, 성적으로 노골적인 내용, 위험한 콘텐츠)에 대한 차단 임계값을 정의할 수 있게 합니다. 이 필터들은 기본적으로 꺼져 있지만 필요에 따라 구성할 수 있습니다.
* **안전을 위한 시스템 지침**: Vertex AI의 Gemini 모델에 대한 [시스템 지침](https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/safety-system-instructions)은 모델이 어떻게 행동하고 어떤 종류의 콘텐츠를 생성해야 하는지에 대한 직접적인 지침을 제공합니다. 구체적인 지침을 제공함으로써, 조직의 고유한 요구를 충족시키기 위해 모델이 바람직하지 않은 콘텐츠를 생성하지 않도록 사전에 유도할 수 있습니다. 금지되거나 민감한 주제, 면책 조항 언어와 같은 콘텐츠 안전 가이드라인을 정의하고, 모델의 출력이 브랜드의 목소리, 톤, 가치, 대상 고객과 일치하도록 브랜드 안전 가이드라인을 정의하는 시스템 지침을 작성할 수 있습니다.

이러한 조치들은 콘텐츠 안전성에 대해 강력하지만, 에이전트의 의도 불일치, 안전하지 않은 작업, 브랜드 안전성 위험을 줄이기 위해서는 추가적인 검사가 필요합니다.

#### 보안 가드레일을 위한 콜백 및 플러그인

콜백은 도구 및 모델 I/O에 사전 검증을 추가하는 간단하고 에이전트별 방법을 제공하는 반면, 플러그인은 여러 에이전트에 걸쳐 일반적인 보안 정책을 구현하기 위한 재사용 가능한 솔루션을 제공합니다.

가드레일을 추가하기 위해 도구를 수정할 수 없는 경우, [**`도구 실행 전 콜백(Before Tool Callback)`**](../callbacks/types-of-callbacks.md#before-tool-callback) 함수를 사용하여 호출의 사전 검증을 추가할 수 있습니다. 콜백은 에이전트의 상태, 요청된 도구 및 매개변수에 접근할 수 있습니다. 이 접근 방식은 매우 일반적이며, 재사용 가능한 도구 정책의 공통 라이브러리를 만드는 데에도 사용할 수 있습니다. 그러나 가드레일을 강제하기 위한 정보가 매개변수에서 직접 보이지 않는 경우 모든 도구에 적용할 수 없을 수도 있습니다.

=== "Python"

    ```py
    # 가상 콜백 함수
    def validate_tool_params(
        callback_context: CallbackContext, # 올바른 컨텍스트 타입
        tool: BaseTool,
        args: Dict[str, Any],
        tool_context: ToolContext
        ) -> Optional[Dict]: # before_tool_callback의 올바른 반환 타입

      print(f"콜백 트리거됨. 도구: {tool.name}, 인수: {args}")

      # 검증 예시: 상태에서 가져온 필수 사용자 ID가 인수와 일치하는지 확인
      expected_user_id = callback_context.state.get("session_user_id")
      actual_user_id_in_args = args.get("user_id_param") # 도구가 'user_id_param'을 받는다고 가정

      if actual_user_id_in_args != expected_user_id:
          print("검증 실패: 사용자 ID 불일치!")
          # 도구 실행을 막고 피드백을 제공하기 위해 딕셔너리 반환
          return {"error": f"도구 호출 차단됨: 사용자 ID 불일치."}

      # 검증 통과 시 도구 호출을 계속하도록 None 반환
      print("콜백 검증 통과됨.")
      return None

    # 가상 에이전트 설정
    root_agent = LlmAgent( # 특정 에이전트 타입 사용
        model='gemini-2.0-flash',
        name='root_agent',
        instruction="...",
        before_tool_callback=validate_tool_params, # 콜백 할당
        tools = [
          # ... 도구 함수 또는 Tool 인스턴스 목록 ...
          # 예: query_tool_instance
        ]
    )
    ```

=== "Go"

    ```go
    import (
    	"fmt"
    	"reflect"

    	"google.golang.org/adk/agent/llmagent"
    	"google.golang.org/adk/tool"
    )

    // 가상 콜백 함수
    func validateToolParams(
    	ctx tool.Context,
    	t tool.Tool,
    	args map[string]any,
    ) (map[string]any, error) {
    	fmt.Printf("콜백 트리거됨. 도구: %s, 인수: %v\n", t.Name(), args)

    	// 검증 예시: 상태에서 가져온 필수 사용자 ID가 인수와 일치하는지 확인
    	expectedUserIDVal, err := ctx.State().Get("session_user_id")
    	if err != nil {
    		// 이는 예기치 않은 실패이므로 오류를 반환합니다.
    		return nil, fmt.Errorf("내부 오류: 상태에서 session_user_id를 찾을 수 없음: %w", err)
    	}
    	expectedUserID, ok := expectedUserIDVal.(string)
    	if !ok {
    		return nil, fmt.Errorf("내부 오류: 상태의 session_user_id가 문자열이 아님, 타입: %T", expectedUserIDVal)
    	}

    	actualUserIDInArgs, exists := args["user_id_param"]
    	if !exists {
    		// user_id_param이 인수에 없는 경우 처리
    		fmt.Println("검증 실패: 인수에서 user_id_param 누락!")
    		return map[string]any{"error": "도구 호출 차단됨: 인수에서 user_id_param 누락."}, nil
    	}

    	actualUserID, ok := actualUserIDInArgs.(string)
    	if !ok {
    		// user_id_param이 문자열이 아닌 경우 처리
    		fmt.Println("검증 실패: user_id_param이 문자열이 아님!")
    		return map[string]any{"error": "도구 호출 차단됨: user_id_param이 문자열이 아님."}, nil
    	}

    	if actualUserID != expectedUserID {
    		fmt.Println("검증 실패: 사용자 ID 불일치!")
    		// 도구 실행을 막고 모델에 피드백을 제공하기 위해 맵 반환.
    		// 이는 Go 오류가 아니라 에이전트를 위한 메시지입니다.
    		return map[string]any{"error": "도구 호출 차단됨: 사용자 ID 불일치."}, nil
    	}
    	// 검증 통과 시 도구 호출을 계속하도록 nil, nil 반환
    	fmt.Println("콜백 검증 통과됨.")
    	return nil, nil
    }

    // 가상 에이전트 설정
    // rootAgent, err := llmagent.New(llmagent.Config{
    // 	Model: "gemini-2.0-flash",
    // 	Name: "root_agent",
    // 	Instruction: "...",
    // 	BeforeToolCallbacks: []llmagent.BeforeToolCallback{validateToolParams},
    // 	Tools: []tool.Tool{queryToolInstance},
    // })
    ```

=== "Java"

    ```java
    // 가상 콜백 함수
    public Optional<Map<String, Object>> validateToolParams(
      CallbackContext callbackContext,
      Tool baseTool,
      Map<String, Object> input,
      ToolContext toolContext) {

    System.out.printf("콜백 트리거됨. 도구: %s, 인수: %s", baseTool.name(), input);

    // 검증 예시: 상태에서 가져온 필수 사용자 ID가 입력 매개변수와 일치하는지 확인
    Object expectedUserId = callbackContext.state().get("session_user_id");
    Object actualUserIdInput = input.get("user_id_param"); // 도구가 'user_id_param'을 받는다고 가정

    if (!actualUserIdInput.equals(expectedUserId)) {
      System.out.println("검증 실패: 사용자 ID 불일치!");
      // 도구 실행을 막고 피드백을 제공하기 위해 반환
      return Optional.of(Map.of("error", "도구 호출 차단됨: 사용자 ID 불일치."));
    }

    // 검증 통과 시 도구 호출을 계속하도록 반환
    System.out.println("콜백 검증 통과됨.");
    return Optional.empty();
    }

    // 가상 에이전트 설정
    public void runAgent() {
    LlmAgent agent =
        LlmAgent.builder()
            .model("gemini-2.0-flash")
            .name("AgentWithBeforeToolCallback")
            .instruction("...")
            .beforeToolCallback(this::validateToolParams) // 콜백 할당
            .tools(anyToolToUse) // 사용할 도구 정의
            .build();
    }
    ```

그러나 에이전트 애플리케이션에 보안 가드레일을 추가할 때, 단일 에이전트에 국한되지 않는 정책을 구현하는 데에는 플러그인이 권장되는 접근 방식입니다. 플러그인은 자체 포함되고 모듈식으로 설계되어 특정 보안 정책에 대한 개별 플러그인을 만들고, 이를 러너 수준에서 전역적으로 적용할 수 있습니다. 이는 보안 플러그인을 한 번 구성하면 러너를 사용하는 모든 에이전트에 적용되어 반복적인 코드 없이 전체 애플리케이션에 걸쳐 일관된 보안 가드레일을 보장할 수 있음을 의미합니다.

몇 가지 예는 다음과 같습니다:

* **Gemini 심판 플러그인(Gemini as a Judge Plugin)**: 이 플러그인은 Gemini Flash Lite를 사용하여 사용자 입력, 도구 입출력, 에이전트의 응답에 대해 적절성, 프롬프트 인젝션, 탈옥 탐지를 평가합니다. 이 플러그인은 Gemini를 안전 필터로 구성하여 콘텐츠 안전성, 브랜드 안전성, 에이전트 의도 불일치를 완화합니다. 플러그인은 사용자 입력, 도구 입출력, 모델 출력을 Gemini Flash Lite에 전달하도록 구성되며, Gemini Flash Lite가 에이전트에 대한 입력이 안전한지 아닌지를 결정합니다. Gemini가 입력이 안전하지 않다고 판단하면 에이전트는 미리 정해진 응답을 반환합니다: "죄송하지만 도와드릴 수 없습니다. 다른 것을 도와드릴까요?".

* **Model Armor 플러그인**: 지정된 에이전트 실행 지점에서 잠재적인 콘텐츠 안전 위반을 확인하기 위해 Model Armor API를 쿼리하는 플러그인입니다. *Gemini 심판* 플러그인과 유사하게, Model Armor가 유해 콘텐츠 일치를 발견하면 사용자에게 미리 정해진 응답을 반환합니다.

* **PII 편집 플러그인(PII Redaction Plugin)**: [도구 실행 전 콜백](/adk-docs/plugins/#tool-callbacks)을 위해 설계된 전문화된 플러그인으로, 개인 식별 정보가 도구에 의해 처리되거나 외부 서비스로 전송되기 전에 이를 편집하기 위해 특별히 만들어졌습니다.

### 샌드박스화된 코드 실행

코드 실행은 추가적인 보안 영향을 미치는 특별한 도구입니다. 모델이 생성한 코드가 로컬 환경을 손상시켜 잠재적으로 보안 문제를 일으키는 것을 방지하기 위해 샌드박싱을 사용해야 합니다.

Google과 ADK는 안전한 코드 실행을 위한 여러 옵션을 제공합니다. [Vertex Gemini Enterprise API 코드 실행 기능](https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/code-execution-api)은 `tool_execution` 도구를 활성화하여 에이전트가 서버 측에서 샌드박스화된 코드 실행을 활용할 수 있게 합니다. 데이터 분석을 수행하는 코드의 경우, ADK의 [내장 코드 실행기](../tools/built-in-tools.md#code-execution) 도구를 사용하여 [Vertex Code Interpreter 확장 기능](https://cloud.google.com/vertex-ai/generative-ai/docs/extensions/code-interpreter)을 호출할 수 있습니다.

이러한 옵션 중 어느 것도 요구 사항을 만족시키지 못하는 경우, ADK에서 제공하는 빌딩 블록을 사용하여 자체 코드 실행기를 구축할 수 있습니다. 실행 환경은 밀폐형으로 만드는 것을 권장합니다: 제어되지 않는 데이터 유출을 피하기 위해 네트워크 연결 및 API 호출을 허용하지 않고, 사용자 간 데이터 유출 우려를 없애기 위해 실행 간 데이터를 완전히 정리해야 합니다.

### 평가

[에이전트 평가](../evaluate/index.md)를 참조하세요.

### VPC-SC 경계 및 네트워크 제어

에이전트를 VPC-SC 경계 내에서 실행하면 모든 API 호출이 경계 내의 리소스만 조작하도록 보장되어 데이터 유출 가능성을 줄일 수 있습니다.

그러나 ID와 경계는 에이전트 작업에 대한 대략적인 제어만 제공합니다. 도구 사용 가드레일은 이러한 한계를 완화하고, 에이전트 개발자가 허용할 작업을 세밀하게 제어할 수 있는 더 많은 권한을 부여합니다.

### 기타 보안 위험

#### UI에서 모델이 생성한 콘텐츠는 항상 이스케이프 처리하기

에이전트 출력이 브라우저에 시각화될 때 주의해야 합니다. UI에서 HTML 또는 JS 콘텐츠가 제대로 이스케이프 처리되지 않으면, 모델이 반환한 텍스트가 실행되어 데이터 유출로 이어질 수 있습니다. 예를 들어, 간접적인 프롬프트 인젝션은 모델을 속여 브라우저가 세션 콘텐츠를 제3자 사이트로 보내도록 하는 `img` 태그를 포함하게 하거나, 클릭 시 외부 사이트로 데이터를 전송하는 URL을 구성할 수 있습니다. 이러한 콘텐츠를 적절히 이스케이프 처리하여 모델이 생성한 텍스트가 브라우저에 의해 코드로 해석되지 않도록 해야 합니다.