"""Jean-Pierre (Master Sommelier) node implementation.

Focus: Final synthesis, weighted verdict.
Color: #4169E1
Style: Wise, synthesizing, final verdict.
"""

from app.graph.nodes.base import BaseSommelierNode
from app.prompts.jeanpierre import get_jeanpierre_prompt


class JeanPierreNode(BaseSommelierNode):
    """Jean-Pierre - Master Sommelier focused on final synthesis.

    Synthesizes all sommelier evaluations into a final weighted verdict
    with the wisdom of a master sommelier.
    """

    name = "jeanpierre"
    role = "Master Sommelier"

    def get_prompt(self, criteria: str):
        """Return Jean-Pierre's synthesis prompt template."""
        return get_jeanpierre_prompt()
