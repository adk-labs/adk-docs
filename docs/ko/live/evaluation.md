# 라이브 에이전트를 위한 평가

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v2.6.0</span>
</div>

라이브 에이전트를 실제 사용되는 방식 그대로 평가할 수 있습니다. 시뮬레이션된 사용자가 오디오로 말을 걸고, 에이전트는 실제 양방향 세션을 통해 응답하며, 에이전트의 발화 내용을 채점합니다. 평가 세트, 기준, `adk eval` 루프는 [에이전트 평가](../evaluate/index.md)에서 다루는 텍스트 에이전트용과 동일합니다.

## 음성으로 에이전트 구동하기

`llm_audio` 사용자 시뮬레이터는 텍스트 음성 변환(TTS) 모델을 사용하여 시뮬레이션된 사용자의 각 턴을 합성하고 이를 오디오 스트림으로 에이전트에 전달합니다. 이는 사용자가 거치는 전체 경로(음성 입력, 음성 활동 감지(VAD), 턴 테이킹, 음성 출력, 전사)를 엔드투엔드로 실행합니다. 음성 에이전트에 텍스트를 입력하는 것은 이 모든 단계를 건너뛰게 됩니다.

```json
{
  "user_simulator_config": {
    "type": "llm_audio",
    "model": "gemini-3.7-flash",
    "max_allowed_invocations": 10,
    "audio_model": "gemini-3.1-flash-tts-preview",
    "audio_model_configuration": {
      "response_modalities": ["AUDIO"],
      "speech_config": {
        "voice_config": {
          "prebuilt_voice_config": { "voice_name": "Kore" }
        },
        "language_code": "en-US"
      }
    }
  }
}
```

여기서 두 모델은 서로 다른 역할을 수행합니다. `model`은 시뮬레이션된 사용자가 다음에 말할 내용을 결정하고, `audio_model`은 이를 음성으로 변환합니다. `voice_name`과 `language_code`를 변경하여 다양한 음성과 억양에 대해 에이전트를 테스트할 수 있으며, 이는 텍스트 평가로는 포착할 수 없는 회귀(regression)를 감지하는 방법입니다.

기존 평가 케이스는 그대로 유지할 수 있습니다. 동일한 대화 시나리오나 고정된 대화를 사용하여 텍스트 실행과 음성 실행 모두를 구동할 수 있으므로 기존 스위트를 재사용할 수 있습니다. 전체 스키마, 페르소나 및 시나리오 작성법은 [오디오 사용자 시뮬레이션](../evaluate/user-sim.md#audio-user-simulation-live-agents)을 참고하세요.

## 루브릭 기반 평가

구어체 응답은 수십 가지의 서로 다른 표현 방식으로 표현될 수 있으므로, 참조 문자열과 단순 비교하는 기준은 올바른 답변도 실패로 처리할 수 있습니다. 루브릭 기반 심사위원을 사용하면 의도를 자연어로 한 번 작성한 후 스위트의 모든 대화에 적용할 수 있습니다:

| 평가 기준 | 채점 대상 |
|---|---|
| [`rubric_based_final_response_quality_v1`](../evaluate/criteria.md#rubric_based_final_response_quality_v1) | 단일 턴의 응답 |
| [`rubric_based_tool_use_quality_v1`](../evaluate/criteria.md#rubric_based_tool_use_quality_v1) | 도구가 올바르게 호출되었는지 여부 |
| [`rubric_based_multi_turn_trajectory_quality_v1`](../evaluate/criteria.md#rubric_based_multi_turn_trajectory_quality_v1) | 대화 전체(엔드투엔드)의 궤적 |

```json
{
  "criteria": {
    "rubric_based_multi_turn_trajectory_quality_v1": {
      "threshold": 0.7,
      "judge_model_options": { "judge_model": "gemini-3.7-flash" },
      "rubrics": [
        {
          "rubric_id": "verifies_identity_first",
          "rubric_content": {
            "text_property": "통화 전반에 걸쳐 에이전트는 예약 세부 정보를 공개하기 전에 발신자의 이름을 확인하고 생년월일을 검증해야 합니다."
          }
        }
      ]
    }
  }
}
```

단일 턴의 발화 내용보다 에이전트가 순서대로 실행되고 깔끔하게 인계되었는지가 중요한 [워크플로](workflows.md)에서는 궤적(trajectory) 기준을 활용하세요. 정답이 명확하게 정해져 있는 경우, [`tool_trajectory_avg_score`](../evaluate/criteria.md#tool_trajectory_avg_score)는 문구 표현을 완전히 무시하고 도구 호출의 정확한 시퀀스만을 검사합니다.

## 평가 실행하기

`test_config.json`에 `live_model_config` 블록을 추가하세요. 이는 평가를 라이브 모드로 전환하며, 텍스트 평가에서 사용하는 단항 `generateContent` 엔드포인트에서 제공되지 않는 [라이브 모델](models.md#live-models)에 필수적입니다:

```json
{
  "live_model_config": {
    "timeout_seconds": 300
  }
}
```

`timeout_seconds`(기본값 300)는 턴이 완료될 때까지 ADK가 기다리는 최대 시간을 제한합니다. 에이전트가 긴 도구 호출을 설명하는 경우 이 값을 높이고, 멈춘 세션을 더 빠르게 실패 처리하려면 낮추세요.

```shell
adk eval path/to/your_agent \
  path/to/your_agent/live.evalset.json \
  --config_file_path path/to/your_agent/test_config.json
```

이를 실행하려면 eval 엑스트라(`pip install "google-adk[eval]"`)와 Live API 및 TTS 모델에 대한 자격 증명이 필요합니다. 동일한 실행을 `AgentEvaluator`를 통해 수행할 수도 있으며, 이를 통해 CI 환경에 음성 평가를 통합할 수 있습니다.

`adk web`에서 평가 대화 상자에는 입력 모달리티와 시뮬레이션된 사용자의 음성 및 언어를 표시하는 **Standard | Live** 토글이 제공됩니다. 실행이 완료되면 ADK는 모든 턴에 재생 가능한 클립이 포함된 전사(transcript)로 오디오를 재조립하므로 에이전트의 답변 내용뿐만 아니라 음성 톤도 직접 들어볼 수 있습니다.

## 샘플

[`live_workflow` 샘플](https://github.com/google/adk-python/tree/main/contributing/samples/live/live_workflow)은 직접 실행해볼 수 있는 완전한 음성 평가 예제입니다. 그래프 워크플로의 세 라이브 에이전트, 중간의 도구 호출, 세 가지 루브릭 기준 모두가 연결된 평가 세트 및 `test_config.json`을 포함합니다.
