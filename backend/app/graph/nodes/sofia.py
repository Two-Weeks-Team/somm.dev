"""Sofia (Vineyard Scout) node implementation.

Focus: Innovation, emerging tech, growth opportunities.
Color: #DAA520
Style: Curious, forward-looking, growth-focused.
"""

from app.graph.nodes.base import BaseSommelierNode
from app.prompts.sofia import get_sofia_prompt


class SofiaNode(BaseSommelierNode):
    """Sofia - Vineyard Scout focused on innovation and potential.

    Evaluates modern technologies, innovation, and growth opportunities
    with the curiosity of an adventurous vineyard scout.
    """

    name = "sofia"
    role = "Vineyard Scout"

    def get_prompt(self, criteria: str):
        """Return Sofia's evaluation prompt template."""
        return get_sofia_prompt()
