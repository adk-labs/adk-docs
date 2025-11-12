---
hide:
  - toc
---

<div style="text-align: center;">
  <div class="centered-logo-text-group">
    <img src="assets/agent-development-kit.png" alt="エージェント開発キットのロゴ" width="100">
    <h1>エージェント開発キット</h1>
  </div>
</div>

エージェント開発キット（ADK）は、**AIエージェントを開発・デプロイ**するための、柔軟でモジュール式のフレームワークです。ADKはGeminiとGoogleエコシステムに最適化されていますが、**特定のモデルやデプロイ環境に依存せず**、**他のフレームワークとの互換性**も考慮して構築されています。ADKは、エージェント開発をソフトウェア開発のように感じられるように設計されており、開発者が単純なタスクから複雑なワークフローまで、さまざまなエージェントアーキテクチャを容易に作成、デプロイ、オーケストレーションできるようにします。

<div id="centered-install-tabs" class="install-command-container" markdown="1">

<p class="get-started-text" style="text-align: center;">はじめに:</p>

=== "Python"
    <br>
    <p style="text-align: center;">
    <code>pip install google-adk</code>
    </p>

=== "Go"
    <br>
    <p style="text-align: center;">
    <code>go get google.golang.org/adk</code>
    </p>

=== "Java"

    ```xml title="pom.xml"
    <dependency>
        <groupId>com.google.adk</groupId>
        <artifactId>google-adk</artifactId>
        <version>0.3.0</version>
    </dependency>
    ```

    ```gradle title="build.gradle"
    dependencies {
        implementation 'com.google.adk:google-adk:0.3.0'
    }
    ```

</div>

<p style="text-align:center;">
  <a href="/adk-docs/get-started/python/" class="md-button" style="margin:3px">Pythonではじめる</a>
  <a href="/adk-docs/get-started/go/" class="md-button" style="margin:3px">Goではじめる</a>
  <a href="/adk-docs/get-started/java/" class="md-button" style="margin:3px">Javaではじめる</a>
</p>

---

## さらに詳しく

[:fontawesome-brands-youtube:{.youtube-red-icon} 「エージェント開発キットの紹介」動画を見る！](https://www.youtube.com/watch?v=zgrOwow_uTQ){:target="_blank" rel="noopener noreferrer"}

<div class="grid cards" markdown>

-   :material-transit-connection-variant: **柔軟なオーケストレーション**

    ---

    ワークフローエージェント（`Sequential`、`Parallel`、`Loop`）を使用して予測可能なパイプラインを定義したり、LLM駆動の動的ルーティング（`LlmAgent`転送）を活用して適応的な動作を実現したりできます。

    [**エージェントについて学ぶ**](agents/index.md)

-   :material-graph: **マルチエージェントアーキテクチャ**

    ---

    複数の専門エージェントを階層的に構成することで、モジュール式でスケーラブルなアプリケーションを構築します。複雑な連携や委任を可能にします。

    [**マルチエージェントシステムを探る**](agents/multi-agents.md)

-   :material-toolbox-outline: **豊富なツールエコシステム**

    ---

    エージェントに多様な機能を持たせましょう。構築済みツール（検索、コード実行）の使用、カスタム関数の作成、サードパーティライブラリの統合、さらには他のエージェントをツールとして使用することも可能です。

    [**ツール一覧を見る**](tools/index.md)

-   :material-rocket-launch-outline: **デプロイ対応**

    ---

    エージェントをコンテナ化してどこにでもデプロイできます。ローカルでの実行、Vertex AIエージェントエンジンによるスケーリング、Cloud RunやDockerを使用したカスタムインフラへの統合が可能です。

    [**エージェントのデプロイ**](deploy/index.md)

-   :material-clipboard-check-outline: **組み込みの評価機能**

    ---

    事前に定義されたテストケースに対して、最終的な応答品質とステップごとの実行軌跡の両方を評価し、エージェントのパフォーマンスを体系的に評価します。

    [**エージェントの評価**](evaluate/index.md)

-   :material-console-line: **安全でセキュアなエージェントの構築**

    ---

    エージェントの設計にセキュリティと安全性のパターンやベストプラクティスを実装し、強力で信頼性の高いエージェントを構築する方法を学びます。

    [**安全性とセキュリティ**](safety/index.md)

</div>