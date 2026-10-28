# ライブエージェント向けサポート対象モデル

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span>
</div>

ライブエージェントは、`run_live()` の下で2つの[音声アーキテクチャ](architectures/index.md)のいずれかで実行されます。

- **[Speech-to-speech](architectures/speech-to-speech.md)**: 単一のネイティブ音声 Live モデルが、双方向接続を介して音声入力と音声出力を直接処理します。
- **[カスケード (Cascade)](architectures/cascade.md)**: 音声テキスト変換（STT）、任意のテキスト LLM、テキスト音声変換（TTS）を順番に連結します。

## ネイティブ音声モデル { #live-models }

ネイティブ音声モデルは、中間のテキスト音声変換（TTS）ステージを介さずに、音声を入力として受け取り音声をエンドツーエンドで出力します。これにより、単一の双方向接続上で自然な韻律（プロソディ）が実現されます。

| モデル | AI Studio | Agent Platform |
|---|---|---|
| Gemini 2.5 Flash Live | `gemini-2.5-flash-native-audio-preview-12-2025` (Preview) | `gemini-live-2.5-flash-native-audio` (GA) |
| Gemini 3.1 Flash Live | `gemini-3.1-flash-live-preview` (Preview) | 利用不可 |
| Gemini 3.8 Live | `gemini-3.8-live` (GA) | `gemini-3.8-live` (GA) |
| Gemini 3.8 Live Extended Thinking | `gemini-3.8-live-extended-thinking` (GA) | 利用不可 |

Gemini 2.5 Flash Live はバックエンドごとに異なる ID を持つ単一のモデルであり、提供される機能はどちらでも同じです。ADK の `LlmAgent.DEFAULT_LIVE_MODEL` は `gemini-live-2.5-flash-native-audio` であり、このセクションの例で使用されているモデルでもあります。

Gemini 3.1 Flash Live は AI Studio 専用であり、ノンブロッキングツールをサポートしていません。詳細については、[モデルごとの機能サポート](#per-model-feature-support)および [Gemini 3.1 Flash Live モデルページ](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-live-preview)を参照してください。

Gemini 3.8 Live は両方のバックエンドで動作します。Gemini 3.8 Live Extended Thinking はバックグラウンド推論（background reasoning）を追加したモデルで、AI Studio でのみ利用可能であり、[モデルごとの機能サポート](#per-model-feature-support)に記載されているエージェントへの変更が必要です。2つのモデルを比較するには、[AI Studio](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-live) または [Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-8-live) の Gemini 3.8 Live モデルページ、および [Gemini 3.8 Live Extended Thinking モデルページ](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-live-extended-thinking)を参照してください。

これらのモデルは**音声のみ**を生成し、会話の言語を自動的に検出します。`TEXT` レスポンスモダリティはサポートしていないため、発話とともにテキストを取得するには[音声の文字起こし](configuration.md#audio-transcription)を使用します。音声の選択、文字起こし、ターン検出については、[設定](configuration.md)で説明しています。

### モデルごとの機能サポート { #per-model-feature-support }

一部の ADK 設定は、実行しているモデルによって動作が異なります。

| 機能 | Gemini 2.5 Flash Live | Gemini 3.1 Flash Live | Gemini 3.8 Live | Gemini 3.8 Live Extended Thinking |
|---|---|---|---|---|
| [プロアクティブおよび感情的な対話](configuration.md#proactivity-and-affective-dialog) | `RunConfig` によるオプトイン | `RunConfig` 設定は無視される | `RunConfig` 設定は無視される | `RunConfig` 設定は無視される |
| [ノンブロッキングツール](tools.md#non-blocking-tools) | サポート | 非サポート | サポート | すべてのツールで必須（下記参照） |
| ツールの [`response_scheduling`](tools.md#non-blocking-tools) | サポート | 非サポート | サポート | 非サポート |
| [モデル応答の終了](events.md#interaction-status) | `turn_complete` | `turn_complete` | `turn_complete` | `interaction_status` が `IDLE`（下記参照） |

2.5 から新しいモデルに移行する際は、単一のサーバーイベントに複数のパートが含まれることがあるため、`parts[0]` を読み取るのではなく `event.content.parts` を反復処理してください。また、ターンの対象範囲に検出されたすべての音声アクティビティと動画フレームが含まれる場合があり、動画を継続的にストリーミングするとトークンコストが変化します。アップストリームの[移行ノート](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-live-preview#migrating-from-gemini-25-flash-live)を参照してください。

[AI Studio](https://ai.google.dev/gemini-api/docs/models) および [Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/google-models) ドキュメントの各モデルページでは、サポートされている思考レベル（thinking level）など、モデルレベルの動作について説明しています。ADK では、エージェントの `generate_content_config.thinking_config` を通じて思考を設定します。

Gemini 3.8 Live Extended Thinking には ADK Python 2.10 以降が必要であり、エージェントに次の2つの変更を加える必要があります。

- **ノンブロッキングツール**: すべてのツールで `behavior = types.Behavior.NON_BLOCKING` を設定し、`response_scheduling` は未設定のままにします。[ノンブロッキングツール](tools.md#non-blocking-tools)を参照してください。
- **インタラクションステータス**: リクエストごとに `turn_complete` が複数回届くことがあるため、`event.interaction_status`（`/run_live` 上では `interactionStatus`）を読み取ります。この値は、モデルがまだリクエストを処理している間は `IN_PROGRESS` となり、完了すると `IDLE` になります。[インタラクションステータス](events.md#interaction-status)を参照してください。

## カスケードモデル

[カスケードアーキテクチャ](architectures/cascade.md)では、推論ステージに[エージェント向けモデル](../agents/models/index.md)の任意のテキストモデルを使用できます。音声ステージについては、ADK は以下の Gemini 音声モデルをサポートしています。

| ステージ | モデル |
|---|---|
| **音声テキスト変換 (`GeminiSTT`)** | `gemini-3.5-transcribe-live` |
| **テキスト音声変換 (`GeminiTTS`)** | `gemini-3.8-flash-lite-tts`、`gemini-3.8-flash-tts` |

`CascadeLive` には、[ElevenLabs モデル](https://elevenlabs.io/docs/overview/models)用の組み込みアダプタ（`ElevenLabsSTT`、`ElevenLabsTTS`）も含まれており、[カスタム変換](architectures/cascade.md#custom-speech-transforms)を通じて他の任意の音声プロバイダもサポートします。

## バックエンドの選択

Gemini モデルには2つのバックエンドのいずれかを介してアクセスします。ADK は同じコードで両方と通信し、環境変数で切り替えることができるため、一方で開発してもう一方にデプロイできます。

| | AI Studio | Agent Platform |
|---|---|---|
| **正式名称** | Google AI Studio | Gemini Enterprise Agent Platform |
| **最適な用途** | プロトタイピング、開発 | 本番運用、エンタープライズ |
| **認証** | API キー (`GOOGLE_API_KEY`) | Cloud 認証情報 (`GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`) |
| **セットアップ** | API キーのみ | Cloud プロジェクトのセットアップ |
| **制限** | [セッション時間と同時実行数](#platform-limits-and-quotas) | [セッション時間と同時実行数](#platform-limits-and-quotas) |

`GOOGLE_GENAI_USE_ENTERPRISE` 環境変数（AI Studio は `FALSE`、Agent Platform は `TRUE`）で切り替えます。コードの変更は不要です。セットアップについては[クイックスタート](get-started/streaming-python.md)を参照してください。

!!! note "Agent Platform: Live API モデルでは `global` ロケーションはサポートされていません"

    Live API モデルは `GOOGLE_CLOUD_LOCATION=global` では利用できません。`us-central1`、`us-east1`、または `asia-northeast1` などのリージョンエンドポイントを使用し、デプロイする前に [Agent Platform のロケーション](https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/locations)のエンドポイントとロケーションの対応表で確認してください。

## プラットフォームの制限と割り当て { #platform-limits-and-quotas }

両方のバックエンドで、接続とセッションの実行時間、および同時に実行できるセッション数に上限が設けられています。これらの数値は変更される可能性があるため、アップストリームの公式ドキュメントを正式な情報源として扱い、本番環境で制限に依存する前に確認してください。

| 制限 | AI Studio | Agent Platform |
|---|---|---|
| セッション時間（音声のみ） | 15 分 | 15 分 |
| セッション時間（音声 + 動画） | 2 分 | 2 分 |
| 接続の存続時間 | 約 10 分 | 約 10 分 |
| 同時実行セッション数 | [レート制限](https://ai.google.dev/gemini-api/docs/rate-limits)を参照 | 従量課金制でプロジェクトあたり最大 1,000。プロビジョニングされたスループットの場合は無制限 |

Agent Platform では、上記の音声のみの制限とは別に、会話セッションがデフォルトで 10 分に制限されます。

[コンテキストウィンドウの圧縮](sessions.md#context-window-compression)を有効にすると、セッションを期間制限を超えて延長できます。Agent Platform では、[Cloud Console の割り当てページ](https://console.cloud.google.com/iam-admin/quotas)の **「Bidi generate content concurrent requests」** から同時セッション数の増加をリクエストできます。最新の数値については、[AI Studio](https://ai.google.dev/gemini-api/docs/live-api/capabilities)、[Gemini API のレート制限](https://ai.google.dev/gemini-api/docs/rate-limits)、および [Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/live-api/start-manage-session) のドキュメントを確認してください。

## モデル名の扱い方

モデル名をハードコードするのではなく、環境変数から読み取ります。同じモデルでも AI Studio と Agent Platform で ID が異なるため、`.env` 変数を使用することで1つのコードベースで両方のバックエンドに対応でき、モデルの非推奨化（deprecation）からも保護されます。

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

# AI Studio または Agent Platform
# DEMO_AGENT_MODEL=gemini-3.8-live

# AI Studio（マルチステップ推論および低速なツール向け）
# DEMO_AGENT_MODEL=gemini-3.8-live-extended-thinking

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

1. **バックエンドの選択**: プロトタイピングには AI Studio、本番環境には Agent Platform を選択します。これにより上の表の ID 列が決まり、Agent Platform では選択肢が Gemini 2.5 Flash Live と Gemini 3.8 Live に絞られます。
2. **現在の利用可能性の確認**: 上のモデル表と公式ドキュメントを参照してください。
3. **環境変数の設定**: `.env` ファイルにモデル名を設定し、エージェント作成時にそこから読み取ります。

## モデルの互換性と利用可能性

モデルの互換性と利用可能性に関する最新情報については、以下を参照してください。

- **AI Studio**: [Gemini モデルドキュメント](https://ai.google.dev/gemini-api/docs/models)および [Live API 機能ガイド](https://ai.google.dev/gemini-api/docs/live-api/capabilities)
- **Agent Platform**: [Live API の概要](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/live-api)および [Agent Platform モデルドキュメント](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/google-models)

本番環境にデプロイする前に、必ず公式ドキュメントでモデルの利用可能性と機能サポートを確認してください。
