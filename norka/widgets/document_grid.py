# document_grid.py
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


from gi.repository import Gtk, GObject, Gdk
from gi.repository.GdkPixbuf import Pixbuf

from norka.services.storage import storage
from norka.widgets.document_context_menu import DocumentContextMenu


class DocumentGrid(Gtk.Grid):
    __gtype_name__ = 'DocumentGrid'

    __gsignals__ = {
        'document-create': (GObject.SIGNAL_RUN_FIRST, None, (int,))
    }

    def __init__(self):
        super().__init__()

        self.model = Gtk.ListStore(Pixbuf, str, str, int)

        self.selected_path = None
        self.selected_document = None

        self.view = Gtk.IconView()
        self.view.set_model(self.model)
        self.view.set_pixbuf_column(0)
        self.view.set_text_column(1)
        self.view.set_item_width(80)
        self.view.set_activate_on_single_click(True)
        self.view.set_selection_mode(Gtk.SelectionMode.BROWSE)

        self.view.connect('show', self.reload_items)
        self.view.connect('button-press-event', self.on_button_pressed)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_hexpand(True)
        scrolled.set_vexpand(True)
        scrolled.add(self.view)

        self.add(scrolled)

    def reload_items(self, sender: Gtk.Widget = None):
        self.model.clear()
        for document in storage.all():
            icon = Gtk.IconTheme.get_default().load_icon('text-x-generic', 64, 0)
            self.model.append([icon, document.title, document.content, document._id])

        if self.selected_path:
            self.view.select_path(self.selected_path)

    def on_button_pressed(self, widget: Gtk.Widget, event: Gdk.EventButton):
        self.selected_path = self.view.get_path_at_pos(event.x, event.y)

        if not self.selected_path:
            self.selected_document = None
            return self.view.unselect_all()

        if event.button == Gdk.BUTTON_SECONDARY:
            self.view.select_path(self.selected_path)

            self.selected_document = storage.get(self.model.get_value(
                self.model.get_iter(self.selected_path), 3
            ))

            menu = DocumentContextMenu(self.view)
            menu.popup(None, None, None, None, event.button, event.time)

            return

        self.view.unselect_all()
        self.selected_document = None
