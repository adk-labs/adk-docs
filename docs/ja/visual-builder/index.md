# エージェント向け Visual Builder

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.18.0</span><span class="lst-preview">実験的機能</span>
</div>

ADK Visual Builderは、ADKエージェントを作成および管理するための視覚的なワークフロー設計環境を提供するWebベースのツールです。これを使用すると、初心者向けのグラフィカルインターフェースでエージェントを設計、構築、テストでき、エージェントの構築を支援するAI搭載アシスタントも含まれています。

![Visual Agent Builder](../assets/visual-builder.png)

!!! example "実験的機能 (Experimental)"
    Visual Builder機能は実験的なリリースです。[フィードバック](https://github.com/google/adk-python/issues/new?template=feature_request.md)をお待ちしています！

## 始める (Get started)

Visual Builderインターフェースは、ADK Webツールユーザーインターフェースの一部です。ADKライブラリが[インストール](/adk-docs/ja/get-started/installation/#python)されていることを確認し、ADK Webユーザーインターフェースを実行してください。

```console
adk web --port 8000
```

??? tip "ヒント：コード開発ディレクトリから実行してください"

    Visual Builderツールは、ADK Webツールを実行したディレクトリ内の新しいサブディレクトリにプロジェクトファイルを書き込みます。書き込み権限のある開発者ディレクトリの場所からこのコマンドを実行してください。

![Visual Agent Builder start](../assets/visual-builder-start.png)
**図 1:** Visual Builderツールを開始するためのADK Webコントロール。

Visual Builderでエージェントを作成するには：

1.  *図 1*に示すように、ページの左上にある **+** （プラス記号）を選択して、エージェントの作成を開始します。
1.  エージェントアプリケーションの名前を入力し、**Create（作成）**を選択します。
1.  以下のいずれかを実行してエージェントを編集します：
    *   左側のパネルで、エージェントコンポーネントの値を編集します。
    *   中央のパネルで、新しいエージェントコンポーネントを追加します。
    *   右側のパネルで、プロンプトを使用してエージェントを変更したり、ヘルプを取得したりします。
1.  左下隅にある **Save（保存）**を選択して、エージェントを保存します。
1.  新しいエージェントと対話してテストします。
1.  *図 1*に示すように、ページの左上にある鉛筆アイコンを選択して、エージェントの編集を続けます。

Visual Builderを使用する際の注意点は以下の通りです：

*   **エージェントの作成と保存：** エージェントを作成するときは、編集インターフェースを終了する前に必ず **Save（保存）**を選択してください。そうしないと、新しいエージェントが編集できなくなる可能性があります。
*   **エージェントの編集：** エージェントの編集（鉛筆アイコン）は、Visual Builderで作成されたエージェントに対して*のみ*利用可能です。
*   **ツールの追加：** 既存のカスタムツール（Custom Tools）をVisual Builderエージェントに追加する場合は、完全修飾Python関数名を指定してください。

## ワークフローコンポーネントのサポート (Workflow component support)

Visual Builderツールは、エージェントを構築するためのドラッグアンドドロップユーザーインターフェースに加えて、質問に答えたりエージェントワークフローを編集したりできるAI搭載の開発アシスタントを提供します。このツールは、以下を含むADKエージェントワークフローの構築に必要なすべての主要コンポーネントをサポートしています：

*   **エージェント (Agents)**
    *   **ルートエージェント (Root Agent)**: ワークフローの主要な制御エージェントです。ADKエージェントワークフロー内の他のすべてのエージェントは、サブエージェントと見なされます。
    *   [**LLMエージェント:**](/adk-docs/ja/agents/llm-agents/) 生成AIモデルによって駆動されるエージェントです。
    *   [**シーケンシャルエージェント (Sequential Agent):**](/adk-docs/ja/agents/workflow-agents/sequential-agents/) 一連のサブエージェントを順番に実行するワークフローエージェントです。
    *   [**ループエージェント (Loop Agent):**](/adk-docs/ja/agents/workflow-agents/loop-agents/) 特定の条件が満たされるまでサブエージェントを繰り返し実行するワークフローエージェントです。
    *   [**パラレルエージェント (Parallel Agent):**](/adk-docs/ja/agents/workflow-agents/parallel-agents/) 複数のサブエージェントを並行して実行するワークフローエージェントです。
*   **ツール (Tools)**
    *   [**事前構築済みツール (Prebuilt tools):**](/adk-docs/ja/tools/built-in-tools/) ADKが提供する限られたツールセットをエージェントに追加できます。
    *   [**カスタムツール (Custom tools):**](/adk-docs/ja/tools-custom/) カスタムツールを独自に構築してワークフローに追加できます。
*   **コンポーネント (Components)**
    *   [**コールバック (Callbacks)**](/adk-docs/ja/callbacks/) エージェントワークフローイベントの開始時と終了時にエージェントの動作を変更できるフロー制御コンポーネントです。

一部の高度なADK機能は、Agent Config（エージェント設定）機能の制限により、Visual Builderではサポートされていません。詳細については、Agent Configの[既知の制限事項](/adk-docs/ja/agents/config/#known-limitations)を参照してください。

## プロジェクトコードの出力 (Project code output)

Visual Builderツールは、[Agent Config](/adk-docs/ja/agents/config/)形式を使用してコードを生成します。エージェントには `.yaml` 設定ファイルを使用し、カスタムツールにはPythonコードを使用します。これらのファイルは、ADK Webインターフェースを実行したディレクトリのサブフォルダに生成されます。以下のリストは、`DiceAgent` プロジェクトのレイアウト例を示しています：

```none
DiceAgent/
    root_agent.yaml    # メインエージェントコード
    sub_agent_1.yaml   # サブエージェント (存在する場合)
    tools/             # ツールディレクトリ
        __init__.py
        dice_tool.py   # ツールコード
```

!!! note "生成されたエージェントの編集"

    開発環境で生成されたファイルを編集できます。ただし、一部の変更はVisual Builderと互換性がない場合があります。

## 次のステップ (Next steps)

Visual Builder開発アシスタントを使用して、以下のプロンプトで新しいエージェントを構築してみてください：

```none
Help me add a dice roll tool to my current agent.
Use the default model if you need to configure that.
```

（現在のエージェントにサイコロ振りツールを追加するのを手伝って。構成が必要な場合はデフォルトのモデルを使って。）

Visual Builderで使用されるAgent Configコード形式と利用可能なオプションに関する詳細情報を確認してください：

*   [Agent Config (エージェント設定)](/adk-docs/ja/agents/config/)
*   [Agent Config YAMLスキーマ](/adk-docs/ja/api-reference/agentconfig/)