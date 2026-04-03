# モデルコンテキストプロトコル（MCP）

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span><span class="lst-go">Go</span><span class="lst-java">Java</span>
</div>

以前の日本語ページには、英語の原文にはないデータベースツールボックスの拡張内容が含まれていました。このページは現在、英語の構成に合わせており、ADK のローカライズ済みリンクを維持しています。

## MCPの仕組み

MCP は、Gemini や Claude のような大規模言語モデル（LLM）が外部アプリケーション、
データソース、ツールとどのように通信するかを標準化するために設計された
オープンスタンダードです。LLM がコンテキストを取得し、アクションを実行し、
さまざまなシステムと連携する方法を簡素化する、共通の接続メカニズムだと
考えてください。

!!! tip "ADK 用の MCP ツール"
    ADK の事前構築済み MCP ツールの一覧は、
    [Tools and Integrations](/integrations/?topic=mcp) を参照してください。

## ADK における MCP ツール

ADK は、MCP サービスを呼び出すツールを構築したい場合も、他の開発者やエージェントが
あなたのツールと対話できるように MCP サーバーを公開したい場合も、エージェント内で
MCP ツールを使うことを支援します。

ADK と MCP サーバーを組み合わせるためのコードサンプルと設計パターンについては、
[MCP Tools documentation](/ja/tools-custom/mcp-tools/) を参照してください。
ここには次が含まれます。

- **既存の MCP サーバーを ADK 内で使う**: ADK エージェントは MCP クライアントとして
  動作し、外部 MCP サーバーが提供するツールを利用できます。
- **MCP サーバー経由で ADK ツールを公開する**: ADK ツールをラップし、任意の
  MCP クライアントからアクセスできる MCP サーバーの構築方法です。

## ADK エージェントと FastMCP サーバー

[FastMCP](https://github.com/jlowin/fastmcp) は、複雑な MCP プロトコルの詳細や
サーバー管理をすべて処理してくれるため、優れたツールの構築に集中できます。
高レベルで Pythonic に設計されており、多くの場合は関数にデコレータを付けるだけで
済みます。

Cloud Run 上で動作する FastMCP サーバーと ADK を組み合わせる方法については、
[MCP Tools](/ja/tools-custom/mcp-tools/) を参照してください。

## Google Cloud Genmedia 向け MCP サーバー

[Genmedia Services 向け MCP Tools](https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio/tree/main/experiments/mcp-genmedia)
は、Imagen、Veo、Chirp 3 HD voices、Lyria などの Google Cloud 生成メディア
サービスを AI アプリケーションに統合できるようにする、オープンソースの MCP
サーバー群です。

Agent Development Kit (ADK) と [Genkit](https://genkit.dev/) は、これらの MCP
ツールに対する組み込みサポートを提供し、AI エージェントが生成メディアの
ワークフローを効果的にオーケストレーションできるようにします。実装ガイダンスは、
[ADK example agent](https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio/tree/main/experiments/mcp-genmedia/sample-agents/adk)
および [Genkit example](https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio/tree/main/experiments/mcp-genmedia/sample-agents/genkit)
を参照してください。
