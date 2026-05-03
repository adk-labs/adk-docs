---
catalog_title: Database Memory Service
catalog_description: エージェント用の SQL ベースの永続メモリ
catalog_icon: /integrations/assets/adk-database-memory.png
catalog_tags: ["data"]
---


# ADK のデータベース メモリ サービス

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[`adk-database-memory`](https://github.com/anmolg1997/adk-database-memory) は
ADK Python 用のドロップイン永続 `BaseMemoryService`、非同期によるサポート
SQL錬金術。この統合により、ADK に永続的なクロスセッション メモリが提供されます。
独自のデータベースを使用するエージェント: 開発には SQLite、または Postgres / MySQL を使用
生産用に。

## 使用例

- **パーソナライズされたアシスタント**: 長期的なユーザーの好み、事実、および情報を蓄積します。
  セッション全体にわたる過去の決定により、エージェントはオンデマンドでそれらを思い出すことができます。
- **サポートおよびタスク エージェント**: チケット間での会話履歴を保持し、
  デバイスにアクセスできるため、ユーザーが戻るたびにコンテキストを利用できるようになります。
- **セルフホスト展開**: Vertex AI Memory Bank がオプションではない場合
  （オンプレミス、エアギャップ、非 GCP クラウド）、既存のデータベースにメモリを保持します
  使用します。
- **ローカル開発**: SQLite を導入してゼロ構成の永続メモリを実現します。
  存続する場合は再起動し、接続文字列を運用環境の Postgres に切り替えます。

## 前提条件

- Python 3.10以降
- サポートされているデータベース: SQLite、PostgreSQL、または MySQL / MariaDB

## インストール

データベース用のドライバーと一緒にパッケージをインストールします。

```bash
pip install "adk-database-memory[sqlite]"    # SQLite (via aiosqlite)
pip install "adk-database-memory[postgres]"  # PostgreSQL (via asyncpg)
pip install "adk-database-memory[mysql]"     # MySQL / MariaDB (via aiomysql)
```

コア パッケージにはデータベース ドライバーは含まれません。追加のものを選択してください
バックエンドと一致するか、独自の非同期ドライバーを個別にインストールします。

## エージェントと一緒に使用する

サービスが実装するのは、
`google.adk.memory.base_memory_service.BaseMemoryService` なので、どのスロットにも差し込めます
`memory_service` を受け入れる ADK `Runner`:

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

|バックエンド |接続URLの例 |番外編 |
| ---- | ---- | ---- |
| SQLite | `sqlite+aiosqlite:///memory.db` | `[sqlite]` |
| SQLite (インメモリ) | `sqlite+aiosqlite:///:memory:` | `[sqlite]` |
|ポストグレSQL | `postgresql+asyncpg://user:pass@host/db` | `[postgres]` |
| MySQL / マリアDB | `mysql+aiomysql://user:pass@host/db` | `[mysql]` |
|任意の非同期 SQLAlchemy 方言 |ドライバーによって異なります |自分のものを持ってきてください |

## API

|方法 |説明 |
| ---- | ---- |
| `add_session_to_memory(session)` |完了したセッション内のすべてのイベントにインデックスを付けます。 |
| `add_events_to_memory(app_name, user_id, events, ...)` |イベントの明示的なスライスにインデックスを付けます (ストリーミング取り込みに役立ちます)。 |
| `search_memory(app_name, user_id, query)` |指定されたアプリとユーザーを範囲とする、インデックス付きキーワードがクエリと重複する `MemoryEntry` オブジェクトを返します。 |

最初の書き込み時に、サービスは次のような単一のテーブル (`adk_memory_entries`) を作成します。
`(app_name, user_id)` のインデックス。 JSON コンテンツは `JSONB` として保存されます。
PostgreSQL、MySQL の `LONGTEXT`、SQLite の `TEXT`。

検索では、検索と同じキーワード抽出および照合アプローチが使用されます。
ADK のインメモリ サービスと Firestore メモリ サービス。埋め込みベースのリコールの場合、ペア
このパッケージには Vertex AI Memory Bank または Vector ストアが含まれています。

## リソース

- [GitHub repository](https://github.com/anmolg1997/adk-database-memory): ソース
  コード、問題、例。
- [PyPI package](https://pypi.org/project/adk-database-memory/): リリースと
  インストール手順。
- [ADK Memory overview](/sessions/memory/):
  ADK がメモリ サービスを使用する方法の背景。
