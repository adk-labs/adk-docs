---
catalog_title: Google Cloud Parameter Manager
catalog_description: ADK エージェントのランタイム構成パラメータとシークレットを安全に管理および取得します
catalog_icon: /integrations/assets/parameter_manager.png
catalog_tags: ["google"]
---

# ADK向けの Parameter Manager 連携

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.30.0</span>
</div>

[Google Cloud Parameter Manager](https://docs.cloud.google.com/secret-manager/parameter-manager/docs/overview) 連携は、Agent Development Kit (ADK) エージェントが Google Cloud Parameter Manager サービスに接続し、ランタイムにレンダリングされたパラメータ値を取得するための標準インターフェースを提供します。このモジュールにより、Google Cloud Parameter Manager サービスをエージェントの指示（instruction）とツール構成の単一の真実のソース（single source of truth）として使用できます。

## 主なユースケース

Parameter Manager 連携は以下の操作를 서포트합니다:

*   **動的な指示의 업데이트 (Dynamic instruction updates)**: プロンプトインジェクション攻撃を防ぐ, 必須の免責事項リソースを更新する, あるいはコードを再デプロイすることなくエージェントのトーンを即座に調整するために, パラメータを即座に発行できます。
*   **フィーチャーフラグとパラメータの管理 (Feature flag and parameter management)**: 構成を JSON ペ이로드로 저장하고 ツールコンテキストを通じて取得することで, クエリレートを下げたり, テスト用と本番用の API エンドポイントを切り替えたりできます。
*   **入出力ペアによる精度向上 (Accuracy improvement with input and output pairs)**: フューショット（few-shot）の例を YAML ファイルとして保存し, セッション状態にロードしてエージェントのパフォーマンスを段階的に改善できます。
*   **ツールのリアルタイム権限付与 (Just-in-time tool authorization)**: 初期化コードで安全でない静的 API キーを使用する代わりに, 必要に応じてシークレットをメモリにリアルタイムでロードできます。
*   **安全なマルチテナントワークフロー (Secure multi-tenant workflows)**: ユーザーにマッピングされる Parameter Manager ID を保存し, コールバックを使用して解決済みの OAuth トークンでセッション状態を復元できます。
*   **暗号化されたシステムタスク (Encrypted system tasks)**: バックグラウンドでのポーリングタスク中に, メインデータベースのパスワードが LLM の会話履歴に入るのを防ぎます。
*   **マルチリージョンデプロイ (Multi-region deployments)**: グローバルデプロイ全体で共有ロジックを維持しながら, 地域ごとの Parameter Manager のオーバーライドを使用して現地の通貨や連絡先情報を適用できます。

## 前提条件

連携を構成する前に, 以下の要件を満たす必要があります:

- **必須ソフトウェアバージョン**: ADK Python バージョン v1.30.0 以上
- **必須アカウント / API**: [**Parameter Manager API**](https://docs.cloud.google.com/secret-manager/parameter-manager/docs/prepare-environment#enable_api)、[**Secret Manager API**](https://docs.cloud.google.com/secret-manager/docs/configuring-secret-manager)、および **Agent Development Kit API** が有効化された [Google Cloud プロジェクト](https://docs.cloud.google.com/resource-manager/docs/creating-managing-projects)。

セットアップ手順は次のとおりです:

1.  [ADKでエージェントをセットアップします](/get-started/)。
2.  [パラメータを作成します](https://docs.cloud.google.com/secret-manager/parameter-manager/docs/create-parameter)。
3.  エージェントの ID に [Parameter Manager Parameter Accessor](https://docs.cloud.google.com/iam/docs/roles-permissions/parametermanager#parametermanager.parameterAccessor) IAM ロール（`roles/parametermanager.parameterAccessor`）を付与します。このロールにより, エージェントはランタイムにパラメータ構成をレンダリングできます。
4.  パラメータにシークレットが埋め込まれている場合は, パラメータリソースに [Secret Manager Secret Accessor](https://docs.cloud.google.com/iam/docs/roles-permissions/secretmanager#secretmanager.secretAccessor) ロール（`roles/secretmanager.secretAccessor`）を付与します。このクロスサービス権限により, Parameter Manager はエージェントの代わりに参照されたシークレットを解決できます。詳細については, [パラメータに Secret Manager Secret Accessor ロールを付与する](https://docs.cloud.google.com/secret-manager/parameter-manager/docs/reference-secrets-in-parameter#grant_the_secret_manager_secret_accessor_role_to_the_parameter) を参照してください。

## インストール

ADK 拡張パッケージをインストールして, Parameter Manager 連携を有効にします:

```bash
pip install "google-adk[extensions]"
```

## エージェントでの使用

次の例は, 資格情報を構成し, 安全にパラメータを取得する, 完全で動作するコードを示しています。

### グローバルパラメータ

```python
import os

from google.adk import Agent
from google.adk.integrations.parameter_manager.parameter_client import ParameterManagerClient

# グローバル Parameter Manager からパラメータを取得
project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
parameter_id = os.environ.get("ADK_TEST_PARAMETER_ID")
parameter_version = os.environ.get("ADK_TEST_PARAMETER_VERSION", "latest")

if not project_id or not parameter_id:
    raise ValueError("GOOGLE_CLOUD_PROJECT and ADK_TEST_PARAMETER_ID environment variables must be set.")

resource_name = f"projects/{project_id}/locations/global/parameters/{parameter_id}/versions/{parameter_version}"

print("Fetching parameter from global Parameter Manager...")
# Parameter Manager クライアントを初期化
client = ParameterManagerClient()

# パ라미터 가져오기
try:
    parameter_payload = client.get_parameter(resource_name)
    print("Successfully fetched parameter.")
except Exception as e:
    print(f"Error fetching parameter: {e}")
    raise e

# エージェントを初期化
root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
)

print("Agent initialized successfully.")
```

### リージョンパラメータ

```python
import os

from google.adk import Agent
from google.adk.integrations.parameter_manager.parameter_client import ParameterManagerClient

# リージョン Parameter Manager からパラメータを取得
project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
location = os.environ.get("GOOGLE_CLOUD_PROJECT_LOCATION")
parameter_id = os.environ.get("ADK_TEST_PARAMETER_ID")
parameter_version = os.environ.get("ADK_TEST_PARAMETER_VERSION", "latest")

if not project_id or not location or not parameter_id:
    raise ValueError("GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_PROJECT_LOCATION, and ADK_TEST_PARAMETER_ID environment variables must be set.")

resource_name = f"projects/{project_id}/locations/{location}/parameters/{parameter_id}/versions/{parameter_version}"

print(f"Fetching parameter from regional Parameter Manager ({location})...")
# Parameter Manager クライアントを初期화 (リージョン)
client = ParameterManagerClient(location=location)

# パラメータを取得
try:
    parameter_payload = client.get_parameter(resource_name)
    print("Successfully fetched parameter.")
except Exception as e:
    print(f"Error fetching parameter: {e}")
    raise e

# エージェントを初期化
root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
)

print("Agent initialized successfully.")
```

## リソース

-   [Parameter Manager ドキュメント](https://docs.cloud.google.com/secret-manager/parameter-manager/docs/overview)
-   [ADK GitHub リポジトリ](https://github.com/google/adk-python)
-   [フューショット（few-shot）の例を含める](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/prompts/few-shot-examples)
