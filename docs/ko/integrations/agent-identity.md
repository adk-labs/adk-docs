---
catalog_title: Google Cloud Agent Identity
catalog_description: 에이전트의 OAuth 토큰과 API 키를 관리합니다
catalog_icon: /integrations/assets/agent-identity.svg
catalog_tags: ["google"]
---

# ADK용 Agent Identity Auth Manager

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.30.0</span><span class="lst-preview">미리보기</span>
</div>

[Google Cloud Agent Identity](https://docs.cloud.google.com/iam/docs/agent-identity-overview)
서비스는 자격 증명 구성 저장, 토큰 생성 및 저장, 접근 감사 등 인증 자격 증명의 전체
라이프사이클을 관리하는 간소화된 Google 관리형 솔루션을 제공합니다. 이 방식을 통해
더 안전하고 간편하게 에이전트를 개발할 수 있습니다.

!!! example "Preview 릴리스"

    Agent Identity Auth Manager 기능은 Preview 릴리스입니다. 자세한 내용은
    [출시 단계 설명](https://cloud.google.com/products#product-launch-stages)을
    참고하세요.

## 사용 사례

- **간소화된 OAuth 흐름**: 커스텀 인프라를 직접 구축하지 않고도 인증 자격 증명의 전체
  라이프사이클을 관리합니다.
- **안전한 토큰 교환 및 저장**: 자격 증명 구성을 안전하게 저장하고 토큰을 교환합니다.
- **감사 로깅**: 저장된 자격 증명에 대한 접근 내역을 조회하고 감사합니다.

## 사전 요구사항

- [Google Cloud 프로젝트](https://cloud.google.com/resource-manager/docs/creating-managing-projects)
- 프로젝트에 생성된 하나 이상의 Agent Identity
  [인증 제공자(auth provider)](https://cloud.google.com/iam/docs/manage-auth-providers-v2)
- 호출자 ID에 부여된
  [`agentidentity.user`](https://docs.cloud.google.com/iam/docs/roles-permissions/agentidentity#agentidentity.user)
  역할 또는 동등한 권한
- [애플리케이션 기본 사용자 인증 정보(ADC)](https://docs.cloud.google.com/docs/authentication/application-default-credentials)
  (`gcloud auth application-default login`)를 통한 인증 구성

## 설치

필요한 클라이언트 라이브러리를 다운로드하려면 `agent-identity` 추가 패키지 그룹을
설치합니다.

```bash
pip install "google-adk[agent-identity]"
```

## 에이전트와 함께 사용하기

ADK에서 Agent Identity Auth Manager를 사용하려면 다음 단계를 따르세요.

### 인증 제공자 등록

ADK가 지정된 `CustomAuthScheme`에 어떤 `BaseAuthProvider`를 사용할지 결정할 수 있도록
`GcpAuthProvider` 인스턴스를 `CredentialManager`에 등록합니다. 이 작업은 에이전트
코드에서 한 번만 수행하면 됩니다.

```python
from google.adk.auth.credential_manager import CredentialManager
from google.adk.integrations.agent_identity import GcpAuthProvider

CredentialManager.register_auth_provider(GcpAuthProvider())
```

### 도구 구성

`GcpAuthProviderScheme` 객체로 Agent Identity 인증 제공자를 구성한 다음, 지원되는
`Tool` 또는 `Toolset`의 `auth_scheme` 매개변수로 전달합니다. 다음 예제는
`McpToolset`과 함께 사용하는 방법을 보여주지만, `GcpAuthProviderScheme`은
`AuthenticatedFunctionTool` 같은 다른 도구와도 함께 사용할 수 있습니다. 전체 예제는
[GCP Auth 샘플](https://github.com/google/adk-python/tree/main/contributing/samples/gcp_auth)을
참고하세요.

```python
from google.adk.integrations.agent_identity import GcpAuthProviderScheme
from google.adk.tools.mcp import McpToolset

auth_scheme = GcpAuthProviderScheme(
    # 기존 V1 API를 사용하는 경우 리소스 이름에 'authProviders' 대신 'connectors'를 사용합니다: projects/.../connectors/...
    name="projects/PROJECT_ID/locations/LOCATION/authProviders/AUTH_PROVIDER_NAME",
    # continue_uri is only needed for 3-legged OAuth flows. This URI receives
    # the redirect after user consent and must be hosted by your application.
    continue_uri=CONTINUE_URI
)

toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(url="https://YOUR_MCP_SERVER_URL"),
    auth_scheme=auth_scheme,
)
```

### OAuth 동의 처리

- **인증 요청 감지**: 기존 흐름과 마찬가지로 사용자 동의가 필요할 때마다
  `auth_uri` 필드를 포함하는 `adk-request-credential`이라는 `FunctionCall` 이벤트가
  생성됩니다. 사용자 앱에서는 팝업 창에서 `auth_uri`를 열어 사용자 동의 흐름을 이어가야
  합니다.
- **Continue URI 핸들러**:
    - 사용자가 서드파티 제공자 웹사이트에서 OAuth 동의 흐름을 완료하면, 시스템은 앞서
      `GcpAuthProviderScheme`에 정의한 `continue_uri` 콜백으로 리다이렉트합니다.
      에이전트 애플리케이션 서비스에서 이 리다이렉트를 구현해야 합니다. 발급을 완료하려면
      핸들러에서 다음 자격 증명 엔드포인트로 POST 요청을 전송해야 합니다:
      `https://agentidentitycredentials.googleapis.com/v1/{auth_provider_name}/credentials:finalize`.
    - 자격 증명 발급 완료 처리가 성공하면 웹 애플리케이션은 `FunctionResponse`를 전송하여
      에이전트를 재개해야 합니다. 샘플 구현은
      [샘플 코드](https://docs.cloud.google.com/iam/docs/auth-with-3lo-v2#resume-conversation)를
      참고하세요. 기본 사용자 동의 흐름과 달리 에이전트를 재개할 때 인증 코드(authorization
      code)는 필요하지 않습니다.
    - 자세한 내용은
      [핸들러 샘플 구현](https://docs.cloud.google.com/iam/docs/auth-with-3lo-v2#validation-endpoint)을
      참고하세요.
- **대화 재개**: 동의 흐름의 성공 여부와 관계없이, 에이전트 앱은 대화 턴(turn)을
  완료하기 위해 에이전트를 재개해야 합니다. ADK는 동의가 정상적으로 완료되었는지
  자동으로 판단하며, 완료되지 않은 경우 오류를 발생시킵니다.

## 리소스

- [Google Cloud Agent Identity 개요](https://docs.cloud.google.com/iam/docs/agent-identity-overview)
- [Google Cloud Agent Identity를 사용한 2-legged OAuth](https://docs.cloud.google.com/iam/docs/auth-with-2lo-v2)
- [Google Cloud Agent Identity를 사용한 3-legged OAuth](https://docs.cloud.google.com/iam/docs/auth-with-3lo-v2)
- [Google Cloud Agent Identity를 사용한 API 키 인증](https://docs.cloud.google.com/iam/docs/auth-with-api-key-v2)
- [샘플 에이전트 코드](https://github.com/google/adk-python/tree/main/src/google/adk/integrations/agent_identity)
