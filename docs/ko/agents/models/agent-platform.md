# ADK 에이전트를 위한 에이전트 플랫폼 호스팅 모델

엔터프라이즈급 확장성, 안정성, Google과의 통합
Cloud의 MLOps 에코시스템에서는 에이전트 플랫폼 엔드포인트에 배포된 모델을 사용할 수 있습니다.
여기에는 Model Garden의 모델이나 직접 미세 조정한 모델이 포함됩니다.

**통합 방법:** 전체 에이전트 플랫폼 엔드포인트 리소스 문자열 전달
(`projects/PROJECT_ID/locations/LOCATION/endpoints/ENDPOINT_ID`)를 직접
`LlmAgent`의 `model` 매개변수입니다.

## 에이전트 플랫폼 설정

에이전트 플랫폼에 맞게 환경이 구성되어 있는지 확인하세요.

1. **인증:** ADC(애플리케이션 기본 자격 증명) 사용:

    ```shell
    gcloud auth application-default login
    ```

2. **환경 변수:** 프로젝트와 위치를 설정합니다.

    ```shell
    export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
    export GOOGLE_CLOUD_LOCATION="YOUR_VERTEX_AI_LOCATION" # e.g., us-central1
    ```

3. **에이전트 플랫폼 백엔드 활성화:** 결정적으로 `google-genai` 라이브러리를 확인하세요.
   대상 에이전트 플랫폼:

    ```shell
    export GOOGLE_GENAI_USE_VERTEXAI=TRUE
    ```

## 모델 정원 배포

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.2.0</span><span class="lst-java">Java v0.1.0</span>
</div>

다양한 개방형 및 독점 모델을 배포할 수 있습니다.
[Model Garden](https://console.cloud.google.com/vertex-ai/model-garden)
끝점으로.

**예:**

=== "Python"

    ```python
    from google.adk.agents import LlmAgent
    from google.genai import types # For config objects

    # --- Example Agent using a Llama 3 model deployed from Model Garden ---

    # Replace with your actual Agent Platform Endpoint resource name
    llama3_endpoint = "projects/YOUR_PROJECT_ID/locations/us-central1/endpoints/YOUR_LLAMA3_ENDPOINT_ID"

    agent_llama3_vertex = LlmAgent(
        model=llama3_endpoint,
        name="llama3_vertex_agent",
        instruction="You are a helpful assistant based on Llama 3, hosted on Agent Platform.",
        generate_content_config=types.GenerateContentConfig(max_output_tokens=2048),
        # ... other agent parameters
    )
    ```

=== "Java"

    ```java
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.models.Gemini;
    import com.google.genai.types.GenerateContentConfig;

    // ...

    // Replace with your actual Agent Platform Endpoint resource name
    String llama3Endpoint = "projects/YOUR_PROJECT_ID/locations/us-central1/endpoints/YOUR_LLAMA3_ENDPOINT_ID";

    LlmAgent agentLlama3Vertex = LlmAgent.builder()
        .model(Gemini.builder()
            .modelName(llama3Endpoint)
            .build())
        .name("llama3_vertex_agent")
        .instruction("You are a helpful assistant based on Llama 3, hosted on Agent Platform.")
        .generateContentConfig(GenerateContentConfig.builder()
            .maxOutputTokens(2048)
            .build())
        // ... other agent parameters
        .build();
    ```

## 미세 조정된 모델 엔드포인트

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.2.0</span><span class="lst-java">Java v0.1.0</span>
</div>

미세 조정된 모델 배포(Gemini 또는 기타 아키텍처 기반)
에이전트 플랫폼에서 지원)을 사용하면 직접 사용할 수 있는 엔드포인트가 생성됩니다.

**예:**

=== "Python"

    ```python
    from google.adk.agents import LlmAgent

    # --- Example Agent using a fine-tuned Gemini model endpoint ---

    # Replace with your fine-tuned model's endpoint resource name
    finetuned_gemini_endpoint = "projects/YOUR_PROJECT_ID/locations/us-central1/endpoints/YOUR_FINETUNED_ENDPOINT_ID"

    agent_finetuned_gemini = LlmAgent(
        model=finetuned_gemini_endpoint,
        name="finetuned_gemini_agent",
        instruction="You are a specialized assistant trained on specific data.",
        # ... other agent parameters
    )
    ```

=== "Java"

    ```java
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.models.Gemini;

    // ...

    // Replace with your fine-tuned model's endpoint resource name
    String finetunedGeminiEndpoint = "projects/YOUR_PROJECT_ID/locations/us-central1/endpoints/YOUR_FINETUNED_ENDPOINT_ID";

    LlmAgent agentFinetunedGemini = LlmAgent.builder()
        .model(Gemini.builder()
            .modelName(finetunedGeminiEndpoint)
            .build())
        .name("finetuned_gemini_agent")
        .instruction("You are a specialized assistant trained on specific data.")
        // ... other agent parameters
        .build();
    ```

## 에이전트 플랫폼의 Anthropic Claude {#anthropic-claude}

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.2.0</span><span class="lst-java">Java v0.1.0</span>
</div>

Anthropic과 같은 일부 제공업체는 다음을 통해 모델을 직접 제공합니다.
에이전트 플랫폼.

**예:**

=== "Python"

    **통합 방법:** 직접 모델 문자열을 사용합니다(예:
    `"claude-3-sonnet@20240229"`), *ADK 내에서 *수동 등록이 필요*합니다.

    **등록 이유는 무엇입니까?** ADK의 레지스트리는 `gemini-*` 문자열을 자동으로 인식합니다.
    표준 에이전트 플랫폼 엔드포인트 문자열(`projects/.../endpoints/...`) 및
    `google-genai` 라이브러리를 통해 라우팅합니다. 직접 사용되는 다른 모델 유형의 경우
    Claude와 같은 에이전트 플랫폼을 통해 ADK 레지스트리에 명시적으로 알려야 합니다.
    특정 래퍼 클래스(이 경우 `Claude`)는 해당 모델을 처리하는 방법을 알고 있습니다.
    에이전트 플랫폼 백엔드가 있는 식별자 문자열입니다.

    **설정:**

    1. **에이전트 플랫폼 환경:** 통합된 에이전트 플랫폼 설정(ADC, Env)을 보장합니다.
       바르스, `GOOGLE_GENAI_USE_VERTEXAI=TRUE`)가 완성되었습니다.

    2. **공급자 라이브러리 설치:** 구성된 필수 클라이언트 라이브러리를 설치합니다.
       에이전트 플랫폼용.

        ```shell
        pip install "anthropic[vertex]"
        ```

    3. **모델 클래스 등록:** 애플리케이션 시작 부분에 이 코드를 추가하세요.
       *Claude 모델 문자열을 사용하여 에이전트를 생성하기 전*:

        ```python
        # Required for using Claude model strings directly via Agent Platform with LlmAgent
        from google.adk.models.anthropic_llm import Claude
        from google.adk.models.registry import LLMRegistry

        LLMRegistry.register(Claude)
        ```

       ```python
       from google.adk.agents import LlmAgent
       from google.adk.models.anthropic_llm import Claude # Import needed for registration
       from google.adk.models.registry import LLMRegistry # Import needed for registration
       from google.genai import types

       # --- Register Claude class (do this once at startup) ---
       LLMRegistry.register(Claude)

       # --- Example Agent using Claude 3 Sonnet on Agent Platform ---

       # Standard model name for Claude 3 Sonnet on Agent Platform
       claude_model_vertexai = "claude-3-sonnet@20240229"

       agent_claude_vertexai = LlmAgent(
           model=claude_model_vertexai, # Pass the direct string after registration
           name="claude_vertexai_agent",
           instruction="You are an assistant powered by Claude 3 Sonnet on Agent Platform.",
           generate_content_config=types.GenerateContentConfig(max_output_tokens=4096),
           # ... other agent parameters
       )
       ```

=== "Java"

    **통합 방법:** 공급자별 모델 클래스(예: `com.google.adk.models.Claude`)를 직접 인스턴스화하고 에이전트 플랫폼 백엔드로 구성합니다.

    **직접 인스턴스화하는 이유** Java ADK의 `LlmRegistry`는 기본적으로 주로 Gemini 모델을 처리합니다. Agent Platform의 Claude와 같은 타사 모델의 경우 ADK의 래퍼 클래스(예: `Claude`) 인스턴스를 `LlmAgent`에 직접 제공합니다. 이 래퍼 클래스는 에이전트 플랫폼용으로 구성된 특정 클라이언트 라이브러리를 통해 모델과 상호 작용하는 역할을 담당합니다.

    **설정:**

    1. **에이전트 플랫폼 환경:**
        * Google Cloud 프로젝트와 리전이 올바르게 설정되었는지 확인하세요.
        * **애플리케이션 기본 자격 증명(ADC):** ADC가 사용자 환경에 올바르게 구성되어 있는지 확인하세요. 이는 일반적으로 `gcloud auth application-default login`를 실행하여 수행됩니다. Java 클라이언트 라이브러리는 이러한 자격 증명을 사용하여 에이전트 플랫폼을 인증합니다. 자세한 설정은 [Google Cloud Java documentation on ADC](https://cloud.google.com/java/docs/reference/google-auth-library/latest/com.google.auth.oauth2.GoogleCredentials#com_google_auth_oauth2_GoogleCredentials_getApplicationDefault__)를 따르세요.

    2. **공급자 라이브러리 종속성:**
        * **타사 클라이언트 라이브러리(종종 전이적):** ADK 핵심 라이브러리에는 에이전트 플랫폼의 일반적인 타사 모델에 필요한 클라이언트 라이브러리(예: Anthropic의 필수 클래스)가 **전이적 종속성**으로 포함되는 경우가 많습니다. 즉, `pom.xml` 또는 `build.gradle`에서 Anthropic Vertex SDK에 대한 별도의 종속성을 명시적으로 추가할 필요가 없을 수도 있습니다.

    3. **모델 인스턴스화 및 구성:**
        `LlmAgent`를 생성할 때 `Claude` 클래스(또는 다른 공급자에 해당하는 클래스)를 인스턴스화하고 해당 `VertexBackend`를 구성합니다.

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
            // Model name for Claude 3 Sonnet on Agent Platform (or other versions)
            String claudeModelVertexAi = "claude-3-7-sonnet"; // Or any other Claude model

            // Configure the AnthropicOkHttpClient with the VertexBackend
            AnthropicClient anthropicClient = AnthropicOkHttpClient.builder()
                .backend(
                    VertexBackend.builder()
                        .region("us-east5") // Specify your Agent Platform region
                        .project("your-gcp-project-id") // Specify your GCP Project ID
                        .googleCredentials(GoogleCredentials.getApplicationDefault())
                        .build())
                .build();

            // Instantiate LlmAgent with the ADK Claude wrapper
            LlmAgent agentClaudeVertexAi = LlmAgent.builder()
                .model(new Claude(claudeModelVertexAi, anthropicClient)) // Pass the Claude instance
                .name("claude_vertexai_agent")
                .instruction("You are an assistant powered by Claude 3 Sonnet on Agent Platform.")
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

## 에이전트 플랫폼의 개방형 모델 {#open-models}

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

Agent Platform은 MaaS(Model-as-a-Service)를 통해 Meta Llama와 같은 엄선된 오픈 소스 모델을 제공합니다. 이러한 모델은 관리형 API를 통해 액세스할 수 있으므로 기본 인프라를 관리하지 않고도 배포하고 확장할 수 있습니다. 사용 가능한 옵션의 전체 목록은 [Agent Platform open models for MaaS](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/maas/use-open-models#open-models) 설명서를 참조하세요.

=== "Python"

    [LiteLLM](https://docs.litellm.ai/) 라이브러리를 사용하여 에이전트 플랫폼 MaaS에서 Meta의 Llama와 같은 개방형 모델에 액세스할 수 있습니다.

    **통합 방법:** `LiteLlm` 래퍼 클래스를 사용하고 설정합니다.
    `LlmAgent`의 `model` 매개변수로 사용됩니다. ADK에서 LiteLLM을 사용하는 방법에 대한 [LiteLLM model connector for ADK agents](/agents/models/litellm/#litellm-model-connector-for-adk-agents) 문서를 확인하세요.

    **설정:**

    1. **에이전트 플랫폼 환경:** 통합된 에이전트 플랫폼 설정(ADC, Env)을 보장합니다.
       바르스, `GOOGLE_GENAI_USE_VERTEXAI=TRUE`)가 완성되었습니다.

    2. **LiteLLM 설치:**
            ```shell
            pip install litellm
            ```

    **예:**

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
