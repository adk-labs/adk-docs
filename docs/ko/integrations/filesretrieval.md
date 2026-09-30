---
catalog_title: Files Retrieval Tool
catalog_description: 벡터 유사도 검색을 사용하여 로컬 문서를 색인화하고 검색합니다
catalog_icon: /integrations/assets/filesretrieval.png
catalog_tags: ["google", "data"]
---

# ADK용 Files Retrieval 도구

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span>
</div>

`FilesRetrieval` 도구를 사용하면 ADK 에이전트가 검색 증강 생성(RAG)을 사용하여 로컬 문서를 색인화(index)하고 쿼리할 수 있습니다. Google의 Gemini 임베딩 모델을 사용하여 지정한 디렉터리에 대해 LlamaIndex `VectorStoreIndex`를 빌드합니다. 그러면 에이전트가 로컬 텍스트 파일, Markdown 문서 및 소스 파일에서 관련 발췌본을 검색하여 프로젝트별 컨텍스트를 기반으로 답변을 제공할 수 있습니다.

## 사용 사례

- **코드베이스 및 문서 검색**: 로컬 저장소에서 관련 함수, 설계 노트 및 문서를 검색하여 기술적인 질문에 답변합니다.
- **로컬 지식 기반 그라운딩(Grounding)**: 호스팅된 문서 저장소에 먼저 문서를 로드할 필요 없이 자체 파일 시스템에서 직접 내부 마크다운 파일, 기술 사양 및 가이드를 색인화합니다. 문서 콘텐츠는 색인을 위해 구성된 임베딩 모델로 전송되므로, 민감한 자료를 색인화하기 전에 Google AI Studio 또는 Agent Platform의 데이터 처리 약관을 검토하세요.
- **컨텍스트 강화 지원**: 보고서, 로그 또는 텍스트 파일에서 관련 도메인별 데이터를 검색하여 검증된 원본 자료를 바탕으로 에이전트 응답을 근거화합니다.

## 사전 준비 사항

`FilesRetrieval` 도구는 ADK가 기본적으로 설치하지 않는 LlamaIndex로 문서를 색인화합니다. 이를 제공하는 엑스트라 패키지를 설치하세요.

```bash
pip install "google-adk[extensions]"
```

그런 다음 Google AI Studio 또는 Agent Platform에 대한 자격 증명을 구성합니다.

=== "Google AI Studio"

    [Google AI Studio](https://aistudio.google.com/)에서 API 키를 생성하고 환경 변수를 설정합니다.

    ```bash
    export GOOGLE_API_KEY="your-api-key"
    ```

=== "Agent Platform"

    Google Cloud 자격 증명으로 Agent Platform 액세스를 구성합니다.

    ```bash
    export GOOGLE_GENAI_USE_ENTERPRISE=TRUE
    export GOOGLE_CLOUD_PROJECT="your-project-id"
    export GOOGLE_CLOUD_LOCATION="<global | us | eu>"
    ```

!!! note
    
    프로덕션 환경에서는 `embedding_model=GoogleGenAIEmbedding(model_name="gemini-embedding-2", embed_batch_size=1)`을 사용하여 GA 모델을 명시적으로 전달하세요. 자세한 내용은 [Gemini Embedding](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/embedding-2)을 참조하세요. ADK 에이전트를 Google Cloud 리소스 및 서비스에 연결하는 방법에 대한 자세한 내용은 Google Cloud [연결 가이드](/ko/get-started/google-cloud/)를 참조하세요.

## 에이전트와 함께 사용

이 예제에서는 로컬 데이터 디렉터리에 대해 `FilesRetrieval`을 구성하고 이를 ADK 에이전트에 연결합니다. 실행하기 전에 에이전트 모듈 옆에 `data/` 디렉터리를 생성하고 색인화할 `.txt` 또는 `.md` 파일을 추가하세요. `FilesRetrieval`은 생성될 때 전체 디렉터리를 로드하고 임베딩하므로 디렉터리가 이미 존재해야 하며, 에이전트 모듈을 가져올 때마다 콘텐츠가 다시 색인화됩니다.

```python
import os
from google.adk.agents import Agent
from google.adk.tools.retrieval.files_retrieval import FilesRetrieval

# 소스 문서가 포함된 디렉터리 경로
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# FilesRetrieval 도구 초기화
files_retrieval = FilesRetrieval(
    name="search_documents",
    description=(
        "Search through local documentation files to find relevant"
        " information. Use this tool when the user asks questions about"
        " architecture, project structure, or tools."
    ),
    input_dir=DATA_DIR,
)

# 검색 도구가 장착된 에이전트 생성
root_agent = Agent(
    model="gemini-flash-latest",
    name="files_retrieval_agent",
    instruction=(
        "You are a helpful assistant that answers questions based on local"
        " documentation files. Always use the search_documents tool to retrieve"
        " relevant context before generating your answer."
    ),
    tools=[files_retrieval],
)
```

## 사용 가능한 도구

`FilesRetrieval` 클래스는 도구입니다. `tools=[...]`로 연결되면 에이전트는 단일 `query` 문자열 매개변수를 취하는 하나의 함수를 확인합니다.

도구 | 설명
---- | -----------
`search_documents` | 색인화된 디렉터리의 문서에 대해 시맨틱 벡터 검색을 수행하고 주어진 자연어 쿼리에 대해 가장 관련성 높은 콘텐츠 청크를 반환합니다. `name` 매개변수로 이름을 바꿀 수 있습니다.

## 구성

`FilesRetrieval` 생성자는 다음 매개변수를 허용합니다.

매개변수 | 타입 | 필수 여부 | 기본값 | 설명
--------- | ---- | -------- | ------- | -----------
`name` | `str` | **예** | — | 함수 호출을 위해 모델에서 사용하는 도구의 고유 식별자입니다.
`description` | `str` | **예** | — | 에이전트가 검색 도구를 언제 어떻게 호출해야 하는지에 대한 설명입니다.
`input_dir` | `str` | **예** | — | 로드하고 색인화할 문서가 포함된 로컬 파일 시스템 디렉터리 경로입니다.
`embedding_model` | `Optional[BaseEmbedding]` | 아니요 | `None` | 커스텀 LlamaIndex `BaseEmbedding` 인스턴스입니다. 생략할 경우 기본값은 `GoogleGenAIEmbedding(model_name="gemini-embedding-2-preview", embed_batch_size=1)`입니다.

### 커스텀 임베딩 모델

LlamaIndex의 `BaseEmbedding` 인터페이스를 준수하는 인스턴스를 전달하여 임베딩 모델을 맞춤설정할 수 있습니다.

```python
from google.adk.tools.retrieval.files_retrieval import FilesRetrieval
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding

custom_embedding = GoogleGenAIEmbedding(
    model_name="gemini-embedding-2",
    embed_batch_size=1,
)

files_retrieval = FilesRetrieval(
    name="search_documents",
    description="Search local knowledge base files.",
    input_dir=os.path.join(os.path.dirname(__file__), "data"),
    embedding_model=custom_embedding,
)
```

## 추가 리소스

- [VectorStoreIndex 사용 (LlamaIndex)](https://docs.llamaindex.ai/en/stable/module_guides/indexing/vector_store_index/)
- [PyPI의 llama-index-embeddings-google-genai](https://pypi.org/project/llama-index-embeddings-google-genai/)
