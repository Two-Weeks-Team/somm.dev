"""Grading prompt templates for subjective BMAD evaluation items.

This module contains structured prompt templates for items that require
LLM-based subjective evaluation. Each prompt includes:
- Item description and context
- Scoring rubric with clear criteria
- Expected evidence to support the score
- Output schema specification

Subjective items requiring LLM evaluation:
- A1-A4: Problem Definition (A1: Problem Clarity, A2: Target Users, A3: Significance, A4: Alternatives)
- B2-B4: Technical Design (B2: Technology Choice, B3: Scalability, B4: Security)
- C3, C5: Implementation (C3: Error Handling, C5: CI/CD & DevOps)
- D3-D4: Documentation (D3: Code Documentation, D4: Contributing Guide)
"""

from typing import Dict, Any

# Output schema specification for all LLM grading responses
OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "score": {"type": "integer", "description": "Score value (0 to max_score)"},
        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
        "evidence": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of specific evidence supporting the score",
        },
        "rationale": {
            "type": "string",
            "description": "Detailed explanation for the score",
        },
    },
    "required": ["score", "confidence", "evidence", "rationale"],
}

GRADING_PROMPTS: Dict[str, Dict[str, Any]] = {
    # ==========================================================================
    # Category A: Problem Definition (25 pts)
    # ==========================================================================
    "A1": {
        "name": "Problem Clarity",
        "max_score": 7,
        "description": "How clearly is the problem defined in the repository?",
        "prompt": """Evaluate how clearly the problem is defined in this repository.

Review the README, documentation, and any problem statement files to assess:
1. Is there a clear problem statement?
2. Does it explain what issue the project solves?
3. Is the scope and context well-defined?
4. Are constraints and requirements stated?

Repository Context:
{context}

Provide your evaluation in the required JSON format.""",
        "rubric": {
            0: "No problem statement found",
            1: "Problem mentioned but completely unclear",
            2: "Vague problem statement with minimal context",
            3: "Problem partially defined with some context",
            4: "Clear problem statement but missing scope or constraints",
            5: "Well-defined problem with good context",
            6: "Very clear problem with scope, context, and partial constraints",
            7: "Exceptional clarity with full context, scope, constraints, and requirements",
        },
    },
    "A2": {
        "name": "Target User Identification",
        "max_score": 6,
        "description": "How well are the target users identified and described?",
        "prompt": """Evaluate how well the target users are identified in this repository.

Review the README and documentation to assess:
1. Are target users explicitly mentioned?
2. Is there a clear description of who will use this?
3. Are user needs or pain points described?
4. Are there user personas or use cases?

Repository Context:
{context}

Provide your evaluation in the required JSON format.""",
        "rubric": {
            0: "No users identified",
            1: "Users mentioned but not described",
            2: "Users vaguely described",
            3: "Some user description with basic needs",
            4: "Well-described target users with needs",
            5: "Detailed user identification with use cases",
            6: "Comprehensive user personas with detailed needs analysis",
        },
    },
    "A3": {
        "name": "Problem Significance",
        "max_score": 6,
        "description": "Why does this problem matter? Is the significance demonstrated?",
        "prompt": """Evaluate how well the significance of the problem is demonstrated.

Review the README and documentation to assess:
1. Is there an explanation of why this problem matters?
2. Are there metrics, data, or evidence supporting significance?
3. Is the impact or value proposition clear?
4. Does it explain consequences of not solving this problem?

Repository Context:
{context}

Provide your evaluation in the required JSON format.""",
        "rubric": {
            0: "Significance not mentioned",
            1: "Significance unclear or unjustified",
            2: "Some importance mentioned but not demonstrated",
            3: "Basic significance shown with minimal reasoning",
            4: "Clear significance with reasonable justification",
            5: "Strong significance case with some data/evidence",
            6: "Compelling case with data, metrics, or strong evidence",
        },
    },
    "A4": {
        "name": "Existing Solutions Analysis",
        "max_score": 6,
        "description": "How well are existing alternatives and competitors analyzed?",
        "prompt": """Evaluate the analysis of existing solutions and alternatives.

Review the README and documentation to assess:
1. Are existing solutions or competitors mentioned?
2. Is there a comparison with alternatives?
3. Is the differentiation or unique value explained?
4. Are there clear reasons why this solution is better?

Repository Context:
{context}

Provide your evaluation in the required JSON format.""",
        "rubric": {
            0: "No analysis of alternatives",
            1: "Alternatives mentioned without analysis",
            2: "Basic competitor mention with minimal comparison",
            3: "Some comparison with existing solutions",
            4: "Good competitive analysis with differentiation",
            5: "Thorough analysis with clear value proposition vs alternatives",
            6: "Comprehensive analysis with detailed comparison and positioning",
        },
    },
    # ==========================================================================
    # Category B: Technical Design (25 pts)
    # ==========================================================================
    "B2": {
        "name": "Technology Choice",
        "max_score": 6,
        "description": "How appropriate and well-reasoned are the technology choices?",
        "prompt": """Evaluate the appropriateness and reasoning behind technology choices.

Review the tech stack, dependencies, and any architecture docs to assess:
1. Are the chosen technologies appropriate for the problem?
2. Is there reasoning or justification for key choices?
3. Are trade-offs considered?
4. Are the choices aligned with modern best practices?

Repository Context:
{context}

Provide your evaluation in the required JSON format.""",
        "rubric": {
            0: "No technology information or inappropriate choices",
            1: "Technologies listed without justification",
            2: "Basic technology choices with minimal reasoning",
            3: "Adequate choices with some justification",
            4: "Well-reasoned choices aligned with problem domain",
            5: "Optimal choices with clear justification and trade-off analysis",
            6: "Exceptional choices with comprehensive rationale and best practices",
        },
    },
    "B3": {
        "name": "Scalability Consideration",
        "max_score": 6,
        "description": "How well is growth and scalability planned for?",
        "prompt": """Evaluate the consideration for scalability and growth.

Review the architecture, code structure, and documentation to assess:
1. Are there any scalability considerations mentioned?
2. Is the architecture designed to handle growth?
3. Are there load balancing, caching, or distribution strategies?
4. Are database and infrastructure choices scalable?

Repository Context:
{context}

Provide your evaluation in the required JSON format.""",
        "rubric": {
            0: "No scalability considerations",
            1: "Scalability mentioned but not addressed",
            2: "Basic scalability awareness",
            3: "Some scalability planning in architecture",
            4: "Good scalability design with some strategies",
            5: "Comprehensive scalability strategy for most aspects",
            6: "Complete scalability architecture with all aspects covered",
        },
    },
    "B4": {
        "name": "Security Design",
        "max_score": 6,
        "description": "How comprehensive are the security measures and design?",
        "prompt": """Evaluate the security measures and security-conscious design.

Review the code, configuration, and documentation to assess:
1. Are security considerations present?
2. Is input validation and sanitization implemented?
3. Are there authentication/authorization mechanisms?
4. Are secrets managed properly (no hardcoded credentials)?
5. Are dependencies scanned or kept up to date?

Repository Context:
{context}

Provide your evaluation in the required JSON format.""",
        "rubric": {
            0: "No security considerations",
            1: "Security mentioned but not implemented",
            2: "Basic security awareness (e.g., no obvious vulnerabilities)",
            3: "Some security measures in place",
            4: "Good security practices with validation and auth",
            5: "Strong security architecture with multiple layers",
            6: "Comprehensive security with all best practices implemented",
        },
    },
    # ==========================================================================
    # Category C: Implementation (30 pts)
    # ==========================================================================
    "C3": {
        "name": "Error Handling",
        "max_score": 6,
        "description": "How robust and comprehensive is the error handling?",
        "prompt": """Evaluate the robustness and comprehensiveness of error handling.

Review the code to assess:
1. Are exceptions caught and handled appropriately?
2. Is there input validation with meaningful error messages?
3. Are edge cases and failure modes considered?
4. Is there logging or monitoring for errors?
5. Are there recovery mechanisms or fallback strategies?

Repository Context:
{context}

Provide your evaluation in the required JSON format.""",
        "rubric": {
            0: "No error handling (bare excepts or silent failures)",
            1: "Minimal error handling (few try/catch blocks)",
            2: "Basic error handling for main paths",
            3: "Good error handling for most operations",
            4: "Comprehensive error handling with meaningful messages",
            5: "Thorough error handling with logging and edge cases",
            6: "Exceptional error handling with recovery and monitoring",
        },
    },
    "C5": {
        "name": "CI/CD & DevOps",
        "max_score": 6,
        "description": "How comprehensive is the CI/CD pipeline and DevOps setup?",
        "prompt": """Evaluate the CI/CD pipeline and DevOps practices.

Review configuration files and workflows to assess:
1. Is there a CI pipeline (automated tests, builds)?
2. Is there a CD pipeline (automated deployment)?
3. Are there environment configurations (dev/staging/prod)?
4. Is there monitoring, logging, or observability setup?
5. Are there infrastructure-as-code configurations?

Repository Context:
{context}

Provide your evaluation in the required JSON format.""",
        "rubric": {
            0: "No CI/CD or DevOps setup",
            1: "Basic CI configuration but not functional",
            2: "Basic CI pipeline (tests or builds)",
            3: "Working CI with tests and basic automation",
            4: "Good CI/CD with automated testing and deployment",
            5: "Comprehensive CI/CD with environments and some monitoring",
            6: "Full DevOps with CI/CD, monitoring, and infrastructure-as-code",
        },
    },
    # ==========================================================================
    # Category D: Documentation (20 pts)
    # ==========================================================================
    "D3": {
        "name": "Code Documentation",
        "max_score": 5,
        "description": "How well is the code documented with comments and docstrings?",
        "prompt": """Evaluate the quality and completeness of code documentation.

Review the source code to assess:
1. Are there docstrings or JSDoc comments for functions/classes?
2. Are complex algorithms or business logic explained?
3. Are there inline comments for non-obvious code?
4. Is the documentation consistent and up-to-date?
5. Are public APIs well-documented?

Repository Context:
{context}

Provide your evaluation in the required JSON format.""",
        "rubric": {
            0: "No code documentation",
            1: "Minimal documentation (few comments)",
            2: "Basic comments for some functions",
            3: "Good documentation with docstrings for most public APIs",
            4: "Very good documentation with explanations for complex logic",
            5: "Excellent documentation with comprehensive docstrings and inline comments",
        },
    },
    "D4": {
        "name": "Contributing Guide",
        "max_score": 4,
        "description": "How comprehensive is the contributor experience documentation?",
        "prompt": """Evaluate the contributing guide and contributor experience.

Review CONTRIBUTING.md, README sections, or related docs to assess:
1. Is there a contributing guide?
2. Are development setup instructions provided?
3. Are coding standards and guidelines documented?
4. Is there a code of conduct or PR template?
5. Are issue templates or contribution workflows defined?

Repository Context:
{context}

Provide your evaluation in the required JSON format.""",
        "rubric": {
            0: "No contributing guide",
            1: "Basic contribution instructions",
            2: "Some development setup and contribution guidelines",
            3: "Good contributing guide with standards and setup",
            4: "Comprehensive contributor guide with templates and workflows",
        },
    },
}

# Lists for easy reference
SUBJECTIVE_ITEMS = list(GRADING_PROMPTS.keys())


def get_prompt(item_id: str) -> Dict[str, Any]:
    """Get the grading prompt for a specific BMAD item.

    Args:
        item_id: The BMAD item ID (e.g., "A1", "B2")

    Returns:
        Dictionary containing prompt template, rubric, and metadata

    Raises:
        KeyError: If item_id is not a subjective grading item
    """
    if item_id not in GRADING_PROMPTS:
        raise KeyError(f"No grading prompt found for item {item_id}")
    return GRADING_PROMPTS[item_id]


def format_prompt(item_id: str, context: str) -> str:
    """Format a grading prompt with the given repository context.

    Args:
        item_id: The BMAD item ID
        context: Repository context string to insert into the prompt

    Returns:
        Formatted prompt string ready for LLM consumption
    """
    prompt_template = get_prompt(item_id)["prompt"]
    return prompt_template.replace("{context}", context)


def get_rubric(item_id: str) -> Dict[int, str]:
    """Get the scoring rubric for a specific item.

    Args:
        item_id: The BMAD item ID

    Returns:
        Dictionary mapping score values to rubric descriptions
    """
    return get_prompt(item_id)["rubric"]


def get_max_score(item_id: str) -> int:
    """Get the maximum score for a specific item.

    Args:
        item_id: The BMAD item ID

    Returns:
        Maximum score value for the item
    """
    return get_prompt(item_id)["max_score"]
