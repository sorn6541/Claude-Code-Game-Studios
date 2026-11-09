---
name: project-stage-detect
description: "프로젝트 상태 분석, 개발 단계 감지, 누락된 문서/에셋 식별 및 다음 단계 권장 ('현재 개발 어디 단계인가요?')."
argument-hint: "[선택 사항: 'programmer' 또는 'designer'와 같은 역할 필터]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Bash(bash "*/.claude/skills/project-stage-detect/../../hooks/yaml-helper.sh" resolve_config *), Bash(bash .claude/scripts/artifact-check.sh), Bash(bash ".claude/scripts/artifact-check.sh"), Bash(bash ./.claude/scripts/artifact-check.sh), Bash(bash .claude/scripts/artifact-check.sh *), Bash(bash ".claude/scripts/artifact-check.sh" *), Bash(bash ./.claude/scripts/artifact-check.sh *)
model: haiku
---

# 프로젝트 개발 단계 감지 (Project Stage Detection)

프로젝트 전체를 스캔하여 현재 개발 단계, 산출물 완성도, 해결이 필요한 누락(Gap) 요소를 정밀 진단합니다.
다음과 같은 상황에 매우 유용합니다:
- 기존 프로젝트(Brownfield)를 이어받았을 때
- 새로운 코드베이스에 온보딩할 때
- 마일스톤 또는 게이트 진입 전 누락된 항목을 점검할 때
- "현재 개발이 어디까지 진행되었는가?"를 파악할 때

---

## 워크플로우

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys workflow,automation`

**자동화 모드(Automation mode)**: `project.local.yaml` → `project.yaml` → 기본값 `collaborative`.

**워크플로우 등급(`workflow`)**:
- `minimal`: 1페이지 브리프와 코드 중심. GDD나 ADR의 부재를 결함으로 취급하지 않음.
- `standard`: 표준 게임 개발 단계. 필수 문서 누락 시 갭으로 표시.
- `full`: 철저한 검증. 모든 누락 문서와 검증 산출물을 갭으로 보고.

---

### 1. 주요 디렉토리 스캔

결정론적 단일 스크립트 실행으로 전체 카탈로그 산출물 존재 여부를 파악합니다:

```
Bash: bash .claude/scripts/artifact-check.sh
```

스크립트 결과(`PRESENT`, `ABSENT`, `SHORT`, `PATTERN_MISS`, `NO_CHECK`)를 기반으로 다음 영역의 품질과 세부 상태를 분석합니다:

1. **기획 문서 (`design/`)**:
   - GDD 파일 수 및 필수 문서(`game-concept.md` 또는 `design/game-brief.md`, `game-pillars.md`, `systems-index.md`) 확인
   - `systems-index.md`가 있는 경우 정의된 전체 시스템 수 대비 상세 기획서가 완성된 시스템 비율 계산
   - 내러티브(`design/narrative/`) 및 레벨 기획(`design/levels/`) 문서 수량 집계

2. **소스 코드 (엔진별 코드 루트 — Godot `src/`, Unity `Assets/`, Unreal `Source/`)**:
   - 소스 코드 파일 수 및 규모 집계
   - 주요 하위 디렉토리(core, gameplay, ai, ui 등) 구조 확인

3. **프로덕션 관리 산출물 (`production/`)**:
   - 활성 스프린트 계획, 마일스톤 정의, 로드맵 문서 확인 (`minimal`에서는 스프린트 대신 스토리 진행도로 평가)

4. **프로토타입 (`prototypes/`)**:
   - 프로토타입 디렉토리 및 플레이 가능 여부 확인

5. **테스트 (`tests/`)**:
   - 단위 테스트, 통합 테스트, 테스트 러너 설정 여부 확인

---

### 2. 개발 단계 감지 (Detect Stage)

스캔 결과를 바탕으로 현재 프로젝트가 속한 개발 단계를 결정합니다:

| 개발 단계 | 주요 기준 |
|---|---|
| **Concept (콘셉트)** | 게임 콘셉트/브리프 구상 단계, 엔진 미결정 또는 초기 프로토타입 검토 단계 |
| **Systems Design (시스템 기획)** | 콘셉트 확정, 코어 시스템 분해 및 시스템별 GDD 작성 단계 |
| **Technical Setup (기술 셋업)** | 엔진 확정, 아키텍처 청사진 및 기술 결정(ADR) 수립 단계 |
| **Pre-Production (프리프로덕션)** | 버티컬 슬라이스 검증, 에픽/스토리 생성, 스프린트 1 계획 수립 단계 |
| **Production (프로덕션)** | 스프린트 주기별 스토리 구현, 게임플레이 시스템 및 콘텐츠 본격 개발 단계 |
| **Polish (폴리싱)** | 기능 구현 완료, 성능 최적화, 밸런싱, 게임패드/접근성 다듬기 단계 |
| **Release (릴리스)** | 플랫폼 인증, 스토어 빌드 제출, 패치 노트 및 출시 준비 단계 |

---

### 3. 문서 및 아키텍처 갭(Gaps) 식별

현재 단계 및 이전 단계에서 완성되었어야 할 산출물 중 누락되거나 불완전한 항목을 식별합니다:
- 현재 단계 이전의 필수 산출물 누락 → **블로커 (Critical Gap)**
- 현재 단계의 권장 산출물 미작성 → **주의 (Warning)**
- 소스 코드는 존재하나 대응하는 기획 문서/ADR 부재 → **문서 부채 (Tech Debt)**

---

### 4. 보고서 출력

결과를 명확하고 구조화된 한국어 보고서로 출력합니다:

```markdown
# 프로젝트 상태 분석 보고서

- **감지된 개발 단계:** [단계명] (신뢰도: 높음/중간/낮음)
- **적용 워크플로우:** [minimal / standard / full]

## 산출물 완성도 요약
- 기획 문서: [완성된 GDD 수] / [전체 시스템 수] ([퍼센트]%)
- 소스 코드: [파일 수]개 파일 ([추정 라인 수])
- 테스트: [테스트 파일 수]개
- 아키텍처: ADR [개수]개

## 식별된 주요 갭 (Gaps)
1. **[블로커]**: [누락된 필수 산출물 및 영향]
2. **[권장사항]**: [보강이 필요한 문서나 테스트]

## 권장 다음 단계 (Next Steps)
1. `[/추천스킬1]` — [작업 설명]
2. `[/추천스킬2]` — [작업 설명]
```

보고서 작성 후 사용자의 확인을 받고 다음 작업을 안내합니다.
