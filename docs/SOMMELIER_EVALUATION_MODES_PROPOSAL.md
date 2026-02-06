# Somm.dev 평가 모드 확장 제안서

> 작성일: 2026-02-06  
> 버전: 1.0  
> 목적: Fairthon 75기법 아키텍처를 somm.dev 브랜딩에 맞게 적용

---

## Executive Summary

somm.dev의 와인 소믈리에 브랜딩을 유지하면서 Fairthon의 75개 분석 기법을 도입합니다.
기존 **Six Sommeliers** 평가 모드에 더해, 심층 분석을 위한 **Grand Tasting** 모드를 추가합니다.

| 모드 | 브랜드명 | 소요 시간 | 분석 깊이 |
|------|---------|----------|----------|
| **Standard Tasting** | Six Sommeliers | ~2분 | 6명의 전문 소믈리에 평가 |
| **Grand Tasting** | Sommelier Masterclass | ~5분 | 75개 분석 기법 전체 적용 |

---

## 1. 브랜딩 전략

### 1.1 핵심 브랜딩 원칙

somm.dev의 **와인 소믈리에 컨셉**을 모든 기능에 일관되게 적용:

| 기존 용어 (Fairthon) | somm.dev 브랜딩 |
|---------------------|----------------|
| Six Thinking Hats | **Six Sommeliers** |
| White Hat (사실) | **Marcel** - Cellar Master |
| Red Hat (감성) | **Isabella** - Wine Critic |
| Black Hat (리스크) | **Heinrich** - Quality Inspector |
| Yellow Hat (기회) | **Sofia** - Vineyard Scout |
| Green Hat (혁신) | **Laurent** - Winemaker |
| Blue Hat (통합) | **Jean-Pierre** - Master Sommelier |
| Full 75 Techniques | **Grand Tasting** / **Sommelier Masterclass** |
| Technique Categories | **Tasting Notes Categories** |

### 1.2 평가 모드 브랜딩

```
┌─────────────────────────────────────────────────────────────────┐
│                    🍷 Evaluation Style                          │
│         Choose your tasting experience                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌───────────────────────┐   ┌───────────────────────┐        │
│   │  🍷 Standard Tasting  │   │  🏆 Grand Tasting     │        │
│   │      [Recommended]    │   │                       │        │
│   │                       │   │                       │        │
│   │  Six Sommeliers       │   │  Sommelier Masterclass│        │
│   │  ~2 minutes           │   │  ~5 minutes           │        │
│   │                       │   │                       │        │
│   │  Our expert panel of  │   │  Comprehensive 75-    │        │
│   │  6 sommeliers taste   │   │  technique deep dive  │        │
│   │  your code            │   │  analysis             │        │
│   │                       │   │                       │        │
│   │  • Marcel (Structure) │   │  • Problem Analysis   │        │
│   │  • Isabella (Quality) │   │  • Innovation Check   │        │
│   │  • Heinrich (Security)│   │  • Risk Assessment    │        │
│   │  • Sofia (Innovation) │   │  • User Empathy       │        │
│   │  • Laurent (Craft)    │   │  • Feasibility        │        │
│   │  • Jean-Pierre (Final)│   │  • Opportunity        │        │
│   │                       │   │  • Presentation       │        │
│   │                       │   │  • Synthesis          │        │
│   └───────────────────────┘   └───────────────────────┘        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 평가 모드 상세 설계

### 2.1 Standard Tasting (Six Sommeliers)

**현재 구현 상태**: ✅ 완료 (기존 시스템)

기존 somm.dev의 6명 소믈리에 에이전트가 병렬로 평가 수행:

```
                    ┌─────────────┐
                    │   START     │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │ RAG Enrich  │
                    └──────┬──────┘
                           │
    ┌──────────────────────┼──────────────────────┐
    │          │           │           │          │
┌───▼───┐ ┌───▼───┐ ┌─────▼─────┐ ┌───▼───┐ ┌───▼───┐
│Marcel │ │Isabella│ │ Heinrich  │ │ Sofia │ │Laurent│
│(구조) │ │(품질)  │ │ (보안)    │ │(혁신) │ │(구현) │
└───┬───┘ └───┬───┘ └─────┬─────┘ └───┬───┘ └───┬───┘
    │         │           │           │         │
    └─────────┴─────┬─────┴───────────┴─────────┘
                    │
             ┌──────▼──────┐
             │ Jean-Pierre │
             │  (통합)     │
             └──────┬──────┘
                    │
                    ▼
                   END
```

**특징**:
- 6명의 전문 소믈리에가 각자의 관점에서 평가
- 병렬 실행으로 빠른 결과 (~2분)
- Jean-Pierre가 최종 통합 및 점수 산정
- 대부분의 프로젝트에 권장

### 2.2 Grand Tasting (Sommelier Masterclass)

**구현 상태**: 🔄 신규 개발 필요

75개 분석 기법을 8개 카테고리로 구성하여 심층 분석:

```
                         ┌─────────────┐
                         │   START     │
                         └──────┬──────┘
                                │
                         ┌──────▼──────┐
                         │ RAG Enrich  │
                         └──────┬──────┘
                                │
                         ┌──────▼──────┐
                         │  Baseline   │
                         └──────┬──────┘
                                │
┌───────┬───────┬───────┬───────┼───────┬───────┬───────┬───────┐
│       │       │       │       │       │       │       │       │
▼       ▼       ▼       ▼       ▼       ▼       ▼       ▼       ▼
Aroma  Palate  Body   Finish  Balance Vintage Terroir  Cellar
(분석)  (혁신)  (위험)  (공감)  (실현)  (기회)  (표현)  (통합)
│       │       │       │       │       │       │       │       │
└───────┴───────┴───────┴───────┼───────┴───────┴───────┴───────┘
                                │
                         ┌──────▼──────┐
                         │Deep Synthesis│
                         │(Grand Finale)│
                         └──────┬──────┘
                                │
                                ▼
                               END
```

---

## 3. Tasting Notes Categories (기법 카테고리)

### 75개 기법의 브랜딩 매핑

| Fairthon 카테고리 | Somm.dev 브랜딩 | 와인 메타포 | 기법 수 |
|------------------|----------------|------------|--------|
| problem-analysis | **Aroma Notes** | 향 분석 - 문제의 본질 파악 | 9개 |
| innovation | **Palate Notes** | 맛 분석 - 혁신적 요소 탐색 | 9개 |
| risk-analysis | **Body Notes** | 바디감 - 구조적 리스크 평가 | 5개 |
| user-centricity | **Finish Notes** | 여운 - 사용자 경험 분석 | 7개 |
| feasibility | **Balance Notes** | 균형 - 실현 가능성 검토 | 6개 |
| opportunity | **Vintage Notes** | 빈티지 - 성장 기회 발굴 | 4개 |
| presentation | **Terroir Notes** | 테루아 - 표현력 평가 | 5개 |
| synthesis | **Cellar Notes** | 셀러 - 종합 숙성 분석 | 4개 |

### 카테고리별 주요 기법

#### 🍇 Aroma Notes (문제 분석)
```yaml
techniques:
  - five_whys: "5 Whys - 근본 원인 추적"
  - 5w1h: "5W1H - 체계적 상황 분석"
  - assumption_reversal: "가정 뒤집기"
  - constraint_mapping: "제약 조건 매핑"
  - pestle_analysis: "PESTLE 거시환경 분석"
```

#### 🍷 Palate Notes (혁신)
```yaml
techniques:
  - first_principles: "제1원칙 사고"
  - scamper: "SCAMPER 기법"
  - design_thinking: "디자인 씽킹"
  - triz: "TRIZ 혁신 방법론"
  - cross_pollination: "교차 수분"
```

#### 🏺 Body Notes (리스크)
```yaml
techniques:
  - reverse_brainstorming: "역브레인스토밍"
  - pre_mortem: "사전 부검"
  - swot_analysis: "SWOT 분석"
  - fmea: "고장모드 영향분석"
  - risk_matrix: "리스크 매트릭스"
```

#### ✨ Finish Notes (사용자 공감)
```yaml
techniques:
  - empathy_mapping: "공감 지도"
  - jobs_to_be_done: "고객 과업 이론"
  - kano_model: "카노 모델"
  - persona_journey: "페르소나 여정"
  - role_playing: "역할극"
```

#### ⚖️ Balance Notes (실현성)
```yaml
techniques:
  - technology_readiness_level: "기술성숙도(TRL)"
  - porters_five_forces: "포터의 5가지 경쟁요인"
  - ecosystem_thinking: "생태계 사고"
  - chaos_engineering: "카오스 엔지니어링"
```

#### 📅 Vintage Notes (기회)
```yaml
techniques:
  - scenario_planning: "시나리오 플래닝"
  - okr: "OKR 목표 설정"
  - opportunity_spotting: "기회 발견"
  - what_if_scenarios: "가정 시나리오"
```

#### 🏔️ Terroir Notes (표현)
```yaml
techniques:
  - metaphor_mapping: "메타포 매핑"
  - mythic_frameworks: "신화적 프레임워크"
  - emotion_orchestra: "감정 오케스트라"
```

#### 🏛️ Cellar Notes (통합)
```yaml
techniques:
  - business_model_canvas: "비즈니스 모델 캔버스"
  - balanced_scorecard: "균형성과표"
  - meta_analysis: "메타 분석"
  - six_thinking_hats: "6가지 사고 모자"
```

---

## 4. 기술 구현 계획

### 4.1 백엔드 아키텍처 변경

```
backend/app/
├── graph/
│   ├── graph.py                    # 기존 (Standard Tasting)
│   ├── grand_tasting_graph.py      # 신규 (Grand Tasting)
│   ├── graph_factory.py            # 모드별 그래프 선택기
│   └── nodes/
│       ├── marcel.py               # 기존 유지
│       ├── isabella.py             # 기존 유지
│       ├── ...
│       └── tasting_notes/          # 신규: Grand Tasting 노드
│           ├── aroma_notes.py      # problem-analysis
│           ├── palate_notes.py     # innovation
│           ├── body_notes.py       # risk-analysis
│           ├── finish_notes.py     # user-centricity
│           ├── balance_notes.py    # feasibility
│           ├── vintage_notes.py    # opportunity
│           ├── terroir_notes.py    # presentation
│           └── cellar_notes.py     # synthesis
│
├── techniques/
│   ├── definitions/                # 75개 YAML 정의 (Fairthon 포팅)
│   │   ├── aroma/
│   │   │   ├── five-whys.yaml
│   │   │   └── ...
│   │   ├── palate/
│   │   ├── body/
│   │   ├── finish/
│   │   ├── balance/
│   │   ├── vintage/
│   │   ├── terroir/
│   │   └── cellar/
│   ├── registry.py                 # 기법 레지스트리
│   ├── mappings.py                 # 항목-기법 매핑
│   └── yaml_technique.py           # YAML 기법 실행기
│
└── api/routes/
    └── evaluate.py                 # evaluation_mode 파라미터 추가
```

### 4.2 API 변경사항

```python
# POST /api/evaluate
{
    "github_url": "https://github.com/user/repo",
    "evaluation_mode": "standard_tasting" | "grand_tasting",  # 신규 파라미터
    "model_id": "gemini-3-flash",
    "language": "ko"
}
```

```python
# backend/app/graph/graph_factory.py
from app.graph.graph import create_evaluation_graph as create_standard_graph
from app.graph.grand_tasting_graph import create_grand_tasting_graph

def get_evaluation_graph(mode: str = "standard_tasting"):
    """평가 모드에 따른 그래프 선택"""
    if mode == "standard_tasting":
        return create_standard_graph()
    elif mode == "grand_tasting":
        return create_grand_tasting_graph()
    raise ValueError(f"Unknown evaluation mode: {mode}")
```

### 4.3 프론트엔드 변경사항

```tsx
// src/components/evaluation/EvaluationModeSelector.tsx
export type EvaluationMode = "standard_tasting" | "grand_tasting";

const modes = [
  {
    id: "standard_tasting" as const,
    title: "Standard Tasting",
    subtitle: "Six Sommeliers",
    description: "6명의 전문 소믈리에가 코드를 테이스팅합니다",
    duration: "~2분",
    icon: Wine,
    features: [
      "Marcel - 구조 분석",
      "Isabella - 품질 평가",
      "Heinrich - 보안 검증",
      "Sofia - 혁신 탐색",
      "Laurent - 구현 품질",
      "Jean-Pierre - 최종 통합"
    ],
    recommended: true,
  },
  {
    id: "grand_tasting" as const,
    title: "Grand Tasting",
    subtitle: "Sommelier Masterclass",
    description: "75개 분석 기법으로 심층 분석을 수행합니다",
    duration: "~5분",
    icon: Trophy,
    features: [
      "Aroma Notes - 문제 분석",
      "Palate Notes - 혁신 평가",
      "Body Notes - 리스크 분석",
      "Finish Notes - 사용자 공감",
      "Balance Notes - 실현성",
      "Vintage Notes - 기회 발굴",
      "Terroir Notes - 표현력",
      "Cellar Notes - 종합 분석"
    ],
    recommended: false,
  },
];
```

---

## 5. 구현 로드맵

### Phase 1: 기반 구축 (3일)

| 작업 | 담당 | 산출물 |
|------|------|--------|
| 75개 YAML 기법 정의 포팅 | Backend | `techniques/definitions/` |
| 기법 레지스트리 구현 | Backend | `techniques/registry.py` |
| 기법-항목 매핑 구현 | Backend | `techniques/mappings.py` |

### Phase 2: Grand Tasting 그래프 (4일)

| 작업 | 담당 | 산출물 |
|------|------|--------|
| 8개 Tasting Notes 노드 구현 | Backend | `graph/nodes/tasting_notes/` |
| Grand Tasting 그래프 조립 | Backend | `graph/grand_tasting_graph.py` |
| 그래프 팩토리 구현 | Backend | `graph/graph_factory.py` |

### Phase 3: API 및 프론트엔드 (3일)

| 작업 | 담당 | 산출물 |
|------|------|--------|
| API 엔드포인트 수정 | Backend | `api/routes/evaluate.py` |
| 모드 선택 UI 구현 | Frontend | `EvaluationModeSelector.tsx` |
| i18n 다국어 지원 | Frontend | `locales/ko.json`, `locales/en.json` |

### Phase 4: 테스트 및 검증 (2일)

| 작업 | 담당 | 산출물 |
|------|------|--------|
| 단위 테스트 | Both | `tests/` |
| 통합 테스트 | Both | E2E 테스트 |
| 성능 검증 | Both | 벤치마크 리포트 |

**총 예상 기간: 12일 (약 2.5주)**

---

## 6. 예상 비용 및 성능

### 토큰 사용량 예상

| 모드 | 입력 토큰 | 출력 토큰 | 예상 비용 (GPT-4) |
|------|----------|----------|------------------|
| Standard Tasting | ~15,000 | ~5,000 | ~$0.60 |
| Grand Tasting | ~50,000 | ~15,000 | ~$1.95 |

### 실행 시간 예상

| 모드 | 병렬 노드 | 순차 노드 | 총 시간 |
|------|----------|----------|--------|
| Standard Tasting | 5 (Sommeliers) | 2 (RAG, JP) | ~120초 |
| Grand Tasting | 8 (Categories) | 3 (RAG, Base, Synth) | ~300초 |

---

## 7. 결론

### 핵심 차별점

1. **브랜딩 일관성**: 모든 기능이 와인 소믈리에 컨셉으로 통일
2. **선택적 심층 분석**: 필요시 Grand Tasting으로 75개 기법 전체 적용
3. **기존 자산 활용**: 현재 Six Sommeliers 시스템 완전 유지

### 권장 사용 시나리오

| 시나리오 | 권장 모드 |
|---------|----------|
| 일반 프로젝트 리뷰 | Standard Tasting |
| 투자 유치 전 검토 | Grand Tasting |
| 해커톤 제출물 평가 | Standard Tasting |
| 학술 프로젝트 심사 | Grand Tasting |
| 빠른 피드백 필요 | Standard Tasting |
| 상세 개선점 도출 | Grand Tasting |

### 다음 단계

1. ✅ 본 제안서 검토 및 승인
2. ⏳ Phase 1 착수: YAML 기법 정의 포팅
3. ⏳ Phase 2-4 순차 진행

---

## 부록 A: 75개 기법 전체 목록

### Aroma Notes (문제 분석) - 11개
| ID | 영문명 | 한글명 |
|----|-------|-------|
| five_whys | Five Whys | 5 Whys |
| 5w1h | 5W1H Analysis | 5W1H 분석 |
| question_storming | Question Storming | 질문 폭풍 |
| failure_analysis | Failure Analysis | 실패 분석 |
| assumption_reversal | Assumption Reversal | 가정 뒤집기 |
| data_mining | Data Mining Insights | 데이터 마이닝 |
| fact_checking | Fact Checking | 팩트 체킹 |
| morphological_analysis | Morphological Analysis | 형태학적 분석 |
| pestle_analysis | PESTLE Analysis | PESTLE 분석 |
| mind_mapping | Mind Mapping | 마인드맵 |
| constraint_mapping | Constraint Mapping | 제약 조건 매핑 |

### Palate Notes (혁신) - 13개
| ID | 영문명 | 한글명 |
|----|-------|-------|
| first_principles | First Principles Thinking | 제1원칙 사고 |
| scamper | SCAMPER | SCAMPER |
| design_thinking | Design Thinking | 디자인 씽킹 |
| triz | TRIZ | 트리즈 |
| cross_pollination | Cross-Pollination | 교차 수분 |
| concept_blending | Concept Blending | 개념 블렌딩 |
| lateral_thinking | Lateral Thinking | 수평적 사고 |
| random_stimulation | Random Stimulation | 랜덤 자극 |
| biomimicry | Biomimicry | 생체모방 |
| analogical_thinking | Analogical Thinking | 유추적 사고 |
| reversal_inversion | Reversal/Inversion | 역전/반전 |
| provocation_technique | Provocation Technique | 도발 기법 |
| quantum_superposition | Quantum Superposition | 양자 중첩 사고 |

### Body Notes (리스크) - 8개
| ID | 영문명 | 한글명 |
|----|-------|-------|
| reverse_brainstorming | Reverse Brainstorming | 역브레인스토밍 |
| pre_mortem | Pre-Mortem Analysis | 사전 부검 |
| swot_analysis | SWOT Analysis | SWOT 분석 |
| fmea | FMEA | 고장모드 영향분석 |
| risk_matrix | Risk Matrix | 리스크 매트릭스 |
| anti_solution | Anti-Solution | 반(反)해결책 |
| devil_advocate | Devil's Advocate | 악마의 옹호자 |
| zombie_apocalypse | Zombie Apocalypse | 좀비 아포칼립스 |

### Finish Notes (사용자 공감) - 12개
| ID | 영문명 | 한글명 |
|----|-------|-------|
| empathy_mapping | Empathy Mapping | 공감 지도 |
| jobs_to_be_done | Jobs to Be Done | 고객 과업 이론 |
| kano_model | Kano Model | 카노 모델 |
| persona_journey | Persona Journey | 페르소나 여정 |
| role_playing | Role Playing | 역할극 |
| emotional_journey | Emotional Journey | 감정 여정 |
| sensory_exploration | Sensory Exploration | 감각 탐험 |
| gut_check | Gut Check | 직감 체크 |
| body_wisdom_dialogue | Body Wisdom Dialogue | 몸의 지혜 대화 |
| inner_child_conference | Inner Child Conference | 내면 아이 회의 |
| alien_anthropologist | Alien Anthropologist | 외계인 인류학자 |
| first_impression_analysis | First Impression Analysis | 첫인상 분석 |

### Balance Notes (실현성) - 8개
| ID | 영문명 | 한글명 |
|----|-------|-------|
| technology_readiness_level | Technology Readiness Level | 기술성숙도(TRL) |
| porters_five_forces | Porter's Five Forces | 포터의 5가지 경쟁요인 |
| ecosystem_thinking | Ecosystem Thinking | 생태계 사고 |
| chaos_engineering | Chaos Engineering Mindset | 카오스 엔지니어링 |
| resource_constraints | Resource Constraints | 자원 제약 |
| evolutionary_pressure | Evolutionary Pressure | 진화적 압력 |
| trait_transfer | Trait Transfer | 특성 전이 |
| decision_tree_mapping | Decision Tree Mapping | 의사결정 트리 |

### Vintage Notes (기회) - 10개
| ID | 영문명 | 한글명 |
|----|-------|-------|
| scenario_planning | Scenario Planning | 시나리오 플래닝 |
| okr | OKR | 목표 및 핵심 결과 |
| opportunity_spotting | Opportunity Spotting | 기회 발견 |
| what_if_scenarios | What If Scenarios | 가정 시나리오 |
| value_mapping | Value Proposition Mapping | 가치 제안 매핑 |
| strength_analysis | Strength Analysis | 강점 분석 |
| plus_points | Plus Points | 장점 포인트 |
| yes_and_building | Yes-And Building | 예스-앤드 구축 |
| future_self_interview | Future Self Interview | 미래 자아 인터뷰 |
| permission_giving | Permission Giving | 허락 부여 |

### Terroir Notes (표현) - 5개
| ID | 영문명 | 한글명 |
|----|-------|-------|
| metaphor_mapping | Metaphor Mapping | 메타포 매핑 |
| mythic_frameworks | Mythic Frameworks | 신화적 프레임워크 |
| emotion_orchestra | Emotion Orchestra | 감정 오케스트라 |
| time_travel_talk_show | Time Travel Talk Show | 시간여행 토크쇼 |
| drunk_history_retelling | Drunk History Retelling | 취중진담 역사 |

### Cellar Notes (통합) - 8개
| ID | 영문명 | 한글명 |
|----|-------|-------|
| business_model_canvas | Business Model Canvas | 비즈니스 모델 캔버스 |
| balanced_scorecard | Balanced Scorecard | 균형성과표 |
| meta_analysis | Meta-Analysis | 메타 분석 |
| six_thinking_hats | Six Thinking Hats | 6가지 사고 모자 |
| synthesis_framework | Synthesis Framework | 종합 프레임워크 |
| priority_matrix | Priority Matrix | 우선순위 매트릭스 |
| consensus_building | Consensus Building | 합의 형성 |
| indigenous_wisdom | Indigenous Wisdom | 토착 지혜 |

---

## 부록 B: 소믈리에 ↔ Hat 매핑 상세

| Sommelier | Wine Role | Hat | Thinking Mode | 주요 평가 항목 |
|-----------|-----------|-----|---------------|--------------|
| **Marcel** | Cellar Master | White | 사실과 데이터 | A1, A2 (문제정의) |
| **Isabella** | Wine Critic | Red | 감성과 직관 | A2, A3, D3 (UX) |
| **Heinrich** | Quality Inspector | Black | 리스크와 비판 | B3, B4, C3 (보안) |
| **Sofia** | Vineyard Scout | Yellow | 기회와 긍정 | A4, B1 (시장성) |
| **Laurent** | Winemaker | Green | 창의와 혁신 | A3, B1, B3 (기술) |
| **Jean-Pierre** | Master Sommelier | Blue | 프로세스 통합 | 전체 종합 |
