# 信頼性向上のための A2A 拡張

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python 1.27.0</span>
</div>

ADK は、更新版 [A2aAgentExecutor](https://github.com/google/adk-python/blob/main/src/google/adk/a2a/executor/a2a_agent_executor_impl.py)
クラスの一部として、Agent2Agent（A2A）サポート向けの拡張を提供し、メッセージとデータ処理を改善します。
更新版には、コアのエージェント実行ロジックに対するアーキテクチャ変更と、A2A のデータ処理を改善する拡張が含まれており、
既存の A2A エージェントとの後方互換性も維持されています。

A2A 拡張オプションを有効にすると、サーバーは更新版 agent executor 実装を使用するようになります。
この更新は一般的な利点をいくつか提供しますが、特に A2A と ADK の両方がストリーミングモードで動作する場合に、
レガシー A2A-ADK 実装で見つかった重大な制限を解消します。新しい実装は次の問題に対処します。

-   **メッセージの重複:** ユーザーメッセージがタスク履歴内で重複するのを防ぎます。
-   **出力の誤分類:** リモートエージェントの ADK 出力がイベント thought に誤って変換されるのを防ぎます。
-   **サブエージェントのデータ損失:** リモートエージェントのサブエージェントツリーに複数のエージェントが入れ子になっていても、リモートエージェントの ADK 出力が確実に保持されるようにし、データ損失をなくします。

## クライアント側の拡張有効化

クライアントは、トランスポート定義の [A2A 拡張](https://a2a-protocol.org/latest/topics/extensions/) 有効化メカニズムを通じて、この拡張を使いたいことを示します。
JSON-RPC と HTTP トランスポートでは `X-A2A-Extensions` HTTP ヘッダーで指定します。
gRPC では `X-A2A-Extensions` メタデータ値で指定します。

拡張を有効にするには、クライアントが `use_legacy=False` を指定して `RemoteA2aAgent` を生成します。
これにより、送信リクエストの要求拡張一覧に `https://adk.dev/a2a/a2a-extension/` が追加されます。
この拡張を有効にすると、サーバーは新しい agent executor 実装を使うことになります。

```python
from google.adk.agents import RemoteA2aAgent

remote_agent = RemoteA2aAgent(
    name="remote_agent",
    url="http://localhost:8000/a2a/remote_agent",
    use_legacy=False,
)
```

`A2aAgentExecutor` は、リクエスト内で a2a 拡張が検出されると、デフォルトで新しい実装を使用します。
新しい agent executor 実装を使わないようにするには、クライアントがこの拡張を送らないようにするだけです（`use_legacy=True` で `RemoteA2aAgent` を生成）。
あるいは、サーバー側の `A2aAgentExecutor` を `use_legacy=True` で生成することもできます。

## 仕組み

リクエストを受け取ると、[A2aAgentExecutor](https://github.com/google/adk-python/blob/main/src/google/adk/a2a/executor/a2a_agent_executor.py) が拡張を検出します。
クライアントが新しい agent executor ロジックの使用を要求していることを理解し、リクエストをそれに対応する新しい実装へルーティングします。
リクエストが受理されたことを確認できるように、この拡張はクライアントへ返されるレスポンスメタデータの "activated extensions" 一覧と、A2A Events のメタデータにも含まれます。

## Agent Card の定義

エージェントは AgentCapabilities.extensions 一覧内の AgentCard で、この拡張機能を広告します。

例となる AgentExtension ブロック:

```json
{
  "uri": "https://adk.dev/a2a/a2a-extension/",
  "description": "新しい agent executor 実装を利用できる機能",
  "required": false
}
```
