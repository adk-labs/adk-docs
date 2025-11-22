# ADK용 Go 빠른 시작

이 가이드는 ADK(Agent Development Kit) for Go를 사용하여 시작하는 방법을 보여줍니다. 시작하기 전에 다음이 설치되어 있는지 확인하십시오.

*   Go 1.24.4 이상
*   ADK Go v0.2.0 이상

## 에이전트 프로젝트 생성

다음 파일 및 디렉토리 구조로 에이전트 프로젝트를 생성합니다.

```none
my_agent/
    agent.go    # 메인 에이전트 코드
    .env        # API 키 또는 프로젝트 ID
```

??? tip "명령줄을 사용하여 이 프로젝트 구조 생성"

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

### 에이전트 코드 정의

내장된 [Google 검색 도구](/adk-docs/ko/tools/built-in-tools/#google-search)를 사용하는 기본 에이전트 코드를 생성합니다. 프로젝트 디렉토리의 `my_agent/agent.go` 파일에 다음 코드를 추가합니다.

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
		Description: "지정된 도시의 현재 시간을 알려줍니다.",
		Instruction: "지정된 도시의 현재 시간을 알려주는 유용한 도우미입니다.",
		Tools: []tool.Tool{
			geminitool.GoogleSearch{},
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

### 프로젝트 및 종속성 구성

`go mod` 명령을 사용하여 프로젝트 모듈을 초기화하고 에이전트 코드 파일의 `import` 문에 따라 필요한 패키지를 설치합니다.

```console
go mod init my-agent/main
go mod tidy
```

### API 키 설정

이 프로젝트는 API 키가 필요한 Gemini API를 사용합니다. Gemini API 키가 아직 없는 경우 Google AI Studio의 [API 키](https://aistudio.google.com/app/apikey) 페이지에서 키를 생성합니다.

터미널 창에서 프로젝트의 `.env` 또는 `env.bat` 파일에 API 키를 작성하여 환경 변수를 설정합니다.

=== "MacOS / Linux"

    ```bash title="업데이트: my_agent/.env"
    echo 'export GOOGLE_API_KEY="YOUR_API_KEY"' > .env
    ```

=== "Windows"

    ```console title="업데이트: my_agent/env.bat"
    echo 'set GOOGLE_API_KEY="YOUR_API_KEY"' > env.bat
    ```

??? tip "ADK에서 다른 AI 모델 사용"
    ADK는 다양한 생성형 AI 모델 사용을 지원합니다. ADK 에이전트에서 다른 모델을 구성하는 방법에 대한 자세한 내용은 [모델 및 인증](/adk-docs/ko/agents/models)을 참조하세요.


## 에이전트 실행

정의한 대화형 명령줄 인터페이스 또는 ADK Go 명령줄 도구에서 제공하는 ADK 웹 사용자 인터페이스를 사용하여 ADK 에이전트를 실행할 수 있습니다. 이 두 가지 옵션을 통해 에이전트를 테스트하고 상호 작용할 수 있습니다.

### 명령줄 인터페이스로 실행

다음 Go 명령을 사용하여 에이전트를 실행합니다.

```console title="다음에서 실행: my_agent/ 디렉토리"
# 키 및 설정 로드: source .env 또는 env.bat
go run agent.go
```

![adk-run.png](/adk-docs/ko/assets/adk-run.png)

### 웹 인터페이스로 실행

다음 Go 명령을 사용하여 ADK 웹 인터페이스로 에이전트를 실행합니다.

```console title="다음에서 실행: my_agent/ 디렉토리"
# 키 및 설정 로드: source .env 또는 env.bat
go run agent.go web api webui
```

이 명령은 에이전트용 채팅 인터페이스가 있는 웹 서버를 시작합니다. 웹 인터페이스는 (http://localhost:8080)에서 액세스할 수 있습니다. 왼쪽 상단 모서리에서 에이전트를 선택하고 요청을 입력합니다.

![adk-web-dev-ui-chat.png](/adk-docs/ko/assets/adk-web-dev-ui-chat.png)

## 다음: 에이전트 빌드

ADK가 설치되었고 첫 번째 에이전트가 실행 중이므로 이제 빌드 가이드를 사용하여 자신만의 에이전트를 빌드해 보세요.

*  [에이전트 빌드](/adk-docs/ko/tutorials/)