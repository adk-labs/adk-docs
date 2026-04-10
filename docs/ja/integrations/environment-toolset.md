---
catalog_title: Environment Toolset
catalog_description: ファイル、スクリプト、コード実行のためのローカルおよびカスタム計算環境を作成します
catalog_icon: /integrations/assets/adk.png
catalog_tags: ["code", "google"]
---

# ADK 向け Environment Toolset

<div class="language-support-tag">
  <span class="lst-supported">ADK でサポート</span><span class="lst-python">Python v1.29.0</span><span class="lst-preview">Experimental</span>
</div>

特にコーディングやファイル操作のように、複数のエージェント要求にまたがって
保持される計算環境でのコード実行とファイル操作が必要なタスクがあります。
ADK の ***EnvironmentToolset*** クラスを使うと、エージェントは環境とやり取りして
ファイル操作を実行し、シェルコマンドを実行できます。
Environment Toolset は、ADK エージェントで使用するローカルまたはリモート実行環境を
構成・利用するための汎用フレームワークとして設計されています。
ADK はこのフレームワーク向けに [***LocalEnvironment***](#local-environment)
実装を提供しています。

!!! example "Experimental"
    Environment Toolset 機能は experimental であり、変更される可能性があります。
    フィードバックがあれば
    [こちら](https://github.com/google/adk-python/issues/new?template=feature_request.md)からお送りください。

## はじめに

***EnvironmentToolset*** に ***LocalEnvironment*** インスタンスを追加して、
エージェントがローカル環境とやり取りできるようにします。

```python
from google.adk import Agent
from google.adk.environment import LocalEnvironment
from google.adk.tools.environment import EnvironmentToolset

root_agent = Agent(
    model="gemini-flash-latest",
    name="my_agent",
    instruction="""
    あなたはローカル環境を使ってコマンド実行とファイル I/O を行える
    便利な AI アシスタントです。環境のルールとユーザーの指示に従ってください。
    """,
    tools=[
        EnvironmentToolset(
            environment=LocalEnvironment(),
        ),
    ],
)
```

完全な実装例は
[Local environment sample](https://github.com/google/adk-python/tree/main/contributing/samples/local_environment)
を参照してください。

### エージェントで試す

対話セッションで、ファイル操作やコマンド実行が必要なプロンプトを与えると、
Environment Toolset を設定したエージェントとやり取りできます。次のプロンプトを試してください。

```none
Write a Python file named hello.py to the working directory
that prints 'Hello from ADK!'. Then read the file to verify
its contents, and finally execute it using a command.
```

この指示により、エージェントは次の操作を行います。

-   ファイル作成: `hello.py` を作成し、"Hello from ADK!" の内容を書き込みます。
-   ファイル読み取り: `hello.py` を読み込み、内容を確認します。
-   実行: `hello.py` を実行し、出力を返します。

## LocalEnvironment {#local-environment}

***LocalEnvironment*** クラスは ADK が提供する環境実装で、
***Environment Toolset*** とともに使います。この環境には次の機能があります。

-   **ローカル実行:** Python asyncio subprocess を使って、ローカルマシン上で
    シェルコマンドやスクリプトを直接実行します。
-   **ファイル操作:** 指定した作業ディレクトリ内でファイルを作成、読み取り、変更します。
-   **カスタマイズ:** エージェントのワークスペース用に環境変数と作業ディレクトリを設定できます。
-   **フレームワーク互換性:** グラフベースのワークフローを含め、ADK 1.0 と ADK 2.0
    の両方に対応します。

### 構成オプション

***LocalEnvironment*** クラスは次のパラメータをサポートします。

-   **working_dir**: (任意) エージェントがファイル操作とコマンド実行を行うディレクトリです。
    作業ディレクトリを設定すると、生成されたファイルはエージェント終了後も利用できます。
    詳細は [ファイルの永続化](#file-persistence) を参照してください。
-   **env_vars**: (任意) 実行コンテキストに設定する環境変数の辞書です。

次のコードサンプルは、***LocalEnvironment*** オブジェクトにこれらのオプションを設定する方法を示します。

```python
local_environment=LocalEnvironment(
    working_dir="/tmp/my_agent_workspace",
    env_vars={"PORT": "8080", "LOG_LEVEL": "DEBUG"},
)
```

### ファイル操作

***LocalEnvironment*** 実装には、ローカル計算環境でエージェントが実行できる次のツールが含まれます。

-   ***ReadFile***: エージェントの指示に従って既存のテキストファイルを読み取ります。
-   ***EditFile***: エージェントの指示に従って既存のテキストファイルを編集します。
-   ***WriteFile***: エージェントの指示に従って新しいテキストファイルを作成します。
-   ***Execute***: インストーラ、シェルスクリプト、プログラムコードの実行を含むターミナルコマンドを、
    エージェントの指示に従って実行します。

!!! danger "Danger: Potential data loss, code execution"

    ローカル環境でターミナルコマンドを実行すると、その環境のデータが失われたり、
    コードやアプリケーションの実行に影響したりする可能性があります。ファイル変更や
    コマンド実行を許可する前に、人的な承認チェックを導入することを検討してください。

***LocalEnvironment*** で実行されるコマンドは `asyncio.create_subprocess_shell` を使うため、
長時間実行タスク中でもエージェントは応答性を保てます。

### ファイルの永続化 {#file-persistence}

***LocalEnvironment*** で生成されたファイルと出力は、デフォルトでは一時ディレクトリに配置されます。
そのディレクトリは、たとえば ADK Web セッションを終了したときのように、エージェントが終了すると削除されます。
ただし、環境に ***working directory*** を設定している場合、その場所に書き込まれたファイルは
エージェント終了後も *削除されません*。

**Tip:** エージェントセッション間のファイル保持をより細かく制御したい場合は、
[***Artifacts***](/ja/artifacts/) と Artifact Service を使ってファイルを環境へアップロード/
ダウンロードしてください。

## カスタム環境

***EnvironmentToolset*** アーキテクチャは拡張可能で、リモート環境を含む独自のカスタム環境を
作成できます。この機能向けの実行環境は
[BaseEnvironment](https://github.com/google/adk-python/blob/main/src/google/adk/environment/_base_environment.py)
クラスを基に作成することを推奨します。開始にあたっては
[LocalEnvironment](https://github.com/google/adk-python/blob/main/src/google/adk/environment/_local_environment.py)
実装を参照するとよいでしょう。
