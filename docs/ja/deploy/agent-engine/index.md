# Vertex AI Agent Engine にデプロイ

<div class="language-support-tag" title="Vertex AI Agent Engine は現在 Python のみをサポートします。">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

Google Cloud Vertex AI
[Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview) は
開発者がエージェントを本番環境でスケールさせ、ガバナンスできるようにするモジュール型サービス群です。
Agent Engine ランタイムを使うと、エンドツーエンドで管理されたインフラ上にエージェントをデプロイできるため、
知的でインパクトのあるエージェントに注力できます。ADK エージェントを Agent Engine にデプロイすると、
そのコードは Agent Engine 製品が提供するエージェントサービス群の一部である
*Agent Engine ランタイム* 環境で実行されます。

このガイドには用途別の次のデプロイパスが含まれます。

*   **[標準デプロイ](/adk-docs/deploy/agent-engine/deploy/)**: 既存の
    Google Cloud プロジェクトを持ち、ADK エージェントを Agent Engine ランタイムへ丁寧にデプロイしたい場合はこの方法を使ってください。
    このパスでは Cloud Console、ADK コマンドラインインターフェイスを用いて、手順を追って実装します。
    Google Cloud プロジェクトの構築に慣れたユーザーや、本番デプロイを検討しているユーザー向けに推奨されます。

*   **[Agent Starter Pack デプロイ](/adk-docs/deploy/agent-engine/asp/)**:
    既存の Google Cloud プロジェクトがなく、開発とテスト目的で特にプロジェクトを新規作成する場合は、この高速デプロイを使います。
    Agent Starter Pack（ASP）は ADK プロジェクトのデプロイを迅速化し、ADK エージェントが Agent Engine
    ランタイムで動作するために必須ではない一部の Google Cloud サービスを設定します。

!!! note "Google Cloud の Agent Engine サービス"

    Agent Engine は有償サービスです。無料アクセス枠を超えると料金が発生する可能性があります。
    詳細は [Agent Engine 料金ページ](https://cloud.google.com/vertex-ai/pricing#vertex-ai-agent-engine) を参照してください。

## デプロイペイロード {#payload}

ADK エージェントプロジェクトを Agent Engine にデプロイすると、以下の内容がサービスへアップロードされます。

- ADK エージェントコード
- ADK エージェントコード内で宣言された依存関係

デプロイには ADK API サーバーや ADK Web UI ライブラリは含まれません。
ADK API サーバー機能は Agent Engine サービス側が提供するライブラリで実装されます。
