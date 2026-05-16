---
catalog_title: Google Cloud Agent Identity
catalog_description: 에이전트의 OAuth 토큰과 API 키를 관리합니다
catalog_icon: /integrations/assets/agent-identity.svg
catalog_tags: ["google"]
---

# ADK용 Agent Identity Auth Manager

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.30.0</span><span class="lst-preview">Preview</span>
</div>

[Google Cloud Agent Identity](https://docs.cloud.google.com/iam/docs/agent-identity-overview)
서비스는 자격 증명 구성 저장, 토큰 생성 및 저장, 접근 감사 등 인증 자격 증명의 전체
수명 주기를 관리하는 간소화된 Google 관리형 솔루션을 제공합니다. 이 접근 방식은
안전하고 단순한 에이전트 개발 경험을 가능하게 합니다.

!!! example "Preview release"

    Agent Identity Auth Manager 기능은 Preview 릴리스입니다. 자세한 내용은
    [출시 단계 설명](https://cloud.google.com/products#product-launch-stages)을
    참고하세요.

## 사용 사례

- **간소화된 OAuth 흐름**: 커스텀 인프라를 만들지 않고 인증 자격 증명의 전체 수명
  주기를 관리합니다.
- **토큰의 안전한 교환 및 저장**: 자격 증명 구성을 안전하게 저장하고 토큰을 교환합니다.
- **감사 로깅**: 저장된 자격 증명에 대한 접근을 확인하고 감사합니다.

## 전제 조건

- [Google Cloud 프로젝트](https://cloud.google.com/resource-manager/docs/creating-managing-projects)
- 프로젝트에 생성된 하나 이상의 Agent Identity
  [auth provider](https://cloud.google.com/iam/docs/manage-auth-providers)
- 호출자 ID에
  [`iamconnectors.user`](https://docs.cloud.google.com/iam/docs/roles-permissions/iamconnectors#iamconnectors.user)
  역할 또는 동등한 권한 필요
- [Application Default Credentials](https://docs.cloud.google.com/docs/authentication/application-default-credentials)
  (`gcloud auth application-default login`)로 인증 구성

## 설치

필요한 클라이언트 라이브러리를 다운로드하려면 `agent-identity` extra package group을
설치합니다.

```bash
pip install "google-adk[agent-identity]"
```

## 에이전트와 함께 사용

ADK 안에서 Agent Identity Auth Manager를 사용하려면 다음 단계를 따르세요.

### Auth provider 등록

ADK가 지정된 `CustomAuthScheme`에 사용할 `BaseAuthProvider`를 결정할 수 있도록
`GcpAuthProvider` 인스턴스를 `CredentialManager`에 등록합니다. 이 작업은 에이전트
코드에서 한 번만 수행하면 됩니다.

```python
from google.adk.auth.credential_manager import CredentialManager
from google.adk.integrations.agent_identity import GcpAuthProvider

CredentialManager.register_auth_provider(GcpAuthProvider())
```

### 도구 구성

`GcpAuthProviderScheme` 객체로 Agent Identity auth provider를 구성한 다음, 지원되는
`Tool` 또는 `Toolset`의 `auth_scheme` 매개변수로 전달합니다. 다음 예제는
`McpToolset`과 함께 사용하는 방법을 보여주지만, `GcpAuthProviderScheme`은
`AuthenticatedFunctionTool` 같은 다른 도구와도 함께 사용할 수 있습니다. 전체 예제는
[GCP Auth sample](https://github.com/google/adk-python/tree/main/contributing/samples/gcp_auth)을
참고하세요.

```python
from google.adk.integrations.agent_identity import GcpAuthProviderScheme
from google.adk.tools.mcp import McpToolset

auth_scheme = GcpAuthProviderScheme(
    name="projects/PROJECT_ID/locations/LOCATION/connectors/AUTH_PROVIDER_NAME",
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

- **Auth Request 감지**: 기존 흐름과 유사하게 사용자 동의가 필요할 때마다
  `adk-request-credential`이라는 `FunctionCall` 이벤트가 생성되고 `auth_uri` 필드를
  포함합니다. 사용자 앱은 사용자 동의 흐름을 계속 진행하기 위해 팝업 창에서
  `auth_uri`를 열어야 합니다.
- **Continue URI Handler**:
    - 사용자가 타사 provider 웹사이트에서 OAuth 동의 흐름을 완료하면, 시스템은 앞서
      `GcpAuthProviderScheme`에 정의한 `continue_uri` callback으로 redirect합니다.
      에이전트 애플리케이션 서비스는 이 redirect를 구현해야 합니다. 발급을 마무리하려면
      handler가 credentials endpoint로 POST 요청을 제출해야 합니다.
      `https://iamconnectorcredentials.googleapis.com/v1alpha/{connector_name}/credentials:finalize`.
    - 자격 증명 finalization이 성공하면 웹 애플리케이션은 FunctionResponse를 보내
      에이전트를 재개해야 합니다. 샘플 구현은
      [sample code](https://docs.cloud.google.com/iam/docs/auth-with-3lo#resume-conversation)를
      참고하세요. 네이티브 사용자 동의 흐름과 달리 에이전트를 재개하는 데 authorization
      code가 필요하지 않습니다.
    - 자세한 내용은
      [sample handler implementation](https://docs.cloud.google.com/iam/docs/auth-with-3lo#validation-endpoint)을
      참고하세요.
- **대화 재개**: 동의 흐름의 성공 여부와 관계없이, 에이전트 앱은 conversation turn을
  완료하기 위해 에이전트를 재개해야 합니다. ADK는 동의가 성공적으로 완료되었는지
  자동으로 판단하고, 완료되지 않은 경우 오류를 발생시킵니다.

## 리소스

- [Google Cloud Agent Identity Overview](https://docs.cloud.google.com/iam/docs/agent-identity-overview)
- [Google Cloud Agent Identity를 사용한 2-legged OAuth](https://docs.cloud.google.com/iam/docs/auth-with-2lo)
- [Google Cloud Agent Identity를 사용한 3-legged OAuth](https://docs.cloud.google.com/iam/docs/auth-with-3lo)
- [Google Cloud Agent Identity를 사용한 API key auth](https://docs.cloud.google.com/iam/docs/auth-with-api-key)
- [Sample agent code](https://github.com/google/adk-python/tree/main/contributing/samples/gcp_auth)
