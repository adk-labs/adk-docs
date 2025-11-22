# 最初のインテリジェントエージェントチームを構築する: ADKを使用したプログレッシブな天気ボット

<!-- Optional outer container for overall padding/spacing -->
<div style="padding: 10px 0;">

  <!-- Line 1: Open in Colab -->
  <!-- This div ensures the link takes up its own line and adds space below -->
  <div style="margin-bottom: 10px;">
    <a href="https://colab.research.google.com/github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb" target="_blank" style="display: inline-flex; align-items: center; gap: 5px; text-decoration: none; color: #4285F4;">
      <img width="32px" src="https://www.gstatic.com/pantheon/images/bigquery/welcome_page/colab-logo.svg" alt="Google Colaboratory logo">
      <span>Colabで開く</span>
    </a>
  </div>

  <!-- Line 2: Share Links -->
  <!-- This div acts as a flex container for the "Share to" text and icons -->
  <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
    <!-- Share Text -->
    <span style="font-weight: bold;">共有:</span>

    <!-- Social Media Links -->
    <a href="https://www.linkedin.com/sharing/share-offsite/?url=https%3A//github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb" target="_blank" title="Share on LinkedIn">
      <img width="20px" src="https://upload.wikimedia.org/wikipedia/commons/8/81/LinkedIn_icon.svg" alt="LinkedIn logo" style="vertical-align: middle;">
    </a>
    <a href="https://bsky.app/intent/compose?text=https%3A//github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb" target="_blank" title="Share on Bluesky">
      <img width="20px" src="https://upload.wikimedia.org/wikipedia/commons/7/7a/Bluesky_Logo.svg" alt="Bluesky logo" style="vertical-align: middle;">
    </a>
    <a href="https://twitter.com/intent/tweet?url=https%3A//github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb" target="_blank" title="Share on X (Twitter)">
      <img width="20px" src="https://upload.wikimedia.org/wikipedia/commons/5/5a/X_icon_2.svg" alt="X logo" style="vertical-align: middle;">
    </a>
    <a href="https://reddit.com/submit?url=https%3A//github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb" target="_blank" title="Share on Reddit">
      <img width="20px" src="https://redditinc.com/hubfs/Reddit%20Inc/Brand/Reddit_Logo.png" alt="Reddit logo" style="vertical-align: middle;">
    </a>
    <a href="https://www.facebook.com/sharer/sharer.php?u=https%3A//github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb" target="_blank" title="Share on Facebook">
      <img width="20px" src="https://upload.wikimedia.org/wikipedia/commons/5/51/Facebook_f_logo_%282019%29.svg" alt="Facebook logo" style="vertical-align: middle;">
    </a>
  </div>

</div>

このチュートリアルは、[Agent Development Kit](https://google.github.io/adk-docs/get-started/)の[クイックスタート例](https://google.github.io/adk-docs/get-started/quickstart/)から拡張されたものです。これで、より深く掘り下げ、より洗練された**マルチエージェントシステム**を構築する準備が整いました。

シンプルな基盤の上に高度な機能を段階的に積み重ねながら、**天気ボットのエージェントチーム**の構築に着手します。天気を調べることができる単一のエージェントから始めて、次のような機能を順次追加していきます。

*   異なるAIモデルの活用 (Gemini, GPT, Claude)。
*   個別のタスク（挨拶や別れの挨拶など）に特化したサブエージェントの設計。
*   エージェント間でのインテリジェントな委譲（Delegation）の有効化。
*   永続的なセッション状態（Session State）を使用してエージェントに記憶を持たせる。
*   コールバックを使用して重要な安全ガードレールを実装する。

**なぜ天気ボットチームなのか？**

このユースケースは一見シンプルに見えますが、複雑で実用的なエージェントアプリケーションを構築するために不可欠なADKのコアコンセプトを探求するための、実用的で親しみやすいキャンバスを提供します。インタラクションの構造化、状態管理、安全性の確保、そして複数のAI「頭脳」を連携させる方法を学びます。

**ADKとは何でしたか？**

念のため説明すると、ADKは大規模言語モデル（LLM）を搭載したアプリケーションの開発を効率化するために設計されたPythonフレームワークです。推論、計画、ツールの使用、ユーザーとの動的な対話、そしてチーム内での効果的な連携が可能なエージェントを作成するための堅牢なビルディングブロックを提供します。

**この高度なチュートリアルで習得できること：**

*   ✅ **ツールの定義と使用:** エージェントに特定の能力（データの取得など）を与えるPython関数（`tools`）を作成し、それらを効果的に使用する方法をエージェントに指示します。
*   ✅ **マルチLLMの柔軟性:** LiteLLM統合を通じて、エージェントが様々な主要LLM（Gemini, GPT-4o, Claude Sonnet）を利用できるように構成し、タスクごとに最適なモデルを選択できるようにします。
*   ✅ **エージェントの委譲と連携:** 特化したサブエージェントを設計し、チーム内で最も適切なエージェントへユーザーのリクエストを自動的にルーティング（`auto flow`）できるようにします。
*   ✅ **記憶のためのセッション状態:** `Session State`と`ToolContext`を活用して、エージェントが会話のターンを超えて情報を記憶できるようにし、より文脈に沿った対話を実現します。
*   ✅ **コールバックによる安全ガードレール:** `before_model_callback`と`before_tool_callback`を実装して、事前定義されたルールに基づいてリクエストやツールの使用を検査、修正、またはブロックし、アプリケーションの安全性と制御を強化します。

**最終的な到達点：**

このチュートリアルを完了すると、機能的なマルチエージェント天気ボットシステムを構築したことになります。このシステムは、天気情報を提供するだけでなく、会話のやり取りを処理し、最後にチェックした都市を記憶し、定義された安全境界内で動作します。これらすべてがADKを使用して調整されます。

**前提条件：**

*   ✅ **Pythonプログラミングの確かな理解。**
*   ✅ **大規模言語モデル（LLM）、API、およびエージェントの概念に関する知識。**
*   ❗ **重要：ADKクイックスタートチュートリアルの完了、または同等のADK基礎知識（Agent, Runner, SessionService, 基本的なTool使用法）。** このチュートリアルはこれらの概念の上に直接構築されます。
*   ✅ 使用するLLMの**APIキー**（例：Gemini用のGoogle AI Studio、OpenAI Platform、Anthropic Console）。

---

**実行環境に関する注意：**

このチュートリアルは、Google Colab、Colab Enterprise、またはJupyter Notebookのような対話型ノートブック環境向けに構成されています。以下の点に注意してください。

*   **非同期コードの実行:** ノートブック環境では、非同期コードの処理が異なります。`await`を使用する例（イベントループがすでに実行されている場合に適しており、ノートブックでは一般的）や、`asyncio.run()`を使用する例（スタンドアロンの`.py`スクリプトや特定のノートブック設定で必要になることが多い）が出てきます。コードブロックでは両方のシナリオについてのガイダンスを提供します。
*   **手動でのRunner/Session設定:** 手順には、`Runner`および`SessionService`インスタンスを明示的に作成することが含まれます。このアプローチは、エージェントの実行ライフサイクル、セッション管理、および状態の永続性をきめ細かく制御できるため、ここで紹介しています。

**代替手段：ADKの組み込みツール（Web UI / CLI / API Server）を使用する場合**

ADKの標準ツールを使用してランナーとセッション管理を自動的に処理する設定を希望する場合は、[こちら](https://github.com/google/adk-docs/tree/main/examples/python/tutorial/agent_team/adk-tutorial)にその目的に合わせて構成されたコードがあります。そのバージョンは、`adk web`（Web UI用）、`adk run`（CLI対話用）、または`adk api_server`（API公開用）のようなコマンドで直接実行するように設計されています。その代替リソースにある`README.md`の指示に従ってください。

---

**エージェントチームを構築する準備はできましたか？ さあ、始めましょう！**

> **注意:** このチュートリアルは、adkバージョン1.0.0以上で動作します。

```python
# @title ステップ 0: セットアップとインストール
# マルチモデルサポートのためにADKとLiteLLMをインストールします

!pip install google-adk -q
!pip install litellm -q

print("Installation complete.")
```

```python
# @title 必要なライブラリのインポート
import os
import asyncio
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm # マルチモデルサポート用
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types # メッセージのContent/Parts作成用

import warnings
# すべての警告を無視
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.ERROR)

print("Libraries imported.")
```

```python
# @title APIキーの設定（実際のキーに置き換えてください！）

# --- 重要: プレースホルダーを実際のAPIキーに置き換えてください ---

# Gemini APIキー (Google AI Studioから取得: https://aistudio.google.com/app/apikey)
os.environ["GOOGLE_API_KEY"] = "YOUR_GOOGLE_API_KEY" # <--- 置き換え

# [オプション]
# OpenAI APIキー (OpenAI Platformから取得: https://platform.openai.com/api-keys)
os.environ['OPENAI_API_KEY'] = 'YOUR_OPENAI_API_KEY' # <--- 置き換え

# [オプション]
# Anthropic APIキー (Anthropic Consoleから取得: https://console.anthropic.com/settings/keys)
os.environ['ANTHROPIC_API_KEY'] = 'YOUR_ANTHROPIC_API_KEY' # <--- 置き換え

# --- キーの確認 (オプションのチェック) ---
print("API Keys Set:")
print(f"Google API Key set: {'Yes' if os.environ.get('GOOGLE_API_KEY') and os.environ['GOOGLE_API_KEY'] != 'YOUR_GOOGLE_API_KEY' else 'No (REPLACE PLACEHOLDER!)'}")
print(f"OpenAI API Key set: {'Yes' if os.environ.get('OPENAI_API_KEY') and os.environ['OPENAI_API_KEY'] != 'YOUR_OPENAI_API_KEY' else 'No (REPLACE PLACEHOLDER!)'}")
print(f"Anthropic API Key set: {'Yes' if os.environ.get('ANTHROPIC_API_KEY') and os.environ['ANTHROPIC_API_KEY'] != 'YOUR_ANTHROPIC_API_KEY' else 'No (REPLACE PLACEHOLDER!)'}")

# このマルチモデル設定ではVertex AIではなくAPIキーを直接使用するようにADKを構成
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"


# @markdown **セキュリティ上の注意:** APIキーをノートブックに直接ハードコーディングするのではなく、安全に管理（ColabのSecretsや環境変数を使用するなど）することがベストプラクティスです。上記のプレースホルダー文字列を置き換えてください。
```

```python
# --- 簡単に使用するためのモデル定数の定義 ---

# サポートされているその他のモデルはこちらを参照: https://ai.google.dev/gemini-api/docs/models#model-variations
MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"

# サポートされているその他のモデルはこちらを参照: https://docs.litellm.ai/docs/providers/openai#openai-chat-completion-models
MODEL_GPT_4O = "openai/gpt-4.1" # 他の試行例: gpt-4.1-mini, gpt-4o など

# サポートされているその他のモデルはこちらを参照: https://docs.litellm.ai/docs/providers/anthropic
MODEL_CLAUDE_SONNET = "anthropic/claude-sonnet-4-20250514" # 他の試行例: claude-opus-4-20250514 , claude-3-7-sonnet-20250219 など

print("\nEnvironment configured.")
```

---

## ステップ 1: 最初のエージェント - 基本的な天気予報検索

まずは、天気ボットの基本構成要素となる、特定のタスク（天気情報の検索）を実行できる単一のエージェントを構築することから始めましょう。これには2つの主要な部分の作成が含まれます。

1.  **ツール (Tool):** エージェントに天気データを取得する*能力*を与えるPython関数。
2.  **エージェント (Agent):** ユーザーのリクエストを理解し、天気ツールを持っていることを認識し、いつどのようにそれを使用するかを決定するAI「頭脳」。

---

**1\. ツールの定義 (`get_weather`)**

ADKにおいて、**ツール (Tools)** は単なるテキスト生成を超えて、エージェントに具体的な機能を与える構成要素です。これらは通常、APIの呼び出し、データベースへのクエリ、計算の実行など、特定のアクションを実行する通常のPython関数です。

最初のツールは、*モック（模擬）*の天気レポートを提供します。これにより、まだ外部APIキーを必要とせずに、エージェントの構造に集中することができます。後で、このモック関数を実際の天気サービスを呼び出す関数に簡単に置き換えることができます。

**重要な概念：Docstring（ドキュメンテーション文字列）は極めて重要です！** エージェントのLLMは、以下の点を理解するために、関数の**docstring**に大きく依存しています。

*   ツールが*何を*するのか。
*   *いつ*それを使用するのか。
*   *どのような引数*が必要か（`city: str`）。
*   *どのような情報*を返すのか。

**ベストプラクティス:** ツールには、明確で説明的かつ正確なdocstringを記述してください。これはLLMがツールを正しく使用するために不可欠です。

```python
# @title get_weather ツールの定義
def get_weather(city: str) -> dict:
    """指定された都市の現在の天気予報を取得します。

    Args:
        city (str): 都市の名前 (例: "New York", "London", "Tokyo").

    Returns:
        dict: 天気情報を含む辞書。
              'status' キー ('success' または 'error') を含みます。
              'success' の場合、天気の詳細を含む 'report' キーが含まれます。
              'error' の場合、'error_message' キーが含まれます。
    """
    print(f"--- Tool: get_weather called for city: {city} ---") # ツール実行のログ
    city_normalized = city.lower().replace(" ", "") # 基本的な正規化

    # モック天気データ
    mock_weather_db = {
        "newyork": {"status": "success", "report": "The weather in New York is sunny with a temperature of 25°C."},
        "london": {"status": "success", "report": "It's cloudy in London with a temperature of 15°C."},
        "tokyo": {"status": "success", "report": "Tokyo is experiencing light rain and a temperature of 18°C."},
    }

    if city_normalized in mock_weather_db:
        return mock_weather_db[city_normalized]
    else:
        return {"status": "error", "error_message": f"Sorry, I don't have weather information for '{city}'."}

# ツール使用例 (オプションのテスト)
print(get_weather("New York"))
print(get_weather("Paris"))
```

---

**2\. エージェントの定義 (`weather_agent`)**

次に、**エージェント**自体を作成しましょう。ADKの `Agent` は、ユーザー、LLM、および利用可能なツール間の相互作用を調整します。

いくつかの主要なパラメータを設定します。

*   `name`: このエージェントの一意の識別子（例："weather\_agent\_v1"）。
*   `model`: 使用するLLMを指定します（例：`MODEL_GEMINI_2_0_FLASH`）。まずは特定のGeminiモデルから始めます。
*   `description`: エージェントの全体的な目的の簡潔な要約です。これは後で、他のエージェントがタスクを*この*エージェントに委譲するかどうかを決定する際に重要になります。
*   `instruction`: 振る舞い方、ペルソナ、目標、そして具体的に割り当てられた `tools` を*どのように、いつ*利用するかについて、LLMへの詳細なガイダンスです。
*   `tools`: エージェントが使用を許可されている実際のPythonツール関数のリスト（例：`[get_weather]`）。

**ベストプラクティス:** 明確で具体的な `instruction`（指示）プロンプトを提供してください。指示が詳細であればあるほど、LLMは自分の役割とツールの効果的な使用方法をよりよく理解できます。必要であれば、エラー処理についても明示的に記述してください。

**ベストプラクティス:** 説明的な `name` と `description` の値を選択してください。これらはADK内部で使用され、自動委譲（後述）のような機能に不可欠です。

```python
# @title 天気エージェントの定義
# 前に定義したモデル定数の1つを使用
AGENT_MODEL = MODEL_GEMINI_2_0_FLASH # Geminiで開始

weather_agent = Agent(
    name="weather_agent_v1",
    model=AGENT_MODEL, # Gemini用の文字列またはLiteLlmオブジェクトが可能
    description="Provides weather information for specific cities.",
    instruction="You are a helpful weather assistant. "
                "When the user asks for the weather in a specific city, "
                "use the 'get_weather' tool to find the information. "
                "If the tool returns an error, inform the user politely. "
                "If the tool is successful, present the weather report clearly.",
    tools=[get_weather], # 関数を直接渡す
)

print(f"Agent '{weather_agent.name}' created using model '{AGENT_MODEL}'.")
```

---

**3\. Runnerとセッションサービスのセットアップ**

会話を管理し、エージェントを実行するには、さらに2つのコンポーネントが必要です。

*   `SessionService`: さまざまなユーザーやセッションの会話履歴と状態を管理する責任があります。`InMemorySessionService`は、すべてをメモリに保存するシンプルな実装で、テストや単純なアプリケーションに適しています。交換されたメッセージを追跡します。状態の永続性についてはステップ4で詳しく説明します。
*   `Runner`: インタラクションフローを調整するエンジンです。ユーザー入力を受け取り、適切なエージェントにルーティングし、エージェントのロジックに基づいてLLMとツールの呼び出しを管理し、`SessionService`を介してセッションの更新を処理し、インタラクションの進行状況を表すイベント（Event）を生成（yield）します。

```python
# @title セッションサービスとRunnerのセットアップ

# --- セッション管理 ---
# 重要な概念: SessionServiceは会話履歴と状態を保存します。
# InMemorySessionServiceは、このチュートリアル用のシンプルな非永続ストレージです。
session_service = InMemorySessionService()

# インタラクションコンテキストを識別するための定数を定義
APP_NAME = "weather_tutorial_app"
USER_ID = "user_1"
SESSION_ID = "session_001" # 簡単のため固定IDを使用

# 会話が行われる特定のセッションを作成
session = await session_service.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID
)
print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")

# --- または ---

# 標準のPythonスクリプト（.pyファイル）として実行する場合は、次の行のコメントを解除してください：

# async def init_session(app_name:str,user_id:str,session_id:str) -> InMemorySessionService:
#     session = await session_service.create_session(
#         app_name=app_name,
#         user_id=user_id,
#         session_id=session_id
#     )
#     print(f"Session created: App='{app_name}', User='{user_id}', Session='{session_id}'")
#     return session
# 
# session = asyncio.run(init_session(APP_NAME,USER_ID,SESSION_ID))

# --- Runner ---
# 重要な概念: Runnerはエージェントの実行ループを調整します。
runner = Runner(
    agent=weather_agent, # 実行したいエージェント
    app_name=APP_NAME,   # 実行をアプリに関連付ける
    session_service=session_service # セッションマネージャーを使用
)
print(f"Runner created for agent '{runner.agent.name}'.")
```

---

**4\. エージェントとの対話**

エージェントにメッセージを送り、応答を受け取る方法が必要です。LLMの呼び出しやツールの実行には時間がかかる可能性があるため、ADKの `Runner` は非同期で動作します。

次のような `async` ヘルパー関数 (`call_agent_async`) を定義します。

1.  ユーザークエリ文字列を受け取ります。
2.  それをADK `Content` 形式にパッケージ化します。
3.  ユーザー/セッションコンテキストと新しいメッセージを指定して `runner.run_async` を呼び出します。
4.  ランナーによって生成（yield）される **イベント（Events）** を反復処理します。イベントは、エージェントの実行におけるステップ（例：ツール呼び出し要求、ツール結果受信、中間LLM思考、最終応答）を表します。
5.  `event.is_final_response()` を使用して **最終応答** イベントを特定し、出力します。

**なぜ `async` なのか？** LLMや（外部APIなどの）ツールとの対話は、I/Oバウンドな操作です。`asyncio`を使用することで、プログラムは実行をブロックすることなくこれらの操作を効率的に処理できます。

```python
# @title エージェント対話関数の定義

from google.genai import types # メッセージContent/Parts作成用

async def call_agent_async(query: str, runner, user_id, session_id):
  """エージェントにクエリを送信し、最終応答を出力します。"""
  print(f"\n>>> User Query: {query}")

  # ADK形式でユーザーのメッセージを準備
  content = types.Content(role='user', parts=[types.Part(text=query)])

  final_response_text = "Agent did not produce a final response." # デフォルト値

  # 重要な概念: run_asyncはエージェントロジックを実行し、イベントを生成します。
  # イベントを反復処理して最終的な回答を見つけます。
  async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
      # 実行中の*すべての*イベントを見るには、下の行のコメントを解除してください
      # print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")

      # 重要な概念: is_final_response() はターンの終了メッセージを示します。
      if event.is_final_response():
          if event.content and event.content.parts:
             # 最初の部分にテキスト応答があると仮定
             final_response_text = event.content.parts[0].text
          elif event.actions and event.actions.escalate: # 潜在的なエラー/エスカレーションの処理
             final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
          # 必要に応じてここでさらにチェックを追加 (例: 特定のエラーコード)
          break # 最終応答が見つかったらイベント処理を停止

  print(f"<<< Agent Response: {final_response_text}")
```

---

**5\. 会話の実行**

最後に、いくつかのクエリをエージェントに送信してセットアップをテストしましょう。`async` 呼び出しをメインの `async` 関数にラップし、`await` を使用して実行します。

出力を確認してください：

*   ユーザーのクエリを確認します。
*   エージェントがツールを使用するときの `--- Tool: get_weather called... ---` ログに注目してください。
*   天気データが利用できない場合（パリの例）の処理方法を含め、エージェントの最終応答を観察してください。

```python
# @title 初期会話の実行

# 対話ヘルパーをawaitするために非同期関数が必要です
async def run_conversation():
    await call_agent_async("What is the weather like in London?",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID)

    await call_agent_async("How about Paris?",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID) # ツールのエラーメッセージを想定

    await call_agent_async("Tell me the weather in New York",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID)

# 非同期コンテキスト（Colab/Jupyterなど）でawaitを使用して会話を実行
await run_conversation()

# --- または ---

# 標準のPythonスクリプト（.pyファイル）として実行する場合は、次の行のコメントを解除してください：
# import asyncio
# if __name__ == "__main__":
#     try:
#         asyncio.run(run_conversation())
#     except Exception as e:
#         print(f"An error occurred: {e}")
```

---

おめでとうございます！ 最初のADKエージェントの構築と対話に成功しました。エージェントはユーザーのリクエストを理解し、ツールを使って情報を見つけ、ツールの結果に基づいて適切に応答します。

次のステップでは、このエージェントを動かしている基礎となる言語モデルを簡単に切り替える方法を探ります。

## ステップ 2: LiteLLMによるマルチモデル化 [オプション]

ステップ1では、特定のGeminiモデルを使用した機能的な天気エージェントを構築しました。効果的ですが、実際のアプリケーションでは、*異なる*大規模言語モデル（LLM）を使用できる柔軟性が役立つことがよくあります。なぜでしょうか？

*   **パフォーマンス:** 一部のモデルは特定のタスク（コーディング、推論、クリエイティブな執筆など）に優れています。
*   **コスト:** モデルによって価格が異なります。
*   **機能:** モデルによって、機能、コンテキストウィンドウサイズ、ファインチューニングのオプションが異なります。
*   **可用性/冗長性:** 代替手段を用意しておけば、あるプロバイダーで問題が発生してもアプリケーションの機能を維持できます。

ADKは[**LiteLLM**](https://github.com/BerriAI/litellm)ライブラリとの統合により、モデル間の切り替えをシームレスに行います。LiteLLMは、100以上の異なるLLMに対する一貫したインターフェースとして機能します。

**このステップでは、以下を行います：**

1.  `LiteLlm` ラッパーを使用して、OpenAI（GPT）やAnthropic（Claude）などのプロバイダーのモデルを使用するようにADK `Agent` を構成する方法を学びます。
2.  それぞれ異なるLLMでバックアップされた天気エージェントのインスタンスを定義し、構成（独自のセッションとランナーを使用）し、即座にテストします。
3.  これらの異なるエージェントと対話し、同じ基礎ツールを使用している場合でも、応答にどのような変化があるか（またはないか）を観察します。

---

**1\. `LiteLlm` のインポート**

初期セットアップ（ステップ0）でこれをインポートしましたが、これがマルチモデルサポートの重要なコンポーネントです。

```python
# @title 1. LiteLlmのインポート
from google.adk.models.lite_llm import LiteLlm
```

**2\. マルチモデルエージェントの定義とテスト**

モデル名の文字列（デフォルトはGoogleのGeminiモデル）だけを渡す代わりに、希望するモデル識別子の文字列を `LiteLlm` クラス内にラップします。

*   **重要な概念: `LiteLlm` ラッパー:** `LiteLlm(model="provider/model_name")` という構文は、このエージェントへのリクエストをLiteLLMライブラリ経由で指定されたモデルプロバイダーにルーティングするようADKに指示します。

ステップ0でOpenAIとAnthropicに必要なAPIキーを設定していることを確認してください。設定直後に各エージェントと対話するために、`call_agent_async` 関数（以前に定義したもの、現在は `runner`, `user_id`, `session_id` を受け入れます）を使用します。

以下の各ブロックは次を実行します。

*   特定のLiteLLMモデル（`MODEL_GPT_4O` または `MODEL_CLAUDE_SONNET`）を使用してエージェントを定義します。
*   そのエージェントのテスト実行用に、*新しく別の* `InMemorySessionService` とセッションを作成します。これにより、このデモンストレーションのために会話履歴が分離されます。
*   特定のエージェントとそのセッションサービス用に構成された `Runner` を作成します。
*   即座に `call_agent_async` を呼び出してクエリを送信し、エージェントをテストします。

**ベストプラクティス:** モデル名には定数（ステップ0で定義した `MODEL_GPT_4O`, `MODEL_CLAUDE_SONNET` など）を使用して、タイプミスを防ぎ、コード管理を容易にしてください。

**エラー処理:** エージェント定義を `try...except` ブロックで囲みます。これにより、特定のプロバイダーのAPIキーが見つからないか無効な場合でも、コードセル全体の実行が失敗するのを防ぎ、*構成されている*モデルでチュートリアルを続行できます。

まず、OpenAIのGPT-4oを使用したエージェントを作成してテストしましょう。

```python
# @title GPTエージェントの定義とテスト

# ステップ1の 'get_weather' 関数が環境で定義されていることを確認してください。
# 前述の 'call_agent_async' が定義されていることを確認してください。

# --- GPT-4oを使用するエージェント ---
weather_agent_gpt = None # Noneで初期化
runner_gpt = None      # runnerをNoneで初期化

try:
    weather_agent_gpt = Agent(
        name="weather_agent_gpt",
        # 主な変更点: LiteLLMモデル識別子をラップする
        model=LiteLlm(model=MODEL_GPT_4O),
        description="Provides weather information (using GPT-4o).",
        instruction="You are a helpful weather assistant powered by GPT-4o. "
                    "Use the 'get_weather' tool for city weather requests. "
                    "Clearly present successful reports or polite error messages based on the tool's output status.",
        tools=[get_weather], # 同じツールを再利用
    )
    print(f"Agent '{weather_agent_gpt.name}' created using model '{MODEL_GPT_4O}'.")

    # InMemorySessionServiceは、このチュートリアル用のシンプルな非永続ストレージです。
    session_service_gpt = InMemorySessionService() # 専用サービスを作成

    # インタラクションコンテキストを識別するための定数を定義
    APP_NAME_GPT = "weather_tutorial_app_gpt" # このテスト用の一意のアプリ名
    USER_ID_GPT = "user_1_gpt"
    SESSION_ID_GPT = "session_001_gpt" # 簡単のため固定IDを使用

    # 会話が行われる特定のセッションを作成
    session_gpt = await session_service_gpt.create_session(
        app_name=APP_NAME_GPT,
        user_id=USER_ID_GPT,
        session_id=SESSION_ID_GPT
    )
    print(f"Session created: App='{APP_NAME_GPT}', User='{USER_ID_GPT}', Session='{SESSION_ID_GPT}'")

    # このエージェントとそのセッションサービスに固有のランナーを作成
    runner_gpt = Runner(
        agent=weather_agent_gpt,
        app_name=APP_NAME_GPT,       # 特定のアプリ名を使用
        session_service=session_service_gpt # 特定のセッションサービスを使用
        )
    print(f"Runner created for agent '{runner_gpt.agent.name}'.")

    # --- GPTエージェントのテスト ---
    print("\n--- Testing GPT Agent ---")
    # call_agent_asyncが正しいrunner, user_id, session_idを使用していることを確認
    await call_agent_async(query = "What's the weather in Tokyo?",
                           runner=runner_gpt,
                           user_id=USER_ID_GPT,
                           session_id=SESSION_ID_GPT)
    # --- または ---

    # 標準のPythonスクリプト（.pyファイル）として実行する場合は、次の行のコメントを解除してください：
    # import asyncio
    # if __name__ == "__main__":
    #     try:
    #         asyncio.run(call_agent_async(query = "What's the weather in Tokyo?",
    #                      runner=runner_gpt,
    #                       user_id=USER_ID_GPT,
    #                       session_id=SESSION_ID_GPT)
    #     except Exception as e:
    #         print(f"An error occurred: {e}")

except Exception as e:
    print(f"❌ Could not create or run GPT agent '{MODEL_GPT_4O}'. Check API Key and model name. Error: {e}")

```

次に、AnthropicのClaude Sonnetに対しても同じことを行います。

```python
# @title Claudeエージェントの定義とテスト

# ステップ1の 'get_weather' 関数が環境で定義されていることを確認してください。
# 前述の 'call_agent_async' が定義されていることを確認してください。

# --- Claude Sonnetを使用するエージェント ---
weather_agent_claude = None # Noneで初期化
runner_claude = None      # runnerをNoneで初期化

try:
    weather_agent_claude = Agent(
        name="weather_agent_claude",
        # 主な変更点: LiteLLMモデル識別子をラップする
        model=LiteLlm(model=MODEL_CLAUDE_SONNET),
        description="Provides weather information (using Claude Sonnet).",
        instruction="You are a helpful weather assistant powered by Claude Sonnet. "
                    "Use the 'get_weather' tool for city weather requests. "
                    "Analyze the tool's dictionary output ('status', 'report'/'error_message'). "
                    "Clearly present successful reports or polite error messages.",
        tools=[get_weather], # 同じツールを再利用
    )
    print(f"Agent '{weather_agent_claude.name}' created using model '{MODEL_CLAUDE_SONNET}'.")

    # InMemorySessionServiceは、このチュートリアル用のシンプルな非永続ストレージです。
    session_service_claude = InMemorySessionService() # 専用サービスを作成

    # インタラクションコンテキストを識別するための定数を定義
    APP_NAME_CLAUDE = "weather_tutorial_app_claude" # 一意のアプリ名
    USER_ID_CLAUDE = "user_1_claude"
    SESSION_ID_CLAUDE = "session_001_claude" # 簡単のため固定IDを使用

    # 会話が行われる特定のセッションを作成
    session_claude = await session_service_claude.create_session(
        app_name=APP_NAME_CLAUDE,
        user_id=USER_ID_CLAUDE,
        session_id=SESSION_ID_CLAUDE
    )
    print(f"Session created: App='{APP_NAME_CLAUDE}', User='{USER_ID_CLAUDE}', Session='{SESSION_ID_CLAUDE}'")

    # このエージェントとそのセッションサービスに固有のランナーを作成
    runner_claude = Runner(
        agent=weather_agent_claude,
        app_name=APP_NAME_CLAUDE,       # 特定のアプリ名を使用
        session_service=session_service_claude # 特定のセッションサービスを使用
        )
    print(f"Runner created for agent '{runner_claude.agent.name}'.")

    # --- Claudeエージェントのテスト ---
    print("\n--- Testing Claude Agent ---")
    # call_agent_asyncが正しいrunner, user_id, session_idを使用していることを確認
    await call_agent_async(query = "Weather in London please.",
                           runner=runner_claude,
                           user_id=USER_ID_CLAUDE,
                           session_id=SESSION_ID_CLAUDE)

    # --- または ---

    # 標準のPythonスクリプト（.pyファイル）として実行する場合は、次の行のコメントを解除してください：
    # import asyncio
    # if __name__ == "__main__":
    #     try:
    #         asyncio.run(call_agent_async(query = "Weather in London please.",
    #                      runner=runner_claude,
    #                       user_id=USER_ID_CLAUDE,
    #                       session_id=SESSION_ID_CLAUDE)
    #     except Exception as e:
    #         print(f"An error occurred: {e}")


except Exception as e:
    print(f"❌ Could not create or run Claude agent '{MODEL_CLAUDE_SONNET}'. Check API Key and model name. Error: {e}")
```

両方のコードブロックからの出力を注意深く観察してください。以下のことがわかります。

1.  各エージェント（`weather_agent_gpt`, `weather_agent_claude`）は（APIキーが有効であれば）正常に作成されます。
2.  それぞれに専用のセッションとランナーが設定されます。
3.  各エージェントは、クエリを処理する際に `get_weather` ツールを使用する必要があることを正しく認識します（`--- Tool: get_weather called... ---` ログが表示されます）。
4.  *基礎となるツールのロジック*は同一であり、常にモックデータを返します。
5.  しかし、各エージェントによって生成される **最終的なテキスト応答** は、言い回し、口調、フォーマットがわずかに異なる場合があります。これは、指示プロンプトが異なるLLM（GPT-4o 対 Claude Sonnet）によって解釈され実行されるためです。

このステップは、ADK + LiteLLMが提供するパワーと柔軟性を示しています。コアアプリケーションロジック（ツール、基本的なエージェント構造）を一貫させながら、さまざまなLLMを使用してエージェントを簡単に実験し、デプロイすることができます。

次のステップでは、単一のエージェントを超えて、互いにタスクを委譲できる小さなチームを構築します！

---

## ステップ 3: エージェントチームの構築 - 挨拶と別れの委譲

ステップ1と2では、天気検索のみに焦点を当てた単一のエージェントを構築し、実験しました。特定のタスクには効果的ですが、実際のアプリケーションでは、より幅広いユーザーインタラクションを処理することがよくあります。単一の天気エージェントにさらに多くのツールや複雑な指示を追加し続けることも*可能*ですが、これはすぐに管理不能になり、効率が低下する可能性があります。

より堅牢なアプローチは、**エージェントチーム**を構築することです。これには以下が含まれます。

1.  それぞれが特定の機能（例：天気、挨拶、計算）のために設計された、複数の**特化型エージェント**を作成する。
2.  初期のユーザーリクエストを受け取る**ルートエージェント**（またはオーケストレーター）を指定する。
3.  ユーザーの意図に基づいて、ルートエージェントがリクエストを最も適切な特化型サブエージェントに**委譲（delegate）**できるようにする。

**なぜエージェントチームを構築するのか？**

*   **モジュール性:** 個々のエージェントの開発、テスト、保守が容易になります。
*   **専門化:** 各エージェントは特定のタスクに合わせて微調整（指示、モデル選択）できます。
*   **スケーラビリティ:** 新しいエージェントを追加することで、新しい機能を簡単に追加できます。
*   **効率性:** 単純なタスク（挨拶など）には、より単純で安価なモデルを使用できる可能性があります。

**このステップでは、以下を行います：**

1.  挨拶（`say_hello`）と別れ（`say_goodbye`）を処理するための簡単なツールを定義します。
2.  2つの新しい特化型サブエージェント、`greeting_agent` と `farewell_agent` を作成します。
3.  メインの天気エージェント（`weather_agent_v2`）を更新して、**ルートエージェント**として機能させます。
4.  ルートエージェントにサブエージェントを構成し、**自動委譲**を有効にします。
5.  さまざまな種類のリクエストをルートエージェントに送信して、委譲フローをテストします。

---

**1\. サブエージェント用のツールの定義**

まず、新しいスペシャリストエージェントのツールとして機能する簡単なPython関数を作成しましょう。ツールを使用するエージェントにとって、明確なdocstringが不可欠であることを忘れないでください。

```python
# @title 挨拶と別れのエージェント用のツールの定義
from typing import Optional # Optionalをインポートすることを確認

# このステップを単独で実行する場合は、ステップ1の 'get_weather' が利用可能であることを確認してください。
# def get_weather(city: str) -> dict: ... (from Step 1)

def say_hello(name: Optional[str] = None) -> str:
    """簡単な挨拶を提供します。名前が指定されている場合は使用されます。

    Args:
        name (str, optional): 挨拶する相手の名前。指定されていない場合は一般的な挨拶がデフォルトになります。

    Returns:
        str: 親しみやすい挨拶メッセージ。
    """
    if name:
        greeting = f"Hello, {name}!"
        print(f"--- Tool: say_hello called with name: {name} ---")
    else:
        greeting = "Hello there!" # nameがNoneまたは明示的に渡されなかった場合のデフォルトの挨拶
        print(f"--- Tool: say_hello called without a specific name (name_arg_value: {name}) ---")
    return greeting

def say_goodbye() -> str:
    """会話を終了するための簡単な別れのメッセージを提供します。"""
    print(f"--- Tool: say_goodbye called ---")
    return "Goodbye! Have a great day."

print("Greeting and Farewell tools defined.")

# オプションの自己テスト
print(say_hello("Alice"))
print(say_hello()) # 引数なしでテスト（デフォルトの "Hello there!" を使用するはず）
print(say_hello(name=None)) # 名前を明示的にNoneとしてテスト（デフォルトの "Hello there!" を使用するはず）
```

---

**2\. サブエージェントの定義（挨拶と別れ）**

次に、スペシャリスト用の `Agent` インスタンスを作成します。非常に焦点を絞った `instruction` と、重要な点として明確な `description` に注目してください。`description` は、*ルートエージェント*が*いつ*これらのサブエージェントに委譲するかを決定するために使用する主要な情報です。

**ベストプラクティス:** サブエージェントの `description` フィールドは、その特定の機能を正確かつ簡潔に要約する必要があります。これは効果的な自動委譲に不可欠です。

**ベストプラクティス:** サブエージェントの `instruction` フィールドは、その限られた範囲に合わせて調整し、何をすべきか、そして*何をすべきでないか*（例：「あなたの*唯一の*タスクは...」）を正確に伝える必要があります。

```python
# @title 挨拶と別れのサブエージェントの定義

# Gemini以外のモデルを使用する場合は、LiteLlmがインポートされ、APIキーが設定されていることを確認してください（ステップ0/2から）
# from google.adk.models.lite_llm import LiteLlm
# MODEL_GPT_4O, MODEL_CLAUDE_SONNET などが定義されている必要があります
# そうでない場合は、引き続き以下を使用してください: model = MODEL_GEMINI_2_0_FLASH

# --- 挨拶エージェント ---
greeting_agent = None
try:
    greeting_agent = Agent(
        # 単純なタスクには、異なる（またはより安価な）モデルを使用可能
        model = MODEL_GEMINI_2_0_FLASH,
        # model=LiteLlm(model=MODEL_GPT_4O), # 他のモデルを実験したい場合
        name="greeting_agent",
        instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting to the user. "
                    "Use the 'say_hello' tool to generate the greeting. "
                    "If the user provides their name, make sure to pass it to the tool. "
                    "Do not engage in any other conversation or tasks.",
        description="Handles simple greetings and hellos using the 'say_hello' tool.", # 委譲に重要
        tools=[say_hello],
    )
    print(f"✅ Agent '{greeting_agent.name}' created using model '{greeting_agent.model}'.")
except Exception as e:
    print(f"❌ Could not create Greeting agent. Check API Key ({greeting_agent.model}). Error: {e}")

# --- 別れのエージェント ---
farewell_agent = None
try:
    farewell_agent = Agent(
        # 同じまたは異なるモデルを使用可能
        model = MODEL_GEMINI_2_0_FLASH,
        # model=LiteLlm(model=MODEL_GPT_4O), # 他のモデルを実験したい場合
        name="farewell_agent",
        instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message. "
                    "Use the 'say_goodbye' tool when the user indicates they are leaving or ending the conversation "
                    "(e.g., using words like 'bye', 'goodbye', 'thanks bye', 'see you'). "
                    "Do not perform any other actions.",
        description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.", # 委譲に重要
        tools=[say_goodbye],
    )
    print(f"✅ Agent '{farewell_agent.name}' created using model '{farewell_agent.model}'.")
except Exception as e:
    print(f"❌ Could not create Farewell agent. Check API Key ({farewell_agent.model}). Error: {e}")
```

---

**3\. サブエージェントを持つルートエージェント（天気エージェント v2）の定義**

ここで、`weather_agent` をアップグレードします。主な変更点は以下のとおりです。

*   `sub_agents` パラメータの追加: 作成したばかりの `greeting_agent` と `farewell_agent` インスタンスを含むリストを渡します。
*   `instruction` の更新: ルートエージェントにサブエージェント*について*、そして*いつ*それらにタスクを委譲すべきかを明示的に伝えます。

**重要な概念: 自動委譲（Auto Flow）** `sub_agents` リストを提供することで、ADKは自動委譲を有効にします。ルートエージェントがユーザークエリを受け取ると、LLMは自身の指示とツールだけでなく、各サブエージェントの `description` も考慮します。LLMがクエリがサブエージェントの説明された能力（例：「簡単な挨拶を処理する」）とよりよく一致すると判断した場合、そのターンのために制御をそのサブエージェントに*転送*する特別な内部アクションを自動的に生成します。その後、サブエージェントは独自のモデル、指示、ツールを使用してクエリを処理します。

**ベストプラクティス:** ルートエージェントの指示が委譲の決定を明確に導くようにしてください。サブエージェントを名前で言及し、委譲が発生すべき条件を説明してください。

```python
# @title サブエージェントを持つルートエージェントの定義

# ルートエージェントを定義する前に、サブエージェントが正常に作成されたことを確認してください。
# また、元の 'get_weather' ツールが定義されていることも確認してください。
root_agent = None
runner_root = None # runnerの初期化

if greeting_agent and farewell_agent and 'get_weather' in globals():
    # オーケストレーションを処理するためにルートエージェントには有能なGeminiモデルを使用しましょう
    root_agent_model = MODEL_GEMINI_2_0_FLASH

    weather_agent_team = Agent(
        name="weather_agent_v2", # 新しいバージョン名を付ける
        model=root_agent_model,
        description="The main coordinator agent. Handles weather requests and delegates greetings/farewells to specialists.",
        instruction="You are the main Weather Agent coordinating a team. Your primary responsibility is to provide weather information. "
                    "Use the 'get_weather' tool ONLY for specific weather requests (e.g., 'weather in London'). "
                    "You have specialized sub-agents: "
                    "1. 'greeting_agent': Handles simple greetings like 'Hi', 'Hello'. Delegate to it for these. "
                    "2. 'farewell_agent': Handles simple farewells like 'Bye', 'See you'. Delegate to it for these. "
                    "Analyze the user's query. If it's a greeting, delegate to 'greeting_agent'. If it's a farewell, delegate to 'farewell_agent'. "
                    "If it's a weather request, handle it yourself using 'get_weather'. "
                    "For anything else, respond appropriately or state you cannot handle it.",
        tools=[get_weather], # ルートエージェントは中核タスクのためにまだ天気ツールが必要
        # 主な変更点: ここでサブエージェントをリンク！
        sub_agents=[greeting_agent, farewell_agent]
    )
    print(f"✅ Root Agent '{weather_agent_team.name}' created using model '{root_agent_model}' with sub-agents: {[sa.name for sa in weather_agent_team.sub_agents]}")

else:
    print("❌ Cannot create root agent because one or more sub-agents failed to initialize or 'get_weather' tool is missing.")
    if not greeting_agent: print(" - Greeting Agent is missing.")
    if not farewell_agent: print(" - Farewell Agent is missing.")
    if 'get_weather' not in globals(): print(" - get_weather function is missing.")


```

---

**4\. エージェントチームとの対話**

特化型サブエージェントを持つルートエージェント（`weather_agent_team` - *注：この変数名が前のコードブロック「# @title サブエージェントを持つルートエージェントの定義」で定義された名前、おそらく`weather_agent_team`と一致することを確認してください*）を定義したので、委譲メカニズムをテストしてみましょう。

次のコードブロックは以下を実行します。

1.  `async` 関数 `run_team_conversation` を定義します。
2.  この関数内で、このテスト実行のためだけの*新しく専用の* `InMemorySessionService` と特定のセッション（`session_001_agent_team`）を作成します。これにより、チームのダイナミクスをテストするために会話履歴が分離されます。
3.  `weather_agent_team`（ルートエージェント）と専用のセッションサービスを使用するように構成された `Runner`（`runner_agent_team`）を作成します。
4.  更新された `call_agent_async` 関数を使用して、さまざまなタイプのクエリ（挨拶、天気リクエスト、別れ）を `runner_agent_team` に送信します。この特定のテストのために、ランナー、ユーザーID、セッションIDを明示的に渡します。
5.  `run_team_conversation` 関数を直ちに実行します。

次のようなフローが予想されます。

1.  "Hello there!" クエリが `runner_agent_team` に送られます。
2.  ルートエージェント（`weather_agent_team`）がそれを受け取り、指示と `greeting_agent` の説明に基づいてタスクを委譲します。
3.  `greeting_agent` がクエリを処理し、`say_hello` ツールを呼び出し、応答を生成します。
4.  "What is the weather in New York?" クエリは委譲*されず*、ルートエージェントが `get_weather` ツールを使用して直接処理します。
5.  "Thanks, bye!" クエリは `farewell_agent` に委譲され、このエージェントは `say_goodbye` ツールを使用します。

```python
# @title エージェントチームとの対話
import asyncio # asyncioがインポートされていることを確認

# ルートエージェント（例：'weather_agent_team' または前のセルの 'root_agent'）が定義されていることを確認。
# call_agent_async関数が定義されていることを確認。

# 会話関数を定義する前にルートエージェント変数が存在するか確認
root_agent_var_name = 'root_agent' # ステップ3ガイドのデフォルト名
if 'weather_agent_team' in globals(): # ユーザーが代わりにこの名前を使用したか確認
    root_agent_var_name = 'weather_agent_team'
elif 'root_agent' not in globals():
    print("⚠️ Root agent ('root_agent' or 'weather_agent_team') not found. Cannot define run_team_conversation.")
    # コードブロックが実行された場合に後でNameErrorを防ぐためにダミー値を割り当て
    root_agent = None # または実行を防ぐフラグを設定

# ルートエージェントが存在する場合のみ定義して実行
if root_agent_var_name in globals() and globals()[root_agent_var_name]:
    # 会話ロジックのメイン非同期関数を定義。
    # この関数内の 'await' キーワードは非同期操作に必要です。
    async def run_team_conversation():
        print("\n--- Testing Agent Team Delegation ---")
        session_service = InMemorySessionService()
        APP_NAME = "weather_tutorial_agent_team"
        USER_ID = "user_1_agent_team"
        SESSION_ID = "session_001_agent_team"
        session = await session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
        )
        print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")

        actual_root_agent = globals()[root_agent_var_name]
        runner_agent_team = Runner( # またはInMemoryRunnerを使用
            agent=actual_root_agent,
            app_name=APP_NAME,
            session_service=session_service
        )
        print(f"Runner created for agent '{actual_root_agent.name}'.")

        # --- awaitを使用した対話 (async def内で正しい) ---
        await call_agent_async(query = "Hello there!",
                               runner=runner_agent_team,
                               user_id=USER_ID,
                               session_id=SESSION_ID)
        await call_agent_async(query = "What is the weather in New York?",
                               runner=runner_agent_team,
                               user_id=USER_ID,
                               session_id=SESSION_ID)
        await call_agent_async(query = "Thanks, bye!",
                               runner=runner_agent_team,
                               user_id=USER_ID,
                               session_id=SESSION_ID)

    # --- `run_team_conversation` 非同期関数の実行 ---
    # 環境に基づいて以下の方法のいずれかを選択してください。
    # 注: 使用するモデルのAPIキーが必要になる場合があります！

    # 方法 1: 直接 await (ノートブック/非同期REPLのデフォルト)
    # 環境がトップレベルのawaitをサポートしている場合（Colab/Jupyterノートブックなど）、
    # イベントループがすでに実行されているため、関数を直接awaitできます。
    print("Attempting execution using 'await' (default for notebooks)...")
    await run_team_conversation()

    # 方法 2: asyncio.run (標準Pythonスクリプト [.py] 用)
    # ターミナルから標準Pythonスクリプトとしてこのコードを実行する場合、
    # スクリプトコンテキストは同期的です。非同期関数を実行するための
    # イベントループを作成・管理するには `asyncio.run()` が必要です。
    # この方法を使用するには：
    # 1. 上記の `await run_team_conversation()` 行をコメントアウトします。
    # 2. 次のブロックのコメントを解除します：
    """
    import asyncio
    if __name__ == "__main__": # スクリプトが直接実行されたときのみ実行されるようにする
        print("Executing using 'asyncio.run()' (for standard Python scripts)...")
        try:
            # イベントループを作成し、非同期関数を実行し、ループを閉じます。
            asyncio.run(run_team_conversation())
        except Exception as e:
            print(f"An error occurred: {e}")
    """

else:
    # 前のステップでルートエージェントが正常に定義されなかった場合、このメッセージが出力されます
    print("\n⚠️ Skipping agent team conversation execution as the root agent was not successfully defined in a previous step.")
```

---

出力ログ、特に `--- Tool: ... called ---` メッセージを注意深く見てください。以下のことが観察されるはずです。

*   "Hello there!" の場合、`say_hello` ツールが呼び出されました（`greeting_agent` が処理したことを示します）。
*   "What is the weather in New York?" の場合、`get_weather` ツールが呼び出されました（ルートエージェントが処理したことを示します）。
*   "Thanks, bye!" の場合、`say_goodbye` ツールが呼び出されました（`farewell_agent` が処理したことを示します）。

これで **自動委譲** の成功が確認できました！ ルートエージェントは、指示と `sub_agents` の `description` に導かれ、ユーザーのリクエストをチーム内の適切なスペシャリストエージェントに正しくルーティングしました。

これで、複数の連携するエージェントでアプリケーションを構造化できました。このモジュラー設計は、より複雑で有能なエージェントシステムを構築するための基本です。次のステップでは、セッション状態を使用してエージェントにターンを超えて情報を記憶する能力を与えます。

## ステップ 4: セッション状態による記憶とパーソナライゼーションの追加

これまでのところ、エージェントチームは委譲を通じてさまざまなタスクを処理できますが、各インタラクションは最初からやり直しになります。エージェントは、セッション内の過去の会話やユーザーの好みを記憶していません。より洗練された文脈認識型の体験を作成するには、エージェントに **記憶** が必要です。ADKは **セッション状態（Session State）** を通じてこれを提供します。

**セッション状態とは何ですか？**

*   特定のユーザーセッション（`APP_NAME`, `USER_ID`, `SESSION_ID` で識別）に関連付けられた Python 辞書（`session.state`）です。
*   そのセッション内の *複数の会話ターンにわたって* 情報を保持します。
*   エージェントとツールはこの状態を読み書きできるため、詳細を記憶し、動作を適応させ、応答をパーソナライズできます。

**エージェントが状態と対話する方法:**

1.  **`ToolContext` (主要な方法):** ツールは `ToolContext` オブジェクト（最後の引数として宣言されている場合、ADKによって自動的に提供されます）を受け取ることができます。このオブジェクトは `tool_context.state` を介してセッション状態への直接アクセスを提供し、ツールが実行 *中* に設定を読み取ったり結果を保存したりできるようにします。
2.  **`output_key` (エージェント応答の自動保存):** `Agent` は `output_key="your_key"` で構成できます。これにより、ADKはそのターンのエージェントの最終テキスト応答を `session.state["your_key"]` に自動的に保存します。

**このステップでは、以下を行うことで天気ボットチームを強化します:**

1.  以前のステップからの干渉なしに状態を明確に示すために、**新しい** `InMemorySessionService` を使用します。
2.  `temperature_unit` のユーザー設定でセッション状態を初期化します。
3.  `ToolContext` を介してこの設定を読み取り、出力形式（摂氏/華氏）を調整する状態認識型の天気ツール（`get_weather_stateful`）を作成します。
4.  この状態認識ツールを使用するようにルートエージェントを更新し、`output_key` を構成して最終的な天気予報をセッション状態に自動的に保存するようにします。
5.  会話を実行して、初期状態がツールにどのように影響するか、手動の状態変更がその後の動作をどのように変更するか、そして `output_key` がどのようにエージェントの応答を保持するかを観察します。

---

**1\. 新しいセッションサービスと状態の初期化**

以前のステップからの干渉なしに状態管理を明確に示すために、新しい `InMemorySessionService` をインスタンス化します。また、ユーザーの好みの温度単位を定義する初期状態を持つセッションを作成します。

```python
# @title 1. 新しいセッションサービスと状態の初期化

# 必要なセッションコンポーネントのインポート
from google.adk.sessions import InMemorySessionService

# この状態デモンストレーション用に新しいセッションサービスインスタンスを作成
session_service_stateful = InMemorySessionService()
print("✅ New InMemorySessionService created for state demonstration.")

# チュートリアルのこの部分用に新しいセッションIDを定義
SESSION_ID_STATEFUL = "session_state_demo_001"
USER_ID_STATEFUL = "user_state_demo"

# 初期状態データの定義 - ユーザーは最初、摂氏を好む
initial_state = {
    "user_preference_temperature_unit": "Celsius"
}

# 初期状態を提供してセッションを作成
session_stateful = await session_service_stateful.create_session(
    app_name=APP_NAME, # 一貫したアプリ名を使用
    user_id=USER_ID_STATEFUL,
    session_id=SESSION_ID_STATEFUL,
    state=initial_state # <<< 作成時に状態を初期化
)
print(f"✅ Session '{SESSION_ID_STATEFUL}' created for user '{USER_ID_STATEFUL}'.")

# 初期状態が正しく設定されたことを確認
retrieved_session = await session_service_stateful.get_session(app_name=APP_NAME,
                                                         user_id=USER_ID_STATEFUL,
                                                         session_id = SESSION_ID_STATEFUL)
print("\n--- Initial Session State ---")
if retrieved_session:
    print(retrieved_session.state)
else:
    print("Error: Could not retrieve session.")
```

---

**2\. 状態認識型天気ツールの作成 (`get_weather_stateful`)**

次に、新しいバージョンの天気ツールを作成します。主な特徴は、`tool_context: ToolContext` を受け入れ、`tool_context.state` にアクセスできることです。`user_preference_temperature_unit` を読み取り、それに応じて温度をフォーマットします。

*   **重要な概念: `ToolContext`** このオブジェクトは、ツールのロジックがセッションのコンテキスト（状態変数の読み書きを含む）と対話することを可能にするブリッジです。ツール関数の最後のパラメータとして定義すると、ADKが自動的に注入します。

*   **ベストプラクティス:** 状態から読み取る際は、キーがまだ存在しない場合を処理するために `dictionary.get('key', default_value)` を使用して、ツールがクラッシュしないようにしてください。

```python
from google.adk.tools.tool_context import ToolContext

def get_weather_stateful(city: str, tool_context: ToolContext) -> dict:
    """天気を取得し、セッション状態に基づいて温度単位を変換します。"""
    print(f"--- Tool: get_weather_stateful called for {city} ---")

    # --- 状態から設定を読み取る ---
    preferred_unit = tool_context.state.get("user_preference_temperature_unit", "Celsius") # デフォルトは摂氏
    print(f"--- Tool: Reading state 'user_preference_temperature_unit': {preferred_unit} ---")

    city_normalized = city.lower().replace(" ", "")

    # モック天気データ (内部的には常に摂氏で保存)
    mock_weather_db = {
        "newyork": {"temp_c": 25, "condition": "sunny"},
        "london": {"temp_c": 15, "condition": "cloudy"},
        "tokyo": {"temp_c": 18, "condition": "light rain"},
    }

    if city_normalized in mock_weather_db:
        data = mock_weather_db[city_normalized]
        temp_c = data["temp_c"]
        condition = data["condition"]

        # 状態の設定に基づいて温度をフォーマット
        if preferred_unit == "Fahrenheit":
            temp_value = (temp_c * 9/5) + 32 # 華氏を計算
            temp_unit = "°F"
        else: # デフォルトは摂氏
            temp_value = temp_c
            temp_unit = "°C"

        report = f"The weather in {city.capitalize()} is {condition} with a temperature of {temp_value:.0f}{temp_unit}."
        result = {"status": "success", "report": report}
        print(f"--- Tool: Generated report in {preferred_unit}. Result: {result} ---")

        # 状態への書き戻しの例 (このツールではオプション)
        tool_context.state["last_city_checked_stateful"] = city
        print(f"--- Tool: Updated state 'last_city_checked_stateful': {city} ---")

        return result
    else:
        # 都市が見つからない場合の処理
        error_msg = f"Sorry, I don't have weather information for '{city}'."
        print(f"--- Tool: City '{city}' not found. ---")
        return {"status": "error", "error_message": error_msg}

print("✅ State-aware 'get_weather_stateful' tool defined.")

```

---

**3\. サブエージェントの再定義とルートエージェントの更新**

このステップが自己完結し、正しく構築されるように、まず `greeting_agent` と `farewell_agent` をステップ3とまったく同じように再定義します。次に、新しいルートエージェント (`weather_agent_v4_stateful`) を定義します。

*   新しい `get_weather_stateful` ツールを使用します。
*   委譲のために挨拶と別れのサブエージェントを含めます。
*   **重要な点として**、`output_key="last_weather_report"` を設定して、最終的な天気の応答をセッション状態に自動的に保存します。

```python
# @title 3. サブエージェントの再定義と output_key を使用したルートエージェントの更新

# 必要なインポートを確認: Agent, LiteLlm, Runner
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
# ツール 'say_hello', 'say_goodbye' が定義されていることを確認 (ステップ3から)
# モデル定数 MODEL_GPT_4O, MODEL_GEMINI_2_0_FLASH などが定義されていることを確認

# --- 挨拶エージェントの再定義 (ステップ3から) ---
greeting_agent = None
try:
    greeting_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="greeting_agent",
        instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting using the 'say_hello' tool. Do nothing else.",
        description="Handles simple greetings and hellos using the 'say_hello' tool.",
        tools=[say_hello],
    )
    print(f"✅ Agent '{greeting_agent.name}' redefined.")
except Exception as e:
    print(f"❌ Could not redefine Greeting agent. Error: {e}")

# --- 別れのエージェントの再定義 (ステップ3から) ---
farewell_agent = None
try:
    farewell_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="farewell_agent",
        instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message using the 'say_goodbye' tool. Do not perform any other actions.",
        description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.",
        tools=[say_goodbye],
    )
    print(f"✅ Agent '{farewell_agent.name}' redefined.")
except Exception as e:
    print(f"❌ Could not redefine Farewell agent. Error: {e}")

# --- 更新されたルートエージェントの定義 ---
root_agent_stateful = None
runner_root_stateful = None # runnerの初期化

# ルートエージェントを作成する前に前提条件を確認
if greeting_agent and farewell_agent and 'get_weather_stateful' in globals():

    root_agent_model = MODEL_GEMINI_2_0_FLASH # オーケストレーションモデルの選択

    root_agent_stateful = Agent(
        name="weather_agent_v4_stateful", # 新しいバージョン名
        model=root_agent_model,
        description="Main agent: Provides weather (state-aware unit), delegates greetings/farewells, saves report to state.",
        instruction="You are the main Weather Agent. Your job is to provide weather using 'get_weather_stateful'. "
                    "The tool will format the temperature based on user preference stored in state. "
                    "Delegate simple greetings to 'greeting_agent' and farewells to 'farewell_agent'. "
                    "Handle only weather requests, greetings, and farewells.",
        tools=[get_weather_stateful], # 状態認識ツールを使用
        sub_agents=[greeting_agent, farewell_agent], # サブエージェントを含める
        output_key="last_weather_report" # <<< エージェントの最終的な天気の応答を自動保存
    )
    print(f"✅ Root Agent '{root_agent_stateful.name}' created using stateful tool and output_key.")

    # --- このルートエージェントと新しいセッションサービス用のRunnerを作成 ---
    runner_root_stateful = Runner(
        agent=root_agent_stateful,
        app_name=APP_NAME,
        session_service=session_service_stateful # 新しい状態保持セッションサービスを使用
    )
    print(f"✅ Runner created for stateful root agent '{runner_root_stateful.agent.name}' using stateful session service.")

else:
    print("❌ Cannot create stateful root agent. Prerequisites missing.")
    if not greeting_agent: print(" - greeting_agent definition missing.")
    if not farewell_agent: print(" - farewell_agent definition missing.")
    if 'get_weather_stateful' not in globals(): print(" - get_weather_stateful tool missing.")

```

---

**4\. 対話と状態フローのテスト**

それでは、`runner_root_stateful`（状態保持エージェントおよび `session_service_stateful` に関連付けられている）を使用して、状態の相互作用をテストするように設計された会話を実行してみましょう。以前に定義した `call_agent_async` 関数を使用し、正しいランナー、ユーザーID（`USER_ID_STATEFUL`）、およびセッションID（`SESSION_ID_STATEFUL`）を渡していることを確認します。

会話フローは次のようになります。

1.  **天気の確認（ロンドン）:** `get_weather_stateful` ツールは、セクション1で初期化されたセッション状態から初期の「Celsius」設定を読み取るはずです。ルートエージェントの最終応答（摂氏での天気レポート）は、`output_key` 構成によって `state['last_weather_report']` に保存されるはずです。
2.  **手動での状態更新:** `InMemorySessionService` インスタンス（`session_service_stateful`）内に保存されている状態を*直接変更*します。
    *   **なぜ直接変更するのか？** `session_service.get_session()` メソッドはセッションの*コピー*を返します。そのコピーを変更しても、後続のエージェント実行で使用される状態には影響しません。`InMemorySessionService` を使用するこのテストシナリオでは、内部の `sessions` 辞書にアクセスして、`user_preference_temperature_unit` の*実際の*保存値を「Fahrenheit」に変更します。*注：実際のアプリケーションでは、状態の変更は通常、内部ストレージの直接操作ではなく、`EventActions(state_delta=...)` を返すツールまたはエージェントロジックによってトリガーされます。*
3.  **天気の再確認（ニューヨーク）:** `get_weather_stateful` ツールは、状態から更新された「Fahrenheit」設定を読み取り、それに応じて温度を変換するはずです。ルートエージェントの*新しい*応答（華氏での天気）は、`output_key` によって `state['last_weather_report']` の以前の値を上書きします。
4.  **エージェントへの挨拶:** 状態保持操作と並行して、`greeting_agent` への委譲が依然として正しく機能することを確認します。このインタラクションは、この特定のシーケンスにおいて `output_key` によって保存される*最後の*応答になります。
5.  **最終状態の検査:** 会話の後、セッションを最後にもう一度取得（コピーを取得）し、その状態を出力して、`user_preference_temperature_unit` が実際に「Fahrenheit」であることを確認し、`output_key` によって保存された最終値（この実行では挨拶になる）を観察し、ツールによって書き込まれた `last_city_checked_stateful` の値を確認します。

```python
# @title 4. 状態フローと output_key をテストするための対話
import asyncio # asyncioがインポートされていることを確認

# 状態保持ランナー (runner_root_stateful) が前のセルから利用可能であることを確認
# call_agent_async, USER_ID_STATEFUL, SESSION_ID_STATEFUL, APP_NAME が定義されていることを確認

if 'runner_root_stateful' in globals() and runner_root_stateful:
    # 状態保持会話ロジックのメイン非同期関数を定義。
    # この関数内の 'await' キーワードは非同期操作に必要です。
    async def run_stateful_conversation():
        print("\n--- Testing State: Temp Unit Conversion & output_key ---")

        # 1. 天気の確認 (初期状態を使用: 摂氏)
        print("--- Turn 1: Requesting weather in London (expect Celsius) ---")
        await call_agent_async(query= "What's the weather in London?",
                               runner=runner_root_stateful,
                               user_id=USER_ID_STATEFUL,
                               session_id=SESSION_ID_STATEFUL
                              )

        # 2. 手動で状態設定を華氏に更新 - ストレージを直接変更
        print("\n--- Manually Updating State: Setting unit to Fahrenheit ---")
        try:
            # 内部ストレージに直接アクセス - これはテスト用のInMemorySessionServiceに固有です
            # 注: 永続サービス (Database, VertexAI) を使用した本番環境では、
            # 通常、内部ストレージを直接操作するのではなく、エージェントのアクションまたは
            # 利用可能な場合は特定のサービスAPIを介して状態を更新します。
            stored_session = session_service_stateful.sessions[APP_NAME][USER_ID_STATEFUL][SESSION_ID_STATEFUL]
            stored_session.state["user_preference_temperature_unit"] = "Fahrenheit"
            # オプション: ロジックが依存している場合はタイムスタンプも更新することをお勧めします
            # import time
            # stored_session.last_update_time = time.time()
            print(f"--- Stored session state updated. Current 'user_preference_temperature_unit': {stored_session.state.get('user_preference_temperature_unit', 'Not Set')} ---") # 安全のため .get を追加
        except KeyError:
            print(f"--- Error: Could not retrieve session '{SESSION_ID_STATEFUL}' from internal storage for user '{USER_ID_STATEFUL}' in app '{APP_NAME}' to update state. Check IDs and if session was created. ---")
        except Exception as e:
             print(f"--- Error updating internal session state: {e} ---")

        # 3. 天気を再度確認 (ツールは華氏を使用するはず)
        # これにより output_key を介して 'last_weather_report' も更新されます
        print("\n--- Turn 2: Requesting weather in New York (expect Fahrenheit) ---")
        await call_agent_async(query= "Tell me the weather in New York.",
                               runner=runner_root_stateful,
                               user_id=USER_ID_STATEFUL,
                               session_id=SESSION_ID_STATEFUL
                              )

        # 4. 基本的な委譲のテスト (依然として機能するはず)
        # これにより 'last_weather_report' が再度更新され、NYの天気予報が上書きされます
        print("\n--- Turn 3: Sending a greeting ---")
        await call_agent_async(query= "Hi!",
                               runner=runner_root_stateful,
                               user_id=USER_ID_STATEFUL,
                               session_id=SESSION_ID_STATEFUL
                              )

    # --- `run_stateful_conversation` 非同期関数の実行 ---
    # 環境に基づいて以下の方法のいずれかを選択してください。

    # 方法 1: 直接 await (ノートブック/非同期REPLのデフォルト)
    # 環境がトップレベルのawaitをサポートしている場合（Colab/Jupyterノートブックなど）、
    # イベントループがすでに実行されているため、関数を直接awaitできます。
    print("Attempting execution using 'await' (default for notebooks)...")
    await run_stateful_conversation()

    # 方法 2: asyncio.run (標準Pythonスクリプト [.py] 用)
    # ターミナルから標準Pythonスクリプトとしてこのコードを実行する場合、
    # スクリプトコンテキストは同期的です。非同期関数を実行するための
    # イベントループを作成・管理するには `asyncio.run()` が必要です。
    # この方法を使用するには：
    # 1. 上記の `await run_stateful_conversation()` 行をコメントアウトします。
    # 2. 次のブロックのコメントを解除します：
    """
    import asyncio
    if __name__ == "__main__": # スクリプトが直接実行されたときのみ実行されるようにする
        print("Executing using 'asyncio.run()' (for standard Python scripts)...")
        try:
            # イベントループを作成し、非同期関数を実行し、ループを閉じます。
            asyncio.run(run_stateful_conversation())
        except Exception as e:
            print(f"An error occurred: {e}")
    """

    # --- 会話後の最終セッション状態の検査 ---
    # このブロックは、いずれかの実行方法が完了した後に実行されます。
    print("\n--- Inspecting Final Session State ---")
    final_session = await session_service_stateful.get_session(app_name=APP_NAME,
                                                         user_id= USER_ID_STATEFUL,
                                                         session_id=SESSION_ID_STATEFUL)
    if final_session:
        # 潜在的に欠落しているキーへの安全なアクセスのために .get() を使用
        print(f"Final Preference: {final_session.state.get('user_preference_temperature_unit', 'Not Set')}")
        print(f"Final Last Weather Report (from output_key): {final_session.state.get('last_weather_report', 'Not Set')}")
        print(f"Final Last City Checked (by tool): {final_session.state.get('last_city_checked_stateful', 'Not Set')}")
        # 詳細表示のために完全な状態を出力
        # print(f"Full State Dict: {final_session.state}") # 詳細表示用
    else:
        print("\n❌ Error: Could not retrieve final session state.")

else:
    print("\n⚠️ Skipping state test conversation. Stateful root agent runner ('runner_root_stateful') is not available.")
```

---

会話フローと最終的なセッション状態の出力を見直すことで、以下のことが確認できます。

*   **状態の読み取り:** 天気ツール (`get_weather_stateful`) は、ロンドンに対して最初に「Celsius」を使用して、状態から `user_preference_temperature_unit` を正しく読み取りました。
*   **状態の更新:** 直接変更により、保存された設定が正常に「Fahrenheit」に変更されました。
*   **状態の読み取り（更新後）:** ツールはその後、ニューヨークの天気を尋ねられたときに「Fahrenheit」を読み取り、変換を実行しました。
*   **ツールの状態書き込み:** ツールは、`tool_context.state` を介して `last_city_checked_stateful`（2回目の天気チェック後の「New York」）を状態に正常に書き込みました。
*   **委譲:** 「Hi!」に対する `greeting_agent` への委譲は、状態変更後も正しく機能しました。
*   **`output_key`:** `output_key="last_weather_report"` は、ルートエージェントが最終的に応答した*各ターン*について、ルートエージェントの*最終*応答を正常に保存しました。このシーケンスでは、最後の応答は挨拶（"Hello, there!"）であったため、それが状態キー内の天気レポートを上書きしました。
*   **最終状態:** 最終チェックにより、設定が「Fahrenheit」として保持されたことが確認されました。

これで、`ToolContext` を使用してエージェントの動作をパーソナライズするためにセッション状態を統合し、`InMemorySessionService` をテストするために手動で状態を操作し、`output_key` がエージェントの最後の応答を状態に保存するためのシンプルなメカニズムを提供する方法を観察することに成功しました。この状態管理の基本的な理解は、次のステップでコールバックを使用して安全ガードレールを実装する際に重要になります。

---

## ステップ 5: 安全性の追加 - `before_model_callback` による入力ガードレール

エージェントチームは、好みを記憶し、ツールを効果的に使用できるようになり、能力が向上しています。しかし、実際のシナリオでは、潜在的に問題のあるリクエストがコアの大規模言語モデル（LLM）に到達する*前*に、エージェントの動作を制御する安全メカニズムが必要になることがよくあります。

ADKは **コールバック（Callbacks）** を提供します。これは、エージェントの実行ライフサイクルの特定のポイントにフックできる関数です。`before_model_callback` は、入力の安全性確保に特に役立ちます。

**`before_model_callback` とは何ですか？**

*   エージェントがコンパイルされたリクエスト（会話履歴、指示、最新のユーザーメッセージを含む）を基盤となるLLMに送信する*直前*に、ADKが実行するPython関数です。
*   **目的:** 事前定義されたルールに基づいて、リクエストを検査し、必要に応じて修正し、または完全にブロックします。

**一般的なユースケース:**

*   **入力バリデーション/フィルタリング:** ユーザー入力が基準を満たしているか、または許可されていないコンテンツ（PIIやキーワードなど）を含んでいるかを確認します。
*   **ガードレール:** 有害な、トピック外の、またはポリシー違反のリクエストがLLMによって処理されるのを防ぎます。
*   **動的プロンプト修正:** 送信直前に、適切な情報（例：セッション状態から）をLLMリクエストコンテキストに追加します。

**仕組み:**

1.  `callback_context: CallbackContext` と `llm_request: LlmRequest` を受け入れる関数を定義します。

    *   `callback_context`: エージェント情報、セッション状態（`callback_context.state`）などへのアクセスを提供します。
    *   `llm_request`: LLM向けの完全なペイロード（`contents`, `config`）を含みます。

2.  関数内での処理:

    *   **検査:** `llm_request.contents`（特に最後のユーザーメッセージ）を調べます。
    *   **修正（注意して使用）:** `llm_request` の一部を変更*できます*。
    *   **ブロック（ガードレール）:** `LlmResponse` オブジェクトを返します。ADKはこの応答をすぐに返し、そのターンのLLM呼び出しを*スキップ*します。
    *   **許可:** `None` を返します。ADKは（修正された可能性のある）リクエストでLLMを呼び出す処理を続行します。

**このステップでは、以下を行います:**

1.  特定のキーワード（"BLOCK"）がないかユーザーの入力をチェックする `before_model_callback` 関数（`block_keyword_guardrail`）を定義します。
2.  このコールバックを使用するように状態保持ルートエージェント（ステップ4の `weather_agent_v4_stateful`）を更新します。
3.  この更新されたエージェントに関連付けられているが、状態の継続性を維持するために*同じ状態保持セッションサービス*を使用する新しいランナーを作成します。
4.  通常のリクエストとキーワードを含むリクエストの両方を送信して、ガードレールをテストします。

---

**1\. ガードレールコールバック関数の定義**

この関数は、`llm_request` コンテンツ内の最後のユーザーメッセージを検査します。"BLOCK"（大文字小文字を区別しない）が見つかった場合、フローをブロックするために `LlmResponse` を構築して返します。それ以外の場合は `None` を返します。

```python
# @title 1. before_model_callback ガードレールの定義

# 必要なインポートが利用可能であることを確認
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types # 応答コンテンツ作成用
from typing import Optional

def block_keyword_guardrail(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """
    最新のユーザーメッセージに 'BLOCK' が含まれているか検査します。見つかった場合、
    LLM呼び出しをブロックし、事前定義された LlmResponse を返します。
    それ以外の場合は、続行するために None を返します。
    """
    agent_name = callback_context.agent_name # モデル呼び出しがインターセプトされているエージェントの名前を取得
    print(f"--- Callback: block_keyword_guardrail running for agent: {agent_name} ---")

    # リクエスト履歴の最新のユーザーメッセージからテキストを抽出
    last_user_message_text = ""
    if llm_request.contents:
        # 役割が 'user' である最新のメッセージを見つける
        for content in reversed(llm_request.contents):
            if content.role == 'user' and content.parts:
                # 簡単のためテキストは最初の部分にあると仮定
                if content.parts[0].text:
                    last_user_message_text = content.parts[0].text
                    break # 最後のユーザーメッセージテキストを発見

    print(f"--- Callback: Inspecting last user message: '{last_user_message_text[:100]}...' ---") # 最初の100文字をログ出力

    # --- ガードレールロジック ---
    keyword_to_block = "BLOCK"
    if keyword_to_block in last_user_message_text.upper(): # 大文字小文字を区別しないチェック
        print(f"--- Callback: Found '{keyword_to_block}'. Blocking LLM call! ---")
        # オプションで、ブロックイベントを記録するために状態にフラグを設定
        callback_context.state["guardrail_block_keyword_triggered"] = True
        print(f"--- Callback: Set state 'guardrail_block_keyword_triggered': True ---")

        # フローを停止し、代わりにこれを送り返すために LlmResponse を構築して返す
        return LlmResponse(
            content=types.Content(
                role="model", # エージェントの視点からの応答を模倣
                parts=[types.Part(text=f"I cannot process this request because it contains the blocked keyword '{keyword_to_block}'.")],
            )
            # 注: 必要に応じてここに error_message フィールドを設定することもできます
        )
    else:
        # キーワードが見つからない場合、リクエストがLLMに進むことを許可
        print(f"--- Callback: Keyword not found. Allowing LLM call for {agent_name}. ---")
        return None # Noneを返すと、ADKは通常通り続行するよう合図されます

print("✅ block_keyword_guardrail function defined.")

```

---

**2\. コールバックを使用するためのルートエージェントの更新**

ルートエージェントを再定義し、`before_model_callback` パラメータを追加して、新しいガードレール関数を指定します。明確にするために、新しいバージョン名を付けます。

*重要:* ルートエージェントの定義がすべてのコンポーネントにアクセスできるように、サブエージェント（`greeting_agent`, `farewell_agent`）と状態認識ツール（`get_weather_stateful`）が以前のステップからまだ利用可能でない場合は、このコンテキスト内で再定義する必要があります。

```python
# @title 2. before_model_callback を使用したルートエージェントの更新


# --- サブエージェントの再定義 (このコンテキストに存在することを確認) ---
greeting_agent = None
try:
    # 定義済みのモデル定数を使用
    greeting_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="greeting_agent", # 一貫性のために元の名前を保持
        instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting using the 'say_hello' tool. Do nothing else.",
        description="Handles simple greetings and hellos using the 'say_hello' tool.",
        tools=[say_hello],
    )
    print(f"✅ Sub-Agent '{greeting_agent.name}' redefined.")
except Exception as e:
    print(f"❌ Could not redefine Greeting agent. Check Model/API Key ({greeting_agent.model}). Error: {e}")

farewell_agent = None
try:
    # 定義済みのモデル定数を使用
    farewell_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="farewell_agent", # 元の名前を保持
        instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message using the 'say_goodbye' tool. Do not perform any other actions.",
        description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.",
        tools=[say_goodbye],
    )
    print(f"✅ Sub-Agent '{farewell_agent.name}' redefined.")
except Exception as e:
    print(f"❌ Could not redefine Farewell agent. Check Model/API Key ({farewell_agent.model}). Error: {e}")


# --- コールバックを持つルートエージェントの定義 ---
root_agent_model_guardrail = None
runner_root_model_guardrail = None

# 続行する前にすべてのコンポーネントを確認
if greeting_agent and farewell_agent and 'get_weather_stateful' in globals() and 'block_keyword_guardrail' in globals():

    # 定義済みのモデル定数を使用
    root_agent_model = MODEL_GEMINI_2_0_FLASH

    root_agent_model_guardrail = Agent(
        name="weather_agent_v5_model_guardrail", # 明確化のための新しいバージョン名
        model=root_agent_model,
        description="Main agent: Handles weather, delegates greetings/farewells, includes input keyword guardrail.",
        instruction="You are the main Weather Agent. Provide weather using 'get_weather_stateful'. "
                    "Delegate simple greetings to 'greeting_agent' and farewells to 'farewell_agent'. "
                    "Handle only weather requests, greetings, and farewells.",
        tools=[get_weather_stateful],
        sub_agents=[greeting_agent, farewell_agent], # 再定義されたサブエージェントを参照
        output_key="last_weather_report", # ステップ4のoutput_keyを保持
        before_model_callback=block_keyword_guardrail # <<< ガードレールコールバックを割り当て
    )
    print(f"✅ Root Agent '{root_agent_model_guardrail.name}' created with before_model_callback.")

    # --- このエージェント用のRunnerを作成、同じ状態保持セッションサービスを使用 ---
    # ステップ4の session_service_stateful が存在することを確認
    if 'session_service_stateful' in globals():
        runner_root_model_guardrail = Runner(
            agent=root_agent_model_guardrail,
            app_name=APP_NAME, # 一貫したAPP_NAMEを使用
            session_service=session_service_stateful # <<< ステップ4のサービスを使用
        )
        print(f"✅ Runner created for guardrail agent '{runner_root_model_guardrail.agent.name}', using stateful session service.")
    else:
        print("❌ Cannot create runner. 'session_service_stateful' from Step 4 is missing.")

else:
    print("❌ Cannot create root agent with model guardrail. One or more prerequisites are missing or failed initialization:")
    if not greeting_agent: print("   - Greeting Agent")
    if not farewell_agent: print("   - Farewell Agent")
    if 'get_weather_stateful' not in globals(): print("   - 'get_weather_stateful' tool")
    if 'block_keyword_guardrail' not in globals(): print("   - 'block_keyword_guardrail' callback")
```

---

**3\. ガードレールをテストするための対話**

ガードレールの動作をテストしましょう。状態がこれらの変更にまたがって持続することを示すために、ステップ4と同じセッション（`SESSION_ID_STATEFUL`）を使用します。

1.  通常の天気リクエストを送信します（ガードレールを通過して実行されるはずです）。
2.  "BLOCK" を含むリクエストを送信します（コールバックによってインターセプトされるはずです）。
3.  挨拶を送信します（ルートエージェントのガードレールを通過し、委譲され、通常どおり実行されるはずです）。

```python
# @title 3. モデル入力ガードレールをテストするための対話
import asyncio # asyncioがインポートされていることを確認

# ガードレールエージェントのランナーが利用可能であることを確認
if 'runner_root_model_guardrail' in globals() and runner_root_model_guardrail:
    # ガードレールテスト会話のためのメイン非同期関数を定義。
    # この関数内の 'await' キーワードは非同期操作に必要です。
    async def run_guardrail_test_conversation():
        print("\n--- Testing Model Input Guardrail ---")

        # コールバックを持つエージェントのランナーと既存の状態保持セッションIDを使用
        # よりクリーンなインタラクション呼び出しのためのヘルパーラムダを定義
        interaction_func = lambda query: call_agent_async(query,
                                                         runner_root_model_guardrail,
                                                         USER_ID_STATEFUL, # 既存のユーザーIDを使用
                                                         SESSION_ID_STATEFUL # 既存のセッションIDを使用
                                                        )
        # 1. 通常のリクエスト (コールバック許可、以前の状態変更から華氏を使用するはず)
        print("--- Turn 1: Requesting weather in London (expect allowed, Fahrenheit) ---")
        await interaction_func("What is the weather in London?")

        # 2. ブロックされたキーワードを含むリクエスト (コールバックがインターセプト)
        print("\n--- Turn 2: Requesting with blocked keyword (expect blocked) ---")
        await interaction_func("BLOCK the request for weather in Tokyo") # コールバックが "BLOCK" をキャッチするはず

        # 3. 通常の挨拶 (コールバックがルートエージェントを許可、委譲が発生)
        print("\n--- Turn 3: Sending a greeting (expect allowed) ---")
        await interaction_func("Hello again")

    # --- `run_guardrail_test_conversation` 非同期関数の実行 ---
    # 環境に基づいて以下の方法のいずれかを選択してください。

    # 方法 1: 直接 await (ノートブック/非同期REPLのデフォルト)
    # 環境がトップレベルのawaitをサポートしている場合（Colab/Jupyterノートブックなど）、
    # イベントループがすでに実行されているため、関数を直接awaitできます。
    print("Attempting execution using 'await' (default for notebooks)...")
    await run_guardrail_test_conversation()

    # 方法 2: asyncio.run (標準Pythonスクリプト [.py] 用)
    # ターミナルから標準Pythonスクリプトとしてこのコードを実行する場合、
    # スクリプトコンテキストは同期的です。非同期関数を実行するための
    # イベントループを作成・管理するには `asyncio.run()` が必要です。
    # この方法を使用するには：
    # 1. 上記の `await run_guardrail_test_conversation()` 行をコメントアウトします。
    # 2. 次のブロックのコメントを解除します：
    """
    import asyncio
    if __name__ == "__main__": # スクリプトが直接実行されたときのみ実行されるようにする
        print("Executing using 'asyncio.run()' (for standard Python scripts)...")
        try:
            # イベントループを作成し、非同期関数を実行し、ループを閉じます。
            asyncio.run(run_guardrail_test_conversation())
        except Exception as e:
            print(f"An error occurred: {e}")
    """

    # --- 会話後の最終セッション状態の検査 ---
    # このブロックは、いずれかの実行方法が完了した後に実行されます。
    # オプション: コールバックによって設定されたトリガーフラグの状態を確認
    print("\n--- Inspecting Final Session State (After Guardrail Test) ---")
    # この状態保持セッションに関連付けられたセッションサービスインスタンスを使用
    final_session = await session_service_stateful.get_session(app_name=APP_NAME,
                                                         user_id=USER_ID_STATEFUL,
                                                         session_id=SESSION_ID_STATEFUL)
    if final_session:
        # 安全なアクセスのために .get() を使用
        print(f"Guardrail Triggered Flag: {final_session.state.get('guardrail_block_keyword_triggered', 'Not Set (or False)')}")
        print(f"Last Weather Report: {final_session.state.get('last_weather_report', 'Not Set')}") # 成功していればロンドンの天気であるはず
        print(f"Temperature Unit: {final_session.state.get('user_preference_temperature_unit', 'Not Set')}") # 華氏であるはず
        # print(f"Full State Dict: {final_session.state}") # 詳細表示用
    else:
        print("\n❌ Error: Could not retrieve final session state.")

else:
    print("\n⚠️ Skipping model guardrail test. Runner ('runner_root_model_guardrail') is not available.")
```

---

実行フローを観察してください。

1.  **ロンドンの天気:** コールバックが `weather_agent_v5_model_guardrail` に対して実行され、メッセージを検査し、「Keyword not found. Allowing LLM call.」を出力して `None` を返します。エージェントは処理を続行し、`get_weather_stateful` ツール（ステップ4の状態変更による「Fahrenheit」設定を使用）を呼び出し、天気を返します。この応答は `output_key` を介して `last_weather_report` を更新します。
2.  **BLOCK リクエスト:** コールバックが `weather_agent_v5_model_guardrail` に対して再度実行され、メッセージを検査し、「BLOCK」を見つけ、「Blocking LLM call!」を出力し、状態フラグを設定し、事前定義された `LlmResponse` を返します。エージェントの基盤となるLLMは、このターンでは*決して呼び出されません*。ユーザーにはコールバックのブロックメッセージが表示されます。
3.  **Hello Again:** コールバックが `weather_agent_v5_model_guardrail` に対して実行され、リクエストを許可します。その後、ルートエージェントは `greeting_agent` に委譲します。*注：ルートエージェントで定義された `before_model_callback` は、サブエージェントに自動的に適用されるわけではありません。* `greeting_agent` は通常どおり処理を進め、`say_hello` ツールを呼び出し、挨拶を返します。

入力安全層の実装に成功しました！ `before_model_callback` は、高価または潜在的に危険なLLM呼び出しが行われる*前に*ルールを適用し、エージェントの動作を制御する強力なメカニズムを提供します。次に、同様の概念を適用して、ツール使用自体の周りにガードレールを追加します。

## ステップ 6: 安全性の追加 - `before_tool_callback` によるツール引数ガードレール

ステップ5では、ユーザー入力がLLMに到達する*前*に検査し、潜在的にブロックするガードレールを追加しました。次に、LLMがツールを使用することを決定した*後*、そのツールが実際に実行される*前*に、もう1つの制御レイヤーを追加します。これは、LLMがツールに渡そうとしている*引数（arguments）*を検証するのに役立ちます。

ADKは、まさにこの目的のために `before_tool_callback` を提供します。

**`before_tool_callback` とは何ですか？**

*   LLMがその使用を要求し、引数を決定した後、特定のツール関数が実行される*直前*に実行されるPython関数です。
*   **目的:** ツール引数の検証、特定の入力に基づくツール実行の防止、引数の動的な変更、またはリソース使用ポリシーの適用。

**一般的なユースケース:**

*   **引数バリデーション:** LLMによって提供された引数が有効か、許可された範囲内か、または予想される形式に準拠しているかを確認します。
*   **リソース保護:** コストがかかる、制限されたデータにアクセスする、または望ましくない副作用を引き起こす可能性のある入力（例：特定のパラメータに対するAPI呼び出しのブロック）でツールが呼び出されるのを防ぎます。
*   **動的引数修正:** ツールが実行される前に、セッション状態またはその他のコンテキスト情報に基づいて引数を調整します。

**仕組み:**

1.  `tool: BaseTool`, `args: Dict[str, Any]`, `tool_context: ToolContext` を受け入れる関数を定義します。

    *   `tool`: 呼び出されようとしているツールオブジェクト（`tool.name` を検査）。
    *   `args`: LLMがツールのために生成した引数の辞書。
    *   `tool_context`: セッション状態（`tool_context.state`）、エージェント情報などへのアクセスを提供。

2.  関数内での処理:

    *   **検査:** `tool.name` と `args` 辞書を調べます。
    *   **修正:** `args` 辞書内の値を*直接*変更します。`None` を返すと、ツールはこれらの修正された引数で実行されます。
    *   **ブロック/オーバーライド（ガードレール）:** **辞書**を返します。ADKはこの辞書をツール呼び出しの*結果*として扱い、元のツール関数の実行を完全に*スキップ*します。辞書は、ブロックしているツールの予想される戻り形式と一致するのが理想的です。
    *   **許可:** `None` を返します。ADKは、（修正された可能性のある）引数で実際のツール関数を実行する処理を続行します。

**このステップでは、以下を行います:**

1.  `get_weather_stateful` ツールが都市「Paris」で呼び出されたかどうかを具体的にチェックする `before_tool_callback` 関数（`block_paris_tool_guardrail`）を定義します。
2.  「Paris」が検出された場合、コールバックはツールをブロックし、カスタムエラー辞書を返します。
3.  `before_model_callback` とこの新しい `before_tool_callback` の*両方*を含むようにルートエージェント（`weather_agent_v6_tool_guardrail`）を更新します。
4.  同じ状態保持セッションサービスを使用して、このエージェント用の新しいランナーを作成します。
5.  許可された都市とブロックされた都市（「Paris」）の天気をリクエストして、フローをテストします。

---

**1\. ツールガードレールコールバック関数の定義**

この関数は `get_weather_stateful` ツールをターゲットにします。`city` 引数をチェックします。それが「Paris」の場合、ツール独自のエラー応答に似たエラー辞書を返します。それ以外の場合は、`None` を返してツールの実行を許可します。

```python
# @title 1. before_tool_callback ガードレールの定義

# 必要なインポートが利用可能であることを確認
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from typing import Optional, Dict, Any # 型ヒント用

def block_paris_tool_guardrail(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict]:
    """
    'get_weather_stateful' が 'Paris' に対して呼び出されているか確認します。
    そうであれば、ツールの実行をブロックし、特定のエラー辞書を返します。
    そうでなければ、None を返してツール呼び出しを続行させます。
    """
    tool_name = tool.name
    agent_name = tool_context.agent_name # ツール呼び出しを試みているエージェント
    print(f"--- Callback: block_paris_tool_guardrail running for tool '{tool_name}' in agent '{agent_name}' ---")
    print(f"--- Callback: Inspecting args: {args} ---")

    # --- ガードレールロジック ---
    target_tool_name = "get_weather_stateful" # FunctionToolで使用される関数名と一致させる
    blocked_city = "paris"

    # 正しいツールであるか、そしてcity引数がブロックされた都市と一致するかを確認
    if tool_name == target_tool_name:
        city_argument = args.get("city", "") # 'city' 引数を安全に取得
        if city_argument and city_argument.lower() == blocked_city:
            print(f"--- Callback: Detected blocked city '{city_argument}'. Blocking tool execution! ---")
            # オプションで状態を更新
            tool_context.state["guardrail_tool_block_triggered"] = True
            print(f"--- Callback: Set state 'guardrail_tool_block_triggered': True ---")

            # ツールの予想される出力形式と一致する辞書を返してエラーとする
            # この辞書がツールの結果となり、実際のツール実行はスキップされます。
            return {
                "status": "error",
                "error_message": f"Policy restriction: Weather checks for '{city_argument.capitalize()}' are currently disabled by a tool guardrail."
            }
        else:
             print(f"--- Callback: City '{city_argument}' is allowed for tool '{tool_name}'. ---")
    else:
        print(f"--- Callback: Tool '{tool_name}' is not the target tool. Allowing. ---")


    # 上記のチェックで辞書が返されなかった場合、ツールの実行を許可
    print(f"--- Callback: Allowing tool '{tool_name}' to proceed. ---")
    return None # None を返すと、実際のツール関数の実行が許可されます

print("✅ block_paris_tool_guardrail function defined.")


```

---

**2\. 両方のコールバックを使用するためのルートエージェントの更新**

ルートエージェントを再度再定義します（`weather_agent_v6_tool_guardrail`）。今回は、ステップ5の `before_model_callback` と並んで `before_tool_callback` パラメータを追加します。

*自己完結型の実行に関する注意:* ステップ5と同様に、このエージェントを定義する前に、すべての前提条件（サブエージェント、ツール、`before_model_callback`）が実行コンテキストで定義または利用可能であることを確認してください。

```python
# @title 2. 両方のコールバックでルートエージェントを更新（自己完結型）

# --- 前提条件が定義されていることを確認 ---
# (以下が含まれているか、実行されていることを確認: Agent, LiteLlm, Runner, ToolContext,
#  MODEL constants, say_hello, say_goodbye, greeting_agent, farewell_agent,
#  get_weather_stateful, block_keyword_guardrail, block_paris_tool_guardrail)

# --- サブエージェントの再定義 (このコンテキストに存在することを確認) ---
greeting_agent = None
try:
    # 定義済みのモデル定数を使用
    greeting_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="greeting_agent", # 一貫性のために元の名前を保持
        instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting using the 'say_hello' tool. Do nothing else.",
        description="Handles simple greetings and hellos using the 'say_hello' tool.",
        tools=[say_hello],
    )
    print(f"✅ Sub-Agent '{greeting_agent.name}' redefined.")
except Exception as e:
    print(f"❌ Could not redefine Greeting agent. Check Model/API Key ({greeting_agent.model}). Error: {e}")

farewell_agent = None
try:
    # 定義済みのモデル定数を使用
    farewell_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="farewell_agent", # 元の名前を保持
        instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message using the 'say_goodbye' tool. Do not perform any other actions.",
        description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.",
        tools=[say_goodbye],
    )
    print(f"✅ Sub-Agent '{farewell_agent.name}' redefined.")
except Exception as e:
    print(f"❌ Could not redefine Farewell agent. Check Model/API Key ({farewell_agent.model}). Error: {e}")

# --- 両方のコールバックを持つルートエージェントの定義 ---
root_agent_tool_guardrail = None
runner_root_tool_guardrail = None

if ('greeting_agent' in globals() and greeting_agent and
    'farewell_agent' in globals() and farewell_agent and
    'get_weather_stateful' in globals() and
    'block_keyword_guardrail' in globals() and
    'block_paris_tool_guardrail' in globals()):

    root_agent_model = MODEL_GEMINI_2_0_FLASH

    root_agent_tool_guardrail = Agent(
        name="weather_agent_v6_tool_guardrail", # 新しいバージョン名
        model=root_agent_model,
        description="Main agent: Handles weather, delegates, includes input AND tool guardrails.",
        instruction="You are the main Weather Agent. Provide weather using 'get_weather_stateful'. "
                    "Delegate greetings to 'greeting_agent' and farewells to 'farewell_agent'. "
                    "Handle only weather, greetings, and farewells.",
        tools=[get_weather_stateful],
        sub_agents=[greeting_agent, farewell_agent],
        output_key="last_weather_report",
        before_model_callback=block_keyword_guardrail, # モデルガードレールを保持
        before_tool_callback=block_paris_tool_guardrail # <<< ツールガードレールを追加
    )
    print(f"✅ Root Agent '{root_agent_tool_guardrail.name}' created with BOTH callbacks.")

    # --- Runnerを作成、同じ状態保持セッションサービスを使用 ---
    if 'session_service_stateful' in globals():
        runner_root_tool_guardrail = Runner(
            agent=root_agent_tool_guardrail,
            app_name=APP_NAME,
            session_service=session_service_stateful # <<< ステップ4/5のサービスを使用
        )
        print(f"✅ Runner created for tool guardrail agent '{runner_root_tool_guardrail.agent.name}', using stateful session service.")
    else:
        print("❌ Cannot create runner. 'session_service_stateful' from Step 4/5 is missing.")

else:
    print("❌ Cannot create root agent with tool guardrail. Prerequisites missing.")


```

---

**3\. ツールガードレールをテストするための対話**

再び、前のステップと同じ状態保持セッション（`SESSION_ID_STATEFUL`）を使用して、インタラクションフローをテストしましょう。

1.  "New York" の天気リクエスト: 両方のコールバックを通過し、ツールが実行されます（状態から華氏設定を使用）。
2.  "Paris" の天気リクエスト: `before_model_callback` を通過します。LLMが `get_weather_stateful(city='Paris')` をリクエストします。`before_tool_callback` がインターセプトし、ツールをブロックしてエラー辞書を返します。エージェントはこのエラーを伝えます。
3.  "London" の天気リクエスト: 両方のコールバックを通過し、ツールが正常に実行されます。

```python
# @title 3. ツール引数ガードレールをテストするための対話
import asyncio # asyncioがインポートされていることを確認

# ツールガードレールエージェントのランナーが利用可能であることを確認
if 'runner_root_tool_guardrail' in globals() and runner_root_tool_guardrail:
    # ツールガードレールテスト会話のためのメイン非同期関数を定義。
    # この関数内の 'await' キーワードは非同期操作に必要です。
    async def run_tool_guardrail_test():
        print("\n--- Testing Tool Argument Guardrail ('Paris' blocked) ---")

        # 両方のコールバックを持つエージェントのランナーと既存の状態保持セッションを使用
        # よりクリーンなインタラクション呼び出しのためのヘルパーラムダを定義
        interaction_func = lambda query: call_agent_async(query,
                                                         runner_root_tool_guardrail,
                                                         USER_ID_STATEFUL, # 既存のユーザーIDを使用
                                                         SESSION_ID_STATEFUL # 既存のセッションIDを使用
                                                        )
        # 1. 許可された都市 (両方のコールバックを通過し、華氏状態を使用するはず)
        print("--- Turn 1: Requesting weather in New York (expect allowed) ---")
        await interaction_func("What's the weather in New York?")

        # 2. ブロックされた都市 (モデルコールバックは通過するが、ツールコールバックによってブロックされるはず)
        print("\n--- Turn 2: Requesting weather in Paris (expect blocked by tool guardrail) ---")
        await interaction_func("How about Paris?") # ツールコールバックがこれをインターセプトするはず

        # 3. 別の許可された都市 (再び正常に動作するはず)
        print("\n--- Turn 3: Requesting weather in London (expect allowed) ---")
        await interaction_func("Tell me the weather in London.")

    # --- `run_tool_guardrail_test` 非同期関数の実行 ---
    # 環境に基づいて以下の方法のいずれかを選択してください。

    # 方法 1: 直接 await (ノートブック/非同期REPLのデフォルト)
    # 環境がトップレベルのawaitをサポートしている場合（Colab/Jupyterノートブックなど）、
    # イベントループがすでに実行されているため、関数を直接awaitできます。
    print("Attempting execution using 'await' (default for notebooks)...")
    await run_tool_guardrail_test()

    # 方法 2: asyncio.run (標準Pythonスクリプト [.py] 用)
    # ターミナルから標準Pythonスクリプトとしてこのコードを実行する場合、
    # スクリプトコンテキストは同期的です。非同期関数を実行するための
    # イベントループを作成・管理するには `asyncio.run()` が必要です。
    # この方法を使用するには：
    # 1. 上記の `await run_tool_guardrail_test()` 行をコメントアウトします。
    # 2. 次のブロックのコメントを解除します：
    """
    import asyncio
    if __name__ == "__main__": # スクリプトが直接実行されたときのみ実行されるようにする
        print("Executing using 'asyncio.run()' (for standard Python scripts)...")
        try:
            # イベントループを作成し、非同期関数を実行し、ループを閉じます。
            asyncio.run(run_tool_guardrail_test())
        except Exception as e:
            print(f"An error occurred: {e}")
    """

    # --- 会話後の最終セッション状態の検査 ---
    # このブロックは、いずれかの実行方法が完了した後に実行されます。
    # オプション: ツールブロックトリガーフラグの状態を確認
    print("\n--- Inspecting Final Session State (After Tool Guardrail Test) ---")
    # この状態保持セッションに関連付けられたセッションサービスインスタンスを使用
    final_session = await session_service_stateful.get_session(app_name=APP_NAME,
                                                         user_id=USER_ID_STATEFUL,
                                                         session_id= SESSION_ID_STATEFUL)
    if final_session:
        # 安全なアクセスのために .get() を使用
        print(f"Tool Guardrail Triggered Flag: {final_session.state.get('guardrail_tool_block_triggered', 'Not Set (or False)')}")
        print(f"Last Weather Report: {final_session.state.get('last_weather_report', 'Not Set')}") # 成功していればロンドンの天気であるはず
        print(f"Temperature Unit: {final_session.state.get('user_preference_temperature_unit', 'Not Set')}") # 華氏であるはず
        # print(f"Full State Dict: {final_session.state}") # 詳細表示用
    else:
        print("\n❌ Error: Could not retrieve final session state.")

else:
    print("\n⚠️ Skipping tool guardrail test. Runner ('runner_root_tool_guardrail') is not available.")
```

---

出力を分析しましょう。

1.  **New York:** `before_model_callback` がリクエストを許可します。LLMが `get_weather_stateful` をリクエストします。`before_tool_callback` が実行され、引数 (`{'city': 'New York'}`) を検査し、"Paris" でないことを確認し、"Allowing tool..." を出力して `None` を返します。実際の `get_weather_stateful` 関数が実行され、状態から "Fahrenheit" を読み取り、天気レポートを返します。エージェントはこれを中継し、`output_key` を介して保存されます。
2.  **Paris:** `before_model_callback` がリクエストを許可します。LLMが `get_weather_stateful(city='Paris')` をリクエストします。`before_tool_callback` が実行され、引数を検査し、"Paris" を検出し、"Blocking tool execution!" を出力し、状態フラグを設定し、エラー辞書 `{'status': 'error', 'error_message': 'Policy restriction...'}` を返します。実際の `get_weather_stateful` 関数は **実行されません**。エージェントは、エラー辞書を*ツールの出力であるかのように*受け取り、そのエラーメッセージに基づいて応答を作成します。
3.  **London:** New Yorkと同様に動作し、両方のコールバックを通過してツールを正常に実行します。新しいロンドンの天気レポートは、状態内の `last_weather_report` を上書きします。

これで、何がLLMに到達するかだけでなく、LLMによって生成された特定の引数に基づいてエージェントのツールを*どのように*使用できるかを制御する重要な安全層を追加しました。`before_model_callback` や `before_tool_callback` のようなコールバックは、堅牢で安全かつポリシーに準拠したエージェントアプリケーションを構築するために不可欠です。

---

## 結論: エージェントチームの準備が整いました！

おめでとうございます！ 単一の基本的な天気エージェントの構築から始まり、Agent Development Kit (ADK) を使用して洗練されたマルチエージェントチームを構築する旅を無事に終えました。

**達成したことを振り返りましょう:**

*   単一のツール（`get_weather`）を備えた**基本的なエージェント**から始めました。
*   LiteLLMを使用してADKの**マルチモデルの柔軟性**を探求し、Gemini、GPT-4o、Claudeなどの異なるLLMで同じコアロジックを実行しました。
*   特化したサブエージェント（`greeting_agent`, `farewell_agent`）を作成し、ルートエージェントからの**自動委譲**を有効にすることで、**モジュール性**を取り入れました。
*   **セッション状態（Session State）**を使用してエージェントに**記憶**を与え、ユーザーの好み（`temperature_unit`）や過去の対話（`output_key`）を記憶できるようにしました。
*   `before_model_callback`（特定の入力キーワードのブロック）と `before_tool_callback`（都市「Paris」などの引数に基づくツール実行のブロック）の両方を使用して、重要な**安全ガードレール**を実装しました。

このプログレッシブな天気ボットチームの構築を通じて、複雑でインテリジェントなアプリケーションを開発するために不可欠なADKのコアコンセプトを実践的に学びました。

**重要なポイント:**

*   **エージェントとツール:** 機能と推論を定義するための基本的なビルディングブロックです。明確な指示とdocstringが最も重要です。
*   **Runnerとセッションサービス:** エージェントの実行を調整し、会話のコンテキストを維持するエンジンおよびメモリ管理システムです。
*   **委譲:** マルチエージェントチームを設計することで、専門化、モジュール性、および複雑なタスクの管理が向上します。エージェントの `description` は自動フロー（auto-flow）の鍵です。
*   **セッション状態 (`ToolContext`, `output_key`):** コンテキストを認識し、パーソナライズされたマルチターンの会話型エージェントを作成するために不可欠です。
*   **コールバック (`before_model`, `before_tool`):** 重要な操作（LLM呼び出しやツール実行）の*前に*、安全性、検証、ポリシー適用、および動的な修正を実装するための強力なフックです。
*   **柔軟性 (`LiteLlm`):** ADKは、パフォーマンス、コスト、機能のバランスを取りながら、タスクに最適なLLMを選択する力を提供します。

**次はどこへ？**

天気ボットチームは素晴らしい出発点です。ADKをさらに探求し、アプリケーションを強化するためのいくつかのアイデアを以下に示します。

1.  **実際の天気API:** `get_weather` ツールの `mock_weather_db` を実際の天気API（OpenWeatherMap, WeatherAPIなど）への呼び出しに置き換えます。
2.  **より複雑な状態:** より多くのユーザー設定（例：好みの場所、通知設定）や会話の要約をセッション状態に保存します。
3.  **委譲の洗練:** 異なるルートエージェントの指示やサブエージェントの説明を実験して、委譲ロジックを微調整します。「予報」エージェントを追加できるでしょうか？
4.  **高度なコールバック:**
    *   `after_model_callback` を使用して、LLMの応答が生成された*後*に、潜在的に再フォーマットしたりサニタイズしたりします。
    *   `after_tool_callback` を使用して、ツールから返された結果を処理またはログ記録します。
    *   エージェントレベルの開始/終了ロジックのために `before_agent_callback` または `after_agent_callback` を実装します。
5.  **エラー処理:** エージェントがツールのエラーや予期しないAPI応答を処理する方法を改善します。ツール内に再試行ロジックを追加することもできます。
6.  **永続的なセッションストレージ:** セッション状態を永続的に保存するために、`InMemorySessionService` の代替手段を探ります（例：FirestoreやCloud SQLなどのデータベースを使用 - カスタム実装または将来のADK統合が必要です）。
7.  **ストリーミングUI:** エージェントチームをWebフレームワーク（ADKストリーミングクイックスタートで示されているFastAPIなど）と統合して、リアルタイムのチャットインターフェースを作成します。

Agent Development Kitは、洗練されたLLM搭載アプリケーションを構築するための堅牢な基盤を提供します。このチュートリアルで扱った概念（ツール、状態、委譲、コールバック）を習得することで、ますます複雑化するエージェントシステムに取り組む準備が整います。

ハッピービルディング！