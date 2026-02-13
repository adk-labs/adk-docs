# ADK エージェント用の Google Gemini モデル

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">Typescript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

ADK は、幅広い機能を備えた Google Gemini 系の生成 AI モデルをサポートします。
ADK は次のような豊富な Gemini 機能をサポートしています。
[コード実行](/adk-docs/tools/gemini-api/code-execution/)、
[Google Search](/adk-docs/tools/gemini-api/google-search/)、
[コンテキストキャッシュ](/adk-docs/context/caching/)、
[コンピュータ使用](/adk-docs/tools/gemini-api/computer-use/)、
および [Interactions API](#interactions-api) を含みます。

## はじめに

以下のコード例は、エージェントで Gemini モデルを使用する基本実装を示します。

=== "Python"

    ```python
    from google.adk.agents import LlmAgent

    # --- Example using a stable Gemini Flash model ---
    agent_gemini_flash = LlmAgent(
        # Use the latest stable Flash model identifier
        model="gemini-2.5-flash",
        name="gemini_flash_agent",
        instruction="You are a fast and helpful Gemini assistant.",
        # ... other agent parameters
    )
    ```

=== "TypeScript"

    ```typescript
    import {LlmAgent} from '@google/adk';

    // --- Example #2: using a powerful Gemini Pro model with API Key in model ---
    export const rootAgent = new LlmAgent({
      name: 'hello_time_agent',
      model: 'gemini-2.5-flash',
      description: 'Gemini flash agent',
      instruction: `You are a fast and helpful Gemini assistant.`,
    });
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
    // --- Example #1: using a stable Gemini Flash model with ENV variables---
    LlmAgent agentGeminiFlash =
        LlmAgent.builder()
            // Use the latest stable Flash model identifier
            .model("gemini-2.5-flash") // Set ENV variables to use this model
            .name("gemini_flash_agent")
            .instruction("You are a fast and helpful Gemini assistant.")
            // ... other agent parameters
            .build();
    ```


## Gemini モデル認証

このセクションでは、Google AI Studio（迅速な開発）または Google Cloud Vertex AI
（エンタープライズ用途）による Gemini モデルの認証を説明します。
これは ADK 内で Google の主要モデルを利用する最も直接的な方法です。

**統合方法:** 下記いずれかで認証を完了すると、`LlmAgent` の `model`
パラメータにモデル識別子文字列を直接渡せるようになります。


!!! tip

    ADK が Gemini モデルで内部的に使用する `google-genai` ライブラリは、
    Google AI Studio または Vertex AI のどちらでも接続できます。

    **音声/動画ストリーミングのサポート**

    ADK で音声/動画ストリーミングを使用するには、Live API をサポートする
    Gemini モデルを使用してください。Gemini Live API をサポートする **モデル ID**
    は以下を参照してください。

    - [Google AI Studio: Gemini Live API](https://ai.google.dev/gemini-api/docs/models#live-api)
    - [Vertex AI: Gemini Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)

### Google AI Studio

最もシンプルな方法で、すぐに始める場合に推奨します。

*   **認証方法:** API Key
*   **セットアップ:**
    1.  **API キーを取得:** [Google AI Studio](https://aistudio.google.com/apikey) からキーを取得します。
    2.  **環境変数を設定:** プロジェクトのルートディレクトリに `.env`（Python）
        または `.properties`（Java）を作成し、次の行を追加します。ADK はこのファイルを自動的に読み込みます。

        ```shell
        export GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
        export GOOGLE_GENAI_USE_VERTEXAI=FALSE
        ```

        （または）

        モデル初期化時に `Client` 経由で変数を渡します（後述）。

* **モデル:** 利用可能モデル一覧は
  [Google AI for Developers](https://ai.google.dev/gemini-api/docs/models) を参照してください。

### Google Cloud Vertex AI

スケーラブルで本番利用向けには Vertex AI を推奨します。
Vertex AI 上の Gemini はエンタープライズ向け機能、セキュリティ、コンプライアンス制御を提供します。
開発環境とユースケースに応じて、以下の方法のいずれかで認証します。

**事前要件:** [Vertex AI が有効化された](https://console.cloud.google.com/apis/enableflow;apiid=aiplatform.googleapis.com) Google Cloud プロジェクトが必要です。

### **方法 A: ユーザー認証情報（ローカル開発向け）**

1.  **gcloud CLI のインストール:** 公式 [インストール手順](https://cloud.google.com/sdk/docs/install)に従います。
2.  **ADC でログイン:** このコマンドでブラウザーが開き、ローカル開発のユーザーアカウント認証が行われます。
    ```bash
    gcloud auth application-default login
    ```
3.  **環境変数を設定:**
    ```shell
    export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
    export GOOGLE_CLOUD_LOCATION="YOUR_VERTEX_AI_LOCATION" # e.g., us-central1
    ```

    ライブラリに Vertex AI の使用を明示します。

    ```shell
    export GOOGLE_GENAI_USE_VERTEXAI=TRUE
    ```

4. **モデル:** 利用可能なモデル ID は
  [Vertex AI ドキュメント](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models) で確認してください。

### **方法 B: Vertex AI Express Mode**
[Vertex AI Express Mode](https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview)
は API キー ベースの簡易セットアップで、迅速なプロトタイピングに適しています。

1.  **Express Mode にサインアップ**して API キーを取得します。
2.  **環境変数を設定:**
    ```shell
    export GOOGLE_API_KEY="PASTE_YOUR_EXPRESS_MODE_API_KEY_HERE"
    export GOOGLE_GENAI_USE_VERTEXAI=TRUE
    ```

### **方法 C: サービスアカウント（本番/自動化向け）**

デプロイ済みアプリケーションでは、サービスアカウントが標準的な方法です。

1.  [サービスアカウントを作成](https://cloud.google.com/iam/docs/service-accounts-create#console) し、
    `Vertex AI User` ロールを付与します。
2.  **アプリケーションへ認証情報を設定:**
    *   **Google Cloud 内:** Cloud Run、GKE、VM、または他の Google Cloud サービスで
    エージェントを実行している場合、サービスアカウント認証情報は環境で自動提供されるため
    キーファイルは不要です。
    *   **それ以外:** [サービスアカウントキーファイル](https://cloud.google.com/iam/docs/keys-create-delete#console)を作成し、
    環境変数でそのパスを指定します。
        ```bash
        export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/keyfile.json"
        ```
    キーファイルの代わりに Workload Identity で認証できますが、このガイドでは扱いません。

!!! warning "認証情報の保護"

    サービスアカウント認証情報や API キーは高権限資格情報です。
    公開しないでください。運用では Google Cloud Secret Manager などを使って
    安全に保管・参照してください。

!!! note "Gemini モデルのバージョン"

    常に公式 Gemini ドキュメントで最新のモデル名を確認してください。
    プレビュー版は利用可能性やクォータ制限が異なる場合があります。

## トラブルシューティング

### エラーコード 429 - RESOURCE_EXHAUSTED

このエラーは、リクエスト数が処理能力として割り当てられた上限を超えると発生します。

以下のいずれかを実施して対処できます。

1.  使用するモデルのクォータ上限を引き上げる申請をします。

2.  クライアント側リトライを有効にします。リトライにより、一時的なクォータ不足時に
    一定時間待機して自動再送することで回避可能です。

    リト라이オプションの設定には2通りあります。

    **オプション 1:** `generate_content_config` 内でエージェントに対してリトライを設定します。

    この方法はこのモデルアダプターを直接インスタンス化する場合に適しています。

    ```python
    root_agent = Agent(
        model='gemini-2.5-flash',
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

    **オプション 2:** このモデルアダプター自体のリトライオプションを設定します。

    この方法はアダプターインスタンスを別途取得しない場合に適しています。

    ```python
    from google.genai import types

    # ...

    agent = Agent(
        model=Gemini(
        retry_options=types.HttpRetryOptions(initial_delay=1, attempts=2),
        )
    )
    ```

## Gemini Interactions API {#interactions-api}

<div class="language-support-tag" title="Java ADK は現在 Gemini と Anthropic モデルのみをサポートしています。">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.21.0</span>
</div>

Gemini の [Interactions API](https://ai.google.dev/gemini-api/docs/interactions)
は、***generateContent*** 推論 API の代替で、ステートフルな会話を可能にします。
各リクエストで会話履歴全体を送信する代わりに `previous_interaction_id`
を用いてやり取りを連結できるため、長い会話に対して効率的です。

次のコード断片のように、Gemini モデル設定で
`use_interactions_api=True` を設定すると Interactions API を有効化できます。

```python
from google.adk.agents.llm_agent import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools.google_search_tool import GoogleSearchTool

root_agent = Agent(
    model=Gemini(
        model="gemini-2.5-flash",
        use_interactions_api=True,  # Enable Interactions API
    ),
    name="interactions_test_agent",
    tools=[
        GoogleSearchTool(bypass_multi_tools_limit=True),  # Converted to function tool
        get_current_weather,  # Custom function tool
    ],
)
```

完全なサンプルは
[Interactions API サンプル](https://github.com/google/adk-python/tree/main/contributing/samples/interactions_api)を参照してください。

### 既知の制限

Interactions API は、[Google Search](/adk-docs/tools/built-in-tools/#google-search) のような
カスタム関数呼び出しツールと、同じエージェント内の組み込みツールを混在して使用することを**サポートしません**。
`bypass_multi_tools_limit` パラメータで組み込みツールをカスタムツールとして動作させることで
回避できます。

```python
# Use bypass_multi_tools_limit=True to convert google_search to a function tool
GoogleSearchTool(bypass_multi_tools_limit=True)
```

この例では、組み込み google_search を関数呼び出しツール（GoogleSearchAgentTool）
へ変換し、カスタム関数ツールと共存できるようにします。
