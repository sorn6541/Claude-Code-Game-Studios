---
name: smoke-check
description: "QA 인계 전 핵심 경로 스모크 게이트 — 자동화 테스트 스위트 실행. 실패 시 빌드는 QA 불가 상태로 판정."
argument-hint: "[sprint | quick | --platform pc|console|mobile|all]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, AskUserQuestion, Bash(bash "*/.claude/skills/smoke-check/../../hooks/yaml-helper.sh" resolve_config *), Bash(bash .claude/scripts/project-coherence.sh*), Bash(command -v *), Bash(uname -s), Bash(godot --headless --path . --import), Bash(timeout 900 godot --headless *), Bash(timeout 1800 godot --headless *), Bash(grep -q 'com.unity.test-framework' Packages/manifest.json), Bash(echo present), Bash(echo ABSENT)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys automation,workflow,qa.level,testing.strict`

# 스모크 체크 (Smoke Check)

"구현 완료"와 "QA 인계 준비 완료" 사이의 핵심 관문(Gate)입니다. 자동화된 테스트 스위트를 실행하고, 테스트 커버리지 갭을 점검하며, 개발자와 함께 핵심 경로를 검증하여 최종 PASS/FAIL 판정 보고서를 생성합니다.

원칙은 단순합니다: **스모크 체크를 통과하지 못한 빌드는 QA팀에 넘기지 않습니다.**
망가진 빌드를 QA팀에 넘기는 것은 테스터의 시간을 낭비하고 팀의 사기를 저하시킵니다.

**산출물 경로:** `production/qa/smoke-[날짜].md`

---

모든 질문은 `.claude/docs/automation-modes.md`의 협업 규칙을 따릅니다.

**`qa.level`에 따른 판정 기준:**
- `minimal`: 스모크 체크는 선택 사항입니다. FAIL 판정이 나와도 권고 수준이며 인계를 차단하지 않습니다.
- `standard`: 단계 전환(Phase transition) 전 필수 통과.
- `full`: 매 커밋 및 전 단계 필수 통과.

## 인수 분석 (Parse Arguments)

인수는 조합하여 실행할 수 있습니다: `/smoke-check sprint --platform console`

**기본 모드 (첫 번째 인수, 기본값: `sprint`):**
- `sprint`: 현재 스프린트의 스토리에 대한 전체 스모크 체크 실행.
- `quick`: 커버리지 스캔(3단계) 및 수동 배치 3 생략 (수정 후 빠른 재검증용).

**플랫폼 플래그 (`--platform`, 기본값: 없음):**
- `--platform pc`: PC 고유 점검 (키보드, 마우스, 창 모드 등) 추가.
- `--platform console`: 콘솔 고유 점검 (게임패드, TV 안전 영역, 플랫폼 인증 요건) 추가.
- `--platform mobile`: 모바일 고유 점검 (터치, 가로/세로 회전, 발열/배터리 동작) 추가.
- `--platform all`: 모든 플랫폼 변형 추가 및 플랫폼별 판정 테이블 출력.

---

## 단계별 실행 구조

- **1단계: 테스트 환경 감지 (Phase 1: Detect Test Setup)**: `references/1-detect-setup.md` 참조
- **2단계: 자동화 테스트 실행 (Phase 2: Run Automated Tests)**: `references/2-run-tests.md` 참조
- **3단계: 테스트 커버리지 확인 (Phase 3: Check Test Coverage)**: `references/3-coverage.md` 참조
- **4단계: 수동 스모크 점검 실행 (Phase 4: Run Manual Smoke Checks)**: `references/4-manual-checks.md` 참조
- **5단계: 보고서 생성 (Phase 5: Generate Report)**: `references/5-report.md` 참조
- **6단계: 작성 승인 및 게이트 판정 (Phase 6: Write and Gate)**: `references/6-write-gate.md` 참조

## 협업 프로토콜 (Collaborative Protocol)

- **미실행(NOT RUN)을 임의로 FAIL로 처리하지 마십시오.** 미실행 상태로 기록하고 개발자에게 수동 확인을 요청합니다.
- **실패 항목을 에이전트가 임의로 수정하지 마십시오.** 실패 원인을 보고하고 해결이 필요한 내용을 설명합니다.
- **PASS WITH WARNINGS(경고 포함 통과)**는 QA 인계를 차단하지 않으며, `/story-done`에서 후속 조치할 권고 사항으로 기록합니다.
- **사전 승인 없이 보고서 파일을 작성하지 마십시오.** 6단계에서 사용자에게 명시적 확인을 받은 후 파일을 생성합니다.
