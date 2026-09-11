---
catalog_title: CopilotKit
catalog_description: エージェントに React、Angular、Vue、モバイル、Slack フロントエンドを追加
catalog_icon: /integrations/assets/copilotkit.png
---

# ADK 向け CopilotKit ユーザー インターフェース

<div class="language-support-tag">
  <span class="lst-supported">ADK でサポート</span><span class="lst-python">Python</span>
</div>

[CopilotKit](https://github.com/CopilotKit/CopilotKit) は、[AG-UI](/integrations/ag-ui/) を介してアプリケーションをエージェントに接続するオープンソースのフロントエンド ライブラリおよびランタイムのセットです。ADK では、`ag-ui-adk` パッケージがエージェントを AG-UI エンドポイントとして公開し、CopilotKit はそのエンドポイントに対して React、Angular、Vue、React Native、または Slack で利用可能なチャット画面、フロントエンド ツール、生成 UI (Generative UI)、Human-in-the-loop (人間参加型) コントロールを提供します。

[AG-UI 統合ページ](/integrations/ag-ui/) では、プロトコルとフルスタック サンプルをスキャフォールディングする `create` コマンドについて説明しています。このページでは、既存の ADK プロジェクトに CopilotKit を追加する方法を説明します。

## ユースケース

- **チャット サーフェス**: ADK エージェントのメッセージ、ツール呼び出し、推論プロセスを、Web またはモバイル アプリ向けのパッケージ化されたチャット コンポーネントにストリーミングします。
- **フロントエンド ツール**: ナビゲーション、レコードのオープン、アプリケーション状態の読み取りなど、ブラウザで実行される関数をエージェントから呼び出せるようにします。
- **生成 UI**: ツール呼び出しとその結果をプレーン テキストではなく、リッチなアプリケーション コンポーネントでレンダリングします。
- **Human-in-the-loop**: ユーザーが提案されたアクションを承認、編集、または拒否するまでエージェントの実行を一時停止し、その回答を受け取って再開します。
- **メッセージング チャネル**: オープンソースの Channels SDK を使用して、Slack 内で同じエージェントを実行します。

## 前提条件

- Python 3.10 〜 3.14 および Node.js 18 以降
- [Google AI Studio](https://aistudio.google.com/app/apikey) の Gemini API キー（`GOOGLE_API_KEY` としてエクスポート）
- 以下のフロントエンド手順を実行するための React アプリケーション（Next.js など）

## インストール

バックエンド パッケージをインストールします:

```bash
pip install google-adk ag-ui-adk fastapi "uvicorn[standard]"
```

Web アプリケーションにフロントエンド パッケージをインストールします:

```bash
npm install @copilotkit/react-core @copilotkit/runtime @ag-ui/client hono zod
```

## エージェントでの使用

### 1. AG-UI 経由でエージェントを公開する

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

`AGUIToolset()` ツールセットにより、フロントエンドで登録されたツールをエージェントが呼び出せるようになります。`ADKAgent.from_app()` と `ResumabilityConfig` でミドルウェアを作成すると、フロントエンド ツールの呼び出し時に実行を一時停止し、結果が返されたときに再開できます。

バックエンドを起動します:

```bash
uvicorn agent:app --reload --port 8000
```

### 2. CopilotKit Runtime にエンドポイントを登録する

CopilotKit Runtime は Web アプリケーション内で動作し、AG-UI の実行を ADK エンドポイントに転送します。Next.js アプリの場合、以下のルートを追加します:

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

### 3. チャットのレンダリング

React ツリーのルート近くに Provider を 1 回マウントし、その配下の任意の場所にチャット コンポーネントを配置します:

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

`CopilotChat` コンポーネントは、メッセージ状態、ストリーミング、ツール呼び出しの表示、添付ファイル、および提案を処理します。

### 4. フロントエンド ツールの追加

ブラウザ内でツールを登録します。ADK 側の `AGUIToolset()` により、実行ごとにエージェントからツールが利用可能になります:

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

Provider の下、`<CopilotChat />` の横に `<SearchTool />` をレンダリングします。

## 利用可能なフック (Hooks)

フック | 説明
---- | -----------
`useFrontendTool` | ブラウザで実行され、エージェントに結果を返すツールを登録
`useRenderTool` | バックエンド ツールの進行状況と結果を名前でレンダリング
`useComponent` | エージェントがチャット内に配置できるレンダリング専用コンポーネントを登録
`useHumanInTheLoop` | 実行を継続する前に UI が `respond()` を呼び出す必要があるツールを登録
`useAgentContext` | 実行ごとにアプリケーション状態をコンテキストとしてエージェントと共有
`useAgent` | カスタム チャット画面を構築する際にメッセージ、状態、実行ステータスを読み取り

すべてのフックは `@copilotkit/react-core/v2` からエクスポートされます。パラメータと戻り値については、[CopilotKit フック リファレンス](https://docs.copilotkit.ai/reference/hooks/useFrontendTool)をご覧ください。

## その他のクライアント

同じ CopilotKit Runtime ルートと ADK エンドポイントが、すべての CopilotKit クライアントに対応します:

- **Angular**: `provideCopilotKit()` と `<copilot-chat>` コンポーネントを含む `@copilotkit/angular` パッケージ。[Angular ガイド](https://docs.copilotkit.ai/angular)をご覧ください。
- **Vue**: `CopilotKitProvider` と `CopilotChat` を含む `@copilotkit/vue` パッケージ。[Vue ガイド](https://docs.copilotkit.ai/vue)をご覧ください。
- **React Native**: ヘッドレス フックと `@copilotkit/react-native/components` 配下のオプションのパッケージ化されたチャットを含む `@copilotkit/react-native` パッケージ。[React Native ガイド](https://docs.copilotkit.ai/react-native)をご覧ください。

## メッセージング チャネル

オープンソースの Channels SDK を使用すると、Slack ワークスペースを `ag-ui-adk` エンドポイントに直接接続できます。CopilotKit Runtime ルートは不要です:

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

アダプターはデフォルトでソケット モード (Socket Mode) で実行されるため、ローカル開発にはアプリ レベルのトークンのみが必要で、パブリック URL は不要です。各 Slack スレッドは 1 つの AG-UI スレッドにマッピングされ、Block Kit のレンダリング、インタラクション、承認はアダプターによって処理されます。Slack アプリの設定とセルフホストでのデプロイについては、[Channels のドキュメント](https://docs.copilotkit.ai/slack)をご覧ください。

## その他のリソース

- [ADK 向け CopilotKit ドキュメント](https://docs.copilotkit.ai/adk)
- [GitHub の CopilotKit](https://github.com/CopilotKit/CopilotKit)
- [PyPI の AG-UI 向け ADK ミドルウェア (`ag-ui-adk`)](https://pypi.org/project/ag-ui-adk/)
- [ADK ミドルウェアのソース コード](https://github.com/ag-ui-protocol/ag-ui/tree/main/integrations/adk-middleware)
- [AG-UI Dojo](https://dojo.ag-ui.com)（ライブ ADK サンプル）
