from gi.repository import GObject
from gi.repository.GdkPixbuf import Pixbuf


class GridItem(GObject.GObject):
    __gtype_name_ = 'GridItem'

    icon = GObject.Property(type=GObject.Object)
    title = GObject.Property(type=str)
    content = GObject.Property(type=str)
    document_id = GObject.Property(type=int)
    tooltip = GObject.Property(type=str)

    def __init__(self, icon: Pixbuf, title: str,
                 content: str,
                 document_id: int,
                 tooltip: str = None):
        super().__init__()

        self.icon = icon
        self.title = title
        self.content = content
        self.document_id = document_id
        self.tooltip = tooltip
