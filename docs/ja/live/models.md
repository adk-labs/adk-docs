# ライブエージェント向けサポート対象モデル

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span>
</div>

ライブエージェントには双方向接続を維持できるモデルが必要であり、標準の Gemini モデルでは対応できません。ライブエージェント以外で ADK がサポートするモデル、および非 Gemini プロバイダーについては、[エージェント用モデル](../agents/models/index.md) を参照してください。

## ライブモデル

ライブエージェントは、中間の Text-to-Speech（音声合成）段階を経由せず、音声を入力として受け取り音声を直接出力するモデル上でエンドツーエンドで実行されます。これにより、自然な抑揚（プロソディ）を持つ人間のような音声が実現されます。これは、標準の Gemini モデルが双方向接続上で実行できないことです。

同じモデルでもバックエンドごとに異なる ID を持ちます。

| モデル | AI Studio | Agent Platform |
|---|---|---|
| Gemini 2.5 Flash Live | `gemini-2.5-flash-native-audio-preview-12-2025` | `gemini-live-2.5-flash-native-audio` |

`gemini-live-2.5-flash-native-audio` は ADK の `LlmAgent.DEFAULT_LIVE_MODEL` であり、このセクションの例で使用されているモデルです。

## バックエンドの選択

ライブモデルには 2 つのバックエンドのいずれかを介してアクセスします。ADK は同じコードで両方と通信します。環境変数で切り替えることができるため、一方の開発環境で開発し、もう一方の本番環境にデプロイできます。

| | AI Studio | Agent Platform |
|---|---|---|
| **正式名称** | Google AI Studio | Gemini Enterprise Agent Platform |
| **最適な用途** | プロトタイピング、開発 | 本番運用、エンタープライズ |
| **認証** | API キー (`GOOGLE_API_KEY`) | Cloud 認証情報 (`GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`) |
| **セットアップ** | API キーのみ | Cloud プロジェクトのセットアップ |
| **制限** | [セッション時間と同時実行数](#platform-limits-and-quotas) | [セッション時間と同時実行数](#platform-limits-and-quotas) |

`GOOGLE_GENAI_USE_ENTERPRISE` 環境変数（AI Studio は `FALSE`、Agent Platform は `TRUE`）で切り替えます。コードの変更は不要です。セットアップについては [クイックスタート](get-started/streaming-python.md) を参照してください。

!!! note "Agent Platform: ロケーションのサポート確認"

    Agent Platform では、ロケーション（リージョン）によってライブモデルの利用可否が異なります。デプロイする前に、[Agent Platform のロケーション](https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/locations) のエンドポイントとロケーションの対応表で `GOOGLE_CLOUD_LOCATION` を確認してください。`us-central1`、`us-east1`、または `asia-northeast1` などのリージョンエンドポイントが安全なデフォルトです。

これらのモデルは、自然なプロソディを持つ音声を直接生成し、会話の言語を独自に検出します。音声、文字起こし、ターン検出など、その上に設定する項目については [設定](configuration.md) で説明されています。

モデルレベルで固定されている特性が 1 つあります。ライブモデルは**音声のみ**を出力します。`TEXT` レスポンスモダリティをサポートしていないため、発話とともにテキストを取得するには [音声の文字起こし](configuration.md#audio-transcription) を使用します。

### モデルごとの機能サポート

一部の `RunConfig` 設定は、実行しているモデルに依存します。

| 機能 | `gemini-live-2.5-flash-native-audio` |
|---|---|
| [プロアクティブおよび感情的な対話](configuration.md#proactivity-and-affective-dialog) | `RunConfig` によるオプトイン |
| ツールの [`response_scheduling`](tools.md#non-blocking-tools) | サポート |

## プラットフォームの制限と割り当て

両方のバックエンドで、接続とセッションの実行時間、および同時に実行できるセッション数に上限が設けられています。これらの数値は変更される可能性があるため、アップストリームの公式ドキュメントを正式な情報源として扱い、本番環境で制限に依存する前に確認してください。

| 制限 | AI Studio | Agent Platform |
|---|---|---|
| セッション時間（音声のみ） | 15 分 | 15 分 |
| セッション時間（音声 + 動画） | 2 分 | 2 分 |
| 接続の存続時間 | 約 10 分 | 約 10 分 |
| 同時実行セッション数 | [レート制限](https://ai.google.dev/gemini-api/docs/rate-limits) を参照 | 従量課金制でプロジェクトあたり最大 1,000。プロビジョニングされたスループットの場合は無制限 |

Agent Platform では、上記の音声のみの制限とは別に、会話セッションがデフォルトで 10 分に制限されます。

[コンテキストウィンドウの圧縮](sessions.md#context-window-compression) を有効にすると、セッションを期間制限を超えて延長できます。Agent Platform では、[Cloud Console の割り当てページ](https://console.cloud.google.com/iam-admin/quotas) の **「Bidi generate content concurrent requests」** から同時セッション数の増加をリクエストできます。最新の数値については、[AI Studio](https://ai.google.dev/gemini-api/docs/live-api/capabilities)、[Gemini API のレート制限](https://ai.google.dev/gemini-api/docs/rate-limits)、および [Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/live-api/start-manage-session) のドキュメントを確認してください。

## モデル名の扱い方

モデル名をハードコードするのではなく、環境変数から読み取ります。同じモデルでも AI Studio と Agent Platform で ID が異なるため、`.env` 変数を使用することで 1 つのコードベースで両方のバックエンドに対応でき、モデルの非推奨化（deprecation）からも保護されます。

**推奨パターン:**

```python
import os
from google.adk.agents import Agent

# 適切なデフォルト値へのフォールバックを伴う環境変数の使用
agent = Agent(
    name="my_agent",
    model=os.getenv("DEMO_AGENT_MODEL", "gemini-live-2.5-flash-native-audio"),
    tools=[...],
    instruction="..."
)
```

**環境変数を使用する理由:**

- **バックエンド固有の ID**: 同じモデルでも AI Studio と Agent Platform で名前が異なるため、両者間を移動するにはモデル ID を変更する必要があります。環境変数を使用することで、コードからそれを排除できます。
- **モデルの利用可能性の変化**: モデルは定期的にリリースされ、非推奨化されます。1年前に書かれたライブエージェントが、存在しなくなったモデルにコード上で固定されるべきではありません。
- **環境固有の設定**: 開発、ステージング、本番の各環境で異なるモデルを使用します。

**`.env` ファイルの設定:**

```bash
# AI Studio
DEMO_AGENT_MODEL=gemini-2.5-flash-native-audio-preview-12-2025

# Agent Platform
# DEMO_AGENT_MODEL=gemini-live-2.5-flash-native-audio
```

!!! note "環境変数の読み込み順序"

    `python-dotenv` で `.env` ファイルを使用する場合、環境変数を読み取るモジュールをインポートする**前**に `load_dotenv()` を呼び出す必要があります。そうしないと、`os.getenv()` は `None` を返し、`.env` の設定を無視してデフォルト値にフォールバックします。

    **`main.py` での正しい順序:**

    ```python
    from dotenv import load_dotenv
    from pathlib import Path

    # エージェントをインポートする前に .env ファイルをロード
    load_dotenv(Path(__file__).parent / ".env")

    # これで環境変数を使用するモジュールを安全にインポート可能
    from google_search_agent.agent import agent
    ```

    **間違った順序（機能しません）:**

    ```python
    from dotenv import load_dotenv
    from google_search_agent.agent import agent  # エージェントはここで環境変数を読み取ってしまう

    # 遅すぎます！ エージェントはすでにデフォルトモデルで初期化されています
    load_dotenv(Path(__file__).parent / ".env")
    ```

    これは Python のインポート動作によるものです。モジュールをインポートすると、そのトップレベルコードが即座に実行されます。エージェントモジュールがインポート時に `os.getenv("DEMO_AGENT_MODEL")` を呼び出す場合、`.env` ファイルはすでに読み込まれている必要があります。

**適切なモデルの選択:**

1. **バックエンドの選択**: プロトタイピングには AI Studio、本番環境には Agent Platform を選択します。これにより、上の表の ID 列が決まります。
2. **現在の利用可能性の確認**: 上のモデル表と公式ドキュメントを参照してください。
3. **環境変数の設定**: `.env` ファイルにモデル名を設定し、エージェント作成時にそこから読み取ります。

## モデルの互換性と利用可能性

モデルの互換性と利用可能性に関する最新情報については、以下を参照してください。

- **AI Studio**: [Gemini モデルドキュメント](https://ai.google.dev/gemini-api/docs/models) および [Live API 機能ガイド](https://ai.google.dev/gemini-api/docs/live-api/capabilities)
- **Agent Platform**: [Live API の概要](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/live-api) および [Agent Platform モデルドキュメント](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/google-models)

本番環境にデプロイする前に、必ず公式ドキュメントでモデルの利用可能性と機能サポートを確認してください。
