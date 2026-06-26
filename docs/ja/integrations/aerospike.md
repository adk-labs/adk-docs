---
catalog_title: Aerospike
catalog_description: 単一の Aerospike クラスタに ADK エージェントのセッション, メモリ, アーティファクトを格納します
catalog_icon: /integrations/assets/aerospike.png
catalog_tags: ["data"]
---

# ADK向けのAerospike連携

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span>
</div>

[`adk-aerospike`](https://github.com/aerospike-community/adk-aerospike) 連携は、ADK エージェントを分散リアルタイムキー値データベースである [Aerospike](https://aerospike.com/) に接続します。アプリケーションプロセス内でネイティブの Aerospike クライアントを使用し、単一のクラスタ上で3つすべての ADK Python ストレージインターフェースを実装します。`aerospike://` URI スキーマを一度登録すれば、`adk` CLI はセッション、アーティファクト、メモリに Aerospike を使用できるようになります。

この連携を利用するには、いくつかの方法があります:

| アプローチ | 説明 |
| -------- | ----------- |
| **セッションサービス** | `AerospikeSessionService`: スコープ付き状態(`app:`, `user:`, session)、チャンク化ストレージ付きイベント履歴、アトミックな `append_event`。 |
| **メモリサービス** | `AerospikeMemoryService`: トークンごとのポスティングリスト(posting-list)キーによる語彙적単語重複検索。 `InMemoryMemoryService` と同じセマンティクス。 |
| **アーティファクトサービス** | `AerospikeArtifactService`: セッションまたは `user:` ネームスペースごとのバージョン管理された Blob の保存。 |
| **フルスタック** | 3つすべてのサービスを1つの `Runner` に組み込むか、対応する `aerospike://` URI を `adk web` / `adk run` に渡します。 |

## 主なユースケース

- **本番エージェントの永続化 (Production agent persistence)**: 別個のメモリサービスを運用することなく、会話状態、ツール出力、およびユーザー範囲のデータを再起動やレプリカ間で保持します。
- **高スループットエージェント (High-throughput agents)**: セッションの追加レイテンシが重要となるチャット、音声、リアルタイムオーケストレーションにおいて、ミリ秒未満の読み書きを実現します。
- **語彙的長期メモリ (Lexical long-term memory)**: 書き込み時にテキストをトークン化し、ポスティングリストキー (`app:user:kw:<token>`) へのポイント読み取りによってメモリ行を復元します。埋め込みモデルは不要です。
- **マルチモーダルアーティファクト (Multimodal artifacts)**: 画像、ファイル、生成された出力をバージョン履歴付きで保存します。 `user:` ファイル名はセッション間で可視化されます (ADK 仕様)。
- **セルフホストおよびマルチテナント (Self-hosted and multi-tenant)**: 単一のネームスペースで、テナント範囲のアーティファクトおよびメモリ操作用の複合セカンダリインデックスを提供します。 Community または Enterprise、オンプレミスまたはクラウドで利用できます。

## 前提条件

- Python 3.11 以降
- [Python用ADK](/get-started/python/) (`google-adk`)
- Aerospike Database 7.x または 8.x (Community または Enterprise)
- 接続可能なクラスタ (以下のローカル Docker の例を参照)

開発用のローカル Aerospike の起動:

```bash
docker run --rm -d --name aerospike -p 3000-3003:3000-3003 aerospike/aerospike-server:latest
```

実行可能な例におけるモデル呼び出しのために、`GOOGLE_API_KEY`（またはモデルプロバイダの資格情報）を設定します。

## インストール

```bash
pip install google-adk adk-aerospike
```

## エージェントでの使用

=== "セッション + Runner"

    永続化されたセッションを持つ完全なマルチターンエージェントを構成するために、`AerospikeSessionService` を ADK `Runner` に組み込みます。

    ```python
    import asyncio

    from adk_aerospike import AerospikeSessionService
    from google.adk.agents import LlmAgent
    from google.adk.runners import Runner
    from google.genai import types

    async def main() -> None:
        session_service = AerospikeSessionService.from_uri(
            "aerospike://localhost:3000/adk"
        )
        agent = LlmAgent(
            name="assistant",
            model="gemini-flash-latest",
            instruction="Be helpful. Keep replies under 30 words.",
        )
        runner = Runner(
            agent=agent,
            app_name="myapp",
            session_service=session_service,
        )

        session = await session_service.create_session(
            app_name="myapp", user_id="user-1"
        )
        async for event in runner.run_async(
            user_id="user-1",
            session_id=session.id,
            new_message=types.Content(
                role="user", parts=[types.Part(text="Hello")]
            ),
        ):
            if event.content:
                for part in event.content.parts or []:
                    if part.text:
                        print(part.text)

        session_service.close()

    asyncio.run(main())
    ```

=== "セッション API"

    状態、イベント、一覧表示のために、セッションサービスを直接使用します。スコープ付きのキーは ADK の規則（`app:`, `user:`, `temp:`）に従います。

    ```python
    import asyncio

    from adk_aerospike import AerospikeSessionService
    from google.adk.events import Event, EventActions
    from google.genai import types

    async def main() -> None:
        svc = AerospikeSessionService.from_uri("aerospike://localhost:3000/adk")

        session = await svc.create_session(
            app_name="support_bot",
            user_id="alice",
            state={
                "topic": "billing",
                "app:tenant": "acme-corp",
                "user:nickname": "Allie",
                "temp:scratch": "throwaway",
            },
        )

        await svc.append_event(
            session,
            Event(
                invocation_id="i1",
                author="user",
                content=types.Content(
                    role="user",
                    parts=[types.Part(text="Where is my invoice?")],
                ),
                actions=EventActions(state_delta={"turn": 1}),
            ),
        )

        fetched = await svc.get_session(
            app_name="support_bot",
            user_id="alice",
            session_id=session.id,
        )
        print(fetched.state)
        # topic, turn, app:tenant, user:nickname — temp: キーは永続化されません。

        svc.close()

    asyncio.run(main())
    ```

=== "メモリサービス"

    テキストを含むセッションイベントを永続化し、ベクトルインデックスなしで単語重複で検索します。

    ```python
    import asyncio

    from adk_aerospike import AerospikeMemoryService
    from google.adk.events import Event, EventActions
    from google.adk.sessions import Session
    from google.genai import types

    async def main() -> None:
        memory = AerospikeMemoryService.from_uri(
            "aerospike://localhost:3000/adk", top_k=10
        )

        session = Session(
            id="s-1",
            app_name="support_bot",
            user_id="alice",
            events=[
                Event(
                    invocation_id="i",
                    author="user",
                    content=types.Content(
                        role="user",
                        parts=[types.Part(text="Python uses duck typing.")],
                    ),
                    actions=EventActions(),
                ),
            ],
        )
        await memory.add_session_to_memory(session)

        resp = await memory.search_memory(
            app_name="support_bot",
            user_id="alice",
            query="python duck typing",
        )
        for m in resp.memories:
            print(m.content.parts[0].text)

        memory.close()

    asyncio.run(main())
    ```

=== "アー티팩트 서비스"

    セッションごとにバージョン管理されたアーティファクトを保存します。セッション間での可視性を高めるために、`user:` ファイル名プレフィックスを使用してください。

    ```python
    import asyncio

    from adk_aerospike import AerospikeArtifactService
    from google.genai import types

    async def main() -> None:
        svc = AerospikeArtifactService.from_uri(
            "aerospike://localhost:3000/adk"
        )

        await svc.save_artifact(
            app_name="support_bot",
            user_id="alice",
            session_id="s-1",
            filename="report.pdf",
            artifact=types.Part(
                inline_data=types.Blob(
                    mime_type="application/pdf", data=b"%PDF-1.4..."
                ),
            ),
        )

        latest = await svc.load_artifact(
            app_name="support_bot",
            user_id="alice",
            session_id="s-1",
            filename="report.pdf",
        )
        print(latest.inline_data.mime_type)

        svc.close()

    asyncio.run(main())
    ```

=== "3つのサービスを組み合わせる"

    ```python
    from adk_aerospike import (
        AerospikeArtifactService,
        AerospikeMemoryService,
        AerospikeSessionService,
    )
    from google.adk.agents import LlmAgent
    from google.adk.runners import Runner

    uri = "aerospike://localhost:3000/adk"

    session_service = AerospikeSessionService.from_uri(uri)
    artifact_service = AerospikeArtifactService.from_uri(uri)
    memory_service = AerospikeMemoryService.from_uri(uri)

    agent = LlmAgent(name="assistant", model="gemini-flash-latest")
    runner = Runner(
        agent=agent,
        app_name="myapp",
        session_service=session_service,
        artifact_service=artifact_service,
        memory_service=memory_service,
    )
    ```

=== "`adk web` と `adk run`"

    URI スキーマを一度登録します（たとえば、エージェントの隣の `services.py` 内）:

    ```python
    import adk_aerospike

    adk_aerospike.register()
    ```

    次に、各ストレージの役割について同一のネームスペースを向くように CLI に指定します:

    ```bash
    adk web \
      --session_service_uri=aerospike://localhost:3000/adk \
      --artifact_service_uri=aerospike://localhost:3000/adk \
      --memory_service_uri=aerospike://localhost:3000/adk
    ```

    !!! note

        `register()` は `aerospike://` を ADK のサービスレジストリに組み込むため、開発 UI と CLI がカスタムファクトリコードなしでこれらの URL を解決できるようになります。

## 構成

### 接続 URI

3つのサービスすべてで1つの URI 形式が共有されます:

```text
aerospike://[user:pass@]host[:port][,host2[:port],…]/<namespace>[?option=value]
```

例:

```text
aerospike://localhost:3000/adk
aerospike://user:pass@node1:3000,node2:3000/prod?set_prefix=prod_&tls=true
```

| クエリパラメータ | 説明 |
| --------------- | ----------- |
| `set_prefix` | Aerospike セット名のプレフィックス (デフォルトは `adk_`)。複数のアプリで1つのネームスペースを共有可能です。 |
| `tls=true` | TLSを有効にします。 mTLSの詳細については、`from_uri` に `tls_config={...}` を渡します。 |
| `auth_mode` | `INTERNAL` (デフォルト)、`EXTERNAL`、`EXTERNAL_INSECURE`、または `PKI`。 |

サービス間で共有接続プールを利用するために、既存の `aerospike.Client` および `Schema` を使用してサービスを構築することもできます。

### 状態のスコープ指定

セッションの `state` は、プレフィックスキーを使用します ([`google.adk.sessions.state.State`](https://github.com/google/adk-python) と同様):

| プレフィックス | 保存先 | 可視性 |
| ------ | --------- | ---------- |
| `app:foo` | `adk_app_state` | アプリの全ユーザー |
| `user:foo` | `adk_user_state` | セッションを超えた現在のユーザー |
| `temp:foo` | 永続化されない | 現在の呼び出し（invocation）のみ |
| _(プレフィックスなし)_ | 세션 레코드 | 現在のセッションのみ |

`get_session` は、ADK 互換性のためにプレフィックスが復元された1つの dict にすべてのスコープをマージします。

## 利用可能なサービス

### サービス

| サービス | ADK インターフェース | 説明 |
| ------- | ------------- | ----------- |
| `AerospikeSessionService` | `BaseSessionService` | セッション、イベント、スコープ付き状態。セッションレコード上のホットイベントテール。256KiBでのクローズドチャンク。ほとんどの追加は1回のアトミックな `operate()`。 `get_session` は 1 RTT でセッション+アプリ+ユーザー状態を取得するために `batch_read` を使用します。 |
| `AerospikeArtifactService` | `BaseArtifactService` | `(app, user, session, filename)` ごとのバージョン管理されたアーティファクト。バージョンあたり最大 8MiB までのインラインペイロード。 `user:` ファイル名は ADK ユーザーネームスペースセンチネルを使用します。 |
| `AerospikeMemoryService` | `BaseMemoryService` | テキストを含むイベントごとに1つのメモリ行。トークンごとのポスティングリスト PK。 `search_memory` はクエリトークンの重複でランク付けします。 |

### URI 登録

| 関数 | 説明 |
| -------- | ----------- |
| `adk_aerospike.register()` | CLI および `adk web` 用に `aerospike://` を ADK のサービスレジ스트リに登録します。 |

## ストレージレイアウト

ネームスペース内のデフォルトのセットプレフィックス `adk_`:

| セット | キーパターン | 用途 |
| --- | ----------- | ------- |
| `adk_sessions` | `app:user:session` | セッションレコード（状態 + ホットイベントテール） |
| `adk_sessions` | `app:user:session:c:NNNNNNNN` | チャンク化されたイベント |
| `adk_sessions` | `app:user:sl` | `list_sessions` 用のセッションリストマニフェスト |
| `adk_app_state` | `app` | アプリスコープの状態 |
| `adk_user_state` | `app:user` | ユーザースコープの状態 |
| `adk_artifacts` | `app:user:session:fname:ver` | アーティファクトのバージョン |
| `adk_memory` | `app:user:session:event_id` | メモリ行 |
| `adk_memory` | `app:user:kw:token` | 語彙検索用のポスティングリスト |

インデックス、チャンキング不変条件、および運用上の注意事項については、リポジトリの [データモデル](https://github.com/aerospike-community/adk-aerospike/blob/main/docs/data-model.md) を参照してください。

## 追加のリソース

- [adk-aerospike GitHub リポジトリ](https://github.com/aerospike-community/adk-aerospike)
- [adk-aerospike PyPI ページ](https://pypi.org/project/adk-aerospike/)
- [実行可能な例](https://github.com/aerospike-community/adk-aerospike/tree/main/examples)
- [Aerospike 公式ドキュメント](https://aerospike.com/docs/)
- [ADK セッションおよびメモリ](/sessions/)
