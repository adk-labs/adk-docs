# サービス登録

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.34.0</span>
</div>

セッション、アーティファクト、メモリ、および Agent2Agent（A2A）タスクストア向けのカスタムサービスを登録することで、ADK ランタイムの機能を拡張できます。カスタムサービスを登録すると、独自のバックエンドシステムやストレージプロバイダーをエージェントに統合できます。

次のいずれかの方法を使用してカスタムサービスを登録します。

*   **`services.yaml`**: シンプルなコンストラクタでインスタンス化されるサービス用の YAML 設定ファイルです。
*   **`services.py`**: カスタム初期化や複雑なロジックを必要とするサービス用の Python スクリプトです。

## `services.yaml` でサービスを登録する

シンプルなコンストラクタ（例: `MyService(uri="...")`）でインスタンス化されるサービスを登録するには、`services.yaml` または `services.yml` ファイルを使用します。このファイルをエージェントディレクトリ（`adk run` の場合）またはエージェントのルートディレクトリ（`adk web` および `adk api_server` の場合）に配置します。

`services.yaml` でカスタムサービスを定義します:

```yaml
services:
  - scheme: mysession
    type: session
    class: my_custom_package.modules.MyCustomSessionService
  - scheme: myartifact
    type: artifact
    class: my_custom_package.storage.MyCustomArtifactService
  - scheme: mymemory
    type: memory
    class: my_custom_package.modules.MyCustomMemoryService
  - scheme: mytaskstore
    type: task_store
    class: my_custom_package.tasks.MyCustomTaskStore
```

`services.yaml` ファイルは次のプロパティをサポートしています:

*   `scheme`: カスタムサービスをトリガーする URI スキーム（例: `mysession://`）。
*   `type`: サービスの種類。`session`、`artifact`、`memory`、または `task_store` を指定できます。
*   `class`: サービス実装の完全修飾クラス名。

## `services.py` でサービスを登録する

複雑な初期化が必要な場合や、サービスの作成プロセスをより細かく制御する必要がある場合は、`services.yaml` と同じ場所に配置した `services.py` ファイルを使用します。

`services.py` でカスタムの `session`、`artifact`、`memory` サービスを登録します:

```python
from google.adk.cli.service_registry import get_service_registry
from my_custom_package.modules import MyCustomSessionService
from my_custom_package.storage import MyCustomArtifactService
from my_custom_package.memory import MyCustomMemoryService

def my_session_factory(uri: str, **kwargs):
    # カスタムロジックをここに追加します。
    return MyCustomSessionService(uri=uri, **kwargs)

def my_artifact_factory(uri: str, **kwargs):
    """カスタムアーティファクトサービスをインスタンス化するファクトリ関数。"""
    return MyCustomArtifactService(uri=uri, **kwargs)

def my_memory_factory(uri: str, **kwargs):
    """カスタムメモリサービスをインスタンス化するファクトリ関数。"""
    return MyCustomMemoryService(uri=uri, **kwargs)

# レジストリを取得します。
registry = get_service_registry()

# セッション、アーティファクト、メモリサービスを登録します。
registry.register_session_service("mysession", my_session_factory)
registry.register_artifact_service("myartifact", my_artifact_factory)
registry.register_memory_service("mymemory", my_memory_factory)
```

このサンプルスクリプトは次の処理を行います:

1.  `get_service_registry` をインポートして、サービスレジストリのインスタンスを取得します。
2.  URI とキーワード引数を受け取り、カスタムサービスのインスタンスを返すファクトリ関数（`my_session_factory` など）を定義します。
3.  `register_session_service`、`register_artifact_service`、および `register_memory_service` を使用して、目的のスキーム（`mysession` など）でファクトリ関数を登録します。

## サービスの読み込み

ADK コマンドラインツール（`adk run`、`adk web`、または `adk api_server`）でエージェントを実行すると、ADK は `services.yaml`（または `services.yml`）と `services.py` からカスタムサービスを自動的に検出して読み込みます。

### 検出場所

ADK は実行するコマンドに基づいて設定ファイルを検索します:

*   **`adk run`**: エージェントディレクトリ内のサービスファイルを検出します。
*   **`adk web` および `adk api_server`**: コマンドに渡されたエージェントのルートディレクトリ内のサービスファイルを検出します。

### 読み込み順序と優先順位

対象ディレクトリに `services.yaml` と `services.py` の両方が存在する場合:

1.  **読み込み順序**: ADK は最初に `services.yaml` を読み込み、次に `services.py` を読み込みます。
2.  **優先順位**: 同じスキームを持つサービスが両方のファイルで定義されている場合、`services.py` の定義が優先されます。
