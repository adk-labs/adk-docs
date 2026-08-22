# ADK 向け Agents CLI クイックスタート

このガイドでは、Agents CLI を使用して Agent Development Kit (ADK) をすばやく起動および実行する方法について説明します。Antigravity、Claude Code、Codex などのコーディング エージェントとともに Agents CLI ツールセットを使用して、ADK エージェントの構築、評価、デプロイを行えます。詳細については、[Agents CLI](https://google.github.io/agents-cli/) のドキュメントを参照してください。
開始する前に、以下がインストールされていることを確認してください。

*   Python 3.11 以降: Agents CLI は Python 版 ADK エージェントをサポートしています
*   環境と依存関係を管理するための [`uv`](https://docs.astral.sh/uv/getting-started/installation/) ツール
*   スキルをインストールするための [Node.js](https://nodejs.org/en/download)
*   [Antigravity](https://antigravity.google/)、[Claude Code](https://docs.anthropic.com/en/docs/claude-code)、[Codex](https://github.com/openai/codex) などのコーディング エージェント

Google Cloud などのサービスに ADK エージェントをデプロイする場合は、以下のツールもインストールされていることを確認してください。

*   [Google Cloud CLI](https://cloud.google.com/sdk/docs/install)
*   [Terraform](https://developer.hashicorp.com/terraform/downloads)

## インストール

次のコマンドを実行して Agents CLI をインストールします。この手順により、`agents-cli` コマンド、ADK Python パッケージ、およびマシンの既存のコーディング エージェントに ADK スキルがインストールされます。

```shell
uvx google-agents-cli setup
```

??? tip "代替インストール方法"

    **pipx:**

    ```shell
    pipx install google-agents-cli && agents-cli setup
    ```

    **pip:**

    ```shell
    pip install google-agents-cli && agents-cli setup
    ```

    **スキルのみ:**

    ```shell
    npx skills add google/agents-cli
    ```

自分で実行する必要があるのはインストール コマンドのみです。インストール後は、コーディング エージェントを使用して ADK エージェントの構築と実行を行えます。

## 認証

Agents CLI でエージェントを実行するには、生成 AI API の認証情報が必要です。最も簡単なオプションは、Google AI Studio の Gemini API キーです。[API キー](https://aistudio.google.com/app/apikey) ページでキーを作成し、次のステップでプロジェクトをスキャフォールディングした後、その `.env` ファイルを開いて設定します。

```env title="更新: .env"
GEMINI_API_KEY=YOUR_API_KEY
```

SDK が Vertex AI の代わりにそのキーを使用するように、同じファイル内の 3 つの `GOOGLE_CLOUD_*` 行をコメントアウトします。

??? note "代わりに Google Cloud Agent Platform を使用する"

    すでに Google Cloud プロジェクトがある場合、Agents CLI はアプリケーション デフォルト認証情報 (ADC) を取得します。

    ```shell
    gcloud auth application-default login
    ```

    生成された `.env` ファイル内の `GOOGLE_CLOUD_*` 行のコメントを解除し、プロジェクト識別子に設定されていることを確認してください。ADK を使用した Google Cloud サービスおよびプロジェクトへの接続の詳細については、ADK の [Google Cloud セットアップ ガイド](/ja/get-started/google-cloud/) を参照してください。

## エージェントの構築

コーディング エージェントを開き、スキルが認識されていることを確認します。

=== "Antigravity"

    ```shell
    antigravity            # IDE またはターミナルから起動
    # 環境に Agents CLI スキルが一覧表示されていることを確認
    ```

=== "Claude Code"

    ```shell
    claude
    /skills                # リストに google-agents-cli-* エントリが表示されることを確認
    ```

=== "Codex"

    ```shell
    codex
    /skills                # リストに google-agents-cli-* エントリが表示されることを確認
    ```

??? note "他のコーディング エージェントの使用"

    Agents CLI は、[スキル](https://agentskills.io/what-are-skills) をサポートする任意のコーディング エージェントで動作します。ほとんどのエージェントは `/skills` コマンドまたは設定パネルを通じてスキルを一覧表示します。

次に、構築したい内容をコーディング エージェントに伝えます。

```shell title="コーディング エージェント プロンプト"
Use agents-cli to build an agent that turns long text into short
bullet-point summaries
```

コーディング エージェントは `google-agents-cli-workflow` および `google-agents-cli-scaffold` スキルをアクティブ化し、エージェントが呼び出すツール、期待される入出力、評価基準について確認の質問を行い、プロジェクトをスキャフォールディングします。

次に、コーディング エージェントは `google-agents-cli-adk-code` スキルを使用してエージェント コードを `app/agent.py` に記述します。最終的に、エージェント コード、テスト、および評価データセットを含む動作可能なプロジェクトが次のファイル構造で完成します。

```none
my-agent/
    app/
        agent.py                # メイン エージェント コード
        fast_api_app.py         # サーバー、テレメトリ、ルート
        app_utils/              # セッションおよびアーティファクト サービス
    tests/
        eval/                   # 評価データセットとメトリクス
        integration/            # エンドツーエンド エージェント テスト
        unit/
    pyproject.toml              # プロジェクト設定と依存関係
    agents-cli-manifest.yaml    # Agents CLI 設定
    Dockerfile                  # デプロイ用コンテナ イメージ
    GEMINI.md                   # コーディング エージェント向けプロジェクト ガイダンス
    .env                        # API キーまたはプロジェクト ID
```

エージェントのテスト、評価、デプロイを計画している場合は、このプロジェクト構造を使用してください。ADK 学習用の単一ファイル エージェントを作成する場合は、代わりに `adk create` コマンドを使用します。

## エージェントの実行

コーディング エージェントにローカル プレイグラウンドの起動を依頼するか、自身で実行します。

```console
agents-cli playground
```

このコマンドはホット リロード付きで ADK Web インターフェースを起動するため、編集内容がプロジェクトに即座に反映されます。プレイグラウンドには [http://localhost:8080](http://localhost:8080) からアクセスできます。左上でエージェントを選択し、いくつかの段落のテキストを貼り付けます。エージェントが箇条書きの短い要約で応答します。

## 次へ: エージェントの評価とデプロイ

Agents CLI をインストールし最初のエージェントを実行できたので、次のような指示を使用してコーディング エージェントで評価およびデプロイを行えます。

*   ***「このエージェントの評価を作成して実行して」***: スコープ設定時に定義した成功基準に対して [エージェントを評価](https://google.github.io/agents-cli/guide/evaluation/) します。コーディング エージェントが結果を採点し、原因別に失敗をグループ化し、合格するまでエージェントの指示を調整します。
*   ***「これを Cloud Run にデプロイして」***: Agent Runtime、Cloud Run、または GKE に [エージェントをデプロイ](/ja/deploy/agent-runtime/agents-cli/) します。
*   ***「エージェントのオブザーバビリティ インフラを設定して」***: プロンプト・レスポンス ログおよびコンテンツ ログを追加します。

評価、デプロイ、オブザーバビリティを含む完全なウォークスルーについては、Agents CLI の [チュートリアル: 最初のエージェントの構築](https://google.github.io/agents-cli/guide/quickstart-tutorial/) を参照してください。
