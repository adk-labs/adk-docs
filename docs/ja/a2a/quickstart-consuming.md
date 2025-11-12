# クイックスタート: A2A経由でリモートエージェントを利用する

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span><span class="lst-preview">実験的</span>
</div>

このクイックスタートでは、開発者にとって最も一般的な出発点である**「リモートエージェントがあり、ADKエージェントでA2A経由でそれを使用するにはどうすればよいですか？」**について説明します。これは、さまざまなエージェントが連携して対話する必要がある複雑なマルチエージェントシステムを構築するために不可欠です。

## 概要

このサンプルは、Agent Development Kit（ADK）の**Agent2Agent（A2A）**アーキテクチャを示し、複数のエージェントが連携して複雑なタスクを処理する方法を紹介します。このサンプルでは、サイコロを振って数字が素数かどうかを確認できるエージェントを実装しています。

```text
┌─────────────────┐    ┌──────────────────┐    ┌────────────────────┐
│   ルートエージェント    │───▶│   ロールエージェント     │    │   リモートプライム     │
│  （ローカル）        │    │   （ローカル）        │    │   エージェント            │
│                 │    │                  │    │  （localhost:8001）  │
│                 │───▶│                  │◀───│                    │
└─────────────────┘    └──────────────────┘    └────────────────────┘
```

A2A基本サンプルは、以下で構成されています。

- **ルートエージェント**（`root_agent`）：特殊なサブエージェントにタスクを委任するメインオーケストレーター
- **ロールエージェント**（`roll_agent`）：サイコロを振る操作を処理するローカルサブエージェント
- **プライムエージェント**（`prime_agent`）：数字が素数かどうかを確認するリモートA2Aエージェント。このエージェントは別のA2Aサーバーで実行されています。

## ADKサーバーでエージェントを公開する

ADKには、A2Aプロトコルを使用してエージェントを公開するための組み込みCLIコマンド`adk api_server --a2a`が付属しています。

`a2a_basic`の例では、まずローカルルートエージェントが使用できるように、A2Aサーバー経由で`check_prime_agent`を公開する必要があります。

### 1. サンプルコードの取得 { #getting-the-sample-code }

まず、必要な依存関係がインストールされていることを確認してください。

```bash
pip install google-adk[a2a]
```

[**`a2a_basic`** サンプル](https://github.com/google/adk-python/tree/main/contributing/samples/a2a_basic)をクローンして移動できます。

```bash
git clone https://github.com/google/adk-python.git
```

ご覧のとおり、フォルダー構造は次のようになっています。

```text
a2a_basic/
├── remote_a2a/
│   └── check_prime_agent/
│       ├── __init__.py
│       ├── agent.json
│       └── agent.py
├── README.md
├── __init__.py
└── agent.py # ローカルルートエージェント
```

#### メインエージェント（`a2a_basic/agent.py`）

- **`roll_die(sides: int)`**：サイコロを振るための関数ツール
- **`roll_agent`**：サイコロ振りに特化したローカルエージェント
- **`prime_agent`**：リモートA2Aエージェントの構成
- **`root_agent`**：委任ロジックを備えたメインオーケストレーター

#### リモートプライムエージェント（`a2a_basic/remote_a2a/check_prime_agent/`）

- **`agent.py`**：素数判定サービスの実装
- **`agent.json`**：A2Aエージェントのエージェントカード
- **`check_prime(nums: list[int])`**：素数判定アルゴリズム

### 2. リモートプライムエージェントサーバーの起動 { #start-the-remote-prime-agent-server }

ADKエージェントがA2A経由でリモートエージェントを利用する方法を示すには、まずプライムエージェント（`check_prime_agent`の下）をホストするリモートエージェントサーバーを起動する必要があります。

```bash
# ポート8001でcheck_prime_agentを提供するリモートa2aサーバーを起動します
adk api_server --a2a --port 8001 contributing/samples/a2a_basic/remote_a2a
```

??? note "デバッグ用のロギングを追加する `--log_level debug`"
    デバッグレベルのロギングを有効にするには、`adk api_server`に`--log_level debug`を追加します。
    ```bash
    adk api_server --a2a --port 8001 contributing/samples/a2a_basic/remote_a2a --log_level debug
    ```
    これにより、エージェントのテスト時に検査できる、より豊富なログが提供されます。

??? note "なぜポート8001を使用するのですか？"
    このクイックスタートでは、ローカルでテストする場合、エージェントはlocalhostを使用するため、公開されたエージェント（リモートのプライムエージェント）のA2Aサーバーの`port`は、利用側エージェントのポートとは異なる必要があります。利用側エージェントと対話する`adk web`のデフォルトポートは`8000`であるため、A2Aサーバーは別のポート`8001`を使用して作成されます。

実行すると、次のようなものが表示されます。

``` shell
INFO:     Started server process [56558]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
```
  
### 3. リモートエージェントの必須エージェントカード（`agent-card.json`）に注意してください { #look-out-for-the-required-agent-card-agent-json-of-the-remote-agent }

A2Aプロトコルでは、各エージェントが何をするかを記述したエージェントカードを持っている必要があります。

他の誰かがすでにエージェントで利用しようとしているリモートA2Aエージェントを構築している場合は、エージェントカード（`agent-card.json`）があることを確認する必要があります。

このサンプルでは、`check_prime_agent`にはすでにエージェントカードが提供されています。

```json title="a2a_basic/remote_a2a/check_prime_agent/agent-card.json"

{
  "capabilities": {},
  "defaultInputModes": ["text/plain"],
  "defaultOutputModes": ["application/json"],
  "description": "An agent specialized in checking whether numbers are prime. It can efficiently determine the primality of individual numbers or lists of numbers.",
  "name": "check_prime_agent",
  "skills": [
    {
      "id": "prime_checking",
      "name": "Prime Number Checking",
      "description": "Check if numbers in a list are prime using efficient mathematical algorithms",
      "tags": ["mathematical", "computation", "prime", "numbers"]
    }
  ],
  "url": "http://localhost:8001/a2a/check_prime_agent",
  "version": "1.0.0"
}
```

??? note "ADKのエージェントカードに関する詳細情報"

    ADKでは、`to_a2a(root_agent)`ラッパーを使用してエージェントカードを自動的に生成できます。他のユーザーが使用できるように既存のエージェントを公開する方法について詳しく知りたい場合は、[A2Aクイックスタート（公開）](quickstart-exposing.md)チュートリアルをご覧ください。

### 4. メイン（利用側）エージェントの実行 { #run-the-main-consuming-agent }

  ```bash
  # 別のターミナルで、adk Webサーバーを実行します
  adk web contributing/samples/
  ```

#### 仕組み

メインエージェントは`RemoteA2aAgent()`関数を使用してリモートエージェント（この例では`prime_agent`）を利用します。以下に示すように、`RemoteA2aAgent()`には`name`、`description`、および`agent_card`のURLが必要です。

```python title="a2a_basic/agent.py"
<...code truncated...>

from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

prime_agent = RemoteA2aAgent(
    name="prime_agent",
    description="Agent that handles checking if numbers are prime.",
    agent_card=(
        f"http://localhost:8001/a2a/check_prime_agent{AGENT_CARD_WELL_KNOWN_PATH}"
    ),
)

<...code truncated>
```

次に、エージェントで`RemoteA2aAgent`を単純に使用できます。この場合、`prime_agent`は以下の`root_agent`のサブエージェントの1つとして使用されます。

```python title="a2a_basic/agent.py"
from google.adk.agents.llm_agent import Agent
from google.genai import types

root_agent = Agent(
    model="gemini-2.0-flash",
    name="root_agent",
    instruction="""
      <You are a helpful assistant that can roll dice and check if numbers are prime.
      You delegate rolling dice tasks to the roll_agent and prime checking tasks to the prime_agent.
      Follow these steps:
      1. If the user asks to roll a die, delegate to the roll_agent.
      2. If the user asks to check primes, delegate to the prime_agent.
      3. If the user asks to roll a die and then check if the result is prime, call roll_agent first, then pass the result to prime_agent.
      Always clarify the results before proceeding.>
    """,
    global_instruction=(
        "You are DicePrimeBot, ready to roll dice and check prime numbers."
    ),
    sub_agents=[roll_agent, prime_agent],
    tools=[example_tool],
    generate_content_config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(  # avoid false alarm about rolling dice.
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.OFF,
            ),
        ]
    ),
)
```

## 対話の例

メインエージェントとリモートエージェントの両方が実行されたら、ルートエージェントと対話して、A2A経由でリモートエージェントを呼び出す方法を確認できます。

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

A2Aサーバー経由でリモートエージェントを使用するエージェントを作成したので、次のステップは別のエージェントからそれに接続する方法を学ぶことです。

- [**A2Aクイックスタート（公開）**](./quickstart-exposing.md)：他のエージェントがA2Aプロトコル経由で既存のエージェントを使用できるように公開する方法を学びます。
