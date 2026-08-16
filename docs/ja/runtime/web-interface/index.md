# Web インターフェースの使用

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

ADK Web インターフェースを使用すると、ブラウザからエージェントを直接テストできます。このツールは、エージェントを対話型で開発およびデバッグするための簡単な方法を提供します。

![ADK Web Interface](../../assets/adk-web-dev-ui-chat.png)

!!! warning "注意: ADK Web は開発専用です"

    ADK Web は***本番環境へのデプロイでの使用を意図して設計されていません***。
    ADK Web は開発およびデバッグ目的でのみ使用してください。

## Web インターフェースの起動

次のコマンドを使用して、ADK Web インターフェースでエージェントを実行します。

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
        Maven を使用して ADK Web サーバーをコンパイルして実行します。
        ```console
        mvn compile exec:java \
         -Dexec.args="--adk.agents.source-dir=src/main/java/agents --server.port=8080"
        ```
    === "Gradle"
        Gradle を使用する場合、`build.gradle` または `build.gradle.kts` ビルド ファイルの plugins セクションに次の Java プラグインが必要です。

        ```groovy
        plugins {
            id('java')
            // other plugins
        }
        ```
        次に、ビルド ファイルのトップレベル領域に新しいタスクを作成します。

        ```groovy
        tasks.register('runADKWebServer', JavaExec) {
            dependsOn classes
            classpath = sourceSets.main.runtimeClasspath
            mainClass = 'com.google.adk.web.AdkWebServer'
            args '--adk.agents.source-dir=src/main/java/agents', '--server.port=8080'
        }
        ```

        最後に、コマンドラインから次のコマンドを実行します。
        ```console
        gradle runADKWebServer
        ```

    Java では、Web インターフェースと API サーバーが一緒にバンドルされています。

=== "Python"

    ```shell
    +-----------------------------------------------------------------------------+
    | ADK Web Server started                                                      |
    |                                                                             |
    | For local testing, access at http://localhost:8000.                         |
    +-----------------------------------------------------------------------------+
    ```

=== "TypeScript"

    ```shell
    +-----------------------------------------------------------------------------+
    | ADK Web Server started                                                      |
    |                                                                             |
    | For local testing, access at http://localhost:8000.                         |
    +-----------------------------------------------------------------------------+
    ```

=== "Go"

    ```shell
    2025/01/01 00:00:00 Starting the web server: &{port:8080 ...}
    2025/01/01 00:00:00 Web servers starts on http://localhost:8080
    2025/01/01 00:00:00        webui:  you can access API using http://localhost:8080/ui/
    2025/01/01 00:00:00        api:  you can access API using http://localhost:8080/api
    ```

=== "Java"

    ```shell
    +-----------------------------------------------------------------------------+
    | ADK Web Server started                                                      |
    |                                                                             |
    | For local testing, access at http://localhost:8000.                         |
    +-----------------------------------------------------------------------------+
    ```

## 機能

ADK Web インターフェースの主な機能:

- **チャット インターフェース**: エージェントにメッセージを送信し、リアルタイムの応答を確認
- **セッション管理**: セッションの作成と切り替え
- **状態の検査**: 開発中にセッション状態を検査および変更
- **イベント履歴**: エージェントの実行中に生成されたすべてのイベントを検査

## 共通オプション

=== "Python"

    `adk web` コマンドの一般的なオプションです。使用可能なすべてのオプションを確認するには、`adk web --help` を実行してください。

    | オプション | 説明 | デフォルト |
    |--------|-------------|---------|
    | `--port` | サーバーを実行するポート | `8000` |
    | `--host` | ホスト バインディング アドレス | `127.0.0.1` |
    | `--session_service_uri` | カスタム セッション ストレージ URI | `<agents_dir>/<agent>/.adk/session.db` のエージェントごとの SQLite |
    | `--artifact_service_uri` | カスタム アーティファクト ストレージ URI | `<agents_dir>/<agent>/.adk/artifacts` のエージェントごとのディレクトリ |
    | `--reload/--no-reload` | コード変更時の自動リロードを有効化 | `true` |

    ローカルの `.adk` フォルダの代わりにインメモリのセッションおよびアーティファクト サービスにフォールバックするには、`--no_use_local_storage` を渡します。

    例:

    ```shell
    adk web --port 3000 --session_service_uri "sqlite:///sessions.db"
    ```

=== "TypeScript"

    `adk web` コマンドの一般的なオプションです。使用可能なすべてのオプションを確認するには、`adk web --help` を実行してください。

    | オプション | 説明 | デフォルト |
    |--------|-------------|---------|
    | `--port` | サーバーを実行するポート | `8000` |
    | `--host` | ホスト バインディング アドレス | `127.0.0.1` |
    | `--session_service_uri` | カスタム セッション ストレージ URI | インメモリ |
    | `--artifact_service_uri` | カスタム アーティファクト ストレージ URI | ローカル `.adk/artifacts` |
    | `--reload/--no-reload` | コード変更時の自動リロードを有効化 | `true` |

    例:

    ```shell
    adk web --port 3000 --session_service_uri "sqlite:///sessions.db"
    ```

=== "Go"

    !!! note "Go フラグは Python/TypeScript と異なります"

        Go Web ランチャーは、Python または TypeScript の `adk web` と同じフラグを使用しません。`--host`、`--session_service_uri`、`--artifact_service_uri`、`--reload` などのオプションは使用できません。セッションおよびアーティファクト サービスは、コマンドライン フラグではなく、`launcher.Config` を構築するときに Go コードで構成されます。

    フラグは `web`、`api`、`webui` サブコマンドに分割されています。関連するサブコマンド キーワードの後にフラグを渡します。

    **`web` サブコマンド フラグ** (`web` の直後に渡す):

    | フラグ | 説明 | デフォルト |
    |------|-------------|---------|
    | `-port` | HTTP サーバーのポート | `8080` |
    | `-write-timeout` | HTTP 応答書き込みタイムアウト | `15s` |
    | `-read-timeout` | HTTP リクエスト読み取りタイムアウト | `15s` |
    | `-idle-timeout` | キープアライブ アイドル接続タイムアウト | `60s` |
    | `-shutdown-timeout` | グレースフル シャットダウン待機時間 | `15s` |
    | `-otel_to_cloud` | OpenTelemetry データを GCP にエクスポート | `false` |

    **`api` サブコマンド フラグ** (`api` の後に渡す):

    | フラグ | 説明 | デフォルト |
    |------|-------------|---------|
    | `-webui_address` | CORS 用に許可された WebUI オリジン | `localhost:8080` |
    | `-path_prefix` | REST API の URL パス プレフィックス | `/api` |
    | `-sse-write-timeout` | SSE (ストリーミング) 応答のタイムアウト | `120s` |
    | `-trace_capacity` | 保持する最大インメモリ トレース数 | `10000` |

    **`webui` サブコマンド フラグ** (`webui` の後に渡す):

    | フラグ | 説明 | デフォルト |
    |------|-------------|---------|
    | `-api_server_address` | ブラウザから見た REST API URL | `http://localhost:8080/api` |

    たとえば、カスタム API プレフィックスを使用してポート 9090 で実行するには:

    ```shell
    go run agent.go web -port 9090 api -path_prefix /myapi webui -api_server_address http://localhost:9090/myapi
    ```

## 使用状況テレメトリ (Usage telemetry)

ADK Web UI は、機能の採用状況を理解し、使いやすさの問題を発見し、全体的な開発者エクスペリエンスを向上させるために、匿名の使用状況テレメトリ データを収集します。データ収集は、明示的に有効にすることを選択するまで、デフォルトでオフ (OFF) になっています。

Web UI の画面右上にあるユーザー アイコン (User Settings) に移動することで、いつでも使用状況テレメトリを有効または無効にできます。この設定は、ローカル マシンの `~/.adk/config.json` に保存されている単一の統一された設定を更新します。必要に応じて、このファイルを直接編集して `telemetry` 属性を `false` に設定することにより、データ収集を手動で非アクティブ化することもできます。

```json
{
  "telemetry": false
}
```

**収集されるデータ**

有効にすると、Web UI テレメトリは次の標準ページ イベントと機能の操作をキャプチャします。

- **標準ナビゲーション**: ページ ビュー、セッションの開始、アクティブなセッションの継続時間。
- **環境**: ADK バージョンとランタイム言語。
- **機能の使用**: ビルダー モード機能の使用、エージェント チャットの使用、実行トレースまたはイベント ログ ビューアの切り替え、評価セットの作成、エージェント構造グラフ ビューのクリック。

**収集されないデータ**

Web UI は、機密データ、プライベート データ、または個人データを収集しません。具体的には以下が含まれます。

- エージェントのプロンプト、システム指示、または LLM 応答のコンテンツ。
- ユーザー認証情報、ユーザー名、API キー、OAuth トークン、またはシークレット。
- Google Cloud プロジェクト ID または Cloud アカウントの詳細。
- 個人を特定できる情報 (PII)。
