---
catalog_title: Datadog
catalog_description: LLM アプリケーションの開発、評価、監視
catalog_icon: /integrations/assets/datadog.png
catalog_tags: ["observability"]
---


# ADK の Datadog 可観測性

<div class="language-support-tag">
    <span class="lst-supported">Supported in:</span>
    <span class="lst-python">Python</span>
</div>

[Datadog LLM
Observability](https://www.datadoghq.com/product/llm-observability/) が AI を支援
エンジニア、データ サイエンティスト、アプリケーション開発者が
LLM アプリケーションをすばやく開発、評価、監視できるよう支援します。
構造化された実験、AI エージェント全体のエンドツーエンド トレース、
評価により、出力品質、パフォーマンス、コスト、全体的なリスクを
自信を持って改善できます。

## 概要

Datadog LLM 可観測性は [Google ADK で構築したエージェントを自動的に計測し、
トレース](https://docs.datadoghq.com/llm_observability/instrumentation/auto_instrumentation?tab=python#google-adk)でき、
次のことが可能になります。

- **エージェントの実行と対話を観察** - すべてを自動的にキャプチャします
  エージェントの実行、ツールの呼び出し、エージェント内でのコードの実行
- 基盤となる Google GenAI SDK で行われた **LLM の呼び出しと応答をキャプチャ**
- **エラー率、トークンの使用量、コストを提供することで問題をデバッグします**。
  LLM 呼び出しとツールの使用状況に関するすぐに使える評価

## 前提条件

[Datadog account](https://www.datadoghq.com/) をお持ちでない場合は、サインアップしてください。
1 つと [get your API
key](https://docs.datadoghq.com/account_management/api-app-keys/#api-keys)。

## インストール

必要なパッケージをインストールします。

```bash
pip install ddtrace
```

## セットアップ

### Google ADK を使用してアプリケーションを作成する

Google ADK を使用するアプリケーションをお持ちでない場合は、次の手順に従ってください。
[ADK Getting Started Guide](https://google.github.io/adk-docs/get-started/)から
サンプル ADK エージェントを作成します。

### 環境変数を構成する

以下の環境ではMLアプリケーション名を指定する必要があります。
変数。 ML アプリケーションは、LLM 可観測性トレースのグループです。
特定の LLM ベースのアプリケーションに関連付けられています。 [ML Application Naming
Guidelines](https://docs.datadoghq.com/llm_observability/instrumentation/sdk?tab=python#application-naming-guidelines)を参照
ML アプリケーション名の制限の詳細については、「ML アプリケーション名に関する制限」を参照してください。

```shell
export DD_API_KEY=<YOUR_DD_API_KEY>
export DD_SITE=<YOUR_DD_SITE>
export DD_LLMOBS_ENABLED=true
export DD_LLMOBS_ML_APP=<YOUR_ML_APP_NAME>
export DD_LLMOBS_AGENTLESS_ENABLED=true
export DD_APM_TRACING_ENABLED=false  # Only set this if you are not using Datadog APM
```

これらの変数は、アプリケーションを実行する前にエクスポートする必要があります。
それらを次の `ddtrace-run` コマンドで使用できます。
エージェントの `.env` ファイル。

### アプリケーションを実行する

環境変数を設定したら、
アプリケーションを作成し、LLM ベースのアプリケーションの観察を開始します。

```shell
ddtrace-run adk run my_agent
```

## 観察してください

[Datadog LLM Observability Traces
View](https://app.datadoghq.com/llm/traces) に移動して、によって生成されたトレースを確認します。
アプリケーション。

![datadog-observability.png](./assets/datadog-observability.png)

## サポートとリソース
- [Datadog LLM Observability](https://www.datadoghq.com/product/llm-observability/)
- [Datadog Support](https://docs.datadoghq.com/help/)
