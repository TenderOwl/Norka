# document_grid.py
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
import random
from datetime import datetime
from gettext import gettext as _
from urllib.parse import urlparse, unquote_plus

import cairo
from gi.repository import Gtk, GObject, Gdk
from gi.repository.GdkPixbuf import Pixbuf, Colorspace

from norka.define import TARGET_ENTRY_TEXT, RESOURCE_PREFIX
from norka.services.settings import Settings
from norka.services.storage import Storage
from norka.utils import find_child


class DocumentGrid(Gtk.Grid):
    __gtype_name__ = 'DocumentGrid'

    __gsignals__ = {
        'document-create': (GObject.SIGNAL_RUN_FIRST, None, (int,)),
        'document-import': (GObject.SIGNAL_RUN_LAST, None, (str,)),
    }

    def __init__(self, settings: Settings, storage: Storage):
        super().__init__()

        self.settings = settings
        self.storage = storage
        self.settings.connect("changed", self.on_settings_changed)

        self.model = Gtk.ListStore(Pixbuf, str, str, int, str)

        self.show_archived = False
        self.selected_path = None
        self.selected_document = None

        self.view = Gtk.IconView()
        self.view.set_model(self.model)
        self.view.set_pixbuf_column(0)
        self.view.set_text_column(1)
        self.view.set_tooltip_column(4)
        self.view.set_item_width(80)
        self.view.set_activate_on_single_click(True)
        self.view.set_selection_mode(Gtk.SelectionMode.BROWSE)

        self.view.connect('show', self.reload_items)
        self.view.connect('button-press-event', self.on_button_pressed)

        # Enable drag-drop
        enforce_target = Gtk.TargetEntry.new('text/plain', Gtk.TargetFlags.OTHER_APP, TARGET_ENTRY_TEXT)
        self.view.drag_dest_set(Gtk.DestDefaults.MOTION | Gtk.DestDefaults.DROP | Gtk.DestDefaults.HIGHLIGHT,
                                [enforce_target], Gdk.DragAction.COPY)
        self.view.connect('drag-data-received', self.on_drag_data_received)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_hexpand(True)
        scrolled.set_vexpand(True)
        scrolled.add(self.view)

        self.add(scrolled)

    def on_settings_changed(self, settings, key):
        if key == "sort-desc":
            self.reload_items(self)

    def reload_items(self, sender: Gtk.Widget = None, path: str = '/') -> None:
        order_desc = self.settings.get_boolean('sort-desc')
        self.model.clear()

        # For non-root path add virtual "upper" folder.
        if path != '/':
            self.create_folder_model(title='..', path='/')

        # Load folders first
        for folder in self.storage.get_folders(path=path):
            self.create_folder_model(title=folder.title, path=folder.path)

        # Then load documents, not before foldes.
        for document in self.storage.all(path=path, with_archived=self.show_archived, desc=order_desc):
            # icon = Gtk.IconTheme.get_default().load_icon('text-x-generic', 64, 0)
            opacity = 0.2 if document.archived else 1

            # generate icon. It needs to stay in cache
            icon = self.gen_preview(document.content[:200], opacity=opacity)

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

    def create_folder_model(self, title: str, path: str, tooltip: str = None):
        icon = Pixbuf.new_from_resource(RESOURCE_PREFIX + '/icons/folder.svg')
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

    def on_button_pressed(self, widget: Gtk.Widget, event: Gdk.EventButton):
        self.selected_path = self.view.get_path_at_pos(event.x, event.y)

        if not self.selected_path:
            self.selected_document = None
            self.view.unselect_all()
            return True

        if event.button == Gdk.BUTTON_SECONDARY:
            self.view.select_path(self.selected_path)

            self.selected_document = self.storage.get(self.model.get_value(
                self.model.get_iter(self.selected_path), 3
            ))

            found, rect = self.view.get_cell_rect(self.selected_path)

            builder = Gtk.Builder()
            builder.add_from_resource(f"{RESOURCE_PREFIX}/ui/documents_grid_context_menu.ui")

            menu_popover: Gtk.PopoverMenu = builder.get_object('popover-menu')
            find_child(menu_popover, "archive").set_visible(not self.selected_document.archived)
            find_child(menu_popover, "unarchive").set_visible(self.selected_document.archived)

            menu_popover.set_relative_to(self.view)
            menu_popover.set_pointing_to(rect)
            menu_popover.popup()

            return True

        self.view.unselect_all()
        self.selected_document = None

    # Move handler to window class
    def on_drag_data_received(self, widget: Gtk.Widget, drag_context: Gdk.DragContext, x: int, y: int,
                              data: Gtk.SelectionData, info: int, time: int) -> None:
        if info == TARGET_ENTRY_TEXT:
            uris = data.get_text().split('\n')

            for uri in uris:
                # Skip empty items
                if not uri:
                    continue

                p = urlparse(unquote_plus(uri))
                filename = os.path.abspath(os.path.join(p.netloc, p.path))

                self.emit('document-import', filename)
