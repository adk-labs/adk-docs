# クイックスタート: A2A経由でリモートエージェントを公開する

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span><span class="lst-preview">実験的</span>
</div>

このクイックスタートでは、開発者にとって最も一般的な出発点である**「エージェントがあります。他のエージェントがA2A経由で私のエージェントを使用できるように公開するにはどうすればよいですか？」**について説明します。これは、さまざまなエージェントが連携して対話する必要がある複雑なマルチエージェントシステムを構築するために不可欠です。

## 概要

このサンプルは、ADKエージェントを簡単に公開して、A2Aプロトコルを使用して別のエージェントから利用できるようにする方法を示しています。

ADKエージェントをA2A経由で公開するには、主に2つの方法があります。

* **`to_a2a(root_agent)`関数を使用する**: `adk deploy api_server`の代わりに`uvicorn`経由でサーバーを介して公開できるように、既存のエージェントをA2Aで動作するように変換したいだけの場合は、この関数を使用します。つまり、エージェントを本番環境に対応させたい場合に`uvicorn`経由で公開したいものをより厳密に制御できます。さらに、`to_a2a()`関数は、エージェントコードに基づいてエージェントカードを自動生成します。
* **独自のエージェントカード（`agent.json`）を作成し、`adk api_server --a2a`を使用してホストする**: このアプローチには主に2つの利点があります。まず、`adk api_server --a2a`は`adk web`と連携して動作するため、エージェントの利用、デバッグ、テストが簡単になります。次に、`adk api_server`を使用すると、複数の個別のエージェントを持つ親フォルダーを指定できます。エージェントカード（`agent.json`）を持つエージェントは、同じサーバーを介して他のエージェントがA2A経由で自動的に利用できるようになります。ただし、独自のエージェントカードを作成する必要があります。エージェントカードを作成するには、[A2A Pythonチュートリアル](https://a2a-protocol.org/latest/tutorials/python/1-introduction/)に従ってください。

このクイックスタートでは、エージェントを公開する最も簡単な方法であり、舞台裏でエージェントカードを自動生成するため、`to_a2a()`に焦点を当てます。`adk api_server`アプローチを使用したい場合は、[A2Aクイックスタート（利用）ドキュメント](quickstart-consuming.md)でその使用法を確認できます。

```text
前:
                                                ┌────────────────────┐
                                                │ Hello Worldエージェント  │
                                                │  （Pythonオブジェクト）   │
                                                | エージェントカードなし │
                                                └────────────────────┘

                                                          │
                                                          │ to_a2a()
                                                          ▼

後:
┌────────────────┐                             ┌───────────────────────────────┐
│   ルートエージェント   │       A2Aプロトコル          │ A2A公開Hello Worldエージェント │
│(RemoteA2aAgent)│────────────────────────────▶│      （localhost: 8001）         │
│(localhost:8000)│                             └───────────────────────────────┘
└────────────────┘
```

このサンプルは、以下で構成されています。

- **リモートHello Worldエージェント**（`remote_a2a/hello_world/agent.py`）：他のエージェントがA2A経由で使用できるように公開したいエージェントです。サイコロを振ったり、素数を確認したりするエージェントです。`to_a2a()`関数を使用して公開され、`uvicorn`を使用して提供されます。
- **ルートエージェント**（`agent.py`）：リモートHello Worldエージェントを呼び出すだけの単純なエージェントです。

## `to_a2a(root_agent)`関数でリモートエージェントを公開する

ADKを使用して構築された既存のエージェントを取得し、`to_a2a()`関数を使用してラップするだけでA2A互換にすることができます。たとえば、`root_agent`に次のように定義されたエージェントがある場合：

```python
# ここにエージェントコード
root_agent = Agent(
    model='gemini-2.0-flash',
    name='hello_world_agent',
    
    <...your agent code...>
)
```

次に、`to_a2a(root_agent)`を使用するだけで簡単にA2A互換にすることができます。

```python
from google.adk.a2a.utils.agent_to_a2a import to_a2a

# エージェントをA2A互換にする
a2a_app = to_a2a(root_agent, port=8001)
```

`to_a2a()`関数は、[ADKエージェントからスキル、機能、メタデータを抽出する](https://github.com/google/adk-python/blob/main/src/google/adk/a2a/utils/agent_card_builder.py)ことで、舞台裏でメモリ内にエージェントカードを自動生成するため、`uvicorn`を使用してエージェントエンドポイントが提供されるときに、既知のエージェントカードが利用可能になります。

`agent_card`パラメータを使用して独自のエージェントカードを提供することもできます。値は`AgentCard`オブジェクトまたはエージェントカードJSONファイルへのパスにすることができます。

**`AgentCard`オブジェクトの例：**
```python
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from a2a.types import AgentCard

# A2Aエージェントカードを定義する
my_agent_card = AgentCard(
    name="file_agent",
    url="http://example.com",
    description="Test agent from file",
    version="1.0.0",
    capabilities={},
    skills=[],
    defaultInputModes=["text/plain"],
    defaultOutputModes=["text/plain"],
    supportsAuthenticatedExtendedCard=False,
)
a2a_app = to_a2a(root_agent, port=8001, agent_card=my_agent_card)
```

**JSONファイルへのパスの例：**
```python
from google.adk.a2a.utils.agent_to_a2a import to_a2a

# ファイルからA2Aエージェントカードを読み込む
a2a_app = to_a2a(root_agent, port=8001, agent_card="/path/to/your/agent-card.json")
```

それでは、サンプルコードを見ていきましょう。

### 1. サンプルコードの取得 { #getting-the-sample-code }

まず、必要な依存関係がインストールされていることを確認してください。

```bash
pip install google-adk[a2a]
```

[**a2a_root** サンプル](https://github.com/google/adk-python/tree/main/contributing/samples/a2a_root)をクローンして移動できます。

```bash
git clone https://github.com/google/adk-python.git
```

ご覧のとおり、フォルダー構造は次のようになっています。

```text
a2a_root/
├── remote_a2a/
│   └── hello_world/    
│       ├── __init__.py
│       └── agent.py    # リモートHello Worldエージェント
├── README.md
└── agent.py            # ルートエージェント
```

#### ルートエージェント（`a2a_root/agent.py`）

- **`root_agent`**：リモートA2Aサービスに接続する`RemoteA2aAgent`
- **エージェントカードURL**：リモートサーバー上の既知のエージェントカードエンドポイントを指します

#### リモートHello Worldエージェント（`a2a_root/remote_a2a/hello_world/agent.py`）

- **`roll_die(sides: int)`**：状態管理付きのサイコロを振るための関数ツール
- **`check_prime(nums: list[int])`**：素数判定用の非同期関数
- **`root_agent`**：包括的な指示を持つメインエージェント
- **`a2a_app`**：`to_a2a()`ユーティリティを使用して作成されたA2Aアプリケーション

### 2. リモートA2Aエージェントサーバーの起動 { #start-the-remote-a2a-agent-server }

これで、hello_worldエージェント内の`a2a_app`をホストするリモートエージェントサーバーを起動できます。

```bash
# 現在の作業ディレクトリがadk-python/であることを確認してください
# uvicornを使用してリモートエージェントを起動します
uvicorn contributing.samples.a2a_root.remote_a2a.hello_world.agent:a2a_app --host localhost --port 8001
```

??? note "なぜポート8001を使用するのですか？"
    このクイックスタートでは、ローカルでテストする場合、エージェントはlocalhostを使用するため、公開されたエージェント（リモートのプライムエージェント）のA2Aサーバーの`port`は、利用側エージェントのポートとは異なる必要があります。利用側エージェントと対話する`adk web`のデフォルトポートは`8000`であるため、A2Aサーバーは別のポート`8001`を使用して作成されます。

実行すると、次のようなものが表示されます。

```shell
INFO:     Started server process [10615]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://localhost:8001 (Press CTRL+C to quit)
```

### 3. リモートエージェントが実行されていることを確認する { #check-that-your-remote-agent-is-running }

`a2a_root/remote_a2a/hello_world/agent.py`の`to_a2a()`関数の一部として以前に自動生成されたエージェントカードにアクセスして、エージェントが起動して実行されていることを確認できます。

[http://localhost:8001/.well-known/agent-card.json](http://localhost:8001/.well-known/agent-card.json)

エージェントカードの内容が表示され、次のようになっているはずです。

```json
{"capabilities":{},"defaultInputModes":["text/plain"],"defaultOutputModes":["text/plain"],"description":"hello world agent that can roll a dice of 8 sides and check prime numbers.","name":"hello_world_agent","protocolVersion":"0.2.6","skills":[{"description":"hello world agent that can roll a dice of 8 sides and check prime numbers. 
      I roll dice and answer questions about the outcome of the dice rolls.
      I can roll dice of different sizes.
      I can use multiple tools in parallel by calling functions in parallel(in one request and in one round).
      It is ok to discuss previous dice roles, and comment on the dice rolls.
      When I are asked to roll a die, I must call the roll_die tool with the number of sides. Be sure to pass in an integer. Do not pass in a string.
      I should never roll a die on my own.
      When checking prime numbers, call the check_prime tool with a list of integers. Be sure to pass in a list of integers. I should never pass in a string.
      I should not check prime numbers before calling the tool.
      When I are asked to roll a die and check prime numbers, I should always make the following two function calls:
      1. I should first call the roll_die tool to get a roll. Wait for the function response before calling the check_prime tool.
      2. After I get the function response from roll_die tool, I should call the check_prime tool with the roll_die result.
        2.1 If user asks I to check primes based on previous rolls, make sure I include the previous rolls in the list.
      3. When I respond, I must include the roll_die result from step 1.
      I should always perform the previous 3 steps when asking for a roll and checking prime numbers.
      I should not rely on the previous history on prime results.
    ","id":"hello_world_agent","name":"model","tags":["llm"]},{"description":"Roll a die and return the rolled result.\n\nArgs:\n  sides: The integer number of sides the die has.\n  tool_context:... [truncated]
```

### 4. メイン（利用側）エージェントの実行 { #run-the-main-consuming-agent }

リモートエージェントが実行されたので、開発UIを起動して、エージェントとして「a2a_root」を選択できます。

```bash
# 別のターミナルで、adk Webサーバーを実行します
adk web contributing/samples/
```

adk Webサーバーを開くには、[http://localhost:8000](http://localhost:8000)にアクセスしてください。

## 対話の例

両方のサービスが実行されたら、ルートエージェントと対話して、A2A経由でリモートエージェントを呼び出す方法を確認できます。

**単純なサイコロ振り：**
この対話では、ローカルエージェントであるロールエージェントを使用します。

```text
ユーザー：6面体のサイコロを振ってください
ボット：4を振りました。
```

**素数判定：**

この対話では、A2A経由でリモートエージェントであるプライムエージェントを使用します。

```text
ユーザー：7は素数ですか？
ボット：はい、7は素数です。
```

**組み合わせた操作：**

この対話では、ローカルのロールエージェントとリモートのプライムエージェントの両方を使用します。

```text
ユーザー：10面体のサイコロを振って、それが素数かどうかを確認してください
ボット：8を振りました。
ボット：8は素数ではありません。
```

## 次のステップ

A2Aサーバー経由でリモートエージェントを公開するエージェントを作成したので、次のステップは別のエージェントからそれを利用する方法を学ぶことです。

- [**A2Aクイックスタート（利用）**](./quickstart-consuming.md)：エージェントがA2Aプロトコルを使用して他のエージェントを使用する方法を学びます。
