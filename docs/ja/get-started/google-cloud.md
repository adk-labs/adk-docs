# Google Cloud および Agent Platform への接続

このガイドでは、ADK エージェントを Google Cloud Platform (GCP) サービス、Google Cloud Agent Platform で動作するモデル、および Agent Platform サービスと接続して認証する方法について説明します。

## Google Cloud Agent Platform のセットアップ

エージェントを Google Cloud または Agent Platform サービスに接続する前に、以下の前提条件を完了していることを確認してください。

*  **Agent Platform API** (`aiplatform.googleapis.com`) が有効になっている Google Cloud プロジェクト。
*  [gcloud CLI](https://cloud.google.com/sdk/docs/install) ツールのインストール。

## Google Cloud 認証オプション

ADK エージェントを Google Cloud に接続する際の認証オプションは複数あります。詳細は以下の表のとおりです。

| 方法 | 主な用途 | 認証メカニズム | 環境 |
| :--- | :--- | :--- | :--- |
| [**User Credentials (ユーザー認証情報)**](#user-credentials) | ローカルでの開発およびテスト | `gcloud` を介したアプリケーションのデフォルト認証情報 (ADC) | ローカルワークステーション |
| [**Service Account (サービスアカウント)**](#service-account) | 本番環境へのデプロイおよび CI/CD | Google IAM サービスアカウントキー / Workload Identity | Google Cloud (Agent Runtime, Cloud Run, GKE) または外部サーバー |
| [**Express Mode (エクスプレスモード)**](#express-mode) | 迅速なプロトタイピングおよびテスト | API キー | ローカルまたはクラウド環境 |
| [**Agent Identity (エージェント ID)**](/ja/integrations/agent-identity) | 本番環境へのデプロイおよび CI/CD | Google IAM サービスアカウントキー / Workload Identity | Google Cloud (Agent Runtime, Cloud Run, GKE) |

!!! warning "警告: 認証情報の保護"

    ユーザー認証情報、サービスアカウントの認証情報、および API キーは非常に機密性の高い情報です。認証情報ファイルやキーをコードベースに直接コミットしないでください。可能な限り、[Google Cloud Agent Identity](/ja/integrations/agent-identity/)、[Google Cloud Secret Manager](https://cloud.google.com/security/products/secret-manager)、またはその他の同様のシークレット管理ツールを使用してください。

### ローカル開発用のユーザー認証情報 {#user-credentials}

ローカル開発環境で動作するユーザー認証情報認証方式を用いて Google Cloud に接続します。

1. ADK エージェントアプリケーションを実行する*前*に、アプリケーションのデフォルト認証情報 (ADC) を使用してローカルワークステーションを認証します。
    ```bash
    gcloud auth application-default login
    ```
2. Agent Platform を有効にし、プロジェクトの詳細を指定するための環境変数を設定します。

    === ".env ファイル"

        ```console
        # ADK コードプロジェクトに追加しますが、ソース管理には含めないでください
        GOOGLE_GENAI_USE_ENTERPRISE=TRUE
        GOOGLE_CLOUD_PROJECT=your-project-id
        GOOGLE_CLOUD_LOCATION=cloud-location   # 例: us-central1
        ```

    === "ターミナル"

        ```bash
        export GOOGLE_GENAI_USE_ENTERPRISE=TRUE
        export GOOGLE_CLOUD_PROJECT="your-project-id"
        export GOOGLE_CLOUD_LOCATION="cloud-location"   # 例: us-central1
        ```

!!! note "`GOOGLE_GENAI_USE_ENTERPRISE` は以前は `GOOGLE_GENAI_USE_ENTERPRISE` でした"

    これらの変数名は同等であり、同じ動作をします。`GOOGLE_GENAI_USE_ENTERPRISE` を設定してもエージェントが Agent Platform に接続しない場合は、古いバージョンの ADK を使用している可能性があります。代わりに `GOOGLE_GENAI_USE_ENTERPRISE` を使用するか、最新バージョンの ADK にアップデートしてください。

### 本番環境用のサービスアカウント {#service-account}

安全にホストされた環境にデプロイする場合は、接続認証にサービスアカウントを使用します。

1. [サービスアカウント (Service Account)](https://docs.cloud.google.com/iam/docs/service-account-overview) を作成し、`Agent Platform User` ロールを付与します。
2. デプロイ戦略に従って、エージェントアプリケーションに認証情報を提供します。
    * **Google Cloud にデプロイする場合 (Agent Runtime, Cloud Run, GKE):**
        環境によって認証情報が自動的に提供されます。キーファイルの設定は不要です。
    * **外部で実行する場合:**
        [サービスアカウントキーファイル](https://cloud.google.com/iam/docs/keys-create-delete#console) (`.json`) を生成し、`GOOGLE_APPLICATION_CREDENTIALS` 환경변수를 설정합니다.
        ```bash
        export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
        ```

!!! tip "Workload Identity オプション"

    キーファイルの代わりに、[Workload Identity](https://docs.cloud.google.com/kubernetes-engine/docs/how-to/workload-identity) を使用してサービスアカウントを認証することもできます。

### テスト用の Agent Platform エクスプレスモード {#express-mode}

Express Mode は、完全な gcloud 認証を行うことなく、プロトタイピング用に API キーベースの簡素化されたセットアップを提供します。

1. API キーを取得するために、[Express Mode](https://console.cloud.google.com/expressmode) に登録します。
2. 以下の環境変数を設定します。

    === ".env ファイル"

        ```console
        # ADK コードプロジェクトに追加しますが、ソース管理には含めないでください
        GOOGLE_GENAI_USE_ENTERPRISE=TRUE
        GOOGLE_GENAI_API_KEY=PASTE_YOUR_ACTUAL_EXPRESS_MODE_API_KEY_HERE
        ```

    === "ターミナル"

        ```bash
        export GOOGLE_GENAI_USE_ENTERPRISE=TRUE
        export GOOGLE_GENAI_API_KEY="PASTE_YOUR_EXPRESS_MODE_API_KEY_HERE"
        ```

## Google Cloud ホストモデル

Google Cloud Agent Platform は、Gemini モデル、サードパーティ AI モデル、オープンウェイトモデル、および組織向けにカスタムチューニングされたモデルを含め、ADK エージェントに接続できる幅広い AI モデルをホストしています。ADK エージェントを Google Cloud および Agent Platform に接続すると、アプリケーションの要件に合った AI モデルを利用できるようになります。プロジェクトに適したモデルを探索し、見つけるために以下のリソースを確認してください。

*   ADK エージェントでの [Gemini モデル](/ja/agents/models/google-gemini/) の使用に関する詳細情報を取得します。
*   ADK エージェントで使用できるサードパーティおよびカスタムモデルのオプションを、[Agent Platform ホストモデル](/ja/agents/models/agent-platform/) で探索します。
*   Google Cloud で利用可能なモデルおよびモデル ID は、[Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/google-models) のドキュメントで確認できます。

## その他の Google Cloud サービス接続

多くの Google Cloud サービスは、ADK エージェントを使用して GCP API やリソースにアクセスするための認証ヘルパーとともに、ADK 統合を提供しています。詳細については、以下のページを参照してください。

* [Google Cloud Application Integration](/ja/integrations/application-integration/)
* [BigQuery Toolset](/ja/integrations/bigquery/)
* [BigQuery Agent Analytics](/ja/integrations/bigquery-agent-analytics/)
* [Data Agent](/ja/integrations/data-agent/)
