# エージェント間でルーティングする

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-typescript">TypeScript v1.0.0</span><span class="lst-preview">試験運用</span>
</div>

!!! example "試験運用"

    エージェントルーティングは試験運用の機能であり、今後のリリースで変更される可能性があります。
    [フィードバック](https://github.com/google/adk-js/issues/new?template=feature_request.md)を
    お待ちしています。

異なるタスク向けのエージェントを構築する場合、各呼び出しをどのエージェントが
処理するかを実行時に選択するルーティング関数を定義できます。`RoutedAgent` は
この機能を提供し、エラー時のエージェントフォールバック、A/B テスト、計画モード、
入力の複雑さに基づく自動ルーティングを可能にします。選択されたエージェントが
出力を生成する前に失敗した場合、ルーティング関数はエラーコンテキスト付きで再度
呼び出され、フォールバックを選択できます。

`RoutedAgent` は、`SequentialAgent` や `ParallelAgent` のような
[ワークフローエージェント](workflow-agents/index.md)とは異なります。ワークフロー
エージェントは複数のエージェントを固定パターンでオーケストレーションします。また、
LLM がどのエージェントへ引き継ぐかを決める
[LLM 主導の委譲](multi-agents.md#b-llm-driven-delegation-agent-transfer)とも
異なります。`RoutedAgent` では、開発者が明示的なルーティング関数を書き、呼び出し
ごとに **1 つの** エージェントを選択します。モデルレベルのルーティングについては
[モデルルーティング](models/routing.md)を参照してください。

## ルーティングの仕組み {#how-routing-works}

`RoutedAgent` と [`RoutedLlm`](models/routing.md) はどちらも、選択と
フェイルオーバーを処理する共通のルーティングユーティリティを基盤にしています。

ルーター関数は、利用可能なエージェントのマップと現在のコンテキストを受け取り、
実行するエージェントのキーを返します。同期関数でも非同期関数でもかまいません。

=== "TypeScript"

    ```typescript
    type AgentRouter = (
      agents: Readonly<Record<string, BaseAgent>>,
      context: InvocationContext,
      errorContext?: { failedKeys: ReadonlySet<string>; lastError: unknown },
    ) => Promise<string | undefined> | string | undefined;
    ```

**`agents` パラメータ**には、明示的なキーを持つ `Record<string, BaseAgent>`、または
エージェント配列を渡せます。配列を渡した場合は、各エージェントの `name` プロパティが
キーとして使用されます。

**フェイルオーバーの動作:**

- ルーターは最初の選択のために、まず `errorContext` なしで呼び出されます。
- 選択されたエージェントが **イベントを 1 つも yield する前に** エラーを投げた
  場合、ルーターは `failedKeys` と `lastError` を含む `errorContext` 付きで再度
  呼び出されます。
- 選択されたエージェントが **イベントを yield した後に** エラーを投げた場合、部分的な
  結果がすでに出力されているため、エラーは再試行されず直接伝播します。
- すでに試行されたキーは再選択できません。ルーターが以前に失敗したキーを返した場合、
  エラーが伝播します。
- ルーターが `undefined` を返した場合、ルーティングは停止し、最後のエラーが投げられます。

## 基本的な使用方法 {#basic-usage}

複数のエージェントを作成し、キーを返すルーター関数を定義して、それらを
`RoutedAgent` でラップします。次の例では、呼び出し間で変化する外部設定値に基づいて
2 つのエージェント間でルーティングします。

=== "TypeScript"

    ```typescript
    --8<-- "examples/typescript/snippets/agents/routing/basic-usage.ts:full"
    ```

次の呼び出しの前に `config.selectedAgent` を `'agent_b'` に変更すると、別の
エージェントへルーティングされます。

## エラー時のフォールバック

エージェントが失敗すると、ルーターは `errorContext` 付きで再度呼び出され、
フォールバックを選択できます。フェイルオーバーは、エージェントがイベントを yield する
前に失敗した場合にのみ適用されます（[ルーティングの仕組み](#how-routing-works)を
参照）。次の例では、失敗したエージェントを再選択しないように
`errorContext.failedKeys` を確認します。

=== "TypeScript"

    ```typescript
    --8<-- "examples/typescript/snippets/agents/routing/fallback.ts:config"
    ```

## 計画モード

ルーターは任意の外部状態を読み取り、異なる指示、モデル、ツールを持つエージェントの
中から選択できます。これにより、エージェントが動作を動的に切り替える計画モードを
実装できます。たとえば、基本エージェントには読み書きツールを持たせ、計画エージェントは
読み取り専用アクセスに制限し、分析のためにより強力なモデルを使わせることができます。

次の例では、別の `RoutedAgent` 構成を示します。runner の完全な設定については
[基本的な使用方法](#basic-usage)を参照してください。

=== "TypeScript"

    ```typescript
    --8<-- "examples/typescript/snippets/agents/routing/planning-mode.ts:config"
    ```

呼び出し前に `planningMode = true` を設定すると、制限されたツールセットと異なる
指示を持つ計画エージェントへルーティングされます。

## 複雑さに基づく自動ルーティング

ルーター関数は軽量な分類モデルを呼び出して入力を分類し、その結果に応じて異なる
エージェントへルーティングできます。ルーターは非同期にできるため、エージェントを
選択する前に内部で LLM 呼び出しを実行できます。

次の例では、別の `RoutedAgent` 構成を示します。runner の完全な設定については
[基本的な使用方法](#basic-usage)を参照してください。

=== "TypeScript"

    ```typescript
    --8<-- "examples/typescript/snippets/agents/routing/auto-routing.ts:config"
    ```
