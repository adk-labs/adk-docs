---
catalog_title: StackOne
catalog_description: 에이전트를 200개 이상의 SaaS 제공업체에 연결합니다
catalog_icon: /integrations/assets/stackone.png
catalog_tags: ["connectors"]
---

# ADK용 StackOne 플러그인

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[StackOne ADK Plugin](https://github.com/StackOneHQ/stackone-adk-plugin)은
ADK 에이전트를 [StackOne](https://stackone.com)의 통합 AI 통합 게이트웨이를 통해
수백 개의 제공업체에 연결합니다. 각 API마다 도구 함수를 수동으로 정의하는 대신,
이 플러그인은 연결된 제공업체에서 사용 가능한 도구를 동적으로 탐지하여 ADK의
네이티브 도구로 노출합니다. HRIS, ATS, CRM, 생산성 및 일정 관리 도구를 비롯해
더 많은 [통합](https://www.stackone.com/connectors)을 지원합니다.

## 사용 사례

- **영업 및 수익 운영:** CRM(예: HubSpot, Salesforce)에서 리드를 찾고, 연락처
  데이터를 보강하고, 개인화된 아웃리치를 작성하고, 활동을 다시 기록하는 에이전트를
  하나의 대화 안에서 구축할 수 있습니다.

- **People Operations:** ATS(예: Greenhouse, Ashby)에서 후보자를 선별하고,
  일정 도구(예: Google Calendar, Calendly)에서 가용성을 확인하며, 면접 평가표를
  수집하고, 지원자를 파이프라인 단계 사이에서 이동시키고, HRIS(예: BambooHR,
  Workday)로 온보딩을 자동화하는 에이전트를 만들어 전 직원 생애주기를 수작업 없이
  처리할 수 있습니다.

- **마케팅 자동화:** CRM의 오디언스 세그먼트를 이메일 플랫폼(예: Mailchimp,
  Klaviyo)으로 동기화하고, 이메일 시퀀스를 트리거하며, 채널 전반의 참여 지표를
  보고하는 캠페인 에이전트를 구축할 수 있습니다.

- **제품 전달:** 지원 도구(예: Intercom, Zendesk, Slack)에서 들어오는 피드백을
  분류하고, 프로젝트 관리 도구(예: Linear, Jira)에 이슈를 생성 및 우선순위화하며,
  옵저버빌리티 플랫폼(예: PagerDuty, Datadog)의 인사이트를 활용해 사고를
  해결하는 에이전트를 구축하여 제품 조사, 전달, 신뢰성을 단일 워크플로로
  연결할 수 있습니다.

## 전제 조건

- 최소 하나의 제공업체가 연결된 [StackOne 계정](https://app.stackone.com)
- [StackOne Dashboard](https://app.stackone.com)에서 발급한 StackOne API 키
- [Gemini API 키](https://aistudio.google.com/apikey)

## 설치

```bash
pip install stackone-adk
```

또는 `uv` 사용 시:

```bash
uv add stackone-adk
```

## 에이전트와 함께 사용

!!! tip "환경 변수"

    아래 예제를 실행하기 전에 API 키를 환경 변수로 설정하세요.

    ```bash
    export STACKONE_API_KEY="your-stackone-api-key"
    export GOOGLE_API_KEY="your-google-api-key"
    ```

    `STACKONE_API_KEY`가 설정되면 플러그인이 이를 자동으로 읽고 연결된 계정을 탐지합니다.

=== "Python"

    === "App과 함께 사용(권장)"

        ```python
        import asyncio

        from google.adk.agents import Agent
        from google.adk.apps import App
        from google.adk.runners import InMemoryRunner
        from stackone_adk import StackOnePlugin


        async def main():
            plugin = StackOnePlugin()
            # 특정 계정으로 범위를 제한할 수도 있습니다:
            # plugin = StackOnePlugin(account_id="YOUR_ACCOUNT_ID")

            tools = plugin.get_tools()
            print(f"Discovered {len(tools)} tools")

            agent = Agent(
                model="gemini-flash-latest",
                name="scheduling_agent",
                description="Manages scheduling, HR, and CRM through StackOne.",
                instruction=(
                    "You are a helpful assistant powered by StackOne. "
                    "You help users manage their scheduling, HR, and CRM tasks "
                    "by using the available tools.\n\n"
                    "Always be helpful and provide clear, organized responses."
                ),
                tools=tools,
            )

            app = App(
                name="scheduling_app",
                root_agent=agent,
                plugins=[plugin],
            )

            async with InMemoryRunner(app=app) as runner:
                events = await runner.run_debug(
                    "Get my most recent scheduled meeting from Calendly.",
                    quiet=True,
                )
                # 에이전트의 최종 텍스트 응답 추출
                for event in reversed(events):
                    if event.content and event.content.parts:
                        text_parts = [p.text for p in event.content.parts if p.text]
                        if text_parts:
                            print("".join(text_parts))
                            break


        asyncio.run(main())
        ```

    === "Runner를 직접 사용"

        ```python
        import asyncio

        from google.adk.agents import Agent
        from google.adk.runners import InMemoryRunner
        from stackone_adk import StackOnePlugin


        async def main():
            plugin = StackOnePlugin()
            # 특정 계정으로 범위를 제한할 수도 있습니다:
            # plugin = StackOnePlugin(account_id="YOUR_ACCOUNT_ID")

            tools = plugin.get_tools()
            print(f"Discovered {len(tools)} tools")

            agent = Agent(
                model="gemini-flash-latest",
                name="scheduling_agent",
                description="Manages scheduling, HR, and CRM through StackOne.",
                instruction=(
                    "You are a helpful assistant powered by StackOne. "
                    "You help users manage their scheduling, HR, and CRM tasks "
                    "by using the available tools.\n\n"
                    "Always be helpful and provide clear, organized responses."
                ),
                tools=tools,
            )

            async with InMemoryRunner(
                app_name="scheduling_app", agent=agent
            ) as runner:
                events = await runner.run_debug(
                    "Get my most recent scheduled meeting from Calendly.",
                    quiet=True,
                )
                # 에이전트의 최종 텍스트 응답 추출
                for event in reversed(events):
                    if event.content and event.content.parts:
                        text_parts = [p.text for p in event.content.parts if p.text]
                        if text_parts:
                            print("".join(text_parts))
                            break


        asyncio.run(main())
        ```

## 검색 및 실행 모드

`mode="search_and_execute"`를 사용하면 플러그인은 정확히 두 개의 도구,
`tool_search`와 `tool_execute`만 등록합니다. 모델은 전체 카탈로그를 처음부터
보는 대신 런타임에 이 도구들을 사용해 적절한 StackOne 도구를 찾고 호출합니다.

모든 도구 정의를 모델에 등록하면 세 가지 비용이 있습니다.

- **토큰 오버헤드:** 도구 스키마가 프롬프트 토큰을 소비하여 추론에 사용할 수
  있는 토큰을 줄입니다.
- **페이로드 제한:** 큰 카탈로그는 제공업체의 페이로드 제한을 초과할 수 있습니다.
  예를 들어 Gemini는 요청당 함수 선언의 크기와 수에 하드 제한을 적용합니다.
- **선택 정확도:** 도구 후보 집합이 커질수록 비슷한 도구를 구분해야 하므로
  도구 선택 품질이 낮아질 수 있습니다.

이 모드는 카탈로그 크기와 관계없이 등록되는 도구 수를 두 개로 유지합니다.
모델은 런타임에 자연어 쿼리로 적절한 도구를 찾습니다.

이 모드에는 `stackone-adk>=0.2.0`이 필요합니다.

=== "Python"

    ```python
    import asyncio

    from google.adk.agents import Agent
    from google.adk.apps import App
    from google.adk.runners import InMemoryRunner
    from stackone_adk import StackOnePlugin


    async def main():
        plugin = StackOnePlugin(
            mode="search_and_execute",
            account_ids=["YOUR_ACCOUNT_ID"],
            search={"method": "auto", "top_k": 10},
        )

        agent = Agent(
            model="gemini-flash-latest",
            name="stackone_agent",
            description="Connects to multiple SaaS providers through StackOne.",
            instruction=(
                "You are an assistant powered by StackOne. To answer the "
                "user's request, first call tool_search with a short query "
                "to find the right action, then call tool_execute with the "
                "chosen tool name and parameters that match the schema "
                "returned by tool_search."
            ),
            tools=plugin.get_tools(),
        )

        app = App(
            name="stackone_app",
            root_agent=agent,
            plugins=[plugin],
        )

        async with InMemoryRunner(app=app) as runner:
            events = await runner.run_debug(
                "List the first 3 workers.",
                quiet=True,
            )
            for event in reversed(events):
                if event.content and event.content.parts:
                    text_parts = [p.text for p in event.content.parts if p.text]
                    if text_parts:
                        print("".join(text_parts))
                        break


    asyncio.run(main())
    ```

모델은 먼저 자연어 쿼리와 함께 `tool_search`를 호출하고, 이름, 설명,
파라미터 스키마가 포함된 짧은 후보 도구 목록을 받습니다. 그런 다음 모델은
선택한 도구 이름과 스키마에 맞는 파라미터로 `tool_execute`를 호출합니다.
두 호출 모두 SDK를 통해 StackOne의 AI Integration Gateway로 라우팅됩니다.

## 사용 가능한 도구

고정된 도구 세트를 제공하는 통합과 달리 StackOne 도구는 StackOne API를 통해
연결된 제공업체에서 **동적으로 탐지**됩니다. 어떤 도구를 사용할 수 있는지는
[StackOne Dashboard](https://app.stackone.com)에 연결한 SaaS 제공업체에 따라 달라집니다.

탐지된 도구를 나열하려면:

```python
plugin = StackOnePlugin(account_id="YOUR_ACCOUNT_ID") # 선택 사항: 생략하면 연결된 모든 계정 사용
for tool in plugin.get_tools():
    print(f"{tool.name}: {tool.description}")
```

### 지원되는 통합 카테고리

Category | Example providers
-------- | -----------------
HRIS | HiBob, BambooHR, Workday, SAP SuccessFactors, Personio, Gusto
ATS | Greenhouse, Ashby, Lever, Bullhorn, SmartRecruiters, Teamtailor
CRM & Sales | Salesforce, HubSpot, Pipedrive, Zoho CRM, Close, Copper
Marketing | Mailchimp, Klaviyo, ActiveCampaign, Brevo, GetResponse
Ticketing & Support | Zendesk, Freshdesk, Jira, ServiceNow, PagerDuty, Linear
Productivity | Asana, ClickUp, Slack, Microsoft Teams, Notion, Confluence
Scheduling | Calendly, Cal.com
LMS & Learning | 360Learning, Docebo, Go1, Cornerstone, LinkedIn Learning
Commerce | Shopify, BigCommerce, WooCommerce, Etsy
Developer Tools | GitHub, GitLab, Twilio

200개 이상의 지원 제공업체 전체 목록은
[StackOne integrations page](https://www.stackone.com/connectors)를 참조하세요.

## 구성

### 플러그인 파라미터

Parameter | Type | Default | Description
--------- | ---- | ------- | -----------
`api_key` | `str | None` | `None` | StackOne API 키입니다. `STACKONE_API_KEY` 환경 변수로 폴백합니다.
`account_id` | `str | None` | `None` | 모든 도구에 적용할 기본 계정 ID입니다.
`base_url` | `str | None` | `None` | API URL 재정의입니다(기본값: `https://api.stackone.com`).
`plugin_name` | `str` | `"stackone_plugin"` | ADK용 플러그인 식별자입니다.
`providers` | `list[str] | None` | `None` | 제공업체 이름으로 필터링합니다(예: `["calendly", "hibob"]`).
`actions` | `list[str] | None` | `None` | glob 문법을 사용하는 작업 패턴 필터입니다.
`account_ids` | `list[str] | None` | `None` | 특정 연결 계정 ID로 도구 범위를 제한합니다.
`mode` | `Literal["search_and_execute"] | None` | `None` | 도구 등록 전략입니다. `None`이면 탐지된 모든 도구를 에이전트에 등록합니다. `"search_and_execute"`이면 플러그인이 두 도구(`tool_search`, `tool_execute`)를 등록하고, 모델이 런타임에 도구를 선택하고 호출합니다.
`search` | `SearchConfig | None` | `None` | `StackOneToolSet`으로 전달되는 검색 백엔드 구성입니다. `mode="search_and_execute"`일 때 적용됩니다. 해당 모드에서는 기본값이 `{"method": "auto"}`입니다.
`execute` | `ExecuteToolsConfig | None` | `None` | `StackOneToolSet`으로 전달되는 실행 구성입니다.
`timeout` | `float` | `180.0` | HTTP 호출(계정 탐지 및 도구 실행)의 요청별 제한 시간(초)입니다. 느린 커넥터에는 값을 늘리세요.

### 도구 필터링

제공업체, 작업 패턴, 계정 ID 또는 조합으로 도구를 필터링할 수 있습니다.

```python
# 계정 지정
plugin = StackOnePlugin(account_ids=["acct-hibob-1", "acct-bamboohr-1"])

# 읽기 전용 작업
plugin = StackOnePlugin(actions=["*_list_*", "*_get_*"])

# glob 패턴을 사용한 특정 작업
plugin = StackOnePlugin(actions=["calendly_list_events", "calendly_get_event_*"])

# 복합 필터
plugin = StackOnePlugin(
    actions=["*_list_*", "*_get_*"],
    account_ids=["acct-hibob-1"],
)
```

## 추가 리소스

- [StackOne ADK Plugin Repository](https://github.com/StackOneHQ/stackone-adk-plugin)
- [StackOne Documentation](https://docs.stackone.com/)
- [StackOne Dashboard](https://app.stackone.com)
- [StackOne Python AI SDK](https://github.com/StackOneHQ/stackone-ai-python)
