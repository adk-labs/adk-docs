# クイックスタート: A2A経由でリモートエージェントを公開する

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-java">Java</span><span class="lst-preview">実験的</span>
</div>

このクイックスタートでは、開発者にとって最も一般的な出発点である**「エージェントがある。ほかのエージェントがA2A経由で自分のエージェントを使えるようにするにはどうすればよいですか？」**について説明します。これは、さまざまなエージェントが協力して相互作用する必要がある複雑なマルチエージェントシステムを構築するうえで重要です。

## 概要

このサンプルでは、Quarkus を使って ADK エージェントを公開し、別のエージェントが A2A Protocol を使ってそれを利用できるようにする方法を示します。

Java では、ADK A2A extension に依存して A2A サーバーをネイティブに構築します。Quarkus フレームワークを使うため、標準の Quarkus `@ApplicationScoped` バインディング内でエージェントを直接設定するだけで済みます。

```text
┌─────────────────┐                             ┌───────────────────────────────┐
│   Root Agent    │       A2A Protocol          │ A2A-Exposed Check Prime Agent │
│                 │────────────────────────────▶│       (localhost:9090)        │
└─────────────────┘                             └───────────────────────────────┘
```

## Quarkusでリモートエージェントを公開する

Quarkus を使うと、受信する HTTP JSON-RPC ペイロードやセッションを手動で扱わずに、エージェントを A2A 実行エンドポイントへマッピングできます。

### 1. サンプルコードを取得する { #getting-the-sample-code }

最も早い開始方法は、[**`adk-java`** リポジトリ](https://github.com/google/adk-java) 内の `contrib/samples/a2a_server` フォルダにあるスタンドアロンの Quarkus アプリを確認することです。

```bash
cd contrib/samples/a2a_server
```

### 2. 動作の仕組み

コアランタイムは提供される `AgentExecutor` を使用し、ネイティブ `BaseAgent` を構成する CDI `@Produces` bean の作成を要求します。Quarkus A2A extension はこれを検出し、エンドポイントを自動的に配線します。

```java title="A2aExposingSnippet.java"
--8<-- "examples/java/snippets/src/main/java/a2a/A2aExposingSnippet.java:a2a-launcher"
```

アプリは、HTTP でマウントされた `/a2a/remote/v1/message:send` に届く JSON-RPC 呼び出しを自動的に処理し、一部、履歴、コンテキストを直接 `BaseAgent` のフローへ渡します。

### 3. リモート A2A エージェントサーバーを起動する { #start-the-remote-a2a-agent-server }

ネイティブ ADK 構成では、Quarkus の開発モードタスクを実行できます。

```bash
./mvnw -f contrib/samples/a2a_server/pom.xml quarkus:dev
```

実行すると、Quarkus が A2A 準拠の REST パスを自動的にホストします。手動の `curl` を使えば、ネイティブ A2A 仕様でペイロードをすぐにスモークテストできます。

```bash
curl -X POST http://localhost:9090 \
  -H "Content-Type: application/json" \
  -d '{
        "jsonrpc": "2.0",
        "id": "cli-check",
        "method": "message/send",
        "params": {
          "message": {
            "kind": "message",
            "contextId": "cli-demo-context",
            "messageId": "cli-check-id",
            "role": "user",
            "parts": [
              { "kind": "text", "text": "Is 3 prime?" }
            ]
          }
        }
      }'
```

### 4. リモートエージェントが実行中であることを確認する { #check-that-your-remote-agent-is-running }

適切なエージェントカードは、次の標準パスで自動的に公開されます。
[http://localhost:9090/.well-known/agent-card.json](http://localhost:9090/.well-known/agent-card.json)

レスポンスJSON内で、エージェント設定から動的に反映された名前が見えるはずです。

## 次のステップ

これで、A2A 経由でエージェントを公開できました。次は、別のエージェントオーケストレーターからそれをネイティブに利用する方法を学びましょう。

- [**A2A クイックスタート（利用） for Java**](./quickstart-consuming-java.md): エージェントオーケストレーターのラッパーが公開済みサービスへ下流接続する方法を学びます。
