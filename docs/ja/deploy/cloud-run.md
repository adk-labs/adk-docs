# Cloud Runへのデプロイ

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span><span class="lst-go">Go</span><span class="lst-java">Java</span>
</div>

[Cloud Run](https://cloud.google.com/run)は、Googleのスケーラブルなインフラストラクチャ上で直接コードを実行できる、フルマネージドプラットフォームです。

エージェントをデプロイするには、`adk deploy cloud_run`コマンド（*Pythonに推奨*）を使用するか、Cloud Runを介して`gcloud run deploy`コマンドを使用します。

## エージェントのサンプル

各コマンドでは、[LLMエージェント](../agents/llm-agents.md)ページで定義されている`Capital Agent`のサンプルを参照します。このサンプルが特定のディレクトリ（例：`capital_agent`）内にあると仮定します。

先に進むには、エージェントのコードが以下のように構成されていることを確認してください。

=== "Python"

    1. エージェントのコードが、エージェントディレクトリ内の`agent.py`というファイルにあります。
    2. エージェント変数の名前が`root_agent`です。
    3. `__init__.py`がエージェントディレクトリ内にあり、`from . import agent`を含んでいます。
    4. `requirements.txt`ファイルがエージェントディレクトリに存在します。

=== "Go"

    1. アプリケーションのエントリーポイント（mainパッケージとmain()関数）が単一のGoファイルにあります。`main.go`を使用することが強力な慣例です。
    2. エージェントのインスタンスがランチャー設定に渡されます。通常は`services.NewSingleAgentLoader(agent)`を使用します。`adkgo`ツールはこのランチャーを使用して、正しいサービスでエージェントを起動します。
    3. 依存関係を管理するために、`go.mod`と`go.sum`ファイルがプロジェクトディレクトリに存在します。

    詳細は次のセクションを参照してください。GitHubリポジトリで[サンプルアプリ](https://github.com/google/adk-docs/tree/main/examples/go/cloud-run)を見つけることもできます。

=== "Java"

    1. エージェントのコードが、エージェントディレクトリ内の`CapitalAgent.java`というファイルにあります。
    2. エージェント変数はグローバルで、`public static final BaseAgent ROOT_AGENT`の形式に従います。
    3. エージェントの定義が静的（static）クラスメソッド内に存在します。

    詳細は次のセクションを参照してください。GitHubリポジトリで[サンプルアプリ](https://github.com/google/adk-docs/tree/main/examples/java/cloud-run)を見つけることもできます。

## 環境変数

[セットアップとインストール](../get-started/installation.md)ガイドの説明に従って環境変数を設定してください。

```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1 # またはお好みのロケーション
export GOOGLE_GENAI_USE_VERTEXAI=True
```

*(`your-project-id`を実際のGCPプロジェクトIDに置き換えてください)*

または、AI StudioのAPIキーを使用することもできます。

```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1 # またはお好みのロケーション
export GOOGLE_GENAI_USE_VERTEXAI=FALSE
export GOOGLE_API_KEY=your-api-key
```
*(`your-project-id`を実際のGCPプロジェクトIDに、`your-api-key`をAI Studioの実際のAPIキーに置き換えてください)*

## 前提条件

1. Google Cloudプロジェクトが必要です。以下の情報を知っている必要があります。
    1. プロジェクト名（例："my-project"）
    2. プロジェクトのロケーション（例："us-central1"）
    3. サービスアカウント（例："1234567890-compute@developer.gserviceaccount.com"）
    4. GOOGLE_API_KEY

## シークレット

サービスアカウントが読み取れるシークレットを作成したことを確認してください。

### GOOGLE_API_KEYシークレットのエントリ

シークレットは手動で作成するか、CLIを使用できます。
```bash
echo "<<ここにGOOGLE_API_KEYを入力してください>>" | gcloud secrets create GOOGLE_API_KEY --project=my-project --data-file=-
```

### 読み取り権限
サービスアカウントがこのシークレットを読み取れるように、適切な権限を付与する必要があります。
```bash
gcloud secrets add-iam-policy-binding GOOGLE_API_KEY --member="serviceAccount:1234567890-compute@developer.gserviceaccount.com" --role="roles/secretmanager.secretAccessor" --project=my-project
```

## デプロイペイロード {#payload}

ADKエージェントのワークフローをGoogle Cloud Runにデプロイすると、以下のコンテンツがサービスにアップロードされます。

- ADKエージェントのコード
- ADKエージェントのコードで宣言されたすべての依存関係
- エージェントが使用するADK APIサーバーのコードバージョン

デフォルトのデプロイには、ADKウェブユーザーインターフェースライブラリは含まれ*ません*。`adk deploy cloud_run`コマンドの`--with_ui`オプションのように、デプロイ設定で指定しない限り含まれません。

## デプロイコマンド

=== "Python - adk CLI"

    ### adk CLI

    `adk deploy cloud_run`コマンドは、エージェントのコードをGoogle Cloud Runにデプロイします。

    Google Cloudで認証済みであることを確認してください（`gcloud auth login`および`gcloud config set project <your-project-id>`）。

    #### 環境変数の設定

    任意ですが推奨：環境変数を設定すると、デプロイコマンドがよりクリーンになります。

    ```bash
    # Google CloudプロジェクトIDを設定
    export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"

    # 希望のGoogle Cloudロケーションを設定
    export GOOGLE_CLOUD_LOCATION="us-central1" # 例のロケーション

    # エージェントのコードディレクトリへのパスを設定
    export AGENT_PATH="./capital_agent" # capital_agentが現在のディレクトリにあると仮定

    # Cloud Runサービスの名前を設定（任意）
    export SERVICE_NAME="capital-agent-service"

    # アプリケーション名を設定（任意）
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

    ##### オプションフラグを含む完全なコマンド

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

    * `AGENT_PATH`: （必須）エージェントのソースコードが含まれるディレクトリへのパスを指定する位置引数（例：サンプルでは`$AGENT_PATH`、または`capital_agent/`）。このディレクトリには、少なくとも`__init__.py`とメインのエージェントファイル（例：`agent.py`）が含まれている必要があります。

    ##### オプション

    * `--project TEXT`: （必須）Google CloudプロジェクトID（例：`$GOOGLE_CLOUD_PROJECT`）。
    * `--region TEXT`: （必須）デプロイ先のGoogle Cloudロケーション（例：`$GOOGLE_CLOUD_LOCATION`、`us-central1`）。
    * `--service_name TEXT`: （任意）Cloud Runサービスの名前（例：`$SERVICE_NAME`）。デフォルトは`adk-default-service-name`です。
    * `--app_name TEXT`: （任意）ADK APIサーバーのアプリケーション名（例：`$APP_NAME`）。デフォルトは`AGENT_PATH`で指定されたディレクトリの名前です（例：`AGENT_PATH`が`./capital_agent`の場合、`capital_agent`）。
    * `--agent_engine_id TEXT`: （任意）Vertex AI Agent Engineを介してマネージドセッションサービスを使用している場合、そのリソースIDをここに指定します。
    * `--port INTEGER`: （任意）コンテナ内でADK APIサーバーがリッスンするポート番号。デフォルトは8000です。
    * `--with_ui`: （任意）これを含めると、エージェントAPIサーバーと共にADK開発UIがデプロイされます。デフォルトではAPIサーバーのみがデプロイされます。
    * `--temp_folder TEXT`: （任意）デプロイプロセス中に生成される中間ファイルを保存するディレクトリを指定します。デフォルトは、システムの一次ディレクトリ内にあるタイムスタンプ付きのフォルダです。（*注意：このオプションは、問題のトラブルシューティング以外では通常必要ありません。*）
    * `--help`: ヘルプメッセージを表示して終了します。

    ##### 認証アクセス
    デプロイプロセス中に、`[your-service-name] への未認証の呼び出しを許可しますか？ (y/N)?` というプロンプトが表示されることがあります。

    * エージェントのAPIエンドポイントへの認証なしの公開アクセスを許可するには `y` を入力します。
    * 認証を要求するには `N` を入力するか、デフォルトでEnterキーを押します（例：「エージェントのテスト」セクションで示すようにIDトークンを使用）。

    正常に実行されると、コマンドはエージェントをCloud Runにデプロイし、デプロイされたサービスのURLを提供します。

=== "Python - gcloud CLI"

    ### Python用 gcloud CLI

    または、`Dockerfile`を使用して標準の`gcloud run deploy`コマンドでデプロイすることもできます。この方法は`adk`コマンドに比べて手動での設定が多くなりますが、特にエージェントをカスタムの[FastAPI](https://fastapi.tiangolo.com/)アプリケーションに埋め込みたい場合に柔軟性を提供します。

    Google Cloudで認証済みであることを確認してください（`gcloud auth login`および`gcloud config set project <your-project-id>`）。

    #### プロジェクト構造

    プロジェクトファイルを以下のように整理します。

    ```txt
    your-project-directory/
    ├── capital_agent/
    │   ├── __init__.py
    │   └── agent.py       # エージェントのコード（「エージェントのサンプル」タブ参照）
    ├── main.py            # FastAPIアプリケーションのエントリーポイント
    ├── requirements.txt   # Pythonの依存関係
    └── Dockerfile         # コンテナのビルド手順
    ```

    `your-project-directory/`のルートに以下のファイル（`main.py`, `requirements.txt`, `Dockerfile`）を作成します。

    #### コードファイル

    1. このファイルはADKの`get_fast_api_app()`を使用してFastAPIアプリケーションをセットアップします。

        ```python title="main.py"
        import os

        import uvicorn
        from fastapi import FastAPI
        from google.adk.cli.fast_api import get_fast_api_app

        # main.pyが配置されているディレクトリを取得
        AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
        # セッションサービスURIの例（例：SQLite）
        SESSION_SERVICE_URI = "sqlite:///./sessions.db"
        # CORSで許可されるオリジンの例
        ALLOWED_ORIGINS = ["http://localhost", "http://localhost:8080", "*"]
        # Webインターフェースを提供する場合はweb=True、それ以外はFalseに設定
        SERVE_WEB_INTERFACE = True

        # FastAPIアプリインスタンスを取得する関数を呼び出す
        # エージェントのディレクトリ名（'capital_agent'）がエージェントフォルダと一致することを確認
        app: FastAPI = get_fast_api_app(
            agents_dir=AGENT_DIR,
            session_service_uri=SESSION_SERVICE_URI,
            allow_origins=ALLOWED_ORIGINS,
            web=SERVE_WEB_INTERFACE,
        )

        # 必要に応じて、以下にFastAPIのルートや設定を追加できます
        # 例：
        # @app.get("/hello")
        # async def read_root():
        #     return {"Hello": "World"}

        if __name__ == "__main__":
            # Cloud Runから提供されるPORT環境変数を使用し、デフォルトは8080
            uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
        ```

        *注意：`agent_dir`を`main.py`があるディレクトリに指定し、Cloud Runとの互換性のために`os.environ.get("PORT", 8080)`を使用しています。*

    2. 必要なPythonパッケージをリストアップします。

        ```txt title="requirements.txt"
        google-adk
        # エージェントが必要とするその他の依存関係を追加
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

    `your-project-directory/`のルートに別々のフォルダを作成することで、同じCloud Runインスタンス内に複数のエージェントを定義し、デプロイできます。各フォルダは1つのエージェントを表し、その設定で`root_agent`を定義する必要があります。

    構造例：

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
    # エージェントが必要とする可能性のあるその他の環境変数を追加
    ```

    * `capital-agent-service`: Cloud Runサービスに付けたい名前。
    * `--source .`: gcloudに現在のディレクトリのDockerfileからコンテナイメージをビルドするように指示します。
    * `--region`: デプロイリージョンを指定します。
    * `--project`: GCPプロジェクトを指定します。
    * `--allow-unauthenticated`: サービスへの公開アクセスを許可します。プライベートサービスの場合はこのフラグを削除してください。
    * `--set-env-vars`: 実行中のコンテナに必要な環境変数を渡します。ADKとエージェントが必要とするすべての変数（アプリケーションのデフォルト認証情報を使用しない場合のAPIキーなど）を含めるようにしてください。

    `gcloud`はDockerイメージをビルドし、Google Artifact RegistryにプッシュしてからCloud Runにデプロイします。完了すると、デプロイされたサービスのURLが出力されます。

    デプロイオプションの完全なリストについては、[`gcloud run deploy`のリファレンスドキュメント](https://cloud.google.com/sdk/gcloud/reference/run/deploy)を参照してください。

=== "Go - adkgo CLI"

    ### adk CLI

    `adkgo`コマンドは`google/adk-go`リポジトリの`cmd/adkgo`にあります。使用する前に、`adk-go`リポジトリのルートからビルドする必要があります。

    `go build ./cmd/adkgo`

    `adkgo deploy cloudrun`コマンドは、アプリケーションのデプロイを自動化します。独自のDockerfileを提供する必要はありません。

    #### エージェントのコード構造

    `adkgo`ツールを使用する場合、`main.go`ファイルはランチャーフレームワークを使用する必要があります。これは、ツールがコードをコンパイルし、結果の実行ファイルを特定のコマンドライン引数（`web`、`api`、`a2a`など）で実行して必要なサービスを起動するためです。ランチャーはこれらの引数を正しく解析するように設計されています。

    `main.go`は次のようになります。

    ```go title="main.go"
    --8<-- "examples/go/cloud-run/main.go"
    ```

    #### 仕組み
    1. `adkgo`ツールは、`main.go`を静的リンクされたLinux用バイナリにコンパイルします。
    2. このバイナリを最小限のコンテナにコピーするDockerfileを生成します。
    3. `gcloud`を使用してこのコンテナをビルドし、Cloud Runにデプロイします。
    4. デプロイ後、新しく作成されたサービスに安全に接続するローカルプロキシを起動します。

    Google Cloudで認証済みであることを確認してください（`gcloud auth login`および`gcloud config set project <your-project-id>`）。

    #### 環境変数の設定

    任意ですが推奨：環境変数を設定すると、デプロイコマンドがよりクリーンになります。

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

    * `-p, --project_name`: Google CloudプロジェクトID（例：`$GOOGLE_CLOUD_PROJECT`）。
    * `-r, --region`: デプロイ先のGoogle Cloudロケーション（例：`$GOOGLE_CLOUD_LOCATION`、`us-central1`）。
    * `-s, --service_name`: Cloud Runサービスの名前（例：`$SERVICE_NAME`）。
    * `-e, --entry_point_path`: エージェントのソースコードが含まれるメインのGoファイルへのパス（例：`$AGENT_PATH`）。

    ##### 任意

    * `--proxy_port`: 認証プロキシがリッスンするローカルポート。デフォルトは8081です。
    * `--server_port`: Cloud Runコンテナ内でサーバーがリッスンするポート番号。デフォルトは8080です。
    * `--a2a`: これを含めると、Agent2Agent通信が有効になります。デフォルトで有効です。
    * `--a2a_agent_url`: 公開エージェントカードで広告されるA2AエージェントカードのURL。このフラグは`--a2a`フラグと同時に使用する場合にのみ有効です。
    * `--api`: これを含めると、ADK APIサーバーがデプロイされます。デフォルトで有効です。
    * `--webui`: これを含めると、エージェントAPIサーバーと共にADK開発UIがデプロイされます。デフォルトで有効です。
    * `--temp_dir`: ビルドアーティファクト用の一時ディレクトリ。デフォルトは`os.TempDir()`です。
    * `--help`: ヘルプメッセージを表示して終了します。

    ##### 認証アクセス
    サービスはデフォルトで`--no-allow-unauthenticated`でデプロイされます。

    正常に実行されると、コマンドはエージェントをCloud Runにデプロイし、プロキシ経由でサービスにアクセスするためのローカルURLを提供します。

=== "Java - gcloud CLI"

    ### Java用 gcloud CLI

    Javaエージェントは、標準の`gcloud run deploy`コマンドと`Dockerfile`を使用してデプロイできます。これは、現在JavaエージェントをGoogle Cloud Runにデプロイする推奨方法です。

    Google Cloudで[認証](https://cloud.google.com/docs/authentication/gcloud)済みであることを確認してください。具体的には、ターミナルから`gcloud auth login`および`gcloud config set project <your-project-id>`コマンドを実行します。

    #### プロジェクト構造

    プロジェクトファイルを以下のように整理します。

    ```txt
    your-project-directory/
    ├── src/
    │   └── main/
    │       └── java/
    │             └── agents/
    │                 ├── capitalagent/
    │                     └── CapitalAgent.java    # エージェントのコード
    ├── pom.xml                                    # Java adk と adk-dev の依存関係
    └── Dockerfile                                 # コンテナのビルド手順
    ```

    プロジェクトディレクトリのルートに`pom.xml`と`Dockerfile`を作成します。エージェントのコードファイル（`CapitalAgent.java`）は上記のようにディレクトリ内に配置します。

    #### コードファイル

    1. こちらがエージェントの定義です。[LLMエージェント](../agents/llm-agents.md)にあるコードと同じですが、2つの注意点があります。

           * エージェントは**グローバルな public static final 変数**として初期化されます。

           * エージェントの定義は、静的メソッドで公開するか、宣言時にインライン化することができます。

        `CapitalAgent`の例のコードは、[examples](https://github.com/google/adk-docs/blob/main/examples/java/cloud-run/src/main/java/agents/capitalagent/CapitalAgent.java)リポジトリで確認してください。

    2. 以下の依存関係とプラグインを`pom.xml`ファイルに追加します。

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
    # エージェントが必要とする可能性のあるその他の環境変数を追加
    ```

    * `capital-agent-service`: Cloud Runサービスに付けたい名前。
    * `--source .`: gcloudに現在のディレクトリのDockerfileからコンテナイメージをビルドするように指示します。
    * `--region`: デプロイリージョンを指定します。
    * `--project`: GCPプロジェクトを指定します。
    * `--allow-unauthenticated`: サービスへの公開アクセスを許可します。プライベートサービスの場合はこのフラグを削除してください。
    * `--set-env-vars`: 実行中のコンテナに必要な環境変数を渡します。ADKとエージェントが必要とするすべての変数（アプリケーションのデフォルト認証情報を使用しない場合のAPIキーなど）を含めるようにしてください。

    `gcloud`はDockerイメージをビルドし、Google Artifact RegistryにプッシュしてからCloud Runにデプロイします。完了すると、デプロイされたサービスのURLが出力されます。

    デプロイオプションの完全なリストについては、[`gcloud run deploy`のリファレンスドキュメント](https://cloud.google.com/sdk/gcloud/reference/run/deploy)を参照してください。

## エージェントのテスト

エージェントがCloud Runにデプロイされたら、（有効にしている場合は）デプロイされたUIを介して、または`curl`のようなツールを使用してAPIエンドポイントと直接対話できます。デプロイ後に提供されるサービスURLが必要です。

=== "UIテスト"

    ### UIテスト

    UIを有効にしてエージェントをデプロイした場合：

    *   **adk CLI:** デプロイ時に`--webui`フラグを含めました。
    *   **gcloud CLI:** `main.py`で`SERVE_WEB_INTERFACE = True`と設定しました。

    デプロイ後に提供されたCloud RunサービスのURLにウェブブラウザでアクセスするだけで、エージェントをテストできます。

    ```bash
    # URL形式の例
    # https://your-service-name-abc123xyz.a.run.app
    ```

    ADK開発UIを使用すると、ブラウザで直接エージェントと対話し、セッションを管理し、実行詳細を表示できます。

    エージェントが意図通りに機能していることを確認するには、次のようにします。

    1. ドロップダウンメニューからエージェントを選択します。
    2. メッセージを入力し、エージェントから期待される応答を受け取ることを確認します。

    予期しない動作が発生した場合は、[Cloud Run](https://console.cloud.google.com/run)のコンソールログを確認してください。

=== "APIテスト (curl)"

    ### APIテスト (curl)

    `curl`のようなツールを使用して、エージェントのAPIエンドポイントと対話できます。これはプログラムによる対話や、UIなしでデプロイした場合に便利です。

    デプロイ後に提供されるサービスURLと、サービスが未認証アクセスを許可するように設定されていない場合は認証用のIDトークンが必要になります。

    #### アプリケーションURLの設定

    例のURLを、デプロイされたCloud Runサービスの実際のURLに置き換えてください。

    ```bash
    export APP_URL="YOUR_CLOUD_RUN_SERVICE_URL"
    # 例：export APP_URL="https://adk-default-service-name-abc123xyz.a.run.app"
    ```

    #### IDトークンの取得（必要な場合）

    サービスが認証を要求する場合（つまり、`gcloud`で`--allow-unauthenticated`を使用しなかったか、`adk`のプロンプトに'N'と答えた場合）、IDトークンを取得します。

    ```bash
    export TOKEN=$(gcloud auth print-identity-token)
    ```

    *サービスが未認証アクセスを許可する場合は、以下の`curl`コマンドから`-H "Authorization: Bearer $TOKEN"`ヘッダーを省略できます。*

    #### 利用可能なアプリの一覧表示

    デプロイされたアプリケーション名を確認します。

    ```bash
    curl -X GET -H "Authorization: Bearer $TOKEN" $APP_URL/list-apps
    ```

    *（必要に応じて、この出力に基づいて後続のコマンドの`app_name`を調整してください。デフォルトはしばしばエージェントのディレクトリ名、例：`capital_agent`です）*

    #### セッションの作成または更新

    特定のユーザーとセッションの状態を初期化または更新します。`capital_agent`を実際のアプリ名に置き換えてください。`user_123`と`session_abc`の値は例の識別子です。希望のユーザーIDとセッションIDに置き換えることができます。

    ```bash
    curl -X POST -H "Authorization: Bearer $TOKEN" \
        $APP_URL/apps/capital_agent/users/user_123/sessions/session_abc \
        -H "Content-Type: application/json" \
        -d '{"preferred_language": "English", "visit_count": 5}'
    ```

    #### エージェントの実行

    エージェントにプロンプトを送信します。`capital_agent`をアプリ名に置き換え、必要に応じてユーザー/セッションIDとプロンプトを調整してください。

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
            "text": "カナダの首都はどこですか？"
            }]
        },
        "streaming": false
        }'
    ```

    * サーバー送信イベント（SSE）を受信したい場合は、`"streaming": true`に設定します。
    * 応答には、最終的な回答を含むエージェントの実行イベントが含まれます。