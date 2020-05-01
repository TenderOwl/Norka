# window.py
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

from gi.repository import Gtk, Granite, GLib, Gio

from src.widgets.document_grid import DocumentGrid
from src.widgets.document_room import DocumentRoom
from src.widgets.editor import Editor
from src.widgets.header import Header


class NorkaWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'NorkaWindow'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_default_size(830, 520)

        self.header = Header()
        self.header.back_button.connect('clicked', self.icon_list_activated)
        self.set_titlebar(self.header)
        self.header.show()

        self.documents_room = DocumentRoom()
        self.documents_room.connect('document-create', self.document_create)

        self.screens = Gtk.Stack()
        self.screens.set_transition_duration(400)
        self.screens.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.screens.add_named(self.documents_room, 'document_room')
        self.screens.add_named(Editor(), 'editor')
        self.screens.show_all()

        # self.document_grid.view.connect('item-activated', self.icon_activated)

        self.add(self.screens)

    # def init_actions(self):
    #     items = [{
    #         'name': 'document.create', 'callback': lambda x: print, 'accel': '<Control>n'
    #     }]
    #
    #     for item in items:
    #         action = self.make_action(**item)
    #         self.add_action(action)
    #
    # def make_action(self, name, callback=None, accel=None) -> Gio.SimpleAction:
    #     action = Gio.SimpleAction.new(name, None)
    #     action.connect('activate', callback)
    #     return action
    #
    def icon_list_activated(self, button):
        self.screens.set_visible_child_name('document_room')
        self.header.toggle_document_mode()
    #
    # def icon_activated(self, icon_view, path):
    #     model_iter = self.document_grid.model.get_iter(path)
    #     filepath = self.document_grid.model.get_value(model_iter, 2)
    #     print(filepath)
    #
    #     editor = self.screens.get_child_by_name('editor')
    #     editor.load_document(file_path=filepath)
    #     self.screens.set_visible_child_name('editor')
    #
    #     self.header.toggle_document_mode()

    def document_create(self, sender, index):
        self.screens.set_visible_child_name('editor')
        self.header.toggle_document_mode()
