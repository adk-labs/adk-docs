---
catalog_title: GKE Code Executor
catalog_description: 安全かつスケーラブルな GKE 環境で AI 生成コードを実行します
catalog_icon: /integrations/assets/gke.png
catalog_tags: ["code","google"]
---

# ADK 向け Google Cloud GKE Code Executor ツール

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.14.0</span>
</div>

GKE Code Executor (`GkeCodeExecutor`) は、Google Kubernetes Engine (GKE) を
活用して LLM が生成したコードを安全かつスケーラブルに実行する方法を
提供します。セキュリティと分離が重要な GKE 本番環境では、この実行器を
利用するべきです。次の 2 つの実行モードをサポートします。

1.  **Sandbox Mode（推奨）:** [Agent Sandbox](https://github.com/kubernetes-sigs/agent-sandbox)
    クライアントを利用し、テンプレートからオンデマンドで作成された
    サンドボックスインスタンス内でコードを実行します。このモードは
    [事前ウォーム済みサンドボックス](https://docs.cloud.google.com/kubernetes-engine/docs/how-to/agent-sandbox#create_a_sandboxtemplate_and_sandboxwarmpool)
    を活用して低遅延を実現し、サンドボックス環境とのより直接的な
    やり取りをサポートします。
2.  **Job Mode:** ワークロード分離のために gVisor ベースの GKE Sandbox
    環境を使用します。各コード実行リクエストごとに、強化された Pod 構成を
    持つ一時的なサンドボックス Kubernetes Job を動的に作成します。
    このモードは後方互換性のために提供されます。

## 実行モード

### Sandbox Mode (`executor_type="sandbox"`)

推奨されるモードです。`k8s-agent-sandbox` クライアントライブラリを使用し、
GKE クラスタ内の Agent Sandbox を作成して通信します。コード実行リクエストが
あると、次の手順を実行します。

1.  指定したテンプレートを使って `SandboxClaim` を作成します。
2.  サンドボックスインスタンスの準備完了を待ちます。
3.  確保したサンドボックス内でコードを実行します。
4.  標準出力と標準エラーを取得します。
5.  `SandboxClaim` を削除し、それに伴ってサンドボックスインスタンスも
    クリーンアップします。

この方式は事前ウォーム済みサンドボックスを利用し、Agent Sandbox
コントローラが提供する起動時間最適化を活かすため、Job Mode より高速です。

**主な利点:**

Job Mode のすべての利点に加えて、Sandbox Mode には次の特徴があります。

*   **低遅延:** 完全な Kubernetes Job を作成する方式より起動時間を短縮できます。
*   **管理された環境:** サンドボックスのライフサイクル管理に Agent Sandbox
    フレームワークを活用します。

**前提条件:**

*   GKE クラスタに既存の Agent Sandbox デプロイが必要です。これには
    サンドボックスコントローラとその拡張（例: sandbox claim controller、
    sandbox warmpool controller）、router、gateway、関連する
    `SandboxTemplate` リソース（例: `python-sandbox-template`）が含まれます。
*   ADK エージェントが `SandboxClaim` リソースを作成・削除できるための
    必要な RBAC 権限が必要です。

### Job Mode (`executor_type="job"`)

このモードは後方互換性のために提供されます。コード実行リクエストがあると、
`GkeCodeExecutor` は次の手順を実行します。

1.  **ConfigMap を作成:** 実行する Python コードを保存するための Kubernetes
    ConfigMap を作成します。
2.  **サンドボックス Pod を作成:** 新しい Kubernetes Job を作成し、その Job が
    強化されたセキュリティコンテキストと gVisor ランタイムを有効にした Pod を
    作成します。ConfigMap のコードはこの Pod にマウントされます。
3.  **コードを実行:** コードはサンドボックス Pod 内で実行され、基盤ノードや
    他のワークロードから分離されます。
4.  **結果を取得:** 実行時の標準出力と標準エラーストリームを Pod のログから
    取得します。
5.  **リソースをクリーンアップ:** 実行完了後、Job と関連する ConfigMap を
    自動的に削除し、成果物を残しません。

**主な利点:**

*   **強化されたセキュリティ:** コードはカーネルレベルの分離を提供する
    gVisor サンドボックス環境で実行されます。
*   **一時的な実行環境:** 各コード実行は独立した一時 Pod で実行され、
    実行間の状態引き継ぎを防ぎます。
*   **リソース制御:** 実行 Pod の CPU / メモリ制限を設定してリソース乱用を
    防げます。
*   **スケーラビリティ:** 大量のコード実行を並列で処理でき、基盤ノードの
    スケジューリングとスケーリングは GKE が担います。
*   **最小限のセットアップ:** 標準的な GKE 機能と gVisor のみを前提にします。

## システム要件

GKE Code Executor ツールを使って ADK プロジェクトを正しくデプロイするには、
次の要件を満たす必要があります。

- **gVisor が有効なノードプール**を持つ GKE クラスタ。
  これは Job Mode のデフォルトイメージと一般的な Agent Sandbox テンプレートの
  両方で必要です。
- エージェントのサービスアカウントに特定の **RBAC 権限**が必要です。
    - **Job Mode:** **Jobs** の作成・監視・削除、**ConfigMaps** の管理、
      **Pods** の一覧取得と **logs** の読み取りが必要です。Job Mode 向けの
      完全ですぐ使える設定については、
      [deployment_rbac.yaml](https://github.com/google/adk-python/blob/main/contributing/samples/gke_agent_sandbox/deployment_rbac.yaml)
      サンプルを参照してください。
    - **Sandbox Mode:** Agent Sandbox がデプロイされている名前空間内で
      **SandboxClaim** および **Sandbox** リソースを作成、取得、監視、削除する
      権限が必要です。
- 適切な extras を含めてクライアントライブラリをインストールします:
  `pip install google-adk[gke]`

## 構成パラメータ

`GkeCodeExecutor` は次のパラメータで構成できます。

| Parameter | Type | Description |
| ---------------------- | ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `namespace` | `str` | 実行リソース（Job または SandboxClaim）を作成する Kubernetes 名前空間です。デフォルトは `"default"` です。 |
| `executor_type` | `Literal["job", "sandbox"]` | 実行モードを指定します。デフォルトは `"job"` です。 |
| `image` | `str` | （Job Mode）実行 Pod に使用するコンテナイメージです。デフォルトは `"python:3.11-slim"` です。 |
| `timeout_seconds` | `int` | （Job Mode）コード実行のタイムアウト秒数です。デフォルトは `300` です。 |
| `cpu_requested` | `str` | （Job Mode）実行 Pod が要求する CPU 量です。デフォルトは `"200m"` です。 |
| `mem_requested` | `str` | （Job Mode）実行 Pod が要求するメモリ量です。デフォルトは `"256Mi"` です。 |
| `cpu_limit` | `str` | （Job Mode）実行 Pod が利用できる最大 CPU 量です。デフォルトは `"500m"` です。 |
| `mem_limit` | `str` | （Job Mode）実行 Pod が利用できる最大メモリ量です。デフォルトは `"512Mi"` です。 |
| `kubeconfig_path` | `str` | 認証に使用する kubeconfig ファイルのパスです。in-cluster config またはローカルの既定 kubeconfig にフォールバックします。 |
| `kubeconfig_context` | `str` | 使用する `kubeconfig` コンテキストです。 |
| `sandbox_gateway_name` | `str \| None` | （Sandbox Mode）利用するサンドボックスゲートウェイ名です。任意です。 |
| `sandbox_template` | `str \| None` | （Sandbox Mode）利用する `SandboxTemplate` 名です。デフォルトは `"python-sandbox-template"` です。 |

## 使用例

=== "Python - Sandbox Mode（推奨）"

    ```python
    from google.adk.agents import LlmAgent
    from google.adk.code_executors import GkeCodeExecutor
    from google.adk.code_executors import CodeExecutionInput
    from google.adk.agents.invocation_context import InvocationContext

    # Sandbox Mode 用の実行器を初期化
    # 名前空間には SandboxClaims と Sandbox への RBAC 権限が必要です
    gke_sandbox_executor = GkeCodeExecutor(
        namespace="agent-sandbox-system",  # 通常は agent-sandbox がインストールされている場所
        executor_type="sandbox",
        sandbox_template="python-sandbox-template",
        sandbox_gateway_name="your-gateway-name", # 任意
    )

    # 直接実行の例:
    ctx = InvocationContext()
    result = gke_sandbox_executor.execute_code(ctx, CodeExecutionInput(code="print('Hello from Sandbox Mode')"))
    print(result.stdout)

    # Agent と組み合わせる例:
    gke_sandbox_agent = LlmAgent(
        name="gke_sandbox_coding_agent",
        model="gemini-2.5-flash",
        instruction="あなたはサンドボックスを使って Python コードを書いて実行する有用な AI エージェントです。",
        code_executor=gke_sandbox_executor,
    )
    ```

=== "Python - Job Mode"

    ```python
    from google.adk.agents import LlmAgent
    from google.adk.code_executors import GkeCodeExecutor
    from google.adk.code_executors import CodeExecutionInput
    from google.adk.agents.invocation_context import InvocationContext

    # Job Mode 用の実行器を初期化
    # 名前空間には Jobs、ConfigMaps、Pods、Logs への RBAC 権限が必要です
    gke_executor = GkeCodeExecutor(
        namespace="agent-ns",
        executor_type="job",
        timeout_seconds=600,
        cpu_limit="1000m",  # 1 CPU core
        mem_limit="1Gi",
    )

    # 直接実行の例:
    ctx = InvocationContext()
    result = gke_executor.execute_code(ctx, CodeExecutionInput(code="print('Hello from Job Mode')"))
    print(result.stdout)

    # Agent と組み合わせる例:
    gke_agent = LlmAgent(
        name="gke_coding_agent",
        model="gemini-2.5-flash",
        instruction="あなたは Python コードを書いて実行する有用な AI エージェントです。",
        code_executor=gke_executor,
    )
    ```
