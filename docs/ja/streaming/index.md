# ADKにおける双方向ストリーミング(live)

!!! info

    これは実験的な機能です。現在、Pythonで利用可能です。

!!! info

    これはサーバーサイドストリーミングやトークンレベルストリーミングとは異なります。このセクションは双方向ストリーミング(live)に関するものです。
    
ADKの双方向ストリーミング(live)は、[Gemini Live API](https://ai.google.dev/gemini-api/docs/live)の低遅延な双方向音声・映像対話機能をAIエージェントに追加します。

双方向ストリーミング(live)モードを使用すると、エンドユーザーに対して、エージェントの応答に音声コマンドで割り込む機能など、自然で人間らしい音声会話の体験を提供できます。ストリーミング機能を持つエージェントは、テキスト、音声、映像の入力を処理し、テキストと音声の出力を提供できます。

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

<div class="grid cards" markdown>

-   :material-console-line: **クイックスタート (双方向ストリーミング)**

    ---

    このクイックスタートでは、シンプルなエージェントを構築し、ADKのストリーミングを使用して低遅延かつ双方向の音声・映像コミュニケーションを実装します。

    - [クイックスタート (双方向ストリーミング)](../get-started/streaming/quickstart-streaming.md)

-   :material-console-line: **カスタム音声ストリーミングアプリのサンプル**

    ---

    この記事では、ADKストリーミングとFastAPIで構築されたカスタム非同期Webアプリのサーバーとクライアントのコードの概要を説明します。Server Sent Events (SSE)とWebSocketsの両方を使用して、リアルタイムの双方向音声・テキスト通信を可能にします。

    - [カスタム音声ストリーミングアプリのサンプル (SSE)](custom-streaming.md)
    - [カスタム音声ストリーミングアプリのサンプル (WebSockets)](custom-streaming-ws.md)

-   :material-console-line: **双方向ストリーミング開発ガイドシリーズ**

    ---

    ADKによる双方向ストリーミング開発をより深く掘り下げるための記事シリーズです。基本的な概念とユースケース、コアAPI、そしてエンドツーエンドのアプリケーション設計について学ぶことができます。

    - [双方向ストリーミング開発ガイドシリーズ: パート1 - はじめに](dev-guide/part1.md)

-   :material-console-line: **ストリーミングツール**

    ---

    ストリーミングツールを使用すると、ツール(関数)が中間結果をエージェントにストリーミングで返し、エージェントがその中間結果に応答できます。例えば、ストリーミングツールを使って株価の変動を監視し、エージェントに反応させることができます。別の例として、エージェントにビデオストリームを監視させ、ストリームに変化があった場合にその変化を報告させることも可能です。

    - [ストリーミングツール](streaming-tools.md)

-   :material-console-line: **カスタム音声ストリーミングアプリのサンプル**

    ---

    この記事では、ADKストリーミングとFastAPIで構築されたカスタム非同期Webアプリのサーバーとクライアントのコードの概要を説明します。Server Sent Events (SSE)とWebSocketsの両方を使用して、リアルタイムの双方向音声・テキスト通信を可能にします。

    - [ストリーミング設定](configuration.md)

-   :material-console-line: **ブログ投稿: Google ADK + Vertex AI Live API**

    ---

    この記事では、ADKの双方向ストリーミング(live)を使用してリアルタイムの音声/映像ストリーミングを行う方法を紹介します。LiveRequestQueueを使用してカスタムの対話型AIエージェントを構築するためのPythonサーバーの例を提供します。

    - [ブログ投稿: Google ADK + Vertex AI Live API](https://medium.com/google-cloud/google-adk-vertex-ai-live-api-125238982d5e)

</div>