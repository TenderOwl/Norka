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
import os
import time

from gi.repository import Gtk, Gio, GLib, Gdk, Granite
from gi.repository.GdkPixbuf import Pixbuf

from norka.define import FONT_SIZE_MIN, FONT_SIZE_MAX, FONT_SIZE_FAMILY, FONT_SIZE_DEFAULT
from norka.gobject_worker import GObjectWorker
from norka.models.document import Document
from norka.services.export import Exporter
from norka.services.logger import Logger
from norka.services.medium import Medium, PublishStatus
from norka.services.storage import storage
from norka.services.writeas import Writeas
from norka.widgets.document_grid import DocumentGrid
from norka.widgets.editor import Editor
from norka.widgets.export_dialog import ExportFileDialog, ExportFormat
from norka.widgets.header import Header
from norka.widgets.message_dialog import MessageDialog
from norka.widgets.rename_dialog import RenameDialog
from norka.widgets.welcome import Welcome


class NorkaWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'NorkaWindow'

    def __init__(self, settings: Gio.Settings, **kwargs):
        super().__init__(**kwargs)

        self.set_default_icon(Pixbuf.new_from_resource_at_scale(
            '/com/github/tenderowl/norka/icons/com.github.tenderowl.norka.svg',
            128, 128, True
        ))
        self.settings = settings
        self._configure_timeout_id = None

        Granite.widgets_utils_set_color_primary(self,
                                                Gdk.RGBA(red=0.29, green=0.50, blue=0.64, alpha=1.0),
                                                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.current_size = (786, 520)
        self.resize(*self.settings.get_value('window-size'))
        self.connect('configure-event', self.on_configure_event)
        self.connect('destroy', self.on_window_delete_event)

        # Export clients
        self.medium_client = Medium()
        self.writeas_client = Writeas()
        self.uri_to_open = None

        # Make a header
        self.header = Header(self.settings)
        self.set_titlebar(self.header)
        self.header.show()

        # Init screens
        self.welcome_grid = Welcome()
        self.welcome_grid.connect('activated', self.on_welcome_activated)

        self.document_grid = DocumentGrid()
        self.document_grid.connect('document-create', self.on_document_create_activated)
        self.document_grid.connect('document-import', self.on_document_import)
        self.document_grid.view.connect('item-activated', self.on_document_item_activated)

        self.editor = Editor()

        self.screens = Gtk.Stack()
        self.screens.set_transition_duration(400)
        self.screens.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)

        self.screens.add_named(self.welcome_grid, 'welcome-grid')
        self.screens.add_named(self.document_grid, 'document-grid')
        self.screens.add_named(self.editor, 'editor-grid')

        self.screens.show_all()

        self.toast = Granite.WidgetsToast()

        self.overlay = Gtk.Overlay()
        self.overlay.add_overlay(self.screens)
        self.overlay.add_overlay(self.toast)
        self.overlay.show_all()

        self.add(self.overlay)

        # Init actions
        self.init_actions()

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
        self.editor.update_font(self.settings.get_string('font'))

    def init_actions(self) -> None:
        """Initialize app-wide actions.

        """
        action_items = {
            'document': [
                {
                    'name': 'create',
                    'action': self.on_document_create_activated,
                    'accels': ('<Control>n',)
                },
                {
                    'name': 'save',
                    'action': self.on_document_save_activated,
                    'accels': ('<Control>s',)
                },
                {
                    'name': 'close',
                    'action': self.on_document_close_activated,
                    'accels': ('<Control>w',)
                },
                {
                    'name': 'rename',
                    'action': self.on_document_rename_activated,
                    'accels': ('F2',)
                },
                {
                    'name': 'archive',
                    'action': self.on_document_archive_activated,
                    'accels': (None,)
                },
                {
                    'name': 'unarchive',
                    'action': self.on_document_unarchive_activated,
                    'accels': (None,)
                },
                {
                    'name': 'delete',
                    'action': self.on_document_delete_activated,
                    'accels': ('<Shift>Delete',)
                },
                {
                    'name': 'import',
                    'action': self.on_document_import_activated,
                    'accels': ('<Control>o',)
                },
                {
                    'name': 'export',
                    'action': self.on_export_plaintext,
                    'accels': (None,)
                },
                {
                    'name': 'export-markdown',
                    'action': self.on_export_markdown,
                    'accels': ('<Control><Shift>s',)
                },
                {
                    'name': 'export-html',
                    'action': self.on_export_html,
                    'accels': (None,)
                },
                {
                    'name': 'export-medium',
                    'action': self.on_export_medium,
                    'accels': (None,)
                },
                {
                    'name': 'export-writeas',
                    'action': self.on_export_writeas,
                    'accels': (None,)
                },
                {
                    'name': 'search',
                    'action': self.on_document_search_activated,
                    'accels': ('<Control>k',)
                },
                {
                    'name': 'zoom_in',
                    'action': self.on_zoom_in,
                    'accels': ('<Control>equal', '<Control>plus')
                },
                {
                    'name': 'zoom_out',
                    'action': self.on_zoom_out,
                    'accels': ('<Control>minus',)
                },
                {
                    'name': 'zoom_default',
                    'action': self.on_zoom_default,
                    'accels': ('<Control>0',)
                },
                {
                    'name': 'search_text',
                    'action': self.on_text_search_activated,
                    'accels': ('<Control>f',)
                },
                {
                    'name': 'search_text_next',
                    'action': self.on_text_search_forward,
                    'accels': ('<Control>g',)
                },
                {
                    'name': 'search_text_prev',
                    'action': self.on_text_search_backward,
                    'accels': ('<Control><Shift>g',)
                },
                {
                    'name': 'toggle_archived',
                    'action': self.on_toggle_archive,
                    'accels': (None,)
                },
            ]
        }

        for action_group_key, actions in action_items.items():
            action_group = Gio.SimpleActionGroup()

            for item in actions:
                action = Gio.SimpleAction(name=item['name'])
                action.connect('activate', item['action'])
                self.get_application().set_accels_for_action(f'{action_group_key}.{item["name"]}', item["accels"])
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
        # If document already loaded to editor we need to close it before create new one
        if self.editor.document:
            self.on_document_close_activated(sender, event)

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

    def on_document_import_activated(self, sender, event):
        dialog = Gtk.FileChooserNative.new(
            "Import files into Norka",
            self,
            Gtk.FileChooserAction.OPEN
        )

        filter_markdown = Gtk.FileFilter()
        filter_markdown.set_name("Text Files")
        filter_markdown.add_mime_type("text/plain")
        dialog.add_filter(filter_markdown)
        dialog_result = dialog.run()

        if dialog_result == Gtk.ResponseType.ACCEPT:
            file_path = dialog.get_filename()
            self.import_document(file_path)

        dialog.destroy()

    def on_document_import(self, sender: Gtk.Widget = None, file_path: str = None) -> None:
        self.import_document(file_path=file_path)

    def import_document(self, file_path: str) -> bool:
        """Import files from filesystem.
        Creates new document in storage and fill it with file's contents.

        :param sender:
        :param filepath: path to file to import
        """
        if not os.path.exists(file_path):
            return False

        self.header.show_spinner(True)
        try:
            with open(file_path, 'r') as _file:
                lines = _file.readlines()
                filename = os.path.basename(file_path)[:file_path.rfind('.')]

                _doc = Document(title=filename, content='\r\n'.join(lines))
                _doc_id = storage.add(_doc)

                self.document_grid.reload_items()
            return True
        except Exception as e:
            print(e)
            return False
        finally:
            self.header.show_spinner(False)

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
            if storage.update(doc_id=doc._id, data={'archived': True}):
                self.check_documents_count()
                self.document_grid.reload_items()

    def on_document_unarchive_activated(self, sender: Gtk.Widget = None, event=None) -> None:
        """Unarchive document.

        :param sender:
        :param event:
        :return:
        """
        doc = self.document_grid.selected_document
        if doc:
            if storage.update(doc_id=doc._id, data={'archived': False}):
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

            if result == Gtk.ResponseType.APPLY and storage.delete(doc._id):
                self.document_grid.reload_items()
                self.check_documents_count()

    def on_export_plaintext(self, sender: Gtk.Widget = None, event=None) -> None:
        """Export document from storage to local files or web-services.

        :param sender:
        :param event:
        :return:
        """
        doc = self.document_grid.selected_document or self.editor.document
        if not doc:
            return

        dialog = ExportFileDialog(
            "Export document to file",
            self,
            Gtk.FileChooserAction.SAVE
        )
        dialog.set_current_name(doc.title)
        export_format = ExportFormat.PlainText
        dialog.set_format(export_format)
        dialog_result = dialog.run()

        if dialog_result == Gtk.ResponseType.ACCEPT:
            self.header.show_spinner(True)
            basename, ext = os.path.splitext(dialog.get_filename())
            if ext not in export_format[1]:
                ext = export_format[1][0][1:]

            GObjectWorker.call(Exporter.export_plaintext,
                               (basename + ext, doc),
                               callback=self.on_export_callback)

        dialog.destroy()

    def on_export_markdown(self, sender: Gtk.Widget = None, event=None) -> None:
        """Export document from storage to local files or web-services.

        :param sender:
        :param event:
        :return:
        """
        doc = self.document_grid.selected_document or self.editor.document
        if not doc:
            return

        dialog = ExportFileDialog(
            "Export document to file",
            self,
            Gtk.FileChooserAction.SAVE
        )
        dialog.set_current_name(doc.title)
        export_format = ExportFormat.Markdown
        dialog.set_format(export_format)
        dialog_result = dialog.run()

        if dialog_result == Gtk.ResponseType.ACCEPT:
            self.header.show_spinner(True)
            basename, ext = os.path.splitext(dialog.get_filename())
            if ext not in export_format[1]:
                ext = export_format[1][0][1:]

            GObjectWorker.call(Exporter.export_markdown,
                               (basename + ext, doc),
                               callback=self.on_export_callback)

        dialog.destroy()

    def on_export_html(self, sender: Gtk.Widget = None, event=None) -> None:
        """Export document from storage to local files or web-services.

        :param sender:
        :param event:
        :return:
        """
        doc = self.document_grid.selected_document or self.editor.document
        if not doc:
            return

        dialog = ExportFileDialog(
            "Export document to file",
            self,
            Gtk.FileChooserAction.SAVE
        )
        dialog.set_current_name(doc.title)
        export_format = ExportFormat.Html
        dialog.set_format(export_format)
        dialog_result = dialog.run()

        if dialog_result == Gtk.ResponseType.ACCEPT:
            self.header.show_spinner(True)
            basename, ext = os.path.splitext(dialog.get_filename())
            if ext not in export_format[1]:
                ext = export_format[1][0][1:]

            GObjectWorker.call(Exporter.export_html,
                               (basename + ext, doc),
                               callback=self.on_export_callback)

        dialog.destroy()

    def on_export_callback(self, result):
        self.header.show_spinner(False)
        self.disconnect_toast()
        if result:
            self.toast.set_title("Document exported.")
            self.toast.set_default_action("Open folder")
            self.uri_to_open = f"file://{os.path.dirname(result)}"
            self.toast.connect("default-action", self.open_uri)
            self.toast.send_notification()
        else:
            self.toast.set_title("Export goes wrong.")
            self.toast.send_notification()

    def on_export_medium(self, sender: Gtk.Widget = None, event=None) -> None:
        """Configure Medium client and export document asynchronously

        :param sender:
        :param event:
        :return:
        """

        token = self.settings.get_string("medium-personal-token")
        user_id = self.settings.get_string("medium-user-id")

        if not token or not user_id:
            self.toast.set_title("You need to set Medium token in Preferences -> Export")
            self.toast.set_default_action("Configure")
            self.disconnect_toast()
            self.toast.connect("default-action", self.get_application().on_preferences)
            self.toast.send_notification()

        else:
            self.header.show_spinner(True)
            self.medium_client.set_token(token)
            GObjectWorker.call(self.medium_client.create_post,
                               args=(user_id, self.editor.document, PublishStatus.DRAFT),
                               callback=self.on_export_medium_callback)

    def on_export_medium_callback(self, result):

        self.header.show_spinner(False)
        if result:
            self.toast.set_title("Document successfully exported!")
            self.toast.set_default_action("View")
            self.uri_to_open = result["url"]
            self.disconnect_toast()
            self.toast.connect("default-action", self.open_uri)
        else:
            self.toast.set_title("Export failed!")
            self.toast.set_default_action(None)
        self.toast.send_notification()

    def on_export_writeas(self, sender: Gtk.Widget = None, event=None) -> None:
        """Configure Write.as client and export document asynchronously

        :param sender:
        :param event:
        :return:
        """
        token = self.settings.get_string("writeas-access-token")

        if not token:
            self.toast.set_title("You have to login to Write.as in Preferences -> Export")
            self.toast.set_default_action("Configure")
            self.disconnect_toast()
            self.toast.connect("default-action", self.get_application().on_preferences)
            self.toast.send_notification()

        else:
            self.header.show_spinner(True)
            self.writeas_client.set_token(access_token=token)
            GObjectWorker.call(self.writeas_client.create_post,
                               args=(self.editor.document,),
                               callback=self.on_export_writeas_callback)

    def on_export_writeas_callback(self, result):
        self.header.show_spinner(False)
        if result:
            self.toast.set_title("Document successfully exported!")
            self.toast.set_default_action("View")
            self.disconnect_toast()
            self.uri_to_open = f"https://write.as/{result['id']}"
            self.toast.connect("default-action", self.open_uri)
        else:
            self.toast.set_title(f"Export failed.")
            self.toast.set_default_action(None)
        self.toast.send_notification()

    def on_document_search_activated(self, sender: Gtk.Widget = None, event=None) -> None:
        """Open search dialog to find a documents

        :param sender:
        :param event:
        :return:
        """
        # dialog = SearchDialog()
        # dialog.run()
        # dialog.destroy()
        pass

    def on_text_search_activated(self, sender: Gtk.Widget = None, event=None) -> None:
        """Open search dialog to find text in a documents
        """
        self.editor.on_search_text_activated(sender, event)

    def on_text_search_forward(self, sender: Gtk.Widget = None, event=None) -> None:
        if self.screens.get_visible_child_name() == 'editor-grid' \
                and self.editor.search_revealer.get_child_revealed():
            self.editor.search_forward(sender=sender, event=event)

    def on_text_search_backward(self, sender: Gtk.Widget = None, event=None) -> None:
        if self.screens.get_visible_child_name() == 'editor-grid' \
                and self.editor.search_revealer.get_child_revealed():
            self.editor.search_backward(sender=sender, event=event)

    def on_zoom_in(self, sender, event) -> None:
        self.zooming(Gdk.ScrollDirection.UP)

    def on_zoom_out(self, sender, event) -> None:
        self.zooming(Gdk.ScrollDirection.DOWN)

    def on_zoom_default(self, sender, event) -> None:
        self.settings.set_int('zoom', 100)
        self.settings.set_string("font", f'{FONT_SIZE_FAMILY} {FONT_SIZE_DEFAULT}')

    def toggle_spellcheck(self, state: bool) -> None:
        self.editor.set_spellcheck(state)

    def set_style_scheme(self, scheme_id: str) -> None:
        self.editor.set_style_scheme(scheme_id)

    def set_autoindent(self, autoindent: bool) -> None:
        self.editor.view.set_auto_indent(autoindent)

    def set_tabs_spaces(self, state: bool) -> None:
        self.editor.view.set_insert_spaces_instead_of_tabs(state)

    def set_indent_width(self, size: int) -> None:
        self.editor.view.set_tab_width(size)

    def zooming(self, direction: Gdk.ScrollDirection) -> None:

        font = self.get_current_font()
        zoom = self.settings.get_int('zoom')

        if direction == Gdk.ScrollDirection.UP:
            zoom += 10
        elif direction == Gdk.ScrollDirection.DOWN:
            zoom -= 10

        font_size = int(FONT_SIZE_DEFAULT * zoom / 100)
        if font_size < FONT_SIZE_MIN or font_size > FONT_SIZE_MAX:
            return

        self.settings.set_string('font', f'{font} {font_size}')
        self.settings.set_int('zoom', zoom)

    def get_current_font(self) -> str:
        font = self.settings.get_string("font")
        return font[:font.rfind(" ")]

    def get_current_font_size(self) -> float:
        font = self.settings.get_string("font")
        return float(font[font.rfind(" ") + 1:])

    def on_toggle_archive(self, action: Gio.SimpleAction, name: str = None):
        self.document_grid.show_archived = self.header.archived_button.get_active()
        self.document_grid.reload_items()

    def open_uri(self, event):
        if self.uri_to_open:
            Gtk.show_uri_on_window(None, self.uri_to_open, Gdk.CURRENT_TIME)
            self.uri_to_open = None

    def disconnect_toast(self):
        try:
            self.toast.disconnect_by_func(self.get_application().on_preferences)
        except:
            pass

        try:
            self.toast.disconnect_by_func(self.open_uri)
        except:
            pass
