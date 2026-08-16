# ADK エージェント用 Claude モデル

<div class="language-support-tag">
   <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

Python と Java の両方で ADK とともに Anthropic の Claude モデルを使用できます。以下の言語とバックエンドに一致するパスを選択してください。

## Python

Python からは次の方法で Claude モデルを使用できます。

- **Agent Platform ネイティブ:** Claude モデル文字列を直接渡します。ADK のレジストリがそれを `Claude` ラッパーにルーティングします。詳細については、[Agent Platform 上の Anthropic Claude](/agents/models/agent-platform/#anthropic-claude) を参照してください。
- **LiteLLM を介した直接 Anthropic API:** Anthropic API キーとともに `LiteLlm` コネクタを使用します。詳細については、[LiteLLM](/agents/models/litellm/#anthropic-thinking-blocks) を参照してください。

## Java

Java では、ADK の `Claude` ラッパー クラスを使用して、Anthropic API キーまたは Agent Platform バックエンドで Claude モデルを直接統合できます。Google Cloud Agent Platform サービスを通じて Claude にアクセスすることもできます。[Agent Platform 上のサードパーティ モデル](/agents/models/agent-platform/#anthropic-claude) を参照してください。

### はじめに

次のコード例は、エージェントで Claude モデルを使用するための基本的な実装を示しています。

```java
public static LlmAgent createAgent() {

  AnthropicClient anthropicClient = AnthropicOkHttpClient.builder()
      .apiKey("ANTHROPIC_API_KEY")
      .build();

  Claude claudeModel = new Claude(
      "claude-sonnet-4-6", anthropicClient
  );

  return LlmAgent.builder()
      .name("claude_direct_agent")
      .model(claudeModel)
      .instruction("You are a helpful AI assistant powered by Anthropic Claude.")
      .build();
}
```

### 前提条件

- **依存関係:** Java ADK の `com.google.adk.models.Claude` ラッパーは Anthropic の公式 Java SDK のクラスに依存しており、通常は*推移的依存関係*として含まれます。詳細については、[Anthropic Java SDK](https://github.com/anthropics/anthropic-sdk-java) を参照してください。
- **Anthropic API キー:** Anthropic から API キーを取得し、シークレット マネージャーを使用して安全に管理します。

### 実装例

`com.google.adk.models.Claude` をインスタンス化し、目的の Claude モデル名と API キーで構成された `AnthropicOkHttpClient` を提供します。次に、以下の例に示すように、`Claude` インスタンスを `LlmAgent` に渡します。

```java
import com.anthropic.client.AnthropicClient;
import com.google.adk.agents.LlmAgent;
import com.google.adk.models.Claude;
import com.anthropic.client.okhttp.AnthropicOkHttpClient; // Anthropic SDK より

public class DirectAnthropicAgent {

  private static final String CLAUDE_MODEL_ID = "claude-sonnet-4-6"; // または好みの Claude モデル

  public static LlmAgent createAgent() {

    // 機密キーは安全な構成からロードすることをお勧めします
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
        // ... その他の LlmAgent 構成
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
