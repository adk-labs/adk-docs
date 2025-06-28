# GKEへのデプロイ

[GKE](https://cloud.google.com/gke)はGoogle CloudのマネージドKubernetesサービスです。Kubernetesを使用してコンテナ化されたアプリケーションをデプロイおよび管理できます。

エージェントをデプロイするには、GKE上で実行されているKubernetesクラスタが必要です。Google Cloudコンソールまたは`gcloud`コマンドラインツールを使用してクラスタを作成できます。

この例では、シンプルなエージェントをGKEにデプロイします。エージェントは、LLMとして`Gemini 2.0 Flash`を使用するFastAPIアプリケーションになります。環境変数を使用して、LLMプロバイダーとしてVertex AIまたはAI Studioを使用できます。

## エージェントのサンプル

各コマンドでは、[LLMエージェント](../agents/llm-agents.md)ページで定義されている`capital_agent`サンプルを参照します。このサンプルは`capital_agent`ディレクトリにあると仮定します。

進めるには、エージェントのコードが次のように設定されていることを確認してください。

1.  エージェントのコードがエージェントディレクトリ内の`agent.py`というファイルにあること。
2.  エージェントの変数名が`root_agent`であること。
3.  `__init__.py`がエージェントディレクトリ内にあり、`from . import agent`を含んでいること。

## 環境変数

[セットアップとインストール](../get-started/installation.md)ガイドで説明されているように環境変数を設定します。また、`kubectl`コマンドラインツールをインストールする必要もあります。インストール手順は[Google Kubernetes Engineドキュメント](https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-access-for-kubectl)にあります。

```bash
export GOOGLE_CLOUD_PROJECT=your-project-id # あなたのGCPプロジェクトID
export GOOGLE_CLOUD_LOCATION=us-central1 # または希望のロケーション
export GOOGLE_GENAI_USE_VERTEXAI=true # Vertex AIを使用する場合はtrueに設定
export GOOGLE_CLOUD_PROJECT_NUMBER=$(gcloud projects describe --format json $GOOGLE_CLOUD_PROJECT | jq -r ".projectNumber")
```

`jq`がインストールされていない場合は、次のコマンドを使用してプロジェクト番号を取得できます。

```bash
gcloud projects describe $GOOGLE_CLOUD_PROJECT
```

そして、出力からプロジェクト番号をコピーします。

```bash
export GOOGLE_CLOUD_PROJECT_NUMBER=YOUR_PROJECT_NUMBER
```

## デプロイオプション

エージェントをGKEにデプロイするには、**Kubernetesマニフェストを使用して手動でデプロイする**か、**`adk deploy gke`コマンドを使用して自動でデプロイする**かのいずれかの方法があります。あなたのワークフローに最適なアプローチを選択してください。

Google Cloudで認証されていることを確認してください（`gcloud auth login`と`gcloud config set project <your-project-id>`）。

### APIの有効化

プロジェクトに必要なAPIを有効にします。`gcloud`コマンドラインツールを使用してこれを行うことができます。

```bash
gcloud services enable \
    container.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    aiplatform.googleapis.com
```

### オプション1：gcloudとkubectlを使用した手動デプロイ

### GKEクラスタの作成

`gcloud`コマンドラインツールを使用してGKEクラスタを作成できます。この例では、`us-central1`リージョンに`adk-cluster`という名前のAutopilotクラスタを作成します。

> GKE Standardクラスタを作成する場合は、[Workload Identity](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity)が有効になっていることを確認してください。Workload IdentityはAutoPilotクラスタではデフォルトで有効になっています。

```bash
gcloud container clusters create-auto adk-cluster \
    --location=$GOOGLE_CLOUD_LOCATION \
    --project=$GOOGLE_CLOUD_PROJECT
```

クラスタを作成したら、`kubectl`を使用して接続する必要があります。このコマンドは、`kubectl`が新しいクラスタの認証情報を使用するように設定します。

```bash
gcloud container clusters get-credentials adk-cluster \
    --location=$GOOGLE_CLOUD_LOCATION \
    --project=$GOOGLE_CLOUD_PROJECT
```

### プロジェクト構造

プロジェクトファイルを次のように整理します。

```txt
your-project-directory/
├── capital_agent/
│   ├── __init__.py
│   └── agent.py       # エージェントのコード（「エージェントのサンプル」タブを参照）
├── main.py            # FastAPIアプリケーションのエントリポイント
├── requirements.txt   # Pythonの依存関係
└── Dockerfile         # コンテナのビルド手順
```

`your-project-directory/`のルートに次のファイル（`main.py`, `requirements.txt`, `Dockerfile`）を作成します。

### コードファイル

1.  このファイルは、ADKの`get_fast_api_app()`を使用してFastAPIアプリケーションをセットアップします。

    ```python title="main.py"
    import os

    import uvicorn
    from fastapi import FastAPI
    from google.adk.cli.fast_api import get_fast_api_app

    # main.pyが配置されているディレクトリを取得
    AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
    # セッションDBのURLの例（例：SQLite）
    SESSION_DB_URL = "sqlite:///./sessions.db"
    # CORSで許可するオリジンの例
    ALLOWED_ORIGINS = ["http://localhost", "http://localhost:8080", "*"]
    # Webインターフェースを提供する場合はweb=True、それ以外はFalseに設定
    SERVE_WEB_INTERFACE = True

    # FastAPIアプリのインスタンスを取得する関数を呼び出す
    # エージェントのディレクトリ名（'capital_agent'）がエージェントフォルダと一致することを確認
    app: FastAPI = get_fast_api_app(
        agents_dir=AGENT_DIR,
        session_db_url=SESSION_DB_URL,
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

    *注：`agent_dir`を`main.py`があるディレクトリに指定し、Cloud Runとの互換性のために`os.environ.get("PORT", 8080)`を使用します。*

2.  必要なPythonパッケージをリストアップします。

    ```txt title="requirements.txt"
    google_adk
    # エージェントが必要とするその他の依存関係を追加
    ```

3.  コンテナイメージを定義します。

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

### コンテナイメージのビルド

コンテナイメージを保存するために、Google Artifact Registryリポジトリを作成する必要があります。`gcloud`コマンドラインツールを使用してこれを行うことができます。

```bash
gcloud artifacts repositories create adk-repo \
    --repository-format=docker \
    --location=$GOOGLE_CLOUD_LOCATION \
    --description="ADK repository"
```

`gcloud`コマンドラインツールを使用してコンテナイメージをビルドします。この例では、イメージをビルドし、`adk-repo/adk-agent:latest`としてタグ付けします。

```bash
gcloud builds submit \
    --tag $GOOGLE_CLOUD_LOCATION-docker.pkg.dev/$GOOGLE_CLOUD_PROJECT/adk-repo/adk-agent:latest \
    --project=$GOOGLE_CLOUD_PROJECT \
    .
```

イメージがビルドされ、Artifact Registryにプッシュされたことを確認します。

```bash
gcloud artifacts docker images list \
  $GOOGLE_CLOUD_LOCATION-docker.pkg.dev/$GOOGLE_CLOUD_PROJECT/adk-repo \
  --project=$GOOGLE_CLOUD_PROJECT
```

### Vertex AI用のKubernetesサービスアカウントの設定

エージェントがVertex AIを使用する場合、必要な権限を持つKubernetesサービスアカウントを作成する必要があります。この例では、`adk-agent-sa`という名前のサービスアカウントを作成し、`Vertex AI User`ロールにバインドします。

> AI Studioを使用し、APIキーでモデルにアクセスしている場合は、この手順をスキップできます。

```bash
kubectl create serviceaccount adk-agent-sa
```

```bash
gcloud projects add-iam-policy-binding projects/${GOOGLE_CLOUD_PROJECT} \
    --role=roles/aiplatform.user \
    --member=principal://iam.googleapis.com/projects/${GOOGLE_CLOUD_PROJECT_NUMBER}/locations/global/workloadIdentityPools/${GOOGLE_CLOUD_PROJECT}.svc.id.goog/subject/ns/default/sa/adk-agent-sa \
    --condition=None
```

### Kubernetesマニフェストファイルの作成

プロジェクトディレクトリに`deployment.yaml`という名前のKubernetesデプロイメントマニフェストファイルを作成します。このファイルは、GKEにアプリケーションをデプロイする方法を定義します。

```yaml title="deployment.yaml"
cat <<  EOF > deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: adk-agent
spec:
  replicas: 1
  selector:
    matchLabels:
      app: adk-agent
  template:
    metadata:
      labels:
        app: adk-agent
    spec:
      serviceAccount: adk-agent-sa
      containers:
      - name: adk-agent
        imagePullPolicy: Always
        image: $GOOGLE_CLOUD_LOCATION-docker.pkg.dev/$GOOGLE_CLOUD_PROJECT/adk-repo/adk-agent:latest
        resources:
          limits:
            memory: "128Mi"
            cpu: "500m"
            ephemeral-storage: "128Mi"
          requests:
            memory: "128Mi"
            cpu: "500m"
            ephemeral-storage: "128Mi"
        ports:
        - containerPort: 8080
        env:
          - name: PORT
            value: "8080"
          - name: GOOGLE_CLOUD_PROJECT
            value: GOOGLE_CLOUD_PROJECT
          - name: GOOGLE_CLOUD_LOCATION
            value: GOOGLE_CLOUD_LOCATION
          - name: GOOGLE_GENAI_USE_VERTEXAI
            value: GOOGLE_GENAI_USE_VERTEXAI
          # AI Studioを使用する場合は、GOOGLE_GENAI_USE_VERTEXAIをfalseに設定し、以下を設定します：
          # - name: GOOGLE_API_KEY
          #   value: GOOGLE_API_KEY
          # エージェントが必要とするその他の環境変数を追加
---
apiVersion: v1
kind: Service
metadata:
  name: adk-agent
spec:       
  type: LoadBalancer
  ports:
    - port: 80
      targetPort: 8080
  selector:
    app: adk-agent
EOF
```

### アプリケーションのデプロイ

`kubectl`コマンドラインツールを使用してアプリケーションをデプロイします。このコマンドは、デプロイメントとサービスのマニフェストファイルをGKEクラスタに適用します。

```bash
kubectl apply -f deployment.yaml
```

数分後、次のようにデプロイメントのステータスを確認できます。

```bash
kubectl get pods -l=app=adk-agent
```

このコマンドは、デプロイメントに関連付けられたPodをリスト表示します。ステータスが`Running`のPodが表示されるはずです。

Podが実行中になったら、次のようにサービスのステータスを確認できます。

```bash
kubectl get service adk-agent
```

出力に`External IP`が表示された場合、サービスはインターネットからアクセス可能です。外部IPが割り当てられるまで数分かかることがあります。

次のようにしてサービスの外部IPアドレスを取得できます。

```bash
kubectl get svc adk-agent -o=jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

### オプション2：`adk deploy gke`を使用した自動デプロイ

ADKは、GKEへのデプロイを効率化するためのCLIコマンドを提供します。これにより、手動でのイメージビルド、Kubernetesマニフェストの記述、Artifact Registryへのプッシュが不要になります。

#### 前提条件

始める前に、次のものが設定されていることを確認してください。

1.  **実行中のGKEクラスタ：** Google Cloud上にアクティブなKubernetesクラスタが必要です。

2.  **`gcloud` CLI：** Google Cloud CLIがインストールされ、認証され、ターゲットプロジェクトを使用するように設定されている必要があります。`gcloud auth login`と`gcloud config set project [YOUR_PROJECT_ID]`を実行してください。

3.  **必要なIAM権限：** コマンドを実行するユーザーまたはサービスアカウントには、最低でも次のロールが必要です。

    *   **Kubernetes Engine 開発者** (`roles/container.developer`): GKEクラスタと対話するため。

    *   **Artifact Registry 書き込み担当者** (`roles/artifactregistry.writer`): エージェントのコンテナイメージをプッシュするため。

4.  **Docker：** コンテナイメージをビルドするために、ローカルマシンでDockerデーモンが実行されている必要があります。

### `deploy gke`コマンド

このコマンドは、エージェントへのパスとターゲットGKEクラスタを指定するパラメータを受け取ります。

#### 構文

```bash
adk deploy gke [OPTIONS] AGENT_PATH
```

### 引数とオプション

| 引数 | 説明 | 必須 |
| --- | --- | --- |
| AGENT_PATH | エージェントのルートディレクトリへのローカルファイルパス。 | はい |
| --project | GKEクラスタが配置されているGoogle CloudプロジェクトID。 | はい |
| --cluster_name | GKEクラスタの名前。 | はい |
| --region | クラスタのGoogle Cloudリージョン（例：us-central1）。 | はい |
| --with_ui | エージェントのバックエンドAPIと、付随するフロントエンドユーザーインターフェースの両方をデプロイします。 | いいえ |
| --verbosity | デプロイプロセスのロギングレベルを設定します。オプション：debug, info, warning, error。 | いいえ |

### 動作の仕組み
`adk deploy gke`コマンドを実行すると、ADKは次のステップを自動的に実行します。

-   コンテナ化：エージェントのソースコードからDockerコンテナイメージをビルドします。

-   イメージのプッシュ：コンテナイメージにタグを付け、プロジェクトのArtifact Registryにプッシュします。

-   マニフェストの生成：必要なKubernetesマニフェストファイル（`Deployment`と`Service`）を動的に生成します。

-   クラスタへのデプロイ：これらのマニフェストを指定したGKEクラスタに適用し、次の処理がトリガーされます。

    `Deployment`は、GKEにArtifact Registryからコンテナイメージを取得し、1つ以上のPodで実行するように指示します。

    `Service`は、エージェント用の安定したネットワークエンドポイントを作成します。デフォルトでは、これはLoadBalancerサービスであり、エージェントをインターネットに公開するためのパブリックIPアドレスをプロビジョニングします。

### 使用例
これは、`~/agents/multi_tool_agent/`にあるエージェントを`test`という名前のGKEクラスタにデプロイする実践的な例です。

```bash
adk deploy gke \
    --project myproject \
    --cluster_name test \
    --region us-central1 \
    --with_ui \
    --verbosity info \
    ~/agents/multi_tool_agent/
```

### デプロイの確認
`adk deploy gke`を使用した場合は、`kubectl`を使用してデプロイを確認します。

1.  Podの確認：エージェントのPodが`Running`状態であることを確認します。

    ```bash
    kubectl get pods
    ```
    デフォルトのネームスペースに`adk-default-service-name-xxxx-xxxx ... 1/1 Running`のような出力が表示されるはずです。

2.  外部IPの検索：エージェントのサービスのパブリックIPアドレスを取得します。

    ```bash
    kubectl get service
    NAME                       TYPE           CLUSTER-IP      EXTERNAL-IP     PORT(S)        AGE
    adk-default-service-name   LoadBalancer   34.118.228.70   34.63.153.253   80:32581/TCP   5d20h
    ```

外部IPに移動し、UI経由でエージェントと対話できます。
![alt text](../assets/agent-gke-deployment.png)

## エージェントのテスト

エージェントがGKEにデプロイされたら、（有効になっている場合は）デプロイされたUIを介して、または`curl`のようなツールを使用してAPIエンドポイントと直接対話できます。デプロイ後に提供されるサービスURLが必要です。

=== "UIテスト"

    ### UIテスト

    UIを有効にしてエージェントをデプロイした場合：

    WebブラウザでKubernetesサービスのURLに移動するだけでエージェントをテストできます。

    ADK dev UIを使用すると、ブラウザで直接エージェントと対話し、セッションを管理し、実行の詳細を表示できます。

    エージェントが意図したとおりに動作していることを確認するには、次のことができます。

    1.  ドロップダウンメニューからエージェントを選択します。
    2.  メッセージを入力し、エージェントから期待される応答を受け取ることを確認します。

    予期しない動作が発生した場合は、次のようにエージェントのPodログを確認してください。

    ```bash
    kubectl logs -l app=adk-agent
    ```

=== "APIテスト (curl)"

    ### APIテスト (curl)

    `curl`のようなツールを使用して、エージェントのAPIエンドポイントと対話できます。これは、プログラムによる対話や、UIなしでデプロイした場合に便利です。

    #### アプリケーションURLの設定

    サンプルURLを、デプロイしたCloud Runサービスの実際のURLに置き換えてください。

    ```bash
    export APP_URL="KUBERNETES_SERVICE_URL"
    ```

    #### 利用可能なアプリのリスト表示

    デプロイされたアプリケーション名を確認します。

    ```bash
    curl -X GET $APP_URL/list-apps
    ```

    *(必要に応じて、この出力に基づいて次のコマンドの`app_name`を調整してください。デフォルトは多くの場合、エージェントのディレクトリ名です。例：`capital_agent`)*

    #### セッションの作成または更新

    特定のユーザーとセッションの状態を初期化または更新します。`capital_agent`を実際のアプリ名に置き換えてください（異なる場合）。`user_123`と`session_abc`の値はサンプル識別子です。希望のユーザーIDとセッションIDに置き換えることができます。

    ```bash
    curl -X POST \
        $APP_URL/apps/capital_agent/users/user_123/sessions/session_abc \
        -H "Content-Type: application/json" \
        -d '{"state": {"preferred_language": "English", "visit_count": 5}}'
    ```

    #### エージェントの実行

    エージェントにプロンプトを送信します。`capital_agent`をアプリ名に置き換え、必要に応じてユーザー/セッションIDとプロンプトを調整してください。

    ```bash
    curl -X POST $APP_URL/run_sse \
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

    *   Server-Sent Events（SSE）を受信したい場合は、`"streaming": true`に設定します。
    *   応答には、最終的な回答を含むエージェントの実行イベントが含まれます。

## トラブルシューティング

これらは、エージェントをGKEにデプロイする際に遭遇する可能性のある一般的な問題です。

### `Gemini 2.0 Flash`に対する403権限拒否

これは通常、KubernetesサービスアカウントがVertex AI APIにアクセスするために必要な権限を持っていないことを意味します。[Vertex AI用のKubernetesサービスアカウントの設定](#configure-kubernetes-service-account-for-vertex-ai)セクションで説明されているように、サービスアカウントを作成し、`Vertex AI User`ロールにバインドしたことを確認してください。AI Studioを使用している場合は、デプロイメントマニフェストに`GOOGLE_API_KEY`環境変数を設定し、それが有効であることを確認してください。

### 読み取り専用データベースへの書き込み試行

UIにセッションIDが作成されず、エージェントがどのメッセージにも応答しないことがあります。これは通常、SQLiteデータベースが読み取り専用であることが原因です。これは、エージェントをローカルで実行し、その後SQLiteデータベースをコンテナにコピーするコンテナイメージを作成した場合に発生する可能性があります。その場合、データベースはコンテナ内で読み取り専用になります。

```bash
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) attempt to write a readonly database
[SQL: UPDATE app_states SET state=?, update_time=CURRENT_TIMESTAMP WHERE app_states.app_name = ?]
```

この問題を修正するには、次のいずれかを実行できます。

コンテナイメージをビルドする前に、ローカルマシンからSQLiteデータベースファイルを削除します。これにより、コンテナが起動したときに新しいSQLiteデータベースが作成されます。

```bash
rm -f sessions.db
```

または（推奨）、プロジェクトディレクトリに`.dockerignore`ファイルを追加して、SQLiteデータベースがコンテナイメージにコピーされないように除外します。

```txt title=".dockerignore"
sessions.db
```

コンテナイメージを再ビルドし、アプリケーションを再度デプロイします。

## クリーンアップ

GKEクラスタと関連するすべてのリソースを削除するには、次のように実行します。

```bash
gcloud container clusters delete adk-cluster \
    --location=$GOOGLE_CLOUD_LOCATION \
    --project=$GOOGLE_CLOUD_PROJECT
```

Artifact Registryリポジトリを削除するには、次のように実行します。

```bash
gcloud artifacts repositories delete adk-repo \
    --location=$GOOGLE_CLOUD_LOCATION \
    --project=$GOOGLE_CLOUD_PROJECT
```

不要になった場合は、プロジェクトを削除することもできます。これにより、GKEクラスタ、Artifact Registryリポジトリ、および作成したその他のリソースを含む、プロジェクトに関連付けられているすべてのリソースが削除されます。

```bash
gcloud projects delete $GOOGLE_CLOUD_PROJECT
```