---
catalog_title: Sprites
catalog_description: 에이전트 코드 실행을 위한 체크포인트 및 복구 기능이 있는 영구적이고 상태 유지가 가능한 Linux 샌드박스
catalog_icon: /integrations/assets/sprites.png
catalog_tags: ["code"]
---

# ADK용 Sprites 플러그인

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span>
</div>

[Sprites ADK 플러그인](https://github.com/superfly/sprites-adk)은 ADK 에이전트를 [Fly.io](https://fly.io)에서 제공하는 영구적이고 상태 유지가 가능한 Linux 샌드박스인 [Sprites](https://sprites.dev)에 연결합니다. 일시적인 샌드박스와 달리 Sprite는 세션 간에 파일 시스템, 설치된 패키지, 실행 중인 프로세스를 그대로 유지하며 전체 상태를 **체크포인트 생성 및 복구(checkpoint and restore)**할 수 있습니다. 따라서 에이전트는 위험한 변경 전에 환경을 스냅샷하고 문제가 발생하면 롤백할 수 있습니다.

## 사용 사례

- **영구적인 개발 환경(Persistent development environments)**: 세션 간에 이름이 지정된 Sprite가 재사용됩니다. 이전 실행의 패키지와 파일이 그대로 남아 있으므로 장기 프로젝트가 매번 처음부터 다시 환경을 빌드할 필요가 없습니다.

- **안전한 코드 실행(Secure code execution)**: 에이전트가 생성한 Python, JavaScript 또는 bash를 호스트 머신 대신 격리된 마이크로VM(microVM)에서 실행합니다.

- **안전한 실험(Safe experimentation)**: 패키지 업그레이드, 마이그레이션 또는 대량 편집 전에 전체 환경의 체크포인트를 생성하고 변경으로 인해 오류가 발생할 경우 체크포인트 상태로 다시 복구합니다.

- **파일 워크플로(File workflows)**: 스크립트와 데이터를 샌드박스에 작성하고 실행한 다음 결과를 다시 읽어옵니다.

## 사전 준비 사항

- [Sprites](https://sprites.dev) 계정
- Sprites API 토큰 (`SPRITES_TOKEN` 환경 변수로 설정)

## 설치

```bash
pip install sprites-adk
```

## 에이전트와 함께 사용

```python
from sprites_adk import SpritesPlugin
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner

# SpritesPlugin()은 실행할 때마다 새로운 샌드박스를 제공합니다.
# SpritesPlugin(sprite_name="my-project")는 세션 간에 하나의 영구 환경을 재사용합니다.
plugin = SpritesPlugin(
  # token="your-sprites-token"  # 또는 SPRITES_TOKEN 환경 변수를 설정합니다.
)

root_agent = Agent(
    model="gemini-flash-latest",
    name="sandbox_agent",
    instruction="Run code and commands in the Sprite sandbox, not locally.",
    tools=plugin.get_tools(),
)

# 러너에 플러그인을 등록하여 수명 주기 콜백 및 정리가 실행되도록 합니다.
runner = InMemoryRunner(agent=root_agent, plugins=[plugin])
```

## 사용 가능한 도구

도구 | 설명
---- | -----------
`execute_command_in_sprite` | 샌드박스에서 셸 명령 실행
`execute_code_in_sprite` | Python, JavaScript 또는 bash 코드 실행
`write_file_to_sprite` | 샌드박스에 텍스트 파일 쓰기
`read_file_from_sprite` | 샌드박스에서 텍스트 파일 읽기
`create_sprite_checkpoint` | 전체 환경(파일 시스템, 패키지, 프로세스) 스냅샷 생성
`list_sprite_checkpoints` | 사용 가능한 체크포인트 목록 조회
`restore_sprite_checkpoint` | 체크포인트로 롤백 (파괴적인 작업이므로 확인 필요)

## 추가 리소스

- [PyPI의 sprites-adk](https://pypi.org/project/sprites-adk/)
- [GitHub의 sprites-adk](https://github.com/superfly/sprites-adk)
- [Sprites 문서](https://docs.sprites.dev)
