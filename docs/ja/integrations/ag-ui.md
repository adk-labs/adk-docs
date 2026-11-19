---
catalog_title: AG-UI
catalog_description: ストリーミング、状態同期、エージェント型アクション対応の対話型チャット UI を構築します
catalog_icon: /integrations/assets/ag-ui.png
catalog_tags: []
---
# AG-UI と CopilotKit でチャット体験を構築する

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span><span class="lst-go">Go</span><span class="lst-java">Java</span>
</div>

リッチで応答性の高いインターフェースを通じてユーザーがエージェントと対話できるようにしたいと思っても、ストリーミングイベントやクライアントの状態管理に対応した UI をゼロから構築するには多大な労力がかかります。[AG-UI](https://docs.ag-ui.com/) はまさにその課題を解決するために設計された、エージェントに直接接続できるリッチなユーザーインターフェースプロトコルです。

[AG-UI](https://github.com/ag-ui-protocol/ag-ui) は、モバイルから Web、さらにはコマンドラインまで、幅広い技術スタックでリッチクライアントを構築するための一貫したインターフェースを提供します。AG-UI をサポートするクライアントには次のようなものがあります。

- [CopilotKit](https://copilotkit.ai) は、エージェントを Web アプリケーションと緊密に統合するためのツールとコンポーネントを提供します。
- [Kotlin](https://github.com/ag-ui-protocol/ag-ui/tree/main/sdks/community/kotlin)、[Java](https://github.com/ag-ui-protocol/ag-ui/tree/main/sdks/community/java)、[Go](https://github.com/ag-ui-protocol/ag-ui/tree/main/sdks/community/go/example/client) 向けのクライアント、および TypeScript による [CLI 実装](https://github.com/ag-ui-protocol/ag-ui/tree/main/apps/client-cli-example/src)

このチュートリアルでは、CopilotKit を使用して ADK エージェントをバックエンドに持つサンプルアプリを作成し、AG-UI がサポートする主な機能を紹介します。

## クイックスタート

まず、ADK エージェントとシンプルな Web クライアントを備えたサンプルアプリケーションを作成しましょう。

```
npx create-ag-ui-app@latest --adk
```

### チャット

チャットはエージェントを提供するうえで馴染み深いインターフェースであり、AG-UI はユーザーとエージェント間のメッセージストリーミングを処理します。

```tsx title="src/app/page.tsx"
<CopilotSidebar
  clickOutsideToClose={false}
  defaultOpen={true}
  labels={{
    title: "ポップアップアシスタント",
    initial: "👋 こんにちは！エージェントとチャットしています。このエージェントには、開始に役立ついくつかのツールが付属しています..."
  }}
/>
```

チャット UI の詳細については、[CopilotKit のドキュメント](https://docs.copilotkit.ai/adk/agentic-chat-ui)をご覧ください。

### ツールベースの生成 UI（ツールのレンダリング）

AG-UI を使用すると、ツールの情報を生成 UI（Generative UI）と共有してユーザーに表示できます。

```tsx title="src/app/page.tsx"
useCopilotAction({
  name: "get_weather",
  description: "指定された場所の天気を取得します。",
  available: "disabled",
  parameters: [
    { name: "location", type: "string", required: true },
  ],
  render: ({ args }) => {
    return <WeatherCard location={args.location} themeColor={themeColor} />
  },
});
```

ツールベースの生成 UI の詳細については、[CopilotKit のドキュメント](https://docs.copilotkit.ai/adk/generative-ui/tool-based)をご覧ください。

### 共有状態

ADK エージェントはステートフルに構成でき、エージェントと UI の間で状態を同期することで、高度でスムーズなユーザーエクスペリエンスを実現できます。状態は双方向に同期できるため、ユーザーやアプリケーションの他の部分による変更をエージェントが自動的に認識できます。

```tsx title="src/app/page.tsx"
const { state, setState } = useCoAgent<AgentState>({
  name: "my_agent",
  initialState: {
    proverbs: [
      "CopilotKitは新しいかもしれませんが、スライスされたパン以来の最高の発明です。",
    ],
  },
})
```

共有状態の詳細については、[CopilotKit のドキュメント](https://docs.copilotkit.ai/adk/shared-state)をご覧ください。

### 試してみる

```
npm install && npm run dev
```

## リソース

AG-UI を使用して UI に組み込めるその他の機能については、CopilotKit のドキュメントを参照してください。

- [エージェント型生成 UI（Agentic Generative UI）](https://docs.copilotkit.ai/adk/generative-ui/agentic)
- [ヒューマンインザループ（Human in the Loop）](https://docs.copilotkit.ai/adk/human-in-the-loop/agent)
- [フロントエンドアクション](https://docs.copilotkit.ai/adk/frontend-actions)

または、[AG-UI Dojo](https://dojo.ag-ui.com) で実際に試してみてください。
