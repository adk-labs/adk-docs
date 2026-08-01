# ADK エージェント向け OpenAI モデル

<div class="language-support-tag">
   <span class="lst-supported">ADKでサポート</span><span class="lst-go">Go v2.1.0</span><span class="lst-preview">実験的機能</span>
</div>

!!! example "実験的機能"

    `openaimodel` パッケージは実験的機能であり、将来動作が変更または削除される可能性があります。皆さまの [フィードバック](https://github.com/google/adk-go/issues/new?template=feature_request.md) を歓迎します！

ADK では OpenAI モデルを使用できます。接続方法は言語によって異なります。

- **Go — ネイティブ サポート:** ADK Go は OpenAI Responses API をターゲットとし、`model.LLM` インターフェースを実装する `openaimodel` パッケージを直接提供します。[はじめに](#はじめに)を参照してください。
- **Python — LiteLLM 経由:** ADK Python は LiteLLM コネクタを通じて OpenAI モデル（および他の多くのプロバイダー）にアクセスします。[LiteLLM](/ja/agents/models/litellm/)を参照してください。

## はじめに

`openaimodel` パッケージは、OpenAI API と対話するためのクライアントを提供します。このパッケージは `model.LLM` インターフェースを実装しているため、OpenAI Responses API 表面を公開しているプロバイダーと互換性があります。
以下のコード例は、エージェントで OpenAI モデルを使用する基本的な実装を示しています。

=== "Go"

    ```go
    import (
    	"context"
    	"log"

    	"github.com/openai/openai-go/v3"
    	"google.golang.org/adk/v2/agent/llmagent"
    	"google.golang.org/adk/v2/model/openaimodel"
    )

    // モデルのインスタンス化
    llm, err := openaimodel.NewModel(context.Background(), openai.ChatModelGPT4oMini, &openaimodel.ClientConfig{})
    if err != nil {
      log.Fatal(err)
    }

    // エージェントの作成
    agent, err := llmagent.New(llmagent.Config{
      Name:        "openai_agent",
      Model:       llm,
      Instruction: "You are a helpful AI assistant.",
    })
    if err != nil {
      log.Fatal(err)
    }
    ```

完全な実行可能サンプルについては、ADK Go リポジトリの [examples/openai/](https://github.com/google/adk-go/tree/main/examples/openai) を参照してください。

## サポートされている機能

- テキスト生成（ストリーミングおよび非ストリーミング）
- 関数（ツール）呼び出し (Function tool calling)
- `OutputSchema` (JSON スキーマ) を介した構造化出力
- 推論トークン計算を含む推論モデル（例: o-シリーズ）
- トークン Logprob

## 制限事項

- **テキストのみ** — マルチモーダル入力（画像、音声、ファイル）はサポートされていません。
- **関数ツールのみ** — 組み込みツール（Google 検索、コード実行など）はサポートされていません。
- **構造化出力は OpenAI 厳格モード（Strict mode）を使用** — `OutputSchema` に宣言されたすべてのフィールドは必須（required）として扱われます。
- 一部の `GenerateContentConfig` オプションは黙って無視されるのではなくエラーを返します: `TopK`、停止シーケンス（stop sequences）、複数候補（multiple candidates）、頻度/存在ペナルティ、リクエスト ラベル、およびセーフティ設定。

## 構成オプション

`ClientConfig` はクライアントを構成するための複数のオプションを提供します。

- `APIKey`: OpenAI API キー。
- `BaseURL`: カスタム エンドポイント URL（OpenAI 互換エンドポイントに便利です）。
- `HTTPClient`: カスタム `*http.Client`。
- `Options`: 高度な `openai-go` リクエスト オプション（`[]option.RequestOption`）。

`APIKey` または `BaseURL` を空のままにすると、標準の `openai-go` SDK のデフォルト動作により、自動的に `OPENAI_API_KEY` および `OPENAI_BASE_URL` 環境変数にフォールバックします。

## OpenAI モデルの認証

OpenAI 모델を使用する場合、OpenAI API で認証するために API キーを提供する必要があります。この情報を提供する最も直接的な方法は、環境変数または `.env` ファイルを使用することです。

`openaimodel` パッケージは、ベース URL を構成することにより、OpenAI 互換のエンドポイント（Ollama、LM Studio、vLLM などを通じてサービス提供されるローカル モデルなど）もサポートします。

=== "OpenAI API"

    ```bash
    # .env 構成ファイル
    OPENAI_API_KEY="PASTE_YOUR_OPENAI_API_KEY_HERE"
    ```

=== "OpenAI 互換エンドポイント"

    ```bash
    # .env 構成ファイル
    OPENAI_API_KEY="api-key-if-required"
    OPENAI_BASE_URL="http://localhost:11434/v1" # 例: ローカル Ollama エンドポイント
    ```
