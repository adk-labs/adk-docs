# Agent Engine へのデプロイメント（Agent Starter Pack）

<div class="language-support-tag" title="Vertex AI Agent Engine は現在 Python のみをサポートしています。">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

このデプロイ手順では、[Agent Starter Pack](https://github.com/GoogleCloudPlatform/agent-starter-pack)（ASP）と ADK コマンドラインインターフェース（CLI）を使用してデプロイを行う方法を説明します。
ASP による Agent Engine ランタイムへのデプロイは高速化パスであり、**開発とテスト**用途でのみ使用してください。
ASP は ADK エージェントワークフローを実行するために厳密には不要な Google Cloud リソースを構成するため、運用デプロイを行う前に構成内容を必ず十分に確認してください。

このガイドでは、ASP ツールを使って既存プロジェクトにプロジェクトテンプレートを適用し、デプロイ成果物を追加して、エージェントプロジェクトをデプロイ可能な状態にする方法を示します。
この手順は、ADK プロジェクトをデプロイするために必要な Google Cloud サービスを構成するためのものです。

-   [事前準備](#prerequisites-ad): Google Cloud アカウント、プロジェクト、および必要なソフトウェアをインストールします。
-   [ADK プロジェクトの準備](#prepare-ad): 既存の ADK プロジェクトファイルをデプロイ準備状態に変更します。
-   [Google Cloud プロジェクトへの接続](#connect-ad): 開発環境を Google Cloud とプロジェクトに接続します。
-   [ADK プロジェクトのデプロイ](#deploy-ad): Google Cloud プロジェクトに必須サービスをプロビジョニングして、コードをアップロードします。

デプロイ済みエージェントのテストについては、[デプロイ済みエージェントのテスト](/adk-docs/deploy/agent-engine/test/)を参照してください。
ASP の CLI ツールに関する詳細は、
[CLI リファレンス](https://googlecloudplatform.github.io/agent-starter-pack/cli/enhance.html)
および
[開発ガイド](https://googlecloudplatform.github.io/agent-starter-pack/guide/development-guide.html)
をご参照ください。

### 事前準備 {#prerequisites-ad}

このデプロイパスを使用するには、次のリソースを準備する必要があります。

-   **Google Cloud アカウント**: 以下の管理者権限を持つこと。
    -   **Google Cloud プロジェクト**: [請求が有効化された](https://cloud.google.com/billing/docs/how-to/modify-project)空の Google Cloud プロジェクト。
        プロジェクト作成方法は [プロジェクトの作成と管理](https://cloud.google.com/resource-manager/docs/creating-managing-projects)を参照してください。
-   **Python 環境**: [ASP プロジェクト](https://googlecloudplatform.github.io/agent-starter-pack/guide/getting-started.html)がサポートする Python バージョン。
-   **uv ツール**: Python 開発環境の管理と ASP ツールの実行に使用します。
    インストール手順は [uv インストール](https://docs.astral.sh/uv/getting-started/installation/)を参照してください。
-   **Google Cloud CLI ツール**: gcloud CLI。インストール手順は
    [Google Cloud Command Line Interface](https://cloud.google.com/sdk/docs/install)を参照してください。
-   **Make ツール**: ビルド自動化ツール。ほとんどの Unix 系システムに付属します。
    詳細は [Make のドキュメント](https://www.gnu.org/software/make/) を参照してください。

### ADK プロジェクトの準備 {#prepare-ad}

ADK プロジェクトを Agent Engine にデプロイする場合、デプロイ操作をサポートする追加ファイルが必要です。以下の ASP コマンドは、既存プロジェクトをバックアップした後、デプロイ用ファイルを追加します。

このガイドは、デプロイ対象の ADK プロジェクトを更新すると仮定しています。
ADK プロジェクトがない場合やテスト用プロジェクトを使う場合は、先に
[Quickstart](/adk-docs/get-started/quickstart/)
のガイドを実行して
[multi_tool_agent](https://github.com/google/adk-docs/tree/main/examples/python/snippets/get-started/multi_tool_agent)
のプロジェクトを作成してください。以下の例では `multi_tool_agent` を使用します。

ADK プロジェクトを Agent Engine へのデプロイ向けに準備するには:

1.  開発環境の端末で、エージェントフォルダを含む
    **親ディレクトリ**に移動します。例:

    ```
    your-project-directory/
    ├── multi_tool_agent/
    │   ├── __init__.py
    │   ├── agent.py
    │   └── .env
    ```

    `your-project-directory/` に移動します。

1.  ASP の `enhance` コマンドを実行して、デプロイに必要なファイルをプロジェクトに追加します。

    ```shell
    uvx agent-starter-pack enhance --adk -d agent_engine
    ```

1.  ASP ツールの指示に従います。通常、既定値をすべて受け入れて進めて問題ありません。
    ただし **GCP リージョン**の選択時は
    [サポートされるリージョン](https://docs.cloud.google.com/agent-builder/locations#supported-regions-agent-engine)
    を選択してください。

処理が正常に完了すると、次のメッセージが表示されます。

```
> Success! Your agent project is ready.
```

!!! tip "ノート"
    ASP ツールは実行中に Google Cloud への接続を求めるリマインダーを表示する場合がありますが、この段階では
    *必須ではありません*。

ADK プロジェクトに対する ASP の変更点は、[ADK プロジェクトの変更](#adk-asp-changes)を参照してください。

### Google Cloud プロジェクトへの接続 {#connect-ad}

ADK プロジェクトをデプロイする前に、Google Cloud とプロジェクトに接続します。Google Cloud アカウントでログインした後、
デプロイ対象のプロジェクトがアカウントから見えることと、現在のプロジェクトとして設定されていることを確認します。

Google Cloud に接続してプロジェクトを確認するには:

1.  開発環境のターミナルで Google Cloud アカウントにログインします。

    ```shell
    gcloud auth application-default login
    ```

1.  対象プロジェクトを設定します。

    ```shell
    gcloud config set project your-project-id-xxxxx
    ```

1.  対象プロジェクトが設定されていることを確認します。

    ```shell
    gcloud config get-value project
    ```

Cloud Project ID が正常に設定されると、Agent Engine デプロイの準備が整います。

### ADK プロジェクトのデプロイ {#deploy-ad}

ASP を使用する場合、デプロイは段階的に実行されます。
最初の段階では `make` コマンドで Agent Engine 上で ADK ワークフローを実行するための必要サービスを
プロビジョニングします。次の段階で ASP はプロジェクトコードを Agent Engine サービスにアップロードし、
ホステッド環境で実行します。

!!! warning "重要"
    これらの手順を実行する前に、Google Cloud の対象デプロイプロジェクトが
    **現在のプロジェクト**として設定されていることを確認してください。
    `make backend` は現在設定されている Google Cloud プロジェクトを使ってデプロイを実行します。
    現在のプロジェクト設定方法は
    [Google Cloud プロジェクトへの接続](#connect-ad)を参照してください。

Google Cloud プロジェクトに ADK プロジェクトをデプロイするには:

1.  ターミナルで、エージェントフォルダを含む親ディレクトリ（例: `your-project-directory/`）にいることを確認します。

1.  次の ASP の make コマンドで、更新済みのローカルプロジェクトコードを Google Cloud 開発環境にデプロイします。

    ```shell
    make backend
    ```

この処理が正常に完了すると、Google Cloud Agent Engine で実行中のエージェントと対話できるようになります。
デプロイ済みエージェントのテスト方法は
[デプロイ済みエージェントのテスト](/adk-docs/deploy/agent-engine/test/)
を参照してください。

### ADK プロジェクトの変更内容 {#adk-asp-changes}

ASP ツールはデプロイのためにプロジェクトに追加ファイルを追加します。以下の手順は、既存のプロジェクトを変更する前にバックアップを作成します。

参考の元プロジェクトは
[multi_tool_agent](https://github.com/google/adk-docs/tree/main/examples/python/snippets/get-started/multi_tool_agent)
で、開始時の構成は次の通りです。

```
multi_tool_agent/
├─ __init__.py
├─ agent.py
└─ .env
```

ASP enhance コマンドで Agent Engine デプロイ情報を追加すると、新しい構成は次のようになります。

```
multi-tool-agent/
├─ app/                 # コアアプリケーションコード
│   ├─ agent.py         # メインエージェントロジック
│   ├─ agent_engine_app.py # Agent Engine アプリケーションロジック
│   └─ utils/           # ユーティリティ関数とヘルパー
├─ .cloudbuild/         # Google Cloud Build 用 CI/CD 設定
├─ deployment/          # インフラとデプロイスクリプト
├─ notebooks/           # プロトタイピングと評価用 Jupyter ノートブック
├─ tests/               # 単体・統合・負荷テスト
├─ Makefile             # Makefile
├─ GEMINI.md            # AI 補助開発ガイド
└─ pyproject.toml       # プロジェクト依存関係と設定
```

更新後の ADK プロジェクトフォルダ内の `README.md` で詳細情報を確認してください。
ASP の利用詳細は
[開発ガイド](https://googlecloudplatform.github.io/agent-starter-pack/guide/development-guide.html)
を参照してください。

## デプロイ済みエージェントのテスト

ADK エージェントをデプロイした後、新しいホステッド環境でワークフローをテストする必要があります。 Agent Engine にデプロイされた
ADK エージェントのテスト方法については
[Agent Engine でデプロイされたエージェントをテストする](/adk-docs/deploy/agent-engine/test/)
をご参照ください。
