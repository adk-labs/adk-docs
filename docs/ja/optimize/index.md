# エージェントの最適化

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.24.0</span>
</div>

ADK は、評価結果に基づいてエージェントを自動最適化するための拡張可能なフレームワークを提供します。
標準では、`adk optimize` コマンドを使って、デフォルトのオプティマイザーで ADK 評価結果に基づくシンプルなエージェントをすばやく最適化できます。
より複雑なユースケースでは、カスタム eval データを使うサンプラーを開発したり、新しい最適化戦略を実装したりできます。

### 定義

* **サンプラー**: サンプラーは、エージェントオプティマイザーが候補の最適化エージェントを評価できるようにします。
要求されたとき、サンプラーは eval 主導のエージェント最適化に役立つ詳細な評価結果をオプティマイザーへ提供します。
* **エージェントオプティマイザー**: エージェントオプティマイザーはサンプラーからの評価結果を確認し、それを使ってエージェントを改善します。

## 例 - `adk optimize` でシンプルなエージェントを最適化する {#example}

この例では、小さな eval セットでの評価結果に基づいて [`hello_world`](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world) サンプルエージェントの指示を更新するために `adk optimize` コマンドを使用します。

### ステップ 1: 例のデータセットを指定する {#exampledataset}

デフォルトの `hello_world` エージェントの指示は、数が素数かどうかを判定する方法を説明しています。
この例の eval セットでは、エージェントに指示していない別の観点が追加されます。数はその素数性に応じて "good" または "bad" になり得ます。
オプティマイザーはこの新しいルールを導き出し、エージェントの指示に追加することが期待されます。

[`contributing/samples/hello_world/`](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world) に `train_eval_set.evalset.json` ファイルを作成し、次の内容を入れます。

```json
{
  "eval_set_id": "train_eval_set",
  "name": "train_eval_set",
  "eval_cases": [
    {
      "eval_id": "simple",
      "conversation": [
        {
          "invocation_id": "inv1",
          "user_content": {
            "parts": [ {"text": "Is 7 prime?"} ],
            "role": "user"
          },
          "final_response": {
            "parts": [ {"text": "7 is a prime number."} ],
            "role": "model"
          }
        }
      ],
      "session_input": {
        "app_name": "hello_world",
        "user_id": "user"
      }
    },
    {
      "eval_id": "is_good",
      "conversation": [
        {
          "invocation_id": "inv1",
          "user_content": {
            "parts": [ {"text": "Is 4 a bad number?"} ],
            "role": "user"
          },
          "final_response": {
            "parts": [ {"text": "4 is not prime so it is a good number."} ],
            "role": "model"
          }
        }
      ],
      "session_input": {
        "app_name": "hello_world",
        "user_id": "user"
      }
    },
    {
      "eval_id": "is_bad",
      "conversation": [
        {
          "invocation_id": "inv1",
          "user_content": {
            "parts": [ {"text": "Is 5 a bad number?"} ],
            "role": "user"
          },
          "final_response": {
            "parts": [ {"text": "5 is prime so it is a bad number."} ],
            "role": "model"
          }
        }
      ],
      "session_input": {
        "app_name": "hello_world",
        "user_id": "user"
      }
    }
  ]
}
```

### ステップ 2: サンプラー設定を定義する

サンプラー設定は、候補の最適化エージェントを評価するプロセスを制御します。
たとえば、エージェント出力の正解基準を指定し、エージェント最適化に使う eval セットも指定します。

設定オプションの全一覧は [下記](#localevalsampler) にあります。ひとまず、[`contributing/samples/hello_world/`](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world) に `sampler_config.json` ファイルを次の内容で作成してください。

```json
{
  "eval_config": {
    "criteria": {
      "response_match_score": 0.75
    }
  },
  "app_name": "hello_world",
  "train_eval_set": "train_eval_set"
}
```

### ステップ 3: 最適化ジョブを実行する

`adk optimize` コマンドを実行し、`hello_world` エージェントのディレクトリを指定して、上で作成した設定ファイルを渡します。

```bash
adk optimize contributing/samples/hello_world \
--sampler_config_file_path contributing/samples/hello_world/sampler_config.json
```

最終出力は異なりますが、次のような形になることがあります。

```text
<logs and intermediate output>
================================================================================
Optimized root agent instructions:
--------------------------------------------------------------------------------
<existing unmodified instructions omitted for brevity>

**Special Rules for "Good" and "Bad" Numbers:**
*   A "bad number" is defined as a prime number.
*   A "good number" is defined as a non-prime number (i.e., a composite number or 1).
*   If a user asks if a number is "good" or "bad", you must always use the `check_prime` tool to determine its primality first.
*   After determining primality with the tool, respond according to the definitions above. Questions about "good" or "bad" numbers, when referring to primality, are objective and you are fully capable of answering them. Do not state you cannot answer such questions.
================================================================================
```

## `adk optimize` コマンドを使う

```bash
adk optimize [OPTIONS] AGENT_MODULE_FILE_PATH
```

* `AGENT_MODULE_FILE_PATH`: `agent` という名前のモジュールを含む `__init__.py` ファイルのパスです。
`agent` モジュールには `root_agent` が含まれていなければなりません。
有効なセットアップ例として、[`hello_world`](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world) エージェントを参照してください。
* `--sampler_config_file_path PATH`: サンプラーの設定ファイルへのパスです。
サンプラーの実装と設定フォーマットは [下記](#localevalsampler) で説明します。
* `--optimizer_config_file_path PATH`（任意）: エージェントオプティマイザーの設定ファイルへのパスです。
指定しない場合はデフォルト設定が使われます。
オプティマイザーの実装、設定フォーマット、デフォルト設定は [下記](#geparootagentpromptoptimizer) で説明します。
* `--print_detailed_results`（任意）: エージェントオプティマイザーが測定した詳細メトリクスの出力を有効にします。
* `--log_level`（任意）: ログレベルを設定します。
デフォルトは `INFO` です。
有効な値は `DEBUG`、`INFO`、`WARNING`、`ERROR`、`CRITICAL` です。

## 利用可能なサンプラーとエージェントオプティマイザー

ADK には次のサンプラーとエージェントオプティマイザーが用意されています。
`adk optimize` コマンドは、下記の `LocalEvalSampler` と `GEPARootAgentPromptOptimizer` を使用します。
これらは独自のスクリプトでも使用できます。

### `LocalEvalSampler` {#localevalsampler}

[`LocalEvalSampler`](https://github.com/google/adk-python/blob/main/src/google/adk/optimization/local_eval_sampler.py) は、ADK の [`LocalEvalService`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/local_eval_service.py) を使って候補エージェントを評価します。
評価結果を [`UnstructuredSamplingResult`](#sampler-results) として提供します。
`LocalEvalSampler` は、以下のフィールドを含む `LocalEvalSamplerConfig` で設定できます。

* `eval_config`: 評価基準とユーザーシミュレーションオプションを提供する [`EvalConfig`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_config.py) です。
* `app_name`: 評価に使うアプリ名です。
* `train_eval_set`: 最適化に使う eval セット名です。
* `train_eval_case_ids`（任意）: 最適化に使う eval case（example）の ID です。
指定しない場合は `train_eval_set` のすべての eval case が使われます。
* `validation_eval_set`（任意）: 最適化済みエージェントの検証に使う eval セット名です。
指定しない場合は `train_eval_set` が再利用されます。
* `validation_eval_case_ids`（任意）: 最適化済みエージェントの検証に使う eval case（example）の ID です。
指定しない場合は `validation_eval_set` のすべての eval case が使われます。
`validation_eval_set` も指定されていない場合は、実質的に train eval case が再利用されます。

`LocalEvalSampler` を初期化する際には、`LocalEvalSamplerConfig` で指定された train および validation eval セットにアクセスできる [`EvalSetsManager`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_sets_manager.py) も提供する必要があります。

### `GEPARootAgentPromptOptimizer` {#geparootagentpromptoptimizer}

[`GEPARootAgentPromptOptimizer`](https://github.com/google/adk-python/blob/main/src/google/adk/optimization/gepa_root_agent_prompt_optimizer.py) は、[GEPA](https://gepa-ai.github.io/gepa/) オプティマイザーを使ってルートエージェントの指示を改善します。
このオプティマイザーは、サンプラーが評価結果を [`UnstructuredSamplingResult`](#sampler-results) として提供することを期待します。
出力は [`OptimizerResult`](#agent-optimizer-results) のサブクラスで、[スコア付き最適化エージェントのリスト](#agent-optimizer-results) と最適化中に収集された追加メトリクスを指定します。

注意: `GEPARootAgentPromptOptimizer` は、サブエージェント、エージェントツール、スキル、またはルートエージェントの他の側面は改善しません。

`GEPARootAgentPromptOptimizer` は、次のフィールドを含む `GEPARootAgentPromptOptimizerConfig` で設定できます。

* `optimizer_model`（任意）: 評価結果を分析してエージェントを最適化するために使うモデルです。
デフォルトは `"gemini-flash-latest"` です。
* `model_configuration`（任意）: オプティマイザーモデルの設定です。
デフォルトは 1 万トークンの thinking budget を持つ設定です。
* `max_metric_calls`（任意）: 最適化中に実行する評価の最大数です。
デフォルトは 100 です。
* `reflection_minibatch_size`（任意）: 一度にエージェント指示を更新するために使う例の数です。
デフォルトは 3 です。
* `run_dir`（任意）: 必要に応じて中間および最終の最適化結果を保存するディレクトリです。
ウォームスタートを容易にします。

## 主要データ型

ADK は、サンプラーからオプティマイザーへの eval データの受け渡しと、オプティマイザーの出力を管理するために
[`optimization/data_types.py`](https://github.com/google/adk-python/blob/main/src/google/adk/optimization/data_types.py) にいくつかの基本データ型を定義しています。
これらのデータ型は、カスタム eval や最適化戦略に対応できるよう拡張可能に設計されています。

### サンプラー結果 {#sampler-results}

* [`SamplingResult`](https://github.com/google/adk-python/blob/main/src/google/adk/optimization/data_types.py):
サンプラー出力の基礎クラスです。
  * example UID を、その例に対するエージェントの全体スコアへ対応付ける `scores` 辞書を含む必要があります。
* [`UnstructuredSamplingResult`](https://github.com/google/adk-python/blob/main/src/google/adk/optimization/data_types.py):
`SamplingResult` の組み込みサブクラスで、トラジェクトリ、中間出力、サブメトリクスなどの、非構造化かつ各例ごとの JSON 直列化可能な評価データを保持する任意の `data` フィールドを追加します。

多くのユースケースでは `UnstructuredSamplingResult` を使えます。
代わりに、より構造化された形式で追加評価データを返す独自の `SamplingResult` サブクラスを作成することもできます。
ただし、サンプラーとオプティマイザーの両方がその形式をサポートしていなければなりません。

### エージェントオプティマイザー結果 {#agent-optimizer-results}

* [`AgentWithScores`](https://github.com/google/adk-python/blob/main/src/google/adk/optimization/data_types.py):
全体スコアを伴う単一の最適化済みエージェントを表します。
  * 更新済み [`Agent`](https://github.com/google/adk-python/blob/main/src/google/adk/agents/llm_agent.py) オブジェクトである `optimized_agent` を含む必要があります。
  * エージェントの `overall_score`（通常は validation セット上）を含められます。
* [`OptimizerResult`](https://github.com/google/adk-python/blob/main/src/google/adk/optimization/data_types.py):
最適化プロセスの最終出力を表します。
  * `optimized_agents` のリストを含む必要があります（要素は `AgentWithScores` またはそのサブクラス）。
  複数メトリクスでエージェントの最適性を測る場合、パレートフロンティアを表現するために複数エントリが必要になることがあります。

候補の最適化済みエージェントについて細かなメトリクスを公開するために、`AgentWithScores` の独自サブクラスを作成できます。
たとえば、正確性、安全性、整合性などを別々に採点したい場合があります。
同様に、`OptimizerResult` の独自サブクラスを作成して、オプティマイザーの最適化プロセス全体に関するメトリクス（評価した候補数、総評価数など）を公開できます。

## 新しいサンプラーとエージェントオプティマイザーの作成と利用

ユースケースに複雑なサンプリングと評価ロジック、または独自のエージェント最適化戦略が必要な場合は、以下で説明する `Sampler` と `AgentOptimizer` の抽象クラスを使って独自実装を作成できます。
この API に従うことで、ADK 提供のサンプラーとエージェントオプティマイザーを独自実装と組み合わせて使えます。

### 新しいサンプラーを作成する

カスタム評価用の新しいサンプラーを作成するには、[`Sampler`](https://github.com/google/adk-python/blob/main/src/google/adk/optimization/sampler.py) 基底クラスを継承するクラスを作成する必要があります。
また、評価結果を返すためにサンプラーが使う [`SamplingResult`](#sampler-results) のサブクラスも指定する必要があります。
サンプラーは次の抽象メソッドを実装しなければなりません。

* `get_train_example_ids(self)`: 最適化に使う example UID のリストを返します。
* `get_validation_example_ids(self)`: 最適化済みエージェントの検証に使う example UID のリストを返します。
<!-- disableFinding(LINE_OVER_80) -->
* `sample_and_score(self, candidate, example_set, batch, capture_full_eval_data)`: 指定された `example_set`（`"train"` または `"validation"`）からの `batch` の例に対して `candidate` エージェントを評価します。
計算済みの各例スコアと、`capture_full_eval_data` が `True` の場合に eval 主導のエージェント最適化に必要な追加データを含む [`SamplingResult`](#sampler-results) サブクラスを返す必要があります。
追加の eval データの形式は、`SamplingResult` をサブクラス化して必要に応じて選べます。
ただし、エージェントオプティマイザーも同じ `SamplingResult` サブクラスをサポートしている必要があります。
[`UnstructuredSamplingResult`](#sampler-results) は、追加データを各例ごとの非構造化辞書に保存する最も単純なケースを実装しています。
<!-- enableFinding(LINE_OVER_80) -->

### 新しいエージェントオプティマイザーを作成する

カスタムエージェントオプティマイザーを作成するには、[`AgentOptimizer`](https://github.com/google/adk-python/blob/main/src/google/adk/optimization/agent_optimizer.py) 基底クラスを継承するクラスを作る必要があります。
また、評価結果を受け取る [`SamplingResult`](#sampler-results) のサブクラスと、各最適化済みエージェントおよびそのスコア/メトリクスを表すために使う [`AgentWithScores`](#agent-optimizer-results) のサブクラスも指定する必要があります。
オプティマイザーは次の抽象メソッドを実装しなければなりません。

* `optimize(self, initial_agent, sampler)`: このメソッドは最適化プロセスをオーケストレーションします。
改善対象の `initial_agent` と、候補評価に使う `sampler` を受け取ります。
候補の最適化済みエージェントのリストと、それらのスコア/メトリクス、および最適化プロセス全体に関連するメトリクスを含む [`OptimizerResult`](#agent-optimizer-results) サブクラスを返す必要があります。
候補ごとのスコア/メトリクス形式は、`AgentWithScores` をサブクラス化することで必要に応じて選べます。
あるいは、各候補最適化済みエージェントに対して単一の全体スコアを指定できる `AgentWithScores` をそのまま使うこともできます。

### エージェントをプログラムで最適化する

`adk optimize` コマンドは [`LocalEvalSampler`](#localevalsampler) と [`GEPARootAgentPromptOptimizer`](#geparootagentpromptoptimizer) を使用します。
カスタムサンプラーやエージェントオプティマイザーを使う場合は、エージェントをプログラムで最適化する必要があります。
以下の参照コードは、上の [例](#example) に対する `adk optimize` コマンドの機能を再現します。
使うには、例に示した [データセット](#exampledataset) を作成し、[同じディレクトリ](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world) 内の Python スクリプトからこのコードを実行してください。

```python
import asyncio
import logging
import os

import agent  # the hello_world agent
from google.adk.cli.utils import envs
from google.adk.cli.utils import logs
from google.adk.evaluation.eval_config import EvalConfig
from google.adk.evaluation.local_eval_sets_manager import LocalEvalSetsManager
from google.adk.optimization.gepa_root_agent_prompt_optimizer import GEPARootAgentPromptOptimizer
from google.adk.optimization.gepa_root_agent_prompt_optimizer import GEPARootAgentPromptOptimizerConfig
from google.adk.optimization.local_eval_sampler import LocalEvalSampler
from google.adk.optimization.local_eval_sampler import LocalEvalSamplerConfig

# setup environment variables (API keys, etc.) and logging
envs.load_dotenv_for_agent(".", ".")
logs.setup_adk_logger(logging.INFO)

# create the sampler
sampler_config = LocalEvalSamplerConfig(
    eval_config=EvalConfig(criteria={"response_match_score": 0.75}),
    app_name="hello_world",  # typically the name of the directory containing the agent
    train_eval_set="train_eval_set",  # from the example
)
eval_sets_manager = LocalEvalSetsManager(
    agents_dir=os.path.dirname(os.getcwd()),
)
sampler = LocalEvalSampler(sampler_config, eval_sets_manager)

# create the optimizer
opt_config = GEPARootAgentPromptOptimizerConfig()
optimizer = GEPARootAgentPromptOptimizer(config=opt_config)

# optimize the root agent
initial_agent = agent.root_agent
result = asyncio.run(
    optimizer.optimize(initial_agent, sampler)
)

# show the results
best_idx = result.gepa_result["best_idx"]
print(
    "Validation score:",
    result.optimized_agents[best_idx].overall_score,
    "Optimized prompt:",
    result.optimized_agents[best_idx].optimized_agent.instruction,
    "GEPA metrics:",
    result.gepa_result,
    sep="\n",
)
```
