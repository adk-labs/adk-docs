# クイックスタート: A2A を介したリモート エージェントの使用

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-kotlin">Kotlin</span><span class="lst-preview">実験的機能</span>
</div>

このクイックスタートでは、すべての開発者にとって最も一般的な出発点である **「リモート エージェントがある場合、自作の ADK エージェントから A2A 経由でそれを利用するにはどうすればよいか？」** について説明します。これは、さまざまなエージェントが連携して相互作用する必要がある複雑なマルチエージェント システムを構築する上で重要です。

## 概要

このサンプルでは、Kotlin 向け Agent Development Kit (ADK) における **Agent2Agent (A2A)** アーキテクチャを実演し、ローカル エージェントがタスクの一部を他の場所で実行されているエージェントに委譲する方法を示します。

```text
┌─────────────────┐         ┌────────────────────────┐
│   Root Agent    │────────▶│   Remote Prime Agent   │
│   (Local)       │◀────────│   (localhost:8001)     │
└─────────────────┘         └────────────────────────┘
```

- **Root Agent** (`root_agent`): サブエージェントに委譲するローカル オーケストレーター
- **Prime Agent** (`prime_agent`): 数値が素数かどうかを判定するリモート A2A エージェント（別の A2A サーバーで実行）

## A2A 依存関係の追加

A2A サポートは別個のアーティファクトとして提供されます。`A2AAgent` の `httpClient` パラメータはデフォルトで `JdkA2AHttpClient()` に設定されるため、コンパイル クラスパスに A2A SDK クライアントも含める必要があります。

```kotlin title="build.gradle.kts"
implementation("com.google.adk:google-adk-kotlin-a2a:0.9.0")
implementation("org.a2aproject.sdk:a2a-java-sdk-client:1.0.0.Final")
```

## リモート エージェント サーバーの起動

リモート エージェントを使用するには、まずそれが実行されている必要があります。adk-kotlin はまだ A2A 経由でエージェントを公開できないため、サーバーは別の場所から提供する必要があります（A2A はワイヤ プロトコルであるため、どの言語でも構いません）。

adk-python の `a2a_basic` サンプルは、このページで委譲する素数判定エージェントを提供します。adk-python チェックアウト ディレクトリから次を実行します。

```bash
adk api_server --a2a --port 8001 contributing/samples/a2a/a2a_basic/remote_a2a
```

A2A プロトコルでは、各エージェントが何を行うかを記述した **エージェント カード (Agent card)** を、そのエージェント自身のプレフィックス配下の既知 (well-known) のパスで公開する必要があります。

```text
http://localhost:8001/a2a/check_prime_agent/.well-known/agent-card.json
```

次に進む前に、カードにアクセスできることを確認してください。

```bash
curl http://localhost:8001/a2a/check_prime_agent/.well-known/agent-card.json
```

!!! note "このクライアントが通信できるサーバー"

    Kotlin クライアントは **A2A 1.0** カードを読み取るため、カードには各エントリに `protocolBinding` を持つ `supportedInterfaces` 配列が含まれている必要があります。A2A 0.3 向けに作成されたカードは代わりにトップレベルの `url` と `preferredTransport` を宣言しており、`A2AAgent` はこれを `AgentCardResolutionError: Failed to parse agent card` エラーで拒否します。

    サンプルのチェックインされた `agent.json` は 0.3 スタイルのカードですが、adk-python はそのファイルをそのまま配信しません。起動時にカードを解析し、a2a-sdk 1.x の下でその解析により `url` と `preferredTransport` が `supportedInterfaces` に昇格されます。adk-python には `a2a-sdk>=0.3.4,<2` が必要なため、新規インストールでは 1.x に解決され、ワイヤ上のカードは A2A 1.0 になります。

    adk-java の `a2a_server` サンプルは 0.3.x A2A SDK に固定されており 0.3 カードを配信するため、このページのサーバーとしては機能しません。

??? note "代わりに独自のカードを配信する"

    A2A 1.0 カードを公開する任意のサーバーを使用できます。クライアントが受け入れる最小限のカードは `<your-base-url>/.well-known/agent-card.json` から配信されます。

    ```json title=".well-known/agent-card.json"
    {
      "name": "check_prime_agent",
      "description": "Checks whether numbers are prime.",
      "version": "1.0.0",
      "url": "http://localhost:9090",
      "preferredTransport": "JSONRPC",
      "capabilities": { "streaming": true },
      "defaultInputModes": ["text/plain"],
      "defaultOutputModes": ["application/json"],
      "skills": [],
      "supportedInterfaces": [
        { "protocolBinding": "JSONRPC", "url": "http://localhost:9090" }
      ]
    }
    ```

    そのベース URL（`http://localhost:9090`）を以下の `agentCardUrl` として渡します。

## リモート エージェントへの接続

`A2AAgent` はそのカードを取得し、リモート エージェントの説明やリモートがストリーミングをサポートしているかどうかを読み取ります。渡す `name` は、カードが通知する名前とは無関係に、自身のエージェント ツリー内におけるこのエージェントの識別子です。サスペンド関数であるため、コルーチンから呼び出してください。

```kotlin title="A2AConsumer.kt"
--8<-- "examples/kotlin/snippets/a2a/A2AConsumer.kt:remote_agent"
```

すでに `AgentCard` を保持している場合（たとえば自身で解決したカードや設定にチェックインされた静的カード）、それを直接受け取る非サスペンドのオーバーロード `A2AAgent(name = ..., agentCard = ...)` を使用できます。

## サブエージェントとしての使用

返されたエージェントは `BaseAgent` であるため、ローカル エージェントとまったく同様に `subAgents` に配置されます。ADK はネットワーク経由の A2A プロトコルを処理します。

```kotlin title="A2AConsumer.kt"
--8<-- "examples/kotlin/snippets/a2a/A2AConsumer.kt:root_agent"
```

## 次のステップ

Kotlin エージェントを A2A 経由で公開する機能はまだサポートされていません。adk-kotlin は現在コンシューマー側のみを提供しています。エージェントを公開するには、他の言語向けのクイックスタートを参照してください。

- [**Python 向け A2A クイックスタート（エージェントの公開）**](./quickstart-exposing.md)
- [**Java 向け A2A クイックスタート（エージェントの公開）**](./quickstart-exposing-java.md)
