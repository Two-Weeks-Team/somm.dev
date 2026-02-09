from app.graph.nodes.technique_categories.base_category import BaseCategoryNode
from app.techniques.schema import TechniqueCategory


class BalanceCategoryNode(BaseCategoryNode):
    category = TechniqueCategory.BALANCE
    display_name = "Feasibility"
