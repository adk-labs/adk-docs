# Vertex AI Agent Engine에 배포

<div class="language-support-tag" title="Vertex AI Agent Engine은 현재 Python만 지원합니다.">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

Google Cloud Vertex AI
[Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)은
개발자가 에이전트를 생산 환경에서 확장·거버넌스할 수 있도록 돕는 모듈형 서비스 집합입니다.
Agent Engine 런타임을 사용하면 end-to-end 관리형 인프라에서 에이전트를 배포할 수 있어,
보다 지능적이고 영향력 있는 에이전트 개발에 집중할 수 있습니다.
ADK 에이전트를 Agent Engine에 배포하면 코드는 Agent Engine 제품에서 제공되는
다양한 에이전트 서비스 세트의 일부인 *Agent Engine 런타임* 환경에서 실행됩니다.

이 가이드에는 다음과 같은 배포 경로가 포함됩니다.

*   **[표준 배포](/adk-docs/deploy/agent-engine/deploy/)**: 기존 Google Cloud 프로젝트가 있고,
    ADK 에이전트를 Agent Engine 런타임으로 정교하게 배포하려는 경우 이 경로를 따르세요. 이 경로는 Cloud
    Console, ADK CLI를 사용하며 단계별 지침을 제공합니다. Google Cloud 프로젝트 구성에 익숙하고 운영 배포를 준비하는 사용자에게 권장됩니다.

*   **[Agent Starter Pack 배포](/adk-docs/deploy/agent-engine/asp/)**:
    기존 Google Cloud 프로젝트가 없고, 개발 및 테스트 전용으로 프로젝트를 새로 만드는 경우
    이 빠른 배포 경로를 사용하세요. Agent Starter Pack(ASP)는 ADK 프로젝트를 빠르게 배포하며,
    ADK 에이전트가 Agent Engine 런타임으로 실행되기 위해 반드시 필요한 것은 아닌 일부 Google Cloud 서비스를 자동 구성합니다.

!!! note "Google Cloud의 Agent Engine 서비스"

    Agent Engine은 유료 서비스이며, 무료 접근 한도 초과 시 요금이 발생할 수 있습니다.
    자세한 내용은 [Agent Engine 가격 페이지](https://cloud.google.com/vertex-ai/pricing#vertex-ai-agent-engine)를 참고하세요.

## 배포 페이로드 {#payload}

ADK 에이전트 프로젝트를 Agent Engine에 배포하면 서비스에 다음 콘텐츠가 업로드됩니다.

- ADK 에이전트 코드
- ADK 에이전트 코드에 선언된 모든 의존성

배포에 ADK API 서버 또는 ADK 웹 사용자 인터페이스 라이브러리는 포함되지 않습니다.
Agent Engine 서비스가 ADK API 서버 기능에 필요한 라이브러리를 제공합니다.
