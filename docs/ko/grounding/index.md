# 데이터로 에이전트 그라운딩

그라운딩은 AI 에이전트를 외부 정보 소스에 연결해 더 정확하고 최신이며 검증 가능한 응답을 생성하도록 하는 과정입니다. 권위 있는 데이터에 응답을 근거시키면 환각을 줄이고 사용자에게 신뢰할 수 있는 출처에 기반한 답변을 제공할 수 있습니다.

ADK는 여러 그라운딩 방식을 지원합니다.

- **Google Search Grounding**: 뉴스, 날씨, 모델 학습 이후 바뀌었을 수 있는 사실처럼 최신 데이터가 필요한 쿼리에 대해 에이전트를 실시간 웹 정보에 연결합니다.
- **Grounding with Search**: 독점 정보가 필요한 쿼리를 위해 에이전트를 조직의 비공개 문서와 엔터프라이즈 데이터에 연결합니다.
- **Agentic RAG**: Agent Retrieval, Knowledge Engine 또는 기타 검색 시스템을 사용해 쿼리와 필터를 동적으로 구성하며 검색 방법을 추론하는 에이전트를 빌드합니다.

<div class="grid cards" markdown>

-   :material-magnify: **Google Search Grounding**

    ---

    에이전트가 웹의 실시간 권위 있는 정보에 접근할 수 있게 합니다. Google Search 그라운딩 설정, 데이터 흐름 이해, 그라운딩된 응답 해석, 사용자에게 인용 표시 방법을 알아보세요.

    - [Google Search Grounding 이해하기](google_search_grounding.md)

-   :material-file-search: **Grounding with Search**

    ---

    에이전트를 인덱싱된 엔터프라이즈 문서와 비공개 데이터 저장소에 연결합니다. Agent Search 데이터 저장소 구성, 조직 지식 기반으로 응답 그라운딩, 출처 표시 방법을 알아보세요.

    - [Grounding with Search 이해하기](grounding_with_search.md)

-   :material-post: **블로그: Vector Search 2.0과 ADK로 10분 만에 만드는 Agentic RAG**

    ---

    단순한 검색 후 생성 패턴을 넘어서는 Agentic RAG 시스템을 빌드하는 방법을 알아보세요. 이 글에서는 사용자 의도를 파싱하고, 메타데이터 필터를 구성하며, Vector Search 2.0과 ADK의 하이브리드 검색으로 런던 Airbnb 목록 2,000개를 검색하는 여행 에이전트를 만드는 과정을 다룹니다.

    - [블로그: Vector Search 2.0과 ADK로 10분 만에 만드는 Agentic RAG](https://medium.com/google-cloud/10-minute-agentic-rag-with-the-new-vector-search-2-0-and-adk-655fff0bacac)

-   :material-notebook: **Vector Search 2.0 여행 에이전트 노트북**

    ---

    Agentic RAG 블로그 글과 함께 볼 수 있는 실습용 Jupyter 노트북입니다. 실제 Airbnb 데이터, 자동 임베딩, RRF 순위 지정 기반 하이브리드 검색, ADK 도구 통합을 사용해 엔드투엔드 여행 에이전트를 빌드합니다.

    - [Vector Search 2.0 여행 에이전트 노트북](https://github.com/google/adk-samples/blob/main/python/notebooks/grounding/vectorsearch2_travel_agent.ipynb)

-   :material-text-search: **Deep Search Agent**

    ---

    주제를 인용이 포함된 종합 보고서로 변환하는 프로덕션 준비형 풀스택 리서치 에이전트입니다. 계획 승인에 human-in-the-loop를 사용하고, 반복 검색 정제와 계획/조사/비평/작성용 멀티 에이전트 구조를 갖춥니다.

    - [Deep Search Agent](https://github.com/google/adk-samples/tree/main/python/agents/deep-search)

-   :material-file-document-multiple: **RAG Agent**

    ---

    Knowledge Engine 기반 문서 Q&A 에이전트입니다. 문서를 업로드하고 질문하면 출처 자료를 가리키는 URL 형식의 인용과 함께 정확한 답변을 받을 수 있습니다.

    - [RAG Agent](https://github.com/google/adk-samples/tree/main/python/agents/RAG)

</div>
