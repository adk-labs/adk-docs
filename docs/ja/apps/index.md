# アプリ: ワークフロー管理クラス

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.14.0</span>
</div>

***App***クラスは、Agent Development Kit（ADK）エージェントワークフロー全体の上位コンテナです。***ルートエージェント***によってグループ化されたエージェントのコレクションのライフサイクル、構成、および状態を管理するように設計されています。**App**クラスは、エージェントワークフローの全体的な運用インフラストラクチャの懸念事項を、個々のエージェントのタスク指向の推論から分離します。

ADKワークフローで***App***オブジェクトを定義することはオプションであり、エージェントコードの整理方法とエージェントの実行方法を変更します。実用的な観点から、***App***クラスを使用して、エージェントワークフローの次の機能を構成します。

*   [**コンテキストキャッシュ**](/adk-docs/context/caching/)
*   [**コンテキスト圧縮**](/adk-docs/context/compaction/)
*   [**エージェントの再開**](/adk-docs/runtime/resume/)
*   [**プラグイン**](/adk-docs/plugins/)

このガイドでは、ADKエージェントワークフローの構成と管理にAppクラスを使用する方法について説明します。

## Appクラスの目的

***App***クラスは、複雑なエージェントシステムを構築する際に発生するいくつかのアーキテクチャ上の問題に対処します。

*   **一元化された構成:** APIキーやデータベースクライアントなどの共有リソースを管理するための一元化された単一の場所を提供し、すべてのエージェントに構成を渡す必要がなくなります。
*   **ライフサイクル管理:** ***App***クラスには***起動時***および***シャットダウン時***のフックが含まれており、複数の呼び出しにわたって存在する必要があるデータベース接続プールやインメモリキャッシュなどの永続的なリソースを確実に管理できます。
*   **状態スコープ:** `app:*`プレフィックスを使用してアプリケーションレベルの状態の明示的な境界を定義し、この状態のスコープと存続期間を開発者に明確にします。
*   **デプロイ単位:** ***App***の概念は、正式な*デプロイ可能単位*を確立し、エージェントアプリケーションのバージョン管理、テスト、および提供を簡素化します。

## Appオブジェクトを定義する

***App***クラスは、エージェントワークフローのプライマリコンテナとして使用され、プロジェクトのルートエージェントが含まれています。***ルートエージェント***は、プライマリコントローラエージェントと追加のサブエージェントのコンテナです。

### ルートエージェントでアプリを定義する

***Agent***基本クラスからサブクラスを作成して、ワークフローの***ルートエージェント***を作成します。次に、次のサンプルコードに示すように、***App***オブジェクトを定義し、***ルートエージェント***オブジェクトとオプション機能で構成します。

```python title="agent.py"
from google.adk.agents.llm_agent import Agent
from google.adk.apps import App

root_agent = Agent(
    model='gemini-2.5-flash',
    name='greeter_agent',
    description='An agent that provides a friendly greeting.',
    instruction='Reply with Hello, World!',
)

app = App(
    name="agents",
    root_agent=root_agent,
    # Optionally include App-level features:
    # plugins, context_cache_config, resumability_config
)
```

!!! tip "推奨：`app`変数名を使用する"

    エージェントプロジェクトコードで、***App***オブジェクトを変数名`app`に設定して、ADKコマンドラインインターフェイスランナーツールと互換性があるようにします。

### Appエージェントを実行する

次のコードサンプルに示すように、`app`パラメータを使用して***Runner***クラスを使用してエージェントワークフローを実行できます。

```python title="main.py"
import asyncio
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from agent import app # agent.pyからコードをインポート

load_dotenv() # APIキーと設定を読み込む
# インポートされたアプリケーションオブジェクトを使用してランナーを設定する
runner = InMemoryRunner(app=app)

async def main():
    try:  # run_debug()にはADK Python 1.18以降が必要です。
        response = await runner.run_debug("Hello there!")
        
    except Exception as e:
        print(f"An error occurred during agent execution: {e}")

if __name__ == "__main__":
    asyncio.run(main())

```

!!! note "`Runner.run_debug()`のバージョン要件"

    `Runner.run_debug()`コマンドには、ADK Python v1.18.0以降が必要です。より多くのセットアップコードが必要な`Runner.run()`を使用することもできます。詳細については、次を参照してください。

次のコマンドを使用して、`main.py`コードでAppエージェントを実行します。

```console
python main.py
```

## 次のステップ

より完全なサンプルコードの実装については、[Hello Worldアプリ](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world_app)のコード例を参照してください。
