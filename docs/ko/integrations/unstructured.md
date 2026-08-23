---
catalog_title: Unstructured
catalog_description: PDF, Office 문서, 이미지 및 40가지 이상의 파일 형식을 정형화되고 AI가 바로 사용할 수 있는 데이터로 파싱합니다.
catalog_icon: /integrations/assets/unstructured.png
catalog_tags: ["mcp"]
---

# ADK용 Unstructured Transform MCP 도구

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span>
</div>

[Unstructured Transform MCP 서버](https://docs.unstructured.io/transform/overview)는 ADK 에이전트를 원시 파일을 구조화된 AI 지원 데이터로 변환하는 문서 처리 플랫폼인 [Unstructured](https://unstructured.io)에 연결합니다. 이 통합을 통해 에이전트는 자연어를 사용하여 PDF, Office 문서, 이메일, 이미지 및 스캔된 파일(총 40가지 이상의 [지원되는 파일 형식](https://docs.unstructured.io/transform/supported-file-types))을 분할, 강화, 청크 및 임베딩 처리된 출력물로 파싱할 수 있는 기능을 제공합니다. Transform은 호스팅형 원격 MCP 서버이므로 로컬에 설치하거나 실행할 필요가 없습니다.

## 사용 사례

- **RAG 수집(Ingestion)**: 이종 문서 모음을 벡터 저장소 및 검색 파이프라인을 위해 깔끔하게 정리되고 청크 처리가 완료되었으며 임베딩 준비가 된 출력물로 파싱합니다.
- **문서 Q&A 에이전트**: 에이전트가 필요에 따라 계약서, 보고서 또는 논문을 가져와 파싱한 다음, 파싱된 콘텐츠를 기반으로 질문에 답변하도록 합니다.
- **형식 정규화**: 혼합된 입력물(스캔된 PDF, 스프레드시트, 프레젠테이션, 이메일 스레드)을 하나의 일관된 구조화된 표현으로 변환합니다.
- **에이전트 런타임 시 OCR**: 더 큰 에이전트 워크플로 내의 한 단계로서 이미지와 스캔된 문서에서 텍스트와 구조를 추출합니다.
- **정형 데이터 추출**: 양식, 청구서 및 계약서에서 사용자가 제공한 스키마 또는 서버가 문서에서 작성한 스키마와 일치하는 JSON 형식으로 명명된 필드를 추출합니다.

## 사전 준비 사항

- [Unstructured 계정](https://transform.unstructured.io) 및 API 키. [API 키 받기](https://docs.unstructured.io/transform/code#get-your-unstructured-api-key-and-url)를 참고하세요.
- 에이전트 모델용 [Gemini API 키](https://aistudio.google.com/apikey).
- Python 3.10 이상.

## 설치

`mcp` 엑스트라가 포함된 ADK를 설치합니다. 이 엑스트라는 필수 사양이며, 이것이 없으면 ADK의 MCP 클래스를 가져올 수 없습니다.

```bash
pip install "google-adk[mcp]"
```

## 에이전트와 함께 사용

환경 변수로 API 키를 설정합니다.

```bash
export UNSTRUCTURED_API_KEY="<your-unstructured-api-key>"
export GOOGLE_API_KEY="<your-gemini-api-key>"
export GOOGLE_GENAI_USE_VERTEXAI=FALSE
```

서버는 초기 핸드셰이크를 포함하여 모든 요청에서 Unstructured API 키를 Bearer 토큰으로 인증합니다. 파싱 작업은 비동기식으로 실행되므로 `wait_seconds` 헬퍼 함수를 통해 에이전트가 상태 확인 사이에 일시 중지할 수 있도록 합니다.

=== "Python"

    === "원격 MCP 서버"

        ```python
        import asyncio
        import os

        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams


        async def wait_seconds(seconds: int) -> dict:
            """다음 상태 확인을 진행하기 전에 대기합니다. 별도의 지시가 없는 한 30초 동안 대기합니다.

            Args:
                seconds: 대기할 시간(초).

            Returns:
                대기했음을 확인하는 dict.
            """
            seconds = max(1, min(int(seconds), 120))
            await asyncio.sleep(seconds)
            return {"waited_seconds": seconds}


        root_agent = Agent(
            model="gemini-flash-latest",
            name="transform_agent",
            instruction=(
                "You parse documents with the Unstructured Transform MCP server. "
                "Pass public https:// file URLs straight to start_transform_job. It "
                "returns a job_id; poll with check_job_status, calling "
                "wait_seconds(30) between checks (jobs take 30 seconds to a few "
                "minutes). When the job completes, call get_job_results and "
                "report the parsed content back to the user. start_transform_job "
                "accepts an optional stages config; it auto-selects a parse "
                "strategy by default, but if the output looks low quality "
                "(garbled text or lost tables), re-run the file with a hi_res "
                "partition strategy for a cleaner result. If the user wants "
                "specific fields rather than the whole document, extract "
                "instead of just parsing. The extraction tools read the element "
                "JSON a parse produces, so parse the file first and keep the "
                "output_ref that get_job_results returns for it. Call "
                "suggest_extraction_schema_for_file with that output_ref when "
                "you need a schema, then start_extraction_job with "
                "element_json_refs set to the output_refs and schema_to_extract "
                "set to a JSON Schema passed as a JSON string. Poll and read an "
                "extraction job with check_job_status and get_job_results like "
                "any other job; its results come back inline, wrapped with the "
                "source filename, so report that filename with each object. If "
                "asked to parse a local file, explain that this requires the "
                "upload helper from the Unstructured ADK guide."
            ),
            tools=[
                wait_seconds,
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://mcp.transform.unstructured.io",  # root URL; do not append /mcp
                        headers={
                            "Authorization": f"Bearer {os.environ['UNSTRUCTURED_API_KEY']}",
                        },
                        timeout=30.0,  # ADK's 5s default is too short for a remote handshake
                        sse_read_timeout=300.0,
                    ),
                    tool_filter=[
                        "request_file_upload_url",
                        "start_transform_job",
                        "suggest_extraction_schema_for_file",
                        "start_extraction_job",
                        "check_job_status",
                        "get_job_results",
                    ],
                )
            ],
        )
        ```

!!! note

    문서 변환은 비동기식으로 진행됩니다. `start_transform_job`이 작업을 시작하면 에이전트가 `check_job_status`를 폴링하고, 완료되면 `get_job_results`가 결과물에 대한 사전 서명된 다운로드 URL을 반환합니다. 모델 속도 제한(rate limit)을 불필요하게 초과하지 않도록 위의 예와 같이 상태 확인 사이에 일시 정지하도록 에이전트에 지시해야 합니다.

    정형 데이터 추출은 각 파일에 대해 `get_job_results`가 반환하는 `output_ref`로 식별되는 요소 JSON에서 실행되는 두 번째 비동기 작업입니다. 따라서 파싱 후 추출하는 프롬프트는 두 번의 폴링 루프를 실행하므로 추가 시간과 모델 단계를 고려하세요.

    **로컬** 파일을 파싱하려면, 에이전트에 `request_file_upload_url`에 의해 반환된 사전 서명된 URL로 파일 바이트를 HTTP `PUT`하는 일반 함수 도구도 필요합니다 (이 업로드는 MCP 호출이 아니며 `Authorization` 헤더를 보내서는 안 됩니다). 업로드 및 대기 헬퍼가 포함된 완전한 에이전트는 [Unstructured Transform ADK 가이드](https://docs.unstructured.io/transform/install/google-adk)에서 확인할 수 있습니다.

## 사용 가능한 도구

도구 | 설명
---- | -----------
`request_file_upload_url` | 로컬 파일에 대해 사전 서명된 업로드 URL 및 파일 참조를 반환합니다.
`start_transform_job` | 업로드된 파일 또는 공개 HTTP(S) URL에 대한 파싱 작업을 시작하고 `job_id`를 반환합니다.
`suggest_extraction_schema_for_file` | 아직 스키마가 없는 경우 파싱된 하나의 문서 요소 JSON에서 JSON 스키마 초안을 작성합니다.
`start_extraction_job` | JSON 스키마에 대해 파싱된 요소 JSON에 대한 정형 데이터 추출 작업을 시작하고 `job_id`를 반환합니다.
`check_job_status` | 작업이 `SCHEDULED`, `IN_PROGRESS` 또는 `COMPLETED` 상태인지 보고합니다. 파싱 및 추출 작업 모두에 사용됩니다.
`get_job_results` | 완료된 작업의 출력을 반환합니다 (파싱 작업의 경우 사전 서명된 다운로드 URL, 추출 작업의 경우 인라인 추출 데이터).

## 리소스

- [Unstructured Transform 문서](https://docs.unstructured.io/transform/overview)
- [Unstructured Transform용 ADK 설치 가이드](https://docs.unstructured.io/transform/install/google-adk)
- [지원되는 파일 형식](https://docs.unstructured.io/transform/supported-file-types)
