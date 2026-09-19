---
catalog_title: LiveKit
catalog_description: ライブ音声エージェントを WebRTC ルームや電話通話に接続します
catalog_icon: /integrations/assets/livekit.png
catalog_tags: ["connectors"]
---

# ADK 向け LiveKit ランナー

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v2.9.0</span><span class="lst-preview">試験運用中</span>
</div>

ADK は、WebRTC および SIP 電話通信のためのオープンソース プラットフォームである [LiveKit](https://livekit.io/) を介してライブエージェントを提供できる `LiveKitRunner` クラスを提供します。この統合は、オーディオおよびビデオのキャプチャ、再生、バージイン（割り込み）、キャプション、通話制御を処理するトランスポートアダプターとして機能するため、エージェントコードを変更することなく、ブラウザ、電話、ゲームクライアントから ADK エージェントに到達できるようになります。

## ユースケース

LiveKit は、ブラウザアプリ、モバイルアプリ、SIP 電話通話、ゲームやイマーシブクライアントなど、さまざまなユースケースで使用できます。

### ブラウザおよびモバイルアプリ

エージェントは通常の参加者（participant）としてルームに参加するため、任意の LiveKit クライアント SDK がエージェントと通信できます。コネクタは、LiveKit 自身のコンポーネントがバインドするチャンネルにキャプションと発話状態を発行するため、追加の配線なしでそれらのコンポーネントが ADK エージェントと連携します:

| LiveKit リソース | ADK エージェントが得られる機能 |
| :--- | :--- |
| [クライアント SDK](https://docs.livekit.io/transport/) | Browser、Swift、Android、Flutter、React Native、Unity、C++、Rust、ESP32 |
| [UI コンポーネント](https://github.com/orgs/livekit/repositories?q=components) | React、SwiftUI、Compose、Flutter 向けの事前構築済み音声アシスタントウィジェット |
| [スターターアプリ](https://github.com/livekit-examples) | プラットフォームごとの稼働可能なアプリ、およびフロントエンドなしでエージェントと対話できる Agents Playground |

### 電話通話

SIP 発信者は通常の LiveKit 参加者であるため、[インバウンドトランク](https://docs.livekit.io/telephony/accepting-calls/inbound-trunk/) と [ディスパッチルール](https://docs.livekit.io/telephony/accepting-calls/dispatch-rule/) がワーカーを指すように設定されると、電話通話がエージェントに届きます。

発信者の ID は発信者が話す前に ADK セッション状態に格納されるため、関数ツールは他の状態値と同様にそれを読み取ることができます:

```python
from google.adk.tools.tool_context import ToolContext

async def greet_by_account(tool_context: ToolContext) -> str:
  """発信者を確認してから挨拶します。"""
  number = tool_context.state.get("livekit_caller_phone_number")  # '+15105550100'
  if not number:
    return "I could not see the number you are calling from."
  return await crm.lookup(number)  # 独自の顧客照会ロジック
```

コネクタはキーパッド入力を単一のターンにバッファリングするため、6 桁の口座番号が 6 回の割り込みではなく 1 つの入力として届きます。

### ゲームおよびイマーシブクライアント

LiveKit の [Unity SDK](https://github.com/livekit/client-sdk-unity) は、LiveKit Cloud または自前でホストするサーバーをバックエンドとして、Unity アプリにリアルタイムのオーディオ、ビデオ、データチャンネルを追加します。ADK エージェントをルームに配置すると、プレイヤーは音声主導の NPC やゲーム内アシスタントのように、ゲーム世界に対しても働きかけるキャラクターと会話できます:

```python
from google.adk.integrations.livekit import current_call
from google.adk.tools.tool_context import ToolContext

async def open_the_door(door_id: str, tool_context: ToolContext) -> str:
  """ゲームワールド内のドアを開きます。"""
  call = current_call(tool_context)
  return await call.perform_rpc(method="open_door", payload=door_id)
```

クライアントが返す内容はすべてモデルが解説するツール結果となるため、エージェントは実際に何が起きたかを説明できます。Unity クライアント側では 1 つの RPC メソッドを登録するだけで済み、ADK が会話、ツール呼び出し、セッションを管理します。

## はじめに

- `livekit` エクストラを含む [ADK](https://adk.dev) >= 2.9.0。
- [ライブモデル](../live/models.md) の認証情報。
- セルフホスト型または LiveKit Cloud 上の LiveKit サーバー。どちらも同じ API を公開しているため、同じワーカーコードが両方に対して実行できます。ローカル開発の場合は `livekit-server --dev` を実行します。
- 環境変数に設定された `LIVEKIT_URL`、`LIVEKIT_API_KEY`、`LIVEKIT_API_SECRET`。

```bash
pip install "google-adk[livekit]" "livekit-agents>=1.4"
```

すでに作成済みのエージェントから始められます。`LiveKitToolset()` を追加すると、通話の切断や発信者の転送などの通話制御機能が利用可能になります。このツールセットは通話が存在する場合にのみアクティブになるため、`adk web` でもエージェントは変更なしで実行できます:

```python
from google.adk.agents import Agent
from google.adk.integrations.livekit import LiveKitToolset
from google.adk.runners import InMemoryRunner

root_agent = Agent(
    model="gemini-live-2.5-flash-native-audio",
    name="support_agent",
    instruction="You help customers troubleshoot their home internet.",
    tools=[check_line_status, LiveKitToolset()],  # check_line_status は独自のツールです
)
runner = InMemoryRunner(agent=root_agent, app_name="support")
```

エージェントを接続するには、ランナーに接続済みのルームを渡します。本番環境では通話ごとに LiveKit がディスパッチするワーカーを実行し、同じコードでブラウザと電話の両方に対応します。

```python
from google.adk.integrations.livekit import LiveKitRunner
from livekit.agents import AgentServer
from livekit.agents import cli
from livekit.agents import JobContext

server = AgentServer()


@server.rtc_session(agent_name="support")
async def entrypoint(ctx: JobContext) -> None:
  """ディスパッチされた通話を ADK エージェントにブリッジします。"""
  await ctx.connect()
  # LiveKit には ADK のユーザー ID やセッション ID がありません。サンプルではジョブのメタデータから読み取ります。
  await LiveKitRunner(
      runner=runner, room=ctx.room, user_id="live-user", session_id=ctx.room.name
  ).start()


if __name__ == "__main__":
  cli.run_app(server)
```

## ワーカーのデプロイ

ワーカーは LiveKit サーバーにアウトバウンド接続を行い、その同じ接続経由でディスパッチされたジョブを受信するため、アウトバウンドのネットワークアクセスのみが必要で、パブリックアドレスやロードバランサーは不要です。それ以外は通常の ADK コンテナと同じであり、他の ADK エージェントと同様にデプロイされます。エントリポイントがワーカーモジュールを指すように設定してください:

```dockerfile
CMD ["python", "-m", "support_agent.livekit_worker", "start"]
```

[Agents CLI](../get-started/agents-cli.md) は、`pyproject.toml` の `deployment_target` に従ってそのコンテナを Agent Runtime、Cloud Run、または GKE にデプロイします。[Agents CLI によるデプロイ](../deploy/agent-runtime/agents-cli.md) を参照するか、[Cloud Run](../deploy/cloud-run.md) または [GKE](../deploy/gke.md) に手動でデプロイしてください。

Cloud Run は `$PORT` をプローブしますが、ワーカーは固定ポートでヘルスチェックエンドポイントを提供するため、両者を一致させる必要があります。サーバー作成時に環境変数からポートを読み込むように設定します:

```python
import os

server = AgentServer(port=int(os.environ["PORT"]))
```

`--port=8081` でデプロイしても同様に動作します（これは本番環境でワーカーが使用するポートです）。また、ワーカーは通話と通話の間はアイドル状態になるため、ディスパッチを受け入れ続けられるように `--no-cpu-throttling` と `--min-instances=1` を指定して実行してください。

ディスパッチされた各ジョブは独自のプロセスで実行されるため、永続的な [セッションサービス](../sessions/index.md) を使用してください。`InMemoryRunner` クラスは通話間で何も永続化しません。

## その他のリソース

- [LiveKit サンプル](https://github.com/google/adk-python/tree/main/contributing/samples/integrations/livekit)
- [ライブおよび音声エージェント](../live/index.md)
- [カスタムサーバーの構築](../live/custom-server.md)
- [LiveKit ドキュメント](https://docs.livekit.io/)
