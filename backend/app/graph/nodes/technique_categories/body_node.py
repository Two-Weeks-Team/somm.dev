from app.graph.nodes.technique_categories.base_category import BaseCategoryNode
from app.techniques.schema import TechniqueCategory


class BodyCategoryNode(BaseCategoryNode):
    category = TechniqueCategory.BODY
    display_name = "Risk Analysis"
