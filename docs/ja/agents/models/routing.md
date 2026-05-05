# モデル間でルーティングする

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-typescript">TypeScript v1.0.0</span><span class="lst-preview">試験運用</span>
</div>

!!! example "試験運用"

    モデルルーティングは試験運用の機能であり、今後のリリースで変更される可能性があります。
    [フィードバック](https://github.com/google/adk-js/issues/new?template=feature_request.md)を
    お待ちしています。

`LlmAgent` はデフォルトで単一のモデルを使用します。リクエストごとに異なる
モデルから動的に選択する必要がある場合は、どのモデルを使うかを選ぶルーティング
関数を定義できます。`RoutedLlm` はこの機能を提供し、エラー時のモデル
フォールバック、モデル間の A/B テスト、入力の複雑さに基づく自動ルーティングを
可能にします。選択されたモデルが出力を生成する前に失敗した場合、ルーティング
関数はエラーコンテキスト付きで再度呼び出され、別のモデルを選択できます。

`RoutedLlm` を `LlmAgent` の `model` パラメータとして渡します。ルートごとに
モデルだけが変わる場合は `RoutedLlm` を使用してください。指示、ツール、または
サブエージェントも切り替える必要がある場合は、代わりに
[`RoutedAgent`](../routing.md) を使用します。

## ルーティングの仕組み

`LlmRouter` 関数は、利用可能なモデルのマップと現在の `LlmRequest` を受け取り、
使用するモデルのキーを返します。

=== "TypeScript"

    ```typescript
    type LlmRouter = (
      models: Readonly<Record<string, BaseLlm>>,
      request: LlmRequest,
      errorContext?: { failedKeys: ReadonlySet<string>; lastError: unknown },
    ) => Promise<string | undefined> | string | undefined;
    ```

`models` パラメータには、明示的なキーを持つ `Record<string, BaseLlm>`、または
`BaseLlm` インスタンスの配列を渡せます。配列を渡した場合は、各モデルの名前が
キーとして使用されます。

フェイルオーバーは [`RoutedAgent`](../routing.md#how-routing-works) と同じ
ルールに従います。選択されたモデルがレスポンスを 1 つも yield する前に失敗した
場合にのみ、ルーターは `errorContext` 付きで再呼び出しされます。yield 後の
エラーは再試行されず、そのまま伝播します。ルーターは `undefined` を返して
再試行を停止し、最後のエラーを伝播できます。

**ライブ接続:** `RoutedLlm.connect()` は接続時にモデルを選択します。ライブ
接続が確立された後は、ストリームの途中でモデルを切り替えることはできません。

## 基本的な使用方法

次の例では、まずプライマリモデルを試し、プライマリモデルが失敗した場合に
セカンダリモデルへフォールバックする `RoutedLlm` を作成します。ルーターは
失敗したモデルを再選択しないように `errorContext.failedKeys` を確認します。

=== "TypeScript"

    ```typescript
    --8<-- "examples/typescript/snippets/agents/models/routing/basic-usage.ts:full"
    ```
