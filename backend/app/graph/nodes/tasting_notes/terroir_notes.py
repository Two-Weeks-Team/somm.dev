from app.graph.nodes.tasting_notes.base import BaseTastingNoteNode
from app.techniques.mappings import TastingNote


class TerroirNotesNode(BaseTastingNoteNode):
    category = TastingNote.TERROIR
    axis = "presentation"
