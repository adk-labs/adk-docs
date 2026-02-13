# ADKにおける双方向（Bidi）ストリーミング（ライブ）

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.5.0</span><span class="lst-preview">実験的機能</span>
</div>

ADKの双方向（Bidi）ストリーミング（ライブ）は、[Gemini Live API](https://ai.google.dev/gemini-api/docs/live)の低遅延な双方向音声・映像インタラクション機能をAIエージェントに追加します。

双方向ストリーミング（ライブ）モードを使うことで、エンドユーザーに自然で人間らしい音声会話体験を提供できます。ユーザーが音声コマンドでエージェントの応答を割り込むことも可能です。ストリーミング対応エージェントは、テキスト・音声・映像入力を処理し、テキストおよび音声出力を返せます。

<div class="video-grid">
  <div class="video-item">
    <div class="video-container">
      <iframe src="https://www.youtube-nocookie.com/embed/vLUkAGeLR1k" title="ADK Bidi-streaming in 5 minutes" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
    </div>
  </div>
  <div class="video-item">
    <div class="video-container">
      <iframe src="https://www.youtube-nocookie.com/embed/Hwx94smxT_0" title="Shopper's Concierge 2 Demo" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
    </div>
  </div>
</div>

<div class="grid cards" markdown>

-   :material-console-line: **クイックスタート（双方向ストリーミング）**

    ---

    このクイックスタートでは、シンプルなエージェントを構築し、ADKストリーミングを使って低遅延の双方向音声・映像通信を実装します。

    - [クイックスタート（双方向ストリーミング）](../get-started/streaming/quickstart-streaming.md)

-   :material-console-line: **双方向ストリーミング デモアプリケーション**

    ---

    テキスト・音声・画像のマルチモーダル対応を含む、ADK双方向ストリーミングの本番向けリファレンス実装です。FastAPIベースで、リアルタイムWebSocket通信、自動文字起こし、Google Searchツール呼び出し、ストリーミングライフサイクル全体の管理を示します。開発ガイドシリーズ全体でこのデモを参照します。

    - [ADK 双方向ストリーミング デモ](https://github.com/google/adk-samples/tree/main/python/agents/bidi-demo)

-   :material-console-line: **ブログ記事: ADK Bidi-streaming ビジュアルガイド**

    ---

    ADK Bidi-streamingによるリアルタイム・マルチモーダルAIエージェント開発のビジュアルガイドです。直感的な図やイラストで、Bidi-streamingの仕組みとインタラクティブAIエージェントの作り方を理解できます。

    - [ブログ記事: ADK Bidi-streaming ビジュアルガイド](https://medium.com/google-cloud/adk-bidi-streaming-a-visual-guide-to-real-time-multimodal-ai-agent-development-62dd08c81399)

-   :material-console-line: **双方向ストリーミング開発ガイドシリーズ**

    ---

    ADKを使った双方向ストリーミング開発を深掘りするシリーズです。基本概念、ユースケース、コアAPI、エンドツーエンドのアプリケーション設計を学べます。

    - [Part 1: ADK Bidi-streaming 入門](dev-guide/part1.md) - Bidi-streamingの基礎、Live API技術、ADKアーキテクチャ構成要素、FastAPI例によるライフサイクル全体
    - [Part 2: LiveRequestQueueでメッセージ送信](dev-guide/part2.md) - 上流メッセージフロー、テキスト/音声/映像送信、アクティビティ信号、並行実行パターン
    - [Part 3: run_live() によるイベント処理](dev-guide/part3.md) - イベント処理、テキスト/音声/文字起こし処理、自動ツール実行、マルチエージェントワークフロー
    - [Part 4: RunConfig を理解する](dev-guide/part4.md) - 応答モダリティ、ストリーミングモード、セッション管理/再開、コンテキスト圧縮、クォータ管理
    - [Part 5: 音声・画像・映像の使い方](dev-guide/part5.md) - 音声仕様、モデルアーキテクチャ、音声文字起こし、VAD（音声活動検出）、プロアクティブ/感情対話機能

-   :material-console-line: **ストリーミングツール**

    ---

    ストリーミングツールを使うと、ツール（関数）が中間結果をエージェントにストリーミングし、エージェントがその中間結果に応答できます。例えば株価変動を監視して反応させたり、ビデオストリームの変化を検知して報告させたりできます。

    - [ストリーミングツール](streaming-tools.md)

-   :material-console-line: **ブログ記事: Google ADK + Vertex AI Live API**

    ---

    この記事では、ADKの双方向ストリーミング（ライブ）を使ってリアルタイム音声/映像ストリーミングを実装する方法を紹介します。`LiveRequestQueue` を使ってカスタム対話型AIエージェントを構築するPythonサーバー例を提供します。

    - [ブログ記事: Google ADK + Vertex AI Live API](https://medium.com/google-cloud/google-adk-vertex-ai-live-api-125238982d5e)

-   :material-console-line: **ブログ記事: Claude Code SkillsでADK開発を加速**

    ---

    Claude Code Skillsを使ってADK開発を加速する方法を、双方向ストリーミングチャットアプリの構築例とともに解説します。AI支援コーディングを活用して、より良いエージェントをより速く作る方法を学べます。

    - [ブログ記事: Claude Code SkillsでADK開発を加速](https://medium.com/@kazunori279/supercharge-adk-development-with-claude-code-skills-d192481cbe72)

</div>
