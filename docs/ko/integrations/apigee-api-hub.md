---
catalog_title: Apigee API Hub
catalog_description: Apigee API hub의 문서화된 API를 도구로 손쉽게 변환
catalog_icon: /adk-docs/integrations/assets/apigee.png
catalog_tags: ["connectors", "google"]
---

# ADK용 Apigee API Hub 도구

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span>
</div>

**ApiHubToolset**을 사용하면 Apigee API Hub의 문서화된 API를
코드 몇 줄만으로 도구로 변환할 수 있습니다.
이 문서에서는 API와의 안전한 연결을 위한 인증 설정을 포함해 단계별 방법을 설명합니다.

**사전 준비**

1. [ADK 설치](/adk-docs/get-started/installation/)
2. [Google Cloud CLI](https://cloud.google.com/sdk/docs/install?db=bigtable-docs#installation_instructions) 설치
3. 문서화된(OpenAPI 사양) API를 보유한 [Apigee API Hub](https://cloud.google.com/apigee/docs/apihub/what-is-api-hub) 인스턴스
4. 프로젝트 구조를 설정하고 필요한 파일 생성

```console
project_root_folder
 |
 `-- my_agent
     |-- .env
     |-- __init__.py
     |-- agent.py
     `__ tool.py
```

## API Hub Toolset 생성

참고: 이 튜토리얼에는 에이전트 생성이 포함됩니다. 이미 에이전트가 있다면 일부 단계만 따르면 됩니다.

1. APIHubToolset이 API Hub API에서 명세를 가져오도록 접근 토큰을 가져옵니다.
   터미널에서 다음 명령 실행:

    ```shell
    gcloud auth print-access-token
    # 'ya29....' 같은 액세스 토큰이 출력됩니다.
    ```

2. 사용 계정이 필요한 권한을 갖추었는지 확인합니다. 미리 정의된 역할 `roles/apihub.viewer`를 사용하거나 다음 권한을 부여할 수 있습니다.

    1. **apihub.specs.get (필수)**
    2. apihub.apis.get (선택)
    3. apihub.apis.list (선택)
    4. apihub.versions.get (선택)
    5. apihub.versions.list (선택)
    6. apihub.specs.list (선택)

3. `tools.py`에 `APIHubToolset`으로 도구를 생성합니다.

   API가 인증을 요구하면 도구에 인증을 구성해야 합니다. 다음 코드 샘플은 API 키 설정을 보여줍니다.
   ADK는 토큰 기반 인증(API Key, Bearer token), 서비스 계정, OpenID Connect를 지원합니다. 향후 다양한 OAuth2 플로우를 지원할 예정입니다.

    ```py
    from google.adk.tools.openapi_tool.auth.auth_helpers import token_to_scheme_credential
    from google.adk.tools.apihub_tool.apihub_toolset import APIHubToolset

    # API에 대한 인증 제공. 인증이 필요 없는 API라면 생략 가능
    auth_scheme, auth_credential = token_to_scheme_credential(
        "apikey", "query", "apikey", apikey_credential_str
    )

    sample_toolset = APIHubToolset(
        name="apihub-sample-tool",
        description="Sample Tool",
        access_token="...",  # 단계 1에서 생성한 액세스 토큰을 붙여넣으세요
        apihub_resource_name="...", # API Hub 리소스 이름
        auth_scheme=auth_scheme,
        auth_credential=auth_credential,
    )
    ```

   운영 환경 배포에서는 접근 토큰 대신 서비스 계정 사용을 권장합니다.
   위 코드 조각에서는 `service_account_json=service_account_cred_json_str`를 사용하고,
   토큰 대신 서비스 계정 자격 증명을 제공합니다.

   apihub\_resource\_name의 경우, API에 사용 중인 OpenAPI Spec의 특정 ID를 알고 있으면
   `` `projects/my-project-id/locations/us-west1/apis/my-api-id/versions/version-id/specs/spec-id` ``를 사용합니다.
   Toolset이 API에서 사용 가능한 첫 번째 spec을 자동으로 가져오게 하려면
   `` `projects/my-project-id/locations/us-west1/apis/my-api-id` ``를 사용합니다.

4. Agent.py를 만들고 생성한 도구를 에이전트 정의에 추가합니다.

    ```py
    from google.adk.agents.llm_agent import LlmAgent
    from .tools import sample_toolset

    root_agent = LlmAgent(
        model='gemini-2.0-flash',
        name='enterprise_assistant',
        instruction='Help user, leverage the tools you have access to',
        tools=sample_toolset.get_tools(),
    )
    ```

5. `__init__.py`를 구성해 에이전트를 노출합니다.

    ```py
    from . import agent
    ```

6. Google ADK Web UI를 시작하고 에이전트를 실행합니다.

    ```shell
    # `project_root_folder`에서 `adk web` 실행
    adk web
    ```

   그런 다음 [http://localhost:8000](http://localhost:8000)로 이동해 웹 UI에서 에이전트를 테스트하세요.
