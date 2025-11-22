# Bright Data

[Bright Data MCP 서버](https://github.com/brightdata/brightdata-mcp)는 ADK 에이전트를 Bright Data의 웹 데이터 플랫폼에 연결합니다. 이 도구는 에이전트에게 실시간 웹 검색, 웹페이지 스크래핑, 구조화된 데이터 추출, 원격 브라우저 제어 및 인기 있는 플랫폼의 사전 구축된 데이터 피드 액세스 기능을 제공합니다.

## 사용 사례

- **실시간 웹 검색**: 최적화된 웹 검색을 수행하여 AI 친화적인 형식(JSON/마크다운)으로 최신 정보를 얻습니다.

- **구조화된 데이터 추출**: AI 기반 추출을 사용하여 모든 웹페이지를 선택적 사용자 지정 프롬프트와 함께 깨끗하고 구조화된 JSON 데이터로 변환합니다.

- **브라우저 자동화**: 복잡한 상호 작용, 자바스크립트 렌더링 및 동적 콘텐츠 추출을 위해 실제 브라우저를 원격으로 제어합니다.

- **사전 구축된 데이터 API**: Amazon, LinkedIn, Instagram, TikTok, Google Maps 등을 포함한 인기 있는 플랫폼의 60개 이상의 구조화된 데이터 세트에 액세스합니다.

- **광고 분석**: 업계 표준 광고 차단 필터 목록을 사용하여 웹페이지에서 광고를 추출하고 분석합니다.

## 전제 조건

- API 토큰을 얻으려면 [Bright Data 계정](https://brightdata.com/)에 가입하세요.
- 자세한 내용은 [설명서](https://docs.brightdata.com/mcp-server/overview)를 참조하세요.
- 서버는 프로토타이핑 및 일상적인 워크플로에 유용한 **월 5,000개 요청의 무료 등급**을 제공합니다.

## 에이전트와 함께 사용

=== "로컬 MCP 서버"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from google.adk.tools.mcp_tool import McpToolset
    from mcp import StdioServerParameters

    BRIGHTDATA_API_TOKEN = "YOUR_BRIGHTDATA_API_TOKEN"

    root_agent = Agent(
        model="gemini-1.5-pro",
        name="brightdata_agent",
        instruction="Bright Data를 사용하여 사용자가 웹 데이터에 액세스하도록 돕습니다.",
        tools=[
            McpToolset(
                connection_params=StdioConnectionParams(
                    server_params = StdioServerParameters(
                        command="npx",
                        args=[
                            "@brightdata/mcp",
                        ],
                        env={
                            "API_TOKEN": BRIGHTDATA_API_TOKEN,
                            "PRO_MODE": "true",  # 선택 사항: 60개 이상의 모든 도구 활성화
                        }
                    ),
                    timeout=300,
                ),
            )
        ],
    )
    ```

=== "원격 MCP 서버"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
    from google.adk.tools.mcp_tool import McpToolset

    BRIGHTDATA_API_TOKEN = "YOUR_BRIGHTDATA_API_TOKEN"

    root_agent = Agent(
        model="gemini-1.5-pro",
        name="brightdata_agent",
        instruction="""Bright Data를 사용하여 사용자가 웹 데이터에 액세스하도록 돕습니다.""",
        tools=[
            McpToolset(
                connection_params=StreamableHTTPServerParams(
                    url=f"https://mcp.brightdata.com/mcp?token={BRIGHTDATA_API_TOKEN}",
                ),
            )
        ],
    )
    ```

## 사용 예

에이전트가 설정되고 실행되면 명령줄 인터페이스 또는 웹 인터페이스를 통해 상호 작용할 수 있습니다. 다음은 몇 가지 예입니다.

**샘플 에이전트 프롬프트:**

> Amazon에서 iPhone 15 Pro의 현재 가격과 세부 정보를 알려주세요.

> Google에서 "2025년 기후 변화 뉴스"를 검색하고 상위 5개 결과를 요약하세요.

> techcrunch.com 홈페이지를 스크랩하고 모든 기사 헤드라인과 링크를 추출하세요.

에이전트는 적절한 Bright Data 도구를 자동으로 호출하여 포괄적인 답변을 제공하므로 수동 탐색이나 차단에 대한 걱정 없이 실시간 웹 데이터에 쉽게 액세스할 수 있습니다.

## 사용 가능한 도구

Bright Data MCP 서버는 두 가지 모드로 작동합니다.

### 신속 모드(무료 등급 - 기본값)

도구 <img width="100px"/> | 설명
---- | -----------
`search_engine` | Google, Bing 또는 Yandex SERP를 JSON 또는 마크다운으로 스크랩합니다.
`scrape_as_markdown` | 내장된 차단 해제 기능으로 웹페이지를 깨끗한 마크다운으로 변환합니다.
`scrape_as_html` | 차단기를 우회하면서 웹페이지에서 원시 HTML을 반환합니다.
`extract` | 사용자 지정 프롬프트로 마크다운 출력을 구조화된 JSON으로 변환합니다.
`session_stats` | 세션 사용 통계 및 도구 호출 횟수를 봅니다.

### 프로 모드(60개 이상의 추가 도구)

환경 변수에서 `PRO_MODE=true`를 설정하여 프로 모드를 활성화하면 다음에 액세스할 수 있습니다.

**일괄 작업:**
- `search_engine_batch`: 최대 10개의 검색어를 동시에 실행합니다.
- `scrape_batch`: 최대 10개의 URL을 동시에 스크랩합니다.

**브라우저 자동화:**
- `scraping_browser.*`: 복잡한 상호 작용을 위한 전체 브라우저 제어.
- 탐색, 클릭, 입력, 스크롤, 스크린샷 찍기 등.

**웹 데이터 API(60개 이상의 구조화된 데이터 세트):**

- **전자상거래**: `web_data_amazon_product`, `web_data_walmart_product`, `web_data_ebay_product`, `web_data_etsy_products`, `web_data_bestbuy_products`, `web_data_zara_products`
- **소셜 미디어**: `web_data_linkedin_person_profile`, `web_data_instagram_profiles`, `web_data_facebook_posts`, `web_data_tiktok_profiles`, `web_data_x_posts`, `web_data_reddit_posts`
- **비즈니스 인텔리전스**: `web_data_linkedin_company_profile`, `web_data_crunchbase_company`, `web_data_zoominfo_company_profile`
- **검색 및 리뷰**: `web_data_amazon_product_search`, `web_data_amazon_product_reviews`, `web_data_google_maps_reviews`, `web_data_facebook_company_reviews`
- **지도 및 지역**: `web_data_google_maps_reviews`, `web_data_zillow_properties_listing`, `web_data_booking_hotel_listings`
- **앱 스토어**: `web_data_google_play_store`, `web_data_apple_app_store`
- **미디어 및 뉴스**: `web_data_youtube_videos`, `web_data_youtube_comments`, `web_data_reuter_news`
- **개발자 도구**: `web_data_github_repository_file`
- **금융**: `web_data_yahoo_finance_business`

모든 웹 데이터 API 도구는 캐시되거나 새로운 구조화된 데이터를 JSON 형식으로 반환하며, 종종 실시간 스크래핑보다 더 신뢰할 수 있습니다.

## 구성 옵션

Bright Data MCP 서버는 사용자 지정을 위해 여러 환경 변수를 지원합니다.

변수 | 설명 | 기본값
---- | ---- | ----
`API_TOKEN` | Bright Data API 토큰(필수) | -
`PRO_MODE` | 60개 이상의 모든 고급 도구 활성화 | `false`
`RATE_LIMIT` | 사용자 지정 속도 제한(예: "100/1h", "50/30m") | 제한 없음
`WEB_UNLOCKER_ZONE` | 사용자 지정 웹 언락커 영역 이름 | `mcp_unlocker`
`BROWSER_ZONE` | 사용자 지정 브라우저 API 영역 이름 | `mcp_browser`

## 추가 리소스

- [Bright Data MCP 서버 설명서](https://docs.brightdata.com/mcp-server/overview)
- [Bright Data MCP 서버 리포지토리](https://github.com/brightdata/brightdata-mcp)
- [전체 도구 설명서](https://github.com/brightdata-com/brightdata-mcp/blob/main/assets/Tools.md)
- [사용 예](https://github.com/brightdata-com/brightdata-mcp/blob/main/examples)
- [대화형 플레이그라운드](https://brightdata.com/ai/playground-chat)
