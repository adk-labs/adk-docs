# 에이전트 런타임에 배포

<div class="language-support-tag" title="Agent Runtime currently supports only Python.">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

Google Cloud 에이전트 플랫폼
[Agent Runtime](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)
개발자가 에이전트를 확장하고 관리하는 데 도움이 되는 모듈식 서비스 세트입니다.
생산. 에이전트 런타임 런타임을 사용하면 프로덕션 환경에 에이전트를 배포할 수 있습니다.
엔드투엔드 관리형 인프라를 통해 지능적인 구축에 집중할 수 있습니다.
그리고 영향력 있는 에이전트. ADK 에이전트를 에이전트 런타임에 배포하면 코드가
더 큰 세트의 일부인 *에이전트 런타임 런타임* 환경에서 실행됩니다.
Agent Runtime 제품이 제공하는 에이전트 서비스의 내용입니다.

이 가이드에는 다음과 같은 배포 경로가 포함되어 있습니다.
목적:

* **[Standard deployment](/deploy/agent-runtime/deploy/)**: 팔로우
    에이전트에 ADK 에이전트 배포를 신중하게 관리하려는 경우 이 표준 배포 경로
    런타임 런타임. 이 배포 경로는 Cloud Console, ADK 명령줄을 사용합니다.
    인터페이스를 제공하며 단계별 지침을 제공합니다. 이 경로를 권장합니다
    Google Cloud 프로젝트 구성에 이미 익숙한 사용자를 위해
    프로덕션 배포를 준비하는 사용자.

* **[Agents CLI deployment](/deploy/agent-runtime/agents-cli/)**:
    완전히 구성된 Google을 설정하려면 이 가속화된 배포 경로를 따르세요.
    CI/CD, 코드형 인프라, 배포 파이프라인을 갖춘 클라우드 환경
    ADK 에이전트의 경우. 결제가 사용 설정된 Google Cloud 프로젝트가 필요합니다.
    Agent Platform의 Agents CLI는 ADK 프로젝트를 신속하게 배포하는 데 도움이 됩니다.
    핵심 기능을 확장하는 고급 서비스 구성이 포함됩니다.
    보다 성숙한 사용 사례를 위한 에이전트 런타임 런타임.

!!! note "Google Cloud의 에이전트 런타임 서비스"

    Agent Runtime은 유료 서비스이므로 이용시 비용이 발생할 수 있습니다.
    무료 액세스 등급보다 높습니다. 자세한 내용은 다음에서 확인할 수 있습니다.
    [Agent Runtime pricing page](https://cloud.google.com/vertex-ai/pricing#vertex-ai-agent-engine).

## 배포 페이로드 {#payload}

ADK 에이전트 프로젝트를 Agent Runtime에 배포하면 다음 내용이 표시됩니다.
서비스에 업로드된 내용:

- ADK 에이전트 코드
- ADK 에이전트 코드에 선언된 모든 종속성

배포에는 ADK API 서버 또는 ADK 웹 사용자가 포함되지 *않습니다*
인터페이스 라이브러리. 에이전트 런타임 서비스는 ADK API용 라이브러리를 제공합니다.
서버 기능.
