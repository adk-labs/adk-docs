---
catalog_title: AgentOps
catalog_description: Session replays, metrics, and monitoring for ADK agents
catalog_icon: /adk-docs/integrations/assets/agentops.png
catalog_tags: ["observability"]
---
# AgentOpsによるエージェントの可観測性

**わずか2行のコード**で、[AgentOps](https://www.agentops.ai)はエージェントのセッションリプレイ、メトリクス、モニタリングを提供します。

## ADKにAgentOpsを選ぶ理由

可観測性は、対話型AIエージェントを開発・展開する上で重要な側面です。これにより、開発者はエージェントのパフォーマンス、ユーザーとの対話方法、外部ツールやAPIの使用方法を理解できます。

AgentOpsを統合することで、開発者はADKエージェントの動作、LLMとの対話、ツール使用に関する深い洞察を得ることができます。

Google ADKには独自のOpenTelemetryベースのトレースシステムが含まれており、これは主に開発者にエージェント内の基本的な実行フローをトレースする方法を提供することを目的としています。AgentOpsは、以下を備えた専用のより包括的な可観測性プラットフォームを提供することで、これを強化します。

*   **統一されたトレースとリプレイ分析:** ADKやAIスタックの他のコンポーネントからのトレースを統合します。
*   **豊富な視覚化:** エージェントの実行フロー、LLM呼び出し、ツールパフォーマンスを視覚化する直感的なダッシュボード。
*   **詳細なデバッグ:** 特定のスパンにドリルダウンし、プロンプト、補完、トークン数、エラーを表示します。
*   **LLMのコストとレイテンシの追跡:** レイテンシ、コスト（トークン使用量経由）を追跡し、ボトルネックを特定します。
*   **簡素化されたセットアップ:** わずか数行のコードで開始できます。

![AgentOpsエージェント可観測性ダッシュボード](https://raw.githubusercontent.com/AgentOps-AI/agentops/refs/heads/main/docs/images/external/app_screenshots/overview.png)

![ネストされたエージェント、LLM、ツールスパンを含むADKトレースを示すAgentOpsダッシュボード。](../assets/agentops-adk-trace-example.jpg)

*複数ステップのADKアプリケーション実行からのトレースを表示するAgentOpsダッシュボード。メインエージェントのワークフロー、個々のサブエージェント、LLM呼び出し、ツール実行など、スパンの階層構造を確認できます。明確な階層に注目してください。メインワークフローエージェントスパンには、さまざまなサブエージェント操作、LLM呼び出し、ツール実行の子スパンが含まれています。*

## AgentOpsとADKの始め方

AgentOpsをADKアプリケーションに統合するのは簡単です。

1.  **AgentOpsのインストール:**
    ```bash
    pip install -U agentops
    ```

2. **APIキーの作成**
    ここでユーザーAPIキーを作成します：[APIキーの作成](https://app.agentops.ai/settings/projects) そして、環境を設定します：

    環境変数にAPIキーを追加します：
    ```
    AGENTOPS_API_KEY=<YOUR_AGENTOPS_API_KEY>
    ```

3.  **AgentOpsの初期化:**
    ADKアプリケーションスクリプト（例：ADK `Runner`を実行するメインのPythonファイル）の冒頭に次の行を追加します。

    ```python
    import agentops
    agentops.init()
    ```

    これにより、AgentOpsセッションが開始され、ADKエージェントが自動的に追跡されます。

    詳細な例：

    ```python
    import agentops
    import os
    from dotenv import load_dotenv

    # 環境変数の読み込み（オプション、APIキーに.envファイルを使用する場合）
    load_dotenv()

    agentops.init(
        api_key=os.getenv("AGENTOPS_API_KEY"), # AgentOps APIキー
        trace_name="my-adk-app-trace"  # オプション：トレースの名前
        # auto_start_session=Trueがデフォルトです。
        # セッションの開始/終了を手動で制御したい場合はFalseに設定します。
    )
    ```

    > 🚨 🔑 AgentOps APIキーは、サインアップ後に[AgentOpsダッシュボード](https://app.agentops.ai/)で確認できます。環境変数（`AGENTOPS_API_KEY`）として設定することをお勧めします。

初期化されると、AgentOpsはADKエージェントの計測を自動的に開始します。

**ADKエージェントのすべてのテレメトリデータをキャプチャするために必要なのはこれだけです**

## AgentOpsがADKを計測する方法

AgentOpsは、ADKのネイティブテレメトリと競合することなくシームレスな可観測性を提供するために、洗練された戦略を採用しています。

1.  **ADKのネイティブテレメトリの無効化:**
    AgentOpsはADKを検出し、ADKの内部OpenTelemetryトレーサー（通常は`trace.get_tracer('gcp.vertex.agent')`）をインテリジェントにパッチします。これを`NoOpTracer`に置き換えることで、テレメトリスパンを作成しようとするADK自身の試みを効果的に無効にします。これにより、重複したトレースが防止され、AgentOpsが可観測性データの信頼できるソースになります。

2.  **AgentOps制御のスパン作成:**
    AgentOpsは、主要なADKメソッドをラップしてスパンの論理的な階層を作成することで制御します。

    *   **エージェント実行スパン（例：`adk.agent.MySequentialAgent`）:**
        ADKエージェント（`BaseAgent`、`SequentialAgent`、`LlmAgent`など）が`run_async`メソッドを開始すると、AgentOpsはそのエージェントの実行の親スパンを開始します。

    *   **LLM対話スパン（例：`adk.llm.gemini-pro`）:**
        エージェントがLLMを呼び出す場合（ADKの`BaseLlmFlow._call_llm_async`経由）、AgentOpsは通常LLMモデルにちなんで名付けられた専用の子スパンを作成します。このスパンはリクエストの詳細（プロンプト、モデルパラメータ）をキャプチャし、完了時（ADKの`_finalize_model_response_event`経由）に応答の詳細（補完、トークン使用量、終了理由など）を記録します。

    *   **ツール使用スパン（例：`adk.tool.MyCustomTool`）:**
        エージェントがツールを使用する場合（ADKの`functions.__call_tool_async`経由）、AgentOpsはツールにちなんで名付けられた単一の包括的な子スパンを作成します。このスパンには、ツールの入力パラメータと返される結果が含まれます。

3.  **豊富な属性収集:**
    AgentOpsはADKの内部データ抽出ロジックを再利用します。ADKの特定のテレメトリ関数（例：`google.adk.telemetry.trace_tool_call`、`trace_call_llm`）をパッチします。これらの関数のAgentOpsラッパーは、ADKが収集した詳細情報を取得し、*現在アクティブなAgentOpsスパン*に属性としてアタッチします。

## AgentOpsでのADKエージェントの視覚化

ADKアプリケーションをAgentOpsで計測すると、AgentOpsダッシュボードでエージェントの実行を明確で階層的なビューで確認できます。

1.  **初期化:**
    `agentops.init()`が呼び出されると（例：`agentops.init(trace_name="my_adk_application")`）、initパラメータ`auto_start_session=True`（デフォルトでtrue）の場合、初期の親スパンが作成されます。このスパンは、多くの場合`my_adk_application.session`のような名前になり、そのトレース内のすべての操作のルートになります。

2.  **ADK Runnerの実行:**
    ADK `Runner`がトップレベルのエージェント（例：ワークフローをオーケストレーションする`SequentialAgent`）を実行すると、AgentOpsはセッショントレースの下に対応するエージェントスパンを作成します。このスパンは、トップレベルのADKエージェントの名前（例：`adk.agent.YourMainWorkflowAgent`）を反映します。

3.  **サブエージェントとLLM/ツール呼び出し:**
    このメインエージェントが、サブエージェント、LLM、またはツールの呼び出しを含むロジックを実行すると、次のようになります。
    *   各**サブエージェントの実行**は、その親エージェントの下にネストされた子スパンとして表示されます。
    *   **大規模言語モデル**への呼び出しは、さらにネストされた子スパン（例：`adk.llm.<model_name>`）を生成し、プロンプトの詳細、応答、トークン使用量をキャプチャします。
    *   **ツールの呼び出し**も、個別の-子スパン（例：`adk.tool.<your_tool_name>`）を生成し、そのパラメータと結果を表示します。

これにより、スパンのウォーターフォールが作成され、ADKアプリケーションの各ステップの順序、期間、詳細を確認できます。LLMのプロンプト、補完、トークン数、ツールの入出力、エージェント名など、関連するすべての属性がキャプチャされて表示されます。

実践的なデモンストレーションとして、Google ADKとAgentOpsを使用した人間による承認ワークフローを示すサンプルJupyter Notebookを調べることができます。
[GitHubのGoogle ADK人間承認の例](https://github.com/AgentOps-AI/agentops/blob/main/examples/google_adk/human_approval.ipynb)。

この例は、ツール使用を伴う複数ステップのエージェントプロセスがAgentOpsでどのように視覚化されるかを示しています。

## 利点

*   **簡単なセットアップ:** 包括的なADKトレースのための最小限のコード変更。
*   **深い可視性:** 複雑なADKエージェントフローの内部動作を理解します。
*   **迅速なデバッグ:** 詳細なトレースデータで問題を迅速に特定します。
*   **パフォーマンスの最適化:** レイテンシとトークン使用量を分析します。

AgentOpsを統合することで、ADK開発者は堅牢なAIエージェントを構築、デバッグ、保守する能力を大幅に向上させることができます。

## 詳細情報

始めるには、[AgentOpsアカウントを作成](http://app.agentops.ai)してください。機能リクエストやバグレポートについては、[AgentOpsリポジトリ](https://github.com/AgentOps-AI/agentops)でAgentOpsチームにお問い合わせください。

### 外部リンク
🐦 [Twitter](http://x.com/agentopsai) • 📢 [Discord](http://x.com/agentopsai) • 🖇️ [AgentOpsダッシュボード](http://app.agentops.ai) • 📙 [ドキュメント](http.docs.agentops.ai)
