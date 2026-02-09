"""BMAD 17-item evaluation canon definitions."""

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class BMADItem:
    """Single BMAD evaluation item."""

    item_id: str
    name: str
    description: str
    max_score: int
    category: str
    rubric: Dict[int, str]


@dataclass(frozen=True)
class BMADCategory:
    """BMAD evaluation category."""

    category_id: str
    name: str
    max_score: int
    items: List[str]


# Category A — Problem Definition (25 pts)
_A1 = BMADItem(
    item_id="A1",
    name="Problem Clarity",
    description="How clearly is the problem defined?",
    max_score=7,
    category="A",
    rubric={
        1: "Problem unclear/missing",
        3: "Problem partially defined",
        5: "Problem clearly stated",
        7: "Exceptional clarity with context, scope, and constraints",
    },
)

_A2 = BMADItem(
    item_id="A2",
    name="Target User Identification",
    description="Who are the target users?",
    max_score=6,
    category="A",
    rubric={
        1: "No users identified",
        3: "Users vaguely described",
        5: "Users well-identified",
        6: "Detailed personas with needs analysis",
    },
)

_A3 = BMADItem(
    item_id="A3",
    name="Problem Significance",
    description="Why does this problem matter?",
    max_score=6,
    category="A",
    rubric={
        1: "Significance unclear",
        3: "Some importance shown",
        5: "Clear significance demonstrated",
        6: "Compelling case with data/evidence",
    },
)

_A4 = BMADItem(
    item_id="A4",
    name="Existing Solutions Analysis",
    description="What alternatives exist?",
    max_score=6,
    category="A",
    rubric={
        1: "No analysis of alternatives",
        3: "Basic competitor mention",
        5: "Good competitive analysis",
        6: "Thorough analysis with differentiation",
    },
)

# Category B — Technical Design (25 pts)
_B1 = BMADItem(
    item_id="B1",
    name="Architecture Design",
    description="System architecture quality.",
    max_score=7,
    category="B",
    rubric={
        1: "No architecture",
        3: "Basic structure",
        5: "Well-designed architecture",
        7: "Exceptional architecture with clear patterns",
    },
)

_B2 = BMADItem(
    item_id="B2",
    name="Technology Choice",
    description="Appropriateness of tech stack.",
    max_score=6,
    category="B",
    rubric={
        1: "Inappropriate choices",
        3: "Adequate choices",
        5: "Well-reasoned choices",
        6: "Optimal choices with justification",
    },
)

_B3 = BMADItem(
    item_id="B3",
    name="Scalability Consideration",
    description="Growth planning.",
    max_score=6,
    category="B",
    rubric={
        1: "No scalability thought",
        3: "Basic scalability",
        5: "Good scalability planning",
        6: "Comprehensive scalability strategy",
    },
)

_B4 = BMADItem(
    item_id="B4",
    name="Security Design",
    description="Security measures.",
    max_score=6,
    category="B",
    rubric={
        1: "No security consideration",
        3: "Basic security",
        5: "Good security practices",
        6: "Comprehensive security architecture",
    },
)

# Category C — Implementation (30 pts)
_C1 = BMADItem(
    item_id="C1",
    name="Code Quality",
    description="Code cleanliness and standards.",
    max_score=7,
    category="C",
    rubric={
        1: "Poor code quality",
        3: "Basic code quality",
        5: "Good code quality",
        7: "Exceptional code quality with best practices",
    },
)

_C2 = BMADItem(
    item_id="C2",
    name="Testing Coverage",
    description="Test quality and coverage.",
    max_score=6,
    category="C",
    rubric={
        1: "No tests",
        3: "Basic tests",
        5: "Good test coverage",
        6: "Comprehensive testing strategy",
    },
)

_C3 = BMADItem(
    item_id="C3",
    name="Error Handling",
    description="Robustness.",
    max_score=6,
    category="C",
    rubric={
        1: "No error handling",
        3: "Basic error handling",
        5: "Good error handling",
        6: "Comprehensive error handling with recovery",
    },
)

_C4 = BMADItem(
    item_id="C4",
    name="Performance Optimization",
    description="Performance considerations.",
    max_score=5,
    category="C",
    rubric={
        1: "No optimization",
        3: "Basic optimization",
        5: "Well-optimized with benchmarks",
    },
)

_C5 = BMADItem(
    item_id="C5",
    name="CI/CD & DevOps",
    description="Deployment pipeline.",
    max_score=6,
    category="C",
    rubric={
        1: "No CI/CD",
        3: "Basic CI pipeline",
        5: "Good CI/CD setup",
        6: "Comprehensive DevOps with monitoring",
    },
)

# Category D — Documentation (20 pts)
_D1 = BMADItem(
    item_id="D1",
    name="README Quality",
    description="README completeness.",
    max_score=6,
    category="D",
    rubric={
        1: "No/minimal README",
        3: "Basic README",
        5: "Good README",
        6: "Exceptional README with all sections",
    },
)

_D2 = BMADItem(
    item_id="D2",
    name="API Documentation",
    description="API docs quality.",
    max_score=5,
    category="D",
    rubric={
        1: "No API docs",
        3: "Basic API docs",
        5: "Comprehensive API documentation",
    },
)

_D3 = BMADItem(
    item_id="D3",
    name="Code Documentation",
    description="In-code documentation.",
    max_score=5,
    category="D",
    rubric={
        1: "No code docs",
        3: "Basic comments",
        5: "Well-documented with docstrings",
    },
)

_D4 = BMADItem(
    item_id="D4",
    name="Contributing Guide",
    description="Contributor experience.",
    max_score=4,
    category="D",
    rubric={
        1: "No contributing guide",
        2: "Basic guide",
        3: "Good guide",
        4: "Comprehensive contributing guide",
    },
)

BMAD_ITEMS: Dict[str, BMADItem] = {
    "A1": _A1,
    "A2": _A2,
    "A3": _A3,
    "A4": _A4,
    "B1": _B1,
    "B2": _B2,
    "B3": _B3,
    "B4": _B4,
    "C1": _C1,
    "C2": _C2,
    "C3": _C3,
    "C4": _C4,
    "C5": _C5,
    "D1": _D1,
    "D2": _D2,
    "D3": _D3,
    "D4": _D4,
}

BMAD_CATEGORIES: Dict[str, BMADCategory] = {
    "A": BMADCategory(
        category_id="A",
        name="Problem Definition",
        max_score=25,
        items=["A1", "A2", "A3", "A4"],
    ),
    "B": BMADCategory(
        category_id="B",
        name="Technical Design",
        max_score=25,
        items=["B1", "B2", "B3", "B4"],
    ),
    "C": BMADCategory(
        category_id="C",
        name="Implementation",
        max_score=30,
        items=["C1", "C2", "C3", "C4", "C5"],
    ),
    "D": BMADCategory(
        category_id="D",
        name="Documentation",
        max_score=20,
        items=["D1", "D2", "D3", "D4"],
    ),
}


def get_item(item_id: str) -> BMADItem:
    """Get a BMAD item by ID. Raises KeyError if not found."""
    return BMAD_ITEMS[item_id]


def list_items() -> List[BMADItem]:
    """List all 17 BMAD items in order (A1, A2, ..., D4)."""
    return [BMAD_ITEMS[k] for k in sorted(BMAD_ITEMS.keys())]


def get_items_by_category(category: str) -> List[BMADItem]:
    """Get all items in a category (A, B, C, or D)."""
    return [item for item in BMAD_ITEMS.values() if item.category == category]


def get_category(category_id: str) -> BMADCategory:
    """Get category by ID. Raises KeyError if not found."""
    return BMAD_CATEGORIES[category_id]


def get_max_total() -> int:
    """Return the maximum total score (always 100)."""
    return 100


def get_category_max(category: str) -> int:
    """Return max score for a category."""
    return BMAD_CATEGORIES[category].max_score
