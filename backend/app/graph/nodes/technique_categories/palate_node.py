from app.graph.nodes.technique_categories.base_category import BaseCategoryNode
from app.techniques.schema import TechniqueCategory


class PalateCategoryNode(BaseCategoryNode):
    category = TechniqueCategory.PALATE
    display_name = "Innovation"
