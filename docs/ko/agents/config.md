# 에이전트 구성을 사용하여 에이전트 빌드

<div class="language-support-tag">
  <span class="lst-supported">ADK 지원</span><span class="lst-python">Python v1.11.0</span><span class="lst-preview">실험용</span>
</div>

ADK 에이전트 구성 기능을 사용하면 코드를 작성하지 않고도 ADK 워크플로를 빌드할 수 있습니다. 에이전트 구성은 에이전트에 대한 간략한 설명이 포함된 YAML 형식 텍스트 파일을 사용하므로 누구나 ADK 에이전트를 조립하고 실행할 수 있습니다. 다음은 기본 에이전트 구성 정의의 간단한 예입니다.

```
name: assistant_agent
model: gemini-2.5-flash
description: 사용자의 질문에 답변할 수 있는 도우미 에이전트입니다.
instruction: 사용자의 다양한 질문에 답변하는 에이전트입니다.
```

에이전트 구성 파일을 사용하여 함수, 도구, 하위 에이전트 등을 통합할 수 있는 더 복잡한 에이전트를 빌드할 수 있습니다. 이 페이지에서는 에이전트 구성 기능을 사용하여 ADK 워크플로를 빌드하고 실행하는 방법을 설명합니다. 에이전트 구성 형식에서 지원하는 구문 및 설정에 대한 자세한 내용은 [에이전트 구성 구문 참조](/adk-docs/api-reference/agentconfig/)를 참조하세요.

!!! example "실험용"
    에이전트 구성 기능은 실험용이며 [알려진 제한 사항](#known-limitations)이 있습니다. [피드백](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=agent%20config)을 환영합니다!

## 시작하기

이 섹션에서는 설치 설정, 에이전트 빌드 및 에이전트 실행을 포함하여 ADK 및 에이전트 구성 기능을 사용하여 에이전트 빌드를 설정하고 시작하는 방법을 설명합니다.

### 설정

Google Agent Development Kit 라이브러리를 설치하고 Gemini API와 같은 생성형 AI 모델에 대한 액세스 키를 제공해야 합니다. 이 섹션에서는 에이전트 구성 파일로 에이전트를 실행하기 전에 설치하고 구성해야 하는 사항에 대한 세부 정보를 제공합니다.

!!! note
    에이전트 구성 기능은 현재 Gemini 모델만 지원합니다. 추가 기능 제한에 대한 자세한 내용은 [알려진 제한 사항](#known-limitations)을 참조하세요.

에이전트 구성과 함께 사용하도록 ADK를 설정하려면:

1.  [설치](/adk-docs/get-started/installation/#python) 지침에 따라 ADK Python 라이브러리를 설치합니다. *현재 Python이 필요합니다.* 자세한 내용은 [알려진 제한 사항](?tab=t.0#heading=h.xefmlyt7zh0i)을 참조하세요.
1.  터미널에서 다음 명령어를 실행하여 ADK가 설치되었는지 확인합니다.

        adk --version

    이 명령어는 설치된 ADK 버전을 보여줍니다.

!!! Tip
    `adk` 명령어가 실행되지 않고 2단계에서 버전이 나열되지 않으면 Python 환경이 활성화되어 있는지 확인하세요. Mac 및 Linux 터미널에서 `source .venv/bin/activate`를 실행합니다. 다른 플랫폼 명령어는 [설치](/adk-docs/get-started/installation/#python) 페이지를 참조하세요.

### 에이전트 빌드

`adk create` 명령어를 사용하여 에이전트 구성으로 에이전트를 빌드하여 에이전트용 프로젝트 파일을 만들고 생성된 `root_agent.yaml` 파일을 편집합니다.

에이전트 구성과 함께 사용할 ADK 프로젝트를 만들려면:

1.  터미널 창에서 다음 명령어를 실행하여 구성 기반 에이전트를 만듭니다.

        adk create --type=config my_agent

    이 명령어는 `root_agent.yaml` 파일과 `.env` 파일이 포함된 `my_agent/` 폴더를 생성합니다.

1.  `my_agent/.env` 파일에서 에이전트가 생성형 AI 모델 및 기타 서비스에 액세스할 수 있도록 환경 변수를 설정합니다.

    1.  Google API를 통해 Gemini 모델에 액세스하려면 파일에 API 키가 포함된 줄을 추가합니다.

            GOOGLE_GENAI_USE_VERTEXAI=0
            GOOGLE_API_KEY=<your-Google-Gemini-API-key>

        Google AI Studio [API 키](https://aistudio.google.com/app/apikey) 페이지에서 API 키를 얻을 수 있습니다.

    1.  Google Cloud를 통해 Gemini 모델에 액세스하려면 다음 줄을 파일에 추가합니다.

            GOOGLE_GENAI_USE_VERTEXAI=1
            GOOGLE_CLOUD_PROJECT=<your_gcp_project>
            GOOGLE_CLOUD_LOCATION=us-central1

        Cloud 프로젝트 생성에 대한 자세한 내용은 Google Cloud 문서의 [프로젝트 생성 및 관리](https://cloud.google.com/resource-manager/docs/creating-managing-projects)를 참조하세요.

1.  텍스트 편집기를 사용하여 아래와 같이 에이전트 구성 파일 `my_agent/root_agent.yaml`을 편집합니다.

```
# yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
name: assistant_agent
model: gemini-2.5-flash
description: 사용자의 질문에 답변할 수 있는 도우미 에이전트입니다.
instruction: 사용자의 다양한 질문에 답변하는 에이전트입니다.
```

ADK [샘플 저장소](https://github.com/search?q=repo%3Agoogle%2Fadk-python+path%3A%2F%5Econtributing%5C%2Fsamples%5C%2F%2F+.yaml&type=code) 또는 [에이전트 구성 구문](/adk-docs/api-reference/agentconfig/) 참조를 통해 `root_agent.yaml` 에이전트 구성 파일에 대한 더 많은 구성 옵션을 찾을 수 있습니다.

### 에이전트 실행

에이전트 구성 편집을 완료하면 웹 인터페이스, 명령줄 터미널 실행 또는 API 서버 모드를 사용하여 에이전트를 실행할 수 있습니다.

에이전트 구성으로 정의된 에이전트를 실행하려면:

1.  터미널에서 `root_agent.yaml` 파일이 포함된 `my_agent/` 디렉토리로 이동합니다.
1.  다음 명령어 중 하나를 입력하여 에이전트를 실행합니다.
    -   `adk web` - 에이전트용 웹 UI 인터페이스를 실행합니다.
    -   `adk run` - 사용자 인터페이스 없이 터미널에서 에이전트를 실행합니다.
    -   `adk api_server` - 다른 애플리케이션에서 사용할 수 있는 서비스로 에이전트를 실행합니다.

에이전트 실행 방법에 대한 자세한 내용은 [빠른 시작](/adk-docs/get-started/quickstart/#run-your-agent)의 *에이전트 실행* 항목을 참조하세요. ADK 명령줄 옵션에 대한 자세한 내용은 [ADK CLI 참조](/adk-docs/api-reference/cli/)를 참조하세요.

## 예시 구성

이 섹션에서는 에이전트 빌드를 시작하는 데 도움이 되는 에이전트 구성 파일의 예시를 보여줍니다. 추가적이고 더 완전한 예시는 ADK [샘플 저장소](https://github.com/search?q=repo%3Agoogle%2Fadk-python+path%3A%2F%5Econtributing%5C%2Fsamples%5C%2F%2F+root_agent.yaml&type=code)를 참조하세요.

### 내장 도구 예시

다음 예시는 Google 검색을 사용하여 에이전트에 기능을 제공하는 내장 ADK 도구 함수를 사용합니다. 이 에이전트는 검색 도구를 자동으로 사용하여 사용자 요청에 응답합니다.

```
# yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
name: search_agent
model: gemini-2.0-flash
description: 'Google 검색 쿼리를 수행하고 결과에 대한 질문에 답변하는 에이전트.'
instruction: Google 검색 쿼리를 수행하고 결과에 대한 질문에 답변하는 에이전트입니다.
tools:
  - name: google_search
```

자세한 내용은 [ADK 샘플 저장소](https://github.com/google/adk-python/blob/main/contributing/samples/tool_builtin_config/root_agent.yaml)에서 이 샘플의 전체 코드를 참조하세요.

### 커스텀 도구 예시

다음 예시는 Python 코드로 빌드되고 구성 파일의 `tools:` 섹션에 나열된 커스텀 도구를 사용합니다. 에이전트는 이 도구를 사용하여 사용자가 제공한 숫자 목록이 소수인지 확인합니다.

```
# yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
agent_class: LlmAgent
model: gemini-2.5-flash
name: prime_agent
description: 숫자가 소수인지 확인하는 것을 처리합니다.
instruction: |
  숫자가 소수인지 확인하는 일을 담당합니다.
  소수인지 확인하라는 요청을 받으면 정수 목록으로 check_prime 도구를 호출해야 합니다.
  절대로 수동으로 소수를 확인하려고 시도하지 마세요.
  소수 결과를 루트 에이전트에 반환합니다.
tools:
  - name: ma_llm.check_prime
```

자세한 내용은 [ADK 샘플 저장소](https://github.com/google/adk-python/blob/main/contributing/samples/multi_agent_llm_config/prime_agent.yaml)에서 이 샘플의 전체 코드를 참조하세요.

### 하위 에이전트 예시

다음 예시는 구성 파일의 `sub_agents:` 섹션에 두 개의 하위 에이전트와 `tools:` 섹션에 예시 도구가 정의된 에이전트를 보여줍니다. 이 에이전트는 사용자가 원하는 것을 결정하고 요청을 해결하기 위해 하위 에이전트 중 하나에 위임합니다. 하위 에이전트는 에이전트 구성 YAML 파일을 사용하여 정의됩니다.

```
# yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
agent_class: LlmAgent
model: gemini-2.5-flash
name: root_agent
description: 코드 및 수학 튜터링을 제공하는 학습 도우미.
instruction: |
  코드 및 수학 질문에 대해 학생들을 돕는 학습 도우미입니다.

  코딩 질문은 code_tutor_agent에, 수학 질문은 math_tutor_agent에 위임합니다.

  다음 단계를 따르세요.
  1. 사용자가 프로그래밍 또는 코딩에 대해 질문하면 code_tutor_agent에 위임합니다.
  2. 사용자가 수학 개념 또는 문제에 대해 질문하면 math_tutor_agent에 위임합니다.
  3. 항상 명확한 설명을 제공하고 학습을 장려하세요.
sub_agents:
  - config_path: code_tutor_agent.yaml
  - config_path: math_tutor_agent.yaml
```

자세한 내용은 [ADK 샘플 저장소](https://github.com/google/adk-python/blob/main/contributing/samples/multi_agent_basic_config/root_agent.yaml)에서 이 샘플의 전체 코드를 참조하세요.

## 에이전트 구성 배포

코드 기반 에이전트와 동일한 절차를 사용하여 [Cloud Run](/adk-docs/deploy/cloud-run/) 및 [에이전트 엔진](/adk-docs/deploy/agent-engine/)을 사용하여 에이전트 구성 에이전트를 배포할 수 있습니다. 에이전트 구성 기반 에이전트를 준비하고 배포하는 방법에 대한 자세한 내용은 [Cloud Run](/adk-docs/deploy/cloud-run/) 및 [에이전트 엔진](/adk-docs/deploy/agent-engine/) 배포 가이드를 참조하세요.

## 알려진 제한 사항 {#known-limitations}

에이전트 구성 기능은 실험용이며 다음과 같은 제한 사항이 있습니다.

-   **모델 지원:** 현재 Gemini 모델만 지원됩니다. 타사 모델과의 통합은 진행 중입니다.
-   **프로그래밍 언어:** 에이전트 구성 기능은 현재 도구 및 프로그래밍 코드가 필요한 기타 기능에 대해 Python 코드만 지원합니다.
-   **ADK 도구 지원:** 다음 ADK 도구는 에이전트 구성 기능에서 지원되지만 *모든 도구가 완전히 지원되는 것은 아닙니다*.
    -   `google_search`
    -   `load_artifacts`
    -   `url_context`
    -   `exit_loop`
    -   `preload_memory`
    -   `get_user_choice`
    -   `enterprise_web_search`
    -   `load_web_page`: 웹 페이지에 액세스하려면 정규화된 경로가 필요합니다.
-   **에이전트 유형 지원:** `LangGraphAgent` 및 `A2aAgent` 유형은 아직 지원되지 않습니다.
    -   `AgentTool`
    -   `LongRunningFunctionTool`
    -   `VertexAiSearchTool`
    -   `McpToolset`
    -   `ExampleTool`

## 다음 단계

ADK 에이전트 구성으로 무엇을 어떻게 빌드할지에 대한 아이디어는 ADK [adk-samples](https://github.com/search?q=repo:google/adk-python+path:/%5Econtributing%5C/samples%5C//+root_agent.yaml&type=code) 저장소의 YAML 기반 에이전트 정의를 참조하세요. 에이전트 구성 형식에서 지원하는 구문 및 설정에 대한 자세한 내용은 [에이전트 구성 구문 참조](/adk-docs/api-reference/agentconfig/)를 참조하세요.