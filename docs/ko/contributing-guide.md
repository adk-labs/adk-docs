에이전트 개발 키트(ADK)에 기여하는 데 관심을 가져주셔서 감사합니다! 저희는 아래에 나열된 핵심 프레임워크, 문서 및 관련 구성 요소에 대한 기여를 환영합니다.

이 가이드는 참여 방법에 대한 정보를 제공합니다.

## 기여 준비하기

### 올바른 리포지토리 선택하기

ADK 프로젝트는 여러 리포지토리로 나뉘어 있습니다. 기여하려는 내용에 맞는 리포지토리를 찾아보세요:

리포지토리 | 설명 | 상세 가이드
--- | --- | ---
[`google/adk-python`](https://github.com/google/adk-python) | 핵심 Python 라이브러리 소스 코드를 포함합니다. | [`CONTRIBUTING.md`](https://github.com/google/adk-python/blob/main/CONTRIBUTING.md)
[`google/adk-python-community`](https://github.com/google/adk-python-community) | 커뮤니티에서 기여한 도구, 통합 및 스크립트를 포함합니다. | [`CONTRIBUTING.md`](https://github.com/google/adk-python-community/blob/main/CONTRIBUTING.md)
[`google/adk-go`](https://github.com/google/adk-go) | 핵심 Go 라이브러리 소스 코드를 포함합니다. | 
[`google/adk-java`](https://github.com/google/adk-java) | 핵심 Java 라이브러리 소스 코드를 포함합니다. | [`CONTRIBUTING.md`](https://github.com/google/adk-java/blob/main/CONTRIBUTING.md)
[`google/adk-docs`](https://github.com/google/adk-docs) | 현재 읽고 계신 문서 사이트의 소스를 포함합니다. | [`CONTRIBUTING.md`](https://github.com/google/adk-docs/blob/main/CONTRIBUTING.md)
[`google/adk-web`](https://github.com/google/adk-web) | `adk web` 개발 UI의 소스를 포함합니다. |

이러한 리포지토리의 루트 디렉토리에는 일반적으로 `CONTRIBUTING.md` 파일이 있으며, 해당 구성 요소에 대한 요구 사항, 테스트, 코드 리뷰 프로세스 등에 대한 더 자세한 정보가 포함되어 있습니다.

### CLA에 서명하기

이 프로젝트에 기여하려면 [기여자 라이선스 계약(Contributor License Agreement, CLA)](https://cla.developers.google.com/about)에 동의해야 합니다. 기여한 내용의 저작권은 기여자(또는 소속 회사)에게 있으며, 이 계약은 프로젝트의 일부로서 귀하의 기여물을 사용하고 재배포할 수 있는 권한을 저희에게 부여하는 것입니다.

만약 귀하 또는 현재 소속된 회사가 이미 Google CLA에 서명했다면(다른 프로젝트를 위한 것이었더라도), 다시 서명할 필요가 없을 수 있습니다.

<https://cla.developers.google.com/>를 방문하여 현재 계약 상태를 확인하거나 새 계약에 서명하세요.

### 커뮤니티 가이드라인 검토하기

이 프로젝트는 [Google의 오픈소스 커뮤니티 가이드라인](https://opensource.google/conduct/)을 따릅니다.

## 논의에 참여하기

질문이 있거나, 아이디어를 공유하고 싶거나, ADK를 어떻게 사용하고 있는지 논의하고 싶으신가요? **[Python](https://github.com/google/adk-python/discussions)** 또는 **[Java](https://github.com/google/adk-java/discussions)** Discussions를 방문해 주세요!

이곳은 다음과 같은 활동을 위한 주요 공간입니다:

* 질문하고 커뮤니티와 관리자로부터 도움받기
* 자신의 프로젝트나 사용 사례 공유하기 (`Show and Tell`)
* 공식적인 이슈를 생성하기 전에 잠재적인 기능이나 개선 사항에 대해 논의하기
* ADK에 대한 일반적인 대화 나누기

## 기여하는 방법

ADK에 기여할 수 있는 몇 가지 방법이 있습니다:

### 이슈 보고하기 { #reporting-issues-bugs-errors }

프레임워크에서 버그를 발견하거나 문서에서 오류를 찾았다면:

* **프레임워크 버그:** [`google/adk-python`](https://github.com/google/adk-python/issues/new) 또는 [`google/adk-java`](https://github.com/google/adk-java/issues/new)에 이슈를 생성하세요.
* **문서 오류:** [`google/adk-docs`에 이슈 생성하기 (버그 템플릿 사용)](https://github.com/google/adk-docs/issues/new?template=bug_report.md)

### 개선 사항 제안하기 { #suggesting-enhancements }

새로운 기능이나 기존 기능 개선에 대한 아이디어가 있으신가요?

* **프레임워크 개선:** [`google/adk-python`](https://github.com/google/adk-python/issues/new) 또는 [`google/adk-java`](https://github.com/google/adk-java/issues/new)에 이슈를 생성하세요.
* **문서 개선:** [`google/adk-docs`에 이슈 생성하기](https://github.com/google/adk-docs/issues/new)

### 문서 개선하기 { #improving-documentation }

오타, 불분명한 설명 또는 누락된 정보를 발견하셨나요? 변경 사항을 직접 제출해 주세요:

* **방법:** 제안하는 개선 사항을 담아 풀 리퀘스트(PR)를 제출하세요.
* **위치:** [`google/adk-docs`에서 풀 리퀘스트 생성하기](https://github.com/google/adk-docs/pulls)

### 코드 작성하기 { #writing-code }

버그를 수정하거나 새로운 기능을 구현하고, 문서에 사용할 코드 샘플을 기여하여 도움을 주세요:

**방법:** 코드 변경 사항을 담아 풀 리퀘스트(PR)를 제출하세요.

* **Python 프레임워크:** [`google/adk-python`에서 풀 리퀘스트 생성하기](https://github.com/google/adk-python/pulls)
* **Java 프레임워크:** [`google/adk-java`에서 풀 리퀘스트 생성하기](https://github.com/google/adk-java/pulls)
* **문서:** [`google/adk-docs`에서 풀 리퀘스트 생성하기](https://github.com/google/adk-docs/pulls)

### 코드 리뷰

* 프로젝트 구성원을 포함한 모든 기여는 리뷰 과정을 거칩니다.

* 저희는 코드 제출 및 리뷰를 위해 GitHub 풀 리퀘스트(PR)를 사용합니다. PR에 변경 사항을 명확하게 설명해 주세요.

## 라이선스

기여함으로써 귀하는 귀하의 기여물이 프로젝트의 [Apache 2.0 라이선스](https://github.com/google/adk-docs/blob/main/LICENSE)에 따라 라이선스가 부여된다는 데 동의하게 됩니다.

## 질문이 있으신가요?

진행이 막히거나 질문이 있으면, 해당 리포지토리의 이슈 트래커에 자유롭게 이슈를 생성해 주세요.