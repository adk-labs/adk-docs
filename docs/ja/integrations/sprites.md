---
catalog_title: Sprites
catalog_description: エージェントのコード実行のためのチェックポイントと復元機能を備えた、永続的でステートフルな Linux サンドボックス
catalog_icon: /integrations/assets/sprites.png
catalog_tags: ["code"]
---

# ADK用 Sprites プラグイン

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span>
</div>

[Sprites ADK プラグイン](https://github.com/superfly/sprites-adk) は、ADK エージェントを [Fly.io](https://fly.io) が提供する永続的でステートフルな Linux サンドボックスである [Sprites](https://sprites.dev) に接続します。一時的なサンドボックスとは異なり、Sprite はセッション間でファイルシステム、インストールされたパッケージ、実行中のプロセスを保持し、状態全体を **チェックポイント作成と復元（checkpoint and restore）** できます。これにより、エージェントは危険な変更の前に環境のスナップショットを作成し、問題が発生した場合はロールバックできます。

## ユースケース

- **永続的な開発環境（Persistent development environments）**: セッション間で名前付きの Sprite が再利用されます。以前の実行의パッケージやファイルが残っているため、長期にわたるプロジェクトで毎回最初から環境を構築し直す必要がありません。

- **安全なコード実行（Secure code execution）**: エージェントが生成した Python、JavaScript、または bash を、ホストマシンではなく、分離されたマイクロVM（microVM）で実行します。

- **安全な実験（Safe experimentation）**: パッケージのアップグレード、移行、または一括編集の前に環境全体のチェックポイントを作成し、変更によって問題が発生した場合はそのチェックポイントまで復元します。

- **ファイルワークフロー（File workflows）**: スクリプトやデータをサンドボックスに書き込み、それを実行し、結果を読み戻します。

## 前提条件

- [Sprites](https://sprites.dev) アカウント
- Sprites API トークン（`SPRITES_TOKEN` 환경변수로 설정）

## インストール

```bash
pip install sprites-adk
```

## エージェントとの連携

```python
from sprites_adk import SpritesPlugin
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner

# SpritesPlugin() は実行ごとに新しいサンドボックスを提供します。
# SpritesPlugin(sprite_name="my-project") はセッション間で1つの永続的な環境を再利用します。
plugin = SpritesPlugin(
  # token="your-sprites-token"  # 또는 SPRITES_TOKEN 환경변수를 설정합니다.
)

root_agent = Agent(
    model="gemini-flash-latest",
    name="sandbox_agent",
    instruction="Run code and commands in the Sprite sandbox, not locally.",
    tools=plugin.get_tools(),
)

# ライフサイクルコールバックとクリーンアップが実行されるように、ランナーにプラグインを登録します。
runner = InMemoryRunner(agent=root_agent, plugins=[plugin])
```

## 利用可能なツール

ツール | 説明
---- | -----------
`execute_command_in_sprite` | サンドボックスでシェルコマンドを実行する
`execute_code_in_sprite` | Python、JavaScript、または bash コードを実行する
`write_file_to_sprite` | サンドボックスにテキストファイルを書き込む
`read_file_from_sprite` | サンドボックスからテキストファイルを読み取る
`create_sprite_checkpoint` | 環境全体（ファイルシステム、パッケージ、プロセス）のスナップショットを作成する
`list_sprite_checkpoints` | 利用可能なチェックポイントの一覧を表示する
`restore_sprite_checkpoint` | チェックポイントにロールバックする（破壊的、確認が必要）

## 追加リソース

- [PyPI の sprites-adk](https://pypi.org/project/sprites-adk/)
- [GitHub の sprites-adk](https://github.com/superfly/sprites-adk)
- [Sprites ドキュメント](https://docs.sprites.dev)
