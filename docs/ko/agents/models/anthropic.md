# ADK 에이전트를 위한 Claude 모델

<div class="language-support-tag" title="Java에서 지원됩니다. Python은 Vertex를 거치지 않는 Anthropic API 직접 호출은 LiteLLM을 통해 지원됩니다.">
   <span class="lst-supported">Supported in ADK</span><span class="lst-java">Java v0.2.0</span>
</div>

ADK의 `Claude` 래퍼 클래스를 사용하면 Anthropic API 키 또는
Vertex AI 백엔드를 통해 Java ADK 애플리케이션에 Anthropic의 Claude 모델을 직접 통합할 수 있습니다.
또한 Google Cloud Vertex AI 서비스를 통해 Anthropic 모델에 접근할 수 있습니다.
자세한 내용은 [Vertex AI의 타사 모델](/adk-docs/agents/models/vertex/#third-party-models-on-vertex-ai-eg-anthropic-claude) 섹션을 참조하세요.
또한 Python에서는 [LiteLLM](/adk-docs/agents/models/litellm/) 라이브러리를 통해 Anthropic 모델을 사용할 수 있습니다.

## 시작하기

다음 코드 예제는 에이전트에서 Claude 모델을 사용하는 기본 구현을 보여줍니다.

```java
public static LlmAgent createAgent() {

  AnthropicClient anthropicClient = AnthropicOkHttpClient.builder()
      .apiKey("ANTHROPIC_API_KEY")
      .build();

  Claude claudeModel = new Claude(
      "claude-3-7-sonnet-latest", anthropicClient
  );

  return LlmAgent.builder()
      .name("claude_direct_agent")
      .model(claudeModel)
      .instruction("You are a helpful AI assistant powered by Anthropic Claude.")
      .build();
}
```

## 사전 요구 사항

1.  **종속성:**
    *   **Anthropic SDK 클래스(전이 종속성):** Java ADK의 `com.google.adk.models.Claude`
    래퍼는 Anthropic 공식 Java SDK의 클래스를 사용합니다.
    이러한 클래스는 일반적으로 *전이 종속성*으로 포함됩니다.
    자세한 내용은 [Anthropic Java SDK](https://github.com/anthropics/anthropic-sdk-java)를 확인하세요.

2.  **Anthropic API 키:**
    *   Anthropic에서 API 키를 발급받습니다. 비밀 관리자(secret manager)로 이 키를 안전하게 관리하세요.

## 구현 예시

원하는 Claude 모델 이름과 API 키가 설정된 `AnthropicOkHttpClient`를 사용해
`com.google.adk.models.Claude`를 인스턴스화합니다.
그런 다음 다음 예시처럼 `Claude` 인스턴스를 `LlmAgent`에 전달합니다.

```java
import com.anthropic.client.AnthropicClient;
import com.google.adk.agents.LlmAgent;
import com.google.adk.models.Claude;
import com.anthropic.client.okhttp.AnthropicOkHttpClient; // Anthropic SDK에서 제공

public class DirectAnthropicAgent {

  private static final String CLAUDE_MODEL_ID = "claude-3-7-sonnet-latest"; // 원하는 Claude 모델로 변경

  public static LlmAgent createAgent() {

    // 민감한 키는 안전한 설정에서 로드하는 것이 좋습니다.
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
        .instruction("You are a helpful AI assistant powered by Anthropic Claude.")
        // ... 기타 LlmAgent 구성
        .build();
  }

  public static void main(String[] args) {
    try {
      LlmAgent agent = createAgent();
      System.out.println("Successfully created direct Anthropic agent: " + agent.name());
    } catch (IllegalStateException e) {
      System.err.println("Error creating agent: " + e.getMessage());
    }
  }
}
```
