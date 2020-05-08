# document_context_menu.py
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

from gi.repository import Gtk, Granite


class DocumentContextMenu(Gtk.Menu):

    def __init__(self, attach_to=None):
        super().__init__()
        self.attach_to_widget(attach_to)

        export_menu = Gtk.MenuItem(action_name='document.export')
        export_menu.add(Granite.AccelLabel.from_action_name('Export...', 'document.export'))

        rename_menu = Gtk.MenuItem(action_name='document.rename')
        rename_menu.add(Granite.AccelLabel.from_action_name('Rename', 'document.rename'))

        archive_menu = Gtk.MenuItem(action_name='document.archive')
        archive_menu.add(Granite.AccelLabel.from_action_name('Archive', 'document.archive'))

        delete_menu = Gtk.MenuItem(action_name='document.delete')
        delete_menu.add(Granite.AccelLabel.from_action_name('Delete', 'document.delete'))

        self.append(export_menu)
        self.append(Gtk.SeparatorMenuItem())
        self.append(rename_menu)
        self.append(Gtk.SeparatorMenuItem())
        self.append(archive_menu)
        self.append(delete_menu)
        self.show_all()
