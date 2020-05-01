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
# use or other dealings in this Software without prior written
# authorization.


import os
from gi.repository import Gtk
from gi.repository.GdkPixbuf import Pixbuf


class DocumentGrid(Gtk.Grid):
    __gtype_name__ = 'DocumentGrid'

    def __init__(self):
        super().__init__()

        self.model = Gtk.ListStore(Pixbuf, str, str)

        self.view = Gtk.IconView.new_with_model(self.model)
        self.view.set_pixbuf_column(0)
        self.view.set_text_column(1)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_hexpand(True)
        scrolled.set_vexpand(True)
        scrolled.add(self.view)

        self.add(scrolled)

        for item in os.listdir('.'):
            if os.path.isdir(item):
                icon_name = 'folder'
            else:
                icon_name = 'text-x-generic'

            icon = Gtk.IconTheme.get_default().load_icon(icon_name, 64, 0)
            self.model.append([icon, os.path.basename(item), os.path.abspath(item)])
