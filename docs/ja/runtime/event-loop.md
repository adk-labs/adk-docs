# Runtime Event Loop

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">Typescript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

ADK Runtime は、ユーザー対話中にエージェントアプリを動かす基盤エンジンです。
定義したエージェント、ツール、コールバックを連携させ、
入力に応じた情報フロー・状態変更・LLM/ストレージ連携を管理します。

Runtime はエージェントアプリの **エンジン** と考えるとわかりやすいです。
開発者は部品（Agent/Tool）を定義し、
Runtime がそれらを接続して実行します。

## コアアイデア: Event Loop

ADK Runtime の中心は **Event Loop** です。
`Runner` と実行ロジック（Agent、LLM 呼び出し、Callback、Tool）の
協調を回す仕組みです。

![intro_components.png](../assets/event-loop.png)

シンプルに言うと:

1. `Runner` がユーザー問い合わせを受け取りメイン `Agent` を開始
2. `Agent` が応答/ツール要求/状態変更などを `Event` として `yield`
3. `Runner` が受け取って処理（状態保存など）し上流へ転送
4. `Agent` は `Runner` 処理後にのみ再開
5. 現在の問い合わせでイベントが尽きるまで繰り返し

このイベント駆動ループが ADK 実行モデルの基本です。

## Event Loop の内部

!!! Note
    メソッド名や引数名は SDK 言語ごとに異なります。

### Runner の役割（オーケストレータ）

`Runner` は 1 回の invocation の中央調整役です。

1. **開始**: ユーザークエリを受け、SessionService に履歴追加
2. **Kick-off**: メインエージェント実行開始
3. **受信/処理**: `yield` された `Event` を即時処理
   - `state_delta` / `artifact_delta` などを Services でコミット
4. **上流転送**: UI/呼び出し元へ転送
5. **反復**: エージェントを再開し次イベント生成へ

### 実行ロジックの役割（Agent/Tool/Callback）

実際の判断・計算は実行ロジック側が担います。

1. 現在の `InvocationContext` で実行
2. 伝える内容を `Event` にして `yield`
3. `yield` 直後に一時停止
4. `Runner` 処理後に再開
5. 再開時は前イベントでコミット済み状態を参照可能

この `yield / pause / resume` サイクルが Runtime の中核です。

## Runtime の主要コンポーネント

1. ### `Runner`

      * **役割:** 1 ユーザークエリ実行の入口 (`run_async`)
      * **機能:** Event Loop 管理、イベント処理/コミット、上流転送

2. ### 実行ロジック

      * `Agent`（`BaseAgent`, `LlmAgent` など）
      * `Tools`（`BaseTool`, `FunctionTool`, `AgentTool` など）
      * `Callbacks`（フック関数）
      * **機能:** 判断/計算/外部連携を行い `Event` を `yield`

3. ### `Event`

      * **役割:** Runner と実行ロジック間のメッセージ
      * **機能:** コンテンツ + 副作用意図（`actions`）を運ぶ

4. ### `Services`

      * `SessionService`: Session 保存/読込、state 適用、履歴管理
      * `ArtifactService`: バイナリアーティファクト管理
      * `MemoryService`: （任意）長期意味記憶

5. ### `Session`

      * **役割:** 1 会話の状態/履歴コンテナ

6. ### `Invocation`

      * **役割:** 1 ユーザークエリに対する処理単位
      * **機能:** 複数の agent run / LLM call / tool 実行を `invocation_id` で束ねる

## シンプルな invocation フロー

![intro_components.png](../assets/invocation-flow.png)

典型例（ツール呼び出しを含む場合）:

1. ユーザー入力受信
2. Runner が Session を読み込み、ユーザーイベント記録
3. root agent 実行
4. LLM がツール呼び出しを判断
5. FunctionCall イベント `yield`
6. Agent 一時停止
7. Runner 処理/転送
8. Agent 再開
9. ツール実行
10. ツール結果取得
11. FunctionResponse イベント `yield`
12. Agent 一時停止
13. Runner が状態/アーティファクト差分をコミット
14. Agent 再開
15. 最終応答生成
16. テキストイベント `yield`
17. Agent 一時停止
18. Runner 転送
19. Agent 終了
20. Runner ループ完了

## 重要な Runtime 振る舞い

### 状態更新コミットのタイミング

状態変更は、`state_delta` を含むイベントが `yield` され、
Runner が処理した後に永続化が保証されます。

したがって `yield` 後に再開したコードは、
直前イベントのコミット済み状態を前提にできます。

### Session State の "Dirty Read"

同一 invocation 内では、コミット前のローカル状態が読める場合があります。

- 利点: 同一ステップ内コンポーネント連携がしやすい
- 注意: コミット前に失敗すると変更が失われる可能性

重要な状態遷移は、必ずイベント経由でコミットされる設計にしてください。

### Streaming vs Non-Streaming (`partial=True`)

- ストリーミング時は `partial=True` を即時転送
- 多くの場合、partial イベントの `actions` はコミットしない
- 最終イベント（`partial=False` など）で状態差分をコミット
- 非ストリーミングは単一イベントで処理

これにより、UI の逐次表示と状態一貫性を両立できます。

## Async が基本 (`run_async`)

ADK Runtime は非同期実行を前提に設計されています。
LLM 応答待ちやツール実行を効率よく扱うためです。

- 主要入口: `Runner.run_async`
- 同期 `run` は便宜用ラッパーで、内部で `run_async` を使うことが多い

### 同期コールバック/ツール利用時の注意

- ブロッキング I/O はイベントループ停滞の原因
  - Python は `asyncio.to_thread` などで回避可能
  - TypeScript は Promise ベース I/O を推奨
- CPU-bound 同期処理はスレッドを占有

これらを理解すると、状態整合性・ストリーミング更新・非同期実行に関する
設計/デバッグが容易になります。
