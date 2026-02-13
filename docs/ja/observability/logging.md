# エージェント開発キット（ADK）におけるロギング

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

エージェント開発キット（ADK）は、Pythonの標準`logging`モジュールを使用して、柔軟かつ強力なロギング機能を提供します。これらのログの設定方法と解釈を理解することは、エージェントの振る舞いを監視し、問題を効果的にデバッグするために非常に重要です。

## ロギングの思想

ADKのロギングに対するアプローチは、デフォルトで過度に冗長になることなく、詳細な診断情報を提供することです。アプリケーション開発者が設定できるように設計されており、開発環境であれ本番環境であれ、特定のニーズに合わせてログ出力を調整できます。

- **標準ライブラリ:** 標準の`logging`ライブラリを使用しているため、これと互換性のある任意の設定やハンドラはADKでも機能します。
- **階層的なロガー:** ロガーはモジュールパスに基づいて階層的に命名されます（例: `google_adk.google.adk.agents.llm_agent`）。これにより、フレームワークのどの部分がログを生成するかをきめ細かく制御できます。
- **ユーザーによる設定:** フレームワーク自体はロギングを設定しません。アプリケーションのエントリーポイントで目的のロギング設定を行うのは、フレームワークを使用する開発者の責任です。

## ロギングの設定方法

メインのアプリケーションスクリプト（例: `main.py`）で、エージェントを初期化して実行する前にロギングを設定できます。最も簡単な方法は`logging.basicConfig`を使用することです。

### 設定例

`DEBUG`レベルのメッセージを含む詳細なロギングを有効にするには、スクリプトの先頭に以下を追加します。

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)

# ADKエージェントのコードはここに続きます...
# from google.adk.agents import LlmAgent
# ...
```

### ADK CLIを使用したロギング設定

ADKの組み込みWebサーバーやAPIサーバーを使用してエージェントを実行する場合、コマンドラインから直接ログの詳細度を簡単に制御できます。`adk web`、`adk api_server`、`adk deploy cloud_run`コマンドはすべて`--log_level`オプションを受け入れます。

これにより、エージェントのソースコードを変更することなく、簡単にロギングレベルを設定できます。

> **注意:** コマンドラインでの設定は、ADKのロガーに対してプログラムによる設定（`logging.basicConfig`など）よりも常に優先されます。本番環境では`INFO`または`WARNING`を使用し、問題解決時のみ`DEBUG`を有効にすることが推奨されます。

**`adk web`の使用例:**

`DEBUG`レベルのロギングでWebサーバーを起動するには、次のように実行します。

```bash
adk web --log_level DEBUG path/to/your/agents_dir
```

`--log_level`オプションで利用可能なログレベルは次のとおりです。

- `DEBUG`
- `INFO` (デフォルト)
- `WARNING`
- `ERROR`
- `CRITICAL`

> `-v`または`--verbose`を`--log_level DEBUG`のショートカットとして使用することもできます。
>
> ```bash
> adk web -v path/to/your/agents_dir
> ```

### ログレベル

ADKは標準のログレベルを使用してメッセージを分類します。設定されたレベルによって、どの情報が記録されるかが決まります。

| レベル | 説明 | 記録される情報の種類 |
| :--- | :--- | :--- |
| **`DEBUG`** | **デバッグに不可欠です。** きめ細かい診断情報のための最も詳細なレベルです。 | <ul><li>**完全なLLMプロンプト:** システム指示、履歴、ツールを含む、言語モデルに送信された完全なリクエスト。</li><li>サービスからの詳細なAPIレスポンス。</li><li>内部の状態遷移と変数値。</li></ul> |
| **`INFO`** | エージェントのライフサイクルに関する一般情報です。 | <ul><li>エージェントの初期化と起動。</li><li>セッションの作成および削除イベント。</li><li>ツール名と引数を含むツールの実行。</li></ul> |
| **`WARNING`** | 潜在的な問題や非推奨機能の使用を示します。エージェントは機能し続けますが、注意が必要な場合があります。 | <ul><li>非推奨のメソッドやパラメータの使用。</li><li>システムが回復した、致命的ではないエラー。</li></ul> |
| **`ERROR`** | ある操作の完了を妨げた深刻なエラーです。 | <ul><li>外部サービス（例：LLM、Session Service）へのAPI呼び出しの失敗。</li><li>エージェント実行中の未処理の例外。</li><li>設定エラー。</li></ul> |

> **注意:** 本番環境では`INFO`または`WARNING`の使用を推奨します。`DEBUG`ログは非常に冗長であり、機密情報を含む可能性があるため、積極的に問題をトラブルシューティングしている場合にのみ有効にしてください。

## ログの読み方と理解

`basicConfig`の例にある`format`文字列が、各ログメッセージの構造を決定します。

以下はログエントリのサンプルです。

```text
2025-07-08 11:22:33,456 - DEBUG - google_adk.google.adk.models.google_llm - LLM Request: contents { ... }
```

| ログセグメント                  | フォーマット指定子 | 意味                                           |
| ------------------------------- | ---------------- | ---------------------------------------------- |
| `2025-07-08 11:22:33,456`       | `%(asctime)s`    | タイムスタンプ                                 |
| `DEBUG`                         | `%(levelname)s`  | 重要度レベル                                   |
| `google_adk.models.google_llm`  | `%(name)s`       | ロガー名（ログを生成したモジュール）           |
| `LLM Request: contents { ... }` | `%(message)s`    | 実際のログメッセージ                           |

ロガー名を読めば、ログの発生源をすぐに特定し、エージェントのアーキテクチャ内でのコンテキストを理解できます。

## ログを使用したデバッグ：実践例

**シナリオ:** エージェントが期待される出力を生成せず、LLMに送信されるプロンプトが不正確か、情報が欠落している疑いがあります。

**手順:**

1.  **DEBUGロギングの有効化:** `main.py`で、設定例に示したようにロギングレベルを`DEBUG`に設定します。

    ```python
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )
    ```

2.  **エージェントの実行:** 通常通りにエージェントのタスクを実行します。

3.  **ログの確認:** コンソール出力から`google.adk.models.google_llm`ロガーからの`LLM Request:`で始まるメッセージを探します。

    ```log
    ...
    2025-07-10 15:26:13,778 - DEBUG - google_adk.google.adk.models.google_llm - Sending out request, model: gemini-2.0-flash, backend: GoogleLLMVariant.GEMINI_API, stream: False
    2025-07-10 15:26:13,778 - DEBUG - google_adk.google.adk.models.google_llm - 
    LLM Request:
    -----------------------------------------------------------
    System Instruction:

          You roll dice and answer questions about the outcome of the dice rolls.
          You can roll dice of different sizes.
          ...
        

    You are an agent. Your internal name is "hello_world_agent".

    The description about you is "hello world agent that can roll a dice of 8 sides and check prime numbers."
    -----------------------------------------------------------
    Contents:
    {"parts":[{"text":"Roll a 6 sided dice"}],"role":"user"}
    {"parts":[{"function_call":{"args":{"sides":6},"name":"roll_die"}}],"role":"model"}
    {"parts":[{"function_response":{"name":"roll_die","response":{"result":2}}}],"role":"user"}
    -----------------------------------------------------------
    Functions:
    roll_die: {'sides': {'type': <Type.INTEGER: 'INTEGER'>}} 
    check_prime: {'nums': {'items': {'type': <Type.INTEGER: 'INTEGER'>}, 'type': <Type.ARRAY: 'ARRAY'>}} 
    -----------------------------------------------------------

    2025-07-10 15:26:13,779 - INFO - google_genai.models - AFC is enabled with max remote calls: 10.
    2025-07-10 15:26:14,309 - INFO - google_adk.google.adk.models.google_llm - 
    LLM Response:
    -----------------------------------------------------------
    Text:
    I have rolled a 6 sided die, and the result is 2.
    ...
    ```

4.  **プロンプトの分析:** 記録されたリクエストの`System Instruction`、`contents`、`functions`セクションを調べることで、以下を確認できます。
    -   システム指示は正しいか？
    -   会話履歴（`user`と`model`のターン）は正確か？
    -   最新のユーザーからのクエリは含まれているか？
    -   正しいツールがモデルに提供されているか？
    -   モデルによってツールは正しく呼び出されているか？
    -   モデルが応答するのにどれくらいの時間がかかっているか？

この詳細な出力により、不適切なプロンプトエンジニアリングからツールの定義に関する問題まで、幅広い問題をログファイルから直接診断できます。