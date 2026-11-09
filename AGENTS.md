# Antigravity Game Studios -- Game Studio Agent Architecture

49개의 전문화된 서브에이전트와 70개 이상의 워크플로우 스킬을 통해 조율되는 인디 게임 개발 아키텍처입니다.
각 에이전트는 고유한 도메인(기획, 아트, 프로그래밍, 오디오, QA, 프로덕션 등)을 담당하여 관심사 분리와 최고 수준의 품질을 유지합니다.

---

## 기본 지침 (Global Rules)

- **언어 원칙**: 모든 응답, 분석, 문서 및 주석은 원칙적으로 한국어로 작성합니다.
- **정확성 및 검증**: 최신 웹 검색 및 내부 문서를 교차 검토하여 정확한 정보만 제공합니다.
- **간결한 어조**: 군더더기 없이 명확하고 간결하게 답변합니다.

---

## 기술 스택 (Technology Stack)

- **엔진**: [선택: Godot 4 / Unity / Unreal Engine 5]
- **언어**: [선택: GDScript / C# / C++ / Blueprint]
- **버전 관리**: Git (트렁크 기반 개발, Trunk-based development)
- **빌드 시스템**: 엔진 설정 후 지정
- **에셋 파이프라인**: 엔진 설정 후 지정

> **참고**: Godot, Unity, Unreal 각각에 최적화된 전용 스페셜리스트 에이전트 그룹이 구성되어 있습니다. 프로젝트에 설정된 엔진에 맞는 전문가를 활용하십시오.

---

## 프로젝트 구조 (Project Structure)

@.agents/docs/directory-structure.md

---

## 엔진 버전 레퍼런스 (Engine Version Reference)

<!-- ENGINE-REFERENCE-IMPORT: 선택한 엔진에 따라 변경됩니다. 기본값은 Godot입니다. -->
@docs/engine-reference/godot/VERSION.md

---

## 기술 환경 설정 (Technical Preferences)

프로젝트 루트의 `project.yaml`이 기본 설정 저장소입니다(엔진, 전문가, 네이밍 규칙, 타깃 플랫폼, 성능 목표, 워크플로우 모드).
스킬들은 `resolve_config`를 통해 설정을 확인합니다(`.agents/docs/config-resolution.md` 참조).

`.agents/docs/technical-preferences.md`는 레거시 대체 설정 문서입니다.

---

## 조율 규칙 (Coordination Rules)

@.agents/docs/coordination-rules.md

---

## 협업 프로토콜 (Collaboration Protocol)

**자율적인 임의 실행이 아닌, 사용자 주도의 협업 원칙을 따릅니다.**
모든 주요 작업은 **질문(Question) -> 옵션 제시(Options) -> 사용자 결정(Decision) -> 초안 작성(Draft) -> 최종 승인(Approval)** 단계를 거칩니다.

1. **파일 작성 전 확인**: `write_file` 또는 `edit_file` 도구를 사용하기 전에 반드시 사용자에게 `"이 내용을 [파일경로]에 작성할까요?"`라고 확인을 받습니다.
   - 예외: `production/session-state/active.md` 덧붙이기(append), 에이전트 메모리 작성, 오케스트레이션 스킬에서 이미 승인된 대상 경로에 신규 파일 작성(`production/`, `docs/`, `tests/` 한정).
2. **초안 및 요약 제시**: 승인을 요청하기 전에 변경될 내용의 요약이나 초안을 먼저 보여줍니다.
3. **다중 파일 변경 승인**: 여러 파일을 수정할 때는 전체 변경 계획에 대한 명시적 승인을 받습니다.
4. **임의 커밋 금지**: 사용자의 명시적인 지시나 승인 없이 `git commit`을 실행하지 않습니다.
5. **응답 없는 질문**: 질문이 건너뛰어지거나 무시된 경우, 임의로 진행하지 않고 일반 텍스트로 다시 질문한 뒤 대기합니다.

상세 프로토콜 및 예시는 `docs/COLLABORATIVE-DESIGN-PRINCIPLE.md`를 참조하십시오.

> **첫 세션이신가요?** 엔진이 설정되지 않았거나 게임 기획 초기 단계라면 `/start` 스킬을 실행하여 온보딩 가이드를 시작하십시오.

---

## 도구 매핑 (Antigravity Tool Mapping)

Antigravity 환경에서는 다음 표준 도구를 사용하여 협업합니다:

- **명령어 실행**: `run_command` (빌드, 테스트, git 작업 등)
- **파일 읽기**: `read_file` (소스코드, GDD, 설정 파일 열람)
- **파일 작성/수정**: `write_file`, `edit_file` (사전 승인 원칙 준수)
- **사용자 질문/선택**: `ask_question` (구조화된 의사결정 시 선택지 제공)
- **웹 검색**: `search_web` (엔진 문서, API, 최신 정보 검색)
- **서브에이전트 호출**: `invoke_subagent`, `define_subagent` (도메인 전문가 에이전트 위임)

---

## 코딩 표준 (Coding Standards)

@.agents/docs/coding-standards.md

---

## 컨텍스트 관리 (Context Management)

- **`production/session-state/active.md`는 세션 체크포인트입니다.** 세션 메모리는 대화 컨텍스트가 아니라 이 파일에 저장됩니다. 대화 압축(compaction), 재시작 후에는 가장 먼저 이 파일을 읽어 진행 상태를 복원합니다.
- **`.agents/scripts/` 도우미 스크립트**: 스크립트는 자체적인 판단(점수 매기기 등)을 내리지 않고 사실과 관찰 결과만을 출력합니다.
