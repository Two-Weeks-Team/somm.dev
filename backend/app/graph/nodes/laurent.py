"""Laurent (Winemaker) node implementation.

Focus: Implementation details, code craftsmanship.
Color: #228B22
Style: Pragmatic, detail-oriented, implementation.
"""

from app.graph.nodes.base import BaseSommelierNode
from app.prompts.laurent import get_laurent_prompt


class LaurentNode(BaseSommelierNode):
    """Laurent - Winemaker focused on implementation quality.

    Evaluates algorithms, code craftsmanship, and implementation details
    with the pragmatism of a master winemaker.
    """

    name = "laurent"
    role = "Winemaker"

    def get_prompt(self, criteria: str):
        """Return Laurent's evaluation prompt template."""
        return get_laurent_prompt()
