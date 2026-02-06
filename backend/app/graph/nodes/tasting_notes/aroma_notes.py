from app.graph.nodes.tasting_notes.base import BaseTastingNoteNode
from app.techniques.mappings import TastingNote


class AromaNotesNode(BaseTastingNoteNode):
    category = TastingNote.AROMA
    axis = "problem-analysis"
