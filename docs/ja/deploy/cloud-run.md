# Cloud Runへのデプロイ

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span><span class="lst-go">Go</span><span class="lst-java">Java</span>
</div>

[Cloud Run](https://cloud.google.com/run)は、Googleのスケーラブルなインフラストラクチャ上でコードを直接実行できる、フルマネージドプラットフォームです。

エージェントをデプロイするには、`adk deploy cloud_run`コマンド (_Pythonに推奨_) またはCloud Run経由で`gcloud run deploy`コマンドを使用できます。

## エージェントのサンプル

各コマンドについて、[LLMエージェント](../agents/llm-agents.md)ページで定義されている`Capital Agent`サンプルを参照します。これはディレクトリ (例: `capital_agent`) にあると仮定します。

続行するには、エージェントコードが次のように構成されていることを確認してください。

=== "Python"

    1. エージェントコードは、エージェントディレクトリ内の`agent.py`というファイルにあります。
    2. エージェント変数は`root_agent`という名前です。
    3. `__init__.py`はエージェントディレクトリ内にあり、`from . import agent`を含んでいます。
    4. `requirements.txt`ファイルはエージェントディレクトリにあります。

=== "Go"

    1. アプリケーションのエントリポイント (メインパッケージとmain()関数) は単一のGoファイルにあります。main.goを使用することは強力な慣習です。
    2. エージェントインスタンスはランチャー構成に渡され、通常はagent.NewSingleLoader(yourAgent)を使用します。adkgoツールは、このランチャーを使用して、正しいサービスでエージェントを起動します。
    3. go.modおよびgo.sumファイルは、依存関係を管理するためにプロジェクトディレクトリにあります。

    詳細については、次のセクションを参照してください。GitHubリポジトリで[サンプルアプリ](https://github.com/google/adk-docs/tree/main/examples/go/cloud-run)も参照できます。

=== "Java"

    1. エージェントコードは、エージェントディレクトリ内の`CapitalAgent.java`というファイルにあります。
    2. エージェント変数はグローバルで、`public static final BaseAgent ROOT_AGENT`形式に従います。
    3. エージェント定義は静的クラスメソッドにあります。

    詳細については、次のセクションを参照してください。GitHubリポジトリで[サンプルアプリ](https://github.com/google/adk-docs/tree/main/examples/java/cloud-run)も参照できます。


## 環境変数

[セットアップとインストール](../get-started/installation.md)ガイドで説明されているように、環境変数を設定します。

```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1 # または任意の場所
export GOOGLE_GENAI_USE_VERTEXAI=True
```

_(`your-project-id`を実際のGCPプロジェクトIDに置き換えます)_

または、AI StudioのAPIキーを使用することもできます

```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1 # または任意の場所
export GOOGLE_GENAI_USE_VERTEXAI=FALSE
export GOOGLE_API_KEY=your-api-key
```
*( `your-project-id`を実際のGCPプロジェクトIDに、`your-api-key`をAI Studioの実際のAPIキーに置き換えます)*

## 前提条件

1. Google Cloudプロジェクトが必要です。次の情報を知っている必要があります。
    1. プロジェクト名 (例: "my-project")
    1. プロジェクトの場所 (例: "us-central1")
    1. サービスアカウント (例: "1234567890-compute@developer.gserviceaccount.com")
    1. GOOGLE_API_KEY

## シークレット

サービスアカウントが読み取れるシークレットを作成したことを確認してください。

### GOOGLE_API_KEYシークレットのエントリ

シークレットを手動で作成するか、CLIを使用できます。
```bash
echo "<<ここにGOOGLE_API_KEYを挿入>>" | gcloud secrets create GOOGLE_API_KEY --project=my-project --data-file=-
```

### 読み取り権限
サービスアカウントにこのシークレットを読み取るための適切な権限を付与する必要があります。
```bash
gcloud secrets add-iam-policy-binding GOOGLE_API_KEY --member="serviceAccount:1234567890-compute@developer.gserviceaccount.com" --role="roles/secretmanager.secretAccessor" --project=my-project
```

## デプロイペイロード {#payload}

ADKエージェントワークフローをGoogle Cloud Runにデプロイすると、次のコンテンツがサービスにアップロードされます。

- ADKエージェントコード
- ADKエージェントコードで宣言されているすべての依存関係
- エージェントが使用するADK APIサーバーコードバージョン

デフォルトのデプロイには、`adk deploy cloud_run`コマンドの`--with_ui`オプションなどのデプロイ設定で指定しない限り、ADKウェブユーザーインターフェースライブラリは含まれません。

## デプロイコマンド

=== "Python - adk CLI"

    ### adk CLI

    `adk deploy cloud_run`コマンドは、エージェントコードをGoogle Cloud Runにデプロイします。

    Google Cloudで認証されていることを確認してください (`gcloud auth login` および `gcloud config set project <your-project-id>`)。

    #### 環境変数の設定

    オプションですが推奨: 環境変数を設定すると、デプロイコマンドがより簡潔になります。

    ```bash
    # Google CloudプロジェクトIDを設定
    export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"

    # 希望のGoogle Cloudロケーションを設定
    export GOOGLE_CLOUD_LOCATION="us-central1" # 例のロケーション

    # エージェントコードディレクトリへのパスを設定
    export AGENT_PATH="./capital_agent" # capital_agentが現在のディレクトリにあると仮定

    # Cloud Runサービスの名称を設定 (オプション)
    export SERVICE_NAME="capital-agent-service"

    # アプリケーション名を指定 (オプション)
    export APP_NAME="capital-agent-app"
    ```

    #### コマンドの使用法

    ##### 最小限のコマンド

    ```bash
    adk deploy cloud_run \
    --project=$GOOGLE_CLOUD_PROJECT \
    --region=$GOOGLE_CLOUD_LOCATION \
    $AGENT_PATH
    ```

    ##### オプションのフラグ付きの完全なコマンド

    ```bash
    adk deploy cloud_run \
    --project=$GOOGLE_CLOUD_PROJECT \
    --region=$GOOGLE_CLOUD_LOCATION \
    --service_name=$SERVICE_NAME \
    --app_name=$APP_NAME \
    --with_ui \
    $AGENT_PATH
    ```

    ##### 引数

    * `AGENT_PATH`: (必須) エージェントのソースコードを含むディレクトリへのパスを指定する位置引数 (例: 例の`$AGENT_PATH`、または`capital_agent/`)。このディレクトリには、少なくとも`__init__.py`とメインエージェントファイル (例: `agent.py`) が含まれている必要があります。

    ##### オプション

    * `--project TEXT`: (必須) Google CloudプロジェクトID (例: `$GOOGLE_CLOUD_PROJECT`)。
    * `--region TEXT`: (必須) デプロイするGoogle Cloudのロケーション (例: `$GOOGLE_CLOUD_LOCATION`、`us-central1`)。
    * `--service_name TEXT`: (オプション) Cloud Runサービスの名前 (例: `$SERVICE_NAME`)。デフォルトは`adk-default-service-name`です。
    * `--app_name TEXT`: (オプション) ADK APIサーバーのアプリケーション名 (例: `$APP_NAME`)。デフォルトは`AGENT_PATH`で指定されたディレクトリの名前 (例: `AGENT_PATH`が`./capital_agent`の場合`capital_agent`) です。
    * `--agent_engine_id TEXT`: (オプション) Vertex AI Agent Engineを介して管理セッションサービスを使用している場合、ここにそのリソースIDを指定します。
    * `--port INTEGER`: (オプション) ADK APIサーバーがコンテナ内でリッスンするポート番号。デフォルトは8000です。
    * `--with_ui`: (オプション) 含めると、ADK開発UIがエージェントAPIサーバーとともにデプロイされます。デフォルトでは、APIサーバーのみがデプロイされます。
    * `--temp_folder TEXT`: (オプション) デプロイプロセス中に生成される中間ファイルを保存するディレクトリを指定します。デフォルトは、システムの一時ディレクトリ内のタイムスタンプ付きフォルダです。*(注: このオプションは、問題のトラブルシューティングが必要な場合を除き、通常は必要ありません。)*
    * `--help`: ヘルプメッセージを表示して終了します。

    ##### 認証アクセス
    デプロイプロセス中に、「[your-service-name]への未認証呼び出しを許可しますか (y/N)?」というプロンプトが表示される場合があります。

    * 認証なしでエージェントのAPIエンドポイントへの公開アクセスを許可するには`y`を入力します。
    * 認証を要求するには`N`を入力します (またはデフォルトの場合はEnterを押します)。(例: 「エージェントのテスト」セクションで示すように、IDトークンを使用します)。

    正常に実行されると、コマンドはエージェントをCloud Runにデプロイし、デプロイされたサービスのURLを提供します。

=== "Python - gcloud CLI"

    ### Python用gcloud CLI

    代わりに、標準の`gcloud run deploy`コマンドを`Dockerfile`とともに使用してデプロイできます。この方法は`adk`コマンドと比較してより手動でのセットアップが必要ですが、特にエージェントをカスタムの[FastAPI](https://fastapi.tiangolo.com/)アプリケーションに埋め込みたい場合に柔軟性を提供します。

    Google Cloudで認証されていることを確認してください (`gcloud auth login` および `gcloud config set project <your-project-id>`)。

    #### プロジェクト構造

    プロジェクトファイルを次のように整理します。

    ```txt
    your-project-directory/
    ├── capital_agent/
    │   ├── __init__.py
    │   └── agent.py       # エージェントコード (「エージェントのサンプル」タブを参照)
    ├── main.py            # FastAPIアプリケーションのエントリポイント
    ├── requirements.txt   # Pythonの依存関係
    └── Dockerfile         # コンテナのビルド指示
    ```

    `your-project-directory/`のルートに次のファイル (`main.py`、`requirements.txt`、`Dockerfile`) を作成します。

    #### コードファイル

    1. このファイルは、ADKの`get_fast_api_app()`を使用してFastAPIアプリケーションをセットアップします。

        ```python title="main.py"
        import os

        import uvicorn
        from fastapi import FastAPI
        from google.adk.cli.fast_api import get_fast_api_app

        # main.pyが存在するディレクトリを取得
        AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
        # セッションサービスURIの例 (例: SQLite)
        SESSION_SERVICE_URI = "sqlite:///./sessions.db"
        # CORSの許可されたオリジンの例
        ALLOWED_ORIGINS = ["http://localhost", "http://localhost:8080", "*"]
        # ウェブインターフェースを提供する場合はweb=True、それ以外の場合はFalseに設定
        SERVE_WEB_INTERFACE = True

        # FastAPIアプリインスタンスを取得する関数を呼び出す
        # エージェントディレクトリ名 ('capital_agent') がエージェントフォルダと一致していることを確認してください
        app: FastAPI = get_fast_api_app(
            agents_dir=AGENT_DIR,
            session_service_uri=SESSION_SERVICE_URI,
            allow_origins=ALLOWED_ORIGINS,
            web=SERVE_WEB_INTERFACE,
        )

        # 必要に応じて、さらにFastAPIルートや設定を追加できます
        # 例:
        # @app.get("/hello")
        # async def read_root():
        #     return {"Hello": "World"}

        if __name__ == "__main__":
            # Cloud Runが提供するPORT環境変数を使用し、デフォルトは8080
            uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
        ```

        *注: `agent_dir`を`main.py`が存在するディレクトリに指定し、Cloud Runの互換性のために`os.environ.get("PORT", 8080)`を使用します。*

    2. 必要なPythonパッケージをリストします。

        ```txt title="requirements.txt"
google-adk
# エージェントに必要なその他の依存関係を追加してください
```

    3. コンテナイメージを定義します。

        ```dockerfile title="Dockerfile"
        FROM python:3.13-slim
        WORKDIR /app

        COPY requirements.txt .
        RUN pip install --no-cache-dir -r requirements.txt

        RUN adduser --disabled-password --gecos "" myuser && \
            chown -R myuser:myuser /app

        COPY . .

        USER myuser

        ENV PATH="/home/myuser/.local/bin:$PATH"

        CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
        ```

    #### 複数のエージェントの定義

    `your-project-directory/`のルートに個別のフォルダを作成することで、同じCloud Runインスタンス内で複数のエージェントを定義およびデプロイできます。各フォルダは1つのエージェントを表し、その構成に`root_agent`を定義する必要があります。

    例の構造:

    ```txt
    your-project-directory/
    ├── capital_agent/
    │   ├── __init__.py
    │   └── agent.py       # `root_agent`の定義を含む
    ├── population_agent/
    │   ├── __init__.py
    │   └── agent.py       # `root_agent`の定義を含む
    └── ...
    ```

    #### `gcloud`を使用したデプロイ

    ターミナルで`your-project-directory`に移動します。

    ```bash
    gcloud run deploy capital-agent-service \
    --source . \
    --region $GOOGLE_CLOUD_LOCATION \
    --project $GOOGLE_CLOUD_PROJECT \
    --allow-unauthenticated \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION,GOOGLE_GENAI_USE_VERTEXAI=$GOOGLE_GENAI_USE_VERTEXAI"
    # エージェントに必要なその他の環境変数を追加してください
    ```

    * `capital-agent-service`: Cloud Runサービスに与えたい名前です。
    * `--source .`: 現在のディレクトリのDockerfileからコンテナイメージをビルドするようにgcloudに指示します。
    * `--region`: デプロイリージョンを指定します。
    * `--project`: GCPプロジェクトを指定します。
    * `--allow-unauthenticated`: サービスへの公開アクセスを許可します。プライベートサービスの場合はこのフラグを削除します。
    * `--set-env-vars`: 実行中のコンテナに必要な環境変数を渡します。ADKとエージェントに必要なすべての変数 (Application Default Credentialsを使用しない場合のAPIキーなど) を含めるようにしてください。

    `gcloud`はDockerイメージをビルドし、Google Artifact Registryにプッシュし、Cloud Runにデプロイします。完了すると、デプロイされたサービスのURLが出力されます。

    デプロイオプションの完全なリストについては、[`gcloud run deploy`リファレンスドキュメント](https://cloud.google.com/sdk/gcloud/reference/run/deploy)を参照してください。

=== "Go - adkgo CLI"

    ### adk CLI

    adkgoコマンドは、google/adk-goリポジトリのcmd/adkgoの下にあります。使用する前に、adk-goリポジトリのルートからビルドする必要があります。

    `go build ./cmd/adkgo`

    adkgo deploy cloudrunコマンドは、アプリケーションのデプロイを自動化します。独自のDockerfileを提供する必要はありません。

    #### エージェントコード構造

    adkgoツールを使用する場合、main.goファイルはランチャーフレームワークを使用する必要があります。これは、ツールがコードをコンパイルし、結果の実行ファイルを特定のコマンドライン引数 (web、api、a2aなど) で実行して必要なサービスを開始するためです。ランチャーは、これらの引数を正しく解析するように設計されています。

    main.goは次のようになります。

    ```go title="main.go"
    --8<-- "examples/go/cloud-run/main.go"
    ```

    #### 動作原理
    1. adkgoツールは、main.goをLinux用の静的にリンクされたバイナリにコンパイルします。
    2. このバイナリを最小限のコンテナにコピーするDockerfileを生成します。
    3. gcloudを使用して、このコンテナをビルドし、Cloud Runにデプロイします。
    4. デプロイ後、新しいサービスに安全に接続するローカルプロキシを開始します。

    Google Cloudで認証されていることを確認してください (`gcloud auth login` および `gcloud config set project <your-project-id>`)。

    #### 環境変数の設定

    オプションですが推奨: 環境変数を設定すると、デプロイコマンドがより簡潔になります。

    ```bash
    # Google CloudプロジェクトIDを設定
    export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"

    # 希望のGoogle Cloudロケーションを設定
    export GOOGLE_CLOUD_LOCATION="us-central1"

    # エージェントのメインGoファイルへのパスを設定
    export AGENT_PATH="./examples/go/cloud-run/main.go"

    # Cloud Runサービスの名前を設定
    export SERVICE_NAME="capital-agent-service"
    ```

    #### コマンドの使用法

    ```bash
    ./adkgo deploy cloudrun \
        -p $GOOGLE_CLOUD_PROJECT \
        -r $GOOGLE_CLOUD_LOCATION \
        -s $SERVICE_NAME \
        --proxy_port=8081 \
        --server_port=8080 \
        -e $AGENT_PATH \
        --a2a --api --webui
    ```

    ##### 必須

    * `-p, --project_name`: Google CloudプロジェクトID (例: $GOOGLE_CLOUD_PROJECT)。
    * `-r, --region`: デプロイするGoogle Cloudのロケーション (例: $GOOGLE_CLOUD_LOCATION、us-central1)。
    * `-s, --service_name`: Cloud Runサービスの名前 (例: $SERVICE_NAME)。
    * `-e, --entry_point_path`: エージェントのソースコードを含むメインGoファイルへのパス (例: $AGENT_PATH)。

    ##### オプション

    * `--proxy_port`: 認証プロキシがリッスンするローカルポート。デフォルトは8081です。
    * `--server_port`: Cloud Runコンテナ内でサーバーがリッスンするポート番号。デフォルトは8080です。
    * `--a2a`: 含めると、Agent2Agent通信が有効になります。デフォルトで有効です。
    * `--a2a_agent_url`: 公開エージェントカードで宣伝されているA2AエージェントカードURL。このフラグは`--a2a`フラグと一緒に使用する場合にのみ有効です。
    * `--api`: 含めると、ADK APIサーバーがデプロイされます。デフォルトで有効です。
    * `--webui`: 含めると、ADK開発UIがエージェントAPIサーバーとともにデプロイされます。デフォルトで有効です。
    * `--temp_dir`: ビルド成果物用の一時ディレクトリ。デフォルトはos.TempDir()です。
    * `--help`: ヘルプメッセージを表示して終了します。

    ##### 認証アクセス
    サービスはデフォルトで`--no-allow-unauthenticated`でデプロイされます。

    正常に実行されると、コマンドはエージェントをCloud Runにデプロイし、プロキシを介してサービスにアクセスするためのローカルURLを提供します。

=== "Java - gcloud CLI"

    ### Java用gcloud CLI

    標準の`gcloud run deploy`コマンドと`Dockerfile`を使用してJavaエージェントをデプロイできます。これが現在、Google Cloud RunにJavaエージェントをデプロイする推奨方法です。

    Google Cloudで[認証](https://cloud.google.com/docs/authentication/gcloud)されていることを確認してください。
    特に、ターミナルで`gcloud auth login`コマンドと`gcloud config set project <your-project-id>`コマンドを実行してください。

    #### プロジェクト構造

    プロジェクトファイルを次のように整理してください。

    ```txt
    your-project-directory/
    ├── src/
    │   └── main/
    │       └── java/
    │             └── agents/
    │                 ├── capitalagent/
    │                     └── CapitalAgent.java    # エージェントコード
    ├── pom.xml                                    # Java adkおよびadk-devの依存関係
    └── Dockerfile                                 # コンテナのビルド指示
    ```

    プロジェクトディレクトリのルートに`pom.xml`と`Dockerfile`を作成してください。エージェントコードファイル (`CapitalAgent.java`) は、上記のようにディレクトリ内に配置してください。

    #### コードファイル

    1. これがエージェントの定義です。これは[LLMエージェント](../agents/llm-agents.md)に存在するコードと同じですが、2つの注意点があります。

           * エージェントは**グローバルなpublic static final変数**として初期化されます。

           * エージェントの定義は、静的メソッドで公開することも、宣言時にインラインで記述することもできます。

        `CapitalAgent`のコード例は、[examples](https://github.com/google/adk-docs/blob/main/examples/java/cloud-run/src/main/java/agents/capitalagent/CapitalAgent.java)リポジトリを参照してください。

    2. pom.xmlファイルに次の依存関係とプラグインを追加してください。

        ```xml title="pom.xml"
        <dependencies>
          <dependency>
             <groupId>com.google.adk</groupId>
             <artifactId>google-adk</artifactId>
             <version>0.1.0</version>
          </dependency>
          <dependency>
             <groupId>com.google.adk</groupId>
             <artifactId>google-adk-dev</artifactId>
             <version>0.1.0</version>
          </dependency>
        </dependencies>

        <plugin>
          <groupId>org.codehaus.mojo</groupId>
          <artifactId>exec-maven-plugin</artifactId>
          <version>3.2.0</version>
          <configuration>
            <mainClass>com.google.adk.web.AdkWebServer</mainClass>
            <classpathScope>compile</classpathScope>
          </configuration>
        </plugin>
        ```

    3.  コンテナイメージを定義します。

        ```dockerfile title="Dockerfile"
        --8<-- "examples/java/cloud-run/Dockerfile"
        ```

    #### `gcloud`を使用したデプロイ

    ターミナルで`your-project-directory`に移動します。

    ```bash
    gcloud run deploy capital-agent-service \
    --source . \
    --region $GOOGLE_CLOUD_LOCATION \
    --project $GOOGLE_CLOUD_PROJECT \
    --allow-unauthenticated \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION,GOOGLE_GENAI_USE_VERTEXAI=$GOOGLE_GENAI_USE_VERTEXAI"
    # エージェントに必要なその他の環境変数を追加してください
    ```

    * `capital-agent-service`: Cloud Runサービスに与えたい名前です。
    * `--source .`: 現在のディレクトリのDockerfileからコンテナイメージをビルドするようにgcloudに指示します。
    * `--region`: デプロイリージョンを指定します。
    * `--project`: GCPプロジェクトを指定します。
    * `--allow-unauthenticated`: サービスへの公開アクセスを許可します。プライベートサービスの場合はこのフラグを削除します。
    * `--set-env-vars`: 実行中のコンテナに必要な環境変数を渡します。ADKとエージェントに必要なすべての変数 (Application Default Credentialsを使用しない場合のAPIキーなど) を含めるようにしてください。

    `gcloud`はDockerイメージをビルドし、Google Artifact Registryにプッシュし、Cloud Runにデプロイします。完了すると、デプロイされたサービスのURLが出力されます。

    デプロイオプションの完全なリストについては、[`gcloud run deploy`リファレンスドキュメント](https://cloud.google.com/sdk/gcloud/reference/run/deploy)を参照してください。

## エージェントのテスト

エージェントがCloud Runにデプロイされたら、デプロイされたUI (有効な場合) または`curl`などのツールを使用してそのAPIエンドポイントと直接対話できます。デプロイ後に提供されたサービスURLが必要です。

=== "UIテスト"

    ### UIテスト

    UIが有効な状態でエージェントをデプロイした場合:

    *   **adk CLI:** デプロイ時に`--webui`フラグを含めました。
    *   **gcloud CLI:** `main.py`で`SERVE_WEB_INTERFACE = True`を設定しました。

    デプロイ後に提供されたCloud RunサービスURLをウェブブラウザで開くだけで、エージェントをテストできます。

    ```bash
    # 例のURL形式
    # https://your-service-name-abc123xyz.a.run.app
    ```

    ADK開発UIを使用すると、エージェントと対話したり、セッションを管理したり、実行の詳細をブラウザで直接確認したりできます。

    エージェントが意図どおりに動作していることを確認するには、次の操作を行います。

    1. ドロップダウンメニューからエージェントを選択します。
    2. メッセージを入力し、エージェントから期待される応答を受信することを確認します。

    予期しない動作が発生した場合は、[Cloud Run](https://console.cloud.google.com/run)コンソールログを確認してください。

=== "APIテスト (curl)"

    ### APIテスト (curl)

    `curl`などのツールを使用してエージェントのAPIエンドポイントと対話できます。これは、プログラムによる対話や、UIなしでデプロイした場合に役立ちます。

    デプロイ後に提供されたサービスURLと、サービスが未認証アクセスを許可するように設定されていない場合は、認証のためのIDトークンが必要になることがあります。

    #### アプリケーションURLの設定

    例のURLを、デプロイされたCloud Runサービスの実際のURLに置き換えます。

    ```bash
    export APP_URL="YOUR_CLOUD_RUN_SERVICE_URL"
    # 例: export APP_URL="https://adk-default-service-name-abc123xyz.a.run.app"
    ```

    #### IDトークンの取得 (必要な場合)

    サービスに認証が必要な場合 (つまり、`gcloud`で`--allow-unauthenticated`を使用しなかったか、`adk`のプロンプトで「N」と回答した場合)、IDトークンを取得します。

    ```bash
    export TOKEN=$(gcloud auth print-identity-token)
    ```

    *サービスが未認証アクセスを許可している場合、以下の`curl`コマンドから`-H "Authorization: Bearer $TOKEN"`ヘッダーを省略できます。*

    #### 利用可能なアプリをリスト表示

    デプロイされたアプリケーション名を確認します。

    ```bash
    curl -X GET -H "Authorization: Bearer $TOKEN" $APP_URL/list-apps
    ```

    *(必要に応じて、この出力に基づいて以下のコマンドの`app_name`を調整します。デフォルトは通常、エージェントディレクトリ名、例: `capital_agent`です)。*

    #### セッションの作成または更新

    特定のユーザーとセッションの状態を初期化または更新します。`capital_agent`を実際のアプリ名に置き換え、必要に応じてユーザー/セッションIDを調整します。`user_123`と`session_abc`は識別子の例であり、希望するユーザーIDとセッションIDに置き換えることができます。

    ```bash
    curl -X POST -H "Authorization: Bearer $TOKEN" \
        $APP_URL/apps/capital_agent/users/user_123/sessions/session_abc \
        -H "Content-Type: application/json" \
        -d '{"preferred_language": "English", "visit_count": 5}'
    ```

    #### エージェントの実行

    エージェントにプロンプトを送信します。`capital_agent`をアプリ名に置き換え、必要に応じてユーザー/セッションIDとプロンプトを調整します。

    ```bash
    curl -X POST -H "Authorization: Bearer $TOKEN" \
        $APP_URL/run_sse \
        -H "Content-Type: application/json" \
        -d '{
        "app_name": "capital_agent",
        "user_id": "user_123",
        "session_id": "session_abc",
        "new_message": {
            "role": "user",
            "parts": [{
            "text": "カナダの首都は何ですか？"
            }]
        },
        "streaming": false
        }'
    ```

    * SSE (Server-Sent Events) を受信したい場合は、`"streaming": true`に設定します。
    * 応答には、最終的な回答を含むエージェントの実行イベントが含まれます。
