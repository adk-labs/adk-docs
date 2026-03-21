# ランタイム

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

ADK は、開発中のエージェントを実行およびテストするためのいくつかの方法を
提供します。開発ワークフローに最も合う方法を選んでください。

## エージェントを実行する方法

<div class="grid cards" markdown>

-   :material-web:{ .lg .middle } **Dev UI**

    ---

    `adk web` を使って、エージェントと対話するためのブラウザベース UI を
    起動します。

    [:octicons-arrow-right-24: Web インターフェースを使用する](web-interface.md)

-   :material-console:{ .lg .middle } **Command Line**

    ---

    `adk run` を使って、ターミナルから直接エージェントと対話します。

    [:octicons-arrow-right-24: コマンドラインを使用する](command-line.md)

-   :material-api:{ .lg .middle } **API Server**

    ---

    `adk api_server` を使って、エージェントを RESTful API として公開します。

    [:octicons-arrow-right-24: API サーバーを使用する](api-server.md)

</div>

## 技術リファレンス

ランタイムの設定や動作についてより詳細な情報が必要な場合は、次のページを
参照してください。

- **[Event Loop](event-loop.md)**: yield / pause / resume のサイクルを含む、
  ADK を動かすコアのイベントループを理解します。
- **[Resume Agents](resume.md)**: 以前の状態からエージェント実行を再開する
  方法を学びます。
- **[Runtime Config](runconfig.md)**: RunConfig を使ってランタイム動作を設定
  します。
