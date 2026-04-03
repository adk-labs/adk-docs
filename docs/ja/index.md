---
hide:
  - navigation
  - toc
---

<div style="text-align: center;">
  <div class="centered-logo-text-group">
    <img src="assets/agent-development-kit.png" alt="Agent Development Kit Logo" width="100">
    <h1>Agent Development Kit</h1>
  </div>
</div>

Agent Development Kit (ADK) は、**AIエージェントの開発とデプロイ**のための、柔軟でモジュール化されたフレームワークです。GeminiやGoogleエコシステム向けに最適化されていますが、ADKは**モデル非依存**かつ**デプロイ環境非依存**であり、**他のフレームワークとの互換性**も考慮して構築されています。ADKは、エージェント開発をよりソフトウェア開発に近い感覚で行えるように設計されており、開発者が単純なタスクから複雑なワークフローに及ぶエージェントアーキテクチャを容易に作成、デプロイ、オーケストレーションできるようにします。

??? tip "お知らせ: ADK Go 1.0.0 をリリース!"

    ADK Go 1.0.0 リリースでは、OpenTelemetry 統合、プラグインによる
    自己修復ロジック、改善されたヒューマンインプット対応など、
    いくつかの主要機能が追加されました。詳しくは
    [ADK Go v1.0 の発表](https://developers.googleblog.com/adk-go-10-arrives/)
    を参照してください。

??? tip "お知らせ: ADK Java 1.0.0 をリリース!"

    ADK Java 1.0.0 が利用可能になりました。このリリースには複数の
    バグ修正と機能改善が含まれています。詳細は
    [ブログでの発表](https://developers.googleblog.com/announcing-adk-for-java-100-building-the-future-of-ai-agents-in-java/)
    をご覧ください。これらの改善を活用し、アプリケーションの最適な
    パフォーマンスを確保するために ADK Java 1.0.0 へアップグレードしてください。

<div id="centered-install-tabs" class="install-command-container" markdown="1">

<p class="get-started-text" style="text-align: center;">使用を開始:</p>

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

=== "TypeScript"
    <br>
    <p style="text-align: center;">
    <code>npm install @google/adk</code>
    </p>

=== "Java"

    ```xml title="pom.xml"
    <dependency>
        <groupId>com.google.adk</groupId>
        <artifactId>google-adk</artifactId>
        <version>1.0.0</version>
    </dependency>
    ```

    ```gradle title="build.gradle"
    dependencies {
        implementation 'com.google.adk:google-adk:1.0.0'
    }
    ```

</div>

<p style="text-align:center;">
  <a href="/get-started/python/" class="md-button" style="margin:3px">Pythonで始める</a>
  <a href="/get-started/typescript/" class="md-button" style="margin:3px">TypeScriptで始める</a>
  <a href="/get-started/go/" class="md-button" style="margin:3px">Goで始める</a>
  <a href="/get-started/java/" class="md-button" style="margin:3px">Javaで始める</a>
</p>

---

## さらに詳しく

[:fontawesome-brands-youtube:{.youtube-red-icon} 「Introducing Agent Development Kit」を視聴する！](https://www.youtube.com/watch?v=zgrOwow_uTQ){:target="_blank" rel="noopener noreferrer"}

<div class="grid cards" markdown>

-   :material-transit-connection-variant: **柔軟なオーケストレーション**

    ---

    予測可能なパイプラインのためにワークフローエージェント（`Sequential`、`Parallel`、`Loop`）を使用してワークフローを定義したり、適応的な動作のためにLLM駆動の動的ルーティング（`LlmAgent` transfer）を活用したりできます。

    [**エージェントについて学ぶ**](agents/index.md)

-   :material-graph: **マルチエージェント・アーキテクチャ**

    ---

    複数の専門的なエージェントを階層的に構成することで、モジュール式でスケーラブルなアプリケーションを構築します。複雑な調整や委任が可能になります。

    [**マルチエージェントシステムを探求**](agents/multi-agents.md)

-   :material-toolbox-outline: **豊富なツールエコシステム**

    ---

    エージェントに多様な機能を装備させましょう。事前構築されたツール（検索、コード実行）の使用、カスタム関数の作成、サードパーティライブラリの統合、さらには他のエージェントをツールとして使用することも可能です。

    [**ツールとインテグレーションを見る**](integrations/index.md)

-   :material-rocket-launch-outline: **デプロイ対応**

    ---

    エージェントをコンテナ化して、どこにでもデプロイできます。ローカルでの実行、Vertex AI Agent Engineでのスケーリング、またはCloud RunやDockerを使用したカスタムインフラストラクチャへの統合が可能です。

    [**エージェントをデプロイ**](deploy/index.md)

-   :material-clipboard-check-outline: **組み込みの評価機能**

    ---

    最終的な回答の品質と、ステップごとの実行軌跡（trajectory）の両方を、事前に定義されたテストケースと照らし合わせて、エージェントのパフォーマンスを体系的に評価します。

    [**エージェントを評価**](evaluate/index.md)

-   :material-console-line: **安心かつ安全なエージェントの構築**

    ---

    セキュリティおよび安全性のパターンとベストプラクティスをエージェントの設計に実装することで、強力で信頼できるエージェントを構築する方法を学びます。

    [**安全性とセキュリティ**](safety/index.md)

</div>
