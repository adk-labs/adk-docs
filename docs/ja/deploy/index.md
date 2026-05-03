# エージェントのデプロイ

ADK でエージェントをビルドしてテストしたら、次のステップは、本番環境でアクセス、クエリ、利用できるようにすること、または他のアプリケーションと統合できるようにデプロイすることです。デプロイにより、エージェントはローカル開発マシンからスケーラブルで信頼性の高い環境へ移行します。

<img src="../assets/deploy-agent.png" alt="エージェントのデプロイ">

## デプロイ オプション

ADK エージェントは、本番環境への準備状況やカスタムの柔軟性に関する要件に応じて、さまざまな環境へデプロイできます。

### Agent Platform の Agent Runtime

[Agent Runtime](agent-runtime/index.md) は、ADK などのフレームワークで構築した AI エージェントをデプロイ、管理、スケーリングするために設計された、Google Cloud のフルマネージドな自動スケーリング サービスです。

[Agent Runtime へのエージェントのデプロイ](agent-runtime/index.md) の詳細をご覧ください。

### Cloud Run

[Cloud Run](https://cloud.google.com/run) は、エージェントをコンテナベースのアプリケーションとして実行できる、Google Cloud のマネージド自動スケーリング コンピューティング プラットフォームです。

[Cloud Run へのエージェントのデプロイ](cloud-run.md) の詳細をご覧ください。

### Google Kubernetes Engine (GKE)

[Google Kubernetes Engine (GKE)](https://cloud.google.com/kubernetes-engine) は、エージェントをコンテナ化された環境で実行できる Google Cloud のマネージド Kubernetes サービスです。デプロイをより細かく制御したい場合や、オープンモデルを実行する場合に適した選択肢です。

[GKE へのエージェントのデプロイ](gke.md) の詳細をご覧ください。

### その他のコンテナ対応インフラストラクチャ

エージェントを手動でコンテナ イメージにパッケージ化し、コンテナ イメージをサポートする任意の環境で実行できます。たとえば Docker や Podman を使ってローカルで実行できます。オフラインまたは切断された環境で実行したい場合や、Google Cloud に接続しないシステムで実行する場合に適しています。

[Cloud Run へのエージェントのデプロイ](cloud-run.md#deployment-commands) の手順に従ってください。gcloud CLI の「デプロイ コマンド」セクションに、FastAPI エントリ ポイントと Dockerfile の例があります。
