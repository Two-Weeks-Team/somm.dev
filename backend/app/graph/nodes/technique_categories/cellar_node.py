from app.graph.nodes.technique_categories.base_category import BaseCategoryNode
from app.techniques.schema import TechniqueCategory


class CellarCategoryNode(BaseCategoryNode):
    category = TechniqueCategory.CELLAR
    display_name = "Synthesis"
