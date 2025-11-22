# OpenAPIとのREST API連携

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span>
</div>

ADKは、[OpenAPI仕様（v3.x）](https://swagger.io/specification/)から呼び出し可能なツールを直接自動生成することで、外部REST APIとの連携を簡素化します。これにより、APIエンドポイントごとに個別の関数ツールを手動で定義する必要がなくなります。

!!! tip "主なメリット"
    `OpenAPIToolset` を使用して、既存のAPIドキュメント（OpenAPI仕様）からエージェントツール（`RestApiTool`）を即座に作成し、エージェントがWebサービスをシームレスに呼び出せるようにします。

## 主要コンポーネント

*   **`OpenAPIToolset`**: 主に使用する基本クラスです。OpenAPI仕様でこのクラスを初期化すると、仕様の解析とツールの生成が処理されます。
*   **`RestApiTool`**: `GET /pets/{petId}` や `POST /pets` のような、呼び出し可能な単一のAPIオペレーションを表すクラスです。`OpenAPIToolset` は、仕様で定義された各オペレーションに対して `RestApiTool` インスタンスを1つ作成します。

## 動作の仕組み

`OpenAPIToolset` を使用する際のプロセスは、以下の主要なステップで構成されます。

1.  **初期化と解析**:
    *   OpenAPI仕様をPythonの辞書、JSON文字列、またはYAML文字列の形式で `OpenAPIToolset` に提供します。
    *   ツールセットは内部で仕様を解析し、内部参照（`$ref`）を解決して完全なAPI構造を理解します。

2.  **オペレーションの検出**:
    *   仕様の `paths` オブジェクト内で定義されているすべての有効なAPIオペレーション（例：`GET`, `POST`, `PUT`, `DELETE`）を識別します。

3.  **ツールの生成**:
    *   検出された各オペレーションに対して、`OpenAPIToolset` は対応する `RestApiTool` インスタンスを自動的に作成します。
    *   **ツール名**: 仕様の `operationId` から派生します（`snake_case` に変換、最大60文字）。`operationId` がない場合は、メソッドとパスから名前が生成されます。
    *   **ツール説明**: LLMのために、オペレーションの `summary` または `description` を使用します。
    *   **API詳細**: 必要なHTTPメソッド、パス、サーバーのベースURL、パラメータ（パス、クエリ、ヘッダー、クッキー）、およびリクエストボディのスキーマを内部に保存します。

4.  **`RestApiTool` の機能**: 生成された各 `RestApiTool` は以下を実行します。
    *   **スキーマ生成**: オペレーションのパラメータとリクエストボディに基づいて `FunctionDeclaration` を動的に作成します。このスキーマは、LLMにツールの呼び出し方（期待される引数）を伝えます。
    *   **実行**: LLMによって呼び出されると、LLMから提供された引数とOpenAPI仕様の詳細を使用して、正しいHTTPリクエスト（URL、ヘッダー、クエリパラメータ、ボディ）を構築します。認証が設定されていればそれを処理し、`requests` ライブラリを使用してAPI呼び出しを実行します。
    *   **レスポンス処理**: APIレスポンス（通常はJSON）をエージェントフローに返します。

5.  **認証**: `OpenAPIToolset` を初期化する際に、グローバルな認証（APIキーやOAuthなど。詳細は[認証](/adk-docs/ja/tools/authentication/)を参照）を設定できます。この認証設定は、生成されたすべての `RestApiTool` インスタンスに自動的に適用されます。

## 使用ワークフロー

OpenAPI仕様をエージェントに統合するには、以下の手順に従います。

1.  **仕様の取得**: OpenAPI仕様ドキュメントを取得します（例：`.json` や `.yaml` ファイルから読み込む、URLから取得する）。
2.  **ツールセットのインスタンス化**: 仕様のコンテンツとタイプ（`spec_str`/`spec_dict`, `spec_str_type`）を渡して `OpenAPIToolset` のインスタンスを作成します。APIで必要な場合は、認証情報（`auth_scheme`, `auth_credential`）を提供します。

    ```python
    from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import OpenAPIToolset

    # JSON文字列の例
    openapi_spec_json = '...' # あなたのOpenAPI JSON文字列
    toolset = OpenAPIToolset(spec_str=openapi_spec_json, spec_str_type="json")

    # 辞書の例
    # openapi_spec_dict = {...} # あなたのOpenAPI仕様（辞書形式）
    # toolset = OpenAPIToolset(spec_dict=openapi_spec_dict)
    ```

3.  **エージェントへの追加**: 取得したツールを `LlmAgent` の `tools` リストに含めます。

    ```python
    from google.adk.agents import LlmAgent

    my_agent = LlmAgent(
        name="api_interacting_agent",
        model="gemini-2.0-flash", # またはお好みのモデル
        tools=[toolset], # ツールセットを渡す
        # ... その他のエージェント設定 ...
    )
    ```

4.  **エージェントへの指示**: エージェントの指示を更新し、新しいAPIの機能と使用可能なツールの名前（例：`list_pets`, `create_pet`）を伝えます。仕様から生成されたツールの説明もLLMの助けになります。
5.  **エージェントの実行**: `Runner` を使用してエージェントを実行します。LLMがAPIのいずれかを呼び出す必要があると判断すると、適切な `RestApiTool` を対象とする関数呼び出しを生成し、そのツールが自動的にHTTPリクエストを処理します。

## 例

この例では、シンプルなペットストアのOpenAPI仕様（モックのレスポンスには `httpbin.org` を使用）からツールを生成し、エージェントを介してそれらと対話する方法を示します。

???+ "コード：ペットストアAPI"

    ```python title="openapi_example.py"
    --8<-- "examples/python/snippets/tools/openapi_tool.py"
    ```