---
catalog_title: Slack
catalog_description: メンション、DM、スレッドの返信に答えるボットとしてエージェントを実行します
catalog_icon: /integrations/assets/slack.png
catalog_tags: ["connectors", "google"]
---

# ADK 向け Slack ランナー

<div class="language-support-tag"><span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span></div>

ADK は [Socket Mode](https://api.slack.com/apis/connections/socket) を使用してエージェントを Slack に直接デプロイするための `SlackRunner` クラスを提供します。この統合は、イベントの受信、レスポンスの送信、および会話スレッドの自動管理を処理するアダプターとして機能します。

## ユースケース

- **Socket Mode デプロイ**: 公開 HTTP エンドポイントを公開することなく、ワークスペースのイベントをエージェントにルーティングします。
- **スレッド管理**: ダイレクト メッセージやネストされたスレッドの返信全体で継続的な会話コンテキストを維持します。
- **イベント駆動型トリガー**: ダイレクト メッセージやアプリのメンションを使用してエージェント ワークフローを自動的に有効化します。

## 前提条件

- [Slack API ダッシュボード](https://api.slack.com/apps) で構成された Slack アプリ。まず Slack アカウントにサインインする必要があります。
- `app_mentions:read`、`chat:write`、および `im:history` ボット トークン スコープを持つボット ユーザー OAuth トークン（`xoxb-...`）。
- `connections:write` スコープを持つ WebSocket アプリレベル トークン（`xapp-...`）。

## インストール

ターミナルで次のコマンドを実行して、必要な Slack Socket Mode 依存関係とともに ADK をインストールします。

```bash
pip install "google-adk[slack]"
```

## エージェントでの使用

この例では、エージェントを Slack にデプロイするためのエンドツーエンドのセットアップを示します。コア エージェントを構成し、会話履歴を管理するためのインメモリ セッションを確立し、Socket Mode とともに SlackRunner を使用してワークスペースに接続し、受信用イベントを処理します。

```python
import asyncio
import os
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.integrations.slack import SlackRunner
from slack_bolt.app.async_app import AsyncApp

# コア エージェントの定義
root_agent = Agent(
    model="gemini-flash-latest",
    name="slack_agent",
    instruction="You are a helpful team assistant running on Slack.",
)

# Socket Mode 経由で Slack に接続
runner = Runner(
    app_name="slack_agent",
    agent=root_agent,
    session_service=InMemorySessionService(),
    auto_create_session=True,
)
slack_app = AsyncApp(token=os.environ["SLACK_BOT_TOKEN"])
slack_runner = SlackRunner(runner, slack_app)

asyncio.run(slack_runner.start(os.environ["SLACK_APP_TOKEN"]))
```

## その他のリソース

- [Slack API ドキュメント](https://api.slack.com/docs)
- [PyPI の google-adk](https://pypi.org/project/google-adk/)
