from app.graph.nodes.tasting_notes.base import BaseTastingNoteNode
from app.techniques.mappings import TastingNote


class VintageNotesNode(BaseTastingNoteNode):
    category = TastingNote.VINTAGE
    axis = "opportunity"
