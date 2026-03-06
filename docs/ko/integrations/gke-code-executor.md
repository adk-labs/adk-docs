---
catalog_title: GKE Code Executor
catalog_description: 안전하고 확장 가능한 GKE 환경에서 AI 생성 코드를 실행합니다
catalog_icon: /adk-docs/integrations/assets/gke.png
catalog_tags: ["code","google"]
---

# ADK용 Google Cloud GKE Code Executor 도구

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.14.0</span>
</div>

GKE Code Executor(`GkeCodeExecutor`)는 Google Kubernetes Engine(GKE)을 활용해
LLM이 생성한 코드를 안전하고 확장 가능하게 실행하는 방법을 제공합니다.
보안과 격리가 중요한 GKE 프로덕션 환경에서는 이 실행기를 사용하는 것이
좋습니다. 이 도구는 두 가지 실행 모드를 지원합니다.

1.  **Sandbox Mode(권장):** [Agent Sandbox](https://github.com/kubernetes-sigs/agent-sandbox)
    클라이언트를 사용해 템플릿으로부터 온디맨드로 생성된 샌드박스 인스턴스
    내부에서 코드를 실행합니다. 이 모드는
    [사전 예열된 샌드박스](https://docs.cloud.google.com/kubernetes-engine/docs/how-to/agent-sandbox#create_a_sandboxtemplate_and_sandboxwarmpool)를
    활용해 지연 시간을 낮추고, 샌드박스 환경과 더 직접적인 상호작용을 지원합니다.
2.  **Job Mode:** 워크로드 격리를 위해 gVisor 기반 GKE Sandbox 환경을 사용합니다.
    각 코드 실행 요청마다 강화된 Pod 구성을 가진 임시 샌드박스 Kubernetes Job을
    동적으로 생성합니다. 이 모드는 이전 버전과의 호환성을 위해 제공됩니다.

## 실행 모드

### Sandbox Mode (`executor_type="sandbox"`)

권장 모드입니다. `k8s-agent-sandbox` 클라이언트 라이브러리를 사용해 GKE
클러스터 내 Agent Sandbox를 생성하고 통신합니다. 코드 실행 요청이 들어오면
다음 단계를 수행합니다.

1.  지정한 템플릿으로 `SandboxClaim`을 생성합니다.
2.  샌드박스 인스턴스가 준비될 때까지 기다립니다.
3.  확보한 샌드박스에서 코드를 실행합니다.
4.  표준 출력과 표준 오류를 가져옵니다.
5.  `SandboxClaim`을 삭제하고, 이에 따라 샌드박스 인스턴스도 정리합니다.

이 접근 방식은 사전 예열된 샌드박스를 활용하고 Agent Sandbox 컨트롤러가
제공하는 시작 시간 최적화를 사용하므로 Job Mode보다 더 빠릅니다.

**주요 이점:**

Job Mode의 모든 장점에 더해, Sandbox Mode는 다음 기능도 제공합니다.

*   **낮은 지연 시간:** 완전한 Kubernetes Job을 생성하는 방식보다 시작 시간을 줄입니다.
*   **관리형 환경:** 샌드박스 수명 주기 관리를 위해 Agent Sandbox 프레임워크를 활용합니다.

**전제 조건:**

*   GKE 클러스터에 기존 Agent Sandbox 배포가 있어야 하며, 여기에는 샌드박스
    컨트롤러와 그 확장(예: sandbox claim controller, sandbox warmpool controller),
    router, gateway, 관련 `SandboxTemplate` 리소스(예: `python-sandbox-template`)가
    포함되어야 합니다.
*   ADK 에이전트가 `SandboxClaim` 리소스를 생성하고 삭제할 수 있는 필요한
    RBAC 권한이 있어야 합니다.

### Job Mode (`executor_type="job"`)

이 모드는 이전 버전과의 호환성을 위해 제공됩니다. 코드 실행 요청이 들어오면
`GkeCodeExecutor`는 다음 단계를 수행합니다.

1.  **ConfigMap 생성:** 실행할 Python 코드를 저장하기 위한 Kubernetes ConfigMap을 생성합니다.
2.  **샌드박스 Pod 생성:** 새로운 Kubernetes Job을 생성하고, 이 Job이 강화된
    보안 컨텍스트와 gVisor 런타임이 활성화된 Pod를 생성합니다. ConfigMap에
    저장된 코드를 해당 Pod에 마운트합니다.
3.  **코드 실행:** 코드는 샌드박스 Pod 내부에서 실행되며, 기본 노드와 다른
    워크로드로부터 격리됩니다.
4.  **결과 수집:** 실행의 표준 출력과 표준 오류 스트림을 Pod 로그에서 수집합니다.
5.  **리소스 정리:** 실행이 완료되면 Job과 연결된 ConfigMap을 자동으로 삭제해
    아무런 아티팩트도 남기지 않습니다.

**주요 이점:**

*   **강화된 보안:** 코드는 커널 수준 격리를 제공하는 gVisor 샌드박스 환경에서 실행됩니다.
*   **임시 실행 환경:** 각 코드 실행은 독립된 임시 Pod에서 이루어져 실행 간 상태 전이를 방지합니다.
*   **리소스 제어:** 실행 Pod의 CPU/메모리 제한을 구성해 리소스 남용을 방지할 수 있습니다.
*   **확장성:** 많은 수의 코드 실행을 병렬로 처리할 수 있으며, 기본 노드의 스케줄링과
    확장은 GKE가 담당합니다.
*   **최소 설정:** 표준 GKE 기능과 gVisor에 의존합니다.

## 시스템 요구 사항

GKE Code Executor 도구를 사용해 ADK 프로젝트를 성공적으로 배포하려면
다음 요구 사항을 충족해야 합니다.

- GKE 클러스터에 **gVisor가 활성화된 노드 풀**이 있어야 합니다.
  이는 Job Mode의 기본 이미지와 일반적인 Agent Sandbox 템플릿 모두에 필요합니다.
- 에이전트 서비스 계정에는 특정 **RBAC 권한**이 필요합니다.
    - **Job Mode:** **Jobs** 생성, 감시, 삭제 권한과 **ConfigMaps** 관리 권한,
      **Pods** 목록 조회 및 **logs** 읽기 권한이 필요합니다. Job Mode용 완전한
      즉시 사용 가능한 설정은
      [deployment_rbac.yaml](https://github.com/google/adk-python/blob/main/contributing/samples/gke_agent_sandbox/deployment_rbac.yaml)
      샘플을 참조하세요.
    - **Sandbox Mode:** Agent Sandbox가 배포된 네임스페이스 안에서 **SandboxClaim**
      및 **Sandbox** 리소스를 생성, 조회, 감시, 삭제할 수 있는 권한이 필요합니다.
- 적절한 extras를 포함해 클라이언트 라이브러리를 설치하세요:
  `pip install google-adk[gke]`

## 구성 파라미터

`GkeCodeExecutor`는 다음 파라미터로 구성할 수 있습니다.

| Parameter | Type | Description |
| ---------------------- | ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `namespace` | `str` | 실행 리소스(Job 또는 SandboxClaim)가 생성될 Kubernetes 네임스페이스입니다. 기본값은 `"default"`입니다. |
| `executor_type` | `Literal["job", "sandbox"]` | 실행 모드를 지정합니다. 기본값은 `"job"`입니다. |
| `image` | `str` | (Job Mode) 실행 Pod에 사용할 컨테이너 이미지입니다. 기본값은 `"python:3.11-slim"`입니다. |
| `timeout_seconds` | `int` | (Job Mode) 코드 실행 제한 시간(초)입니다. 기본값은 `300`입니다. |
| `cpu_requested` | `str` | (Job Mode) 실행 Pod가 요청할 CPU 양입니다. 기본값은 `"200m"`입니다. |
| `mem_requested` | `str` | (Job Mode) 실행 Pod가 요청할 메모리 양입니다. 기본값은 `"256Mi"`입니다. |
| `cpu_limit` | `str` | (Job Mode) 실행 Pod가 사용할 수 있는 최대 CPU 양입니다. 기본값은 `"500m"`입니다. |
| `mem_limit` | `str` | (Job Mode) 실행 Pod가 사용할 수 있는 최대 메모리 양입니다. 기본값은 `"512Mi"`입니다. |
| `kubeconfig_path` | `str` | 인증에 사용할 kubeconfig 파일 경로입니다. in-cluster config 또는 기본 로컬 kubeconfig로 폴백합니다. |
| `kubeconfig_context` | `str` | 사용할 `kubeconfig` 컨텍스트입니다. |
| `sandbox_gateway_name` | `str \| None` | (Sandbox Mode) 사용할 샌드박스 게이트웨이 이름입니다. 선택 사항입니다. |
| `sandbox_template` | `str \| None` | (Sandbox Mode) 사용할 `SandboxTemplate` 이름입니다. 기본값은 `"python-sandbox-template"`입니다. |

## 사용 예시

=== "Python - Sandbox Mode (권장)"

    ```python
    from google.adk.agents import LlmAgent
    from google.adk.code_executors import GkeCodeExecutor
    from google.adk.code_executors import CodeExecutionInput
    from google.adk.agents.invocation_context import InvocationContext

    # Sandbox Mode용 실행기 초기화
    # 네임스페이스에는 SandboxClaims 및 Sandbox에 대한 RBAC 권한이 있어야 합니다.
    gke_sandbox_executor = GkeCodeExecutor(
        namespace="agent-sandbox-system",  # 일반적으로 agent-sandbox가 설치된 위치
        executor_type="sandbox",
        sandbox_template="python-sandbox-template",
        sandbox_gateway_name="your-gateway-name", # 선택 사항
    )

    # 직접 실행 예시:
    ctx = InvocationContext()
    result = gke_sandbox_executor.execute_code(ctx, CodeExecutionInput(code="print('Hello from Sandbox Mode')"))
    print(result.stdout)

    # Agent와 함께 사용하는 예시:
    gke_sandbox_agent = LlmAgent(
        name="gke_sandbox_coding_agent",
        model="gemini-2.5-flash",
        instruction="당신은 샌드박스를 사용해 Python 코드를 작성하고 실행하는 유용한 AI 에이전트입니다.",
        code_executor=gke_sandbox_executor,
    )
    ```

=== "Python - Job Mode"

    ```python
    from google.adk.agents import LlmAgent
    from google.adk.code_executors import GkeCodeExecutor
    from google.adk.code_executors import CodeExecutionInput
    from google.adk.agents.invocation_context import InvocationContext

    # Job Mode용 실행기 초기화
    # 네임스페이스에는 Jobs, ConfigMaps, Pods, Logs에 대한 RBAC 권한이 있어야 합니다.
    gke_executor = GkeCodeExecutor(
        namespace="agent-ns",
        executor_type="job",
        timeout_seconds=600,
        cpu_limit="1000m",  # 1 CPU core
        mem_limit="1Gi",
    )

    # 직접 실행 예시:
    ctx = InvocationContext()
    result = gke_executor.execute_code(ctx, CodeExecutionInput(code="print('Hello from Job Mode')"))
    print(result.stdout)

    # Agent와 함께 사용하는 예시:
    gke_agent = LlmAgent(
        name="gke_coding_agent",
        model="gemini-2.5-flash",
        instruction="당신은 Python 코드를 작성하고 실행하는 유용한 AI 에이전트입니다.",
        code_executor=gke_executor,
    )
    ```
