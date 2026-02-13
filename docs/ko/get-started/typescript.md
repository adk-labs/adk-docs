# ADK TypeScript 빠른 시작

이 가이드는 TypeScript용 Agent Development Kit(ADK) 사용을 시작하고 실행하는 방법을 보여줍니다.
시작하기 전에 다음 항목을 설치했는지 확인하세요.

*   Node.js 24.13.0 이상
*   Node Package Manager (npm) 11.8.0 이상

## 에이전트 프로젝트 생성

프로젝트용 빈 `my-agent` 디렉터리를 생성합니다.

```none
my-agent/
```

??? tip "명령줄로 프로젝트 구조 생성하기"

    === "MacOS / Linux"

        ```bash
        mkdir -p my-agent/
        ```

    === "Windows"

        ```console
        mkdir my-agent
        ```

### 프로젝트 및 의존성 구성

`npm` 도구를 사용해 프로젝트 의존성을 설치합니다.
여기에는 패키지 파일, ADK TypeScript 메인 라이브러리, 개발 도구가 포함됩니다.
`my-agent/` 디렉터리에서 아래 명령을 실행해 `package.json`을 생성하고 의존성을 설치합니다.

```console
cd my-agent/
# ES 모듈로 프로젝트 초기화
npm init --yes
npm pkg set type="module"
npm pkg set main="agent.ts"
# ADK 라이브러리 설치
npm install @google/adk
# 개발 도구를 dev dependency로 설치
npm install -D @google/adk-devtools
```

### 에이전트 코드 정의

`getCurrentTime`이라는 [Function Tool](/adk-docs/tools/function-tools/)의 간단한 구현을 포함한
기본 에이전트 코드를 만듭니다.
프로젝트 디렉터리에 `agent.ts`를 만들고 다음 코드를 추가합니다.

```typescript title="my-agent/agent.ts"
import {FunctionTool, LlmAgent} from '@google/adk';
import {z} from 'zod';

/* Mock tool implementation */
const getCurrentTime = new FunctionTool({
  name: 'get_current_time',
  description: 'Returns the current time in a specified city.',
  parameters: z.object({
    city: z.string().describe("The name of the city for which to retrieve the current time."),
  }),
  execute: ({city}) => {
    return {status: 'success', report: `The current time in ${city} is 10:30 AM`};
  },
});

export const rootAgent = new LlmAgent({
  name: 'hello_time_agent',
  model: 'gemini-2.5-flash',
  description: 'Tells the current time in a specified city.',
  instruction: `You are a helpful assistant that tells the current time in a city.
                Use the 'getCurrentTime' tool for this purpose.`,
  tools: [getCurrentTime],
});
```

### API 키 설정

이 프로젝트는 Gemini API를 사용하므로 API 키가 필요합니다.
Gemini API 키가 없다면 [API 키 페이지](https://aistudio.google.com/app/apikey)에서
Google AI Studio를 통해 키를 생성하세요.

터미널 창에서 다음과 같이 `.env` 파일에 API 키를 기록해 환경 변수를 설정합니다.

```bash title="Update: my-agent/.env"
echo 'GEMINI_API_KEY="YOUR_API_KEY"' > .env
```

??? tip "ADK에서 다른 AI 모델 사용"
    ADK는 여러 생성형 AI 모델을 지원합니다. ADK 에이전트에서 다른 모델을 구성하는 방법은
    [Models & Authentication](/adk-docs/agents/models)을 참조하세요.

## 에이전트 실행

`@google/adk-devtools` 라이브러리를 사용해 ADK 에이전트를 실행할 수 있습니다.
`run` 명령으로 대화형 CLI를 사용하거나 `web` 명령으로 ADK 웹 사용자 인터페이스를 사용할 수 있습니다.
두 방식 모두 에이전트를 테스트하고 상호 작용할 수 있습니다.

### CLI로 실행

```bash
adk run my-agent/agent.ts
```

### 웹 UI로 실행

```bash
adk web my-agent/agent.ts
```
