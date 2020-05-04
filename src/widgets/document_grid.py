# document_grid.py
#
# Copyright 2020 Andrey Maksimov
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE X CONSORTIUM BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the name(s) of the above copyright
# holders shall not be used in advertising or otherwise to promote the sale,
# election-box-aluse or other dealings in this Software without prior written
# authorization.

import os
from gi.repository import Gtk, GObject, Gdk
from gi.repository.GdkPixbuf import Pixbuf

from src.services.storage import storage
from src.widgets.rename_popover import RenamePopover


class DocumentGrid(Gtk.Grid):
    __gtype_name__ = 'DocumentGrid'

    __gsignals__ = {
        'document-create': (GObject.SIGNAL_RUN_FIRST, None, (int,))
    }

    def __init__(self):
        super().__init__()

        self.model = Gtk.ListStore(Pixbuf, str, str, int)

        self.view = Gtk.IconView()
        self.view.set_model(self.model)
        self.view.set_pixbuf_column(0)
        self.view.set_text_column(1)
        self.view.set_item_width(80)
        self.view.set_activate_on_single_click(True)

        self.view.connect('show', self.reload_items)
        self.view.connect('button-press-event', self.key_pressed)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_hexpand(True)
        scrolled.set_vexpand(True)
        scrolled.add(self.view)

        self.add(scrolled)

    def reload_items(self, widget):
        self.model.clear()
        for document in storage.all():
            icon = Gtk.IconTheme.get_default().load_icon('text-x-generic', 64, 0)
            self.model.append([icon, document.title, document.content, document._id])

    def rename_item(self, widget) -> bool:
        print(f'Rename item')
        return True

    def key_pressed(self, widget: Gtk.Widget, event: Gdk.EventButton):
        if event.type == Gdk.EventType.BUTTON_PRESS and \
                event.button == Gdk.BUTTON_SECONDARY:

            path = self.view.get_path_at_pos(event.x, event.y)
            if not path:
                return

            self.view.select_path(path)
            item_title = self.model.get_value(self.model.get_iter(path), 1)
            popover = RenamePopover(widget, item_title)
            popover.show_all()
            popover.popup()
