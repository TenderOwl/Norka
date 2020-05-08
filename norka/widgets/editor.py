# editor.py
#
# MIT License
#
# Copyright (c) 2020 Andrey Maksimov <meamka@ya.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import gi

from norka.models.document import Document
from norka.services.storage import storage

gi.require_version('GtkSource', '3.0')
from gi.repository import Gtk, GtkSource


class Editor(Gtk.ScrolledWindow):
    __gtype_name__ = 'Editor'

    def __init__(self):
        super().__init__()

        self.document = None

        self.buffer = GtkSource.Buffer()
        self.manager = GtkSource.LanguageManager()
        self.buffer.set_language(self.manager.get_language("markdown"))

        self.view = GtkSource.View()
        self.view.set_buffer(self.buffer)
        self.view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.view.set_auto_indent(True)
        self.view.set_smart_home_end(True)
        self.view.set_insert_spaces_instead_of_tabs(True)
        self.view.set_tab_width(4)

        self.add(self.view)

    def create_document(self, title: str = 'Unnamed') -> None:
        """Create new document and put it to storage

        :param title: title of the document. Defaults to 'Unnamed'
        :type title: str
        :return: None
        """
        self.document = Document(title=title)
        self.document._id = storage.add(self.document)

    def load_document(self, doc_id: int) -> None:
        """Load :model:`Document` from storage with given `doc_id`.

        :param doc_id: id of the document to load
        :type doc_id: int
        :return: None
        """
        self.document = storage.get(doc_id)

        self.buffer.set_text(self.document.content)
        self.buffer.end_not_undoable_action()
        self.buffer.set_modified(False)
        self.buffer.place_cursor(self.buffer.get_start_iter())

    def unload_document(self) -> None:
        """Save current document and clear text buffer

        :return: None
        """
        if not self.document:
            return

        self.save_document()
        self.buffer.set_text('')
        self.document = None

    def load_file(self, path: str) -> bool:
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

    def save_document(self) -> bool:
        if not self.document:
            return False

        text = self.buffer.get_text(
            self.buffer.get_start_iter(),
            self.buffer.get_end_iter(),
            True
        )
        if storage.update(self.document._id, {"content": text}):
            self.document.content = text
            return True
