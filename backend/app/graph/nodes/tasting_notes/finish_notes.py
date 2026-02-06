from app.graph.nodes.tasting_notes.base import BaseTastingNoteNode
from app.techniques.mappings import TastingNote


class FinishNotesNode(BaseTastingNoteNode):
    category = TastingNote.FINISH
    axis = "user-centricity"
