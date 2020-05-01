from gi.repository import Gtk, Granite, GObject

from src.widgets.document_grid import DocumentGrid


class DocumentRoom(Gtk.Stack):
    __gtype_name__ = 'DocumentRoom'

    __gsignals__ = {
        'document-create': (GObject.SIGNAL_RUN_FIRST, None, (int,))
    }

    def __init__(self):
        super().__init__()

        self.welcome_grid = Granite.WidgetsWelcome()
        self.welcome_grid.set_title('No documents yet')
        self.welcome_grid.set_subtitle('Create one and start writing')
        self.welcome_grid.append('document-new', 'New document', 'Create empty document')
        self.document_grid = DocumentGrid()

        self.welcome_grid.connect('activated', self.welcome_activated)

        self.add_named(self.welcome_grid, 'welcome-grid')
        self.add_named(self.document_grid, 'document-grid')

    def welcome_activated(self, sender, index):
        print('Activated index', index)
        if index == 0:
            self.emit('document-create', 0)
            self.set_visible_child_name('document-grid')
