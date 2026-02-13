# 데이터 기반으로 에이전트 근거 강화

Grounding은 AI 에이전트를 외부 정보 소스에 연결해 응답을 보다 정확하고 최신이며 검증 가능한 형태로 만드는 과정입니다.
신뢰할 수 있는 데이터에 근거해 응답을 생성하면 환각(hallucination)을 줄이고 사용자에게 신뢰 가능한 출처 기반 답변을 제공할 수 있습니다.

ADK는 여러 grounding 방식 을 지원합니다.

- **Google Search Grounding:** 뉴스, 날씨, 최신 변경 정보 등 시의성이 높은 쿼리에 대해 실시간 웹 정보를 에이전트에 연결합니다.
- **Vertex AI Search Grounding:** 조직의 비공개 문서와 엔터프라이즈 데이터에 대한 쿼리를 위해 사내 문서를 연결합니다.
- **Agentic RAG:** Vector Search 2.0, Vertex AI RAG Engine 또는 기타 검색 시스템을 이용해,
  검색/필터를 동적으로 구성하는 방식으로 추론하는 에이전트를 구축합니다.

<div class="grid cards" markdown>

-   :material-magnify: **Google Search Grounding**

    ---

    에이전트가 웹의 실시간 권위 있는 정보를 사용할 수 있게 합니다. Google Search grounding 설정,
    데이터 흐름 이해, grounding 응답 해석, 사용자에게 인용 표시 방법을 확인하세요.

    - [Google Search Grounding 이해하기](google_search_grounding.md)

-   :material-file-search: **Vertex AI Search Grounding**

    ---

    인덱싱된 엔터프라이즈 문서와 비공개 데이터 저장소에 에이전트를 연결합니다.
    Vertex AI Search 데이터 저장소 구성, 조직 지식 기반 기반 grounding, 소스 귀속 표시 방법을 확인하세요.

    - [Vertex AI Search Grounding 이해하기](vertex_ai_search_grounding.md)

-   :material-post: **블로그 글: Vector Search 2.0과 ADK를 활용한 10분 Agentic RAG**

    ---

    단순 retrieve-then-generate 패턴을 넘는 Agentic RAG 시스템 구축 방법을 배웁니다. 이 글에서는 사용자 의도를 해석하고
    메타데이터 필터를 구성하며, Vector Search 2.0과 ADK로 하이브리드 검색을 수행해
    런던 Airbnb 목록 2,000건을 검색하는 여행 에이전트를 구현합니다.

    - [블로그 글: Vector Search 2.0과 ADK를 활용한 10분 Agentic RAG](https://medium.com/google-cloud/10-minute-agentic-rag-with-the-new-vector-search-2-0-and-adk-655fff0bacac)

-   :material-notebook: **Vector Search 2.0 여행 에이전트 노트북**

    ---

    Agentic RAG 블로그 포스트의 실습형 Jupyter 노트북 예시입니다. 실제 Airbnb 데이터를 사용해
    자동 임베딩, RRF 랭킹 하이브리드 검색, ADK 툴 통합을 포함한 엔드투엔드 여행 에이전트를 구축하세요.

    - [Vector Search 2.0 여행 에이전트 노트북](https://github.com/google/adk-samples/blob/main/python/notebooks/grounding/vectorsearch2_travel_agent.ipynb)

-   :material-text-search: **Deep Search Agent**

    ---

    주제 기반의 종합 보고서를 인용과 함께 생성하는 production-ready 풀스택 리서치 에이전트입니다.
    human-in-the-loop 승인 플로우와 반복 검색 정제, 그리고 기획/조사/평가/작성의 멀티에이전트 구조를 제공합니다.

    - [Deep Search Agent](https://github.com/google/adk-samples/tree/main/python/agents/deep-search)

-   :material-file-document-multiple: **RAG Agent**

    ---

    Vertex AI RAG Engine 기반 문서 Q&A 에이전트입니다. 문서를 업로드하고 질문하면
    출처 URL을 포함한 정확한 답변과 인용을 받을 수 있습니다.

    - [RAG Agent](https://github.com/google/adk-samples/tree/main/python/agents/RAG)

</div>
