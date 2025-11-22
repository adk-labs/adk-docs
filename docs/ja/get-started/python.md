# ADK用Pythonクイックスタート

このガイドでは、Agent Development Kit (ADK) for Pythonを使い始める方法について説明します。開始する前に、次のものがインストールされていることを確認してください。

*   Python 3.10以降
*   パッケージインストールのための`pip`

## インストール

次のコマンドを実行してADKをインストールします。

```shell
pip install google-adk
```

??? tip "推奨: Python仮想環境の作成とアクティブ化"

    Python仮想環境を作成します。

    ```shell
    python -m venv .venv
    ```

    Python仮想環境をアクティブ化します。

    === "Windows CMD"

        ```console
        .venv\Scripts\activate.bat
        ```

    === "Windows Powershell"

        ```console
        .venv\Scripts\Activate.ps1
        ```

    === "MacOS / Linux"

        ```bash
        source .venv/bin/activate
        ```

## エージェントプロジェクトを作成する

`adk create`コマンドを実行して、新しいエージェントプロジェクトを開始します。

```shell
adk create my_agent
```

### エージェントプロジェクトを探索する

作成されたエージェントプロジェクトは次の構造を持ち、`agent.py`ファイルにはエージェントのメイン制御コードが含まれています。

```none
my_agent/
    agent.py      # メインエージェントコード
    .env          # APIキーまたはプロジェクトID
    __init__.py
```

## エージェントプロジェクトを更新する

`agent.py`ファイルには`root_agent`の定義が含まれており、これはADKエージェントの唯一の必須要素です。エージェントが使用するツールを定義することもできます。生成された`agent.py`コードを更新して、エージェントが使用する`get_current_time`ツールを含めるようにします。これは次のコードに示されています。

```python
from google.adk.agents.llm_agent import Agent

# モックツールの実装
def get_current_time(city: str) -> dict:
    """指定された都市の現在時刻を返します。"""
    return {"status": "success", "city": city, "time": "午前10時30分"}

root_agent = Agent(
    model='gemini-3-pro-preview',
    name='root_agent',
    description="指定された都市の現在時刻を伝えます。",
    instruction="あなたは都市の現在時刻を伝えるのに役立つアシスタントです。この目的のために'get_current_time'ツールを使用してください。",
    tools=[get_current_time],
)
```

### APIキーを設定する

このプロジェクトはAPIキーを必要とするGemini APIを使用します。まだGemini APIキーをお持ちでない場合は、Google AI Studioの[APIキー](https://aistudio.google.com/app/apikey)ページでキーを作成してください。

ターミナルウィンドウで、APIキーを`.env`ファイルに環境変数として書き込みます。

```console title="更新: my_agent/.env"
echo 'GOOGLE_API_KEY="YOUR_API_KEY"' > .env
```

??? tip "ADKで他のAIモデルを使用する"
    ADKは多くの生成AIモデルの使用をサポートしています。ADKエージェントで他のモデルを構成する方法の詳細については、[モデルと認証](/adk-docs/ja/agents/models)を参照してください。

## エージェントを実行する

`adk run`コマンドを使用して対話型コマンドラインインターフェースでADKエージェントを実行するか、`adk web`コマンドを使用してADKが提供するADKウェブユーザーインターフェースを使用して実行できます。これらのオプションの両方で、エージェントをテストして対話できます。

### コマンドラインインターフェースで実行する

`adk run`コマンドラインツールを使用してエージェントを実行します。

```console
adk run my_agent
```

![adk-run.png](/adk-docs/ja/assets/adk-run.png)

### ウェブインターフェースで実行する

ADKフレームワークは、エージェントをテストして対話するために使用できるウェブインターフェースを提供します。次のコマンドを使用してウェブインターフェースを起動できます。

```console
adk web --port 8000
```

!!! note

    `my_agent/`フォルダを含む**親ディレクトリ**からこのコマンドを実行してください。たとえば、エージェントが`agents/my_agent/`内にある場合は、`agents/`ディレクトリから`adk web`を実行してください。

このコマンドは、エージェント用のチャットインターフェースを備えたウェブサーバーを起動します。ウェブインターフェースは(http://localhost:8000)でアクセスできます。左上隅でエージェントを選択し、リクエストを入力します。

![adk-web-dev-ui-chat.png](/adk-docs/ja/assets/adk-web-dev-ui-chat.png)

## 次へ: エージェントを構築する

ADKがインストールされ、最初のエージェントが実行中になったので、ビルドガイドを使用して独自のエージェントを構築してみてください。

*  [エージェントを構築する](/adk-docs/ja/tutorials/)