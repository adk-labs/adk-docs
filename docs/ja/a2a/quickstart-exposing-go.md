# クイックスタート: A2A経由でリモートエージェントを公開する

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-go">Go</span><span class="lst-preview">実験的</span>
</div>

このクイックスタートでは、開発者にとって最も一般的な出発点である**「エージェントがあります。他のエージェントがA2A経由で私のエージェントを使用できるように公開するにはどうすればよいですか？」**について説明します。これは、さまざまなエージェントが連携して対話する必要がある複雑なマルチエージェントシステムを構築するために不可欠です。

## 概要

このサンプルは、ADKエージェントを簡単に公開して、A2Aプロトコルを使用して別のエージェントから利用できるようにする方法を示しています。

Goでは、A2Aランチャーを使用してエージェントを公開します。これにより、エージェントカードが動的に生成されます。

```text
┌─────────────────┐                             ┌───────────────────────────────┐
│   ルートエージェント    │       A2Aプロトコル          │ A2A公開された素数チェックエージェント │
│                 │────────────────────────────▶│      （localhost: 8001）        │
└─────────────────┘                             └───────────────────────────────┘
```

このサンプルは、以下で構成されています。

- **リモートプライムエージェント**（`remote_a2a/check_prime_agent/main.go`）：他のエージェントがA2A経由で使用できるように公開したいエージェントです。素数チェックを処理するエージェントです。A2Aランチャーを使用して公開されます。
- **ルートエージェント**（`main.go`）：リモートプライムエージェントを呼び出すだけの単純なエージェントです。

## A2Aランチャーでリモートエージェントを公開する

Go ADKを使用して構築された既存のエージェントを取得し、A2Aランチャーを使用してA2A互換にすることができます。

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
│       └── main.go    # リモートプライムエージェント
├── go.mod
├── go.sum
└── main.go            # ルートエージェント
```

#### ルートエージェント（`a2a_basic/main.go`）

- **`newRootAgent`**：リモートA2Aサービスに接続するローカルエージェントです。

#### リモートプライムエージェント（`a2a_basic/remote_a2a/check_prime_agent/main.go`）

- **`checkPrimeTool`**：素数チェック用の関数です。
- **`main`**：エージェントを作成し、A2Aサーバーを起動するメイン関数です。

### 2. リモートA2Aエージェントサーバーの起動 { #start-the-remote-a2a-agent-server }

これで、`check_prime_agent`をホストするリモートエージェントサーバーを起動できます。

```bash
# リモートエージェントを起動します
go run remote_a2a/check_prime_agent/main.go
```

実行すると、次のようなものが表示されます。

```shell
2025/11/06 11:00:19 Starting A2A prime checker server on port 8001
2025/11/06 11:00:19 Starting the web server: &{port:8001}
2025/11/06 11:00:19 
2025/11/06 11:00:19 Web servers starts on http://localhost:8001
2025/11/06 11:00:19        a2a:  you can access A2A using jsonrpc protocol: http://localhost:8001
```

### 3. リモートエージェントが実行されていることを確認する { #check-that-your-remote-agent-is-running }

A2Aランチャーによって自動生成されたエージェントカードにアクセスして、エージェントが起動して実行されていることを確認できます。

[http://localhost:8001/.well-known/agent-card.json](http://localhost:8001/.well-known/agent-card.json)

エージェントカードの内容が表示されます。

### 4. メイン（利用側）エージェントの実行 { #run-the-main-consuming-agent }

リモートエージェントが実行されたので、メインエージェントを実行できます。

```bash
# 別のターミナルで、メインエージェントを実行します
go run main.go
```

#### 仕組み

リモートエージェントは、`main`関数のA2Aランチャーを使用して公開されます。ランチャーは、サーバーの起動とエージェントカードの生成を処理します。

```go title="remote_a2a/check_prime_agent/main.go"
--8<-- "examples/go/a2a_basic/remote_a2a/check_prime_agent/main.go:a2a-launcher"
```

## 対話の例

両方のサービスが実行されたら、ルートエージェントと対話して、A2A経由でリモートエージェントを呼び出す方法を確認できます。

**素数判定：**

この対話では、A2A経由でリモートエージェントであるプライムエージェントを使用します。

```text
ユーザー：サイコロを振って、それが素数かどうかを確認してください
ボット：わかりました。まずサイコロを振って、その結果が素数かどうかを確認します。

ボットがツールを呼び出します：transfer_to_agent、引数：map[agent_name:roll_agent]
ボットがツールを呼び出します：roll_die、引数：map[sides:6]
ボットがツールを呼び出します：transfer_to_agent、引数：map[agent_name:prime_agent]
ボットがツールを呼び出します：prime_checking、引数：map[nums:[3]]
ボット：3は素数です。
...
```

## 次のステップ

A2Aサーバー経由でリモートエージェントを公開するエージェントを作成したので、次のステップは別のエージェントからそれを利用する方法を学ぶことです。

- [**A2Aクイックスタート（利用）**](./quickstart-consuming-go.md)：エージェントがA2Aプロトコルを使用して他のエージェントを使用する方法を学びます。
