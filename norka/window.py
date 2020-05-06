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

from gi.repository import Gtk, Gio

from norka.widgets.document_grid import DocumentGrid
from norka.widgets.editor import Editor
from norka.widgets.header import Header
from norka.widgets.welcome import Welcome
from .services.storage import storage


class NorkaWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'NorkaWindow'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_default_size(786, 520)

        self.header = Header()
        self.header.add_button.connect('clicked', self.document_create)
        self.header.back_button.connect('clicked', self.icon_list_activated)
        self.set_titlebar(self.header)
        self.header.show()

        self.welcome_grid = Welcome()
        self.welcome_grid.connect('activated', self.welcome_activated)

        self.document_grid = DocumentGrid()
        self.document_grid.connect('document-create', self.document_create)
        self.document_grid.view.connect('item-activated', self.icon_activated)

        self.editor = Editor()

        self.screens = Gtk.Stack()
        self.screens.set_transition_duration(400)
        self.screens.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)

        self.screens.add_named(self.welcome_grid, 'welcome-grid')
        self.screens.add_named(self.document_grid, 'document-grid')
        self.screens.add_named(self.editor, 'editor-grid')

        self.screens.show_all()

        self.add(self.screens)

        self.init_actions()

        # If here's at least one document in storage
        # then show documents grid
        if storage.count() > 0:
            self.screens.set_visible_child_name('document-grid')

    def init_actions(self):
        items = [{
            'group': '',
            'name': 'create',
            'callback': lambda x: print,
            'accel': '<Control>n'
        }]

        document_actions = Gio.SimpleActionGroup()
        create_document = Gio.SimpleAction(name="create")
        create_document.connect('activate', self.document_create)
        self.get_application().set_accels_for_action('document.create', ('<Control>n',))
        document_actions.add_action(create_document)

        self.insert_action_group('document', document_actions)

        # self.add_action_entries()

    # def make_action(self, name, callback=None, accel=None) -> Gio.SimpleAction:
    #     action = Gio.SimpleAction.new(name, None)
    #     action.connect('activate', callback)
    #     return action

    def on_delete_event(self):
        if self.editor.document:
            try:
                self.editor.save_document()
                print(f'Document "{self.editor.document.title}" saved')
            except Exception as e:
                print(e)
        else:
            print('Nothing to save')

    def icon_list_activated(self, button):
        self.screens.set_visible_child_name('document-grid')
        self.editor.unload_document()
        self.document_grid.reload_items(self)
        self.header.toggle_document_mode()
        self.header.update_title()

    def welcome_activated(self, sender: Welcome, index: int):
        if index == 0:
            self.document_create(sender, index)

    def icon_activated(self, icon_view, path):
        model_iter = self.document_grid.model.get_iter(path)
        doc_id = self.document_grid.model.get_value(model_iter, 3)
        print(f'Activated Document.Id {doc_id}')

        editor = self.screens.get_child_by_name('editor-grid')
        editor.load_document(doc_id)
        self.screens.set_visible_child_name('editor-grid')

        self.header.toggle_document_mode()
        self.header.update_title(title=self.document_grid.model.get_value(model_iter, 1))

    def document_create(self, sender=None, index=None):
        self.editor.create_document()
        self.screens.set_visible_child_name('editor-grid')
        self.header.toggle_document_mode()
