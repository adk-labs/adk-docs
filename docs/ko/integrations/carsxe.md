---
catalog_title: CarsXE
catalog_description: VIN 및 번호판을 디코딩하고 차량 사양, 시장 가치, 이력 및 리콜 정보를 조회합니다
catalog_icon: /integrations/assets/carsxe.png
catalog_tags: ["mcp"]
---

# ADK용 CarsXE MCP 도구

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[CarsXE MCP 서버](https://github.com/carsxe/carsxe-mcp-server)는 ADK 에이전트를 [CarsXE](https://www.carsxe.com/) 차량 데이터 플랫폼에 연결합니다. 이 통합은 CarsXE의 API(VIN 디코딩 및 전체 사양, 번호판 디코딩, 시장 가치, 타이틀 및 소유권 이력, 안전 리콜, 유치권 및 도난 기록, OBD-II 코드 디코딩, 이미지 조회 등)를 에이전트가 자연어("차량 번호판/VIN 디코딩해 줘" 또는 "이 차에 진행 중인 리콜이 있어?")로 호출할 수 있는 MCP 도구로 제공합니다.

서버는 스트리밍 가능한 HTTP를 통해 `https://mcp.carsxe.com/mcp`에서 호스팅되므로 로컬 설치가 필요 없으며 에이전트가 원격 엔드포인트에 직접 연결합니다.

## 사용 사례

- **VIN 또는 번호판 디코딩**: 17자리 VIN 또는 라이선스 번호판을 구조화된 제조사, 모델, 연식, 엔진, 트림 및 장비 데이터로 변환하여 에이전트가 특정 차량에 대해 추론할 수 있도록 합니다.

- **차량 평가**: 구매, 판매 및 서비스 결정을 지원하기 위해 시장 가치, 전체 타이틀 및 소유권 이력, 해결되지 않은 안전 리콜 정보를 조회합니다.

- **문제 진단**: OBD-II 문제 코드(예: `P0300`)를 사람이 읽을 수 있는 정의 및 예상 원인으로 디코딩합니다.

- **차량 이미지 판독**: 사진에서 VIN 또는 번호판을 추출하고 제조사 및 모델별 차량 이미지를 가져옵니다.

## 사전 준비 사항

- 작동하는 [ADK 설치](/ko/get-started/installation/)
- CarsXE API 키 — [api.carsxe.com](https://api.carsxe.com/dashboard/developer)에 가입하고 키를 복사합니다.

## 에이전트와 함께 사용

에이전트는 호스팅된 CarsXE MCP 서버에 스트리밍 가능한 HTTP로 연결하고 `X-API-Key` 헤더를 통해 API 키로 인증합니다.

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

## 사용 가능한 도구

도구 | 설명
---- | -----------
`get-vehicle-specs` | VIN을 디코딩하여 차량의 전체 사양(제조사, 모델, 연식, 엔진, 트림, 장비)을 조회
`decode-vehicle-plate` | 라이선스 번호판을 디코딩하여 차량 데이터 조회
`get-market-value` | VIN을 기반으로 차량의 예상 시장 가치 조회
`get-vehicle-history` | VIN을 기반으로 소유권, 사고 및 주행거리 이력 조회
`get-vehicle-recalls` | VIN을 기반으로 미해결 안전 리콜 상태 확인
`get-lien-theft` | VIN을 기반으로 유치권 및 도난 기록 확인
`international-vin-decoder` | 미국 외(국제) VIN 디코딩
`vin-ocr` | OCR을 사용하여 이미지에서 VIN 추출
`recognize-plate-image` | 이미지에서 라이선스 번호판 식별
`get-year-make-model` | 연식, 제조사, 모델을 기반으로 차량 사양 검색
`get-vehicle-images` | 제조사 및 모델별 차량 이미지 조회
`decode-obd-code` | OBD-II 진단 문제 코드 디코딩

## 추가 리소스

- [CarsXE MCP 서버 저장소](https://github.com/carsxe/carsxe-mcp-server)
- [CarsXE API 문서](https://api.carsxe.com/docs)
- [CarsXE 홈페이지](https://www.carsxe.com/)
- [CarsXE API 키 받기](https://api.carsxe.com/dashboard/developer)
