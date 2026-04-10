에이전트 개발 키트(ADK)에 기여하고자 해 주셔서 감사합니다! 아래에 나열된 핵심 프레임워크, 문서 및 관련 구성 요소에 대한 기여를 환영합니다.

이 가이드는 참여 방법을 안내합니다.

## 커뮤니티 참여하기

* ADK에 대해 토론하거나 질문을 하거나 에이전트 전반에 대해 이야기하고 싶다면 Reddit의 **[r/agentdevelopmentkit](https://www.reddit.com/r/agentdevelopmentkit/)**를 방문하세요.
* 월간 커뮤니티 콜 업데이트를 받고 싶다면 **[ADK Community Google Group](https://groups.google.com/g/adk-community)**에 참여하세요.
* 버그를 신고하거나 ADK 프레임워크에 기여하고 싶다면 아래 섹션에서 적절한 저장소를 찾는 방법과 시작 방법을 확인하세요.

## 기여 준비하기

### 올바른 리포지토리 선택하기

ADK 프로젝트는 여러 리포지토리로 나뉘어 있습니다. 기여할 대상에 맞는 리포지토리를 찾아보세요.

리포지토리 | 설명 | 상세 가이드
--- | --- | ---
[`google/adk-python`](https://github.com/google/adk-python) | 핵심 Python 라이브러리 소스 코드를 포함합니다. | [`CONTRIBUTING.md`](https://github.com/google/adk-python/blob/main/CONTRIBUTING.md)
[`google/adk-python-community`](https://github.com/google/adk-python-community) | 커뮤니티가 기여한 도구, 통합, 스크립트를 포함합니다. | [`CONTRIBUTING.md`](https://github.com/google/adk-python-community/blob/main/CONTRIBUTING.md)
[`google/adk-js`](https://github.com/google/adk-js) | 핵심 JavaScript 라이브러리 소스 코드를 포함합니다. | [`CONTRIBUTING.md`](https://github.com/google/adk-js/blob/main/CONTRIBUTING.md)
[`google/adk-go`](https://github.com/google/adk-go) | 핵심 Go 라이브러리 소스 코드를 포함합니다. | [`CONTRIBUTING.md`](https://github.com/google/adk-go/blob/main/CONTRIBUTING.md)
[`google/adk-java`](https://github.com/google/adk-java) | 핵심 Java 라이브러리 소스 코드를 포함합니다. | [`CONTRIBUTING.md`](https://github.com/google/adk-java/blob/main/CONTRIBUTING.md)
[`google/adk-docs`](https://github.com/google/adk-docs) | 현재 보고 계신 문서 사이트의 소스를 포함합니다. | [`CONTRIBUTING.md`](https://github.com/google/adk-docs/blob/main/CONTRIBUTING.md)
[`google/adk-samples`](https://github.com/google/adk-samples) | ADK 샘플 에이전트를 포함합니다. | [`CONTRIBUTING.md`](https://github.com/google/adk-samples/blob/main/CONTRIBUTING.md)
[`google/adk-web`](https://github.com/google/adk-web) | `adk web` 개발 UI의 소스를 포함합니다. |

이러한 리포지토리에는 일반적으로 루트에 `CONTRIBUTING.md` 파일이 있으며, 해당 구성 요소의 요구 사항, 테스트, 코드 리뷰 절차 등에 대한 자세한 정보가 담겨 있습니다.

### CLA에 서명하기

이 프로젝트에 대한 기여에는 [기여자 라이선스 계약(Contributor License Agreement, CLA)](https://cla.developers.google.com/about) 이 필요합니다. 귀하(또는 귀하의 고용주)는 기여물의 저작권을 보유하며, 이 계약은 프로젝트의 일부로서 귀하의 기여를 사용하고 재배포할 수 있는 권한을 저희에게 부여합니다.

귀하 또는 현재 고용주가 이미 Google CLA에 서명했다면(다른 프로젝트를 위한 것이었더라도), 다시 서명할 필요가 없을 수 있습니다.

<https://cla.developers.google.com/>에서 현재 계약 상태를 확인하거나 새 계약에 서명하세요.

### 커뮤니티 가이드라인 검토하기

이 프로젝트는 [Google의 오픈소스 커뮤니티 가이드라인](https://opensource.google/conduct/)을 따릅니다.

## 기여 방법

ADK에 기여하는 방법은 여러 가지가 있습니다.

### 이슈 보고하기 { #reporting-issues-bugs-errors }

프레임워크의 버그나 문서의 오류를 발견했다면:

* **프레임워크 버그:** [`google/adk-python`](https://github.com/google/adk-python/issues/new), [`google/adk-js`](https://github.com/google/adk-js/issues/new), [`google/adk-go`](https://github.com/google/adk-go/issues/new), 또는 [`google/adk-java`](https://github.com/google/adk-java/issues/new)에 이슈를 열어 주세요.
* **문서 오류:** [문서 버그 템플릿을 사용해 `google/adk-docs`에 이슈를 여세요](https://github.com/google/adk-docs/issues/new?template=bug_report.md)

### 개선 사항 제안하기 { #suggesting-enhancements }

새 기능이나 기존 기능 개선 아이디어가 있나요?

* **프레임워크 개선:** [`google/adk-python`](https://github.com/google/adk-python/issues/new), [`google/adk-js`](https://github.com/google/adk-js/issues/new), [`google/adk-go`](https://github.com/google/adk-go/issues/new), 또는 [`google/adk-java`](https://github.com/google/adk-java/issues/new)에 이슈를 열어 주세요.
* **문서 개선:** [`google/adk-docs`](https://github.com/google/adk-docs/issues/new)에 이슈를 여세요.

### 문서 개선하기 { #improving-documentation }

오타, 불명확한 설명, 누락된 정보를 발견했다면 변경 사항을 직접 제출하세요.

* **방법:** 제안하는 개선 사항이 담긴 Pull Request(PR)를 제출하세요.
* **위치:** [`google/adk-docs`에서 Pull Request 만들기](https://github.com/google/adk-docs/pulls)

### 코드 작성하기 { #writing-code }

버그를 수정하거나, 새 기능을 구현하거나, 문서용 코드 샘플을 기여하는 데 도움을 주세요.

**방법:** 코드 변경 사항이 담긴 Pull Request(PR)를 제출하세요.

* **Python 프레임워크:** [`google/adk-python`에서 Pull Request 만들기](https://github.com/google/adk-python/pulls)
* **TypeScript 프레임워크:** [`google/adk-js`에서 Pull Request 만들기](https://github.com/google/adk-js/pulls)
* **Go 프레임워크:** [`google/adk-go`에서 Pull Request 만들기](https://github.com/google/adk-go/pulls)
* **Java 프레임워크:** [`google/adk-java`에서 Pull Request 만들기](https://github.com/google/adk-java/pulls)
* **문서:** [`google/adk-docs`에서 Pull Request 만들기](https://github.com/google/adk-docs/pulls)

### 코드 리뷰

* 프로젝트 구성원을 포함한 모든 기여는 리뷰 과정을 거칩니다.

* 코드 제출과 리뷰에는 GitHub Pull Request(PR)를 사용합니다. PR에 변경 사항을 명확하게 설명해 주세요.

## 라이선스

기여함으로써 귀하는 귀하의 기여물이 프로젝트의 [Apache 2.0 라이선스](https://github.com/google/adk-docs/blob/main/LICENSE) 하에 라이선스되는 데 동의하게 됩니다.

## 질문이 있으신가요?

막히거나 질문이 있으면 관련 리포지토리의 이슈 트래커에 자유롭게 이슈를 열어 주세요.
