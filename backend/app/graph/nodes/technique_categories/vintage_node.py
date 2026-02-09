from app.graph.nodes.technique_categories.base_category import BaseCategoryNode
from app.techniques.schema import TechniqueCategory


class VintageCategoryNode(BaseCategoryNode):
    category = TechniqueCategory.VINTAGE
    display_name = "Opportunity"
