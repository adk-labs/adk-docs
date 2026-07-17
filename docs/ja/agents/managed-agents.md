# Managed agents (マネージドエージェント)

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v2.4.0</span><span class="lst-preview">Preview</span>
</div>

Managed agents（マネージドエージェント）を使用すると、ADK フロー内から Managed Agents API をサポートする Google のファーストパーティ製の即座に利用可能なエージェントを使用できます。Managed agents は、[Gemini API](https://ai.google.dev/gemini-api/docs/agents) および [Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/managed-agents) を通じて提供されます。`ManagedAgent` クラスは、専用のサーバーサイド実行環境で実行されるマネージドエージェント（Antigravity エージェントなど）に接続するため、サンドボックスの管理やクライアントサイドの関数宣言の作成を行うことなく、強力な組み込み機能を利用できます。

`ManagedAgent` は、他の ADK エージェントと同じ `BaseAgent` 契約を実装しているため、スタンドアロンで使用することも、ADK フローに直接組み込むこともできます。この環境を自分で構築して運用するのではなく、専用の組み込みツールを備えた堅牢なサーバーホスト型のエージェントが必要な場合に適しています。

## Managed agents とは何ですか？

*Managed agent（マネージドエージェント）*とは、独自の ADK プロセスで実行されるのではなく、Managed Agents API を通じて Google が推論、ツール、および実行環境をホストして運用するエージェントのことです。`ManagedAgent` は、標準の `generate_content` 呼び出しを発行する代わりに、サーバーサイドの*インタラクション（interaction）*を作成し、結果を ADK フローにストリーミングして送り返します。Managed agents には、いくつかの組み込みのメリットがあります。

- **ファーストパーティ製の即座に利用可能なエージェント:** 既製のエージェント（Antigravity エージェントなど）の `agent_id` を参照して接続します.
- **組み込みのサーバーサイド実行:** Web 検索やコード実行などの機能がサーバー上のマネージドサンドボックスで実行されるため、ローカルサンドボックスのプロビジョニングやセキュリティ保護は不要です.
- **クライアントサイドの関数宣言なし:** サーバーサイドのツールはマネージドエージェント上で構成されるため、ローカルで宣言または実行することはありません.

## 自分で構築する場合と Managed agents を使用する場合の比較

Managed agents と ADK エージェントは、それぞれ異なる問題を解決します。どちらを選択するかは、主にすぐに使える組み込み機能の便利さと、きめ細かな制御との間のトレードオフになります。

- **Managed agents** は、強力なエージェントをすぐに利用できるように提供しますが、柔軟性は限られています。ツールセットは事前定義されたサーバーサイドのものであり、エージェントはマネージド環境でのみ動作し、クライアントサイドツールや MCP ツールはサポートされていません。
- **ADK エージェント**（[`LlmAgent`](/ja/agents/llm-agents/) など）は、モデル、指示、ツール（カスタム関数ツールや MCP ツールを含む）、および実行の場所に対するきめ細かな制御を提供します。

## 前提条件

`ManagedAgent` は 2 つのバックエンドをサポートしています。使用する予定のバックエンドの前提条件を完了し、認証情報（credentials）と `agent_id` を取得してください。

### Gemini API バックエンド

- **認証:** Gemini API キーを取得し、それを `GEMINI_API_KEY` 環境変数として設定します.
- **エージェント ID:** 接続先の `agent_id` が必要です。次のいずれかを行います。
    - [Gemini API エージェントのドキュメント](https://ai.google.dev/gemini-api/docs/agents)に従って、新しいエージェントを作成します。
    - 以下の例で使用されている `antigravity-preview-05-2026` などの、即座に利用可能なエージェント ID を使用します。

### Agent Platform バックエンド

- **認証:** Agent Platform には Google Cloud の認証情報が必要です。[Agent Platform のセットアップ手順](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/managed-agents/create-manage#before-you-begin)に従って、ローカル環境を認証します（例: `gcloud auth application-default login` を使用）。
- **ロケーション:** Managed Agents API は `global` ロケーションからのみ提供されます。`ManagedAgent` は、Agent Platform バックエンドで `global` への接続を強制します。
- **エージェント ID:** Gemini API と同様に `agent_id` が必要です。[エージェントの作成と管理ガイド](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/managed-agents/create-manage)を介して作成するか、プロジェクトで利用可能な既製のエージェント ID を使用します。

## 始める

次の例では、2 つのマネージドエージェントを作成します。1 つは Web 検索を使用して質問に回答し、もう 1 つはサーバーサイドでコードを実行して計算問題を解決します。どちらもマネージド環境（`environment={'type': 'remote'}`）でツールを実行します。

=== "Python"

    ```python
    import os
    from google.adk.agents import ManagedAgent
    from google.adk.tools import google_search
    from google.genai import types

    # MANAGED_AGENT_ID と適切な環境設定があることを確認してください。
    _AGENT_ID = os.environ.get('MANAGED_AGENT_ID', 'antigravity-preview-05-2026')

    managed_search_agent = ManagedAgent(
        name='managed_search_agent',
        description='Answers questions that need fresh, grounded information from the web.',
        agent_id=_AGENT_ID,
        environment={'type': 'remote'},
        tools=[google_search],
    )

    # 生の types.Tool を使用するマネージドコード実行エージェント
    managed_code_execution_agent = ManagedAgent(
        name='managed_code_execution_agent',
        description='Solves computational questions by running code server-side.',
        agent_id=_AGENT_ID,
        environment={'type': 'remote'},
        tools=[types.Tool(code_execution=types.ToolCodeExecution())],
    )
    ```

## 仕組み

`ManagedAgent` を呼び出すと、ADK は [Interactions API](https://ai.google.dev/gemini-api/docs/interactions-overview) を介してリクエストをマネージドエージェントに送信し、中間および最終的な結果をリアルタイムで ADK フローにストリーミングして戻します。推論,ツール,および実行はすべて,ADK プロセスではなく Google のマネージド環境で実行されます.

!!! note "`ManagedAgent` が Managed Agents API にどのようにマッピングされるか"

    ADK `ManagedAgent` は、新しいマネージドエージェントリソースを作成または登録しません。バックエンドに既に存在するエージェント（`agent_id` で指定されたもの）に接続し、その設定（`tools` や `environment` など）を実行時のインタラクションごとのオーバーライドとして適用します。Managed Agents API の用語で言えば、ADK は完全にデータプレーン（Interactions API）のみで動作し、コントロールプレーン（エージェントリソースを作成および管理する Agents API）には触れません。これら 2 つのプレーンの違いについては、[Managed Agents API のシステムアーキテクチャ](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/managed-agents)を参照してください。

### ローカルセッションとリモート状態

`ManagedAgent` はローカルに状態をほとんど保持しません。ADK セッションは、出力するイベント上で `previous_interaction_id` とサンドボックスの `environment_id` の 2 つの値のみを保持します。新しいターンが発生するたびに、エージェントは以前のセッションイベントをスキャンしてこれら両方の値を復元し、再利用することで会話とサンドボックスを継続します。

それ以外のすべてはサーバーサイドに存在します。Managed Agents API がサンドボックス環境と完全なインタラクション履歴を所有し、ローカルセッションではなく、そのリモートインタラクションが会話を継続するための真実のソース（source of truth）となります。応答テキストはローカルの ADK イベントとリモートのインタラクション履歴の両方に表示されますが、ADK はリモートの状態を復元して再利用するために必要な ID のみを保存し、以前のターンを再送信することはありません。

## 制限事項

- **ロケーションの固定（Agent Platform のみ）:** Agent Platform バックエンドの場合、Managed Agents API は現在 `global` ロケーションからのみ提供されます。リージョナルエンドポイントはエラーを発生させます。
- **サーバーサイドツールのみ:** クライアントで実行されるツール（Python 関数、呼び出し可能オブジェクト）および MCP ツールはサポートされておらず、`NotImplementedError` を発生させます。
- **ストリーミングのみ:** エージェントはストリーミングインタラクション（`stream=True`）を使用します。バックグラウンドポーリング実行および厳密な非ストリーミング接続は、まだ完全にはサポートされていません。
- **バックエンドの違い:** Gemini API と Agent Platform バックエンドは、現在、動作パターンが若干異なります。使用する予定の特定のバックエンドに対してテストを行ってください。

## 次のステップ

- **サンプル:** [Managed Agent Basic](https://github.com/google/adk-python/tree/main/contributing/samples/managed_agent/basic) および [Managed Agent Code Execution](https://github.com/google/adk-python/tree/main/contributing/samples/managed_agent/code_execution)。
- **バックエンドドキュメント:** [Gemini API エージェント](https://ai.google.dev/gemini-api/docs/agents) および [Agent Platform Managed Agents](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/managed-agents)。
- **関連する ADK トピック:** [エージェント向けのモデル](/ja/agents/models/)、[マルチエージェントワークフロー](/ja/workflows/)、[カスタムツール](/ja/tools-custom/)。
