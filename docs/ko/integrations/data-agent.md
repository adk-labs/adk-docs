---
catalog_title: Data Agents
catalog_description: AI 기반 에이전트로 데이터를 분석합니다
catalog_icon: /adk-docs/integrations/assets/vertex-ai.png
catalog_tags: ["data", "google"]
---

# ADK용 Google Cloud Data Agents 도구

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.23.0</span>
</div>

다음은 [Conversational Analytics API](https://docs.cloud.google.com/gemini/docs/conversational-analytics-api/overview) 기반 Data Agents와 통합하기 위한 도구 모음입니다.

Data Agents는 자연어를 사용해 데이터를 분석할 수 있도록 돕는 AI 기반 에이전트입니다. Data Agent를 구성할 때 **BigQuery**, **Looker**, **Looker Studio**를 포함한 지원 데이터 소스를 선택할 수 있습니다.

**사전 준비 사항**

이 도구를 사용하기 전에 Google Cloud에서 Data Agents를 빌드하고 구성해야 합니다:

* [HTTP 및 Python으로 data agent 빌드하기](https://docs.cloud.google.com/gemini/docs/conversational-analytics-api/build-agent-http)
* [Python SDK로 data agent 빌드하기](https://docs.cloud.google.com/gemini/docs/conversational-analytics-api/build-agent-sdk)
* [BigQuery Studio에서 data agent 만들기](https://docs.cloud.google.com/bigquery/docs/create-data-agents#create_a_data_agent)

`DataAgentToolset`에는 다음 도구가 포함됩니다:

* **`list_accessible_data_agents`**: 구성된 GCP 프로젝트에서 액세스 권한이 있는 Data Agents를 나열합니다.
* **`get_data_agent_info`**: 전체 리소스 이름을 기반으로 특정 Data Agent의 상세 정보를 조회합니다.
* **`ask_data_agent`**: 특정 Data Agent와 자연어로 대화합니다.

이 도구들은 `DataAgentToolset` 툴셋으로 패키징되어 있습니다.

```py
--8<-- "examples/python/snippets/tools/built-in-tools/data_agent.py"
```
