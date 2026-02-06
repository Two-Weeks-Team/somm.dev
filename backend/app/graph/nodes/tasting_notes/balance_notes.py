from app.graph.nodes.tasting_notes.base import BaseTastingNoteNode
from app.techniques.mappings import TastingNote


class BalanceNotesNode(BaseTastingNoteNode):
    category = TastingNote.BALANCE
    axis = "feasibility"
