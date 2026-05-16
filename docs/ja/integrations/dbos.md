---
catalog_title: DBOS
catalog_description: human approval と安全な versioning を備えた resilient, scalable, long-running agent
catalog_icon: /integrations/assets/dbos.png
catalog_tags: ["resilience"]
---

# ADK 向け DBOS プラグイン

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[DBOS](https://dbos.dev) は、信頼性の高い workflow と AI agent を構築するための
durable execution framework です。ADK と統合し、LLM call、tool execution、
agent orchestration を fault-tolerant かつ scalable にします。エージェントは crash、
deploy、restart の後でも正確に中断地点から再開され、別の orchestration service を
必要とせず、ユーザーが所有する database を基盤に動作します。

## ユースケース

DBOS プラグインは ADK エージェントに production-grade reliability と orchestration を追加します。

- **Durable execution**: LLM とツールの出力を永続化します。crash、deploy、machine failure
  から、進行状況を失ったり side effect を重複させたりせずにエージェントを自動復旧します。
  手動の [session resumption](/ja/runtime/resume/) は不要です。
- **組み込み retry と backoff**: LLM provider と tool execution の一時的な失敗に対応するため、
  exponential backoff を備えた構成可能な retry policy を提供します。
- **Long-running agents**: エージェントとツールを数時間、数日、数か月にわたって実行します。
- **Human-in-the-loop**: 実行を一時停止し、外部 signal または human approval を受け取った後で
  後から再開します。
- **Rate limiting を備えた scalable execution**: workflow 内で複数のエージェントを組み合わせるか、
  durable queue と組み込み rate limiting を使って分散 worker 全体へ agent workflow を拡張します。
- **Observability と management**: [DBOS Console](https://docs.dbos.dev/production/workflow-management)から
  agent workflow を inspect、cancel、resume、fork できます。

## 前提条件

- Python 3.10+
- [Gemini API key](https://aistudio.google.com/app/api-keys)、またはサポートされている
  [モデル](/ja/agents/models/)

## インストール

```bash
pip install dbos-google-adk
```

## エージェントでの使用

この統合は、各 LLM call が durable DBOS workflow step として実行されるように
ADK エージェントをラップします。`@DBOS.step()` で decorate された tool function は、
構成可能な retry とともに個別に checkpoint されます。

### 基本設定

`Runner` に `DBOSPlugin` を追加し、`@DBOS.workflow()` からエージェントを駆動して、
エージェントと workflow を定義します。

```python
import asyncio
import logging

from dbos import DBOS, DBOSConfig
from dbos_google_adk import DBOSPlugin
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Decorate tool calls with @DBOS.step() for durable execution
@DBOS.step()
async def get_weather(city: str) -> str:
    """Get the weather for a city."""
    return f"Sunny in {city}"

agent = LlmAgent(name="weather", model="gemini-flash-latest", tools=[get_weather])
runner = Runner(
    app_name="my-agent",
    agent=agent,
    plugins=[DBOSPlugin()],
    session_service=InMemorySessionService(),
)

# Drive the agent from a DBOS workflow for durable execution
@DBOS.workflow()
async def run_agent(user_id: str, session_id: str, message: str) -> str:
    new_message = types.Content(role="user", parts=[types.Part.from_text(text=message)])
    async for event in runner.run_async(
        user_id=user_id, session_id=session_id, new_message=new_message
    ):
        if event.is_final_response():
            return event.content.parts[0].text
    return ""


async def main():
    # DBOS checkpoints to SQLite by default. Postgres is recommended for production.
    config: DBOSConfig = {"name": "my-agent", "system_database_url": "sqlite:///dbostest.sqlite"}
    DBOS(config=config)
    DBOS.launch()

    await runner.session_service.create_session(
        app_name="my-agent", user_id="u", session_id="s"
    )
    print(await run_agent("u", "s", "How is the weather in San Francisco?"))


if __name__ == "__main__":
    asyncio.run(main())
```

### Durable event compaction

Durable event compaction では、summarizer を `DBOSEventSummarizer` でラップすると、
compaction LLM call も checkpoint されます。

```python
from dbos_google_adk import DBOSEventSummarizer
from google.adk.models.google_llm import Gemini

summarizer = DBOSEventSummarizer.from_llm(Gemini(model="gemini-flash-latest"))
```

## 仕組み

`DBOSPlugin` と `DBOSEventSummarizer` は、ADK エージェントを durable DBOS workflow
内で実行します。

- **LLM call** は `DBOSPlugin` によって intercept され、DBOS step として実行されます。
  呼び出しが失敗するか worker が crash すると、DBOS は最後に成功した step から再開し、
  無駄な token spend を減らします。
- **Tool function** は `@DBOS.step()` で decorate されると個別に checkpoint されます。
  出力は database に保存されるため、replay は完了済みの tool execution を完全にスキップします。
- **Workflow execution** は各 step の後に database(SQLite または Postgres)へ serialize されて
  保存されます。同じ database にアクセスできる任意の worker process が実行を引き継げるため、
  distributed failover と horizontal scaling が可能です。

## 機能

| 機能 | 説明 |
| --- | --- |
| Durable tool execution | LLM call に加えて、`@DBOS.step()` で decorate された tool function が、失敗時の構成可能な retry とともに database に checkpoint されます |
| Failure recovery | process restart 時に最後に成功した step から in-flight workflow を再開するか、[DBOS Conductor](https://docs.dbos.dev/production/conductor) を使う distributed setting で automatic fail-over します |
| Parallel tool calls | 単一の LLM response から複数の tool call を replay-safe に並行 dispatch し、次の LLM step の前に join します |
| Debugging | 過去の workflow execution を step-by-step で replay します。bug fix のために特定の step から workflow を fork して restart できます |
| Long-running agents | workflow は数時間、数日、数か月にわたって実行でき、state は完了まで database に保持されます |
| Observability | すべての LLM call と tool execution は記録された step であり、[DBOS Console](https://docs.dbos.dev/production/workflow-management) dashboard または OpenTelemetry で確認できます |
| Human-in-the-loop | DBOS [workflow notifications](https://docs.dbos.dev/python/tutorials/workflow-communication#workflow-messaging-and-notifications) を通じて外部 signal または human approval を受け取り、後から実行を再開します |
| Rate limiting を備えた scalable execution | workflow 内で複数のエージェントを組み合わせるか、[durable queues](https://docs.dbos.dev/python/tutorials/queue-tutorial) を使って分散 worker 全体で agent workflow を実行します。API backpressure に対応する組み込み rate limiting を提供します |
| Safe versioning | in-flight execution を中断せずに [DBOS patching or versioning](https://docs.dbos.dev/python/tutorials/upgrading-workflows) を使って新しいエージェントバージョンを upgrade および deploy します |

## 追加リソース

- [DBOS Python documentation](https://docs.dbos.dev/python/programming-guide) - DBOS workflow、step、queue の完全な reference
- [dbos-google-adk on PyPI](https://pypi.org/project/dbos-google-adk/) - Python package
- [DBOS GitHub repository](https://github.com/dbos-inc/dbos-transact-py) - Source code and examples
- [DBOS Discord](https://discord.gg/eMUHrvbu67) - Questions and community discussion
