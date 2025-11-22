# ADKツールの実行確認を取得する

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.14.0</span><span class="lst-preview">試験運用版</span>
</div>

一部のエージェントワークフローでは、意思決定、検証、セキュリティ、または一般的な監視のために確認が必要です。このような場合、ワークフローを続行する前に、人間または監視システムから応答を取得する必要があります。Agent Development Kit（ADK）の*ツール確認*機能を使用すると、ADKツールは実行を一時停止し、ユーザーまたは他のシステムと対話して確認したり、続行する前に構造化データを収集したりできます。ADKツールでツール確認を使用するには、次の方法があります。

-   **[ブール値の確認](#boolean-confirmation):** `require_confirmation`パラメータを使用してFunctionToolを設定できます。このオプションは、はいまたはいいえの確認応答のためにツールを一時停止します。
-   **[高度な確認](#advanced-confirmation):** 構造化データ応答が必要なシナリオでは、確認を説明するテキストプロンプトと期待される応答で`FunctionTool`を設定できます。

!!! example "試験運用版"
    ツール確認機能は試験運用版であり、いくつかの[既知の制限](#known-limitations)があります。
    [フィードバック](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=tool%20confirmation)をお待ちしております！

リクエストがユーザーにどのように伝達されるかを設定でき、システムはADKサーバーのREST APIを介して送信された[リモート応答](#remote-response)を使用することもできます。ADK Webユーザーインターフェイスで確認機能を使用する場合、エージェントワークフローは図1に示すように、ユーザーに入力を要求するダイアログボックスを表示します。

![ツール確認のためのデフォルトのユーザーインターフェイスのスクリーンショット](/adk-docs/ja/assets/confirmation-ui.png)

**図1.** 高度なツール応答実装を使用した確認応答要求ダイアログボックスの例。

次のセクションでは、確認シナリオでこの機能を使用する方法について説明します。完全なコードサンプルについては、[human_tool_confirmation](https://github.com/google/adk-python/blob/fc90ce968f114f84b14829f8117797a4c256d710/contributing/samples/human_tool_confirmation/agent.py)の例を参照してください。エージェントワークフローに人間の入力を組み込む追加の方法があります。詳細については、[ヒューマンインザループ](/adk-docs/ja/agents/multi-agents/#human-in-the-loop-pattern)エージェントパターンを参照してください。

## ブール値の確認 {#boolean-confirmation}

ツールがユーザーから単純な`はい`または`いいえ`のみを必要とする場合は、`FunctionTool`クラスをラッパーとして使用して確認ステップを追加できます。たとえば、`reimburse`というツールがある場合、次の例に示すように、`FunctionTool`クラスでラップし、`require_confirmation`パラメータを`True`に設定することで確認ステップを有効にできます。

```
# agent.pyから
root_agent = Agent(
   ...
   tools=[
        # ツール呼び出しにユーザーの確認を要求するには、require_confirmationをTrueに設定します。
        FunctionTool(reimburse, require_confirmation=True),
    ],
...
```

この実装方法は最小限のコードで済みますが、ユーザーまたは確認システムからの単純な承認に限定されます。このアプローチの完全な例については、[human_tool_confirmation](https://github.com/google/adk-python/blob/fc90ce968f114f84b14829f8117797a4c256d710/contributing/samples/human_tool_confirmation/agent.py)のコードサンプルを参照してください。

### 確認関数の要求

入力値をブール値の応答を返す関数に置き換えることで、`require_confirmation`応答の動作を変更できます。次の例は、確認が必要かどうかを判断するための関数を示しています。

```
async def confirmation_threshold(
    amount: int, tool_context: ToolContext
) -> bool:
  """金額が1000を超える場合はtrueを返します。"""
  return amount > 1000
```

この関数は、`require_confirmation`パラメータのパラメータ値として設定できます。

```
root_agent = Agent(
   ...
   tools=[
        # ユーザーの確認を要求するには、require_confirmationをTrueに設定します
        FunctionTool(reimburse, require_confirmation=confirmation_threshold),
    ],
...
```

この実装の完全な例については、[human_tool_confirmation](https://github.com/google/adk-python/blob/fc90ce968f114f84b14829f8117797a4c256d710/contributing/samples/human_tool_confirmation/agent.py)のコードサンプルを参照してください。

## 高度な確認 {#advanced-confirmation}

ツールの確認にユーザーへの詳細な説明やより複雑な応答が必要な場合は、tool_confirmation実装を使用します。このアプローチは、`ToolContext`オブジェクトを拡張して、ユーザーへのリクエストのテキスト説明を追加し、より複雑な応答データを可能にします。この方法でツールの確認を実装する場合、ツールの実行を一時停止し、特定の情報を要求してから、提供されたデータでツールを再開できます。

この確認フローには、システムが人間の応答に対する入力リクエストを組み立てて送信するリクエストステージと、システムが返されたデータを受信して処理する応答ステージがあります。

### 確認の定義

高度な確認でツールを作成する場合は、ToolContextオブジェクトを含む関数を作成します。次に、tool_confirmationオブジェクト、`hint`および`payload`パラメータを持つ`tool_context.request_confirmation()`メソッドを使用して確認を定義します。これらのプロパティは次のように使用されます。

-   `hint`: ユーザーに必要なものを説明する説明的なメッセージ。
-   `payload`: 返されると予想されるデータの構造。このデータ型はAnyであり、辞書やpydanticモデルなど、JSON形式の文字列にシリアル化できる必要があります。

次のコードは、従業員の休暇申請を処理するツールの実装例を示しています。

```
def request_time_off(days: int, tool_context: ToolContext):
  """従業員の休暇を申請します。"""
  ...
  tool_confirmation = tool_context.tool_confirmation
  if not tool_confirmation:
    tool_context.request_confirmation(
        hint=(
            '期待されるToolConfirmationペイロードを持つFunctionResponseで応答することにより、'
            'ツール呼び出しrequest_time_off()を承認または拒否してください。'
        ),
        payload={
            'approved_days': 0,
        },
    )
    # ツールが確認応答を待っていることを示す中間ステータスを返します。
    return {'status': 'マネージャーの承認が必要です。'}

  approved_days = tool_confirmation.payload['approved_days']
  approved_days = min(approved_days, days)
  if approved_days == 0:
    return {'status': '休暇申請は拒否されました。', 'approved_days': 0}
  return {
      'status': 'ok',
      'approved_days': approved_days,
  }
```

このアプローチの完全な例については、[human_tool_confirmation](https://github.com/google/adk-python/blob/fc90ce968f114f84b14829f8117797a4c256d710/contributing/samples/human_tool_confirmation/agent.py)のコードサンプルを参照してください。確認が取得される間、エージェントワークフローツールの実行が一時停止されることに注意してください。確認が受信された後、`tool_confirmation.payload`オブジェクトで確認応答にアクセスし、ワークフローの実行を続行できます。

## REST APIによるリモート確認 {#remote-response}

エージェントワークフローの人間による確認のためのアクティブなユーザーインターフェイスがない場合は、コマンドラインインターフェイスを介して確認を処理するか、電子メールやチャットアプリケーションなどの別のチャネルを介してルーティングできます。ツール呼び出しを確認するには、ユーザーまたは呼び出し元のアプリケーションがツール確認データを含む`FunctionResponse`イベントを送信する必要があります。

リクエストは、ADK APIサーバーの`/run`または`/run_sse`エンドポイント、またはADKランナーに直接送信できます。次の例では、`curl`コマンドを使用して確認を`/run_sse`エンドポイントに送信します。

```
 curl -X POST http://localhost:8000/run_sse \
 -H "Content-Type: application/json" \
 -d 
'{ 
    "app_name": "human_tool_confirmation",
    "user_id": "user",
    "session_id": "7828f575-2402-489f-8079-74ea95b6a300",
    "new_message": {
        "parts": [
            {
                "function_response": {
                    "id": "adk-13b84a8c-c95c-4d66-b006-d72b30447e35",
                    "name": "adk_request_confirmation",
                    "response": {
                        "confirmed": true
                    }
                }
            }
        ],
        "role": "user"
    }
}'
```

確認のためのRESTベースの応答は、次の要件を満たす必要があります。

-   `function_response`の`id`は、`RequestConfirmation` `FunctionCall`イベントの`function_call_id`と一致する必要があります。
-   `name`は`adk_request_confirmation`である必要があります。
-   `response`オブジェクトには、確認ステータスとツールで必要な追加のペイロードデータが含まれます。

!!! note "注：再開機能による確認"

    ADKエージェントワークフローが
    [再開](/adk-docs/ja/runtime/resume/)機能で構成されている場合は、確認
    応答とともに呼び出しID（`invocation_id`）パラメーターも指定する必要があります。
    指定する呼び出しIDは、確認リクエストを生成した呼び出しと同じでなければなりません。
    そうしないと、システムは確認応答で新しい呼び出しを開始します。
    エージェントが再開機能を使用する場合は、応答に含めることができるように、
    確認リクエストとともに呼び出しIDをパラメーターとして含めることを検討してください。
    再開機能の使用方法の詳細については、
    [停止したエージェントの再開](/adk-docs/ja/runtime/resume/)を参照してください。

## 既知の制限 {#known-limitations}

ツール確認機能には、次の制限があります。

-   [DatabaseSessionService](/adk-docs/ja/api-reference/python/google-adk.html#google.adk.sessions.DatabaseSessionService)はこの機能ではサポートされていません。
-   [VertexAiSessionService](/adk-docs/ja/api-reference/python/google-adk.html#google.adk.sessions.VertexAiSessionService)はこの機能ではサポートされていません。

## 次のステップ

エージェントワークフロー用のADKツールの構築の詳細については、[関数ツール](/adk-docs/ja/tools-custom/function-tools/)を参照してください。