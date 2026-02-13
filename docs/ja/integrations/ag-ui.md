---
catalog_title: AG-UI
catalog_description: Build interactive chat UIs with streaming, state sync, and agentic actions
catalog_icon: /adk-docs/integrations/assets/ag-ui.png
catalog_tags: []
---
# AG-UIとCopilotKitでチャット体験を構築する

エージェントビルダーとして、ユーザーがリッチで応答性の高いインターフェイスを介してエージェントと対話できるようにしたいと考えています。UIをゼロから構築するには、特にストリーミングイベントとクライアントの状態をサポートするために多大な労力が必要です。まさにそのために[AG-UI](https://docs.ag-ui.com/)は設計されました。エージェントに直接接続されたリッチなユーザーエクスペリエンスです。

[AG-UI](https://github.com/ag-ui-protocol/ag-ui)は、モバイルからWeb、さらにはコマンドラインまで、テクノロジースタック全体でリッチなクライアントを強化するための一貫したインターフェイスを提供します。AG-UIをサポートするさまざまなクライアントがあります。

- [CopilotKit](https://copilotkit.ai)は、エージェントをWebアプリケーションと緊密に統合するためのツールとコンポーネントを提供します。
- [Kotlin](https://github.com/ag-ui-protocol/ag-ui/tree/main/sdks/community/kotlin)、[Java](https://github.com/ag-ui-protocol/ag-ui/tree/main/sdks/community/java)、[Go](https://github.com/ag-ui-protocol/ag-ui/tree/main/sdks/community/go/example/client)、およびTypeScriptの[CLI実装](https://github.com/ag-ui-protocol/ag-ui/tree/main/apps/client-cli-example/src)用のクライアント

このチュートリアルでは、CopilotKitを使用して、AG-UIでサポートされている機能の一部を示すADKエージェントに裏打ちされたサンプルアプリを作成します。

## クイックスタート

開始するには、ADKエージェントとシンプルなWebクライアントを備えたサンプルアプリケーションを作成しましょう。

```
npx create-ag-ui-app@latest --adk
```

### チャット

チャットはエージェントを公開するための使い慣れたインターフェイスであり、AG-UIはユーザーとエージェント間のストリーミングメッセージを処理します。

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

チャットUIの詳細については、[CopilotKitのドキュメント](https://docs.copilotkit.ai/adk/agentic-chat-ui)をご覧ください。

### ツールベースのジェネレーティブUI（レンダリングツール）

AG-UIを使用すると、ツール情報をジェネレーティブUIと共有して、ユーザーに表示できます。

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

ツールベースのジェネレーティブUIの詳細については、[CopilotKitのドキュメント](https://docs.copilotkit.ai/adk/generative-ui/tool-based)をご覧ください。

### 共有状態

ADKエージェントはステートフルにすることができ、エージェントとUIの間でその状態を同期することで、強力で流動的なユーザーエクスペリエンスが可能になります。状態は双方向に同期できるため、エージェントはユーザーまたはアプリケーションの他の部分によって行われた変更を自動的に認識します。

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

共有状態の詳細については、[CopilotKitのドキュメント](https://docs.copilotkit.ai/adk/shared-state)をご覧ください。

### 試してみる！

```
npm install && npm run dev
```

## リソース

AG-UIを使用してUIに組み込むことができるその他の機能については、CopilotKitのドキュメントを参照してください。

- [エージェントジェネレーティブUI](https://docs.copilotkit.ai/adk/generative-ui/agentic)
- [ヒューマンインザループ](https://docs.copilotkit.ai/adk/human-in-the-loop/agent)
- [フロントエンドアクション](https://docs.copilotkit.ai/adk/frontend-actions)

または、[AG-UI道場](https://dojo.ag-ui.com)で試してみてください。
