# クイックスタート: A2A経由でリモートエージェントを利用する

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-go">Go</span><span class="lst-preview">実験的</span>
</div>

このクイックスタートでは、開発者にとって最も一般的な出発点である**「リモートエージェントがあり、ADKエージェントでA2A経由でそれを使用するにはどうすればよいですか？」**について説明します。これは、さまざまなエージェントが連携して対話する必要がある複雑なマルチエージェントシステムを構築するために不可欠です。

## 概要

このサンプルは、Agent Development Kit（ADK）の**Agent-to-Agent（A2A）**アーキテクチャを示し、複数のエージェントが連携して複雑なタスクを処理する方法を紹介します。このサンプルでは、サイコロを振って数字が素数かどうかを確認できるエージェントを実装しています。

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

`a2a_basic`の例では、まずローカルルートエージェントが使用できるように、A2Aサーバー経由で`check_prime_agent`を公開する必要があります。

### 1. サンプルコードの取得 { #getting-the-sample-code }

まず、Goがインストールされ、環境が設定されていることを確認してください。

[**`a2a_basic`** サンプル](https://github.com/google/adk-docs/tree/main/examples/go/a2a_basic)をクローンして移動できます。

```bash
cd examples/go/a2a_basic
```

ご覧のとおり、フォルダー構造は次のようになっています。

```text
a2a_basic/
├── remote_a2a/
│   └── check_prime_agent/
│       └── main.go
├── go.mod
├── go.sum
└── main.go # ローカルルートエージェント
```

#### メインエージェント（`a2a_basic/main.go`）

- **`rollDieTool`**：サイコロを振るための関数ツール
- **`newRollAgent`**：サイコロ振りに特化したローカルエージェント
- **`newPrimeAgent`**：リモートA2Aエージェントの構成
- **`newRootAgent`**：委任ロジックを備えたメインオーケストレーター

#### リモートプライムエージェント（`a2a_basic/remote_a2a/check_prime_agent/main.go`）

- **`checkPrimeTool`**：素数判定アルゴリズム
- **`main`**：素数判定サービスとA2Aサーバーの実装

### 2. リモートプライムエージェントサーバーの起動 { #start-the-remote-prime-agent-server }

ADKエージェントがA2A経由でリモートエージェントを利用する方法を示すには、まずプライムエージェント（`check_prime_agent`の下）をホストするリモートエージェントサーバーを起動する必要があります。

```bash
# ポート8001でcheck_prime_agentを提供するリモートa2aサーバーを起動します
go run remote_a2a/check_prime_agent/main.go
```

実行すると、次のようなものが表示されます。

``` shell
2025/11/06 11:00:19 Starting A2A prime checker server on port 8001
2025/11/06 11:00:19 Starting the web server: &{port:8001}
2025/11/06 11:00:19 
2025/11/06 11:00:19 Web servers starts on http://localhost:8001
2025/11/06 11:00:19        a2a:  you can access A2A using jsonrpc protocol: http://localhost:8001
```
  
### 3. リモートエージェントの必須エージェントカードに注意してください { #look-out-for-the-required-agent-card-of-the-remote-agent }

A2Aプロトコルでは、各エージェントが何をするかを記述したエージェントカードを持っている必要があります。

Go ADKでは、A2Aランチャーを使用してエージェントを公開すると、エージェントカードが動的に生成されます。`http://localhost:8001/.well-known/agent-card.json`にアクセスして、生成されたカードを確認できます。

### 4. メイン（利用側）エージェントの実行 { #run-the-main-consuming-agent }

  ```bash
  # 別のターミナルで、メインエージェントを実行します
  go run main.go
  ```

#### 仕組み

メインエージェントは`remoteagent.New`を使用してリモートエージェント（この例では`prime_agent`）を利用します。以下に示すように、`Name`、`Description`、および`AgentCardSource` URLが必要です。

```go title="a2a_basic/main.go"
--8<-- "examples/go/a2a_basic/main.go:new-prime-agent"
```

次に、ルートエージェントでリモートエージェントを単純に使用できます。この場合、`primeAgent`は以下の`root_agent`のサブエージェントの1つとして使用されます。

```go title="a2a_basic/main.go"
--8<-- "examples/go/a2a_basic/main.go:new-root-agent"
```

## 対話の例

メインエージェントとリモートエージェントの両方が実行されたら、ルートエージェントと対話して、A2A経由でリモートエージェントを呼び出す方法を確認できます。

**単純なサイコロ振り：**
この対話では、ローカルエージェントであるロールエージェントを使用します。

```text
ユーザー：6面体のサイコロを振ってください
ボットがツールを呼び出します：transfer_to_agent、引数：map[agent_name:roll_agent]
ボットがツールを呼び出します：roll_die、引数：map[sides:6]
ボット：6面体のサイコロを振った結果は6です。
```

**素数判定：**

この対話では、A2A経由でリモートエージェントであるプライムエージェントを使用します。

```text
ユーザー：7は素数ですか？
ボットがツールを呼び出します：transfer_to_agent、引数：map[agent_name:prime_agent]
ボットがツールを呼び出します：prime_checking、引数：map[nums:[7]]
ボット：はい、7は素数です。
```

**組み合わせた操作：**

この対話では、ローカルのロールエージェントとリモートのプライムエージェントの両方を使用します。

```text
ユーザー：サイコロを振って、それが素数かどうかを確認してください
ボット：わかりました。まずサイコロを振って、その結果が素数かどうかを確認します。

ボットがツールを呼び出します：transfer_to_agent、引数：map[agent_name:roll_agent]
ボTットがツールを呼び出します：roll_die、引数：map[sides:6]
ボットがツールを呼び出します：transfer_to_agent、引数：map[agent_name:prime_agent]
ボットがツールを呼び出します：prime_checking、引数：map[nums:[3]]
ボット：3は素数です。
```

## 次のステップ

A2Aサーバー経由でリモートエージェントを使用するエージェントを作成したので、次のステップは独自のエージェントを公開する方法を学ぶことです。

- [**A2Aクイックスタート（公開）**](./quickstart-exposing-go.md)：他のエージェントがA2Aプロトコル経由で既存のエージェントを使用できるように公開する方法を学びます。
