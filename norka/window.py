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

from gi.repository import Gtk, Gio, Granite

from norka.widgets.document_grid import DocumentGrid
from norka.widgets.editor import Editor
from norka.widgets.header import Header
from norka.widgets.welcome import Welcome
from norka.services.storage import storage
from norka.widgets.rename_dialog import RenameDialog


class NorkaWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'NorkaWindow'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_default_size(786, 520)

        self.init_actions()

        self.header = Header()
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

        # If here's at least one document in storage
        # then show documents grid
        self.check_documents_count()

    def init_actions(self):
        action_items = {
            'document': [
                {
                    'name': 'create',
                    'action': self.document_create,
                    'accel': '<Control>n'
                },
                {
                    'name': 'close',
                    'action': self.document_close_activated,
                    'accel': '<Control>w'
                },
                {
                    'name': 'rename',
                    'action': self.rename_activated,
                    'accel': 'F2'
                },
                {
                    'name': 'archive',
                    'action': self.archive_activated,
                    'accel': None
                },
                {
                    'name': 'delete',
                    'action': self.delete_activated,
                    'accel': None
                }
            ]
        }

        for action_group_key, actions in action_items.items():
            action_group = Gio.SimpleActionGroup()

            for item in actions:
                action = Gio.SimpleAction(name=item['name'])
                action.connect('activate', item['action'])
                self.get_application().set_accels_for_action(f'{action_group_key}.{item["name"]}', (item["accel"],))
                action_group.add_action(action)

            self.insert_action_group(action_group_key, action_group)

    def on_window_delete_event(self):
        if self.editor.document:
            try:
                self.editor.save_document()
                print(f'Document "{self.editor.document.title}" saved')
            except Exception as e:
                print(e)
        else:
            print('Nothing to save')

    def check_documents_count(self):
        if storage.count() > 0:
            self.screens.set_visible_child_name('document-grid')
        else:
            self.screens.set_visible_child_name('welcome-grid')

    def document_close_activated(self, sender: Gtk.Widget, event=None) -> None:
        self.screens.set_visible_child_name('document-grid')
        self.editor.unload_document()
        self.document_grid.reload_items()
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

    def document_create(self, sender: Gtk.Widget = None, index=None):
        self.editor.create_document()
        self.screens.set_visible_child_name('editor-grid')
        self.header.toggle_document_mode()

    def rename_activated(self, sender: Gtk.Widget = None, event=None) -> None:
        print(f'rename_activated')
        doc = self.document_grid.selected_document
        if doc:
            popover = RenameDialog(doc.title)
            response = popover.run()
            try:
                if response == Gtk.ResponseType.APPLY:
                    new_title = popover.entry.get_text()

                    if storage.update(doc_id=doc._id, data={'title': new_title}):
                        self.document_grid.reload_items()
            except Exception as e:
                print(e)
            finally:
                popover.destroy()

    def archive_activated(self, sender: Gtk.Widget = None, event=None) -> None:
        doc = self.document_grid.selected_document
        if doc:
            if storage.update(
                    doc_id=doc._id,
                    data={'archived': True}
            ):
                self.check_documents_count()
                self.document_grid.reload_items()

    def delete_activated(self, sender: Gtk.Widget = None, event=None) -> None:
        doc = self.document_grid.selected_document

        prompt = Granite.MessageDialog.with_image_from_icon_name(
            f"Permanently delete “{doc.title}”?",
            "Deleted items are not sent to Archive and are not recoverable",
            "dialog-warning",
            Gtk.ButtonsType.OK
        )
        if doc:
            prompt.run()

        if doc and storage.update(
                doc_id=doc._id,
                data={'archived': True}
        ):
            self.document_grid.reload_items()
            self.check_documents_count()
