---
catalog_title: CopilotKit
catalog_description: 에이전트에 React, Angular, Vue, 모바일 및 Slack 프론트엔드 추가
catalog_icon: /integrations/assets/copilotkit.png
---

# ADK용 CopilotKit 사용자 인터페이스

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span>
</div>

[CopilotKit](https://github.com/CopilotKit/CopilotKit)은 [AG-UI](/integrations/ag-ui/)를 통해 애플리케이션을 에이전트에 연결하는 오픈소스 프론트엔드 라이브러리 및 런타임 모음입니다. ADK에서는 `ag-ui-adk` 패키지를 통해 에이전트를 AG-UI 엔드포인트로 노출하고, CopilotKit은 해당 엔드포인트에 React, Angular, Vue, React Native 또는 Slack에서 사용할 수 있는 채팅 화면, 프론트엔드 도구, 생성형 UI(Generative UI), HITL(Human-in-the-Loop) 컨트롤을 제공합니다.

[AG-UI 통합 페이지](/integrations/ag-ui/)에서 프로토콜과 풀스택 샘플을 스캐폴딩하는 `create` 명령어를 다룹니다. 이 페이지에서는 기존 ADK 프로젝트에 CopilotKit을 추가하는 방법을 설명합니다.

## 주요 사용 사례

- **채팅 인터페이스**: ADK 에이전트의 메시지, 도구 호출, 추론 과정을 웹이나 모바일 앱용 패키지형 채팅 컴포넌트로 스트리밍합니다.
- **프론트엔드 도구**: 에이전트가 탐색, 레코드 열기, 애플리케이션 상태 읽기 등 브라우저에서 실행되는 함수를 호출할 수 있도록 합니다.
- **생성형 UI**: 도구 호출과 결과를 단순 텍스트 대신 애플리케이션 컴포넌트로 렌더링합니다.
- **HITL (Human-in-the-Loop)**: 사용자가 제안된 작업을 승인, 수정 또는 거부할 때까지 에이전트 실행을 일시 중지한 다음, 응답과 함께 재개합니다.
- **메시징 채널**: 오픈소스 Channels SDK를 사용하여 Slack에서 동일한 에이전트를 실행합니다.

## 사전 요구사항

- Python 3.10 ~ 3.14 및 Node.js 18 이상
- [Google AI Studio](https://aistudio.google.com/app/apikey)의 Gemini API 키 (`GOOGLE_API_KEY` 환경 변수로 내보내기)
- 아래 프론트엔드 단계를 위한 React 애플리케이션 (예: Next.js)

## 설치

백엔드 패키지 설치:

```bash
pip install google-adk ag-ui-adk fastapi "uvicorn[standard]"
```

웹 애플리케이션에 프론트엔드 패키지 설치:

```bash
npm install @copilotkit/react-core @copilotkit/runtime @ag-ui/client hono zod
```

## 에이전트와 함께 사용

### 1. AG-UI를 통해 에이전트 노출

```python title="agent.py"
from fastapi import FastAPI
from google.adk.agents import Agent
from google.adk.apps import App, ResumabilityConfig

from ag_ui_adk import ADKAgent, AGUIToolset, add_adk_fastapi_endpoint

root_agent = Agent(
    model="gemini-flash-latest",
    name="copilotkit_agent",
    instruction=(
        "You are a helpful assistant. Use the frontend tools when they fit "
        "the request."
    ),
    tools=[AGUIToolset()],
)

adk_app = App(
    name="copilotkit_app",
    root_agent=root_agent,
    resumability_config=ResumabilityConfig(is_resumable=True),
)

ag_ui_agent = ADKAgent.from_app(
    adk_app,
    user_id="local_user",
    use_in_memory_services=True,
)

app = FastAPI()
add_adk_fastapi_endpoint(app, ag_ui_agent, path="/ag-ui")
```

`AGUIToolset()` 도구 모음은 프론트엔드에 등록된 도구를 에이전트가 호출할 수 있게 합니다. `ADKAgent.from_app()`과 `ResumabilityConfig`로 미들웨어를 생성하면 프론트엔드 도구 호출 시 실행을 일시 정지하고 결과가 도착했을 때 재개할 수 있습니다.

백엔드 시작:

```bash
uvicorn agent:app --reload --port 8000
```

### 2. CopilotKit Runtime에 엔드포인트 등록

CopilotKit Runtime은 웹 애플리케이션 내부에서 실행되며 AG-UI 실행을 ADK 엔드포인트로 전달합니다. Next.js 앱의 경우 라우트를 추가합니다:

```typescript title="app/api/copilotkit/[[...slug]]/route.ts"
import { HttpAgent } from "@ag-ui/client";
import {
  CopilotRuntime,
  InMemoryAgentRunner,
  createCopilotEndpoint,
} from "@copilotkit/runtime/v2";
import { handle } from "hono/vercel";

const runtime = new CopilotRuntime({
  agents: {
    default: new HttpAgent({
      url: process.env.ADK_AG_UI_URL ?? "http://localhost:8000/ag-ui",
    }),
  },
  runner: new InMemoryAgentRunner(),
});

const app = createCopilotEndpoint({
  runtime,
  basePath: "/api/copilotkit",
});

export const GET = handle(app);
export const POST = handle(app);
export const PATCH = handle(app);
export const DELETE = handle(app);
```

### 3. 채팅 UI 렌더링

React 트리의 루트 근처에 Provider를 한 번 마운트한 다음, 그 아래 어느 위치에든 채팅 컴포넌트를 배치합니다:

```tsx title="app/providers.tsx"
"use client";

import { CopilotKit } from "@copilotkit/react-core/v2";
import "@copilotkit/react-core/v2/styles.css";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <CopilotKit runtimeUrl="/api/copilotkit" useSingleEndpoint={false}>
      {children}
    </CopilotKit>
  );
}
```

```tsx title="app/page.tsx"
"use client";

import { CopilotChat } from "@copilotkit/react-core/v2";

export default function Page() {
  return (
    <main style={{ height: "100vh" }}>
      <CopilotChat agentId="default" />
    </main>
  );
}
```

`CopilotChat` 컴포넌트는 메시지 상태 관리, 스트리밍, 도구 호출 표시, 첨부 파일 및 추천 질문을 처리합니다.

### 4. 프론트엔드 도구 추가

브라우저에서 도구를 등록합니다. ADK 측의 `AGUIToolset()`은 매 실행마다 이 도구를 에이전트에 노출합니다:

```tsx title="app/SearchTool.tsx"
"use client";

import { useFrontendTool } from "@copilotkit/react-core/v2";
import { z } from "zod";

export function SearchTool() {
  useFrontendTool({
    name: "searchDocs",
    description: "Search the current application documentation.",
    parameters: z.object({
      query: z.string(),
    }),
    handler: async ({ query }) => {
      const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
      return response.text();
    },
  });

  return null;
}
```

`<SearchTool />`을 Provider 아래, `<CopilotChat />` 옆에 렌더링합니다.

## 사용 가능한 훅 (Hooks)

훅 | 설명
---- | -----------
`useFrontendTool` | 브라우저에서 실행되고 결과를 에이전트에 반환하는 도구 등록
`useRenderTool` | 백엔드 도구의 진행 상황 및 결과를 이름별로 렌더링
`useComponent` | 에이전트가 채팅에 배치할 수 있는 렌더링 전용 컴포넌트 등록
`useHumanInTheLoop` | 실행이 계속되기 전에 UI에서 반드시 `respond()`를 호출해야 하는 도구 등록
`useAgentContext` | 매 실행마다 애플리케이션 상태를 컨텍스트로 에이전트와 공유
`useAgent` | 커스텀 채팅 화면 구축 시 메시지, 상태, 실행 상태 읽기

모든 훅은 `@copilotkit/react-core/v2`에서 export됩니다. 매개변수 및 반환 값에 대한 자세한 내용은 [CopilotKit 훅 참조](https://docs.copilotkit.ai/reference/hooks/useFrontendTool)를 참조하세요.

## 기타 클라이언트

동일한 CopilotKit Runtime 라우트와 ADK 엔드포인트가 모든 CopilotKit 클라이언트를 지원합니다:

- **Angular**: `provideCopilotKit()` 및 `<copilot-chat>` 컴포넌트가 포함된 `@copilotkit/angular` 패키지. [Angular 가이드](https://docs.copilotkit.ai/angular)를 참조하세요.
- **Vue**: `CopilotKitProvider` 및 `CopilotChat`이 포함된 `@copilotkit/vue` 패키지. [Vue 가이드](https://docs.copilotkit.ai/vue)를 참조하세요.
- **React Native**: 헤드리스 훅 및 `@copilotkit/react-native/components` 아래의 선택적 패키지형 채팅이 포함된 `@copilotkit/react-native` 패키지. [React Native 가이드](https://docs.copilotkit.ai/react-native)를 참조하세요.

## 메시징 채널

오픈소스 Channels SDK는 Slack 워크스페이스를 `ag-ui-adk` 엔드포인트에 직접 연결합니다. CopilotKit Runtime 라우트가 필요하지 않습니다:

```bash
npm install @copilotkit/bot @copilotkit/bot-slack @copilotkit/bot-ui
```

```typescript title="slack-bot.ts"
import { createBot } from "@copilotkit/bot";
import {
  defaultSlackContext,
  defaultSlackTools,
  SanitizingHttpAgent,
  slack,
} from "@copilotkit/bot-slack";

const bot = createBot({
  adapters: [
    slack({
      botToken: process.env.SLACK_BOT_TOKEN!,
      appToken: process.env.SLACK_APP_TOKEN!,
    }),
  ],
  agent: (threadId) => {
    const agent = new SanitizingHttpAgent({
      url: process.env.ADK_AG_UI_URL ?? "http://localhost:8000/ag-ui",
    });
    agent.threadId = threadId;
    return agent;
  },
  tools: [...defaultSlackTools],
  context: [...defaultSlackContext],
});

bot.onMention(({ thread }) => thread.runAgent());

await bot.start();
```

어댑터는 기본적으로 소켓 모드(Socket Mode)에서 실행되므로 로컬 개발 시 앱 수준 토큰만 있으면 되며 공용 URL은 필요하지 않습니다. 각 Slack 스레드는 하나의 AG-UI 스레드에 매핑되며, Block Kit 렌더링, 상호작용, 승인은 어댑터에 의해 처리됩니다. Slack 앱 설정 및 자체 호스팅 배포에 대한 자세한 내용은 [Channels 문서](https://docs.copilotkit.ai/slack)를 참조하세요.

## 추가 리소스

- [ADK용 CopilotKit 문서](https://docs.copilotkit.ai/adk)
- [GitHub의 CopilotKit](https://github.com/CopilotKit/CopilotKit)
- [PyPI의 AG-UI용 ADK 미들웨어 (`ag-ui-adk`)](https://pypi.org/project/ag-ui-adk/)
- [ADK 미들웨어 소스 코드](https://github.com/ag-ui-protocol/ag-ui/tree/main/integrations/adk-middleware)
- [AG-UI Dojo](https://dojo.ag-ui.com) (라이브 ADK 예제 제공)
