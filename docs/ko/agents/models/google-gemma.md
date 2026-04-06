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

=== "Python"
    ```python
    # GEMINI_API_KEY 환경 변수를 API 키로 설정합니다.
    # export GEMINI_API_KEY="YOUR_API_KEY"

    from google.adk.agents import LlmAgent
    from google.adk.models import Gemini

    # 간단히 사용해 볼 도구
    def get_weather(location: str) -> str:
        return f"위치: {location}. 날씨: 맑음, 화씨 76도, 풍속 8mph."

    root_agent = LlmAgent(
        model=Gemini(model="gemma-4-31b-it"),
        name="weather_agent",
        instruction="현재 날씨를 알려 줄 수 있는 유용한 도우미입니다.",
        tools=[get_weather]
    )
    ```

=== "Java"
    ```java
    // GEMINI_API_KEY 환경 변수를 API 키로 설정합니다.
    // export GEMINI_API_KEY="YOUR_API_KEY"

    import com.google.adk.agents.LlmAgent;
    import com.google.adk.tools.Annotations.Schema;
    import com.google.adk.tools.FunctionTool;

    LlmAgent weatherAgent = LlmAgent.builder()
        .model("gemma-4-31b-it")
        .name("weather_agent")
        .instruction("""
            현재 날씨를 알려 줄 수 있는 유용한 도우미입니다.
        """)
        .tools(FunctionTool.create(this, "getWeather"))
        .build();

    @Schema(
        name = "getWeather",
        description = "지정한 위치의 날씨 예보를 가져옵니다."
    )
    public Map<String, String> getWeather(
        @Schema(
            name = "location",
            description = "날씨 예보를 조회할 위치"
        )
        String location
    ) {
        return Map.of(
            "forecast",
            "위치: " + location + ". 날씨: 맑음, 화씨 76도, 풍속 8mph."
        );
    }
    ```

## vLLM 예시

이러한 서비스의 Gemma 4 엔드포인트에 액세스하려면 Python용 [LiteLLM](/agents/models/litellm/) 라이브러리와 Java용 [LangChain4j](https://docs.langchain4j.dev/)를 통해 vLLM 모델을 사용할 수 있습니다.

다음 예시는 ADK 에이전트에서 Gemma 4 vLLM 엔드포인트를 사용하는 방법을 보여 줍니다.

### 설정

1. **모델 배포:** 원하는 모델을
    [Vertex AI](https://console.cloud.google.com/vertex-ai/publishers/google/model-garden/gemma4),
    [Google Kubernetes Engine](https://docs.cloud.google.com/kubernetes-engine/docs/tutorials/serve-gemma-gpu-vllm),
    또는 [Cloud Run](https://docs.cloud.google.com/run/docs/run-gemma-on-cloud-run)에 배포하고,
    OpenAI 호환 API 엔드포인트를 사용합니다.
    API 기본 URL에는 `/v1`이 포함되어야 합니다(예: `https://your-vllm-endpoint.run.app/v1`).
    * *ADK 도구에 중요:* 배포 시 서빙 도구가 호환되는 tool/function calling과 reasoning parser를 지원하고 활성화하는지 확인하세요.
2. **인증:** 엔드포인트에서 인증을 처리하는 방식을 결정합니다(예: API key, bearer token).

### 코드

=== "Python"
    ```python
    import subprocess
    from google.adk.agents import LlmAgent
    from google.adk.models.lite_llm import LiteLlm

    # --- vLLM 엔드포인트에 호스팅된 모델을 사용하는 예시 에이전트 ---

    # 모델 배포에서 제공하는 엔드포인트 URL
    api_base_url = "https://your-vllm-endpoint.run.app/v1"

    # 사용 중인 vLLM 엔드포인트 구성에서 인식하는 모델 이름
    model_name_at_endpoint = "openai/google/gemma-4-31B-it"

    # 간단히 사용해 볼 도구
    def get_weather(location: str) -> str:
        return f"위치: {location}. 날씨: 맑음, 화씨 76도, 풍속 8mph."

    # 인증 예시: Cloud Run 배포에서 gcloud identity token 사용
    # 엔드포인트 보안 방식에 맞게 조정하세요.
    try:
        gcloud_token = subprocess.check_output(
            ["gcloud", "auth", "print-identity-token", "-q"]
        ).decode().strip()
        auth_headers = {"Authorization": f"Bearer {gcloud_token}"}
    except Exception as e:
        print(f"경고: gcloud 토큰을 가져올 수 없습니다 - {e}.")
        auth_headers = None  # 또는 적절히 오류를 처리하세요.

    root_agent = LlmAgent(
        model=LiteLlm(
            model=model_name_at_endpoint,
            api_base=api_base_url,
            # 필요한 경우 인증 헤더를 전달합니다.
            extra_headers=auth_headers,
            # 엔드포인트가 API 키를 사용한다면 다음과 같이 지정할 수도 있습니다.
            # api_key="YOUR_ENDPOINT_API_KEY",
            extra_body={
                "chat_template_kwargs": {
                    "enable_thinking": True  # 사고 기능 사용
                },
                "skip_special_tokens": False  # False로 설정해야 합니다.
            },
        ),
        name="weather_agent",
        instruction="현재 날씨를 알려 줄 수 있는 유용한 도우미입니다.",
        tools=[get_weather],  # 도구 등록
    )
    ```

=== "Java"
    vLLM에 호스팅된 Gemma를 사용하려면 OpenAI 호환 라이브러리를 사용해야 합니다.
    LangChain4j는 `pom.xml`에 추가할 수 있는 OpenAI 의존성을 제공합니다.

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

    OpenAI 호환 채팅 모델(스트리밍 또는 비스트리밍)을 만든 뒤 `LangChain4j` 래퍼로 감싸서 `LlmAgent`에 전달합니다.

    ```java
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.models.langchain4j.LangChain4j;
    import com.google.adk.tools.Annotations.Schema;
    import com.google.adk.tools.FunctionTool;
    import dev.langchain4j.model.chat.StreamingChatModel;
    import dev.langchain4j.model.openai.OpenAiStreamingChatModel;

    // 모델 배포에서 제공하는 엔드포인트 URL
    String apiBaseUrl = "https://your-vllm-endpoint.run.app/v1";

    // 사용 중인 vLLM 엔드포인트 구성에서 인식하는 모델 이름
    String gemmaModelName = "gg-hf-gg/gemma-4-31b-it";

    // 먼저 LangChain4j로 OpenAI 호환 채팅 모델을 정의합니다.
    StreamingChatModel model =
        OpenAiStreamingChatModel.builder()
            .modelName(gemmaModelName)
            // 엔드포인트에 API 키가 필요하다면 사용하세요.
            // .apiKey("YOUR_ENDPOINT_API_KEY")
            .baseUrl(apiBaseUrl)
            .customParameters(
                Map.of(
                    "skip_special_tokens", false,
                    "chat_template_kwargs", Map.of("enable_thinking", true)
                )
            )
            .build();

    // LangChain4j 래퍼 모델로 에이전트를 구성합니다.
    LlmAgent weatherAgent = LlmAgent.builder()
        .model(new LangChain4j(model))
        .name("weather_agent")
        .instruction("""
            현재 날씨를 알려 줄 수 있는 유용한 도우미입니다.
        """)
        .tools(FunctionTool.create(this, "getWeather"))
        .build();

    @Schema(
        name = "getWeather",
        description = "지정한 위치의 날씨 예보를 가져옵니다."
    )
    public Map<String, String> getWeather(
        @Schema(
            name = "location",
            description = "날씨 예보를 조회할 위치"
        )
        String location
    ) {
        return Map.of(
            "forecast",
            "위치: " + location + ". 날씨: 맑음, 화씨 76도, 풍속 8mph."
        );
    }
    ```

## Gemma 4, ADK, Google Maps MCP로 음식 투어 에이전트 만들기
이 샘플은 Gemma 4, ADK, Google Maps MCP 서버를 사용해 개인화된 음식 투어 에이전트를 만드는 방법을 보여 줍니다. 에이전트는 사용자가 제공한 음식 사진 또는 텍스트 설명, 위치, 선택적 예산을 바탕으로 먹을 곳을 추천하고 도보 경로로 정리합니다.

### 사전 요구 사항

- [Google AI Studio](https://aistudio.google.com/app/apikey)에서 API 키를 받습니다.
  `GEMINI_API_KEY` 환경 변수를 Gemini API 키로 설정하세요.
- Google Cloud Console에서 [Google Maps API](https://console.cloud.google.com/maps-api/)를 사용 설정합니다.
- [Google Maps Platform API 키](https://console.cloud.google.com/maps-api/credentials)를 만듭니다.
  `MAPS_API_KEY` 환경 변수를 API 키로 설정하세요.
- ADK를 설치하고 Python 환경에서 구성하거나 Java 프로젝트에서 Java 종속성을 구성합니다.

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
