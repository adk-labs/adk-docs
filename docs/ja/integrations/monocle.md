---
catalog_title: Monocle
catalog_description: Open-source observability, tracing, and debugging of LLM applications
catalog_icon: /adk-docs/integrations/assets/monocle.png
catalog_tags: ["observability"]
---
# Monocleによるエージェントの可観測性

[Monocle](https://github.com/monocle2ai/monocle) は、LLMアプリケーションとAIエージェントの監視、デバッグ、改善のためのオープンソースの可観測性プラットフォームです。自動インスツルメンテーションを通じて、Google ADKアプリケーションに包括的なトレース機能を提供します。Monocleは、ローカルファイルやコンソール出力など、さまざまな宛先にエクスポートできるOpenTelemetry互換のトレースを生成します。

## 概要

MonocleはGoogle ADKアプリケーションを自動的にインスツルメントし、次のことを可能にします。

- **エージェントのインタラクションのトレース** - すべてのエージェントの実行、ツール呼び出し、モデルリクエストを完全なコンテキストとメタデータで自動的にキャプチャ
- **実行フローの監視** - 詳細なトレースを通じて、エージェントの状態、委任イベント、実行フローを追跡
- **問題のデバッグ** - 詳細なトレースを分析して、ボトルネック、失敗したツール呼び出し、予期しないエージェントの動作を迅速に特定
- **柔軟なエクスポートオプション** - 分析のためにトレースをローカルファイルまたはコンソールにエクスポート
- **OpenTelemetry互換** - OTLP互換のバックエンドで動作する標準のOpenTelemetryトレースを生成

Monocleは、次のGoogle ADKコンポーネントを自動的にインスツルメントします。

- **`BaseAgent.run_async`** - エージェントの実行、エージェントの状態、委任イベントをキャプチャします
- **`FunctionTool.run_async`** - ツール名、パラメータ、結果を含むツールの実行をキャプチャします
- **`Runner.run_async`** - リクエストコンテキストと実行フローを含むランナーの実行をキャプチャします

## インストール

### 1. 必要なパッケージのインストール { #install-required-packages }

```bash
pip install monocle_apptrace google-adk
```

## セットアップ

### 1. Monocleテレメトリーの構成 { #configure-monocle-telemetry }

Monocleは、テレメトリーを初期化するとGoogle ADKを自動的にインスツルメントします。アプリケーションの開始時に`setup_monocle_telemetry()`を呼び出すだけです。

```python
from monocle_apptrace import setup_monocle_telemetry

# Monocleテレメトリーを初期化 - Google ADKを自動的にインスツルメントします
setup_monocle_telemetry(workflow_name="my-adk-app")
```

これだけです！MonocleはGoogle ADKエージェント、ツール、ランナーを自動的に検出してインスツルメントします。

### 2. エクスポーターの構成 (オプション) { #configure-exporters }

デフォルトでは、MonocleはトレースをローカルJSONファイルにエクスポートします。環境変数を使用して異なるエクスポーターを構成できます。

#### コンソールへのエクスポート (デバッグ用)

環境変数を設定します。

```bash
export MONOCLE_EXPORTER="console"
```

#### ローカルファイルへのエクスポート (デフォルト)

```bash
export MONOCLE_EXPORTER="file"
```

または、`MONOCLE_EXPORTER`変数を省略するだけです。デフォルトは`file`です。

## 監視

トレースのセットアップが完了したので、すべてのGoogle ADK SDKリクエストはMonocleによって自動的にトレースされます。

```python
from monocle_apptrace import setup_monocle_telemetry
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

# Monocleテレメトリーを初期化 - ADKを使用する前に呼び出す必要があります
setup_monocle_telemetry(workflow_name="weather_app")

# ツール関数を定義
def get_weather(city: str) -> dict:
    """指定された都市の現在の天気予報を取得します。

    Args:
        city (str): 天気予報を取得する都市の名前です。

    Returns:
        dict: ステータスと結果、またはエラーメッセージです。
    """
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": (
                "ニューヨークの天気は晴れで、気温は摂氏25度（華氏77度）です。"
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"'{city}'の天気情報は利用できません。",
        }

# ツールを備えたエージェントを作成
agent = Agent(
    name="weather_agent",
    model="gemini-2.0-flash-exp",
    description="天気ツールを使用して質問に答えるエージェント。",
    instruction="利用可能なツールを使用して回答を見つける必要があります。",
    tools=[get_weather]
)

app_name = "weather_app"
user_id = "test_user"
session_id = "test_session"
runner = InMemoryRunner(agent=agent, app_name=app_name)
session_service = runner.session_service

await session_service.create_session(
    app_name=app_name,
    user_id=user_id,
    session_id=session_id
)

# エージェントを実行 (すべてのインタラクションは自動的にトレースされます)
async for event in runner.run_async(
    user_id=user_id,
    session_id=session_id,
    new_message=types.Content(role="user", parts=[
        types.Part(text="ニューヨークの天気はどうですか？")]
    )
):
    if event.is_final_response():
        print(event.content.parts[0].text.strip())
```

## トレースへのアクセス

デフォルトでは、Monocleはローカルディレクトリ`./monocle`にJSONファイルでトレースを生成します。ファイル名の形式は次のとおりです。

```
monocle_trace_{workflow_name}_{trace_id}_{timestamp}.json
```

各トレースファイルには、以下をキャプチャするOpenTelemetry互換のスパンの配列が含まれています。

- **エージェント実行スパン** - エージェントの状態、委任イベント、実行フロー
- **ツール実行スパン** - ツール名、入力パラメータ、出力結果
- **LLMインタラクションスパン** - モデル呼び出し、プロンプト、応答、トークン使用量 (Geminiまたは他のLLMを使用している場合)

これらのトレースファイルは、OpenTelemetry互換ツールを使用して分析したり、カスタム分析スクリプトを記述したりできます。

## VS Code拡張機能によるトレースの視覚化

[Okahu Trace Visualizer](https://marketplace.visualstudio.com/items?itemName=OkahuAI.okahu-ai-observability) VS Code拡張機能は、Visual Studio CodeでMonocleが生成したトレースを直接視覚化および分析するための対話型方法を提供します。

### インストール

1. VS Codeを開きます
2. `Ctrl+P` (Macでは`Cmd+P`) を押してクイックオープンを開きます
3. 次のコマンドを貼り付けてEnterキーを押します。

```
ext install OkahuAI.okahu-ai-observability
```

または、[VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=OkahuAI.okahu-ai-observability)からインストールすることもできます。

### 機能

拡張機能は以下を提供します。

- **カスタムアクティビティバーパネル** - トレースファイル管理専用のサイドバー
- **インタラクティブファイルツリー** - カスタムReact UIでトレースファイルを閲覧および選択
- **分割ビュー分析** - JSONデータビューアーと並行してガントチャートを視覚化
- **リアルタイム通信** - VS CodeとReactコンポーネント間のシームレスなデータフロー
- **VS Codeテーマ設定** - VS Codeのライト/ダークテーマと完全に統合

### 使用方法

1. Monocleトレースが有効なADKアプリケーションを実行した後、トレースファイルは`./monocle`ディレクトリに生成されます
2. VS CodeアクティビティバーからOkahu Trace Visualizerパネルを開きます
3. インタラクティブファイルツリーからトレースファイルを参照して選択します
4. 次の方法でトレースを表示します。
   - **ガントチャートの視覚化** - スパンのタイムラインと階層を表示
   - **JSONデータビューアー** - 詳細なスパン属性とイベントを検査
   - **トークン数** - LLM呼び出しのトークン使用量を表示
   - **エラーバッジ** - 失敗した操作をすばやく識別

![Monocle VS Code拡張機能](../assets/monocle-vs-code-ext.png)

## トレースされる内容

MonocleはGoogle ADKから次の情報を自動的にキャプチャします。

- **エージェントの実行**: エージェントの状態、委任イベント、実行フロー
- **ツール呼び出し**: ツール名、入力パラメータ、出力結果
- **ランナーの実行**: リクエストコンテキストと全体的な実行フロー
- **タイミング情報**: 各操作の開始時刻、終了時刻、期間
- **エラー情報**: 例外とエラーの状態

すべてのトレースはOpenTelemetry形式で生成され、OTLP互換のすべての可観測性バックエンドと互換性があります。

## サポートとリソース

- [Monocleドキュメント](https://docs.okahu.ai/monocle_overview/)
- [Monocle GitHubリポジトリ](https://github.com/monocle2ai/monocle)
- [Google ADK Travel Agentの例](https://github.com/okahu-demos/adk-travel-agent)
- [Discordコミュニティ](https://discord.gg/D8vDbSUhJX)
