---
hide:
  - toc
---
# AG-UI 및 CopilotKit으로 채팅 경험 구축

에이전트 개발자라면 사용자가 풍부하고 반응성이 뛰어난 인터페이스를 통해 에이전트와 상호작용하기를 바랄 것입니다. 하지만 스트리밍 이벤트와 클라이언트 상태까지 지원하는 UI를 처음부터 직접 구축하려면 많은 노력이 필요합니다. [AG-UI](https://docs.ag-ui.com/)는 바로 이러한 문제를 해결하여 에이전트와 직접 연결된 풍부한 사용자 경험을 제공하기 위해 설계되었습니다.

[AG-UI](https://github.com/ag-ui-protocol/ag-ui)는 모바일과 웹은 물론 명령줄(CLI)에 이르기까지 다양한 기술 스택 전반에서 풍부한 클라이언트를 구현할 수 있도록 일관된 인터페이스를 제공합니다. 현재 AG-UI를 지원하는 다양한 클라이언트가 제공됩니다.

- [CopilotKit](https://copilotkit.ai)은 에이전트를 웹 애플리케이션과 긴밀하게 통합하기 위한 도구와 컴포넌트를 제공합니다.
- [Kotlin](https://github.com/ag-ui-protocol/ag-ui/tree/main/sdks/community/kotlin), [Java](https://github.com/ag-ui-protocol/ag-ui/tree/main/sdks/community/java), [Go](https://github.com/ag-ui-protocol/ag-ui/tree/main/sdks/community/go/example/client) 클라이언트 및 TypeScript 기반 [CLI 구현](https://github.com/ag-ui-protocol/ag-ui/tree/main/apps/client-cli-example/src)

이 튜토리얼에서는 CopilotKit을 사용하여 AG-UI의 주요 기능을 살펴볼 수 있는 ADK 에이전트 기반 샘플 앱을 만들어 봅니다.

## 빠른 시작

시작하려면 ADK 에이전트와 간단한 웹 클라이언트가 있는 샘플 애플리케이션을 만들어 보겠습니다.

```
npx create-ag-ui-app@latest --adk
```

### 채팅

채팅은 에이전트와 상호작용하는 친숙한 인터페이스이며, AG-UI는 사용자와 에이전트 간의 스트리밍 메시지를 처리합니다.

```tsx title="src/app/page.tsx"
<CopilotSidebar
  clickOutsideToClose={false}
  defaultOpen={true}
  labels={{
    title: "팝업 도우미",
    initial: "👋 안녕하세요! 에이전트와 채팅 중입니다. 이 에이전트에는 시작하는 데 도움이 되는 몇 가지 도구가 함께 제공됩니다..."
  }}
/>
```

채팅 UI에 대한 자세한 내용은 [CopilotKit 문서](https://docs.copilotkit.ai/adk/agentic-chat-ui)에서 확인하세요.

### 도구 기반 생성형 UI(도구 렌더링)

AG-UI를 사용하면 생성형 UI에 도구 호출 정보를 전달하여 사용자에게 시각적으로 렌더링할 수 있습니다.

```tsx title="src/app/page.tsx"
useCopilotAction({
  name: "get_weather",
  description: "지정된 위치의 날씨를 가져옵니다.",
  available: "disabled",
  parameters: [
    { name: "location", type: "string", required: true },
  ],
  render: ({ args }) => {
    return <WeatherCard location={args.location} themeColor={themeColor} />
  },
});
```

도구 기반 생성형 UI에 대한 자세한 내용은 [CopilotKit 문서](https://docs.copilotkit.ai/adk/generative-ui/tool-based)에서 확인하세요.

### 공유 상태

ADK 에이전트는 상태를 가질 수 있으며, 에이전트와 UI 간에 이 상태를 동기화하면 강력하고 매끄러운 사용자 경험을 구현할 수 있습니다. 상태는 양방향으로 동기화되므로 사용자가 변경한 내용이나 애플리케이션의 다른 부분에서 발생한 변경 사항을 에이전트가 자동으로 인식합니다.

```tsx title="src/app/page.tsx"
const { state, setState } = useCoAgent<AgentState>({
  name: "my_agent",
  initialState: {
    proverbs: [
      "CopilotKit은 새로울 수 있지만 빵 이후 최고의 발명품입니다.",
    ],
  },
})
```

공유 상태에 대한 자세한 내용은 [CopilotKit 문서](https://docs.copilotkit.ai/adk/shared-state)에서 확인하세요.

### 사용해 보세요!

```
npm install && npm run dev
```

## 리소스

AG-UI를 사용하여 UI에 구현할 수 있는 다른 기능은 CopilotKit 문서를 참고하세요.

- [에이전트 기반 생성형 UI](https://docs.copilotkit.ai/adk/generative-ui/agentic)
- [Human in the Loop](https://docs.copilotkit.ai/adk/human-in-the-loop/agent)
- [프런트엔드 액션](https://docs.copilotkit.ai/adk/frontend-actions)

또는 [AG-UI Dojo](https://dojo.ag-ui.com)에서 직접 체험해 보세요.
