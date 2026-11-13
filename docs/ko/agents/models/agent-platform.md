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
    export GOOGLE_GENAI_USE_ENTERPRISE=TRUE
    ```

## 모델 정원 배포

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.2.0</span><span class="lst-java">Java v0.1.0</span>
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
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.2.0</span><span class="lst-java">Java v0.1.0</span>
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
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.2.0</span><span class="lst-typescript">TypeScript v2.4.0</span><span class="lst-go">Go v2.7.0</span><span class="lst-java">Java v0.1.0</span><span class="lst-kotlin">Kotlin v1.4.0</span>
</div>

Anthropic과 같은 일부 제공업체는 Agent Platform을 통해 모델을 직접 제공합니다. 확장 추론(extended thinking) 및 프롬프트 캐싱을 포함하여 Agent Platform에서 Claude 모델을 설정하고 사용하려면 Claude 모델 가이드의 [Agent Platform을 통해 연결](/ko/agents/models/anthropic/#connect-through-agent-platform)을 참고하세요.

## 에이전트 플랫폼의 개방형 모델 {#open-models}

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

Agent Platform은 MaaS(Model-as-a-Service)를 통해 Meta Llama와 같은 엄선된 오픈 소스 모델을 제공합니다. 이러한 모델은 관리형 API를 통해 액세스할 수 있으므로 기본 인프라를 관리하지 않고도 배포하고 확장할 수 있습니다. 사용 가능한 옵션의 전체 목록은 [Agent Platform open models for MaaS](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/maas/use-open-models#open-models) 설명서를 참고하세요.

=== "Python"

    [LiteLLM](https://docs.litellm.ai/) 라이브러리를 사용하여 에이전트 플랫폼 MaaS에서 Meta의 Llama와 같은 개방형 모델에 액세스할 수 있습니다.

    **통합 방법:** `LiteLlm` 래퍼 클래스를 사용하고 설정합니다.
    `LlmAgent`의 `model` 매개변수로 사용됩니다. ADK에서 LiteLLM을 사용하는 방법에 대한 [LiteLLM model connector for ADK agents](/agents/models/litellm/#litellm-model-connector-for-adk-agents) 문서를 확인하세요.

    **설정:**

    1. **에이전트 플랫폼 환경:** 통합된 에이전트 플랫폼 설정(ADC, Env)을 보장합니다.
       바르스, `GOOGLE_GENAI_USE_ENTERPRISE=TRUE`)가 완성되었습니다.

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
