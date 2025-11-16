# モデルコンテキストプロトコルツール

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

このガイドでは、モデルコンテキストプロトコル（MCP）をADKと統合する2つの方法について説明します。

## モデルコンテキストプロトコル（MCP）とは？

モデルコンテキストプロトコル（MCP）は、GeminiやClaudeなどの大規模言語モデル（LLM）が外部アプリケーション、データソース、ツールと通信する方法を標準化するために設計されたオープンスタンダードです。LLMがコンテキストを取得し、アクションを実行し、さまざまなシステムと対話する方法を簡素化するユニバーサルな接続メカニズムと考えてください。

MCPはクライアントサーバーアーキテクチャに従い、**データ**（リソース）、**インタラクティブテンプレート**（プロンプト）、**アクション可能な関数**（ツール）が**MCPサーバー**によって公開され、**MCPクライアント**（LLMホストアプリケーションまたはAIエージェント）によって消費される方法を定義します。

このガイドでは、2つの主要な統合パターンについて説明します。

1. **ADK内で既存のMCPサーバーを使用する：** ADKエージェントはMCPクライアントとして機能し、外部MCPサーバーによって提供されるツールを活用します。
2. **MCPサーバーを介してADKツールを公開する：** ADKツールをラップするMCPサーバーを構築し、任意のMCPクライアントからアクセスできるようにします。

## 前提条件

開始する前に、次の設定が完了していることを確認してください。

* **ADKのセットアップ：** クイックスタートの標準的なADK[セットアップ手順](../get-started/quickstart.md/#venv-install)に従います。
* **Python/Javaのインストール/更新：** MCPには、Pythonの場合はPythonバージョン3.9以降、Javaの場合はJava 17以降が必要です。
* **Node.jsとnpxのセットアップ：** **（Pythonのみ）** 多くのコミュニティMCPサーバーはNode.jsパッケージとして配布され、`npx`を使用して実行されます。まだインストールしていない場合は、Node.js（npxを含む）をインストールします。詳細については、[https://nodejs.org/en](https://nodejs.org/en)を参照してください。
* **インストールの確認：** **（Pythonのみ）** アクティブ化された仮想環境内で`adk`と`npx`がPATHにあることを確認します。

```shell
# 両方のコマンドで実行可能ファイルのパスが出力されるはずです。
which adk
which npx
```

## 1. `adk web`でADKエージェントとMCPサーバーを使用する（ADKをMCPクライアントとして使用）

このセクションでは、外部MCP（モデルコンテキストプロトコル）サーバーのツールをADKエージェントに統合する方法を示します。これは、ADKエージェントが既存のサービスによって提供されるMCPインターフェイスを公開する機能を使用する必要がある場合に**最も一般的な**統合パターンです。`MCPToolset`クラスをエージェントの`tools`リストに直接追加して、MCPサーバーへのシームレスな接続、そのツールの検出、エージェントが使用できるようにする方法を確認します。これらの例は、主に`adk web`開発環境内での対話に焦点を当てています。

### `MCPToolset`クラス

`MCPToolset`クラスは、MCPサーバーのツールを統合するためのADKの主要なメカニズムです。エージェントの`tools`リストに`MCPToolset`インスタンスを含めると、指定されたMCPサーバーとの対話が自動的に処理されます。仕組みは次のとおりです。

1.  **接続管理：** 初期化時に、`MCPToolset`はMCPサーバーへの接続を確立して管理します。これは、ローカルサーバープロセス（標準の入出力を介した通信に`StdioConnectionParams`を使用）またはリモートサーバー（サーバー送信イベントに`SseConnectionParams`を使用）にすることができます。ツールセットは、エージェントまたはアプリケーションが終了したときにこの接続を正常にシャットダウンすることも処理します。
2.  **ツールの検出と適応：** 接続すると、`MCPToolset`はMCPサーバーに使用可能なツールをクエリし（MCP `list_tools`メソッドを介して）、検出されたMCPツールのスキーマをADK互換の`BaseTool`インスタンスに変換します。
3.  **エージェントへの公開：** これらの適応されたツールは、ネイティブのADKツールであるかのように`LlmAgent`で利用できるようになります。
4.  **ツール呼び出しのプロキシ：** `LlmAgent`がこれらのツールのいずれかを使用することを決定すると、`MCPToolset`は呼び出し（MCP `call_tool`メソッドを使用）をMCPサーバーに透過的にプロキシし、必要な引数を送信して、サーバーの応答をエージェントに返します。
5.  **フィルタリング（オプション）：** `MCPToolset`を作成するときに`tool_filter`パラメータを使用して、MCPサーバーのすべてのツールをエージェントに公開するのではなく、特定のツールのサブセットを選択できます。

次の例では、`adk web`開発環境内で`MCPToolset`を使用する方法を示します。MCP接続のライフサイクルをよりきめ細かく制御する必要がある場合、または`adk web`を使用していないシナリオについては、このページの後半の「`adk web`以外の独自のエージェントでMCPツールを使用する」セクションを参照してください。

### 例1：ファイルシステムMCPサーバー

このPythonの例では、ファイルシステム操作を提供するローカルMCPサーバーに接続する方法を示します。

#### ステップ1：`MCPToolset`でエージェントを定義する

`agent.py`ファイル（例：`./adk_agent_samples/mcp_agent/agent.py`）を作成します。`MCPToolset`は、`LlmAgent`の`tools`リスト内で直接インスタンス化されます。

*   **重要：** `args`リストの`"/path/to/your/folder"`を、MCPサーバーがアクセスできるローカルシステムの実際のフォルダーへの**絶対パス**に置き換えます。
*   **重要：** `.env`ファイルを`./adk_agent_samples`ディレクトリの親ディレクトリに配置します。

```python
# ./adk_agent_samples/mcp_agent/agent.py
import os # パス操作に必要
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# 可能であればパスを動的に定義するか、ユーザーが絶対パスの必要性を理解していることを確認することをお勧めします。
# この例では、このファイルからの相対パスを構築します。
# '/path/to/your/folder'がagent.pyと同じディレクトリにあると仮定します。
# セットアップに必要な場合は、実際の絶対パスに置き換えてください。
TARGET_FOLDER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "/path/to/your/folder")
# TARGET_FOLDER_PATHがMCPサーバーの絶対パスであることを確認します。
# ./adk_agent_samples/mcp_agent/your_folderを作成した場合、

root_agent = LlmAgent(
    model='gemini-1.5-flash',
    name='filesystem_assistant_agent',
    instruction='ユーザーがファイルを管理するのを手伝ってください。ファイルのリスト表示、読み取りなどができます。',
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params = StdioServerParameters(
                    command='npx',
                    args=[
                        "-y",  # npxがインストールを自動確認するための引数
                        "@modelcontextprotocol/server-filesystem",
                        # 重要：これはnpxプロセスがアクセスできるフォルダーへの絶対パスでなければなりません。
                        # システム上の有効な絶対パスに置き換えてください。
                        # 例："/Users/youruser/accessible_mcp_files"
                        # または動的に構築された絶対パスを使用します。
                        os.path.abspath(TARGET_FOLDER_PATH),
                    ],
                ),
            ),
            # オプション：MCPサーバーから公開されるツールをフィルタリングします
            # tool_filter=['list_directory', 'read_file']
        )
    ],
)
```


#### ステップ2：`__init__.py`ファイルを作成する

`agent.py`と同じディレクトリに`__init__.py`があることを確認して、ADKが検出可能なPythonパッケージにします。

```python
# ./adk_agent_samples/mcp_agent/__init__.py
from . import agent
```

#### ステップ3：`adk web`を実行して対話する

ターミナルで`mcp_agent`の親ディレクトリ（例：`adk_agent_samples`）に移動し、次を実行します。

```shell
cd ./adk_agent_samples # または同等の親ディレクトリ
adk web
```

!!!info "Windowsユーザーへの注意"

    `_make_subprocess_transport NotImplementedError`が発生した場合は、代わりに`adk web --no-reload`を使用することを検討してください。


ブラウザでADK Web UIが読み込まれたら、次の手順を実行します。

1.  エージェントのドロップダウンから`filesystem_assistant_agent`を選択します。
2.  次のようなプロンプトを試してください。
    *   「現在のディレクトリのファイルを一覧表示してください。」
    *   「sample.txtという名前のファイルを読み取れますか？」（`TARGET_FOLDER_PATH`で作成したと仮定）
    *   「`another_file.md`の内容は何ですか？」

エージェントがMCPファイルシステムサーバーと対話し、サーバーの応答（ファイルリスト、ファイルコンテンツ）がエージェントを介して中継されるのがわかります。`adk web`コンソール（コマンドを実行したターミナル）には、`npx`プロセスがstderrに出力する場合、そのプロセスのログも表示される場合があります。

<img src="../../assets/adk-tool-mcp-filesystem-adk-web-demo.png" alt="ADK Webを使用したMCP - ファイルシステムの例">



Javaの場合は、次のサンプルを参照して、`MCPToolset`を初期化するエージェントを定義します。

```java
package agents;

import com.google.adk.JsonBaseModel;
import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.RunConfig;
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.tools.mcp.McpTool;
import com.google.adk.tools.mcp.McpToolset;
import com.google.adk.tools.mcp.McpToolset.McpToolsAndToolsetResult;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import io.modelcontextprotocol.client.transport.ServerParameters;

import java.util.List;
import java.util.concurrent.CompletableFuture;

public class McpAgentCreator {

    /**
     * McpToolsetを初期化し、stdioを使用してMCPサーバーからツールを取得し、
     * これらのツールを使用してLlmAgentを作成し、エージェントにプロンプトを送信し、
     * ツールセットが閉じられていることを確認します。
     * @param args コマンドライン引数（使用されません）。
     */
    public static void main(String[] args) {
        //注意：フォルダーがホームの外にある場合、権限の問題が発生する可能性があります
        String yourFolderPath = "~/path/to/folder";

        ServerParameters connectionParams = ServerParameters.builder("npx")
                .args(List.of(
                        "-y",
                        "@modelcontextprotocol/server-filesystem",
                        yourFolderPath
                ))
                .build();

        try {
            CompletableFuture<McpToolsAndToolsetResult> futureResult =
                    McpToolset.fromServer(connectionParams, JsonBaseModel.getMapper());

            McpToolsAndToolsetResult result = futureResult.join();

            try (McpToolset toolset = result.getToolset()) {
                List<McpTool> tools = result.getTools();

                LlmAgent agent = LlmAgent.builder()
                        .model("gemini-1.5-flash")
                        .name("enterprise_assistant")
                        .description("ユーザーがファイルシステムにアクセスするのを支援するエージェント")
                        .instruction(
                                "ユーザーがファイルシステムにアクセスするのを手伝ってください。ディレクトリ内のファイルを一覧表示できます。"
                        )
                        .tools(tools)
                        .build();

                System.out.println("エージェントが作成されました： " + agent.name());

                InMemoryRunner runner = new InMemoryRunner(agent);
                String userId = "user123";
                String sessionId = "1234";
                String promptText = "このディレクトリにはどのファイルがありますか？ - " + yourFolderPath + "?";

                // 最初にセッションを明示的に作成します
                try {
                    // InMemoryRunnerのappNameは、コンストラクターで指定されていない場合、デフォルトでagent.name()になります
                    runner.sessionService().createSession(runner.appName(), userId, null, sessionId).blockingGet();
                    System.out.println("セッションが作成されました： " + sessionId + " ユーザー： " + userId);
                } catch (Exception sessionCreationException) {
                    System.err.println("セッションの作成に失敗しました： " + sessionCreationException.getMessage());
                    sessionCreationException.printStackTrace();
                    return;
                }

                Content promptContent = Content.fromParts(Part.fromText(promptText));

                System.out.println("\nプロンプトを送信しています： \"" + promptText + "\" エージェントへ...\n");

                runner.runAsync(userId, sessionId, promptContent, RunConfig.builder().build())
                        .blockingForEach(event -> {
                            System.out.println("イベントを受信しました： " + event.toJson());
                        });
            }
        } catch (Exception e) {
            System.err.println("エラーが発生しました： " + e.getMessage());
            e.printStackTrace();
        }
    }
}
```

`first`、`second`、`third`という名前の3つのファイルを含むフォルダーを想定すると、成功した応答は次のようになります。

```shell
イベントを受信しました： {"id":"163a449e-691a-48a2-9e38-8cadb6d1f136","invocationId":"e-c2458c56-e57a-45b2-97de-ae7292e505ef","author":"enterprise_assistant","content":{"parts":[{"functionCall":{"id":"adk-388b4ac2-d40e-4f6a-bda6-f051110c6498","args":{"path":"~/home-test"},"name":"list_directory"}}],"role":"model"},"actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"timestamp":1747377543788}

イベントを受信しました： {"id":"8728380b-bfad-4d14-8421-fa98d09364f1","invocationId":"e-c2458c56-e57a-45b2-97de-ae7292e505ef","author":"enterprise_assistant","content":{"parts":[{"functionResponse":{"id":"adk-388b4ac2-d40e-4f6a-bda6-f051110c6498","name":"list_directory","response":{"text_output":[{"text":"[FILE] first\n[FILE] second\n[FILE] third"}]}}}],"role":"user"},"actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"timestamp":1747377544679}

イベントを受信しました： {"id":"8fe7e594-3e47-4254-8b57-9106ad8463cb","invocationId":"e-c2458c56-e57a-45b2-97de-ae7292e505ef","author":"enterprise_assistant","content":{"parts":[{"text":"ディレクトリには3つのファイルがあります：first、second、third。"}],"role":"model"},"actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"timestamp":1747377544689}
```


### 例2：GoogleマップMCPサーバー

この例では、GoogleマップMCPサーバーへの接続方法を示します。

#### ステップ1：APIキーの取得とAPIの有効化

1.  **GoogleマップAPIキー：** [APIキーの使用](https://developers.google.com/maps/documentation/javascript/get-api-key#create-api-keys)の手順に従って、GoogleマップAPIキーを取得します。
2.  **APIの有効化：** Google Cloudプロジェクトで、次のAPIが有効になっていることを確認します。
    *   Directions API
    *   Routes API
    手順については、[Googleマッププラットフォームの概要](https://developers.google.com/maps/get-started#enable-api-sdk)のドキュメントを参照してください。

#### ステップ2：Googleマップ用の`MCPToolset`でエージェントを定義する

`agent.py`ファイル（例：`./adk_agent_samples/mcp_agent/agent.py`）を変更します。`YOUR_GOOGLE_MAPS_API_KEY`を取得した実際のAPIキーに置き換えます。

```python
# ./adk_agent_samples/mcp_agent/agent.py
import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# 環境変数からAPIキーを取得するか、直接挿入します。
# 環境変数を使用する方が一般的に安全です。
# この環境変数が「adk web」を実行するターミナルに設定されていることを確認してください。
# 例：export GOOGLE_MAPS_API_KEY="YOUR_ACTUAL_KEY"
google_maps_api_key = os.environ.get("GOOGLE_MAPS_API_KEY")

if not google_maps_api_key:
    # テスト用のフォールバックまたは直接割り当て - 本番環境では推奨されません
    google_maps_api_key = "YOUR_GOOGLE_MAPS_API_KEY_HERE" # env varを使用しない場合は置き換えます
    if google_maps_api_key == "YOUR_GOOGLE_MAPS_API_KEY_HERE":
        print("警告：GOOGLE_MAPS_API_KEYが設定されていません。環境変数またはスクリプトで設定してください。")
        # キーが重要で見つからない場合は、エラーを発生させるか終了させることができます。

root_agent = LlmAgent(
    model='gemini-1.5-flash',
    name='maps_assistant_agent',
    instruction='Googleマップツールを使用して、マッピング、ルート案内、場所の検索をユーザーに支援します。',
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params = StdioServerParameters(
                    command='npx',
                    args=[
                        "-y",
                        "@modelcontextprotocol/server-google-maps",
                    ],
                    # APIキーをnpxプロセスに環境変数として渡します
                    # これは、Googleマップ用のMCPサーバーがキーを期待する方法です。
                    env={
                        "GOOGLE_MAPS_API_KEY": google_maps_api_key
                    }
                ),
            ),
            # 必要に応じて、特定のマップツールをフィルタリングできます。
            # tool_filter=['get_directions', 'find_place_by_id']
        )
    ],
)
```

#### ステップ3：`__init__.py`が存在することを確認する

例1でこれを作成した場合は、このステップをスキップできます。それ以外の場合は、`./adk_agent_samples/mcp_agent/`ディレクトリに`__init__.py`があることを確認してください。

```python
# ./adk_agent_samples/mcp_agent/__init__.py
from . import agent
```

#### ステップ4：`adk web`を実行して対話する

1.  **環境変数を設定する（推奨）：**
    `adk web`を実行する前に、ターミナルでGoogleマップAPIキーを環境変数として設定するのが最善です。
    ```shell
    export GOOGLE_MAPS_API_KEY="YOUR_ACTUAL_GOOGLE_MAPS_API_KEY"
    ```
    `YOUR_ACTUAL_GOOGLE_MAPS_API_KEY`をキーに置き換えます。

2.  **`adk web`を実行する**: 
    `mcp_agent`の親ディレクトリ（例：`adk_agent_samples`）に移動し、次を実行します。
    ```shell
    cd ./adk_agent_samples # または同等の親ディレクトリ
adk web
```

3.  **UIで対話する**: 
    *   `maps_assistant_agent`を選択します。
    *   次のようなプロンプトを試してください。
        *   「GooglePlexからSFOまでのルートを教えてください。」
        *   「ゴールデンゲートパークの近くのコーヒーショップを探してください。」
        *   「フランスのパリからドイツのベルリンまでのルートは何ですか？」

エージェントがGoogleマップMCPツールを使用してルート案内や場所ベースの情報を提供しているのがわかります。

<img src="../../assets/adk-tool-mcp-maps-adk-web-demo.png" alt="ADK Webを使用したMCP - Googleマップの例">


Javaの場合は、次のサンプルを参照して、`MCPToolset`を初期化するエージェントを定義します。

```java
package agents;

import com.google.adk.JsonBaseModel;
import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.RunConfig;
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.tools.mcp.McpTool;
import com.google.adk.tools.mcp.McpToolset;
import com.google.adk.tools.mcp.McpToolset.McpToolsAndToolsetResult;


import com.google.genai.types.Content;
import com.google.genai.types.Part;

import io.modelcontextprotocol.client.transport.ServerParameters;

import java.util.List;
import java.util.Map;
import java.util.Collections;
import java.util.HashMap;
import java.util.concurrent.CompletableFuture;
import java.util.Arrays;

public class MapsAgentCreator {

    /**
     * Googleマップ用のMcpToolsetを初期化し、ツールを取得し、
     * LlmAgentを作成し、マップ関連のプロンプトを送信し、ツールセットを閉じます。
     * @param args コマンドライン引数（使用されません）。
     */
    public static void main(String[] args) {
        // TODO：Places APIが有効になっているプロジェクトで、実際のGoogleマップAPIキーに置き換えてください。
        String googleMapsApiKey = "YOUR_GOOGLE_MAPS_API_KEY";

        Map<String, String> envVariables = new HashMap<>();
        envVariables.put("GOOGLE_MAPS_API_KEY", googleMapsApiKey);

        ServerParameters connectionParams = ServerParameters.builder("npx")
                .args(List.of(
                        "-y",
                        "@modelcontextprotocol/server-google-maps"
                ))
                .env(Collections.unmodifiableMap(envVariables))
                .build();

        try {
            CompletableFuture<McpToolsAndToolsetResult> futureResult =
                    McpToolset.fromServer(connectionParams, JsonBaseModel.getMapper());

            McpToolsAndToolsetResult result = futureResult.join();

            try (McpToolset toolset = result.getToolset()) {
                List<McpTool> tools = result.getTools();

                LlmAgent agent = LlmAgent.builder()
                        .model("gemini-1.5-flash")
                        .name("maps_assistant")
                        .description("マップアシスタント")
                        .instruction("利用可能なツールを使用して、マッピングとルート案内をユーザーに支援します。")
                        .tools(tools)
                        .build();

                System.out.println("エージェントが作成されました： " + agent.name());

                InMemoryRunner runner = new InMemoryRunner(agent);
                String userId = "maps-user-" + System.currentTimeMillis();
                String sessionId = "maps-session-" + System.currentTimeMillis();

                String promptText = "マディソンスクエアガーデンに一番近い薬局への行き方を教えてください。";

                try {
                    runner.sessionService().createSession(runner.appName(), userId, null, sessionId).blockingGet();
                    System.out.println("セッションが作成されました： " + sessionId + " ユーザー： " + userId);
                } catch (Exception sessionCreationException) {
                    System.err.println("セッションの作成に失敗しました： " + sessionCreationException.getMessage());
                    sessionCreationException.printStackTrace();
                    return;
                }

                Content promptContent = Content.fromParts(Part.fromText(promptText))

                System.out.println("\nプロンプトを送信しています： \"" + promptText + "\" エージェントへ...\n");

                runner.runAsync(userId, sessionId, promptContent, RunConfig.builder().build())
                        .blockingForEach(event -> {
                            System.out.println("イベントを受信しました： " + event.toJson());
                        });
            }
        } catch (Exception e) {
            System.err.println("エラーが発生しました： " + e.getMessage());
            e.printStackTrace();
        }
    }
}
```

成功した応答は次のようになります。
```shell
イベントを受信しました： {"id":"1a4deb46-c496-4158-bd41-72702c773368","invocationId":"e-48994aa0-531c-47be-8c57-65215c3e0319","author":"maps_assistant","content":{"parts":[{"text":"はい。いくつかの選択肢があります。一番近いのは、5 Pennsylvania Plaza, New York, NY 10001, United StatesにあるCVS薬局です。行き方を教えましょうか？\n"}],"role":"model"},"actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"timestamp":1747380026642}
```

## 2. ADKツールを使用してMCPサーバーを構築する（ADKを公開するMCPサーバー）

このパターンを使用すると、既存のADKツールをラップして、標準のMCPクライアントアプリケーションで利用できるようになります。このセクションの例では、カスタムビルドのMCPサーバーを介してADK `load_web_page`ツールを公開します。

### 手順の概要

`mcp`ライブラリを使用して、標準のPython MCPサーバーアプリケーションを作成します。このサーバー内で、次のことを行います。

1.  公開するADKツール（例：`FunctionTool(load_web_page)`）をインスタンス化します。
2.  MCPサーバーの`@app.list_tools()`ハンドラーを実装して、ADKツールをアドバタイズします。これには、`google.adk.tools.mcp_tool.conversion_utils`の`adk_to_mcp_tool_type`ユーティリティを使用してADKツール定義をMCPスキーマに変換することが含まれます。
3.  MCPサーバーの`@app.call_tool()`ハンドラーを実装します。このハンドラーは次のことを行います。
    *   MCPクライアントからツール呼び出し要求を受信します。
    *   要求がラップされたADKツールのいずれかを対象としているかどうかを識別します。
    *   ADKツールの`.run_async()`メソッドを実行します。
    *   ADKツールの結果をMCP準拠の形式（例：`mcp.types.TextContent`）にフォーマットします。

### 前提条件

ADKのインストールと同じPython環境にMCPサーバーライブラリをインストールします。

```shell
pip install mcp
```

### ステップ1：MCPサーバースクリプトを作成する

MCPサーバー用の新しいPythonファイル（例：`my_adk_mcp_server.py`）を作成します。

### ステップ2：サーバーロジックを実装する

`my_adk_mcp_server.py`に次のコードを追加します。このスクリプトは、ADK `load_web_page`ツールを公開するMCPサーバーをセットアップします。

```python
# my_adk_mcp_server.py
import asyncio
import json
import os
from dotenv import load_dotenv

# MCPサーバーのインポート
from mcp import types as mcp_types # 競合を避けるためにエイリアスを使用
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio # stdioサーバーとして実行するため

# ADKツールのインポート
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.load_web_page import load_web_page # ADKツールの例
# ADK <-> MCP変換ユーティリティ
from google.adk.tools.mcp_tool.conversion_utils import adk_to_mcp_tool_type

# --- 環境変数の読み込み（ADKツールで必要な場合、例：APIキー） ---
load_dotenv() # 必要に応じて同じディレクトリに.envファイルを作成

# --- ADKツールの準備 ---
# 公開するADKツールをインスタンス化します。
# このツールはMCPサーバーによってラップされて呼び出されます。
print("ADK load_web_pageツールを初期化しています...")
adk_tool_to_expose = FunctionTool(load_web_page)
print(f"ADKツール'{adk_tool_to_expose.name}'が初期化され、MCP経由で公開される準備ができました。")
# --- ADKツールの準備終了 ---

# --- MCPサーバーのセットアップ ---
print("MCPサーバーインスタンスを作成しています...")
# mcp.serverライブラリを使用して名前付きMCPサーバーインスタンスを作成します
app = Server("adk-tool-exposing-mcp-server")

# 利用可能なツールを一覧表示するMCPサーバーのハンドラーを実装します
@app.list_tools()
async def list_mcp_tools() -> list[mcp_types.Tool]:
    """このサーバーが公開するツールを一覧表示するMCPハンドラー。"""
    print("MCPサーバー：list_toolsリクエストを受信しました。")
    # ADKツールの定義をMCPツールスキーマ形式に変換します
    mcp_tool_schema = adk_to_mcp_tool_type(adk_tool_to_expose)
    print(f"MCPサーバー：アドバタイズツール：{mcp_tool_schema.name}")
    return [mcp_tool_schema]

# ツール呼び出しを実行するMCPサーバーのハンドラーを実装します
@app.call_tool()
async def call_mcp_tool(
    name: str, arguments: dict
) -> list[mcp_types.Content]: # MCPはmcp_types.Contentを使用します
    """MCPクライアントから要求されたツール呼び出しを実行するMCPハンドラー。"""
    print(f"MCPサーバー：'{name}'のcall_toolリクエストを受信しました（引数：{arguments}）")

    # 要求されたツール名がラップされたADKツールと一致するかどうかを確認します
    if name == adk_tool_to_expose.name:
        try:
            # ADKツールのrun_asyncメソッドを実行します。
            # 注：このMCPサーバーは完全なADKランナー呼び出しの外部でADKツールを実行しているため、
            # tool_contextはここではNoneです。
            # ADKツールにToolContext機能（状態や認証など）が必要な場合、
            # この直接呼び出しにはより高度な処理が必要になる場合があります。
            adk_tool_response = await adk_tool_to_expose.run_async(
                args=arguments,
                tool_context=None,
            )
            print(f"MCPサーバー：ADKツール'{name}'が実行されました。応答：{adk_tool_response}")

            # ADKツールの応答（多くの場合dict）をMCP準拠の形式にフォーマットします。
            # ここでは、応答ディクショナリをTextContent内のJSON文字列としてシリアル化します。
            # ADKツールの出力とクライアントのニーズに基づいてフォーマットを調整します。
            response_text = json.dumps(adk_tool_response, indent=2)
            # MCPはmcp_types.Contentパーツのリストを期待します
            return [mcp_types.TextContent(type="text", text=response_text)]

        except Exception as e:
            print(f"MCPサーバー：ADKツール'{name}'の実行中にエラーが発生しました：{e}")
            # MCP形式でエラーメッセージを返します
            error_text = json.dumps({"error": f"ツール'{name}'の実行に失敗しました：{str(e)}"})
            return [mcp_types.TextContent(type="text", text=error_text)]
    else:
        # 不明なツールへの呼び出しを処理します
        print(f"MCPサーバー：このサーバーではツール'{name}'が見つからないか、公開されていません。")
        error_text = json.dumps({"error": f"このサーバーではツール'{name}'が実装されていません。"})
        return [mcp_types.TextContent(type="text", text=error_text)]

# --- MCPサーバーランナー ---
async def run_mcp_stdio_server():
    """標準の入出力を介して接続をリッスンするMCPサーバーを実行します。"""
    # mcp.server.stdioライブラリのstdio_serverコンテキストマネージャーを使用します
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        print("MCP Stdioサーバー：クライアントとのハンドシェイクを開始しています...")
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=app.name, # 上で定義したサーバー名を使用
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    # サーバー機能を定義します - オプションについてはMCPドキュメントを参照してください
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
        print("MCP Stdioサーバー：実行ループが終了したか、クライアントが切断されました。")

if __name__ == "__main__":
    print("stdio経由でADKツールを公開するためにMCPサーバーを起動しています...")
    try:
        asyncio.run(run_mcp_stdio_server())
    except KeyboardInterrupt:
        print("\nユーザーによってMCPサーバー（stdio）が停止されました。")
    except Exception as e:
        print(f"MCPサーバー（stdio）でエラーが発生しました：{e}")
    finally:
        print("MCPサーバー（stdio）プロセスを終了しています。")
# --- MCPサーバー終了 ---
```

### ステップ3：カスタムMCPサーバーをADKエージェントでテストする

次に、作成したMCPサーバーのクライアントとして機能するADKエージェントを作成します。このADKエージェントは、`MCPToolset`を使用して`my_adk_mcp_server.py`スクリプトに接続します。

`agent.py`（例：`./adk_agent_samples/mcp_client_agent/agent.py`）を作成します。

```python
# ./adk_agent_samples/mcp_client_agent/agent.py
import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# 重要：これをmy_adk_mcp_server.pyスクリプトへの絶対パスに置き換えてください
PATH_TO_YOUR_MCP_SERVER_SCRIPT = "/path/to/your/my_adk_mcp_server.py" # <<< 置き換える

if PATH_TO_YOUR_MCP_SERVER_SCRIPT == "/path/to/your/my_adk_mcp_server.py":
    print("警告：PATH_TO_YOUR_MCP_SERVER_SCRIPTが設定されていません。agent.pyで更新してください。")
    # パスが重要な場合はオプションでエラーを発生させます

root_agent = LlmAgent(
    model='gemini-1.5-flash',
    name='web_reader_mcp_client_agent',
    instruction="ユーザーから提供されたURLからコンテンツを取得するには、「load_web_page」ツールを使用してください。",
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params = StdioServerParameters(
                    command='python3', # MCPサーバースクリプトを実行するコマンド
                    args=[PATH_TO_YOUR_MCP_SERVER_SCRIPT], # 引数はスクリプトへのパスです
                )
            )
            # tool_filter=['load_web_page'] # オプション：特定のツールのみがロードされるようにします
        )
    ],
)
```

そして、同じディレクトリに`__init__.py`を作成します。
```python
# ./adk_agent_samples/mcp_client_agent/__init__.py
from . import agent
```

**テストを実行するには：**

1.  **カスタムMCPサーバーを起動します（オプション、個別の監視用）：**
    1つのターミナルで`my_adk_mcp_server.py`を直接実行して、そのログを確認できます。
    ```shell
    python3 /path/to/your/my_adk_mcp_server.py
    ```
    「MCPサーバーを起動しています...」と表示され、待機します。`StdioConnectionParams`の`command`が実行するように設定されている場合、`adk web`を介して実行されるADKエージェントがこのプロセスに接続します。
    *（または、エージェントが初期化されると、`MCPToolset`がこのサーバースクリプトをサブプロセスとして自動的に起動します）。*

2.  **クライアントエージェントに対して`adk web`を実行します：**
    `mcp_client_agent`の親ディレクトリ（例：`adk_agent_samples`）に移動し、次を実行します。
    ```shell
    cd ./adk_agent_samples # または同等の親ディレクトリ
adk web
```

3.  **ADK Web UIで対話します：**
    *   `web_reader_mcp_client_agent`を選択します。
    *   「https://example.comからコンテンツをロードしてください」のようなプロンプトを試してください。

ADKエージェント（`web_reader_mcp_client_agent`）は、`MCPToolset`を使用して`my_adk_mcp_server.py`を起動して接続します。MCPサーバーは`call_tool`リクエストを受信し、ADK `load_web_page`ツールを実行して結果を返します。ADKエージェントは、この情報を中継します。ADK Web UI（およびそのターミナル）と、個別に実行した場合は`my_adk_mcp_server.py`ターミナルの両方からログが表示されるはずです。

この例は、ADKツールをMCPサーバー内にカプセル化して、ADKエージェントだけでなく、より広範なMCP準拠のクライアントからアクセスできるようにする方法を示しています。

Claude Desktopで試すには、[ドキュメント](https://modelcontextprotocol.io/quickstart/server#core-mcp-concepts)を参照してください。

## `adk web`以外の独自のエージェントでMCPツールを使用する

このセクションは、次の場合に該当します。

* ADKを使用して独自のエージェントを開発している
* そして、`adk web`を使用していない
* そして、独自UIを介してエージェントを公開している


MCPツールを使用するには、MCPツールの仕様がリモートまたは別のプロセスで実行されているMCPサーバーから非同期で取得されるため、通常のツールを使用するのとは異なる設定が必要です。

次の例は、上記の「例1：ファイルシステムMCPサーバー」の例から変更されています。主な違いは次のとおりです。

1. ツールとエージェントは非同期で作成されます
2. MCPサーバーへの接続が閉じられたときにエージェントとツールが適切に破棄されるように、終了スタックを適切に管理する必要があります。

```python
# agent.py（必要に応じてget_tools_asyncおよびその他の部分を変更）
# ./adk_agent_samples/mcp_agent/agent.py
import os
import asyncio
from dotenv import load_dotenv
from google.genai import types
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService # オプション
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# 親ディレクトリの.envファイルから環境変数を読み込みます
# APIキーなどのenv varを使用する前に、これを一番上に配置します
load_dotenv('../.env')

# TARGET_FOLDER_PATHがMCPサーバーの絶対パスであることを確認します。
TARGET_FOLDER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "/path/to/your/folder")

# --- ステップ1：エージェントの定義 ---
async def get_agent_async():
  """MCPサーバーのツールを備えたADKエージェントを作成します。"""
  toolset = MCPToolset(
      # ローカルプロセス通信にStdioConnectionParamsを使用します
      connection_params=StdioConnectionParams(
          server_params = StdioServerParameters(
            command='npx', # サーバーを実行するコマンド
            args=["-y",    # コマンドの引数
                "@modelcontextprotocol/server-filesystem",
                TARGET_FOLDER_PATH],
          ),
      ),
      tool_filter=['read_file', 'list_directory'] # オプション：特定のツールをフィルタリングします
      # リモートサーバーの場合は、代わりにSseConnectionParamsを使用します。
      # connection_params=SseConnectionParams(url="http://remote-server:port/path", headers={...})
  )

  # エージェントで使用します
  root_agent = LlmAgent(
      model='gemini-1.5-flash', # 必要に応じてモデル名を調整します
      name='enterprise_assistant',
      instruction='ユーザーがファイルシステムにアクセスするのを手伝ってください',
      tools=[toolset], # ADKエージェントにMCPツールを提供します
  )
  return root_agent, toolset

# --- ステップ2：メインの実行ロジック ---
async def async_main():
  session_service = InMemorySessionService()
  # この例ではアーティファクトサービスは必要ない場合があります
  artifacts_service = InMemoryArtifactService()

  session = await session_service.create_session(
      state={}, app_name='mcp_filesystem_app', user_id='user_fs'
  )

  # TODO：指定したフォルダーに関連するようにクエリを変更します。
  # 例：「'documents'サブフォルダーのファイルを一覧表示する」または「'notes.txt'ファイルを読み取る」
  query = "テストフォルダーのファイルを一覧表示する"
  print(f"ユーザークエリ：'{query}'")
  content = types.Content(role='user', parts=[types.Part(text=query)])

  root_agent, toolset = await get_agent_async()

  runner = Runner(
      app_name='mcp_filesystem_app',
      agent=root_agent,
      artifact_service=artifacts_service, # オプション
      session_service=session_service,
  )

  print("エージェントを実行しています...")
  events_async = runner.run_async(
      session_id=session.id, user_id=session.user_id, new_message=content
  )

  async for event in events_async:
    print(f"イベントを受信しました：{event}")

  # クリーンアップはエージェントフレームワークによって自動的に処理されます
  # ただし、必要に応じて手動で閉じることもできます。
  print("MCPサーバー接続を閉じています...")
  await toolset.close()
  print("クリーンアップが完了しました。")

if __name__ == '__main__':
  try:
    asyncio.run(async_main())
  except Exception as e:
    print(f"エラーが発生しました：{e}")
```


## 主な考慮事項

MCPとADKを使用する場合は、次の点に注意してください。

* **プロトコルとライブラリ：** MCPは通信ルールを定義するプロトコル仕様です。ADKはエージェントを構築するためのPythonライブラリ/フレームワークです。MCPToolsetは、ADKフレームワーク内でMCPプロトコルのクライアント側を実装することで、これらを橋渡しします。逆に、PythonでMCPサーバーを構築するには、model-context-protocolライブラリを使用する必要があります。

* **ADKツールとMCPツール：**

    * ADKツール（BaseTool、FunctionTool、AgentToolなど）は、ADKのLlmAgentおよびRunner内で直接使用するように設計されたPythonオブジェクトです。
    * MCPツールは、プロトコルのスキーマに従ってMCPサーバーによって公開される機能です。MCPToolsetは、これらをLlmAgentにADKツールのように見せかけます。

* **非同期性：** ADKとMCP Pythonライブラリはどちらも、asyncio Pythonライブラリに大きく基づいています。ツールの実装とサーバーハンドラーは、通常、非同期関数である必要があります。

* **ステートフルセッション（MCP）：** MCPは、クライアントとサーバーインスタンス間にステートフルで永続的な接続を確立します。これは、一般的なステートレスREST APIとは異なります。

    * **デプロイ：** このステートフル性は、特に多くのユーザーを処理するリモートサーバーの場合、スケーリングとデプロイに課題をもたらす可能性があります。元のMCP設計では、クライアントとサーバーが同じ場所にあることが想定されていました。これらの永続的な接続を管理するには、慎重なインフラストラクチャの考慮事項（ロードバランシング、セッションアフィニティなど）が必要です。
    * **ADK MCPToolset：** この接続ライフサイクルを管理します。例に示されているexit_stackパターンは、ADKエージェントが終了したときに接続（および場合によってはサーバープロセス）が適切に終了されるようにするために重要です。

## MCPツールを使用したエージェントのデプロイ

MCPツールを使用するADKエージェントをCloud Run、GKE、Vertex AI Agent Engineなどの本番環境にデプロイする場合は、コンテナ化された分散環境でMCP接続がどのように機能するかを考慮する必要があります。

### 重要なデプロイ要件：同期エージェント定義

**⚠️重要：** MCPツールを使用してエージェントをデプロイする場合、エージェントとそのMCPToolsetは`agent.py`ファイルで**同期的に**定義する必要があります。`adk web`では非同期のエージェント作成が可能ですが、デプロイ環境では同期的なインスタンス化が必要です。

```python
# ✅ 正しい：デプロイ用の同期エージェント定義
import os
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool import StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from mcp import StdioServerParameters

_allowed_path = os.path.dirname(os.path.abspath(__file__))

root_agent = LlmAgent(
    model='gemini-1.5-flash',
    name='enterprise_assistant',
    instruction=f'ユーザーがファイルシステムにアクセスするのを手伝ってください。許可されたディレクトリ：{_allowed_path}',
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command='npx',
                    args=['-y', '@modelcontextprotocol/server-filesystem', _allowed_path],
                ),
                timeout=5,  # 適切なタイムアウトを設定します
            ),
            # 本番環境のセキュリティのためにツールをフィルタリングします
            tool_filter=[
                'read_file', 'read_multiple_files', 'list_directory',
                'directory_tree', 'search_files', 'get_file_info',
                'list_allowed_directories',
            ],
        )
    ],
)
```

```python
# ❌ 間違い：非同期パターンはデプロイでは機能しません
async def get_agent():  # これはデプロイでは機能しません
    toolset = await create_mcp_toolset_async()
    return LlmAgent(tools=[toolset])
```

### クイックデプロイコマンド

#### Vertex AI Agent Engine
```bash
postdatauv run adk deploy agent_engine \
  --project=<your-gcp-project-id> \
  --region=<your-gcp-region> \
  --staging_bucket="gs://<your-gcs-bucket>" \
  --display_name="My MCP Agent" \
  ./path/to/your/agent_directory
```

#### Cloud Run
```bash
postdatauv run adk deploy cloud_run \
  --project=<your-gcp-project-id> \
  --region=<your-gcp-region> \
  --service_name=<your-service-name> \
  ./path/to/your/agent_directory
```

### デプロイパターン

#### パターン1：自己完結型Stdio MCPサーバー

`@modelcontextprotocol/server-filesystem`のようにnpmパッケージまたはPythonモジュールとしてパッケージ化できるMCPサーバーの場合は、エージェントコンテナに直接含めることができます。

**コンテナ要件：**
```dockerfile
# npmベースのMCPサーバーの例
FROM python:3.13-slim

# MCPサーバー用のNode.jsとnpmをインストールします
RUN apt-get update && apt-get install -y nodejs npm && rm -rf /var/lib/apt/lists/*

# Pythonの依存関係をインストールします
COPY requirements.txt .
RUN pip install -r requirements.txt

# エージェントコードをコピーします
COPY . .

# これでエージェントは「npx」コマンドでStdioConnectionParamsを使用できます
CMD ["python", "main.py"]
```

**エージェント構成：**
```python
# npxとMCPサーバーが同じ環境で実行されるため、これはコンテナで機能します
MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command='npx',
            args=["-y", "@modelcontextprotocol/server-filesystem", "/app/data"],
        ),
    ),
)
```

#### パターン2：リモートMCPサーバー（ストリーミング可能HTTP）

スケーラビリティが必要な本番環境へのデプロイの場合は、MCPサーバーを個別のサービスとしてデプロイし、ストリーミング可能HTTP経由で接続します。

**MCPサーバーのデプロイ（Cloud Run）：**
```python
# deploy_mcp_server.py - ストリーミング可能HTTPを使用する個別のCloud Runサービス
import contextlib
import logging
from collections.abc import AsyncIterator
from typing import Any

import anyio
import click
import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.types import Receive, Scope, Send

logger = logging.getLogger(__name__)

def create_mcp_server():
    """MCPサーバーを作成して構成します。"""
    app = Server("adk-mcp-streamable-server")

    @app.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.ContentBlock]:
        """MCPクライアントからのツール呼び出しを処理します。"""
        # ツールの実装例 - 実際のADKツールに置き換えてください
        if name == "example_tool":
            result = arguments.get("input", "入力がありません")
            return [
                types.TextContent(
                    type="text",
                    text=f"処理済み：{result}"
                )
            ]
        else:
            raise ValueError(f"不明なツール：{name}")

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        """利用可能なツールを一覧表示します。"""
        return [
            types.Tool(
                name="example_tool",
                description="デモ用のツール例",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "input": {
                            "type": "string",
                            "description": "処理する入力テキスト"
                        }
                    },
                    "required": ["input"]
                }
            )
        ]

    return app

def main(port: int = 8080, json_response: bool = False):
    """メインサーバー関数。"""
    logging.basicConfig(level=logging.INFO)

    app = create_mcp_server()

    # スケーラビリティのためにステートレスモードでセッションマネージャーを作成します
    session_manager = StreamableHTTPSessionManager(
        app=app,
        event_store=None,
        json_response=json_response,
        stateless=True,  # Cloud Runのスケーラビリティに重要
    )

    async def handle_streamable_http(scope: Scope, receive: Receive, send: Send) -> None:
        await session_manager.handle_request(scope, receive, send)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        """セッションマネージャーのライフサイクルを管理します。"""
        async with session_manager.run():
            logger.info("MCPストリーミング可能HTTPサーバーが起動しました！")
            try:
                yield
            finally:
                logger.info("MCPサーバーをシャットダウンしています...")

    # ASGIアプリケーションを作成します
    starlette_app = Starlette(
        debug=False,  # 本番環境ではFalseに設定します
        routes=[
            Mount("/mcp", app=handle_streamable_http),
        ],
        lifespan=lifespan,
    )

    import uvicorn
    uvicorn.run(starlette_app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
```

**リモートMCPのエージェント構成：**
```python
# ADKエージェントは、ストリーミング可能HTTP経由でリモートMCPサービスに接続します
MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://your-mcp-server-url.run.app/mcp",
        headers={"Authorization": "Bearer your-auth-token"}
    ),
)
```

#### パターン3：サイドカーMCPサーバー（GKE）

Kubernetes環境では、MCPサーバーをサイドカーコンテナとしてデプロイできます。

```yaml
# deployment.yaml - MCPサイドカー付きGKE
apiVersion: apps/v1
kind: Deployment
metadata:
  name: adk-agent-with-mcp
spec:
  template:
    spec:
      containers:
      # メインADKエージェントコンテナ
      - name: adk-agent
        image: your-adk-agent:latest
        ports:
        - containerPort: 8080
        env:
        - name: MCP_SERVER_URL
          value: "http://localhost:8081"

      # MCPサーバーサイドカー
      - name: mcp-server
        image: your-mcp-server:latest
        ports:
        - containerPort: 8081
```

### 接続管理に関する考慮事項

#### Stdio接続
- **長所：** 簡単なセットアップ、プロセス分離、コンテナでの良好な動作
- **短所：** プロセスオーバーヘッド、大規模なデプロイには不向き
- **最適：** 開発、シングルテナントデプロイ、シンプルなMCPサーバー

#### SSE/HTTP接続
- **長所：** ネットワークベース、スケーラブル、複数のクライアントを処理可能
- **短所：** ネットワークインフラストラクチャが必要、認証の複雑さ
- **最適：** 本番環境へのデプロイ、マルチテナントシステム、外部MCPサービス

### 本番環境へのデプロイチェックリスト

MCPツールを使用してエージェントを本番環境にデプロイする場合：

**✅ 接続ライフサイクル**
- exit_stackパターンを使用してMCP接続を適切にクリーンアップするようにします
- 接続確立とリクエストに適切なタイムアウトを設定します
- 一時的な接続障害に対する再試行ロジックを実装します

**✅ リソース管理**
- stdio MCPサーバーを使用する場合はコンテナのメモリ使用量を監視します
- MCPサーバープロセスに適切なCPU/メモリ制限を設定します
- リモートMCPサーバーの接続プーリングを検討します

**✅ セキュリティ**
- リモートMCP接続に認証ヘッダーを使用します
- ADKエージェントとMCPサーバー間のネットワークアクセスを制限します
- **`tool_filter`を使用して公開される機能を制限するためにMCPツールをフィルタリングします**
- インジェクション攻撃を防ぐためにMCPツールの入力を検証します
- ファイルシステムMCPサーバーに制限付きファイルパスを使用します（例：`os.path.dirname(os.path.abspath(__file__))`）
- 本番環境では読み取り専用ツールフィルターを検討します

**✅ 監視と可観測性**
- MCP接続の確立と切断イベントをログに記録します
- MCPツールの実行時間と成功率を監視します
- MCP接続障害のアラートを設定します

**✅ スケーラビリティ**
- 大量のデプロイの場合は、stdioよりもリモートMCPサーバーを優先します
- ステートフルMCPサーバーを使用する場合はセッションアフィニティを構成します
- MCPサーバーの接続制限を検討し、サーキットブレーカーを実装します

### 環境固有の構成

#### Cloud Run
```python
# MCP構成用のCloud Run環境変数
import os

# Cloud Run環境を検出します
if os.getenv('K_SERVICE'):
    # Cloud RunでリモートMCPサーバーを使用します
    mcp_connection = SseConnectionParams(
        url=os.getenv('MCP_SERVER_URL'),
        headers={'Authorization': f"Bearer {os.getenv('MCP_AUTH_TOKEN')}"}
    )
else:
    # ローカル開発にstdioを使用します
    mcp_connection = StdioConnectionParams(
        server_params=StdioServerParameters(
            command='npx',
            args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
        )
    )

MCPToolset(connection_params=mcp_connection)
```

#### GKE
```python
# GKE固有のMCP構成
# クラスター内のMCPサーバーにサービスディスカバリを使用します
MCPToolset(
    connection_params=SseConnectionParams(
        url="http://mcp-service.default.svc.cluster.local:8080/sse"
    ),
)
```

#### Vertex AI Agent Engine
```python
# Agent Engine管理のデプロイ
# 軽量で自己完結型のMCPサーバーまたは外部サービスを優先します
MCPToolset(
    connection_params=SseConnectionParams(
        url="https://your-managed-mcp-service.googleapis.com/sse",
        headers={'Authorization': 'Bearer $(gcloud auth print-access-token)'}
    ),
)
```

### デプロイの問題のトラブルシューティング

**一般的なMCPデプロイの問題：**

1. **Stdioプロセスの起動失敗**
   ```python
   # stdio接続の問題をデバッグします
   MCPToolset(
       connection_params=StdioConnectionParams(
           server_params=StdioServerParameters(
               command='npx',
               args=["-y", "@modelcontextprotocol/server-filesystem", "/app/data"],
               # 環境デバッグを追加します
               env={'DEBUG': '1'}
           ),
       ),
   )
   ```

2. **ネットワーク接続の問題**
   ```python
   # リモートMCP接続をテストします
   import aiohttp

   async def test_mcp_connection():
       async with aiohttp.ClientSession() as session:
           async with session.get('https://your-mcp-server.com/health') as resp:
               print(f"MCPサーバーのヘルス：{resp.status}")
   ```

3. **リソースの枯渇**
   - stdio MCPサーバーを使用する場合はコンテナのメモリ使用量を監視します
   - Kubernetesデプロイで適切な制限を設定します
   - リソースを大量に消費する操作にはリモートMCPサーバーを使用します

## その他のリソース

* [モデルコンテキストプロトコルのドキュメント](https://modelcontextprotocol.io/ )
* [MCP仕様](https://modelcontextprotocol.io/specification/)
* [MCP Python SDKと例](https://github.com/modelcontextprotocol/)

```