# ADK에서 Anthropic Claude 모델 사용하기

<div class="language-support-tag">
   <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v2.4.0</span><span class="lst-go">Go v2.7.0</span><span class="lst-java">Java v0.2.0</span><span class="lst-kotlin">Kotlin v1.4.0</span>
</div>

Agent Development Kit(ADK) 에이전트의 모델로 Anthropic의 Claude 모델을 사용할 수 있습니다. 프레임워크는 ADK 요청, 도구 및 응답을 Claude 호출로 변환하는 Claude 모델 클래스를 제공하므로 Gemini로 에이전트를 구축하는 것과 동일한 방식으로 Claude를 사용하여 에이전트를 구축할 수 있으며, 다음과 같은 작업이 가능합니다:

-   ADK 도구, 세션 및 콜백을 변경하지 않고 그대로 유지하면서 Claude에서 에이전트를 실행합니다.
-   단일 멀티 에이전트 시스템에서 Claude 에이전트와 Gemini 에이전트를 결합하고 각 에이전트의 작업에 따라 모델을 선택합니다.
-   확장 추론(extended thinking)을 사용하여 복잡한 작업에서 Claude에 더 많은 추론 시간을 부여합니다.

Anthropic API 키를 사용하는 **Anthropic API** 또는 Google Cloud 프로젝트와 자격 증명을 사용하는 **Google Cloud**를 통해 Claude에 연결할 수 있습니다. 선택에 도움이 필요하면 [백엔드 선택](#choose-a-backend)을 참고하세요.

## 시작하기 {#get-started}

다음 예시는 Anthropic API를 통해 Claude를 호출하는 에이전트를 생성합니다. 실행하기 전에 [Anthropic Console](https://console.anthropic.com/)에서 API 키를 발급받아 환경 변수로 설정하세요. 프로덕션 환경에서는 소스 코드나 셸 기록 대신 보안 비밀 관리자(Secret Manager)에 키를 저장하세요:

```shell
export ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY"
```

=== "Python"

    Anthropic SDK와 함께 ADK를 설치합니다:

    ```shell
    pip install "google-adk[extensions]"
    ```

    `AnthropicLlm` 인스턴스를 생성하여 에이전트에 전달합니다. 이 클래스는 `ANTHROPIC_API_KEY` 환경 변수에서 API 키를 읽어옵니다. `AnthropicLlm` 클래스는 ADK Python v1.20.0 이상에서 사용할 수 있습니다.

    ```python
    from google.adk.agents import LlmAgent
    from google.adk.models.anthropic_llm import AnthropicLlm

    root_agent = LlmAgent(
        name="claude_agent",
        model=AnthropicLlm(model="claude-sonnet-4-6"),
        instruction="You are a helpful assistant.",
    )
    ```

=== "TypeScript"

    TypeScript에서 Claude는 Google Cloud Agent Platform을 통해서만 사용할 수 있습니다. ADK 통합 패키지와 Anthropic SDK를 설치합니다:

    ```shell
    npm install @google/adk @google/adk-integrations @anthropic-ai/sdk @anthropic-ai/vertex-sdk
    ```

    [Agent Platform 설정](#connect-through-agent-platform)을 완료한 다음, `Claude` 인스턴스를 생성하여 에이전트에 전달합니다:

    ```typescript
    import {LlmAgent} from '@google/adk';
    import {Claude} from '@google/adk-integrations';

    export const rootAgent = new LlmAgent({
      name: 'claude_agent',
      model: new Claude({model: 'claude-sonnet-4-6@default'}),
      instruction: 'You are a helpful assistant.',
    });
    ```

=== "Go"

    !!! example "실험적 기능"

        `anthropicmodel` 패키지는 실험적 기능입니다. API 및 동작에 제한 사항이 있을 수 있으며 프로덕션 환경에서의 사용은 권장되지 않습니다.

    `anthropicmodel.NewModel`로 모델을 생성하여 에이전트에 전달합니다. `APIKey`가 비어 있으면 모델은 `ANTHROPIC_API_KEY` 환경 변수에서 키를 읽어옵니다.

    ```go
    import (
    	"context"
    	"log"

    	"google.golang.org/adk/v2/agent/llmagent"
    	"google.golang.org/adk/v2/model/anthropicmodel"
    )

    llm, err := anthropicmodel.NewModel(context.Background(), "claude-sonnet-4-6", anthropicmodel.ClientConfig{
    	Backend: anthropicmodel.BackendAnthropic,
    })
    if err != nil {
    	log.Fatal(err)
    }

    agent, err := llmagent.New(llmagent.Config{
    	Name:        "claude_agent",
    	Model:       llm,
    	Instruction: "You are a helpful assistant.",
    })
    if err != nil {
    	log.Fatal(err)
    }
    ```

    실행 가능한 전체 샘플은 ADK Go 저장소의 [examples/anthropic/](https://github.com/google/adk-go/tree/main/examples/anthropic)을 참고하세요.

=== "Java"

    ADK Java 코어 라이브러리에는 [Anthropic Java SDK](https://github.com/anthropics/anthropic-sdk-java)가 종속 항목으로 포함되어 있습니다. `AnthropicClient`를 생성하고 `Claude` 인스턴스로 감싼 후 에이전트에 전달합니다:

    ```java
    import com.anthropic.client.AnthropicClient;
    import com.anthropic.client.okhttp.AnthropicOkHttpClient;
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.models.Claude;

    public class ClaudeAgent {

      public static LlmAgent createAgent() {
        AnthropicClient anthropicClient = AnthropicOkHttpClient.builder()
            .apiKey(System.getenv("ANTHROPIC_API_KEY"))
            .build();

        return LlmAgent.builder()
            .name("claude_agent")
            .model(new Claude("claude-sonnet-4-6", anthropicClient))
            .instruction("You are a helpful assistant.")
            .build();
      }
    }
    ```

=== "Kotlin"

    Gradle 빌드에 ADK Anthropic 통합 모듈을 추가합니다. 이 모듈은 JVM 전용입니다.

    ```kotlin
    implementation("com.google.adk:google-adk-kotlin-integrations-anthropic:1.5.0")
    ```

    `Claude` 인스턴스를 생성하여 에이전트에 전달합니다. `apiKey`를 생략하면 모델은 `ANTHROPIC_API_KEY` 환경 변수에서 키를 읽어옵니다.

    ```kotlin
    import com.google.adk.kt.agents.Instruction
    import com.google.adk.kt.agents.LlmAgent
    import com.google.adk.kt.models.anthropic.Claude

    val rootAgent =
      LlmAgent(
        name = "claude_agent",
        model = Claude(name = "claude-sonnet-4-6"),
        instruction = Instruction("You are a helpful assistant."),
      )
    ```

## 백엔드 선택 {#choose-a-backend}

결제, 액세스 권한 및 할당량을 관리하는 위치에 따라 백엔드를 선택하세요:

-   **Anthropic API:** 이미 Anthropic 계정이 있고 그곳에서 Claude 사용량을 관리하는 경우 이 백엔드를 사용하세요. Anthropic API 키로 인증합니다.
-   **Google Cloud:** 애플리케이션이 Google Cloud에서 실행되거나 Google Cloud 프로젝트의 IAM 권한, 할당량 및 결제를 통해 Claude 사용량을 관리하려는 경우 이 백엔드를 사용하세요. 애플리케이션 기본 사용자 인증 정보(ADC)로 인증하므로 별도의 API 키를 관리할 필요가 없습니다.

다음 표는 각 언어에서 백엔드를 선택하는 방법을 보여줍니다:

| 언어 | Anthropic API | Agent Platform |
| :--------- | :-------------------------------------------------- | :------------------------------------------------------------------- |
| Python | `AnthropicLlm` 인스턴스 | `Claude` 인스턴스 또는 `claude-*` 모델 문자열 |
| TypeScript | 지원되지 않음 | `Claude` 인스턴스 또는 `Claude` 등록 후 `claude-*` 문자열 |
| Go | `ClientConfig.Backend`를 `BackendAnthropic`으로 설정 | `ClientConfig.Backend`를 `BackendVertex`로 설정 |
| Java | API 키를 사용하는 `AnthropicClient`가 포함된 `Claude` | `VertexBackend`를 사용하는 `AnthropicClient`가 포함된 `Claude` |
| Kotlin | `Claude(name, apiKey)` | `Claude(name, vertexCredentials)` |

!!! warning "Python 모델 문자열은 Google Cloud Agent Platform을 사용합니다"

    Python에서 `model="claude-sonnet-4-6"`과 같은 단순 `claude-*` 모델 문자열은 Agent Platform 백엔드로 라우팅되며 Google Cloud 프로젝트 설정이 필요합니다. Python에서 Anthropic API를 사용하려면 문자열 대신 `AnthropicLlm` 인스턴스를 전달하세요.

## Google Cloud를 통해 연결 {#connect-through-agent-platform}

Google Cloud를 통해 Claude를 사용하려면 Google Cloud 환경을 설정하세요:

1.  Google Cloud 프로젝트의 [Model Garden](https://console.cloud.google.com/vertex-ai/model-garden)에서 사용하려는 Claude 모델을 사용 설정합니다.
2.  애플리케이션 기본 사용자 인증 정보(ADC)를 설정합니다:

    ```shell
    gcloud auth application-default login
    ```

3.  프로젝트와 모델을 사용할 수 있는 리전(예: `global` 또는 `us-east5`)을 설정합니다:

    ```shell
    export GOOGLE_CLOUD_PROJECT="your-project-id"
    export GOOGLE_CLOUD_LOCATION="global"
    ```

ADK를 Google Cloud에 연결하는 방법에 대한 자세한 내용은 [Google Cloud 및 Agent Platform에 연결](/ko/get-started/google-cloud/)을 참고하세요.

다음 예시는 Google Cloud를 통해 Claude를 호출하는 에이전트를 생성합니다:

=== "Python"

    Claude 모델 문자열을 에이전트에 전달합니다. ADK는 `claude-*` 문자열을 `GOOGLE_CLOUD_PROJECT` 및 `GOOGLE_CLOUD_LOCATION`을 읽어오는 `Claude` 클래스로 라우팅합니다.

    ```python
    from google.adk.agents import LlmAgent

    root_agent = LlmAgent(
        name="claude_agent",
        model="claude-sonnet-4-6",
        instruction="You are a helpful assistant.",
    )
    ```

    ADK Python v2.9.0 이상은 모든 `claude-*` 모델 문자열을 `Claude`로 라우팅합니다. 이전 버전에서 ADK가 모델 문자열을 인식하지 못하는 경우 `google.adk.models`에서 `Claude`를 가져와 인스턴스로 전달하세요(`model=Claude(model="claude-sonnet-4-6")`).

=== "TypeScript"

    시작 시 `Claude`를 한 번 등록하면 모든 에이전트가 이름으로 `claude-*` 모델 문자열을 참조할 수 있습니다:

    ```typescript
    import {LLMRegistry, LlmAgent} from '@google/adk';
    import {Claude} from '@google/adk-integrations';

    LLMRegistry.register(Claude);

    export const rootAgent = new LlmAgent({
      name: 'claude_agent',
      model: 'claude-sonnet-4-6@default',
      instruction: 'You are a helpful assistant.',
    });
    ```

=== "Go"

    `Backend`를 `BackendVertex`로 설정합니다. `Project`와 `Location`이 비어 있으면 모델은 `GOOGLE_CLOUD_PROJECT` 및 `GOOGLE_CLOUD_LOCATION`을 읽고 자격 증명으로 ADC를 사용합니다.

    ```go
    llm, err := anthropicmodel.NewModel(ctx, "claude-sonnet-4-6", anthropicmodel.ClientConfig{
    	Backend: anthropicmodel.BackendVertex,
    })
    if err != nil {
    	log.Fatal(err)
    }
    ```

=== "Java"

    `VertexBackend`로 `AnthropicClient`를 구성합니다:

    ```java
    import com.anthropic.client.AnthropicClient;
    import com.anthropic.client.okhttp.AnthropicOkHttpClient;
    import com.anthropic.vertex.backends.VertexBackend;
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.models.Claude;
    import com.google.auth.oauth2.GoogleCredentials;
    import java.io.IOException;

    public class ClaudeAgentPlatformAgent {

      public static LlmAgent createAgent() throws IOException {
        AnthropicClient anthropicClient = AnthropicOkHttpClient.builder()
            .backend(
                VertexBackend.builder()
                    .project("your-project-id")
                    .region("global")
                    .googleCredentials(GoogleCredentials.getApplicationDefault())
                    .build())
            .build();

        return LlmAgent.builder()
            .name("claude_agent")
            .model(new Claude("claude-sonnet-4-6", anthropicClient))
            .instruction("You are a helpful assistant.")
            .build();
      }
    }
    ```

=== "Kotlin"

    `Claude` 생성자에 `VertexCredentials`를 전달합니다. 설정되지 않은 값은 `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION` 및 ADC로 폴백됩니다.

    ```kotlin
    import com.google.adk.kt.agents.Instruction
    import com.google.adk.kt.agents.LlmAgent
    import com.google.adk.kt.models.VertexCredentials
    import com.google.adk.kt.models.anthropic.Claude

    val rootAgent =
      LlmAgent(
        name = "claude_agent",
        model = Claude(name = "claude-sonnet-4-6", vertexCredentials = VertexCredentials()),
        instruction = Instruction("You are a helpful assistant."),
      )
    ```

## 확장 추론 구성

<div class="language-support-tag">
   <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.34.0</span><span class="lst-go">Go v2.7.0</span><span class="lst-kotlin">Kotlin v1.4.0</span>
</div>

확장 추론(extended thinking)을 사용하면 Claude가 응답하기 전에 문제를 단계적으로 추론할 수 있으므로 계획 수립, 분석, 도구 간 선택과 같은 다단계 작업에 도움이 됩니다. 표준 추론 구성의 `thinking_budget` 필드로 이를 구성합니다:

| `thinking_budget` | 동작 |
| :--- | :--- |
| 음수(예: `-1`) | **적응형 추론(Adaptive thinking).** Claude가 각 요청에 대해 추론할 양을 스스로 결정합니다. |
| `0` | **추론 사용 안 함.** Claude가 확장 추론 없이 응답합니다. |
| 양수 | **수동 추론(Manual thinking).** Claude가 지정된 토큰 수까지 사용하여 추론합니다. 최소 및 최대 예산은 Anthropic의 확장 추론 문서를 참고하세요. |

고정된 토큰 예산이 필요한 경우가 아니라면 적응형 추론을 사용하세요. 일부 최신 Claude 모델은 적응형 추론만 허용합니다. 사용 중인 모델에 대한 자세한 내용은 Anthropic의 확장 추론 문서를 참고하세요. 추론 구성을 설정할 때는 반드시 `thinking_budget` 값을 설정해야 합니다.

Claude가 투입하는 추론 노력의 양을 제어하려면 **effort** 수준을 `low`, `medium`, `high`, `xhigh` 또는 `max`로 설정하세요. Claude는 표준 `thinking_level` 설정을 지원하지 않으므로 대신 effort를 사용하세요. 추론 또는 effort가 활성화된 동안에는 ADK가 `temperature`, `top_p` 또는 `top_k`를 Claude에 전송하지 않습니다.

=== "Python"

    ADK Python v2.4.0 이상에서 제공되는 `AnthropicGenerateContentConfig`에 `effort`를 설정합니다:

    ```python
    from google.adk.agents import LlmAgent
    from google.adk.models import AnthropicGenerateContentConfig
    from google.genai import types

    root_agent = LlmAgent(
        name="claude_reasoning_agent",
        model="claude-sonnet-4-6",
        instruction="You are a helpful assistant.",
        generate_content_config=AnthropicGenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=-1),
            effort="high",
        ),
    )
    ```

    `AnthropicGenerateContentConfig`에 `thinking_level`을 설정하면 유효성 검사 오류가 발생합니다. 일반 `types.GenerateContentConfig`에 설정하면 ADK가 이를 무시하고 경고를 기록합니다.

=== "Go"

    에이전트의 `GenerateContentConfig`에 추론 예산을 설정하고 모델의 `ClientConfig`에 effort 수준을 설정합니다:

    ```go
    llm, err := anthropicmodel.NewModel(ctx, "claude-sonnet-4-6", anthropicmodel.ClientConfig{
    	Effort: anthropicmodel.EffortHigh,
    })
    if err != nil {
    	log.Fatal(err)
    }

    agent, err := llmagent.New(llmagent.Config{
    	Name:        "claude_reasoning_agent",
    	Model:       llm,
    	Instruction: "You are a helpful assistant.",
    	GenerateContentConfig: &genai.GenerateContentConfig{
    		ThinkingConfig: &genai.ThinkingConfig{ThinkingBudget: genai.Ptr[int32](-1)},
    	},
    })
    ```

=== "Kotlin"

    에이전트의 `GenerateContentConfig`에 추론 예산을 설정하고 `Claude` 생성자에 effort 수준을 설정합니다:

    ```kotlin
    import com.anthropic.models.messages.OutputConfig
    import com.google.adk.kt.agents.Instruction
    import com.google.adk.kt.agents.LlmAgent
    import com.google.adk.kt.models.anthropic.Claude
    import com.google.adk.kt.types.GenerateContentConfig
    import com.google.adk.kt.types.ThinkingConfig

    val rootAgent =
      LlmAgent(
        name = "claude_reasoning_agent",
        model = Claude(name = "claude-sonnet-4-6", effort = OutputConfig.Effort.HIGH),
        instruction = Instruction("You are a helpful assistant."),
        generateContentConfig =
          GenerateContentConfig(thinkingConfig = ThinkingConfig(thinkingBudget = -1)),
      )
    ```

ADK는 응답에서 Claude의 추론 내용을 사고(thought) 파트로 반환하며, Anthropic API의 요구 사항에 따라 한 턴 내의 도구 호출 전반에 걸쳐 추론 블록과 서명(signature)을 보존합니다.

## 고급 활용

ADK는 프롬프트 캐싱 및 LiteLLM 라이브러리를 통한 모델 액세스를 포함하여 Anthropic 모델의 고급 활용 기능을 지원합니다.

### 프롬프트 캐싱

<div class="language-support-tag">
   <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v2.8.0</span><span class="lst-go">Go v2.7.0</span><span class="lst-kotlin">Kotlin v1.4.0</span>
</div>

긴 지침이나 많은 도구를 가진 에이전트는 모든 요청에서 동일한 프롬프트 프리픽스를 전송합니다. Claude 프롬프트 캐싱은 해당 프리픽스를 저장하여 이후 요청에서 재사용함으로써 비용과 지연 시간을 줄여줍니다. ADK는 도구 선언, 시스템 지침 및 최신 대화 콘텐츠에 캐시 중단점(cache breakpoint)을 배치합니다.

Anthropic은 기본값인 5분 캐시 유효 시간(TTL)과 1시간 캐시 유효 시간을 지원합니다. 동일한 에이전트에 대한 요청 간격이 보통 5분을 초과하는 경우 1시간 유효 시간을 사용하세요. 자세한 내용은 Anthropic의 [프롬프트 캐싱](https://docs.claude.com/en/docs/build-with-claude/prompt-caching) 문서를 참고하세요.

=== "Python"

    `App`에 `ContextCacheConfig`를 설정합니다. `ttl_seconds` 값을 3600 이상으로 지정하면 1시간 캐시가 선택됩니다. 이 구성에 대한 자세한 내용은 [컨텍스트 캐싱](/ko/context/caching/)을 참고하세요.

    ```python
    from google.adk.agents.context_cache_config import ContextCacheConfig
    from google.adk.apps.app import App

    app = App(
        name="claude_caching_app",
        root_agent=root_agent,
        context_cache_config=ContextCacheConfig(
            min_tokens=2048,  # Skip caching for short prompts.
            ttl_seconds=600,
        ),
    )
    ```

=== "Go"

    모델의 `ClientConfig`에 `PromptCache`를 설정합니다. 1시간 캐시를 선택하려면 `TTL`을 `PromptCacheTTL1h`로 설정하세요.

    ```go
    llm, err := anthropicmodel.NewModel(ctx, "claude-sonnet-4-6", anthropicmodel.ClientConfig{
    	PromptCache: &anthropicmodel.PromptCacheConfig{TTL: anthropicmodel.PromptCacheTTL5m},
    })
    ```

=== "Kotlin"

    `App`에 `ContextCacheConfig`를 설정합니다. `ttl`을 1시간 이상으로 지정하면 1시간 캐시가 선택됩니다.

    ```kotlin
    @OptIn(ExperimentalContextCachingFeature::class)
    import com.google.adk.kt.agents.ContextCacheConfig
    import com.google.adk.kt.apps.App
    import kotlin.time.Duration.Companion.minutes

    val app =
      App(
        appName = "claude_caching_app",
        rootAgent = rootAgent,
        contextCacheConfig = ContextCacheConfig(minTokens = 2048, ttl = 10.minutes),
      )
    ```

### LiteLLM을 통해 Claude 사용하기

Python에서는 `anthropic/` 모델 문자열과 함께 `LiteLlm` 커넥터를 사용하여 Claude에 연결할 수도 있습니다. 애플리케이션이 이미 LiteLLM을 통해 모델을 라우팅하는 경우 이 경로를 사용하세요. 설정 방법은 [LiteLLM](/ko/agents/models/litellm/#anthropic-thinking-blocks)을 참고하세요.

## 구성 옵션

Claude 모델 클래스는 다음 옵션을 허용합니다:

=== "Python"

    이 옵션들은 `AnthropicLlm`과 `Claude` 모두에 적용됩니다.

    | 옵션 | 타입 | 기본값 | 설명 |
    | :--- | :--- | :--- | :--- |
    | `model` | `str` | `"claude-sonnet-4-20250514"` (`AnthropicLlm`), `"claude-3-5-sonnet-v2@20241022"` (`Claude`) | Claude 모델 ID입니다. |
    | `max_tokens` | `int` | `8192` | 요청에 `max_output_tokens`가 설정되지 않은 경우의 최대 출력 토큰 수입니다. |
    | `client` | `AsyncAnthropic` 또는 `AsyncAnthropicVertex` | `None` | 사전 구성된 Anthropic 클라이언트입니다. `Claude` 클래스에는 `AsyncAnthropicVertex` 클라이언트가 필요합니다. |

=== "TypeScript"

    | 옵션 | 타입 | 기본값 | 설명 |
    | :--- | :--- | :--- | :--- |
    | `model` | `string` | `'claude-sonnet-4-6@default'` | Agent Platform의 Claude 모델 ID입니다. |
    | `maxTokens` | `number` | `8192` | 요청에 `maxOutputTokens`가 설정되지 않은 경우의 최대 출력 토큰 수입니다. |

=== "Go"

    주요 `ClientConfig` 필드:

    | 옵션 | 타입 | 기본값 | 설명 |
    | :--- | :--- | :--- | :--- |
    | `Backend` | `Backend` | `BackendAnthropic` | 서빙 백엔드: `BackendAnthropic` 또는 `BackendVertex`입니다. |
    | `APIKey` | `string` | `ANTHROPIC_API_KEY` | `BackendAnthropic`용 Anthropic API 키입니다. |
    | `Project` | `string` | `GOOGLE_CLOUD_PROJECT` | `BackendVertex`용 Google Cloud 프로젝트입니다. |
    | `Location` | `string` | `GOOGLE_CLOUD_LOCATION` | `BackendVertex`용 Google Cloud 리전입니다. |
    | `MaxTokens` | `int` | `8192` | 요청에 `MaxOutputTokens`가 설정되지 않은 경우의 최대 출력 토큰 수입니다. |
    | `MaxRetries` | `*int` | `2` | 실패한 요청에 대해 Anthropic SDK가 재시도하는 횟수입니다. |
    | `Effort` | `Effort` | 모델 기본값 | 추론 노력(effort) 수준입니다. |
    | `PromptCache` | `*PromptCacheConfig` | `nil` | 설정 시 프롬프트 캐싱을 활성화합니다. |

    전체 목록은 [`anthropicmodel` 패키지 레퍼런스](https://pkg.go.dev/google.golang.org/adk/v2/model/anthropicmodel)를 참고하세요.

=== "Java"

    | 옵션 | 타입 | 기본값 | 설명 |
    | :--- | :--- | :--- | :--- |
    | `modelName` | `String` | 필수 | Claude 모델 ID입니다. |
    | `anthropicClient` | `AnthropicClient` | 필수 | Anthropic API 또는 `VertexBackend`용으로 구성된 Anthropic 클라이언트입니다. |
    | `maxTokens` | `int` | `8192` | 각 요청에 대한 최대 출력 토큰 수입니다. |

=== "Kotlin"

    | 옵션 | 타입 | 기본값 | 설명 |
    | :--- | :--- | :--- | :--- |
    | `name` | `String` | 필수 | Claude 모델 ID입니다. |
    | `apiKey` | `String?` | `ANTHROPIC_API_KEY` | Anthropic API 키입니다. Anthropic API 백엔드를 선택합니다. |
    | `vertexCredentials` | `VertexCredentials` | 없음 | 프로젝트, 위치 및 자격 증명입니다. Agent Platform 백엔드를 선택합니다. |
    | `client` | `AnthropicClient` | 없음 | `apiKey` 또는 `vertexCredentials` 대신 사용되는 사전 구성된 Anthropic 클라이언트입니다. |
    | `maxTokens` | `Int` | `8192` | 요청에 설정된 값이 없는 경우의 최대 출력 토큰 수입니다. |
    | `effort` | `OutputConfig.Effort?` | `null` | 추론 노력(effort) 수준입니다. |

## 제한 사항

-   **Live API:** Claude 모델은 Live API를 사용한 ADK 양방향 스트리밍을 지원하지 않습니다.
-   **TypeScript:** `Claude` 클래스는 스트리밍 없이 전체 응답을 반환하며 텍스트, 함수 호출 및 함수 응답 파트만 허용합니다. 전체 목록은 [Claude 통합 가이드](https://github.com/google/adk-js/blob/main/docs/guides/integrations/models/anthropic_llm/index.md#limitations)를 참고하세요.

## 다음 단계

-   [Agent Platform 호스팅 모델](/ko/agents/models/agent-platform/): Agent Platform에 배포된 다른 모델을 사용합니다.
-   [LiteLLM](/ko/agents/models/litellm/): 다른 제공업체의 모델에 연결합니다.
-   [컨텍스트 캐싱](/ko/context/caching/): 캐시 설정에 대해 자세히 알아봅니다.
