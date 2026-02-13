# データを用いたエージェントのグラウンディング

Grounding は、AI エージェントを外部情報ソースに接続し、より正確で最新かつ検証可能な応答を生成するプロセスです。
信頼できるデータに基づいて応答を行うことで、ハルシネーションを減らし、ユーザーに信頼できる情報源に基づいた回答を提供できます。

ADK は複数のグラウンディング手法をサポートします。

- **Google Search Grounding**: ニュース、天気、モデル学習後に変更された事実など、最新データを必要とするクエリ向けに、エージェントをリアルタイム Web 情報へ接続します。
- **Vertex AI Search Grounding**: 自社のプライベート文書やエンタープライズデータへのクエリに対応するため、組織のインデックス化文書へ接続します。
- **Agentic RAG**: Vector Search 2.0、Vertex AI RAG Engine、またはその他の検索システムを使って、検索クエリとフィルターを動的に構築・調整するエージェントを構築します。

<div class="grid cards" markdown>

-   :material-magnify: **Google Search Grounding**

    ---

    エージェントがWebのリアルタイムで信頼性の高い情報へアクセスできるようにします。Google Search grounding
    の設定、データフローの理解、grounding 応答の解釈、ユーザー向けの引用表示方法を確認します。

    - [Google Search Grounding を理解する](google_search_grounding.md)

-   :material-file-search: **Vertex AI Search Grounding**

    ---

    インデックス化されたエンタープライズ文書やプライベートデータリポジトリにエージェントを接続します。
    Vertex AI Search データストアの設定、組織知識ベースでの grounding、ソース帰属の提供方法を学びます。

    - [Vertex AI Search Grounding を理解する](vertex_ai_search_grounding.md)

-   :material-post: **ブログ記事: Vector Search 2.0 と ADK を用いた10分で作る Agentic RAG**

    ---

    単純な retrieve-then-generate パターンを超える Agentic RAG システムの構築方法を紹介します。
    このガイドでは、ユーザー意図の解析、メタデータフィルターの構築、Vector Search 2.0 と ADK を使った
    ハイブリッド検索で 2,000 件のロンドン Airbnb 一覧を検索する旅行エージェントの構築例を扱います。

    - [ブログ記事: Vector Search 2.0 と ADK を用いた10分で作る Agentic RAG](https://medium.com/google-cloud/10-minute-agentic-rag-with-the-new-vector-search-2-0-and-adk-655fff0bacac)

-   :material-notebook: **Vector Search 2.0 旅行エージェントノートブック**

    ---

    Agentic RAG 記事の実践的な Jupyter ノートブックです。実際の Airbnb データを用いて
    auto-embedding、RRF ランキングのハイブリッド検索、ADK ツール統合を含む
    エンドツーエンドの旅行エージェントを構築します。

    - [Vector Search 2.0 旅行エージェントノートブック](https://github.com/google/adk-samples/blob/main/python/notebooks/grounding/vectorsearch2_travel_agent.ipynb)

-   :material-text-search: **Deep Search Agent**

    ---

    トピックを包括的なレポートへ変換するためのプロダクション対応フルスタック調査エージェントです。
    human-in-the-loop の計画承認、反復検索改善、プランニング・調査・批評・作成のマルチエージェント構成を備えます。

    - [Deep Search Agent](https://github.com/google/adk-samples/tree/main/python/agents/deep-search)

-   :material-file-document-multiple: **RAG Agent**

    ---

    Vertex AI RAG Engine を用いたドキュメント Q&A エージェントです。文書をアップロードして質問するだけで、
    URL でソースを示す正確な回答と引用を取得できます。

    - [RAG Agent](https://github.com/google/adk-samples/tree/main/python/agents/RAG)

</div>
