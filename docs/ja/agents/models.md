# ADKでさまざまなモデルを使用する

<div class="language-support-tag" title="Java ADKは現在、GeminiおよびAnthropicモデルをサポートしています。">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

Agent Development Kit (ADK) は柔軟性を考慮して設計されており、さまざまな大規模言語モデル (LLM) をエージェントに統合できます。Google Geminiモデルのセットアップは[基盤モデルのセットアップ](../get-started/installation.md)ガイドで説明されていますが、このページでは、Geminiを効果的に活用し、外部でホストされているモデルやローカルで実行されているモデルを含む、その他の一般的なモデルを統合する方法について詳しく説明します。

ADKは主に、モデル統合のために2つのメカニズムを使用します。

1. **直接文字列 / レジストリ:** Google Cloudと密接に統合されたモデル (Google AI StudioまたはVertex AI経由でアクセスするGeminiモデルなど) や、Vertex AIエンドポイントでホストされているモデルの場合。通常、モデル名またはエンドポイントリソース文字列を`LlmAgent`に直接提供します。ADKの内部レジストリは、この文字列を適切なバックエンドクライアントに解決し、多くの場合`google-genai`ライブラリを利用します。
2. **ラッパークラス:** Googleエコシステム外のモデルや、特定のクライアント構成が必要なモデル (ApigeeまたはLiteLLM経由でアクセスするモデルなど) との幅広い互換性のために。特定のラッパークラス (例: `ApigeeLlm`または`LiteLlm`) をインスタンス化し、このオブジェクトを`LlmAgent`の`model`パラメータとして渡します。

以下のセクションでは、必要に応じてこれらの方法を使用する方法について説明します。

## Google Geminiモデルの使用

このセクションでは、迅速な開発のためのGoogle AI Studio、またはエンタープライズアプリケーションのためのGoogle Cloud Vertex AIのいずれかを介して、GoogleのGeminiモデルで認証する方法について説明します。これは、ADK内でGoogleの主要モデルを使用する最も直接的な方法です。

**統合方法:** 以下のいずれかの方法で認証すると、モデルの識別子文字列を`LlmAgent`の`model`パラメータに直接渡すことができます。

!!! tip

    ADKがGeminiモデルに内部的に使用する`google-genai`ライブラリは、Google AI StudioまたはVertex AIのいずれかを介して接続できます。

    **音声/ビデオストリーミングのモデルサポート**

    ADKで音声/ビデオストリーミングを使用するには、Live APIをサポートするGeminiモデルを使用する必要があります。Gemini Live APIをサポートする**モデルID**は、次のドキュメントに記載されています。

    - [Google AI Studio: Gemini Live API](https://ai.google.dev/gemini-api/docs/models#live-api)
    - [Vertex AI: Gemini Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)

### Google AI Studio

これは最も簡単な方法であり、迅速に始めることをお勧めします。

*   **認証方法:** APIキー
*   **セットアップ:** 
    1.  **APIキーの取得:** [Google AI Studio](https://aistudio.google.com/apikey)からキーを取得します。
    2.  **環境変数の設定:** プロジェクトのルートディレクトリに`.env`ファイル (Python) または`.properties`ファイル (Java) を作成し、次の行を追加します。ADKは自動的にこのファイルを読み込みます。

        ```shell
        export GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
        export GOOGLE_GENAI_USE_VERTEXAI=FALSE
        ```

        (または)

        `Client`を介したモデル初期化中にこれらの変数を渡します (以下の例を参照)。

* **モデル:** [Google AI for Developersサイト](https://ai.google.dev/gemini-api/docs/models)で利用可能なすべてのモデルを見つけます。

### Google Cloud Vertex AI

スケーラブルで本番環境向けのユースケースには、Vertex AIが推奨されるプラットフォームです。Vertex AI上のGeminiは、エンタープライズグレードの機能、セキュリティ、コンプライアンス管理をサポートしています。開発環境とユースケースに基づいて、*以下の認証方法のいずれかを選択してください*。

**前提条件:** [Vertex AIが有効になっている](https://console.cloud.google.com/apis/enableflow;apiid=aiplatform.googleapis.com) Google Cloudプロジェクト。

### **方法A: ユーザー認証情報 (ローカル開発用)**

1.  **gcloud CLIのインストール:** 公式の[インストール手順](https://cloud.google.com/sdk/docs/install)に従います。
2.  **ADCを使用したログイン:** このコマンドはブラウザを開き、ローカル開発用のユーザーアカウントを認証します。
    ```bash
    gcloud auth application-default login
    ```
3.  **環境変数の設定:** 
    ```shell
    export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
    export GOOGLE_CLOUD_LOCATION="YOUR_VERTEX_AI_LOCATION" # 例: us-central1
    ```

    ライブラリにVertex AIを使用するように明示的に指示します。

    ```shell
    export GOOGLE_GENAI_USE_VERTEXAI=TRUE
    ```

4. **モデル:** [Vertex AIドキュメント](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models)で利用可能なモデルIDを見つけます。

### **方法B: Vertex AI Expressモード**
[Vertex AI Expressモード](https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview)は、迅速なプロトタイピングのための簡素化されたAPIキーベースのセットアップを提供します。

1.  **Expressモードに登録**してAPIキーを取得します。
2.  **環境変数の設定:** 
    ```shell
    export GOOGLE_API_KEY="PASTE_YOUR_EXPRESS_MODE_API_KEY_HERE"
    export GOOGLE_GENAI_USE_VERTEXAI=TRUE
    ```

### **方法C: サービスアカウント (本番環境および自動化用)**

デプロイされたアプリケーションの場合、サービスアカウントが標準的な方法です。

1.  [**サービスアカウントを作成**](https://cloud.google.com/iam/docs/service-accounts-create#console)し、`Vertex AI User`ロールを付与します。
2.  **アプリケーションに認証情報を提供する:** 
    *   **Google Cloudの場合:** Cloud Run、GKE、VM、またはその他のGoogle Cloudサービスでエージェントを実行している場合、環境は自動的にサービスアカウント認証情報を提供できます。キーファイルを作成する必要はありません。
    *   **その他の場合:** [サービスアカウントキーファイル](https://cloud.google.com/iam/docs/keys-create-delete#console)を作成し、環境変数でそれを指定します。
        ```bash
        export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/keyfile.json"
        ```
    キーファイルの代わりに、Workload Identityを使用してサービスアカウントを認証することもできますが、これはこのガイドの範囲外です。

**例:**

=== "Python"

    ```python
    from google.adk.agents import LlmAgent

    # --- 安定版Gemini Flashモデルを使用する例 ---
    agent_gemini_flash = LlmAgent(
        # 最新の安定版Flashモデル識別子を使用
        model="gemini-2.0-flash",
        name="gemini_flash_agent",
        instruction="あなたは高速で役立つGeminiアシスタントです。",
        # ... その他のエージェントパラメータ
    )

    # --- 強力なGemini Proモデルを使用する例 ---
    # 注意: 必要に応じて、特定のプレビューバージョンを含め、最新のモデル名については常に公式のGeminiドキュメントを確認してください。
    # プレビューモデルは、可用性や割り当て制限が異なる場合があります。
    agent_gemini_pro = LlmAgent(
        # 最新の一般提供版Proモデル識別子を使用
        model="gemini-2.5-pro-preview-03-25",
        name="gemini_pro_agent",
        instruction="あなたは強力で知識豊富なGeminiアシスタントです。",
        # ... その他のエージェントパラメータ
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
    // --- 例 #1: 環境変数を使用して安定版Gemini Flashモデルを使用する ---
    LlmAgent agentGeminiFlash = 
        LlmAgent.builder()
            // 最新の安定版Flashモデル識別子を使用
            .model("gemini-2.0-flash") // このモデルを使用するために環境変数を設定
            .name("gemini_flash_agent")
            .instruction("あなたは高速で役立つGeminiアシスタントです。")
            // ... その他のエージェントパラメータ
            .build();

    // --- 例 #2: モデルにAPIキーがある強力なGemini Proモデルを使用する ---
    LlmAgent agentGeminiPro = 
        LlmAgent.builder()
            // 最新の一般提供版Proモデル識別子を使用
            .model(new Gemini("gemini-2.5-pro-preview-03-25",
                Client.builder()
                    .vertexAI(false)
                    .apiKey("API_KEY") // APIキーを設定 (または) プロジェクト/ロケーション
                    .build()))
            // または、API_KEYを直接渡すこともできます
            // .model(new Gemini("gemini-2.5-pro-preview-03-25", "API_KEY"))
            .name("gemini_pro_agent")
            .instruction("あなたは強力で知識豊富なGeminiアシスタントです。")
            // ... その他のエージェントパラメータ
            .build();

    // 注意: 必要に応じて、特定のプレビューバージョンを含め、最新のモデル名については常に公式のGeminiドキュメントを確認してください。
    // プレビューモデルは、可用性や割り当て制限が異なる場合があります。
    ```

!!! warning "認証情報の保護"

    サービスアカウントの認証情報またはAPIキーは強力な認証情報です。決して公開しないでください。
    [Google Cloud Secret Manager](https://cloud.google.com/security/products/secret-manager)などの
    シークレットマネージャーを使用して、本番環境で安全に保存およびアクセスしてください。

### トラブルシューティング

#### エラーコード429 - RESOURCE_EXHAUSTED

このエラーは通常、リクエスト数がリクエストを処理するために割り当てられた容量を超過した場合に発生します。

これを軽減するには、次のいずれかを実行できます。

1. 使用しようとしているモデルの割り当て制限を増やすようリクエストします。

2. クライアントサイドのリトライを有効にします。リトライを使用すると、クライアントは遅延後にリクエストを自動的に再試行できるため、割り当ての問題が一時的な場合に役立ちます。

    リトライオプションを設定する方法は2つあります。

    **オプション1:** generate_content_configの一部としてエージェントでリトライオプションを設定します。

    このモデルアダプターを自分でインスタンス化する場合は、このオプションを使用します。

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

    **オプション2:** このモデルアダプターのリトライオプション。

    アダプターのインスタンスを自分でインスタンス化する場合は、このオプションを使用します。

    ```python
    from google.genai import types

    # ...

    agent = Agent(
        model=Gemini(
        retry_options=types.HttpRetryOptions(initial_delay=1, attempts=2),
        )
    )
    ```

## Anthropicモデルの使用

<div class="language-support-tag" title="Javaで利用可能です。PythonでのAnthropic API (非Vertex) の直接サポートはLiteLLM経由です。">
   <span class="lst-supported">ADKでサポート</span><span class="lst-java">Java v0.2.0</span>
</div>

ADKの`Claude`ラッパークラスを使用することで、AnthropicのClaudeモデルをAPIキー経由で直接、またはVertex AIバックエンドからJava ADKアプリケーションに統合できます。

Vertex AIバックエンドについては、[Vertex AI上のサードパーティモデル (例: Anthropic Claude)](#third-party-models-on-vertex-ai-eg-anthropic-claude)セクションを参照してください。

**前提条件:**

1.  **依存関係:** 
    *   **Anthropic SDKクラス (推移的):** Java ADKの`com.google.adk.models.Claude`ラッパーは、Anthropicの公式Java SDKのクラスに依存しています。これらは通常、**推移的依存関係**として含まれています。

2.  **Anthropic APIキー:** 
    *   AnthropicからAPIキーを取得します。シークレットマネージャーを使用してこのキーを安全に管理します。

**統合:**

目的のClaudeモデル名とAPIキーで構成された`AnthropicOkHttpClient`を提供して`com.google.adk.models.Claude`をインスタンス化します。その後、この`Claude`インスタンスを`LlmAgent`に渡します。

**例:**

```java
import com.anthropic.client.AnthropicClient;
import com.google.adk.agents.LlmAgent;
import com.google.adk.models.Claude;
import com.anthropic.client.okhttp.AnthropicOkHttpClient; // AnthropicのSDKから

public class DirectAnthropicAgent {

  private static final String CLAUDE_MODEL_ID = "claude-3-7-sonnet-latest"; // または任意のClaudeモデル

  public static LlmAgent createAgent() {

    // 機密性の高いキーは安全な設定から読み込むことをお勧めします
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
        .instruction("あなたはAnthropic Claudeを搭載した役立つAIアシスタントです。")
        // ... その他のLlmAgent構成
        .build();
  }

  public static void main(String[] args) {
    try {
      LlmAgent agent = createAgent();
      System.out.println("直接Anthropicエージェントの作成に成功しました: " + agent.name());
    } catch (IllegalStateException e) {
      System.err.println("エージェントの作成エラー: " + e.getMessage());
    }
  }
}
```

## AIモデル用Apigeeゲートウェイの使用

<div class="language-support-tag">
   <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.18.0</span>
</div>

[Apigee](https://docs.cloud.google.com/apigee/docs/api-platform/get-started/what-apigee) は、生成AIモデルのトラフィックを管理および制御する方法を変革する強力な[AIゲートウェイ](https://cloud.google.com/solutions/apigee-ai)として機能します。Apigeeプロキシを介してAIモデルのエンドポイント (Vertex AIやGemini APIなど) を公開することで、すぐにエンタープライズグレードの機能を利用できます。

- **モデルの安全性:** 脅威保護のためのModel Armorなどのセキュリティポリシーを実装します。

- **トラフィック管理:** コストを管理し、乱用を防ぐためにレート制限とトークン制限を適用します。

- **パフォーマンス:** セマンティックキャッシュと高度なモデルルーティングを使用して、応答時間と効率を向上させます。

- **モニタリングと可視性:** すべてのAIリクエストのきめ細かなモニタリング、分析、監査を行います。

**注:** `ApigeeLLM`ラッパーは現在、Vertex AIおよびGemini API (generateContent) で使用するように設計されています。他のモデルやインターフェースのサポートを継続的に拡張しています。

**統合方法:** Apigeeのガバナンスをエージェントのワークフローに統合するには、`ApigeeLlm`ラッパーをインスタンス化し、それを`LlmAgent`または他のエージェントタイプに渡すだけです。

**例:**

```python

from google.adk.agents import LlmAgent
from google.adk.models.apigee_llm import ApigeeLlm

# ApigeeLlmラッパーをインスタンス化
model = ApigeeLlm(
    # モデルへのApigeeルートを指定します。詳細については、ApigeeLlmのドキュメント (https://github.com/google/adk-python/tree/main/contributing/samples/hello_world_apigeellm) を確認してください。
    model="apigee/gemini-2.5-flash",
    # デプロイされたApigeeプロキシのプロキシURL (ベースパスを含む)
    proxy_url=f"https://{APIGEE_PROXY_URL}",
    # 必要な認証/認可ヘッダー (APIキーなど) を渡す
    custom_headers={"foo": "bar"}
)

# 設定済みのモデルラッパーをLlmAgentに渡す
agent = LlmAgent(
    model=model,
    name="my_governed_agent",
    instruction="あなたはGeminiを搭載し、Apigeeによって管理されている役立つアシスタントです。",
    # ... その他のエージェントパラメータ
)

```

この構成により、エージェントからのすべてのAPI呼び出しは最初にApigeeを介してルーティングされ、そこで必要なすべてのポリシー (セキュリティ、レート制限、ロギング) が実行された後、リクエストは基盤となるAIモデルのエンドポイントに安全に転送されます。

Apigeeプロキシを使用する完全なコード例については、[Hello World Apigee LLM](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world_apigeellm)を参照してください。

## LiteLLMを介したクラウドおよびプロプライエタリモデルの使用

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span>
</div>

OpenAI、Anthropic (非Vertex AI)、Cohereなどのプロバイダーから幅広いLLMにアクセスするために、ADKはLiteLLMライブラリを介した統合を提供します。

**統合方法:** `LiteLlm`ラッパークラスをインスタンス化し、それを`LlmAgent`の`model`パラメータに渡します。

**LiteLLMの概要:** [LiteLLM](https://docs.litellm.ai/)は、100以上のLLMに標準化されたOpenAI互換インターフェースを提供する翻訳レイヤーとして機能します。

**セットアップ:** 

1. **LiteLLMのインストール:** 
        ```shell
        pip install litellm
        ```
2. **プロバイダーAPIキーの設定:** 使用する特定のプロバイダーのAPIキーを環境変数として構成します。

    * *OpenAIの例:* 

        ```shell
        export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
        ```

    * *Anthropic (非Vertex AI) の例:* 

        ```shell
        export ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY"
        ```

    * *その他のプロバイダーの正しい環境変数名については、[LiteLLMプロバイダーのドキュメント](https://docs.litellm.ai/docs/providers)を参照してください。*

        **例:**

        ```python
        from google.adk.agents import LlmAgent
        from google.adk.models.lite_llm import LiteLlm

        # --- OpenAIのGPT-4oを使用するエージェントの例 ---
        # (OPENAI_API_KEYが必要)
        agent_openai = LlmAgent(
            model=LiteLlm(model="openai/gpt-4o"), # LiteLLMモデル文字列形式
            name="openai_agent",
            instruction="あなたはGPT-4oを搭載した役立つアシスタントです。",
            # ... その他のエージェントパラメータ
        )

        # --- AnthropicのClaude Haiku (非Vertex) を使用するエージェントの例 ---
        # (ANTHROPIC_API_KEYが必要)
        agent_claude_direct = LlmAgent(
            model=LiteLlm(model="anthropic/claude-3-haiku-20240307"),
            name="claude_direct_agent",
            instruction="あなたはClaude Haikuを搭載したアシスタントです。",
            # ... その他のエージェントパラメータ
        )
        ```

!!! warning "LiteLLMのWindowsエンコーディングに関する注意"

    WindowsでLiteLLMとともにADKエージェントを使用すると、`UnicodeDecodeError`が発生する場合があります。このエラーは、LiteLLMがUTF-8ではなくデフォルトのWindowsエンコーディング (`cp1252`) を使用してキャッシュファイルを読み取ろうとしたときに発生します。

    これを防ぐには、`PYTHONUTF8`環境変数を`1`に設定することをお勧めします。これにより、PythonはすべてのファイルI/OにUTF-8を使用するよう強制されます。

    **例 (PowerShell):**
    ```powershell
    # 現在のセッションに設定
    $env:PYTHONUTF8 = "1"

    # ユーザーに永続的に設定
    [System.Environment]::SetEnvironmentVariable('PYTHONUTF8', '1', [System.EnvironmentVariableTarget]::User)
    ```


## LiteLLMを介したオープンおよびローカルモデルの使用

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span>
</div>

最大限の制御、コスト削減、プライバシー、またはオフラインのユースケースのために、オープンソースモデルをローカルで実行したり、自己ホストしたり、LiteLLMを使用して統合したりできます。

**統合方法:** ローカルモデルサーバーを指すように構成された`LiteLlm`ラッパークラスをインスタンス化します。

### Ollama統合

[Ollama](https://ollama.com/)を使用すると、オープンソースモデルをローカルで簡単に実行できます。

#### モデルの選択

エージェントがツールに依存している場合は、[Ollamaウェブサイト](https://ollama.com/search?c=tools)からツールサポートのあるモデルを選択していることを確認してください。

信頼できる結果を得るには、ツールサポートのある適度なサイズのモデルを使用することをお勧めします。

モデルのツールサポートは、次のコマンドで確認できます。

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

機能の下に`tools`がリストされているはずです。

モデルが使用しているテンプレートを見て、必要に応じて調整することもできます。

```bash
ollama show --modelfile llama3.2 > model_file_to_modify
```

たとえば、上記のモデルのデフォルトテンプレートは、モデルが常に関数を呼び出す必要があることを本質的に示唆しています。これにより、関数呼び出しの無限ループが発生する可能性があります。

```
次の関数が与えられた場合、与えられたプロンプトに最も適切に回答する関数呼び出しのJSONを適切な引数とともに応答してください。

{"name": 関数名, "parameters": 引数名とその値の辞書} の形式で応答してください。変数は使用しないでください。
```

このようなプロンプトをより記述的なものに置き換えることで、無限のツール呼び出しループを防ぐことができます。

たとえば:

```
ユーザーのプロンプトと、以下にリストされている利用可能な関数を確認してください。
まず、これらの関数のいずれかを呼び出すことが最も適切な応答方法であるかを判断してください。プロンプトが特定の操作を要求したり、外部データの検索を必要としたり、関数によって処理される計算を伴う場合は、関数呼び出しが必要になる可能性が高いです。プロンプトが一般的な質問であったり、直接回答できる場合は、関数呼び出しは不要である可能性が高いです。

関数呼び出しが必要であると判断した場合: {"name": "function_name", "parameters": {"argument_name": "value"}} という形式のJSONオブジェクトのみで応答してください。パラメータの値が変数ではなく具体的なものであることを確認してください。

関数呼び出しが不要であると判断した場合: ユーザーのプロンプトにプレーンテキストで直接応答し、要求された回答または情報を提供してください。JSONは出力しないでください。
```

その後、次のコマンドを使用して新しいモデルを作成できます。

```bash
ollama create llama3.2-modified -f model_file_to_modify
```

#### ollama_chatプロバイダーの使用

LiteLLMラッパーを使用して、Ollamaモデルでエージェントを作成できます。

```py
root_agent = Agent(
    model=LiteLlm(model="ollama_chat/mistral-small3.1"),
    name="dice_agent",
    description=(
        "8面サイコロを振って素数をチェックできるハローワールドエージェント。"
    ),
    instruction="""
      サイコロを振り、その結果に関する質問に答えます。
    """,
    tools=[
        roll_die,
        check_prime,
    ],
)
```

**`ollama`ではなく`ollama_chat`プロバイダーを設定することが重要です。`ollama`を使用すると、無限ツール呼び出しループや以前のコンテキストの無視などの予期しない動作が発生する可能性があります。**

`api_base`はLiteLLM内で生成用に提供できますが、LiteLLMライブラリはv1.65.5以降の完了後、env変数に依存する他のAPIを呼び出しています。そのため、現時点では、`OLLAMA_API_BASE`環境変数をollamaサーバーを指すように設定することをお勧めします。

```bash
export OLLAMA_API_BASE="http://localhost:11434"
adk web
```

#### openaiプロバイダーの使用

代わりに`openai`をプロバイダー名として使用することもできます。ただし、この場合も`OLLAMA_API_BASE`の代わりに`OPENAI_API_BASE=http://localhost:11434/v1`と`OPENAI_API_KEY=anything`の環境変数を設定する必要があります。**APIベースの末尾に`/v1`が追加されていることに注意してください。**

```py
root_agent = Agent(
    model=LiteLlm(model="openai/mistral-small3.1"),
    name="dice_agent",
    description=(
        "8面サイコロを振って素数をチェックできるハローワールドエージェント。"
    ),
    instruction="""
      サイコロを振り、その結果に関する質問に答えます。
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

#### デバッグ

インポート直後のエージェントコードに以下を追加することで、Ollamaサーバーに送信されたリクエストを確認できます。

```py
import litellm
litellm._turn_on_debug()
```

次のような行を探してください。

```bash
Request Sent from LiteLLM:
curl -X POST \
http://localhost:11434/api/chat \
-d '{'model': 'mistral-small3.1', 'messages': [{'role': 'system', 'content': ...
```

### 自己ホスト型エンドポイント (例: vLLM)

<div class="language-support-tag">
   <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span>
</div>

[vLLM](https://github.com/vllm-project/vllm)のようなツールを使用すると、モデルを効率的にホストし、多くの場合OpenAI互換APIエンドポイントを公開できます。

**セットアップ:** 

1. **モデルのデプロイ:** vLLM (または同様のツール) を使用して選択したモデルをデプロイします。APIベースURLをメモしておきます (例: `https://your-vllm-endpoint.run.app/v1`)。
    * *ADKツールにとって重要:* デプロイするときは、サービングツールがOpenAI互換のツール/関数呼び出しをサポートし、有効にしていることを確認してください。vLLMの場合、これはモデルに応じて`--enable-auto-tool-choice`フラグと、場合によっては特定の`--tool-call-parser`を伴う可能性があります。ツール使用に関するvLLMのドキュメントを参照してください。
2. **認証:** エンドポイントが認証をどのように処理するかを決定します (例: APIキー、ベアラートークン)。

    **統合例:**

    ```python
    import subprocess
    from google.adk.agents import LlmAgent
    from google.adk.models.lite_llm import LiteLlm

    # --- vLLMエンドポイントでホストされているモデルを使用するエージェントの例 ---

    # vLLMデプロイによって提供されるエンドポイントURL
    api_base_url = "https://your-vllm-endpoint.run.app/v1"

    # vLLMエンドポイント構成で認識されるモデル名
    model_name_at_endpoint = "hosted_vllm/google/gemma-3-4b-it" # vllm_test.pyの例

    # 認証 (例: Cloud Runデプロイ用のgcloud IDトークンを使用)
    # エンドポイントのセキュリティに基づいてこれを調整
    try:
        gcloud_token = subprocess.check_output(
            ["gcloud", "auth", "print-identity-token", "-q"]
        ).decode().strip()
        auth_headers = {"Authorization": f"Bearer {gcloud_token}"}
    except Exception as e:
        print(f"警告: gcloudトークンを取得できませんでした - {e}。エンドポイントが保護されていないか、別の認証が必要な場合があります。")
        auth_headers = None # または適切にエラーを処理

    agent_vllm = LlmAgent(
        model=LiteLlm(
            model=model_name_at_endpoint,
            api_base=api_base_url,
            # 必要に応じて認証ヘッダーを渡す
            extra_headers=auth_headers
            # または、エンドポイントがAPIキーを使用する場合:
            # api_key="YOUR_ENDPOINT_API_KEY"
        ),
        name="vllm_agent",
        instruction="あなたは自己ホスト型vLLMエンドポイントで実行されている役立つアシスタントです。",
        # ... その他のエージェントパラメータ
    )
    ```

## Vertex AIでホストおよびチューニングされたモデルの使用

Google CloudのMLOpsエコシステムとのエンタープライズグレードのスケーラビリティ、信頼性、および統合のために、Vertex AIエンドポイントにデプロイされたモデルを使用できます。これには、Model Gardenのモデルまたは独自のファインチューニングされたモデルが含まれます。

**統合方法:** 完全なVertex AIエンドポイントリソース文字列 (`projects/PROJECT_ID/locations/LOCATION/endpoints/ENDPOINT_ID`) を`LlmAgent`の`model`パラメータに直接渡します。

**Vertex AIセットアップ (統合):** 

環境がVertex AI用に構成されていることを確認してください。

1. **認証:** アプリケーションデフォルト認証情報 (ADC) を使用します。

    ```shell
    gcloud auth application-default login
    ```

2. **環境変数:** プロジェクトとロケーションを設定します。

    ```shell
    export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
    export GOOGLE_CLOUD_LOCATION="YOUR_VERTEX_AI_LOCATION" # 例: us-central1
    ```

3. **Vertexバックエンドの有効化:** 重要なのは、`google-genai`ライブラリがVertex AIをターゲットにしていることを確認することです。

    ```shell
    export GOOGLE_GENAI_USE_VERTEXAI=TRUE
    ```

### Model Gardenのデプロイ

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.2.0</span>
</div>

[Vertex AI Model Garden](https://console.cloud.google.com/vertex-ai/model-garden)からさまざまなオープンおよびプロプライエタリモデルをエンドポイントにデプロイできます。

**例:**

```python
from google.adk.agents import LlmAgent
from google.genai import types # 設定オブジェクト用

# --- Model GardenからデプロイされたLlama 3モデルを使用するエージェントの例 ---

# 実際のVertex AIエンドポイントリソース名に置き換える
lama3_endpoint = "projects/YOUR_PROJECT_ID/locations/us-central1/endpoints/YOUR_LLAMA3_ENDPOINT_ID"

agent_llama3_vertex = LlmAgent(
    model=llama3_endpoint,
    name="llama3_vertex_agent",
    instruction="あなたはVertex AIでホストされているLlama 3ベースの役立つアシスタントです。",
    generate_content_config=types.GenerateContentConfig(max_output_tokens=2048),
    # ... その他のエージェントパラメータ
)
```

### ファインチューニングされたモデルのエンドポイント

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.2.0</span>
</div>

ファインチューニングされたモデル (GeminiまたはVertex AIでサポートされているその他のアーキテクチャに基づく) をデプロイすると、直接使用できるエンドポイントが生成されます。

**例:**

```python
from google.adk.agents import LlmAgent

# --- ファインチューニングされたGeminiモデルのエンドポイントを使用するエージェントの例 ---

# ファインチューニングされたモデルのエンドポイントリソース名に置き換える
finetuned_gemini_endpoint = "projects/YOUR_PROJECT_ID/locations/us-central1/endpoints/YOUR_FINETUNED_ENDPOINT_ID"

agent_finetuned_gemini = LlmAgent(
    model=finetuned_gemini_endpoint,
    name="finetuned_gemini_agent",
    instruction="あなたは特定のデータでトレーニングされた専門アシスタントです。",
    # ... その他のエージェントパラメータ
)
```

### Vertex AI上のサードパーティモデル (例: Anthropic Claude)

Anthropicのような一部のプロバイダーは、Vertex AIを介して直接モデルを提供しています。

=== "Python"

    **統合方法:** 直接モデル文字列 (例: `"claude-3-sonnet@20240229"`) を使用しますが、ADK内での*手動登録が必要です*。

    **登録の理由:** ADKのレジストリは、`gemini-*`文字列と標準のVertex AIエンドポイント文字列 (`projects/.../endpoints/...`) を自動的に認識し、`google-genai`ライブラリを介してルーティングします。Vertex AIを介して直接使用される他のモデルタイプ (Claudeなど) の場合、ADKレジストリに、Vertex AIバックエンドでそのモデル識別子文字列を処理する方法を知っている特定のラッパークラス (この場合は`Claude`) を明示的に伝える必要があります。

    **セットアップ:** 

    1. **Vertex AI環境:** 統合されたVertex AIセットアップ (ADC、環境変数、`GOOGLE_GENAI_USE_VERTEXAI=TRUE`) が完了していることを確認してください。

    2. **プロバイダーライブラリのインストール:** Vertex AI用に構成された必要なクライアントライブラリをインストールします。

        ```shell
        pip install "anthropic[vertex]"
        ```

    3. **モデルクラスの登録:** Claudeモデル文字列を使用してエージェントを作成する*前に*、アプリケーションの起動時にこのコードを追加します。

        ```python
        # LlmAgentでVertex AI経由でClaudeモデル文字列を直接使用するために必要です
        from google.adk.models.anthropic_llm import Claude
        from google.adk.models.registry import LLMRegistry

        LLMRegistry.register(Claude)
        ```

       **例:**

       ```python
       from google.adk.agents import LlmAgent
       from google.adk.models.anthropic_llm import Claude # 登録に必要
       from google.adk.models.registry import LLMRegistry # 登録に必要
       from google.genai import types

       # --- Claudeクラスの登録 (起動時に一度だけ実行) ---
       LLMRegistry.register(Claude)

       # --- Vertex AI上のClaude 3 Sonnetを使用するエージェントの例 ---

       # Vertex AI上のClaude 3 Sonnetの標準モデル名
       claude_model_vertexai = "claude-3-sonnet@20240229"

       agent_claude_vertexai = LlmAgent(
           model=claude_model_vertexai, # 登録後に直接文字列を渡す
           name="claude_vertexai_agent",
           instruction="あなたはVertex AI上のClaude 3 Sonnetを搭載したアシスタントです。",
           generate_content_config=types.GenerateContentConfig(max_output_tokens=4096),
           # ... その他のエージェントパラメータ
       )
       ```

=== "Java"

    **統合方法:** プロバイダー固有のモデルクラス (例: `com.google.adk.models.Claude`) を直接インスタンス化し、Vertex AIバックエンドで構成します。

    **直接インスタンス化の理由:** Java ADKの`LlmRegistry`は、デフォルトで主にGeminiモデルを処理します。Vertex AI上のClaudeのようなサードパーティモデルの場合、ADKのラッパークラス (例: `Claude`) のインスタンスを`LlmAgent`に直接提供します。このラッパークラスは、Vertex AI用に構成された特定のクライアントライブラリを介してモデルと対話する役割を担います。

    **セットアップ:** 

    1. **Vertex AI環境:** 
        *   Google Cloudプロジェクトとリージョンが正しく設定されていることを確認してください。
        *   **Application Default Credentials (ADC):** ADCが環境で正しく構成されていることを確認してください。これは通常、`gcloud auth application-default login`を実行することによって行われます。Javaクライアントライブラリは、これらの認証情報を使用してVertex AIで認証します。詳細なセットアップについては、[Google Cloud JavaドキュメントのADC](https://cloud.google.com/java/docs/reference/google-auth-library/latest/com.google.auth.oauth2.GoogleCredentials#com_google_auth_oauth2_GoogleCredentials_getApplicationDefault__)を参照してください。

    2. **プロバイダーライブラリの依存関係:** 
        *   **サードパーティクライアントライブラリ (多くの場合推移的):** ADKコアライブラリには、Vertex AI上の一般的なサードパーティモデル (Anthropicに必要なクラスなど) の必要なクライアントライブラリが**推移的依存関係**として含まれていることがよくあります。これは、`pom.xml`または`build.gradle`にAnthropic Vertex SDKの別の依存関係を明示的に追加する必要がないことを意味します。

    3. **モデルのインスタンス化と構成:** 
        `LlmAgent`を作成するときに、`Claude`クラス (または別のプロバイダーの同等のクラス) をインスタンス化し、その`VertexBackend`を構成します。

    **例:**

    ```java
    import com.anthropic.client.AnthropicClient;
    import com.anthropic.client.okhttp.AnthropicOkHttpClient;
    import com.anthropic.vertex.backends.VertexBackend;
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.models.Claude; // Claude用ADKラッパー
    import com.google.auth.oauth2.GoogleCredentials;
    import java.io.IOException;

    // ... その他のインポート

    public class ClaudeVertexAiAgent {

        public static LlmAgent createAgent() throws IOException {
            // Vertex AI上のClaude 3 Sonnetのモデル名 (またはその他のバージョン)
            String claudeModelVertexAi = "claude-3-7-sonnet"; // または他のClaudeモデル

            // VertexBackendでAnthropicOkHttpClientを構成する
            AnthropicClient anthropicClient = AnthropicOkHttpClient.builder()
                .backend(
                    VertexBackend.builder()
                        .region("us-east5") // Vertex AIのリージョンを指定
                        .project("your-gcp-project-id") // GCPプロジェクトIDを指定
                        .googleCredentials(GoogleCredentials.getApplicationDefault())
                        .build())
                .build();

            // ADK ClaudeラッパーでLlmAgentをインスタンス化する
            LlmAgent agentClaudeVertexAi = LlmAgent.builder()
                .model(new Claude(claudeModelVertexAi, anthropicClient)) // Claudeインスタンスを渡す
                .name("claude_vertexai_agent")
                .instruction("あなたはVertex AI上のClaude 3 Sonnetを搭載したアシスタントです。")
                // .generateContentConfig(...) // オプション: 必要に応じて生成設定を追加
                // ... その他のエージェントパラメータ
                .build();

            return agentClaudeVertexAi;
        }

        public static void main(String[] args) {
            try {
                LlmAgent agent = createAgent();
                System.out.println("エージェントの作成に成功しました: " + agent.name());
                // ここで通常、RunnerとSessionを設定してエージェントと対話します
            } catch (IOException e) {
                System.err.println("エージェントの作成に失敗しました: " + e.getMessage());
                e.printStackTrace();
            }
        }
    }
    ```