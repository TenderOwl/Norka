import gi

gi.require_version('GtkSource', '3.0')
from gi.repository import Gtk, GtkSource


class Editor(Gtk.ScrolledWindow):
    __gtype_name__ = 'Editor'

    def __init__(self):
        super().__init__()

        self.buffer = GtkSource.Buffer()
        self.view = GtkSource.View.new_with_buffer(self.buffer)

        self.add(self.view)

    def load_document(self, file_path):
        self.load_file(file_path)

    def unload_document(self):
        self.buffer.set_text('')

    def load_file(self, path):
        self.buffer.begin_not_undoable_action()
        try:
            txt = open(path).read()
        except Exception as e:
            print(e)
            return False
        self.buffer.set_text(txt)
        self.buffer.end_not_undoable_action()

        self.buffer.set_modified(False)
        self.buffer.place_cursor(self.buffer.get_start_iter())
        return True
