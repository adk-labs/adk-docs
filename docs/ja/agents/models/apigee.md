# ADK エージェント用 Apigee AI Gateway

<div class="language-support-tag">
   <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.18.0</span><span class="lst-java">Java v0.4.0</span>
</div>

[Apigee](https://docs.cloud.google.com/apigee/docs/api-platform/get-started/what-apigee) は強力な [AI Gateway](https://cloud.google.com/solutions/apigee-ai) を提供し、生成 AI モデルのトラフィックを管理および制御する方法を変革します。Apigee プロキシ経由で AI モデル エンドポイント (Agent Platform や Gemini API など) を公開することで、次のエンタープライズ グレードの機能を即座に利用できます。

- **モデルの安全性:** 脅威保護のための Model Armor などのセキュリティ ポリシーを実装します。
- **トラフィック ガバナンス:** コストを管理し、不正使用を防止するために、レート制限とトークン制限を適用します。
- **パフォーマンス:** セマンティック キャッシュと高度なモデル ルーティングを使用して、応答時間と効率を向上させます。
- **モニタリングと可視性:** すべての AI リクエストの詳細なモニタリング、分析、監査を取得します。

   `ApigeeLlm` ラッパーは、Agent Platform および Gemini API (generateContent) で使用するように設計されています。他のモデルやインターフェースのサポートも継続的に拡大しています。セルフホスト型または他のプロバイダーを含む OpenAI 互換モデルの場合は、`CompletionsHTTPClient` を使用して Apigee プロキシ経由でトラフィックをルーティングします。

## 実装例

`ApigeeLlm` ラッパー オブジェクトをインスタンス化し、それを `LlmAgent` または他のエージェント タイプに渡すことで、Apigee のガバナンスをエージェントのワークフローに統合します。

=== "Python"

    ```python
    from google.adk.agents import LlmAgent
    from google.adk.models.apigee_llm import ApigeeLlm

    # ApigeeLlm ラッパーをインスタンス化
    model = ApigeeLlm(
        # モデルへの Apigee ルートを指定。詳細については、ApigeeLlm のドキュメントを参照してください (https://github.com/google/adk-python/tree/main/contributing/samples/models/hello_world_apigeellm)。
        model="apigee/gemini-flash-latest",
        # ベースパスを含むデプロイされた Apigee プロキシのプロキシ URL
        proxy_url=f"https://{APIGEE_PROXY_URL}",
        # 必要な認証/認可ヘッダー (API キーなど) を渡す
        custom_headers={"foo": "bar"}
    )

    # 構成されたモデル ラッパーを LlmAgent に渡す
    agent = LlmAgent(
        model=model,
        name="my_governed_agent",
        instruction="You are a helpful assistant powered by Gemini and governed by Apigee.",
        # ... その他のエージェント パラメータ
    )
    ```

=== "Java"

    ```java
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.models.ApigeeLlm;
    import com.google.common.collect.ImmutableMap;

    ApigeeLlm apigeeLlm =
            ApigeeLlm.builder()
                .modelName("apigee/gemini-flash-latest") // モデルへの Apigee ルートを指定
                .proxyUrl(APIGEE_PROXY_URL) // ベースパスを含むデプロイされた Apigee プロキシのプロキシ URL
                .customHeaders(ImmutableMap.of("foo", "bar")) // 必要な認証/認可ヘッダー (API キーなど) を渡す
                .build();
    LlmAgent agent =
        LlmAgent.builder()
            .model(apigeeLlm)
            .name("my_governed_agent")
            .description("my_governed_agent")
            .instruction("You are a helpful assistant powered by Gemini and governed by Apigee.")
            // ツールは次に追加されます
            .build();
    ```

この構成により、エージェントからのすべての API 呼び出しが最初に Apigee を経由してルーティングされ、リクエストが基礎となる AI モデル エンドポイントに安全に転送される前に、必要なすべてのポリシー (セキュリティ、レート制限、ロギング) が実行されます。Apigee プロキシを使用した完全なコード例については、[Hello World Apigee LLM](https://github.com/google/adk-python/tree/main/contributing/samples/models/hello_world_apigeellm) を参照してください。

## OpenAI との互換性

`CompletionsHTTPClient` は、OpenAI API 形式との互換性を考慮して設計された汎用 HTTP クライアントです。ネイティブの Gemini または Vertex AI プロトコルではなく、標準の OpenAI 互換 `/chat/completions` エンドポイントを期待するプロキシ (Apigee など) を介してリクエストをルーティングできます。このクライアントは以下を処理します。

- **ペイロードの構築**: `LlmRequest` オブジェクトを OpenAI 互換 API で必要な形式に変換します。
- **応答の処理**: プロキシからのストリーミング応答と非ストリーミング応答を管理します。
- **信頼性**: `tenacity` を使用して非ストリーミング リクエストを再試行しますが、コンストラクタに `retry_options=types.HttpRetryOptions(...)` を渡した場合に限られます。デフォルトでは各リクエストは 1 回のみ試行され、ストリーミング リクエストは再試行されません。
- **正規化**: 応答とストリーミング チャンクを、ADK フレームワークの他の部分で期待される標準形式に解析します。

### 実装例

```python
import asyncio
from google.adk.models.apigee_llm import CompletionsHTTPClient
from google.adk.models.llm_request import LlmRequest
from google.genai import types

async def test_client():
    # 1. クライアントを初期化
    client = CompletionsHTTPClient(
        base_url="https://your-apigee-proxy-url.com/v1",
        headers={"Authorization": "Bearer YOUR_API_KEY"}
    )

    # 2. 最小限のリクエストを構築
    request = LlmRequest(
        model="gpt-4o",  # ターゲット モデル ID に置き換える
        contents=[types.Content(role="user", parts=[types.Part.from_text(text="Hello!")])]
    )

    # 3. 非ストリーミング生成を実行
    async for response in client.generate_content_async(request, stream=False):
        if response.content and response.content.parts:
            print(f"Response: {response.content.parts[0].text}")

if __name__ == "__main__":
    asyncio.run(test_client())
```
