# ADKにおける双方向（Bidi）ストリーミング（ライブ）

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.5.0</span><span class="lst-preview">実験的機能</span>
</div>

ADKの双方向（Bidi）ストリーミング（ライブ）は、[Gemini Live API](https://ai.google.dev/gemini-api/docs/live)の低遅延な双方向音声・映像インタラクション機能をAIエージェントに追加します。

!!! example "実験的プレビューリリース"

    双方向（Bidi）ストリーミング機能は実験的なものです。

双方向ストリーミング、またはライブモードを使用すると、エンドユーザーに自然で人間らしい音声会話体験を提供できます。これには、ユーザーがエージェントの応答を音声コマンドで割り込む機能も含まれます。ストリーミング機能を備えたエージェントは、テキスト、音声、映像の入力を処理でき、テキストと音声の出力を提供できます。

<div class="video-grid">
  <div class="video-item">
    <div class="video-container">
      <iframe src="https://www.youtube-nocookie.com/embed/Tu7-voU7nnw?si=RKs7EWKjx0bL96i5" title="Shopper's Concierge" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
    </div>
  </div>

  <div class="video-item">
    <div class="video-container">
      <iframe src="https://www.youtube-nocookie.com/embed/LwHPYyw7u6U?si=xxIEhnKBapzQA6VV" title="Shopper's Concierge" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
    </div>
  </div>
</div>

!!! info

    これは、サーバーサイドストリーミングやトークンレベルストリーミングとは異なります。
    トークンレベルストリーミングは、言語モデルが応答を生成し、それを一度に1トークンずつユーザーに送り返す一方向のプロセスです。これにより「タイピング」のような効果が生まれ、即座に応答しているかのような印象を与え、回答の冒頭部分が表示されるまでの時間を短縮します。ユーザーが完全なプロンプトを送信し、モデルがそれを処理した後、モデルが応答を部分ごとに生成して送り返し始めます。このセクションは、双方向ストリーミング（ライブ）に関するものです。

<div class="grid cards" markdown>

-   :material-console-line: **クイックスタート（双方向ストリーミング）**

    ---

    このクイックスタートでは、簡単なエージェントを構築し、ADKのストリーミングを使用して、低遅延で双方向の音声・映像通信を実装します。

    - [クイックスタート（双方向ストリーミング）](../get-started/streaming/quickstart-streaming.md)

-   :material-console-line: **カスタムオーディオストリーミングアプリのサンプル**

    ---

    この記事では、ADK StreamingとFastAPIで構築されたカスタム非同期Webアプリのサーバーとクライアントのコードの概要を説明します。WebSocketsを介してリアルタイムで双方向の音声・テキスト通信を可能にします。

    - [カスタムオーディオストリーミングアプリのサンプル（WebSockets）](custom-streaming-ws.md)

-   :material-console-line: **双方向ストリーミング開発ガイドシリーズ**

    ---

    ADKを使用した双方向ストリーミング開発について、より深く掘り下げるための記事シリーズです。基本的な概念とユースケース、コアAPI、そしてエンドツーエンドのアプリケーション設計について学ぶことができます。

    - [双方向ストリーミング開発ガイドシリーズ：パート1 - 導入](dev-guide/part1.md)

-   :material-console-line: **ストリーミングツール**

    ---

    ストリーミングツールを使用すると、ツール（関数）が中間結果をエージェントにストリーミングで返し、エージェントはそれらの中間結果に応答することができます。例えば、ストリーミングツールを使って株価の変動を監視し、エージェントにそれに反応させることができます。別の例として、エージェントにビデオストリームを監視させ、ストリームに変化があった場合にエージェントがその変化を報告するようにすることもできます。

    - [ストリーミングツール](streaming-tools.md)

-   :material-console-line: **カスタムオーディオストリーミングアプリのサンプル**

    ---

    この記事では、ADK StreamingとFastAPIで構築されたカスタム非同期Webアプリのサーバーとクライアントのコードの概要を説明します。Server Sent Events (SSE) と WebSocketsの両方を使用して、リアルタイムで双方向の音声・テキスト通信を可能にします。

    - [ストリーミング設定](configuration.md)

-   :material-console-line: **ブログ記事：Google ADK + Vertex AI Live API**

    ---

    この記事では、リアルタイムの音声・映像ストリーミングのためにADKで双方向ストリーミング（ライブ）を使用する方法を紹介します。`LiveRequestQueue`を使用してカスタムの対話型AIエージェントを構築するためのPythonサーバーの例を提供します。

    - [ブログ記事：Google ADK + Vertex AI Live API](https://medium.com/google-cloud/google-adk-vertex-ai-live-api-125238982d5e)

-   :material-console-line: **ブログ記事：Claude Code SkillsでADK開発を飛躍的に加速**

    ---

    この記事では、Claude Code Skillsを使用してADK開発を加速する方法を、双方向ストリーミングチャットアプリの構築例とともに示します。AIを活用したコーディング支援を利用して、より良いエージェントをより速く構築する方法を学びましょう。

    - [ブログ記事：Claude Code SkillsでADK開発を飛躍的に加速](https://medium.com/@kazunori279/supercharge-adk-development-with-claude-code-skills-d192481cbe72)

</div>