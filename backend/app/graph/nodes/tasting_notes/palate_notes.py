from app.graph.nodes.tasting_notes.base import BaseTastingNoteNode
from app.techniques.mappings import TastingNote


class PalateNotesNode(BaseTastingNoteNode):
    category = TastingNote.PALATE
    axis = "innovation"
