# 내장 도구

이러한 내장 도구는 Google 검색 또는 코드 실행기와 같은 즉시 사용 가능한 기능을 제공하여 에이전트에게 일반적인 기능을 제공합니다. 예를 들어 웹에서 정보를 검색해야 하는 에이전트는 추가 설정 없이 **google\_search** 도구를 직접 사용할 수 있습니다.

## 사용 방법

1. **가져오기:** 도구 모듈에서 원하는 도구를 가져옵니다. Python에서는 `agents.tools`이고, Go에서는 `google.golang.org/adk/tool/geminitool`이며, Java에서는 `com.google.adk.tools`입니다.
2. **구성:** 필요한 매개변수가 있는 경우 제공하여 도구를 초기화합니다.
3. **등록:** 초기화된 도구를 에이전트의 **도구** 목록에 추가합니다.

에이전트에 추가되면 에이전트는 **사용자 프롬프트**와 **지침**을 기반으로 도구 사용을 결정할 수 있습니다. 프레임워크는 에이전트가 도구를 호출할 때 도구 실행을 처리합니다. 중요: 이 페이지의 ***제한 사항*** 섹션을 확인하세요.

## 사용 가능한 내장 도구

참고: Go는 Google 검색 도구 및 `geminitool` 패키지를 통한 기타 내장 도구를 지원합니다.
참고: Java는 현재 Google 검색 및 코드 실행 도구만 지원합니다.

### Google 검색

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

`google_search` 도구는 에이전트가 Google 검색을 사용하여 웹 검색을 수행할 수 있도록 합니다. `google_search` 도구는 Gemini 2 모델과만 호환됩니다. 도구에 대한 자세한 내용은 [Google 검색 그라운딩 이해](../grounding/google_search_grounding.md)를 참조하세요.

!!! warning "`google_search` 도구 사용 시 추가 요구 사항"
    Google 검색으로 그라운딩을 사용하고 응답에서 검색 제안을 받는 경우, 프로덕션 및 애플리케이션에 검색 제안을 표시해야 합니다.
    Google 검색으로 그라운딩에 대한 자세한 내용은 [Google AI Studio](https://ai.google.dev/gemini-api/docs/grounding/search-suggestions) 또는 [Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/grounding/grounding-search-suggestions)의 Google 검색으로 그라운딩 설명서를 참조하세요. UI 코드(HTML)는 Gemini 응답에서 `renderedContent`로 반환되며, 정책에 따라 앱에 HTML을 표시해야 합니다.

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/built-in-tools/google_search.py"
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/tools/built-in-tools/google_search.go"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/tools/GoogleSearchAgentApp.java:full_code"
    ```

### 코드 실행

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

`built_in_code_execution` 도구는 에이전트가 코드를 실행할 수 있게 하며,
특히 Gemini 2 모델을 사용할 때 그렇습니다. 이를 통해 모델은 계산, 데이터 조작 또는 작은 스크립트 실행과 같은 작업을 수행할 수 있습니다.

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/built-in-tools/code_execution.py"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/tools/CodeExecutionAgentApp.java:full_code"
    ```

### GKE 코드 실행기

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.14.0</span>
</div>

GKE 코드 실행기(`GkeCodeExecutor`)는 gVisor를 사용하여 워크로드 격리를 수행하는 GKE(Google Kubernetes Engine) 샌드박스 환경을 활용하여 LLM 생성 코드를 실행하기 위한 안전하고 확장 가능한 방법을 제공합니다. 각 코드 실행 요청에 대해 강화된 Pod 구성으로 임시 샌드박스형 Kubernetes 작업을 동적으로 생성합니다. 보안 및 격리가 중요한 GKE의 프로덕션 환경에 이 실행기를 사용해야 합니다.

#### 작동 방식

코드 실행 요청이 이루어지면 `GkeCodeExecutor`는 다음 단계를 수행합니다.

1.  **ConfigMap 생성:** 실행해야 하는 Python 코드를 저장하기 위해 Kubernetes ConfigMap이 생성됩니다.
2.  **샌드박스형 Pod 생성:** 강화된 보안 컨텍스트와 gVisor 런타임이 활성화된 Pod를 생성하는 새 Kubernetes 작업이 생성됩니다. ConfigMap의 코드가 이 Pod에 마운트됩니다.
3.  **코드 실행:** 코드는 기본 노드 및 다른 워크로드와 격리된 샌드박스형 Pod 내에서 실행됩니다.
4.  **결과 검색:** 실행의 표준 출력 및 오류 스트림이 Pod의 로그에서 캡처됩니다.
5.  **리소스 정리:** 실행이 완료되면 작업 및 관련 ConfigMap이 자동으로 삭제되어 아티팩트가 남지 않도록 합니다.

#### 주요 이점

*   **향상된 보안:** 코드는 커널 수준 격리가 있는 gVisor 샌드박스 환경에서 실행됩니다.
*   **임시 환경:** 각 코드 실행은 자체 임시 Pod에서 실행되어 실행 간 상태 전송을 방지합니다.
*   **리소스 제어:** 실행 Pod에 대한 CPU 및 메모리 제한을 구성하여 리소스 남용을 방지할 수 있습니다.
*   **확장성:** GKE가 기본 노드의 예약 및 확장을 처리하므로 많은 수의 코드 실행을 병렬로 실행할 수 있습니다.

#### 시스템 요구 사항

GKE 코드 실행기 도구를 사용하여 ADK 프로젝트를 성공적으로 배포하려면 다음 요구 사항을 충족해야 합니다.

- **gVisor 지원 노드 풀**이 있는 GKE 클러스터.
- 에이전트의 서비스 계정에는 다음을 수행할 수 있는 특정 **RBAC 권한**이 필요합니다.
    - 각 실행 요청에 대한 **작업** 생성, 감시 및 삭제.
    - 작업의 Pod에 코드를 주입하기 위한 **ConfigMap** 관리.
    - 실행 결과를 검색하기 위한 **Pod** 나열 및 **로그** 읽기.
- GKE 추가 기능과 함께 클라이언트 라이브러리 설치: `pip install google-adk[gke]`

완전하고 즉시 사용 가능한 구성은
[deployment_rbac.yaml](https://github.com/google/adk-python/blob/main/contributing/samples/gke_agent_sandbox/deployment_rbac.yaml)
샘플을 참조하세요. ADK 워크플로를 GKE에 배포하는 방법에 대한 자세한 내용은
[Google Kubernetes Engine(GKE)에 배포](/adk-docs/deploy/gke/)를 참조하세요.

=== "Python"

    ```python
    from google.adk.agents import LlmAgent
    from google.adk.code_executors import GkeCodeExecutor

    # 서비스 계정에 필요한 RBAC 권한이 있는 네임스페이스를 대상으로 실행기 초기화.
    # 이 예제에서는 사용자 지정 시간 초과 및 리소스 제한도 설정합니다.
    gke_executor = GkeCodeExecutor(
        namespace="agent-sandbox",
        timeout_seconds=600,
        cpu_limit="1000m",  # 1 CPU 코어
        mem_limit="1Gi",
    )

    # 이제 에이전트는 생성하는 모든 코드에 이 실행기를 사용합니다.
    gke_agent = LlmAgent(
        name="gke_coding_agent",
        model="gemini-2.0-flash",
        instruction="당신은 Python 코드를 작성하고 실행하는 유용한 AI 에이전트입니다.",
        code_executor=gke_executor,
    )
    ```

#### 구성 매개변수

`GkeCodeExecutor`는 다음 매개변수로 구성할 수 있습니다.

| 매개변수            | 유형   | 설명                                                                             |
| -------------------- | ------ | --------------------------------------------------------------------------------------- |
| `namespace`          | `str`  | 실행 작업이 생성될 Kubernetes 네임스페이스. 기본값은 `"default"`입니다. |
| `image`              | `str`  | 실행 Pod에 사용할 컨테이너 이미지. 기본값은 `"python:3.11-slim"`입니다.         |
| `timeout_seconds`    | `int`  | 코드 실행 시간 초과(초). 기본값은 `300`입니다.                           |
| `cpu_requested`      | `str`  | 실행 Pod에 요청할 CPU 양. 기본값은 `"200m"`입니다.                   |
| `mem_requested`      | `str`  | 실행 Pod에 요청할 메모리 양. 기본값은 `"256Mi"`입니다.               |
| `cpu_limit`          | `str`  | 실행 Pod가 사용할 수 있는 최대 CPU 양. 기본값은 `"500m"`입니다.                  |
| `mem_limit`          | `str`  | 실행 Pod가 사용할 수 있는 최대 메모리 양. 기본값은 `"512Mi"`입니다.              |
| `kubeconfig_path`    | `str`  | 인증에 사용할 kubeconfig 파일 경로. 클러스터 내 구성 또는 기본 로컬 kubeconfig로 대체됩니다. |
| `kubeconfig_context` | `str`  | 사용할 `kubeconfig` 컨텍스트.  |

### Vertex AI RAG 엔진

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

`vertex_ai_rag_retrieval` 도구는 에이전트가 Vertex
AI RAG 엔진을 사용하여 개인 데이터 검색을 수행할 수 있도록 합니다.

Vertex AI RAG 엔진으로 그라운딩을 사용하는 경우 사전에 RAG 코퍼스를 준비해야 합니다.
설정 방법은 [RAG ADK 에이전트 샘플](https://github.com/google/adk-samples/blob/main/python/agents/RAG/rag/shared_libraries/prepare_corpus_and_data.py) 또는 [Vertex AI RAG 엔진 페이지](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/rag-quickstart)를 참조하세요.

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/built-in-tools/vertexai_rag_engine.py"
    ```

### Vertex AI 검색

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span>
</div>

`vertex_ai_search_tool`은 Google Cloud Vertex AI Search를 사용하여 에이전트가
비공개로 구성된 데이터 저장소(예: 내부 문서, 회사 정책, 지식 기반)를 검색할 수 있도록 합니다. 이 내장 도구는 구성 중에 특정 데이터 저장소 ID를 제공해야 합니다. 도구에 대한 자세한 내용은 [Vertex AI 검색 그라운딩 이해](../grounding/vertex_ai_search_grounding.md)를 참조하세요.


```py
--8<-- "examples/python/snippets/tools/built-in-tools/vertexai_search.py"
```


### BigQuery

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.1.0</span>
</div>

다음은 BigQuery와의 통합을 제공하기 위한 도구 모음입니다.

* **`list_dataset_ids`**: GCP 프로젝트에 있는 BigQuery 데이터세트 ID를 가져옵니다.
* **`get_dataset_info`**: BigQuery 데이터세트에 대한 메타데이터를 가져옵니다.
* **`list_table_ids`**: BigQuery 데이터세트에 있는 테이블 ID를 가져옵니다.
* **`get_table_info`**: BigQuery 테이블에 대한 메타데이터를 가져옵니다.
* **`execute_sql`**: BigQuery에서 SQL 쿼리를 실행하고 결과를 가져옵니다.
* **`forecast`**: `AI.FORECAST` 함수를 사용하여 BigQuery AI 시계열 예측을 실행합니다.
* **`ask_data_insights`**: 자연어를 사용하여 BigQuery 테이블의 데이터에 대한 질문에 답변합니다.

이들은 `BigQueryToolset` 도구 세트에 패키지되어 있습니다.



```py
--8<-- "examples/python/snippets/tools/built-in-tools/bigquery.py"
```


### Spanner

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.11.0</span>
</div>

다음은 Spanner와의 통합을 제공하기 위한 도구 모음입니다.

* **`list_table_names`**: GCP Spanner 데이터베이스에 있는 테이블 이름을 가져옵니다.
* **`list_table_indexes`**: GCP Spanner 데이터베이스에 있는 테이블 인덱스를 가져옵니다.
* **`list_table_index_columns`**: GCP Spanner 데이터베이스에 있는 테이블 인덱스 열을 가져옵니다.
* **`list_named_schemas`**: Spanner 데이터베이스에 대한 명명된 스키마를 가져옵니다.
* **`get_table_schema`**: Spanner 데이터베이스 테이블 스키마 및 메타데이터 정보를 가져옵니다.
* **`execute_sql`**: Spanner 데이터베이스에서 SQL 쿼리를 실행하고 결과를 가져옵니다.
* **`similarity_search`**: 텍스트 쿼리를 사용하여 Spanner에서 유사성 검색을 수행합니다.

이들은 `SpannerToolset` 도구 세트에 패키지되어 있습니다.



```py
--8<-- "examples/python/snippets/tools/built-in-tools/spanner.py"
```


### Bigtable

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.12.0</span>
</div>

다음은 Bigtable과의 통합을 제공하기 위한 도구 모음입니다.

* **`list_instances`**: Google Cloud 프로젝트의 Bigtable 인스턴스를 가져옵니다.
* **`get_instance_info`**: Google Cloud 프로젝트의 메타데이터 인스턴스 정보를 가져옵니다.
* **`list_tables`**: GCP Bigtable 인스턴스의 테이블을 가져옵니다.
* **`get_table_info`**: GCP Bigtable의 메타데이터 테이블 정보를 가져옵니다.
* **`execute_sql`**: Bigtable 테이블에서 SQL 쿼리를 실행하고 결과를 가져옵니다.

이들은 `BigtableToolset` 도구 세트에 패키지되어 있습니다.



```py
--8<-- "examples/python/snippets/tools/built-in-tools/bigtable.py"
```

## 다른 도구와 함께 내장 도구 사용하기

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span><span class="lst-java">Java</span>
</div>

다음 코드 샘플은 여러 내장 도구를 사용하거나
여러 에이전트를 사용하여 다른 도구와 함께 내장 도구를 사용하는 방법을 보여줍니다.

=== "Python"

    ```py
    from google.adk.tools.agent_tool import AgentTool
    from google.adk.agents import Agent
    from google.adk.tools import google_search
    from google.adk.code_executors import BuiltInCodeExecutor


    search_agent = Agent(
        model='gemini-2.0-flash',
        name='SearchAgent',
        instruction="""
        당신은 Google 검색 전문가입니다.
        """,
        tools=[google_search],
    )
    coding_agent = Agent(
        model='gemini-2.0-flash',
        name='CodeAgent',
        instruction="""
        당신은 코드 실행 전문가입니다.
        """,
        code_executor=BuiltInCodeExecutor(),
    )
    root_agent = Agent(
        name="RootAgent",
        model="gemini-2.0-flash",
        description="루트 에이전트",
        tools=[AgentTool(agent=search_agent), AgentTool(agent=coding_agent)],
    )
    ```

=== "Java"

    ```java
    import com.google.adk.agents.BaseAgent;
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.tools.AgentTool;
    import com.google.adk.tools.BuiltInCodeExecutionTool;
    import com.google.adk.tools.GoogleSearchTool;
    import com.google.common.collect.ImmutableList;

    public class NestedAgentApp {

      private static final String MODEL_ID = "gemini-2.0-flash";

      public static void main(String[] args) {

        // 검색 에이전트 정의
        LlmAgent searchAgent =
            LlmAgent.builder()
                .model(MODEL_ID)
                .name("SearchAgent")
                .instruction("당신은 Google 검색 전문가입니다.")
                .tools(new GoogleSearchTool()) // GoogleSearchTool 인스턴스화
                .build();


        // 코딩 에이전트 정의
        LlmAgent codingAgent =
            LlmAgent.builder()
                .model(MODEL_ID)
                .name("CodeAgent")
                .instruction("당신은 코드 실행 전문가입니다.")
                .tools(new BuiltInCodeExecutionTool()) // BuiltInCodeExecutionTool 인스턴스화
                .build();

        // 루트 에이전트 정의, AgentTool.create()를 사용하여 검색 에이전트와 코딩 에이전트를 래핑
        BaseAgent rootAgent =
            LlmAgent.builder()
                .name("RootAgent")
                .model(MODEL_ID)
                .description("루트 에이전트")
                .tools(
                    AgentTool.create(searchAgent), // create 메서드 사용
                    AgentTool.create(codingAgent)   // create 메서드 사용
                 )
                .build();

        // 참고: 이 샘플은 에이전트 정의만 보여줍니다.
        // 이 에이전트들을 실행하려면 Runner와 SessionService와 통합해야 합니다.
        // 이전 예제와 유사하게.
        System.out.println("에이전트가 성공적으로 정의되었습니다:");
        System.out.println("  루트 에이전트: " + rootAgent.name());
        System.out.println("  검색 에이전트 (중첩됨): " + searchAgent.name());
        System.out.println("  코드 에이전트 (중첩됨): " + codingAgent.name());
      }
    }
    ```


### 제한 사항

!!! warning

    현재 각 루트 에이전트 또는 단일 에이전트당 하나의 내장 도구만
    지원됩니다. 동일한 에이전트에서 다른 유형의 도구를 사용할 수 없습니다.

 예를 들어, 단일 에이전트 내에서 ***다른 도구와 함께 내장 도구***를 사용하는 다음 접근 방식은 현재 지원되지 **않습니다**:

=== "Python"

    ```py
    root_agent = Agent(
        name="RootAgent",
        model="gemini-2.0-flash",
        description="루트 에이전트",
        tools=[custom_function],
        code_executor=BuiltInCodeExecutor() # <-- 도구와 함께 사용할 때 지원되지 않음
    )
    ```

=== "Java"

    ```java
     LlmAgent searchAgent =
            LlmAgent.builder()
                .model(MODEL_ID)
                .name("SearchAgent")
                .instruction("당신은 Google 검색 전문가입니다.")
                .tools(new GoogleSearchTool(), new YourCustomTool()) // <-- 지원되지 않음
                .build();
    ```

ADK Python에는 이 제한을 우회하는 내장 해결 방법이 있습니다.
`GoogleSearchTool` 및 `VertexAiSearchTool`의 경우 (`bypass_multi_tools_limit=True`를 사용하여 활성화), 예:
[샘플 에이전트](https://github.com/google/adk-python/tree/main/contributing/samples/built_in_multi_tools).

!!! warning

    내장 도구는 하위 에이전트 내에서 사용할 수 없습니다. 단,
    위에서 언급한 해결 방법 때문에 ADK Python의 `GoogleSearchTool` 및 `VertexAiSearchTool`은 예외입니다.

예를 들어, 하위 에이전트 내에서 내장 도구를 사용하는 다음 접근 방식은
현재 지원되지 **않습니다**:

=== "Python"

    ```py
    url_context_agent = Agent(
        model='gemini-2.0-flash',
        name='UrlContextAgent',
        instruction="""
        당신은 URL 컨텍스트 전문가입니다.
        """,
        tools=[url_context],
    )
    coding_agent = Agent(
        model='gemini-2.0-flash',
        name='CodeAgent',
        instruction="""
        당신은 코드 실행 전문가입니다.
        """,
        code_executor=BuiltInCodeExecutor(),
    )
    root_agent = Agent(
        name="RootAgent",
        model="gemini-2.0-flash",
        description="루트 에이전트",
        sub_agents=[
            url_context_agent,
            coding_agent
        ],
    )
    ```

=== "Java"

    ```java
    LlmAgent searchAgent =
        LlmAgent.builder()
            .model("gemini-2.0-flash")
            .name("SearchAgent")
            .instruction("당신은 Google 검색 전문가입니다.")
            .tools(new GoogleSearchTool())
            .build();

    LlmAgent codingAgent =
        LlmAgent.builder()
            .model("gemini-2.0-flash")
            .name("CodeAgent")
            .instruction("당신은 코드 실행 전문가입니다.")
            .tools(new BuiltInCodeExecutionTool())
            .build();


    LlmAgent rootAgent =
        LlmAgent.builder()
            .name("RootAgent")
            .model("gemini-2.0-flash")
            .description("루트 에이전트")
            .subAgents(searchAgent, codingAgent) // 지원되지 않음, 하위 에이전트가 내장 도구를 사용하기 때문.
            .build();
    ```