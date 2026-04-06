# ADK エージェント向け Google Gemma モデル

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span>
</div>

ADK エージェントは、幅広い機能を提供する [Google Gemma](https://ai.google.dev/gemma/docs) 系の生成AIモデルを利用できます。ADK は [ツール呼び出し](/tools-custom/)
や [構造化出力](/agents/llm-agents/#structuring-data-input_schema-output_schema-output_key) を含む多くの Gemma 機能をサポートしています。

Gemma 4 は [Gemini API](https://ai.google.dev/gemini-api/docs) 経由で利用できるほか、
Google Cloud 上のさまざまなセルフホスティング विकल्पでも利用できます:
[Vertex AI](https://console.cloud.google.com/vertex-ai/publishers/google/model-garden/gemma4)、
[Google Kubernetes Engine](https://docs.cloud.google.com/kubernetes-engine/docs/tutorials/serve-gemma-gpu-vllm)、
[Cloud Run](https://docs.cloud.google.com/run/docs/run-gemma-on-cloud-run)。

## Gemini API の例

[Google AI Studio](https://aistudio.google.com/app/apikey) で API キーを作成します。

=== "Python"
    ```python
    # GEMINI_API_KEY 環境変数に API キーを設定します。
    # export GEMINI_API_KEY="YOUR_API_KEY"

    from google.adk.agents import LlmAgent
    from google.adk.models import Gemini

    # 試しに使えるシンプルなツール
    def get_weather(location: str) -> str:
        return f"場所: {location}. 天気: 晴れ、華氏76度、風速8mph。"

    root_agent = LlmAgent(
        model=Gemini(model="gemma-4-31b-it"),
        name="weather_agent",
        instruction="現在の天気を案内できる役立つアシスタントです。",
        tools=[get_weather]
    )
    ```

=== "Java"
    ```java
    // GEMINI_API_KEY 環境変数に API キーを設定します。
    // export GEMINI_API_KEY="YOUR_API_KEY"

    import com.google.adk.agents.LlmAgent;
    import com.google.adk.tools.Annotations.Schema;
    import com.google.adk.tools.FunctionTool;

    LlmAgent weatherAgent = LlmAgent.builder()
        .model("gemma-4-31b-it")
        .name("weather_agent")
        .instruction("""
            現在の天気を案内できる役立つアシスタントです。
        """)
        .tools(FunctionTool.create(this, "getWeather"))
        .build();

    @Schema(
        name = "getWeather",
        description = "指定した場所の天気予報を取得します。"
    )
    public Map<String, String> getWeather(
        @Schema(
            name = "location",
            description = "天気予報を取得する場所"
        )
        String location
    ) {
        return Map.of(
            "forecast",
            "場所: " + location + ". 天気: 晴れ、華氏76度、風速8mph。"
        );
    }
    ```

## vLLM の例

これらのサービスで Gemma 4 エンドポイントにアクセスするには、Python 用の [LiteLLM](/agents/models/litellm/) ライブラリと Java 用の [LangChain4j](https://docs.langchain4j.dev/) を通じて vLLM モデルを利用できます。

以下の例では、ADK エージェントで Gemma 4 vLLM エンドポイントを使う方法を示します。

### セットアップ

1. **モデルのデプロイ:** 選んだモデルを
    [Vertex AI](https://console.cloud.google.com/vertex-ai/publishers/google/model-garden/gemma4)、
    [Google Kubernetes Engine](https://docs.cloud.google.com/kubernetes-engine/docs/tutorials/serve-gemma-gpu-vllm)、
    または [Cloud Run](https://docs.cloud.google.com/run/docs/run-gemma-on-cloud-run) にデプロイし、
    OpenAI 互換 API エンドポイントを使用します。
    API のベース URL には `/v1` が含まれる点に注意してください（例: `https://your-vllm-endpoint.run.app/v1`）。
    * *ADK ツールで重要:* デプロイ時には、利用するサービングツールが互換性のある tool/function calling と reasoning parser をサポートし、有効化していることを確認してください。
2. **認証:** エンドポイントが認証をどのように処理するかを決めます（例: API key、bearer token）。

### コード

=== "Python"
    ```python
    import subprocess
    from google.adk.agents import LlmAgent
    from google.adk.models.lite_llm import LiteLlm

    # --- vLLM エンドポイント上のモデルを使うサンプルエージェント ---

    # モデルデプロイで提供されるエンドポイント URL
    api_base_url = "https://your-vllm-endpoint.run.app/v1"

    # 利用中の vLLM エンドポイント設定で認識されるモデル名
    model_name_at_endpoint = "openai/google/gemma-4-31B-it"

    # 試しに使えるシンプルなツール
    def get_weather(location: str) -> str:
        return f"場所: {location}. 天気: 晴れ、華氏76度、風速8mph。"

    # 認証例: Cloud Run デプロイで gcloud identity token を使用
    # エンドポイントのセキュリティ方式に合わせて調整してください。
    try:
        gcloud_token = subprocess.check_output(
            ["gcloud", "auth", "print-identity-token", "-q"]
        ).decode().strip()
        auth_headers = {"Authorization": f"Bearer {gcloud_token}"}
    except Exception as e:
        print(f"警告: gcloud トークンを取得できませんでした - {e}.")
        auth_headers = None  # 必要に応じて適切にエラー処理してください。

    root_agent = LlmAgent(
        model=LiteLlm(
            model=model_name_at_endpoint,
            api_base=api_base_url,
            # 必要なら認証ヘッダーを渡します。
            extra_headers=auth_headers,
            # エンドポイントが API キーを使う場合は次のように指定できます。
            # api_key="YOUR_ENDPOINT_API_KEY",
            extra_body={
                "chat_template_kwargs": {
                    "enable_thinking": True  # 思考機能を有効化
                },
                "skip_special_tokens": False  # False に設定する必要があります。
            },
        ),
        name="weather_agent",
        instruction="現在の天気を案内できる役立つアシスタントです。",
        tools=[get_weather],  # ツール登録
    )
    ```

=== "Java"
    vLLM でホストされた Gemma を使うには、OpenAI 互換ライブラリを使用する必要があります。
    LangChain4j は `pom.xml` に追加できる OpenAI 依存関係を提供します。

    ```xml
    <!-- LangChain4j to ADK bridge -->
    <dependency>
        <groupId>com.google.adk</groupId>
        <artifactId>google-adk-langchain4j</artifactId>
        <version>${adk.version}</version>
    </dependency>
    <!-- Core LangChain4j library -->
    <dependency>
        <groupId>dev.langchain4j</groupId>
        <artifactId>langchain4j-core</artifactId>
        <version>${langchain4j.version}</version>
    </dependency>
    <!-- OpenAI compatible model -->
    <dependency>
        <groupId>dev.langchain4j</groupId>
        <artifactId>langchain4j-open-ai</artifactId>
        <version>${langchain4j.version}</version>
    </dependency>
    ```

    OpenAI 互換のチャットモデル（ストリーミングまたは非ストリーミング）を作成し、`LangChain4j` ラッパーで包んでから `LlmAgent` に渡します。

    ```java
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.models.langchain4j.LangChain4j;
    import com.google.adk.tools.Annotations.Schema;
    import com.google.adk.tools.FunctionTool;
    import dev.langchain4j.model.chat.StreamingChatModel;
    import dev.langchain4j.model.openai.OpenAiStreamingChatModel;

    // モデルデプロイで提供されるエンドポイント URL
    String apiBaseUrl = "https://your-vllm-endpoint.run.app/v1";

    // 利用中の vLLM エンドポイント設定で認識されるモデル名
    String gemmaModelName = "gg-hf-gg/gemma-4-31b-it";

    // まず LangChain4j で OpenAI 互換チャットモデルを定義します。
    StreamingChatModel model =
        OpenAiStreamingChatModel.builder()
            .modelName(gemmaModelName)
            // エンドポイントに API キーが必要なら使用します。
            // .apiKey("YOUR_ENDPOINT_API_KEY")
            .baseUrl(apiBaseUrl)
            .customParameters(
                Map.of(
                    "skip_special_tokens", false,
                    "chat_template_kwargs", Map.of("enable_thinking", true)
                )
            )
            .build();

    // LangChain4j ラッパーモデルでエージェントを構成します。
    LlmAgent weatherAgent = LlmAgent.builder()
        .model(new LangChain4j(model))
        .name("weather_agent")
        .instruction("""
            現在の天気を案内できる役立つアシスタントです。
        """)
        .tools(FunctionTool.create(this, "getWeather"))
        .build();

    @Schema(
        name = "getWeather",
        description = "指定した場所の天気予報を取得します。"
    )
    public Map<String, String> getWeather(
        @Schema(
            name = "location",
            description = "天気予報を取得する場所"
        )
        String location
    ) {
        return Map.of(
            "forecast",
            "場所: " + location + ". 天気: 晴れ、華氏76度、風速8mph。"
        );
    }
    ```

## Gemma 4, ADK, Google Maps MCP を使ったフードツアーエージェントの作成
このサンプルでは、Gemma 4、ADK、Google Maps MCP サーバーを使って、パーソナライズされたフードツアーエージェントを作成する方法を示します。エージェントは、ユーザーが提供した料理の写真またはテキスト説明、場所、任意の予算を受け取り、食事場所を提案して徒歩ルートにまとめます。

### 前提条件

- [Google AI Studio](https://aistudio.google.com/app/apikey) で API キーを取得します。
  `GEMINI_API_KEY` 環境変数を Gemini API キーに設定します。
- Google Cloud Console で [Google Maps API](https://console.cloud.google.com/maps-api/) を有効にします。
- [Google Maps Platform API key](https://console.cloud.google.com/maps-api/credentials) を作成します。
  `MAPS_API_KEY` 環境変数を API キーに設定します。
- ADK をインストールして Python 環境で設定するか、Java プロジェクトで Java 依存関係を設定します。

### プロジェクト構成
```bash
food_tour_app/
├── __init__.py
└── agent.py
```
**プロジェクト全体は [こちら](https://github.com/google/adk-samples/tree/main/python/agents/gemma-food-tour-guide) で確認できます**

`agent.py`
```python
import os
import dotenv
from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

dotenv.load_dotenv()

system_instruction = """
You are an expert personalized food tour guide.
Your goal is to build a culinary tour based on the user's inputs: a photo of a dish (or a text description), a location, and a budget.

Follow these 4 rigorous steps:
1. **Identify the Cuisine/Dish:** Analyze the user's provided description or image URL to determine the primary cuisine or specific dish.
2. **Find the Best Spots:** Use the `search_places` tool to find highly rated restaurants, stalls, or cafes serving that cuisine/dish in the user's specified location.
   **CRITICAL RULE FOR PLACES:** `search_places` returns AI-generated place data summaries along with `place_id`, latitude/longitude coordinates, and map links for each place, but may lack a direct, explicit name field. You must carefully associate each described place to its provided `place_id` or `lat_lng`.
3. **Build the Route:** Use the `compute_routes` tool to structure a walking-optimized route between the selected spots.
   **CRITICAL ROUTING RULE:** To avoid hallucinating, you MUST provide the `origin` and `destination` using the exact `place_id` string OR `lat_lng` object returned by `search_places`. Do NOT guess or hallucinate an `address` or `place_id` if you do not know the exact name.
4. **Insider Tips:** Provide specific "order this, skip that" insider tips for each location on the tour.

Structure your response clearly and concisely. If the user provides a budget, ensure your suggestions align with it.
"""

MAPS_MCP_URL = "https://mapstools.googleapis.com/mcp"

def get_maps_mcp_toolset():
    dotenv.load_dotenv()
    maps_api_key = os.getenv("MAPS_API_KEY")
    if not maps_api_key:
        print("Warning: MAPS_API_KEY environment variable not found.")
        maps_api_key = "no_api_found"

    tools = MCPToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=MAPS_MCP_URL,
            headers={
                "X-Goog-Api-Key": maps_api_key
            }
        )
    )
    print("Google Maps MCP Toolset configured.")
    return tools

maps_toolset = get_maps_mcp_toolset()

root_agent = LlmAgent(
    model=Gemini(model="gemma-4-31b-it"),
    name="food_tour_agent",
    instruction=system_instruction,
    tools=[maps_toolset],
)
```

### 環境変数
エージェントを実行する前に必要な環境変数を設定します。
```
export MAPS_API_KEY="YOUR_GOOGLE_MAPS_API_KEY"
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

### 使用例
Food Tour Agent の機能を試すには、次のプロンプトをチャットに貼り付けてみてください。

- *"トロントでラーメンツアーをしたいです。1日の予算は60ドルです。上位3スポットの徒歩ルートを作って、それぞれで何を注文すべきか教えてください。"*
- *"このディープディッシュピザの写真 [画像URLを挿入] があります。シカゴの Navy Pier 周辺でこれに最適な場所を見つけたいです。徒歩ツアーを構成して、各立ち寄り先で必食の一切れを教えてください。"*
- *"ダウンタウン・オースティンで本格的な BBQ ツアーを探しています。予算は100ドル以下に抑えたいです。評価の高い3か所をつなぐ徒歩ルートを作り、最高の肉の部位についての内部情報を教えてください。"*

エージェントは次のことを行います。

1. 可能性の高い料理や料理スタイルを推測します。
2. Google Maps MCP ツールを使って関連する場所を検索します。
3. 選択した立ち寄り先の間の徒歩ルートを計算します。
4. 推薦と内部情報を含む構造化されたフードツアーを返します。
