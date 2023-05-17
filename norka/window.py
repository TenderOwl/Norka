# window.py
#
# MIT License
#
# Copyright (c) 2020-2022 Andrey Maksimov <meamka@ya.ru>
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
from gettext import gettext as _

from gi.repository import Gtk, Gio, GLib, Gdk, Adw
from gi.repository.GdkPixbuf import Pixbuf

from norka.define import FONT_SIZE_MIN, FONT_SIZE_MAX, FONT_SIZE_FAMILY, FONT_SIZE_DEFAULT, RESOURCE_PREFIX
from norka.gobject_worker import GObjectWorker
from norka.models.document import Document
from norka.services import distro
from norka.services.backup import BackupService
from norka.services.export import Exporter, PDFExporter, Printer
from norka.services.logger import Logger
from norka.services.medium import Medium, PublishStatus
from norka.services.storage import Storage
from norka.services.writeas import Writeas
from norka.widgets.document_grid import DocumentGrid
from norka.widgets.editor import Editor
from norka.widgets.export_dialog import ExportFileDialog, ExportFormat
from norka.widgets.extended_stats_dialog import ExtendedStatsDialog
from norka.widgets.header import NorkaHeader
from norka.widgets.message_dialog import MessageDialog
from norka.widgets.preview import Preview
from norka.widgets.quick_find_dialog import QuickFindDialog
from norka.widgets.rename_popover import RenamePopover
from norka.widgets.welcome import Welcome


@Gtk.Template(resource_path=(f"{RESOURCE_PREFIX}/ui/window.ui"))
class NorkaWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'NorkaWindow'

    content_box: Gtk.Box = Gtk.Template.Child()
    header: NorkaHeader = Gtk.Template.Child()
    overlay: Adw.ToastOverlay = Gtk.Template.Child()
    screens: Gtk.Stack = Gtk.Template.Child()

    def __init__(self, settings: Gio.Settings, storage: Storage, **kwargs):
        super().__init__(**kwargs)

        self.set_icon_name('com.github.tenderowl.norka.svg')
        self.settings = settings
        self.storage = storage
        self.preview = None
        self.extended_stats_dialog = None

        self.set_default_size(*self.settings.get_value('window-size'))

        # Export clients
        self.medium_client = Medium()
        self.writeas_client = Writeas()
        self.uri_to_open = None
        
        # Init screens
        self.welcome_grid = Welcome()
        # self.welcome_grid.connect('activated', self.on_welcome_activated)
        self.welcome_grid.connect('document-import', self.on_document_import)

        self.document_grid = DocumentGrid(self.settings, storage=self.storage)
        self.document_grid.connect('path-changed', self.on_path_changed)
        self.document_grid.connect('document-create', self.on_document_create_activated)
        self.document_grid.connect('document-import', self.on_document_import)
        self.document_grid.connect('rename-folder', self.on_folder_rename_activated)
        self.document_grid.view.connect('item-activated', self.on_document_item_activated)

        self.editor = Editor(self.storage, self.settings)
        self.editor.connect('update-document-stats', self.update_document_stats)

        self.screens.add_named(self.welcome_grid, 'welcome-grid')
        self.screens.add_named(self.document_grid, 'document-grid')
        self.screens.add_named(self.editor, 'editor-grid')

        self.toast = Adw.Toast()

        # Init actions
        self.init_actions()

        # If here's at least one document in storage
        # then show documents grid
        self.check_grid_items()

        # Pull the Settings
        self.toggle_spellcheck(self.settings.get_boolean('spellcheck'))
        self.autosave = self.settings.get_boolean('autosave')
        self.set_autoindent(self.settings.get_boolean('autoindent'))
        self.set_tabs_spaces(self.settings.get_boolean('spaces-instead-of-tabs'))
        self.set_indent_width(self.settings.get_int('indent-width'))
        self.set_style_scheme(self.settings.get_string('stylescheme'))
        self.editor.update_font(self.settings.get_string('font'))

    @property
    def is_document_editing(self) -> bool:
        """Returns if Norka is on editor screen or not
        """
        return self.screens.get_visible_child_name() == 'editor-grid'

    def init_actions(self) -> None:
        """Initialize app-wide actions.

        """
        action_items = {
            'folder': [
                {
                    'name': 'create',
                    'action': self.on_folder_create,
                    'accels': ('<Control><Shift>n',)
                },
            ],
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
                    'action': self.on_document_rename,
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
                    'name': 'export-pdf',
                    'action': self.on_export_pdf,
                    'accels': (None,)
                },
                {
                    'name': 'export-docx',
                    'action': self.on_export_docx,
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
                    'name': 'backup',
                    'action': self.on_backup,
                    'accels': (None,)
                },
                {
                    'name': 'preview',
                    'action': self.on_preview,
                    'accels': ('<Control><Shift>p',)
                },
                {
                    'name': 'print',
                    'action': self.on_print,
                    'accels': ('<Control>p',)
                },
                # {
                #     'name': 'search',
                #     'action': self.search_activated,
                #     'accels': ('<Control>k',)
                # },
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
                    'action': self.search_activated,
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
                {
                    'name': 'show_extended_stats',
                    'action': self.on_show_extended_stats,
                    'accels': (None,)
                },
            ]
        }

        for action_group_key, actions in action_items.items():
            action_group = Gio.SimpleActionGroup()

            for item in actions:
                action = Gio.SimpleAction(name=item['name'])
                action.connect('activate', item['action'])
                self.get_application().set_accels_for_action(
                    f'{action_group_key}.{item["name"]}', item["accels"])
                action_group.add_action(action)

            self.insert_action_group(action_group_key, action_group)

    def do_close_request(self) -> None:
        """Save opened document before window is closed.

        """
        try:
            if self.autosave:
                self.editor.save_document()
            else:
                print('Ask for action!')

            if not self.is_maximized():
                self.settings.set_value("window-size",
                                        GLib.Variant("ai", self.get_default_size()))

        except Exception as e:
            Logger.error(e)

    def check_grid_items(self) -> None:
        """Check for documents count in storage and switch between screens
        whether there is at least one document or not.

        """
        if self.storage.count_all(path=self.document_grid.current_folder_path) > 0 \
                or self.document_grid.current_folder_path != '/':
            self.toggle_welcome(False)
            # self.screens.set_visible_child_name('document-grid')

            last_doc_id = self.settings.get_int('last-document-id')
            if last_doc_id and last_doc_id != -1:
                self.screens.set_visible_child_name('editor-grid')
                self.editor.load_document(last_doc_id)
                self.header.toggle_document_mode()
                self.header.update_title(title=self.editor.document.title)
        else:
            self.toggle_welcome(True)

    def toggle_welcome(self, state=True):
        if state:
            self.screens.set_visible_child_name('welcome-grid')
        else:
            self.screens.set_visible_child_name('document-grid')

    def on_document_close_activated(self,
                                    sender: Gtk.Widget,
                                    event=None) -> None:
        """Save and close opened document.

        """

        # Should work only in editor mode.
        if self.screens.get_visible_child_name() == 'editor-grid':
            self.screens.set_visible_child_name('document-grid')
            self.editor.unload_document(save=self.autosave)
            if self.extended_stats_dialog:
                self.extended_stats_dialog.close()
                self.extended_stats_dialog = None

            self.document_grid.reload_items(
                path=self.document_grid.current_folder_path)
            self.header.toggle_document_mode()
            self.header.update_title()
            self.settings.set_int('last-document-id', -1)

            self.check_grid_items()

    def on_document_item_activated(self, sender: Gtk.Widget, path: Gtk.TreePath) -> None:
        """Activate currently selected document in grid and open it in editor.

        :param sender:
        :param path:
        :return:
        """

        folder = self.document_grid.selected_folder
        if folder:
            self.folder_activate(folder.absolute_path)
            Logger.debug(f'Activated Folder {folder.absolute_path}')

        else:
            doc_id = self.document_grid.selected_document_id
            Logger.debug(f'Activated Document.Id {doc_id}')
            self.document_activate(doc_id)

    def folder_activate(self, folder_path: str) -> None:
        if folder_path.endswith('..'):
            folder_path = folder_path[:-3]
        self.document_grid.reload_items(path=folder_path)

    def document_activate(self, doc_id):
        Logger.info(f'Document {doc_id} activated')
        editor = self.screens.get_child_by_name('editor-grid')
        editor.load_document(doc_id)
        editor.connect('update-document-stats', self.update_document_stats)
        self.screens.set_visible_child_name('editor-grid')
        self.header.toggle_document_mode()
        self.header.update_title(title=editor.document.title)
        self.settings.set_int('last-document-id', doc_id)

    def on_path_changed(self, grid: DocumentGrid, old_path: str, new_path: str) -> None:
        self.header.update_path_label(new_path)

    def on_folder_create(self, sender: Gtk.Widget = None, event=None) -> None:
        popover = RenamePopover(self.header.add_folder_button,
                                '',
                                label_title=_('Name folder with:'))
        popover.rename_button.set_label(_('Create'))
        popover.connect('activate', self.on_folder_create_activated)
        popover.popup()

    def on_folder_rename(self, sender: Gtk.Widget = None, event=None) -> None:
        popover = RenamePopover(self.header.add_folder_button, '')
        popover.connect('activate', self.on_folder_rename_activated)
        popover.popup()

    def on_document_create_activated(self,
                                     sender: Gtk.Widget = None,
                                     event=None,
                                     title: str = None) -> None:
        """Create new document named 'Nameless' :) and activate it in editor.

        :param sender:
        :param event:
        :return:
        """
        # If document already loaded to editor we need to close it before create new one
        if self.editor.document:
            self.on_document_close_activated(sender, event)

        self.editor.create_document(
            title=title, folder_path=self.document_grid.current_folder_path)
        self.screens.set_visible_child_name('editor-grid')
        self.header.toggle_document_mode()
        self.header.update_title(title=self.editor.document.title)

    def on_document_save_activated(self,
                                   sender: Gtk.Widget = None,
                                   event=None) -> None:
        """Save opened document to storage.

        :param sender:
        :param event:
        :return:
        """
        self.editor.save_document()

    def on_document_import_activated(self, sender, event):
        dialog = Gtk.FileChooserNative.new(_("Import files into Norka"), self,
                                           Gtk.FileChooserAction.OPEN)

        filter_markdown = Gtk.FileFilter()
        filter_markdown.set_name(_("Text Files"))
        filter_markdown.add_mime_type("text/plain")
        dialog.add_filter(filter_markdown)
        dialog_result = dialog.run()

        if dialog_result == Gtk.ResponseType.ACCEPT:
            file_path = dialog.get_filename()
            self.import_document(file_path)

        dialog.destroy()

    def on_document_import(self,
                           sender: Gtk.Widget = None,
                           file_path: str = None) -> None:
        if self.import_document(file_path=file_path):
            self.check_grid_items()

    def import_document(self, file_path: str) -> bool:
        """Import files from filesystem.
        Creates new document in storage and fill it with file's contents.

        :param file_path: path to file to import
        """
        if not os.path.exists(file_path):
            return False

        self.header.show_spinner(True)
        try:
            with open(file_path, 'r') as _file:
                lines = _file.readlines()
                filename = os.path.basename(file_path)[:file_path.rfind('.')]

                _doc = Document(title=filename,
                                content=''.join(lines),
                                folder=self.document_grid.current_folder_path)
                _doc_id = self.storage.add(_doc)

                self.document_grid.reload_items()
            return True
        except Exception as e:
            print(e)
            return False
        finally:
            self.check_grid_items()
            self.header.show_spinner(False)

    def on_folder_create_activated(self, sender: Gtk.Widget, title: str):
        sender.destroy()

        self.storage.add_folder(title,
                                path=self.document_grid.current_folder_path)
        self.document_grid.reload_items(
            path=self.document_grid.current_folder_path)
        self.check_grid_items()

    def on_folder_rename_activated(self, sender: Gtk.Widget, title: str):
        sender.destroy()

        folder = self.document_grid.selected_folder
        if folder and self.storage.rename_folder(folder, title):
            self.document_grid.reload_items(
                path=self.document_grid.current_folder_path)

    def on_document_rename(self,
                           sender: Gtk.Widget = None,
                           event=None) -> None:
        """Renames selected document.
        Show rename dialog and update document title if a user puts a new one in the entry.

        :param sender:
        :param event:
        :return:
        """
        if self.document_grid.is_folder_selected:
            item = self.document_grid.selected_folder
        else:
            item = self.document_grid.selected_document
        if not item:
            return

        found, rect = self.document_grid.view.get_cell_rect(
            self.document_grid.selected_path)
        popover = RenamePopover(self.overlay, item.title)
        popover.set_pointing_to(rect)
        if self.document_grid.is_folder_selected:
            popover.connect('activate', self.on_folder_rename_activated)
        else:
            popover.connect('activate', self.on_document_rename_activated)
        popover.popup()

    def on_document_rename_activated(self, sender: Gtk.Widget, title: str):
        sender.destroy()

        doc_id = self.document_grid.selected_document_id
        if not doc_id:
            return

        if self.storage.update(doc_id=doc_id, data={'title': title}):
            self.document_grid.reload_items()

    def on_document_archive_activated(self,
                                      sender: Gtk.Widget = None,
                                      event=None) -> None:
        """Marks document as archived. Recoverable.

        :param sender:
        :param event:
        :return:
        """
        doc_id = self.document_grid.selected_document_id
        if doc_id:
            if self.storage.update(doc_id=doc_id, data={'archived': True}):
                self.check_grid_items()
                self.document_grid.reload_items()

    def on_document_unarchive_activated(self,
                                        sender: Gtk.Widget = None,
                                        event=None) -> None:
        """Unarchive document.

        :param sender:
        :param event:
        :return:
        """
        doc_id = self.document_grid.selected_document_id
        if doc_id:
            if self.storage.update(doc_id=doc_id, data={'archived': False}):
                self.check_grid_items()
                self.document_grid.reload_items()

    def on_document_delete_activated(self,
                                     sender: Gtk.Widget = None,
                                     event=None) -> None:
        """Permanently remove document from storage. Non-recoverable.

        :param sender:
        :param event:
        :return:
        """
        if self.document_grid.is_folder_selected:
            item = self.document_grid.selected_folder
        else:
            item = self.document_grid.selected_document

        if item:
            prompt = MessageDialog(
                f"Permanently delete “{item.title}”?",
                "Deleted items are not sent to Archive and not recoverable at all",
                "dialog-warning",
            )

            result = prompt.run()
            prompt.destroy()

            if result == Gtk.ResponseType.APPLY:
                if self.document_grid.is_folder_selected:
                    self.storage.delete_folder(item)
                else:
                    self.storage.delete(item.document_id)
                self.document_grid.reload_items()
                self.check_grid_items()

    def on_export_plaintext(self,
                            sender: Gtk.Widget = None,
                            event=None) -> None:
        """Export document from storage to local files or web-services.

        :param sender:
        :param event:
        :return:
        """
        doc = self.document_grid.selected_document or self.editor.document
        if not doc:
            return

        dialog = ExportFileDialog("Export document to file", self,
                                  Gtk.FileChooserAction.SAVE)
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

    def on_export_markdown(self,
                           sender: Gtk.Widget = None,
                           event=None) -> None:
        """Export document from storage to local files or web-services.

        :param sender:
        :param event:
        :return:
        """
        doc = self.document_grid.selected_document or self.editor.document
        if not doc:
            return

        dialog = ExportFileDialog("Export document to file", self,
                                  Gtk.FileChooserAction.SAVE)
        dialog.set_current_name(doc.title)
        export_format = ExportFormat.Markdown
        dialog.set_format(export_format)
        dialog_result = dialog.run()

        if dialog_result == Gtk.ResponseType.ACCEPT:
            self.header.show_spinner(True)
            basename, ext = os.path.splitext(dialog.get_filename())
            if ext not in export_format[1]:
                ext = export_format[1][0][1:]

            GObjectWorker.call(Exporter.export_markdown, (basename + ext, doc),
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

        dialog = ExportFileDialog(_("Export document to file"), self,
                                  Gtk.FileChooserAction.SAVE)
        dialog.set_current_name(doc.title)
        export_format = ExportFormat.Html
        dialog.set_format(export_format)
        dialog_result = dialog.run()

        if dialog_result == Gtk.ResponseType.ACCEPT:
            self.header.show_spinner(True)
            basename, ext = os.path.splitext(dialog.get_filename())
            if ext not in export_format[1]:
                ext = export_format[1][0][1:]

            GObjectWorker.call(Exporter.export_html, (basename + ext, doc),
                               callback=self.on_export_callback)

        dialog.destroy()

    def on_export_docx(self, sender: Gtk.Widget = None, event=None) -> None:
        """Export document from storage to local files or web-services.

        :param sender:
        :param event:
        :return:
        """
        doc = self.document_grid.selected_document or self.editor.document
        if not doc:
            return

        dialog = ExportFileDialog(_("Export document to file"), self,
                                  Gtk.FileChooserAction.SAVE)
        dialog.set_current_name(doc.title)
        export_format = ExportFormat.Docx
        dialog.set_format(export_format)
        dialog_result = dialog.run()

        if dialog_result == Gtk.ResponseType.ACCEPT:
            self.header.show_spinner(True)
            basename, ext = os.path.splitext(dialog.get_filename())
            if ext not in export_format[1]:
                ext = export_format[1][0][1:]

            GObjectWorker.call(Exporter.export_docx, (basename + ext, doc),
                               callback=self.on_export_callback)

        dialog.destroy()

    def on_export_pdf(self, sender: Gtk.Widget = None, event=None) -> None:
        """Export document from storage to local files or web-services.

        :param sender:
        :param event:
        :return:
        """
        doc = self.document_grid.selected_document or self.editor.document
        if not doc:
            return

        dialog = ExportFileDialog(_("Export document to file"), self,
                                  Gtk.FileChooserAction.SAVE)
        dialog.set_current_name(doc.title)
        export_format = ExportFormat.Pdf
        dialog.set_format(export_format)
        dialog_result = dialog.run()

        if dialog_result == Gtk.ResponseType.ACCEPT:
            self.header.show_spinner(True)
            basename, ext = os.path.splitext(dialog.get_filename())
            if ext not in export_format[1]:
                ext = export_format[1][0][1:]

            pdf_exporter = PDFExporter(basename + ext, doc)
            pdf_exporter.connect('finished',
                                 lambda x, path: self.on_export_callback(path))
            pdf_exporter.print()

        dialog.destroy()

    def on_export_callback(self, result):
        self.header.show_spinner(False)
        self.disconnect_toast()
        if result:
            self.toast.set_title(_("Document exported."))
            self.toast.set_default_action(_("Open folder"))
            self.uri_to_open = f"file://{os.path.dirname(result)}"
            self.toast.connect("default-action", self.open_uri)
            self.toast.send_notification()
        else:
            self.toast.set_title(_("Export goes wrong."))
            self.toast.send_notification()

    def on_export_medium(self, sender: Gtk.Widget = None, event=None) -> None:
        """Configure Medium client and export document asynchronously

        :param sender:
        :param event:
        :return:
        """

        doc = self.document_grid.selected_document or self.editor.document
        if not doc:
            return

        token = self.settings.get_string("medium-personal-token")
        user_id = self.settings.get_string("medium-user-id")

        if not token or not user_id:
            self.toast.set_title(
                _("You need to set Medium token in Preferences -> Export"))
            self.toast.set_default_action(_("Configure"))
            self.disconnect_toast()
            self.toast.connect("default-action",
                               self.get_application().on_preferences)
            self.toast.send_notification()

        else:
            self.header.show_spinner(True)
            self.medium_client.set_token(token)
            GObjectWorker.call(self.medium_client.create_post,
                               args=(user_id, doc, PublishStatus.DRAFT),
                               callback=self.on_export_medium_callback)

    def on_export_medium_callback(self, result):

        self.header.show_spinner(False)
        if result:
            self.toast.set_title(_("Document successfully exported!"))
            self.toast.set_default_action(_("View"))
            self.uri_to_open = result["url"]
            self.disconnect_toast()
            self.toast.connect("default-action", self.open_uri)
        else:
            self.toast.set_title(_("Export failed!"))
            self.toast.set_default_action(None)
        self.toast.send_notification()

    def on_export_writeas(self, sender: Gtk.Widget = None, event=None) -> None:
        """Configure Write.as client and export document asynchronously

        :param sender:
        :param event:
        :return:
        """

        doc = self.document_grid.selected_document or self.editor.document
        if not doc:
            return

        token = self.settings.get_string("writeas-access-token")

        if not token:
            self.toast.set_title(
                "You have to login to Write.as in Preferences -> Export")
            self.toast.set_default_action("Configure")
            self.disconnect_toast()
            self.toast.connect("default-action",
                               self.get_application().on_preferences)
            self.toast.send_notification()

        else:
            self.header.show_spinner(True)
            self.writeas_client.set_token(access_token=token)
            GObjectWorker.call(self.writeas_client.create_post,
                               args=(doc,),
                               callback=self.on_export_writeas_callback)

    def on_export_writeas_callback(self, result):
        self.header.show_spinner(False)
        if result:
            self.toast.set_title(_("Document successfully exported!"))
            self.toast.set_default_action(_("View"))
            self.disconnect_toast()
            self.uri_to_open = f"https://write.as/{result['id']}"
            self.toast.connect("default-action", self.open_uri)
        else:
            self.toast.set_title(_("Export failed."))
            self.toast.set_default_action(None)
        self.toast.send_notification()

    def on_backup(self, sender: Gtk.Widget = None, event=None) -> None:
        dialog: Gtk.FileChooserNative = Gtk.FileChooserNative.new(
            _("Select folder to store backup"),
            self,
            Gtk.FileChooserAction.SELECT_FOLDER,
            _("Select"),
        )
        dialog.set_create_folders(True)
        dialog_result = dialog.run()

        if dialog_result == Gtk.ResponseType.ACCEPT:
            self.header.show_spinner(True)

            backup_service = BackupService(settings=self.settings)
            GObjectWorker.call(backup_service.save,
                               args=(dialog.get_filename(),),
                               callback=self.on_backup_finished)

            self.toast.set_title(_("Backup started."))
            self.toast.send_notification()

        dialog.destroy()

    def on_backup_finished(self, result):
        self.header.show_spinner(False)
        if result:
            self.toast.set_title(_("All documents saved."))
            self.toast.set_default_action(_("Open folder"))
            self.uri_to_open = f"file://{result}"
            self.toast.connect("default-action", self.open_uri)
        else:
            self.toast.set_title(_("Backup failed."))
        self.toast.send_notification()

    def search_activated(self, sender, event=None):
        if self.screens.get_visible_child_name() == 'document-grid':
            self.on_document_search_activated(sender, event)
        elif self.screens.get_visible_child_name() == 'editor-grid':
            self.on_text_search_activated(sender, event)
        else:
            pass

    def on_document_search_activated(self,
                                     sender: Gtk.Widget = None,
                                     event=None) -> None:
        """Open search dialog to find a documents
        """
        dialog = QuickFindDialog(self.storage)
        response = dialog.run()

        if response == Gtk.ResponseType.APPLY and dialog.document_id:
            self.document_activate(dialog.document_id)
        dialog.destroy()

    def on_text_search_activated(self,
                                 sender: Gtk.Widget = None,
                                 event=None) -> None:
        """Open search dialog to find text in a documents
        """
        self.editor.on_search_text_activated(sender, event)

    def on_text_search_forward(self,
                               sender: Gtk.Widget = None,
                               event=None) -> None:
        if self.screens.get_visible_child_name() == 'editor-grid' \
                and self.editor.search_revealer.get_child_revealed():
            self.editor.search_forward(sender=sender, event=event)

    def on_text_search_backward(self,
                                sender: Gtk.Widget = None,
                                event=None) -> None:
        if self.screens.get_visible_child_name() == 'editor-grid' \
                and self.editor.search_revealer.get_child_revealed():
            self.editor.search_backward(sender=sender, event=event)

    def on_zoom_in(self, sender, event) -> None:
        self.zooming(Gdk.ScrollDirection.UP)

    def on_zoom_out(self, sender, event) -> None:
        self.zooming(Gdk.ScrollDirection.DOWN)

    def on_zoom_default(self, sender, event) -> None:
        self.settings.set_int('zoom', 100)
        self.settings.set_string("font",
                                 f'{FONT_SIZE_FAMILY} {FONT_SIZE_DEFAULT}')

    def toggle_spellcheck(self, state: bool) -> None:
        self.editor.set_spellcheck(state)

    def set_spellcheck_language(self, language_code: str) -> None:
        self.editor.set_spellcheck_language(language_code)

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

    def on_toggle_archive(self,
                          action: Gio.SimpleAction,
                          name: str = None) -> None:
        show_archived = self.header.archived_button.get_active()
        self.document_grid.show_archived = show_archived
        self.document_grid.reload_items()

        self.toggle_welcome(not show_archived and self.storage.count_all(
            path=self.document_grid.current_folder_path,
            with_archived=show_archived) == 0)

    def on_show_extended_stats(self,
                               action: Gio.SimpleAction,
                               name: str = None) -> None:
        if not self.extended_stats_dialog:
            self.extended_stats_dialog = ExtendedStatsDialog(window=self)
            self.extended_stats_dialog.connect(
                'destroy', self.on_extended_stats_dialog_close)

        if self.extended_stats_dialog and self.editor.document:
            self.extended_stats_dialog.document = self.editor.document
        self.extended_stats_dialog.present()
        self.update_document_stats(None)

    def on_extended_stats_dialog_close(self, dialog: Gtk.Widget = None) -> None:
        self.extended_stats_dialog = None

    def open_uri(self, event) -> None:
        if self.uri_to_open:
            Gtk.show_uri_on_window(None, self.uri_to_open, Gdk.CURRENT_TIME)
            self.uri_to_open = None

    def disconnect_toast(self):
        """Disconnect toast action. Weird way, need ti rewrite it"""
        try:
            self.toast.disconnect_by_func(
                self.get_application().on_preferences)
        except:
            pass

        try:
            self.toast.disconnect_by_func(self.open_uri)
        except:
            pass

    def on_preview(self, sender, event):
        if not self.is_document_editing:
            Logger.debug('Not in edit mode')
            return

        doc = self.document_grid.selected_document or self.editor.document

        if not doc:
            return

        if not self.preview:
            # create preview window
            text = doc.content if doc else None
            self.preview = Preview(parent=self, text=text)
            # connect signal handlers
            self.editor.scrolled.get_vscrollbar().connect(
                'value-changed', self.scroll_preview)
            self.editor.buffer.connect('changed', self.preview.buffer_changed)
            self.editor.connect('document-load', self.preview.show_preview)
            self.editor.connect('document-close', self.preview.show_empty_page)
            self.preview.connect('destroy', self.on_preview_close)

        if doc:
            self.preview.show_preview(self)

    def scroll_preview(self, range: Gtk.Range):
        if not self.preview:
            return

        adjustment = range.get_adjustment()
        percent = adjustment.get_value() / adjustment.get_upper()
        print(
            f'Scrolled to: {percent * 100}% / {adjustment.get_lower()} / {adjustment.get_upper()}'
        )
        self.preview.scroll_to(percent)

    def on_preview_close(self, sender):
        self.preview = None

    def update_document_stats(self, editor):
        stats = self.editor.stats
        document_path = self.editor.document.folder if self.editor.document else None
        self.header.update_stats(stats, document_path=document_path)
        if self.extended_stats_dialog:
            self.extended_stats_dialog.update_stats(stats)

    def on_print(self, sender, event=None):
        doc = self.document_grid.selected_document or self.editor.document
        if not doc:
            return

        printer = Printer(doc)
        printer.connect('finished', self.on_printer_callback)
        printer.print()

    def on_printer_callback(self, printer: Printer) -> None:
        print('printer callback resulted: ')
