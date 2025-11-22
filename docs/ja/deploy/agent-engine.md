# Vertex AI Agent Engine へのデプロイ

<div class="language-support-tag" title="Vertex AI Agent Engineは現在Pythonのみをサポートしています。">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span>
</div>

[Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)は、開発者が本番環境でAIエージェントをデプロイ、管理、スケーリングできるようにする、フルマネージドのGoogle Cloudサービスです。Agent Engineが本番環境でのエージェントのスケーリングに必要なインフラストラクチャを処理するため、開発者はインテリジェントでインパクトのあるアプリケーションの作成に集中できます。このガイドでは、ADKプロジェクトを迅速にデプロイしたい場合のための高速デプロイ手順と、エージェントをAgent Engineに慎重にデプロイしたい場合のための標準的なステップバイステップの手順を提供します。

!!! example "プレビュー: Vertex AI Express モード"
    Google Cloudプロジェクトをお持ちでない場合でも、[Vertex AI Express モード](https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview)を使用してAgent Engineを無料でお試しいただけます。この機能の使用方法については、[標準デプロイ](#standard-deployment)セクションをご覧ください。

## 高速デプロイ

このセクションでは、[Agent Starter Pack](https://github.com/GoogleCloudPlatform/agent-starter-pack) (ASP)とADKコマンドラインインターフェース(CLI)ツールを使用したデプロイ方法について説明します。このアプローチでは、ASPツールを使用して既存のプロジェクトにプロジェクトテンプレートを適用し、デプロイ用のアーティファクトを追加して、エージェントプロジェクトのデプロイ準備を整えます。以下の手順では、ASPを使用してADKプロジェクトのデプロイに必要なサービスをGoogle Cloudプロジェクトにプロビジョニングする方法を説明します。

-   [前提条件](#prerequisites-ad): Google Cloudアカウント、プロジェクトのセットアップ、および必要なソフトウェアのインストール。
-   [ADKプロジェクトの準備](#prepare-ad): デプロイの準備として、既存のADKプロジェクトファイルを変更。
-   [Google Cloudプロジェクトへの接続](#connect-ad): 開発環境をGoogle CloudおよびGoogle Cloudプロジェクトに接続。
-   [ADKプロジェクトのデプロイ](#deploy-ad): Google Cloudプロジェクトに必要なサービスをプロビジョニングし、ADKプロジェクトのコードをアップロード。

デプロイされたエージェントのテストについては、[デプロイされたエージェントのテスト](#test-deployment)をご覧ください。Agent Starter Packとそのコマンドラインツールの使用に関する詳細については、[CLIリファレンス](https://googlecloudplatform.github.io/agent-starter-pack/cli/enhance.html)および[開発ガイド](https://googlecloudplatform.github.io/agent-starter-pack/guide/development-guide.html)をご覧ください。

### 前提条件 {#prerequisites-ad}

このデプロイパスを使用するには、以下のリソースが設定されている必要があります。

-   **Google Cloudアカウント**: 以下への管理者アクセス権を持つこと。
-   **Google Cloudプロジェクト**: [課金が有効](https://cloud.google.com/billing/docs/how-to/modify-project)になっている空のGoogle Cloudプロジェクト。プロジェクトの作成については、[プロジェクトの作成と管理](https://cloud.google.com/resource-manager/docs/creating-managing-projects)をご覧ください。
-   **Python環境**: 3.9から3.13までのPythonバージョン。
-   **UVツール**: Python開発環境の管理とASPツールの実行。インストール詳細は[UVのインストール](https://docs.astral.sh/uv/getting-started/installation/)をご覧ください。
-   **Google Cloud CLIツール**: gcloudコマンドラインインターフェース。インストール詳細は[Google Cloudコマンドラインインターフェース](https://cloud.google.com/sdk/docs/install)をご覧ください。
-   **Makeツール**: ビルド自動化ツール。このツールはほとんどのUnixベースのシステムに含まれています。インストール詳細は[Makeツール](https://www.gnu.org/software/make/)のドキュメントをご覧ください。

### ADKプロジェクトの準備 {#prepare-ad}

ADKプロジェクトをAgent Engineにデプロイする際には、デプロイ操作をサポートするための追加ファイルが必要です。次のASPコマンドは、プロジェクトをバックアップし、デプロイ目的のファイルをプロジェクトに追加します。

この手順は、デプロイのために変更する既存のADKプロジェクトがあることを前提としています。ADKプロジェクトがない場合やテストプロジェクトを使用したい場合は、Pythonの[クイックスタート](/adk-docs/ja/get-started/quickstart/)ガイドを完了し、[multi_tool_agent](https://github.com/google/adk-docs/tree/main/examples/python/snippets/get-started/multi_tool_agent)プロジェクトを作成してください。以下の手順では、`multi_tool_agent`プロジェクトを例として使用します。

ADKプロジェクトをAgent Engineへのデプロイ準備をするには：

1.  開発環境のターミナルウィンドウで、エージェントフォルダを含む**親ディレクトリ**に移動します。例えば、プロジェクト構造が以下のようになっている場合：

    ```
    your-project-directory/
    ├── multi_tool_agent/
    │   ├── __init__.py
    │   ├── agent.py
    │   └── .env
    ```

    `your-project-directory/`に移動します。

2.  ASPの`enhance`コマンドを実行して、デプロイに必要なファイル群をプロジェクトに追加します。

    ```shell
    uvx agent-starter-pack enhance --adk -d agent_engine
    ```

3.  ASPツールの指示に従います。通常はすべての質問にデフォルトの回答で問題ありません。ただし、**GCPリージョン**のオプションについては、[Agent Engineがサポートするリージョン](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview#supported-regions)のいずれかを選択してください。

このプロセスが正常に完了すると、ツールは次のメッセージを表示します。

```
> Success! Your agent project is ready.
```

!!! tip "注"
    実行中にASPツールがGoogle Cloudへの接続を促すメッセージを表示することがありますが、この段階での接続は*必須ではありません*。

ASPがADKプロジェクトに加える変更についての詳細は、[ADKプロジェクトへの変更点](#adk-asp-changes)をご覧ください。

### Google Cloudプロジェクトへの接続 {#connect-ad}

ADKプロジェクトをデプロイする前に、Google Cloudおよびご自身のプロジェクトに接続する必要があります。Google Cloudアカウントにログインした後、デプロイ対象のプロジェクトがアカウントから見えること、およびそれが現在のプロジェクトとして設定されていることを確認してください。

Google Cloudに接続し、プロジェクトをリスト表示するには：

1.  開発環境のターミナルウィンドウで、Google Cloudアカウントにログインします。

    ```shell
    gcloud auth application-default login
    ```

2.  Google CloudプロジェクトIDを使用して対象プロジェクトを設定します。

    ```shell
    gcloud config set project your-project-id-xxxxx
    ```

3.  Google Cloudの対象プロジェクトが設定されていることを確認します。

    ```shell
    gcloud config get-value project
    ```

Google Cloudへの接続とCloudプロジェクトIDの設定が正常に完了すれば、ADKプロジェクトファイルをAgent Engineにデプロイする準備は完了です。

### ADKプロジェクトのデプロイ {#deploy-ad}

ASPツールを使用する場合、デプロイは段階的に行われます。最初の段階では、`make`コマンドを実行してAgent Engine上でADKワークフローを実行するために必要なサービスをプロビジョニングします。第2段階では、プロジェクトコードがAgent Engineサービスにアップロードされ、エージェントプロジェクトが実行されます。

!!! warning "重要"
    *これらの手順を実行する前に、Google Cloudのデプロイ対象プロジェクトが***現在のプロジェクト***として設定されていることを確認してください*。`make backend`コマンドは、デプロイ実行時に現在設定されているGoogle Cloudプロジェクトを使用します。現在のプロジェクトの設定と確認については、[Google Cloudプロジェクトへの接続](#connect-ad)をご覧ください。

ADKプロジェクトをGoogle CloudプロジェクトのAgent Engineにデプロイするには：

1.  ターミナルウィンドウで、エージェントフォルダを含む親ディレクトリ（例：`your-project-directory/`）にいることを確認します。

2.  以下のASP makeコマンドを実行して、更新されたローカルプロジェクトのコードをGoogle Cloud開発環境にデプロイします。

    ```shell
    make backend
    ```

このプロセスが正常に完了すると、Google Cloud Agent Engine上で実行されているエージェントと対話できるようになります。デプロイされたエージェントのテストに関する詳細は、次のセクションを参照してください。

このプロセスが正常に完了すると、Google Cloud Agent Engine上で実行されているエージェントと対話できるようになります。デプロイされたエージェントのテストに関する詳細は、[デプロイされたエージェントのテスト](#test-deployment)をご覧ください。

### ADKプロジェクトへの変更点 {#adk-asp-changes}

ASPツールは、デプロイのためにプロジェクトにさらにファイルを追加します。下記の手順では、変更前に既存のプロジェクトファイルをバックアップします。このガイドでは、[multi_tool_agent](https://github.com/google/adk-docs/tree/main/examples/python/snippets/get-started/multi_tool_agent)プロジェクトを参照例として使用します。元のプロジェクトは、以下のファイル構造から始まります。

```
multi_tool_agent/
├─ __init__.py
├─ agent.py
└─ .env
```

Agent Engineのデプロイ情報を追加するためにASP enhanceコマンドを実行した後の新しい構造は以下の通りです。

```
multi-tool-agent/
├─ app/                 # コアアプリケーションコード
│   ├─ agent.py         # メインのエージェントロジック
│   ├─ agent_engine_app.py # Agent Engineアプリケーションロジック
│   └─ utils/           # ユーティリティ関数とヘルパー
├─ .cloudbuild/         # Google Cloud Build用のCI/CDパイプライン設定
├─ deployment/          # インフラとデプロイスクリプト
├─ notebooks/           # プロトタイピングと評価用のJupyterノートブック
├─ tests/               # ユニット、インテグレーション、負荷テスト
├─ Makefile             # 共通コマンド用のMakefile
├─ GEMINI.md            # AI支援開発ガイド
└─ pyproject.toml       # プロジェクトの依存関係と設定
```

詳細については、更新されたADKプロジェクトフォルダ内のREADME.mdファイルをご覧ください。Agent Starter Packの使用に関する詳細については、[開発ガイド](https://googlecloudplatform.github.io/agent-starter-pack/guide/development-guide.html)をご覧ください。

## 標準デプロイ

このセクションでは、Agent Engineへのデプロイをステップバイステップで実行する方法について説明します。これらの手順は、デプロイ設定を慎重に管理したい場合や、Agent Engineで既存のデプロイを変更する場合に適しています。

### 前提条件

この手順は、ADKプロジェクトとGCPプロジェクトが既に定義されていることを前提としています。ADKプロジェクトがない場合は、[エージェントの定義](#define-your-agent)のテストプロジェクト作成手順を参照してください。

!!! example "プレビュー: Vertex AI Express モード"
    既存のGCPプロジェクトがない場合、[Vertex AI Express モード](https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview)を使用してAgent Engineを無料でお試しいただけます。

=== "Google Cloudプロジェクト"

    デプロイ手順を開始する前に、以下が揃っていることを確認してください。
    
    1.  **Google Cloudプロジェクト**: [Vertex AI APIが有効化](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com)されたGoogle Cloudプロジェクト。
    
    2.  **認証済みのgcloud CLI**: Google Cloudで認証されている必要があります。ターミナルで次のコマンドを実行してください。
        ```shell
        gcloud auth application-default login
        ```
    
    3.  **Google Cloud Storage (GCS) バケット**: Agent Engineは、デプロイのためにエージェントのコードと依存関係をステージングするGCSバケットを必要とします。バケットがない場合は、[こちら](https://cloud.google.com/storage/docs/creating-buckets)の手順に従って作成してください。
    
    4.  **Python環境**: 3.9から3.13までのPythonバージョン。
    
    5.  **Vertex AI SDKのインストール**
    
        Agent EngineはPython用Vertex AI SDKの一部です。詳細については、[Agent Engineクイックスタートドキュメント](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/quickstart)を参照できます。
    
        ```shell
        pip install google-cloud-aiplatform[adk,agent_engines]>=1.111
        ```

=== "Vertex AI Express モード"

    デプロイ手順を開始する前に、以下が揃っていることを確認してください。
    
    1.  **ExpressモードプロジェクトのAPIキー**: [Expressモードのサインアップ](https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview#eligibility)に従って、gmailアカウントでExpressモードプロジェクトにサインアップします。そのプロジェクトからAgent Engineで使用するAPIキーを取得してください！
    
    2.  **Python環境**: 3.9から3.13までのPythonバージョン。
    
    3.  **Vertex AI SDKのインストール**
    
        Agent EngineはPython用Vertex AI SDKの一部です。詳細については、[Agent Engineクイックスタートドキュメント](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/quickstart)を参照できます。
    
        ```shell
        pip install google-cloud-aiplatform[adk,agent_engines]>=1.111
        ```

### エージェントの定義 {#define-your-agent}

この手順は、デプロイのために変更する既存のADKプロジェクトがあることを前提としています。ADKプロジェクトがない場合やテストプロジェクトを使用したい場合は、Pythonの[クイックスタート](/adk-docs/ja/get-started/quickstart/)ガイドを完了し、[multi_tool_agent](https://github.com/google/adk-docs/tree/main/examples/python/snippets/get-started/multi_tool_agent)プロジェクトを作成してください。以下の手順では、`multi_tool_agent`プロジェクトを例として使用します。

### Vertex AIの初期化

次に、Vertex AI SDKを初期化します。これにより、SDKに使用するGoogle Cloudプロジェクトとリージョン、およびデプロイ用ファイルのステージング場所が指定されます。

!!! tip "IDEユーザー向けヒント"
    この初期化コードは、次のステップ3から6のデプロイロジックと一緒に、別の`deploy.py`スクリプトに配置することができます。

=== "Google Cloudプロジェクト"

    ```python title="deploy.py"
    import vertexai
    from agent import root_agent # agent.pyにエージェントがない場合は変更してください
    
    # TODO: プロジェクトに合わせてこれらの値を入力してください
    PROJECT_ID = "your-gcp-project-id"
    LOCATION = "us-central1"  # 他のオプションについては https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview#supported-regions を参照
    STAGING_BUCKET = "gs://your-gcs-bucket-name"
    
    # Vertex AI SDKを初期化
    vertexai.init(
        project=PROJECT_ID,
        location=LOCATION,
        staging_bucket=STAGING_BUCKET,
    )
    ```

=== "Vertex AI Express モード"

    ```python title="deploy.py"
    import vertexai
    from agent import root_agent # agent.pyにエージェントがない場合は変更してください
    
    # TODO: APIキーに合わせてこの値を入力してください
    API_KEY = "your-express-mode-api-key"
    
    # Vertex AI SDKを初期化
    vertexai.init(
        api_key=API_KEY,
    )
    ```


### デプロイのためのエージェント準備

エージェントをAgent Engineと互換性のあるものにするには、`AdkApp`オブジェクトでラップする必要があります。

```python title="deploy.py"
from vertexai import agent_engines

# エージェントをAdkAppオブジェクトでラップ
app = agent_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
)
```

!!!info
    AdkAppがAgent Engineにデプロイされると、永続的でマネージドなセッション状態のために自動的に`VertexAiSessionService`を使用します。これにより、追加の設定なしでマルチターンの対話メモリが提供されます。ローカルでのテストでは、アプリケーションはデフォルトで一時的なインメモリのセッションサービスを使用します。

### エージェントのローカルテスト (任意)

デプロイする前に、エージェントの振る舞いをローカルでテストできます。

`async_stream_query`メソッドは、エージェントの実行トレースを表すイベントのストリームを返します。

```python title="deploy.py"
# 対話履歴を維持するためのローカルセッションを作成
session = await app.async_create_session(user_id="u_123")
print(session)
```

`create_session`の期待される出力 (ローカル):

```console
Session(id='c6a33dae-26ef-410c-9135-b434a528291f', app_name='default-app-name', user_id='u_123', state={}, events=[], last_update_time=1743440392.8689594)
```

エージェントにクエリを送信します。以下のコードを"deploy.py"Pythonスクリプトまたはノートブックにコピー＆ペーストしてください。

```py title="deploy.py"
events = []
async for event in app.async_stream_query(
    user_id="u_123",
    session_id=session.id,
    message="whats the weather in new york",
):
    events.append(event)

# 完全なイベントストリームはエージェントの思考プロセスを示します
print("--- Full Event Stream ---")
for event in events:
    print(event)

# 簡単なテストでは、最終的なテキスト応答だけを抽出できます
final_text_responses = [
    e for e in events
    if e.get("content", {}).get("parts", [{}])[0].get("text")
    and not e.get("content", {}).get("parts", [{}])[0].get("function_call")
]
if final_text_responses:
    print("\n--- Final Response ---")
    print(final_text_responses[0]["content"]["parts"][0]["text"])
```

#### 出力の理解

上記のコードを実行すると、いくつかのタイプのイベントが表示されます。

*   **ツール呼び出しイベント**: モデルがツール（例: `get_weather`）の呼び出しを要求します。
*   **ツール応答イベント**: システムがツール呼び出しの結果をモデルに返します。
*   **モデル応答イベント**: エージェントがツール結果を処理した後の最終的なテキスト応答。

`async_stream_query`の期待される出力 (ローカル):

```console
{'parts': [{'function_call': {'id': 'af-a33fedb0-29e6-4d0c-9eb3-00c402969395', 'args': {'city': 'new york'}, 'name': 'get_weather'}}], 'role': 'model'}
{'parts': [{'function_response': {'id': 'af-a33fedb0-29e6-4d0c-9eb3-00c402969395', 'name': 'get_weather', 'response': {'status': 'success', 'report': 'The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).'}}}], 'role': 'user'}
{'parts': [{'text': 'The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).'}], 'role': 'model'}
```

### Agent Engineへのデプロイ

エージェントのローカルでの振る舞いに満足したら、デプロイできます。これはPython SDKまたは`adk`コマンドラインツールを使用して行うことができます。

このプロセスは、コードをパッケージ化し、コンテナにビルドし、マネージドなAgent Engineサービスにデプロイします。このプロセスには数分かかることがあります。

=== "ADK CLI"

    ターミナルから`adk deploy`コマンドラインツールを使用してデプロイできます。
    以下のデプロイコマンド例では、`multi_tool_agent`サンプルコードをデプロイ対象のプロジェクトとして使用します。

    ```shell
    adk deploy agent_engine \
        --project=my-cloud-project-xxxxx \
        --region=us-central1 \
        --staging_bucket=gs://my-cloud-project-staging-bucket-name \
        --display_name="My Agent Name" \
        /multi_tool_agent
    ```

    利用可能なストレージバケット名は、Google Cloudコンソールのデプロイプロジェクトの
    [Cloud Storageバケット](https://pantheon.corp.google.com/storage/browser)
    セクションで確認できます。`adk deploy`コマンドの使用に関する詳細は、
    [ADK CLIリファレンス](/adk-docs/ja/api-reference/cli/cli.html#adk-deploy)をご覧ください。

    !!! tip
        ADKプロジェクトをデプロイする際は、メインのADKエージェント定義(`root_agent`)が
        検出可能であることを確認してください。

=== "Python"

    このコードブロックは、Pythonスクリプトまたはノートブックからデプロイを開始します。

    ```python title="deploy.py"
    from vertexai import agent_engines

    remote_app = agent_engines.create(
        agent_engine=app,
        requirements=[
            "google-cloud-aiplatform[adk,agent_engines]"   
        ]
    )

    print(f"Deployment finished!")
    print(f"Resource Name: {remote_app.resource_name}")
    # Resource Name: "projects/{PROJECT_NUMBER}/locations/{LOCATION}/reasoningEngines/{RESOURCE_ID}"
    #       注: PROJECT_NUMBERはPROJECT_IDとは異なります。
    ```

=== "Vertex AI Express モード"

    Vertex AI Expressモードは、ADK CLIデプロイとPythonデプロイの両方をサポートしています。

    以下のデプロイコマンド例では、`multi_tool_agent`サンプルコードをExpressモードでデプロイするプロジェクトとして使用します。

    ```shell
    adk deploy agent_engine \
        --display_name="My Agent Name" \
        --api_key=your-api-key-here
        /multi_tool_agent
    ```

    !!! tip
        ADKプロジェクトをデプロイする際は、メインのADKエージェント定義(`root_agent`)が
        検出可能であることを確認してください。

    このコードブロックは、Pythonスクリプトまたはノートブックからデプロイを開始します。

    ```python title="deploy.py"
    from vertexai import agent_engines

    remote_app = agent_engines.create(
        agent_engine=app,
        requirements=[
            "google-cloud-aiplatform[adk,agent_engines]"   
        ]
    )

    print(f"Deployment finished!")
    print(f"Resource Name: {remote_app.resource_name}")
    # Resource Name: "projects/{PROJECT_NUMBER}/locations/{LOCATION}/reasoningEngines/{RESOURCE_ID}"
    #       注: PROJECT_NUMBERはPROJECT_IDとは異なります。
    ```


#### モニタリングと検証

*   Google Cloudコンソールの[Agent Engine UI](https://console.cloud.google.com/vertex-ai/agents/agent-engines)でデプロイ状況をモニタリングできます。
*   `remote_app.resource_name`はデプロイされたエージェントの一意の識別子です。エージェントと対話するために必要になります。この情報はADK CLIコマンドから返されるレスポンスからも取得できます。
*   追加の詳細については、Agent Engineドキュメントの[エージェントのデプロイ](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/deploy)および[デプロイされたエージェントの管理](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/manage/overview)をご覧ください。

## デプロイされたエージェントのテスト {#test-deployment}

エージェントのAgent Engineへのデプロイが完了したら、Google Cloudコンソールを通じてデプロイされたエージェントを表示し、RESTコールまたはPython用Vertex AI SDKを使用してエージェントと対話できます。

Cloudコンソールでデプロイされたエージェントを表示するには：

-   Google CloudコンソールのAgent Engineページに移動します：
    [https://console.cloud.google.com/vertex-ai/agents/agent-engines](https://console.cloud.google.com/vertex-ai/agents/agent-engines)

このページには、現在選択されているGoogle Cloudプロジェクトにデプロイされているすべてのエージェントが一覧表示されます。エージェントが表示されない場合は、Google Cloudコンソールで対象のプロジェクトが選択されていることを確認してください。既存のGoogle Cloudプロジェクトの選択に関する詳細は、[プロジェクトの作成と管理](https://cloud.google.com/resource-manager/docs/creating-managing-projects#identifying_projects)をご覧ください。

### Google Cloudプロジェクト情報の検索

デプロイをテストするには、プロジェクトのアドレスとリソース識別情報（`PROJECT_ID`, `LOCATION`, `RESOURCE_ID`）が必要です。Cloudコンソールまたは`gcloud`コマンドラインツールを使用してこの情報を見つけることができます。

!!! note "Vertex AI Express モード APIキー"
    Vertex AI Expressモードを使用している場合は、この手順をスキップしてAPIキーを使用できます。

Google Cloudコンソールでプロジェクト情報を見つけるには：

1.  Google Cloudコンソールで、Agent Engineページに移動します：
    [https://console.cloud.google.com/vertex-ai/agents/agent-engines](https://console.cloud.google.com/vertex-ai/agents/agent-engines)

2.  ページの上部で**API URL**を選択し、デプロイされたエージェントの**クエリURL**文字列をコピーします。形式は次のようになります：

        https://$(LOCATION_ID)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION_ID)/reasoningEngines/$(RESOURCE_ID):query

`gloud`でプロジェクト情報を見つけるには：

1.  開発環境で、Google Cloudに認証されていることを確認し、次のコマンドを実行してプロジェクトを一覧表示します：

    ```shell
    gcloud projects list
    ```

2.  デプロイに使用したプロジェクトIDを取得し、このコマンドを実行して追加の詳細情報を取得します：

    ```shell
    gcloud asset search-all-resources \
        --scope=projects/$(PROJECT_ID) \
        --asset-types='aiplatform.googleapis.com/ReasoningEngine' \
        --format="table(name,assetType,location,reasoning_engine_id)"
    ```

### RESTコールを使用したテスト

Agent Engineにデプロイされたエージェントと対話する簡単な方法は、`curl`ツールを使用したRESTコールです。このセクションでは、エージェントへの接続を確認する方法と、デプロイされたエージェントによるリクエストの処理をテストする方法について説明します。

#### エージェントへの接続確認

CloudコンソールのAgent Engineセクションで利用可能な**クエリURL**を使用して、実行中のエージェントへの接続を確認できます。この確認はデプロイされたエージェントを実行するのではなく、エージェントに関する情報を返します。

デプロイされたエージェントからレスポンスを取得するためにRESTコールを送信するには：

-   開発環境のターミナルウィンドウで、リクエストを構築して実行します：

    === "Google Cloudプロジェクト"

        ```shell
        curl -X GET \
            -H "Authorization: Bearer $(gcloud auth print-access-token)" \
            "https://$(LOCATION)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION)/reasoningEngines"
        ```

    === "Vertex AI Express モード"
    
        ```shell
        curl -X GET \
            -H "x-goog-api-key:YOUR-EXPRESS-MODE-API-KEY" \
            "https://aiplatform.googleapis.com/v1/reasoningEngines"
        ```

デプロイが成功した場合、このリクエストは有効なリクエストのリストと期待されるデータ形式で応答します。

!!! tip "エージェント接続のアクセス権"
    この接続テストでは、呼び出し元のユーザーがデプロイされたエージェントの有効なアクセストークンを持っている必要があります。他の環境からテストする場合は、呼び出し元のユーザーがGoogle Cloudプロジェクトのエージェントに接続するアクセス権を持っていることを確認してください。

#### エージェントリクエストの送信

エージェントプロジェクトからレスポンスを取得するには、まずセッションを作成し、セッションIDを受け取ってから、そのセッションIDを使用してリクエストを送信する必要があります。このプロセスは以下の手順で説明します。

RESTを介してデプロイされたエージェントとの対話をテストするには：

1.  開発環境のターミナルウィンドウで、このテンプレートを使用してリクエストを構築し、セッションを作成します：

    === "Google Cloudプロジェクト"

        ```shell
        curl \
            -H "Authorization: Bearer $(gcloud auth print-access-token)" \
            -H "Content-Type: application/json" \
            https://$(LOCATION)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION)/reasoningEngines/$(RESOURCE_ID):query \
            -d '{"class_method": "async_create_session", "input": {"user_id": "u_123"},}'
        ```

    === "Vertex AI Express モード"
    
        ```shell
        curl \
            -H "x-goog-api-key:YOUR-EXPRESS-MODE-API-KEY" \
            -H "Content-Type: application/json" \
            https://aiplatform.googleapis.com/v1/reasoningEngines/$(RESOURCE_ID):query \
            -d '{"class_method": "async_create_session", "input": {"user_id": "u_123"},}'
        ```

2.  前のコマンドのレスポンスで、**id**フィールドから作成された**セッションID**を抽出します：

    ```json
    {
        "output": {
            "userId": "u_123",
            "lastUpdateTime": 1757690426.337745,
            "state": {},
            "id": "4857885913439920384", # セッションID
            "appName": "9888888855577777776",
            "events": []
        }
    }
    ```

3.  開発環境のターミナルウィンドウで、このテンプレートと前のステップで作成したセッションIDを使用してリクエストを構築し、エージェントにメッセージを送信します：

    === "Google Cloudプロジェクト"

        ```shell
        curl \
        -H "Authorization: Bearer $(gcloud auth print-access-token)" \
        -H "Content-Type: application/json" \
        https://$(LOCATION)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION)/reasoningEngines/$(RESOURCE_ID):streamQuery?alt=sse -d '{
        "class_method": "async_stream_query",
        "input": {
            "user_id": "u_123",
            "session_id": "4857885913439920384",
            "message": "Hey whats the weather in new york today?",
        }
        }'
        ```

    === "Vertex AI Express モード"

        ```shell
        curl \
        -H "x-goog-api-key:YOUR-EXPRESS-MODE-API-KEY" \
        -H "Content-Type: application/json" \
        https://aiplatform.googleapis.com/v1/reasoningEngines/$(RESOURCE_ID):streamQuery?alt=sse -d '{
        "class_method": "async_stream_query",
        "input": {
            "user_id": "u_123",
            "session_id": "4857885913439920384",
            "message": "Hey whats the weather in new york today?",
        }
        }'
        ```

このリクエストは、デプロイされたエージェントコードからJSON形式のレスポンスを生成するはずです。RESTコールを使用してAgent EngineにデプロイされたADKエージェントと対話する方法の詳細については、Agent Engineドキュメントの[デプロイされたエージェントの管理](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/manage/overview#console)および[Agent Development Kitエージェントの使用](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/use/adk)をご覧ください。

### Pythonを使用したテスト

Agent Engineにデプロイされたエージェントをより洗練された、再現可能な方法でテストするためにPythonコードを使用できます。この手順では、デプロイされたエージェントとのセッションを作成し、処理のためにエージェントにリクエストを送信する方法を説明します。

#### リモートセッションの作成

`remote_app`オブジェクトを使用して、デプロイされたリモートエージェントへの接続を作成します。

```py
# 新しいスクリプトにいる場合やADK CLIを使用してデプロイした場合は、次のように接続できます：
# remote_app = agent_engines.get("your-agent-resource-name")
remote_session = await remote_app.async_create_session(user_id="u_456")
print(remote_session)
```

`create_session`の期待される出力 (リモート):

```console
{'events': [],
'user_id': 'u_456',
'state': {},
'id': '7543472750996750336',
'app_name': '7917477678498709504',
'last_update_time': 1743683353.030133}
```

`id`の値はセッションIDで、`app_name`はAgent EngineにデプロイされたエージェントのリソースIDです。

#### リモートエージェントへのクエリ送信

```py
async for event in remote_app.async_stream_query(
    user_id="u_456",
    session_id=remote_session["id"],
    message="whats the weather in new york",
):
    print(event)
```

`async_stream_query`の期待される出力 (リモート):

```console
{'parts': [{'function_call': {'id': 'af-f1906423-a531-4ecf-a1ef-723b05e85321', 'args': {'city': 'new york'}, 'name': 'get_weather'}}], 'role': 'model'}
{'parts': [{'function_response': {'id': 'af-f1906423-a531-4ecf-a1ef-723b05e85321', 'name': 'get_weather', 'response': {'status': 'success', 'report': 'The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).'}}}], 'role': 'user'}
{'parts': [{'text': 'The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).'}], 'role': 'model'}
```

Agent EngineにデプロイされたADKエージェントとの対話に関する詳細については、Agent Engineドキュメントの[デプロイされたエージェントの管理](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/manage/overview)および[Agent Development Kitエージェントの使用](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/use/adk)をご覧ください。

#### マルチモーダルクエリの送信

エージェントにマルチモーダルクエリ（例：画像を含む）を送信するには、`async_stream_query`の`message`パラメータを`types.Part`オブジェクトのリストで構築します。各パートはテキストまたは画像にすることができます。

画像を含めるには、画像のGoogle Cloud Storage (GCS) URIを提供して`types.Part.from_uri`を使用できます。

```python
from google.genai import types

image_part = types.Part.from_uri(
    file_uri="gs://cloud-samples-data/generative-ai/image/scones.jpg",
    mime_type="image/jpeg",
)
text_part = types.Part.from_text(
    text="What is in this image?",
)

async for event in remote_app.async_stream_query(
    user_id="u_456",
    session_id=remote_session["id"],
    message=[text_part, image_part],
):
    print(event)
```

!!!note 
    モデルとの基盤となる通信では画像のBase64エンコーディングが関与する場合がありますが、Agent Engineにデプロイされたエージェントに画像データを送信するための推奨およびサポートされている方法は、GCS URIを提供することです。

## デプロイペイロード {#payload}

ADKエージェントプロジェクトをAgent Engineにデプロイすると、以下のコンテンツがサービスにアップロードされます。

- ADKエージェントのコード
- ADKエージェントのコードで宣言されているすべての依存関係

デプロイには、ADK APIサーバーやADKウェブユーザーインターフェースライブラリは含まれ*ません*。Agent EngineサービスがADK APIサーバー機能のためのライブラリを提供します。

## デプロイのクリーンアップ

テストとしてデプロイを実行した場合、終了後にクラウドリソースをクリーンアップすることをお勧めします。Google Cloudアカウントに予期せぬ請求が発生するのを避けるために、デプロイされたAgent Engineインスタンスを削除できます。

```python
remote_app.delete(force=True)
```

`force=True`パラメータは、セッションなど、デプロイされたエージェントから生成されたすべての子リソースも削除します。Google Cloudの[Agent Engine UI](https://console.cloud.google.com/vertex-ai/agents/agent-engines)を介してデプロイされたエージェントを削除することもできます。