---
catalog_title: Google Cloud Secret Manager
catalog_description: LLM に公開することなく、ランタイムにシークレットを安全に取得します
catalog_icon: /integrations/assets/secret_manager.png
catalog_tags: ["google"]
---

# ADK向けの Secret Manager 連携

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.29.0</span>
</div>

[Secret Manager](https://docs.cloud.google.com/secret-manager/docs/overview) 連携は、ADK 에이전트가 런타임에 민감한 자격 증명(예: API 키, 데이터베이스 패스워드, 개인 키)을 안전하게 가져올 수 있는 표준 인터페이스를 제공합니다. 이 방식을 사용하면 소스 코드에 민감한 정보를 하드코딩하지 않고, LLM의 컨텍스트 창, 대화 기록 또는 관측 가능성(observability) 로그에 노출되지 않도록 안전하게 보호할 수 있습니다.

## 主なユースケース

- **ツールのリアルタイム権限付与 (Just-in-time tool authorization)**: エージェントの初期化コードに静的な API キーを格納することは安全ではありません。この連携を使用すると、ADK エージェントはランタイムに Secret Manager から資格情報を動的に取得し、必要なときにのみキーをメモリにロードします。
- **安全なマルチテナントワークフロー (Secure multi-tenant workflows)**: フロントエンドから生のユーザー トークンを渡すのを避けるため、エージェントはユーザー ID を特定の Secret Manager リソースにマッピングできます。 `before_agent_callback` フックは、ユーザーのシークレットを動的に取得し、 `session.state` OAuth トークンを安全に復元します。
- **암호화된 시스템 작업 (Encrypted system tasks)**: データベースのポーリングなどのバックグラウンドのシステムタスクは、ツールロジックの内部で Secret Manager から直接資格情報を取得します。これにより、パスワードが LLM の会話履歴に入るのを防ぎ、モデルには実行の要約のみが公開されます。

## 前提条件

- **必須ソフトウェアバージョン**: ADK Python バージョン v1.29.0 以上
- **必須アカウント / API**: [**Secret Manager API**](https://docs.cloud.google.com/secret-manager/docs/configuring-secret-manager) と **Agent Development Kit API** が有効化された [Google Cloud プロジェクト](https://docs.cloud.google.com/resource-manager/docs/creating-managing-projects)。

セットアップ手順は次のとおりです:

1.  [ADKでエージェントをセットアップします](/get-started/)。
2.  Secret Manager で [シークレットを作成](https://docs.cloud.google.com/secret-manager/docs/creating-and-accessing-secrets)します（API キーなど）。
3.  エージェントの ID に [`Secret Manager Secret Accessor`](https://docs.cloud.google.com/iam/docs/roles-permissions/secretmanager#secretmanager.secretAccessor) IAM ロールを付与します。

## インストール

```bash
pip install "google-adk[extensions]"
```

## エージェントでの使用

```python
import os

from google.adk import Agent
from google.adk.integrations.secret_manager.secret_client import SecretManagerClient

# グローバル Secret Manager からシークレットを取得
project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
secret_id = os.environ.get("ADK_TEST_SECRET_ID")
secret_version = os.environ.get("ADK_TEST_SECRET_VERSION", "latest")

if not project_id or not secret_id:
    raise ValueError("GOOGLE_CLOUD_PROJECT and ADK_TEST_SECRET_ID environment variables must be set.")

resource_name = f"projects/{project_id}/secrets/{secret_id}/versions/{secret_version}"

print("Fetching secret from global Secret Manager...")
# Secret Manager クライアントを初期化 (グローバル)
client = SecretManagerClient()

# シークレットを取得
try:
    secret_payload = client.get_secret(resource_name)
    print("Successfully fetched secret.")
    # 必要に応じて、エージェントまたはそのツールで secret_payload を使用できるようになります。
except Exception as e:
    print(f"Error fetching secret: {e}")
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
- [Secret Manager ドキュメント](https://docs.cloud.google.com/secret-manager/docs/overview)。
- [ADK GitHub リポジトリ](https://github.com/google/adk-python)。
