# ADK TypeScript クイックスタート

このガイドでは、Agent Development Kit (ADK) を TypeScript で使い始めて実行する方法を説明します。開始前に以下をインストールしてください。

*   Node.js 24.13.0 以上
*   Node Package Manager (npm) 11.8.0 以上

## エージェントプロジェクトの作成

プロジェクト用に空の `my-agent` ディレクトリを作成します。

```none
my-agent/
```

??? tip "コマンドラインでこの構成を作成"

    === "MacOS / Linux"

        ```bash
        mkdir -p my-agent/
        ```

    === "Windows"

        ```console
        mkdir my-agent
        ```

### プロジェクトと依存関係の設定

`npm` ツールを使って、package ファイル、ADK TypeScript メインライブラリ、
開発ツールを含む依存関係をインストールします。`my-agent/` ディレクトリで以下のコマンドを実行し、
`package.json` を作成して依存関係をインストールします。

```console
cd my-agent/
# initialize a project as an ES module
npm init --yes
npm pkg set type="module"
npm pkg set main="agent.ts"
# install ADK libraries
npm install @google/adk
# install dev tools as a dev dependency
npm install -D @google/adk-devtools
```

### エージェントコードを定義

`getCurrentTime` という [Function Tool](/adk-docs/tools/function-tools/) のシンプルな実装を含む、
基本エージェントのコードを作成します。`my-agent` プロジェクトに `agent.ts` を作成して次を追加します。

```typescript title="my-agent/agent.ts"
import {FunctionTool, LlmAgent} from '@google/adk';
import {z} from 'zod';

/* Mock tool implementation */
const getCurrentTime = new FunctionTool({
  name: 'get_current_time',
  description: 'Returns the current time in a specified city.',
  parameters: z.object({
    city: z.string().describe("The name of the city for which to retrieve the current time."),
  }),
  execute: ({city}) => {
    return {status: 'success', report: `The current time in ${city} is 10:30 AM`};
  },
});

export const rootAgent = new LlmAgent({
  name: 'hello_time_agent',
  model: 'gemini-2.5-flash',
  description: 'Tells the current time in a specified city.',
  instruction: `You are a helpful assistant that tells the current time in a city.
                Use the 'getCurrentTime' tool for this purpose.`,
  tools: [getCurrentTime],
});
```

### API キーを設定

このプロジェクトは Gemini API を使用するため API キーが必要です。まだ持っていない場合は
[API キー](https://aistudio.google.com/app/apikey) ページで Google AI Studio から作成してください。

ターミナルで、プロジェクトの `.env` に API キーを書き込み、環境変数を設定します。

```bash title="Update: my-agent/.env"
echo 'GEMINI_API_KEY="YOUR_API_KEY"' > .env
```

??? tip "ADK で他の AI モデルを使用"
    ADK は多くの生成AIモデルをサポートします。ADK エージェントで他のモデルを設定する方法は
    [Models & Authentication](/adk-docs/agents/models) を参照してください。

## エージェントを実行

`@google/adk-devtools` ライブラリを使い、`run` コマンドでインタラクティブ
CLI として実行するか、`web` コマンドで ADK Web UI を使うことができます。
両方ともエージェントのテストと対話を行えます。

### コマンドラインで実行

```bash
adk run my-agent/agent.ts
```

### Web UI で実行

```bash
adk web my-agent/agent.ts
```
