---
catalog_title: Code Execution Tool with Agent Runtime
catalog_description: 안전하고 확장 가능한 환경에서 AI 생성 코드 실행
catalog_icon: /integrations/assets/agent-platform.svg
catalog_tags: ["code", "google"]
---


# ADK용 에이전트 런타임 코드 실행 도구

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.17.0</span>
</div>

Agent Runtime 코드 실행 ADK 도구는 [Google Cloud Agent Runtime](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview) 서비스를 사용하여 짧은 지연 시간(latency)으로 효율성 높게 AI 생성 코드를 실행할 수 있는 방법을 제공합니다. 이 도구는 빠른 실행을 위해 설계되었고 에이전트 워크플로에 최적화되어 있으며, 보안 강화를 위해 샌드박스 환경을 사용합니다. 코드 실행 도구를 사용하면 여러 요청에 걸쳐 코드와 데이터가 유지되므로 다음과 같은 복잡한 다단계 코딩 작업을 수행할 수 있습니다:

- **코드 개발 및 디버깅:** 여러 요청에 걸쳐 코드 버전을 테스트하고 반복 개선하는 에이전트 작업을 구성합니다.
- **데이터 분석이 포함된 코드:** 최대 100MB의 데이터 파일을 업로드하고, 매 코드 실행마다 데이터를 다시 로드할 필요 없이 코드 기반 분석을 여러 번 수행합니다.

이 코드 실행 도구는 Agent Runtime 제품군의 일부이지만, 이를 사용하기 위해 에이전트를 반드시 Agent Runtime에 배포할 필요는 없습니다. 로컬이나 다른 서비스에서 에이전트를 실행하면서도 이 도구를 사용할 수 있습니다. Agent Runtime의 코드 실행 기능에 대한 자세한 내용은 [Agent Runtime Code Execution](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/code-execution/overview) 문서를 참고하세요.


## 도구 사용

Agent Runtime 코드 실행 도구를 ADK 에이전트와 함께 사용하려면 먼저 Google Cloud Agent Runtime으로 샌드박스 환경을 생성해야 합니다.

ADK 에이전트와 함께 코드 실행 도구를 사용하려면 다음 단계를 따르세요:

1. Agent Runtime의 [Code Execution quickstart](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/code-execution/quickstart) 안내에 따라 코드 실행 샌드박스 환경을 생성합니다.
1. 샌드박스 환경을 생성한 Google Cloud 프로젝트에 액세스하도록 설정된 ADK 에이전트를 생성합니다.
1. 다음 코드 예시는 코드 실행 도구를 사용하도록 구성된 에이전트를 보여줍니다. `SANDBOX_RESOURCE_NAME`을 직접 생성한 샌드박스 환경 리소스 이름으로 바꾸세요.

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

`sandbox_resource_name` 값의 예상 형식과 대체 매개변수인 `agent_engine_resource_name`에 대한 자세한 내용은 [구성 매개변수](#config-parameters)를 참고하세요. 이 도구에 권장되는 시스템 지침을 포함한 고급 예시는 [고급 예시](#advanced-example) 또는 전체 [에이전트 코드 예시](https://github.com/google/adk-python/tree/main/contributing/samples/agent_engine_code_execution)를 참고하세요.

## 작동 방식

`AgentEngineSandboxCodeExecutor` 도구는 에이전트 작업 전반에 걸쳐 단일 샌드박스를 유지하므로, ADK 워크플로 세션 내의 모든 작업에서 샌드박스 상태가 유지됩니다.

1. **샌드박스 생성:** 코드 실행이 필요한 다단계 작업의 경우, Agent Runtime은 지정된 언어와 머신 구성으로 샌드박스를 생성하여 코드 실행 환경을 격리합니다. 미리 생성된 샌드박스가 없으면 코드 실행 도구가 기본 설정으로 샌드박스를 자동 생성합니다.
1. **상태 유지를 통한 코드 실행:** 도구 호출을 위해 AI가 생성한 코드가 샌드박스로 스트리밍된 뒤 격리된 환경 내에서 실행됩니다. 실행 후에도 샌드박스는 동일한 세션 내의 후속 도구 호출을 위해 *활성 상태로 유지*되며, 동일한 에이전트의 다음 도구 호출을 위해 변수, 임포트한 모듈, 파일 상태를 보존합니다.
1. **결과 조회:** 표준 출력과 캡처된 오류 스트림이 수집되어 호출한 에이전트로 다시 전달됩니다.
1. **샌드박스 정리:** 에이전트 작업이나 대화가 종료되면 에이전트가 샌드박스를 명시적으로 삭제하거나, 샌드박스 생성 시 지정한 TTL(Time-To-Live) 기능에 따라 자동으로 정리되게 할 수 있습니다.

## 주요 이점

- **지속적인 상태 유지:** 여러 도구 호출 간에 데이터 조작 결과나 변수 컨텍스트를 이어가야 하는 복잡한 작업을 해결할 수 있습니다.
- **정밀한 격리:** 가벼운 실행 환경을 유지하면서도 강력한 프로세스 수준 격리를 제공하여 도구 코드 실행의 안전성을 보장합니다.
- **Agent Runtime 통합:** Agent Runtime의 도구 사용 및 오케스트레이션 계층과 긴밀하게 통합되어 있습니다.
- **낮은 지연 시간 성능:** 빠른 실행을 염두에 두고 설계되어 에이전트가 큰 오버헤드 없이 복잡한 도구 사용 워크플로를 효율적으로 실행할 수 있습니다.
- **유연한 컴퓨팅 구성:** 특정 프로그래밍 언어, CPU 성능, 메모리 구성을 지정하여 샌드박스를 생성할 수 있습니다.

## 시스템 요구사항

ADK 에이전트와 함께 Agent Runtime 코드 실행 도구를 사용하려면 다음 요구사항을 충족해야 합니다:

- Agent Platform API가 활성화된 Google Cloud 프로젝트
- 에이전트의 서비스 계정에 부여된 **roles/aiplatform.user** 역할 (다음 작업을 허용함):
    - 코드 실행 샌드박스 생성, 조회, 목록 확인 및 삭제
    - 코드 실행 샌드박스에서 코드 실행

## 구성 매개변수 {#config-parameters}

Agent Runtime 코드 실행 도구는 다음 매개변수를 제공합니다. 다음 리소스 매개변수 중 하나를 반드시 설정해야 합니다:

- **`sandbox_resource_name`**: 각 도구 호출에 사용할 기존 샌드박스 환경의 리소스 경로입니다. 예상되는 문자열 형식은 다음과 같습니다:
    ```
    projects/{$PROJECT_ID}/locations/{$LOCATION_ID}/reasoningEngines/{$REASONING_ENGINE_ID}/sandboxEnvironments/{$SANDBOX_ENVIRONMENT_ID}

    # Example:
    projects/my-vertex-agent-project/locations/us-central1/reasoningEngines/6842888880301111172/sandboxEnvironments/6545148888889161728
    ```
- **`agent_engine_resource_name`**: 도구가 샌드박스 환경을 생성할 Agent Runtime 리소스 이름입니다. 예상되는 문자열 형식은 다음과 같습니다:
    ```
    projects/{$PROJECT_ID}/locations/{$LOCATION_ID}/reasoningEngines/{$REASONING_ENGINE_ID}

    # Example:
    projects/my-vertex-agent-project/locations/us-central1/reasoningEngines/6842888880301111172
    ```

Google Cloud 클라이언트 연결과 Google Cloud Agent Runtime API를 사용하여 다음 설정을 포함한 Agent Runtime 샌드박스 환경을 별도로 구성할 수 있습니다:

- **프로그래밍 언어** (Python 및 JavaScript 포함)
- CPU 및 메모리 크기를 포함한 **컴퓨팅 환경**

Google Cloud Agent Runtime 연결 및 샌드박스 환경 구성에 대한 자세한 내용은 Agent Runtime [Code Execution quickstart](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/code-execution/quickstart#create_a_sandbox)를 참고하세요.

## 고급 예시 {#advanced-example}

다음 예제 코드는 ADK 에이전트에서 코드 실행기(Code Executor) 도구를 구현하는 방법을 보여줍니다. 이 예시에는 코드 실행 운영 지침을 설정하는 `base_system_instruction` 함수가 포함되어 있습니다. 이 지침은 선택 사항이지만 이 도구에서 최상의 결과를 얻기 위해 강력히 권장됩니다.

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
      print(df.shape)
      ```
      The output will be presented to you as:
      ```tool_output
      (49, 7)

      ```
    - To display the result of a numerical computation:
      ```tool_code
      x = 10 ** 9 - 12 ** 5
      print(f'{{x=}}')
      ```
      The output will be presented to you as:
      ```tool_output
      x=999751168

      ```
    - You **never** generate ```tool_output yourself.
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

이 예제 코드를 사용하는 전체 ADK 에이전트 구현은 [agent_engine_code_execution 샘플](https://github.com/google/adk-python/tree/main/contributing/samples/agent_engine_code_execution)을 참고하세요.
