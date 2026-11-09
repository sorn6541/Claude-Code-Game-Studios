---
name: help
description: "다음에 무엇을 해야 할까요? 막히거나 진행 방향을 모를 때 실행하는 나침반 가이드."
argument-hint: "[선택 사항: 방금 완료한 작업, 예: 'finished design-review' 또는 'stuck on ADRs']"
user-invocable: true
allowed-tools: Read, Glob, Grep, Bash(bash "*/.claude/skills/help/../../hooks/yaml-helper.sh" resolve_config *), Bash(bash "*/.claude/skills/help/../../scripts/story-status.sh"), Bash(bash .claude/scripts/story-status.sh*), Bash(bash .claude/scripts/artifact-check.sh *), Bash(bash ".claude/scripts/artifact-check.sh" *), Bash(bash ./.claude/scripts/artifact-check.sh *), Bash(git log *)
model: haiku
---

# 스튜디오 도움말 — 다음에 무엇을 해야 할까요?

이 스킬은 읽기 전용입니다. 현황을 보고하며 파일을 직접 작성하지 않습니다.

현재 게임 개발 파이프라인에서 프로젝트가 정확히 어디에 위치해 있는지 파악하고, **다음에 진행할 최적의 단계**를 안내합니다. 이는 가벼운 나침반 역할이며 전체 감사가 아닙니다. (종합적인 누락 분석이 필요한 경우 `/project-stage-detect`를 사용하십시오.)

## 실시간 프로젝트 상태

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys project.stage,workflow`

스킬 실행 전 위 설정이 자동 확인됩니다:
- `project.stage`: 2단계를 판정하기 위한 공식 개발 단계 (`project.yaml` 우선, 없으면 `production/stage.txt`).
- `workflow`: 2단계와 5단계를 위한 워크플로우 등급.

---

## 1단계: 워크플로우 카탈로그 확인

`.claude/docs/workflow-catalog.yaml`을 읽습니다. 모든 개발 단계, 순서별 스텝, 필수/선택 여부, 완료를 증명하는 산출물 패턴이 정의되어 있습니다.

---

## 2단계: 현재 개발 단계 판정

**먼저 `workflow` 값을 확인합니다.** 만약 `minimal` 등급이라면 단계별 사다리가 아닌 미니멀 경로(`paths.minimal`)를 따르므로, 3단계를 거친 뒤 바로 **4m 단계**로 이동합니다.

그 외의 경우:
1. `project.stage` 값을 카탈로그의 단계 키로 매핑합니다:
   - "Concept" → `concept`
   - "Systems Design" → `systems-design`
   - "Technical Setup" → `technical-setup`
   - "Pre-Production" → `pre-production`
   - "Production" → `production`
   - "Polish" → `polish`
   - "Release" → `release`
2. 단계가 지정되지 않은 경우 산출물(코드 수, 에픽, ADR, GDD 등)을 기반으로 현재 단계를 추론합니다.

---

## 3단계: 세션 컨텍스트 확인

`production/session-state/active.md`가 존재하면 STATUS 및 CHECKPOINT 블록을 확인합니다:
- 가장 최근에 진행하던 작업
- 진행 중인 작업 또는 미해결 질문
- STATUS 블록의 현재 에픽/기능/태스크

이를 통해 사용자가 방금 완료했거나 막혀 있는 작업을 파악하여 맞춤형으로 안내합니다.

---

## 4단계: 현재 단계의 스텝 완료 여부 확인

카탈로그에 정의된 현재 단계의 각 스텝에 대해 산출물 검사를 실행합니다:

```
Bash: bash .claude/scripts/artifact-check.sh --phase [현재단계]
```

스크립트의 실행 상태 매핑:
- `PRESENT`: **완료 (Complete)**
- `ABSENT`: **미완료 (Incomplete)**
- `SHORT`: **미완료 (수량 부족)**
- `PATTERN_MISS`: **미완료 (파일은 있으나 필수 마커 누락)**
- `NO_CHECK`: **수동 확인 필요(MANUAL) 또는 알 수 없음(UNKNOWN)**

### 프로덕션 단계 특수 케이스: `sprint-status.yaml` 확인
현재 단계가 `production`인 경우 `production/sprint-status.yaml`을 직접 읽어 스토리별 상태를 파악합니다:
- `in-progress` → 현재 진행 중인 작업으로 표시
- `ready-for-dev` → 다음 진행할 작업으로 표시
- `done` → 완료로 집계
- `blocked` → 블로커 이유와 함께 차단 상태로 표시

---

## 4m단계: 미니멀 경로 (`workflow: minimal` 전용)

`minimal` 등급에서는 단계별 복잡한 검사 대신 카탈로그의 미니멀 경로(엔진 → `design/game-brief.md` → 스토리 → 구현)를 점검합니다:

```
Bash: bash .claude/scripts/artifact-check.sh --path minimal
```

우선순위 순서대로 다음 작업을 안내합니다:
1. `engine-setup` 미완료 → `/setup-engine`
2. `game-brief` 미완료 → 기개발 코드가 있으면 `/reverse-document design`, 없으면 `/brainstorm`
3. `create-stories` 미완료 → `/create-stories`
4. 스토리가 존재하는 경우:
   - `IN_REVIEW` 상태인 스토리 → `/story-done [경로]` (작업이 완료되어 검증 및 종료 대기 중)
   - `IN_PROGRESS` 상태인 스토리 → `/dev-story [경로]` 또는 `/story-done [경로]`
   - `TODO` 상태인 스토리 → `/dev-story [경로]`
   - `BLOCKED` 상태인 스토리 → 블로커 해결 안내

---

## 5단계: 현재 위치 및 다음 단계 식별

완료 데이터를 바탕으로 다음을 도출합니다:
1. **마지막 확인된 완료 스텝** (가장 최근 완료된 필수 작업)
2. **현재 블로커 (다음 필수 작업)** — 사용자가 지금 바로 진행해야 할 단 하나의 필수 스텝
3. **선택적 기회 (선택 작업)** — 병행하거나 미리 수행할 수 있는 유용한 작업
4. **이후 예정된 필수 스텝** — 앞으로 진행될 작업 로드맵

---

## 6단계: 진행 중인 작업 점검

`active.md`에 진행 중인 작업이 있다면 상단에 눈에 띄게 안내합니다:
"현재 [작업명]을 진행 중이셨던 것으로 보입니다."

---

## 7단계: 결과 제시 (출력 형식)

답변은 **간결하고 명확하게** 작성합니다:

```markdown
## 현재 위치: [개발 단계명]

**진행 중인 작업:** [active.md에서 확인된 작업]

### ✓ 완료됨
- [완료된 작업명]
- [완료된 작업명]

### → 다음 단계 (필수)
**[작업명]** — [설명]
실행 명령: `[/명령어]`

### ~ 선택 사항
- **[작업명]** — [설명] → `/명령어`

### 그 다음 예정 작업
- [이후 필수 작업명] (`/명령어`)

---
**[다음 단계명]** 게이트에 근접했습니다 → 준비가 완료되면 `/gate-check`를 실행하십시오.
```

---

## 협업 프로토콜 (Collaborative Protocol)

- **다음 스킬을 절대 자동으로 실행하지 마십시오.** 권장 사항을 제시하고, 사용자가 직접 호출하도록 안내합니다.
- **수동 확인(MANUAL) 스텝**에 대해서는 임의로 판단하지 말고 사용자에게 완료 여부를 묻습니다.
- **단 하나의 핵심 추천**: 사용자가 답변을 읽고 나서 '지금 당장 무엇을 해야 하는가'를 명확히 알 수 있도록 단 하나의 1순위 액션을 제시하십시오.
