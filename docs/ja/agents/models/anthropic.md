# ADK エージェント用の Claude モデル

<div class="language-support-tag" title="Java でサポートされています。Python の直接 Anthropic API（非 Vertex）は LiteLLM 経由でサポートされます。">
   <span class="lst-supported">Supported in ADK</span><span class="lst-java">Java v0.2.0</span>
</div>

ADK の `Claude` ラッパークラスを使用すると、Anthropic API キー、または Vertex AI
バックエンド経由で Java ADK アプリケーションに Anthropic の Claude モデルを直接統合できます。
また、Google Cloud Vertex AI サービスからも Anthropic モデルにアクセスできます。
詳細は [Vertex AI のサードパーティモデル](/adk-docs/agents/models/vertex/#third-party-models-on-vertex-ai-eg-anthropic-claude) セクションを参照してください。
Python の場合は [LiteLLM](/adk-docs/agents/models/litellm/) ライブラリ経由で
Anthropic モデルを利用することもできます。

## はじめに

以下のコード例は、エージェントで Claude モデルを使用する基本実装を示します。

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

## 事前準備

1.  **依存関係:**
    *   **Anthropic SDK クラス（トランジティブ）:** Java ADK の `com.google.adk.models.Claude`
    ラッパーは、Anthropic 公式の Java SDK のクラスに依存しています。
    これらは通常、*トランジティブ依存関係*として含まれます。
    詳細は [Anthropic Java SDK](https://github.com/anthropics/anthropic-sdk-java) を参照してください。

2.  **Anthropic API キー:**
    *   Anthropic から API キーを取得し、シークレットマネージャーで安全に管理してください。

## 実装例

希望する Claude モデル名と、API キーを設定した `AnthropicOkHttpClient` を用いて
`com.google.adk.models.Claude` をインスタンス化します。次に、以下の例のように
この `Claude` インスタンスを `LlmAgent` に渡します。

```java
import com.anthropic.client.AnthropicClient;
import com.google.adk.agents.LlmAgent;
import com.google.adk.models.Claude;
import com.anthropic.client.okhttp.AnthropicOkHttpClient; // From Anthropic's SDK

public class DirectAnthropicAgent {

  private static final String CLAUDE_MODEL_ID = "claude-3-7-sonnet-latest"; // お好みの Claude モデル名

  public static LlmAgent createAgent() {

    // 機密キーは安全な設定から読み込むことを推奨します
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
        // ... other LlmAgent configurations
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
