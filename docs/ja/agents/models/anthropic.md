# ADK エージェント用の Claude モデル

<div class="language-support-tag">
   <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

Python と Java の両方で、ADK と共に Anthropic の Claude モデルを使用できます。以下から、使用する言語とバックエンドに対応するパスを選択してください。

## Python

Python から Claude モデルを使用する方法は以下の通りです：

- **ネイティブ、Agent Platform 上:** `Claude` ラッパーを登録し、Claude モデル文字列を使用します。[Agent Platform 上の Anthropic Claude](/ja/agents/models/agent-platform/#anthropic-claude) セクションを参照してください。
- **直接の Anthropic API、LiteLLM 経由:** Anthropic API キーと共に `LiteLlm` コネクタを使用します。[LiteLLM](/ja/agents/models/litellm/#anthropic-thinking-blocks) セクションを参照してください。

## Java

Java では、ADK の `Claude` ラッパークラスを使用して、Anthropic API キーまたは Agent Platform バックエンド経由で Java ADK アプリケーションに Anthropic の Claude モデルを直接統合できます。また、Google Cloud Agent Platform サービス経由で Claude にアクセスすることもできます。詳細は [Agent Platform のサードパーティモデル](/ja/agents/models/agent-platform/#anthropic-claude) セクションを参照してください。

### はじめに

以下のコード例は、エージェントで Claude モデルを使用する基本実装を示します：

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

### 事前準備

- **依存関係:** Java ADK の `com.google.adk.models.Claude` ラッパーは、Anthropic 公式の Java SDK のクラスに依存しています。これらは通常、*トランジティブ依存関係*として含まれます。詳細は [Anthropic Java SDK](https://github.com/anthropics/anthropic-sdk-java) を参照してください。
- **Anthropic API キー:** Anthropic から API キーを取得し、シークレットマネージャー等で安全に管理してください。

### 実装例

希望する Claude モデル名と、API キーを設定した `AnthropicOkHttpClient` を用いて `com.google.adk.models.Claude` をインスタンス化します。次に、以下の例のように `Claude` インスタンスを `LlmAgent` に渡します：

```java
import com.anthropic.client.AnthropicClient;
import com.google.adk.agents.LlmAgent;
import com.google.adk.models.Claude;
import com.anthropic.client.okhttp.AnthropicOkHttpClient; // Anthropic SDKから提供

public class DirectAnthropicAgent {

  private static final String CLAUDE_MODEL_ID = "claude-sonnet-4-6"; // お好みの Claude モデル名

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
