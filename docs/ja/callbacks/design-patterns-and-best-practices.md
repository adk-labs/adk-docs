# コールバックのためのデザインパターンとベストプラクティス

コールバックは、エージェントのライフサイクルに介入するための強力なフックを提供します。ここでは、ADKでコールバックを効果的に活用する方法を示す一般的なデザインパターンと、その実装におけるベストプラクティスを紹介します。

## デザインパターン

これらのパターンは、コールバックを使用してエージェントの振る舞いを強化または制御する典型的な方法を示しています。

### 1. ガードレールとポリシー適用 { #guardrails-policy-enforcement }

**パターンの概要:**
リクエストがLLMやツールに到達する前にそれを傍受し、ルールを適用します。

**実装:**
- `before_model_callback` を使用して `LlmRequest` のプロンプトを検査します。
- `before_tool_callback` を使用してツールの引数を検査します。
- ポリシー違反（例：禁止されたトピック、不適切な言葉）が検出された場合：
  - 事前に定義されたレスポンス（`LlmResponse` または `dict`/`Map`）を返して操作をブロックします。
  - オプションとして `context.state` を更新し、違反をログに記録します。

**使用例:**
`before_model_callback` が `llm_request.contents` に機密性の高いキーワードが含まれていないかチェックし、見つかった場合は標準の「このリクエストは処理できません」という `LlmResponse` を返し、LLMの呼び出しを防ぎます。

### 2. 動的な状態管理 { #dynamic-state-management }

**パターンの概要:**
コールバック内でセッションの状態を読み書きし、エージェントの振る舞いをコンテキストに応じて変化させ、ステップ間でデータを渡します。

**実装:**
- `callback_context.state` または `tool_context.state` にアクセスします。
- 変更（`state['key'] = value`）は、後続の `Event.actions.state_delta` で自動的に追跡されます。
- 変更は `SessionService` によって永続化されます。

**使用例:**
`after_tool_callback` がツールの結果から得た `transaction_id` を `tool_context.state['last_transaction_id']` に保存します。後の `before_agent_callback` は `state['user_tier']` を読み取り、エージェントの挨拶をカスタマイズするかもしれません。

### 3. ロギングとモニタリング { #logging-and-monitoring }

**パターンの概要:**
オブザーバビリティ（可観測性）とデバッグのために、特定のライフサイクルポイントで詳細なログを追加します。

**実装:**
- コールバック（例：`before_agent_callback`, `after_tool_callback`, `after_model_callback`）を実装します。
- 以下を含む構造化されたログを出力または送信します：
  - エージェント名
  - ツール名
  - 呼び出しID（Invocation ID）
  - コンテキストや引数からの関連データ

**使用例:**
`INFO: [Invocation: e-123] Before Tool: search_api - Args: {'query': 'ADK'}` のようなログメッセージを記録します。

### 4. キャッシング { #caching }

**パターンの概要:**
結果をキャッシュすることで、冗長なLLM呼び出しやツールの実行を回避します。

**実装手順:**
1.  **操作前:** `before_model_callback` または `before_tool_callback` 内で：
    - リクエスト/引数に基づいてキャッシュキーを生成します。
    - `context.state`（または外部キャッシュ）でこのキーを確認します。
    - 見つかった場合、キャッシュされた `LlmResponse` や結果を直接返します。

2.  **操作後:** キャッシュミスが発生した場合：
    - 対応する `after_` コールバックを使用して、新しい結果をそのキーでキャッシュに保存します。

**使用例:**
`get_stock_price(symbol)` のための `before_tool_callback` が `state[f"cache:stock:{symbol}"]` をチェックします。存在すればキャッシュされた価格を返し、そうでなければAPI呼び出しを許可し、`after_tool_callback` が結果を状態キーに保存します。

### 5. リクエスト/レスポンスの変更 { #request-response-modification }

**パターンの概要:**
データがLLM/ツールに送信される直前、または受信された直後にデータを変更します。

**実装オプション:**
- **`before_model_callback`:** `llm_request` を変更します（例：`state` に基づいてシステム指示を追加する）。
- **`after_model_callback`:** 返された `LlmResponse` を変更します（例：テキストのフォーマット、コンテンツのフィルタリング）。
- **`before_tool_callback`:** ツールの `args` ディクショナリ（JavaではMap）を変更します。
- **`after_tool_callback`:** `tool_response` ディクショナリ（JavaではMap）を変更します。

**使用例:**
`context.state['lang'] == 'es'` の場合、`before_model_callback` は `llm_request.config.system_instruction` に「ユーザーの言語設定：スペイン語」を追加します。

### 6. 条件付きでのステップのスキップ { #conditional-skipping-of-steps }

**パターンの概要:**
特定の条件に基づいて、標準的な操作（エージェントの実行、LLM呼び出し、ツールの実行）を防ぎます。

**実装:**
- `before_` コールバックから値を返すことで、通常の実行をスキップします：
  - `before_agent_callback` から `Content`
  - `before_model_callback` から `LlmResponse`
  - `before_tool_callback` から `dict`
- フレームワークは、この返された値をそのステップの結果として解釈します。

**使用例:**
`before_tool_callback` が `tool_context.state['api_quota_exceeded']` をチェックします。`True` の場合、`{'error': 'APIクオータを超えました'}` を返し、実際のツール関数の実行を防ぎます。

### 7. ツール固有のアクション（認証と要約制御） { #tool-specific-actions-authentication-summarization-control }

**パターンの概要:**
主に認証とツール結果のLLMによる要約制御など、ツールのライフサイクルに特有のアクションを処理します。

**実装:**
ツールのコールバック（`before_tool_callback`, `after_tool_callback`）内で `ToolContext` を使用します：

- **認証:** `before_tool_callback` 内で、認証情報が必要だが見つからない場合（例：`tool_context.get_auth_response` や状態チェックによる）、`tool_context.request_credential(auth_config)` を呼び出します。これにより認証フローが開始されます。
- **要約:** ツールの生の辞書出力をLLMにそのまま渡すか、直接表示する可能性がある場合（デフォルトのLLM要約ステップをバイパスする場合）、`tool_context.actions.skip_summarization = True` を設定します。

**使用例:**
セキュアなAPIのための `before_tool_callback` は状態内の認証トークンをチェックし、なければ `request_credential` を呼び出します。構造化JSONを返すツールの `after_tool_callback` は `skip_summarization = True` を設定するかもしれません。

### 8. アーティファクトの処理 { #artifact-handling }

**パターンの概要:**
エージェントのライフサイクル中に、セッション関連のファイルや大きなデータブロブを保存またはロードします。

**実装:**
- **保存:** `callback_context.save_artifact` / `await tool_context.save_artifact` を使用してデータを保存します：
  - 生成されたレポート
  - ログ
  - 中間データ
- **ロード:** `load_artifact` を使用して以前に保存されたアーティファクトを取得します。
- **追跡:** 変更は `Event.actions.artifact_delta` を介して追跡されます。

**使用例:**
"generate_report" ツールの `after_tool_callback` は、`await tool_context.save_artifact("report.pdf", report_part)` を使用して出力ファイルを保存します。`before_agent_callback` は、`callback_context.load_artifact("agent_config.json")` を使用して設定アーティファクトをロードするかもしれません。

## コールバックのベストプラクティス

### 設計原則

**責務を単一に保つ:**
各コールバックを、ロギングのみ、検証のみなど、単一の明確に定義された目的のために設計します。モノリシックなコールバックは避けてください。

**パフォーマンスへの配慮:**
コールバックはエージェントの処理ループ内で同期的に実行されます。長時間実行されたりブロッキングしたりする操作（ネットワーク呼び出し、重い計算）は避けてください。必要であればオフロードしますが、これにより複雑さが増すことに注意してください。

### エラーハンドリング

**エラーを適切に処理する:**
- コールバック関数内で `try...except/catch` ブロックを使用します。
- エラーを適切にログに記録します。
- エージェントの呼び出しを停止するか、回復を試みるかを決定します。
- コールバックのエラーでプロセス全体がクラッシュしないようにします。

### 状態管理

**状態を慎重に管理する:**
- `context.state` の読み書きは意図的に行います。
- 変更は*現在*の呼び出し内ですぐに反映され、イベント処理の最後に永続化されます。
- 意図しない副作用を避けるため、広範な構造を変更するのではなく、特定の状態キーを使用します。
- 特に永続的な `SessionService` の実装では、明確さのために状態の接頭辞（`State.APP_PREFIX`, `State.USER_PREFIX`, `State.TEMP_PREFIX`）の使用を検討してください。

### 信頼性

**べき等性を考慮する:**
コールバックが外部に副作用のあるアクション（例：外部カウンターのインクリメント）を実行する場合、フレームワークやアプリケーションでの再試行の可能性に対応するため、可能であればべき等（同じ入力で複数回実行しても安全）になるように設計します。

### テストとドキュメンテーション

**徹底的にテストする:**
- モックのコンテキストオブジェクトを使用してコールバック関数を単体テストします。
- 統合テストを実行し、コールバックがエージェントのフロー全体で正しく機能することを確認します。

**明確さを確保する:**
- コールバック関数には説明的な名前を使用します。
- その目的、実行タイミング、副作用（特に状態の変更）を説明する明確なドキュメント文字列（docstring）を追加します。

**正しいコンテキスト型を使用する:**
常に提供される特定のコンテキスト型（エージェント/モデル用は `CallbackContext`、ツール用は `ToolContext`）を使用し、適切なメソッドとプロパティにアクセスできるようにします。

これらのパターンとベストプラクティスを適用することで、コールバックを効果的に使用し、ADKでより堅牢で、観測可能で、カスタマイズされたエージェントの振る舞いを作成できます。