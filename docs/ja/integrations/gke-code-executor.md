---
catalog_title: GKE Code Executor
catalog_description: 安全かつスケーラブルな GKE 環境で AI 生成コードを実行します
catalog_icon: /adk-docs/integrations/assets/gke.png
catalog_tags: ["code","google"]
---

# ADK 向け Google Cloud GKE Code Executor ツール

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.14.0</span>
</div>

GKE Code Executor (`GkeCodeExecutor`) は、gVisor によるワークロード分離を使う
GKE (Google Kubernetes Engine) Sandbox 環境を活用し、
LLM 生成コードを安全かつスケーラブルに実行する方法を提供します。
各コード実行リクエストごとに、強化された Pod 構成を持つ一時的な
サンドボックス Kubernetes Job を動的に作成します。
セキュリティと分離が重要な GKE 本番環境で使用すべき実行器です。

## 仕組み

コード実行リクエストを受けると、`GkeCodeExecutor` は次を実行します:

1.  **ConfigMap を作成:** 実行対象 Python コードを保存する Kubernetes ConfigMap を作成します。
2.  **サンドボックス Pod を作成:** 新しい Kubernetes Job を作成し、そこから強化セキュリティコンテキストと gVisor ランタイム有効化済み Pod を作成します。ConfigMap のコードを Pod にマウントします。
3.  **コードを実行:** コードはサンドボックス Pod 内で実行され、基盤ノードや他ワークロードから分離されます。
4.  **結果を取得:** 実行の標準出力と標準エラーを Pod ログから取得します。
5.  **リソースをクリーンアップ:** 実行完了後、Job と関連 ConfigMap を自動削除し、成果物を残しません。

## 主な利点

*   **強化されたセキュリティ:** コードはカーネルレベル分離を持つ gVisor サンドボックス環境で実行されます。
*   **一時実行環境:** 各実行は独立した一時 Pod で行われ、実行間の状態持ち越しを防ぎます。
*   **リソース制御:** 実行 Pod の CPU/メモリ制限を設定してリソース乱用を防げます。
*   **スケーラビリティ:** 多数のコード実行を並列に処理でき、基盤ノードのスケジューリング/スケーリングは GKE が担当します。

## システム要件

GKE Code Executor ツールで ADK プロジェクトを正常にデプロイするには、
次の要件を満たす必要があります:

- **gVisor 有効ノードプール**を持つ GKE クラスタ。
- エージェントのサービスアカウントに次を許可する特定の **RBAC 権限**:
    - 各実行リクエストごとの **Jobs** 作成・監視・削除。
    - Job の Pod へコード注入するための **ConfigMaps** 管理。
    - 実行結果取得のための **Pods** 一覧取得と **logs** 読み取り。
- GKE extras を含むクライアントライブラリのインストール: `pip install google-adk[gke]`

完全でそのまま使える設定例は
[deployment_rbac.yaml](https://github.com/google/adk-python/blob/main/contributing/samples/gke_agent_sandbox/deployment_rbac.yaml)
を参照してください。ADK ワークフローの GKE デプロイ詳細は
[Deploy to Google Kubernetes Engine (GKE)](/adk-docs/deploy/gke/) を参照してください。

=== "Python"

    ```python
    from google.adk.agents import LlmAgent
    from google.adk.code_executors import GkeCodeExecutor

    # Initialize the executor, targeting the namespace where its ServiceAccount
    # has the required RBAC permissions.
    # This example also sets a custom timeout and resource limits.
    gke_executor = GkeCodeExecutor(
        namespace="agent-sandbox",
        timeout_seconds=600,
        cpu_limit="1000m",  # 1 CPU core
        mem_limit="1Gi",
    )

    # The agent now uses this executor for any code it generates.
    gke_agent = LlmAgent(
        name="gke_coding_agent",
        model="gemini-2.0-flash",
        instruction="You are a helpful AI agent that writes and executes Python code.",
        code_executor=gke_executor,
    )
    ```

## 設定パラメータ

`GkeCodeExecutor` は次のパラメータで設定できます:

| Parameter            | Type   | Description                                                                             |
| -------------------- | ------ | --------------------------------------------------------------------------------------- |
| `namespace`          | `str`  | 実行 Job を作成する Kubernetes 名前空間。デフォルトは `"default"`。 |
| `image`              | `str`  | 実行 Pod に使用するコンテナイメージ。デフォルトは `"python:3.11-slim"`。         |
| `timeout_seconds`    | `int`  | コード実行タイムアウト (秒)。デフォルトは `300`。                           |
| `cpu_requested`      | `str`  | 実行 Pod の要求 CPU 量。デフォルトは `"200m"`。                   |
| `mem_requested`      | `str`  | 実行 Pod の要求メモリ量。デフォルトは `"256Mi"`。               |
| `cpu_limit`          | `str`  | 実行 Pod が使用可能な最大 CPU 量。デフォルトは `"500m"`。                  |
| `mem_limit`          | `str`  | 実行 Pod が使用可能な最大メモリ量。デフォルトは `"512Mi"`。              |
| `kubeconfig_path`    | `str`  | 認証に使用する kubeconfig ファイルパス。in-cluster 設定またはローカル既定 kubeconfig へフォールバックします。 |
| `kubeconfig_context` | `str`  | 使用する `kubeconfig` コンテキスト。  |
