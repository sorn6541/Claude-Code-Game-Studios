---
name: brainstorm
description: "게임 콘셉트 발굴 및 선정을 안내. 게임 아이디어, 새 콘셉트, 게임잼 아이디어가 필요하거나 새로운 방향을 탐색할 때 사용."
argument-hint: "[장르 또는 테마 힌트, 또는 'open'] [--review full|lean|solo]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, WebSearch, Agent, AskUserQuestion, Bash(bash "*/.claude/skills/brainstorm/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys review_mode,automation,docs.density,workflow`

# 브레인스토밍 (Brainstorm)

아이디어가 없거나 거친 초기 발상 단계에서, 다음 단계가 구현할 수 있는 구체적인 기획 문서를 도출합니다. 작성되는 문서의 깊이는 `workflow` 설정에 따라 결정됩니다:

- **`minimal`**: 아래의 린 브리프(Lean Brief) 플로우를 따릅니다. 1페이지 분량의 `design/game-brief.md`를 작성하고 종료합니다. 복잡한 기둥(Pillars) 분석이나 디렉터 게이트 승인 절차를 생략하고 즉시 코드로 진입할 수 있도록 돕습니다.
- **`standard` 또는 `full`**: `references/full-concept.md`를 참조하여 진행합니다. `.claude/docs/templates/game-concept.md` 템플릿 기반으로 완성형 `design/gdd/game-concept.md`를 작성하며, 디렉터 에이전트들의 게이트 판정(`.claude/docs/director-gates/`)을 거칩니다.

스킬 실행 시 `--review` 옵션으로 리뷰 모드를 임시 재정의할 수 있습니다.
질문은 `ask_question` 도구를 활용하며, 옵션 번호를 매겨 사용자의 결정을 기다립니다.

---

## 린 브리프 플로우 (`workflow: minimal`)

10~15번의 긴 문답 대신, 핵심을 관통하는 몇 번의 대화로 1페이지 브리프를 완성하고 빠르게 개발에 착수합니다. 템플릿(`.claude/docs/templates/game-brief.md`)을 기반으로 작성합니다. 이미 `design/game-brief.md`가 존재한다면 새로 쓰지 않고 다듬는 방식으로 진행합니다.

1. **콘셉트 제안 (Concept)**: 사용자가 입력한 힌트(또는 힌트가 없다면 한 번의 열린 질문)를 바탕으로 **2~3개의 한 줄 콘셉트**(동사 중심 또는 장르와 테마의 조합)를 제안합니다. 사용자가 하나를 선택하거나 조합하도록 안내합니다.
2. **브리프 작성 (Fill the brief)**: 대화를 통해 다음 핵심 항목을 채웁니다:
   - **가제 (Working title)**: 브리프의 제목.
   - **피치 (Pitch)**: 흥미를 유발하는 한 줄 요약.
   - **핵심 루프 (Core loop)**: 플레이어가 반복하는 2~4단계의 행동 루프.
   - **목표 및 패배 조건 (Player goal & fail state)**: 무엇을 달성해야 하고, 어떻게 게임오버되는가.
   - **MVP (최소 기능 제품 목록)**: 게임을 구성하는 핵심 항목 목록 (각 항목은 스토리로 변환됨). **7개 초과 시 과감히 쳐냅니다.** MVP로서는 너무 길다고 알리고 코어 루프 없이도 돌아가는 요소를 Out of scope로 이동시켜 7개 이하로 압축합니다.
   - **범위 제외 (Out of scope)**: 이번 개발에서 의도적으로 만들지 않을 항목들.
   - **구현 순서 (Build order)**: 가장 리스크가 크거나 아직 검증되지 않은 핵심 파트부터 우선순위 지정.
   - **타깃 유저, 아트/오디오 방향성, 레퍼런스 게임**: 각 한 줄로 간단히 명시.
3. **전체 브리프 검토 및 승인**: 완성된 브리프 전문을 보여주고 명시적으로 질문합니다:
   `"브리프가 완성되었습니다. 이 내용을 design/game-brief.md에 작성할까요?"`
   선택지: `작성하기(Yes — write it)` / `수정하기(Revise a field first)`.
   명시적 승인을 받았을 때만 `design/game-brief.md`를 생성합니다.
4. **다음 단계 안내 (Next steps)**:
   1. `/setup-engine`: 엔진이 설정되지 않은 경우 엔진 선택 및 구성.
   2. `/create-stories`: MVP 목록을 구현 가능한 스토리들로 분할.
   3. `/dev-story`: 첫 게임 코드 구현 착수.

판정: **COMPLETE** — 게임 브리프가 작성되었으며, 다음 단계는 코드 구현입니다.
