---
catalog_title: Code Execution Tool with Agent Runtime
catalog_description: 안전하고 확장 가능한 GKE 환경에서 AI 생성 코드 실행
catalog_icon: /integrations/assets/agent-platform.svg
catalog_tags: ["code", "google"]
---


# ADK용 에이전트 런타임 코드 실행 도구

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.17.0</span>
</div>

에이전트 런타임 코드 실행 ADK 도구는 짧은 지연 시간과 높은
AI 생성 코드를 실행하는 효율적인 방법
[Google Cloud Agent Runtime](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)
서비스. 이 도구는 빠른 실행을 위해 설계되었으며 에이전트 워크플로에 맞게 조정되었습니다.
보안 강화를 위해 샌드박스 환경을 사용합니다. 코드 실행 도구
여러 요청에 걸쳐 코드와 데이터가 유지되도록 하여 복잡하고
다음을 포함한 다단계 코딩 작업:

- **코드 개발 및 디버깅:** 테스트하고 디버깅하는 에이전트 작업을 만듭니다.
    여러 요청에 걸쳐 코드 버전을 반복합니다.
- **데이터 분석이 포함된 코드:** 최대 100MB의 데이터 파일을 업로드하고 실행합니다.
    각 코드 실행에 대해 데이터를 다시 로드할 필요 없이 여러 코드 기반 분석을 수행합니다.

이 코드 실행 도구는 Agent Runtime 제품군의 일부이지만
이를 사용하려면 에이전트를 Agent Runtime에 배포해야 합니다. 에이전트를 실행할 수 있습니다
로컬로 또는 다른 서비스와 함께 이 도구를 사용하세요. 에 대한 자세한 내용은
에이전트 런타임의 코드 실행 기능은 다음을 참조하세요.
[Agent Runtime Code Execution](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/code-execution/overview)
문서.


## 도구 사용

에이전트 런타임 코드 실행 도구를 사용하려면 샌드박스를 생성해야 합니다.
ADK와 함께 도구를 사용하기 전에 Google Cloud Agent Runtime을 사용하는 환경
대리인.

ADK 에이전트와 함께 코드 실행 도구를 사용하려면 다음 안내를 따르세요.

1. 에이전트 런타임의 지침을 따릅니다.
    [Code Execution quickstart](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/code-execution/quickstart)
    코드 실행 샌드박스 환경을 만듭니다.
1. Google Cloud 프로젝트에 액세스하기 위한 설정으로 ADK 에이전트를 만듭니다.
    샌드박스 환경을 만든 곳입니다.
1. 다음 코드 예시는 코드를 사용하도록 구성된 에이전트를 보여줍니다.
    실행 도구. `SANDBOX_RESOURCE_NAME`를 샌드박스 환경으로 교체
    생성한 리소스 이름입니다.

```python
from google.adk.agents.llm_agent import Agent
from google.adk.code_executors.agent_engine_sandbox_code_executor import AgentEngineSandboxCodeExecutor

root_agent = Agent(
    model="gemini-flash-latest",
    name="agent_engine_code_execution_agent",
    instruction="You are a helpful agent that can write and execute code to answer questions and solve problems.",
    code_executor=AgentEngineSandboxCodeExecutor(
        sandbox_resource_name="SANDBOX_RESOURCE_NAME",
    ),
)
```

`sandbox_resource_name` 값의 예상 형식에 대한 자세한 내용과
대체 `agent_engine_resource_name` 매개변수는 [Configuration
parameters](#config-parameters)를 참조하세요. 다음을 포함한 좀 더 고급 예를 들어보면
도구에 권장되는 시스템 지침은 [Advanced
example](#advanced-example) 또는 전체 내용을 참조하세요.
[agent code example](https://github.com/google/adk-python/tree/main/contributing/samples/agent_engine_code_execution).

## 작동 방식

`AgentEngineCodeExecutor` 도구는 전체 기간 동안 단일 샌드박스를 유지합니다.
에이전트의 작업, 즉 샌드박스의 상태가 에이전트 내의 모든 작업에서 지속됨을 의미합니다.
ADK 워크플로 세션.

1. **샌드박스 생성:** 코드 실행이 필요한 다단계 작업의 경우,
    에이전트 런타임은 지정된 언어와 시스템으로 샌드박스를 생성합니다.
    구성, 코드 실행 환경을 격리합니다. 샌드박스가 없는 경우
    사전 생성된 코드 실행 도구는 다음을 사용하여 자동으로 생성합니다.
    기본 설정.
1. **지속성을 갖춘 코드 실행:** 도구 호출을 위한 AI 생성 코드
    샌드박스로 스트리밍된 후 격리된 환경 내에서 실행됩니다.
    환경. 실행 후 샌드박스는 후속 작업을 위해 *활성 상태로 유지*됩니다.
    동일한 세션 내 도구 호출, 변수 보존, 가져온 모듈,
    동일한 에이전트의 다음 도구 호출에 대한 파일 상태입니다.
1. **결과 검색:** 표준 출력 및 캡처된 오류
    스트림이 수집되어 호출 에이전트로 다시 전달됩니다.
1. **샌드박스 정리:** 에이전트 작업이나 대화가 끝나면
    에이전트는 샌드박스를 명시적으로 삭제하거나 TTL 기능을 사용할 수 있습니다.
    샌드박스를 만들 때 지정된 샌드박스입니다.

## 주요 이점

- **지속적 상태:** 데이터를 조작하거나
    변수 컨텍스트는 여러 도구 호출 간에 전달되어야 합니다.
- **대상 격리:** 강력한 프로세스 수준 격리를 제공합니다.
    경량을 유지하면서 도구 코드 실행이 안전한지 확인합니다.
- **에이전트 런타임 통합:** 에이전트 런타임에 긴밀하게 통합됨
    도구 사용 및 오케스트레이션 계층.
- **낮은 지연 성능:** 속도를 고려하여 설계되어 상담원이 다음 작업을 수행할 수 있습니다.
    상당한 오버헤드 없이 복잡한 도구 사용 워크플로를 효율적으로 실행합니다.
- **유연한 컴퓨팅 구성:** 특정 기능을 갖춘 샌드박스 생성
    프로그래밍 언어, 처리 능력 및 메모리 구성.

## 시스템 요구사항¶

에이전트 런타임을 성공적으로 사용하려면 다음 요구 사항을 충족해야 합니다.
ADK 에이전트를 사용한 코드 실행 도구:

- Agent Platform API가 활성화된 Google Cloud 프로젝트
- 에이전트의 서비스 계정에는 **roles/aiplatform.user** 역할이 필요합니다.
    다음을 허용합니다.
    - 코드 실행 샌드박스 생성, 가져오기, 나열 및 삭제
    - 코드 실행 샌드박스 실행

## 구성 매개변수 {#config-parameters}

에이전트 런타임 코드 실행 도구에는 다음 매개변수가 있습니다. 설정해야 합니다.
다음 리소스 매개변수 중 하나:

- **`sandbox_resource_name`** : 샌드박스 리소스 경로
    각 도구 호출에 사용되는 기존 샌드박스 환경입니다. 예상되는
문자열 형식은 다음과 같습니다.
    ```
    projects/{$PROJECT_ID}/locations/{$LOCATION_ID}/reasoningEngines/{$REASONING_ENGINE_ID}/sandboxEnvironments/{$SANDBOX_ENVIRONMENT_ID}

    # Example:
    projects/my-vertex-agent-project/locations/us-central1/reasoningEngines/6842888880301111172/sandboxEnvironments/6545148888889161728
    ```
- **`agent_engine_resource_name`**: 도구가 실행되는 에이전트 런타임 리소스 이름
샌드박스 환경을 만듭니다. 예상되는 문자열 형식은 다음과 같습니다.
    ```
    projects/{$PROJECT_ID}/locations/{$LOCATION_ID}/reasoningEngines/{$REASONING_ENGINE_ID}

    # Example:
    projects/my-vertex-agent-project/locations/us-central1/reasoningEngines/6842888880301111172
    ```

Google Cloud Agent Runtime의 API를 사용하여 에이전트 런타임 샌드박스를 구성할 수 있습니다.
다음을 포함하여 Google Cloud 클라이언트 연결을 사용하여 별도로 환경을 관리합니다.
다음 설정:

- **프로그래밍 언어**(Python 및 JavaScript 포함)
- CPU 및 메모리 크기를 포함한 **컴퓨팅 환경**

Google Cloud Agent Runtime 연결 및 구성에 대한 자세한 내용은
샌드박스 환경, 에이전트 런타임 참조
[Code Execution quickstart](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/code-execution/quickstart#create_a_sandbox).

## 고급 예 {#advanced-example}

다음 예제 코드는 Code Executor 도구 사용을 구현하는 방법을 보여줍니다.
ADK 에이전트에서. 이 예에는 설정할 `base_system_instruction` 절이 포함되어 있습니다.
코드 실행을 위한 운영 지침. 이 지시 조항은
선택 사항이지만 이 도구에서 최상의 결과를 얻으려면 강력히 권장됩니다.

```python
from google.adk.agents.llm_agent import Agent
from google.adk.code_executors.agent_engine_sandbox_code_executor import AgentEngineSandboxCodeExecutor

def base_system_instruction():
  """Returns: data science agent system instruction."""

  return """
  # Guidelines

  **Objective:** Assist the user in achieving their data analysis goals, **with emphasis on avoiding assumptions and ensuring accuracy.** Reaching that goal can involve multiple steps. When you need to generate code, you **don't** need to solve the goal in one go. Only generate the next step at a time.

  **Code Execution:** All code snippets provided will be executed within the sandbox environment.

  **Statefulness:** All code snippets are executed and the variables stays in the environment. You NEVER need to re-initialize variables. You NEVER need to reload files. You NEVER need to re-import libraries.

  **Output Visibility:** Always print the output of code execution to visualize results, especially for data exploration and analysis. For example:
    - To look a the shape of a pandas.DataFrame do:
      ```tool_code
      인쇄(df.shape)
      ```
      The output will be presented to you as:
      ```tool_outputs
      (49, 7)

      ```
    - To display the result of a numerical computation:
      ```tool_code
      x = 10 ** 9 - 12 ** 5
      인쇄(f'{{x=}}')
      ```
      The output will be presented to you as:
      ```tool_outputs
      x=999751168

      ```
    - You **never** generate ```tool_outputs yourself.
    - You can then use this output to decide on next steps.
    - Print just variables (e.g., `print(f'{{variable=}}')`.

  **No Assumptions:** **Crucially, avoid making assumptions about the nature of the data or column names.** Base findings solely on the data itself. Always use the information obtained from `explore_df` to guide your analysis.

  **Available files:** Only use the files that are available as specified in the list of available files.

  **Data in prompt:** Some queries contain the input data directly in the prompt. You have to parse that data into a pandas DataFrame. ALWAYS parse all the data. NEVER edit the data that are given to you.

  **Answerability:** Some queries may not be answerable with the available data. In those cases, inform the user why you cannot process their query and suggest what type of data would be needed to fulfill their request.

  """

root_agent = Agent(
    model="gemini-flash-latest",
    name="agent_engine_code_execution_agent",
    instruction=base_system_instruction() + """


You need to assist the user with their queries by looking at the data and the context in the conversation.
You final answer should summarize the code and code execution relevant to the user query.

You should include all pieces of data to answer the user query, such as the table from code execution results.
If you cannot answer the question directly, you should follow the guidelines above to generate the next step.
If the question can be answered directly with writing any code, you should do that.
If you doesn't have enough data to answer the question, you should ask for clarification from the user.

You should NEVER install any package on your own like `pip install ...`.
When plotting trends, you should make sure to sort and order the data by the x-axis.


""",
    code_executor=AgentEngineSandboxCodeExecutor(
        # Replace with your sandbox resource name if you already have one.
        sandbox_resource_name="SANDBOX_RESOURCE_NAME",
        # Replace with agent engine resource name used for creating sandbox if
        # sandbox_resource_name is not set:
        # agent_engine_resource_name="AGENT_ENGINE_RESOURCE_NAME",
    ),
)
```

이 예제 코드를 사용하는 ADK 에이전트의 전체 버전은 다음을 참조하세요.
[agent_engine_code_execution sample](https://github.com/google/adk-python/tree/main/contributing/samples/agent_engine_code_execution).
