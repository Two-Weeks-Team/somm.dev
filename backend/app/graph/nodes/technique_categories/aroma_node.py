from app.graph.nodes.technique_categories.base_category import BaseCategoryNode
from app.techniques.schema import TechniqueCategory


class AromaCategoryNode(BaseCategoryNode):
    category = TechniqueCategory.AROMA
    display_name = "Problem Analysis"
