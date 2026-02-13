# Web インターフェースを使う

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

ADK Web インターフェースを使うと、ブラウザで直接エージェントをテストできます。この
ツールは、エージェントを対話的に開発・デバッグするためのシンプルな方法を提供します。

![ADK Web Interface](../assets/adk-web-dev-ui-chat.png)

!!! warning "注意: ADK Web は開発用途のみ"

    ADK Web は ***本番デプロイでの利用を想定していません***。
    ADK Web は開発およびデバッグ用途でのみ利用してください。

## Web インターフェースを起動する

ADK Web インターフェースでエージェントを実行するには、次のコマンドを使用します:

=== "Python"

    ```shell
    adk web
    ```

=== "TypeScript"

    ```shell
    npx adk web
    ```

=== "Go"

    ```shell
    go run agent.go web api webui
    ```

=== "Java"

    ポート番号を必ず更新してください。
    === "Maven"
        Maven では、ADK Web サーバーをコンパイルして実行します:
        ```console
        mvn compile exec:java \
         -Dexec.args="--adk.agents.source-dir=src/main/java/agents --server.port=8080"
        ```
    === "Gradle"
        Gradle では、`build.gradle` または `build.gradle.kts` の plugins セクションに次の Java プラグインが必要です:

        ```groovy
        plugins {
            id('java')
            // other plugins
        }
        ```
        その後、ビルドファイルのトップレベルに新しいタスクを作成します:

        ```groovy
        tasks.register('runADKWebServer', JavaExec) {
            dependsOn classes
            classpath = sourceSets.main.runtimeClasspath
            mainClass = 'com.google.adk.web.AdkWebServer'
            args '--adk.agents.source-dir=src/main/java/agents', '--server.port=8080'
        }
        ```

        最後に、コマンドラインで次を実行します:
        ```console
        gradle runADKWebServer
        ```


    Java では、Web インターフェースと API サーバーが同梱されています。

サーバーはデフォルトで `http://localhost:8000` で起動します:

```shell
+-----------------------------------------------------------------------------+
| ADK Web Server started                                                      |
|                                                                             |
| For local testing, access at http://localhost:8000.                         |
+-----------------------------------------------------------------------------+
```

## 機能

ADK Web インターフェースの主な機能:

- **チャットインターフェース**: エージェントへメッセージを送信し、リアルタイムで応答を確認
- **セッション管理**: セッションの作成と切り替え
- **状態確認**: 開発中にセッション状態を表示・変更
- **イベント履歴**: エージェント実行中に生成されたすべてのイベントを確認

## 主なオプション

| Option | Description | Default |
|--------|-------------|---------|
| `--port` | サーバー起動ポート | `8000` |
| `--host` | ホストバインドアドレス | `127.0.0.1` |
| `--session_service_uri` | カスタムセッションストレージ URI | In-memory |
| `--artifact_service_uri` | カスタムアーティファクトストレージ URI | ローカル `.adk/artifacts` |
| `--reload/--no-reload` | コード変更時の自動リロード有効化 | `true` |

### オプション付きの例

```shell
adk web --port 3000 --session_service_uri "sqlite:///sessions.db"
```
