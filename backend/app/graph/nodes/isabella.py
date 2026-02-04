"""Isabella (Wine Critic) node implementation.

Focus: Code quality, aesthetics, developer experience.
Color: #C41E3A
Style: Poetic, aesthetic-focused, craft appreciation.
"""

from app.graph.nodes.base import BaseSommelierNode
from app.prompts.isabella import get_isabella_prompt


class IsabellaNode(BaseSommelierNode):
    """Isabella - Wine Critic focused on aesthetics and DX.

    Evaluates code readability, elegance, and developer experience
    with the eye of a renowned wine critic.
    """

    name = "isabella"
    role = "Wine Critic"

    def get_prompt(self, criteria: str):
        """Return Isabella's evaluation prompt template."""
        return get_isabella_prompt()
