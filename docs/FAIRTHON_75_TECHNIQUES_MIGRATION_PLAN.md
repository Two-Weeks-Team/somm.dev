# Fairthon 75기법 vs somm.dev 아키텍처 비교 분석 보고서

> 작성일: 2026-02-06
> 목적: Fairthon의 75기법 아키텍처를 somm.dev에 적용하기 위한 분석 및 개선 계획

---

## 1. 핵심 개념 정리

### Fairthon의 3가지 평가 모드

| 모드 | 설명 | 특징 |
|------|------|------|
| **BMAD Quick** | 빠른 기본 평가 | 단일 BMAD 에이전트, 4개 카테고리 평가, ~30초 |
| **Six Hats (6햇기법)** | Edward de Bono의 6가지 사고 모자 | 5개 분석 햇 + 1개 통합 햇, P0+P1 기법 적용, ~2분 |
| **Full Techniques (75기법)** | 75개 분석 기법 전체 적용 | 8개 카테고리, 49개 활성 기법, ~5분 |

### 75기법 아키텍처 (Fairthon)

```
3-Layer Evaluation Architecture:
├── Layer 1: BMAD Framework (17 평가 항목)
├── Layer 2: Six Thinking Hats (6개 사고 관점)
└── Layer 3: 75 Techniques (분석 기법)

8개 기법 카테고리:
├── problem-analysis (9개) - 문제 분석 기법
├── innovation (9개) - 혁신 기법
├── risk-analysis (5개) - 리스크 분석 기법
├── user-centricity (7개) - 사용자 중심 기법
├── feasibility (6개) - 실현 가능성 기법
├── opportunity (4개) - 기회 탐색 기법
├── presentation (5개) - 프레젠테이션 기법
└── synthesis (4개) - 종합 분석 기법
```

---

## 2. somm.dev 현재 아키텍처

### 현재 구조 (단일 모드)

```
somm.dev/backend/
├── app/
│   ├── graph/
│   │   ├── graph.py          # 단일 LangGraph (6 Sommelier)
│   │   ├── nodes/            # Marcel, Isabella, Heinrich, Sofia, Laurent, JeanPierre
│   │   └── state.py
│   └── techniques/
│       ├── loader.py         # YAML 기법 로더 (기초)
│       ├── schema.py         # 기법 정의 스키마
│       └── definitions/
│           └── basic.yaml    # 단일 기본 기법 정의
```

### somm.dev의 6 Sommelier 에이전트

| Sommelier | 역할 | Fairthon 매핑 |
|-----------|------|---------------|
| Marcel | Structure & Metrics | White Hat (사실 분석) |
| Isabella | Code Quality | Red Hat (감성 분석) |
| Heinrich | Testing & Security | Black Hat (리스크 분석) |
| Sofia | Innovation & Tech | Yellow/Green Hat (기회/혁신) |
| Laurent | Implementation | Green Hat (창의적 분석) |
| Jean-Pierre | Final Synthesis | Blue Hat (통합) |

---

## 3. 현재 4가지 모드의 적용 기법 분석

### Fairthon의 실제 기법 적용

| 모드 | 적용 기법 수 | 우선순위 |
|------|------------|---------|
| BMAD Quick | ~4개 (P0 핵심만) | P0 only |
| Six Hats | ~15개 (P0+P1) | P0 + P1 |
| Full Techniques | 49개 (전체) | P0 + P1 + P2 |

### 기법 우선순위 체계

```python
# Fairthon의 technique_mappings.py에서
TECHNIQUE_ITEM_MAPPINGS = {
    # P0 - 핵심 필수 기법
    "five_whys": { "priority": "P0", "category": "analysis" },
    "first_principles": { "priority": "P0", "category": "innovation" },
    "reverse_brainstorming": { "priority": "P0", "category": "risk" },
    "scamper": { "priority": "P0", "category": "innovation" },
    "swot_analysis": { "priority": "P0", "category": "risk" },
    "business_model_canvas": { "priority": "P0", "category": "synthesis" },
    
    # P1 - 중요 기법
    "5w1h": { "priority": "P1", "category": "analysis" },
    "empathy_mapping": { "priority": "P1", "category": "empathy" },
    "design_thinking": { "priority": "P1", "category": "innovation" },
    # ... 더 많은 P1 기법
    
    # P2 - 선택적 기법
    "chaos_engineering": { "priority": "P2", "category": "risk" },
    # ... 더 많은 P2 기법
}
```

---

## 4. somm.dev 개선 계획

### 4.1 Phase 1: 기법 시스템 도입

**현재 상태:**
- `techniques/definitions/basic.yaml` - 단일 기본 정의만 존재
- 기법 선택/적용 로직 없음

**개선 목표:**
```
backend/app/techniques/
├── definitions/           # Fairthon에서 포팅
│   ├── problem-analysis/
│   │   ├── five-whys.yaml
│   │   ├── 5w1h.yaml
│   │   └── ...
│   ├── innovation/
│   │   ├── scamper.yaml
│   │   ├── first-principles.yaml
│   │   └── ...
│   └── ... (8개 카테고리)
├── registry.py           # 기법 레지스트리
├── mappings.py           # 항목-기법 매핑
└── yaml_technique.py     # YAML 기법 실행기
```

### 4.2 Phase 2: 다중 평가 모드 지원

**그래프 아키텍처 확장:**

```python
# 새로운 그래프 구조
backend/app/graph/
├── graph.py              # 현재 (6 Sommelier 유지)
├── six_hats_graph.py     # 새로 추가 (Fairthon 포팅)
├── full_techniques_graph.py  # 새로 추가 (75기법)
└── graph_factory.py      # 모드별 그래프 생성기
```

### 4.3 Phase 3: 모드 선택 UI

**프론트엔드 컴포넌트 추가:**

```tsx
// src/components/evaluation/EvaluationModeSelector.tsx
export type EvaluationMode = "sommelier" | "six_hats" | "full_techniques";

const modes = [
  {
    id: "sommelier",
    title: "Sommelier Quick",
    description: "6명의 소믈리에 에이전트 평가",
    duration: "~1분",
    icon: Wine,
    features: ["6 전문 에이전트", "코드 품질 중심", "빠른 피드백"],
  },
  {
    id: "six_hats",
    title: "Six Thinking Hats",
    description: "6가지 사고 관점의 체계적 분석",
    duration: "~2분",
    icon: Hat,
    features: ["6가지 사고 모자", "P0+P1 기법 적용", "균형잡힌 분석"],
    recommended: true,
  },
  {
    id: "full_techniques",
    title: "Full 75 Techniques",
    description: "75개 분석 기법 전체 적용",
    duration: "~5분",
    icon: Shield,
    features: ["49개 활성 기법", "8개 카테고리", "심층 분석"],
  },
];
```

---

## 5. 6햇기법 vs 75기법 선택 화면 제안

### 5.1 UI/UX 설계

```
┌─────────────────────────────────────────────────────────────┐
│                    평가 모드 선택                            │
│  프로젝트에 맞는 평가 방식을 선택하세요                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ 🍷 Quick    │  │ 🎩 Six Hats │  │ 🛡️ Full     │        │
│  │             │  │ [추천]      │  │             │        │
│  │ ~1분        │  │ ~2분        │  │ ~5분        │        │
│  │             │  │             │  │             │        │
│  │ 6 Sommelier │  │ 6 Thinking  │  │ 75 기법     │        │
│  │ 빠른 피드백  │  │ 균형 분석   │  │ 심층 분석   │        │
│  │             │  │             │  │             │        │
│  │ • 코드 품질  │  │ • White Hat │  │ • 문제 분석 │        │
│  │ • 구조 점검  │  │ • Red Hat   │  │ • 혁신 평가 │        │
│  │ • 보안 리뷰  │  │ • Black Hat │  │ • 리스크    │        │
│  │             │  │ • Yellow    │  │ • 사용자 UX │        │
│  │             │  │ • Green Hat │  │ • 실현성    │        │
│  │             │  │ • Blue Hat  │  │ • 기회 탐색 │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 모드 전환 로직

```typescript
// API 요청 시 모드 전달
const evaluateProject = async (mode: EvaluationMode) => {
  const formData = new FormData();
  formData.append("evaluation_mode", mode);
  // ...
};
```

```python
# 백엔드에서 그래프 선택
def get_evaluation_graph(mode: str):
    if mode == "sommelier":
        return create_sommelier_graph()  # 현재 6 Sommelier
    elif mode == "six_hats":
        return create_six_hats_graph()   # Fairthon 포팅
    elif mode == "full_techniques":
        return create_full_techniques_graph()  # 75기법
    raise ValueError(f"Unknown mode: {mode}")
```

---

## 6. 마이그레이션 로드맵

| Phase | 작업 | 예상 기간 |
|-------|------|----------|
| **1** | 기법 정의 YAML 포팅 (75개) | 2일 |
| **2** | `six_hats_graph.py` 포팅 | 3일 |
| **3** | `full_techniques_graph.py` 포팅 | 3일 |
| **4** | API 엔드포인트 수정 (`evaluation_mode` 파라미터) | 1일 |
| **5** | 프론트엔드 `EvaluationModeSelector` 컴포넌트 | 2일 |
| **6** | i18n 다국어 지원 | 1일 |
| **7** | 테스트 및 검증 | 2일 |

**총 예상 기간: 2주**

---

## 7. 핵심 포팅 대상 파일

### Fairthon → somm.dev

| Fairthon 파일 | somm.dev 대상 | 우선순위 |
|--------------|--------------|---------|
| `graphs/six_hats_graph.py` | `graph/six_hats_graph.py` | P0 |
| `graphs/full_techniques_graph.py` | `graph/full_techniques_graph.py` | P0 |
| `techniques/templates/*.yaml` (75개) | `techniques/definitions/` | P0 |
| `techniques/yaml_technique.py` | `techniques/yaml_technique.py` | P0 |
| `criteria/technique_mappings.py` | `techniques/mappings.py` | P1 |
| `criteria/hat_mappings.py` | `techniques/hat_mappings.py` | P1 |
| `components/EvaluationModeSelector.tsx` | `components/evaluation/` | P1 |

---

## 8. 결론 및 권장사항

### 즉시 실행 가능한 작업

1. **Fairthon 75개 YAML 기법 정의 복사** - 가장 빠른 가치 추가
2. **`six_hats_graph.py` 포팅** - 6햇기법 지원
3. **API에 `evaluation_mode` 파라미터 추가**

### 장기적 고려사항

- somm.dev의 **6 Sommelier 브랜딩 유지**하면서 Six Hats 방법론 적용
- 기존 Sommelier ↔ Six Hats 간 **역할 매핑** 명확화
- **토큰 비용 최적화** (Full Techniques는 비용이 높음)

---

## 부록: Fairthon 75개 기법 전체 목록

### problem-analysis (9개)
- five-whys.yaml
- 5w1h.yaml
- question-storming.yaml
- failure-analysis.yaml
- assumption-reversal.yaml
- data-mining.yaml
- fact-checking.yaml
- morphological-analysis.yaml
- pestle-analysis.yaml
- mind-mapping.yaml
- constraint-mapping.yaml

### innovation (9개)
- provocation-technique.yaml
- quantum-superposition.yaml
- scamper.yaml
- reversal-inversion.yaml
- first-principles-thinking.yaml
- concept-blending.yaml
- triz.yaml
- random-stimulation.yaml
- lateral-thinking.yaml
- design-thinking.yaml
- cross-pollination.yaml
- biomimicry.yaml
- analogical-thinking.yaml

### risk-analysis (5개)
- reverse-brainstorming.yaml
- risk-matrix.yaml
- pre-mortem.yaml
- anti-solution.yaml
- zombie-apocalypse.yaml
- swot-analysis.yaml
- fmea.yaml
- devil-advocate.yaml

### user-centricity (7개)
- persona-journey.yaml
- sensory-exploration.yaml
- gut-check.yaml
- body-wisdom-dialogue.yaml
- emotional-journey.yaml
- role-playing.yaml
- jobs-to-be-done.yaml
- kano-model.yaml
- inner-child-conference.yaml
- empathy-mapping.yaml
- first-impression-analysis.yaml
- alien-anthropologist.yaml

### feasibility (6개)
- resource-constraints.yaml
- ecosystem-thinking.yaml
- evolutionary-pressure.yaml
- chaos-engineering.yaml
- trait-transfer.yaml
- technology-readiness-level.yaml
- porters-five-forces.yaml
- decision-tree-mapping.yaml

### opportunity (4개)
- plus-points.yaml
- what-if-scenarios.yaml
- yes-and-building.yaml
- value-mapping.yaml
- strength-analysis.yaml
- scenario-planning.yaml
- okr.yaml
- future-self-interview.yaml
- opportunity-spotting.yaml
- permission-giving.yaml

### presentation (5개)
- drunk-history-retelling.yaml
- time-travel-talk-show.yaml
- mythic-frameworks.yaml
- metaphor-mapping.yaml
- emotion-orchestra.yaml

### synthesis (4개)
- indigenous-wisdom.yaml
- consensus-building.yaml
- synthesis-framework.yaml
- six-thinking-hats.yaml
- priority-matrix.yaml
- meta-analysis.yaml
- balanced-scorecard.yaml
- business-model-canvas.yaml
