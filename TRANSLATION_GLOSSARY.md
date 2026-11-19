# ADK Documentation Translation & Developer Terminology Guide (KO / JA)

This document defines the canonical translation standards and developer terminology glossary for Korean (`docs/ko/`) and Japanese (`docs/ja/`) localizations of the Agent Development Kit (ADK) documentation.

---

## 1. Core Principles

1. **Write for practicing software & AI engineers**:
   - Translate prose into natural, idiomatic technical Korean (`~합니다`/`~하세요` style) and Japanese (`です`/`ます` style) used in modern developer documentation.
   - Avoid word-for-word machine-translation calques (직역투 / 直訳調). Restructure sentences so cause-and-effect, conditions, and API behavior read clearly at first glance.
2. **Never translate code identifiers, types, or CLI syntax**:
   - Keep class names, method/function names, parameter/field names, environment variables, CLI commands/flags, package names, and literal string values in English code spans (e.g., `` `App` ``, `` `Runner` ``, `` `LlmAgent` ``, `` `Context` ``, `` `ToolContext` ``, `` `CallbackContext` ``, `` `InvocationContext` ``, `` `ReadonlyContext` ``, `` `RunConfig` ``, `` `Event` ``, `` `Session` ``, `` `FunctionTool` ``, `` `McpToolset` ``, `` `BasePlugin` ``, `` `InstructionProvider` ``).
   - If the English source uses bold-italics (`***App***`, `***Runner***`, `***Agent***`, `***Event***`) to refer to an SDK class or parameter (`on_startup`, `streaming_mode`), keep the identifier in English (`***App*** 클래스` / `` `App` 클래스 ``, `***App*** クラス` / `` `App` クラス ``) — **never** translate class/parameter identifiers into `***앱*** 클래스`, `***실행기*** 클래스`, or `***스트리밍 모드*** 매개변수`.
3. **Preserve MkDocs & structural syntax 100%**:
   - Never alter fenced code blocks (` ``` `), `--8<--` snippet includes, relative file/image paths, URLs, heading anchor IDs (`{#anchor-id}`), HTML tags (`<div class="language-support-tag">`), tab headers (`=== "Python"`), admonition types (`!!! note`, `!!! warning`, `!!! tip`, `!!! example`), or integration catalog frontmatter keys and `catalog_tags` values (`catalog_tags` must stay in English so `render_catalog()` filtering works).
   - Remove stray zero-width characters (`\u200b`, `\u200c`, `\u200d`, `\ufeff`) introduced by machine translation tools.
   - Translate markdown table headers (`| Parameter | Type | Description |` -> `| 매개변수 | 타입 | 설명 |` / `| パラメータ | 型 | 説明 |`).

---

## 2. Developer Terminology Glossary (EN → KO / JA)

### A. Software Architecture & Engineering Terms

| English Term | Korean (권장 표현) | Japanese (推奨表現) | Avoid / Mistranslation (금지·주의 표현) |
|---|---|---|---|
| **separation of concerns** | 관심사 분리 | 関心の分離 | ❌ 우려 사항 분리 / 懸念事項の分離 |
| **cross-cutting concerns / functionality** | 횡단 관심사 / 공통 기능 | 横断的関心事 / 共通機能 | ❌ 교차 절단 기능 / 交差切断 |
| **short-circuit (workflow / execution)** | 조기 종료하다 / 단축 실행하다 | 早期終了する / ショートサーキットする | ❌ 워크플로를 단락시키다 / 短絡させる |
| **hook / callback hook** | 훅(hook) / 콜백 훅 | フック / コールバックフック | ❌ 후크 |
| **lifecycle** | 라이프사이클 (또는 생명주기) | ライフサイクル | ⚠️ 어색한 '수명 주기' 남발 지양 (GCS 버킷 수명 주기 등 공식 명칭 제외) |
| **logic (business / custom / agent logic)** | 로직 | ロジック | ❌ 논리 (불리언/수학 논리 제외) |
| **expose (methods / properties / columns)** | 제공하다 (외부 API·엔드포인트는 '외부에 공개하다/노출하다' 가능) | 提供する / 公開する（列・ビューは「列として提供する」等も可） | ❌ 내부 메서드·컬럼에 기계적으로 '노출합니다' 반복 |
| **publish (to Pub/Sub topic / queue)** | 발행(publish)하다 / 게시하다 | パブリッシュ（発行）する | ❌ 토픽에 공개하다 / トピックに公開する |
| **retrieve (state / session / artifact / credentials)** | 조회하다 / 가져오다 / 불러오다 | 取得する | ❌ 자격 증명·아티팩트·오디오를 '검색하다' (search와 혼동) |
| **persist (to database / storage / session)** | 영구 저장하다 / 저장하다 | 永続化する / 保存する | ❌ 파일로 유지하다 ('상태를 유지하다'와 구분) |
| **blob / large data blob** | 블롭(blob) / 대용량 바이너리 데이터 | Blob / 大容量バイナリデータ | ❌ 데이터 덩어리 / 大きなデータのかたまり |
| **raw bytes** | 원시 바이트(raw bytes) | 生バイト列（raw bytes） | ❌ 生のバイト (부자연스러운 직역 주의) |
| **serialize / deserialize** | 직렬화 / 역직렬화 | シリアライズ / デシリアライズ | — |
| **rigid columns / fixed schema** | 고정 컬럼 스키마 | 固定カラムスキーマ | ❌ 엄격한 열 구조 |
| **idempotent / idempotency** | 멱등성(idempotency) / 멱등적 | べき等（idempotent）/ べき等性 | — |
| **silently ignored / silently drops** | 별도 경고 없이 무시됨 / 경고 없이 누락됨 | 警告なしで無視される / 暗黙的に破棄される | ❌ 조용히 무시됨 / 黙って無視される |
| **refresh (cache / token)** | 갱신하다 | 更新する / リフレッシュする | ❌ 새로 고쳐지다 |
| **fingerprint** | 핑거프린트(fingerprint) | フィンガープリント | ❌ 지문 / 指紋 |
| **latency** | 지연 시간(latency) | レイテンシ | ❌ 대기 시간 (큐 대기 시간(queue wait time)과 구분) |
| **throughput** | 처리량(throughput) | スループット | — |
| **backoff (exponential backoff)** | 백오프 (지수 백오프) | バックオフ（指数バックオフ） | — |
| **boilerplate** | 보일러플레이트(상용구 코드) | ボイラープレート | — |
| **out of the box** | 별도 설정 없이 기본 제공되는 | 標準で（そのまま）利用可能な | ❌ 상자에서 꺼내자마자 |
| **under the hood** | 내부적으로 | 内部的には | ❌ 후드 아래에서 |
| **on the fly** | 실행 중에 동적으로 / 실시간으로 | 実行時に動的に / オンザフライで | ❌ 즉석에서 날아가는 |

### B. AI, LLM & ADK Domain Terms

| English Term | Korean (권장 표현) | Japanese (推奨表現) | Avoid / Mistranslation (금지·주의 표현) |
|---|---|---|---|
| **context window** | 컨텍스트 윈도우 | コンテキストウィンドウ | ❌ 컨텍스트 창 / コンテキスト窓 |
| **context compaction** | 컨텍스트 압축 | コンテキスト圧縮（コンパクション） | — |
| **grounding** | 그라운딩(Grounding) | グラウンディング（Grounding） | ❌ 접지 / 接地 |
| **instruction / system instruction** | 지침(instruction) / 시스템 지침 | 指示（instruction）/ システム指示 | ❌ 명령 (`InstructionProvider`를 '명령 공급자'로 번역 금지) |
| **invocation** | 호출(invocation) | 呼び出し（invocation） | — |
| **turn** | 턴(turn) | ターン | — |
| **pronoun resolution** | 대명사 참조 해석 | 代名詞の参照解決 | ❌ 대명사 해상도 |
| **cascade / half-cascade architecture** | 캐스케이드 / 하프 캐스케이드 아키텍처 | カスケード / ハーフカスケードアーキテクチャ | ❌ 계단식 / 절반 계단식 모델 |
| **transcription (audio / speech)** | 전사(transcription) / 음성 텍스트 변환 | 文字起こし（transcription） | — |
| **barge-in / interruption** | 끼어들기(바지인, barge-in) / 인터럽트 | 割り込み（バージイン、barge-in） | — |
| **tool confirmation (HITL)** | 도구 실행 승인(Tool Confirmation) | ツール実行の確認（Tool Confirmation） | ❌ 도구 확인 (단순 조회와 혼동) |
| **tool-only / tool-oriented method** | 도구 전용 메서드 | ツール専用メソッド | ❌ 도구 지향 메서드 / ツール指向メソッド |
| **only on its own (built-in tool limit)** | 단독으로만 (다른 도구와 함께 사용 불가) | 単独でのみ（他のツールと併用不可） | ❌ 자체적으로만 |
| **hallucination** | 할루시네이션(환각) | ハルシネーション | — |
| **orchestrator / sub-agent** | 오케스트레이터 / 서브 에이전트(하위 에이전트) | オーケストレーター / サブエージェント | — |
| **in-memory (runner / session / service)** | 인메모리(in-memory) | インメモリ（in-memory） | ❌ 메모리 내 실행기 |

### C. Common Table Headers

| English | Korean | Japanese |
|---|---|---|
| `Parameter` / `Field` / `Attribute` | `매개변수` / `필드` / `속성` | `パラメータ` / `フィールド` / `属性` |
| `Variable` / `Property` | `변수` / `속성(프로퍼티)` | `変数` / `プロパティ` |
| `Type` | `타입` | `型` |
| `Default` | `기본값` | `デフォルト` |
| `Required` | `필수 여부` (`필수` / `선택`) | `必須`（`必須` / `任意`） |
| `Tool` / `Capability` | `도구` / `기능` | `ツール` / `機能` |
| `Description` / `Purpose` | `설명` / `목적(용도)` | `説明` / `目的（用途）` |
