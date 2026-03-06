# 2026-03-06 mkdocs nav review

## 점검 범위

- `mkdocs.yml`의 영어/한국어/일본어 `nav`
- 최근 추가/수정 문서의 메뉴 노출 경로
- 메뉴 비노출 원인이 될 수 있는 잘못된 링크 문자열

## 확인 결과

- 영어 `Reference > API Reference > Go ADK` 항목에 잘못된 문자열이 포함되어 있었음
  - 기존: `https://pkg.go.dev/google.golang.org/adk" target="_blank`
  - 조치: 정상 URL `https://pkg.go.dev/google.golang.org/adk` 로 수정
- ko/ja `API Reference` 메뉴는 존재하지 않는 locale 경로를 가리키고 있었음
  - 예: `docs/ko/api-reference/python/index.html`, `docs/ja/api-reference/python/index.html`
  - 조치: 공용 정적 HTML 경로 `/adk-docs/api-reference/...` 로 수정

## 수정 내용

- `mkdocs.yml`
  - 영어 `Go ADK` 링크 문자열 오류 수정
  - ko `Python/Typescript/Java/CLI/Agent Config` API Reference 링크를 공용 절대 경로로 수정
  - ja `Python/Typescript/Java/CLI/Agent Config` API Reference 링크를 공용 절대 경로로 수정

## 추가 관찰 사항

- 영어 nav에는 `Skills for Agents`가 존재하지만, `docs/ko/skills/index.md`, `docs/ja/skills/index.md`는 아직 없음
- 따라서 ko/ja 메뉴에서 동일 섹션이 보이지 않는 것은 nav 정의 누락이라기보다 번역 문서 자체 부재에 따른 상태임

## 검증

- `git diff --check -- mkdocs.yml` 통과
- `mkdocs.yml`에서 `target="_blank`가 섞인 비정상 URL 문자열 제거 확인
- ko/ja API Reference 링크가 더 이상 locale 내부에 없는 HTML 파일을 직접 가리키지 않도록 정리
