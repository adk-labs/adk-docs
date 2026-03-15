# 2026-03-15 upstream main sync

## 작업 목적

- fork 저장소의 `main`에 `upstream/main` 최신 변경을 반영한다.
- 기준 기간은 **2026-03-12 ~ 2026-03-15** upstream 변경이다.
- 병합 후 영문 원문 변경을 기준으로 ko/ja 번역 반영 작업을 진행한다.

## 병합 결과

- 병합 기준 공통 조상: `90a1ba2a3722b54d615d6a2cad5abede75cd1e01`
- 병합 커밋: `8a03175972de08674faaf302b37b7ecc7b687b2c`
- 병합 메시지: `Merge remote-tracking branch 'upstream/main'`
- 확인한 변경 로그:
  - `upstream-doc-change-log/2026-03-12.md`
  - `upstream-doc-change-log/2026-03-14.md`
  - `upstream-doc-change-log/2026-03-15.md`

## 기간 내 upstream 관련 커밋

- `ba99c0b8` `fix: security improvements in adk-scaffold skill (#1412)`
- `4c11cfd0` `Global Skills Install (#1415)`
- `87019788` `callback tests fix (#1416)`
- `eb110806` `Updating Typescript docs for 0.5.0 release (#1430)`
- `301e9427` `Added the missing java snippets in google-gemini.md (#1421)`
- `3e6e36cd` `Add the missing java snippets to apps/index.md (#1422)`
- `cfaedfd8` `Added a python and a java code snippet for loading a yaml agent. (#1423)`
- `8e0e6b20` `Added the missing java snippets to context/index.md (#1426)`
- `bf1de38a` `Added the missing java snippet in caching.md (#1427)`
- `ca0dd9c3` `chore: update adk java javadocs to 0.9.0 (#1432)`
- `ca9d1ec6` `Added the missing java code snippets. (#1417)`
- `dc173ce3` `Upgrade GitHub Actions to latest versions (#1419)`
- `441fe9a9` `Footer correction: mkdocs.yml (#1434)`

## 번역 대상 영문 문서

- `docs/tutorials/coding-with-ai.md`
- `docs/agents/config.md`
- `docs/agents/models/google-gemini.md`
- `docs/apps/index.md`
- `docs/context/caching.md`
- `docs/context/index.md`
- `docs/sessions/state.md`

## 비번역 범위

- `skills/adk-scaffold/SKILL.md`
- `tools/skills/README.md`
- 자동 생성 API reference HTML 및 workflow 파일

## 다음 단계

1. 소규모/중간 규모 문서부터 ko/ja 번역 동기화
2. 컨텍스트/세션 문서를 별도 배치로 정리
3. 각 배치별 `knowledge` 기록, 검증, 커밋, 푸시 수행
