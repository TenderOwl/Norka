# document_grid.py
#
# MIT License
#
# Copyright (c) 2020-2021 Andrey Maksimov <meamka@ya.ru>
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
from datetime import datetime
from gettext import gettext as _
from typing import Optional
from urllib.parse import urlparse, unquote_plus

import cairo
from gi.repository import Gtk, GObject, Gdk, Gio
from gi.repository.GdkPixbuf import Pixbuf, Colorspace

from norka.define import TARGET_ENTRY_TEXT, TARGET_ENTRY_REORDER, RESOURCE_PREFIX
from norka.models.document import Document
from norka.models.folder import Folder
from norka.services.logger import Logger
from norka.services.settings import Settings
from norka.services.storage import Storage
from norka.utils import find_child
from norka.widgets.folder_create_dialog import FolderCreateDialog


class DocumentGrid(Gtk.Box):
    __gtype_name__ = 'DocumentGrid'

    __gsignals__ = {
        'path-changed': (GObject.SIGNAL_RUN_FIRST, None, (str, str)),
        'document-create': (GObject.SIGNAL_RUN_FIRST, None, (int,)),
        'document-import': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        'document-activated': (GObject.SIGNAL_RUN_FIRST, None, ()),
        'rename-folder': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
    }

    show_archived = GObject.Property(type=bool, default=False)

    def __init__(self, settings: Settings, storage: Storage):
        super().__init__()

        self.last_selected_path = None
        self.settings = settings
        self.storage = storage
        self.settings.connect("changed", self.on_settings_changed)

        self.model = Gtk.ListStore(Pixbuf, str, str, int, str)

        self.selected_path = None
        # self.selected_document = None

        # Store current virtual files path.
        self.current_path = '/'

        self.set_orientation(Gtk.Orientation.VERTICAL)

        self.infobar = Gtk.InfoBar(message_type=Gtk.MessageType.INFO)
        infobar_label = Gtk.Label(label=_("Archived files only"))
        infobar_label.add_css_class('heading')
        self.infobar.add_child(infobar_label)
        self.bind_property('show_archived', self.infobar, 'revealed',
                           GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.BIDIRECTIONAL)

        self.view = Gtk.IconView()
        self.view.set_model(self.model)
        self.view.set_pixbuf_column(0)
        self.view.set_text_column(1)
        self.view.set_tooltip_column(4)
        self.view.set_item_width(80)
        self.view.set_activate_on_single_click(True)
        self.view.set_selection_mode(Gtk.SelectionMode.SINGLE)

        self.view.connect('show', self.reload_items)
        self.view.connect('item-activated', self.on_icon_item_activate)

        event_controller = Gtk.GestureClick()
        event_controller.connect('pressed', self.on_button_pressed)
        self.view.add_controller(event_controller)

        # Enable drag-drop
        # drop_target: Gtk.DropTarget = Gtk.DropTarget.new('str', Gdk.DragAction.COPY)
        # self.view.add_controller(drop_target)
        # import_dnd_target = Gtk.TargetEntry.new('text/plain', Gtk.TargetFlags.OTHER_APP, TARGET_ENTRY_TEXT)
        # reorder_dnd_target = Gtk.TargetEntry.new('reorder', Gtk.TargetFlags.SAME_APP, TARGET_ENTRY_REORDER)
        # self.view.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK,
        #                                    [import_dnd_target, reorder_dnd_target],
        #                                    Gdk.DragAction.MOVE)
        # self.view.enable_model_drag_dest([import_dnd_target, reorder_dnd_target],
        #                                  Gdk.DragAction.COPY | Gdk.DragAction.COPY)


        # drop_target.connect("accept", self.on_drag_begin)
        # drop_target.connect("motion", self.on_drag_motion)
        # drop_target.connect("leave", self.on_drag_leave)
        # drop_target.connect("drop", self.on_drag_end)
        # self.view.connect("drag-data-get", self.on_drag_data_get)
        # drop_target.connect('drag-data-received', self.on_drag_data_received)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_hexpand(True)
        scrolled.set_vexpand(True)
        scrolled.set_child(self.view)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.append(self.infobar)
        main_box.append(scrolled)

        self.append(main_box)

    @property
    def current_folder_path(self):
        current_folder_path = self.current_path or '/'
        if current_folder_path != '/' and current_folder_path.endswith('/'):
            current_folder_path = current_folder_path[:-1]
        return current_folder_path

    @property
    def is_folder_selected(self) -> bool:
        if self.selected_path is None:
            return False

        model_iter = self.model.get_iter(self.selected_path)
        doc_id = self.model.get_value(model_iter, 3)
        return doc_id == -1

    @property
    def selected_document_id(self) -> Optional[int]:
        """Returns Id of the selected document or `None`
        """
        if self.is_folder_selected:
            return None

        model_iter = self.model.get_iter(self.selected_path)
        return self.model.get_value(model_iter, 3)

    @property
    def selected_document(self) -> Optional[Document]:
        """Returns selected :model:`Document` or `None`
        """
        Logger.debug('DocumentGrid.selected_document')
        if self.is_folder_selected:
            return None

        if self.selected_path is None:
            return None

        model_iter = self.model.get_iter(self.selected_path)
        doc_id = self.model.get_value(model_iter, 3)
        return self.storage.get(doc_id)

    @property
    def selected_folder(self) -> Optional[Folder]:
        """Returns selected :model:`Folder` or `None` if :model:`Document` selected.
        """
        if not self.is_folder_selected:
            return None

        model_iter = self.model.get_iter(self.selected_path)
        return Folder(
            title=self.model.get_value(model_iter, 1),
            path=self.model.get_value(model_iter, 2)
        )

    def on_settings_changed(self, settings, key):
        if key == "sort-desc":
            self.reload_items(self)

    def on_infobar_response(self, sender: Gtk.Widget, response: Gtk.ResponseType, *_):
        self.infobar.set_revealed(False)
        self.show_archived = False
        self.reload_items()

    def reload_items(self, sender: Gtk.Widget = None, path: str = None) -> None:
        order_desc = self.settings.get_boolean('sort-desc')
        self.model.clear()

        _old_path = self.current_path

        self.current_path = path or self.current_folder_path

        # For non-root path add virtual "upper" folder.
        if self.current_folder_path != '/':
            # /folder 1/folder 2 -> /folder 1
            folder_path = self.current_folder_path[:self.current_folder_path[:-1].rfind('/')] or '/'
            folder_open_icon = Pixbuf.new_from_resource(RESOURCE_PREFIX + '/icons/folder-open.svg')
            self.create_folder_model(title='..', path=folder_path, icon=folder_open_icon,
                                     tooltip=_('Go to the upper folder'))

        # Emit "path-changed" signal.
        self.emit('path-changed', _old_path, self.current_path)

        if not self.show_archived:
            # Load folders first
            Logger.info(f"reload_items: {self.current_folder_path}")
            for folder in self.storage.get_folders(path=self.current_folder_path):
                self.create_folder_model(title=folder.title, path=folder.path)

        # Then load documents, not before foldes.
        if self.show_archived:
            documents = self.storage.archived(desc=order_desc)
        else:
            documents = self.storage.all(path=self.current_folder_path,
                                         with_archived=self.show_archived,
                                         desc=order_desc)

        for document in documents:
            # icon = Gtk.IconTheme.get_default().load_icon('text-x-generic', 64, 0)

            # generate icon. It needs to stay in cache
            icon = self.gen_preview(document.content[:200])

            # Generate tooltip
            tooltip = f"{document.title}"

            if document.created:
                created = datetime.strptime(document.created, "%Y-%m-%d %H:%M:%S.%f")
                tooltip += f"\n<span weight='600' size='smaller' alpha='75%'>" \
                           + _('Created') + f": {created.strftime('%x')}</span>"

            if document.modified:
                modified = datetime.strptime(document.modified, "%Y-%m-%d %H:%M:%S.%f")
                tooltip += f"\n<span weight='600' size='smaller' alpha='75%'>" \
                           + _('Modified') + f": {modified.strftime('%x')}</span>"

            self.model.append([icon,
                               document.title,
                               document.content,
                               document.document_id,
                               tooltip])

        if self.selected_path:
            self.view.select_path(self.selected_path)

    def create_folder_model(self, title: str, path: str, tooltip: str = None, icon: Pixbuf = None):
        icon = icon or Pixbuf.new_from_resource(RESOURCE_PREFIX + '/icons/folder.svg')
        self.model.append([icon,
                           title,
                           path,
                           -1,
                           tooltip or title])

    @staticmethod
    def gen_preview(text, size=9, opacity=1) -> Pixbuf:
        pix = Pixbuf.new(Colorspace.RGB, True, 8, 60, 80)
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, pix.get_width(), pix.get_height())
        context = cairo.Context(surface)

        # Gdk.cairo_set_source_pixbuf(context, pix, 0, 0)
        # context.paint()  # paint the pixbuf
        # context.select_font_face('sans-serif')
        context.set_font_size(size)

        # Document background
        grad = cairo.LinearGradient(0, 0, 0, pix.get_height())
        grad.add_color_stop_rgb(0, 0.95, 0.95, 0.95)
        grad.add_color_stop_rgb(pix.get_height(), 0.93, 0.93, 0.93)
        context.set_source(grad)
        context.paint_with_alpha(opacity)

        # Document Outline
        grad = cairo.LinearGradient(0, 0, 0, pix.get_height())
        grad.add_color_stop_rgba(0, 1, 1, 1, opacity)
        grad.add_color_stop_rgba(pix.get_height(), 0.94, 0.94, 0.94, opacity)
        context.rectangle(1, 1, pix.get_width() - 2, pix.get_height() - 2)
        context.set_source(grad)
        context.stroke()

        # Border
        context.rectangle(0, 0, pix.get_width(), pix.get_height())
        context.set_source_rgba(0.9, 0.9, 0.9, opacity)
        context.stroke()

        # add the text
        for num, line in enumerate(text.split('\n'), 1):
            context.set_source_rgba(0.2, 0.2, 0.24, opacity)

            # Fix to remove \r if it exists
            if line.startswith('\r'):
                line = line[1:]

            if num == 1:
                context.select_font_face('sans-serif', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            else:
                context.select_font_face('monospace', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)

            context.move_to(4, 4 + size * num)
            context.show_text(line)

        # get the resulting pixbuf
        surface = context.get_target()
        return Gdk.pixbuf_get_from_surface(surface, 0, 0, surface.get_width(), surface.get_height())

    def on_icon_item_activate(self, view: Gtk.IconView, path: Gtk.TreePath, *_):
        self.selected_path = path
        self.emit('document-activated')

    def on_button_pressed(self, widget: Gtk.Widget, event):
        """Handle mouse button press event and display context menu if needed.
        """
        self.selected_path = self.view.get_path_at_pos(event.x, event.y)

        if not self.selected_path:
            # self.selected_document = None
            self.view.unselect_all()
            return True

        if event.button == Gdk.BUTTON_SECONDARY:
            self.view.select_path(self.selected_path)

            origin_item = self.selected_folder if self.is_folder_selected else self.selected_document
            if isinstance(origin_item, Folder) and origin_item.title == "..":
                print('System @UP folder. Action declined.')
                return

            # self.selected_document = self.storage.get(self.model.get_value(
            #     self.model.get_iter(self.selected_path), 3
            # ))

            found, rect = self.view.get_cell_rect(self.selected_path)

            builder = Gtk.Builder()
            builder.add_from_resource(f"{RESOURCE_PREFIX}/ui/documents_grid_context_menu.ui")

            # Switch between folder's and document's menus
            if self.is_folder_selected:
                menu_popover: Gtk.PopoverMenu = builder.get_object('folder-popover-menu')
            else:
                menu_popover: Gtk.PopoverMenu = builder.get_object('document-popover-menu')
                find_child(menu_popover, "archive").set_visible(not self.selected_document.archived)
                find_child(menu_popover, "unarchive").set_visible(self.selected_document.archived)

            menu_popover.set_relative_to(self.view)
            menu_popover.set_pointing_to(rect)
            menu_popover.popup()

            return True

        self.view.unselect_all()

    # def on_drag_begin(self, drop: Gdk.Drop, user_data: object) -> None:
    #     self.last_selected_path = self.selected_path

    # def on_drag_motion(self, widget: Gtk.Widget, x: int, y: int, time: int) -> bool:
    #     # Change cursor icon based on drop target.
    #     # if the user move mouse over the folder - it becomes MOVE action
    #     model_path = self.view.get_path_at_pos(x, y)
    #     if not model_path:
    #         return False
    #     model_iter = self.model.get_iter(model_path)
    #     item_id = self.model.get_value(model_iter, 3)
    #
    #     # Select hover cell, make it interactive for the user
    #     self.view.select_path(model_path)
    #
    #     # Folder could have an ID, so this condition going to change
    #     if item_id == -1:
    #         Gdk.drag_status(context, Gdk.DragAction.MOVE, time)
    #         # TODO: Change folder icon on hover
    #         # self.model.set_value(model_iter, 0, Pixbuf.new_from_resource(RESOURCE_PREFIX + '/icons/folder-open.svg'))
    #     else:
    #         Gdk.drag_status(context, Gdk.DragAction.COPY, time)
    #
    #     return True

    # def on_drag_leave(self, widget: Gtk.Widget, time: int) -> None:
    #     # print('on_drag_leave')
    #     pass

    # def on_drag_end(self, widget: Gtk.Widget, context: Gdk.DragContext) -> None:
    #     # print('on_drag_end')
    #     if self.last_selected_path:
    #         self.view.select_path(self.last_selected_path)
    #         self.last_selected_path = None

    # Move handler to window class
    # def on_drag_data_received(self, widget: Gtk.Widget, drag_context: Gdk.DragContext, x: int, y: int,
    #                           data: Gtk.SelectionData, info: int, time: int) -> None:
    #
    #     print(f'Drag info: {info}')
    #
    #     # Handle normal dnd from other apps with files as a target
    #     if info == TARGET_ENTRY_TEXT:
    #         uris = data.get_text().split('\n')
    #
    #         print(data.get_text())
    #         for uri in uris:
    #             # Skip empty items
    #             if not uri:
    #                 continue
    #
    #             p = urlparse(unquote_plus(uri))
    #             filename = os.path.abspath(os.path.join(p.netloc, p.path))
    #             self.emit('document-import', filename)
    #
    #     # Handle reordering and moving inside Norka's virtual filesystem
    #     elif info == TARGET_ENTRY_REORDER:
    #         origin_item = self.selected_folder if self.is_folder_selected else self.selected_document
    #
    #         dest_path = self.view.get_path_at_pos(x, y)
    #         if not dest_path:
    #             print("No dest path")
    #             return
    #
    #         dest_iter = self.model.get_iter(dest_path)
    #         dest_item_id = self.model.get_value(dest_iter, 3)
    #
    #         if dest_item_id == -1:
    #             dest_item = Folder(
    #                 title=self.model.get_value(dest_iter, 1),
    #                 path=self.model.get_value(dest_iter, 2)
    #             )
    #         else:
    #             dest_item = self.storage.get(dest_item_id)
    #
    #         # Don't move item to itself :)
    #         if origin_item.absolute_path == dest_item.absolute_path:
    #             print("Don't move item to itself")
    #             return
    #
    #         # Create folders when doc dropped onto doc
    #         # After creation rename dialog should appear
    #         if isinstance(dest_item, Document):
    #             folder_id = self.create_folder(f'{origin_item.title} + {dest_item.title}',
    #                                            self.current_folder_path)
    #
    #             if folder_id:
    #                 folder = self.storage.get_folder(folder_id)
    #                 self.storage.move(origin_item.document_id, folder.absolute_path)
    #                 self.storage.move(dest_item.document_id, folder.absolute_path)
    #                 self.reload_items()
    #             return
    #
    #             # For folders, we have to move folder and its content to destination
    #         if isinstance(origin_item, Folder):
    #             print(f'Folder "{origin_item.title}": "{origin_item.path}" -> "{dest_item.absolute_path}"')
    #
    #             self.storage.move_folder(origin_item, dest_item.absolute_path)
    #             self.reload_items()
    #         # For regular documents it is easy to move - just update the `path`.
    #         else:
    #             if self.storage.update(origin_item.document_id, {'path': dest_item.absolute_path}):
    #                 print(f'Moved {origin_item.title} to {dest_item.absolute_path}')
    #                 self.reload_items()
    #
    #     Gtk.drag_finish(drag_context, True, drag_context.get_selected_action() == Gdk.DragAction.MOVE, time)

    def create_folder(self, title: str, path: str) -> Optional[int]:
        dialog = FolderCreateDialog(title)
        result = dialog.run()
        folder_path = dialog.folder_title
        dialog.destroy()
        if result == Gtk.ResponseType.ACCEPT:
            print(f'Folder "{folder_path}" created')
            return self.storage.add_folder(folder_path, path)

    def on_folder_rename_activated(self, sender: Gtk.Widget, title: str) -> None:
        sender.destroy()

        folder = self.document_grid.selected_folder
        if folder and self.storage.rename_folder(folder, title):
            self.document_grid.reload_items()

    def filter_model_by_value(self, model, path, iter):
        print(f'filter_model_by_value: {model}; {path}; {iter};')
