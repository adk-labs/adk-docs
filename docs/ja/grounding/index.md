# データによるエージェントのグラウンディング

グラウンディングは、AI エージェントを外部情報ソースに接続し、より正確で最新かつ検証可能な応答を生成できるようにするプロセスです。信頼できるデータに応答を根拠づけることで、ハルシネーションを減らし、信頼できる情報源に裏付けられた回答をユーザーに提供できます。

ADK は複数のグラウンディング手法をサポートしています。

- **Google Search Grounding**: ニュース、天気、モデルの学習後に変わった可能性がある事実など、最新データが必要なクエリ向けに、エージェントをリアルタイムの Web 情報へ接続します。
- **Grounding with Search**: 専有情報が必要なクエリ向けに、エージェントを組織の非公開ドキュメントやエンタープライズ データへ接続します。
- **Agentic RAG**: Agent Retrieval、Knowledge Engine、その他の検索システムを使用して、クエリとフィルタを動的に構築しながら検索方法を推論するエージェントを構築します。

<div class="grid cards" markdown>

-   :material-magnify: **Google Search Grounding**

    ---

    エージェントが Web 上のリアルタイムで信頼できる情報にアクセスできるようにします。Google Search グラウンディングの設定、データフロー、グラウンディングされた応答の解釈、ユーザーへの引用表示について学びます。

    - [Google Search Grounding を理解する](google_search_grounding.md)

-   :material-file-search: **Grounding with Search**

    ---

    エージェントをインデックス化されたエンタープライズ ドキュメントや非公開データ リポジトリに接続します。Agent Search データストアの設定、組織のナレッジベースに基づく応答のグラウンディング、出典表示の方法を学びます。

    - [Grounding with Search を理解する](grounding_with_search.md)

-   :material-post: **ブログ記事: Vector Search 2.0 と ADK で作る 10 分 Agentic RAG**

    ---

    単純な検索して生成するパターンを超える Agentic RAG システムの構築方法を学びます。この記事では、ユーザー意図を解析し、メタデータ フィルタを構築し、Vector Search 2.0 と ADK のハイブリッド検索で 2,000 件のロンドン Airbnb リストを検索する旅行エージェントの構築手順を紹介します。

    - [ブログ記事: Vector Search 2.0 と ADK で作る 10 分 Agentic RAG](https://medium.com/google-cloud/10-minute-agentic-rag-with-the-new-vector-search-2-0-and-adk-655fff0bacac)

-   :material-notebook: **Vector Search 2.0 旅行エージェント ノートブック**

    ---

    Agentic RAG ブログ記事に対応する実践的な Jupyter ノートブックです。実際の Airbnb データ、自動埋め込み、RRF ランキングによるハイブリッド検索、ADK ツール統合を使用して、エンドツーエンドの旅行エージェントを構築します。

    - [Vector Search 2.0 旅行エージェント ノートブック](https://github.com/google/adk-samples/blob/main/python/notebooks/grounding/vectorsearch2_travel_agent.ipynb)

-   :material-text-search: **Deep Search Agent**

    ---

    トピックを引用付きの包括的なレポートへ変換する、本番対応のフルスタック リサーチ エージェントです。計画承認に human-in-the-loop を使い、反復的な検索改善と、計画・調査・批評・執筆を担当するマルチエージェント構成を備えています。

    - [Deep Search Agent](https://github.com/google/adk-samples/tree/main/python/agents/deep-search)

-   :material-file-document-multiple: **RAG Agent**

    ---

    Knowledge Engine を利用したドキュメント Q&A エージェントです。ドキュメントをアップロードして質問すると、ソース資料を指す URL 形式の引用とともに正確な回答を得られます。

    - [RAG Agent](https://github.com/google/adk-samples/tree/main/python/agents/RAG)

</div>
