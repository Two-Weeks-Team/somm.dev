from app.graph.nodes.technique_categories.base_category import BaseCategoryNode
from app.techniques.schema import TechniqueCategory


class FinishCategoryNode(BaseCategoryNode):
    category = TechniqueCategory.FINISH
    display_name = "User-Centricity"
