---
catalog_title: Restate
catalog_description: 耐久セッションと人間承認を備えた高耐障害エージェント実行/オーケストレーション
catalog_icon: /adk-docs/integrations/assets/restate.svg
catalog_tags: []
---

# ADK 向け Restate プラグイン

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Restate](https://restate.dev) は ADK エージェントを本質的に高耐障害で堅牢な
システムへ変える durable execution エンジンです。
永続セッション、人間承認のための pause/resume、
高耐障害マルチエージェントオーケストレーション、安全なバージョニング、
すべての実行に対する可観測性と制御を提供します。
すべての LLM 呼び出しとツール実行はジャーナル化されるため、
障害時でも中断地点から正確に復旧できます。

## ユースケース

Restate プラグインはエージェントに次を提供します:

- **Durable execution**: 進捗を失いません。エージェントがクラッシュしても
  自動リトライと復旧で中断地点から再開します。
- **Human-in-the-loop pause/resume**: 人間承認まで
  数日〜数週間実行を停止し、同じ地点から再開できます。
- **Durable state**: 内蔵セッション管理により、エージェントメモリと会話履歴が
  再起動をまたいで保持されます。
- **可観測性とタスク制御**: エージェントの実行内容を正確に把握し、
  任意のタイミングで停止/一時停止/再開できます。
- **高耐障害マルチエージェントオーケストレーション**: 複数エージェント間ワークフローを
  並列実行で堅牢に運用できます。
- **安全なバージョニング**: immutable deployment により、
  進行中実行を壊さず新バージョンをデプロイできます。

## 前提条件

- Python 3.12+
- [Gemini API key](https://aistudio.google.com/app/api-keys)

下記例を動かすには追加で次が必要です:

- [uv](https://docs.astral.sh/uv/) (Python パッケージマネージャ)
- [Docker](https://docs.docker.com/get-docker/) (または
  Restate サーバー用 [Brew/npm/binary](https://docs.restate.dev/develop/local_dev#running-restate-server--cli-locally))

## インストール

Restate SDK for Python をインストール:

```bash
pip install "restate-sdk[serde]"
```

## エージェントで使う

次の手順で durable agent を実行し、Restate UI で実行ジャーナルを確認します:

1. **[restate-google-adk-example repository](https://github.com/restatedev/restate-google-adk-example) を clone し、サンプルへ移動**

    ```bash
    git clone https://github.com/restatedev/restate-google-adk-example.git
    cd restate-google-adk-example/examples/hello-world
    ```

2. **Gemini API キーを export**

    ```bash
    export GOOGLE_API_KEY=your-api-key
    ```

3. **weather agent を起動**

    ```bash
    uv run .
    ```

4. **別ターミナルで Restate を起動**

    ```bash
    docker run --name restate --rm -p 8080:8080 -p 9070:9070 -d \
      --add-host host.docker.internal:host-gateway \
      docker.restate.dev/restatedev/restate:latest
    ```

    他のインストール方法: [Brew, npm, binary
    downloads](https://docs.restate.dev/develop/local_dev#running-restate-server--cli-locally)

5. **エージェントを登録**

    `localhost:9070` の Restate UI を開き、エージェント deployment を登録します
    (例: `http://host.docker.internal:9080`):

    ![Restate registration](./assets/restate-registration.png)

    !!! tip "安全なバージョニング"

        Restate は各 deployment を immutable snapshot として登録します。
        新バージョンデプロイ時、進行中実行は元 deployment で完了し、
        新規リクエストは最新へルーティングされます。
        詳細は
        [version-aware routing](https://docs.restate.dev/services/versioning)
        を参照してください。

6. **エージェントへリクエスト送信**

    Restate UI で **WeatherAgent** を選び、**Playground** で
    リクエストを送信します:

    ![Send request in the UI](./assets/restate-request.png)

    !!! tip "Durable セッションとリトライ"

        このリクエストは Restate 経由で、エージェント転送前に永続化されます。
        各セッション (ここでは `session-1`) は分離・状態保持・durable です。
        実行中にエージェントがクラッシュしても、Restate が自動リトライし、
        最後にジャーナル化されたステップから進捗を失わず再開します。

7. **実行ジャーナル確認**

    **Invocations** タブを開き、対象 invocation をクリックして
    実行ジャーナルを確認します:

    ![Restate journal in the UI](./assets/restate-journal.png)

    !!! tip "エージェント実行の完全制御"

        すべての LLM 呼び出しとツール実行はジャーナルに記録されます。
        UI から一時停止、再開、中間ステップから再実行、停止が可能です。
        **State** タブで現在セッションデータを確認できます。

## 機能

Restate プラグインは ADK エージェントに次の機能を提供します:

| Capability | Description |
| --- | --- |
| Durable tool execution | `restate_object_context().run_typed()` でツールロジックを包み、自動リトライ/復旧 |
| Human-in-the-loop | 外部シグナル (例: 人間承認) まで `restate_object_context().awakeable()` で実行停止 |
| Persistent sessions | `RestateSessionService()` がエージェントメモリ/会話状態を durable 保存 |
| Durable LLM calls | `RestatePlugin()` が LLM 呼び出しをジャーナル化し自動リトライ |
| Multi-agent communication | `restate_object_context().service_call()` による durable cross-agent HTTP 呼び出し |
| Parallel execution | `restate.gather()` でツール/エージェントを並列実行し決定論的に復旧 |

## 追加リソース

- [Restate ADK example repository](https://github.com/restatedev/restate-google-adk-example) - 人間承認付き claims processing など実行可能サンプル
- [Restate ADK tutorial](https://docs.restate.dev/tour/google-adk) - Restate と ADK によるエージェント開発チュートリアル
- [Restate AI documentation](https://docs.restate.dev/ai) - durable AI agent パターンの完全リファレンス
- [Restate SDK on PyPI](https://pypi.org/project/restate-sdk/) - Python パッケージ
