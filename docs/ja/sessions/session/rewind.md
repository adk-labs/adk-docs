# エージェントのセッションを巻き戻す

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.17.0</span>
</div>

ADK セッションの Rewind 機能を使うと、セッションを過去の
リクエスト時点の状態に戻せます。これにより、ミスの取り消し、
別経路の検証、既知の正常ポイントからの再開が可能になります。
このドキュメントでは、機能概要、使い方、制限事項を説明します。

## セッションを巻き戻す

セッションを巻き戻すときは、取り消したいユーザーリクエスト、
すなわち ***invocation*** を指定します。システムはそのリクエストと
それ以降のリクエストを取り消します。
たとえば 3 つのリクエスト (A, B, C) があり、A 時点の状態に戻したい場合、
B を指定します。これにより B と C の変更が取り消されます。セッションの巻き戻しは
***Runner*** インスタンスの rewind メソッドを使って行い、
次のコードのように user、session、invocation id を指定します:

```python
# Create runner
runner = InMemoryRunner(
    agent=agent.root_agent,
    app_name=APP_NAME,
)

# Create a session
session = await runner.session_service.create_session(
    app_name=APP_NAME, user_id=USER_ID
)
# call agent with wrapper function "call_agent_async()"
await call_agent_async(
    runner, USER_ID, session.id, "set state color to red"
)
# ... more agent calls ...
events_list = await call_agent_async(
    runner, USER_ID, session.id, "update state color to blue"
)

# get invocation id
rewind_invocation_id=events_list[1].invocation_id

# rewind invocations (state color: red)
await runner.rewind_async(
    user_id=USER_ID,
    session_id=session.id,
    rewind_before_invocation_id=rewind_invocation_id,
)
```

***rewind*** メソッドを呼ぶと、ADK が管理するセッションレベルのリソースはすべて、
指定した ***invocation id*** の *直前* の状態に復元されます。ただし、
アプリレベルやユーザーレベルの状態・アーティファクトなどのグローバルリソースは
復元されません。セッション巻き戻しの完全な例は
[rewind_session](https://github.com/google/adk-python/tree/main/contributing/samples/rewind_session)
サンプルコードを参照してください。Rewind 機能の制限事項の詳細は
[制限事項](#limitations) を参照してください。

## 仕組み

Rewind 機能は、invocation id で指定した巻き戻しポイントの *前* の状態へ
セッション状態とアーティファクトを復元する、特別な ***rewind*** リクエストを生成します。
この方式では、巻き戻されたリクエストも含め、すべてのリクエストが
後でデバッグ、分析、監査できるようログに保持されます。巻き戻し後、
システムは AI モデルへ次のリクエストを準備する際に、巻き戻されたリクエストを
無視します。つまり、エージェントが使用する AI モデルは、巻き戻しポイントから
次のリクエストまでのやり取りを実質的に忘れた状態になります。

## 制限事項 {#limitations}

Rewind 機能をエージェントのワークフローで使う際に注意すべき制限事項:

*   **グローバルなエージェントリソース:** アプリレベルおよびユーザーレベルの状態・アーティファクトは、
    Rewind 機能では *復元されません*。復元されるのはセッションレベルの状態・アーティファクトのみです。
*   **外部依存:** Rewind 機能は外部依存を管理しません。
    エージェント内のツールが外部システムと連携する場合、
    それらのシステムを以前の状態に戻す責任は利用者側にあります。
*   **原子性:** 状態更新、アーティファクト更新、イベント永続化は
    単一の原子的トランザクションでは実行されません。
    そのため不整合を防ぐために、アクティブセッションの巻き戻しや、
    巻き戻し中のセッションアーティファクト同時操作は避けてください。
