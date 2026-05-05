# エージェント実行をキャンセルする

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-typescript">TypeScript v1.0.0</span>
</div>

エージェント実行に時間がかかりすぎる場合、状況が変わった場合、または不要になった場合、
すでに完了した作業を失わずにキャンセルしたいことがあります。ADK のキャンセルは非破壊的です。
セッションにすでにコミットされたイベントは保持されます。

ADK は `AbortController` と `AbortSignal` を使った正常なキャンセルをサポートします。
`runner.runAsync()` に `AbortSignal` を渡すことで、エージェント実行、LLM 生成、
ツール実行、プラグインコールバックを含む実行スタックの任意の地点で、呼び出し全体を
キャンセルできます。

## はじめに

`AbortController` を作成し、その `signal` を `runner.runAsync()` に渡して、実行を
キャンセルしたいタイミングで `controller.abort()` を呼び出します。

=== "TypeScript"

    ```typescript
    --8<-- "examples/typescript/snippets/runtime/cancel/basic-usage.ts:full"
    ```

## キャンセルの伝播方法

signal を abort すると、キャンセルは実行スタック全体に伝播します。各コンポーネントは
重要なライフサイクル地点で `abortSignal.aborted` を確認し、キャンセルを検出すると早期に
終了します。

| コンポーネント | abort 時の動作 |
| :--- | :--- |
| **Runner** | セッション取得前、プラグインコールバック後、イベントストリーミングループ内で停止します。 |
| **LlmAgent** | 実行ステップ間、モデルコールバックの前後、レスポンスストリーミング中に停止します。 |
| **LoopAgent** | ループ反復間およびサブエージェント実行間で停止します。 |
| **ParallelAgent** | 並行して実行されたサブエージェントの結果をマージするときに停止します。 |
| **Models (Gemini)** | signal が `config.abortSignal` 経由で基盤となる Google GenAI SDK に渡され、進行中の HTTP リクエストをキャンセルします。 |
| **AgentTool** | signal をサブエージェント runner に渡し、セッション作成後に abort を確認します。 |
| **MCPTool** | signal を MCP クライアントの `callTool` メソッドに渡します。 |

`InvocationContext` も signal に listener を登録します。signal がトリガーされると
`endInvocation = true` が自動的に設定され、すべてのコンポーネントに終了処理へ移るよう
通知します。

### キャンセル時の動作

`AbortSignal` がトリガーされると、次の動作が適用されます。

- **正常終了:** `runner.runAsync()` が返す async generator はエラーを投げずに完了します。
  つまり、イベントの yield を停止します。
- **コミット済みイベントは保持:** abort 前に Runner がすでに yield して処理したイベントは、
  セッション履歴にコミットされたまま残ります。
- **部分イベントなし:** 進行中だったがまだ yield されていないイベントは破棄されます。
- **リソースのクリーンアップ:** Gemini API への進行中の LLM リクエストは、SDK のネイティブな
  `AbortSignal` サポートによりキャンセルされ、ネットワークリソースが解放されます。

## 高度な例

次の例では、基本的な `AbortController` の使い方を超えた追加のキャンセルパターンを
示します。

### タイムアウトによるキャンセル

`AbortSignal.timeout()` を使用すると、指定した時間の後にエージェント実行を自動的に
キャンセルできます。これはエージェント実行に時間制限を強制したい場合に便利です。

はじめにの例と同じエージェントおよび runner 設定を使い、`const controller` 以降を
すべて次のコードに置き換えます。

=== "TypeScript"

    ```typescript
    --8<-- "examples/typescript/snippets/runtime/cancel/timeout.ts:run"
    ```

`AbortSignal.any()` を使って、タイムアウトとプログラムによるキャンセルを組み合わせる
こともできます。同じ設定で、`const controller` 以降をすべて次のコードに置き換えます。

=== "TypeScript"

    ```typescript
    --8<-- "examples/typescript/snippets/runtime/cancel/combined-signal.ts:run"
    ```

### カスタムツール内の AbortSignal

`runner.runAsync()` に `AbortSignal` を渡すと、カスタムツール内の
`toolContext.abortSignal` でも利用できます。次の例では、カスタムツール内で abort
signal を確認するパターンを示します。

=== "TypeScript"

    ```typescript
    --8<-- "examples/typescript/snippets/runtime/cancel/custom-tool.ts:tool"
    ```
