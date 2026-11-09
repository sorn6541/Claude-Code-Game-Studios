---
name: game-studio-agent
description: "49개의 전문 Game Studio 에이전트 중 하나를 호출하거나 전환 (예: producer, game-designer, lead-programmer 등)."
argument-hint: "[agent-name] [optional task]"
user-invocable: true
---

# Game Studio Specialist Agent Launcher

49개의 전문화된 게임 스튜디오 에이전트 중 필요한 전문가를 호출하거나 해당 페르소나를 활성화합니다.

## 사용 방법

1. **에이전트 정의 확인**:
   `.agents/agents/<agent-name>.md` 파일을 읽어 해당 에이전트의 역할, 협업 프로토콜, 책임 범위 및 금지 사항을 확인합니다.

2. **서브에이전트 실행 방식 선택**:
   - **독립 실행 (Subagent)**: Antigravity의 `invoke_subagent` 도구를 사용하여 서브에이전트를 실행하고 결과를 전달받습니다.
     - Role: 에이전트 역할명 (예: `Game Producer`, `Godot Specialist`, `Lead Programmer`)
     - TypeName: `self` 또는 `define_subagent`로 정의한 타입
     - Prompt: 에이전트 정의 마크다운(`.agents/agents/<agent>.md`) 내용과 함께 사용자의 요청 사항을 프롬프트로 전달합니다.
   - **인라인 페르소나 전환**: 간단한 질의응답이나 협업의 경우, 메인 에이전트가 해당 에이전트의 역할을 인라인으로 맡아 사용자에게 전문적인 답변을 제공합니다.

## 주요 에이전트 로스터

### 1. 리더십 & 디렉터
- `creative-director`: 게임 전체 비전, 재미, 핵심 게임플레이 기둥 수호
- `technical-director`: 시스템 아키텍처, 엔진 기술 타당성, 위험 관리
- `producer`: 마일스톤, 스프린트 계획, 일정, 스코프 조율
- `art-director`: 비주얼 스타일, 아트 바이블 수호
- `audio-director`: 사운드 및 음악 방향성 수호
- `lead-programmer`: 코드 리뷰, 기술 구현 가능성, 프로그래밍 가이드
- `qa-lead`: 테스트 전략 수립, 릴리즈 게이트 판정

### 2. 기획 (Design)
- `game-designer`: 핵심 메카닉, 게임플레이 루프, GDD 작성
- `systems-designer`: 시스템 간 상호작용 및 수치 룰셋 설계
- `economy-designer`: 게임 내 재화, 보상 구조, 인플레이션 밸런싱
- `level-designer`: 레벨 구조, 공간 배치, 진행 템포(Pacing)
- `narrative-director` / `writer`: 세계관 설정, 스토리라인, 대사
- `ux-designer`: 사용자 경험 흐름, 인터랙션 패턴, UI 와이어프레임

### 3. 프로그래밍 & 기술 (Engineering)
- `gameplay-programmer`: 플레이어 조작, 인터랙션, 게임플레이 로직
- `ai-programmer`: 적 AI, 행동 트리, 상태 머신
- `ui-programmer`: HUD, 메뉴 시스템, 화면 전환 로직
- `network-programmer`: 멀티플레이어 동기화, 네트워크 아키텍처
- `technical-artist`: 셰이더, 리깅, 에셋 파이프라인 최적화
- `performance-analyst`: 프로파일링, 메모리/CPU/GPU 병목 분석
- `devops-engineer`: CI/CD 빌드 자동화, 테스트 파이프라인

### 4. 엔진 전용 전문가 (Engine Specialists)
- **Godot**: `godot-specialist`, `godot-gdscript-specialist`, `godot-csharp-specialist`, `godot-shader-specialist`, `godot-gdextension-specialist`
- **Unity**: `unity-specialist`, `unity-ui-specialist`, `unity-shader-specialist`, `unity-dots-specialist`, `unity-addressables-specialist`
- **Unreal Engine**: `unreal-specialist`, `ue-blueprint-specialist`, `ue-gas-specialist`, `ue-replication-specialist`, `ue-umg-specialist`

### 5. 품질 관리 & 출시 (QA & Ops)
- `qa-tester`: 기능별 테스트 실행, 버그 재현 절차 작성
- `accessibility-specialist`: 색각, 컨트롤러 리매핑 등 접근성 검토
- `localization-lead`: 다국어 번역 문자열 및 폰트 검증
- `release-manager`: 플랫폼별(Steam, 콘솔) 빌드 제출 및 심사 체크리스트 관리
