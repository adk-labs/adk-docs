# コマンドラインを使う

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

ADK はエージェントをテストするための対話型ターミナルインターフェースを提供します。これは
クイックテスト、スクリプト化されたやり取り、CI/CD パイプラインに有用です。

![ADK Run](../assets/adk-run.png)

## エージェントを実行する

ADK コマンドラインインターフェースでエージェントを実行するには、次のコマンドを使用します:

=== "Python"

    ```shell
    adk run my_agent
    ```

=== "TypeScript"

    ```shell
    npx @google/adk-devtools run agent.ts
    ```

=== "Go"

    ```shell
    go run agent.go
    ```

=== "Java"

    `AgentCliRunner` クラスを作成し ( [Java Quickstart](../get-started/java.md) 参照 )、次を実行します:

    ```shell
    mvn compile exec:java -Dexec.mainClass="com.example.agent.AgentCliRunner"
    ```

これにより、クエリを入力し、ターミナル上でエージェントの応答を直接確認できる
対話セッションが開始されます:

```shell
Running agent my_agent, type exit to exit.
[user]: What's the weather in New York?
[my_agent]: The weather in New York is sunny with a temperature of 25°C.
[user]: exit
```

## セッションオプション

`adk run` コマンドには、セッションの保存・再開・リプレイ用オプションがあります。

### セッションを保存する

終了時にセッションを保存するには:

```shell
adk run --save_session path/to/my_agent
```

セッション ID の入力を求められ、セッションは
`path/to/my_agent/<session_id>.session.json` に保存されます。

セッション ID を事前に指定することもできます:

```shell
adk run --save_session --session_id my_session path/to/my_agent
```

### セッションを再開する

以前保存したセッションを続行するには:

```shell
adk run --resume path/to/my_agent/my_session.session.json path/to/my_agent
```

これにより、以前のセッション状態とイベント履歴が読み込まれて表示され、
会話を続けられます。

### セッションをリプレイする

対話入力なしでセッションファイルをリプレイするには:

```shell
adk run --replay path/to/input.json path/to/my_agent
```

入力ファイルには初期状態とクエリを含める必要があります:

```json
{
  "state": {"key": "value"},
  "queries": ["What is 2 + 2?", "What is the capital of France?"]
}
```

## ストレージオプション

| Option | Description | Default |
|--------|-------------|---------|
| `--session_service_uri` | カスタムセッションストレージ URI | `.adk/session.db` 配下の SQLite |
| `--artifact_service_uri` | カスタムアーティファクトストレージ URI | ローカル `.adk/artifacts` |

### ストレージオプションの例

```shell
adk run --session_service_uri "sqlite:///my_sessions.db" path/to/my_agent
```

## すべてのオプション

| Option | Description |
|--------|-------------|
| `--save_session` | 終了時にセッションを JSON ファイルへ保存 |
| `--session_id` | 保存時に使用するセッション ID |
| `--resume` | 再開する保存済みセッションファイルのパス |
| `--replay` | 非対話リプレイ用入力ファイルのパス |
| `--session_service_uri` | カスタムセッションストレージ URI |
| `--artifact_service_uri` | カスタムアーティファクトストレージ URI |
