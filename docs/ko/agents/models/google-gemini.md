# ADK 에이전트를 위한 Google Gemini 모델

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">Typescript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

ADK는 다양한 기능을 제공하는 강력한 Gemini 계열의 생성형 AI 모델을 지원합니다.
ADK는 [코드 실행](/adk-docs/tools/gemini-api/code-execution/),
[Google Search](/adk-docs/tools/gemini-api/google-search/),
[컨텍스트 캐싱](/adk-docs/context/caching/),
[컴퓨터 사용](/adk-docs/tools/gemini-api/computer-use/),
및 [Interactions API](#interactions-api)를 비롯해 여러 Gemini 기능을 지원합니다.

## 시작하기

다음 코드 예제는 에이전트에서 Gemini 모델을 사용하는 기본 구현을 보여줍니다.

=== "Python"

    ```python
    from google.adk.agents import LlmAgent

    # --- Example using a stable Gemini Flash model ---
    agent_gemini_flash = LlmAgent(
        # Use the latest stable Flash model identifier
        model="gemini-2.5-flash",
        name="gemini_flash_agent",
        instruction="You are a fast and helpful Gemini assistant.",
        # ... other agent parameters
    )
    ```

=== "TypeScript"

    ```typescript
    import {LlmAgent} from '@google/adk';

    // --- Example #2: using a powerful Gemini Pro model with API Key in model ---
    export const rootAgent = new LlmAgent({
      name: 'hello_time_agent',
      model: 'gemini-2.5-flash',
      description: 'Gemini flash agent',
      instruction: `You are a fast and helpful Gemini assistant.`,
    });
    ```

=== "Go"

    ```go
    import (
    	"google.golang.org/adk/agent/llmagent"
    	"google.golang.org/adk/model/gemini"
    	"google.golang.org/genai"
    )

    --8<-- "examples/go/snippets/agents/models/models.go:gemini-example"
    ```

=== "Java"

    ```java
    // --- Example #1: using a stable Gemini Flash model with ENV variables---
    LlmAgent agentGeminiFlash =
        LlmAgent.builder()
            // Use the latest stable Flash model identifier
            .model("gemini-2.5-flash") // Set ENV variables to use this model
            .name("gemini_flash_agent")
            .instruction("You are a fast and helpful Gemini assistant.")
            // ... other agent parameters
            .build();
    ```


## Gemini 모델 인증

이 섹션에서는 Google AI Studio를 통한 빠른 개발 또는 Google Cloud Vertex AI를 통한 엔터프라이즈 응용에서 Gemini 모델 인증을 다룹니다. ADK 내에서 Google의 대표 모델을 사용하기 위한 가장 직접적인 방법입니다.

**통합 방식:** 아래 중 하나로 인증을 완료하면 `LlmAgent`의 `model` 매개변수에
모델 식별자 문자열을 직접 전달할 수 있습니다.


!!! tip

    ADK가 Gemini 모델에 대해 내부적으로 사용하는 `google-genai` 라이브러리는
    Google AI Studio 또는 Vertex AI 모두를 통해 연결할 수 있습니다.

    **음성/영상 스트리밍 모델 지원**

    ADK에서 음성/영상 스트리밍을 사용하려면 Live API를 지원하는 Gemini 모델을
    사용해야 합니다. Gemini Live API를 지원하는 **모델 ID**는 다음 문서에서 확인할 수 있습니다.

    - [Google AI Studio: Gemini Live API](https://ai.google.dev/gemini-api/docs/models#live-api)
    - [Vertex AI: Gemini Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)

### Google AI Studio

가장 간단한 방식이며 빠른 시작에 권장됩니다.

*   **인증 방식:** API Key
*   **설정:**
    1.  **API 키 획득:** [Google AI Studio](https://aistudio.google.com/apikey)에서 키를 받습니다.
    2.  **환경 변수 설정:** 프로젝트 루트 디렉터리에 `.env`(Python) 또는 `.properties`(Java) 파일을 만들고 다음 라인을 추가합니다. ADK가 해당 파일을 자동으로 로드합니다.

        ```shell
        export GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
        export GOOGLE_GENAI_USE_VERTEXAI=FALSE
        ```

        (또는)

        모델 초기화 시 `Client`를 통해 다음 변수를 전달합니다(아래 예시 참조).

* **모델:** 모든 사용 가능 모델은
  [Google AI for Developers 사이트](https://ai.google.dev/gemini-api/docs/models)에서 확인할 수 있습니다.

### Google Cloud Vertex AI

확장성과 프로덕션 사용에 적합한 방식으로 Vertex AI를 권장합니다.
Vertex AI의 Gemini는 엔터프라이즈급 기능, 보안, 규정 준수 제어를 제공합니다. 개발 환경과 사용 사례에 따라 아래 방법 중 하나를 선택해 인증하세요.

**사전 요구 사항:** [Vertex AI 사용 설정](https://console.cloud.google.com/apis/enableflow;apiid=aiplatform.googleapis.com)이 된 Google Cloud 프로젝트가 있어야 합니다.

### **방식 A: 사용자 자격 증명(로컬 개발용)**

1.  **gcloud CLI 설치:** 공식 [설치 가이드](https://cloud.google.com/sdk/docs/install)를 따릅니다.
2.  **ADC 로그인:** 이 명령은 로컬 개발에서 사용자 계정 인증용 브라우저를 엽니다.
    ```bash
    gcloud auth application-default login
    ```
3.  **환경 변수 설정:**
    ```shell
    export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
    export GOOGLE_CLOUD_LOCATION="YOUR_VERTEX_AI_LOCATION" # e.g., us-central1
    ```

    라이브러리에서 Vertex AI 사용을 명시적으로 지정합니다.

    ```shell
    export GOOGLE_GENAI_USE_VERTEXAI=TRUE
    ```

4. **모델:** 사용 가능한 모델 ID는
  [Vertex AI 문서](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models)에서 확인하세요.

### **방식 B: Vertex AI Express Mode**
[Vertex AI Express Mode](https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview)는 API 키 기반의 간편 설정을 통해 신속한 프로토타이핑을 지원합니다.

1.  **Express Mode 가입** 후 API 키를 발급받습니다.
2.  **환경 변수 설정:**
    ```shell
    export GOOGLE_API_KEY="PASTE_YOUR_EXPRESS_MODE_API_KEY_HERE"
    export GOOGLE_GENAI_USE_VERTEXAI=TRUE
    ```

### **방식 C: 서비스 계정(프로덕션 및 자동화)**

배포된 애플리케이션의 경우 서비스 계정이 표준 방식입니다.

1.  [서비스 계정 생성](https://cloud.google.com/iam/docs/service-accounts-create#console) 후 `Vertex AI User` 역할을 부여합니다.
2.  **애플리케이션에 자격 증명 제공:**
    *   **Google Cloud 환경:** Cloud Run, GKE, VM 또는 기타 Google Cloud 서비스에서 에이전트를 실행하는 경우,
    서비스 계정 자격 증명을 자동으로 주입할 수 있습니다. 별도 키 파일이 필요하지 않습니다.
    *   **기타 환경:** [서비스 계정 키 파일](https://cloud.google.com/iam/docs/keys-create-delete#console)을 생성하고 환경 변수로 경로를 지정하세요.
        ```bash
        export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/keyfile.json"
        ```
    키 파일 대신 Workload Identity로 서비스 계정 인증을 구성할 수도 있습니다. 그러나 이 가이드의 범위를 벗어납니다.

!!! warning "자격 증명 보안"

    서비스 계정 자격 증명이나 API 키는 강력한 권한을 가집니다.
    공개되지 않도록 관리하고, Google Cloud Secret Manager 같은 비밀 관리 서비스를 사용해 안전하게 저장·조회하세요.

!!! note "Gemini 모델 버전"

    최신 모델명은 항상 공식 Gemini 문서를 확인하세요.
    필요한 경우 미리보기 버전은 가용성이나 할당량 제한이 다를 수 있습니다.

## 문제 해결

### 오류 코드 429 - RESOURCE_EXHAUSTED

이 오류는 요청 수가 할당된 처리량을 초과할 때 발생합니다.

다음 방법 중 하나로 완화할 수 있습니다.

1.  사용하려는 모델에 대한 쿼터 상한을 높여달라고 요청합니다.

2.  클라이언트 측 재시도를 활성화합니다. 재시도는 일시적인 할당량 문제 시 대기 후 자동으로 요청을 다시 보내어 완화할 수 있습니다.

    재시도 옵션을 지정하는 방법은 두 가지입니다.

    **옵션 1:** 에이전트에 직접 `generate_content_config`로 재시도 옵션을 설정합니다.

    이 옵션은 이 모델 어댑터 인스턴스를 직접 직접 생성하는 경우에 적합합니다.

    ```python
    root_agent = Agent(
        model='gemini-2.5-flash',
        ...
        generate_content_config=types.GenerateContentConfig(
            ...
            http_options=types.HttpOptions(
                ...
                retry_options=types.HttpRetryOptions(initial_delay=1, attempts=2),
                ...
            ),
            ...
        )
    ```

    **옵션 2:** 모델 어댑터의 재시도 옵션을 설정합니다.

    이 옵션은 어댑터 인스턴스를 직접 생성하지 않고,
---
    기존 코드에서 설정하는 경우에 적합합니다.

    ```python
    from google.genai import types

    # ...

    agent = Agent(
        model=Gemini(
        retry_options=types.HttpRetryOptions(initial_delay=1, attempts=2),
        )
    )
    ```

## Gemini Interactions API {#interactions-api}

<div class="language-support-tag" title="Java ADK에서는 Gemini와 Anthropic 모델만 현재 지원됩니다.">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.21.0</span>
</div>

Gemini [Interactions API](https://ai.google.dev/gemini-api/docs/interactions)
는 `generateContent` 추론 API의 대안으로, 전체 대화 내역을 매번 전송하지 않고
`previous_interaction_id`를 통해 상호작용을 연결할 수 있는 상태 유지 대화 기능을 제공합니다.
긴 대화에서는 더 효율적으로 동작할 수 있습니다.

다음 코드 조각처럼 Gemini 모델 구성의 `use_interactions_api=True`
매개변수를 설정하면 Interactions API를 사용할 수 있습니다.

```python
from google.adk.agents.llm_agent import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools.google_search_tool import GoogleSearchTool

root_agent = Agent(
    model=Gemini(
        model="gemini-2.5-flash",
        use_interactions_api=True,  # Interactions API 사용
    ),
    name="interactions_test_agent",
    tools=[
        GoogleSearchTool(bypass_multi_tools_limit=True),  # Function tool로 변환
        get_current_weather,  # 커스텀 함수 도구
    ],
)
```

전체 샘플 코드는
[Interactions API 샘플](https://github.com/google/adk-python/tree/main/contributing/samples/interactions_api)을 참조하세요.

### 알려진 제한

Interactions API는 [Google Search](/adk-docs/tools/built-in-tools/#google-search)와 같은
커스텀 함수 호출 도구와 내장 도구를 동일 에이전트에서 함께 사용할 수 **없습니다**.
`bypass_multi_tools_limit` 매개변수를 사용해 내장 도구를 커스텀 도구로 동작하도록 설정하여 제한을 우회할 수 있습니다.

```python
# Use bypass_multi_tools_limit=True to convert google_search to a function tool
GoogleSearchTool(bypass_multi_tools_limit=True)
```

이 예제에서 이 옵션은 내장 google_search을 함수 호출 도구(구글서치 에이전트 도구인
GoogleSearchAgentTool)로 변환하므로, 커스텀 함수 도구와 함께 사용할 수 있습니다.
