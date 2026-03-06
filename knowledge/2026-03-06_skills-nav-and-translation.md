# 2026-03-06 Skills nav and translation

## 배경

- `mkdocs` 검토 중 ko/ja 사이트에서 `Skills for Agents` 메뉴가 보이지 않는 문제를 확인했다.
- 원인 분리를 위해 로컬 영문 문서와 `upstream/main`을 다시 확인했다.

## 확인 결과

- 영문 원문은 로컬과 `upstream/main`에 모두 존재했다.
  - `docs/skills/index.md`
  - `upstream/main:docs/skills/index.md`
- `upstream/main`의 영문 nav에도 이미 `skills/index.md`가 등록되어 있었다.
  - `upstream/main:mkdocs.yml`
- 누락 원인은 ko/ja 번역 파일 부재와 ko/ja nav 미반영이었다.
  - 신규 번역 파일 추가:
    - `docs/ko/skills/index.md`
    - `docs/ja/skills/index.md`
  - nav 반영:
    - ko `에이전트용 스킬`
    - ja `エージェント向けスキル`

## 작업 내용

- 영문 `docs/skills/index.md` 기준으로 ko/ja 문서를 전체 번역했다.
- 코드 블록, 링크, 앵커(`inline-skills`, `known-limitations`)와 구조를 유지했다.
- `mkdocs.yml`의 ko/ja nav에 `skills/index.md`를 추가했다.
- `mkdocs.yml`의 영문 nav에서 `Custom Tools` 들여쓰기가 잘못 밀린 부분을 함께 복구해 nav 계층이 깨지지 않도록 정리했다.
- ja 문서의 language support tag와 예제 admonition 제목을 기존 일본어 문서 스타일에 맞춰 정리했다.

## 검증

- `git grep -n "Skills for ADK agents\\|skills/index.md" upstream/main -- mkdocs.yml docs`
- `rg -n "skills/index.md|에이전트용 스킬|エージェント向けスキル|Skills for Agents" mkdocs.yml`
- `git diff --check -- mkdocs.yml docs/ko/skills/index.md docs/ja/skills/index.md`

## 결과

- 영어 원문에 존재하는 Skills 문서가 ko/ja에도 반영되었다.
- ko/ja 사이트 nav에서 Skills 메뉴가 노출되도록 구성되었다.
