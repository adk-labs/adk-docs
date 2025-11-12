# ADK向けPythonクイックスタート

このガイドでは、Python向けAgent Development Kit（ADK）のセットアップと実行方法について説明します。開始する前に、以下がインストールされていることを確認してください。

*   Python 3.9以降
*   パッケージをインストールするための`pip`

## インストール

次のコマンドを実行してADKをインストールします。

```shell
pip install google-adk
```

??? tip "推奨：Python仮想環境の作成とアクティブ化"

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

## エージェントプロジェクトの作成

`adk create`コマンドを実行して、新しいエージェントプロジェクトを開始します。

```shell
adk create my_agent
```

### エージェントプロジェクトの探索

作成されたエージェントプロジェクトは次の構造を持ち、`agent.py`ファイルにエージェントのメイン制御コードが含まれています。

```none
my_agent/
    agent.py      # メインエージェントコード
    .env          # APIキーまたはプロジェクトID
    __init__.py
```

## エージェントプロジェクトの更新

`agent.py`ファイルには、ADKエージェントの唯一の必須要素である`root_agent`定義が含まれています。エージェントが使用するツールを定義することもできます。次のコードに示すように、生成された`agent.py`コードを更新して、エージェントが使用する`get_current_time`ツールを含めます。

```python
from google.adk.agents.llm_agent import Agent

# モックツール実装
def get_current_time(city: str) -> dict:
    """指定された都市の現在時刻を返します。"""
    return {"status": "success", "city": city, "time": "10:30 AM"}

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description="指定された都市の現在時刻を伝えます。",
    instruction="あなたは都市の現在時刻を伝える役立つアシスタントです。この目的のために「get_current_time」ツールを使用してください。",
    tools=[get_current_time],
)
```

### APIキーの設定

このプロジェクトでは、APIキーが必要なGemini APIを使用します。まだGemini APIキーをお持ちでない場合は、Google AI Studioの[APIキー](https://aistudio.google.com/app/apikey)ページでキーを作成してください。

ターミナルウィンドウで、APIキーを環境変数として`.env`ファイルに書き込みます。

```console title="Update: my_agent/.env"
echo 'GOOGLE_API_KEY="YOUR_API_KEY"' > .env
```

??? tip "ADKで他のAIモデルを使用する"
    ADKは、多くの生成AIモデルの使用をサポートしています。ADKエージェントで他のモデルを構成する方法の詳細については、[モデルと認証](/adk-docs/agents/models)を参照してください。

## エージェントの実行

`adk run`コマンドを使用するインタラクティブなコマンドラインインターフェイス、または`adk web`コマンドを使用してADKが提供するADK Webユーザーインターフェイスを使用して、ADKエージェントを実行できます。これらのオプションの両方で、エージェントをテストして対話できます。

### コマンドラインインターフェイスで実行

`adk run`コマンドラインツールを使用してエージェントを実行します。

```console
adk run my_agent
```

![adk-run.png](/adk-docs/assets/adk-run.png)

### Webインターフェイスで実行

ADKフレームワークは、エージェントをテストして対話するために使用できるWebインターフェイスを提供します。次のコマンドを使用してWebインターフェイスを起動できます。

```console
adk web --port 8000
```

!!! note

    このコマンドは、`my_agent/`フォルダーを含む**親ディレクトリ**から実行してください。たとえば、エージェントが`agents/my_agent/`内にある場合は、`agents/`ディレクトリから`adk web`を実行します。

このコマンドは、エージェント用のチャットインターフェイスを備えたWebサーバーを起動します。（http://localhost:8000）でWebインターフェイスにアクセスできます。左上隅でエージェントを選択し、リクエストを入力します。

![adk-web-dev-ui-chat.png](/adk-docs/assets/adk-web-dev-ui-chat.png)

## 次へ：エージェントの構築

ADKをインストールして最初のエージェントを実行したので、ビルドガイドを使用して独自のエージェントを構築してみてください。

*  [エージェントの構築](/adk-docs/tutorials/)
