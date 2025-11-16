# 에이전트 배포

ADK를 사용하여 에이전트를 빌드하고 테스트한 후 다음 단계는 프로덕션에서 액세스, 쿼리 및 사용하거나 다른 애플리케이션과 통합할 수 있도록 배포하는 것입니다. 배포는 에이전트를 로컬 개발 머신에서 확장 가능하고 안정적인 환경으로 이동합니다.

<img src="../assets/deploy-agent.png" alt="에이전트 배포">

## 배포 옵션

ADK 에이전트는 프로덕션 준비 또는 사용자 지정 유연성에 대한 요구 사항에 따라 다양한 환경에 배포할 수 있습니다.

### Vertex AI의 에이전트 엔진

[에이전트 엔진](agent-engine.md)은 ADK와 같은 프레임워크로 빌드된 AI 에이전트를 배포, 관리 및 확장하기 위해 특별히 설계된 Google Cloud의 완전 관리형 자동 확장 서비스입니다.

[Vertex AI 에이전트 엔진에 에이전트 배포](agent-engine.md)에 대해 자세히 알아보십시오.

### Cloud Run

[Cloud Run](https://cloud.google.com/run)은 에이전트를 컨테이너 기반 애플리케이션으로 실행할 수 있는 Google Cloud의 관리형 자동 확장 컴퓨팅 플랫폼입니다.

[Cloud Run에 에이전트 배포](cloud-run.md)에 대해 자세히 알아보십시오.

### Google Kubernetes Engine(GKE)

[Google Kubernetes Engine(GKE)](https://cloud.google.com/kubernetes-engine)은 에이전트를 컨테이너화된 환경에서 실행할 수 있는 Google Cloud의 관리형 Kubernetes 서비스입니다. GKE는 배포에 대한 더 많은 제어가 필요하거나 개방형 모델을 실행하는 경우 좋은 옵션입니다.

[GKE에 에이전트 배포](gke.md)에 대해 자세히 알아보십시오.

### 기타 컨테이너 친화적인 인프라

에이전트를 수동으로 컨테이너 이미지로 패키징한 다음 컨테이너 이미지를 지원하는 모든 환경에서 실행할 수 있습니다. 예를 들어 Docker 또는 Podman에서 로컬로 실행할 수 있습니다. 이는 오프라인 또는 연결이 끊긴 상태로 실행하거나 Google Cloud에 연결되지 않은 시스템에서 실행하려는 경우 좋은 옵션입니다.

[Cloud Run에 에이전트 배포](cloud-run.md#deployment-commands) 지침을 따르십시오. gcloud CLI의 "배포 명령" 섹션에서 FastAPI 진입점 및 Dockerfile의 예를 찾을 수 있습니다.
