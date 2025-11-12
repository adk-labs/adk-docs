# ADK向けGoクイックスタート

このガイドでは、Go向けAgent Development Kitのセットアップと実行方法について説明します。開始する前に、以下がインストールされていることを確認してください。

*   Go 1.24.4以降

## エージェントプロジェクトの作成

次のファイルとディレクトリ構造でエージェントプロジェクトを作成します。

```none
my_agent/
    agent.go    # メインエージェントコード
    .env        # APIキーまたはプロジェクトID
```

??? tip "コマンドラインを使用してこのプロジェクト構造を作成する"

    === "Windows"

        ```console
        mkdir my_agent\
        type nul > my_agent\agent.go
        type nul > my_agent\env.bat
        ```

    === "MacOS / Linux"

        ```bash
        mkdir -p my_agent/ && \
            touch my_agent/agent.go && \
            touch my_agent/.env
        ```

### エージェントコードの定義

組み込みの[Google検索ツール](/adk-docs/tools/built-in-tools/#google-search)を使用する基本的なエージェントのコードを作成します。プロジェクトディレクトリの`my_agent/agent.go`ファイルに次のコードを追加します。

```go title="my_agent/agent.go"
package main

import (
  "context"
  "log"
  "os"

  "google.golang.org/adk/agent/llmagent"
  "google.golang.org/adk/cmd/launcher/adk"
  "google.golang.org/adk/cmd/launcher/full"
  "google.golang.org/adk/model/gemini"
  "google.golang.org/adk/server/restapi/services"
  "google.golang.org/adk/tool"
  "google.golang.org/adk/tool/geminitool"
  "google.golang.org/genai"
)

func main() {
  ctx := context.Background()

  model, err := gemini.NewModel(ctx, "gemini-2.5-flash", &genai.ClientConfig{
    APIKey: os.Getenv("GOOGLE_API_KEY"),
  })
  if err != nil {
    log.Fatalf("Failed to create model: %v", err)
  }

  agent, err := llmagent.New(llmagent.Config{
    Name:        "hello_time_agent",
    Model:       model,
    Description: "指定された都市の現在時刻を伝えます。",
    Instruction: "あなたは都市の現在時刻を伝える役立つアシスタントです。",
    Tools: []tool.Tool{
      geminitool.GoogleSearch{},
    },
  })
  if err != nil {
    log.Fatalf("Failed to create agent: %v", err)
  }

  config := &adk.Config{
    AgentLoader: services.NewSingleAgentLoader(agent),
  }

  l := full.NewLauncher()
  err = l.Execute(ctx, config, os.Args[1:])
  if err != nil {
    log.Fatalf("run failed: %v\n\n%s", err, l.CommandLineSyntax())
  }
}
```

### プロジェクトと依存関係の構成

`go mod`コマンドを使用して、プロジェクトモジュールを初期化し、エージェントコードファイルの`import`ステートメントに基づいて必要なパッケージをインストールします。

```console
go mod init my-agent/main
go mod tidy
```

### APIキーの設定

このプロジェクトでは、APIキーが必要なGemini APIを使用します。まだGemini APIキーをお持ちでない場合は、Google AI Studioの[APIキー](https://aistudio.google.com/app/apikey)ページでキーを作成してください。

ターミナルウィンドウで、APIキーをプロジェクトの`.env`または`env.bat`ファイルに書き込み、環境変数を設定します。

=== "MacOS / Linux"

    ```bash title="Update: my_agent/.env"
    echo 'export GOOGLE_API_KEY="YOUR_API_KEY"' > .env
    ```

=== "Windows"

    ```console title="Update: my_agent/env.bat"
    echo 'set GOOGLE_API_KEY="YOUR_API_KEY"' > env.bat
    ```

??? tip "ADKで他のAIモデルを使用する"
    ADKは、多くの生成AIモデルの使用をサポートしています。ADKエージェントで他のモデルを構成する方法の詳細については、[モデルと認証](/adk-docs/agents/models)を参照してください。


## エージェントの実行

定義したインタラクティブなコマンドラインインターフェイスまたはADK Goコマンドラインツールによって提供されるADK Webユーザーインターフェイスを使用して、ADKエージェントを実行できます。これらのオプションの両方で、エージェントをテストして対話できます。

### コマンドラインインターフェイスで実行

次のGoコマンドを使用してエージェントを実行します。

```console title="Run from: my_agent/ directory"
# キーと設定を読み込むことを忘れないでください：source .envまたはenv.bat
go run agent.go
```

![adk-run.png](/adk-docs/assets/adk-run.png)

### Webインターフェイスで実行

次のGoコマンドを使用して、ADK Webインターフェイスでエージェントを実行します。

```console title="Run from: my_agent/ directory"
# キーと設定を読み込むことを忘れないでください：source .envまたはenv.bat
go run agent.go web api webui
```

このコマンドは、エージェント用のチャットインターフェイスを備えたWebサーバーを起動します。（http://localhost:8080）でWebインターフェイスにアクセスできます。左上隅でエージェントを選択し、リクエストを入力します。

![adk-web-dev-ui-chat.png](/adk-docs/assets/adk-web-dev-ui-chat.png)

## 次へ：エージェントの構築

ADKをインストールして最初のエージェントを実行したので、ビルドガイドを使用して独自のエージェントを構築してみてください。

*  [エージェントの構築](/adk-docs/tutorials/)

```