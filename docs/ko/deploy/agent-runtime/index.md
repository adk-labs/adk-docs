# Agent Runtime에 배포하기

<div class="language-support-tag" title="Agent Runtime은 현재 Python과 Go를 지원합니다.">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span><span class="lst-go">Go v1.2.0</span>
</div>

Google Cloud Agent Platform의 [Agent Runtime](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)은 프로덕션 환경에서 에이전트를 확장하고 관리할 수 있도록 돕는 모듈형 서비스 모음입니다. Agent Runtime은 엔드투엔드 관리형 인프라를 제공하므로, 인프라 운영 부담 없이 지능적이고 영향력 있는 에이전트를 구축하는 데 집중하며 프로덕션 환경에 배포할 수 있습니다. ADK 에이전트를 Agent Runtime에 배포하면 코드는 Agent Runtime 제품이 제공하는 광범위한 에이전트 서비스 중 하나인 *Agent Runtime* 환경에서 실행됩니다.

이 가이드는 목적에 따라 다음 두 가지 배포 경로를 안내합니다.

* **[표준 배포](/deploy/agent-runtime/deploy/)**: ADK 에이전트를 Agent Runtime에 배포하는 과정을 세밀하게 관리하려는 경우 이 표준 배포 경로를 따르세요. Google Cloud 콘솔과 ADK 명령줄 인터페이스(CLI)를 사용하며 단계별 지침을 제공합니다. Google Cloud 프로젝트 구성에 이미 익숙한 사용자나 프로덕션 배포를 준비하는 사용자에게 권장됩니다.

* **[Agents CLI 배포](/deploy/agent-runtime/agents-cli/)**: ADK 에이전트를 위한 CI/CD, 코드형 인프라(IaC), 배포 파이프라인이 완비된 Google Cloud 환경을 빠르게 구축하려면 이 가속 배포 경로를 따르세요. 결제가 활성화된 Google Cloud 프로젝트가 필요합니다. Agent Platform의 Agents CLI는 ADK 프로젝트를 신속하게 배포할 수 있도록 지원하며, 성숙한 프로덕션 사용 사례를 위해 Agent Runtime의 핵심 기능을 확장하는 고급 서비스 구성을 포함합니다.

!!! note "Google Cloud의 Agent Runtime 서비스"

    Agent Runtime은 유료 서비스이며 무료 사용 한도를 초과하면 비용이 발생할 수 있습니다. 자세한 내용은 [Agent Runtime 요금 페이지](https://cloud.google.com/vertex-ai/pricing#vertex-ai-agent-engine)에서 확인할 수 있습니다.

## 배포 페이로드 {#payload}

ADK 에이전트 프로젝트를 Agent Runtime에 배포하면 다음 항목이 서비스에 업로드됩니다.

- ADK 에이전트 코드
- ADK 에이전트 코드에 선언된 모든 의존성 패키지

사용하는 프로그래밍 언어에 따라 다음 섹션에 설명된 추가 라이브러리가 포함될 수 있습니다.

=== "Python"

    Python으로 배포할 때는 ADK API 서버 또는 ADK 웹 사용자 인터페이스 라이브러리가 포함되지 *않습니다*. Agent Runtime 서비스가 ADK API 서버 기능에 필요한 라이브러리를 제공합니다.

=== "Go"

    Go로 배포할 때는 Agent Runtime의 `:query` 및 `:streamQuery` 메서드를 제공하는 ADK `agentengine` 런처가 포함됩니다. ADK API 서버나 ADK 웹 사용자 인터페이스는 포함되지 *않습니다*.
