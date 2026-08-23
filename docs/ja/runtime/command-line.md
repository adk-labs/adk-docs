# コマンドラインの使用

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

ADK は、エージェントをテストするための対話型ターミナル インターフェースを提供します。これは、簡単なテスト、スクリプト化された対話、および CI/CD パイプラインに役立ちます。

![ADK Run](../assets/adk-run.png)

## エージェントの実行

次のコマンドを使用して、ADK コマンドライン インターフェースでエージェントを実行します。

=== "Python"

    ```shell
    adk run my_agent
    ```

=== "TypeScript"

    ```shell
    npx @google/adk-devtools run agent.ts
    ```

=== "Go"

    Go では、コマンドライン インターフェースはスタンドアロンの `adk` ツールではありません。代わりに、エージェントの `main.go` にランチャーを直接埋め込みます。`full.NewLauncher()` ヘルパーは、コンソール、Web サーバー、およびその他のモードを単一のバイナリにバンドルし、サブコマンド キーワードが指定されていない場合は**コンソールがデフォルト**になります。

    ```go title="main.go"
    import (
        "google.golang.org/adk/v2/cmd/launcher"
        "google.golang.org/adk/v2/cmd/launcher/full"
    )

    func main() {
        // ... エージェントと構成を構築 ...
        l := full.NewLauncher()
        if err := l.Execute(ctx, config, os.Args[1:]); err != nil {
            log.Fatalf("Run failed: %v\n\n%s", err, l.CommandLineSyntax())
        }
    }
    ```

    次のいずれかのコマンドを使用してコンソール モードでエージェントを実行します。

    ```shell
    go run agent.go           # コンソールがデフォルトのサブランチャーです
    go run agent.go console   # または明示的に console サブコマンドを指定します
    ```

=== "Java"

    `AgentCliRunner` クラスを作成し ([Java クイックスタート](../get-started/java.md) を参照)、次を実行します。

    ```shell
    mvn compile exec:java -Dexec.mainClass="com.example.agent.AgentCliRunner"
    ```

これにより、クエリを入力してターミナルでエージェントの応答を直接確認できる対話型セッションが開始されます。

=== "Python"

    ```shell
    Running agent my_agent, type exit to exit.
    [user]: What's the weather in New York?
    [my_agent]: The weather in New York is sunny with a temperature of 25°C.
    [user]: exit
    ```

=== "TypeScript"

    ```shell
    Running agent my_agent, type exit to exit.
    [user]: What's the weather in New York?
    [my_agent]: The weather in New York is sunny with a temperature of 25°C.
    [user]: exit
    ```

=== "Go"

    ```shell
    User -> What's the weather in New York?

    Agent -> The weather in New York is sunny with a temperature of 25°C.

    User ->
    ```

    終了するには、**Ctrl+C** を押すか、EOF (**Ctrl+D**) を送信します。

=== "Java"

    ```shell
    Running agent my_agent, type exit to exit.
    [user]: What's the weather in New York?
    [my_agent]: The weather in New York is sunny with a temperature of 25°C.
    [user]: exit
    ```

## セッション オプション

!!! note "Python のみ"

    `--save_session`、`--resume`、`--replay`、`--session_id` オプションは、Python ADK CLI でのみ使用できます。Go コンソール ランチャーは、コマンドライン フラグによるセッションの保存/再開/再生をサポートしていません。Go では、`launcher.Config` に永続的な `session.Service` 実装 (例: `session/database`) を提供することによって、コード内でセッションの永続性を構成します。

`adk run` コマンドには、セッションの保存、再開、再生のためのオプションが含まれています。

### セッションの保存

終了時にセッションを保存するには:

```shell
adk run --save_session path/to/my_agent
```

セッション ID の入力を求められ、セッションは `path/to/my_agent/<session_id>.session.json` に保存されます。

セッション ID を事前に指定することもできます。

```shell
adk run --save_session --session_id my_session path/to/my_agent
```

### セッションの再開

以前に保存したセッションを続行するには:

```shell
adk run --resume path/to/my_agent/my_session.session.json path/to/my_agent
```

これにより、以前のセッション状態とイベント履歴が読み込まれて表示され、会話を続行できるようになります。

### セッションの再生

対話型の入力なしでセッション ファイルを再生するには:

```shell
adk run --replay path/to/input.json path/to/my_agent
```

入力ファイルには、初期状態とクエリが含まれている必要があります。

```json
{
  "state": {"key": "value"},
  "queries": ["What is 2 + 2?", "What is the capital of France?"]
}
```

## ストレージ オプション

!!! note "Python のみ"

    `--session_service_uri` および `--artifact_service_uri` コマンドライン フラグは、Python ADK CLI でのみ使用できます。Go では、`launcher.Config` を構築するときにコード内でセッションおよびアーティファクト サービスを構成します (例: データベース対応の永続セッション ストアの場合は `session/database`、Cloud Storage 対応のアーティファクトの場合は `artifact/gcsartifact`)。

| オプション | 説明 | デフォルト |
|--------|-------------|---------|
| `--session_service_uri` | カスタム セッション ストレージ URI | `<agents_dir>/<agent>/.adk/session.db` のエージェントごとの SQLite |
| `--artifact_service_uri` | カスタム アーティファクト ストレージ URI | `<agents_dir>/<agent>/.adk/artifacts` のエージェントごとのディレクトリ |
| `--memory_service_uri` | カスタム メモリ サービス URI | インメモリ |

### ストレージ オプションの例

```shell
adk run --session_service_uri "sqlite:///my_sessions.db" path/to/my_agent
```

## すべてのオプション

=== "Python"

    対話型セッションを開始する代わりに単一のメッセージを送信して終了するには、クエリを引数として渡します。

    ```shell
    adk run path/to/my_agent "hello"
    ```

    | オプション | 説明 |
    |--------|-------------|
    | `--save_session` | 終了時にセッションを JSON ファイルに保存 |
    | `--session_id` | 保存時に使用するセッション ID |
    | `--resume` | 再開する保存済みセッション ファイルのパス |
    | `--replay` | 非対話型再生用の入力ファイルのパス |
    | `--session_service_uri` | カスタム セッション ストレージ URI |
    | `--artifact_service_uri` | カスタム アーティファクト ストレージ URI |
    | `--memory_service_uri` | カスタム メモリ サービス URI |
    | `--use_local_storage/--no_use_local_storage` | サービス URI が設定されていない場合にローカルの `.adk` フォルダーを使用するかどうか |
    | `--state` | 実行の初期状態 (JSON 文字列) |
    | `--timeout` | 単一のターンまたはクエリのタイムアウト (例: `30s`、`5m`) |
    | `--in_memory` | セッション データを永続化しない |
    | `--jsonl` | 人間が読めるテキストの代わりに構造化された JSONL を出力 |
    | `--default_llm_model` | エージェントが設定していない場合に使用されるデフォルト モデル |

=== "Go"

    !!! note "Go フラグは Python と異なります"

        Go コンソール ランチャーは、`--save_session`、`--resume`、`--replay`、`--session_id`、`--session_service_uri`、`--artifact_service_uri` をサポートしていません。これらは Python CLI の機能です。セッションおよびアーティファクト サービスは、`launcher.Config` を介して Go コードで構成されます。

    フラグは `console` キーワードの後に渡されます (または `console` がデフォルトの場合は直接渡されます)。

    | フラグ | 説明 | デフォルト |
    |------|-------------|---------|
    | `-streaming_mode` | エージェント応答のストリーミング モード (`none`\|`sse`) | 自動検出 (TTY → `sse`、パイプ → `none`) |
    | `-shutdown-timeout` | グレースフル シャットダウン待機時間 | `2s` |
    | `-otel_to_cloud` | OpenTelemetry データを GCP にエクスポート | `false` |

    たとえば、非ストリーミング出力を強制するには:

    ```shell
    go run agent.go console -streaming_mode none
    ```

    または、SSE ストリーミング (トークン単位の出力) を強制するには:

    ```shell
    go run agent.go -streaming_mode sse
    ```

## 使用状況テレメトリ (Usage telemetry)

ADK CLI は、機能の採用状況を理解し、開発の優先順位を導き、ツールのパフォーマンスを向上させるために、匿名の使用状況テレメトリを収集します。データ収集は、明示的に有効にすることを選択するまで、デフォルトでオフ (OFF) になっています。

テレメトリの設定は、ローカル マシンの `~/.adk/config.json` に保存されます。ターミナルを通じていつでもテレメトリ データの収集を管理できます。

- **有効化**: `adk telemetry enable`
- **無効化**: `adk telemetry disable`
- **ステータス確認**: `adk telemetry status`

`~/.adk/config.json` を開いて `telemetry` 属性を `false` に設定することにより、いつでも手動でテレメトリ データの収集を無効にすることもできます。

```json
{
  "telemetry": false
}
```

**収集されるデータ**

- **環境プロパティ**: オペレーティング システム情報、ランタイム言語とバージョン、インストールされている ADK CLI バージョン。
- **コマンド実行イベント**: 一般的なコマンドとサブコマンドの名前、渡されたフラグ、実行時間、終了コード、エラーが発生した場合の例外タイプ。また、シーケンス番号と、コマンド実行後に破棄されるエフェメラル セッション ID をログに記録します。

**収集されないデータ**

CLI は、機密データ、プライベート データ、または個人データを収集しません。具体的には以下が含まれます。

- エージェント名、プロンプト文字列、ファイル パスなど、コマンドまたはフラグに渡された引数またはパラメータ値。
- ユーザー認証情報、ユーザー名、API キー、OAuth トークン、またはシークレット。
- Google Cloud プロジェクト ID または Cloud アカウントの詳細。
- ソース コード ファイル、ファイル コンテンツ、またはディレクトリ パス。
- 個人を特定できる情報 (PII)。
