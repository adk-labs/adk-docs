---
catalog_title: Zespan
catalog_description: ADK 에이전트를 추적, 평가, 모니터링하기 위한 에이전트 안정성 플랫폼
catalog_icon: /integrations/assets/zespan_logo.png
catalog_tags: ["observability", "evaluation"]
---

# ADK용 Zespan 관측 가능성 (Observability)

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Zespan](https://zespan.com)은 AI 애플리케이션을 위한 에이전트 안정성 플랫폼입니다. Zespan SDK는 에이전트 호출, 모델 호출, 도구 실행 및 다중 에이전트 위임(delegation)을 연결된 스팬(linked spans)으로 캡처하여 ADK 에이전트를 기본적으로 계측(instrument)하며, 조사를 위해 [Zespan 대시보드](https://app.zespan.com)로 보내 비용 기여 및 평가를 수행합니다.

## 개요

ADK 에이전트가 계측되면 Zespan 플랫폼은 다음을 제공합니다.

- **추적 (Tracing):** 지연 시간, 토큰 및 비용과 함께 모든 에이전트, 모델, 도구 및 위임 스팬을 캡처합니다.
- **비용 할당 (Cost attribution):** 모델, 에이전트 및 기간별로 지출을 분석합니다.
- **평가 (Evaluations):** 커스텀 메트릭, 데이터 세트 및 시뮬레이션을 통해 에이전트 동작을 채점합니다.
- **가드레일 (Guardrails):** 런타임에 안전하지 않은 입력 및 출력을 차단, 편집 또는 플래그 처리합니다.
- **프롬프트 관리 (Prompt management):** 캐싱 및 변수 치환을 통해 프롬프트를 조회하고 버전을 관리합니다.

![Zespan 시스템 상태 대시보드](assets/zespan_overview.png)

## 사전 준비 사항

시작하기 전에 Zespan 계정 및 자격 증명을 설정하세요.

1. [app.zespan.com](https://app.zespan.com)에서 회원 가입을 진행합니다.
2. 프로젝트를 생성하고 **Onboarding → API Key**에서 **API 키**를 복사합니다.
3. 환경 변수를 설정합니다.

   ```bash
   export ZESPAN_API_KEY=<your-zespan-api-key>
   export GOOGLE_API_KEY=<your-google-api-key>
   ```

## 설치

ADK와 함께 Zespan SDK를 설치합니다.

=== "Python"

    ```bash
    pip install zespan google-adk
    ```

=== "TypeScript"

    ```bash
    npm install @zespan/sdk @google/adk
    ```

## 트레이스 전송

추적 캡처를 시작하려면 Zespan SDK로 ADK 에이전트를 계측하세요.

=== "Python"

    시작 시 Zespan을 한 번 초기화한 다음, `ZespanADKCallbackHandler`를 생성하고 해당 `.callbacks`를 `LlmAgent`에 전달합니다.

    ```python
    import asyncio
    import os

    import zespan
    from zespan import ZespanADKCallbackHandler
    from google.adk.agents import LlmAgent
    from google.adk.runners import InMemoryRunner
    from google.genai import types

    zespan.init(api_key=os.environ["ZESPAN_API_KEY"])

    handler = ZespanADKCallbackHandler()


    def get_weather(city: str) -> dict:
        """Retrieves the current weather report for a specified city."""
        if city.lower() == "new york":
            return {
                "status": "success",
                "report": "The weather in New York is sunny with a temperature of 25°C.",
            }
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available.",
        }


    agent = LlmAgent(
        name="weather_agent",
        model="gemini-flash-latest",
        description="Agent to answer weather questions.",
        instruction="Use the available tools to find an answer.",
        tools=[get_weather],
        **handler.callbacks,
    )


    async def main():
        runner = InMemoryRunner(agent=agent, app_name="weather_app")
        await runner.session_service.create_session(
            app_name="weather_app", user_id="user", session_id="session"
        )
        async for event in runner.run_async(
            user_id="user",
            session_id="session",
            new_message=types.Content(
                role="user",
                parts=[types.Part(text="What is the weather in New York?")],
            ),
        ):
            if event.is_final_response():
                print(event.content.parts[0].text.strip())


    if __name__ == "__main__":
        asyncio.run(main())
    ```

=== "TypeScript"

    두 가지 접근 방식을 사용할 수 있습니다.

    **`instrumentADK`**는 코디네이터와 러너를 하나의 호출로 래핑하고 위임을 포함한 전체 이벤트 스트림을 가로챕니다.

    ```typescript
    import { zespan, instrumentADK } from "@zespan/sdk";
    import { LlmAgent, InMemoryRunner } from "@google/adk";

    zespan.init({ apiKey: process.env.ZESPAN_API_KEY! });

    function getWeather(city: string): object {
      if (city.toLowerCase() === "new york") {
        return {
          status: "success",
          report: "The weather in New York is sunny with a temperature of 25°C.",
        };
      }
      return {
        status: "error",
        error_message: `Weather information for '${city}' is not available.`,
      };
    }

    const coordinator = new LlmAgent({
      name: "weather_agent",
      model: "gemini-flash-latest",
      description: "Agent to answer weather questions.",
      instruction: "Use the available tools to find an answer.",
      tools: [getWeather],
    });

    const runner = new InMemoryRunner({
      agent: coordinator,
      appName: "weather_app",
    });

    const { runner: tracedRunner } = instrumentADK({ coordinator, runner });

    for await (const event of tracedRunner.runEphemeral({
      userId: "user",
      newMessage: { parts: [{ text: "What is the weather in New York?" }] },
    })) {
      if (event.isFinalResponse()) {
        console.log(event.content.parts[0].text);
      }
    }
    ```

    **`ZespanADKCallbackHandler`**는 ADK의 기본 콜백 시스템을 사용합니다. 에이전트 구성에 `.callbacks`를 분산하여 전달하세요.

    ```typescript
    import { zespan, ZespanADKCallbackHandler } from "@zespan/sdk";
    import { LlmAgent, InMemoryRunner } from "@google/adk";

    zespan.init({ apiKey: process.env.ZESPAN_API_KEY! });

    const handler = new ZespanADKCallbackHandler();

    const agent = new LlmAgent({
      name: "weather_agent",
      model: "gemini-flash-latest",
      description: "Agent to answer weather questions.",
      instruction: "Use the available tools to find an answer.",
      tools: [getWeather],
      ...handler.callbacks,
    });

    const runner = new InMemoryRunner({ agent, appName: "weather_app" });

    for await (const event of runner.runEphemeral({
      userId: "user",
      newMessage: { parts: [{ text: "What is the weather in New York?" }] },
    })) {
      if (event.isFinalResponse()) {
        console.log(event.content.parts[0].text);
      }
    }
    ```

## 다중 에이전트 시스템

Zespan은 코디네이터와 서브 에이전트 스팬을 단일 트레이스로 연결합니다.

=== "Python"

    코디네이터와 모든 서브 에이전트에서 **동일한 핸들러 인스턴스**를 사용합니다. 스팬은 공유된 ADK 호출 ID를 통해 단일 트레이스 아래에 연결됩니다.

    ```python
    handler = ZespanADKCallbackHandler()

    specialist = LlmAgent(
        name="lookup_agent",
        model="gemini-flash-latest",
        tools=[lookup_tool],
        **handler.callbacks,
    )

    coordinator = LlmAgent(
        name="coordinator",
        model="gemini-flash-latest",
        sub_agents=[specialist],
        **handler.callbacks,
    )
    ```

=== "TypeScript"

    `instrumentADK`를 사용하면 모든 `subAgents`가 재귀적으로 자동으로 래핑됩니다.

    ```typescript
    const specialist = new LlmAgent({
      name: "lookup_agent",
      model: "gemini-flash-latest",
      tools: [lookupTool],
    });

    const coordinator = new LlmAgent({
      name: "coordinator",
      model: "gemini-flash-latest",
      subAgents: [specialist],
    });

    const { runner: tracedRunner } = instrumentADK({
      coordinator,
      runner: new InMemoryRunner({ agent: coordinator, appName: "my_app" }),
    });
    ```

    `ZespanADKCallbackHandler`를 사용하면 동일한 인스턴스를 모든 에이전트에 전달합니다.

    ```typescript
    const handler = new ZespanADKCallbackHandler();

    const specialist = new LlmAgent({
      name: "lookup_agent",
      model: "gemini-flash-latest",
      tools: [lookupTool],
      ...handler.callbacks,
    });

    const coordinator = new LlmAgent({
      name: "coordinator",
      model: "gemini-flash-latest",
      subAgents: [specialist],
      ...handler.callbacks,
    });
    ```

## 대시보드에서 트레이스 확인

에이전트를 실행한 다음 [app.zespan.com](https://app.zespan.com)에서 프로젝트를 엽니다. 각 ADK 실행은 다음을 보여주는 계층적 트레이스를 생성합니다.

- 코디네이터와 서브 에이전트 간의 지연 시간 및 위임 링크가 포함된 에이전트 스팬
- 토큰 수, 비용, 종료 이유 및 선택적 프롬프트/완료 텍스트가 포함된 LLM 스팬
- 입력 인자 및 반환 값을 포함하는 도구 스팬

![Zespan ADK 트레이스 목록](assets/zespan_traces.png)

## 리소스

- [Zespan 공식 홈페이지](https://zespan.com)
- [PyPI의 `zespan`](https://pypi.org/project/zespan/)
- [npm의 `@zespan/sdk`](https://www.npmjs.com/package/@zespan/sdk)
- [Zespan 문서](https://docs.zespan.com)
