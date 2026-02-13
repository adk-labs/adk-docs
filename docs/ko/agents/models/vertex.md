# Vertex AI 호스팅 모델 for ADK 에이전트

엔터프라이즈 급 확장성, 안정성, 그리고 Google Cloud의 MLOps 생태계 연동을 위해
Vertex AI 엔드포인트에 배포된 모델을 사용할 수 있습니다.
여기에 Model Garden 모델과 사용자가 파인 튜닝한 모델이 포함됩니다.

**통합 방법:** Vertex AI 엔드포인트 전체 리소스 문자열
(`projects/PROJECT_ID/locations/LOCATION/endpoints/ENDPOINT_ID`)을 `LlmAgent`의
`model` 파라미터에 직접 전달합니다.

## Vertex AI 설정

Vertex AI 환경이 구성되어 있는지 확인하세요.

1. **인증:** Application Default Credentials (ADC) 사용:

    ```shell
    gcloud auth application-default login
    ```

2. **환경 변수 설정:** 프로젝트 및 위치 설정:

    ```shell
    export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
    export GOOGLE_CLOUD_LOCATION="YOUR_VERTEX_AI_LOCATION" # 예: us-central1
    ```

3. **Vertex 백엔드 활성화:** `google-genai` 라이브러리가 Vertex AI를 대상으로 하도록 설정:

    ```shell
    export GOOGLE_GENAI_USE_VERTEXAI=TRUE
    ```

## Model Garden 배포

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.2.0</span>
</div>

[Vertex AI Model Garden](https://console.cloud.google.com/vertex-ai/model-garden)에서
다양한 오픈 소스 및 독점 모델을 엔드포인트로 배포할 수 있습니다.

**예시:**

```python
from google.adk.agents import LlmAgent
from google.genai import types # For config objects

# --- Example Agent using a Llama 3 model deployed from Model Garden ---

# 실제 Vertex AI 엔드포인트 리소스 이름으로 바꿔주세요.
llama3_endpoint = "projects/YOUR_PROJECT_ID/locations/us-central1/endpoints/YOUR_LLAMA3_ENDPOINT_ID"

agent_llama3_vertex = LlmAgent(
    model=llama3_endpoint,
    name="llama3_vertex_agent",
    instruction="You are a helpful assistant based on Llama 3, hosted on Vertex AI.",
    generate_content_config=types.GenerateContentConfig(max_output_tokens=2048),
    # ... other agent parameters
)
```

## 파인 튜닝 모델 엔드포인트

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.2.0</span>
</div>

Gemini 또는 Vertex AI가 지원하는 다른 아키텍처의 파인 튜닝 모델을 배포하면
직접 사용할 수 있는 엔드포인트가 생성됩니다.

**예시:**

```python
from google.adk.agents import LlmAgent

# --- Example Agent using a fine-tuned Gemini model endpoint ---

# 실제 파인 튜닝 모델의 엔드포인트 리소스 이름으로 바꿔주세요.
finetuned_gemini_endpoint = "projects/YOUR_PROJECT_ID/locations/us-central1/endpoints/YOUR_FINETUNED_ENDPOINT_ID"

agent_finetuned_gemini = LlmAgent(
    model=finetuned_gemini_endpoint,
    name="finetuned_gemini_agent",
    instruction="You are a specialized assistant trained on specific data.",
    # ... other agent parameters
)
```

## Vertex AI의 Anthropic Claude {#third-party-models-on-vertex-ai-eg-anthropic-claude}

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.2.0</span><span class="lst-java">Java v0.1.0</span>
</div>

Anthropic 같은 일부 제공업체는 모델을 Vertex AI를 통해 직접 제공합니다.

=== "Python"

    **통합 방법:** 직접 모델 문자열(예: `"claude-3-sonnet@20240229"`)을 사용하되,
    ADK에서 **수동 등록**이 필요합니다.

    **등록이 필요한 이유:** ADK 레지스트리는 기본적으로 `gemini-*` 문자열과
    표준 Vertex AI 엔드포인트 문자열(`projects/.../endpoints/...`)을 인식해
    `google-genai` 라이브러리로 라우팅합니다. Claude처럼 Vertex AI에서 직접
    사용되는 다른 모델은 ADK 레지스트리에 해당 모델 문자열을 처리할 수 있는
    특정 래퍼 클래스(이 예시에서는 `Claude`)를 명시적으로 등록해야 합니다.

    **설정:**

    1. **Vertex AI 환경 구성:** 통합된 Vertex AI 설정(ADC, 환경 변수,
       `GOOGLE_GENAI_USE_VERTEXAI=TRUE`)이 완료되었는지 확인합니다.

    2. **제공업체 라이브러리 설치:** Vertex AI용으로 구성된 필요한 클라이언트 라이브러리를 설치합니다.

        ```shell
        pip install "anthropic[vertex]"
        ```

    3. **모델 클래스 등록:** 에이전트를 생성하기 전에 애플리케이션 시작 부분에 다음 코드를 추가합니다.

        ```python
        # Required for using Claude model strings directly via Vertex AI with LlmAgent
        from google.adk.models.anthropic_llm import Claude
        from google.adk.models.registry import LLMRegistry

        LLMRegistry.register(Claude)
        ```

       **예시:**

       ```python
       from google.adk.agents import LlmAgent
       from google.adk.models.anthropic_llm import Claude # Import needed for registration
       from google.adk.models.registry import LLMRegistry # Import needed for registration
       from google.genai import types

       # --- Register Claude class (do this once at startup) ---
       LLMRegistry.register(Claude)

       # --- Example Agent using Claude 3 Sonnet on Vertex AI ---

       # Standard model name for Claude 3 Sonnet on Vertex AI
       claude_model_vertexai = "claude-3-sonnet@20240229"

       agent_claude_vertexai = LlmAgent(
           model=claude_model_vertexai, # Pass the direct string after registration
           name="claude_vertexai_agent",
           instruction="You are an assistant powered by Claude 3 Sonnet on Vertex AI.",
           generate_content_config=types.GenerateContentConfig(max_output_tokens=4096),
           # ... other agent parameters
       )
       ```

=== "Java"

    **통합 방법:** 제공업체별 모델 클래스를 직접 인스턴스화하고(예: `com.google.adk.models.Claude`) Vertex AI 백엔드로 설정합니다.

    **직접 인스턴스화하는 이유:** Java ADK의 `LlmRegistry`는 기본적으로 Gemini 모델을 주로 다룹니다. Vertex AI의 Claude 같은 타사 모델은
    ADK 래퍼 클래스(예: `Claude`) 인스턴스를 `LlmAgent`에 직접 전달해야 합니다.
    이 래퍼 클래스는 특정 클라이언트 라이브러리를 통해 모델과 상호작용하며,
    해당 라이브러리는 Vertex AI에 맞게 설정됩니다.

    **설정:**

    1.  **Vertex AI 환경:**
        *   Google Cloud 프로젝트와 리전을 올바르게 설정합니다.
        *   **Application Default Credentials (ADC):** 환경에서 ADC가 올바르게 설정되어 있는지 확인합니다.
            일반적으로 `gcloud auth application-default login` 실행으로 설정합니다.
            Java 클라이언트 라이브러리는 Vertex AI 인증을 위해 이 자격 증명을 사용합니다.
            자세한 절차는 [Google Cloud Java의 ADC 문서](https://cloud.google.com/java/docs/reference/google-auth-library/latest/com.google.auth.oauth2.GoogleCredentials#com_google_auth_oauth2_GoogleCredentials_getApplicationDefault_)를 참조하세요.

    2.  **제공업체 라이브러리 종속성:**
        *   **타사 클라이언트 라이브러리(대부분 전이 종속성):** ADK 코어 라이브러리에는
            Vertex AI에서 자주 사용되는 타사 모델(예: Anthropic 필수 클래스)용 클라이언트 라이브러리가
            **트랜지티브 종속성**으로 포함되는 경우가 많습니다.
            따라서 `pom.xml`이나 `build.gradle`에 Anthropic Vertex SDK를 별도로 추가하지
            않아도 되는 경우가 있습니다.

    3.  **모델 인스턴스화 및 구성:**
        `LlmAgent`를 만들 때 `Claude` 클래스(또는 다른 제공업체의 해당 클래스)를 인스턴스화하고
        `VertexBackend`를 구성합니다.

    **예시:**

    ```java
    import com.anthropic.client.AnthropicClient;
    import com.anthropic.client.okhttp.AnthropicOkHttpClient;
    import com.anthropic.vertex.backends.VertexBackend;
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.models.Claude; // ADK's wrapper for Claude
    import com.google.auth.oauth2.GoogleCredentials;
    import java.io.IOException;

    // ... other imports

    public class ClaudeVertexAiAgent {

        public static LlmAgent createAgent() throws IOException {
            // Model name for Claude 3 Sonnet on Vertex AI (or any other Claude model)
            String claudeModelVertexAi = "claude-3-7-sonnet"; // Or any other Claude model

            // Configure the AnthropicOkHttpClient with the VertexBackend
            AnthropicClient anthropicClient = AnthropicOkHttpClient.builder()
                .backend(
                    VertexBackend.builder()
                        .region("us-east5") // Specify your Vertex AI region
                        .project("your-gcp-project-id") // Specify your GCP Project ID
                        .googleCredentials(GoogleCredentials.getApplicationDefault())
                        .build())
                .build();

            // Instantiate LlmAgent with the ADK Claude wrapper
            LlmAgent agentClaudeVertexAi = LlmAgent.builder()
                .model(new Claude(claudeModelVertexAi, anthropicClient)) // Pass the Claude instance
                .name("claude_vertexai_agent")
                .instruction("You are an assistant powered by Claude 3 Sonnet on Vertex AI.")
                // .generateContentConfig(...) // Optional: Add generation config if needed
                // ... other agent parameters
                .build();

            return agentClaudeVertexAi;
        }

        public static void main(String[] args) {
            try {
                LlmAgent agent = createAgent();
                System.out.println("Successfully created agent: " + agent.name());
                // Here you would typically set up a Runner and Session to interact with the agent
            } catch (IOException e) {
                System.err.println("Failed to create agent: " + e.getMessage());
                e.printStackTrace();
            }
        }
    }
    ```

## Vertex AI의 오픈 모델 {#open-models}

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span>
</div>

Vertex AI는 Meta Llama 같은 오픈 소스 모델을 Model-as-a-Service(MaaS)로 선별 제공합니다.
이러한 모델은 관리형 API를 통해 액세스되어, 기본 인프라 관리 없이 배포·확장할 수 있습니다.
전체 목록은 [Vertex AI open models for MaaS](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/maas/use-open-models#open-models) 문서를 참조하세요.

=== "Python"

    [LiteLLM](https://docs.litellm.ai/) 라이브러리를 통해 Vertex AI MaaS의 Meta Llama 등 오픈 모델을 사용할 수 있습니다.

    **통합 방법:** `LiteLlm` 래퍼 클래스를 사용해 `LlmAgent`의 `model` 파라미터로 지정합니다.
    ADK에서 LiteLLM을 사용하는 방법은 [ADK 에이전트를 위한 LiteLLM 모델 커넥터](/adk-docs/agents/models/litellm/#litellm-model-connector-for-adk-agents) 문서를 참고하세요.

    **설정:**

    1. **Vertex AI 환경:** 통합된 Vertex AI 설정(ADC, 환경 변수,
       `GOOGLE_GENAI_USE_VERTEXAI=TRUE`)이 완료되었는지 확인합니다.

    2. **LiteLLM 설치:**
            ```shell
            pip install litellm
            ```
    
    **예시:**

    ```python
    from google.adk.agents import LlmAgent
    from google.adk.models.lite_llm import LiteLlm

    # --- Example Agent using Meta's Llama 4 Scout ---
    agent_llama_vertexai = LlmAgent(
        model=LiteLlm(model="vertex_ai/meta/llama-4-scout-17b-16e-instruct-maas"), # LiteLLM model string format
        name="llama4_agent",
        instruction="You are a helpful assistant powered by Llama 4 Scout.",
        # ... other agent parameters
    )

    ```
