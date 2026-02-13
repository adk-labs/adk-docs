---
catalog_title: Code Execution Tool with Agent Engine
catalog_description: Run AI-generated code in a secure and scalable GKE environment
catalog_icon: /adk-docs/integrations/assets/vertex-ai.png
catalog_tags: ["code", "google"]
---
# 에이전트 엔진을 사용한 코드 실행 도구

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.17.0</span><span class="lst-preview">미리보기</span>
</div>

에이전트 엔진 코드 실행 ADK 도구는 [Google Cloud 에이전트 엔진](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview) 서비스를 사용하여 AI 생성 코드를 실행하기 위한 저지연, 고효율 방법을 제공합니다. 이 도구는 에이전트 워크플로에 맞게 빠른 실행을 위해 설계되었으며 보안 향상을 위해 샌드박스 환경을 사용합니다. 코드 실행 도구를 사용하면 여러 요청에 걸쳐 코드와 데이터가 유지되므로 다음을 포함한 복잡한 다단계 코딩 작업을 수행할 수 있습니다.

-   **코드 개발 및 디버깅:** 여러 요청에 걸쳐 코드 버전을 테스트하고 반복하는 에이전트 작업을 만듭니다.
-   **데이터 분석을 통한 코드:** 최대 100MB의 데이터 파일을 업로드하고 각 코드 실행에 대해 데이터를 다시 로드할 필요 없이 여러 코드 기반 분석을 실행합니다.

이 코드 실행 도구는 에이전트 엔진 제품군의 일부이지만 에이전트를 에이전트 엔진에 배포하여 사용할 필요는 없습니다. 에이전트를 로컬 또는 다른 서비스에서 실행하고 이 도구를 사용할 수 있습니다. 에이전트 엔진의 코드 실행 기능에 대한 자세한 내용은 [에이전트 엔진 코드 실행](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/code-execution/overview) 설명서를 참조하세요.

!!! example "미리보기 출시"
    에이전트 엔진 코드 실행 기능은 미리보기 출시입니다. 자세한 내용은 [출시 단계 설명](https://cloud.google.com/products#product-launch-stages)을 참조하세요.

## 도구 사용

에이전트 엔진 코드 실행 도구를 사용하려면 ADK 에이전트와 함께 도구를 사용하기 전에 Google Cloud 에이전트 엔진으로 샌드박스 환경을 만들어야 합니다.

ADK 에이전트와 함께 코드 실행 도구를 사용하려면:

1.  에이전트 엔진 [코드 실행 빠른 시작](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/code-execution/quickstart)의 지침에 따라 코드 실행 샌드박스 환경을 만듭니다.
1.  샌드박스 환경을 만든 Google Cloud 프로젝트에 액세스하기 위한 설정으로 ADK 에이전트를 만듭니다.
1.  다음 코드 예제는 코드 실행기 도구를 사용하도록 구성된 에이전트를 보여줍니다. `SANDBOX_RESOURCE_NAME`을 만든 샌드박스 환경 리소스 이름으로 바꿉니다.

```python
from google.adk.agents.llm_agent import Agent
from google.adk.code_executors.agent_engine_sandbox_code_executor import AgentEngineSandboxCodeExecutor

root_agent = Agent(
    model="gemini-2.5-flash",
    name="agent_engine_code_execution_agent",
    instruction="당신은 질문에 답하고 문제를 해결하기 위해 코드를 작성하고 실행할 수 있는 유용한 에이전트입니다.",
    code_executor=AgentEngineSandboxCodeExecutor(
        sandbox_resource_name="SANDBOX_RESOURCE_NAME",
    ),
)
```

`sandbox_resource_name` 값의 예상 형식과 대체 `agent_engine_resource_name` 매개변수에 대한 자세한 내용은 [구성 매개변수](#config-parameters)를 참조하세요. 도구에 대한 권장 시스템 지침을 포함한 고급 예제는 [고급 예제](#advanced-example) 또는 전체 [에이전트 코드 예제](https://github.com/google/adk-python/tree/main/contributing/samples/agent_engine_code_execution)를 참조하세요.

## 작동 방식

`AgentEngineCodeExecutor` 도구는 에이전트 작업 전체에서 단일 샌드박스를 유지하므로 샌드박스의 상태가 ADK 워크플로 세션 내의 모든 작업에서 유지됩니다.

1.  **샌드박스 생성:** 코드 실행이 필요한 다단계 작업의 경우 에이전트 엔진은 지정된 언어 및 시스템 구성으로 샌드박스를 만들어 코드 실행 환경을 격리합니다. 미리 만들어진 샌드박스가 없는 경우 코드 실행 도구는 기본 설정을 사용하여 자동으로 샌드박스를 만듭니다.
1.  **지속성을 통한 코드 실행:** 도구 호출을 위해 AI가 생성한 코드는 샌드박스로 스트리밍된 다음 격리된 환경 내에서 실행됩니다. 실행 후 샌드박스는 동일한 에이전트의 다음 도구 호출을 위해 변수, 가져온 모듈 및 파일 상태를 보존하면서 동일한 세션 내의 후속 도구 호출에 대해 *활성 상태를 유지*합니다.
1.  **결과 검색:** 표준 출력 및 캡처된 모든 오류 스트림이 수집되어 호출 에이전트로 다시 전달됩니다.
1.  **샌드박스 정리:** 에이전트 작업 또는 대화가 끝나면 에이전트는 샌드박스를 명시적으로 삭제하거나 샌드박스를 만들 때 지정된 샌드박스의 TTL 기능을 사용할 수 있습니다.

## 주요 이점

-   **지속적인 상태:** 여러 도구 호출 간에 데이터 조작 또는 변수 컨텍스트를 전달해야 하는 복잡한 작업을 해결합니다.
-   **대상 격리:** 강력한 프로세스 수준 격리를 제공하여 도구 코드 실행이 안전하면서도 가볍게 유지되도록 합니다.
-   **에이전트 엔진 통합:** 에이전트 엔진 도구 사용 및 오케스트레이션 계층에 긴밀하게 통합됩니다.
-   **저지연 성능:** 속도를 위해 설계되어 에이전트가 상당한 오버헤드 없이 복잡한 도구 사용 워크플로를 효율적으로 실행할 수 있습니다.
-   **유연한 컴퓨팅 구성:** 특정 프로그래밍 언어, 처리 능력 및 메모리 구성으로 샌드박스를 만듭니다.

## 시스템 요구 사항¶

ADK 에이전트와 함께 에이전트 엔진 코드 실행 도구를 성공적으로 사용하려면 다음 요구 사항을 충족해야 합니다.

-   Vertex API가 활성화된 Google Cloud 프로젝트
-   에이전트의 서비스 계정에는 다음을 수행할 수 있는 **roles/aiplatform.user** 역할이 필요합니다.
    -   코드 실행 샌드박스 생성, 가져오기, 나열 및 삭제
    -   코드 실행 샌드박스 실행

## 구성 매개변수 {#config-parameters}

에이전트 엔진 코드 실행 도구에는 다음 매개변수가 있습니다. 다음 리소스 매개변수 중 하나를 설정해야 합니다.

-   **`sandbox_resource_name`**: 각 도구 호출에 사용하는 기존 샌드박스 환경에 대한 샌드박스 리소스 경로입니다. 예상되는 문자열 형식은 다음과 같습니다.
    ```
    projects/{$PROJECT_ID}/locations/{$LOCATION_ID}/reasoningEngines/{$REASONING_ENGINE_ID}/sandboxEnvironments/{$SANDBOX_ENVIRONMENT_ID}
    
    # 예:
    projects/my-vertex-agent-project/locations/us-central1/reasoningEngines/6842888880301111172/sandboxEnvironments/6545148888889161728
    ```
-   **`agent_engine_resource_name`**: 도구가 샌드박스 환경을 만드는 에이전트 엔진 리소스 이름입니다. 예상되는 문자열 형식은 다음과 같습니다.
    ```
    projects/{$PROJECT_ID}/locations/{$LOCATION_ID}/reasoningEngines/{$REASONING_ENGINE_ID}
    
    # 예:
    projects/my-vertex-agent-project/locations/us-central1/reasoningEngines/6842888880301111172
    ```

Google Cloud 에이전트 엔진의 API를 사용하여 다음 설정을 포함하여 Google Cloud 클라이언트 연결을 사용하여 에이전트 엔진 샌드박스 환경을 별도로 구성할 수 있습니다.

-   Python 및 JavaScript를 포함한 **프로그래밍 언어**
-   CPU 및 메모리 크기를 포함한 **컴퓨팅 환경**

Google Cloud 에이전트 엔진에 연결하고 샌드박스 환경을 구성하는 방법에 대한 자세한 내용은 에이전트 엔진 [코드 실행 빠른 시작](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/code-execution/quickstart#create_a_sandbox)을 참조하세요.

## 고급 예제 {#advanced-example}

다음 예제 코드는 ADK 에이전트에서 코드 실행기 도구 사용을 구현하는 방법을 보여줍니다. 이 예제에는 코드 실행에 대한 운영 지침을 설정하기 위한 `base_system_instruction` 절이 포함되어 있습니다. 이 지침 절은 선택 사항이지만 이 도구에서 최상의 결과를 얻으려면 강력히 권장됩니다.

```python
from google.adk.agents.llm_agent import Agent
from google.adk.code_executors.agent_engine_sandbox_code_executor import AgentEngineSandboxCodeExecutor

def base_system_instruction():
  """반환: 데이터 과학 에이전트 시스템 지침."""

  return """
  # 지침

  **목표:** 사용자가 데이터 분석 목표를 달성하도록 지원하고, **가정을 피하고 정확성을 보장하는 데 중점을 둡니다.** 해당 목표에 도달하는 데는 여러 단계가 포함될 수 있습니다. 코드를 생성해야 할 때 한 번에 목표를 해결할 필요는 없습니다. 한 번에 다음 단계만 생성하십시오.

  **코드 실행:** 제공된 모든 코드 스니펫은 샌드박스 환경 내에서 실행됩니다.

  **상태 유지:** 모든 코드 스니펫이 실행되고 변수는 환경에 유지됩니다. 변수를 다시 초기화할 필요가 없습니다. 파일을 다시 로드할 필요가 없습니다. 라이브러리를 다시 가져올 필요가 없습니다.

  **출력 가시성:** 데이터 탐색 및 분석을 위해 결과를 시각화하기 위해 항상 코드 실행 출력을 인쇄하십시오. 예:
    - pandas.DataFrame의 모양을 보려면 다음을 수행하십시오.
      ```tool_code
      print(df.shape)
      ```
      출력은 다음과 같이 표시됩니다.
      ```tool_outputs
      (49, 7)

      ```
    - 수치 계산 결과를 표시하려면:
      ```tool_code
      x = 10 ** 9 - 12 ** 5
      print(f'{{x=}}')
      ```
      출력은 다음과 같이 표시됩니다.
      ```tool_outputs
      x=999751168

      ```
    - ```tool_outputs를 직접 생성하지 마십시오.
    - 그런 다음 이 출력을 사용하여 다음 단계를 결정할 수 있습니다.
    - 변수만 인쇄하십시오(예: `print(f'{{variable=}}')`).

  **가정 없음:** **결정적으로 데이터의 특성이나 열 이름에 대한 가정을 피하십시오.** 데이터 자체에만 근거하여 결과를 도출하십시오. 항상 `explore_df`에서 얻은 정보를 사용하여 분석을 안내하십시오.

  **사용 가능한 파일:** 사용 가능한 파일 목록에 지정된 대로 사용 가능한 파일만 사용하십시오.

  **프롬프트의 데이터:** 일부 쿼리에는 프롬프트에 직접 입력 데이터가 포함되어 있습니다. 해당 데이터를 pandas DataFrame으로 구문 분석해야 합니다. 항상 모든 데이터를 구문 분석하십시오. 제공된 데이터를 편집하지 마십시오.

  **답변 가능성:** 일부 쿼리는 사용 가능한 데이터로 답변할 수 없을 수 있습니다. 이러한 경우 사용자에게 쿼리를 처리할 수 없는 이유를 알리고 요청을 이행하는 데 필요한 데이터 유형을 제안하십시오.

  """

root_agent = Agent(
    model="gemini-2.5-flash",
    name="agent_engine_code_execution_agent",
    instruction=base_system_instruction() + """


대화의 데이터와 컨텍스트를 보고 사용자의 쿼리를 지원해야 합니다.
최종 답변은 사용자 쿼리와 관련된 코드 및 코드 실행을 요약해야 합니다.

코드 실행 결과의 테이블과 같이 사용자 쿼리에 답변하기 위해 모든 데이터를 포함해야 합니다.
질문에 직접 답변할 수 없는 경우 위의 지침에 따라 다음 단계를 생성해야 합니다.
코드를 작성하여 직접 답변할 수 있는 질문인 경우 그렇게 해야 합니다.
질문에 답변할 데이터가 충분하지 않은 경우 사용자에게 명확한 설명을 요청해야 합니다.

`pip install ...`과 같이 직접 패키지를 설치해서는 안 됩니다.
추세를 그릴 때 x축을 기준으로 데이터를 정렬하고 순서를 지정해야 합니다.


""",
    code_executor=AgentEngineSandboxCodeExecutor(
        # 이미 있는 경우 샌드박스 리소스 이름으로 바꿉니다.
        sandbox_resource_name="SANDBOX_RESOURCE_NAME",
        # sandbox_resource_name이 설정되지 않은 경우 샌드박스를 만드는 데 사용되는 에이전트 엔진 리소스 이름으로 바꿉니다.
        # agent_engine_resource_name="AGENT_ENGINE_RESOURCE_NAME",
    ),
)
```

이 예제 코드를 사용하는 ADK 에이전트의 전체 버전은 [agent_engine_code_execution 샘플](https://github.com/google/adk-python/tree/main/contributing/samples/agent_engine_code_execution)을 참조하세요.
