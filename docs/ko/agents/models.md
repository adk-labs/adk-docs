# ADK에서 다양한 모델 사용

<div class="language-support-tag" title="Java ADK는 현재 Gemini 및 Anthropic 모델을 지원합니다.">
  <span class="lst-supported">ADK 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

ADK(Agent Development Kit)는 유연성을 위해 설계되었으며, 다양한 대규모 언어 모델(LLM)을 에이전트에 통합할 수 있습니다. Google Gemini 모델의 설정은 [기반 모델 설정](../get-started/installation.md) 가이드에 설명되어 있지만, 이 페이지에서는 Gemini를 효과적으로 활용하고 외부에서 호스팅되거나 로컬에서 실행되는 모델을 포함한 다른 인기 있는 모델을 통합하는 방법에 대해 자세히 설명합니다.

ADK는 주로 모델 통합을 위해 두 가지 메커니즘을 사용합니다.

1. **직접 문자열 / 레지스트리:** Google Cloud와 긴밀하게 통합된 모델(Google AI Studio 또는 Vertex AI를 통해 액세스하는 Gemini 모델과 같은) 또는 Vertex AI 엔드포인트에서 호스팅되는 모델의 경우. 일반적으로 모델 이름 또는 엔드포인트 리소스 문자열을 `LlmAgent`에 직접 제공합니다. ADK의 내부 레지스트리는 이 문자열을 적절한 백엔드 클라이언트로 확인하며, 종종 `google-genai` 라이브러리를 활용합니다.
2. **래퍼 클래스:** Google 생태계 외부의 모델 또는 특정 클라이언트 구성이 필요한 모델(Apigee 또는 LiteLLM을 통해 액세스하는 모델과 같은)과의 광범위한 호환성을 위해. 특정 래퍼 클래스(예: `ApigeeLlm` 또는 `LiteLlm`)를 인스턴스화하고 이 객체를 `LlmAgent`의 `model` 매개변수로 전달합니다.

다음 섹션에서는 필요에 따라 이러한 방법을 사용하는 방법에 대해 안내합니다.

## Google Gemini 모델 사용

이 섹션에서는 빠른 개발을 위한 Google AI Studio 또는 엔터프라이즈 애플리케이션을 위한 Google Cloud Vertex AI를 통해 Google Gemini 모델을 사용하여 인증하는 방법에 대해 설명합니다. 이는 ADK 내에서 Google의 주력 모델을 사용하는 가장 직접적인 방법입니다.

**통합 방법:** 아래 방법 중 하나를 사용하여 인증하면 모델의 식별자 문자열을 `LlmAgent`의 `model` 매개변수에 직접 전달할 수 있습니다.

!!! tip

    ADK가 Gemini 모델에 내부적으로 사용하는 `google-genai` 라이브러리는 Google AI Studio 또는 Vertex AI를 통해 연결할 수 있습니다.

    **음성/영상 스트리밍을 위한 모델 지원**

    ADK에서 음성/영상 스트리밍을 사용하려면 라이브 API를 지원하는 Gemini 모델을 사용해야 합니다. Gemini 라이브 API를 지원하는 **모델 ID**는 다음 문서에서 찾을 수 있습니다.

    - [Google AI Studio: Gemini 라이브 API](https://ai.google.dev/gemini-api/docs/models#live-api)
    - [Vertex AI: Gemini 라이브 API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)

### Google AI Studio

가장 간단한 방법이며 빠르게 시작하는 데 권장됩니다.

*   **인증 방법:** API 키
*   **설정:**
    1.  **API 키 가져오기:** [Google AI Studio](https://aistudio.google.com/apikey)에서 키를 얻습니다.
    2.  **환경 변수 설정:** 프로젝트의 루트 디렉토리에 `.env` 파일(Python) 또는 `.properties` 파일(Java)을 만들고 다음 줄을 추가합니다. ADK는 이 파일을 자동으로 로드합니다.

        ```shell
        export GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
        export GOOGLE_GENAI_USE_VERTEXAI=FALSE
        ```

        (또는)

        `Client`를 통해 모델 초기화 중에 이 변수들을 전달합니다(아래 예시 참조).

* **모델:** [Google AI for Developers 사이트](https://ai.google.dev/gemini-api/docs/models)에서 사용 가능한 모든 모델을 찾습니다.

### Google Cloud Vertex AI

확장 가능하고 프로덕션 지향적인 사용 사례의 경우 Vertex AI가 권장되는 플랫폼입니다. Vertex AI의 Gemini는 엔터프라이즈급 기능, 보안 및 규정 준수 제어를 지원합니다. 개발 환경 및 사용 사례에 따라 *아래 인증 방법 중 하나를 선택하십시오*.

**필수 조건:** [Vertex AI가 활성화된](https://console.cloud.google.com/apis/enableflow;apiid=aiplatform.googleapis.com) Google Cloud 프로젝트.

### **방법 A: 사용자 인증 정보 (로컬 개발용)**

1.  **gcloud CLI 설치:** 공식 [설치 지침](https://cloud.google.com/sdk/docs/install)을 따릅니다.
2.  **ADC를 사용하여 로그인:** 이 명령어는 브라우저를 열어 로컬 개발을 위한 사용자 계정을 인증합니다.
    ```bash
    gcloud auth application-default login
    ```
3.  **환경 변수 설정:**
    ```shell
    export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
    export GOOGLE_CLOUD_LOCATION="YOUR_VERTEX_AI_LOCATION" # 예: us-central1
    ```

    라이브러리에 Vertex AI를 사용하도록 명시적으로 지시합니다.

    ```shell
    export GOOGLE_GENAI_USE_VERTEXAI=TRUE
    ```

4. **모델:** [Vertex AI 문서](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models)에서 사용 가능한 모델 ID를 찾습니다.

### **방법 B: Vertex AI Express 모드**
[Vertex AI Express 모드](https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview)는 빠른 프로토타이핑을 위한 간소화된 API 키 기반 설정을 제공합니다.

1.  **Express 모드에 가입**하여 API 키를 받습니다.
2.  **환경 변수 설정:**
    ```shell
    export GOOGLE_API_KEY="PASTE_YOUR_EXPRESS_MODE_API_KEY_HERE"
    export GOOGLE_GENAI_USE_VERTEXAI=TRUE
    ```

### **방법 C: 서비스 계정 (프로덕션 및 자동화용)**

배포된 애플리케이션의 경우 서비스 계정이 표준 방법입니다.

1.  [**서비스 계정 생성**](https://cloud.google.com/iam/docs/service-accounts-create#console) 및 `Vertex AI User` 역할을 부여합니다.
2.  **애플리케이션에 자격 증명 제공:**
    *   **Google Cloud에서:** Cloud Run, GKE, VM 또는 기타 Google Cloud 서비스에서 에이전트를 실행하는 경우 환경에서 서비스 계정 자격 증명을 자동으로 제공할 수 있습니다. 키 파일을 만들 필요가 없습니다.
    *   **다른 곳에서:** [서비스 계정 키 파일](https://cloud.google.com/iam/docs/keys-create-delete#console)을 만들고 환경 변수를 사용하여 가리킵니다.
        ```bash
        export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/keyfile.json"
        ```
    키 파일 대신 워크로드 아이덴티티를 사용하여 서비스 계정을 인증할 수도 있습니다. 그러나 이는 이 가이드의 범위를 벗어납니다.

**예시:**

=== "Python"

    ```python
    from google.adk.agents import LlmAgent

    # --- 안정적인 Gemini Flash 모델을 사용하는 예시 ---
    agent_gemini_flash = LlmAgent(
        # 최신 안정 Flash 모델 식별자 사용
        model="gemini-2.0-flash",
        name="gemini_flash_agent",
        instruction="당신은 빠르고 유용한 Gemini 도우미입니다.",
        # ... 기타 에이전트 매개변수
    )

    # --- 강력한 Gemini Pro 모델을 사용하는 예시 ---
    # 참고: 필요한 경우 특정 프리뷰 버전을 포함하여 최신 모델 이름에 대한 공식 Gemini 문서를 항상 확인하세요.
    # 프리뷰 모델은 가용성 또는 할당량 제한이 다를 수 있습니다.
    agent_gemini_pro = LlmAgent(
        # 최신 일반 출시 Pro 모델 식별자 사용
        model="gemini-2.5-pro-preview-03-25",
        name="gemini_pro_agent",
        instruction="당신은 강력하고 지식이 풍부한 Gemini 도우미입니다.",
        # ... 기타 에이전트 매개변수
    )
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
    // --- 예시 #1: 환경 변수를 사용하여 안정적인 Gemini Flash 모델 사용 ---
    LlmAgent agentGeminiFlash =
        LlmAgent.builder()
            // 최신 안정 Flash 모델 식별자 사용
            .model("gemini-2.0-flash") // 이 모델을 사용하도록 ENV 변수 설정
            .name("gemini_flash_agent")
            .instruction("당신은 빠르고 유용한 Gemini 도우미입니다.")
            // ... 기타 에이전트 매개변수
            .build();

    // --- 예시 #2: 모델에 API 키가 있는 강력한 Gemini Pro 모델 사용 ---
    LlmAgent agentGeminiPro =
        LlmAgent.builder()
            // 최신 일반 출시 Pro 모델 식별자 사용
            .model(new Gemini("gemini-2.5-pro-preview-03-25",
                Client.builder()
                    .vertexAI(false)
                    .apiKey("API_KEY") // API 키 설정 (또는) 프로젝트/위치
                    .build()))
            // 또는 API_KEY를 직접 전달할 수도 있습니다.
            // .model(new Gemini("gemini-2.5-pro-preview-03-25", "API_KEY"))
            .name("gemini_pro_agent")
            .instruction("당신은 강력하고 지식이 풍부한 Gemini 도우미입니다."),
            // ... 기타 에이전트 매개변수
            .build();

    // 참고: 필요한 경우 특정 프리뷰 버전을 포함하여 최신 모델 이름에 대한 공식 Gemini 문서를 항상 확인하세요.
    // 프리뷰 모델은 가용성 또는 할당량 제한이 다를 수 있습니다.
    ```

!!! warning "자격 증명 보안 유지"

    서비스 계정 자격 증명 또는 API 키는 강력한 자격 증명입니다. 공개적으로 노출하지 마세요.
    [Google Cloud Secret Manager](https://cloud.google.com/security/products/secret-manager)와 같은
    보안 관리자를 사용하여 프로덕션 환경에서 안전하게 저장하고 액세스하세요.

### 문제 해결

#### 오류 코드 429 - RESOURCE_EXHAUSTED

이 오류는 일반적으로 요청 수가 요청을 처리하기 위해 할당된 용량을 초과할 때 발생합니다.

이를 완화하려면 다음 중 하나를 수행할 수 있습니다.

1.  사용하려는 모델에 대해 더 높은 할당량 제한을 요청합니다.

2.  클라이언트 측 재시도를 활성화합니다. 재시도를 사용하면 클라이언트가 지연 후 요청을 자동으로 재시도할 수 있으므로 할당량 문제가 일시적인 경우에 도움이 될 수 있습니다.

    재시도 옵션을 설정하는 방법은 두 가지가 있습니다.

    **옵션 1:** generate_content_config의 일부로 에이전트에서 재시도 옵션을 설정합니다.

    이 모델 어댑터를 직접 인스턴스화하는 경우 이 옵션을 사용합니다.

    ```python
    root_agent = Agent(
        model='gemini-2.0-flash',
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

    **옵션 2:** 이 모델 어댑터의 재시도 옵션입니다.

    어댑터 인스턴스를 직접 인스턴스화하는 경우 이 옵션을 사용합니다.

    ```python
    from google.genai import types

    # ...

    agent = Agent(
        model=Gemini(
        retry_options=types.HttpRetryOptions(initial_delay=1, attempts=2),
        )
    )
    ```

## Anthropic 모델 사용

<div class="language-support-tag" title="Java에서 사용 가능합니다. Python에서 Anthropic API (비-Vertex) 직접 지원은 LiteLLM을 통해 제공됩니다.">
   <span class="lst-supported">ADK 지원</span><span class="lst-java">Java v0.2.0</span>
</div>

ADK의 `Claude` 래퍼 클래스를 사용하여 Anthropic의 Claude 모델을 API 키를 통해 직접 통합하거나 Vertex AI 백엔드에서 Java ADK 애플리케이션에 통합할 수 있습니다.

Vertex AI 백엔드에 대해서는 [Vertex AI의 타사 모델(예: Anthropic Claude)](#third-party-models-on-vertex-ai-eg-anthropic-claude) 섹션을 참조하십시오.

**전제 조건:**

1.  **종속성:**
    *   **Anthropic SDK 클래스(전이적):** Java ADK의 `com.google.adk.models.Claude` 래퍼는 Anthropic의 공식 Java SDK의 클래스에 의존합니다. 이들은 일반적으로 **전이적 종속성**으로 포함됩니다.

2.  **Anthropic API 키:**
    *   Anthropic에서 API 키를 얻습니다. 보안 관리자를 사용하여 이 키를 안전하게 관리합니다.

**통합:**

원하는 Claude 모델 이름과 API 키로 구성된 `AnthropicOkHttpClient`를 제공하여 `com.google.adk.models.Claude`를 인스턴스화합니다. 그런 다음 이 `Claude` 인스턴스를 `LlmAgent`에 전달합니다.

**예시:**

```java
import com.anthropic.client.AnthropicClient;
import com.google.adk.agents.LlmAgent;
import com.google.adk.models.Claude;
import com.anthropic.client.okhttp.AnthropicOkHttpClient; // Anthropic의 SDK에서

public class DirectAnthropicAgent {

  private static final String CLAUDE_MODEL_ID = "claude-3-7-sonnet-latest"; // 또는 선호하는 Claude 모델

  public static LlmAgent createAgent() {

    // 민감한 키는 보안 구성에서 로드하는 것이 좋습니다.
    AnthropicClient anthropicClient = AnthropicOkHttpClient.builder()
        .apiKey("ANTHROPIC_API_KEY")
        .build();

    Claude claudeModel = new Claude(
        CLAUDE_MODEL_ID,
        anthropicClient
    );

    return LlmAgent.builder()
        .name("claude_direct_agent")
        .model(claudeModel)
        .instruction("당신은 Anthropic Claude 기반의 유용한 AI 도우미입니다.")
        // ... 기타 LlmAgent 구성
        .build();
  }

  public static void main(String[] args) {
    try {
      LlmAgent agent = createAgent();
      System.out.println("Anthropic 직접 에이전트 생성 성공: " + agent.name());
    } catch (IllegalStateException e) {
      System.err.println("에이전트 생성 오류: " + e.getMessage());
    }
  }
}
```

## AI 모델용 Apigee 게이트웨이 사용

<div class="language-support-tag">
   <span class="lst-supported">ADK 지원</span><span class="lst-python">Python v1.18.0</span>
</div>

[Apigee](https://docs.cloud.google.com/apigee/docs/api-platform/get-started/what-apigee)는 강력한 [AI 게이트웨이](https://cloud.google.com/solutions/apigee-ai) 역할을 하여 생성형 AI 모델 트래픽을 관리하고 제어하는 방식을 변화시킵니다. Apigee 프록시를 통해 AI 모델 엔드포인트(예: Vertex AI 또는 Gemini API)를 노출함으로써 즉시 엔터프라이즈급 기능을 얻을 수 있습니다.

- **모델 안전성:** 위협 방지를 위한 Model Armor와 같은 보안 정책을 구현합니다.

- **트래픽 거버넌스:** 비용을 관리하고 악용을 방지하기 위해 속도 제한 및 토큰 제한을 적용합니다.

- **성능:** Semantic Caching 및 고급 모델 라우팅을 사용하여 응답 시간과 효율성을 향상시킵니다.

- **모니터링 및 가시성:** 모든 AI 요청에 대한 세분화된 모니터링, 분석 및 감사를 제공합니다.

**참고:** `ApigeeLLM` 래퍼는 현재 Vertex AI 및 Gemini API(generateContent)와 함께 사용하도록 설계되었습니다. 다른 모델 및 인터페이스에 대한 지원을 지속적으로 확장하고 있습니다.

**통합 방법:** Apigee의 거버넌스를 에이전트의 워크플로에 통합하려면 `ApigeeLlm` 래퍼를 인스턴스화하고 `LlmAgent` 또는 다른 에이전트 유형에 전달하면 됩니다.

**예시:**

```python

from google.adk.agents import LlmAgent
from google.adk.models.apigee_llm import ApigeeLlm

# ApigeeLlm 래퍼 인스턴스화
model = ApigeeLlm(
    # 모델에 대한 Apigee 경로를 지정합니다. 자세한 내용은 ApigeeLlm 문서를 참조하세요 (https://github.com/google/adk-python/tree/main/contributing/samples/hello_world_apigeellm).
    model="apigee/gemini-2.5-flash",
    # 배포된 Apigee 프록시의 프록시 URL(기본 경로 포함)
    proxy_url=f"https://{APIGEE_PROXY_URL}",
    # 필요한 인증/권한 부여 헤더(예: API 키) 전달
    custom_headers={"foo": "bar"}
)

# 구성된 모델 래퍼를 LlmAgent에 전달
agent = LlmAgent(
    model=model,
    name="my_governed_agent",
    instruction="당신은 Gemini 기반의 Apigee가 관리하는 유용한 도우미입니다.",
    # ... 기타 에이전트 매개변수
)

```

이 구성을 사용하면 에이전트의 모든 API 호출은 Apigee를 통해 먼저 라우팅되며, 여기서 필요한 모든 정책(보안, 속도 제한, 로깅)이 실행된 후 요청이 기본 AI 모델 엔드포인트로 안전하게 전달됩니다.

Apigee 프록시를 사용하는 전체 코드 예시는 [Hello World Apigee LLM](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world_apigeellm)을 참조하세요.

## LiteLLM을 통한 클라우드 및 독점 모델 사용

<div class="language-support-tag">
    <span class="lst-supported">ADK 지원</span><span class="lst-python">Python v0.1.0</span>
</div>

ADK는 LiteLLM 라이브러리를 통해 OpenAI, Anthropic(비-Vertex AI), Cohere 등 다양한 LLM에 대한 통합을 제공합니다.

**통합 방법:** `LiteLlm` 래퍼 클래스를 인스턴스화하고 `LlmAgent`의 `model` 매개변수에 전달합니다.

**LiteLLM 개요:** [LiteLLM](https://docs.litellm.ai/)은 100개 이상의 LLM에 대해 표준화된 OpenAI 호환 인터페이스를 제공하는 변환 계층 역할을 합니다.

**설정:**

1. **LiteLLM 설치:**
        ```shell
        pip install litellm
        ```
2. **제공업체 API 키 설정:** 사용하려는 특정 제공업체에 대한 API 키를 환경 변수로 구성합니다.

    * *OpenAI 예시:*

        ```shell
        export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
        ```

    * *Anthropic(비-Vertex AI) 예시:*

        ```shell
        export ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY"
        ```

    * *다른 제공업체의 올바른 환경 변수 이름은 [LiteLLM 제공업체 문서](https://docs.litellm.ai/docs/providers)를 참조하세요.* 

        **예시:**

        ```python
        from google.adk.agents import LlmAgent
        from google.adk.models.lite_llm import LiteLlm

        # --- OpenAI의 GPT-4o를 사용하는 예시 에이전트 ---
        # (OPENAI_API_KEY 필요)
        agent_openai = LlmAgent(
            model=LiteLlm(model="openai/gpt-4o"), # LiteLLM 모델 문자열 형식
            name="openai_agent",
            instruction="당신은 GPT-4o 기반의 유용한 도우미입니다.",
            # ... 기타 에이전트 매개변수
        )

        # --- Anthropic의 Claude Haiku(비-Vertex)를 사용하는 예시 에이전트 ---
        # (ANTHROPIC_API_KEY 필요)
        agent_claude_direct = LlmAgent(
            model=LiteLlm(model="anthropic/claude-3-haiku-20240307"),
            name="claude_direct_agent",
            instruction="당신은 Claude Haiku 기반의 도우미입니다.",
            # ... 기타 에이전트 매개변수
        )
        ```

!!! warning "LiteLLM용 Windows 인코딩 참고 사항"

    Windows에서 LiteLLM과 함께 ADK 에이전트를 사용하는 경우 `UnicodeDecodeError`가 발생할 수 있습니다. 이 오류는 LiteLLM이 UTF-8 대신 기본 Windows 인코딩(`cp1252`)을 사용하여 캐시된 파일을 읽으려고 시도할 때 발생합니다.

    이를 방지하려면 `PYTHONUTF8` 환경 변수를 `1`로 설정하는 것이 좋습니다. 이렇게 하면 Python이 모든 파일 I/O에 UTF-8을 사용하도록 강제됩니다.

    **예시 (PowerShell):**
    ```powershell
    # 현재 세션에 설정
    $env:PYTHONUTF8 = "1"

    # 사용자에게 영구적으로 설정
    [System.Environment]::SetEnvironmentVariable('PYTHONUTF8', '1', [System.EnvironmentVariableTarget]::User)
    ```


## LiteLLM을 통한 공개 및 로컬 모델 사용

<div class="language-support-tag">
    <span class="lst-supported">ADK 지원</span><span class="lst-python">Python v0.1.0</span>
</div>

최대 제어, 비용 절감, 개인 정보 보호 또는 오프라인 사용 사례를 위해 오픈 소스 모델을 로컬에서 실행하거나 자체 호스팅하고 LiteLLM을 사용하여 통합할 수 있습니다.

**통합 방법:** 로컬 모델 서버를 가리키도록 구성된 `LiteLlm` 래퍼 클래스를 인스턴스화합니다.

### Ollama 통합

[Ollama](https://ollama.com/)를 사용하면 오픈 소스 모델을 로컬에서 쉽게 실행할 수 있습니다.

#### 모델 선택

에이전트가 도구에 의존하는 경우 [Ollama 웹사이트](https://ollama.com/search?c=tools)에서 도구 지원이 있는 모델을 선택해야 합니다.

안정적인 결과를 위해 도구 지원이 있는 적당한 크기의 모델을 사용하는 것이 좋습니다.

모델에 대한 도구 지원은 다음 명령어로 확인할 수 있습니다.

```bash
ollama show mistral-small3.1
  Model
    architecture        mistral3
    parameters          24.0B
    context length      131072
    embedding length    5120
    quantization        Q4_K_M

  Capabilities
    completion
    vision
    tools
```

기능 아래에 `tools`가 나열되어 있어야 합니다.

모델이 사용하는 템플릿을 살펴보고 필요에 따라 조정할 수도 있습니다.

```bash
ollama show --modelfile llama3.2 > model_file_to_modify
```

예를 들어, 위 모델의 기본 템플릿은 모델이 항상 함수를 호출해야 함을 본질적으로 시사합니다. 이로 인해 무한 함수 호출 루프가 발생할 수 있습니다.

```
제공된 다음 함수를 고려하여, 주어진 프롬프트에 가장 적합한 함수 호출에 대한 JSON을 올바른 인자와 함께 응답하십시오.

{"name": 함수 이름, "parameters": 인자 이름과 값의 딕셔너리} 형식으로 응답하십시오. 변수를 사용하지 마십시오.
```

이러한 프롬프트를 보다 설명적인 프롬프트로 교체하여 무한 도구 호출 루프를 방지할 수 있습니다.

예를 들어:

```
사용자의 프롬프트와 아래 나열된 사용 가능한 함수를 검토합니다.
먼저, 이 함수 중 하나를 호출하는 것이 가장 적절한 응답 방법인지 결정합니다. 프롬프트가 특정 작업을 요청하거나 외부 데이터 조회가 필요하거나 함수에서 처리하는 계산을 포함하는 경우 함수 호출이 필요할 가능성이 높습니다. 프롬프트가 일반적인 질문이거나 직접 답변할 수 있는 경우 함수 호출이 필요하지 않을 가능성이 높습니다.

함수 호출이 필요한 경우: {"name": "function_name", "parameters": {"argument_name": "value"}} 형식의 JSON 객체로만 응답합니다. 매개변수 값은 변수가 아닌 구체적인 값인지 확인합니다.

함수 호출이 필요하지 않은 경우: 일반 텍스트로 사용자의 프롬프트에 직접 응답하여 요청된 답변 또는 정보를 제공합니다. JSON을 출력하지 마십시오.
```

그런 다음 다음 명령어를 사용하여 새 모델을 만들 수 있습니다.

```bash
ollama create llama3.2-modified -f model_file_to_modify
```

#### ollama_chat 제공업체 사용

LiteLLM 래퍼를 사용하여 Ollama 모델로 에이전트를 만들 수 있습니다.

```python
root_agent = Agent(
    model=LiteLlm(model="ollama_chat/mistral-small3.1"),
    name="dice_agent",
    description=(
        "8면 주사위를 굴리고 소수를 확인할 수 있는 헬로월드 에이전트."
    ),
    instruction="""
      주사위를 굴리고 주사위 굴림 결과에 대한 질문에 답변합니다.
    """,
    tools=[
        roll_die,
        check_prime,
    ],
)
```

**`ollama` 대신 `ollama_chat` 제공업체를 설정하는 것이 중요합니다. `ollama`를 사용하면 무한 도구 호출 루프 및 이전 컨텍스트 무시와 같은 예기치 않은 동작이 발생할 수 있습니다.**

`api_base`는 생성용 LiteLLM 내에서 제공될 수 있지만, LiteLLM 라이브러리는 v1.65.5 이후 완료 후 env 변수에 의존하는 다른 API를 호출합니다. 따라서 현재는 `OLLAMA_API_BASE` env 변수를 ollama 서버를 가리키도록 설정하는 것이 좋습니다.

```bash
export OLLAMA_API_BASE="http://localhost:11434"
adk web
```

#### openai 제공업체 사용

대안으로 `openai`를 제공업체 이름으로 사용할 수 있습니다. 그러나 이 경우 `OLLAMA_API_BASE` 대신 `OPENAI_API_BASE=http://localhost:11434/v1` 및 `OPENAI_API_KEY=anything` 환경 변수를 설정해야 합니다. **이제 API 베이스에 `/v1`이 추가되어야 합니다.**

```python
root_agent = Agent(
    model=LiteLlm(model="openai/mistral-small3.1"),
    name="dice_agent",
    description=(
        "8면 주사위를 굴리고 소수를 확인할 수 있는 헬로월드 에이전트."
    ),
    instruction="""
      주사위를 굴리고 주사위 굴림 결과에 대한 질문에 답변합니다.
    """,
    tools=[
        roll_die,
        check_prime,
    ],
)
```

```bash
export OPENAI_API_BASE=http://localhost:11434/v1
export OPENAI_API_KEY=anything
adk web
```

#### 디버깅

가져오기 직후 에이전트 코드에 다음을 추가하여 Ollama 서버로 전송된 요청을 볼 수 있습니다.

```python
import litellm
litellm._turn_on_debug()
```

다음과 같은 줄을 찾습니다.

```bash
Request Sent from LiteLLM:
curl -X POST \
http://localhost:11434/api/chat \
-d '{'model': 'mistral-small3.1', 'messages': [{'role': 'system', 'content': ...
```

### 자체 호스팅 엔드포인트 (예: vLLM)

<div class="language-support-tag">
   <span class="lst-supported">ADK 지원</span><span class="lst-python">Python</span>
</div>

[vLLM](https://github.com/vllm-project/vllm)과 같은 도구를 사용하면 모델을 효율적으로 호스팅하고 종종 OpenAI 호환 API 엔드포인트를 노출할 수 있습니다.

**설정:**

1. **모델 배포:** vLLM(또는 유사한 도구)을 사용하여 선택한 모델을 배포합니다. API 기본 URL을 기록해 둡니다(예: `https://your-vllm-endpoint.run.app/v1`).
    * *ADK 도구에 중요:* 배포할 때 서빙 도구가 OpenAI 호환 도구/함수 호출을 지원하고 활성화하는지 확인합니다. vLLM의 경우 모델에 따라 `--enable-auto-tool-choice` 및 잠재적으로 특정 `--tool-call-parser`와 같은 플래그가 필요할 수 있습니다. 도구 사용에 대한 vLLM 문서를 참조하십시오.
2. **인증:** 엔드포인트가 인증을 처리하는 방법(예: API 키, 베어러 토큰)을 결정합니다.

    **통합 예시:**

    ```python
    import subprocess
    from google.adk.agents import LlmAgent
    from google.adk.models.lite_llm import LiteLlm

    # --- vLLM 엔드포인트에서 호스팅되는 모델을 사용하는 예시 에이전트 ---

    # vLLM 배포에서 제공하는 엔드포인트 URL
    api_base_url = "https://your-vllm-endpoint.run.app/v1"

    # vLLM 엔드포인트 구성에서 인식하는 모델 이름
    model_name_at_endpoint = "hosted_vllm/google/gemma-3-4b-it" # vllm_test.py의 예시

    # 인증 (예: Cloud Run 배포를 위한 gcloud ID 토큰 사용)
    # 엔드포인트 보안에 따라 조정
    try:
        gcloud_token = subprocess.check_output(
            ["gcloud", "auth", "print-identity-token", "-q"]
        ).decode().strip()
        auth_headers = {"Authorization": f"Bearer {gcloud_token}"}
    except Exception as e:
        print(f"경고: gcloud 토큰을 가져올 수 없습니다 - {e}. 엔드포인트가 보안되지 않았거나 다른 인증이 필요할 수 있습니다.")
        auth_headers = None # 또는 적절하게 오류 처리

    agent_vllm = LlmAgent(
        model=LiteLlm(
            model=model_name_at_endpoint,
            api_base=api_base_url,
            # 필요한 경우 인증 헤더 전달
            extra_headers=auth_headers
            # 또는 엔드포인트가 API 키를 사용하는 경우:
            # api_key="YOUR_ENDPOINT_API_KEY"
        ),
        name="vllm_agent",
        instruction="당신은 자체 호스팅된 vLLM 엔드포인트에서 실행되는 유용한 도우미입니다.",
        # ... 기타 에이전트 매개변수
    )
    ```

## Vertex AI에서 호스팅 및 미세 조정된 모델 사용

Google Cloud의 MLOps 에코시스템과 엔터프라이즈급 확장성, 안정성 및 통합을 위해 Vertex AI 엔드포인트에 배포된 모델을 사용할 수 있습니다. 여기에는 Model Garden의 모델 또는 직접 미세 조정한 모델이 포함됩니다.

**통합 방법:** 전체 Vertex AI 엔드포인트 리소스 문자열(`projects/PROJECT_ID/locations/LOCATION/endpoints/ENDPOINT_ID`)을 `LlmAgent`의 `model` 매개변수에 직접 전달합니다.

**Vertex AI 설정 (통합):**

환경이 Vertex AI에 대해 구성되었는지 확인합니다.

1. **인증:** ADC(Application Default Credentials)를 사용합니다.

    ```shell
    gcloud auth application-default login
    ```

2. **환경 변수:** 프로젝트 및 위치를 설정합니다.

    ```shell
    export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
    export GOOGLE_CLOUD_LOCATION="YOUR_VERTEX_AI_LOCATION" # 예: us-central1
    ```

3. **Vertex 백엔드 활성화:** 결정적으로 `google-genai` 라이브러리가 Vertex AI를 대상으로 하는지 확인합니다.

    ```shell
    export GOOGLE_GENAI_USE_VERTEXAI=TRUE
    ```

### Model Garden 배포

<div class="language-support-tag">
    <span class="lst-supported">ADK 지원</span><span class="lst-python">Python v0.2.0</span>
</div>

[Vertex AI Model Garden](https://console.cloud.google.com/vertex-ai/model-garden)에서 다양한 오픈 및 독점 모델을 엔드포인트에 배포할 수 있습니다.

**예시:**

```python
from google.adk.agents import LlmAgent
from google.genai import types # config 객체용

# --- Model Garden에서 배포된 Llama 3 모델을 사용하는 예시 에이전트 ---

# 실제 Vertex AI 엔드포인트 리소스 이름으로 대체
lama3_endpoint = "projects/YOUR_PROJECT_ID/locations/us-central1/endpoints/YOUR_LLAMA3_ENDPOINT_ID"

agent_llama3_vertex = LlmAgent(
    model=llama3_endpoint,
    name="llama3_vertex_agent",
    instruction="당신은 Vertex AI에서 호스팅되는 Llama 3 기반의 유용한 도우미입니다.",
    generate_content_config=types.GenerateContentConfig(max_output_tokens=2048),
    # ... 기타 에이전트 매개변수
)
```

### 미세 조정된 모델 엔드포인트

<div class="language-support-tag">
    <span class="lst-supported">ADK 지원</span><span class="lst-python">Python v0.2.0</span>
</div>

미세 조정된 모델(Gemini 또는 Vertex AI에서 지원하는 기타 아키텍처 기반)을 배포하면 직접 사용할 수 있는 엔드포인트가 생성됩니다.

**예시:**

```python
from google.adk.agents import LlmAgent

# --- 미세 조정된 Gemini 모델 엔드포인트를 사용하는 예시 에이전트 ---

# 미세 조정된 모델의 엔드포인트 리소스 이름으로 대체
finetuned_gemini_endpoint = "projects/YOUR_PROJECT_ID/locations/us-central1/endpoints/YOUR_FINETUNED_ENDPOINT_ID"

agent_finetuned_gemini = LlmAgent(
    model=finetuned_gemini_endpoint,
    name="finetuned_gemini_agent",
    instruction="당신은 특정 데이터로 학습된 전문 도우미입니다.",
    # ... 기타 에이전트 매개변수
)
```

### Vertex AI의 타사 모델 (예: Anthropic Claude)

Anthropic와 같은 일부 제공업체는 Vertex AI를 통해 직접 모델을 제공합니다.

=== "Python"

    **통합 방법:** 직접 모델 문자열(예: `"claude-3-sonnet@20240229"`)을 사용하지만, ADK 내에서 *수동 등록이 필요합니다*.

    **등록 이유:** ADK의 레지스트리는 `gemini-*` 문자열 및 표준 Vertex AI 엔드포인트 문자열(`projects/.../endpoints/...`)을 자동으로 인식하고 `google-genai` 라이브러리를 통해 라우팅합니다. Vertex AI를 통해 직접 사용되는 다른 모델 유형(예: Claude)의 경우, ADK 레지스트리에 해당 모델 식별자 문자열을 Vertex AI 백엔드와 함께 처리하는 방법을 아는 특정 래퍼 클래스(이 경우 `Claude`)를 명시적으로 알려야 합니다.

    **설정:**

    1. **Vertex AI 환경:** 통합 Vertex AI 설정(ADC, 환경 변수, `GOOGLE_GENAI_USE_VERTEXAI=TRUE`)이 완료되었는지 확인합니다.

    2. **제공업체 라이브러리 설치:** Vertex AI용으로 구성된 필요한 클라이언트 라이브러리를 설치합니다.

        ```shell
        pip install "anthropic[vertex]"
        ```

    3. **모델 클래스 등록:** Claude 모델 문자열을 사용하여 에이전트를 만들기 *전에* 애플리케이션 시작 부분에 다음 코드를 추가합니다.

        ```python
        # LlmAgent와 함께 Vertex AI를 통해 Claude 모델 문자열을 직접 사용하려면 필요합니다.
        from google.adk.models.anthropic_llm import Claude
        from google.adk.models.registry import LLMRegistry

        LLMRegistry.register(Claude)
        ```

       **예시:**

       ```python
       from google.adk.agents import LlmAgent
       from google.adk.models.anthropic_llm import Claude # 등록에 필요
       from google.adk.models.registry import LLMRegistry # 등록에 필요
       from google.genai import types

       # --- Claude 클래스 등록 (시작 시 한 번 수행) ---
       LLMRegistry.register(Claude)

       # --- Vertex AI의 Claude 3 Sonnet을 사용하는 예시 에이전트 ---

       # Vertex AI의 Claude 3 Sonnet에 대한 표준 모델 이름
       claude_model_vertexai = "claude-3-sonnet@20240229"

       agent_claude_vertexai = LlmAgent(
           model=claude_model_vertexai, # 등록 후 직접 문자열 전달
           name="claude_vertexai_agent",
           instruction="당신은 Vertex AI의 Claude 3 Sonnet 기반 도우미입니다.",
           generate_content_config=types.GenerateContentConfig(max_output_tokens=4096),
           # ... 기타 에이전트 매개변수
       )
       ```

===
"Java"

    **통합 방법:** 제공업체별 모델 클래스(예: `com.google.adk.models.Claude`)를 직접 인스턴스화하고 Vertex AI 백엔드로 구성합니다.

    **직접 인스턴스화 이유:** Java ADK의 `LlmRegistry`는 기본적으로 Gemini 모델을 주로 처리합니다. Vertex AI의 Claude와 같은 타사 모델의 경우 ADK의 래퍼 클래스(예: `Claude`) 인스턴스를 `LlmAgent`에 직접 제공합니다. 이 래퍼 클래스는 Vertex AI용으로 구성된 특정 클라이언트 라이브러리를 통해 모델과 상호 작용합니다.

    **설정:**

    1.  **Vertex AI 환경:**
        *   Google Cloud 프로젝트 및 리전이 올바르게 설정되었는지 확인합니다.
        *   **ADC(Application Default Credentials):** ADC가 환경에 올바르게 구성되었는지 확인합니다. 일반적으로 `gcloud auth application-default login`을 실행하여 수행됩니다. Java 클라이언트 라이브러리는 이 자격 증명을 사용하여 Vertex AI로 인증합니다. 자세한 설정은 [Google Cloud Java 문서의 ADC](https://cloud.google.com/java/docs/reference/google-auth-library/latest/com.google.auth.oauth2.GoogleCredentials#com_google_auth_oauth2_GoogleCredentials_getApplicationDefault__)를 참조하세요.

    2.  **제공업체 라이브러리 종속성:**
        *   **타사 클라이언트 라이브러리(종종 전이적):** ADK 코어 라이브러리에는 Vertex AI의 일반적인 타사 모델(예: Anthropic에 필요한 클래스)에 대한 필요한 클라이언트 라이브러리가 **전이적 종속성**으로 포함되는 경우가 많습니다. 즉, `pom.xml` 또는 `build.gradle`에 Anthropic Vertex SDK에 대한 별도의 종속성을 명시적으로 추가할 필요가 없을 수 있습니다.

    3.  **모델 인스턴스화 및 구성:**
        `LlmAgent`를 만들 때 `Claude` 클래스(또는 다른 제공업체의 해당 클래스)를 인스턴스화하고 `VertexBackend`를 구성합니다.

    **예시:**

    ```java
    import com.anthropic.client.AnthropicClient;
    import com.anthropic.client.okhttp.AnthropicOkHttpClient;
    import com.anthropic.vertex.backends.VertexBackend;
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.models.Claude; // Claude용 ADK 래퍼
    import com.google.auth.oauth2.GoogleCredentials;
    import java.io.IOException;

    // ... 기타 가져오기

    public class ClaudeVertexAiAgent {

        public static LlmAgent createAgent() throws IOException {
            // Vertex AI의 Claude 3 Sonnet에 대한 모델 이름 (또는 다른 버전)
            String claudeModelVertexAi = "claude-3-7-sonnet"; // 또는 다른 Claude 모델

            // VertexBackend로 AnthropicOkHttpClient 구성
            AnthropicClient anthropicClient = AnthropicOkHttpClient.builder()
                .backend(
                    VertexBackend.builder()
                        .region("us-east5") // Vertex AI 리전 지정
                        .project("your-gcp-project-id") // GCP 프로젝트 ID 지정
                        .googleCredentials(GoogleCredentials.getApplicationDefault())
                        .build())
                .build();

            // ADK Claude 래퍼로 LlmAgent 인스턴스화
            LlmAgent agentClaudeVertexAi = LlmAgent.builder()
                .model(new Claude(claudeModelVertexAi, anthropicClient)) // Claude 인스턴스 전달
                .name("claude_vertexai_agent")
                .instruction("당신은 Vertex AI의 Claude 3 Sonnet 기반 도우미입니다.")
                // .generateContentConfig(...) // 선택 사항: 필요한 경우 생성 구성 추가
                // ... 기타 에이전트 매개변수
                .build();

            return agentClaudeVertexAi;
        }

        public static void main(String[] args) {
            try {
                LlmAgent agent = createAgent();
                System.out.println("에이전트 생성 성공: " + agent.name());
                // 여기에서 일반적으로 Runner 및 Session을 설정하여 에이전트와 상호 작용합니다.
            } catch (IOException e) {
                System.err.println("에이전트 생성 실패: " + e.getMessage());
                e.printStackTrace();
            }
        }
    }
    ```
