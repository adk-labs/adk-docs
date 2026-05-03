# エージェント ランタイムにデプロイする

<div class="language-support-tag" title="Agent Runtime currently supports only Python.">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

Google クラウド エージェント プラットフォーム
[Agent Runtime](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)
開発者がエージェントを拡張および管理するのに役立つモジュール式サービスのセットです。
生産。 Agent Runtime ランタイムを使用すると、実稼働環境にエージェントをデプロイできます。
エンドツーエンドの管理されたインフラストラクチャを使用するため、インテリジェントな作成に集中できます。
そして影響力のあるエージェント。 ADK エージェントをエージェント ランタイムにデプロイすると、コード
より大きなセットの一部である *Agent Runtime ランタイム* 環境で実行されます。
Agent Runtime 製品によって提供されるエージェント サービスの概要。

このガイドには、さまざまなサービスを提供する次の展開パスが含まれています。
目的:

* **[Standard deployment](/deploy/agent-runtime/deploy/)**: フォローする
    ADK エージェントのエージェントへのデプロイを慎重に管理する場合は、この標準デプロイ パスを使用します。
    ランタイム ランタイム。このデプロイ パスでは、Cloud Console、ADK コマンドラインを使用します。
    インターフェイスにアクセスし、段階的な手順を説明します。このパスが推奨されます
    すでに Google Cloud プロジェクトの構成に慣れているユーザー向け
    実稼働デプロイメントの準備をしているユーザー。

* **[Agents CLI deployment](/deploy/agent-runtime/agents-cli/)**:
    この高速導入パスに従って、完全に構成された Google をセットアップします。
    CI/CD、コードとしてのインフラストラクチャ、およびデプロイメント パイプラインを備えたクラウド環境
    ADK エージェント用。課金が有効になっている Google Cloud プロジェクトが必要です。
    エージェント プラットフォームのエージェント CLI は、ADK プロジェクトを迅速にデプロイするのに役立ちます。
    のコア機能を拡張する高度なサービス構成が含まれています。
    より成熟したユースケース向けの Agent Runtime ランタイム。

!!! note "Google Cloud 上のエージェント ランタイム サービス"

    Agent Runtime は有料サービスであるため、利用すると費用が発生する場合があります。
    無料アクセス層を超えています。詳細については、
    [Agent Runtime pricing page](https://cloud.google.com/vertex-ai/pricing#vertex-ai-agent-engine)。

## デプロイペイロード {#payload}

ADK エージェント プロジェクトをエージェント ランタイムにデプロイすると、次の内容になります。
サービスにアップロードされたもの:

- ADK エージェント コード
- ADK エージェント コードで宣言された依存関係

デプロイメントには、ADK API サーバーまたは ADK Web ユーザーは「含まれません」
インターフェースライブラリ。 Agent Runtime サービスは、ADK API のライブラリを提供します
サーバー機能。
