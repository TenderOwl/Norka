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

from gi.repository import Gtk, Gio, GLib, Gdk
from gi.repository.GdkPixbuf import Pixbuf

from norka.services.logger import Logger
from norka.services.storage import storage
from norka.widgets.document_grid import DocumentGrid
from norka.widgets.editor import Editor
from norka.widgets.header import Header
from norka.widgets.message_dialog import MessageDialog
from norka.widgets.rename_dialog import RenameDialog
from norka.widgets.welcome import Welcome


class NorkaWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'NorkaWindow'

    def __init__(self, settings: Gio.Settings, **kwargs):
        super().__init__(**kwargs)

        self.set_default_icon(Pixbuf. new_from_resource_at_scale(
            '/com/github/tenderowl/norka/icons/com.tenderowl.norka.svg',
            128, 128, True
        ))
        self.settings = settings
        self._configure_timeout_id = None

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

        # Pull the Settings
        self.toggle_spellcheck(self.settings.get_boolean('spellcheck'))
        self.autosave = self.settings.get_boolean('autosave')
        self.set_autoindent(self.settings.get_boolean('autoindent'))
        self.set_tabs_spaces(self.settings.get_boolean('spaces-instead-of-tabs'))
        self.set_indent_width(self.settings.get_int('indent-width'))
        self.set_style_scheme(self.settings.get_string('stylescheme'))

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
                },
                {
                    'name': 'export',
                    'action': self.on_document_export_activated,
                    'accel': '<Control><Shift>s'
                },
                {
                    'name': 'search',
                    'action': self.on_document_search_activated,
                    'accel': '<Control>k'
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
            if self.autosave:
                self.editor.save_document()
            else:
                print('Ask for action!')

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
        self.editor.unload_document(save=self.autosave)
        self.document_grid.reload_items()
        self.header.toggle_document_mode()
        self.header.update_title()
        self.settings.set_int('last-document-id', -1)

    def on_welcome_activated(self, sender: Welcome, index: int) -> None:
        if index == 0:
            self.on_document_create_activated(sender, index)

    def on_document_item_activated(self, sender: Gtk.Widget, path: Gtk.TreePath) -> None:
        """Activate currently selected document in grid and open it in editor.

        :param sender:
        :param path:
        :return:
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

    def on_document_create_activated(self, sender: Gtk.Widget = None, event=None) -> None:
        """Create new document named 'Nameless' :) and activate it in editor.

        :param sender:
        :param event:
        :return:
        """
        self.editor.create_document()
        self.screens.set_visible_child_name('editor-grid')
        self.header.toggle_document_mode()
        self.header.update_title(title=self.editor.document.title)

    def on_document_save_activated(self, sender: Gtk.Widget = None, event=None) -> None:
        """Save opened document to storage.

        :param sender:
        :param event:
        :return:
        """
        self.editor.save_document()

    def on_document_rename_activated(self, sender: Gtk.Widget = None, event=None) -> None:
        """Rename currently selected document.
        Show rename dialog and update document's title
        if user puts new one in the entry.

        :param sender:
        :param event:
        :return:
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

    def on_document_export_activated(self, sender: Gtk.Widget = None, event=None) -> None:
        """Export document from storage to local files or web-services.

        :param sender:
        :param event:
        :return:
        """
        doc = self.document_grid.selected_document or self.editor.document
        if not doc:
            return

        dialog = Gtk.FileChooserDialog(
            "Export document to file",
            self,
            Gtk.FileChooserAction.SAVE,
            (
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
                Gtk.STOCK_SAVE,
                Gtk.ResponseType.ACCEPT,
            ),
            # use_header_bar=1
        )
        dialog.set_current_name(doc.title)

        filter_markdown = Gtk.FileFilter()
        filter_markdown.set_name("Markdown")
        filter_markdown.add_pattern("*.md")
        filter_markdown.add_pattern("*.MD")
        filter_markdown.add_pattern("*.markdown")
        dialog.add_filter(filter_markdown)
        dialog.set_do_overwrite_confirmation(True)

        extensions = ('.md', '.markdown',)

        if dialog.run() == Gtk.ResponseType.ACCEPT:
            file_name = dialog.get_filename()
            ex_ok = False

            for extension in extensions:
                if file_name.lower().endswith(extension):
                    ex_ok = True
                    break
            if not ex_ok and extensions:
                file_name += extensions[0]

            with open(file_name, "w+", encoding="utf-8") as output:
                data = self.editor.get_text()
                output.write(data)
        dialog.destroy()

    def on_document_search_activated(self, sender: Gtk.Widget = None, event=None) -> None:
        """Open search dialog.

        :param sender:
        :param event:
        :return:
        """
        # dialog = SearchDialog()
        # dialog.run()
        # dialog.destroy()
        pass

    def toggle_spellcheck(self, state: bool) -> None:
        self.editor.set_spellcheck(state)

    def set_style_scheme(self, scheme_id: str) -> None:
        self.editor.set_style_scheme(scheme_id)

    def set_autoindent(self, autoindent):
        self.editor.view.set_auto_indent(autoindent)

    def set_tabs_spaces(self, state):
        self.editor.view.set_insert_spaces_instead_of_tabs(state)

    def set_indent_width(self, size):
        self.editor.view.set_indent_width(size)
