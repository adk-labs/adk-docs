---
catalog_title: Database Memory Service
catalog_description: エージェント向けの SQL ベース永続メモリ
catalog_icon: /integrations/assets/adk-database-memory.png
catalog_tags: ["data"]
---

# ADK 向け Database Memory Service

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span>
</div>

[`adk-database-memory`](https://github.com/anmolg1997/adk-database-memory) は、非同期 SQLAlchemy をバックエンドとする ADK Python 向けのドロップイン永続 `BaseMemoryService` です。この連携により、独自のデータベースを使用して ADK エージェントにセッションをまたぐ永続メモリを提供できます。開発環境では SQLite、本番環境では PostgreSQL や MySQL を利用できます。

## ユースケース

- **パーソナライズされたアシスタント**: 長期的なユーザーの好み、事実、過去の意思決定をセッションをまたいで蓄積し、エージェントが必要に応じて想起できるようにします。
- **サポートおよびタスクエージェント**: チケットやデバイスをまたいで会話履歴を永続化し、ユーザーが戻ってきたときにいつでもコンテキストを利用できるようにします。
- **セルフホストデプロイ**: Vertex AI Memory Bank を利用できない環境（オンプレミス、エアギャップ環境、GCP 以外のクラウドなど）において、既存のデータベース上にメモリを保存します。
- **ローカル開発**: 設定不要で再起動後も保持される SQLite の永続メモリをすぐに導入でき、本番環境では接続文字列を PostgreSQL に切り替えるだけで移行できます。

## 前提条件

- Python 3.10 以降
- サポートされているデータベース: SQLite、PostgreSQL、または MySQL / MariaDB

## インストール

使用するデータベース用のドライバと一緒にパッケージをインストールします。

```bash
pip install "adk-database-memory[sqlite]"    # SQLite (via aiosqlite)
pip install "adk-database-memory[postgres]"  # PostgreSQL (via asyncpg)
pip install "adk-database-memory[mysql]"     # MySQL / MariaDB (via aiomysql)
```

コアパッケージにはデータベースドライバが含まれていません。バックエンドに対応するエクストラを選択するか、任意の非同期ドライバを個別にインストールしてください。

## エージェントでの使用

このサービスは `google.adk.memory.base_memory_service.BaseMemoryService` を実装しているため、`memory_service` を受け取る任意の ADK `Runner` にそのまま組み込めます。

```python
import asyncio

from adk_database_memory import DatabaseMemoryService
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner

memory = DatabaseMemoryService("sqlite+aiosqlite:///memory.db")

agent = Agent(
    name="assistant",
    model="gemini-flash-latest",
    instruction="You are a helpful assistant.",
)

async def main():
    async with memory:
        # Run the agent, then persist the session to memory
        runner = InMemoryRunner(agent=agent, app_name="my_app")
        session = await runner.session_service.create_session(app_name="my_app", user_id="u1")
        # After the session completes:
        await memory.add_session_to_memory(session)

        # Later, recall relevant memories for a new query:
        result = await memory.search_memory(
            app_name="my_app",
            user_id="u1",
            query="what did we decide about the pricing model?",
        )
        for entry in result.memories:
            print(entry.author, entry.timestamp, entry.content)

asyncio.run(main())
```

## サポートされているバックエンド

| バックエンド | 接続 URL の例 | エクストラ |
| ---- | ---- | ---- |
| SQLite | `sqlite+aiosqlite:///memory.db` | `[sqlite]` |
| SQLite（インメモリ） | `sqlite+aiosqlite:///:memory:` | `[sqlite]` |
| PostgreSQL | `postgresql+asyncpg://user:pass@host/db` | `[postgres]` |
| MySQL / MariaDB | `mysql+aiomysql://user:pass@host/db` | `[mysql]` |
| 任意の非同期 SQLAlchemy ダイアレクト | ドライバに依存 | 任意のドライバを個別インストール |

## API

| メソッド | 説明 |
| ---- | ---- |
| `add_session_to_memory(session)` | 完了したセッション内のすべてのイベントをインデックス化します。 |
| `add_events_to_memory(app_name, user_id, events, ...)` | 明示的なイベントのスライスをインデックス化します（ストリーミング取り込みに便利です）。 |
| `search_memory(app_name, user_id, query)` | 指定されたアプリとユーザーをスコープとして、インデックス済みキーワードがクエリと一致する `MemoryEntry` オブジェクトを返します。 |

初回の書き込み時に、サービスは `(app_name, user_id)` にインデックスを持つ単一のテーブル（`adk_memory_entries`）を作成します。JSON コンテンツは PostgreSQL では `JSONB`、MySQL では `LONGTEXT`、SQLite では `TEXT` として保存されます。

取得処理では、ADK のインメモリメモリサービスおよび Firestore メモリサービスと同じキーワード抽出・マッチング方式を使用します。埋め込み（Embedding）ベースの検索を行う場合は、Vertex AI Memory Bank またはベクトルストアと組み合わせて使用してください。

## リソース

- [GitHub リポジトリ](https://github.com/anmolg1997/adk-database-memory): ソースコード、Issue、およびサンプル。
- [PyPI パッケージ](https://pypi.org/project/adk-database-memory/): リリースおよびインストール手順。
- [ADK メモリの概要](/sessions/memory/): ADK におけるメモリサービスの仕組みと背景。
