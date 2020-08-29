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
from norka.services.storage import storage


class QuickFindDialog(Gtk.Dialog):
    __gtype_name__ = 'QuickFindDialog'

    def __init__(self):
        super().__init__(deletable=False,
                         destroy_with_parent=True,
                         use_header_bar=1,
                         title=_("Quick Find"),
                         )

        # Store document_id to response
        self.document_id = None

        self.get_style_context().add_class("quick-find-dialog")

        self.get_header_bar().set_visible(False)
        self.get_header_bar().set_no_show_all(True)

        self.set_default_size(400, 200)
        self.set_modal(True)
        self.set_transient_for(Gtk.Application.get_default().props.active_window)

        revealer = Gtk.Revealer()

        # ListStore to store results
        self.result_store = Gio.ListStore()
        result_box = Gtk.ListBox()
        result_box.bind_model(self.result_store, QuickFindRow)
        result_box.connect('row-activated', self.row_activated)

        placeholder_image = Gtk.Image.new_from_icon_name("folder-saved-search-symbolic",
                                                         Gtk.IconSize.LARGE_TOOLBAR)

        placeholder_label = Gtk.Label(label=_("Quickly find documents, just start typing its name."),
                                      wrap=True,
                                      max_width_chars=32,
                                      justify=Gtk.Justification.CENTER,
                                      )
        placeholder_label.show()

        placeholder_grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL,
                                    halign=Gtk.Align.CENTER,
                                    row_spacing=12,
                                    margin_top=32,
                                    )
        placeholder_grid.get_style_context().add_class("dim-label")
        placeholder_grid.add(placeholder_image)
        placeholder_grid.add(placeholder_label)
        placeholder_grid.show_all()

        result_box.set_placeholder(placeholder_grid)

        scrolled = Gtk.ScrolledWindow(expand=True,
                                      hscrollbar_policy=Gtk.PolicyType.NEVER)
        scrolled.add(result_box)

        self.search_entry = Gtk.SearchEntry(placeholder_text=_('Jump to...'))
        self.search_entry.connect('search-changed', self.search_changed)

        box = self.get_content_area()
        box.set_margin_start(6)
        box.set_margin_end(6)
        box.set_margin_top(6)
        box.set_margin_bottom(6)
        box.set_spacing(6)
        box.pack_start(self.search_entry, False, True, 0)
        box.pack_end(scrolled, True, True, 0)
        self.set_titlebar(None)

        self.connect('key_release_event', self.on_key_release_event)

        self.show_all()

    def on_key_release_event(self, sender, event_key: Gdk.EventKey):
        if event_key.keyval == Gdk.KEY_Escape:
            self.destroy()

        return False

    def search_changed(self, sender: Gtk.SearchEntry):
        self.result_store.remove_all()

        search_text = sender.get_text().strip()

        if not search_text:
            return

        documents = storage.find(search_text=search_text)
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
        archive_icon = Gtk.Image.new_from_icon_name('user-trash-symbolic', Gtk.IconSize.SMALL_TOOLBAR)
        archive_icon.get_style_context().add_class('muted')

        box.pack_start(doc_label, False, True, 0)
        if item.archived:
            box.pack_end(archive_icon, False, False, 0)

        self.add(box)
        self.show_all()
