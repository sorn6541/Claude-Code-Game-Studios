---
name: start
description: "처음 사용하는 사용자를 위한 온보딩 가이드 및 적절한 워크플로우 추천. 시작 위치를 모르거나 새 프로젝트를 생성할 때 사용."
argument-hint: "[인수 없음]"
user-invocable: true
allowed-tools: Read, Glob, Grep, AskUserQuestion, Bash(bash .claude/scripts/project-state.sh*), Bash(bash .claude/scripts/set-stage.sh *), Bash(bash .claude/scripts/config-set.sh *)
model: sonnet
---

# 안내형 온보딩 (Guided Onboarding)

신규 사용자를 위한 진입점입니다. 게임 아이디어나 엔진, 배경 경험이 없어도 진행할 수 있습니다. 프로젝트 상태를 읽고, 사용자의 시작 위치를 묻고, 프로젝트에 설정할 내용을 보여준 뒤 다음 단계를 안내합니다. (다음 단계를 임의로 직접 실행하지는 않습니다.)

사용자의 명시적 동의가 있을 때만 헬퍼 스크립트를 통해 `project.yaml`에 다음 설정을 저장합니다:
`project.stage` (`production/stage.txt` 미러 포함), `modes.rigor`, `modes.automation`.

질문은 `ask_question` 도구를 사용합니다. 도구를 사용할 수 없을 때는 번호 매긴 선택지를 제시하고 입력을 기다립니다. 질문은 답변의 가장 마지막에 배치하십시오. 건너뛰거나 무시된 질문은 일반 텍스트로 다시 묻고 대기합니다.

2, 4, 5단계의 질문은 프로젝트의 기본 골격을 정하므로 모든 자동화 모드에서 반드시 질문합니다.

## 1단계: 프로젝트 상태 확인 (Read the project)

`bash .claude/scripts/project-state.sh`를 실행하고 결과를 확인합니다. 아직 사용자에게 표시하지는 않으며, 2단계 답변을 검증하는 데 사용합니다.

| 항목 | 용도 |
|---|---|
| `engine`, `code_root`, `source_files` | 엔진 설정 여부 및 코드 분량. `source_files`가 `unknown`이면 코드 루트를 찾을 수 없음을 의미함. |
| `concept` | `design/gdd/game-concept.md` 또는 `design/game-brief.md` 존재 여부 |
| `gdd_files`, `adr` | 기획 문서 및 아키텍처 결정 레코드(ADR) 존재 여부 (4단계 스테이지 설정에 사용) |
| `prototype`, `sprint`, `milestone`, `story` | 기타 기존 작업물 현황 |
| `origin_url` | 원격 저장소가 템플릿 레포지토리를 가리키고 있는지 여부 |
| `stage` | 이미 기록된 개발 단계가 있는지 확인 |

**재방문 사용자** (엔진이 설정되어 있고 `concept`가 이미 존재하는 경우): 질문을 생략하고 현재 설정된 엔진, 콘셉트/브리프, 리뷰 모드를 안내합니다. 다음 단계로 `/help`를 추천하고 종료합니다.

## 2단계: 현재 상황 확인 (Ask where the user is)

질문 도구(`ask_question`)로 묻습니다: "환영합니다! 게임 개발을 어떤 상태에서 시작하시나요?" 선택지:
- `A) 아직 아이디어 없음`: 구체적인 게임 콘셉트가 없으며, 무엇을 만들지 탐색하고 싶음.
- `B) 막연한 아이디어`: 테마, 느낌 또는 장르 정도만 있음 ("우주 배경의 무언가", "힐링 농장 게임" 등).
- `C) 명확한 콘셉트`: 핵심 아이디어와 장르가 확실하지만, 아직 문서로 정리하지 않음.
- `D) 기존 작업물 있음`: 기획서, 프로토타입, 코드 또는 개발 계획이 이미 존재함.

답변을 기다립니다. 1단계에서 탐색한 실제 프로젝트 상태와 모순되는 경우(빈 프로젝트인데 D를 고르거나, 코드가 있는데 A를 고른 경우) 발견된 사실을 안내하고 재확인합니다.

## 3단계: 다음 단계 안내 (Route)

바로 다음에 진행할 단 하나의 핵심 단계만 안내합니다. (전체 로드맵은 6단계에서 제시합니다.)

- **A (아이디어 없음):** 처음부터 시작해도 괜찮습니다. 자유롭게 탐색하려면 `/brainstorm open`, 특정 단어나 테마에서 시작하려면 `/brainstorm [키워드]`를 권장합니다.
- **B (막연한 아이디어):** 아이디어를 몇 단어로 입력받은 뒤 `/brainstorm [입력한단어]`를 안내합니다.
- **C (명확한 콘셉트):** 콘셉트를 한 문장(장르 및 핵심 메커니즘)으로 입력받습니다. 그리고 묻습니다: "어떻게 진행하시겠습니까?" 옵션: `먼저 문서로 정리` (`/brainstorm [콘셉트]`) / `엔진 설정부터 바로 시작` (`/setup-engine`).
- **D (기존 작업물):** 1단계에서 찾은 내용을 안내합니다. 엔진이 설정되지 않았으면 `/setup-engine`, 엔진이 설정되어 있으면 `/project-stage-detect`를 안내합니다.

## 4단계: 설정값 확인 및 저장 (Show what you assume, then save it)

두 가지 설정값을 도출합니다.

**Stage(개발 단계):** A, B, C 경로는 `Concept`. D 경로는 디스크 상태에 따라 결정 (`Concept`, `Systems Design`, `Technical Setup` 등).

**Rigor(프로세스 엄격도):** `project.yaml`에 이미 지정되어 있지 않다면 사용자의 설명에 따라 추론합니다:
- 오픈월드, RPG, 시뮬레이션, 샌드박스, 멀티플레이어 등 복잡한 시스템 → `full`
- 상용 출시, Steam 출시 목표, 명확한 단일 코어 루프 → `standard`
- 게임잼, 주말 프로젝트, 프로토타입, 첫 게임, 가벼운 시도 → `minimal`
- 명시되지 않은 경우 기본값: `minimal`

설정 안내 카드를 표시합니다:

```
[설정 예정 정보]
  개발 단계(Stage): [stage] ([도출 근거])
  엄격도(Rigor):     [value] ([도출 근거])
    - minimal: 1페이지 브리프, 굵직한 스토리, 테스트 선택, 약 4단계만에 코드 구현
    - standard: 구현 전 약 8개 기획 문서 작성, 표준 QA 테스트
    - full: standard의 모든 것 + 버티컬 슬라이스 검증 빌드, 엄격한 증거 요구
  * 언제든 /settings 명령으로 변경할 수 있습니다.
```

질문 도구로 확인합니다: "이 설정을 `project.yaml`에 저장할까요?" 선택지: `저장하기(Save)` / `저장하지 않음(Don't save)`.

- **저장하기:** `bash .claude/scripts/set-stage.sh "[stage]"` 실행, rigor가 설정되지 않은 상태였다면 `bash .claude/scripts/config-set.sh modes.rigor [value]` 실행.
- **저장하지 않음:** 저장하지 않고 이번 세션에서만 임시로 해당 값을 유지합니다.

## 5단계: 확인 주기 설정 (Ask how much to confirm)

`modes.automation`이 이미 설정되어 있지 않다면 묻습니다:
"작업을 진행할 때 어느 정도로 확인을 받길 원하시나요?" 선택지:
- `Guided (권장)`: 사소한 결정은 에이전트가 처리하되, 중요한 결정(스코프 변경, 삭제, 스키마 변경)은 사용자에게 확인을 받습니다.
- `Collaborative`: 중요한 단계마다 미리 묻고, 파일을 작성하기 전에 항상 초안을 제시합니다.
- `Autonomous`: 결정을 기록하며 스스로 진행하고, 필수 질문 카테고리에서만 멈춥니다. (가장 빠름)

사용자의 선택에 따라 `bash .claude/scripts/config-set.sh modes.automation [value]`를 실행하여 저장합니다.

## 6단계: 전체 로드맵 제시 (Show the path)

"엄격도 `[value]` 기준의 개발 로드맵입니다. 모든 스킬은 어떤 rigor에서도 실행 가능하며, rigor는 '허용 여부'가 아니라 '필수 여부'를 정의합니다."

로드맵을 제시합니다:

**`minimal`: 코드 실행까지 4단계**
1. `/setup-engine`: 사용할 게임 엔진 선택 및 구성
2. `/brainstorm`: 1페이지 분량의 `design/game-brief.md` 작성
3. `/create-stories`: 브리프의 MVP 목록을 구현 가능한 스토리로 변환
4. `/dev-story`: 첫 게임 코드 구현 시작

**`standard`**
- Concept: `/setup-engine` → `/brainstorm` → `/prototype` → `/art-bible` → `/gate-check`
- Systems Design: `/map-systems` → `/design-system` (시스템당 1회) → `/review-all-gdds` → `/gate-check`
- Architecture: `/create-architecture` → `/architecture-decision` → `/create-control-manifest` → `/architecture-review` → `/test-setup` → `/ux-design` → `/gate-check`
- Pre-Production: `/ux-design` → `/create-epics` → `/create-stories` → `/sprint-plan` → `/gate-check`
- Production: `/dev-story`

**`full`**
- standard의 모든 과정 + Pre-Production 단계의 `/vertical-slice` 및 `/playtest-report` + GDD별 `/design-review`

마지막으로 질문합니다: "[첫 번째 단계]부터 바로 시작하시겠습니까?" 선택지: `예, [첫 번째 단계] 시작` / `다른 작업 먼저 진행`.

## 7단계: 작업 인계 (Hand off)

단 한 줄로 응답합니다: "`[skill]`을 입력하여 시작하십시오."
에이전트가 해당 스킬을 임의로 즉시 실행하지 않으며, 사용자가 직접 입력하여 시작할 수 있도록 안내합니다.
