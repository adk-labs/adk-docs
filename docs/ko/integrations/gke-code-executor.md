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

GKE Code Executor(`GkeCodeExecutor`)는 gVisor 기반 워크로드 격리를 사용하는
GKE(Google Kubernetes Engine) Sandbox 환경을 활용해, LLM 생성 코드를
안전하고 확장 가능하게 실행하는 방법을 제공합니다. 코드 실행 요청마다
강화된 Pod 구성을 가진 임시(ephemeral) 샌드박스 Kubernetes Job을
동적으로 생성합니다. 보안과 격리가 중요한 GKE 프로덕션 환경에서
이 실행기를 사용해야 합니다.

## 동작 방식

코드 실행 요청이 들어오면 `GkeCodeExecutor`는 다음 단계를 수행합니다:

1.  **ConfigMap 생성:** 실행할 Python 코드를 저장하기 위한 Kubernetes ConfigMap을 생성합니다.
2.  **샌드박스 Pod 생성:** 새로운 Kubernetes Job을 생성하고, 이 Job이 강화된 보안 컨텍스트 및 gVisor 런타임이 활성화된 Pod를 생성합니다. ConfigMap의 코드를 해당 Pod에 마운트합니다.
3.  **코드 실행:** 코드는 샌드박스 Pod 내부에서 실행되며, 기본 노드 및 다른 워크로드와 격리됩니다.
4.  **결과 수집:** 실행 표준 출력/에러 스트림을 Pod 로그에서 수집합니다.
5.  **리소스 정리:** 실행이 완료되면 Job과 연결된 ConfigMap을 자동으로 삭제해 아티팩트가 남지 않도록 합니다.

## 주요 이점

*   **강화된 보안:** 코드는 커널 레벨 격리를 제공하는 gVisor 샌드박스 환경에서 실행됩니다.
*   **임시 실행 환경:** 각 코드 실행은 독립된 임시 Pod에서 실행되어 실행 간 상태 전이를 방지합니다.
*   **리소스 제어:** 실행 Pod의 CPU/메모리 제한을 구성해 리소스 남용을 방지할 수 있습니다.
*   **확장성:** 대량의 코드 실행을 병렬로 처리할 수 있으며, 기본 노드의 스케줄링/확장은 GKE가 담당합니다.

## 시스템 요구 사항

GKE Code Executor 도구를 사용해 ADK 프로젝트를 성공적으로 배포하려면
다음 요구 사항을 충족해야 합니다:

- **gVisor 활성화 노드 풀**이 포함된 GKE 클러스터.
- 에이전트 서비스 계정에 다음을 허용하는 특정 **RBAC 권한**이 필요:
    - 각 실행 요청마다 **Jobs** 생성, 모니터링(watch), 삭제.
    - Job의 Pod에 코드를 주입하기 위한 **ConfigMaps** 관리.
    - 실행 결과 조회를 위한 **Pods** 목록 조회 및 **logs** 읽기
- GKE extras 포함 클라이언트 라이브러리 설치: `pip install google-adk[gke]`

완전하고 바로 사용할 수 있는 구성은
[deployment_rbac.yaml](https://github.com/google/adk-python/blob/main/contributing/samples/gke_agent_sandbox/deployment_rbac.yaml)
샘플을 참조하세요. ADK 워크플로를 GKE에 배포하는 방법은
[Google Kubernetes Engine(GKE)에 배포](/adk-docs/deploy/gke/)를 참조하세요.

=== "Python"

    ```python
    from google.adk.agents import LlmAgent
    from google.adk.code_executors import GkeCodeExecutor

    # Initialize the executor, targeting the namespace where its ServiceAccount
    # has the required RBAC permissions.
    # This example also sets a custom timeout and resource limits.
    gke_executor = GkeCodeExecutor(
        namespace="agent-sandbox",
        timeout_seconds=600,
        cpu_limit="1000m",  # 1 CPU core
        mem_limit="1Gi",
    )

    # The agent now uses this executor for any code it generates.
    gke_agent = LlmAgent(
        name="gke_coding_agent",
        model="gemini-2.0-flash",
        instruction="You are a helpful AI agent that writes and executes Python code.",
        code_executor=gke_executor,
    )
    ```

## 구성 파라미터

`GkeCodeExecutor`는 다음 파라미터로 구성할 수 있습니다:

| Parameter            | Type   | Description                                                                             |
| -------------------- | ------ | --------------------------------------------------------------------------------------- |
| `namespace`          | `str`  | 실행 Job이 생성될 Kubernetes 네임스페이스. 기본값은 `"default"`. |
| `image`              | `str`  | 실행 Pod에 사용할 컨테이너 이미지. 기본값은 `"python:3.11-slim"`.         |
| `timeout_seconds`    | `int`  | 코드 실행 타임아웃(초). 기본값은 `300`.                           |
| `cpu_requested`      | `str`  | 실행 Pod 요청 CPU 양. 기본값은 `"200m"`.                   |
| `mem_requested`      | `str`  | 실행 Pod 요청 메모리 양. 기본값은 `"256Mi"`.               |
| `cpu_limit`          | `str`  | 실행 Pod이 사용할 수 있는 최대 CPU 양. 기본값은 `"500m"`.                  |
| `mem_limit`          | `str`  | 실행 Pod이 사용할 수 있는 최대 메모리 양. 기본값은 `"512Mi"`.              |
| `kubeconfig_path`    | `str`  | 인증에 사용할 kubeconfig 파일 경로. in-cluster config 또는 기본 로컬 kubeconfig로 fallback 됩니다. |
| `kubeconfig_context` | `str`  | 사용할 `kubeconfig` 컨텍스트.  |
