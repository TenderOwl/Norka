# quick_find_dialog.py
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

from gettext import gettext as _

from gi.repository import Gtk, Gdk, Gio, GObject

from norka.models.document import Document
from norka.services.storage import Storage


class QuickFindDialog(Gtk.Dialog):
    __gtype_name__ = 'QuickFindDialog'

    def __init__(self, storage: Storage):
        super().__init__(title=_("Quick Find"))

        self.storage = storage

        # Store document_id to response
        self.document_id = None

        self.add_css_class("quick-find-dialog")

        # self.get_header_bar().set_visible(False)
        # self.get_header_bar().set_no_show_all(True)

        self.set_default_size(400, 200)
        self.set_modal(True)
        self.set_transient_for(Gtk.Application.get_default().props.active_window)

        revealer = Gtk.Revealer()

        # ListStore to store results
        self.result_store = Gio.ListStore()
        result_box = Gtk.ListBox()
        result_box.bind_model(self.result_store, QuickFindRow)
        result_box.connect('row-activated', self.row_activated)

        placeholder_image = Gtk.Image.new_from_icon_name("folder-saved-search-symbolic")

        placeholder_label = Gtk.Label(label=_("Quickly find documents, just start typing its name."),
                                      wrap=True,
                                      max_width_chars=32,
                                      justify=Gtk.Justification.CENTER,
                                      )

        placeholder_grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL,
                                    halign=Gtk.Align.CENTER,
                                    row_spacing=12,
                                    margin_top=32,
                                    )
        placeholder_grid.add_css_class("dim-label")
        placeholder_grid.add(placeholder_image)
        placeholder_grid.add(placeholder_label)


        result_box.set_placeholder(placeholder_grid)

        scrolled = Gtk.ScrolledWindow(expand=True,
                                      hscrollbar_policy=Gtk.PolicyType.NEVER)
        scrolled.set_child(result_box)

        self.search_entry = Gtk.SearchEntry(placeholder_text=_('Jump to...'))
        self.search_entry.connect('search-changed', self.search_changed)

        box = Gtk.Box()
        box.set_margin_start(6)
        box.set_margin_end(6)
        box.set_margin_top(6)
        box.set_margin_bottom(6)
        box.set_spacing(6)
        box.append(self.search_entry)
        box.append(scrolled)
        # self.set_titlebar(None)
        self.set_child(box)

        self.event_controller = Gtk.EventControllerKey()
        self.add_controller(self.event_controller)
        self.event_controller.connect('key-released', self.on_key_released)


    def on_key_released(self, sender: Gtk.EventControllerKey, keyval: int, _keycode: int, _state:Gdk.ModifierType, _user_data: object = None):
        if keyval == Gdk.KEY_Escape:
            self.destroy()

        return False

    def search_changed(self, sender: Gtk.SearchEntry):
        self.result_store.remove_all()

        search_text = sender.get_text().strip()

        if not search_text:
            return

        documents = self.storage.find(search_text=search_text)
        for document in documents:
            self.result_store.append(document)

    def row_activated(self, sender: Gtk.ListBox, row: Gtk.ListBoxRow):
        self.document_id = row.document_id
        self.response(Gtk.ResponseType.APPLY)
        self.popdown()

    def popdown(self):
        self.hide()


class QuickFindRow(Gtk.ListBoxRow):
    document_id = GObject.property(type=int)

    def __init__(self, item: Document):
        super().__init__()

        self.document_id = item.document_id

        # Create layout box
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,
                      spacing=6,
                      margin=6)

        doc_label = Gtk.Label(label=item.title)
        archive_icon = Gtk.Image.new_from_icon_name('user-trash-symbolic')
        archive_icon.add_css_class('muted')

        box.append(doc_label)
        if item.archived:
            box.append(archive_icon)

        self.set_child(box)
