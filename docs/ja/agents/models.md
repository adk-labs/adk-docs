# ADKで様々なモデルを使用する

<div class="language-support-tag" title="Java ADKは現在、GeminiおよびAnthropicモデルをサポートしています。">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

Agent Development Kit（ADK）は柔軟性を重視して設計されており、様々な大規模言語モデル（LLM）をエージェントに統合できます。Google Geminiモデルの設定については[基盤モデルの設定](../get-started/installation.md)ガイドで説明していますが、このページでは、Geminiを効果的に活用し、外部でホストされているモデルやローカルで実行されているモデルなど、他の人気のあるモデルを統合する方法について詳しく説明します。

ADKは、主に2つのメカニズムを使用してモデルを統合します。

1.  **直接的な文字列 / レジストリ:** Google Cloudと緊密に統合されたモデル（Google AI StudioやVertex AIを介してアクセスするGeminiモデルなど）や、Vertex AIエンドポイントでホストされているモデル向けです。通常、モデル名またはエンドポイントのリソース文字列を`LlmAgent`に直接提供します。ADKの内部レジストリがこの文字列を適切なバックエンドクライアントに解決し、しばしば`google-genai`ライブラリを利用します。
2.  **ラッパークラス:** 特にGoogleエコシステム外のモデルや、特定のクライアント設定が必要なモデル（ApigeeやLiteLLMを介してアクセスするモデルなど）との幅広い互換性のために使用します。特定のラッパークラス（例：`ApigeeLlm`や`LiteLlm`）をインスタンス化し、このオブジェクトを`LlmAgent`の`model`パラメータとして渡します。

以下のセクションでは、ニーズに応じてこれらの方法を使用するためのガイドを提供します。

## Google Geminiモデルの使用

このセクションでは、迅速な開発のためのGoogle AI Studio、またはエンタープライズアプリケーションのためのGoogle Cloud Vertex AIを介したGoogleのGeminiモデルでの認証方法について説明します。これは、ADK内でGoogleの主力モデルを使用する最も直接的な方法です。

**統合方法:** 以下のいずれかの方法で認証が完了したら、モデルの識別子文字列を`LlmAgent`の`model`パラメータに直接渡すことができます。

!!!tip

    ADKが内部でGeminiモデルに使用する`google-genai`ライブラリは、Google AI StudioまたはVertex AIのいずれかを介して接続できます。

    **音声/動画ストリーミングのモデルサポート**

    ADKで音声/動画ストリーミングを使用するには、Live APIをサポートするGeminiモデルを使用する必要があります。Gemini Live APIをサポートする**モデルID**は、以下のドキュメントで確認できます。

    - [Google AI Studio: Gemini Live API](https://ai.google.dev/gemini-api/docs/models#live-api)
    - [Vertex AI: Gemini Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)

### Google AI Studio

これは最も簡単な方法であり、迅速に開始するために推奨されます。

*   **認証方法:** APIキー
*   **設定:**
    1.  **APIキーの取得:** [Google AI Studio](https://aistudio.google.com/apikey)からキーを取得します。
    2.  **環境変数の設定:** プロジェクトのルートディレクトリに`.env`ファイル（Python）または`.properties`（Java）を作成し、以下の行を追加します。ADKがこのファイルを自動的に読み込みます。

        ```shell
        export GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
        export GOOGLE_GENAI_USE_VERTEXAI=FALSE
        ```

        （または）
        
        モデルの初期化時に`Client`を介してこれらの変数を渡します（以下の例を参照）。

* **モデル:** 利用可能なすべてのモデルは[Google AI for Developersサイト](https://ai.google.dev/gemini-api/docs/models)で確認してください。

### Google Cloud Vertex AI

スケーラブルで本番指向のユースケースには、Vertex AIが推奨されるプラットフォームです。Vertex AI上のGeminiは、エンタープライズグレードの機能、セキュリティ、およびコンプライアンス管理をサポートします。開発環境とユースケースに基づいて、*以下のいずれかの方法を選択して認証*してください。

**前提条件:** [Vertex AIが有効になっている](https://console.cloud.google.com/apis/enableflow;apiid=aiplatform.googleapis.com)Google Cloudプロジェクト。

### **方法A: ユーザー認証情報（ローカル開発用）**

1.  **gcloud CLIのインストール:** 公式の[インストール手順](https://cloud.google.com/sdk/docs/install)に従ってください。
2.  **ADCを使用したログイン:** このコマンドはブラウザを開き、ローカル開発用のユーザーアカウントを認証します。
    ```bash
    gcloud auth application-default login
    ```
3.  **環境変数の設定:**
    ```shell
    export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
    export GOOGLE_CLOUD_LOCATION="YOUR_VERTEX_AI_LOCATION" # 例: us-central1
    ```     
    
    ライブラリにVertex AIを使用することを明示的に伝えます。

    ```shell
    export GOOGLE_GENAI_USE_VERTEXAI=TRUE
    ```

4. **モデル:** 利用可能なモデルIDは[Vertex AIドキュメント](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models)で確認してください。

### **方法B: Vertex AI Expressモード**
[Vertex AI Expressモード](https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview)は、迅速なプロトタイピングのためにAPIキーベースの簡素化された設定を提供します。

1.  **Expressモードにサインアップ**してAPIキーを取得します。
2.  **環境変数の設定:**
    ```shell
    export GOOGLE_API_KEY="PASTE_YOUR_EXPRESS_MODE_API_KEY_HERE"
    export GOOGLE_GENAI_USE_VERTEXAI=TRUE
    ```

### **方法C: サービスアカウント（本番環境＆自動化用）**

デプロイされたアプリケーションでは、サービスアカウントが標準的な方法です。

1.  [**サービスアカウントを作成**](https://cloud.google.com/iam/docs/service-accounts-create#console)し、`Vertex AI ユーザー`ロールを付与します。
2.  **アプリケーションに認証情報を提供:**
    *   **Google Cloud上:** Cloud Run、GKE、VM、その他のGoogle Cloudサービスでエージェントを実行している場合、環境が自動的にサービスアカウントの認証情報を提供できます。キーファイルを作成する必要はありません。
    *   **その他:** [サービスアカウントのキーファイルを作成](https://cloud.google.com/iam/docs/keys-create-delete#console)し、環境変数でそのパスを指し示します。
        ```bash
        export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/keyfile.json"
        ```
    キーファイルの代わりにWorkload Identityを使用してサービスアカウントを認証することもできますが、これはこのガイドの範囲外です。

**例:**

=== "Python"

    ```python
    from google.adk.agents import LlmAgent
    
    # --- 安定版のGemini Flashモデルを使用した例 ---
    agent_gemini_flash = LlmAgent(
        # 最新の安定版Flashモデル識別子を使用
        model="gemini-2.0-flash",
        name="gemini_flash_agent",
        instruction="あなたは高速で役立つGeminiアシスタントです。",
        # ... その他のエージェントパラメータ
    )
    
    # --- 強力なGemini Proモデルを使用した例 ---
    # 注: 必要に応じて特定のプレビュー版を含む最新のモデル名については、
    # 常に公式のGeminiドキュメントを確認してください。プレビューモデルは
    # 利用可能性やクォータ制限が異なる場合があります。
    agent_gemini_pro = LlmAgent(
        # 最新の一般提供Proモデル識別子を使用
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
    // --- 例1: 環境変数を使用して安定版のGemini Flashモデルを使用 ---
    LlmAgent agentGeminiFlash =
        LlmAgent.builder()
            // 最新の安定版Flashモデル識別子を使用
            .model("gemini-2.0-flash") // このモデルを使用するために環境変数を設定
            .name("gemini_flash_agent")
            .instruction("あなたは高速で役立つGeminiアシスタントです。")
            // ... その他のエージェントパラメータ
            .build();

    // --- 例2: モデルにAPIキーを含めて強力なGemini Proモデルを使用 ---
    LlmAgent agentGeminiPro =
        LlmAgent.builder()
            // 最新の一般提供Proモデル識別子を使用
            .model(new Gemini("gemini-2.5-pro-preview-03-25",
                Client.builder()
                    .vertexAI(false)
                    .apiKey("API_KEY") // APIキー（または）プロジェクト/ロケーションを設定
                    .build()))
            // または、API_KEYを直接渡すこともできます
            // .model(new Gemini("gemini-2.5-pro-preview-03-25", "API_KEY"))
            .name("gemini_pro_agent")
            .instruction("あなたは強力で知識豊富なGeminiアシスタントです。")
            // ... その他のエージェントパラメータ
            .build();

    // 注: 必要に応じて特定のプレビュー版を含む最新のモデル名については、
    // 常に公式のGeminiドキュメントを確認してください。プレビューモデルは
    // 利用可能性やクォータ制限が異なる場合があります。
    ```

!!!warning "認証情報を安全に保つ"
    サービスアカウントの認証情報やAPIキーは強力な資格情報です。決して公に公開しないでください。本番環境では[Google Secret Manager](https://cloud.google.com/secret-manager)のようなシークレットマネージャーを使用して、安全に保存・アクセスしてください。

## Anthropicモデルの使用

<div class="language-support-tag" title="Javaで利用可能。直接のAnthropic API（Vertex経由でない）に対するPythonサポートはLiteLLM経由です。">
   <span class="lst-supported">ADKでサポート</span><span class="lst-java">Java v0.2.0</span>
</div>

ADKの`Claude`ラッパークラスを使用することで、APIキーを直接使用するか、Vertex AIバックエンドからAnthropicのClaudeモデルをJava ADKアプリケーションに統合できます。

Vertex AIバックエンドについては、[Vertex AI上のサードパーティモデル](#third-party-models-on-vertex-ai-eg-anthropic-claude)セクションを参照してください。

**前提条件:**

1.  **依存関係:**
    *   **Anthropic SDKクラス（推移的）:** Java ADKの`com.google.adk.models.Claude`ラッパーは、Anthropicの公式Java SDKのクラスに依存しています。これらは通常、**推移的な依存関係**として含まれます。

2.  **Anthropic APIキー:**
    *   AnthropicからAPIキーを取得します。シークレットマネージャーを使用してこのキーを安全に管理してください。

**統合:**

希望するClaudeモデル名とAPIキーで設定された`AnthropicOkHttpClient`を提供して`com.google.adk.models.Claude`をインスタンス化します。次に、この`Claude`インスタンスを`LlmAgent`に渡します。

**例:**

```java
import com.anthropic.client.AnthropicClient;
import com.google.adk.agents.LlmAgent;
import com.google.adk.models.Claude;
import com.anthropic.client.okhttp.AnthropicOkHttpClient; // AnthropicのSDKから

public class DirectAnthropicAgent {
  
  private static final String CLAUDE_MODEL_ID = "claude-3-7-sonnet-latest"; // またはお好みのClaudeモデル

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
        // ... その他のLlmAgent設定
        .build();
  }

  public static void main(String[] args) {
    try {
      LlmAgent agent = createAgent();
      System.out.println("直接Anthropicエージェントの作成に成功しました: " + agent.name());
    } catch (IllegalStateException e) {
      System.err.println("エージェントの作成中にエラーが発生しました: " + e.getMessage());
    }
  }
}
```

## AIモデル向けApigeeゲートウェイの使用

<div class="language-support-tag">
   <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.18.0</span>
</div>

[Apigee](https://docs.cloud.google.com/apigee/docs/api-platform/get-started/what-apigee)は強力な[AIゲートウェイ](https://cloud.google.com/solutions/apigee-ai)として機能し、生成AIモデルのトラフィックを管理および統制する方法を変革します。Apigeeプロキシを介してAIモデルのエンドポイント（Vertex AIやGemini APIなど）を公開することで、即座にエンタープライズグレードの機能を利用できます。

- **モデルの安全性:** 脅威保護のためのModel Armorなどのセキュリティポリシーを実装します。

- **トラフィックガバナンス:** レート制限やトークン制限を実施して、コストを管理し、乱用を防ぎます。

- **パフォーマンス:** セマンティックキャッシングや高度なモデルルーティングを使用して、応答時間と効率を向上させます。

- **モニタリングと可視性:** すべてのAIリクエストに対して、きめ細かいモニタリング、分析、監査を行います。

**注:** `ApigeeLLM`ラッパーは現在、Vertex AIおよびGemini API（generateContent）での使用を想定して設計されています。他のモデルやインターフェースへのサポートは継続的に拡大しています。

**統合方法:** Apigeeのガバナンスをエージェントのワークフローに統合するには、`ApigeeLlm`ラッパーをインスタンス化し、それを`LlmAgent`または他のエージェントタイプに渡すだけです。

**例:**

```python
from google.adk.agents import LlmAgent
from google.adk.models.apigee_llm import ApigeeLlm

# ApigeeLlmラッパーをインスタンス化
model = ApigeeLlm(
    # モデルへのApigeeルートを指定。詳細はApigeeLlmドキュメントを参照(https://github.com/google/adk-python/tree/main/contributing/samples/hello_world_apigeellm)。
    model="apigee/gemini-2.5-flash", 
    # デプロイされたApigeeプロキシのベースパスを含むプロキシURL
    proxy_url=f"https://{APIGEE_PROXY_URL}", 
    # 必要な認証/認可ヘッダーを渡す（APIキーなど）
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

この設定により、エージェントからのすべてのAPI呼び出しは最初にApigeeを経由し、そこで必要なすべてのポリシー（セキュリティ、レート制限、ロギング）が実行された後、リクエストは安全に基盤となるAIモデルのエンドポイントに転送されます。

Apigeeプロキシを使用した完全なコード例については、[Hello World Apigee LLM](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world_apigeellm)を参照してください。

## LiteLLMを介したクラウド＆プロプライエタリモデルの使用

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span>
</div>

OpenAI、Anthropic（Vertex AI経由でない）、Cohereなどのプロバイダーからの広範なLLMにアクセスするために、ADKはLiteLLMライブラリを介した統合を提供します。

**統合方法:** `LiteLlm`ラッパークラスをインスタンス化し、それを`LlmAgent`の`model`パラメータに渡します。

**LiteLLM概要:** [LiteLLM](https://docs.litellm.ai/)は変換レイヤーとして機能し、100以上のLLMに対して標準化されたOpenAI互換のインターフェースを提供します。

**設定:**

1. **LiteLLMのインストール:**
        ```shell
        pip install litellm
        ```
2. **プロバイダーAPIキーの設定:** 使用する特定のプロバイダーのAPIキーを環境変数として設定します。

    * *OpenAIの例:*

        ```shell
        export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
        ```

    * *Anthropic（Vertex AI経由でない）の例:*

        ```shell
        export ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY"
        ```

    * *他のプロバイダーの正しい環境変数名については、[LiteLLMプロバイダードキュメント](https://docs.litellm.ai/docs/providers)を参照してください。*

        **例:**

        ```python
        from google.adk.agents import LlmAgent
        from google.adk.models.lite_llm import LiteLlm

        # --- OpenAIのGPT-4oを使用したエージェントの例 ---
        # (OPENAI_API_KEYが必要)
        agent_openai = LlmAgent(
            model=LiteLlm(model="openai/gpt-4o"), # LiteLLMモデル文字列形式
            name="openai_agent",
            instruction="あなたはGPT-4oを搭載した役立つアシスタントです。",
            # ... その他のエージェントパラメータ
        )

        # --- AnthropicのClaude Haiku（Vertex経由でない）を使用したエージェントの例 ---
        # (ANTHROPIC_API_KEYが必要)
        agent_claude_direct = LlmAgent(
            model=LiteLlm(model="anthropic/claude-3-haiku-20240307"),
            name="claude_direct_agent",
            instruction="あなたはClaude Haikuを搭載したアシスタントです。",
            # ... その他のエージェントパラメータ
        )
        ```

!!!warning "LiteLLMに関するWindowsのエンコーディング注意"

    WindowsでLiteLLMと共にADKエージェントを使用すると、`UnicodeDecodeError`が発生することがあります。このエラーは、LiteLLMがUTF-8ではなく、Windowsのデフォルトエンコーディング（`cp1252`）を使用してキャッシュされたファイルを読み込もうとすることで発生します。

    これを防ぐために、`PYTHONUTF8`環境変数を`1`に設定することをお勧めします。これにより、PythonはすべてのファイルI/OにUTF-8を強制的に使用するようになります。

    **例 (PowerShell):**
    ```powershell
    # 現在のセッションで設定
    $env:PYTHONUTF8 = "1"

    # ユーザーに対して永続的に設定
    [System.Environment]::SetEnvironmentVariable('PYTHONUTF8', '1', [System.EnvironmentVariableTarget]::User)
    ```

## LiteLLMを介したオープン＆ローカルモデルの使用

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span>
</div>

最大限の制御、コスト削減、プライバシー、またはオフラインでのユースケースのために、オープンソースモデルをローカルで実行したり、自己ホストしたりして、LiteLLMを使用して統合することができます。

**統合方法:** ローカルモデルサーバーを指すように設定された`LiteLlm`ラッパークラスをインスタンス化します。

### Ollamaとの統合

[Ollama](https://ollama.com/)を使用すると、オープンソースモデルをローカルで簡単に実行できます。

#### モデルの選択

エージェントがツールに依存している場合は、[Ollamaのウェブサイト](https://ollama.com/search?c=tools)からツールサポートのあるモデルを選択してください。

信頼性の高い結果を得るためには、ツールサポートのある十分なサイズのモデルを使用することをお勧めします。

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

`Capabilities`の下に`tools`がリストされているはずです。

モデルが使用しているテンプレートを確認し、必要に応じて調整することもできます。

```bash
ollama show --modelfile llama3.2 > model_file_to_modify
```

たとえば、上記のモデルのデフォルトテンプレートは、モデルが常にいずれかの関数を呼び出すべきであることを暗に示唆しています。これにより、関数呼び出しの無限ループが発生する可能性があります。

```
以下の関数を考慮し、与えられたプロンプトに最もよく答える関数呼び出しとその適切な引数をJSONで応答してください。

{"name": 関数名, "parameters": 引数名とその値の辞書}の形式で応答してください。変数は使用しないでください。
```

無限のツール呼び出しループを防ぐために、このようなプロンプトをより説明的なものに置き換えることができます。

例:

```
ユーザーのプロンプトと以下にリストされている利用可能な関数を確認してください。
まず、これらの関数の1つを呼び出すことが最も適切な応答方法であるかどうかを判断します。プロンプトが特定のアクションを要求したり、外部データの検索を必要としたり、関数によって処理される計算を伴う場合は、関数呼び出しが必要になる可能性が高いです。プロンプトが一般的な質問であるか、直接回答できる場合は、関数呼び出しは不要である可能性が高いです。

関数呼び出しが必要だと判断した場合：{"name": "function_name", "parameters": {"argument_name": "value"}}の形式のJSONオブジェクトのみで応答してください。パラメータ値は変数ではなく具体的な値であることを確認してください。

関数呼び出しが不要だと判断した場合：ユーザーのプロンプトに直接プレーンテキストで応答し、要求された回答や情報を提供してください。JSONは出力しないでください。
```

その後、次のコマンドで新しいモデルを作成できます。

```bash
ollama create llama3.2-modified -f model_file_to_modify
```

#### `ollama_chat`プロバイダーの使用

当社のLiteLLMラッパーを使用して、Ollamaモデルでエージェントを作成できます。

```py
root_agent = Agent(
    model=LiteLlm(model="ollama_chat/mistral-small3.1"),
    name="dice_agent",
    description=(
        "8面のサイコロを振って素数を確認できるhello worldエージェント。"
    ),
    instruction="""
      サイコロを振り、その結果についての質問に答えます。
    """,
    tools=[
        roll_die,
        check_prime,
    ],
)
```

**`ollama`の代わりにプロバイダーとして`ollama_chat`を設定することが重要です。`ollama`を使用すると、無限のツール呼び出しループや以前のコンテキストの無視など、予期しない動作が発生します。**

生成のためにLiteLLM内で`api_base`を提供できますが、v1.65.5現在、LiteLLMライブラリは完了後に環境変数に依存して他のAPIを呼び出しています。そのため、現時点では環境変数`OLLAMA_API_BASE`をollamaサーバーを指すように設定することをお勧めします。

```bash
export OLLAMA_API_BASE="http://localhost:11434"
adk web
```

#### `openai`プロバイダーの使用

あるいは、プロバイダー名として`openai`を使用することもできます。ただし、この場合は`OLLAMA_API_BASE`の代わりに`OPENAI_API_BASE=http://localhost:11434/v1`と`OPENAI_API_KEY=anything`の環境変数を設定する必要があります。**api baseの末尾に`/v1`が付くことに注意してください。**

```py
root_agent = Agent(
    model=LiteLlm(model="openai/mistral-small3.1"),
    name="dice_agent",
    description=(
        "8面のサイコロを振って素数を確認できるhello worldエージェント。"
    ),
    instruction="""
      サイコロを振り、その結果についての質問に答えます。
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

インポートの直後にエージェントコードに以下を追加することで、Ollamaサーバーに送信されたリクエストを確認できます。

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

### セルフホストエンドポイント（例: vLLM）

<div class="language-support-tag">
   <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span>
</div>

[vLLM](https://github.com/vllm-project/vllm)などのツールを使用すると、モデルを効率的にホストし、しばしばOpenAI互換のAPIエンドポイントを公開できます。

**設定:**

1. **モデルのデプロイ:** vLLM（または同様のツール）を使用して選択したモデルをデプロイします。APIベースURL（例: `https://your-vllm-endpoint.run.app/v1`）をメモしておきます。
    * *ADKツールにとって重要:* デプロイ時、サービングツールがOpenAI互換のツール/関数呼び出しをサポートし、有効にしていることを確認してください。vLLMの場合、モデルによっては`--enable-auto-tool-choice`のようなフラグや、特定の`--tool-call-parser`が必要になる場合があります。vLLMのツール使用に関するドキュメントを参照してください。
2. **認証:** エンドポイントが認証をどのように処理するか（APIキー、ベアラートークンなど）を決定します。

    **統合例:**

    ```python
    import subprocess
    from google.adk.agents import LlmAgent
    from google.adk.models.lite_llm import LiteLlm

    # --- vLLMエンドポイントでホストされているモデルを使用したエージェントの例 ---

    # vLLMデプロイメントから提供されるエンドポイントURL
    api_base_url = "https://your-vllm-endpoint.run.app/v1"

    # *あなたの* vLLMエンドポイント設定で認識されるモデル名
    model_name_at_endpoint = "hosted_vllm/google/gemma-3-4b-it" # vllm_test.pyからの例

    # 認証（例: Cloud Runデプロイメントのためのgcloud IDトークンを使用）
    # エンドポイントのセキュリティに応じてこれを調整してください
    try:
        gcloud_token = subprocess.check_output(
            ["gcloud", "auth", "print-identity-token", "-q"]
        ).decode().strip()
        auth_headers = {"Authorization": f"Bearer {gcloud_token}"}
    except Exception as e:
        print(f"警告: gcloudトークンを取得できませんでした - {e}。エンドポイントが非セキュアか、別の認証が必要な可能性があります。")
        auth_headers = None # または適切にエラーを処理

    agent_vllm = LlmAgent(
        model=LiteLlm(
            model=model_name_at_endpoint,
            api_base=api_base_url,
            # 必要に応じて認証ヘッダーを渡す
            extra_headers=auth_headers
            # 代わりに、エンドポイントがAPIキーを使用する場合:
            # api_key="YOUR_ENDPOINT_API_KEY"
        ),
        name="vllm_agent",
        instruction="あなたはセルフホストされたvLLMエンドポイントで実行されている役立つアシスタントです。",
        # ... その他のエージェントパラメータ
    )
    ```

## Vertex AIでホストおよびチューニングされたモデルの使用

エンタープライズグレードのスケーラビリティ、信頼性、そしてGoogle CloudのMLOpsエコシステムとの統合のために、Vertex AIエンドポイントにデプロイされたモデルを使用できます。これには、Model Gardenのモデルや独自のファインチューニングされたモデルが含まれます。

**統合方法:** 完全なVertex AIエンドポイントのリソース文字列（`projects/PROJECT_ID/locations/LOCATION/endpoints/ENDPOINT_ID`）を`LlmAgent`の`model`パラメータに直接渡します。

**Vertex AI設定（統合）:**

環境がVertex AI用に設定されていることを確認してください。

1. **認証:** アプリケーションのデフォルト認証情報（ADC）を使用します。

    ```shell
    gcloud auth application-default login
    ```

2. **環境変数:** プロジェクトとロケーションを設定します。

    ```shell
    export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
    export GOOGLE_CLOUD_LOCATION="YOUR_VERTEX_AI_LOCATION" # 例: us-central1
    ```

3. **Vertexバックエンドの有効化:** `google-genai`ライブラリがVertex AIをターゲットにしていることを確実にします。

    ```shell
    export GOOGLE_GENAI_USE_VERTEXAI=TRUE
    ```

### Model Gardenのデプロイメント

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.2.0</span>
</div>

[Vertex AI Model Garden](https://console.cloud.google.com/vertex-ai/model-garden)から様々なオープンモデルやプロプライエタリモデルをエンドポイントにデプロイできます。

**例:**

```python
from google.adk.agents import LlmAgent
from google.genai import types # 設定オブジェクト用

# --- Model GardenからデプロイされたLlama 3モデルを使用したエージェントの例 ---

# 実際のVertex AIエンドポイントのリソース名に置き換えてください
llama3_endpoint = "projects/YOUR_PROJECT_ID/locations/us-central1/endpoints/YOUR_LLAMA3_ENDPOINT_ID"

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

ファインチューニングされたモデル（Geminiベースか、Vertex AIでサポートされている他のアーキテクチャかにかかわらず）をデプロイすると、直接使用できるエンドポイントが作成されます。

**例:**

```python
from google.adk.agents import LlmAgent

# --- ファインチューニングされたGeminiモデルのエンドポイントを使用したエージェントの例 ---

# ファインチューニングされたモデルのエンドポイントリソース名に置き換えてください
finetuned_gemini_endpoint = "projects/YOUR_PROJECT_ID/locations/us-central1/endpoints/YOUR_FINETUNED_ENDPOINT_ID"

agent_finetuned_gemini = LlmAgent(
    model=finetuned_gemini_endpoint,
    name="finetuned_gemini_agent",
    instruction="あなたは特定のデータでトレーニングされた専門のアシスタントです。",
    # ... その他のエージェントパラメータ
)
```

### Vertex AI上のサードパーティモデル（例: Anthropic Claude）

Anthropicなどの一部のプロバイダーは、Vertex AIを通じて直接モデルを提供しています。

=== "Python"

    **統合方法:** 直接的なモデル文字列（例: `"claude-3-sonnet@20240229"`）を使用しますが、ADK内での*手動登録が必要*です。
    
    **なぜ登録が必要か？** ADKのレジストリは`gemini-*`文字列や標準のVertex AIエンドポイント文字列（`projects/.../endpoints/...`）を自動的に認識し、`google-genai`ライブラリ経由でルーティングします。Vertex AIを介して直接使用される他のモデルタイプ（Claudeなど）の場合、どの特定のラッパークラス（この場合は`Claude`）がそのモデル識別子文字列をVertex AIバックエンドで処理する方法を知っているかを、ADKレジストリに明示的に伝える必要があります。
    
    **設定:**
    
    1. **Vertex AI環境:** 統合されたVertex AI設定（ADC、環境変数、`GOOGLE_GENAI_USE_VERTEXAI=TRUE`）が完了していることを確認してください。
    
    2. **プロバイダーライブラリのインストール:** Vertex AI用に設定された必要なクライアントライブラリをインストールします。
    
        ```shell
        pip install "anthropic[vertex]"
        ```
    
    3. **モデルクラスの登録:** Claudeモデル文字列を使用するエージェントを作成する*前*に、アプリケーションの開始近くにこのコードを追加します。
    
        ```python
        # LlmAgentでVertex AIを介してClaudeモデル文字列を直接使用するために必要
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
        
       # --- Claudeクラスを登録（起動時に一度実行） ---
       LLMRegistry.register(Claude)
        
       # --- Vertex AI上のClaude 3 Sonnetを使用したエージェントの例 ---
        
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

    **統合方法:** プロバイダー固有のモデルクラス（例: `com.google.adk.models.Claude`）を直接インスタンス化し、Vertex AIバックエンドで設定します。
    
    **なぜ直接インスタンス化するのか？** Java ADKの`LlmRegistry`は、主にGeminiモデルをデフォルトで処理します。Vertex AI上のClaudeのようなサードパーティモデルの場合、ADKのラッパークラス（例: `Claude`）のインスタンスを`LlmAgent`に直接提供します。このラッパークラスは、Vertex AI用に設定された特定のクライアントライブラリを介してモデルと対話する責任を負います。
    
    **設定:**
    
    1.  **Vertex AI環境:**
        *   Google Cloudプロジェクトとリージョンが正しく設定されていることを確認してください。
        *   **アプリケーションのデフォルト認証情報（ADC）:** 環境でADCが正しく設定されていることを確認してください。これは通常、`gcloud auth application-default login`を実行することで行われます。Javaクライアントライブラリはこれらの認証情報を使用してVertex AIに認証します。詳細な設定については、[ADCに関するGoogle Cloud Javaドキュメント](https://cloud.google.com/java/docs/reference/google-auth-library/latest/com.google.auth.oauth2.GoogleCredentials#com_google_auth_oauth2_GoogleCredentials_getApplicationDefault__)に従ってください。
    
    2.  **プロバイダーライブラリの依存関係:**
        *   **サードパーティクライアントライブラリ（多くの場合、推移的）:** ADKコアライブラリには、Vertex AI上の一般的なサードパーティモデル（Anthropicに必要なクラスなど）に必要なクライアントライブラリが**推移的な依存関係**として含まれていることがよくあります。これは、`pom.xml`や`build.gradle`にAnthropic Vertex SDKの別の依存関係を明示的に追加する必要がない場合があることを意味します。

    3.  **モデルのインスタンス化と設定:**
        `LlmAgent`を作成する際に、`Claude`クラス（または別のプロバイダーの同等クラス）をインスタンス化し、その`VertexBackend`を設定します。
    
    **例:**

    ```java
    import com.anthropic.client.AnthropicClient;
    import com.anthropic.client.okhttp.AnthropicOkHttpClient;
    import com.anthropic.vertex.backends.VertexBackend;
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.models.Claude; // ADKのClaudeラッパー
    import com.google.auth.oauth2.GoogleCredentials;
    import java.io.IOException;

    // ... その他のインポート

    public class ClaudeVertexAiAgent {

        public static LlmAgent createAgent() throws IOException {
            // Vertex AI上のClaude 3 Sonnetのモデル名（または他のバージョン）
            String claudeModelVertexAi = "claude-3-7-sonnet"; // または他のClaudeモデル

            // AnthropicOkHttpClientをVertexBackendで設定
            AnthropicClient anthropicClient = AnthropicOkHttpClient.builder()
                .backend(
                    VertexBackend.builder()
                        .region("us-east5") // Vertex AIのリージョンを指定
                        .project("your-gcp-project-id") // GCPプロジェクトIDを指定
                        .googleCredentials(GoogleCredentials.getApplicationDefault())
                        .build())
                .build();

            // ADK ClaudeラッパーでLlmAgentをインスタンス化
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
                // ここでは通常、RunnerとSessionを設定してエージェントと対話します
            } catch (IOException e) {
                System.err.println("エージェントの作成に失敗しました: " + e.getMessage());
                e.printStackTrace();
            }
        }
    }
    ```