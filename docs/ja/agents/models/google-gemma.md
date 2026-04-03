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

```python
# Set GEMINI_API_KEY environment variable to your API key
# export GEMINI_API_KEY="YOUR_API_KEY"

from google.adk.agents import LlmAgent
from google.adk.models import Gemini

# Simple tool to try
def get_weather(location: str) -> str:
    return f"Location: {location}. Weather: sunny, 76 degrees Fahrenheit, 8 mph wind."

root_agent = LlmAgent(
    model=Gemini(model="gemma-4-31b-it"),
    name="weather_agent",
    instruction="You are a helpful assistant that can provide current weather.",
    tools=[get_weather]
)
```

## vLLM の例

これらのサービスで Gemma 4 エンドポイントにアクセスするには、Python 用の [LiteLLM](/agents/models/litellm/) ライブラリ経由で vLLM モデルを使えます。

以下の例では、ADK エージェントで Gemma 4 vLLM エンドポイントを使う方法を示します。

### セットアップ

1. **モデルのデプロイ:** 選んだモデルを
    [Vertex AI](https://console.cloud.google.com/vertex-ai/publishers/google/model-garden/gemma4)、
    [Google Kubernetes Engine](https://docs.cloud.google.com/kubernetes-engine/docs/tutorials/serve-gemma-gpu-vllm)、
    または [Cloud Run](https://docs.cloud.google.com/run/docs/run-gemma-on-cloud-run) を使ってデプロイし、
    OpenAI 互換 API エンドポイントを使用します。
    API base URL に `/v1` が含まれる点に注意してください（例: `https://your-vllm-endpoint.run.app/v1`）。
    * *ADK Tools で重要:* デプロイ時には、提供するサービングツールが互換性のある tool/function calling と reasoning parser をサポートし、有効化していることを確認してください。
2. **認証:** エンドポイントが認証をどのように扱うかを決めます（例: API key、bearer token）。

### コード

```python
import subprocess
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

# --- Example Agent using a model hosted on a vLLM endpoint ---

# Endpoint URL provided by your model deployment
api_base_url = "https://your-vllm-endpoint.run.app/v1"

# Model name as recognized by *your* vLLM endpoint configuration
model_name_at_endpoint = "openai/google/gemma-4-31B-it"

# Simple tool to try
def get_weather(location: str) -> str:
    return f"Location: {location}. Weather: sunny, 76 degrees Fahrenheit, 8 mph wind."

# Authentication (Example: using gcloud identity token for a Cloud Run deployment)
# Adapt this based on your endpoint's security
try:
    gcloud_token = subprocess.check_output(
        ["gcloud", "auth", "print-identity-token", "-q"]
    ).decode().strip()
    auth_headers = {"Authorization": f"Bearer {gcloud_token}"}
except Exception as e:
    print(f"Warning: Could not get gcloud token - {e}.")
    auth_headers = None # Or handle error appropriately

root_agent = LlmAgent(
    model=LiteLlm(
        model=model_name_at_endpoint,
        api_base=api_base_url,
        # Pass authentication headers if needed
        extra_headers=auth_headers
        # Alternatively, if endpoint uses an API key:
        # api_key="YOUR_ENDPOINT_API_KEY",
        extra_body={
            "chat_template_kwargs": {
                "enable_thinking": True # Enable thinking
            },
            "skip_special_tokens": False # Should be set to False
        },
    ),
    name="weather_agent",
    instruction="You are a helpful assistant that can provide current weather.",
    tools=[get_weather] # Tools!
)
```

## Gemma 4, ADK, Google Maps MCP を使ったフードツアーエージェントの作成
このサンプルでは、Gemma 4、ADK、Google Maps MCP サーバーを使って、パーソナライズされたフードツアーエージェントを作成する方法を示します。エージェントは、ユーザーが提供した料理の写真またはテキスト説明、場所、任意の予算を受け取り、食事場所を提案して徒歩ルートにまとめます。

### 前提条件

- [Google AI Studio](https://aistudio.google.com/app/apikey) で API キーを取得します。
  `GEMINI_API_KEY` 環境変数を Gemini API キーに設定します。
- Google Cloud Console で [Google Maps API](https://console.cloud.google.com/maps-api/) を有効にします。
- [Google Maps Platform API key](https://console.cloud.google.com/maps-api/credentials) を作成します。
  `MAPS_API_KEY` 環境変数を API キーに設定します。
- ADK をインストールし、Python 環境で設定します。

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
