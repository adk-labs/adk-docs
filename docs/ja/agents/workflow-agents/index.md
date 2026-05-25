# テンプレート エージェント ワークフロー

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">Typescript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

このセクションでは、1 つ以上のサブエージェントの実行フローを制御する特殊なエージェントである *テンプレート ワークフロー*、別名 *ワークフロー エージェント* を紹介します。テンプレート ワークフロー エージェントは、サブエージェントの実行フローをオーケストレーションするために設計された特殊なコンポーネントです。主な役割は、他のエージェントがどのように、いつ実行されるかを管理し、プロセスの制御フローを定義することです。

!!! note "代替: グラフベース ワークフロー"

    ADK 2.0 以降、テンプレート ワークフローは、

    [グラフベース ワークフロー](/ja/graphs/) や
    [動的ワークフロー](/ja/graphs/dynamic/) など、より柔軟なワークフロー構造に置き換えられました。
    これらのワークフロー アーキテクチャは、エージェント ワークフローを時間とともに進化させるための
    より高い制御性、柔軟性、機能を提供します。

<img src="../../../assets/template_workflows.svg" alt="ADK のテンプレート エージェント ワークフロー">

**図 1.** ADK におけるテンプレート ワークフローの実行パターン

テンプレート ワークフロー エージェントは、事前定義されたロジックに基づいて動作します。オーケストレーションのために AI モデルに問い合わせることなく、シーケンシャル、パラレル、ループなどのタイプに応じて実行順序を決定します。このアプローチにより、決定的で予測可能な実行パターンが得られます。テンプレート ワークフローには、次のタスク実行構造が含まれており、それぞれが異なるタスク完了パターンを実装します。

<div class="grid cards" markdown>

- :material-console-line: **シーケンシャル エージェント ワークフロー**

    ---

    サブエージェントを 1 つずつ順番に実行します。

    [:octicons-arrow-right-24: 詳細はこちら](sequential-agents.md)

- :material-console-line: **ループ エージェント ワークフロー**

    ---

    特定の終了条件が満たされるまで、サブエージェントを繰り返し実行します。

    [:octicons-arrow-right-24: 詳細はこちら](loop-agents.md)

- :material-console-line: **パラレル エージェント ワークフロー**

    ---

    複数のサブエージェントを並列に実行します。

    [:octicons-arrow-right-24: 詳細はこちら](parallel-agents.md)

</div>
