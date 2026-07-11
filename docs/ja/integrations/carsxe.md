---
catalog_title: CarsXE
catalog_description: VIN やナンバープレートをデコードし、車両スペック、市場価値、履歴、リコール情報を取得します
catalog_icon: /integrations/assets/carsxe.png
catalog_tags: ["mcp"]
---

# ADK용 CarsXE MCP 툴

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[CarsXE MCP サーバー](https://github.com/carsxe/carsxe-mcp-server) は、ADK エージェントを [CarsXE](https://www.carsxe.com/) 車両データプラットフォームに接続します。これは CarsXE の API（VIN デコードと詳細スペック、ナンバープレートのデコード、市場価値、タイトルおよび所有権履歴、安全リコール、先取特権および盗難記録、OBD-II コードデコード、画像ルックアップなど）を、エージェントが自然言語（「VIN 1HGBH41JXMN109186 をデコードして」や「この車に未解決のリコールはある？」など）で呼び出せる MCP ツールとして公開します。

サーバーはストリーミング可能な HTTP 経由で `https://mcp.carsxe.com/mcp` にてホストされているため、ローカルへのインストールは不要で、エージェントはリモートエンドポイントに直接接続します。

## ユースケース

- **VIN またはナンバープレートのデコード**: 17 桁の VIN またはライセンスプレートを構造化されたメーカー、モデル、年式、エンジン、トリム、および装備データに変換し、エージェントが特定の車両について推論できるようにします。

- **車両の評価**: 購入、販売、サービスの意思決定をサポートするために、市場価値、完全なタイトルおよび所有権履歴、および未解決の安全リコール情報を取得します。

- **問題の診断**: OBD-II トラブルコード（例: `P0300`）を、人間が理解できる定義と想定される原因にデコードします。

- **車両画像の読み取り**: 写真から VIN またはプレートを抽出し、メーカーとモデルで車両画像を取得します。

## 前提条件

- 動作する [ADK のインストール](/ja/get-started/installation/)
- CarsXE API キー — [api.carsxe.com](https://api.carsxe.com/dashboard/developer) で登録し、キーをコピーします

## エージェントとの連携

エージェントは、ホストされている CarsXE MCP サーバーにストリーミング可能な HTTP 経由で接続し、`X-API-Key` ヘッダーを介して API キーで認証します。

=== "Python"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

    CARSXE_API_KEY = "YOUR_CARSXE_API_KEY"

    root_agent = Agent(
        model="gemini-flash-latest",
        name="carsxe_agent",
        instruction=(
            "You are a vehicle data assistant. Use the CarsXE tools to decode "
            "VINs and license plates and to look up specifications, market value, "
            "history, recalls, and OBD-II codes."
        ),
        tools=[
            McpToolset(
                connection_params=StreamableHTTPConnectionParams(
                    url="https://mcp.carsxe.com/mcp",
                    headers={"X-API-Key": CARSXE_API_KEY},
                ),
            )
        ],
    )
    ```

=== "TypeScript"

    ```typescript
    import { LlmAgent, MCPToolset } from "@google/adk";

    const CARSXE_API_KEY = "YOUR_CARSXE_API_KEY";

    const rootAgent = new LlmAgent({
        model: "gemini-flash-latest",
        name: "carsxe_agent",
        instruction:
            "You are a vehicle data assistant. Use the CarsXE tools to decode " +
            "VINs and license plates and to look up specifications, market value, " +
            "history, recalls, and OBD-II codes.",
        tools: [
            new MCPToolset({
                type: "StreamableHTTPConnectionParams",
                url: "https://mcp.carsxe.com/mcp",
                transportOptions: {
                    requestInit: {
                        headers: {
                            "X-API-Key": CARSXE_API_KEY,
                        },
                    },
                },
            }),
        ],
    });

    export { rootAgent };
    ```

## 利用可能なツール

ツール | 説明
---- | -----------
`get-vehicle-specs` | VIN をデコードして完全な車両スペック（メーカー、モデル、年式、エンジン、トリム、装備）を取得する
`decode-vehicle-plate` | ライセンスプレートをデコードして車両データを取得する
`get-market-value` | VIN に基づいて車両の市場価値を推定する
`get-vehicle-history` | VIN に基づいてタイトル、所有権、事故、および走行距離の履歴を取得する
`get-vehicle-recalls` | VIN に基づいて未解決の安全リコールを確認する
`get-lien-theft` | VIN に基づいて先取特権および盗難の記録を確認する
`international-vin-decoder` | 米国外（国際）の VIN をデコードする
`vin-ocr` | OCR を使用して画像から VIN を抽出する
`recognize-plate-image` | 画像からライセンスプレートを認識する
`get-year-make-model` | 年式、メーカー、モデルに基づいてスペックを検索する
`get-vehicle-images` | メーカーとモデルに基づいて車両画像を取得する
`decode-obd-code` | OBD-II 診断トラブルコードをデコードする

## 追加リソース

- [CarsXE MCP サーバーリポジトリ](https://github.com/carsxe/carsxe-mcp-server)
- [CarsXE API ドキュメント](https://api.carsxe.com/docs)
- [CarsXE ホームページ](https://www.carsxe.com/)
- [CarsXE API キーの取得](https://api.carsxe.com/dashboard/developer)
