# 🍷 Somm.dev - Evaluation Criteria System

> **Four customizable evaluation modes for different use cases**

---

## 1. Overview

Somm.dev provides **four evaluation criteria modes** to suit different evaluation needs:

| Mode | Use Case | Description |
|------|----------|-------------|
| **Basic** | General code review | Standard code quality evaluation across common dimensions |
| **Hackathon** | Competition judging | Gemini 3 Hackathon criteria alignment (40/20/30/10 weights) |
| **Academic** | Research projects | Scholarly evaluation focusing on novelty and methodology |
| **Custom** | Special requirements | User-defined criteria for specific needs |

---

## 2. Basic Evaluation

### 2.1 Purpose
Standard code quality evaluation suitable for most repositories.

### 2.2 Evaluation Aspects

```python
BASIC_CRITERIA = {
    "name": "Basic Evaluation",
    "description": "Standard code quality evaluation",
    "aspects": [
        {
            "name": "code_quality",
            "weight": 0.25,
            "description": "Code readability, maintainability, and best practices"
        },
        {
            "name": "architecture",
            "weight": 0.20,
            "description": "System design, modularity, and scalability"
        },
        {
            "name": "documentation",
            "weight": 0.20,
            "description": "README quality, code comments, and API docs"
        },
        {
            "name": "testing",
            "weight": 0.20,
            "description": "Test coverage, test quality, and CI/CD"
        },
        {
            "name": "security",
            "weight": 0.15,
            "description": "Security practices, vulnerability checks"
        }
    ]
}
```

### 2.3 Prompt Template

```python
BASIC_PROMPT = """Evaluate this repository using standard code quality criteria.

## Evaluation Aspects (Weighted)

1. **Code Quality (25%)**
   - Readability and maintainability
   - Adherence to language best practices
   - Consistency in style and naming

2. **Architecture (20%)**
   - System design and modularity
   - Separation of concerns
   - Scalability considerations

3. **Documentation (20%)**
   - README completeness
   - Code comments quality
   - API documentation if applicable

4. **Testing (20%)**
   - Test coverage
   - Test quality and assertions
   - CI/CD integration

5. **Security (15%)**
   - Secure coding practices
   - Dependency vulnerability checks
   - Secret management

## Wine Metaphors to Use
- Code Quality = Balance and harmony
- Architecture = Structure and foundation
- Documentation = Aroma and bouquet
- Testing = Acidity and freshness
- Security = Purity and cleanliness

Provide specific scores (0-100) for each aspect with detailed tasting notes.
"""
```

---

## 3. Hackathon Evaluation (Gemini 3 Hackathon)

### 3.1 Purpose
Aligned with Gemini 3 Hackathon judging criteria for competition submissions.

### 3.2 Evaluation Aspects (Official Weights)

```python
HACKATHON_CRITERIA = {
    "name": "Gemini 3 Hackathon Judging",
    "description": "Official Gemini 3 Hackathon evaluation criteria",
    "aspects": [
        {
            "name": "technical_execution",
            "weight": 0.40,
            "description": "Technical implementation quality and completeness (40%)"
        },
        {
            "name": "innovation_wow",
            "weight": 0.30,
            "description": "Innovation, creativity, and wow factor (30%)"
        },
        {
            "name": "potential_impact",
            "weight": 0.20,
            "description": "Potential real-world impact and usefulness (20%)"
        },
        {
            "name": "presentation_demo",
            "weight": 0.10,
            "description": "Presentation quality and demo clarity (10%)"
        }
    ]
}
```

### 3.3 Prompt Template

```python
HACKATHON_PROMPT = """Evaluate this repository as a Gemini 3 Hackathon submission.

## Official Judging Criteria (Weighted)

### 1. Technical Execution (40%)
**Weight: 40 points**

Assess:
- Code quality and architecture
- Feature completeness
- Technical complexity appropriate for timeframe
- Proper use of Gemini 3 API
- Error handling and edge cases
- Performance optimization

Wine metaphor: **Body and structure** - How well-built is this implementation?

### 2. Innovation & Wow Factor (30%)
**Weight: 30 points**

Assess:
- Creativity of solution
- Novel application of AI/code evaluation
- Unique features not seen elsewhere
- "Aha!" moments in design
- Creative use of wine metaphor

Wine metaphor: **Complexity and uniqueness** - Is this a rare varietal?

### 3. Potential Impact (20%)
**Weight: 20 points**

Assess:
- Real-world applicability
- Problem-solving effectiveness
- Scalability potential
- Value to developers
- Market differentiation

Wine metaphor: **Aging potential** - Will this improve with time and users?

### 4. Presentation & Demo (10%)
**Weight: 10 points**

Assess:
- README quality and clarity
- Demo video effectiveness (if provided)
- Documentation completeness
- Repository organization
- First impression

Wine metaphor: **Appearance and first pour** - How inviting is the presentation?

## Scoring Guide

- **95-100 (Legendary)**: Exceptional hackathon submission, demo-worthy
- **90-94 (Grand Cru)**: Outstanding, prize-worthy entry
- **85-89 (Premier Cru)**: Excellent, solid contender
- **80-84 (Village)**: Good, meets expectations
- **70-79 (Table)**: Acceptable, room for improvement
- **60-69 (House Wine)**: Light effort, casual submission
- **<60 (Corked)**: Below standards, significant issues

Provide detailed feedback for each criterion with specific examples.
"""
```

### 3.4 Hackathon-Specific Considerations

```python
HACKATHON_SPECIFIC_CHECKS = [
    "Is Gemini 3 API properly integrated?",
    "Does the project leverage structured outputs from Gemini?",
    "Is there evidence of multi-agent orchestration?",
    "Does the wine metaphor enhance the UX?",
    "Is the codebase demo-ready?",
    "Are there clear installation and usage instructions?",
    "Is the project deployed and accessible?"
]
```

---

## 4. Academic Research Evaluation

### 4.1 Purpose
For research projects, thesis code, and academic implementations.

### 4.2 Evaluation Aspects

```python
ACADEMIC_CRITERIA = {
    "name": "Academic Research Evaluation",
    "description": "Scholarly evaluation for research projects",
    "aspects": [
        {
            "name": "novelty",
            "weight": 0.25,
            "description": "Originality and contribution to field"
        },
        {
            "name": "methodology",
            "weight": 0.25,
            "description": "Research methodology and approach"
        },
        {
            "name": "reproducibility",
            "weight": 0.20,
            "description": "Code reproducibility and environment setup"
        },
        {
            "name": "documentation",
            "weight": 0.20,
            "description": "Academic documentation quality"
        },
        {
            "name": "impact",
            "weight": 0.10,
            "description": "Potential research impact and citations"
        }
    ]
}
```

### 4.3 Prompt Template

```python
ACADEMIC_PROMPT = """Evaluate this repository as an academic research project.

## Academic Evaluation Criteria (Weighted)

### 1. Novelty (25%)
**Weight: 25 points**

Assess:
- Originality of approach
- Novel algorithms or methods
- Contribution to existing literature
- Innovation in methodology
- Gap identification in field

Wine metaphor: **Unique varietal** - Is this a new discovery?

### 2. Methodology (25%)
**Weight: 25 points**

Assess:
- Scientific rigor
- Appropriate methods for research question
- Experimental design
- Control mechanisms
- Validity of approach

Wine metaphor: **Winemaking technique** - Is the craft sound?

### 3. Reproducibility (20%)
**Weight: 20 points**

Assess:
- Clear environment setup (requirements.txt, environment.yml)
- Dataset availability and documentation
- Step-by-step reproduction instructions
- Version pinning
- Docker/containerization if applicable

Wine metaphor: **Consistency** - Can this vintage be replicated?

### 4. Documentation (20%)
**Weight: 20 points**

Assess:
- Academic paper quality README
- Inline code documentation
- Jupyter notebooks with explanations
- Citation of prior work
- Theory explanations

Wine metaphor: **Label and provenance** - Is the origin well-documented?

### 5. Research Impact (10%)
**Weight: 10 points**

Assess:
- Potential for citations
- Applicability to other researchers
- Open source contribution value
- Dataset/tool contribution

Wine metaphor: **Cellar investment** - Will this appreciate over time?

## Academic-Specific Checks

- Are datasets properly cited and accessible?
- Are there clear hypotheses or research questions?
- Is the code organized by experiment?
- Are results reproducible and documented?
- Are limitations acknowledged?
"""
```

---

## 5. Custom Evaluation

### 5.1 Purpose
User-defined criteria for specific evaluation needs.

### 5.2 Structure

```python
CUSTOM_CRITERIA_TEMPLATE = {
    "name": "Custom Criteria",
    "description": "User-defined evaluation criteria",
    "aspects": [],  # Populated dynamically
    "custom_instructions": ""  # Additional user instructions
}
```

### 5.3 Custom Criteria Definition

```python
class CustomCriteriaDefinition(BaseModel):
    """Schema for custom evaluation criteria."""
    
    name: str = Field(description="Name of custom criteria set")
    description: str = Field(description="Brief description")
    
    aspects: List[dict] = Field(
        description="List of evaluation aspects",
        min_items=1,
        max_items=8
    )
    
    custom_instructions: Optional[str] = Field(
        default=None,
        description="Additional instructions for evaluators"
    )
    
    @validator('aspects')
    def validate_weights(cls, v):
        total_weight = sum(aspect.get('weight', 0) for aspect in v)
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total_weight}")
        return v

# Example custom criteria
EXAMPLE_CUSTOM = {
    "name": "Startup MVP Evaluation",
    "description": "Evaluate startup MVP codebases",
    "aspects": [
        {"name": "speed_to_market", "weight": 0.30},
        {"name": "mvp_scope", "weight": 0.25},
        {"name": "scalability_roadmap", "weight": 0.20},
        {"name": "user_onboarding", "weight": 0.15},
        {"name": "analytics_integration", "weight": 0.10}
    ],
    "custom_instructions": "Focus on lean startup principles and rapid iteration capability."
}
```

### 5.4 Custom Prompt Generation

```python
def generate_custom_prompt(criteria: CustomCriteriaDefinition) -> str:
    """Generate prompt from custom criteria definition."""
    
    aspects_text = "\n".join([
        f"### {i+1}. {aspect['name'].replace('_', ' ').title()} ({aspect['weight']*100:.0f}%)\n"
        f"**Weight: {aspect['weight']*100:.0f} points**\n"
        f"Evaluate based on: {aspect.get('description', 'General assessment')}\n"
        for i, aspect in enumerate(criteria.aspects)
    ])
    
    return f"""Evaluate this repository using custom criteria: {criteria.name}

## {criteria.description}

## Evaluation Aspects (Weighted)

{aspects_text}

## Additional Instructions

{criteria.custom_instructions or 'Provide comprehensive evaluation for each aspect.'}

## Wine Metaphors

Apply appropriate wine metaphors to each aspect:
- High scores = Full-bodied, well-balanced
- Low scores = Light, needs development
- Unique features = Rare varietal characteristics
"""
```

---

## 6. Criteria Selection Flow

### 6.1 Frontend Selection

```typescript
// components/evaluation/CriteriaSelector.tsx
const CRITERIA_OPTIONS = [
  {
    value: "basic",
    label: "Basic Evaluation",
    description: "Standard code quality review",
    icon: "🍷",
    recommended: true
  },
  {
    value: "hackathon",
    label: "Gemini 3 Hackathon",
    description: "Competition judging criteria",
    icon: "🏆",
    badge: "Official"
  },
  {
    value: "academic",
    label: "Academic Research",
    description: "Scholarly project evaluation",
    icon: "🎓"
  },
  {
    value: "custom",
    label: "Custom Criteria",
    description: "Define your own criteria",
    icon: "⚙️",
    requiresConfig: true
  }
];

export function CriteriaSelector({
  value,
  onChange,
  showCustomConfig
}: CriteriaSelectorProps) {
  return (
    <div className="criteria-selector">
      {CRITERIA_OPTIONS.map((option) => (
        <CriteriaCard
          key={option.value}
          {...option}
          selected={value === option.value}
          onClick={() => onChange(option.value)}
        />
      ))}
      
      {value === "custom" && showCustomConfig && (
        <CustomCriteriaBuilder />
      )}
    </div>
  );
}
```

### 6.2 Backend Processing

```python
# app/api/routes/evaluate.py
from app.prompts.criteria import (
    get_criteria_prompt,
    EvaluationCriteria
)

@router.post("/evaluate")
async def create_evaluation(
    request: EvaluationRequest,
    current_user: User = Depends(get_current_user)
):
    """Create new evaluation with selected criteria."""
    
    # Validate criteria
    try:
        criteria = EvaluationCriteria(request.criteria)
    except ValueError:
        raise HTTPException(400, "Invalid evaluation criteria")
    
    # Get criteria-specific prompt
    criteria_prompt = get_criteria_prompt(criteria)
    
    # Create evaluation record
    evaluation = await Evaluation.create(
        user_id=current_user.id,
        repo_url=request.repo_url,
        criteria=criteria.value,
        status="pending"
    )
    
    # Start evaluation with criteria context
    await evaluation_service.start(
        evaluation_id=evaluation.id,
        repo_url=request.repo_url,
        criteria=criteria,
        criteria_prompt=criteria_prompt
    )
    
    return {"evaluation_id": evaluation.id, "status": "pending"}
```

---

## 7. Criteria Comparison

### 7.1 Aspect Weight Comparison

```
┌─────────────────────┬───────────┬────────────┬───────────┬────────┐
│ Aspect              │ Basic     │ Hackathon  │ Academic  │ Custom │
├─────────────────────┼───────────┼────────────┼───────────┼────────┤
│ Code Quality        │    25%    │    40%*    │    15%    │   --   │
│ Innovation          │    10%    │    30%     │    25%    │   --   │
│ Documentation       │    20%    │    10%     │    20%    │   --   │
│ Testing             │    20%    │    --      │    --     │   --   │
│ Security            │    15%    │    --      │    --     │   --   │
│ Architecture        │    20%    │  (in 40%)  │    --     │   --   │
│ Impact              │    --     │    20%     │    10%    │   --   │
│ Reproducibility     │    --     │    --      │    20%    │   --   │
│ Methodology         │    --     │    --      │    25%    │   --   │
│ Presentation        │    --     │    10%     │    --     │   --   │
└─────────────────────┴───────────┴────────────┴───────────┴────────┘

* Technical Execution includes code quality + architecture
```

### 7.2 Use Case Recommendations

| Scenario | Recommended Criteria | Reason |
|----------|---------------------|--------|
| Portfolio review | **Basic** | Balanced code quality assessment |
| Gemini 3 Hackathon | **Hackathon** | Official judging alignment |
| Thesis code | **Academic** | Research-focused evaluation |
| Startup pitch | **Custom** | MVP-specific criteria |
| Open source lib | **Basic** | General quality for adoption |
| Research paper | **Academic** | Scholarly rigor |
| Side project | **Basic** or **House Wine** tier |

---

## 8. Implementation

### 8.1 Criteria Prompts Location

```
backend/app/prompts/criteria/
├── __init__.py
├── base.py              # Base criteria classes
├── basic.py             # Basic evaluation prompts
├── hackathon.py         # Gemini 3 Hackathon prompts
├── academic.py          # Academic research prompts
└── custom.py            # Custom criteria builder
```

### 8.2 Adding New Criteria

```python
# To add a new criteria mode:

1. Add to EvaluationCriteria enum:
   class EvaluationCriteria(str, Enum):
       BASIC = "basic"
       HACKATHON = "hackathon"
       ACADEMIC = "academic"
       CUSTOM = "custom"
       NEW_MODE = "new_mode"  # Add here

2. Create prompt file:
   # app/prompts/criteria/new_mode.py
   NEW_MODE_PROMPT = """..."""

3. Register in factory:
   # app/prompts/criteria/__init__.py
   CRITERIA_PROMPTS = {
       EvaluationCriteria.BASIC: BASIC_PROMPT,
       EvaluationCriteria.NEW_MODE: NEW_MODE_PROMPT,  # Add here
   }

4. Update frontend selector
```

---

*"The right criteria for the right occasion."* 🍷

— Somm Evaluation System
