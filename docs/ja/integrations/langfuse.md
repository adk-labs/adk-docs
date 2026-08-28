---
catalog_title: Langfuse
catalog_description: LLM アプリケーションのデバッグ、分析、反復改善を行うオープンソース AI エンジニアリング プラットフォーム
catalog_icon: /integrations/assets/langfuse.png
catalog_tags: ["observability", "evaluation"]
---

# ADK 向け Langfuse 可観測性 (Observability)

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span>
</div>

[Langfuse](https://langfuse.com) は、可観測性 (Observability)、評価 (Evaluation)、およびプロンプト管理のためのオープンソース LLM エンジニアリング プラットフォームです。OpenTelemetry (OTel) プロトコルを使用して ADK エージェントから詳細なトレースをキャプチャするため、開発環境や本番環境でエージェント アプリのデバッグ、評価、反復改善を行うことができます。

## 概要

Langfuse は OpenTelemetry を使用して ADK からトレースをキャプチャし、[AI エンジニアリング ループ (AI Engineering Loop)](https://langfuse.com/academy/ai-engineering-loop) をサポートします:

- **[トレース (Trace)](https://langfuse.com/academy/tracing)**: プロンプト、取得されたコンテキスト、ツール呼び出し、出力、レイテンシ、コストを含むリクエストのフルパスをキャプチャ
- **[モニタリング (Monitor)](https://langfuse.com/academy/monitoring)**: 評価方法、ユーザー フィードバック、コストやレイテンシの異常値を使用して、システムの経時的な動作を追跡し、注目すべきトレースを検出
- **[データセットの構築 (Build datasets)](https://langfuse.com/academy/datasets)**: モニタリングでの実際のシナリオや開発時の想定シナリオを、再現可能なテストケースに変換
- **[実験 (Experiment)](https://langfuse.com/academy/experiments)**: 変数 (プロンプト、モデル、検索戦略など) を体系的に変更し、安定したベースラインと各変更を比較
- **[評価 (Evaluate)](https://langfuse.com/academy/evaluate)**: 手動レビュー、コード エバリュエーター チェック、または LLM-as-a-judge を使用して、結果がリリースに適しているかを判断

## インストール

必要なパッケージをインストールします:

```bash
pip install langfuse "google-adk>=2" openinference-instrumentation-google-adk
```

`google-adk` 2.x には Python 3.10 以降が必要です。`"google-adk>=2"` に固定することで、pip が現在の ADK 2.x リリースを確実にインストールします。

## セットアップ

[cloud.langfuse.com](https://cloud.langfuse.com) にサインアップするか、プラットフォームを [セルフホスト](https://langfuse.com/self-hosting) し、API キーを設定します。キーはプロジェクトの設定ページから取得できます。また、[Gemini API キー](https://aistudio.google.com/app/apikey) も設定してください:

```bash
export LANGFUSE_PUBLIC_KEY="pk-lf-..."
export LANGFUSE_SECRET_KEY="sk-lf-..."
export LANGFUSE_BASE_URL="https://cloud.langfuse.com"  # EU リージョン
# その他のリージョン: https://us.cloud.langfuse.com (米国),
# https://jp.cloud.langfuse.com (日本), https://hipaa.cloud.langfuse.com (HIPAA)
export GOOGLE_API_KEY="your-gemini-api-key"
```

Langfuse クライアントを初期化し、ADK を計装 (instrument) します:

```python
from langfuse import get_client
from openinference.instrumentation.google_adk import GoogleADKInstrumentor

langfuse = get_client()

# 接続の確認
if langfuse.auth_check():
    print("Langfuse client is authenticated and ready!")
else:
    print("Authentication failed. Please check your credentials and host.")

GoogleADKInstrumentor().instrument()
```

これで完了です。すべての ADK エージェントのアクティビティが自動的にトレースされ、Langfuse プロジェクトに送信されます。

## 観測 (Observe)

トレースが初期化されたら、通常どおり ADK エージェントを実行すると、すべてのインタラクションが Langfuse に表示されます:

```python
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

def say_hello():
    return {"greeting": "Hello Langfuse 👋"}

agent = Agent(
    name="hello_agent",
    model="gemini-3.5-flash",
    instruction="Always greet using the say_hello tool.",
    tools=[say_hello],
)

APP_NAME = "hello_app"
USER_ID = "demo-user"
SESSION_ID = "demo-session"

session_service = InMemorySessionService()
# create_session は非同期 → ノートブック環境では await します
await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)

runner = Runner(agent=agent, app_name=APP_NAME, session_service=session_service)

user_msg = types.Content(role="user", parts=[types.Part(text="hi")])
for event in runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=user_msg):
    if event.is_final_response():
        if event.content and event.content.parts:
            print(event.content.parts[0].text)
        elif event.error_message:
            print(f"Agent error: {event.error_message}")
```

Langfuse は `runner.run()` に渡す `user_id` と `session_id` をトレースの **ユーザー** および **セッション** に自動的にマッピングします。追加のコードなしで [ユーザー](https://langfuse.com/docs/observability/features/users) や [セッション](https://langfuse.com/docs/observability/features/sessions) の追跡機能を利用できます。

## 名前付きおよびフィルタリング可能なトレース

デフォルトでは、トレースには ADK アプリの名前が付けられます。Langfuse でトレースをフィルタリングしやすくするために、[`propagate_attributes`](https://langfuse.com/docs/observability/sdk/instrumentation) を使用して分かりやすいトレース名、タグ、およびメタデータを設定します。

この方法で属性を設定する場合は、非同期の `runner.run_async()` API を使用してください。同期の `runner.run()` はバックグラウンドのワーカー スレッドでエージェントを実行するため、OpenTelemetry コンテキスト (および `propagate_attributes` からの属性) が ADK スパンに到達しません:

```python
from langfuse import propagate_attributes

SESSION_ID_2 = "demo-session-2"
await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID_2)

with propagate_attributes(
    trace_name="hello-agent-request",
    tags=["google-adk", "cookbook"],
    metadata={"example": "named-trace"},
):
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID_2, new_message=user_msg):
        if event.is_final_response():
            if event.content and event.content.parts:
                print(event.content.parts[0].text)
            elif event.error_message:
                print(f"Agent error: {event.error_message}")
```

## Langfuse でトレースを表示する

**Langfuse ダッシュボード → Traces** を開き、エージェント ループ、ツール呼び出し、およびモデル生成を確認します。トレースは、上記で設定したユーザー、セッション、タグでフィルタリングできます。

![Langfuse での Google ADK 例のトレース](https://langfuse.com/images/cookbook/integration-google-adk/google-adk-trace.png)

マルチエージェント パイプライン、ユーザー フィードバックによるトレースのスコアリング、およびその他の例については、[Langfuse ADK 統合ガイド](https://langfuse.com/integrations/frameworks/google-adk) を参照してください。

## サポートとリソース

- [Langfuse ドキュメント](https://langfuse.com/docs)
- [ADK 統合ガイド](https://langfuse.com/integrations/frameworks/google-adk)
- [GitHub 上の Langfuse リポジトリ](https://github.com/langfuse/langfuse)
