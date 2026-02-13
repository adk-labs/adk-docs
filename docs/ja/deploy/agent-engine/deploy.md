# Vertex AI Agent Engine へのデプロイ

<div class="language-support-tag" title="Vertex AI Agent Engine は現在 Python のみをサポートしています。">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

このデプロイ手順は、Google Cloud の
[Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)
に ADK エージェントコードを標準的な方法でデプロイする手順を説明します。
既存の Google Cloud プロジェクトがあり、ADK エージェントを Agent Engine ランタイムへ慎重にデプロイしたい場合にこの手順を使用してください。
Cloud Console、gcloud、ADK CLI を使用します。この方法は Google Cloud プロジェクト設定に慣れており、運用デプロイを計画しているユーザー向けです。

このガイドでは、次の段階で構成されるデプロイ手順を説明します。

*   [Google Cloud プロジェクトのセットアップ](#setup-cloud-project)
*   [エージェントプロジェクトフォルダの準備](#define-your-agent)
*   [エージェントのデプロイ](#deploy-agent)

## Google Cloud プロジェクトのセットアップ {#setup-cloud-project}

エージェントを Agent Engine にデプロイするには、Google Cloud プロジェクトが必要です。

1. **Google Cloud にログイン**:
    * 既存の Google Cloud ユーザー:
        * [https://console.cloud.google.com](https://console.cloud.google.com) でログインします。
        * 無効化された無料トライアルを利用していた場合、[有料請求アカウント](https://docs.cloud.google.com/free/docs/free-cloud-features#how-to-upgrade)に切り替える必要がある場合があります。
    * Google Cloud の新規ユーザー:
        * [無料トライアルプログラム](https://docs.cloud.google.com/free/docs/free-cloud-features)に参加できます。
        Google Cloud 製品の [無料トライアル](https://docs.cloud.google.com/free/docs/free-cloud-features#during-free-trial)では、91 日間で 300 ドル分のクレジットが利用でき、
        月単位の制限内で複数の製品が無料利用できます。

2. **Google Cloud プロジェクトを作成**
    * 既存の Google Cloud プロジェクトがある場合でも利用可能ですが、このプロセスで新しいサービスが追加される可能性があります。
    * 新規プロジェクトが必要な場合は、[プロジェクトの作成](https://console.cloud.google.com/projectcreate)ページから作成できます。

3. **Google Cloud プロジェクト ID を取得**
    * GCP ホームページでプロジェクト ID（英数字とハイフン）を確認し、
      プロジェクト番号ではなくプロジェクト ID をメモしてください（例: alphanumeric with hyphens）。

    <img src="/adk-docs/assets/project-id.png" alt="Google Cloud Project ID">

4. **Vertex AI を有効化**
    * Agent Engine を使うには [Vertex AI API](https://console.cloud.google.com/apis/library/aiplatform.googleapis.com) を有効化します。
      「Enable」をクリックして API を有効にすると、状態が「API Enabled」と表示されます。

5. **Cloud Resource Manager API を有効化**
    * Agent Engine 利用のため [Cloud Resource Manager API](https://console.developers.google.com/apis/api/cloudresourcemanager.googleapis.com/overview) を有効化します。
      「Enable」をクリックし、状態が「API Enabled」と表示されることを確認します。

## コーディング環境のセットアップ {#prerequisites-coding-env}

Google Cloud プロジェクトの準備が完了したらコーディング環境に戻ります。
この手順では、ターミナルでコマンドライン指示を実行します。

### コーディング環境で Google Cloud 認証

*   Google Cloud と対話するには認証が必要です。gcloud CLI が必要です。
    まだ未使用の場合は、まず
    [インストール](https://docs.cloud.google.com/sdk/docs/install-sdk)を完了してください。

*   ユーザーアカウントで Google Cloud へログインするには、次を実行します。

    ```shell
    gcloud auth login
    ```

    認証後、`You are now authenticated with the gcloud CLI!` が表示されます。

*   コードが Google Cloud で動作するよう認証します。

    ```shell
    gcloud auth application-default login
    ```

    認証後、同様のメッセージが表示されます。

*   （任意）デフォルトプロジェクトを変更する場合:

    ```shell
    gcloud config set project MY-PROJECT-ID
    ```

### エージェント定義 {#define-your-agent}

Google Cloud とコーディング環境の準備が完了すると、デプロイを開始できます。次のようなエージェントプロジェクトフォルダがあるものとします。

```shell
multi_tool_agent/
├── .env
├── __init__.py
└── agent.py
```

プロジェクトファイル構成の詳細は
[multi_tool_agent](https://github.com/google/adk-docs/tree/main/examples/python/snippets/get-started/multi_tool_agent)
サンプルを参照してください。

## エージェントのデプロイ {#deploy-agent}

ターミナルで `adk deploy` CLI を使用してデプロイを実行します。
この処理でコードをパッケージ化し、コンテナとしてビルドして、管理型の Agent Engine サービスにデプロイします。
この処理には数分かかる場合があります。

以下は `multi_tool_agent` サンプルをデプロイする際のコマンド例です。

```shell
PROJECT_ID=my-project-id
LOCATION_ID=us-central1

adk deploy agent_engine \
        --project=$PROJECT_ID \
        --region=$LOCATION_ID \
        --display_name="My First Agent" \
        multi_tool_agent
```

`region` については [Vertex AI Agent Builder locations](https://docs.cloud.google.com/agent-builder/locations#supported-regions-agent-engine) ページで
サポートリージョンを確認してください。
`adk deploy agent_engine` の CLI オプションについては [ADK CLI リファレンス](https://google.github.io/adk-docs/api-reference/cli/cli.html#adk-deploy-agent-engine)
を参照してください。

### デプロイコマンドの出力

成功時は次の出力が表示されます。

```shell
Creating AgentEngine
Create AgentEngine backing LRO: projects/123456789/locations/us-central1/reasoningEngines/751619551677906944/operations/2356952072064073728
View progress and logs at https://console.cloud.google.com/logs/query?project=hopeful-sunset-478017-q0
AgentEngine created. Resource name: projects/123456789/locations/us-central1/reasoningEngines/751619551677906944
To use this AgentEngine in another session:
agent_engine = vertexai.agent_engines.get('projects/123456789/locations/us-central1/reasoningEngines/751619551677906944')
Cleaning up the temp folder: /var/folders/k5/pv70z5m92s30k0n7hfkxszfr00mz24/T/agent_engine_deploy_src/20251219_134245
```

上記例では `RESOURCE_ID` が `751619551677906944` になります。
この ID はエージェントを利用する際に他の値とともに必要になります。

## Agent Engine 上でのエージェント利用

ADK プロジェクトのデプロイが完了すると、Vertex AI SDK、Python requests ライブラリ、または REST API クライアントでエージェントにクエリできます。
このセクションでは、エージェントとのやり取りに必要な値と REST API URL の作成方法を示します。

Agent Engine でエージェントを利用するには以下が必要です:

*   **PROJECT_ID**（例: "my-project-id"）: [プロジェクト詳細ページ](https://console.cloud.google.com/iam-admin/settings)
*   **LOCATION_ID**（例: "us-central1"）: デプロイ時に使用した場所
*   **RESOURCE_ID**（例: "751619551677906944"）: [Agent Engine UI](https://console.cloud.google.com/vertex-ai/agents/agent-engines) で確認

クエリ URL の構造は以下です。

```shell
https://$(LOCATION_ID)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION_ID)/reasoningEngines/$(RESOURCE_ID):query
```

この URL 構造を使ってリクエストを作成します。
REST API の詳細は Agent Engine ドキュメントの
[ADK エージェントの使用](https://docs.cloud.google.com/agent-builder/agent-engine/use/adk#rest-api)
および
[デプロイ済みエージェントの管理](https://docs.cloud.google.com/agent-builder/agent-engine/manage/overview)
を確認してください。
ADK エージェントのテストや操作については
[Agent Engine でデプロイされたエージェントをテストする](/adk-docs/deploy/agent-engine/test/)
を参照してください。

### 監視と検証

*   Google Cloud Console の [Agent Engine UI](https://console.cloud.google.com/vertex-ai/agents/agent-engines) でデプロイ状態を監視できます。
*   詳細は Agent Engine ドキュメントの
    [エージェントのデプロイ](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/deploy)
    と
    [デプロイ済みエージェントの管理](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/manage/overview)
    を参照してください。

## デプロイ済みエージェントのテスト

ADK エージェントのデプロイが完了したら、新しいホステッド環境でワークフローをテストしてください。
詳細は
[Agent Engine 上でデプロイ済みエージェントをテスト](/adk-docs/deploy/agent-engine/test/)
を参照してください。
