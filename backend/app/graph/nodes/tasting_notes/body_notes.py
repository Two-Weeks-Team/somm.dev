from app.graph.nodes.tasting_notes.base import BaseTastingNoteNode
from app.techniques.mappings import TastingNote


class BodyNotesNode(BaseTastingNoteNode):
    category = TastingNote.BODY
    axis = "risk-analysis"
