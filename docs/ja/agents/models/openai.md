# ADK エージェント向け OpenAI モデル

<div class="language-support-tag">
   <span class="lst-supported">ADKでサポート</span><span class="lst-go">Go v2.1.0</span><span class="lst-preview">実験的機能</span>
</div>

!!! example "実験的機能"

    `openaimodel` パッケージは実験的機能であり、将来動作が変更または削除される可能性があります。皆さまの [フィードバック](https://github.com/google/adk-go/issues/new?template=feature_request.md) を歓迎します！

ADK では OpenAI モデルを使用できます。接続方法は言語によって異なります。

- **Go — ネイティブ サポート:** ADK Go は OpenAI Responses API または [Chat Completions API](#chat-completions-api) をターゲットとし、`model.LLM` インターフェースを実装する `openaimodel` パッケージを直接提供します。[はじめに](#get-started)を参照してください。
- **Python — LiteLLM 経由:** ADK Python は LiteLLM コネクタを通じて OpenAI モデル（および他の多くのプロバイダー）にアクセスします。[LiteLLM](/ja/agents/models/litellm/)を参照してください。

## はじめに {#get-started}

`openaimodel` パッケージは、OpenAI API と対話するためのクライアントを提供します。このパッケージは `model.LLM` インターフェースを実装しており、デフォルトで OpenAI Responses API を使用するか、`ClientConfig.API` で選択された場合は [Chat Completions API](#chat-completions-api) を使用します。
以下のコード例は、エージェントで OpenAI モデルを使用する基本的な実装を示しています。

=== "Go"

    === "Responses API"

        ```go
        import (
        	"context"
        	"log"

        	"github.com/openai/openai-go/v3"
        	"google.golang.org/adk/v2/agent/llmagent"
        	"google.golang.org/adk/v2/model/openaimodel"
        )

        // Instantiate the model
        llm, err := openaimodel.NewModel(context.Background(), openai.ChatModelGPT4oMini, &openaimodel.ClientConfig{})
        if err != nil {
          log.Fatal(err)
        }

        // Create the agent
        agent, err := llmagent.New(llmagent.Config{
          Name:        "openai_agent",
          Model:       llm,
          Instruction: "You are a helpful AI assistant.",
        })
        if err != nil {
          log.Fatal(err)
        }
        ```

        完全な実行可能サンプルについては、ADK Go リポジトリの [examples/openai/responses/](https://github.com/google/adk-go/tree/main/examples/openai/responses) を参照してください。

    === "Chat Completions API"

        ADK Go v2.5.0 以降が必要です。

        ```go
        import (
        	"context"
        	"log"
        	"os"

        	"github.com/openai/openai-go/v3"
        	"google.golang.org/adk/v2/agent/llmagent"
        	"google.golang.org/adk/v2/model/openaimodel"
        )

        // Instantiate the model on the Chat Completions API
        llm, err := openaimodel.NewModel(context.Background(), openai.ChatModelGPT4oMini, &openaimodel.ClientConfig{
          APIKey: os.Getenv("OPENAI_API_KEY"),
          API:    openaimodel.APIChatCompletions,
        })
        if err != nil {
          log.Fatal(err)
        }

        // Create the agent
        agent, err := llmagent.New(llmagent.Config{
          Name:        "openai_agent",
          Model:       llm,
          Instruction: "You are a helpful AI assistant.",
        })
        if err != nil {
          log.Fatal(err)
        }
        ```

        完全な実行可能サンプルについては、ADK Go リポジトリの [examples/openai/completions/](https://github.com/google/adk-go/tree/main/examples/openai/completions) を参照してください。

## Chat Completions API {#chat-completions-api}

<div class="language-support-tag">
   <span class="lst-supported">ADKでサポート</span><span class="lst-go">Go v2.5.0</span><span class="lst-preview">実験的機能</span>
</div>

デフォルトでは、`openaimodel` は OpenAI の [Responses API](https://platform.openai.com/docs/api-reference/responses)（`POST /v1/responses`）にリクエストを送信します。ほぼすべての OpenAI 互換プロバイダーが [Chat Completions API](https://platform.openai.com/docs/api-reference/chat)（`POST /v1/chat/completions`）を実装しており、中にはそちらのみを実装しているプロバイダーもあります。これを使用するには、[はじめに](#get-started)の「Chat Completions API」タブに示されているように、`ClientConfig` の `API` フィールドを `openaimodel.APIChatCompletions` に設定します。エージェント、ツール、およびランナーはどちらの API でも同じように動作します。

!!! warning "他のプロバイダー向けの API キーの設定"

    別の OpenAI 互換プロバイダーに接続するには、`BaseURL` にそのエンドポイントを設定し、`APIKey` にそのキーを設定してください。`APIKey` が空の場合、`openai-go` SDK は環境変数 `OPENAI_API_KEY` にフォールバックし、そのキーを `BaseURL` に送信します。

2 つの API は同じ機能をサポートしていますが、次の違いがあります。

- **生成設定:** `StopSequences`、`FrequencyPenalty`、`PresencePenalty`、および `Seed` は Chat Completions API に送信されます。Responses API には同等のフィールドがなく、これらに対してエラーを返します。
- **推論出力:** Chat Completions API は推論テキストを返さないため、レスポンスに思考（thought）パートは含まれず、`ThinkingConfig.IncludeThoughts` は無視されます。推論の深さ（effort）と推論トークン数のカウントは両方の API で機能します。
- **出力トークン上限:** `MaxOutputTokens` は `max_completion_tokens` として送信されます。一部の互換サーバーは古い `max_tokens` フィールドのみを認識するため、そのようなサーバーでは上限が適用されません。

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
- 一部の `GenerateContentConfig` オプションは黙って無視されるのではなくエラーを返します: `TopK`、複数候補（multiple candidates）、リクエスト ラベル、およびセーフティ設定。また、Responses API は停止シーケンス（stop sequences）、頻度/存在ペナルティ、およびシード（seed）も拒否しますが、これらは [Chat Completions API](#chat-completions-api) でサポートされています。

## 構成オプション

`ClientConfig` はクライアントを構成するための複数のオプションを提供します。

- `APIKey`: OpenAI API キー。
- `BaseURL`: カスタム エンドポイント URL（OpenAI 互換エンドポイントに便利です）。
- `HTTPClient`: カスタム `*http.Client`。
- `Options`: 高度な `openai-go` リクエスト オプション（`[]option.RequestOption`）。
- `API`: 呼び出す OpenAI API: `openaimodel.APIResponses`（デフォルト）または `openaimodel.APIChatCompletions`。[Chat Completions API](#chat-completions-api)を参照してください。

`APIKey` または `BaseURL` を空のままにすると、標準の `openai-go` SDK のデフォルト動作により、自動的に `OPENAI_API_KEY` および `OPENAI_BASE_URL` 環境変数にフォールバックします。

## OpenAI モデルの認証

OpenAI モデルを使用する場合、OpenAI API で認証するために API キーを提供する必要があります。この情報を提供する最も直接的な方法は、環境変数または `.env` ファイルを使用することです。

`openaimodel` パッケージは、ベース URL を構成することにより、OpenAI 互換のエンドポイント（Ollama、LM Studio、vLLM などを通じてサービス提供されるローカル モデルなど）もサポートします。エンドポイントが Responses API を提供していない場合は、[Chat Completions API](#chat-completions-api)で説明されているように、`API` も `openaimodel.APIChatCompletions` に設定してください。

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
