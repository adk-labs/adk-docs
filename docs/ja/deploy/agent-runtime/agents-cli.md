# エージェント CLI を使用してエージェント ランタイムにデプロイする

<div class="language-support-tag" title="Agent Runtime currently supports only Python.">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

この展開手順では、次を使用して展開を実行する方法について説明します。
[Agents CLI in Agent Platform](https://google.github.io/agents-cli/)
そしてADK。 Agents CLI を介してエージェント ランタイムにデプロイすると、運用環境への高速パスが提供されます。エージェント CLI は、開発ライフサイクル全体をサポートするために、Google Cloud リソース、CI/CD パイプライン、Infrafraction-as-Code（Terraform）を自動的に構成します。ベスト プラクティスとして、運用展開の前に、生成された構成を必ず確認して、組織のセキュリティおよびコンプライアンスの標準に合わせてください。

この導入ガイドでは、エージェント CLI を使用して、プロジェクト テンプレートを
既存のプロジェクトに展開アーティファクトを追加し、エージェント プロジェクトを準備します。
展開。これらの手順では、エージェント CLI を使用して Google をプロビジョニングする方法を示します。
ADK プロジェクトのデプロイに必要なサービスを含むクラウド プロジェクト。次のとおりです。

- [Prerequisites](#prerequisites-ad): Google Cloud のセットアップ
    プロジェクト、IAM 権限を取得し、必要なソフトウェアをインストールします。
- [Prepare your ADK project](#prepare-ad): を変更してください
    既存の ADK プロジェクト ファイルを使用して、デプロイメントの準備を整えます。
- [Connect to your Google Cloud project](#connect-ad):
    開発環境を Google Cloud と Google Cloud に接続する
    プロジェクト。
- [Deploy your ADK project](#deploy-ad): プロビジョニング
    Google Cloud プロジェクトに必要なサービスを追加し、ADK プロジェクト コードをアップロードします。

デプロイされたエージェントのテストについては、「[Test deployed agent](test.md)」を参照してください。
Agents CLI とそのコマンド ライン ツールの使用方法の詳細については、次の URL を参照してください。
を見てください
[CLI reference](https://google.github.io/agents-cli/cli/)
そして
[Guide](https://google.github.io/agents-cli/)。

### 前提条件 {#prerequisites-ad}

このデプロイメント・パスを使用するには、次のリソースが構成されている必要があります。

- **Google Cloud プロジェクトと権限**: [billing enabled](https://cloud.google.com/billing/docs/how-to/modify-project) の Google Cloud プロジェクト。
    既存のプロジェクトを使用することも、新しいプロジェクトを作成することもできます。このプロジェクト内で次の IAM ロールのいずれかが割り当てられている必要があります。
    - **エージェント プラットフォーム ユーザー ロール** - エージェントをエージェント ランタイムに展開するのに十分です。
    - **オーナー ロール** - 完全な実稼働セットアップ (Terraform インフラストラクチャ プロビジョニング、CI/CD パイプライン、IAM 構成) に必要です。

!!! tip "注記"
    既存のリソースとの競合を避けるために、空のプロジェクトをお勧めします。
    新しいプロジェクトについては、[Creating and managing projects](https://cloud.google.com/resource-manager/docs/creating-managing-projects) を参照してください。

- **Python 環境**: でサポートされている Python バージョン
    [Agents CLI](https://google.github.io/agents-cli/guide/getting-started/)。
- **uv ツール:** Python 開発環境と実行中のエージェント cli を管理します。
    ツール。インストールの詳細については、を参照してください。
    [Install uv](https://docs.astral.sh/uv/getting-started/installation/)。
- **Google Cloud CLI ツール**: gcloud コマンドライン インターフェース。のために
    インストールの詳細については、を参照してください。
    [Google Cloud Command Line Interface](https://cloud.google.com/sdk/docs/install)。
- **ツールの作成**: ビルド自動化ツール。このツールはほとんどのツールの一部です
    Unix ベースのシステムの場合、インストールの詳細については、
    [Make tool](https://www.gnu.org/software/make/) のドキュメント。

### ADK プロジェクトを準備します {#prepare-ad}

ADK プロジェクトをエージェント ランタイムにデプロイする場合は、いくつかの追加ファイルが必要です
導入操作をサポートします。次のエージェント CLI コマンドは、
プロジェクトを作成し、展開目的でファイルをプロジェクトに追加します。

これらの手順は、変更する既存の ADK プロジェクトがあることを前提としています。
展開用に。 ADK プロジェクトがない場合、またはテストを使用したい場合
プロジェクト、[Get started](/get-started/) ガイドのいずれかを完了し、
これによりエージェント プロジェクトが作成されます。次の手順では、`my_agent` を使用します。
プロジェクトを例として挙げます。

ADK プロジェクトをエージェント ランタイムにデプロイするために準備するには:

1. 開発環境のターミナル ウィンドウで、
    エージェント フォルダーを含む **親ディレクトリ**。たとえば、あなたの場合、
    プロジェクトの構造は次のとおりです。

    ```
    your-project-directory/
    ├── my_agent/
    │   ├── __init__.py
    │   ├── agent.py
    │   └── .env
    ```

    `your-project-directory/` に移動します

1. エージェント CLI `scaffold enhance` コマンドを実行して、展開に必要なファイルを
    あなたのプロジェクト。

    ```shell
    agents-cli scaffold enhance --deployment-target agent_engine
    ```

1. エージェント CLI ツールの指示に従います。一般的には受け付けてもらえますが、
    すべての質問に対するデフォルトの回答。ただし、**GCP リージョン**の場合は、
    オプションの場合は、必ず次のいずれかを選択してください
    [supported regions](https://docs.cloud.google.com/agent-builder/locations#supported-regions-agent-engine)
    エージェント ランタイムの場合。

このプロセスが正常に完了すると、ツールに次のメッセージが表示されます。

```
> Success! Your agent project is ready.
```

!!! tip "注記"
    Agents CLI ツールは、Google Cloud に接続するためのリマインダーを表示する場合があります。
    実行中ですが、この段階ではその接続は *必要ありません*。

Agents CLI が ADK プロジェクトに加える変更の詳細については、を参照してください。
[Changes to your ADK project](#adk-agents-cli-changes)。

### Google Cloud プロジェクトに接続します {#connect-ad}

ADK プロジェクトをデプロイする前に、Google Cloud に接続する必要があります。
プロジェクト。 Google Cloud アカウントにログインした後、次のことを確認する必要があります。
デプロイメント ターゲット プロジェクトがアカウントから表示され、それが
現在のプロジェクトとして設定されています。

Google Cloud に接続してプロジェクトを一覧表示するには:

1. 開発環境のターミナル ウィンドウで、
    Google Cloud アカウント:

    ```shell
    gcloud auth application-default login
    ```

1. Google Cloud プロジェクト ID を使用してターゲット プロジェクトを設定します。

    ```shell
    gcloud config set project your-project-id-xxxxx
    ```

1. Google Cloud ターゲット プロジェクトが設定されていることを確認します。

    ```shell
    gcloud config get-value project
    ```

Google Cloud に正常に接続し、クラウド プロジェクトを設定したら
ID さん、ADK プロジェクト ファイルをエージェント ランタイムにデプロイする準備ができました。

### ADK プロジェクトをデプロイします {#deploy-ad}

エージェント CLI を使用する場合は、`agents-cli deploy` コマンドを使用してデプロイします。これ
コマンドはエージェント コードからコンテナを構築し、それをレジストリにプッシュし、
それをホスト環境のエージェント ランタイムにデプロイします。

!!! warning "重要"
    *Google Cloud ターゲット デプロイ プロジェクトが *** 現在のプロジェクトとして設定されていることを確認してください
    これらの手順*を実行する前に、プロジェクト***を実行してください。 `agents-cli deploy` コマンドは、
    現在設定されている Google Cloud プロジェクトがデプロイを実行するときに使用されます。のために
    現在のプロジェクトの設定と確認については、を参照してください。
    [Connect to your Google Cloud project](#connect-ad)。

ADK プロジェクトを Google Cloud プロジェクトのエージェント ランタイムにデプロイするには:

1. ターミナル ウィンドウで、エージェント プロジェクト ディレクトリに移動します (例:
    `your-project-directory/`)。

2. エージェント コードを Google Cloud 開発環境にデプロイします。

    ```shell
    agents-cli deploy
    ```

    このコマンドは、`pyproject.toml` から `deployment_target` を読み取り、デプロイします。
    構成されたターゲット（エージェント ランタイム、Cloud Run、または GKE）に接続します。

3. (オプション) プロンプト応答ロギングなどの可観測性機能を有効にするには、
    コンテンツ ログ、テレメトリ インフラストラクチャをプロビジョニングします。

    ```shell
    agents-cli infra single-project
    ```

    詳細については、「
    [Observability Guide](https://google.github.io/agents-cli/guide/observability/)。

このプロセスが正常に完了すると、と対話できるようになります。
Google Cloud エージェント ランタイム上で実行されるエージェント。テストの詳細については、
導入されたエージェント、を参照してください。
[Test deployed agent](/deploy/agent-runtime/test/)。

### ADK プロジェクトへの変更 {#adk-agents-cli-changes}

Agents CLI ツールは、展開用のプロジェクトにさらにファイルを追加します。手順
以下では、既存のプロジェクト ファイルを変更する前にバックアップします。このガイド
を使用します
[multi_tool_agent](https://github.com/google/adk-docs/tree/main/examples/python/snippets/get-started/multi_tool_agent)
参考例としてプロジェクトを作成します。元のプロジェクトには次のファイルがあります
開始する構造:

```
my_agent/
├─ __init__.py
├─ agent.py
└─ .env
```

エージェント CLI の scaffold 拡張コマンドを実行してエージェント ランタイム展開を追加した後
情報によると、新しい構造は次のとおりです。

```
my-agent/
├─ app/                 # Core application code
│   ├─ agent.py         # Main agent logic
│   ├─ agent_engine_app.py # Agent Runtime application logic
│   └─ utils/           # Utility functions and helpers
├─ .cloudbuild/         # CI/CD pipeline configurations for Google Cloud Build
├─ deployment/          # Infrastructure and deployment scripts
├─ notebooks/           # Jupyter notebooks for prototyping and evaluation
├─ tests/               # Unit, integration, and load tests
├─ Makefile             # Makefile for common commands
├─ GEMINI.md            # AI-assisted development guide
└─ pyproject.toml       # Project dependencies and configuration
```

詳細については、更新された ADK プロジェクト フォルダー内の *README.md* ファイルを参照してください。
エージェント CLI の使用の詳細については、「
[Agents CLI documentation](https://google.github.io/agents-cli/)。

## デプロイされたエージェントをテストする

ADK エージェントのデプロイメントが完了したら、ワークフローをテストする必要があります。
新しいホスト環境。 ADK エージェントのテストの詳細については、
エージェント ランタイムにデプロイされます。を参照してください。
[Test deployed agents in Agent Runtime](/deploy/agent-runtime/test/)。
