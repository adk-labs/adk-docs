---
catalog_title: Perseus Vault Memory
catalog_description: ADK エージェントに永続的、ローカル暗号化されたセッション間メモリを追加します
catalog_icon: /integrations/assets/perseus-vault.svg
catalog_tags: ["data"]
---

# ADK용 Perseus Vault Memory 統合

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span>
</div>

[`adk-perseus-vault-memory`](https://github.com/Perseus-Computing-LLC/adk-mimir-memory) 統合は、ADK エージェントを永続的なセッション間メモリバックエンドである [Perseus Vault](https://github.com/Perseus-Computing-LLC/perseus-vault) に接続します。SQLite データベースが組み込まれた単一の Rust バイナリでサポートされており、**クラウドへの依存関係はゼロ**で、すべてがローカルで実行されます。メモリは AES-256-GCM によって保管時に暗号化され、検索は FTS5 キーワードマッチングと密ベクトル（dense vector）の取得を組み合わせます。

## ユースケース

- **再起動をまたぐ永続的なエージェントメモリ**: プロセスの再起動後もセッションが維持され、エージェントは過去の会話を自動的に思い出します。

- **プライベート、エアギャップ（air-gapped）デプロイ**: クラウドへの依存関係はなく、Perseus Vault はローカルマシン上で完全に動作し、オプションで AES-256-GCM 暗号化を適用できます。

- **メモリにわたるハイブリッド検索**: キーワード（FTS5/BM25）とセマンティック（密ベクトル）検索を組み合わせて、関連する過去のインタラクションを見つけます。

- **ワークスペース認識エージェント**: プロジェクトファイル、git の状態、および設定を把握しているエージェントのために、Perseus とペアリングします。

## 前提条件

- Python 3.10+
- `perseus-vault` バイナーリ（[インストール](#インストール) を参照）
- `google-adk>=1.0.0`

## インストール

Python パッケージをインストールします。

```bash
pip install adk-perseus-vault-memory
```

その後、`perseus-vault` バイナリをインストールします。[リリースピージ](https://github.com/Perseus-Computing-LLC/perseus-vault/releases)からお使いのプラットフォーム用のビルドをダウンロードし、`PATH` に配置します。サービスはデフォルトで `perseus-vault` を探しますが、あるいは `PerseusVaultMemoryService` に `vault_binary="/absolute/path/to/perseus-vault"` を渡すこともできます。

## エージェントとの連携

`PerseusVaultMemoryService` を作成し、`Runner` に渡し、エージェントに `load_memory` ツールを提供して過去のセッションを思い出せるようにします。

```python
from adk_perseus_vault_memory import PerseusVaultMemoryService
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import load_memory

agent = Agent(
    name="memory_assistant",
    model="gemini-flash-latest",
    instruction="You are a helpful assistant with long-term memory.",
    tools=[load_memory],
)

runner = Runner(
    agent=agent,
    app_name="perseus_vault_app",
    session_service=InMemorySessionService(),
    memory_service=PerseusVaultMemoryService(db_path="~/.adk/vault.db"),
)
```

セッション完了後、`await memory_service.add_session_to_memory(session)` を呼び出してセッションを永続化します。エージェントは以降のセッションで `load_memory` ツールを介してメモリを呼び出します。全体の取り込みと検索のフローについては、[ADK メモリ](/ja/sessions/memory/) を参照してください。

### Perseus ライブコンテキスト (オプション)

リアルタイムのワークスペース認識を行うには、`perseus` エクストラをインストールします。

```bash
pip install adk-perseus-vault-memory[perseus]
```

推論時に `@file`、`@search`、`@memory` ディレクティブを解決する、事前構築された `perseus_context_agent` を使用します。

```python
from adk_perseus_vault_memory.perseus_context import perseus_context_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# 事前構築されたエージェントにはモデルが含まれていません。使用前にモデルを設定してください。
perseus_context_agent.model = "gemini-flash-latest"

runner = Runner(
    agent=perseus_context_agent,
    app_name="perseus_app",
    session_service=InMemorySessionService(),
    memory_service=PerseusVaultMemoryService(db_path="~/.adk/vault.db"),
)
```

セッションを作成する際、セッション状態を介して Perseus ディレクティブを設定します（非同期関数内）。

```python
session = await runner.session_service.create_session(
    app_name="perseus_app",
    user_id="user",
    state={
        "_perseus_directives": "@file AGENTS.md @file README.md @memory deployment",
        "_perseus_workspace": "/path/to/project",
    },
)
```

## 利用可能なメモリ操作

| メソッド | 説明 |
|---|---|
| `add_session_to_memory(session)` | セッション全体のイベントを永続化する |
| `add_events_to_memory(...)` | 増分イベントデルタを追加する |
| `add_memory(...)` | 明示的なメモリエントリを保存する |
| `search_memory(...)` | メモリにわたる FTS5 キーワード検索 |

## バックエンドの比較

| バックエンド | 依存関係 | 保管時暗ung化 | 検索 | ホスティング |
|---|---|---|---|---|
| **InMemoryMemoryService** | なし | 永続化されない | キーワード | ローカル (一時的) |
| **VertexAiMemoryBankService** | Google Cloud | Google 管理 | セマンティック (Gemini) | Google Cloud |
| **VertexAiRagMemoryService** | Google Cloud | Google 管理 | ベクトル類似度 | Google Cloud |
| **PerseusVaultMemoryService** | `perseus-vault` バイナリ | ローカル AES-256-GCM | ハイブリッド (FTS5 + 密) | ローカル |

## リソース

- [GitHub の adk-perseus-vault-memory](https://github.com/Perseus-Computing-LLC/adk-mimir-memory)
- [PyPI の adk-perseus-vault-memory](https://pypi.org/project/adk-perseus-vault-memory/)
- [Perseus Vault (バックアップサービス)](https://github.com/Perseus-Computing-LLC/perseus-vault)
- [Perseus Context 統合ガイド](/ja/integrations/perseus/)
