# ADK で Anthropic Claude モデルを使用する

<div class="language-support-tag">
   <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v2.4.0</span><span class="lst-go">Go v2.7.0</span><span class="lst-java">Java v0.2.0</span><span class="lst-kotlin">Kotlin v1.4.0</span>
</div>

Agent Development Kit（ADK）エージェントのモデルとして Anthropic の Claude モデルを使用できます。フレームワークには ADK のリクエスト、ツール、レスポンスを Claude への呼び出しに変換する Claude モデルクラスが用意されているため、Gemini でエージェントを構築するのと同じ方法で Claude を使ったエージェントを構築でき、次のようなことが可能です:

-   ADK のツール、セッション、コールバックをそのまま変更せずに Claude 上でエージェントを実行する。
-   1 つのマルチエージェント システム内で Claude エージェントと Gemini エージェントを組み合わせ、各エージェントのタスクに応じてモデルを選択する。
-   拡張思考（extended thinking）を使用して、複雑なタスクで Claude により深い推論を行わせる。

Claude には、Anthropic API キーを使用する **Anthropic API**、または Google Cloud のプロジェクトと認証情報を使用する **Google Cloud** を通じて接続できます。選択の参考にするには、[バックエンドを選択する](#choose-a-backend)を参照してください。

## はじめに {#get-started}

次の例では、Anthropic API を通じて Claude を呼び出すエージェントを作成します。実行する前に、[Anthropic Console](https://console.anthropic.com/) から API キーを取得し、環境変数として設定してください。本番環境では、ソースコードやシェルの履歴ではなくシークレット マネージャーにキーを保存してください:

```shell
export ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY"
```

=== "Python"

    Anthropic SDK を含む ADK をインストールします:

    ```shell
    pip install "google-adk[extensions]"
    ```

    `AnthropicLlm` インスタンスを作成してエージェントに渡します。このクラスは環境変数 `ANTHROPIC_API_KEY` から API キーを読み取ります。`AnthropicLlm` クラスは ADK Python v1.20.0 以降で利用できます。

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

    TypeScript では、Claude は Google Cloud Agent Platform 経由でのみ利用できます。ADK 統合パッケージと Anthropic SDK をインストールします:

    ```shell
    npm install @google/adk @google/adk-integrations @anthropic-ai/sdk @anthropic-ai/vertex-sdk
    ```

    [Agent Platform のセットアップ](#connect-through-agent-platform)を完了してから、`Claude` インスタンスを作成してエージェントに渡します:

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

    !!! example "実験的機能"

        `anthropicmodel` パッケージは実験的機能です。API や動作に制限がある可能性があり、本番環境での使用は推奨されません。

    `anthropicmodel.NewModel` でモデルを作成し、エージェントに渡します。`APIKey` が空の場合、モデルは環境変数 `ANTHROPIC_API_KEY` からキーを読み取ります。

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

    完全な実行可能サンプルについては、ADK Go リポジトリの [examples/anthropic/](https://github.com/google/adk-go/tree/main/examples/anthropic) を参照してください。

=== "Java"

    ADK Java コアライブラリには依存関係として [Anthropic Java SDK](https://github.com/anthropics/anthropic-sdk-java) が含まれています。`AnthropicClient` を作成し、`Claude` インスタンスでラップしてエージェントに渡します:

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

    Gradle ビルドに ADK Anthropic 統合モジュールを追加します。このモジュールは JVM 専用です。

    ```kotlin
    implementation("com.google.adk:google-adk-kotlin-integrations-anthropic:1.5.0")
    ```

    `Claude` インスタンスを作成してエージェントに渡します。`apiKey` を省略すると、モデルは環境変数 `ANTHROPIC_API_KEY` からキーを読み取ります。

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

## バックエンドを選択する {#choose-a-backend}

請求、アクセス権、割り当てを管理する場所に基づいてバックエンドを選択してください:

-   **Anthropic API:** すでに Anthropic アカウントを持っており、そこで Claude の使用量を管理している場合はこのバックエンドを使用します。Anthropic API キーで認証します。
-   **Google Cloud:** アプリケーションが Google Cloud 上で実行されている場合、または Google Cloud プロジェクトの IAM 権限、割り当て、請求によって Claude の使用量を管理したい場合はこのバックエンドを使用します。アプリケーションのデフォルト認証情報（ADC）で認証するため、個別の API キーを管理する必要はありません。

次の表は、各言語でバックエンドを選択する方法を示しています:

| 言語 | Anthropic API | Agent Platform |
| :--------- | :-------------------------------------------------- | :------------------------------------------------------------------- |
| Python | `AnthropicLlm` インスタンス | `Claude` インスタンス、または `claude-*` モデル文字列 |
| TypeScript | サポート対象外 | `Claude` インスタンス、または `Claude` 登録後の `claude-*` 文字列 |
| Go | `ClientConfig.Backend` を `BackendAnthropic` に設定 | `ClientConfig.Backend` を `BackendVertex` に設定 |
| Java | API キーを使用する `AnthropicClient` を指定した `Claude` | `VertexBackend` を使用する `AnthropicClient` を指定した `Claude` |
| Kotlin | `Claude(name, apiKey)` | `Claude(name, vertexCredentials)` |

!!! warning "Python のモデル文字列は Google Cloud Agent Platform を使用します"

    Python では、`model="claude-sonnet-4-6"` のような単体の `claude-*` モデル文字列は Agent Platform バックエンドにルーティングされ、Google Cloud プロジェクトの設定が必要になります。Python から Anthropic API を使用するには、文字列ではなく `AnthropicLlm` インスタンスを渡してください。

## Google Cloud 経由で接続する {#connect-through-agent-platform}

Google Cloud 経由で Claude を使用するには、Google Cloud 環境をセットアップします:

1.  Google Cloud プロジェクトの [Model Garden](https://console.cloud.google.com/vertex-ai/model-garden) で、使用する Claude モデルを有効にします。
2.  アプリケーションのデフォルト認証情報（ADC）を設定します:

    ```shell
    gcloud auth application-default login
    ```

3.  プロジェクトと、モデルが利用可能なリージョン（`global` や `us-east5` など）を設定します:

    ```shell
    export GOOGLE_CLOUD_PROJECT="your-project-id"
    export GOOGLE_CLOUD_LOCATION="global"
    ```

ADK を Google Cloud に接続する詳細については、[Google Cloud と Agent Platform に接続する](/ja/get-started/google-cloud/)を参照してください。

次の例では、Google Cloud 経由で Claude を呼び出すエージェントを作成します:

=== "Python"

    Claude モデル文字列をエージェントに渡します。ADK は `claude-*` 文字列を、`GOOGLE_CLOUD_PROJECT` と `GOOGLE_CLOUD_LOCATION` を読み取る `Claude` クラスにルーティングします。

    ```python
    from google.adk.agents import LlmAgent

    root_agent = LlmAgent(
        name="claude_agent",
        model="claude-sonnet-4-6",
        instruction="You are a helpful assistant.",
    )
    ```

    ADK Python v2.9.0 以降では、すべての `claude-*` モデル文字列が `Claude` にルーティングされます。それより前のバージョンで ADK がモデル文字列を認識しない場合は、`google.adk.models` から `Claude` をインポートしてインスタンスを渡してください（`model=Claude(model="claude-sonnet-4-6")`）。

=== "TypeScript"

    起動時に一度 `Claude` を登録しておくと、どのエージェントからでも名前で `claude-*` モデル文字列を参照できます:

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

    `Backend` を `BackendVertex` に設定します。`Project` と `Location` が空の場合、モデルは `GOOGLE_CLOUD_PROJECT` と `GOOGLE_CLOUD_LOCATION` を読み取り、認証情報として ADC を使用します。

    ```go
    llm, err := anthropicmodel.NewModel(ctx, "claude-sonnet-4-6", anthropicmodel.ClientConfig{
    	Backend: anthropicmodel.BackendVertex,
    })
    if err != nil {
    	log.Fatal(err)
    }
    ```

=== "Java"

    `VertexBackend` を使用して `AnthropicClient` を構成します:

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

    `Claude` コンストラクタに `VertexCredentials` を渡します。未設定の値は `GOOGLE_CLOUD_PROJECT`、`GOOGLE_CLOUD_LOCATION`、および ADC にフォールバックします。

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

## 拡張思考を構成する

<div class="language-support-tag">
   <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.34.0</span><span class="lst-go">Go v2.7.0</span><span class="lst-kotlin">Kotlin v1.4.0</span>
</div>

拡張思考（extended thinking）を使用すると、Claude は応答する前に問題を段階的に推論できるため、計画立案、分析、ツールの選択といったマルチステップのタスクに役立ちます。標準の思考設定の `thinking_budget` フィールドでこれを構成します:

| `thinking_budget` | 動作 |
| :--- | :--- |
| 負の値（`-1` など） | **アダプティブ思考（Adaptive thinking）。** Claude が各リクエストで推論する量を自動的に選択します。 |
| `0` | **思考なし。** Claude は拡張思考を行わずに応答します。 |
| 正の値 | **手動思考（Manual thinking）。** Claude は指定されたトークン数を上限として推論します。最小および最大の予算については、Anthropic の拡張思考ドキュメントを参照してください。 |

固定のトークン予算が必要な場合を除き、アダプティブ思考を使用してください。一部の新しい Claude モデルはアダプティブ思考のみを受け付けます。使用するモデルの詳細については、Anthropic の拡張思考ドキュメントを参照してください。思考設定を指定する場合は、必ず `thinking_budget` の値を設定する必要があります。

Claude が費やす推論の労力を制御するには、**effort** レベルを `low`、`medium`、`high`、`xhigh`、または `max` に設定します。Claude は標準の `thinking_level` 設定をサポートしていないため、代わりに effort を使用してください。思考または effort が有効な間、ADK は `temperature`、`top_p`、`top_k` を Claude に送信しません。

=== "Python"

    ADK Python v2.4.0 以降で利用可能な `AnthropicGenerateContentConfig` で `effort` を設定します:

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

    `AnthropicGenerateContentConfig` で `thinking_level` を設定すると検証エラーが発生します。通常の `types.GenerateContentConfig` で設定した場合、ADK はそれを無視して警告をログに記録します。

=== "Go"

    エージェントの `GenerateContentConfig` で思考予算を設定し、モデルの `ClientConfig` で effort レベルを設定します:

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

    エージェントの `GenerateContentConfig` で思考予算を設定し、`Claude` コンストラクタで effort レベルを設定します:

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

ADK はレスポンス内で Claude の推論を思考（thought）パートとして返し、Anthropic API の要件に従って、1 ターン内のツール呼び出し間で思考ブロックとその署名（signature）を保持します。

## 高度な活用

ADK は、プロンプト キャッシングや LiteLLM ライブラリを介したモデルへのアクセスなど、Anthropic モデルの高度な活用をサポートしています。

### プロンプトをキャッシュする

<div class="language-support-tag">
   <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v2.8.0</span><span class="lst-go">Go v2.7.0</span><span class="lst-kotlin">Kotlin v1.4.0</span>
</div>

長い指示や多数のツールを持つエージェントは、リクエストごとに同じプロンプト プレフィックスを送信します。Claude のプロンプト キャッシングはそのプレフィックスを保存して後続のリクエストで再利用するため、コストとレイテンシを削減できます。ADK はツール宣言、システム指示、および最新の会話コンテンツにキャッシュ ブレークポイントを配置します。

Anthropic はデフォルトの 5 分間のキャッシュ有効期間と、1 時間のキャッシュ有効期間をサポートしています。同じエージェントへのリクエスト間隔が通常 5 分を超える場合は、1 時間の有効期間を使用してください。詳細については、Anthropic の[プロンプト キャッシング](https://docs.claude.com/en/docs/build-with-claude/prompt-caching)のドキュメントを参照してください。

=== "Python"

    `App` に `ContextCacheConfig` を設定します。`ttl_seconds` に 3600 以上の値を指定すると 1 時間のキャッシュが選択されます。この設定の詳細については、[コンテキスト キャッシング](/ja/context/caching/)を参照してください。

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

    モデルの `ClientConfig` に `PromptCache` を設定します。1 時間のキャッシュを選択するには、`TTL` を `PromptCacheTTL1h` に設定します。

    ```go
    llm, err := anthropicmodel.NewModel(ctx, "claude-sonnet-4-6", anthropicmodel.ClientConfig{
    	PromptCache: &anthropicmodel.PromptCacheConfig{TTL: anthropicmodel.PromptCacheTTL5m},
    })
    ```

=== "Kotlin"

    `App` に `ContextCacheConfig` を設定します。`ttl` に 1 時間以上を指定すると 1 時間のキャッシュが選択されます。

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

### LiteLLM 経由で Claude を使用する

Python では、`anthropic/` モデル文字列を指定した `LiteLlm` コネクタ経由でも Claude に接続できます。アプリケーションですでに LiteLLM を介してモデルをルーティングしている場合は、この方法を使用してください。セットアップについては、[LiteLLM](/ja/agents/models/litellm/#anthropic-thinking-blocks) を参照してください。

## 構成オプション

Claude モデルクラスでは次のオプションを使用できます:

=== "Python"

    これらのオプションは `AnthropicLlm` と `Claude` の両方に適用されます。

    | オプション | 型 | デフォルト | 説明 |
    | :--- | :--- | :--- | :--- |
    | `model` | `str` | `"claude-sonnet-4-20250514"` (`AnthropicLlm`)、`"claude-3-5-sonnet-v2@20241022"` (`Claude`) | Claude モデル ID。 |
    | `max_tokens` | `int` | `8192` | リクエストに `max_output_tokens` が設定されていない場合の最大出力トークン数。 |
    | `client` | `AsyncAnthropic` または `AsyncAnthropicVertex` | `None` | 事前構成された Anthropic クライアント。`Claude` クラスには `AsyncAnthropicVertex` クライアントが必要です。 |

=== "TypeScript"

    | オプション | 型 | デフォルト | 説明 |
    | :--- | :--- | :--- | :--- |
    | `model` | `string` | `'claude-sonnet-4-6@default'` | Agent Platform 上の Claude モデル ID。 |
    | `maxTokens` | `number` | `8192` | リクエストに `maxOutputTokens` が設定されていない場合の最大出力トークン数。 |

=== "Go"

    主な `ClientConfig` フィールド:

    | オプション | 型 | デフォルト | 説明 |
    | :--- | :--- | :--- | :--- |
    | `Backend` | `Backend` | `BackendAnthropic` | サービング バックエンド: `BackendAnthropic` または `BackendVertex`。 |
    | `APIKey` | `string` | `ANTHROPIC_API_KEY` | `BackendAnthropic` 用の Anthropic API キー。 |
    | `Project` | `string` | `GOOGLE_CLOUD_PROJECT` | `BackendVertex` 用の Google Cloud プロジェクト。 |
    | `Location` | `string` | `GOOGLE_CLOUD_LOCATION` | `BackendVertex` 用の Google Cloud リージョン。 |
    | `MaxTokens` | `int` | `8192` | リクエストに `MaxOutputTokens` が設定されていない場合の最大出力トークン数。 |
    | `MaxRetries` | `*int` | `2` | 失敗したリクエストに対して Anthropic SDK が行う再試行回数。 |
    | `Effort` | `Effort` | モデルのデフォルト | 推論の労力（effort）レベル。 |
    | `PromptCache` | `*PromptCacheConfig` | `nil` | 設定するとプロンプト キャッシングが有効になります。 |

    全一覧については、[`anthropicmodel` パッケージ リファレンス](https://pkg.go.dev/google.golang.org/adk/v2/model/anthropicmodel)を参照してください。

=== "Java"

    | オプション | 型 | デフォルト | 説明 |
    | :--- | :--- | :--- | :--- |
    | `modelName` | `String` | 必須 | Claude モデル ID。 |
    | `anthropicClient` | `AnthropicClient` | 必須 | Anthropic API または `VertexBackend` 用に構成された Anthropic クライアント。 |
    | `maxTokens` | `int` | `8192` | 各リクエストの最大出力トークン数。 |

=== "Kotlin"

    | オプション | 型 | デフォルト | 説明 |
    | :--- | :--- | :--- | :--- |
    | `name` | `String` | 必須 | Claude モデル ID。 |
    | `apiKey` | `String?` | `ANTHROPIC_API_KEY` | Anthropic API キー。Anthropic API バックエンドを選択します。 |
    | `vertexCredentials` | `VertexCredentials` | なし | プロジェクト、ロケーション、および認証情報。Agent Platform バックエンドを選択します。 |
    | `client` | `AnthropicClient` | なし | `apiKey` または `vertexCredentials` の代わりに使用される、事前構成された Anthropic クライアント。 |
    | `maxTokens` | `Int` | `8192` | リクエストに指定がない場合の最大出力トークン数。 |
    | `effort` | `OutputConfig.Effort?` | `null` | 推論の労力（effort）レベル。 |

## 制限事項

-   **Live API:** Claude モデルは Live API を使用した ADK の双方向ストリーミングをサポートしていません。
-   **TypeScript:** `Claude` クラスはストリーミングを行わずに完全なレスポンスを返し、テキスト、関数呼び出し、関数レスポンスのパートのみを受け付けます。全一覧については、[Claude 統合ガイド](https://github.com/google/adk-js/blob/main/docs/guides/integrations/models/anthropic_llm/index.md#limitations)を参照してください。

## 次のステップ

-   [Agent Platform でホストされるモデル](/ja/agents/models/agent-platform/): Agent Platform にデプロイされた他のモデルを使用します。
-   [LiteLLM](/ja/agents/models/litellm/): 他のプロバイダーのモデルに接続します。
-   [コンテキスト キャッシング](/ja/context/caching/): キャッシュ設定の詳細を確認します。
