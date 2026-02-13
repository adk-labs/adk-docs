---
catalog_title: Daytona
catalog_description: 보안 샌드박스에서 코드 실행, 셸 명령 실행, 파일 관리를 수행합니다
catalog_icon: /adk-docs/integrations/assets/daytona.png
catalog_tags: ["code"]
---

# ADK용 Daytona 플러그인

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Daytona ADK plugin](https://github.com/daytonaio/daytona-adk-plugin)은 ADK
에이전트를 [Daytona](https://www.daytona.io/) 샌드박스와 연결합니다. 이 통합을 통해
에이전트는 격리된 환경에서 코드를 실행하고, 셸 명령을 실행하며, 파일을 관리할 수 있어
AI가 생성한 코드를 안전하게 실행할 수 있습니다.

## 사용 사례

- **안전한 코드 실행**: 로컬 환경 위험 없이 격리된 샌드박스에서
  Python, JavaScript, TypeScript 코드를 실행합니다.

- **셸 명령 자동화**: 빌드 작업, 설치, 시스템 작업을 위해
  타임아웃과 작업 디렉터리를 설정하여 셸 명령을 실행합니다.

- **파일 관리**: 스크립트와 데이터셋을 샌드박스에 업로드하고,
  생성된 출력 및 결과 파일을 가져옵니다.

## 사전 준비 사항

- [Daytona](https://www.daytona.io/) 계정
- Daytona API 키

## 설치

```bash
pip install daytona-adk
```

## 에이전트와 함께 사용

```python
from daytona_adk import DaytonaPlugin
from google.adk.agents import Agent

plugin = DaytonaPlugin(
  api_key="your-daytona-api-key" # Or set DAYTONA_API_KEY environment variable
)

root_agent = Agent(
    model="gemini-2.5-pro",
    name="sandbox_agent",
    instruction="Help users execute code and commands in a secure sandbox",
    tools=plugin.get_tools(),
)
```

## 사용 가능한 도구

Tool | Description
---- | -----------
`execute_code_in_daytona` | Python, JavaScript, TypeScript 코드 실행
`execute_command_in_daytona` | 셸 명령 실행
`upload_file_to_daytona` | 스크립트/데이터 파일을 샌드박스에 업로드
`read_file_from_daytona` | 스크립트 출력/생성 파일 읽기
`start_long_running_command_daytona` | 백그라운드 프로세스(서버, watcher) 시작

## 더 알아보기

안전한 샌드박스에서 코드를 작성, 테스트, 검증하는 코드 생성 에이전트 구축 가이드는
[이 가이드](https://www.daytona.io/docs/en/google-adk-code-generator)를 확인하세요.

## 추가 리소스

- [Code Generator Agent Guide](https://www.daytona.io/docs/en/google-adk-code-generator)
- [Daytona ADK on PyPI](https://pypi.org/project/daytona-adk/)
- [Daytona ADK on GitHub](https://github.com/daytonaio/daytona-adk-plugin)
- [Daytona Documentation](https://www.daytona.io/docs)
