from app.graph.nodes.technique_categories.base_category import BaseCategoryNode
from app.techniques.schema import TechniqueCategory


class TerroirCategoryNode(BaseCategoryNode):
    category = TechniqueCategory.TERROIR
    display_name = "Presentation"
