# クイックスタート: A2A経由でリモートエージェントを利用する

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-java">Java</span><span class="lst-preview">実験的</span>
</div>

このクイックスタートでは、開発者にとって最も一般的な出発点である**「リモートエージェントがあり、ADKエージェントでA2A経由でそれを使うにはどうすればよいですか？」**について説明します。これは、さまざまなエージェントが連携して相互作用する必要がある複雑なマルチエージェントシステムを構築するうえで重要です。

## 概要

このサンプルは、Agent Development Kit（ADK）for Java の **Agent2Agent（A2A）** アーキテクチャを示し、複数のエージェントが協力して複雑なタスクを処理する方法を紹介します。

```text
┌─────────────────┐    ┌─────────────────┐    ┌────────────────────────┐
│   Root Agent    │───▶│   Roll Agent    │    │   Remote Prime Agent   │
│   (Local)       │    │   (Local)       │    │   (localhost:8001)     │
│                 │───▶│                 │◀───│                        │
└─────────────────┘    └─────────────────┘    └────────────────────────┘
```

A2A Basic サンプルは次の要素で構成されています。

- **Root Agent** (`root_agent`): 専門化されたサブエージェントにタスクを委任するメインオーケストレーター
- **Roll Agent** (`roll_agent`): サイコロを振る処理を担当するローカルサブエージェント
- **Prime Agent** (`prime_agent`): 数字が素数かどうかを確認するリモートA2Aエージェントで、別のA2Aサーバー上で実行されます

## ADK Java SDKでエージェントを利用する

Java では、リクエストを手動で生成する代わりに、ADK が公式A2A SDK `Client` を `RemoteA2AAgent` エンティティの上に正確にラップして利用します。なお、Java SDK は現在 A2A Protocol 0.3 を使用しています。

### 1. サンプルコードを入手する { #getting-the-sample-code }

このクイックスタートに対応する Java ネイティブのサンプルは、`adk-java` ソースコードの `contrib/samples/a2a_basic` にあります。

[**`a2a_basic`** サンプル](https://github.com/google/adk-java/tree/main/contrib/samples/a2a_basic)を開いてください。

```bash
cd contrib/samples/a2a_basic
```

### 2. リモート Prime Agent サーバーを起動する { #start-the-remote-prime-agent-server }

ADK エージェントが A2A 経由でリモートエージェントを利用できることを示すには、まずリモートエージェントサーバーを実行しておく必要があります。独自のA2Aサーバーを任意の言語で実装することもできますが、ADK には `a2a_server` サンプルがあり、` :9090` でエージェントをホストする Quarkus サービスを起動します。

```bash
# adk-java のルートで、9090 ポートの事前構成済み Quarkus リモートサービスを起動します
./mvnw -f contrib/samples/a2a_server/pom.xml quarkus:dev
```

正常に起動すると、エージェントはローカルの HTTP エンドポイント経由でアクセスできるようになります。

### 3. リモートエージェントに必要なエージェントカードを確認する { #look-out-for-the-required-agent-card-of-the-remote-agent }

A2A Protocol では、各エージェントがネットワーク上の他ノードに対して何を行うかを説明するエージェントカードを持つ必要があります。A2Aサーバーでは、エージェントカードは起動時に動的に生成され、静的にホストされます。

ADK Java の Web サービスでは、エージェントカードは通常、ベース URL に対する標準の [`.well-known/agent-card.json`](http://localhost:9090/.well-known/agent-card.json) エンドポイント形式で動的にアクセスできます。

### 4. メイン（利用側）エージェントを実行する { #run-the-main-consuming-agent }

別のターミナルで、クライアントエージェントを実行できます。

```bash
./mvnw -f contrib/samples/a2a_basic/pom.xml exec:java -Dexec.args="http://localhost:9090"
```

#### 動作の仕組み

メインエージェントは、必要な A2A JSON-RPC トランスポートラッパーにアクセスして、リモートエージェント（この例では `prime_agent`）を利用します。下に示すように、対象ホストから `AgentCard` を取得し、公式 A2A `Client` 内にローカルで登録します。

```java title="A2aConsumerSnippet.java"
--8<-- "examples/java/snippets/src/main/java/a2a/A2aConsumerSnippet.java:new-prime-agent"
```

その後、リモートエージェントのインスタンスをエージェントビルダーに自然に渡すことができ、他の標準的な ADK サブエージェントと同様に扱えます。ワイヤ上の変換ロジックは ADK が内部で担います。

```java title="A2aConsumerSnippet.java"
--8<-- "examples/java/snippets/src/main/java/a2a/A2aConsumerSnippet.java:new-root-agent"
```

## 次のステップ

これで、A2Aサーバー経由でリモートエージェントを使うエージェントを作成できました。次は、自分の Java エージェントを公開する方法を学びましょう。

- [**A2A クイックスタート（公開） for Java**](./quickstart-exposing-java.md): 既存のエージェントを公開して、他のエージェントが A2A Protocol 経由で利用できるようにする方法を学びます。
