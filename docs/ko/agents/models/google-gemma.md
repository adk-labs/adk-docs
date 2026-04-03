# ADK 에이전트를 위한 Google Gemma 모델

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span>
</div>

ADK 에이전트는 다양한 기능을 제공하는 [Google Gemma](https://ai.google.dev/gemma/docs) 생성형 AI 모델 계열을 사용할 수 있습니다. ADK는 [도구 호출](/tools-custom/)
과 [구조화된 출력](/agents/llm-agents/#structuring-data-input_schema-output_schema-output_key) 등 여러 Gemma 기능을 지원합니다.

Gemma 4는 [Gemini API](https://ai.google.dev/gemini-api/docs)를 통해 사용할 수 있으며,
또는 Google Cloud의 여러 셀프 호스팅 옵션을 통해 사용할 수도 있습니다:
[Vertex AI](https://console.cloud.google.com/vertex-ai/publishers/google/model-garden/gemma4),
[Google Kubernetes Engine](https://docs.cloud.google.com/kubernetes-engine/docs/tutorials/serve-gemma-gpu-vllm),
[Cloud Run](https://docs.cloud.google.com/run/docs/run-gemma-on-cloud-run).

## Gemini API 예시

[Google AI Studio](https://aistudio.google.com/app/apikey)에서 API 키를 생성합니다.

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

## vLLM 예시

이 서비스의 Gemma 4 엔드포인트에 액세스하려면 Python용 [LiteLLM](/agents/models/litellm/) 라이브러리를 통해 vLLM 모델을 사용할 수 있습니다.

다음 예시는 ADK 에이전트에서 Gemma 4 vLLM 엔드포인트를 사용하는 방법을 보여 줍니다.

### 설정

1. **모델 배포:** 선택한 모델을
    [Vertex AI](https://console.cloud.google.com/vertex-ai/publishers/google/model-garden/gemma4),
    [Google Kubernetes Engine](https://docs.cloud.google.com/kubernetes-engine/docs/tutorials/serve-gemma-gpu-vllm),
    또는 [Cloud Run](https://docs.cloud.google.com/run/docs/run-gemma-on-cloud-run)을 사용해 배포하고,
    OpenAI 호환 API 엔드포인트를 사용합니다.
    API base URL에 `/v1`이 포함된다는 점에 유의하세요(예: `https://your-vllm-endpoint.run.app/v1`).
    * *ADK 도구에 중요:* 배포 시 서빙 도구가 호환되는 tool/function calling과 reasoning parser를 지원하고 활성화하는지 확인하세요.
2. **인증:** 엔드포인트가 인증을 처리하는 방식을 결정합니다(예: API key, bearer token).

### 코드

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

## Gemma 4, ADK, Google Maps MCP로 음식 투어 에이전트 만들기
이 샘플은 Gemma 4, ADK, Google Maps MCP 서버를 사용해 개인화된 음식 투어 에이전트를 만드는 방법을 보여 줍니다. 에이전트는 사용자가 제공한 음식 사진 또는 텍스트 설명, 위치, 선택적 예산을 바탕으로 먹을 곳을 추천하고 도보 경로로 정리합니다.

### 사전 요구 사항

- [Google AI Studio](https://aistudio.google.com/app/apikey)에서 API 키를 받습니다.
  `GEMINI_API_KEY` 환경 변수를 Gemini API 키로 설정하세요.
- Google Cloud Console에서 [Google Maps API](https://console.cloud.google.com/maps-api/)를 사용 설정합니다.
- [Google Maps Platform API 키](https://console.cloud.google.com/maps-api/credentials)를 만듭니다.
  `MAPS_API_KEY` 환경 변수를 API 키로 설정하세요.
- ADK를 설치하고 Python 환경에서 구성합니다.

### 프로젝트 구조
```bash
food_tour_app/
├── __init__.py
└── agent.py
```
**전체 프로젝트는 [여기](https://github.com/google/adk-samples/tree/main/python/agents/gemma-food-tour-guide)에서 확인할 수 있습니다**

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

### 환경 변수
에이전트를 실행하기 전에 필요한 환경 변수를 설정합니다.
```
export MAPS_API_KEY="YOUR_GOOGLE_MAPS_API_KEY"
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

### 사용 예시
Food Tour Agent의 기능을 테스트하려면 채팅에 다음 프롬프트 중 하나를 붙여 넣어 보세요.

- *"토론토에서 라멘 투어를 하고 싶습니다. 하루 예산은 60달러입니다. 상위 3개 장소에 대한 도보 경로를 알려 주고 각 장소에서 무엇을 주문해야 하는지도 알려 주세요."*
- *"이 딥디시 피자 사진 [이미지 URL 삽입]이 있습니다. 시카고 네이비 피어 주변에서 이 메뉴의 최고의 장소를 찾고 싶습니다. 도보 투어를 구성하고 각 정류장에서 꼭 먹어야 할 한 조각이 무엇인지 알려 주세요."*
- *"다운타운 오스틴에서 정통 바비큐 투어를 찾고 있습니다. 예산은 100달러 이하로 유지합시다. 평점이 높은 3곳 사이의 도보 경로를 만들고 가장 좋은 고기 부위에 대한 내부 팁을 알려 주세요."*

에이전트는 다음을 수행합니다.

1. 가능성이 높은 요리 또는 음식 스타일을 추론합니다.
2. Google Maps MCP 도구를 사용해 관련 장소를 검색합니다.
3. 선택한 정류장 사이의 도보 경로를 계산합니다.
4. 추천과 내부 팁이 포함된 구조화된 음식 투어를 반환합니다.
