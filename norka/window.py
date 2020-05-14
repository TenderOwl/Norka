# window.py
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

from gi.repository import Gtk, Gio, Granite, GLib, Gdk

from norka.services.logger import Logger
from norka.services.storage import storage
from norka.widgets.message_dialog import MessageDialog
from norka.widgets.document_grid import DocumentGrid
from norka.widgets.editor import Editor
from norka.widgets.header import Header
from norka.widgets.rename_dialog import RenameDialog
from norka.widgets.welcome import Welcome


class NorkaWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'NorkaWindow'

    def __init__(self, settings: Gio.Settings, **kwargs):
        super().__init__(**kwargs)
        self.settings = settings
        self._configure_timeout_id = None

        # self.set_default_size(786, 520)
        self.current_size = (786, 520)
        self.resize(*self.settings.get_value('window-size'))
        self.connect('configure-event', self.on_configure_event)
        self.connect('destroy', self.on_window_delete_event)

        # Init actions
        self.init_actions()

        # Make a header
        self.header = Header()
        self.set_titlebar(self.header)
        self.header.show()

        # Init screens
        self.welcome_grid = Welcome()
        self.welcome_grid.connect('activated', self.on_welcome_activated)

        self.document_grid = DocumentGrid()
        self.document_grid.connect('document-create', self.on_document_create_activated)
        self.document_grid.view.connect('item-activated', self.on_document_item_activated)

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

    def init_actions(self) -> None:
        """Initialize app-wide actions.

        """
        action_items = {
            'document': [
                {
                    'name': 'create',
                    'action': self.on_document_create_activated,
                    'accel': '<Control>n'
                },
                {
                    'name': 'save',
                    'action': self.on_document_save_activated,
                    'accel': '<Control>s'
                },
                {
                    'name': 'close',
                    'action': self.on_document_close_activated,
                    'accel': '<Control>w'
                },
                {
                    'name': 'rename',
                    'action': self.on_document_rename_activated,
                    'accel': 'F2'
                },
                {
                    'name': 'archive',
                    'action': self.on_document_archive_activated,
                    'accel': 'Delete'
                },
                {
                    'name': 'delete',
                    'action': self.on_document_delete_activated,
                    'accel': '<Shift>Delete'
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

    def on_window_delete_event(self, sender: Gtk.Widget = None) -> None:
        """Save opened document before window is closed.

        """
        try:
            self.editor.save_document()

            if not self.is_maximized():
                self.settings.set_value("window-size", GLib.Variant("ai", self.current_size))
                self.settings.set_value("window-position", GLib.Variant("ai", self.current_position))

        except Exception as e:
            Logger.error(e)

    def on_configure_event(self, window, event: Gdk.EventConfigure):
        if self._configure_timeout_id:
            GLib.source_remove(self._configure_timeout_id)

        self.current_size = window.get_size()
        self.current_position = window.get_position()

    def check_documents_count(self) -> None:
        """Check for documents count in storage and switch between screens
        whether there is at least one document or not.

        """
        if storage.count() > 0:
            self.screens.set_visible_child_name('document-grid')

            last_doc_id = self.settings.get_int('last-document-id')
            if last_doc_id and last_doc_id != -1:
                self.screens.set_visible_child_name('editor-grid')
                self.editor.load_document(last_doc_id)
                self.header.toggle_document_mode()
                self.header.update_title(title=self.editor.document.title)
        else:
            self.screens.set_visible_child_name('welcome-grid')

    def on_document_close_activated(self, sender: Gtk.Widget, event=None) -> None:
        """Save and close opened document.

        """
        self.screens.set_visible_child_name('document-grid')
        self.editor.unload_document()
        self.document_grid.reload_items()
        self.header.toggle_document_mode()
        self.header.update_title()
        self.settings.set_int('last-document-id', -1)

    def on_welcome_activated(self, sender: Welcome, index: int):
        if index == 0:
            self.on_document_create_activated(sender, index)

    def on_document_item_activated(self, icon_view, path):
        """Activate currently selected document in grid and open it in editor.

        """
        model_iter = self.document_grid.model.get_iter(path)
        doc_id = self.document_grid.model.get_value(model_iter, 3)
        Logger.debug('Activated Document.Id %s', doc_id)

        editor = self.screens.get_child_by_name('editor-grid')
        editor.load_document(doc_id)
        self.screens.set_visible_child_name('editor-grid')

        self.header.toggle_document_mode()
        self.header.update_title(title=self.document_grid.model.get_value(model_iter, 1))
        self.settings.set_int('last-document-id', doc_id)

    def on_document_create_activated(self, sender: Gtk.Widget = None, event=None):
        """Create new document named 'Unnamed' :) and activate it in editor.

        """
        self.editor.create_document()
        self.screens.set_visible_child_name('editor-grid')
        self.header.toggle_document_mode()

    def on_document_save_activated(self, sender: Gtk.Widget = None, event=None):
        """Save opened document to storage.

        """
        self.editor.save_document()

    def on_document_rename_activated(self, sender: Gtk.Widget = None, event=None) -> None:
        """Rename currently selected document.
        Show rename dialog and update document's title
        if user puts new one in the entry.

        """
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
                Logger.debug(e)
            finally:
                popover.destroy()

    def on_document_archive_activated(self, sender: Gtk.Widget = None, event=None) -> None:
        """Marks document as archived. Recoverable.

        :param sender:
        :param event:
        :return:
        """
        doc = self.document_grid.selected_document
        if doc:
            if storage.update(
                    doc_id=doc._id,
                    data={'archived': True}
            ):
                self.check_documents_count()
                self.document_grid.reload_items()

    def on_document_delete_activated(self, sender: Gtk.Widget = None, event=None) -> None:
        """Permanently remove document from storage. Non-recoverable.

        :param sender:
        :param event:
        :return:
        """
        doc = self.document_grid.selected_document

        prompt = MessageDialog(
            f"Permanently delete “{doc.title}”?",
            "Deleted items are not sent to Archive and not recoverable at all",
            "dialog-warning",
        )

        if doc:
            result = prompt.run()
            prompt.destroy()

            if result == Gtk.ResponseType.APPLY and storage.update(
                    doc_id=doc._id,
                    data={'archived': True}
            ):
                self.document_grid.reload_items()
                self.check_documents_count()
