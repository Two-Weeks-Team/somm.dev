"""Marcel (Cellar Master) node implementation.

Focus: Repository structure, organization, metrics.
Color: #8B7355
Style: Precise, data-driven, architectural.
"""

from app.graph.nodes.base import BaseSommelierNode
from app.prompts.marcel import get_marcel_prompt


class MarcelNode(BaseSommelierNode):
    """Marcel - Cellar Master focused on architecture and organization.

    Evaluates repository structure, directory hierarchy, and metrics
    with the precision of a master cellar master.
    """

    name = "marcel"
    role = "Cellar Master"

    def get_prompt(self, criteria: str):
        """Return Marcel's evaluation prompt template."""
        return get_marcel_prompt()
