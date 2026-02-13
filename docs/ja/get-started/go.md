# ADK用Goクイックスタート

このガイドでは、Agent Development Kit for Goを使い始める方法について説明します。開始する前に、次のものがインストールされていることを確認してください。

*   Go 1.24.4以降
*   ADK Go v0.2.0以降

## エージェントプロジェクトを作成する

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

### エージェントコードを定義する

組み込みの[Google検索ツール](/adk-docs/ja/tools/built-in-tools/#google-search)を使用する基本的なエージェントのコードを作成します。プロジェクトディレクトリの`my_agent/agent.go`ファイルに次のコードを追加します。

```go title="my_agent/agent.go"
package main

import (
	"context"
	"log"
	"os"

	"google.golang.org/adk/agent"
	"google.golang.org/adk/agent/llmagent"
	"google.golang.org/adk/cmd/launcher"
	"google.golang.org/adk/cmd/launcher/full"
	"google.golang.org/adk/model/gemini"
	"google.golang.org/adk/tool"
	"google.golang.org/adk/tool/geminitool"
	"google.golang.org/genai"
)

func main() {
	ctx := context.Background()

	model, err := gemini.NewModel(ctx, "gemini-3-pro-preview", &genai.ClientConfig{
		APIKey: os.Getenv("GOOGLE_API_KEY"),
	})
	if err != nil {
		log.Fatalf("Failed to create model: %v", err)
	}

	timeAgent, err := llmagent.New(llmagent.Config{
		Name:        "hello_time_agent",
		Model:       model,
		Description: "指定された都市の現在時刻を伝えます。",
		Instruction: "指定された都市の現在時刻を伝えるのに役立つアシスタントです。",
		Tools: []tool.Tool{
			geminitool.GoogleSearch{}
		},
	})
	if err != nil {
		log.Fatalf("Failed to create agent: %v", err)
	}

	config := &launcher.Config{
		AgentLoader: agent.NewSingleLoader(timeAgent),
	}

	l := full.NewLauncher()
	if err = l.Execute(ctx, config, os.Args[1:]); err != nil {
		log.Fatalf("Run failed: %v\n\n%s", err, l.CommandLineSyntax())
	}
}
```

### プロジェクトと依存関係の構成

`go mod`コマンドを使用してプロジェクトモジュールを初期化し、エージェントコードファイルの`import`ステートメントに基づいて必要なパッケージをインストールします。

```console
go mod init my-agent/main
go mod tidy
```

### APIキーを設定する

このプロジェクトはAPIキーを必要とするGemini APIを使用します。まだGemini APIキーをお持ちでない場合は、Google AI Studioの[APIキー](https://aistudio.google.com/app/apikey)ページでキーを作成してください。

ターミナルウィンドウで、APIキーをプロジェクトの`.env`または`env.bat`ファイルに書き込み、環境変数を設定します。

=== "MacOS / Linux"

    ```bash title="更新: my_agent/.env"
    echo 'export GOOGLE_API_KEY="YOUR_API_KEY"' > .env
    ```

=== "Windows"

    ```console title="更新: my_agent/env.bat"
    echo 'set GOOGLE_API_KEY="YOUR_API_KEY"' > env.bat
    ```

??? tip "ADKで他のAIモデルを使用する"
    ADKは多くの生成AIモデルの使用をサポートしています。ADKエージェントで他のモデルを構成する方法の詳細については、[モデルと認証](/adk-docs/ja/agents/models)を参照してください。


## エージェントを実行する

定義した対話型コマンドラインインターフェース、またはADK Goコマンドラインツールが提供するADKウェブユーザーインターフェースを使用して、ADKエージェントを実行できます。これらのオプションの両方で、エージェントをテストして対話できます。

### コマンドラインインターフェースで実行する

次のGoコマンドを使用してエージェントを実行します。

```console title="my_agent/ディレクトリから実行する"
# キーと設定をロードする: source .env または env.bat
go run agent.go
```

![adk-run.png](/adk-docs/ja/assets/adk-run.png)

### ウェブインターフェースで実行する

次のGoコマンドを使用して、ADKウェブインターフェースでエージェントを実行します。

```console title="my_agent/ディレクトリから実行する"
# キーと設定をロードする: source .env または env.bat
go run agent.go web api webui
```

このコマンドは、エージェント用のチャットインターフェースを備えたウェブサーバーを起動します。ウェブインターフェースは(http://localhost:8080)でアクセスできます。左上隅でエージェントを選択し、リクエストを入力します。

![adk-web-dev-ui-chat.png](/adk-docs/ja/assets/adk-web-dev-ui-chat.png)

!!! warning "注意: ADK Web は開発用途限定"

    ADK Web は***本番デプロイでの利用を想定していません***。
    ADK Web は開発とデバッグ用途でのみ使用してください。

## 次へ: エージェントを構築する

ADKがインストールされ、最初のエージェントが実行中になったので、ビルドガイドを使用して独自のエージェントを構築してみてください。

*  [エージェントを構築する](/adk-docs/ja/tutorials/)
