"""Heinrich (Quality Inspector) node implementation.

Focus: Testing, security, risk assessment.
Color: #2F4F4F
Style: Rigor, thorough, methodical.
"""

from app.graph.nodes.base import BaseSommelierNode
from app.prompts.heinrich import get_heinrich_prompt


class HeinrichNode(BaseSommelierNode):
    """Heinrich - Quality Inspector focused on testing and security.

    Evaluates test coverage, security vulnerabilities, and risk
    with the rigor of a master quality inspector.
    """

    name = "heinrich"
    role = "Quality Inspector"

    def get_prompt(self, criteria: str):
        """Return Heinrich's evaluation prompt template."""
        return get_heinrich_prompt()
